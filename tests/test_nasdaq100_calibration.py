"""Tests for the NASDAQ-100 calibration backtest helpers."""

from __future__ import annotations

import pandas as pd
import pytest

from sharks.backtest.nasdaq100_calibration import (
    WEIGHT_CANDIDATES,
    _normalize,
    _ret,
    _period_ends,
    answer_key,
)


class TestWeightCandidates:
    def test_all_sum_to_one(self):
        for name, w in WEIGHT_CANDIDATES.items():
            assert abs(sum(w.values()) - 1.0) < 1e-9, name

    def test_all_five_dims(self):
        for w in WEIGHT_CANDIDATES.values():
            assert set(w) == {"momentum", "contrarian", "cyclic", "quality", "bubble_guard"}


class TestNormalize:
    def test_normalizes(self):
        w = _normalize({"a": 2, "b": 2})
        assert w["a"] == pytest.approx(0.5)


def _frame():
    idx = pd.date_range("2019-01-31", periods=27, freq="ME")
    return pd.DataFrame({
        "A": [100 * 1.02 ** k for k in range(27)],   # steady riser
        "B": [100 * 1.10 ** k for k in range(27)],   # fastest riser
        "C": [100 * 0.98 ** k for k in range(27)],   # faller
        "QQQ": [100 * 1.01 ** k for k in range(27)],
    }, index=idx)


class TestRet:
    def test_simple_return(self):
        f = _frame()
        assert _ret(f, "B", 0, 1) == pytest.approx(0.10)

    def test_beyond_end_none(self):
        f = _frame()
        assert _ret(f, "A", 26, 38) is None


class TestPeriodEnds:
    def test_year_takes_last_month_per_year(self):
        f = _frame()
        ends = _period_ends(f, "year")
        years = {d.year for d in ends}
        assert years == {2019, 2020, 2021}

    def test_month_is_all_rows(self):
        f = _frame()
        assert len(_period_ends(f, "month")) == len(f)


class TestAnswerKey:
    def test_fastest_riser_is_top(self):
        f = _frame()
        ak = answer_key(f, ["A", "B", "C"], "year", 2019, 2021, k=1)
        # B compounds fastest → should be the actual top-1 every year present
        for period, info in ak.items():
            assert info["top_k"][0]["t"] == "B"
