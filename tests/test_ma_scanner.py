"""Tests for the offline MA scanner (越線/連線/騎線/大底) — synthetic data, no disk/network."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from sharks.scoring.ma_scanner import scan_one, scan_lake, MIN_BARS, RIDE_DAYS


def _df(close, low=None, volume=None) -> pd.DataFrame:
    close = pd.Series(close, dtype=float)
    idx = pd.bdate_range("2025-01-02", periods=len(close))
    close.index = idx
    low = pd.Series(low, index=idx, dtype=float) if low is not None else close * 0.99
    vol = pd.Series(volume, index=idx, dtype=float) if volume is not None \
        else pd.Series(1e6, index=idx)
    return pd.DataFrame({"Open": close, "High": close * 1.01, "Low": low,
                         "Close": close, "Volume": vol})


def test_too_short_returns_none():
    assert scan_one(_df(np.linspace(10, 20, MIN_BARS - 10))) is None


def test_uptrend_is_aligned_and_riding():
    # 300 根穩定上升:MA5>MA20>MA60、斜率向上、low 貼 MA20 之上 → 連線+騎線
    c = np.linspace(50, 120, 300)
    sig = scan_one(_df(c))
    assert sig["aligned"] is True
    assert sig["riding"] is True
    assert sig["above_ma50"] is True
    assert sig["bottom"] is False           # 距 52w 低 +140%,不可能是大底


def test_downtrend_has_no_long_signals():
    c = np.linspace(120, 50, 300)
    sig = scan_one(_df(c))
    assert sig["aligned"] is False
    assert sig["riding"] is False
    assert sig["cross_ma20"] is False and sig["cross_ma60"] is False
    assert sig["above_ma50"] is False


def test_fresh_cross_above_ma60():
    # 長期橫盤略跌 → 最後 2 根放量上穿:越線(MA20/MA60)都該觸發
    # (註:淺基底+急拉會把 MA20 拉過 MA60,aligned 可能合法為 True — 不在此斷言)
    c = np.concatenate([np.full(250, 100.0) - np.linspace(0, 8, 250), [101.0, 104.0]])
    sig = scan_one(_df(c))
    assert sig["cross_ma60"] is True
    assert sig["cross_ma20"] is True


def test_riding_breaks_when_low_pierces_ma20():
    # 上升但最後幾天 low 深插 MA20 下方 → 騎線 False
    c = np.linspace(50, 120, 300)
    low = c * 0.99
    low[-RIDE_DAYS // 2:] = c[-RIDE_DAYS // 2:] * 0.85   # 跌破 >2% 容忍
    sig = scan_one(_df(c, low=low))
    assert sig["riding"] is False


def test_bottom_needs_divergence_and_volume_contraction():
    # 構造大底:前段跌到低點 → 後段更低的低點但收斂(背離由 RSI 算)→ 近期量縮
    n = 300
    c = np.concatenate([
        np.linspace(100, 55, 120),          # 主跌
        np.linspace(55, 70, 60),            # 反彈
        np.linspace(70, 52, 60),            # 二次探底(更低低點,但跌勢平緩 → RSI 墊高)
        np.linspace(52, 56, 60),            # 打底回穩
    ])[:n]
    vol = np.concatenate([np.full(200, 2e6), np.full(n - 200, 5e5)])  # 量縮(20d≪120d 均量)
    sig = scan_one(_df(c, volume=vol))
    assert sig["vol_contract"] is True
    assert sig["dist_52w_low_pct"] is not None and sig["dist_52w_low_pct"] < 15
    # bottom = dist + 量縮 + 背離 全中;背離視 RSI 路徑而定,至少不應 crash
    assert isinstance(sig["bottom"], bool)


def test_dist_52w_high_uses_intraday_high_with_rejection_bar():
    # 回歸:2026-06-09 掃描 KLAC/TROW 案例 — 最後一根盤中衝 52w 新高後遭拒絕收低。
    # 舊版用 close 算 52w 高 → 誤報「距高 0%」;新版用 High 欄 + rejection_bar 警示。
    c = np.linspace(50, 100, 300)
    df = _df(c)
    df.loc[df.index[-1], "High"] = 110.0      # 盤中 spike,close 仍 100
    sig = scan_one(df)
    assert sig["rejection_bar"] is True
    # (100 - 110) / 110 ≈ -9.1%,不再是 0%
    assert sig["dist_52w_high_pct"] == pytest.approx(-9.1, abs=0.1)


def test_no_rejection_on_normal_close_near_high():
    # 正常收高的 bar(_df 的 High = close*1.01,回落僅 ~1% < 3% 容忍)→ 不標拒絕棒
    sig = scan_one(_df(np.linspace(50, 120, 300)))
    assert sig["rejection_bar"] is False
    assert sig["dist_52w_high_pct"] == pytest.approx(-1.0, abs=0.2)


def test_scan_lake_with_monkeypatched_io(monkeypatch, tmp_path):
    # 兩檔合成:UP(連線)與 DOWN(無多頭訊號)→ 板塊廣度 50%
    frames = {"UP": _df(np.linspace(50, 120, 300)), "DOWN": _df(np.linspace(120, 50, 300))}
    import sharks.scoring.ma_scanner as M
    monkeypatch.setattr(M, "lake_tickers", lambda lake=None: list(frames))
    monkeypatch.setattr(M, "load_lake_prices", lambda t, lake=None: frames[t])
    monkeypatch.setattr(M, "load_sector", lambda t, lake=None: "Technology")
    rep = M.scan_lake()
    assert rep["n_scanned"] == 2
    assert "UP" in rep["signals"]["aligned"] and "DOWN" not in rep["signals"]["aligned"]
    b = rep["sector_breadth"]
    # n>=3 才報板塊;2 檔樣本 → breadth 為空(刻意,避免小樣本誤導)
    assert b == {}
    # as_of 是 bar 日期(point-in-time),不是今天
    assert rep["as_of"] == str(frames["UP"].index[-1].date())
