"""Offline tests for the Finviz Elite export-API client (no network, no token leak)."""

from __future__ import annotations

import pytest

from sharks.data import finviz_elite as FE


def test_build_url_and_redact_hides_token():
    url = FE.build_export_url("ta_alltime_b30h,sh_price_o5", token="SECRET123", view="111")
    assert "f=ta_alltime_b30h,sh_price_o5" in url and "auth=SECRET123" in url
    red = FE.redact(url)
    assert "SECRET123" not in red and "auth=***" in red          # token never surfaces


def test_columns_param():
    url = FE.build_export_url("x", token="T", columns="1,2,3")
    assert "&c=1,2,3" in url


def test_parse_csv_and_tickers():
    csv_text = "No.,Ticker,Company,Price\n1,AAPL,Apple,200\n2,nvda,Nvidia,100\n"
    rows = FE.parse_csv(csv_text)
    assert len(rows) == 2 and rows[0]["Ticker"] == "AAPL"
    assert FE.tickers_from_rows(rows) == ["AAPL", "NVDA"]          # upper-cased


def test_resolve_filters_preset_vs_raw():
    assert FE.resolve_filters("dipbuy") == FE.PRESETS["dipbuy"]
    assert FE.resolve_filters("sec_technology") == "sec_technology"  # raw passes through


def test_missing_token_raises_clear_error(monkeypatch):
    monkeypatch.delenv("FINVIZ_ELITE_API_KEY", raising=False)
    with pytest.raises(RuntimeError, match="FINVIZ_ELITE_API_KEY"):
        FE.fetch_screen("dipbuy")


def test_finviz_row_to_dims_maps_columns():
    row = {"Ticker": "NVDA", "Perf Month": "12.0%", "SMA50": "5.0%", "SMA200": "20.0%",
           "RSI": "60", "Rel Volume": "2.0", "Insider Trans": "-1.0%", "Inst Trans": "3.0%",
           "ROE": "90.0%", "Gross Margin": "70.0%", "Sales growth past 5 years": "60.0%",
           "Profit Margin": "50.0%", "52W High": "-25.0%"}
    d = FE.finviz_row_to_dims(row)
    assert 60 < d["technical"] <= 100        # strong momentum + above MAs
    assert d["capital"] > 60                  # rel vol 2x + inst buying
    assert d["fundamental"] > 70              # high ROE/margin/growth
    assert d["dist_ath_pct"] == 25.0          # |−25%| from 52w high
    assert d["news"] is None                  # honest TBD


def test_finviz_row_to_dims_absent_columns_are_none():
    d = FE.finviz_row_to_dims({"Ticker": "X", "Company": "Y"})
    assert d["technical"] is None and d["capital"] is None and d["fundamental"] is None
    assert d["valuation"] is None and d["growth"] is None and d["risk"] is None


def test_finviz_extra_dimensions():
    row = {"Ticker": "Z", "P/E": "10", "P/S": "1.5", "PEG": "0.8",
           "EPS growth next year": "40%", "Sales growth past 5 years": "30%",
           "Beta": "2.0", "Short Float": "20%", "Analyst Recom": "1.5"}
    d = FE.finviz_row_to_dims(row)
    assert d["valuation"] > 70      # cheap (low P/E, P/S, PEG<1)
    assert d["growth"] > 70         # strong eps + sales growth
    assert d["risk"] > 60           # high beta + crowded short
    assert d["analyst"] > 80        # recom 1.5 ≈ strong buy


def test_num_parses_suffixes_and_pct():
    assert FE._num({"a": "2.5M"}, "a") == 2_500_000
    assert FE._num({"a": "-25.0%"}, "a") == -25.0
    assert FE._num({"a": "-"}, "a") is None


def test_no_hardcoded_token_in_source():
    # guard: no UUID-style API token literal may be committed in the client
    import pathlib
    import re
    src = pathlib.Path(FE.__file__).read_text(encoding="utf-8")
    uuid_like = re.compile(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}")
    assert not uuid_like.search(src), "a token-like literal is hardcoded — remove it"
