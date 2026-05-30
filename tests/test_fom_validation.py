"""Tests for the FOM predictive-validity (Information Coefficient) primitives."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from sharks.backtest.fom_validation_backtest import (
    spearman_ic,
    quantile_spread,
    hit_rate,
    _forward_returns,
    _aggregate,
    run_validation,
)


class TestSpearmanIC:
    def test_perfect_monotonic_is_one(self):
        scores = {f"T{i}": i for i in range(10)}
        fwd = {f"T{i}": i * 0.01 for i in range(10)}
        assert spearman_ic(scores, fwd) == pytest.approx(1.0)

    def test_perfect_inverse_is_minus_one(self):
        scores = {f"T{i}": i for i in range(10)}
        fwd = {f"T{i}": -i * 0.01 for i in range(10)}
        assert spearman_ic(scores, fwd) == pytest.approx(-1.0)

    def test_too_few_returns_none(self):
        assert spearman_ic({"A": 1, "B": 2}, {"A": 0.1, "B": 0.2}) is None

    def test_nan_forward_skipped(self):
        scores = {f"T{i}": i for i in range(6)}
        fwd = {f"T{i}": i * 0.01 for i in range(5)}
        fwd["T5"] = np.nan
        # 5 valid pairs, still monotonic
        assert spearman_ic(scores, fwd) == pytest.approx(1.0)


class TestQuantileSpread:
    def test_positive_when_high_score_high_return(self):
        scores = {f"T{i}": i for i in range(10)}
        fwd = {f"T{i}": i * 0.02 for i in range(10)}
        sp = quantile_spread(scores, fwd, n_q=5)
        assert sp is not None and sp > 0

    def test_negative_when_inverted(self):
        scores = {f"T{i}": i for i in range(10)}
        fwd = {f"T{i}": -i * 0.02 for i in range(10)}
        assert quantile_spread(scores, fwd, n_q=5) < 0


class TestHitRate:
    def test_top_quantile_all_beat_median(self):
        scores = {f"T{i}": i for i in range(10)}
        fwd = {f"T{i}": i * 0.01 for i in range(10)}
        # top 20% (T8,T9) clearly beat median
        assert hit_rate(scores, fwd, top_frac=0.2) == pytest.approx(1.0)

    def test_inverted_top_quantile_misses(self):
        scores = {f"T{i}": i for i in range(10)}
        fwd = {f"T{i}": -i * 0.01 for i in range(10)}
        assert hit_rate(scores, fwd, top_frac=0.2) == pytest.approx(0.0)


class TestForwardReturns:
    def _frame(self):
        idx = pd.date_range("2020-01-31", periods=6, freq="ME")
        return pd.DataFrame({"A": [10, 11, 12, 13, 14, 15],
                             "B": [100, 90, 80, 70, 60, 50]}, index=idx)

    def test_one_month_forward(self):
        f = _forward_returns(self._frame(), as_of_pos=0, horizon=1)
        assert f["A"] == pytest.approx(0.1)   # 10 -> 11
        assert f["B"] == pytest.approx(-0.1)  # 100 -> 90

    def test_three_month_forward(self):
        f = _forward_returns(self._frame(), as_of_pos=0, horizon=3)
        assert f["A"] == pytest.approx(0.3)   # 10 -> 13

    def test_beyond_data_is_empty(self):
        assert _forward_returns(self._frame(), as_of_pos=5, horizon=1) == {}


class TestAggregate:
    def test_empty(self):
        a = _aggregate([])
        assert a["n_periods"] == 0 and a["mean_ic"] is None

    def test_stable_positive_ic_has_high_ir(self):
        a = _aggregate([0.1, 0.12, 0.09, 0.11, 0.10])
        assert a["mean_ic"] > 0
        assert a["pct_positive"] == 1.0
        assert a["ic_ir"] is not None and a["ic_ir"] > 2  # tight + positive

    def test_noisy_ic_has_low_ir(self):
        a = _aggregate([0.3, -0.3, 0.2, -0.25, 0.05])
        assert abs(a["ic_ir"]) < 2


class TestRunValidationSynthetic:
    def test_monotonic_universe_gives_positive_ic(self):
        # Build a frame where higher-index tickers always trend up harder, so a
        # momentum-based FOM should rank them high and forward returns confirm.
        idx = pd.date_range("2014-01-31", periods=80, freq="ME")
        data = {}
        for i in range(12):
            # each ticker grows at a distinct compounding rate
            rate = 1.0 + 0.005 * i
            data[f"T{i}"] = [100 * rate ** k for k in range(80)]
        closes = pd.DataFrame(data, index=idx)
        out = run_validation(closes, universe=list(data.keys()),
                             horizons=(1, 3), backtest_start="2016-01-01")
        assert out["periods_scored"] > 0
        # With pure persistent trends, 3m IC should be strongly positive.
        ic3 = out["by_horizon"]["3m"]["mean_ic"]
        assert ic3 is not None and ic3 > 0
