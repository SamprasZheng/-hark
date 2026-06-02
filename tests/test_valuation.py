"""Tests for the regime-conditioned valuation system (pure logic)."""

from __future__ import annotations

import numpy as np
import pandas as pd

from sharks.scoring.valuation import (
    ENV_ORDER,
    all_regime_targets,
    industry_pe_valuation,
    peg_fair_pe,
    price_environment,
    regime_forward_return_backtest,
    target_for_regime,
    valuation,
)

BAND = {"ticker": "X", "price": 100.0, "target_low": 80.0, "target_mean": 110.0, "target_high": 140.0}
PE = {"ticker": "Y", "price": 50.0, "forward_eps": 4.0, "trailing_pe": 12.5}  # no analyst band


class TestTargetForRegime:
    def test_optimistic_above_panic(self):
        assert target_for_regime(BAND, "積極樂觀") > target_for_regime(BAND, "悲觀恐慌")

    def test_within_band(self):
        for env in ENV_ORDER:
            t = target_for_regime(BAND, env)
            assert 80.0 <= t <= 140.0

    def test_neutral_is_mid_band(self):
        # band_position 0.5 → low + 0.5*(high-low) = 110
        assert abs(target_for_regime(BAND, "中性") - 110.0) < 1e-6

    def test_pe_fallback(self):
        # 4.0 * 12.5 * 1.0 (中性) = 50
        assert abs(target_for_regime(PE, "中性") - 50.0) < 1e-6
        assert target_for_regime(PE, "積極樂觀") > target_for_regime(PE, "保守")

    def test_no_data_none(self):
        assert target_for_regime({"ticker": "Z", "price": 10}, "中性") is None


class TestAllRegimeTargets:
    def test_monotonic_descending(self):
        t = all_regime_targets(BAND)
        seq = [t[e] for e in ENV_ORDER]
        assert seq == sorted(seq, reverse=True)   # 積極 highest → 恐慌 lowest


class TestValuation:
    def test_upside_and_horizons(self):
        v = valuation(BAND, "積極樂觀")
        assert v["upside_to_target"] > 0
        assert v["est_return"]["quarter"] > v["est_return"]["week"]   # more gap closes over a quarter
        assert v["method"] == "analyst-band"

    def test_no_data(self):
        v = valuation({"ticker": "Z", "price": None}, "中性")
        assert v["upside_to_target"] is None


class TestPriceEnvironment:
    def _series(self, slope, n=400, start=100.0):
        idx = pd.date_range("2023-01-01", periods=n, freq="B")
        return pd.Series([start * (1 + slope) ** i for i in range(n)], index=idx)

    def test_strong_uptrend_optimistic(self):
        s = self._series(0.004)   # steady strong uptrend
        assert price_environment(s, s.index[-1]) in ("積極樂觀", "寬鬆")

    def test_crash_panic(self):
        s = self._series(-0.004)  # steady decline
        assert price_environment(s, s.index[-1]) in ("悲觀恐慌", "保守")

    def test_insufficient_none(self):
        s = self._series(0.001, n=50)
        assert price_environment(s, s.index[-1]) is None


class TestIndustryPEValuation:
    def test_high_beta_high_multiple_deep_downside(self):
        # the NVDA-style flaw fix: high beta + high multiple → deep, REAL downside
        f = {"forward_eps": 6.0, "price": 300.0, "beta": 2.2, "sector": "Technology",
             "earnings_growth_yoy": 0.40, "fwd_pe": 50.0}
        v = industry_pe_valuation(f)
        assert v["realistic_downside"] < -0.40          # NOT −4%
        assert v["premium_to_industry_fair"] > 0         # 50× vs 30× sector → stretched

    def test_low_beta_defensive_shallower(self):
        defensive = {"forward_eps": 30.0, "price": 500.0, "beta": 0.15, "sector": "Industrials",
                     "earnings_growth_yoy": 0.05, "fwd_pe": 16.0}
        aggressive = {"forward_eps": 6.0, "price": 300.0, "beta": 2.2, "sector": "Technology",
                      "earnings_growth_yoy": 0.40, "fwd_pe": 50.0}
        # a low-beta name has a shallower beta-implied floor than a high-beta one
        assert (industry_pe_valuation(defensive)["bear_beta_implied"] / 500.0
                > industry_pe_valuation(aggressive)["bear_beta_implied"] / 300.0)

    def test_peg_clamp(self):
        assert peg_fair_pe(0.40, 30.0) == 40.0          # 40% grower → ~40×
        assert peg_fair_pe(None, 30.0) == 30.0          # no growth → industry P/E
        assert peg_fair_pe(5.0, 30.0) == 75.0           # clamped to 2.5×

    def test_no_data_none(self):
        assert industry_pe_valuation({"price": 100}) is None


class TestBacktest:
    def test_runs_and_buckets(self):
        idx = pd.date_range("2018-01-01", periods=900, freq="B")
        rng = np.random.default_rng(0)
        s = pd.Series(100 * np.cumprod(1 + rng.normal(0.0004, 0.01, 900)), index=idx)
        bt = regime_forward_return_backtest(s)
        assert set(bt.keys()) == set(ENV_ORDER)
        assert all("n" in bt[e] for e in ENV_ORDER)
