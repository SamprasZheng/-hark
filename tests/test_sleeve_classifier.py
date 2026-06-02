"""Tests for the four-sleeve portfolio classifier."""

from __future__ import annotations

import pytest

from sharks.backtest.sleeve_classifier import (
    TARGET_ALLOCATION,
    classify_sleeve,
    classify_portfolio,
)


class TestClassifySleeve:
    def test_target_sums_to_one(self):
        assert abs(sum(TARGET_ALLOCATION.values()) - 1.0) < 1e-9

    def test_leveraged_long_is_moonshot(self):
        for t in ("TARK", "LABU", "TSLL", "AAPB"):
            assert classify_sleeve(t)["sleeve"] == "MOONSHOT"

    def test_inverse_is_hedge(self):
        assert classify_sleeve("SBIT")["sleeve"] == "HEDGE"
        assert classify_sleeve("SQQQ")["sleeve"] == "HEDGE"
        assert classify_sleeve("UVXY")["sleeve"] == "HEDGE"

    def test_beaten_quality_is_value(self):
        for t in ("NKE", "LULU", "STZ"):
            assert classify_sleeve(t)["sleeve"] == "VALUE"

    def test_value_trap_is_not_value(self):
        # low-quality beaten names must NOT land in VALUE
        for t in ("VFC", "UAA"):
            assert classify_sleeve(t)["sleeve"] != "VALUE"

    def test_quality_core_is_fom(self):
        for t in ("PG", "PEP", "CRM"):
            assert classify_sleeve(t)["sleeve"] == "FOM_CORE"

    def test_dead_husk(self):
        assert classify_sleeve("FSRNQ")["sleeve"] == "DEAD"
        assert classify_sleeve("BYND")["sleeve"] == "DEAD"

    def test_narrative_is_moonshot(self):
        assert classify_sleeve("QSU")["sleeve"] == "MOONSHOT"


class TestClassifyPortfolio:
    def _book(self):
        return {"TARK": 1500, "NKE": 200, "PG": 300, "SBIT": 100, "FSRNQ": 0.01}

    def test_dead_excluded_from_base(self):
        r = classify_portfolio(self._book())
        # investable excludes the dead husk
        assert r["investable_usd"] == pytest.approx(2100.01, abs=0.5)

    def test_sleeve_rollup(self):
        r = classify_portfolio(self._book())
        bs = r["by_sleeve"]
        assert bs["MOONSHOT"]["current_usd"] == 1500
        assert bs["VALUE"]["current_usd"] == 200
        assert bs["FOM_CORE"]["current_usd"] == 300
        assert bs["HEDGE"]["current_usd"] == 100

    def test_moonshot_over_cap_flagged(self):
        r = classify_portfolio(self._book())
        assert r["by_sleeve"]["MOONSHOT"]["gap_pct"] > 0  # 1500/2100 ≈ 71% >> 20%
        assert any("MOONSHOT" in a for a in r["actions"])

    def test_trim_priority_leveraged_first(self):
        book = {"TARK": 100, "LABU": 100, "QSU": 100}  # 2x, 3x, narrative
        r = classify_portfolio(book)
        order = [x["ticker"] for x in r["trim_priority_moonshot"]]
        # LABU (3x) should rank ahead of TARK (2x), narrative QSU last
        assert order.index("LABU") < order.index("TARK") < order.index("QSU")

    def test_dead_listed_for_taxloss(self):
        r = classify_portfolio(self._book())
        assert "FSRNQ" in r["dead_for_taxloss"]
