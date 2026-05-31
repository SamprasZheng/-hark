"""Tests for the standardized decision checklist.

Pure helpers (arbitration / routing / confidence / tier) are tested directly;
run_checklist is exercised fully OFFLINE with injected data (network=False) so the
gate sequence is validated without any network call. The live FOM step is covered
by the CLI demo, not here (it needs price history); offline it degrades to ``na``.
"""

from __future__ import annotations

import json

import pytest

from sharks.decision.checklist import (
    run_checklist, arbitrate_signals, route_quadrant, aggregate_confidence,
    tier_of, _load_weights, GENUINE_BULL, SENTIMENT_BULL, GENUINE_BEAR, OBSERVE,
)

WEIGHTS = _load_weights()


class TestTierOf:
    def test_mag7_is_tier1(self):
        assert tier_of("NVDA") == 1 and tier_of("aapl") == 1

    def test_supply_chain_is_tier2(self):
        assert tier_of("ASML") == 2 and tier_of("AMD") == 2

    def test_unknown_is_tier3(self):
        assert tier_of("TSEM") == 3 and tier_of("ZZZZ") == 3


class TestArbitrate:
    def test_two_aligned(self):
        a = arbitrate_signals(0.7, 0.6)
        assert a["aligned"] == 2
        assert a["fired"]["fundamental"] and a["fired"]["technical"]
        assert a["technical_only"] is False and a["notes"] == []

    def test_technical_only_flags_30pct_cap(self):
        a = arbitrate_signals(None, 0.6)
        assert a["aligned"] == 1 and a["technical_only"] is True
        assert any("30%" in n for n in a["notes"])

    def test_sentiment_only_never_opens(self):
        a = arbitrate_signals(None, None, None, 0.9)
        assert a["aligned"] == 1
        assert any("sentiment-only" in n for n in a["notes"])

    def test_no_signal(self):
        a = arbitrate_signals(0.1, 0.2)
        assert a["aligned"] == 0


class TestRouteQuadrant:
    def test_genuine_bull(self):
        q = route_quadrant(fundamental_strong=True, technical_ok=True,
                           order_decelerating=False, premium_rich=False,
                           regime_label="neutral")
        assert q["quadrant"] == GENUINE_BULL

    def test_sentiment_bull_on_decel_into_rich(self):
        q = route_quadrant(fundamental_strong=True, technical_ok=True,
                           order_decelerating=True, premium_rich=True,
                           regime_label="bull_trend")
        assert q["quadrant"] == SENTIMENT_BULL

    def test_genuine_bear_on_macro_break(self):
        q = route_quadrant(fundamental_strong=False, technical_ok=False,
                           order_decelerating=True, premium_rich=False,
                           regime_label="risk_off")
        assert q["quadrant"] == GENUINE_BEAR

    def test_observe_when_nothing_fires(self):
        q = route_quadrant(fundamental_strong=False, technical_ok=False,
                           order_decelerating=False, premium_rich=False,
                           regime_label="neutral")
        assert q["quadrant"] == OBSERVE


class TestAggregateConfidence:
    def test_base_ladder(self):
        assert aggregate_confidence(2, WEIGHTS)["confidence"] == pytest.approx(0.55)

    def test_accelerating_bumps_up(self):
        c = aggregate_confidence(2, WEIGHTS, order_trajectory="accelerating")["confidence"]
        assert c == pytest.approx(0.59)

    def test_decelerating_drags_down(self):
        c = aggregate_confidence(2, WEIGHTS, order_trajectory="decelerating")["confidence"]
        assert c == pytest.approx(0.45)

    def test_clamped_to_max(self):
        c = aggregate_confidence(4, WEIGHTS, fom_percentile=0.9, premium_to_fair=-0.3,
                                 order_trajectory="accelerating", cycle_state="EXPANSION")["confidence"]
        assert c == pytest.approx(0.95)  # 0.80+0.05+0.04+0.04+0.04 clamped


class TestRunChecklistOffline:
    REGIME = {"label": "neutral", "reasons": ["test"], "weights": {}}

    def test_hard_exclusion_short_circuits(self):
        r = run_checklist(
            "PENNY", network=False, regime=self.REGIME,
            fundamentals={"ticker": "PENNY", "price": 3.0, "market_cap": 5e8,
                          "sector": "Technology"})
        assert r.action == "exclude"
        gate = next(s for s in r.steps if s["name"] == "exclusion_gate")
        assert gate["status"] == "fail"
        json.dumps(r.to_dict())  # must be serialisable

    def test_full_offline_scorecard_runs(self):
        r = run_checklist(
            "TSEM", network=False, regime=self.REGIME,
            cycle={"state": "EXPANSION"},
            fundamentals={"ticker": "TSEM", "price": 50.0, "market_cap": 6e9,
                          "sector": "Technology", "forward_eps": 3.0, "beta": 1.2,
                          "analyst_upside": 0.2, "earnings_growth_yoy": 0.4,
                          "revenue_growth_yoy": 0.3, "flags": {"turnaround_score": 4}},
            orderbook={"TSEM": {"book_to_bill": 1.5, "key_segment_yoy": 0.5,
                                "key_segment": "SiPho", "moat": 2, "switching": 2,
                                "optionality": 1, "capital_allocation": 1,
                                "concentration_risk": 1}},
            metrics={"ticker": "TSEM", "sector": "Technology", "forward_eps": 3.0,
                     "price": 50.0, "revenue_growth_yoy": 0.3, "gross_margin": 0.5,
                     "operating_margin": 0.3, "roe": 0.2})
        # structure
        assert r.ticker == "TSEM" and r.tier == 3
        assert r.action in {"long_new", "short_new_put", "watch"}
        assert isinstance(r.confidence, float)
        names = [s["name"] for s in r.steps]
        for required in ("exclusion_gate", "regime", "valuation", "order_demand",
                         "signal_arbitration", "quadrant_route", "confidence"):
            assert required in names
        # the curated order book made the demand step fire with accelerating orders
        od = next(s for s in r.steps if s["name"] == "order_demand")
        assert od["evidence"]["order_trajectory"] == "accelerating"
        # offline => FOM degrades to na, never crashes
        fom = next(s for s in r.steps if s["name"] == "fom")
        assert fom["status"] == "na"
        json.dumps(r.to_dict())
