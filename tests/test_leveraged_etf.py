"""Tests for the leveraged/inverse ETF decay-aware scorer."""

from __future__ import annotations

import math

import pytest

from sharks.scoring.leveraged_etf import (
    LEVERAGED_ETF_REGISTRY,
    audit_leveraged_holdings,
    is_leveraged_etf,
    score_leveraged_etf,
    volatility_drag,
)


class TestVolatilityDrag:
    def test_2x_40vol(self):
        # 0.5 * 2 * 1 * 0.16 = 0.16
        assert math.isclose(volatility_drag(2, 0.40), 0.16, abs_tol=1e-9)

    def test_3x_40vol(self):
        # 0.5 * 3 * 2 * 0.16 = 0.48
        assert math.isclose(volatility_drag(3, 0.40), 0.48, abs_tol=1e-9)

    def test_5x_higher_than_3x(self):
        assert volatility_drag(5, 0.40) > volatility_drag(3, 0.40)

    def test_inverse_minus1(self):
        # 0.5 * -1 * -2 * 0.16 = 0.16
        assert math.isclose(volatility_drag(-1, 0.40), 0.16, abs_tol=1e-9)

    def test_drag_grows_with_vol(self):
        assert volatility_drag(2, 0.60) > volatility_drag(2, 0.30)


class TestRegistry:
    def test_principal_names_present(self):
        for t in ["TARK", "LABU", "ORCX", "SMCL", "CRWG", "SBIT"]:
            assert t in LEVERAGED_ETF_REGISTRY

    def test_is_leveraged(self):
        assert is_leveraged_etf("TARK")
        assert not is_leveraged_etf("NVDA")


class TestScore:
    def test_unknown_ticker(self):
        out = score_leveraged_etf("NVDA")
        assert out["known"] is False

    def test_2x_weak_underlying_trims(self):
        out = score_leveraged_etf("ORCX", underlying_fom=40, annual_vol=0.40)
        assert out["factor"] == 2
        assert out["verdict"] == "TRIM"

    def test_2x_strong_underlying_tactical_ok(self):
        out = score_leveraged_etf("AAPB", underlying_fom=70, annual_vol=0.30)
        assert out["verdict"] == "TACTICAL-OK"

    def test_3x_is_tactical_only_or_sell(self):
        # LABU is 3x; at 40% vol decay is 48% → SELL if weak, else TACTICAL-ONLY.
        weak = score_leveraged_etf("LABU", underlying_fom=40, annual_vol=0.40)
        strong = score_leveraged_etf("LABU", underlying_fom=70, annual_vol=0.40)
        assert weak["verdict"] == "SELL"
        assert strong["verdict"] == "TACTICAL-ONLY"

    def test_5x_avoid(self):
        out = score_leveraged_etf("5QQQ", underlying_fom=80, annual_vol=0.20)
        assert out["verdict"] == "AVOID"

    def test_inverse_hedge_tag(self):
        out = score_leveraged_etf("SBIT")
        assert out["verdict"] == "INVERSE-HEDGE"
        assert out["factor"] == -1

    def test_decay_adjusted_penalises(self):
        out = score_leveraged_etf("LABU", underlying_fom=70, annual_vol=0.40)
        # 48% decay → meaningful penalty below the raw 70.
        assert out["decay_adjusted_score"] < 70

    def test_decay_pct_reported(self):
        out = score_leveraged_etf("ORCX", annual_vol=0.40)
        assert out["annual_decay_pct"] == 16.0


class TestVixAndBearHedges:
    def test_uvxy_long_vol_hedge(self):
        out = score_leveraged_etf("UVXY")
        assert out["vix_futures"] is True
        assert out["verdict"] == "VOL-HEDGE-DECAY"

    def test_uvix_long_vol_hedge(self):
        assert score_leveraged_etf("UVIX")["verdict"] == "VOL-HEDGE-DECAY"

    def test_svix_short_vol_tail_risk(self):
        out = score_leveraged_etf("SVIX")
        assert out["verdict"] == "SHORT-VOL-TAIL-RISK"

    def test_inverse_index_still_hedge_not_vix(self):
        for t in ["SOXS", "SPXU", "SQQQ", "SDOW"]:
            out = score_leveraged_etf(t)
            assert out["vix_futures"] is False
            assert out["verdict"] == "INVERSE-HEDGE"

    def test_vix_note_mentions_contango(self):
        assert "CONTANGO" in score_leveraged_etf("UVXY")["note"].upper()

    def test_bear_hedge_menu_shape(self):
        from sharks.scoring.leveraged_etf import bear_hedge_menu
        m = bear_hedge_menu()
        hedge_tickers = [h["ticker"] for h in m["inverse_and_long_vol_hedges"]]
        assert "UVXY" in hedge_tickers and "SQQQ" in hedge_tickers
        danger = [h["ticker"] for h in m["short_vol_DANGER"]]
        assert "SVIX" in danger
        # short-vol must NOT be presented as a hedge
        assert "SVIX" not in hedge_tickers


class TestAuditHoldings:
    def test_only_leveraged_scored_sorted_by_decay(self):
        holdings = {"NVDA": 0.1, "LABU": 0.05, "ORCX": 0.045, "AAPL": 0.02}
        out = audit_leveraged_holdings(
            holdings,
            underlying_foms={"XBI": 45, "ORCL": 55},
            vols={"LABU": 0.40, "ORCX": 0.40},
        )
        tickers = [r["ticker"] for r in out]
        # NVDA + AAPL skipped; LABU (48% decay) before ORCX (16%).
        assert tickers == ["LABU", "ORCX"]

    def test_empty_when_no_leveraged(self):
        assert audit_leveraged_holdings({"NVDA": 1.0, "AAPL": 1.0}) == []
