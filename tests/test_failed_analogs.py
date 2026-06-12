"""Tests for failed_analogs — synthetic series, no disk/network."""

from __future__ import annotations

import numpy as np
import pandas as pd

from sharks.backtest.failed_analogs import cap_recommendation, classify_outcome, deepkill_ledger


def _fwd(vals):
    return pd.Series(vals, dtype=float)


def test_classify_outcome_tiers():
    assert classify_outcome(100, _fwd([120, 180, 210, 150]))["outcome"] == "monster"   # 高點 +110%
    assert classify_outcome(100, _fwd([110, 135, 120]))["outcome"] == "ok"             # 高點 +35%
    assert classify_outcome(100, _fwd([105, 95, 90, 85]))["outcome"] == "dud"          # 死水
    assert classify_outcome(100, _fwd([90, 70, 45, 50]))["outcome"] == "disaster"      # max_dd -55%
    assert classify_outcome(100, _fwd([110, 80, 55]))["outcome"] == "disaster"         # 終點 -45%
    assert classify_outcome(0, _fwd([1]))["outcome"] == "no_data"


def test_deepkill_ledger_with_failed_loader():
    # WINNER:深殺→觸發→兩年十倍;LOSER:深殺→觸發→再崩(失敗類比)
    def series(rec_mult):
        up = np.linspace(50, 100, 30)
        crash = np.linspace(100, 35, 10)
        base = np.full(8, 35.0)
        rec = 35 * np.linspace(1.0, 1.45, 4)          # 觸發段(站回 MA10 + 連 2 月高)
        after = rec[-1] * np.array(rec_mult)
        c = np.concatenate([up, crash, base, rec, after])
        idx = pd.date_range("2015-01-31", periods=len(c), freq="ME")
        vol = np.concatenate([np.full(48, 1e6), np.full(4, 3e6), np.full(len(after), 2e6)])
        return pd.DataFrame({"Open": np.r_[c[0], c[:-1]], "High": c * 1.02, "Low": c * 0.98,
                             "Close": c, "Volume": vol}, index=idx)

    frames = {"WIN": series(list(np.linspace(1.1, 4.0, 26))),
              "LOSE": series(list(np.linspace(0.9, 0.3, 26)))}
    led = deepkill_ledger(["WIN", "LOSE"], loader=lambda t: frames[t])
    by = {r["ticker"]: r["outcome"] for r in led}
    assert by.get("WIN") == "monster"
    assert by.get("LOSE") == "disaster"


def test_bootstrap_survival_reproducible_and_ordered():
    from sharks.backtest.failed_analogs import bootstrap_survival
    ledger = ([{"end_ret_pct": 150.0, "outcome": "monster"}] * 30
              + [{"end_ret_pct": -50.0, "outcome": "disaster"}] * 10)
    a = bootstrap_survival(ledger, n_boot=2000, seed=7)
    b = bootstrap_survival(ledger, n_boot=2000, seed=7)
    assert a == b                                        # seed 固定可重現
    lo, hi = a["survival_pct"]["ci90"]
    assert lo <= a["survival_pct"]["point"] <= hi        # CI 包住點估計
    assert a["survival_pct"]["point"] == 75.0
    assert a["p_loss_pct_ci95_high"] >= 25.0             # 悲觀端 ≥ 樣本值


def test_cap_recommendation_formula():
    ledger = ([{"end_ret_pct": -30.0}] * 5 + [{"end_ret_pct": 80.0}] * 5)
    rec = cap_recommendation(ledger)
    # P(損)=50%、|平均損|=30% → cap = 2%/(0.5×0.3) = 13.3%;壓力版更低
    assert rec["p_loss"] == 50.0
    assert rec["cap_pct"] == 13.3
    assert rec["cap_stress_pct"] < rec["cap_pct"]
    assert 5.0 <= rec["recommended"] <= 15.0
