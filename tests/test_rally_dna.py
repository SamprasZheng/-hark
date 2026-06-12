"""Tests for rally_dna — synthetic monthly series, no disk/network."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from sharks.backtest.rally_dna import (blowoff_flags, classify_states4, discover_bull_cases,
                                       dna_features, dna_trigger, entry_evidence,
                                       regime_markov4, regime_monte_carlo, td_setup_counts)
from sharks.scoring.reflexivity import reflexivity_state


def _mdf(close, volume=None) -> pd.DataFrame:
    close = pd.Series(close, dtype=float)
    idx = pd.date_range("2015-01-31", periods=len(close), freq="ME")
    close.index = idx
    vol = pd.Series(volume, index=idx, dtype=float) if volume is not None \
        else pd.Series(1e6, index=idx)
    return pd.DataFrame({"Open": close.shift(1).fillna(close.iloc[0]), "High": close * 1.02,
                         "Low": close * 0.98, "Close": close, "Volume": vol})


def test_td_setup_counts_reaches_nine_on_monotonic_rise():
    c = pd.Series(np.linspace(10, 50, 20))
    cnt = td_setup_counts(c, "sell")
    # 前 4 根無比較基準;第 5 根起連續 close>close[-4] → 第 13 根(index 12)達 9
    assert int(cnt.iloc[12]) == 9
    assert int(cnt.max()) == 16
    assert td_setup_counts(c, "buy").max() == 0


def test_blowoff_flag_fires_on_parabolic():
    flat = np.full(24, 100.0)
    para = 100 * (1.18 ** np.arange(1, 9))      # 8 個月 ×1.18 ≈ 6 個月 +170%
    f = blowoff_flags(_mdf(np.concatenate([flat, para])))
    assert bool(f.iloc[-1])
    assert not f.iloc[:24].any()


def test_dna_trigger_fires_after_crash_base_recovery():
    # 漲到 100 → 崩 -60% → 低檔盤整 → 放量站回 MA10 連兩月收高
    up = np.linspace(50, 100, 24)
    crash = np.linspace(100, 40, 8)
    base = np.full(10, 40.0) + np.random.default_rng(1).normal(0, 0.5, 10)
    rec = np.array([44, 49, 55, 62, 70])
    c = np.concatenate([up, crash, base, rec])
    vol = np.concatenate([np.full(42, 1e6), np.full(5, 2.5e6)])   # 回升段放量
    trig = dna_trigger(_mdf(c, volume=vol))
    assert bool(trig.tail(4).any())              # 回升放量段觸發
    assert not trig.iloc[:32].any()              # 上漲與崩跌途中不觸發


def test_dna_trigger_silent_without_kill():
    # 從未被殺 ≥55% 的穩定上升 → 永不觸發(這是「曾被錯殺」的修復訊號)
    trig = dna_trigger(_mdf(np.linspace(50, 150, 60)))
    assert not trig.any()


def test_classify_states4_labels():
    # 平穩漲(bull)→ 12 個月 +35%+(mania)→ 高波動崩(crisis/bear)
    calm = 100 * (1.01 ** np.arange(80))
    para = calm[-1] * (1.06 ** np.arange(1, 13))         # 12 月 +100% → mania
    rng = np.random.default_rng(3)
    crash = para[-1] * np.cumprod(1 + rng.normal(-0.10, 0.12, 10))
    arr = np.concatenate([calm, para, crash])
    close = pd.Series(arr, index=pd.date_range("2010-01-31", periods=len(arr), freq="ME"))
    st = classify_states4(close)
    assert st.iloc[60] == "bull"
    assert st.iloc[91] == "mania"
    assert st.iloc[-1] in ("crisis", "bear")             # 高波動崩跌段


def test_regime_markov4_outputs():
    rng = np.random.default_rng(11)
    close = pd.Series(100 * np.cumprod(1 + rng.normal(0.008, 0.05, 280)),
                      index=pd.date_range("2003-01-31", periods=280, freq="ME"))
    out = regime_markov4(pd.DataFrame({"Close": close}), months_ahead=12, n_paths=400, seed=5)
    assert out["current_state"] in out["states"]
    for a, row in out["transition_matrix"].items():
        s = sum(row.values())
        assert s == 0 or abs(s - 1.0) < 0.01             # 每列轉移機率合 1(或無樣本)


def test_entry_evidence_counts():
    crash = np.concatenate([np.linspace(100, 100, 24), np.linspace(100, 40, 10),
                            np.full(12, 40.0), [44, 48]])
    vol = np.concatenate([np.full(34, 2e6), np.full(14, 8e5)])   # 後段量縮
    ev = entry_evidence(_mdf(crash, volume=vol), len(crash) - 1)
    assert ev["deep_kill"] is True                        # -60% 深殺
    assert ev["vol_contract"] is True
    assert ev["n_evidence"] >= 2


def test_discover_bull_cases_finds_crash_recovery():
    # WINNER:殺 -60% → 谷底 → 24 個月 +200%;FLAT:無事件
    up = np.linspace(50, 100, 30)
    crash = np.linspace(100, 40, 8)
    base = np.full(6, 40.0)
    rec = 40 * (1.06 ** np.arange(1, 25))
    winner = _mdf(np.concatenate([up, crash, base, rec]))
    flat = _mdf(np.full(70, 100.0))
    frames = {"WINNER": winner, "FLAT": flat}
    lib = discover_bull_cases(["WINNER", "FLAT"],
                              loader=lambda t: frames[t],
                              sector_of=lambda t: "Technology")
    assert lib["n_cases"] >= 1
    tks = {c["ticker"] for c in lib["cases"]}
    assert "WINNER" in tks and "FLAT" not in tks
    assert lib["centroid_all"]                       # 質心存在且含特徵
    assert lib["cases"][0]["gain_24m_pct"] >= 100


def test_dna_features_on_killed_recovery():
    crash = np.concatenate([np.linspace(100, 100, 30), np.linspace(100, 40, 10),
                            np.full(8, 40.0), [44, 48, 53]])
    f = dna_features(_mdf(crash), len(crash) - 1)
    assert f["dd_min18"] <= -0.55                  # 曾深殺
    assert f["dist_ma10"] > 0                      # 已站回 MA10 上
    assert f["r3m"] > 0.2                          # 3 月修復動能
    assert dna_features(_mdf(crash), 10) is None   # 樣本不足回 None


def test_apply_rules_engine():
    from sharks.backtest.rally_dna import apply_rules
    rules = [{"id": "r1", "when": {"reflexivity": "斷裂警告"}, "then": {"bucket": "剔除"}},
             {"id": "r2", "when": {"reflexivity": "斷裂警告", "pit_fundamental_contested": True},
              "then": {"human_review": True}},
             {"id": "r3", "when": {"market_state": "mania", "bucket": "可入候補"},
              "then": {"bucket": "watch"}}]
    # 斷裂 + PIT 翻案 → 剔除 + human_review,兩條都 fire
    r = apply_rules({"reflexivity": "斷裂警告", "pit_fundamental_contested": True,
                     "bucket": "watch"}, {"market_state": "bull"}, rules)
    assert r["bucket"] == "剔除" and r["human_review"] is True
    assert r["rules_fired"] == ["r1", "r2"]
    # mania 降級可入候補(ctx 提供 market_state)
    r2 = apply_rules({"reflexivity": "回饋健康", "bucket": "可入候補"},
                     {"market_state": "mania"}, rules)
    assert r2["bucket"] == "watch"
    # 無匹配 → 原樣
    r3 = apply_rules({"reflexivity": "回饋健康", "bucket": "觀察"}, {"market_state": "bull"}, rules)
    assert "rules_fired" not in r3


def test_pit_merger_fills_fcf_from_yfinance():
    from sharks.data.pit_merger import merge_rows, pit_contested
    poly = [{"fiscal": "2026Q1", "end_date": "2026-03-31", "filing_date": "2026-04-29",
             "revenue": 1200.0, "rev_yoy_pct": 20.0, "ocf": 300.0, "capex": None, "fcf": None},
            {"fiscal": "2025Q1", "end_date": "2025-03-31", "filing_date": "2025-04-30",
             "revenue": 1000.0, "rev_yoy_pct": None, "ocf": 100.0, "capex": None, "fcf": None}]
    yf = {"2026-03-29": {"capex": -40.0, "fcf": 260.0}}      # ±10 天容忍內
    out = merge_rows(poly, yf)
    assert out[0]["fcf"] == 260.0 and out[0]["fcf_source"] == "yfinance"
    assert out[0]["ocf_improving_yoy"] is True               # 300 vs 100(同季前年)
    assert out[1]["fcf"] is None and out[1]["fcf_source"] is None
    assert pit_contested(out) is True                        # rev_yoy>0 + OCF 改善 → 翻案爭議


def test_reflexivity_state_tiers():
    base = dict(dist_52w_high_pct=-1.0)
    assert reflexivity_state(**base, inst_trans=-2.0, insider_trans=0.0,
                             fcf_yoy_pct=-5.0)["verdict"] == "斷裂警告"
    assert reflexivity_state(**base, inst_trans=-2.0, insider_trans=0.0,
                             fcf_yoy_pct=None)["verdict"] == "背離觀察"
    assert reflexivity_state(**base, inst_trans=3.0, insider_trans=0.0,
                             fcf_yoy_pct=None)["verdict"] == "回饋健康"
    assert reflexivity_state(**base, inst_trans=None, insider_trans=None,
                             fcf_yoy_pct=None)["verdict"] == "數據缺"
    assert reflexivity_state(dist_52w_high_pct=-30.0, inst_trans=-5.0,
                             insider_trans=-20.0, fcf_yoy_pct=-9.0)["verdict"].startswith("n/a")


def test_regime_monte_carlo_shapes_and_reproducible():
    rng = np.random.default_rng(7)
    r = rng.normal(0.01, 0.05, 260)
    close = pd.Series(100 * np.cumprod(1 + r),
                      index=pd.date_range("2004-01-31", periods=260, freq="ME"))
    df = pd.DataFrame({"Close": close})
    a = regime_monte_carlo(df, months_ahead=12, n_paths=500, seed=9)
    b = regime_monte_carlo(df, months_ahead=12, n_paths=500, seed=9)
    assert a == b                                 # seed 固定 → 可重現
    assert a["current_state"] in ("bull", "bear")
    assert 0 <= a["mc_p_end_positive"] <= 100
    assert 0 <= a["transition"]["bull_stay"] <= 100
