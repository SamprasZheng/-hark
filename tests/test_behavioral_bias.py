"""behavioral_bias 測試 — 純函式、零網路、零磁碟、零 mock(手設輸入打邊界).

涵蓋:偏離分數組成(全亮/部分/全缺)、封頂 10、gscpi 退路口徑、邊界閾值、
損失厭惡/錨定 flag 觸發與不觸發、priority 層級、mania 警語路徑、JSON 可序列化。
"""

from __future__ import annotations

import json

import pytest

from sharks.scoring.behavioral_bias import (DEVIATION_PRIORS, FLAG_PRIORS,
                                            MANIA_NOTE_DEVIATION_MIN, SCORE_CAP,
                                            behavioral_deviation_score,
                                            loss_aversion_flags,
                                            mania_overconfidence_note)


# ── behavioral_deviation_score ──

class TestDeviationScore:
    def test_all_components_fire_caps_at_10(self):
        out = behavioral_deviation_score(
            world_events=["TS_HIGH", "GSCPI_SPIKE", "GPR_EXTREME"],
            gprc_twn_z60=2.5, gscpi=1.8, qqq_vol_ratio=1.6,
            breadth_break_count=12)
        # 六 component 全亮:2.8+2.0+1.5+1.2+1.5+1.0 = 10.0(恰為封頂)
        assert out["score"] == SCORE_CAP == 10.0
        assert set(out["components"]) == {"TS_HIGH", "GSCPI_SPIKE", "GPR_EXTREME",
                                          "TWN_Z60", "VOL_PANIC", "BREADTH_BREAK"}
        assert out["missing"] == []
        # gscpi 在事件清單在場時不重複計分(GSCPI_SPIKE 只算一次)
        assert out["components"]["GSCPI_SPIKE"] == DEVIATION_PRIORS["GSCPI_SPIKE"]["weight"]

    def test_partial_inputs_skip_and_list_missing(self):
        out = behavioral_deviation_score(world_events=["TS_HIGH"])
        assert out["score"] == pytest.approx(2.8)
        assert out["components"] == {"TS_HIGH": 2.8}
        # 四個未供給的可選輸入全列 missing(world_events 有給,不列)
        assert out["missing"] == ["gprc_twn_z60", "gscpi", "qqq_vol_ratio",
                                  "breadth_break_count"]

    def test_no_events_no_inputs_scores_zero(self):
        out = behavioral_deviation_score(world_events=[])
        assert out["score"] == 0.0
        assert out["components"] == {}
        assert len(out["missing"]) == 4

    def test_world_events_none_is_degraded_not_zero_information(self):
        # 事件來源缺席 → 記 missing;raw gscpi 走 GSCPI_SPIKE 同口徑退路(≥1.5)
        out = behavioral_deviation_score(world_events=None, gscpi=1.6)
        assert "world_events" in out["missing"]
        assert out["components"] == {"GSCPI_SPIKE": 2.0}
        # 事件清單在場([]= 求值過無事件)時,raw gscpi 不得越過事件求值結果
        out2 = behavioral_deviation_score(world_events=[], gscpi=1.6)
        assert "GSCPI_SPIKE" not in out2["components"]

    def test_threshold_boundaries(self):
        # 每個數值 component 打在邊界上:>= 觸發、低一格不觸發(不列 missing)
        on = behavioral_deviation_score(world_events=[], gprc_twn_z60=2.0,
                                        qqq_vol_ratio=1.5, breadth_break_count=10)
        assert set(on["components"]) == {"TWN_Z60", "VOL_PANIC", "BREADTH_BREAK"}
        assert on["score"] == pytest.approx(1.2 + 1.5 + 1.0)
        off = behavioral_deviation_score(world_events=[], gprc_twn_z60=1.99,
                                         qqq_vol_ratio=1.49, breadth_break_count=9)
        assert off["components"] == {}
        assert off["score"] == 0.0
        assert off["missing"] == ["gscpi"]      # 有給的輸入不算缺

    def test_unknown_event_ids_ignored(self):
        out = behavioral_deviation_score(world_events=["GPR_ELEVATED", "TARIFF_NEW"])
        assert out["components"] == {}          # 非先驗表內事件不計分、不報錯
        assert out["score"] == 0.0

    def test_result_json_serialisable(self):
        out = behavioral_deviation_score(world_events=["TS_HIGH"], gprc_twn_z60=2.3)
        s = json.dumps(out, ensure_ascii=False)
        assert json.loads(s)["score"] == out["score"]
        assert out["llm_involvement"] == "none"


# ── loss_aversion_flags ──

class TestLossAversionFlags:
    def test_loss_aversion_fires_at_boundary(self):
        flags = loss_aversion_flags(ticker="NVDA", pnl_pct=-8.0, crisis_signal=True)
        assert len(flags) == 1
        f = flags[0]
        assert f["type"] == "LOSS_AVERSION" and f["priority"] == "high"
        assert f["ticker"] == "NVDA"
        assert "損失厭惡" in f["reason"]

    def test_loss_aversion_no_fire_above_threshold_or_no_crisis(self):
        # 虧損未達 -8% → 不觸發
        assert loss_aversion_flags(ticker="NVDA", pnl_pct=-7.9,
                                   crisis_signal=True) == []
        # 無 crisis 訊號(且 regime 非 crisis)→ 不觸發
        assert loss_aversion_flags(ticker="NVDA", pnl_pct=-20.0,
                                   regime_state="bear") == []

    def test_regime_state_crisis_equivalent_to_signal(self):
        flags = loss_aversion_flags(ticker="TSM", pnl_pct=-10.0,
                                    regime_state="crisis")
        assert [f["type"] for f in flags] == ["LOSS_AVERSION"]

    def test_missing_pnl_never_invents(self):
        # pnl 缺值 → 即使 crisis + 久持 + 高偏離也寧缺勿濫
        assert loss_aversion_flags(ticker="AMD", crisis_signal=True,
                                   holding_days=90, deviation_score=9.0) == []

    def test_anchoring_fires_at_boundaries(self):
        flags = loss_aversion_flags(ticker="MU", pnl_pct=-0.1, holding_days=45,
                                    deviation_score=5.5)
        assert len(flags) == 1
        f = flags[0]
        assert f["type"] == "ANCHORING" and f["priority"] == "medium"
        assert "錨定" in f["reason"]
        assert f["observed"]["thresholds"]["holding_days"] == \
            FLAG_PRIORS["ANCHORING_HOLDING_DAYS_MIN"]["value"]

    def test_anchoring_no_fire_each_leg(self):
        base = dict(ticker="MU", pnl_pct=-5.0, holding_days=45, deviation_score=5.5)
        assert loss_aversion_flags(**{**base, "holding_days": 44}) == []
        assert loss_aversion_flags(**{**base, "deviation_score": 5.4}) == []
        assert loss_aversion_flags(**{**base, "pnl_pct": 0.0}) == []
        assert loss_aversion_flags(**{**base, "deviation_score": None}) == []

    def test_both_flags_stack_and_serialisable(self):
        flags = loss_aversion_flags(ticker="SMCI", pnl_pct=-12.0, holding_days=60,
                                    regime_state="crisis", crisis_signal=True,
                                    deviation_score=7.0)
        assert [f["type"] for f in flags] == ["LOSS_AVERSION", "ANCHORING"]
        assert json.loads(json.dumps(flags, ensure_ascii=False))[1]["priority"] == "medium"


# ── mania_overconfidence_note ──

class TestManiaNote:
    def test_fires_only_in_mania_above_threshold(self):
        note = mania_overconfidence_note("mania", MANIA_NOTE_DEVIATION_MIN)
        assert isinstance(note, str) and "過度自信" in note

    def test_none_paths(self):
        assert mania_overconfidence_note("mania", 5.9) is None
        assert mania_overconfidence_note("bull", 9.0) is None
        assert mania_overconfidence_note("crisis", 9.0) is None
        assert mania_overconfidence_note(None, 9.0) is None
        assert mania_overconfidence_note("mania", None) is None
