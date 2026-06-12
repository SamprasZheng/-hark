"""Local transcript + response cache for the Discord brain.

Stores every bot LLM call + response to a GITIGNORED append-only jsonl
(``data/transcripts/discord-<date>.jsonl``) so the principal can:
  * cross-check answers over time,
  * CUT paid ``/ask`` calls by serving a fresh cached answer to a repeated question,
  * search past Q&A,
  * later feed a LOCAL small model (Ollama) richer, grounded context.

observe-only; pure file IO; best-effort — every function swallows its own errors
so logging/caching can NEVER break the live bot. Zero new deps (stdlib only).
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

TRANSCRIPT_DIR = Path("data/transcripts")
CACHE_PATH = TRANSCRIPT_DIR / "_ask_cache.jsonl"
# Market context shifts intraday — a few hours is a safe reuse window for an
# identical research question; longer would risk serving stale macro reads.
DEFAULT_CACHE_TTL_S = 6 * 3600


def _now() -> datetime:
    return datetime.now(timezone.utc)


def make_key(kind: str, text: str) -> str:
    """Stable, case-insensitive key for a (kind, prompt) pair."""
    norm = " ".join((text or "").strip().lower().split())
    return hashlib.sha256(f"{kind}\x00{norm}".encode("utf-8")).hexdigest()[:16]


def log_interaction(*, kind: str, prompt: str, response: str, backend: str = "",
                    model: str = "", cost_usd: Optional[float] = None, latency_ms: int = 0,
                    ok: bool = True, channel: str = "", author: str = "",
                    cache_hit: bool = False, transcript_dir: Path = TRANSCRIPT_DIR
                    ) -> Optional[Path]:
    """Append one interaction to ``data/transcripts/discord-<date>.jsonl``.
    Returns the path written, or None on any failure (best-effort)."""
    try:
        d = Path(transcript_dir)
        d.mkdir(parents=True, exist_ok=True)
        rec = {
            "ts": _now().isoformat(), "kind": kind, "channel": channel, "author": author,
            "prompt": prompt, "response": response, "backend": backend, "model": model,
            "cost_usd": cost_usd, "latency_ms": latency_ms, "ok": ok,
            "cache_hit": cache_hit, "key": make_key(kind, prompt),
        }
        path = d / f"discord-{_now().strftime('%Y-%m-%d')}.jsonl"
        with path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
        return path
    except Exception:
        return None


def get_cached(kind: str, text: str, *, max_age_s: int = DEFAULT_CACHE_TTL_S,
               cache_path: Path = CACHE_PATH) -> Optional[dict]:
    """Most recent cached response for (kind, text) that is younger than
    ``max_age_s``, else None. Best-effort (returns None on any error)."""
    try:
        p = Path(cache_path)
        if not p.exists():
            return None
        key = make_key(kind, text)
        best = None
        for line in p.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            if rec.get("key") == key:
                best = rec  # last write for this key wins
        if not best:
            return None
        age = (_now() - datetime.fromisoformat(best["ts"])).total_seconds()
        if age > max_age_s:
            return None
        best["_age_s"] = int(age)
        return best
    except Exception:
        return None


def put_cached(kind: str, text: str, *, response: str, backend: str = "", model: str = "",
               cost_usd: Optional[float] = None, cache_path: Path = CACHE_PATH) -> None:
    """Append a cache entry for (kind, text). Best-effort (never raises)."""
    try:
        p = Path(cache_path)
        p.parent.mkdir(parents=True, exist_ok=True)
        rec = {"ts": _now().isoformat(), "key": make_key(kind, text), "kind": kind,
               "prompt": text, "response": response, "backend": backend, "model": model,
               "cost_usd": cost_usd}
        with p.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
    except Exception:
        pass


def search(query: str, *, kind: Optional[str] = None, limit: int = 20,
           transcript_dir: Path = TRANSCRIPT_DIR) -> list[dict]:
    """Substring search over stored transcripts (newest first) — the 'future-search'
    + local-model-context retrieval entry point. Best-effort."""
    out: list[dict] = []
    try:
        d = Path(transcript_dir)
        if not d.exists():
            return []
        q = (query or "").lower()
        for f in sorted(d.glob("discord-*.jsonl"), reverse=True):
            for line in reversed(f.read_text(encoding="utf-8").splitlines()):
                if not line.strip():
                    continue
                try:
                    rec = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if kind and rec.get("kind") != kind:
                    continue
                if q in (rec.get("prompt", "") + " " + rec.get("response", "")).lower():
                    out.append(rec)
                    if len(out) >= limit:
                        return out
    except Exception:
        return out
    return out
