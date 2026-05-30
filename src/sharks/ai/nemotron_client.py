"""Sharks-side Nemotron client — stdlib port of the proven yxz pattern.

Mirrors ``D:\\DOT\\yxz\\agents\\src\\firefly\\llm\\nemotron.py`` (the ``NemotronClient``
+ ``_inject_reasoning_prefix`` design) but re-implemented on top of
``urllib.request`` so $hark stays dep-free (``pyproject.toml`` declares
``dependencies = []``).

Default transport: local Ollama at ``127.0.0.1:11434/v1`` (OpenAI-compatible
chat completions). Two opt-outs:

  * ``SHARKS_NEMOTRON_BACKEND=nim`` + ``NVIDIA_API_KEY`` → cloud NIM (same SKUs).
  * ``SHARKS_NEMOTRON_BACKEND=disabled`` → every call returns ``NemotronCall``
    with ``error`` populated, no network touched. Used by tests / CI / replay-
    only backtests.

Reasoning control: Nemotron family responds to a ``detailed thinking on/off``
prefix on the first system message. We inject it transparently so callers don't
need to know the convention — see ``_inject_reasoning_prefix`` (near-direct
copy from the yxz module, kept identical so the two repos stay diff-able).

The client **never raises** — every error path returns a ``NemotronCall`` with
``error`` set, so the dispatcher / scorers can branch on it and degrade
gracefully. This matches the existing ``maybe_generate_thesis`` pattern in
``evidence_card.py:215``.
"""

from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Optional

# ---------------------------------------------------------------------------
# Transport defaults
# ---------------------------------------------------------------------------

LOCAL_OLLAMA_BASE_URL = "http://127.0.0.1:11434/v1"
CLOUD_NIM_BASE_URL = "https://integrate.api.nvidia.com/v1"

# Local model SKUs (Ollama tags). Validated under NemoClaw on RTX 5070 (12 GB
# VRAM); see D:\DOT\yxz\scripts\nemoclaw-e2e-test.sh.
LOCAL_PLANNER_MODEL = os.environ.get("SHARKS_NEMOTRON_PLANNER", "nemotron-3-nano:4b")
LOCAL_EXECUTOR_MODEL = os.environ.get("SHARKS_NEMOTRON_EXECUTOR", "nemotron-3-nano:4b")

# Cloud NIM SKUs — only used when SHARKS_NEMOTRON_BACKEND=nim.
CLOUD_PLANNER_MODEL = os.environ.get(
    "SHARKS_NEMOTRON_CLOUD_PLANNER", "nvidia/llama-3.3-nemotron-super-49b-v1.5"
)
CLOUD_EXECUTOR_MODEL = os.environ.get(
    "SHARKS_NEMOTRON_CLOUD_EXECUTOR", "nvidia/nemotron-nano-9b-v2"
)

REASONING_ON_SYSTEM_PREFIX = "detailed thinking on\n\n"
REASONING_OFF_SYSTEM_PREFIX = "detailed thinking off\n\n"


# ---------------------------------------------------------------------------
# Telemetry + backend descriptor
# ---------------------------------------------------------------------------

@dataclass
class NemotronCall:
    """Captured request/response. Returned on every call (even failures)."""

    model: str
    role: str            # "planner" | "executor"
    reasoning: str       # "on" | "off"
    latency_ms: int
    backend: str = "local"
    prompt_tokens: Optional[int] = None
    completion_tokens: Optional[int] = None
    content: str = ""
    error: Optional[str] = None


@dataclass
class Backend:
    """Resolved transport — base URL + auth + which model SKUs to use."""

    name: str
    base_url: str
    api_key: str
    planner_model: str
    executor_model: str

    def auth_header(self) -> dict[str, str]:
        # Ollama accepts and ignores any bearer; NIM requires the real key.
        return {"Authorization": f"Bearer {self.api_key or 'local'}"}


def resolve_backend() -> Backend:
    """Pick transport based on env. Defaults to LOCAL Ollama."""
    explicit = (os.environ.get("SHARKS_NEMOTRON_BACKEND") or "").strip().lower()
    nvidia_key = os.environ.get("NVIDIA_API_KEY", "").strip()
    override_url = (os.environ.get("SHARKS_NEMOTRON_BASE_URL") or "").strip()

    if explicit == "disabled":
        return Backend(
            name="disabled", base_url="", api_key="",
            planner_model=LOCAL_PLANNER_MODEL,
            executor_model=LOCAL_EXECUTOR_MODEL,
        )

    if explicit == "nim" or (not explicit and nvidia_key and not override_url):
        return Backend(
            name="nim",
            base_url=override_url or CLOUD_NIM_BASE_URL,
            api_key=nvidia_key,
            planner_model=CLOUD_PLANNER_MODEL,
            executor_model=CLOUD_EXECUTOR_MODEL,
        )

    return Backend(
        name="local" if not override_url else "onprem",
        base_url=override_url or LOCAL_OLLAMA_BASE_URL,
        api_key=nvidia_key,  # may be empty; Ollama ignores
        planner_model=LOCAL_PLANNER_MODEL,
        executor_model=LOCAL_EXECUTOR_MODEL,
    )


def _inject_reasoning_prefix(
    messages: list[dict], prefix: str
) -> list[dict]:
    """Prepend the Nemotron reasoning-control prefix to the first system message.

    Mirrors yxz/agents/src/firefly/llm/nemotron.py:232–256 verbatim so both
    repos behave identically.
    """
    if not messages:
        return [{"role": "system", "content": prefix.strip()}]
    out: list[dict] = []
    injected = False
    for m in messages:
        if not injected and m.get("role") == "system":
            new_content = prefix + (m.get("content") or "")
            out.append({**m, "content": new_content})
            injected = True
        else:
            out.append(m)
    if not injected:
        out.insert(0, {"role": "system", "content": prefix.strip()})
    return out


# ---------------------------------------------------------------------------
# Client
# ---------------------------------------------------------------------------

class NemotronClient:
    """Thin stdlib wrapper around an OpenAI-compatible chat completions endpoint."""

    def __init__(self, backend: Optional[Backend] = None, timeout_s: float = 180.0):
        self.backend = backend or resolve_backend()
        self.timeout_s = timeout_s

    @property
    def available(self) -> bool:
        """True if a reachable transport is configured. Local/onprem assume
        reachable; the first call will fail loudly with a transport error if not."""
        if self.backend.name == "disabled":
            return False
        if self.backend.name == "nim":
            return bool(self.backend.api_key)
        return True

    def chat(
        self,
        role: str,
        messages: list[dict],
        *,
        reasoning: str = "off",
        temperature: float = 0.2,
        max_tokens: int = 1024,
        model: Optional[str] = None,
    ) -> NemotronCall:
        """Issue one chat completion. ``role`` ∈ {planner, executor}.

        Never raises — error states are reflected in the returned ``NemotronCall``.
        """
        if model is None:
            model = (
                self.backend.planner_model if role == "planner"
                else self.backend.executor_model
            )
        prefix = REASONING_ON_SYSTEM_PREFIX if reasoning == "on" else REASONING_OFF_SYSTEM_PREFIX
        prepared = _inject_reasoning_prefix(messages, prefix)

        call = NemotronCall(
            model=model, role=role, reasoning=reasoning,
            latency_ms=0, backend=self.backend.name,
        )

        if self.backend.name == "disabled":
            call.error = "backend disabled (SHARKS_NEMOTRON_BACKEND=disabled)"
            return call

        body = {
            "model": model,
            "messages": prepared,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": False,
        }
        headers = {
            **self.backend.auth_header(),
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        data = json.dumps(body).encode("utf-8")
        url = f"{self.backend.base_url}/chat/completions"

        started = time.perf_counter()
        try:
            req = urllib.request.Request(url, data=data, headers=headers, method="POST")
            with urllib.request.urlopen(req, timeout=self.timeout_s) as resp:
                raw = resp.read().decode("utf-8")
                status = resp.status
        except urllib.error.HTTPError as exc:
            call.latency_ms = int((time.perf_counter() - started) * 1000)
            try:
                body_text = exc.read().decode("utf-8", errors="replace")[:300]
            except Exception:
                body_text = ""
            call.error = f"http {exc.code} ({self.backend.name}): {body_text}"
            return call
        except urllib.error.URLError as exc:
            call.latency_ms = int((time.perf_counter() - started) * 1000)
            call.error = f"transport ({self.backend.name}): {exc.reason}"
            return call
        except Exception as exc:  # defensive: any unexpected error → NemotronCall
            call.latency_ms = int((time.perf_counter() - started) * 1000)
            call.error = f"unexpected ({self.backend.name}): {exc}"
            return call

        call.latency_ms = int((time.perf_counter() - started) * 1000)
        if status >= 400:
            call.error = f"http {status} ({self.backend.name}): {raw[:300]}"
            return call

        try:
            payload = json.loads(raw)
        except json.JSONDecodeError as exc:
            call.error = f"non-json response: {exc}"
            return call

        choice = (payload.get("choices") or [{}])[0]
        msg = choice.get("message") or {}
        call.content = msg.get("content") or ""
        usage = payload.get("usage") or {}
        call.prompt_tokens = usage.get("prompt_tokens")
        call.completion_tokens = usage.get("completion_tokens")
        return call
