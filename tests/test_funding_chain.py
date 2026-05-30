"""Offline tests for the funding-chain rupture detector (pure-logic layer)."""

from __future__ import annotations

import pytest

from sharks.regime.funding_chain import (
    INDICATORS,
    TIER_WEIGHT,
    classify_indicator,
    fetch_funding_indicators,
    funding_stress_score,
)


class TestClassifyIndicator:
    def test_higher_worse_bands(self):
        # hy_oas_bp: elevated 450, stress 600
        assert classify_indicator("hy_oas_bp", 300) == "normal"
        assert classify_indicator("hy_oas_bp", 500) == "elevated"
        assert classify_indicator("hy_oas_bp", 650) == "stress"

    def test_lower_worse_bands(self):
        # ccy_basis_bp: elevated -25, stress -50 (more negative = worse)
        assert classify_indicator("ccy_basis_bp", 0) == "normal"
        assert classify_indicator("ccy_basis_bp", -30) == "elevated"
        assert classify_indicator("ccy_basis_bp", -60) == "stress"

    def test_unknown_raises(self):
        with pytest.raises(KeyError):
            classify_indicator("not_an_indicator", 1.0)


class TestTaxonomy:
    def test_tiers_present(self):
        tiers = {spec["tier"] for spec in INDICATORS.values()}
        assert tiers == {1, 2, 3}

    def test_tier3_weight_zero(self):
        assert TIER_WEIGHT[3] == 0.0

    def test_fra_ois_not_in_taxonomy(self):
        # FRA-OIS is obsolete (USD LIBOR ceased mid-2023); must be absent.
        names = " ".join(INDICATORS.keys())
        assert "fra_ois" not in names
        assert "sofr_ois_bp" in INDICATORS


class TestFundingStressScore:
    def test_all_calm(self):
        out = funding_stress_score({
            "sofr_ois_bp": 5, "hy_oas_bp": 300, "nfci": -0.3,
        })
        assert out["verdict"] == "CALM"
        assert out["score"] < 25

    def test_tier1_stress_escalates(self):
        out = funding_stress_score({
            "sofr_ois_bp": 35, "cdx_ig_fin_bp": 150, "hy_oas_bp": 650,
        })
        # 3 Tier-1 stress hits → RUPTURE regardless of exact score.
        assert out["tier1_stress_hits"] == 3
        assert out["verdict"] == "RUPTURE"

    def test_two_tier1_stress_is_stress(self):
        out = funding_stress_score({
            "sofr_ois_bp": 35, "hy_oas_bp": 650, "nfci": -0.2,
        })
        assert out["tier1_stress_hits"] == 2
        assert out["verdict"] in ("STRESS", "RUPTURE")

    def test_tier3_alone_does_not_move_score(self):
        # SLOOS at stress, everything else calm → must NOT escalate.
        out = funding_stress_score({
            "sloos_tightening_pct": 50,   # stress band
            "sofr_ois_bp": 5,             # normal
        })
        # Tier-3 weight 0; only the calm Tier-1 contributes → CALM.
        assert out["verdict"] == "CALM"
        assert out["tier1_stress_hits"] == 0

    def test_breakdown_lists_bands(self):
        out = funding_stress_score({"hy_oas_bp": 650, "nfci": 0.6})
        bands = {b["indicator"]: b["band"] for b in out["breakdown"]}
        assert bands["hy_oas_bp"] == "stress"
        assert bands["nfci"] == "stress"

    def test_unknown_indicator_ignored(self):
        out = funding_stress_score({"made_up": 999, "hy_oas_bp": 300})
        names = {b["indicator"] for b in out["breakdown"]}
        assert "made_up" not in names
        assert "hy_oas_bp" in names

    def test_empty_readings_calm(self):
        out = funding_stress_score({})
        assert out["verdict"] == "CALM"
        assert out["score"] == 0.0


class TestFetchStub:
    def test_fetch_raises_not_implemented(self):
        with pytest.raises(NotImplementedError):
            fetch_funding_indicators("2026-05-30")
