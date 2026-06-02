"""Tests for exchange ticker-suffix recognition (Phase-2 後綴支援)."""

from __future__ import annotations

from sharks.scoring.ticker_suffix import (
    SUFFIX_MAP,
    currency_of,
    fx_caveat,
    is_non_us,
    parse_ticker,
    region_of,
    split_by_region,
)


class TestParse:
    def test_us_primary_no_suffix(self):
        p = parse_ticker("NVDA")
        assert p.is_non_us is False and p.suffix is None and p.base == "NVDA"
        assert p.is_adr_pink is False

    def test_taiwan(self):
        p = parse_ticker("2330.TW")
        assert p.is_non_us and p.suffix == "TW" and p.base == "2330"
        assert p.exchange.currency == "TWD" and p.exchange.region == "APAC"

    def test_korea_kospi_and_kosdaq(self):
        assert parse_ticker("000660.KS").exchange.country == "South Korea"
        assert parse_ticker("322310.KQ").exchange.exchange == "KOSDAQ"

    def test_japan_and_hk(self):
        assert parse_ticker("8053.T").exchange.currency == "JPY"
        assert parse_ticker("0700.HK").exchange.region == "APAC"

    def test_europe_symbol_with_dot_suffix(self):
        # LVMH: base symbol MC, Paris suffix PA — must NOT confuse with Madrid 'MC' suffix
        p = parse_ticker("MC.PA")
        assert p.base == "MC" and p.suffix == "PA"
        assert p.exchange.country == "France" and p.exchange.currency == "EUR"

    def test_madrid_suffix(self):
        assert parse_ticker("ITX.MC").exchange.country == "Spain"

    def test_germany(self):
        assert parse_ticker("RHM.DE").exchange.currency == "EUR"


class TestADRPink:
    def test_adr_pink_flagged_not_non_us(self):
        # OTC ADR pinks trade in USD but track a foreign primary — flagged separately.
        for t in ("BYDDY", "TCEHY", "LVMUY"):
            p = parse_ticker(t)
            assert p.is_adr_pink is True
            assert p.is_non_us is False
            assert currency_of(t) == "USD"

    def test_four_letter_not_pink(self):
        assert parse_ticker("NVDA").is_adr_pink is False


class TestHelpers:
    def test_is_non_us(self):
        assert is_non_us("000660.KS") is True
        assert is_non_us("AAPL") is False

    def test_region_and_currency_defaults_us(self):
        assert region_of("AAPL") == "NA" and currency_of("AAPL") == "USD"

    def test_fx_caveat_only_for_non_us(self):
        assert fx_caveat("AAPL") is None
        c = fx_caveat("2330.TW")
        assert c is not None and "TWD" in c

    def test_split_by_region(self):
        buckets = split_by_region(["AAPL", "2330.TW", "RHM.DE", "BYDDY", "000660.KS"])
        assert "AAPL" in buckets["US"]
        assert "2330.TW" in buckets["APAC"] and "000660.KS" in buckets["APAC"]
        assert "RHM.DE" in buckets["EU"]
        assert "BYDDY" in buckets["ADR_PINK"]

    def test_suffix_map_wellformed(self):
        for suf, ex in SUFFIX_MAP.items():
            assert ex.suffix == suf
            assert ex.region in ("NA", "EU", "APAC")
            assert len(ex.currency) == 3
