"""Cloud → Local task dispatcher.

This is the seam where cloud Claude hands work to local Nemotron. Cloud Claude
emits versioned JSON envelopes:

    {
      "v": 1,
      "type": "thesis" | "news_nlp",
      "as_of": "YYYY-MM-DD",
      "payload": {...}
    }

The dispatcher:

  1. Validates the envelope (rejects unknown ``v`` or ``type``).
  2. Computes a SHA-256 cache key over the canonical task content (sorted JSON,
     model tag, ``as_of``). Cache hit → return instantly with ``cache_hit=True``;
     cache miss → call Nemotron, persist the result, return.
  3. Serialises calls behind a ``max_concurrent=1`` semaphore — Ollama runs one
     request at a time on a single GPU; firing 10 in parallel just queues them
     and burns context.
  4. Honours ``SHARKS_LLM_CACHE_ONLY=1`` — backtests must be deterministic,
     so replay mode refuses any miss with a structured error.

Each call returns a plain dict (not a dataclass) so cloud Claude can serialise
the result back without a custom encoder:

    {
      "ok": bool,
      "content": str | dict,         # str for thesis, dict for news_nlp
      "model": str,
      "backend": "local" | "nim" | "disabled",
      "latency_ms": int,
      "cache_hit": bool,
      "error": Optional[str],
    }

Adding a new task type = add a handler to ``_HANDLERS`` + register in
``_VALID_TYPES``. Nothing else.
"""

from __future__ import annotations

import hashlib
import json
import os
import threading
import time
from pathlib import Path
from typing import Any, Callable, Optional

from sharks.ai.nemotron_client import NemotronClient

# ---------------------------------------------------------------------------
# Envelope contract
# ---------------------------------------------------------------------------

ENVELOPE_VERSION = 1
_VALID_TYPES = ("thesis", "news_nlp")

# Single-shot serialisation: Ollama processes one request at a time on one GPU.
_GPU_LOCK = threading.Semaphore(1)


def _cache_dir() -> Path:
    return Path(os.environ.get("SHARKS_LLM_CACHE_DIR", "outputs/llm-cache"))


def _cache_only() -> bool:
    return os.environ.get("SHARKS_LLM_CACHE_ONLY") == "1"


def _canonical_json(obj: Any) -> str:
    """Stable JSON for hashing. Sorted keys + compact separators + UTF-8."""
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def cache_key(task_type: str, model: str, as_of: str, payload: dict) -> str:
    """SHA-256 over the canonical (type, model, as_of, payload) tuple."""
    blob = f"{task_type}|{model}|{as_of}|{_canonical_json(payload)}"
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


def _validate(task: dict) -> Optional[str]:
    """Return None if valid, else an error string."""
    if not isinstance(task, dict):
        return "task must be a dict"
    if task.get("v") != ENVELOPE_VERSION:
        return f"unsupported envelope version: {task.get('v')!r} (expected {ENVELOPE_VERSION})"
    if task.get("type") not in _VALID_TYPES:
        return f"unknown task type: {task.get('type')!r} (allowed: {_VALID_TYPES})"
    if not task.get("as_of"):
        return "missing as_of"
    if not isinstance(task.get("payload"), dict):
        return "payload must be a dict"
    return None


def _load_cache(key: str) -> Optional[dict]:
    path = _cache_dir() / f"{key}.json"
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def _save_cache(key: str, result: dict) -> None:
    cdir = _cache_dir()
    cdir.mkdir(parents=True, exist_ok=True)
    (cdir / f"{key}.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def _result(
    *, ok: bool, content: Any, model: str, backend: str,
    latency_ms: int, cache_hit: bool = False, error: Optional[str] = None,
) -> dict:
    return {
        "ok": ok, "content": content, "model": model, "backend": backend,
        "latency_ms": latency_ms, "cache_hit": cache_hit, "error": error,
    }


# ---------------------------------------------------------------------------
# Handlers
# ---------------------------------------------------------------------------

_THESIS_SYSTEM = (
    "You are an AndySharks analyst. Generate a concise 100-150 word thesis "
    "for the ticker, mentioning the entry rationale, key risk, and exit "
    "condition. Be sharp, data-driven; do not hedge."
)

_NEWS_NLP_SYSTEM = (
    "You classify a single financial news headline into one of three labels: "
    'bullish, bearish, neutral. Respond ONLY with strict JSON of the form '
    '{"sentiment": "bullish|bearish|neutral", "confidence": 0.0-1.0, '
    '"rationale": "<one sentence>"}. No prose, no markdown.'
)


def _handle_thesis(client: NemotronClient, payload: dict) -> tuple[Any, str, int, str, Optional[str]]:
    """Return (content, model, latency_ms, backend, error)."""
    ticker = payload.get("ticker", "?")
    report = payload.get("report") or {}
    user = (
        f"Ticker: {ticker}\n"
        f"Sector: {report.get('sector', '?')}\n"
        f"Verdict: {report.get('verdict', '?')}\n"
        f"Evidence (top 5): {report.get('evidence', [])[:5]}\n"
        f"Risks (top 5): {report.get('risks', [])[:5]}\n\n"
        f"Write the thesis."
    )
    call = client.chat(
        "executor",
        [{"role": "system", "content": _THESIS_SYSTEM},
         {"role": "user", "content": user}],
        reasoning="off", temperature=0.3, max_tokens=400,
    )
    return call.content, call.model, call.latency_ms, call.backend, call.error


def _handle_news_nlp(client: NemotronClient, payload: dict) -> tuple[Any, str, int, str, Optional[str]]:
    headline = payload.get("headline", "")
    summary = payload.get("summary", "")
    user = (
        f"Headline: {headline}\n"
        + (f"Summary: {summary}\n" if summary else "")
        + 'Classify and respond with strict JSON only.'
    )
    call = client.chat(
        "executor",
        [{"role": "system", "content": _NEWS_NLP_SYSTEM},
         {"role": "user", "content": user}],
        reasoning="off", temperature=0.1, max_tokens=200,
    )
    if call.error:
        return None, call.model, call.latency_ms, call.backend, call.error
    # Best-effort JSON extraction from the model output.
    parsed = _parse_classification(call.content)
    if parsed is None:
        return None, call.model, call.latency_ms, call.backend, "non-classifiable response"
    return parsed, call.model, call.latency_ms, call.backend, None


def _parse_classification(text: str) -> Optional[dict]:
    """Tolerant JSON extraction — strict-JSON prompt sometimes gets prose."""
    text = (text or "").strip()
    if not text:
        return None
    # Find the first {...} block.
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        return None
    try:
        obj = json.loads(text[start:end + 1])
    except json.JSONDecodeError:
        return None
    sentiment = (obj.get("sentiment") or "").lower()
    if sentiment not in ("bullish", "bearish", "neutral"):
        return None
    try:
        confidence = float(obj.get("confidence", 0))
    except (TypeError, ValueError):
        confidence = 0.0
    return {
        "sentiment": sentiment,
        "confidence": max(0.0, min(1.0, confidence)),
        "rationale": str(obj.get("rationale", ""))[:300],
    }


_HANDLERS: dict[str, Callable[[NemotronClient, dict], tuple]] = {
    "thesis": _handle_thesis,
    "news_nlp": _handle_news_nlp,
}


# ---------------------------------------------------------------------------
# Dispatch entry point
# ---------------------------------------------------------------------------

def dispatch(task: dict, *, client: Optional[NemotronClient] = None) -> dict:
    """Validate, cache-check, optionally call Nemotron, persist, return."""
    err = _validate(task)
    if err is not None:
        return _result(
            ok=False, content=None, model="", backend="invalid",
            latency_ms=0, error=err,
        )

    # Resolve which model the call will use (for cache key stability).
    cli = client or NemotronClient()
    task_type = task["type"]
    role = "executor"  # both current types use executor
    model = (cli.backend.planner_model if role == "planner"
             else cli.backend.executor_model)
    key = cache_key(task_type, model, task["as_of"], task["payload"])

    cached = _load_cache(key)
    if cached is not None:
        cached["cache_hit"] = True
        return cached

    if _cache_only():
        return _result(
            ok=False, content=None, model=model, backend=cli.backend.name,
            latency_ms=0,
            error="cache miss with SHARKS_LLM_CACHE_ONLY=1 (replay mode)",
        )

    handler = _HANDLERS[task_type]
    started = time.perf_counter()
    with _GPU_LOCK:
        content, model_used, call_latency, backend, call_err = handler(cli, task["payload"])
    total_latency = int((time.perf_counter() - started) * 1000)

    result = _result(
        ok=(call_err is None and content is not None),
        content=content,
        model=model_used or model,
        backend=backend,
        latency_ms=call_latency or total_latency,
        error=call_err,
    )
    # Persist successes only — failures shouldn't poison the cache.
    if result["ok"]:
        _save_cache(key, result)
    return result
