"""World Monitor 測試 — 純函式 + 注入式 fetcher,零網路零真實磁碟(tmp_path 除外)。

涵蓋:grid 解析(world_indicators 純層)、metrics 計算(z/分位/單月差)、
事件求值(any/all/缺源 degraded/手動旗)、impacts 聚合(cap 取 min、
shift 封頂 0.10)、run_world_monitor 信封(live/stale/failed)。
"""

from __future__ import annotations

import json

from sharks.data.world_indicators import parse_series_grid, _stamp
from sharks.regime.world_monitor import (aggregate_impacts, compute_metrics,
                                         eval_condition, evaluate_events,
                                         percentile_of, run_world_monitor,
                                         trailing_z)


# ── 合成數據 ──

def _rows(series_id, pairs):
    return _stamp(series_id, pairs)


def _gscpi_rows(values, start_year=2000):
    pairs = [(f"{start_year + i // 12}-{i % 12 + 1:02d}-28", v)
             for i, v in enumerate(values)]
    return _rows("GSCPI", pairs)


def _monthly(series_id, values, start_year=1985):
    pairs = [(f"{start_year + i // 12}-{i % 12 + 1:02d}-01", v)
             for i, v in enumerate(values)]
    return _rows(series_id, pairs)


# ── grid 解析(純)──

class TestParseGrid:
    def test_gscpi_grid_skips_junk_header_rows(self):
        grid = [
            [None, None, "NEW YORK FED  ECONOMIC RESEARCH"],
            ["Date", "GSCPI", None],
            [None, None, "https://www.newyorkfed.org/research"],
            ["2026-04-30", 1.823, None],
            ["2026-05-31", 1.769, None],
        ]
        out = parse_series_grid(grid, "Date", ("GSCPI",))
        assert out["GSCPI"] == [("2026-04-30", 1.823), ("2026-05-31", 1.769)]

    def test_gpr_grid_multi_column_and_missing_cells(self):
        grid = [
            ["month", "GPR", "GPRC_TWN"],
            ["2026-04-01", 250.8, 0.242],
            ["2026-05-01", 184.2, None],          # 缺值 → 該欄跳過,不發明
            ["bad-date", 99.0, 9.9],              # 壞日期 → 整列跳過
        ]
        out = parse_series_grid(grid, "month", ("GPR", "GPRC_TWN"))
        assert out["GPR"] == [("2026-04-01", 250.8), ("2026-05-01", 184.2)]
        assert out["GPRC_TWN"] == [("2026-04-01", 0.242)]

    def test_no_header_returns_empty(self):
        assert parse_series_grid([["x", "y"], [1, 2]], "Date", ("GSCPI",)) == {}

    def test_gscpi_text_dates_dd_mon_yyyy(self):
        # NY Fed 真實形狀(2026-06-12 線上驗證):日期是字串 '31-Jan-1998',非日期 cell
        grid = [
            ["Date", "GSCPI", None, None],
            [None, None, None, "NEW YORK FED  ECONOMIC RESEARCH"],
            ["31-Jan-1998", -1.1039, None, None],
            ["31-May-2026", 1.7689, None, None],
        ]
        out = parse_series_grid(grid, "Date", ("GSCPI",))
        assert out["GSCPI"] == [("1998-01-31", -1.1039), ("2026-05-31", 1.7689)]

    def test_stamp_pit_contract(self):
        rows = _stamp("GSCPI", [("2026-05-31", 1.77)])
        r = rows[0]
        assert r["as_of_timestamp"] == "2026-05-31"
        assert r["source_first_visible_at"] is None      # live 路徑不發明 vintage


# ── 統計助手(純)──

class TestStats:
    def test_percentile_of(self):
        hist = list(range(1, 101))
        assert percentile_of(hist, 95) == 95.0
        assert percentile_of([], 1.0) is None

    def test_trailing_z(self):
        flat = [1.0] * 59 + [1.0]
        assert trailing_z(flat) is None                  # sd=0 → None,不發明
        vals = [0.0] * 59 + [3.0]
        z = trailing_z(vals, 60)
        assert z is not None and z > 5                   # 突跳遠超 2σ

    def test_trailing_z_short_history(self):
        assert trailing_z([1.0, 2.0], 60) is None


# ── metrics ──

class TestComputeMetrics:
    def test_full_sources(self):
        gscpi = _gscpi_rows([0.5, 0.68, 1.82, 1.77])
        gpr = {"GPR": _monthly("GPR", [100.0] * 100 + [330.0]),
               "GPRC_TWN": _monthly("GPRC_TWN", [0.05] * 100 + [0.49])}
        daily = {"GPRD_MA30": _rows("GPRD_MA30", [("2026-06-08", 193.2)])}
        m = compute_metrics(gscpi, gpr, daily, manual_flags={"TARIFF_NEW": False})
        assert m["gscpi"] == 1.77
        assert abs(m["gscpi_delta_1m"] - (-0.05)) < 1e-9
        assert m["gpr"] == 330.0 and m["gpr_pctile"] == 100.0
        assert m["gprc_twn"] == 0.49 and m["gprc_twn_z60"] > 2.0
        assert m["gprd_ma30"] == 193.2
        assert m["manual.TARIFF_NEW"] is False

    def test_missing_sources_leave_metrics_absent(self):
        m = compute_metrics(None, None, None)
        assert "gscpi" not in m and "gpr" not in m


# ── 事件求值 ──

CONFIG = {
    "version": 1,
    "events": [
        {"id": "TS_HIGH", "severity": "high",
         "condition": {"any": [
             {"metric": "gprc_twn_z60", "op": ">=", "value": 2.0},
             {"metric": "gprc_twn", "op": ">=", "value": 0.25}]},
         "impact": {"ctx_flag": "world_event_TS_HIGH",
                    "weight_shift": {"give_to": "reflexivity", "take_from": "capital",
                                     "amount": 0.05},
                    "deepkill_cap_multiplier": 0.75, "exposure_penalty": 0.25,
                    "review_groups": ["taiwan_chain"]}},
        {"id": "GSCPI_SPIKE", "severity": "med-high",
         "condition": {"any": [
             {"metric": "gscpi", "op": ">=", "value": 1.5},
             {"all": [{"metric": "gscpi", "op": ">=", "value": 1.0},
                      {"metric": "gscpi_delta_1m", "op": ">=", "value": 0.8}]}]},
         "impact": {"ctx_flag": "world_event_GSCPI_SPIKE",
                    "weight_shift": {"give_to": "reflexivity", "take_from": "tech",
                                     "amount": 0.05},
                    "exposure_penalty": 0.10}},
        {"id": "TARIFF_NEW", "severity": "med-high",
         "condition": {"metric": "manual.TARIFF_NEW", "op": "==", "value": True},
         "impact": {"ctx_flag": "world_event_TARIFF_NEW"}},
    ],
}


class TestEvaluateEvents:
    def test_fires_on_threshold(self):
        fired, missing = evaluate_events(CONFIG, {"gprc_twn_z60": 2.24, "gscpi": 0.5})
        assert [e["id"] for e in fired] == ["TS_HIGH"]
        assert missing == ["manual.TARIFF_NEW"]          # 缺 metric 記 degraded

    def test_all_combinator(self):
        m = {"gscpi": 1.2, "gscpi_delta_1m": 1.1, "manual.TARIFF_NEW": False}
        fired, _ = evaluate_events(CONFIG, m)
        assert [e["id"] for e in fired] == ["GSCPI_SPIKE"]

    def test_manual_flag(self):
        fired, _ = evaluate_events(CONFIG, {"manual.TARIFF_NEW": True})
        assert [e["id"] for e in fired] == ["TARIFF_NEW"]

    def test_no_metrics_no_fire(self):
        fired, missing = evaluate_events(CONFIG, {})
        assert fired == [] and "gscpi" in missing

    def test_missing_metric_is_false_not_error(self):
        missing: list = []
        assert eval_condition({"metric": "nope", "op": ">=", "value": 1}, {}, missing) is False
        assert missing == ["nope"]


class TestAggregateImpacts:
    def test_min_cap_max_penalty_union_groups(self):
        fired, _ = evaluate_events(CONFIG, {"gprc_twn_z60": 3.0, "gscpi": 1.8})
        imp = aggregate_impacts(fired)
        assert imp["ctx_flags"] == {"world_event_TS_HIGH": True,
                                    "world_event_GSCPI_SPIKE": True}
        assert imp["deepkill_cap_multiplier"] == 0.75
        assert imp["exposure_penalty"] == 0.25
        assert imp["review_groups"] == ["taiwan_chain"]
        assert {(s["give_to"], s["take_from"]): s["amount"]
                for s in imp["weight_shifts"]} == {("reflexivity", "capital"): 0.05,
                                                   ("reflexivity", "tech"): 0.05}

    def test_shift_total_capped_at_010(self):
        fired = [{"id": f"E{i}", "impact": {"weight_shift":
                  {"give_to": "reflexivity", "take_from": "capital", "amount": 0.08}}}
                 for i in range(3)]
        imp = aggregate_impacts(fired)
        assert sum(s["amount"] for s in imp["weight_shifts"]) <= 0.10 + 1e-9

    def test_empty(self):
        imp = aggregate_impacts([])
        assert imp["deepkill_cap_multiplier"] is None
        assert imp["exposure_penalty"] == 0.0 and imp["weight_shifts"] == []


# ── orchestration(注入 fetchers + tmp_path)──

def _write_config(tmp_path):
    p = tmp_path / "world_events.json"
    p.write_text(json.dumps(CONFIG), encoding="utf-8")
    return p


class TestRunWorldMonitor:
    def test_live_path_writes_envelope_and_lake(self, tmp_path):
        cfg = _write_config(tmp_path)
        fetchers = {
            "gscpi": lambda: _gscpi_rows([0.5, 1.82, 1.77]),
            "gpr_monthly": lambda: {"GPR": _monthly("GPR", [100.0] * 80 + [250.0]),
                                    "GPRC_TWN": _monthly("GPRC_TWN", [0.05] * 80 + [0.49])},
            "gpr_daily": lambda: {"GPRD_MA30": _rows("GPRD_MA30", [("2026-06-08", 193.2)])},
        }
        rep = run_world_monitor(tmp_path / "outputs", today="2026-06-12",
                                fetchers=fetchers, config_path=cfg,
                                lake_dir=tmp_path / "lake")
        assert rep["live_data"] is True and rep["stale_sources"] == []
        assert "GSCPI_SPIKE" in [e["id"] for e in rep["events_triggered"]]
        assert (tmp_path / "outputs" / "world-monitor-2026-06-12.json").exists()
        assert (tmp_path / "lake" / "gscpi-2026-06-12.json").exists()
        assert rep["llm_involvement"] == "none"

    def test_stale_fallback_from_lake(self, tmp_path):
        cfg = _write_config(tmp_path)
        lake = tmp_path / "lake"
        lake.mkdir()
        (lake / "gscpi-2026-06-10.json").write_text(json.dumps(
            {"retrieved_at": "x", "series": _gscpi_rows([1.9])}), encoding="utf-8")

        def boom():
            raise RuntimeError("network down")
        fetchers = {"gscpi": boom, "gpr_monthly": boom, "gpr_daily": boom}
        rep = run_world_monitor(tmp_path / "outputs", today="2026-06-12",
                                fetchers=fetchers, config_path=cfg, lake_dir=lake)
        assert rep["live_data"] is False
        assert any(s.startswith("gscpi") for s in rep["stale_sources"])
        assert set(rep["failed_sources"]) == {"gpr_monthly", "gpr_daily"}
        assert rep["metrics"]["gscpi"] == 1.9             # 用快照值,標 stale 不發明

    def test_total_failure_never_raises(self, tmp_path):
        cfg = _write_config(tmp_path)

        def boom():
            raise RuntimeError("down")
        rep = run_world_monitor(tmp_path / "outputs", today="2026-06-12",
                                fetchers={"gscpi": boom, "gpr_monthly": boom,
                                          "gpr_daily": boom},
                                config_path=cfg, lake_dir=tmp_path / "empty-lake")
        assert rep["events_triggered"] == []
        assert set(rep["failed_sources"]) == {"gscpi", "gpr_monthly", "gpr_daily"}

    def test_lake_snapshot_immutable(self, tmp_path):
        cfg = _write_config(tmp_path)
        lake = tmp_path / "lake"
        fetchers = {"gscpi": lambda: _gscpi_rows([1.0]),
                    "gpr_monthly": lambda: {}, "gpr_daily": lambda: {}}
        run_world_monitor(tmp_path / "o", today="2026-06-12", fetchers=fetchers,
                          config_path=cfg, lake_dir=lake)
        first = (lake / "gscpi-2026-06-12.json").read_text(encoding="utf-8")
        fetchers["gscpi"] = lambda: _gscpi_rows([9.9])
        run_world_monitor(tmp_path / "o", today="2026-06-12", fetchers=fetchers,
                          config_path=cfg, lake_dir=lake)
        assert (lake / "gscpi-2026-06-12.json").read_text(encoding="utf-8") == first
