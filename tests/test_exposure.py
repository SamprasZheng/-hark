"""Tests for the true total-exposure gauge (pure logic)."""

from __future__ import annotations

from sharks.scoring.exposure import concentration_verdict, crash_scenario, true_exposure


class TestTrueExposure:
    def test_net_worth_and_shares(self):
        e = true_exposure({"A": 100.0, "B": 50.0}, debt_usd=120.0)
        assert e["gross_assets_usd"] == 150
        assert e["net_liquid_worth_usd"] == 30
        assert e["shares_pct"]["A"] == 66.7


class TestCrashScenario:
    def test_beta_scaled_drops(self):
        cs = crash_scenario({"HI": 100.0, "LO": 100.0}, {"HI": 2.0, "LO": 0.5}, market_drop=0.30)
        assert cs["per_container_after"]["HI"] == 40   # 2.0×0.30 = −60%
        assert cs["per_container_after"]["LO"] == 85   # 0.5×0.30 = −15%

    def test_drop_capped_at_95(self):
        cs = crash_scenario({"X": 100.0}, {"X": 5.0}, market_drop=0.50)  # 2.5 → cap 0.95
        assert cs["per_container_after"]["X"] == 5

    def test_income_and_net_worth(self):
        cs = crash_scenario({"A": 100.0}, {"A": 1.0}, market_drop=0.30, debt_usd=50.0,
                            annual_income_usd=100.0, income_hit_frac=0.40)
        assert cs["net_worth_after"] == 20             # 70 − 50
        assert cs["income_loss_est"] == 40
        assert cs["total_hit_assets_plus_income"] == 70  # 30 asset + 40 income


class TestConcentrationVerdict:
    def test_extreme(self):
        e = true_exposure({"A": 89.0, "B": 11.0}, debt_usd=85.0)
        assert concentration_verdict(e, 89.0, 97.0)["level"] == "EXTREME"

    def test_ok_when_diversified(self):
        e = true_exposure({a: 20.0 for a in "ABCDE"}, debt_usd=0.0)
        assert concentration_verdict(e, 20.0, 40.0)["level"] == "OK"
