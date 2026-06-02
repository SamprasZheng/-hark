"""Backend router ("the brain") for the Discord bot.

Hybrid by default (the principal's choice):

  * Persona chat  -> local Nemotron via the existing ``NemotronClient``
                     (private, free, runs on the RTX 5070 / Ollama). Falls back
                     to a tool-less local Claude Code call if Ollama is down.
  * ``/ask`` deep -> local Claude Code CLI in a READ-ONLY research mode, reading
                     the whole ``$hark`` tree. This is the "loopback to local
                     cloud code" the principal asked for — the real Claude Code
                     engine, not the lightweight Nemotron dispatcher.

Hard safety: the ``/ask`` call is locked to read-only tools (Read/Grep/Glob/
WebSearch/WebFetch), explicitly DENIES Write/Edit/Bash, runs in plan-less
``default`` mode with a per-question dollar ceiling, and never commits anything.
Any writeback is a separate, human-reviewed flow — never automatic.

Everything is best-effort and never raises: failures come back as a
``BrainReply`` with ``ok=False`` and a human-readable ``error`` (mirroring the
``NemotronClient`` contract), so the bot can post a clean message instead of
crashing.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import time
from dataclasses import dataclass
from typing import Optional

from sharks.ai.nemotron_client import NemotronClient
from sharks.discord.config import Settings
from sharks.discord.personas import ChatPersona


@dataclass
class BrainReply:
    ok: bool
    text: str = ""
    backend: str = ""          # "nemotron" | "claude" | "none"
    model: str = ""
    latency_ms: int = 0
    cost_usd: Optional[float] = None
    error: Optional[str] = None

    def display(self, max_len: int = 1800) -> str:
        """Discord-safe body (2000-char limit; leave room for a header)."""
        body = self.text if self.ok else f"⚠️ {self.error or 'unknown error'}"
        return body if len(body) <= max_len else body[: max_len - 1] + "…"


# ── Claude Code CLI ───────────────────────────────────────────────────────────

def _claude_bin() -> Optional[str]:
    override = (os.environ.get("SHARKS_DISCORD_CLAUDE_BIN") or "").strip()
    if override:
        return override
    return shutil.which("claude")


def _run_claude(
    prompt: str,
    settings: Settings,
    *,
    system_prompt: Optional[str] = None,
    read_only_tools: bool = False,
    no_tools: bool = False,
) -> BrainReply:
    """Invoke the local Claude Code CLI in headless print mode.

    ``read_only_tools`` -> research allowlist (for /ask). ``no_tools`` -> pure
    chat (for persona-via-claude fallback). Prompt is fed on stdin so it can
    never be swallowed by a variadic flag.
    """
    exe = _claude_bin()
    if not exe:
        return BrainReply(ok=False, backend="claude",
                          error="claude CLI not found on PATH (set SHARKS_DISCORD_CLAUDE_BIN)")

    args = [
        "-p",
        "--output-format", "json",
        "--permission-mode", "default",
        "--model", settings.claude_model,
        "--max-budget-usd", str(settings.claude_budget_usd),
    ]
    if no_tools:
        args += ["--tools", ""]                       # disable all tools = pure chat
    elif read_only_tools:
        args += ["--allowedTools", ",".join(settings.ask_allowed_tools)]
        args += ["--disallowedTools", ",".join(settings.ask_disallowed_tools)]
        for d in settings.add_dirs:
            args += ["--add-dir", d]
    if system_prompt:
        args += ["--append-system-prompt", system_prompt]

    # .cmd/.bat shims (npm on Windows) must go through cmd.exe.
    if os.name == "nt" and exe.lower().endswith((".cmd", ".bat")):
        argv = ["cmd", "/c", exe, *args]
    else:
        argv = [exe, *args]

    started = time.perf_counter()
    try:
        proc = subprocess.run(
            argv,
            input=prompt,
            cwd=str(settings.project_root),
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=settings.claude_timeout_s,
        )
    except subprocess.TimeoutExpired:
        return BrainReply(ok=False, backend="claude", model=settings.claude_model,
                          latency_ms=int((time.perf_counter() - started) * 1000),
                          error=f"claude timed out after {settings.claude_timeout_s}s")
    except Exception as exc:  # defensive — never raise into the bot loop
        return BrainReply(ok=False, backend="claude", error=f"claude spawn failed: {exc}")

    latency = int((time.perf_counter() - started) * 1000)
    if proc.returncode != 0 and not proc.stdout.strip():
        err = (proc.stderr or "").strip()[:400] or f"claude exited {proc.returncode}"
        return BrainReply(ok=False, backend="claude", model=settings.claude_model,
                          latency_ms=latency, error=err)

    text, cost = _parse_claude_json(proc.stdout)
    if text is None:
        return BrainReply(ok=False, backend="claude", model=settings.claude_model,
                          latency_ms=latency,
                          error="could not parse claude output: " + proc.stdout[:200])
    return BrainReply(ok=True, text=text, backend="claude", model=settings.claude_model,
                      latency_ms=latency, cost_usd=cost)


def _parse_claude_json(stdout: str) -> tuple[Optional[str], Optional[float]]:
    """Extract (result_text, cost_usd) from `claude --output-format json`."""
    stdout = (stdout or "").strip()
    if not stdout:
        return None, None
    try:
        obj = json.loads(stdout)
    except json.JSONDecodeError:
        # stream-json or stray prose — take the last JSON object line if any.
        for line in reversed(stdout.splitlines()):
            line = line.strip()
            if line.startswith("{") and line.endswith("}"):
                try:
                    obj = json.loads(line)
                    break
                except json.JSONDecodeError:
                    continue
        else:
            return stdout, None  # not JSON at all — return raw text
    if isinstance(obj, dict):
        if obj.get("is_error"):
            return None, obj.get("total_cost_usd")
        text = obj.get("result") or obj.get("text") or ""
        return (text or None), obj.get("total_cost_usd")
    return stdout, None


# ── Nemotron (local Ollama) ───────────────────────────────────────────────────

def _run_nemotron(system_prompt: str, user: str, settings: Settings, *,
                  model: Optional[str] = None, max_tokens: Optional[int] = None) -> BrainReply:
    client = NemotronClient()
    if not client.available:
        return BrainReply(ok=False, backend="nemotron",
                          error="local Nemotron/Ollama not reachable")
    call = client.chat(
        "executor",
        [{"role": "system", "content": system_prompt},
         {"role": "user", "content": user}],
        reasoning="off",
        temperature=settings.persona_temperature,
        max_tokens=max_tokens or settings.persona_max_tokens,
        model=model or settings.local_model,
    )
    if call.error or not call.content.strip():
        return BrainReply(ok=False, backend="nemotron", model=call.model,
                          latency_ms=call.latency_ms,
                          error=call.error or "empty response")
    return BrainReply(ok=True, text=call.content.strip(), backend="nemotron",
                      model=call.model, latency_ms=call.latency_ms)


# ── Public entry points ───────────────────────────────────────────────────────

def ask_persona(persona: ChatPersona, message: str, settings: Settings) -> BrainReply:
    """Persona chat. Local Nemotron first; Claude (tool-less) fallback unless the
    backend is pinned to 'local'."""
    if settings.backend == "claude":
        return _run_claude(message, settings, system_prompt=persona.system_prompt, no_tools=True)

    reply = _run_nemotron(persona.system_prompt, message, settings)
    if reply.ok or settings.backend == "local":
        return reply
    # hybrid fallback: Nemotron down -> use Claude as a pure chat brain.
    fb = _run_claude(message, settings, system_prompt=persona.system_prompt, no_tools=True)
    if not fb.ok:
        fb.error = f"nemotron: {reply.error}; claude-fallback: {fb.error}"
    return fb


def ask_claude_research(question: str, settings: Settings) -> BrainReply:
    """The /ask loopback: read-only Claude Code over the $hark tree.

    On a 'local' backend (offline pin) this degrades to a tool-less Nemotron
    answer, with a note that it cannot read the repo."""
    if settings.backend == "local":
        sys = (
            "你是 PolkaSharks 投研系統的本地助理。離線模式下你無法讀取檔案,"
            "只能用一般知識回答,並提醒使用者開啟混合模式才能讀取 $hark。"
            "用繁體中文,只做研究與分析,不是個人化投資建議,永不代為下單。"
        )
        rep = _run_nemotron(sys, question, settings)
        if rep.ok:
            rep.text = "（離線模式 · 未讀取 $hark）\n" + rep.text
        return rep

    system = (
        "你是 PolkaSharks 私人投研系統的研究助理,在唯讀模式下運作。"
        "你可以讀取整個 $hark(philosophy/、wiki/、analysts/、outputs/、tech/、"
        "crypto/ 等),回答時盡量引用具體檔案路徑與 outputs/ 的數據。"
        "嚴守界線:只做研究/分析/教育,這不是個人化投資建議,你不是持牌投顧;"
        "系統只產生研究與建議,永不代為下單、轉帳或連接券商/交易所。"
        "用繁體中文,簡潔、可證偽,不要捏造數字或日期(沒資料就說 TBD)。"
    )
    return _run_claude(question, settings, system_prompt=system, read_only_tools=True)


# ── multi-backend router (Discord = front-end to all local resources) ─────────

def list_ollama_models(base_url: str = "http://127.0.0.1:11434") -> list[str]:
    """Live list of pulled Ollama models (empty if the daemon is down)."""
    import urllib.request
    try:
        with urllib.request.urlopen(f"{base_url}/api/tags", timeout=4) as r:
            data = json.loads(r.read().decode("utf-8"))
        return sorted(m.get("name") for m in data.get("models", []) if m.get("name"))
    except Exception:
        return []


def ask_local_model(question: str, settings: Settings,
                    model: Optional[str] = None) -> BrainReply:
    """General Q&A on any local Ollama model (the 'gpu / ollama / nemotron' path)."""
    sys = ("你是 PolkaSharks 跑在使用者自己 GPU 上的本地助理。用繁體中文回答,"
           "做研究與分析,非個人化投資建議,系統只建議、永不下單。")
    rep = _run_nemotron(sys, question, settings, model=model, max_tokens=700)
    rep.backend = "local"
    return rep


def ask_wiki(question: str, settings: Settings,
             model: Optional[str] = None) -> BrainReply:
    """LLM-wiki backend: local keyword RAG over $hark markdown + local synthesis.
    No Claude, no cloud."""
    from sharks.discord import wiki_rag
    hits = wiki_rag.search(question, settings.project_root, k=5)
    if not hits:
        return BrainReply(ok=False, backend="wiki",
                          error="LLM-wiki 找不到相關片段(試試英文關鍵字 / ticker / 概念名)。")
    ctx = wiki_rag.context_block(hits)
    sys = ("你是 PolkaSharks 的 LLM-wiki 檢索助理。只能依據下面提供的 wiki 片段回答,"
           "務必引用來源檔名;片段不足以回答就明說。繁體中文,研究用途、非個人化投資建議。")
    user = f"問題:{question}\n\n可用的 wiki 片段:\n{ctx}"
    rep = _run_nemotron(sys, user, settings, model=model, max_tokens=700)
    rep.backend = "wiki"
    if rep.ok:
        srcs = ", ".join(dict.fromkeys(h.path for h in hits))
        rep.text = f"{rep.text}\n\n_來源:{srcs}_"
    return rep


def ask_codex(question: str, settings: Settings) -> BrainReply:
    """Codex CLI backend (best-effort). Returns clear guidance if not installed."""
    exe = (os.environ.get("SHARKS_DISCORD_CODEX_BIN") or "").strip() or shutil.which("codex")
    if not exe:
        return BrainReply(ok=False, backend="codex",
                          error=("codex CLI 未安裝。安裝後即可用(例:`npm i -g @openai/codex`,"
                                 "或把路徑設到 SHARKS_DISCORD_CODEX_BIN)。"))
    argv = ([exe, "exec", "--skip-git-repo-check", question]
            if not (os.name == "nt" and exe.lower().endswith((".cmd", ".bat")))
            else ["cmd", "/c", exe, "exec", "--skip-git-repo-check", question])
    try:
        proc = subprocess.run(argv, cwd=str(settings.project_root), capture_output=True,
                              text=True, encoding="utf-8", timeout=settings.claude_timeout_s)
    except Exception as exc:
        return BrainReply(ok=False, backend="codex", error=f"codex 執行失敗:{exc}")
    out = (proc.stdout or "").strip()
    if not out:
        return BrainReply(ok=False, backend="codex",
                          error=(proc.stderr or "codex 無輸出")[:300])
    return BrainReply(ok=True, text=out, backend="codex", model="codex")


def ask_backend(backend: str, question: str, settings: Settings,
                model: str = "") -> BrainReply:
    """Dispatch to a chosen resource: claude | local | wiki | codex."""
    backend = (backend or "claude").lower()
    if backend == "claude":
        return ask_claude_research(question, settings)
    if backend in ("local", "ollama", "nemotron"):
        return ask_local_model(question, settings, model=model or None)
    if backend == "wiki":
        return ask_wiki(question, settings, model=model or None)
    if backend == "codex":
        return ask_codex(question, settings)
    return BrainReply(ok=False, backend=backend, error=f"未知後端:{backend}")
