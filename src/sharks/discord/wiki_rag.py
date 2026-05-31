"""Local RAG over the $hark markdown knowledge base — the "LLM-wiki" backend.

Pure-stdlib retrieval (no embeddings server, no cloud) + synthesis on the LOCAL
Ollama model. This is the "use my LLM-wiki via the local GPU, without Claude"
path the principal asked for.

Retrieval is keyword/CJK-bigram overlap rather than the repo's bow-hash embedder
(`rag_library.embed`), because that embedder tokenises ASCII only and would drop
Chinese queries entirely. Substring counting handles mixed 中英文 content, which
is what the wiki actually is.

The index (markdown chunks) is built once and cached per project root.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

# Knowledge roots, in rough priority order. (NOT .venv/.git/node_modules — we
# only rglob under these named dirs + the top-level *.md, so junk never enters.)
ROOTS = ("philosophy", "wiki", "analysts", "tech", "crypto", "docs",
         "raw", "backtest", "trading", "news")

_ASCII = re.compile(r"[a-zA-Z0-9]{2,}")
_CJK = re.compile(r"[一-鿿]+")

_INDEX_CACHE: dict[str, list[tuple[str, str]]] = {}


def _terms(q: str) -> list[str]:
    """Query → search terms: ASCII words + CJK bigrams (so Chinese matches)."""
    terms = {m.group(0).lower() for m in _ASCII.finditer(q)}
    for run in _CJK.findall(q):
        if len(run) <= 2:
            terms.add(run)
        else:
            terms.update(run[i:i + 2] for i in range(len(run) - 1))
    return [t for t in terms if t]


def _chunk(text: str, size: int = 800) -> list[str]:
    out, buf = [], ""
    for para in text.split("\n\n"):
        if buf and len(buf) + len(para) > size:
            out.append(buf.strip())
            buf = para
        else:
            buf = f"{buf}\n\n{para}" if buf else para
    if buf.strip():
        out.append(buf.strip())
    return out


def build_index(project_root: Path) -> list[tuple[str, str]]:
    """Return [(relative_path, chunk_text)] over markdown in ROOTS + top-level *.md
    (so root constitution files like sharks.md/buffet.md are searchable too)."""
    idx: list[tuple[str, str]] = []
    paths: list[Path] = list(project_root.glob("*.md"))            # top-level files
    for root in ROOTS:
        d = project_root / root
        if d.is_dir():
            paths.extend(sorted(d.rglob("*.md")))
    for p in paths:
        try:
            text = p.read_text(encoding="utf-8")
        except OSError:
            continue
        rel = str(p.relative_to(project_root)).replace("\\", "/")
        for ch in _chunk(text):
            if len(ch) >= 40:
                idx.append((rel, ch))
    return idx


def _index(project_root: Path) -> list[tuple[str, str]]:
    key = str(project_root)
    if key not in _INDEX_CACHE:
        _INDEX_CACHE[key] = build_index(project_root)
    return _INDEX_CACHE[key]


@dataclass
class Hit:
    score: int
    path: str
    text: str


def search(question: str, project_root: Path, k: int = 5,
           index: Optional[list[tuple[str, str]]] = None) -> list[Hit]:
    terms = _terms(question)
    if not terms:
        return []
    idx = index if index is not None else _index(project_root)
    scored: list[Hit] = []
    for rel, ch in idx:
        low = ch.lower()
        score = sum(low.count(t) for t in terms)
        if score > 0:
            scored.append(Hit(score, rel, ch))
    scored.sort(key=lambda h: h.score, reverse=True)
    return scored[:k]


def context_block(hits: list[Hit], cap: int = 2600) -> str:
    """Format hits into a context block for the local model, capped."""
    parts, total = [], 0
    for h in hits:
        snippet = h.text[:700]
        block = f"# 來源:{h.path}\n{snippet}"
        if total + len(block) > cap:
            break
        parts.append(block)
        total += len(block)
    return "\n\n---\n\n".join(parts)
