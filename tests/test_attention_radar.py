"""Tests for the attention-radar pure core (no network)."""

from __future__ import annotations

import numpy as np
import pandas as pd

from sharks.scoring.attention_radar import (
    abnormal_attention,
    acceleration,
    attention_score,
)


def _flat(n=60, level=100.0):
    return pd.Series([level] * n, dtype=float)


def _spike(n=60, level=100.0, sd=5.0, spike=300.0, seed=0):
    # noisy baseline (sd>0 so the z-score is defined) with a spike at the end
    rng = np.random.default_rng(seed)
    s = level + rng.normal(0, sd, n)
    s[-1] = spike
    return pd.Series(s, dtype=float)


class TestAbnormal:
    def test_spike_high_z(self):
        z = abnormal_attention(_spike(), baseline=30)
        assert z is not None and z > 5            # a 3x spike on a flat base is a big z

    def test_flat_is_none_or_zero(self):
        # zero std → undefined z → None (guarded)
        assert abnormal_attention(_flat(), baseline=30) is None

    def test_insufficient_data(self):
        assert abnormal_attention(pd.Series([1.0, 2.0, 3.0]), baseline=30) is None

    def test_no_lookahead(self):
        # the latest point must NOT be in its own baseline → a one-off spike is
        # measured against the calm prior window, not a window containing itself.
        s = _spike(n=40)
        z = abnormal_attention(s, baseline=30)
        # if the latest were included in the baseline the z would be much smaller
        assert z is not None and z > 5


class TestAcceleration:
    def test_rising_positive(self):
        s = pd.Series(np.linspace(100, 200, 40))
        assert acceleration(s) > 0

    def test_falling_negative(self):
        s = pd.Series(np.linspace(200, 100, 40))
        assert acceleration(s) < 0


class TestAttentionScore:
    def test_accelerating_not_extreme_scores(self):
        # steady ramp → accelerating, z moderate (not >3) → positive early score
        s = pd.Series(np.linspace(100, 130, 50))
        out = attention_score(s, baseline=30)
        assert out["early_theme_score"] is not None and out["early_theme_score"] >= 0

    def test_extreme_flagged_crowded(self):
        out = attention_score(_spike(n=60, spike=1000.0), baseline=30)
        assert out["crowded"] is True

    def test_insufficient_returns_none_score(self):
        out = attention_score(pd.Series([1.0, 2.0]), baseline=30)
        assert out["early_theme_score"] is None
