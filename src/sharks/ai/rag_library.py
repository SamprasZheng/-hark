"""RAG example library — write + embed past recommendations into the lake.

Per `philosophy/_proposals/ai-quant-us-roadmap-merge-2026-05-30.md` §5 #11, this
module is the primary "learn from past recommendations" mechanism while the
recommendation lake is small. It REPLACES the original QLoRA fine-tuning loop
(deferred until ≥ 500 PIT-honest pairs are available AND the LLM-in-the-loop
backtest pollution isolation protocol is in place).

Hard rules enforced here (see `data/recommendations_lake/README.md` for full
PIT contract):

  1. ``as_of_timestamp`` is immutable after first write.
  2. The embedding is derived from ``prompt_snapshot`` only — never from the
     ``outcome`` block. This makes retrieval lookahead-safe.
  3. ``update_outcome()`` mutates only the ``outcome`` block; everything else
     stays frozen.

The embedding method (``bow-hash-128-v1``) is a stdlib-only stand-in suitable
for the first several hundred records. Bump the method tag and re-embed in a
one-shot migration when the lake graduates to a real sentence encoder.
"""

from __future__ import annotations

import hashlib
import json
import math
import re
from datetime import datetime
from pathlib import Path
from typing import Any

SCHEMA_VERSION = 1
EMBEDDING_METHOD = "bow-hash-128-v1"
EMBEDDING_DIM = 128

_TOKEN_RE = re.compile(r"[a-z0-9]+")


# ---------------------------------------------------------------------------
# Embedding (stdlib-only stand-in)
# ---------------------------------------------------------------------------
def _tokenize(text: str) -> list[str]:
    """Lowercase whitespace + punctuation split. No external deps."""
    return _TOKEN_RE.findall(text.lower())


def _hash_bucket(token: str) -> int:
    """Stable bucket [0, EMBEDDING_DIM) for a token. Uses SHA-256 so the
    bucket assignment is identical across machines and Python versions."""
    digest = hashlib.sha256(token.encode("utf-8")).digest()
    return int.from_bytes(digest[:4], "big") % EMBEDDING_DIM


def embed(text: str) -> list[float]:
    """Bag-of-words hash-trick embedding, L2-normalised. Returns a list[float]
    of length ``EMBEDDING_DIM``. Deterministic for a given text input."""
    counts = [0.0] * EMBEDDING_DIM
    for tok in _tokenize(text):
        counts[_hash_bucket(tok)] += 1.0
    norm = math.sqrt(sum(c * c for c in counts))
    if norm == 0.0:
        return counts
    return [c / norm for c in counts]


def prompt_text_from_snapshot(snapshot: dict[str, Any]) -> str:
    """Canonicalise a ``prompt_snapshot`` dict into the text the embedder sees.

    The order and content here is the embedding's load-bearing contract: any
    change requires a re-embedding migration (and a bump of ``EMBEDDING_METHOD``)
    or retrieval scores will silently drift.
    """
    parts: list[str] = []
    if snapshot.get("regime_label"):
        parts.append(f"regime {snapshot['regime_label']}")
    if snapshot.get("breadth_verdict"):
        parts.append(f"breadth {snapshot['breadth_verdict']}")
    if snapshot.get("liquidity_level"):
        parts.append(f"liquidity {snapshot['liquidity_level']}")
    for entry in snapshot.get("top_n_fom") or []:
        parts.append(
            f"top {entry.get('ticker','?')} fom {entry.get('fom','?')} "
            f"mom {entry.get('momentum','?')}"
        )
    for cite in snapshot.get("wiki_citations") or []:
        parts.append(f"cite {cite}")
    if snapshot.get("prompt_text"):
        parts.append(snapshot["prompt_text"])
    return " | ".join(parts)


# ---------------------------------------------------------------------------
# File I/O — write / update / read
# ---------------------------------------------------------------------------
def _slot_path(lake_dir: Path, slot_id: str, ticker: str, as_of: str) -> Path:
    """Filename per the lake README: <YYYY-MM-DD>-<slot>-<TICKER>.json.

    The date prefix is derived from ``as_of_timestamp`` (the canonical PIT
    marker), not from the system clock at write time.
    """
    date_part = as_of[:10]
    return lake_dir / f"{date_part}-{slot_id}-{ticker.upper()}.json"


def write_recommendation(
    lake_dir: Path,
    slot_id: str,
    ticker: str,
    as_of_timestamp: str,
    prompt_snapshot: dict[str, Any],
    recommendation: dict[str, Any],
) -> Path:
    """Write a new recommendation record. Idempotent for the same content;
    raises if a record with the same slot_id exists with a different
    ``as_of_timestamp`` (silent backdating would corrupt PIT lookups).
    """
    lake_dir = Path(lake_dir)
    lake_dir.mkdir(parents=True, exist_ok=True)
    path = _slot_path(lake_dir, slot_id, ticker, as_of_timestamp)

    if path.exists():
        existing = json.loads(path.read_text(encoding="utf-8"))
        if existing.get("as_of_timestamp") != as_of_timestamp:
            raise ValueError(
                f"refusing to overwrite {path.name}: existing as_of "
                f"{existing.get('as_of_timestamp')!r} != new "
                f"{as_of_timestamp!r}. Recommendation as_of is immutable."
            )

    embedding_text = prompt_text_from_snapshot(prompt_snapshot)
    vector = embed(embedding_text)

    record: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "slot_id": slot_id,
        "ticker": ticker.upper(),
        "as_of_timestamp": as_of_timestamp,
        "prompt_snapshot": prompt_snapshot,
        "recommendation": recommendation,
        "embedding": {
            "method": EMBEDDING_METHOD,
            "vector": vector,
        },
        "outcome": {
            "return_30d": None,
            "return_60d": None,
            "return_90d": None,
            "populated_at": None,
        },
    }
    path.write_text(json.dumps(record, indent=2, ensure_ascii=False), encoding="utf-8")
    return path


def update_outcome(
    record_path: Path,
    *,
    return_30d: float | None = None,
    return_60d: float | None = None,
    return_90d: float | None = None,
    populated_at: str | None = None,
) -> None:
    """Populate the ``outcome`` block post-hoc. Touches no other field — in
    particular leaves ``embedding`` untouched so retrieval scores cannot drift
    when outcomes arrive."""
    record_path = Path(record_path)
    record = json.loads(record_path.read_text(encoding="utf-8"))
    outcome = record.setdefault("outcome", {})
    if return_30d is not None:
        outcome["return_30d"] = return_30d
    if return_60d is not None:
        outcome["return_60d"] = return_60d
    if return_90d is not None:
        outcome["return_90d"] = return_90d
    outcome["populated_at"] = populated_at or datetime.utcnow().isoformat() + "Z"
    record_path.write_text(json.dumps(record, indent=2, ensure_ascii=False), encoding="utf-8")
