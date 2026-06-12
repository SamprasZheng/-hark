"""World Backfill 測試 — 合成序列 + 注入 QQQ 月線,零網路、不讀真實 lake。

涵蓋:as-of 截斷(PIT 形狀:未來列不可見)、重建 = compute_metrics(全序列)
於最後時點、事件列 vintage 標籤、事件只在該月命中、前瞻研究手算對照、
空序列誠實降級、lake 快照挑選(空快照跳過)、月末日期產生(閏年)。
"""

from __future__ import annotations

import json

import pandas as pd

from sharks.data.world_indicators import _stamp
from sharks.regime.world_backfill import (VINTAGE, backfill_events,
                                          event_forward_study, load_world_lake,
                                          month_end_dates,
                                          reconstruct_metrics_asof,
                                          recent_daily_dates, truncate_series)
from sharks.regime.world_monitor import compute_metrics


# ── 合成數據 ──

def _monthly_rows(series_id, values, start_year=1990):
    pairs = [(f"{start_year + i // 12}-{i % 12 + 1:02d}-01", v)
             for i, v in enumerate(values)]
    return _stamp(series_id, pairs)


def _gscpi_rows(values, start_year=1998):
    pairs = [(f"{start_year + i // 12}-{i % 12 + 1:02d}-28", v)
             for i, v in enumerate(values)]
    return _stamp("GSCPI", pairs)


def _series(gscpi_vals=None, gpr_vals=None, twn_vals=None):
    gm = {}
    if gpr_vals is not None:
        gm["GPR"] = _monthly_rows("GPR", gpr_vals)
    if twn_vals is not None:
        gm["GPRC_TWN"] = _monthly_rows("GPRC_TWN", twn_vals)
    return {"gscpi": _gscpi_rows(gscpi_vals) if gscpi_vals is not None else None,
            "gpr_monthly": gm, "gpr_daily": {}}


CONFIG = {
    "version": 1,
    "events": [
        {"id": "GPR_EXTREME", "severity": "high",
         "condition": {"any": [{"metric": "gpr", "op": ">=", "value": 330}]},
         "impact": {}},
        {"id": "GSCPI_SPIKE", "severity": "med-high",
         "condition": {"any": [{"metric": "gscpi", "op": ">=", "value": 1.5}]},
         "impact": {}},
    ],
}


def _qqq(closes, start="2000-01-01"):
    idx = pd.date_range(start, periods=len(closes), freq="MS")
    return pd.DataFrame({"Close": closes}, index=idx)


# ── 截斷(PIT 形狀)──

class TestTruncation:
    def test_no_future_rows_leak(self):
        s = _series(gpr_vals=[100.0] * 24 + [400.0])     # 尖峰在 1992-01
        t = truncate_series(s, "1991-12-31")
        dates = [r["date"] for r in t["gpr_monthly"]["GPR"]]
        assert max(dates) <= "1991-12-31" and len(dates) == 24

    def test_metrics_asof_before_spike_do_not_see_it(self):
        gpr = [100.0] * 24 + [400.0]
        s = _series(gpr_vals=gpr)
        m_before = reconstruct_metrics_asof(s, "1991-12-31")
        m_at = reconstruct_metrics_asof(s, "1992-01-31")
        assert m_before["gpr"] == 100.0                   # 未來尖峰不可見
        assert m_at["gpr"] == 400.0

    def test_reconstruction_at_last_date_matches_full_compute(self):
        s = _series(gscpi_vals=[0.1 * i for i in range(30)],
                    gpr_vals=[100.0 + i for i in range(80)],
                    twn_vals=[0.05 + 0.001 * i for i in range(80)])
        full = compute_metrics(s["gscpi"], s["gpr_monthly"], s["gpr_daily"] or None,
                               manual_flags={})
        recon = reconstruct_metrics_asof(s, "2099-12-31")
        assert recon == full


# ── 事件回填 ──

class TestBackfillEvents:
    def test_rows_carry_vintage_and_fire_only_when_visible(self):
        gpr = [100.0] * 24 + [400.0] + [100.0]            # 尖峰僅 1992-01
        s = _series(gpr_vals=gpr)
        dates = ["1991-12-31", "1992-01-31", "1992-02-29"]
        rows = backfill_events(s, dates, CONFIG)
        assert [r["vintage"] for r in rows] == [VINTAGE] * 3
        assert [r["as_of"] for r in rows] == dates
        assert rows[0]["events"] == []                    # 尖峰前不命中
        assert rows[1]["events"] == ["GPR_EXTREME"]       # 尖峰月命中
        assert rows[2]["events"] == []                    # 回落即退場
        assert rows[1]["metrics"]["gpr"] == 400.0
        assert "gscpi" in rows[1]["degraded_metrics"]     # 缺源記 degraded,不發明

    def test_empty_series_degrades_honestly(self):
        s = {"gscpi": None, "gpr_monthly": {}, "gpr_daily": {}}
        rows = backfill_events(s, ["2020-01-31"], CONFIG)
        assert rows[0]["events"] == []
        assert all(v is None for v in rows[0]["metrics"].values())
        assert reconstruct_metrics_asof(s, "2020-01-31") == {}


# ── 前瞻研究(手算對照)──

class TestForwardStudy:
    def test_hand_computed_returns(self):
        # QQQ 每月 +10%:fwd 1m = 10%、3m = 33.1%、6m = 77.156%
        closes = [100.0 * (1.1 ** i) for i in range(10)]
        qqq = _qqq(closes, start="2000-01-01")
        rows = [{"as_of": f"2000-{m:02d}-28", "events": ["GPR_EXTREME"] if m <= 2 else [],
                 "metrics": {}, "vintage": VINTAGE} for m in range(1, 11)]
        study = event_forward_study(rows, qqq, event_ids=("GPR_EXTREME",))
        e = study["events"]["GPR_EXTREME"]
        assert e["months_fired"] == 2
        assert e["first_fired"] == "2000-01-28" and e["last_fired"] == "2000-02-28"
        assert e["fwd"]["1m"] == {"n": 2, "median_pct": 10.0, "mean_pct": 10.0}
        assert e["fwd"]["3m"]["median_pct"] == 33.1
        assert e["fwd"]["6m"]["median_pct"] == 77.16
        # base rate:10 個月都映射;1m 有 9 格、3m 7 格、6m 4 格
        assert study["base_rate"]["n_months"] == 10
        assert study["base_rate"]["fwd"]["1m"]["n"] == 9
        assert study["base_rate"]["fwd"]["3m"]["n"] == 7
        assert study["base_rate"]["fwd"]["6m"]["n"] == 4

    def test_conditional_vs_base_distinguishes(self):
        # 事件月之後 -50%,其餘月 +10% → 條件式 1m 中位數 = -50%,base 混合
        closes = [100.0, 110.0, 55.0, 60.5, 66.55]
        qqq = _qqq(closes, start="2010-01-01")
        rows = [{"as_of": "2010-01-31", "events": [], "metrics": {}, "vintage": VINTAGE},
                {"as_of": "2010-02-28", "events": ["GSCPI_SPIKE"], "metrics": {},
                 "vintage": VINTAGE},
                {"as_of": "2010-03-31", "events": [], "metrics": {}, "vintage": VINTAGE},
                {"as_of": "2010-04-30", "events": [], "metrics": {}, "vintage": VINTAGE}]
        study = event_forward_study(rows, qqq, horizons=(1,),
                                    event_ids=("GSCPI_SPIKE",))
        e = study["events"]["GSCPI_SPIKE"]
        assert e["fwd"]["1m"] == {"n": 1, "median_pct": -50.0, "mean_pct": -50.0}
        assert study["base_rate"]["fwd"]["1m"]["n"] == 4
        assert study["base_rate"]["fwd"]["1m"]["median_pct"] == 10.0

    def test_event_never_fired_gets_zero_row(self):
        qqq = _qqq([100.0, 110.0, 121.0])
        rows = [{"as_of": "2000-01-31", "events": [], "metrics": {},
                 "vintage": VINTAGE}]
        study = event_forward_study(rows, qqq, event_ids=("TS_HIGH",))
        e = study["events"]["TS_HIGH"]
        assert e["months_fired"] == 0 and e["first_fired"] is None
        assert e["fwd"]["1m"] == {"n": 0, "median_pct": None, "mean_pct": None}

    def test_missing_qqq_returns_honest_none(self):
        study = event_forward_study([], None)
        assert study["base_rate"] is None and study["events"] is None


# ── lake 快照挑選 ──

class TestLoadWorldLake:
    def test_skips_empty_snapshot_falls_back_to_previous(self, tmp_path):
        good = _gscpi_rows([1.0, 1.2])
        (tmp_path / "gscpi-2026-06-10.json").write_text(json.dumps(
            {"retrieved_at": "2026-06-10T00:00:00+00:00", "series": good}),
            encoding="utf-8")
        (tmp_path / "gscpi-2026-06-12.json").write_text(json.dumps(
            {"retrieved_at": "2026-06-12T00:00:00+00:00", "series": []}),
            encoding="utf-8")
        (tmp_path / "gpr_monthly-2026-06-12.json").write_text(json.dumps(
            {"retrieved_at": "x", "series": {"GPR": _monthly_rows("GPR", [100.0])}}),
            encoding="utf-8")
        out = load_world_lake(tmp_path)
        assert out["gscpi"] == good                       # 空快照跳過,退 06-10
        assert out["snapshot_dates"]["gscpi"] == "2026-06-10"
        assert out["snapshot_dates"]["gpr_monthly"] == "2026-06-12"
        assert out["gpr_daily"] is None                   # 缺源 → None,不發明
        assert out["snapshot_dates"]["gpr_daily"] is None

    def test_latest_nonempty_wins(self, tmp_path):
        for d, v in (("2026-06-10", 1.0), ("2026-06-12", 2.0)):
            (tmp_path / f"gscpi-{d}.json").write_text(json.dumps(
                {"retrieved_at": d, "series": _gscpi_rows([v])}), encoding="utf-8")
        out = load_world_lake(tmp_path)
        assert out["gscpi"][-1]["value"] == 2.0
        assert out["snapshot_dates"]["gscpi"] == "2026-06-12"


# ── 日期產生 ──

class TestDates:
    def test_month_end_dates_with_leap_year(self):
        dates = month_end_dates("1999-11", "2000-03")
        assert dates == ["1999-11-30", "1999-12-31", "2000-01-31",
                         "2000-02-29", "2000-03-31"]      # 2000 閏年

    def test_recent_daily_dates(self):
        dates = recent_daily_dates(3, "2026-06-12")
        assert dates == ["2026-06-10", "2026-06-11", "2026-06-12"]
