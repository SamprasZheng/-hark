"""Tests for the Bayesian bottleneck posterior lens (pure logic)."""

from __future__ import annotations

import math

from sharks.scoring.bayesian_update import (
    edge_vs_market,
    milestone_logodds_update,
    posterior_for_ticker,
    prior_from_rubric,
    prior_from_verdict,
)

HIGH = {"A1": 2, "A2": 2, "A3": 2, "A4": 2, "A5": 2}
LOW = {"A1": 1, "A2": 0, "A3": 1, "A4": 0, "A5": 0}


class TestPrior:
    def test_zhibian_high_rubric_beats_taizao_low(self):
        assert prior_from_rubric(HIGH, "質變") > prior_from_rubric(LOW, "太早")

    def test_clamped(self):
        p = prior_from_rubric(HIGH, "質變", confidence=1.0)
        assert 0.05 <= p <= 0.95

    def test_confidence_blend(self):
        # blending with a low confidence should pull the prior down
        hi = prior_from_rubric(HIGH, "質變")
        blended = prior_from_rubric(HIGH, "質變", confidence=0.2)
        assert blended < hi

    def test_verdict_ordering(self):
        c = 0.5
        ps = {v: prior_from_verdict(v, c) for v in ("質變", "結構", "過熱", "太早", "受損")}
        assert ps["質變"] > ps["結構"] > ps["過熱"] > ps["太早"] > ps["受損"]


class TestMilestoneUpdate:
    def test_positive_evidence_raises(self):
        u = milestone_logodds_update(0.5, [{"status": "✅", "lr": 3}, {"status": "✅", "lr": 3}])
        assert u["posterior"] > 0.5

    def test_falsifier_lowers(self):
        u = milestone_logodds_update(0.5, [{"status": "❌", "lr": 3}])
        assert u["posterior"] < 0.5

    def test_pending_is_neutral(self):
        u = milestone_logodds_update(0.6, [{"status": "⏳"}, {"status": "⏳"}])
        assert math.isclose(u["posterior"], 0.6, abs_tol=1e-6)
        assert u["n_evidence"] == 0

    def test_shrinkage_sublinear(self):
        # 6 ✅ should NOT move the posterior 6× as far as 1 ✅ (shrinkage damps)
        one = milestone_logodds_update(0.5, [{"status": "✅", "lr": 3}])
        six = milestone_logodds_update(0.5, [{"status": "✅", "lr": 3}] * 6)
        d1 = one["log_odds_delta"]
        d6 = six["log_odds_delta"]
        assert d6 > d1                      # more evidence still moves further
        assert d6 < 6 * d1                  # but sub-linearly (shrinkage)

    def test_clamped(self):
        u = milestone_logodds_update(0.9, [{"status": "✅", "lr": 50}] * 10)
        assert u["posterior"] <= 0.95


class TestEdge:
    def test_froth_kills_edge(self):
        # high posterior but frothy (bubble_guard −95) ⇒ market already believes ⇒ edge small
        e = edge_vs_market(0.85, bubble_guard=-95)
        assert e["market_implied"] > 0.85
        assert e["edge"] < 0 and e["actionable"] is False

    def test_healthy_gives_edge(self):
        e = edge_vs_market(0.80, bubble_guard=15)
        assert e["market_implied"] < 0.80
        assert e["edge"] > 0.10 and e["actionable"] is True

    def test_none_bubble_guard(self):
        e = edge_vs_market(0.7, bubble_guard=None)
        assert e["edge"] is None and e["actionable"] is None


class TestPosteriorForTicker:
    def test_uncovered_none(self):
        assert posterior_for_ticker("ZZZZ") is None

    def test_lly_high_posterior(self):
        # LLY = 質變, milestone_score 0.55 → prior + positive evidence → high posterior
        r = posterior_for_ticker("LLY", bubble_guard=0)
        assert r["posterior"] > r["prior"]
        assert r["verdict"] == "質變"

    def test_ionq_low(self):
        # IONQ = 太早 → low prior
        r = posterior_for_ticker("IONQ", bubble_guard=None)
        assert r["prior"] < 0.5
        assert r["observe_first"] is True
