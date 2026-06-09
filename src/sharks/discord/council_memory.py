"""Council memory — the closed loop that lets議會結論 feed the LLM-wiki.

Karpathy's LLM-wiki idea is that the system's *compiled state* lives as markdown
the model can read back. A council debate that vanishes after it is posted breaks
that loop. This module closes it:

  記錄 (record)   每次議會結論 → ``wiki/council/<ts>-<topic>.md`` (RAG-searchable,
                 human-readable) **and** an append-only ``_history.jsonl``
                 (structured, cheap to parse). No git auto-commit — the human
                 reviews/commits, same contract as ``wiki_ingest``.
  記憶 (recall)   the next council reads back:
                   • ``memory_brief``   — recent conclusions + top wiki/RAG hits
                     for the topic (so it reasons over **本機 + 已注入(網路)文檔**,
                     not a blank slate → each round is more efficient than scratch).
                   • ``persona_memories`` — each persona's own recent
                     立場/投票 (so every persona *has memory* and can延續 or修正).

Multi-layer closed loop: 結論 → wiki → RAG → 下一場 council 的 memory_brief → 新結論.
The RAG step means web articles you ``/ingest`` into ``wiki/inbox/`` and the
curated ``philosophy/`` 底層邏輯 both flow into the council's context for free.

Pure I/O + parsing — no LLM, no network. Safe to call from anywhere; every write
is best-effort and never raises into the caller.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Optional

from sharks.discord.config import TPE, Settings
from sharks.discord.wiki_ingest import _slug

# Where conclusions land. Under wiki/ so the local RAG (ROOTS includes "wiki")
# indexes them automatically — the conclusion becomes searchable knowledge.
_SUBDIR = ("wiki", "council")
_HISTORY = "_history.jsonl"


# ── write side (結論 → wiki) ───────────────────────────────────────────────────

def _entry(result, topic: str, now: datetime) -> dict:
    """Flatten a CouncilResult into a JSON-safe memory record."""
    return {
        "ts": now.isoformat(),
        "date": now.strftime("%Y-%m-%d"),
        "topic": topic,
        "lean": result.lean(),
        "tally": dict(result.tally or {}),
        "conclusion": (result.conclusion or "").strip(),
        "votes": [
            {
                "persona": v.persona,
                "title": v.title,
                "model": v.model,
                "stance": (v.stance or "").strip(),
                "crossexam": (getattr(v, "crossexam", "") or "").strip(),
                "vote": v.vote,
                "conviction": v.conviction,
                "action": v.action,
            }
            for v in result.votes
        ],
    }


def _render_md(entry: dict) -> str:
    """A human + RAG friendly markdown rendering of one council conclusion."""
    t = entry["tally"] or {}
    head = (
        "---\n"
        "type: council-conclusion\n"
        "tags: [council, 議會, conclusion, memory]\n"
        f"as_of_timestamp: {entry['ts']}\n"
        "author_role: council\n"
        f"topic: {entry['topic']}\n"
        f"lean: {entry['lean']}\n"
        "---\n\n"
        f"# 議會結論 · {entry['date']} · 「{entry['topic']}」\n\n"
        f"**傾向**: {entry['lean']} ｜ 多={t.get('多', 0)} 空={t.get('空', 0)} "
        f"中性={t.get('中性', 0)} 平均信心={t.get('avg_conviction', '?')}/5\n\n"
        f"## 主席結論\n{entry['conclusion'] or '—'}\n\n"
        "## 各人立場與投票\n"
    )
    lines = []
    for v in entry["votes"]:
        lines.append(
            f"- **{v['title']}** (`{v['model']}`) — 投票 {v['vote']}/信心 {v['conviction']}"
            f" · 動作 {v['action'] or '—'}\n"
            f"  - 立場:{v['stance'] or '—'}"
            + (f"\n  - 質詢:{v['crossexam']}" if v.get("crossexam") else "")
        )
    return head + "\n".join(lines) + "\n"


def record(result, settings: Optional[Settings] = None, *,
           topic: Optional[str] = None) -> dict:
    """Persist one council conclusion to the wiki. Returns {ok, path, ...}.

    Writes both a markdown note (RAG + human) and a JSONL memory line. Never
    raises: a memory failure must not break a meeting."""
    try:
        settings = settings or Settings.load()
        if not result or not result.votes:
            return {"ok": False, "error": "empty council result"}
        now = datetime.now(TPE)
        topic = (topic or result.topic or "council").strip() or "council"
        cdir = settings.project_root.joinpath(*_SUBDIR)
        cdir.mkdir(parents=True, exist_ok=True)

        entry = _entry(result, topic, now)
        md_path = cdir / f"{_slug(topic, now)}.md"
        md_path.write_text(_render_md(entry), encoding="utf-8")

        with (cdir / _HISTORY).open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(entry, ensure_ascii=False) + "\n")

        # invalidate the RAG index so the conclusion is searchable immediately
        try:
            from sharks.discord import wiki_rag
            wiki_rag._INDEX_CACHE.clear()
        except Exception:
            pass

        return {
            "ok": True,
            "path": str(md_path.relative_to(settings.project_root)).replace("\\", "/"),
            "topic": topic,
            "lean": entry["lean"],
        }
    except Exception as exc:        # memory is best-effort, never fatal
        return {"ok": False, "error": str(exc)}


# ── read side (wiki → 下一場 council 的記憶) ────────────────────────────────────

def _load_recent(settings: Settings, n: int) -> list[dict]:
    """Newest-first list of the last ``n`` council records from the JSONL log."""
    path = settings.project_root.joinpath(*_SUBDIR) / _HISTORY
    if not path.exists():
        return []
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return []
    out: list[dict] = []
    for raw in reversed(lines):
        raw = raw.strip()
        if not raw:
            continue
        try:
            out.append(json.loads(raw))
        except json.JSONDecodeError:
            continue
        if len(out) >= n:
            break
    return out


def memory_brief(settings: Optional[Settings] = None, topic: str = "", *,
                 n: int = 4, rag_k: int = 3, with_rag: bool = True,
                 cap: int = 1800) -> str:
    """Compact memory block fed into the next council.

    Two parts, both optional: (1) the last ``n`` 議會結論 (so the bench延續/修正
    instead of restarting), and (2) top wiki/RAG hits for ``topic`` (so it reasons
    over 本機 + 已注入(網路) 文檔 — the 底層邏輯 in philosophy/, the articles you
    /ingest). Returns "" when there is nothing to remember."""
    settings = settings or Settings.load()
    parts: list[str] = []

    recent = _load_recent(settings, n)
    if recent:
        rows = []
        for e in recent:
            t = e.get("tally") or {}
            concl = (e.get("conclusion") or "").replace("\n", " ").strip()
            rows.append(
                f"- {e.get('date', '?')} 「{e.get('topic', '?')}」傾向{e.get('lean', '?')}"
                f"(多{t.get('多', 0)}/空{t.get('空', 0)}/中{t.get('中性', 0)}):{concl[:90]}"
            )
        parts.append("【近期議會記憶】(供延續判斷,非定論;若情況已變請明確修正)\n" + "\n".join(rows))

    if with_rag and topic.strip():
        try:
            from sharks.discord import wiki_rag
            hits = wiki_rag.search(topic, settings.project_root, k=rag_k)
            block = wiki_rag.context_block(hits, cap=900) if hits else ""
            if block:
                parts.append("【相關本機/已注入文檔(底層邏輯參考)】\n" + block)
        except Exception:
            pass

    return ("\n\n".join(parts))[:cap]


def persona_memories(settings: Optional[Settings] = None, *,
                     n_entries: int = 8, per: int = 2) -> dict[str, str]:
    """Per-persona memory: {persona_name: "你最近的紀錄…"}.

    Scans the last ``n_entries`` councils and, for each persona, keeps its most
    recent ``per`` 立場/投票 — so every seat remembers what *it* argued and can
    be held to it (延續 or 認錯修正)."""
    settings = settings or Settings.load()
    recent = _load_recent(settings, n_entries)         # newest-first
    seen: dict[str, list[str]] = {}
    for e in recent:
        date = e.get("date", "?")
        topic = e.get("topic", "?")
        for v in e.get("votes", []) or []:
            name = v.get("persona")
            if not name:
                continue
            bucket = seen.setdefault(name, [])
            if len(bucket) >= per:
                continue
            stance = (v.get("stance") or "").replace("\n", " ").strip()
            bucket.append(
                f"{date}「{topic}」你投 {v.get('vote', '?')}/信心{v.get('conviction', '?')}"
                f"({stance[:60]})"
            )
    return {
        name: "你最近的紀錄:" + "；".join(rows) + "。這次請延續或明確修正,別自相矛盾。"
        for name, rows in seen.items() if rows
    }
