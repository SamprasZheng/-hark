"""Tests for the IGV software screen — pure logic only (offline).

The price/fundamentals fetch is network and covered by the CLI run; here we validate
the universe integrity, the NVIDIA-partner tagging, the 錯殺/趨勢 bucketing predicates,
and the partner sort (equity tier first).
"""
from __future__ import annotations

from sharks.scoring.igv_software import (
    IGV_UNIVERSE, NVIDIA_PARTNERS, nvidia_tag, is_oversold, is_momentum,
    partner_sort_key,
)


class TestUniverse:
    def test_universe_is_large_and_unique(self):
        assert len(IGV_UNIVERSE) >= 100
        assert len(IGV_UNIVERSE) == len(set(IGV_UNIVERSE))  # no dupes

    def test_core_software_present(self):
        for t in ("MSFT", "ORCL", "CRM", "NOW", "PANW", "CRWD", "SNPS", "CDNS"):
            assert t in IGV_UNIVERSE


class TestNvidiaTag:
    def test_known_partner_tagged(self):
        tag = nvidia_tag("SNPS")
        assert tag and tag["tier"] == "equity"
        assert "url" in tag and tag["url"].startswith("http")

    def test_non_partner_is_none(self):
        assert nvidia_tag("BOX") is None

    def test_integration_tier_flagged_distinctly(self):
        # DDOG is integration-tier, not a headline partner — must not be over-ranked
        assert nvidia_tag("DDOG")["tier"] == "integration"

    def test_every_igv_partner_has_required_fields(self):
        for t, p in NVIDIA_PARTNERS.items():
            assert {"tier", "type", "note", "url"} <= set(p)
            assert p["tier"] in ("equity", "headline", "medium", "integration")


class TestBuckets:
    def test_oversold_predicate(self):
        # high contrarian + intact moat + not extreme bubble -> oversold
        assert is_oversold({"contrarian": 80, "ip_defensibility": 70, "bubble_guard": 10})
        # extreme bubble disqualifies even with high contrarian
        assert not is_oversold({"contrarian": 80, "ip_defensibility": 70, "bubble_guard": -60})
        # low contrarian (already-run momentum name) is not oversold
        assert not is_oversold({"contrarian": 32, "ip_defensibility": 50, "bubble_guard": -10})

    def test_momentum_predicate(self):
        assert is_momentum({"momentum": 70, "bubble_guard": 0})
        assert not is_momentum({"momentum": 40, "bubble_guard": 0})
        assert not is_momentum({"momentum": 70, "bubble_guard": -60})  # extreme bubble out


class TestPartnerSort:
    def test_equity_tier_sorts_before_headline(self):
        rows = [
            {"ticker": "NOW", "final_fom_alpha": 90, "nvidia": {"tier": "headline"}},
            {"ticker": "SNPS", "final_fom_alpha": 10, "nvidia": {"tier": "equity"}},
            {"ticker": "DDOG", "final_fom_alpha": 99, "nvidia": {"tier": "integration"}},
        ]
        ordered = sorted(rows, key=partner_sort_key)
        assert [r["ticker"] for r in ordered] == ["SNPS", "NOW", "DDOG"]

    def test_within_tier_sorts_by_fom_desc(self):
        rows = [
            {"ticker": "A", "final_fom_alpha": 50, "nvidia": {"tier": "headline"}},
            {"ticker": "B", "final_fom_alpha": 80, "nvidia": {"tier": "headline"}},
        ]
        ordered = sorted(rows, key=partner_sort_key)
        assert [r["ticker"] for r in ordered] == ["B", "A"]
