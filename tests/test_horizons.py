"""Tests for Fix B — multi-horizon FOM lens (fom_3m / fom_12m / fom_36m)."""

from __future__ import annotations

import math

import pytest

from sharks.scoring.fom import (
    HORIZON_PROFILES,
    FOMScore,
    _DEFAULT_WEIGHTS,
    _DEFAULT_BUB_FLOOR,
)


def _fom(momentum, contrarian, cyclic=50.0, quality=50.0, bubble_guard_val=0.0,
         persistence_weeks=0) -> FOMScore:
    return FOMScore(
        ticker="X", as_of="2026-05-29", sector_etf=None,
        momentum=momentum, contrarian=contrarian, cyclic=cyclic,
        quality=quality, bubble_guard_val=bubble_guard_val,
        persistence_weeks=persistence_weeks,
    )


class TestHorizonProfiles:
    def test_three_horizons(self):
        assert set(HORIZON_PROFILES) == {"3m", "12m", "36m"}

    @pytest.mark.parametrize("h", ["3m", "12m", "36m"])
    def test_weights_sum_to_one(self, h):
        total = sum(HORIZON_PROFILES[h]["weights"].values())
        assert math.isclose(total, 1.0, abs_tol=1e-9)

    def test_3m_is_momentum_heavy(self):
        assert HORIZON_PROFILES["3m"]["weights"]["momentum"] > 0.5

    def test_36m_is_contrarian_plus_quality_heavy(self):
        w = HORIZON_PROFILES["36m"]["weights"]
        assert w["contrarian"] + w["quality"] >= 0.55

    def test_3m_floor_is_minus_50(self):
        assert HORIZON_PROFILES["3m"]["bubble_guard_floor"] == -50


class TestHorizonScores:
    def test_returns_three_keys(self):
        hs = _fom(momentum=70, contrarian=40).horizon_scores
        assert set(hs) == {"fom_3m", "fom_12m", "fom_36m"}

    def test_12m_matches_neutral_base(self):
        # The 12m profile == canonical neutral weights + floor -100, so fom_12m
        # should equal base_score (computed with default neutral weights) when
        # the FOMScore itself carries the default neutral config.
        s = _fom(momentum=80, contrarian=40, cyclic=50, quality=70,
                 bubble_guard_val=-95)
        assert s.weights == dict(_DEFAULT_WEIGHTS)
        assert s.bubble_guard_floor == _DEFAULT_BUB_FLOOR
        assert math.isclose(s.horizon_scores["fom_12m"], round(s.base_score, 2), abs_tol=0.01)

    def test_momentum_name_prefers_short_horizon(self):
        # High momentum, low contrarian → 3m emphasis scores higher than 36m.
        s = _fom(momentum=90, contrarian=20, cyclic=50, quality=30,
                 bubble_guard_val=-40)
        hs = s.horizon_scores
        assert hs["fom_3m"] > hs["fom_36m"]

    def test_value_name_prefers_long_horizon(self):
        # Low momentum, high contrarian + quality → 36m emphasis scores higher.
        s = _fom(momentum=20, contrarian=85, cyclic=50, quality=80,
                 bubble_guard_val=30)
        hs = s.horizon_scores
        assert hs["fom_36m"] > hs["fom_3m"]

    def test_persistence_boost_applied_to_horizons(self):
        base = _fom(momentum=60, contrarian=60, persistence_weeks=0).horizon_scores
        boosted = _fom(momentum=60, contrarian=60, persistence_weeks=4).horizon_scores
        # 4 weeks → +20% boost on every horizon.
        for k in base:
            assert boosted[k] > base[k]

    def test_3m_floor_lifts_high_momentum_bubble_name(self):
        # MU-like: mom 82, bub -95. 3m floor -50 lifts the bubble contribution
        # vs 36m which uses floor -100. Even though 36m weights bubble lower
        # (0.15 vs 0.20), the 3m momentum weight dominates so 3m >> 36m here.
        s = _fom(momentum=82, contrarian=36, cyclic=55, quality=70,
                 bubble_guard_val=-95)
        hs = s.horizon_scores
        assert hs["fom_3m"] > hs["fom_36m"]
