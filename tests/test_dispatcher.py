"""Offline tests for the cloud→local dispatcher. No network."""

from __future__ import annotations

import json
from unittest import mock

import pytest

from sharks.ai import dispatcher as dp
from sharks.ai import nemotron_client as nc


@pytest.fixture
def cache_tmp(tmp_path, monkeypatch):
    monkeypatch.setenv("SHARKS_LLM_CACHE_DIR", str(tmp_path))
    monkeypatch.delenv("SHARKS_LLM_CACHE_ONLY", raising=False)
    yield tmp_path


def _fake_call(content: str, error=None, model="nemotron-3-nano:4b"):
    return nc.NemotronCall(
        model=model, role="executor", reasoning="off",
        latency_ms=42, backend="local", content=content, error=error,
    )


# ---------------------------------------------------------------------------
# Envelope validation
# ---------------------------------------------------------------------------

class TestEnvelope:
    def test_rejects_wrong_version(self, cache_tmp):
        r = dp.dispatch({"v": 2, "type": "thesis", "as_of": "2026-05-29", "payload": {}})
        assert r["ok"] is False and "version" in r["error"]

    def test_rejects_unknown_type(self, cache_tmp):
        r = dp.dispatch({"v": 1, "type": "weather", "as_of": "2026-05-29", "payload": {}})
        assert r["ok"] is False and "unknown task type" in r["error"]

    def test_rejects_missing_as_of(self, cache_tmp):
        r = dp.dispatch({"v": 1, "type": "thesis", "payload": {}})
        assert r["ok"] is False and "as_of" in r["error"]

    def test_rejects_bad_payload(self, cache_tmp):
        r = dp.dispatch({"v": 1, "type": "thesis", "as_of": "2026-05-29", "payload": "not a dict"})
        assert r["ok"] is False and "payload" in r["error"]


# ---------------------------------------------------------------------------
# Cache key stability
# ---------------------------------------------------------------------------

class TestCacheKey:
    def test_same_payload_same_key(self):
        k1 = dp.cache_key("thesis", "m", "d", {"a": 1, "b": 2})
        k2 = dp.cache_key("thesis", "m", "d", {"b": 2, "a": 1})  # different order
        assert k1 == k2

    def test_different_as_of_different_key(self):
        k1 = dp.cache_key("thesis", "m", "2026-05-29", {"a": 1})
        k2 = dp.cache_key("thesis", "m", "2026-05-30", {"a": 1})
        assert k1 != k2

    def test_different_type_different_key(self):
        k1 = dp.cache_key("thesis", "m", "d", {"x": 1})
        k2 = dp.cache_key("news_nlp", "m", "d", {"x": 1})
        assert k1 != k2


# ---------------------------------------------------------------------------
# Thesis dispatch
# ---------------------------------------------------------------------------

class TestThesisDispatch:
    def test_happy_path_caches_and_returns(self, cache_tmp):
        client = mock.MagicMock()
        client.backend = mock.MagicMock(planner_model="planner-m", executor_model="exec-m", name="local")
        client.chat.return_value = _fake_call("This is a thesis.", model="exec-m")
        task = {"v": 1, "type": "thesis", "as_of": "2026-05-29",
                "payload": {"ticker": "NVDA", "report": {"sector": "tech", "verdict": "buy"}}}
        r = dp.dispatch(task, client=client)
        assert r["ok"] is True
        assert r["content"] == "This is a thesis."
        assert r["cache_hit"] is False
        # Cache file exists.
        files = list(cache_tmp.iterdir())
        assert len(files) == 1 and files[0].suffix == ".json"

    def test_second_call_hits_cache_no_chat(self, cache_tmp):
        client = mock.MagicMock()
        client.backend = mock.MagicMock(planner_model="p", executor_model="e", name="local")
        client.chat.return_value = _fake_call("first")
        task = {"v": 1, "type": "thesis", "as_of": "2026-05-29",
                "payload": {"ticker": "DELL", "report": {}}}
        dp.dispatch(task, client=client)
        client.chat.reset_mock()
        r2 = dp.dispatch(task, client=client)
        assert r2["cache_hit"] is True
        assert r2["content"] == "first"
        client.chat.assert_not_called()

    def test_chat_error_not_cached(self, cache_tmp):
        client = mock.MagicMock()
        client.backend = mock.MagicMock(planner_model="p", executor_model="e", name="local")
        client.chat.return_value = _fake_call("", error="transport (local): refused")
        task = {"v": 1, "type": "thesis", "as_of": "2026-05-29",
                "payload": {"ticker": "X", "report": {}}}
        r = dp.dispatch(task, client=client)
        assert r["ok"] is False
        assert r["error"] and "transport" in r["error"]
        # Failures must NOT be cached.
        assert list(cache_tmp.iterdir()) == []


# ---------------------------------------------------------------------------
# News-NLP parse
# ---------------------------------------------------------------------------

class TestNewsNLPDispatch:
    def test_strict_json_parsed(self, cache_tmp):
        client = mock.MagicMock()
        client.backend = mock.MagicMock(planner_model="p", executor_model="e", name="local")
        client.chat.return_value = _fake_call(
            '{"sentiment": "bearish", "confidence": 0.82, "rationale": "downgrade"}',
        )
        task = {"v": 1, "type": "news_nlp", "as_of": "2026-05-29",
                "payload": {"ticker": "NVDA", "headline": "Analyst downgrades NVDA"}}
        r = dp.dispatch(task, client=client)
        assert r["ok"] is True
        assert r["content"]["sentiment"] == "bearish"
        assert r["content"]["confidence"] == 0.82

    def test_prose_with_embedded_json_parsed(self, cache_tmp):
        client = mock.MagicMock()
        client.backend = mock.MagicMock(planner_model="p", executor_model="e", name="local")
        client.chat.return_value = _fake_call(
            'Sure, here is the classification: {"sentiment":"bullish","confidence":0.7,"rationale":"beat"} done.'
        )
        task = {"v": 1, "type": "news_nlp", "as_of": "2026-05-29",
                "payload": {"ticker": "DELL", "headline": "DELL beats earnings"}}
        r = dp.dispatch(task, client=client)
        assert r["ok"] is True
        assert r["content"]["sentiment"] == "bullish"

    def test_unparseable_response_is_error(self, cache_tmp):
        client = mock.MagicMock()
        client.backend = mock.MagicMock(planner_model="p", executor_model="e", name="local")
        client.chat.return_value = _fake_call("not classifiable")
        task = {"v": 1, "type": "news_nlp", "as_of": "2026-05-29",
                "payload": {"ticker": "X", "headline": "?"}}
        r = dp.dispatch(task, client=client)
        assert r["ok"] is False
        assert r["error"] and "non-classifiable" in r["error"]


# ---------------------------------------------------------------------------
# Replay-only mode
# ---------------------------------------------------------------------------

class TestCacheOnlyMode:
    def test_miss_rejected_in_replay_mode(self, cache_tmp, monkeypatch):
        monkeypatch.setenv("SHARKS_LLM_CACHE_ONLY", "1")
        client = mock.MagicMock()
        client.backend = mock.MagicMock(planner_model="p", executor_model="e", name="local")
        task = {"v": 1, "type": "thesis", "as_of": "2026-05-29",
                "payload": {"ticker": "X", "report": {}}}
        r = dp.dispatch(task, client=client)
        assert r["ok"] is False
        assert r["error"] and "replay" in r["error"]
        client.chat.assert_not_called()  # crucially no network in replay mode

    def test_hit_works_in_replay_mode(self, cache_tmp, monkeypatch):
        # Warm the cache first (replay OFF).
        client = mock.MagicMock()
        client.backend = mock.MagicMock(planner_model="p", executor_model="e", name="local")
        client.chat.return_value = _fake_call("warm content")
        task = {"v": 1, "type": "thesis", "as_of": "2026-05-29",
                "payload": {"ticker": "Y", "report": {}}}
        dp.dispatch(task, client=client)
        # Now flip to replay-only and re-dispatch.
        monkeypatch.setenv("SHARKS_LLM_CACHE_ONLY", "1")
        client.chat.reset_mock()
        r = dp.dispatch(task, client=client)
        assert r["ok"] is True
        assert r["cache_hit"] is True
        client.chat.assert_not_called()
