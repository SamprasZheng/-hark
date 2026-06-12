"""Tests for the web dashboard backend (sharks.ui.server) — pure helpers + synthetic data,
no network. Chart/scan paths are monkeypatched onto ma_scanner like test_ma_scanner does."""

from __future__ import annotations

import math
import time
from dataclasses import dataclass

import numpy as np
import pandas as pd
import pytest

from sharks.ui.server import (CF_ROWS, IS_ROWS, chart_payload, get_scan, health_action,
                              jsonable, statement_series, submit_job, swap_candidates,
                              us_market_open, JOBS)


# ── jsonable ──

def test_jsonable_numpy_and_nan():
    out = jsonable({"a": np.float64(1.5), "b": np.int64(7), "c": float("nan"),
                    "d": np.bool_(True), "e": [np.float64("inf"), 2.0]})
    assert out == {"a": 1.5, "b": 7, "c": None, "d": True, "e": [None, 2.0]}


def test_jsonable_dataclass_and_timestamp():
    @dataclass
    class Sig:
        ticker: str
        score: float

    out = jsonable({"sig": Sig("NVDA", 88.5), "ts": pd.Timestamp("2026-06-10")})
    assert out["sig"] == {"ticker": "NVDA", "score": 88.5}
    assert out["ts"].startswith("2026-06-10")


# ── statement_series ──

def _stmt_df():
    cols = [pd.Timestamp("2025-12-31"), pd.Timestamp("2024-12-31")]
    return pd.DataFrame(
        {cols[0]: [100.0, -40.0, np.nan], cols[1]: [90.0, -35.0, 55.0]},
        index=["Operating Cash Flow", "Capital Expenditure", "Free Cash Flow"])


def test_statement_series_extracts_and_handles_nan():
    out = statement_series(_stmt_df(), CF_ROWS)
    assert out["operating"] == {"2025-12-31": 100.0, "2024-12-31": 90.0}
    assert out["capex"]["2025-12-31"] == -40.0
    assert out["free_cash_flow"] == {"2025-12-31": None, "2024-12-31": 55.0}
    assert out["investing"] == {}          # 缺科目 → 空 dict,不炸


def test_statement_series_label_fallback():
    df = pd.DataFrame({pd.Timestamp("2025-12-31"): [500.0]},
                      index=["Total Cash From Operating Activities"])  # 舊版 yfinance label
    assert statement_series(df, CF_ROWS)["operating"] == {"2025-12-31": 500.0}


def test_statement_series_empty_input():
    assert statement_series(None, IS_ROWS) == {k: {} for k in IS_ROWS}
    assert statement_series(pd.DataFrame(), IS_ROWS) == {k: {} for k in IS_ROWS}


# ── chart_payload(monkeypatched lake)──

def test_chart_payload_shapes(monkeypatch):
    import sharks.scoring.ma_scanner as M
    n = 300
    close = pd.Series(np.linspace(50, 120, n), index=pd.bdate_range("2025-01-02", periods=n))
    df = pd.DataFrame({"Open": close, "High": close * 1.01, "Low": close * 0.99,
                       "Close": close, "Volume": pd.Series(1e6, index=close.index)})
    monkeypatch.setattr(M, "load_lake_prices", lambda t, lake=None: df)
    out = chart_payload("FAKE", bars=100)
    assert len(out["dates"]) == len(out["close"]) == len(out["ma20"]) == len(out["rsi"]) == 100
    assert out["volume"][0] == 1_000_000
    assert out["ma200"][0] is not None     # 300 根後段已有 MA200
    assert isinstance(out["dates"][0], str)


def test_chart_payload_missing_ticker(monkeypatch):
    import sharks.scoring.ma_scanner as M
    monkeypatch.setattr(M, "load_lake_prices", lambda t, lake=None: None)
    assert chart_payload("NOPE") is None


# ── scan cache(monkeypatched scan_lake)──

def test_get_scan_caches_and_forces(monkeypatch):
    import sharks.scoring.ma_scanner as M
    import sharks.ui.server as S
    calls = {"n": 0}

    def fake_scan(tickers=None, lake=None):
        calls["n"] += 1
        return {"as_of": "2026-06-10", "rows": {}, "sector_breadth": {}}

    monkeypatch.setattr(M, "scan_lake", fake_scan)
    monkeypatch.setitem(S._scan_cache, "report", None)
    get_scan(); get_scan()
    assert calls["n"] == 1                 # 第二次吃快取
    get_scan(force=True)
    assert calls["n"] == 2


# ── jobs ──

def test_submit_job_lifecycle():
    jid = submit_job("t-ok", lambda: {"x": 1})
    for _ in range(100):
        if JOBS[jid]["status"] != "running":
            break
        time.sleep(0.02)
    assert JOBS[jid]["status"] == "done" and JOBS[jid]["result"] == {"x": 1}

    jid2 = submit_job("t-err", lambda: 1 / 0)
    for _ in range(100):
        if JOBS[jid2]["status"] != "running":
            break
        time.sleep(0.02)
    assert JOBS[jid2]["status"] == "error" and "ZeroDivisionError" in JOBS[jid2]["error"]


# ── 持股健檢決策(純函式)──

def test_health_leveraged_sell_swaps_to_underlying():
    h = {"name": "Direxion Daily MSFT Bull 2X", "leveraged_of": "MSFT"}
    a = {"reviewed_verdict": "SELL", "leveraged_scorer": {"annual_decay_pct": 20.2}}
    res = health_action(h, a, None, None)
    assert res["action"] == "換股"
    assert res["swap_to_underlying"] is True
    assert any("MSFT" in r for r in res["reasons"])


def test_health_trim_keeps_trailing_stop_note():
    h = {"name": "GraniteShares 2x CRWV Daily", "leveraged_of": "CRWV"}
    a = {"reviewed_verdict": "TRIM-PARTIAL+TRAIL",
         "review": {"flips_to_sell_when": "underlying rolls over"}}
    res = health_action(h, a, None, None)
    assert res["action"] == "減碼"
    assert any("翻空條件" in r for r in res["reasons"])


def test_health_hold_upgrades_to_warning_on_rejection_or_hot_rsi():
    h = {"name": "Enphase", "leveraged_of": None}
    a = {"verdict": "HOLD", "rationale": "neutral FOM"}
    ok = {"rejection_bar": False, "rsi": 55, "above_ma50": True, "aligned": True, "riding": True}
    assert health_action(h, a, ok, None)["action"] == "續抱"
    rej = {**ok, "rejection_bar": True}
    assert health_action(h, a, rej, None)["action"] == "續抱⚠"
    hot = {**ok, "rsi": 83}
    assert health_action(h, a, hot, None)["action"] == "續抱⚠"


def test_health_tbd_holding_blocks_action():
    h = {"name": "TBD — 疑為 2x NXPI,待驗證", "leveraged_of": None}
    res = health_action(h, {"verdict": "HOLD"}, None, None)
    assert res["action"] == "待驗證"


def test_swap_candidates_filters_and_ranks():
    rows = {
        "AAA": {"sector": "Technology", "aligned": True, "riding": True,
                "rejection_bar": False, "above_ma50": True, "dist_52w_high_pct": -1.0, "rsi": 60},
        "BBB": {"sector": "Technology", "aligned": True, "riding": True,
                "rejection_bar": True, "above_ma50": True, "dist_52w_high_pct": -0.5, "rsi": 60},
        "CCC": {"sector": "Healthcare", "aligned": True, "riding": True,
                "rejection_bar": False, "above_ma50": True, "dist_52w_high_pct": -2.0, "rsi": 55},
        "DDD2": {"sector": "Technology", "aligned": True, "riding": True,
                 "rejection_bar": False, "above_ma50": True, "dist_52w_high_pct": -8.0, "rsi": 50},
    }
    out = swap_candidates("Technology", rows, exclude={"ZZZ"})
    tk = [c["ticker"] for c in out]
    assert tk == ["AAA", "DDD2"]          # BBB 拒絕棒被濾掉;CCC 板塊不符;依距高排序
    assert swap_candidates("Technology", rows, exclude={"AAA", "DDD2"}) == []


# ── 今日推薦來源選擇 ──

def _reco_tree(tmp_path):
    wiki = tmp_path / "wiki" / "05_recommendations"
    out = tmp_path / "outputs"
    wiki.mkdir(parents=True)
    out.mkdir()
    return wiki, out


def test_latest_reco_canonical_beats_older_legacy(tmp_path):
    from sharks.ui.server import latest_reco_file
    wiki, out = _reco_tree(tmp_path)
    (out / "daily-reco-2026-06-10.md").write_text("legacy", encoding="utf-8")
    (wiki / "2026-06-12.md").write_text("canonical", encoding="utf-8")
    (wiki / "2026-05-29-fom-monthly.md").write_text("專題頁不參賽", encoding="utf-8")
    (wiki / "README.md").write_text("readme", encoding="utf-8")
    (wiki / "archive.md").write_text("archive", encoding="utf-8")
    assert latest_reco_file(tmp_path).name == "2026-06-12.md"


def test_latest_reco_newer_legacy_wins_same_day_prefers_canonical(tmp_path):
    from sharks.ui.server import latest_reco_file
    wiki, out = _reco_tree(tmp_path)
    (wiki / "2026-06-12.md").write_text("canonical", encoding="utf-8")
    (out / "daily-reco-2026-06-13.md").write_text("較新的舊家族", encoding="utf-8")
    assert latest_reco_file(tmp_path).name == "daily-reco-2026-06-13.md"
    (wiki / "2026-06-13.md").write_text("同日 canonical", encoding="utf-8")
    assert latest_reco_file(tmp_path).name == "2026-06-13.md"


def test_latest_reco_empty_returns_none(tmp_path):
    from sharks.ui.server import latest_reco_file
    assert latest_reco_file(tmp_path) is None


def test_strip_frontmatter():
    from sharks.ui.server import strip_frontmatter
    md = "---\ntype: recommendation\ntags: [a, b]\n---\n\n# Daily\n內文"
    out = strip_frontmatter(md)
    assert "type: recommendation" not in out and "# Daily" in out
    assert strip_frontmatter("# 無 frontmatter\n---\n分隔線留著") == "# 無 frontmatter\n---\n分隔線留著"


# ── misc ──

def test_us_market_open_returns_bool():
    assert isinstance(us_market_open(), bool)


def test_build_app_constructs():
    from sharks.ui.server import build_app
    app = build_app()
    paths = {r.path for r in app.routes if hasattr(r, "path")}
    assert {"/", "/api/scan", "/api/jobs"} <= paths
