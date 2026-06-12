"""Tests for the /api/world panel loader (sharks.ui.server.world_panel) —
outputs 目錄以 tmp_path 注入,純離線、零網路、無 mock。"""

from __future__ import annotations

import json
from pathlib import Path

from sharks.ui.server import _abm_compact, world_panel


def _write(d: Path, name: str, obj) -> None:
    (d / name).write_text(json.dumps(obj, ensure_ascii=False), encoding="utf-8")


def _monitor(retrieved_at: str = "2026-06-12T09:47:25+00:00") -> dict:
    """合成 world-monitor 輸出(欄位形狀對齊 outputs/world-monitor-2026-06-12.json)。"""
    return {
        "retrieved_at": retrieved_at,
        "as_of": {"gscpi": "2026-05-31", "gpr_monthly": "2026-05-01"},
        "stale_sources": ["gpr_daily"],
        "metrics": {"gscpi": 1.769, "gpr": 184.2, "gprc_twn": 0.489,
                    "gprc_twn_z60": 2.24, "gprc_chn": 1.55},
        "events_triggered": [
            {"id": "TS_HIGH", "name": "台海地緣風險升高", "category": "geopolitical",
             "severity": "high", "impact": {"deepkill_cap_multiplier": 0.75}},
            {"id": "GSCPI_SPIKE", "name": "全球供應鏈壓力尖峰", "category": "supply_chain",
             "severity": "med-high", "impact": {}},
        ],
        "impacts": {"deepkill_cap_multiplier": 0.75, "exposure_penalty": 0.25,
                    "review_groups": ["taiwan_chain"]},
        "disclaimer": "recommend-only;事件=篩選/微調輸入,非倉位指令。",
    }


def _transitions() -> dict:
    """合成 regime-transitions 輸出(形狀對齊 outputs/regime-transitions-2026-06-12.json)。"""
    return {
        "as_of": "2026-06-12",
        "current_outlook": {
            "current_state": "mania",
            "current_bands": {"gpr_band": "elevated", "gscpi_band": "spike"},
            "used_level": "unconditioned",
            "n": 44,
            "next_month_probs": {"bull": 0.2727, "mania": 0.6364, "bear": 0.0909, "crisis": 0.0},
            "low_n": False,
            "fallback_path": [{"level": "joint", "reason": "low_n(n=1<8)"}],
        },
    }


def _backfill() -> dict:
    """合成 world-backfill 輸出(形狀對齊 outputs/world-backfill-2026-06-12.json)。"""
    return {
        "as_of": "2026-06-12",
        "event_forward_study": {
            "underlying": "QQQ",
            "base_rate": {"n_months": 327, "fwd": {
                "1m": {"n": 326, "median_pct": 1.51, "mean_pct": 1.1},
                "3m": {"n": 324, "median_pct": 4.16, "mean_pct": 3.26},
                "6m": {"n": 321, "median_pct": 8.37, "mean_pct": 6.63}}},
            "events": {
                "GSCPI_SPIKE": {"months_fired": 29, "fwd": {
                    "1m": {"n": 28, "median_pct": 1.79},
                    "3m": {"n": 27, "median_pct": 1.35},
                    "6m": {"n": 27, "median_pct": -0.18}}},
                "TS_HIGH": {"months_fired": 46, "fwd": {
                    "3m": {"n": 45, "median_pct": 2.0}}},
            },
        },
    }


class TestWorldPanel:
    def test_no_files_degrades_gracefully(self, tmp_path):
        out = world_panel(outputs_dir=tmp_path)
        assert out["available"] is False
        assert out["abm"] is None
        assert out["behavioral"] is None
        assert out["outlook"] is None
        assert out["history_lens"] is None
        assert "recommend-only" in out["disclaimer"]

    def test_corrupt_json_degrades_not_raises(self, tmp_path):
        (tmp_path / "world-monitor-2026-06-12.json").write_text("{not json", encoding="utf-8")
        out = world_panel(outputs_dir=tmp_path)
        assert out["available"] is False
        assert out["file"] == "world-monitor-2026-06-12.json"

    def test_compacts_latest_monitor_sorted_glob_last(self, tmp_path):
        _write(tmp_path, "world-monitor-2026-06-11.json",
               {**_monitor("2026-06-11T09:00:00+00:00"), "events_triggered": []})
        _write(tmp_path, "world-monitor-2026-06-12.json", _monitor())
        out = world_panel(outputs_dir=tmp_path)
        assert out["available"] is True
        assert out["file"] == "world-monitor-2026-06-12.json"        # 取最新,不取 06-11
        assert [e["id"] for e in out["events_triggered"]] == ["TS_HIGH", "GSCPI_SPIKE"]
        assert out["events_triggered"][0]["severity"] == "high"
        # 指標只下發面板要的 4 個 key(gprc_chn 被裁掉)
        assert out["metrics"] == {"gscpi": 1.769, "gpr": 184.2,
                                  "gprc_twn": 0.489, "gprc_twn_z60": 2.24}
        assert out["impacts"]["deepkill_cap_multiplier"] == 0.75
        assert out["impacts"]["exposure_penalty"] == 0.25
        assert out["stale_sources"] == ["gpr_daily"]
        assert out["retrieved_at"] == "2026-06-12T09:47:25+00:00"
        # 閾值錨點與 config/world_events.json _basis 一致
        assert out["thresholds"] == {"gscpi_spike": 1.5, "gpr_p95": 169.0, "gprc_twn_p95": 0.25}
        assert out["abm"] is None                                     # 無 ABM 檔 → null,不爆

    def test_missing_metric_emits_none_never_invents(self, tmp_path):
        mon = _monitor()
        del mon["metrics"]["gpr"]
        _write(tmp_path, "world-monitor-2026-06-12.json", mon)
        out = world_panel(outputs_dir=tmp_path)
        assert out["metrics"]["gpr"] is None
        assert out["metrics"]["gscpi"] == 1.769


class TestAbmCompact:
    def test_abm_present_extracts_nested_survival_delta(self, tmp_path):
        _write(tmp_path, "world-monitor-2026-06-12.json", _monitor())
        _write(tmp_path, "abm-supply-chain-2026-06-12.json", {
            "as_of": "2026-06-12",
            "generated_at": "2026-06-12T10:00:00+00:00",
            "scenario": "TS_HIGH",
            "results": {"baseline": {"survival_rate": 0.91},
                        "shocked": {"survival_rate_delta": -0.18}},
        })
        out = world_panel(outputs_dir=tmp_path)
        abm = out["abm"]
        assert abm["survival_delta"] == -0.18                 # delta 命名優先於裸 survival_rate
        assert abm["survival_delta_field"] == "survival_rate_delta"
        assert abm["scenario"] == "TS_HIGH"
        assert abm["generated_at"] == "2026-06-12T10:00:00+00:00"

    def test_abm_without_survival_fields_returns_none_values(self):
        abm = _abm_compact({"as_of": "2026-06-12", "note": "schema 未含 survival 數值"})
        assert abm["survival_delta"] is None
        assert abm["survival_delta_field"] is None
        assert _abm_compact(None) is None
        assert _abm_compact("not a dict") is None


class TestBehavioralOutlookHistoryLens:
    def test_behavioral_passthrough_compact(self, tmp_path):
        mon = _monitor()
        mon["behavioral"] = {
            "score": 8.5,
            "components": {"TS_HIGH": 2.8, "GSCPI_SPIKE": 2.0},   # 面板不需要 → 裁掉
            "missing": [],
            "mania_note": "mania 狀態 + 行為偏離 8.5/10 ≥ 6:新倉寧缺勿濫(observe-first)。",
            "regime_state": "mania",
        }
        _write(tmp_path, "world-monitor-2026-06-12.json", mon)
        out = world_panel(outputs_dir=tmp_path)
        assert out["behavioral"] == {
            "score": 8.5,
            "mania_note": "mania 狀態 + 行為偏離 8.5/10 ≥ 6:新倉寧缺勿濫(observe-first)。",
            "regime_state": "mania",
        }

    def test_outlook_compaction_from_latest_transitions(self, tmp_path):
        _write(tmp_path, "world-monitor-2026-06-12.json", _monitor())
        stale = _transitions()
        stale["current_outlook"]["current_state"] = "bull"
        _write(tmp_path, "regime-transitions-2026-06-11.json", stale)
        _write(tmp_path, "regime-transitions-2026-06-12.json", _transitions())
        # .bak / intraday 快照一律排除,不得搶最新
        _write(tmp_path, "regime-transitions-2026-06-13-intraday.json",
               {"current_outlook": {"current_state": "crisis"}})
        (tmp_path / "regime-transitions-2026-06-14.json.bak").write_text("{}", encoding="utf-8")
        out = world_panel(outputs_dir=tmp_path)
        assert out["outlook"] == {
            "current_state": "mania",
            "used_level": "unconditioned",
            "n": 44,
            "low_n": False,
            "next_month_probs": {"bull": 0.2727, "mania": 0.6364, "bear": 0.0909, "crisis": 0.0},
        }

    def test_history_lens_gscpi_spike_vs_base_rate(self, tmp_path):
        _write(tmp_path, "world-monitor-2026-06-12.json", _monitor())
        _write(tmp_path, "world-backfill-2026-06-12.json", _backfill())
        out = world_panel(outputs_dir=tmp_path)
        # 只下發 GSCPI_SPIKE vs 基準率的 3m/6m 中位數(1m/mean/TS_HIGH 都裁掉)
        assert out["history_lens"] == {
            "event": "GSCPI_SPIKE",
            "event_3m": 1.35, "event_6m": -0.18,
            "base_3m": 4.16, "base_6m": 8.37,
        }

    def test_all_null_degrade_when_sections_absent_or_malformed(self, tmp_path):
        _write(tmp_path, "world-monitor-2026-06-12.json", _monitor())   # 無 behavioral 區塊
        _write(tmp_path, "regime-transitions-2026-06-12.json",
               {"as_of": "2026-06-12", "current_outlook": "not a dict"})
        _write(tmp_path, "world-backfill-2026-06-12.json",
               {"as_of": "2026-06-12", "event_forward_study": {
                   "base_rate": {"fwd": {}}, "events": {}}})            # 四格全空 → 整段降級
        out = world_panel(outputs_dir=tmp_path)
        assert out["available"] is True                                  # 主面板照常
        assert out["behavioral"] is None
        assert out["outlook"] is None
        assert out["history_lens"] is None

    def test_outlook_survives_missing_monitor(self, tmp_path):
        """world-monitor 缺檔不拖垮獨立來源:available=False 但 outlook 照下發。"""
        _write(tmp_path, "regime-transitions-2026-06-12.json", _transitions())
        out = world_panel(outputs_dir=tmp_path)
        assert out["available"] is False
        assert out["outlook"]["current_state"] == "mania"
        assert out["outlook"]["next_month_probs"]["mania"] == 0.6364
        assert out["behavioral"] is None
        assert out["history_lens"] is None


def test_api_world_route_registered():
    from sharks.ui.server import build_app
    paths = {r.path for r in build_app().routes if hasattr(r, "path")}
    assert "/api/world" in paths
