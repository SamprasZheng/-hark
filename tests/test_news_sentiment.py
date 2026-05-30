"""Offline tests for the news-sentiment scorer.

Mocks the dispatcher so no network calls happen. Validates the 利空不跌 flag
logic, aggregate counts, graceful empty-input behaviour.
"""

from __future__ import annotations

from unittest import mock

import pytest

from sharks.scoring import news_sentiment as ns


def _mk(sentiment: str, confidence: float = 0.8, cache_hit: bool = False):
    """Build a fake dispatcher result for one headline."""
    return {
        "ok": True,
        "content": {"sentiment": sentiment, "confidence": confidence,
                    "rationale": f"{sentiment} headline"},
        "model": "nemotron-3-nano:4b",
        "backend": "local",
        "latency_ms": 50,
        "cache_hit": cache_hit,
        "error": None,
    }


def _err(msg: str = "unparseable"):
    return {
        "ok": False, "content": None, "model": "m", "backend": "local",
        "latency_ms": 10, "cache_hit": False, "error": msg,
    }


HEADLINES = [
    {"headline": "Analyst downgrades NVDA on margin pressure", "summary": ""},
    {"headline": "NVDA faces export controls in EU", "summary": ""},
    {"headline": "NVDA Q1 beat consensus", "summary": ""},
]


# ---------------------------------------------------------------------------
# classify_headlines aggregation
# ---------------------------------------------------------------------------

class TestClassifyAggregation:
    def test_counts_and_score(self, monkeypatch):
        def fake_dispatch(task, *, client=None):
            text = task["payload"]["headline"]
            if "beat" in text:
                return _mk("bullish", 0.9)
            return _mk("bearish", 0.85)
        monkeypatch.setattr(ns.dp, "dispatch", fake_dispatch)
        out = ns.classify_headlines("NVDA", HEADLINES, "2026-05-29")
        assert out["counts"]["bearish"] == 2
        assert out["counts"]["bullish"] == 1
        assert out["counts"]["neutral"] == 0
        assert -1.0 <= out["score"] <= 1.0
        assert out["score"] < 0  # bearish-leaning

    def test_low_confidence_does_not_count(self, monkeypatch):
        def fake_dispatch(task, *, client=None):
            return _mk("bearish", 0.30)   # below 0.50 floor
        monkeypatch.setattr(ns.dp, "dispatch", fake_dispatch)
        out = ns.classify_headlines("X", HEADLINES, "2026-05-29")
        assert out["counts"]["bearish"] == 0   # ignored
        # but score still reflects confidence-weighted signal
        assert out["score"] < 0

    def test_dispatcher_error_counted(self, monkeypatch):
        def fake_dispatch(task, *, client=None):
            return _err("transport (local): refused")
        monkeypatch.setattr(ns.dp, "dispatch", fake_dispatch)
        out = ns.classify_headlines("X", HEADLINES, "2026-05-29")
        assert out["errors"] == len(HEADLINES)
        assert out["counts"]["bearish"] == 0

    def test_empty_headlines(self, monkeypatch):
        out = ns.classify_headlines("X", [], "2026-05-29")
        assert out["count"] == 0
        assert out["counts"] == {"bullish": 0, "bearish": 0, "neutral": 0}
        assert out["score"] == 0.0

    def test_skips_empty_headline_text(self, monkeypatch):
        calls = []

        def fake_dispatch(task, *, client=None):
            calls.append(task)
            return _mk("bullish")
        monkeypatch.setattr(ns.dp, "dispatch", fake_dispatch)
        ns.classify_headlines("X", [{"headline": ""}, {"headline": "   "}], "2026-05-29")
        assert calls == []  # no dispatch fired for blank text


# ---------------------------------------------------------------------------
# bearish_no_price_follow flag — the 利空不跌 detector
# ---------------------------------------------------------------------------

class TestBearishNoPriceFollow:
    def _patch(self, monkeypatch, *, headlines, dispatcher_results, price_delta):
        results_iter = iter(dispatcher_results)
        monkeypatch.setattr(ns, "fetch_headlines", lambda *a, **k: headlines)
        monkeypatch.setattr(ns.dp, "dispatch", lambda *a, **k: next(results_iter))
        monkeypatch.setattr(ns, "compute_price_delta_pct", lambda *a, **k: price_delta)

    def test_flag_fires_when_two_bearish_and_price_holds(self, monkeypatch):
        self._patch(
            monkeypatch,
            headlines=HEADLINES,
            dispatcher_results=[_mk("bearish"), _mk("bearish"), _mk("neutral")],
            price_delta=+0.2,
        )
        r = ns.analyse("NVDA", "2026-05-29")
        assert r["bearish_no_price_follow"] is True
        assert r["price_held"] is True
        assert r["counts"]["bearish"] == 2

    def test_flag_does_not_fire_when_only_one_bearish(self, monkeypatch):
        self._patch(
            monkeypatch,
            headlines=HEADLINES,
            dispatcher_results=[_mk("bearish"), _mk("bullish"), _mk("neutral")],
            price_delta=+0.5,
        )
        r = ns.analyse("NVDA", "2026-05-29")
        assert r["bearish_no_price_follow"] is False

    def test_flag_does_not_fire_when_price_drops_meaningfully(self, monkeypatch):
        self._patch(
            monkeypatch,
            headlines=HEADLINES,
            dispatcher_results=[_mk("bearish"), _mk("bearish"), _mk("neutral")],
            price_delta=-2.5,   # price followed through bearishly
        )
        r = ns.analyse("NVDA", "2026-05-29")
        assert r["bearish_no_price_follow"] is False

    def test_flag_does_not_fire_when_price_data_missing(self, monkeypatch):
        self._patch(
            monkeypatch,
            headlines=HEADLINES,
            dispatcher_results=[_mk("bearish"), _mk("bearish"), _mk("neutral")],
            price_delta=None,
        )
        r = ns.analyse("NVDA", "2026-05-29")
        assert r["bearish_no_price_follow"] is False
        assert r["price_held"] is False


# ---------------------------------------------------------------------------
# write_jsonl roundtrip + status
# ---------------------------------------------------------------------------

class TestPersistence:
    def test_writes_one_row_per_ticker(self, tmp_path, monkeypatch):
        monkeypatch.setattr(ns, "fetch_headlines", lambda *a, **k: [])
        monkeypatch.setattr(ns, "compute_price_delta_pct", lambda *a, **k: None)
        rows = ns.run(["AAA", "BBB"], "2026-05-29")
        path = ns.write_jsonl(tmp_path, "2026-05-29", rows)
        assert path.exists()
        lines = path.read_text(encoding="utf-8").splitlines()
        assert len(lines) == 2
        import json as _json
        parsed = [_json.loads(l) for l in lines]
        assert {r["ticker"] for r in parsed} == {"AAA", "BBB"}
        # no data at all → status no_data, no errors
        assert all(r["status"] == "no_data" for r in parsed)
