"""Council debate engine — multi-persona 質疑 → 投票 → 結論.

A small multi-agent debate that runs **entirely on the local Ollama model**
(private, free, on the RTX 5070). It exists so a meeting's conclusion is not one
voice but a roomful that disagrees on the record:

  Round 1 (立場)   — each of K analyst personas takes a stance on the day's brief.
  Round 2 (質疑+投票) — each reads the others, rebuts the one it most disagrees
                      with, then casts a structured vote (多/空/中性 + 信心 + 動作).
  主席結論          — a chair persona synthesises the tally + key split into a
                      final 結論 + discipline reminder.

The LLM call is injected as ``ask_fn(system, user, max_tokens) -> (text, ok)`` so
the engine is testable offline and backend-agnostic. ``run_council`` wires it to
the local Nemotron client by default.

Why a clean instruct model by default (qwen2.5:7b): ``nemotron-3-nano:4b`` is a
*reasoning* model — it spends the token budget in a separate ``reasoning`` channel
and returns empty ``content`` when truncated, which is poor for many short debate
turns. The model is configurable; nemotron still works with a larger budget.

Recommend-only: the conclusion is a research view, never an order.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Callable, Optional

from sharks.ai.nemotron_client import NemotronClient
from sharks.discord.personas import ChatPersona, load_personas

# ask_fn(system, user, max_tokens) -> (text, ok)
AskFn = Callable[[str, str, int], tuple[str, bool]]

DEFAULT_COUNCIL = ("huang", "sam", "buffet", "serenity", "bear", "momentum")
DEFAULT_CHAIR = "sharks"
_VOTE_WORDS = {"多": "多", "空": "空", "中性": "中性", "中立": "中性"}
_VOTE_RE = re.compile(r"投票[:：]?\s*(多|空|中性|中立).*?信心[:：]?\s*([1-5])", re.DOTALL)


@dataclass
class Vote:
    persona: str
    title: str
    model: str = ""           # the local model this seat ran on
    stance: str = ""          # round-1 立場 text
    rebuttal_vote: str = ""   # round-2 質疑+投票 text
    vote: str = "中性"        # 多 | 空 | 中性
    conviction: int = 3       # 1..5
    action: str = ""


@dataclass
class CouncilResult:
    topic: str
    votes: list[Vote] = field(default_factory=list)
    tally: dict = field(default_factory=dict)         # {多:int, 空:int, 中性:int, avg_conviction:float}
    conclusion: str = ""
    model: str = ""
    backend: str = ""
    ok: bool = False
    note: str = ""

    def lean(self) -> str:
        t = self.tally
        if not t:
            return "中性"
        order = sorted(("多", "空", "中性"), key=lambda k: t.get(k, 0), reverse=True)
        return order[0]


# ── local ask_fn ──────────────────────────────────────────────────────────────

def make_local_ask(model: str, temperature: float = 0.75) -> tuple[AskFn, str]:
    """Return (ask_fn, backend_name) backed by the local Nemotron/Ollama client."""
    client = NemotronClient()

    def ask(system: str, user: str, max_tokens: int = 260) -> tuple[str, bool]:
        call = client.chat(
            "executor",
            [{"role": "system", "content": system}, {"role": "user", "content": user}],
            reasoning="off", temperature=temperature, max_tokens=max_tokens, model=model,
        )
        return (call.content or "").strip(), (call.error is None and bool((call.content or "").strip()))

    return ask, client.backend.name


# ── vote parsing ──────────────────────────────────────────────────────────────

def _parse_vote(text: str) -> tuple[str, int, str]:
    """Pull (vote, conviction, action) from a round-2 reply. Tolerant: defaults to
    中性/3 if the structured line is missing."""
    vote, conv, action = "中性", 3, ""
    m = _VOTE_RE.search(text or "")
    if m:
        vote = _VOTE_WORDS.get(m.group(1), "中性")
        try:
            conv = max(1, min(5, int(m.group(2))))
        except ValueError:
            conv = 3
    am = re.search(r"動作[:：]\s*(.+)$", text or "", re.MULTILINE)
    if am:
        action = am.group(1).strip()[:80]
    return vote, conv, action


def _tally(votes: list[Vote]) -> dict:
    out = {"多": 0, "空": 0, "中性": 0}
    for v in votes:
        out[v.vote] = out.get(v.vote, 0) + 1
    convs = [v.conviction for v in votes] or [0]
    out["avg_conviction"] = round(sum(convs) / len(convs), 1)
    return out


# ── engine ────────────────────────────────────────────────────────────────────

def run_council(
    topic: str,
    brief: str,
    *,
    council: list[ChatPersona],
    chair: Optional[ChatPersona] = None,
    models: Optional[dict[str, str]] = None,
    default_model: str = "qwen2.5:7b",
    ask_maker: Callable[[str], tuple[AskFn, str]] = make_local_ask,
    brief_cap: int = 1600,
) -> CouncilResult:
    """Run the debate. Each persona can sit on a DIFFERENT local model
    (multi-model council) via ``models`` = {persona_name: model}; a missing name
    falls back to ``default_model``. ``ask_maker(model) -> (ask_fn, backend)`` is
    the single injection point (tests pass a stub that ignores the model)."""
    brief = (brief or "").strip()[:brief_cap]
    models = dict(models or {})
    res = CouncilResult(topic=topic, model=default_model, backend="local")
    if not council:
        res.note = "no council personas configured"
        return res

    _ask_cache: dict[str, AskFn] = {}

    def ask_for(model: str) -> AskFn:
        if model not in _ask_cache:
            _ask_cache[model] = ask_maker(model)[0]
        return _ask_cache[model]

    # Round 1 — 立場 (each persona on its own model)
    for p in council:
        mdl = models.get(p.name, default_model)
        user = (
            f"今日簡報(數據已是 point-in-time):\n{brief}\n\n"
            f"【任務】針對「{topic}」,用你的人格視角給 2-3 句立場。"
            f"先明確選邊:**看多 或 看空**(只有真的毫無方向才用中性),"
            f"再給最關鍵的 1 個理由(扣著上面數據)。態度要鮮明、符合你的人格,"
            f"不要騎牆、不要跟別人一樣。繁體中文,精簡。"
        )
        text, ok = ask_for(mdl)(p.system_prompt, user, 260)
        res.votes.append(Vote(persona=p.name, title=p.title, model=mdl,
                              stance=text if ok else "(模型無回應)"))

    by_name = {v.persona: v for v in res.votes}

    # Round 2 — 質疑 + 投票 (same model per seat)
    for p in council:
        v = by_name[p.name]
        others = "\n".join(f"[{o.title}] {o.stance}" for o in res.votes if o.persona != p.name)
        user = (
            f"今日簡報:\n{brief}\n\n其他分析師的立場:\n{others}\n\n"
            f"【任務】(1) 用一句話**辛辣地反駁**你最不同意的一位(指名道姓,點出他盲點);"
            f"(2) 給最終投票——盡量在 多/空 之間選邊,中性只保留給真的沒有邊際的情況。"
            f"結尾務必『獨立一行』輸出,格式嚴格:\n"
            f"投票: 多/空/中性 | 信心: 1-5 | 動作: <一個具體標的或動作>\n"
            f"繁體中文,精簡。"
        )
        text, ok = ask_for(v.model)(p.system_prompt, user, 300)
        v.rebuttal_vote = text if ok else "(模型無回應)"
        v.vote, v.conviction, v.action = _parse_vote(text)

    res.tally = _tally(res.votes)

    # 主席結論 (chair runs on default_model — usually the strongest 繁中 model)
    chair_sys = (chair.system_prompt if chair else
                 "你是 PolkaSharks 投研議會主席,綜合各analyst意見做結論,只建議不下單。用繁體中文。")
    votes_block = "\n".join(
        f"[{v.title}/{v.model}] 投票={v.vote} 信心={v.conviction} 動作={v.action or '—'}"
        for v in res.votes
    )
    user = (
        f"今日簡報:\n{brief}\n\n議會票數:多={res.tally['多']} 空={res.tally['空']} "
        f"中性={res.tally['中性']} 平均信心={res.tally['avg_conviction']}\n各人最終意見:\n{votes_block}\n\n"
        f"【任務】你是主席,用繁體中文 4-6 句做出今日結論:(1) 綜合票數的整體傾向;"
        f"(2) 點出最大分歧(可點名不同人格/模型);(3) 一句具體可執行的觀察/紀律提醒。"
        f"只建議、不下單,不要捏造數字。"
    )
    conclusion, ok = ask_for(default_model)(chair_sys, user, 460)
    res.conclusion = conclusion if ok else "(主席結論:模型無回應)"
    res.ok = any(v.stance and "無回應" not in v.stance for v in res.votes)
    res.note = "models: " + ", ".join(sorted(set(v.model for v in res.votes)))
    return res


def run_council_local(
    topic: str,
    brief: str,
    *,
    model: str = "qwen2.5:7b",                 # chair + fallback model
    council_names: tuple[str, ...] = DEFAULT_COUNCIL,
    chair_name: str = DEFAULT_CHAIR,
    council_models: tuple[str, ...] = (),      # per-seat models (positional w/ council_names)
    personas: Optional[dict[str, ChatPersona]] = None,
    settings=None,
) -> CouncilResult:
    """Convenience: load personas and run a (multi-model) council locally.

    ``council_models`` assigns a model to each seat positionally (round-robin if
    shorter). Empty → every seat uses ``model`` (single-model council)."""
    personas = personas or load_personas(settings)
    council = [personas[n] for n in council_names if n in personas]
    chair = personas.get(chair_name)
    models: dict[str, str] = {}
    if council_models:
        for i, name in enumerate(council_names):
            models[name] = council_models[i % len(council_models)]
    res = run_council(topic, brief, council=council, chair=chair,
                      models=models, default_model=model)
    if not council:
        res.note = f"none of {council_names} found in roster {sorted(personas)}"
    return res
