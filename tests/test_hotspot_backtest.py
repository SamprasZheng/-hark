"""Tests for the hotspot sector-rotation prediction backtest."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from sharks.backtest.hotspot_backtest import (
    momentum_signal,
    seasonal_signal,
    blend_signals,
    precision_at_k,
    _forward_sector_returns,
    _zscore,
    run_hotspot_backtest,
)


def _trending_frame(n=80):
    """Sectors S0..S4 with distinct persistent uptrends + a benchmark SPY."""
    idx = pd.date_range("2013-01-31", periods=n, freq="ME")
    data = {}
    for i in range(5):
        rate = 1.0 + 0.004 * i
        data[f"S{i}"] = [100 * rate ** k for k in range(n)]
    data["SPY"] = [100 * 1.005 ** k for k in range(n)]
    return pd.DataFrame(data, index=idx)


class TestZScore:
    def test_centers_and_scales(self):
        z = _zscore({"a": 1, "b": 2, "c": 3})
        assert sum(z.values()) == pytest.approx(0.0, abs=1e-9)

    def test_degenerate_all_equal(self):
        z = _zscore({"a": 5, "b": 5})
        assert all(v == 0.0 for v in z.values())


class TestMomentumSignal:
    def test_higher_trend_higher_rs(self):
        f = _trending_frame()
        as_of = f.index[40]
        sig = momentum_signal(f, as_of, ["S0", "S1", "S4"], lookback=3)
        # S4 trends hardest → highest relative strength vs SPY
        assert sig["S4"] > sig["S0"]


class TestSeasonalSignal:
    def test_pit_only_uses_prior_years(self):
        f = _trending_frame()
        as_of = f.index[60]
        sig = seasonal_signal(f, as_of, ["S2"], horizon=3)
        # persistent uptrend → positive seasonal forward estimate
        assert "S2" in sig and sig["S2"] > 0


class TestBlend:
    def test_blend_common_sectors_only(self):
        mom = {"A": 1.0, "B": 0.5, "C": 0.2}
        sea = {"A": 0.1, "B": 0.3}           # no C
        bl = blend_signals(mom, sea, (0.5, 0.5))
        assert set(bl.keys()) == {"A", "B"}


class TestForwardReturns:
    def test_three_month(self):
        f = _trending_frame()
        fwd = _forward_sector_returns(f, as_of_pos=10, horizon=3, sectors=["S4", "SPY"])
        assert fwd["S4"] > 0

    def test_beyond_end_empty(self):
        f = _trending_frame(n=12)
        assert _forward_sector_returns(f, as_of_pos=11, horizon=3, sectors=["S0"]) == {}


class TestPrecisionAtK:
    def test_perfect_prediction(self):
        signal = {"a": 3, "b": 2, "c": 1, "d": 0}
        actual = {"a": 0.3, "b": 0.2, "c": 0.1, "d": 0.0}
        assert precision_at_k(signal, actual, k=2) == pytest.approx(1.0)

    def test_inverted_prediction(self):
        signal = {"a": 3, "b": 2, "c": 1, "d": 0}
        actual = {"a": 0.0, "b": 0.1, "c": 0.2, "d": 0.3}
        assert precision_at_k(signal, actual, k=2) == pytest.approx(0.0)

    def test_too_few_returns_none(self):
        assert precision_at_k({"a": 1}, {"a": 0.1}, k=2) is None


class TestRunBacktestSynthetic:
    def test_persistent_trends_give_momentum_edge(self):
        f = _trending_frame(n=80)
        out = run_hotspot_backtest(
            f, sectors=["S0", "S1", "S2", "S3", "S4"], horizon=3, k=2,
            backtest_start="2015-01-01",
        )
        assert out["periods_scored"] > 0
        mom = out["by_component"]["momentum"]
        # with deterministic persistent trends, momentum IC should be positive
        assert mom["mean_ic"] is not None and mom["mean_ic"] > 0
        # current prediction names the strongest trenders
        names = [h["sector"] for h in out["current_prediction"]["top_hotspots"]]
        assert "S4" in names
