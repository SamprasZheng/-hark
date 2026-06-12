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


class TestWorldPanel:
    def test_no_files_degrades_gracefully(self, tmp_path):
        out = world_panel(outputs_dir=tmp_path)
        assert out["available"] is False
        assert out["abm"] is None
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


def test_api_world_route_registered():
    from sharks.ui.server import build_app
    paths = {r.path for r in build_app().routes if hasattr(r, "path")}
    assert "/api/world" in paths
