"""Offline tests for the order/demand-anchored valuation (pure logic, no network).

Pins the three-layer fair-value: order-validated growth (not yfinance's noisy
field), the quality score, the intangible scorecard multiplier, the order-
trajectory kill-switch, and the verdict logic.
"""

from __future__ import annotations

import pytest

from sharks.scoring import demand_valuation as dv


class TestQualityScore:
    def test_high_quality_scores_high(self):
        m = {"gross_margin": 0.65, "operating_margin": 0.35, "fcf_margin": 0.30,
             "fcf_conversion": 1.1, "roe": 0.30, "net_cash_to_mktcap": 0.10}
        assert dv.quality_score(m) >= 0.85

    def test_missing_data_is_neutral(self):
        assert dv.quality_score({}) == 0.5

    def test_net_debt_drags(self):
        hi = dv.quality_score({"gross_margin": 0.5, "net_cash_to_mktcap": 0.2})
        lo = dv.quality_score({"gross_margin": 0.5, "net_cash_to_mktcap": -0.2})
        assert hi > lo


class TestOrderValidatedGrowth:
    def test_contracted_orderbook_trusts_segment_surge(self):
        ob = {"key_segment_yoy": 2.0, "contracted_rev_usd": 1.3e9}
        g = dv.order_validated_growth(ob, {"revenue_growth_yoy": 0.15})
        assert g == 0.60   # clamped to the +60% cap (the order book backs the surge)

    def test_unbacked_segment_haircut_toward_revenue(self):
        ob = {"key_segment_yoy": 0.40}   # no B:B/backlog/contracted, seg < 0.30 trigger? 0.40>=0.30 → strong
        # use a sub-0.30 segment so it is NOT auto-strong → haircut path
        ob2 = {"key_segment_yoy": 0.20}
        g = dv.order_validated_growth(ob2, {"revenue_growth_yoy": 0.05})
        assert g == 0.05   # min(0.20, max(0.05,0)) = 0.05

    def test_decelerating_orders_haircut_to_zero(self):
        ob = {"key_segment_yoy": 0.30, "book_to_bill": 0.8}
        g = dv.order_validated_growth(ob, {"revenue_growth_yoy": -0.07})
        assert g <= 0.0


class TestOrderTrajectory:
    def test_contracted_is_accelerating(self):
        t = dv.order_trajectory({"contracted_rev_usd": 1.3e9, "key_segment": "SiPho"}, {})
        assert t["state"] == "accelerating" and t["alert"] is None

    def test_btb_below_one_is_decelerating_with_alert(self):
        t = dv.order_trajectory({"book_to_bill": 0.85}, {"revenue_growth_yoy": -0.07})
        assert t["state"] == "decelerating" and "kill-switch" in t["alert"]

    def test_no_data_is_unknown(self):
        t = dv.order_trajectory({}, {})
        assert t["state"] == "unknown" and t["alert"] is not None


class TestIntangibleMultiplier:
    def test_moat_lifts_concentration_penalises(self):
        wide = dv.intangible_multiplier({"moat": 2, "switching": 2, "concentration_risk": 0})
        narrow = dv.intangible_multiplier({"moat": 0, "switching": 0, "concentration_risk": 2})
        assert wide["moat_mult"] > narrow["moat_mult"]
        assert narrow["concentration_penalty"] == 0.14 and wide["concentration_penalty"] == 0.0

    def test_optionality_addon(self):
        assert dv.intangible_multiplier({"optionality": 2})["optionality_addon"] == 0.12


class TestAdjustedFairPE:
    def test_accelerating_growth_beats_decelerating(self):
        intang = dv.intangible_multiplier({"moat": 1, "switching": 1, "concentration_risk": 0})
        accel = dv.adjusted_fair_pe(0.40, 0.7, {"state": "accelerating"}, intang, 30.0)
        decel = dv.adjusted_fair_pe(0.40, 0.7, {"state": "decelerating"}, intang, 30.0)
        assert accel > decel

    def test_no_growth_floors_low(self):
        intang = dv.intangible_multiplier({})
        pe = dv.adjusted_fair_pe(None, 0.5, {"state": "unknown"}, intang, 30.0)
        assert pe is not None and pe <= 30.0 * 1.0


class TestRow:
    def _m(self, **kw):
        base = {"sector": "Technology", "forward_eps": 6.0, "price": 255.0, "fwd_pe": 44.5,
                "gross_margin": 0.27, "operating_margin": 0.16, "fcf_margin": 0.08,
                "roe": 0.15, "net_cash_to_mktcap": 0.05, "revenue_growth_yoy": 0.15}
        base.update(kw)
        return base

    def test_tsem_contracted_lifts_fair_pe_above_static(self):
        ob = dv.DEMAND_ORDERBOOK["TSEM"]
        row = dv.demand_valuation_row("TSEM", self._m(), ob)
        # the contracted SiPho order book + moat should justify a fair P/E well above
        # the flat 30x industry anchor that the static screen used
        assert row["adjusted_fair_pe"] > 30.0
        assert row["order_trajectory"] == "accelerating"
        assert row["forward_fair_value"] is not None
        assert "訂單" in row["verdict"]

    def test_decelerating_name_gets_caution_verdict(self):
        ob = dv.DEMAND_ORDERBOOK["QRVO"]
        row = dv.demand_valuation_row("QRVO", self._m(revenue_growth_yoy=-0.07, forward_eps=7.0, price=104.0), ob)
        assert row["order_trajectory"] == "decelerating"
        assert row["order_alert"] is not None

    def test_lossmaking_has_no_anchor(self):
        row = dv.demand_valuation_row("NVTS", self._m(forward_eps=-0.5, price=27.0),
                                      dv.DEMAND_ORDERBOOK["NVTS"])
        assert row["forward_fair_value"] is None
        assert "選擇權" in row["verdict"]


class TestCLI:
    def test_demand_val_parses(self):
        from sharks.cli import build_parser
        ns = build_parser().parse_args(["demand-val", "--no-network", "--dry-run"])
        assert ns.command == "demand-val" and ns.no_network is True

    def test_demand_val_dry_run_exits_zero(self):
        from sharks.cli import main
        assert main(["demand-val", "--no-network", "--dry-run"]) == 0
