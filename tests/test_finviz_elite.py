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


def test_fetch_universe_batches_and_dedupes(monkeypatch):
    calls = []
    def fake_fetch(filters_or_preset="", *, token=None, view="152", columns=None,
                   tickers=None, timeout=30):
        calls.append(tickers.split(","))
        return [{"Ticker": t} for t in tickers.split(",")]
    monkeypatch.setattr(FE, "fetch_screen", fake_fetch)
    uni = [f"T{i}" for i in range(25)] + ["T1"]      # 26 with a dup
    rows = FE.fetch_universe(uni, batch=10)
    assert len(calls) == 3                            # 26 → batches of 10,10,6
    assert len(rows) == 25                            # dup removed
    assert all(len(c) <= 10 for c in calls)


def test_resolve_target_universe():
    assert FE.resolve_target("universe")[0] == "universe"
    assert FE.resolve_target("fom")[0] == "universe"


def test_write_scan_recommendation(tmp_path):
    from sharks.scoring import rally_signal as RS
    sigs = [RS.assess("AAA", {"technical": 70, "capital": 65, "fundamental": 75}, prior_streak=3),
            RS.assess("BBB", {"technical": 30}, prior_streak=0)]
    p = FE.write_scan_recommendation(tmp_path, sigs, source="universe")
    import json
    rec = json.loads(p.read_text(encoding="utf-8"))
    assert rec["source"] == "universe" and rec["n"] == 2
    assert "ranked" in rec and rec["ranked"][0]["ticker"] in ("AAA", "BBB")


def test_rally_ignition_presets_resolve():
    for p in ("rally_ignition", "mis_killed_2022", "dipbuy"):
        flt = FE.resolve_filters(p)
        assert flt and flt != p and "sh_avgvol" in flt or "sma" in flt.lower()
    # rally_ignition is a filter (not a scope) → filters mode
    kind, flt, tks = FE.resolve_target("rally_ignition")
    assert kind == "filters" and tks is None and "ta_sma20_pa" in flt


def test_build_url_with_tickers_uses_t_param():
    url = FE.build_export_url(token="T", view="152", tickers="RKLB,IRDM", columns="1,2")
    assert "&t=RKLB,IRDM" in url and "&f=" not in url and "auth=T" in url


def test_resolve_target_scope_vs_filters():
    kind, flt, tks = FE.resolve_target("space")           # a basecross theme scope
    assert kind == "scope" and flt is None and "RKLB" in tks
    kind, flt, tks = FE.resolve_target("dipbuy")          # a preset
    assert kind == "filters" and tks is None and flt == FE.PRESETS["dipbuy"]
    kind, flt, tks = FE.resolve_target("ta_alltime_b30h") # raw f=
    assert kind == "filters" and flt == "ta_alltime_b30h"


def test_build_url_custom_view_and_columns():
    url = FE.build_export_url("f1", token="T", view=FE.DIMENSION_VIEW, columns=FE.DIMENSION_COLUMNS)
    assert "v=152" in url and "&c=" in url and "auth=T" in url


def test_signals_from_finviz_fuel_gate():
    rows = [
        # 有燃料(高 ROE/毛利/成長)+ 起漲 + 連續 → 可考慮買入
        {"Ticker": "GOOD", "Perf Month": "12%", "SMA50": "5%", "SMA200": "15%", "RSI": "62",
         "Rel Volume": "1.8", "Inst Trans": "4%", "ROE": "40%", "Gross Margin": "60%",
         "Sales past 5Y": "30%", "Profit Margin": "25%", "52W High": "-30%"},
        # 熱價無基本面(墓園型)
        {"Ticker": "HYPE", "Perf Month": "40%", "SMA50": "20%", "SMA200": "30%", "RSI": "75",
         "Rel Volume": "5", "ROE": "-20%", "Gross Margin": "10%", "Profit Margin": "-15%",
         "52W High": "-10%"},
    ]
    sigs = FE.signals_from_finviz(rows, prior_streaks={"GOOD": 3})
    by = {s.ticker: s for s in sigs}
    assert by["GOOD"].has_fuel and by["GOOD"].buy_consider          # fueled + 連續 → buy
    assert by["HYPE"].conviction.startswith("🚫")                   # hot, no fuel → 墓園
    assert sigs[0].ticker == "GOOD"                                  # ranked first


def test_signals_from_finviz_skips_blank_ticker():
    assert FE.signals_from_finviz([{"Company": "x"}]) == []


def test_no_hardcoded_token_in_source():
    # guard: no UUID-style API token literal may be committed in the client
    import pathlib
    import re
    src = pathlib.Path(FE.__file__).read_text(encoding="utf-8")
    uuid_like = re.compile(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}")
    assert not uuid_like.search(src), "a token-like literal is hardcoded — remove it"


# ── 2026-06-10 delta: the 5 TO_ADD columns (Forward P/E / Earnings / ATR / ownership) ──

def test_forward_pe_preferred_over_trailing_in_valuation():
    # trailing P/E looks stretched (50 → penalty) but Forward P/E is cheap (12 → bonus)
    stretched = FE.finviz_row_to_dims({"Ticker": "G", "P/E": "50", "P/S": "5"})
    fwd_cheap = FE.finviz_row_to_dims({"Ticker": "G", "P/E": "50", "Forward P/E": "12", "P/S": "5"})
    assert fwd_cheap["valuation"] > stretched["valuation"]   # forward PE rescues a growth name
    # absent Forward P/E → behaviour unchanged (still consumes trailing P/E)
    assert FE.finviz_row_to_dims({"Ticker": "G", "P/E": "10", "P/S": "1.5", "PEG": "0.8"})["valuation"] > 70


def test_days_to_earnings_parses_finviz_formats():
    from datetime import date
    asof = date(2026, 6, 10)
    assert FE._days_to_earnings("Jun 12/a", asof=asof) == 2          # 'Mon DD' + session marker
    assert FE._days_to_earnings("Aug 26 AMC", asof=asof) == 77
    assert FE._days_to_earnings("6/12/2026", asof=asof) == 2         # explicit M/D/Y
    assert FE._days_to_earnings("Feb 19", asof=asof) == 254          # past month → rolls to 2027
    assert FE._days_to_earnings("-", asof=asof) is None
    assert FE._days_to_earnings(None, asof=asof) is None


def test_finviz_row_to_flags_gates_and_levels():
    from datetime import date
    asof = date(2026, 6, 10)
    row = {"Ticker": "Q", "Earnings": "Jun 12/a", "ATR": "5.0", "Price": "100",
           "Forward P/E": "18", "Inst Own": "82%", "Insider Own": "15%",
           "Short Float": "22%", "SMA200": "45%"}
    f = FE.finviz_row_to_flags(row, asof=asof)
    assert f["earnings_blackout"] is True            # 2 days out → within the 3-day window
    assert f["squeeze_watch"] is True                # short float 22% + insider own 15%
    assert f["overshoot_200d"] is True               # 45% above 200d MA → 乖離過大
    assert f["atr_pct"] == 5.0                        # 5.0 / 100 * 100
    assert f["inst_own"] == 82.0 and f["insider_own"] == 15.0 and f["forward_pe"] == 18.0


def test_finviz_row_to_flags_clean_row_trips_nothing():
    from datetime import date
    f = FE.finviz_row_to_flags({"Ticker": "C", "Price": "50", "Short Float": "3%",
                                "Insider Own": "1%", "SMA200": "8%"}, asof=date(2026, 6, 10))
    assert f["earnings_blackout"] is False and f["squeeze_watch"] is False
    assert f["overshoot_200d"] is False and f["days_to_earnings"] is None


def test_atr_position_size_risk_budget_and_cap():
    # equity 100k, risk 1% = $1,000 budget; k*ATR = 2.5*4 = $10/share → 100 shares
    s = FE.atr_position_size(entry=100, atr=4, account_equity=100_000, risk_pct=1.0, k=2.5)
    assert s["risk_per_share"] == 10.0 and s["shares"] == 100 and s["stop"] == 90.0
    # position cap binds: 5% of 100k = $5,000 → 50 shares @ $100, not 100
    capped = FE.atr_position_size(100, 4, 100_000, risk_pct=1.0, k=2.5, max_position_pct=5)
    assert capped["shares"] == 50
    assert FE.atr_position_size(0, 4, 100_000) is None        # bad input → None


def test_write_scan_recommendation_embeds_flags(tmp_path):
    import json
    from sharks.scoring import rally_signal as RS
    sigs = [RS.assess("AAA", {"technical": 70, "capital": 65, "fundamental": 75}, prior_streak=3)]
    flags = {"AAA": {"earnings_blackout": True, "squeeze_watch": False,
                     "overshoot_200d": True, "atr": 5.0}}
    p = FE.write_scan_recommendation(tmp_path, sigs, source="universe", flags_by_ticker=flags)
    rec = json.loads(p.read_text(encoding="utf-8"))
    assert rec["earnings_blackout"] == ["AAA"] and rec["overshoot_200d"] == ["AAA"]
    assert rec["squeeze_watch"] == []
    assert rec["ranked"][0]["flags"]["atr"] == 5.0
    # backward compatible: no flags arg → no flags key, summary lists empty
    p2 = FE.write_scan_recommendation(tmp_path, sigs, source="universe")
    rec2 = json.loads(p2.read_text(encoding="utf-8"))
    assert rec2["earnings_blackout"] == [] and "flags" not in rec2["ranked"][0]


# ── 2026-06-13 regression: Custom view (152) Title-Case headers silently zeroed dims ──

def test_custom_view_title_case_headers_populate_dims():
    # The bug: _num matched on exact, lower-ish strings ('52W High', 'SMA50', 'EPS growth
    # next year'); the live Custom-view export uses different wording / casing, so
    # dist_ath_pct / growth went 0/603 and SMA contributions were dropped (06-09→06-12).
    row = {"Ticker": "OKTA", "Performance (Month)": "10.0%",
           "50-Day Simple Moving Average": "6.0%", "200-Day Simple Moving Average": "18.0%",
           "Relative Strength Index (14)": "60",
           "EPS Growth Next Year": "35%", "Sales Growth Past 5 Years": "25%",
           "52-Week High": "-28.0%"}
    d = FE.finviz_row_to_dims(row)
    assert d["dist_ath_pct"] == 28.0          # was None before the header fix
    assert d["growth"] is not None and d["growth"] > 60
    assert d["technical"] is not None         # SMA50/200 now contribute


def test_custom_view_title_case_overshoot_flag():
    from datetime import date
    f = FE.finviz_row_to_flags({"Ticker": "Q", "200-Day Simple Moving Average": "45%",
                                "Price": "100"}, asof=date(2026, 6, 10))
    assert f["overshoot_200d"] is True        # SMA200 resolved via Title-Case header


def test_field_resolves_aliases_and_is_case_insensitive():
    assert FE._field({"sales growth past 5 years": "30%"}, "sales_growth") == 30.0  # case
    assert FE._field({"52-Week High": "-12%"}, "dist_52w_high") == -12.0            # wording
    assert FE._field({"X": "1"}, "no_such_field") is None                           # unknown


def test_flags_coverage_reports_dark_gated_columns():
    full = {"AAA": {"forward_pe": 18.0, "earnings_date": "Jun 12/a", "atr": 5.0,
                    "inst_own": 80.0, "insider_own": 12.0}}
    c = FE.flags_coverage(full)
    assert c["n"] == 1 and c["dark"] == [] and c["fields"]["atr"] == 1
    # the current Custom view (no ownership / ATR / earnings / fwd PE) → all 5 dark
    bare = {"AAA": {"forward_pe": None, "earnings_date": None, "atr": None,
                    "inst_own": None, "insider_own": None, "overshoot_200d": True}}
    assert set(FE.flags_coverage(bare)["dark"]) == set(FE.GATE_COVERAGE_FIELDS)
    assert FE.flags_coverage(None)["n"] == 0          # tolerant of empty/None


def test_scan_json_embeds_gate_coverage(tmp_path):
    import json
    from sharks.scoring import rally_signal as RS
    sigs = [RS.assess("AAA", {"technical": 70}, prior_streak=0)]
    flags = {"AAA": {"forward_pe": 18.0, "earnings_date": "Jun 12/a", "atr": 5.0,
                     "inst_own": 80.0, "insider_own": 12.0}}
    p = FE.write_scan_recommendation(tmp_path, sigs, source="universe", flags_by_ticker=flags)
    rec = json.loads(p.read_text(encoding="utf-8"))
    assert rec["gate_coverage"]["dark"] == [] and rec["gate_coverage"]["fields"]["atr"] == 1
