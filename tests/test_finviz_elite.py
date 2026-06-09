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


def test_no_hardcoded_token_in_source():
    # guard: no UUID-style API token literal may be committed in the client
    import pathlib
    import re
    src = pathlib.Path(FE.__file__).read_text(encoding="utf-8")
    uuid_like = re.compile(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}")
    assert not uuid_like.search(src), "a token-like literal is hardcoded — remove it"
