"""Tests for the 飆股獵手 moonshot hunter — the deliberate inverse of FOM.

Covers the price-computable scorers (volume surge, hype/parabola), the
qualitative evidence gate (only A/B counts), the moonshot blend + the
pure-hype-no-evidence warning, ranking, and leveraged-ETF tagging.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from sharks.scoring.moonshot_hunter import (
    EVIDENCE_KINDS,
    HOT_THRESHOLD,
    evidence_score,
    hype_score,
    moonshot_score,
    rank_moonshots,
    volume_surge_score,
)

AS_OF = pd.Timestamp("2026-05-31")


def _idx(n):
    return pd.date_range(end=AS_OF, periods=n, freq="D")


def _flat_volume(n=80, level=1_000_000):
    return pd.Series([level] * n, index=_idx(n))


def _surging_volume(n=80, base=1_000_000, mult=8.0, recent=5):
    vals = [base] * (n - recent) + [base * mult] * recent
    return pd.Series(vals, index=_idx(n))


def _flat_closes(n=40, level=100.0):
    return pd.Series([level] * n, index=_idx(n))


def _parabolic_closes(n=40, start=10.0):
    # Calm for most of the window, then a vertical ramp (the 飆股 parabola):
    # last leg compounds hard so r6 > 2.0 and recent vol expands.
    vals = [start + 0.02 * i for i in range(n - 7)]
    last = vals[-1]
    for step in [1.15, 1.20, 1.25, 1.30, 1.35, 1.40, 1.45]:
        last = last * step
        vals.append(last)
    return pd.Series(vals, index=_idx(n))


# ─── volume_surge_score ───
class TestVolumeSurge:
    def test_flat_volume_low_score(self):
        assert volume_surge_score(_flat_volume(), AS_OF) < 5.0

    def test_surge_high_score(self):
        s = volume_surge_score(_surging_volume(mult=8.0), AS_OF)
        assert s > 60.0

    def test_bigger_surge_scores_higher(self):
        small = volume_surge_score(_surging_volume(mult=2.0), AS_OF)
        big = volume_surge_score(_surging_volume(mult=10.0), AS_OF)
        assert big > small

    def test_too_little_data_is_zero(self):
        assert volume_surge_score(_flat_volume(n=4), AS_OF) == 0.0

    def test_score_bounded_0_100(self):
        s = volume_surge_score(_surging_volume(mult=1000.0), AS_OF)
        assert 0.0 <= s <= 100.0


# ─── hype_score (inverse of bubble_guard) ───
class TestHype:
    def test_parabola_high_score(self):
        assert hype_score(_parabolic_closes(), AS_OF) > 60.0

    def test_flat_low_score(self):
        assert hype_score(_flat_closes(), AS_OF) < 15.0

    def test_inverse_of_bubble_guard_stance(self):
        # FOM's bubble_guard PUNISHES a parabola; moonshot hype REWARDS it.
        # So the same vertical series must score HIGH here (the documented inversion).
        para = _parabolic_closes()
        assert hype_score(para, AS_OF) >= 60.0

    def test_score_bounded_0_100(self):
        s = hype_score(_parabolic_closes(start=1.0), AS_OF)
        assert 0.0 <= s <= 100.0


# ─── evidence_score (only A/B counts) ───
class TestEvidence:
    def test_no_evidence_zero(self):
        out = evidence_score(None)
        assert out["n_confirmed"] == 0
        assert out["evidence_points"] == 0.0

    def test_a_grade_insider_counts(self):
        ev = {"insider_buying": {"confirmed": True, "grade": "A", "note": "Form 4 cluster buy"}}
        out = evidence_score(ev)
        assert out["n_confirmed"] == 1
        assert "insider_buying" in out["confirmed_kinds"]
        assert out["evidence_points"] == 60.0

    def test_rumour_d_grade_does_not_count(self):
        ev = {"bigtech_partnership": {"confirmed": True, "grade": "D", "note": "twitter rumour"}}
        out = evidence_score(ev)
        assert out["n_confirmed"] == 0
        assert out["confirmed_kinds"] == []

    def test_confirmed_flag_without_ab_grade_rejected(self):
        # confirmed=True but grade C → the grade is the backstop, still rejected.
        ev = {"supply_chain_design_win": {"confirmed": True, "grade": "C"}}
        assert evidence_score(ev)["n_confirmed"] == 0

    def test_two_confirmed_kinds_stack(self):
        ev = {
            "insider_buying": {"confirmed": True, "grade": "A"},
            "bigtech_partnership": {"confirmed": True, "grade": "B"},
        }
        out = evidence_score(ev)
        assert out["n_confirmed"] == 2
        assert out["evidence_points"] == 85.0

    def test_unknown_kind_ignored(self):
        ev = {"some_made_up_kind": {"confirmed": True, "grade": "A"}}
        assert evidence_score(ev)["n_confirmed"] == 0

    def test_evidence_kinds_constant(self):
        assert EVIDENCE_KINDS == {
            "insider_buying", "bigtech_partnership", "supply_chain_design_win"
        }


# ─── moonshot_score + the pure-hype warning ───
class TestMoonshotScore:
    def test_pure_hype_no_evidence_flag_fires(self):
        out = moonshot_score(
            _parabolic_closes(), _surging_volume(mult=8.0), AS_OF,
            evidence=None, ticker="HYPE",
        )
        assert out["price_heat"] >= HOT_THRESHOLD
        assert out["conviction"] == "PURE-HYPE-NO-EVIDENCE"
        assert out["pure_hype_warning"] is True
        assert "graveyard" in out["note"].lower()

    def test_evidence_backed_moonshot_tier(self):
        ev = {
            "insider_buying": {"confirmed": True, "grade": "A", "note": "cluster buy"},
            "bigtech_partnership": {"confirmed": True, "grade": "A", "note": "NVDA deal"},
        }
        out = moonshot_score(
            _parabolic_closes(), _surging_volume(mult=8.0), AS_OF,
            evidence=ev, ticker="REAL",
        )
        assert out["conviction"] == "EVIDENCE-BACKED-MOONSHOT"
        assert out["pure_hype_warning"] is False
        assert out["n_confirmed_evidence"] == 2

    def test_a_grade_insider_plus_partnership_lifts_score(self):
        ev = {
            "insider_buying": {"confirmed": True, "grade": "A"},
            "bigtech_partnership": {"confirmed": True, "grade": "A"},
        }
        with_ev = moonshot_score(_parabolic_closes(), _surging_volume(), AS_OF, evidence=ev, ticker="X")
        without = moonshot_score(_parabolic_closes(), _surging_volume(), AS_OF, evidence=None, ticker="X")
        assert with_ev["moonshot_score"] > without["moonshot_score"]

    def test_avoid_tier_low_everything(self):
        out = moonshot_score(_flat_closes(), _flat_volume(), AS_OF, evidence=None, ticker="DEAD")
        assert out["conviction"] == "AVOID"
        assert out["pure_hype_warning"] is False

    def test_watch_tier_evidence_but_cold_price(self):
        # Confirmed catalyst but flat price → WATCH, not a moonshot yet.
        ev = {"supply_chain_design_win": {"confirmed": True, "grade": "B"}}
        out = moonshot_score(_flat_closes(), _flat_volume(), AS_OF, evidence=ev, ticker="EARLY")
        assert out["conviction"] == "WATCH"

    def test_score_bounded_0_100(self):
        out = moonshot_score(_parabolic_closes(), _surging_volume(mult=50.0), AS_OF,
                             evidence={"insider_buying": {"confirmed": True, "grade": "A"}},
                             ticker="MAX")
        assert 0.0 <= out["moonshot_score"] <= 100.0


# ─── rank_moonshots + leveraged-ETF tagging ───
class TestRankAndTagging:
    def _universe(self):
        closes = pd.DataFrame({
            "PARA": _parabolic_closes(),
            "FLAT": _flat_closes(),
            "TSLL": _parabolic_closes(start=5.0),  # leveraged long ETF in registry
        })
        volumes = pd.DataFrame({
            "PARA": _surging_volume(mult=8.0),
            "FLAT": _flat_volume(),
            "TSLL": _surging_volume(mult=8.0),
        })
        return closes, volumes

    def test_ranking_orders_by_score(self):
        closes, volumes = self._universe()
        ranked = rank_moonshots(closes, volumes, AS_OF)
        scores = [r["moonshot_score"] for r in ranked]
        assert scores == sorted(scores, reverse=True)
        # The flat name must rank last.
        assert ranked[-1]["ticker"] == "FLAT"

    def test_leveraged_etf_tagged(self):
        closes, volumes = self._universe()
        ranked = rank_moonshots(closes, volumes, AS_OF)
        by_t = {r["ticker"]: r for r in ranked}
        assert by_t["TSLL"]["instrument"] == "leveraged_etf"
        assert by_t["PARA"]["instrument"] == "equity"

    def test_evidence_by_ticker_routed(self):
        closes, volumes = self._universe()
        ev_by_t = {"PARA": {"insider_buying": {"confirmed": True, "grade": "A"}}}
        ranked = rank_moonshots(closes, volumes, AS_OF, evidence_by_ticker=ev_by_t)
        by_t = {r["ticker"]: r for r in ranked}
        assert by_t["PARA"]["conviction"] == "EVIDENCE-BACKED-MOONSHOT"
        # No evidence routed to TSLL → pure-hype warning fires on its parabola.
        assert by_t["TSLL"]["conviction"] == "PURE-HYPE-NO-EVIDENCE"
