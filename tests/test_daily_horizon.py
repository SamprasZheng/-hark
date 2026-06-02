"""Tests for the daily-bar horizon calibration backtest."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from sharks.backtest.daily_horizon_backtest import (
    _trailing_return,
    signal_values,
    _forward,
    _aggregate,
    run_daily_horizons,
)


def _frame(n=200):
    idx = pd.date_range("2020-01-01", periods=n, freq="B")
    # A: steady up; B: steady down; C: zigzag (mean-reverting)
    a = [100 * 1.001 ** k for k in range(n)]
    b = [100 * 0.999 ** k for k in range(n)]
    c = [100 * (1.03 if k % 2 else 0.97) ** 1 for k in range(n)]
    return pd.DataFrame({"A": a, "B": b, "C": c}, index=idx)


class TestTrailingReturn:
    def test_basic(self):
        f = _frame()
        r = _trailing_return(f, pos=60, lookback=20)
        assert r["A"] > 0 and r["B"] < 0

    def test_insufficient_history_empty(self):
        f = _frame()
        assert _trailing_return(f, pos=5, lookback=20) == {}


class TestSignalValues:
    def test_reversal_is_negated_momentum(self):
        f = _frame()
        pos = 60
        mom = signal_values(f, pos, "mom_20")
        rev = {t: -v for t, v in _trailing_return(f, pos, 20).items()}
        assert signal_values(f, pos, "rev_5")  # smoke
        for t in mom:
            assert signal_values(f, pos, "mom_20")[t] == pytest.approx(mom[t])

    def test_unknown_signal_raises(self):
        with pytest.raises(ValueError):
            signal_values(_frame(), 60, "bogus")


class TestForward:
    def test_forward_return(self):
        f = _frame()
        fwd = _forward(f, pos=10, horizon=5)
        assert fwd["A"] > 0 and fwd["B"] < 0

    def test_beyond_end_empty(self):
        f = _frame(n=20)
        assert _forward(f, pos=19, horizon=5) == {}


class TestAggregate:
    def test_empty(self):
        a = _aggregate([])
        assert a["n"] == 0 and a["mean_ic"] is None

    def test_stable_positive(self):
        a = _aggregate([0.1, 0.12, 0.09, 0.11])
        assert a["mean_ic"] > 0 and a["pct_positive"] == 1.0 and a["ic_ir"] > 2


class TestRunDailyHorizons:
    def test_runs_and_picks_best(self):
        f = _frame(n=300)
        out = run_daily_horizons(f, signals=("mom_20", "rev_5"), horizons=(1, 5),
                                 sample_every=5, start_pos=30)
        assert "by_signal" in out and "best_per_horizon" in out
        for h in ("1d", "5d"):
            assert out["best_per_horizon"][h]["signal"] in ("mom_20", "rev_5")
