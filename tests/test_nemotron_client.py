"""Offline tests for the stdlib Nemotron client. No network calls.

Mocks ``urllib.request.urlopen`` so the same suite runs in CI without Ollama.
"""

from __future__ import annotations

import io
import json
import urllib.error
from unittest import mock

import pytest

from sharks.ai import nemotron_client as nc


# ---------------------------------------------------------------------------
# Backend resolution
# ---------------------------------------------------------------------------

class TestResolveBackend:
    def test_default_is_local_ollama(self, monkeypatch):
        for v in ("SHARKS_NEMOTRON_BACKEND", "SHARKS_NEMOTRON_BASE_URL", "NVIDIA_API_KEY"):
            monkeypatch.delenv(v, raising=False)
        b = nc.resolve_backend()
        assert b.name == "local"
        assert b.base_url == nc.LOCAL_OLLAMA_BASE_URL

    def test_disabled_short_circuits(self, monkeypatch):
        monkeypatch.setenv("SHARKS_NEMOTRON_BACKEND", "disabled")
        b = nc.resolve_backend()
        assert b.name == "disabled"
        assert b.base_url == ""

    def test_nim_requires_explicit_or_key(self, monkeypatch):
        monkeypatch.delenv("SHARKS_NEMOTRON_BACKEND", raising=False)
        monkeypatch.delenv("SHARKS_NEMOTRON_BASE_URL", raising=False)
        monkeypatch.setenv("NVIDIA_API_KEY", "fake-key")
        b = nc.resolve_backend()
        assert b.name == "nim"
        assert b.base_url == nc.CLOUD_NIM_BASE_URL

    def test_base_url_override_keeps_local_models(self, monkeypatch):
        monkeypatch.delenv("SHARKS_NEMOTRON_BACKEND", raising=False)
        monkeypatch.setenv("SHARKS_NEMOTRON_BASE_URL", "http://onprem.local:8000/v1")
        monkeypatch.delenv("NVIDIA_API_KEY", raising=False)
        b = nc.resolve_backend()
        assert b.name == "onprem"
        assert b.base_url == "http://onprem.local:8000/v1"


# ---------------------------------------------------------------------------
# Reasoning prefix injection
# ---------------------------------------------------------------------------

class TestReasoningPrefix:
    def test_prepends_to_existing_system(self):
        msgs = [{"role": "system", "content": "you are X"}, {"role": "user", "content": "hi"}]
        out = nc._inject_reasoning_prefix(msgs, nc.REASONING_ON_SYSTEM_PREFIX)
        assert out[0]["content"].startswith("detailed thinking on")
        assert "you are X" in out[0]["content"]
        assert out[1]["content"] == "hi"

    def test_inserts_system_when_absent(self):
        msgs = [{"role": "user", "content": "hi"}]
        out = nc._inject_reasoning_prefix(msgs, nc.REASONING_OFF_SYSTEM_PREFIX)
        assert out[0]["role"] == "system"
        assert "detailed thinking off" in out[0]["content"]
        assert out[1]["content"] == "hi"

    def test_empty_messages_yields_lone_system(self):
        out = nc._inject_reasoning_prefix([], nc.REASONING_ON_SYSTEM_PREFIX)
        assert len(out) == 1 and out[0]["role"] == "system"


# ---------------------------------------------------------------------------
# Client.chat — error paths return NemotronCall, never raise
# ---------------------------------------------------------------------------

def _fake_response(payload: dict, status: int = 200):
    """Build a fake urlopen context manager returning the given JSON."""
    body = json.dumps(payload).encode("utf-8")
    fp = io.BytesIO(body)

    class _Ctx:
        def __enter__(self_inner):
            return self_inner
        def __exit__(self_inner, *args):
            return False
        def read(self_inner):
            return fp.getvalue()
        @property
        def status(self_inner):
            return status
    return _Ctx()


class TestClientChat:
    def _client_local(self, monkeypatch):
        for v in ("SHARKS_NEMOTRON_BACKEND", "SHARKS_NEMOTRON_BASE_URL", "NVIDIA_API_KEY"):
            monkeypatch.delenv(v, raising=False)
        return nc.NemotronClient()

    def test_disabled_short_circuits_no_network(self, monkeypatch):
        monkeypatch.setenv("SHARKS_NEMOTRON_BACKEND", "disabled")
        client = nc.NemotronClient()
        # If a network call were attempted, mocking nothing would raise URLError.
        # We assert no exception and error contains "disabled".
        call = client.chat("executor", [{"role": "user", "content": "hi"}])
        assert call.backend == "disabled"
        assert call.content == ""
        assert call.error and "disabled" in call.error

    def test_happy_path_returns_content(self, monkeypatch):
        client = self._client_local(monkeypatch)
        payload = {
            "choices": [{"message": {"role": "assistant", "content": "hello"}}],
            "usage": {"prompt_tokens": 5, "completion_tokens": 1},
        }
        with mock.patch("urllib.request.urlopen", return_value=_fake_response(payload)):
            call = client.chat("executor", [{"role": "user", "content": "ping"}])
        assert call.error is None
        assert call.content == "hello"
        assert call.prompt_tokens == 5
        assert call.completion_tokens == 1
        assert call.model == nc.LOCAL_EXECUTOR_MODEL

    def test_planner_role_picks_planner_model(self, monkeypatch):
        client = self._client_local(monkeypatch)
        payload = {"choices": [{"message": {"content": "ok"}}]}
        with mock.patch("urllib.request.urlopen", return_value=_fake_response(payload)):
            call = client.chat("planner", [{"role": "user", "content": "x"}], reasoning="on")
        assert call.model == nc.LOCAL_PLANNER_MODEL
        assert call.reasoning == "on"

    def test_http_error_becomes_call_error(self, monkeypatch):
        client = self._client_local(monkeypatch)
        err = urllib.error.HTTPError(
            url="http://x", code=500, msg="srv err", hdrs=None,  # type: ignore[arg-type]
            fp=io.BytesIO(b"internal error"),
        )
        with mock.patch("urllib.request.urlopen", side_effect=err):
            call = client.chat("executor", [{"role": "user", "content": "x"}])
        assert call.content == ""
        assert call.error and "http 500" in call.error

    def test_transport_error_becomes_call_error(self, monkeypatch):
        client = self._client_local(monkeypatch)
        with mock.patch("urllib.request.urlopen", side_effect=urllib.error.URLError("conn refused")):
            call = client.chat("executor", [{"role": "user", "content": "x"}])
        assert call.content == ""
        assert call.error and "transport" in call.error

    def test_non_json_response_becomes_call_error(self, monkeypatch):
        client = self._client_local(monkeypatch)

        class _Bad:
            status = 200
            def read(self_inner): return b"not json {{"
            def __enter__(self_inner): return self_inner
            def __exit__(self_inner, *a): return False
        with mock.patch("urllib.request.urlopen", return_value=_Bad()):
            call = client.chat("executor", [{"role": "user", "content": "x"}])
        assert call.error and "non-json" in call.error
