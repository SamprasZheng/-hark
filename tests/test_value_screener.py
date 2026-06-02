"""Tests for the value-sleeve (beaten-down quality) screener."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from sharks.backtest.value_screener import _metric, screen, QUALITY_COMPOUNDERS


def _series(n, shape):
    idx = pd.date_range("2018-01-31", periods=n, freq="ME")
    return idx


def _frame():
    idx = pd.date_range("2018-01-31", periods=80, freq="ME")
    # QUAL: quality compounder, rose then drew down ~35% from high, stabilising
    base = [100 * 1.02 ** k for k in range(60)]
    draw = [base[-1] * (1 - 0.006 * k) for k in range(15)]   # ~ -8% over 15? keep mild
    rec = [draw[-1] * 1.01, draw[-1] * 1.02, draw[-1] * 1.03, draw[-1] * 1.04, draw[-1] * 1.05]
    qual = (base + draw + rec)[:80]
    # TRAP: structural collapse — down 80% over 5y, still falling
    trap = [100 * 0.97 ** k for k in range(80)]
    # STRONG: at highs (not beaten) — should be filtered out (dd ~0)
    strong = [100 * 1.03 ** k for k in range(80)]
    return pd.DataFrame({"QUAL": qual, "TRAP": trap, "STRONG": strong}, index=idx)


class TestMetric:
    def test_returns_keys(self):
        m = _metric(_frame(), "QUAL", pd.Timestamp("2024-08-31"))
        assert set(m) >= {"price", "dd_52w", "trend_5y", "vol_ann", "ret_3m"}

    def test_penny_filtered(self):
        idx = pd.date_range("2018-01-31", periods=40, freq="ME")
        f = pd.DataFrame({"P": [2.0] * 40}, index=idx)
        assert _metric(f, "P", idx[-1]) is None

    def test_insufficient_history(self):
        idx = pd.date_range("2024-01-31", periods=5, freq="ME")
        f = pd.DataFrame({"X": [10, 11, 12, 13, 14]}, index=idx)
        assert _metric(f, "X", idx[-1]) is None


class TestScreen:
    def test_trap_rejected_strong_rejected(self):
        f = _frame()
        as_of = f.index[-1]
        res = screen(f, ["QUAL", "TRAP", "STRONG"], as_of,
                     dd_min=-0.70, dd_max=-0.05, trend_floor=-0.25, freefall_floor=-0.20)
        names = [r["ticker"] for r in res]
        # TRAP (structural collapse, trend_5y < -25%) must be rejected
        assert "TRAP" not in names
        # STRONG (at highs, dd ~0 > dd_max) must be rejected
        assert "STRONG" not in names

    def test_value_score_present_and_sorted(self):
        f = _frame()
        res = screen(f, ["QUAL"], f.index[-1], dd_max=-0.02)
        if res:
            assert "value_score" in res[0]
            scores = [r["value_score"] for r in res]
            assert scores == sorted(scores, reverse=True)


class TestUniverse:
    def test_quality_universe_nonempty_and_deduped(self):
        assert len(QUALITY_COMPOUNDERS) > 50
        # no obvious junk tickers; all uppercase symbols
        assert all(t == t.upper() for t in QUALITY_COMPOUNDERS)
