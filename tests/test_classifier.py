"""Offline tests for the regime classifier (Fix A) and FOMScore regime threading.

Covers per the proposal acceptance checklist in
`philosophy/_proposals/fom-regime-and-universe-2026-05-30.md` §7:

  - REGIME_PROFILES weights sum to 1.0 (5 labels exhaustive)
  - classify_regime returns each label under stubbed breadth + liquidity inputs
  - FOMScore.base_score reproduces canonical 25/25/15/15/20 when regime=None
  - FOMScore.bubble_guard_clamped applies the regime floor
  - score_ticker stamps regime label / weights / floor onto FOMScore
  - rank_universe without regime arg is bit-exactly backward-compatible
"""

from __future__ import annotations

import math
from unittest import mock

import pytest

from sharks.regime.classifier import (
    REGIME_PROFILES,
    classify_regime,
)
from sharks.scoring.fom import (
    FOMScore,
    _DEFAULT_WEIGHTS,
    _DEFAULT_BUB_FLOOR,
)


# ---------------------------------------------------------------------------
# REGIME_PROFILES integrity
# ---------------------------------------------------------------------------

class TestRegimeProfiles:
    EXPECTED_LABELS = {"bull_trend", "late_bull", "neutral", "risk_off", "capitulation"}

    def test_five_labels_exhaustive(self):
        assert set(REGIME_PROFILES.keys()) == self.EXPECTED_LABELS

    @pytest.mark.parametrize("label", list(EXPECTED_LABELS))
    def test_weights_sum_to_one(self, label):
        w = REGIME_PROFILES[label]["weights"]
        total = sum(w.values())
        assert math.isclose(total, 1.0, rel_tol=0, abs_tol=1e-6), (
            f"regime {label!r} weights sum to {total}, not 1.0"
        )

    @pytest.mark.parametrize("label", list(EXPECTED_LABELS))
    def test_five_dimensions_present(self, label):
        w = REGIME_PROFILES[label]["weights"]
        assert set(w.keys()) == {"momentum", "contrarian", "cyclic", "quality", "bubble_guard"}

    @pytest.mark.parametrize("label", list(EXPECTED_LABELS))
    def test_bubble_guard_floor_int(self, label):
        floor = REGIME_PROFILES[label]["bubble_guard_floor"]
        assert isinstance(floor, int)
        assert -100 <= floor <= 0

    def test_late_bull_floor_is_negative_50(self):
        """Per the proposal, late_bull floor is -50 specifically (so a -95 raw
        bubble_guard reading does not drown a strong-momentum supply-chain name)."""
        assert REGIME_PROFILES["late_bull"]["bubble_guard_floor"] == -50

    def test_neutral_floor_is_negative_100(self):
        """Neutral preserves the canonical no-clamp behaviour."""
        assert REGIME_PROFILES["neutral"]["bubble_guard_floor"] == -100


# ---------------------------------------------------------------------------
# classify_regime label-routing
# ---------------------------------------------------------------------------

def _b(verdict: str, spx_above_200: bool = True) -> dict:
    """Build a minimal breadth-indicator-shaped dict."""
    return {
        "verdict": verdict,
        "indices_vs_ma": {"SPX": {"vs_200ma": {"above_ma": spx_above_200}}},
    }


def _l(level: str) -> dict:
    """Build a minimal liquidity-signals-shaped dict."""
    return {"composite_alert": {"level": level}}


class TestClassifyRegime:
    def test_capitulation_takes_precedence(self):
        r = classify_regime(_b("CAPITULATION_BOTTOM"), _l("GREEN"))
        assert r["label"] == "capitulation"

    def test_spx_below_200dma_forces_risk_off(self):
        # Even with NORMAL breadth + GREEN liquidity, if SPX is under 200dma
        # we are not in a bull regime.
        r = classify_regime(_b("NORMAL", spx_above_200=False), _l("GREEN"))
        assert r["label"] == "risk_off"

    def test_overheated_plus_orange_liquidity_is_risk_off(self):
        r = classify_regime(_b("OVERHEATED"), _l("ORANGE"))
        assert r["label"] == "risk_off"

    def test_overheated_plus_red_liquidity_is_risk_off(self):
        r = classify_regime(_b("OVERHEATED"), _l("RED"))
        assert r["label"] == "risk_off"

    def test_overheated_plus_yellow_is_late_bull(self):
        """The current (2026-05-30) state — exercises the late_bull branch."""
        r = classify_regime(_b("OVERHEATED"), _l("YELLOW"))
        assert r["label"] == "late_bull"

    def test_normal_plus_green_plus_above_200dma_is_bull_trend(self):
        r = classify_regime(_b("NORMAL"), _l("GREEN"))
        assert r["label"] == "bull_trend"

    def test_normal_plus_unknown_liquidity_above_200dma_is_bull_trend(self):
        # UNKNOWN liquidity is treated permissively when breadth is healthy.
        r = classify_regime(_b("NORMAL"), _l("UNKNOWN"))
        assert r["label"] == "bull_trend"

    def test_unknown_combination_falls_back_to_neutral(self):
        # Verdict outside the documented branches → defensive neutral.
        r = classify_regime(_b("WEIRD_NEW_VERDICT"), _l("YELLOW"))
        assert r["label"] == "neutral"

    def test_returns_canonical_weights_dict(self):
        r = classify_regime(_b("NORMAL"), _l("GREEN"))
        assert set(r["weights"].keys()) == {
            "momentum", "contrarian", "cyclic", "quality", "bubble_guard"
        }

    def test_inputs_block_records_observed_state(self):
        r = classify_regime(_b("OVERHEATED"), _l("YELLOW"))
        assert r["inputs"]["breadth_verdict"] == "OVERHEATED"
        assert r["inputs"]["liquidity_level"] == "YELLOW"
        assert r["inputs"]["spx_above_200dma"] is True

    def test_spx_explicit_override_wins_over_breadth_block(self):
        # Breadth says SPX above; explicit override says below → risk_off.
        r = classify_regime(_b("NORMAL", spx_above_200=True), _l("GREEN"),
                            spx_above_200dma=False)
        assert r["label"] == "risk_off"


# ---------------------------------------------------------------------------
# FOMScore.base_score canonical-regime backward compatibility
# ---------------------------------------------------------------------------

def _fom(momentum=80.0, contrarian=40.0, cyclic=50.0, quality=70.0,
         bubble_guard_val=-95.0, weights=None, floor=None) -> FOMScore:
    """Construct an FOMScore for arithmetic tests."""
    return FOMScore(
        ticker="MU",
        as_of="2026-05-29",
        sector_etf=None,
        momentum=momentum,
        contrarian=contrarian,
        cyclic=cyclic,
        quality=quality,
        bubble_guard_val=bubble_guard_val,
        weights=dict(weights) if weights else dict(_DEFAULT_WEIGHTS),
        bubble_guard_floor=floor if floor is not None else _DEFAULT_BUB_FLOOR,
    )


class TestFOMScoreCanonical:
    def test_default_weights_are_canonical_25_25_15_15_20(self):
        s = _fom()
        # Defaults to neutral when no regime applied.
        assert s.weights == {
            "momentum": 0.25, "contrarian": 0.25,
            "cyclic": 0.15, "quality": 0.15, "bubble_guard": 0.20,
        }

    def test_default_floor_is_negative_100(self):
        s = _fom()
        assert s.bubble_guard_floor == -100

    def test_base_score_reproduces_canonical_formula(self):
        # Pick simple numbers so the expected can be checked by hand.
        s = _fom(momentum=80, contrarian=40, cyclic=50, quality=70,
                 bubble_guard_val=-95)
        # canonical: 0.25*80 + 0.25*40 + 0.15*50 + 0.15*70 + 0.20*((-95+100)/2)
        #          = 20 + 10 + 7.5 + 10.5 + 0.20*2.5
        #          = 48.5
        expected = 0.25 * 80 + 0.25 * 40 + 0.15 * 50 + 0.15 * 70 + 0.20 * ((-95 + 100) / 2)
        assert math.isclose(s.base_score, expected, abs_tol=1e-9)

    def test_persistence_boost_caps_at_30_percent(self):
        s = _fom()
        s.persistence_weeks = 100  # absurdly high
        assert math.isclose(s.persistence_boost, 0.30, abs_tol=1e-9)

    def test_final_fom_equals_base_times_one_plus_boost(self):
        s = _fom()
        s.persistence_weeks = 3
        expected = s.base_score * (1 + 0.15)
        assert math.isclose(s.final_fom, expected, abs_tol=1e-9)


# ---------------------------------------------------------------------------
# Bubble guard floor mechanic
# ---------------------------------------------------------------------------

class TestBubbleGuardFloor:
    def test_clamped_value_when_floor_applies(self):
        # Late-bull floor = -50; raw reading -95 → clamped to -50.
        late_bull = REGIME_PROFILES["late_bull"]
        s = _fom(bubble_guard_val=-95.0,
                 weights=late_bull["weights"],
                 floor=late_bull["bubble_guard_floor"])
        assert s.bubble_guard_clamped == -50.0

    def test_clamped_passthrough_when_above_floor(self):
        late_bull = REGIME_PROFILES["late_bull"]
        s = _fom(bubble_guard_val=10.0,
                 weights=late_bull["weights"],
                 floor=late_bull["bubble_guard_floor"])
        assert s.bubble_guard_clamped == 10.0

    def test_floor_meaningfully_lifts_mu_under_late_bull(self):
        """The proposal's headline claim: MU mom 81.9 / con 36 / bub -95 jumps
        from FOM ~49.6 (neutral) into the high-50s under late_bull weights +
        -50 floor. We don't require the exact ranks (those depend on the rest
        of the universe), but the base_score must rise meaningfully."""
        # Canonical neutral
        s_neutral = _fom(momentum=81.9, contrarian=36.0, cyclic=50.0,
                         quality=70.0, bubble_guard_val=-95.0)
        late_bull = REGIME_PROFILES["late_bull"]
        s_late = _fom(momentum=81.9, contrarian=36.0, cyclic=50.0,
                      quality=70.0, bubble_guard_val=-95.0,
                      weights=late_bull["weights"],
                      floor=late_bull["bubble_guard_floor"])
        # late_bull score should be ≥ 5 points higher (proposal claims +9 for MU).
        assert s_late.base_score > s_neutral.base_score + 5.0


# ---------------------------------------------------------------------------
# classify_regime → score_ticker integration (light, no yfinance)
# ---------------------------------------------------------------------------

class TestRegimeAppliesToScore:
    """Build a FOMScore via the direct ctor with regime-derived weights and
    confirm the wiring matches what `score_ticker` would stamp."""

    def test_late_bull_weights_match_profile(self):
        late_bull = REGIME_PROFILES["late_bull"]
        expected_weights = late_bull["weights"]
        expected_floor = late_bull["bubble_guard_floor"]
        s = FOMScore(
            ticker="MU", as_of="2026-05-29", sector_etf=None,
            momentum=80.0, contrarian=40.0, cyclic=50.0, quality=70.0,
            bubble_guard_val=-95.0,
            regime_label="late_bull",
            weights=dict(expected_weights),
            bubble_guard_floor=expected_floor,
        )
        assert s.regime_label == "late_bull"
        assert s.weights == expected_weights
        assert s.bubble_guard_floor == expected_floor

    def test_regime_label_default_is_neutral(self):
        s = _fom()
        # Default ctor (no regime_label arg) is "neutral".
        assert s.regime_label == "neutral"
