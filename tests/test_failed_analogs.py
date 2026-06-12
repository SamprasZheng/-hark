"""Tests for failed_analogs — synthetic series, no disk/network."""

from __future__ import annotations

import numpy as np
import pandas as pd

from sharks.backtest.failed_analogs import (_candidate_queue, _load_curated,
                                            cap_recommendation, classify_outcome,
                                            deepkill_ledger, prioritize_candidates,
                                            reset_thin_manifest)

CURATED_YAML = """as_of: 2026-06-12
candidates:
  - ticker: BBBY
    delisted: 2023
    type: bankruptcy
    why: 教科書案例
  - ticker: SIVB
    delisted: 2023
"""


class TestCuratedQueue:
    def test_load_curated_parses_ticker_and_year(self, tmp_path):
        p = tmp_path / "c.yaml"
        p.write_text(CURATED_YAML, encoding="utf-8")
        out = _load_curated(p)
        assert [c["ticker"] for c in out] == ["BBBY", "SIVB"]
        assert out[0]["delisted_utc"] == "2023-01-01" and out[0]["curated"] is True

    def test_load_curated_missing_file(self, tmp_path):
        assert _load_curated(tmp_path / "nope.yaml") == []

    def test_curated_jump_queue_and_done_filter(self, tmp_path):
        p = tmp_path / "c.yaml"
        p.write_text(CURATED_YAML, encoding="utf-8")
        fetch = lambda: [{"ticker": "ZZZZ", "name": "Real Co",
                          "delisted_utc": "2015-06-01"},
                         {"ticker": "BBBY", "name": "dup in feed",
                          "delisted_utc": "2023-05-01"}]
        q = _candidate_queue({"SIVB"}, fetch_fn=fetch, curated_path=p)
        assert [c["ticker"] for c in q] == ["BBBY", "ZZZZ"]   # curated 先、done 濾、feed 去重


class TestResetThinManifest:
    def test_keeps_ok_archives_rest(self, tmp_path):
        import json as _json
        m = tmp_path / "failed-manifest.jsonl"
        lines = [_json.dumps({"ticker": "GOOD", "status": "ok", "bars": 120}),
                 _json.dumps({"ticker": "ABMD", "status": "too_short"}),
                 _json.dumps({"ticker": "XERR", "status": "err:http 500"}),
                 "not-json-garbage"]
        m.write_text("\n".join(lines) + "\n", encoding="utf-8")
        res = reset_thin_manifest(m)
        assert res == {"kept": 1, "archived": 3}
        kept = [_json.loads(x) for x in m.read_text(encoding="utf-8").splitlines()]
        assert [k["ticker"] for k in kept] == ["GOOD"]
        arch = list(tmp_path.glob("failed-manifest.archive-*.jsonl"))
        assert len(arch) == 1
        assert "ABMD" in arch[0].read_text(encoding="utf-8")

    def test_missing_manifest_noop(self, tmp_path):
        res = reset_thin_manifest(tmp_path / "nope.jsonl")
        assert res["kept"] == 0 and res["archived"] == 0


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


# ── Phase 2 候選重排(prioritize_candidates / _candidate_queue)──

def _c(ticker, name=None, delisted=None):
    return {"ticker": ticker, "name": name, "delisted_utc": delisted}


def test_prioritize_shell_names_deprioritized():
    # 殼公司字樣(不分大小寫)墊後;真公司提前
    cands = [_c("AACQ", "Origin ACQUISITION Corp", "2016-03-01"),
             _c("OILX", "Plains Oil Exploration Inc", "2016-02-10"),
             _c("BLNK", "Star Blank Check Co", "2016-01-05")]
    out = [c["ticker"] for c in prioritize_candidates(cands)]
    assert out == ["OILX", "AACQ", "BLNK"]      # 同罰分組內保留原序


def test_prioritize_warrant_suffix_deprioritized():
    # len>=5 結尾 W/R/U(含 Polygon 小寫 w / .U)罰最重;len<5 真公司短碼不誤殺
    cands = [_c("AINCw", "Ashford Inc Wts", "2015-06-01"),
             _c("AAU", "Almaden Minerals", "2015-06-01"),
             _c("AXG.U", None, "2015-06-01"),
             _c("ACMR", "ACM Research Inc", "2015-06-01")]    # 結尾 R 但 len=4 → 不罰
    out = [c["ticker"] for c in prioritize_candidates(cands)]
    assert out == ["AAU", "ACMR", "AINCw", "AXG.U"]


def test_prioritize_year_window_preference():
    # 2012..2023(真公司死亡年代)提前;2010-11 與 2024+ 同樣不加分,同分保原序
    cands = [_c("AAAA", "Alpha Industries Inc", "2024-05-01"),
             _c("BBBB", "Beta Manufacturing Inc", "2016-03-01"),
             _c("CCCC", "Gamma Foods Inc", "2010-07-01"),
             _c("DDDD", "Delta Mining Inc", "2022-11-01")]
    out = [c["ticker"] for c in prioritize_candidates(cands)]
    assert out == ["BBBB", "DDDD", "AAAA", "CCCC"]


def test_prioritize_never_drops_and_is_stable():
    # 不丟棄只重排:集合不變;同分組內保留原始相對順序(穩定排序)
    neutral = [_c(f"N{i:03d}", "Neutral Industries Inc", "2018-01-01") for i in range(20)]
    shells = [_c(f"S{i:03d}", "Shell Acquisition Corp", "2018-01-01") for i in range(5)]
    mixed = []
    for i in range(5):
        mixed += [shells[i]] + neutral[4 * i:4 * i + 4]
    out = prioritize_candidates(mixed)
    assert sorted(c["ticker"] for c in out) == sorted(c["ticker"] for c in mixed)
    assert [c["ticker"] for c in out[:20]] == [c["ticker"] for c in neutral]
    assert [c["ticker"] for c in out[20:]] == [c["ticker"] for c in shells]


def test_prioritize_missing_fields_treated_as_no_signal():
    # 缺 name / delisted_utc → 0 分不發明值;只有有年份加分者提前,其餘保原序
    cands = [_c("AAAA"), _c("BBBB", None, "2015-01-01"), _c("CCCC", "Real Steel Inc", None)]
    out = [c["ticker"] for c in prioritize_candidates(cands)]
    assert out == ["BBBB", "AAAA", "CCCC"]


def test_candidate_queue_filters_then_prioritizes():
    # collect 的接線:fetch_fn 注入(離線)→ 過濾已收/缺 ticker/2010 前 → 重排可關
    raw = [_c("DONE", "Old Done Corp", "2018-01-01"),        # 已在 manifest → 濾掉
           _c("OLDY", "Ancient Industries", "2008-01-01"),   # 2010 前下市 → 濾掉
           _c(None, "No Ticker Corp", "2018-01-01"),         # 缺 ticker → 濾掉
           _c("SPCY", "Hot Spac Acquisition Corp", "2024-02-01"),
           _c("REAL", "Real Steel Inc", "2016-01-01")]
    q = _candidate_queue({"DONE"}, fetch_fn=lambda: raw, prioritize=True)
    assert [c["ticker"] for c in q] == ["REAL", "SPCY"]
    q_off = _candidate_queue({"DONE"}, fetch_fn=lambda: raw, prioritize=False)
    assert [c["ticker"] for c in q_off] == ["SPCY", "REAL"]  # 注入關閉:保留來源順序
