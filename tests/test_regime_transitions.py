"""regime_transitions 測試 — 合成序列手算期望,零網路零真實湖(tmp_path 除外).

涵蓋:band_of 邊界/缺值、無條件轉移手算、low_n 旗、月份斷層跳過、
世界列按月對齊(月 t 條件化 t→t+1)、缺世界月排除於箱表、
regime_outlook 回退鏈(joint→gpr→無條件)、退化路徑(無世界列/空序列)、
build_report+落盤、backfill 載入器(缺檔/壞檔/缺鍵)。
"""

from __future__ import annotations

import json

from sharks.backtest.regime_transitions import (LOW_N, _load_backfill_rows,
                                                band_of, build_report,
                                                regime_outlook,
                                                transition_table, write_report)


# ── 合成助手 ──

def _seq(start_ym: str, states: list[str]) -> list[tuple[str, str]]:
    """連續月份的 (ym, state) 序列。"""
    y, m = int(start_ym[:4]), int(start_ym[5:7])
    out = []
    for s in states:
        out.append((f"{y}-{m:02d}", s))
        y, m = (y + 1, 1) if m == 12 else (y, m + 1)
    return out


# ── band_of ──

class TestBandOf:
    def test_gpr_edges(self):
        assert band_of({"gpr": 145.9})["gpr_band"] == "calm"
        assert band_of({"gpr": 146.0})["gpr_band"] == "elevated"
        assert band_of({"gpr": 329.9})["gpr_band"] == "elevated"
        assert band_of({"gpr": 330.0})["gpr_band"] == "extreme"

    def test_gscpi_edges(self):
        assert band_of({"gscpi": 0.99})["gscpi_band"] == "normal"
        assert band_of({"gscpi": 1.0})["gscpi_band"] == "pressure"
        assert band_of({"gscpi": 1.5})["gscpi_band"] == "spike"
        assert band_of({"gscpi": -0.4})["gscpi_band"] == "normal"

    def test_missing_values_give_none_not_invented(self):
        assert band_of({}) == {"gpr_band": None, "gscpi_band": None}
        out = band_of({"gpr": 100.0})
        assert out["gpr_band"] == "calm" and out["gscpi_band"] is None
        assert band_of(None) == {"gpr_band": None, "gscpi_band": None}

    def test_nested_metrics_shape_from_backfill(self):
        # world_backfill 實際輸出形狀:{as_of, metrics: {...}}
        row = {"as_of": "2026-05-31",
               "metrics": {"gscpi": 1.769, "gpr": 184.2, "gprc_twn_z60": 2.24}}
        assert band_of(row) == {"gpr_band": "elevated", "gscpi_band": "spike"}
        # 平鋪鍵優先於巢狀
        assert band_of({"gpr": 50.0, "metrics": {"gpr": 400.0}})["gpr_band"] == "calm"


# ── 轉移計數(手算)──

class TestTransitionTable:
    def test_unconditioned_counts_hand_checked(self):
        # bull,bull,bull,bear,bull,bull,bear,crisis → 7 個轉移
        # bull→: bull x3, bear x2(n=5);bear→: bull x1, crisis x1(n=2)
        states = _seq("2020-01",
                      ["bull", "bull", "bull", "bear", "bull", "bull", "bear", "crisis"])
        t = transition_table(states)
        assert t["n_transitions"] == 7
        b = t["unconditioned"]["bull"]
        assert b["n"] == 5
        assert b["counts"] == {"bull": 3, "mania": 0, "bear": 2, "crisis": 0}
        assert b["probs"]["bull"] == 0.6 and b["probs"]["bear"] == 0.4
        be = t["unconditioned"]["bear"]
        assert be["n"] == 2 and be["counts"]["crisis"] == 1 and be["counts"]["bull"] == 1
        # 無世界列 → 箱表退化為 None
        assert t["by_gpr_band"] is None and t["by_gscpi_band"] is None
        assert t["by_joint"] is None and t["world_alignment"] is None

    def test_low_n_flagging(self):
        # 9 bull + 1 bear → bull n=9 >= LOW_N → low_n False;crisis n=0 → True
        states = _seq("2020-01", ["bull"] * 9 + ["bear"])
        t = transition_table(states)
        assert t["unconditioned"]["bull"]["n"] == 9
        assert t["unconditioned"]["bull"]["low_n"] is False
        assert t["unconditioned"]["crisis"]["n"] == 0
        assert t["unconditioned"]["crisis"]["low_n"] is True
        assert t["unconditioned"]["crisis"]["probs"] is None
        assert LOW_N == 8

    def test_month_gap_skipped_not_counted(self):
        # 2020-02 缺月 → 2020-01→2020-03 不算一個月轉移
        states = [("2020-01", "bull"), ("2020-03", "bear"), ("2020-04", "bull")]
        t = transition_table(states)
        assert t["n_transitions"] == 1
        assert t["skipped_gaps"] == 1
        assert t["unconditioned"]["bull"]["n"] == 0
        assert t["unconditioned"]["bear"]["counts"]["bull"] == 1

    def test_year_boundary_is_contiguous(self):
        states = [("2020-12", "bull"), ("2021-01", "bear")]
        t = transition_table(states)
        assert t["n_transitions"] == 1 and t["skipped_gaps"] == 0

    def test_world_alignment_month_t_conditions_t_plus_1(self):
        # 狀態 2020-01..05 = bull,bull,bear,bear,bull;只有 2020-02 GPR=400(extreme)
        # 轉移 02→03(bull→bear)應掛 extreme 箱;其餘掛 calm
        states = _seq("2020-01", ["bull", "bull", "bear", "bear", "bull"])
        rows = [{"as_of": f"2020-{m:02d}", "gpr": 400.0 if m == 2 else 100.0,
                 "gscpi": None} for m in range(1, 6)]
        t = transition_table(states, rows)
        ext = t["by_gpr_band"]["extreme"]["bull"]
        assert ext["n"] == 1 and ext["counts"]["bear"] == 1
        calm_bull = t["by_gpr_band"]["calm"]["bull"]
        assert calm_bull["n"] == 1 and calm_bull["counts"]["bull"] == 1
        calm_bear = t["by_gpr_band"]["calm"]["bear"]
        assert calm_bear["n"] == 2
        assert calm_bear["counts"] == {"bull": 1, "mania": 0, "bear": 1, "crisis": 0}
        # gscpi 全缺 → gscpi/joint 箱空(不發明)
        assert t["by_gscpi_band"] == {} and t["by_joint"] == {}
        assert t["world_alignment"]["n_with_world"] == 4

    def test_missing_world_month_excluded_from_bands(self):
        # 2020-02 無世界列 → 該轉移只進無條件表
        states = _seq("2020-01", ["bull", "bull", "bear"])
        rows = [{"as_of": "2020-01", "gpr": 100.0, "gscpi": 0.5}]
        t = transition_table(states, rows)
        assert t["n_transitions"] == 2
        assert t["world_alignment"]["n_with_world"] == 1
        assert t["world_alignment"]["n_without_world"] == 1
        assert t["by_gpr_band"]["calm"]["bull"]["n"] == 1            # 只有 01→02
        joint = t["by_joint"]["calm|normal"]["bull"]
        assert joint["n"] == 1 and joint["counts"]["bull"] == 1

    def test_empty_states_degrade(self):
        t = transition_table([])
        assert t["n_transitions"] == 0
        assert all(c["n"] == 0 and c["low_n"] for c in t["unconditioned"].values())


# ── regime_outlook 回退鏈 ──

def _toy_table():
    # joint(calm|normal) bull n=10(厚格);elevated|normal bull n=2(薄格)
    states = _seq("2010-01", ["bull"] * 11 + ["bull", "bear", "bull"])
    # 月 1..14;前 11 個月 calm/normal,2011-01(第 13 個月)起 elevated
    rows = []
    for i, (ym, _s) in enumerate(states):
        rows.append({"as_of": ym, "gpr": 100.0 if i < 11 else 200.0, "gscpi": 0.0})
    return transition_table(states, rows)


class TestRegimeOutlook:
    def test_thick_joint_cell_used(self):
        t = _toy_table()
        out = regime_outlook("bull", {"gpr_band": "calm", "gscpi_band": "normal"}, t)
        assert out["used_level"] == "joint"
        assert out["n"] >= LOW_N and out["low_n"] is False
        assert out["next_month_probs"]["bull"] > 0.9
        assert out["fallback_path"] == []

    def test_thin_joint_falls_back_to_gpr_then_unconditioned(self):
        t = _toy_table()
        out = regime_outlook("bull", {"gpr_band": "elevated", "gscpi_band": "normal"}, t)
        # elevated joint 與 gpr 箱皆薄 → 落到無條件
        assert out["used_level"] == "unconditioned"
        levels = [f["level"] for f in out["fallback_path"]]
        assert levels == ["joint", "gpr_band"]
        assert all("low_n" in f["reason"] for f in out["fallback_path"])
        assert out["n"] == t["unconditioned"]["bull"]["n"]

    def test_no_world_table_uses_unconditioned(self):
        states = _seq("2020-01", ["bull"] * 10)
        t = transition_table(states)                     # world_rows=None
        out = regime_outlook("bull", {"gpr_band": "calm", "gscpi_band": "normal"}, t)
        assert out["used_level"] == "unconditioned"
        assert out["n"] == 9

    def test_missing_bands_skip_conditioned_levels(self):
        t = _toy_table()
        out = regime_outlook("bull", {"gpr_band": None, "gscpi_band": None}, t)
        assert out["used_level"] == "unconditioned"

    def test_empty_table_returns_none_level(self):
        t = transition_table([])
        out = regime_outlook("bull", {"gpr_band": "calm", "gscpi_band": None}, t)
        assert out["used_level"] is None and out["next_month_probs"] is None
        out2 = regime_outlook(None, None, t)
        assert out2["used_level"] is None


# ── 報告 + 落盤 + backfill 載入 ──

class TestReportAndIO:
    def test_build_report_degraded_and_write(self, tmp_path):
        states = _seq("2020-01", ["bull", "bull", "bear", "bull"])
        rep = build_report(states, None, today="2026-06-12")
        assert rep["llm_involvement"] == "none"
        assert rep["world_conditioned"] is False
        assert rep["n_months"] == 4 and rep["n_transitions"] == 3
        assert "不進 KPI" in rep["note"]
        assert rep["current_outlook"]["current_state"] == "bull"
        p = write_report(rep, tmp_path, "2026-06-12")
        assert p.name == "regime-transitions-2026-06-12.json"
        loaded = json.loads(p.read_text(encoding="utf-8"))
        assert loaded["table"]["n_transitions"] == 3

    def test_build_report_conditioned_uses_latest_row_bands(self):
        states = _seq("2020-01", ["bull"] * 12)
        rows = [{"as_of": ym, "gpr": 100.0, "gscpi": 0.0} for ym, _ in states[:-1]]
        rows.append({"as_of": states[-1][0], "gpr": 350.0, "gscpi": 2.0})
        rep = build_report(states, rows, today="2026-06-12", source_name="x.json")
        assert rep["world_conditioned"] is True
        ob = rep["current_outlook"]["current_bands"]
        assert ob == {"gpr_band": "extreme", "gscpi_band": "spike"}

    def test_load_backfill_missing_malformed_and_valid(self, tmp_path):
        assert _load_backfill_rows(tmp_path) == (None, None)
        bad = tmp_path / "world-backfill-2026-06-01.json"
        bad.write_text("{not json", encoding="utf-8")
        assert _load_backfill_rows(tmp_path) == (None, None)
        nokey = tmp_path / "world-backfill-2026-06-02.json"
        nokey.write_text(json.dumps({"other": 1}), encoding="utf-8")
        assert _load_backfill_rows(tmp_path) == (None, None)
        good = tmp_path / "world-backfill-2026-06-03.json"
        rows = [{"as_of": "2020-01", "gpr": 100.0, "gscpi": 0.1, "gprc_twn_z60": 0.5}]
        good.write_text(json.dumps({"monthly_rows": rows}), encoding="utf-8")
        got, name = _load_backfill_rows(tmp_path)
        assert got == rows and name == "world-backfill-2026-06-03.json"
