"""RAG retrieval — query the recommendation lake at decision time.

Pairs with `rag_library.py`. Two hard guarantees:

  1. **PIT honesty**: ``retrieve(..., before_as_of=T)`` only returns records
     whose ``as_of_timestamp`` is `<=` T. A backtest at simulated time T sees
     only what was visible at T; later recommendations cannot leak.
  2. **Embedding-version locking**: records whose ``embedding.method`` does not
     match the library's current ``EMBEDDING_METHOD`` are skipped (with a count
     returned alongside the results) so a mid-migration partial re-embed never
     silently mixes incompatible vector spaces.

The retrieval interface is intentionally identical to what a sentence-encoder-
backed implementation would expose, so swapping the embedder later does not
ripple into call sites.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

from .rag_library import (
    EMBEDDING_METHOD,
    embed,
    prompt_text_from_snapshot,
)


def _cosine(a: list[float], b: list[float]) -> float:
    """Cosine similarity over two equal-length float lists. Returns 0.0 for
    zero-norm inputs."""
    if len(a) != len(b):
        raise ValueError(f"vector length mismatch: {len(a)} vs {len(b)}")
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    if na == 0.0 or nb == 0.0:
        return 0.0
    return dot / (na * nb)


def load_all(
    lake_dir: Path,
    before_as_of: str | None = None,
) -> list[dict[str, Any]]:
    """Load every record in the lake whose ``as_of_timestamp`` is `<=`
    ``before_as_of`` (lexicographic comparison works because timestamps are
    ISO-8601). If ``before_as_of`` is None, returns all records.
    """
    lake_dir = Path(lake_dir)
    if not lake_dir.is_dir():
        return []
    out: list[dict[str, Any]] = []
    for path in sorted(lake_dir.glob("*.json")):
        try:
            record = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        as_of = record.get("as_of_timestamp")
        if before_as_of is not None and (as_of is None or as_of > before_as_of):
            continue
        record["_path"] = str(path)
        out.append(record)
    return out


def retrieve(
    lake_dir: Path,
    current_prompt_snapshot: dict[str, Any],
    k: int = 5,
    before_as_of: str | None = None,
) -> dict[str, Any]:
    """Return the k records most similar to the current prompt snapshot.

    Result shape:

        {
          "query_text": "...",
          "k": int,
          "before_as_of": str | None,
          "embedding_method": str,                  # what we used to query
          "records_scanned": int,
          "records_skipped_wrong_method": int,
          "results": [
            {"score": 0.83, "path": "...", "record": {...}},
            ...
          ],
        }
    """
    lake_dir = Path(lake_dir)
    query_text = prompt_text_from_snapshot(current_prompt_snapshot)
    query_vec = embed(query_text)

    records_scanned = 0
    skipped_wrong_method = 0
    scored: list[tuple[float, str, dict[str, Any]]] = []

    for record in load_all(lake_dir, before_as_of=before_as_of):
        records_scanned += 1
        emb_block = record.get("embedding") or {}
        if emb_block.get("method") != EMBEDDING_METHOD:
            skipped_wrong_method += 1
            continue
        vector = emb_block.get("vector")
        if not isinstance(vector, list):
            continue
        try:
            score = _cosine(query_vec, vector)
        except ValueError:
            continue
        scored.append((score, record["_path"], record))

    scored.sort(key=lambda triple: triple[0], reverse=True)

    return {
        "query_text": query_text,
        "k": k,
        "before_as_of": before_as_of,
        "embedding_method": EMBEDDING_METHOD,
        "records_scanned": records_scanned,
        "records_skipped_wrong_method": skipped_wrong_method,
        "results": [
            {"score": score, "path": path, "record": record}
            for score, path, record in scored[:k]
        ],
    }
