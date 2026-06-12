"""Global Exposure 測試 — 純函式注入 config,零磁碟零網路。

涵蓋:群組命中/板塊底線/default、taiwan_exposed 旗標、world_factor 折減
(無事件=1.0、地板 0.65)、rally_dna 權重微調(donor 不破 0.05、總和不變)
與世界事件規則經 apply_rules 的端到端旗標路徑。
"""

from __future__ import annotations

from sharks.backtest.rally_dna import apply_rules, apply_world_weight_shifts
from sharks.scoring.global_exposure import exposure_for, world_factor

CFG = {
    "groups": {
        "taiwan_chain": {"weight": 0.9, "tickers": ["TSM", "COHR", "MU"]},
        "china_revenue": {"weight": 0.6, "tickers": ["AAPL", "NKE"]},
    },
    "sector_base": {"Technology": 0.45, "Utilities": 0.1},
    "default": 0.25,
}


class TestExposureFor:
    def test_group_hit(self):
        e = exposure_for("TSM", config=CFG)
        assert e["global_exposure"] == 0.9
        assert e["taiwan_exposed"] is True
        assert e["groups"] == ["taiwan_chain"]

    def test_sector_fallback(self):
        e = exposure_for("ORCL", sector="Technology", config=CFG)
        assert e["global_exposure"] == 0.45 and e["taiwan_exposed"] is False

    def test_default_when_no_group_no_sector(self):
        assert exposure_for("XOM", config=CFG)["global_exposure"] == 0.25

    def test_max_of_group_and_sector(self):
        e = exposure_for("AAPL", sector="Technology", config=CFG)
        assert e["global_exposure"] == 0.6                # 群組 0.6 > 板塊 0.45

    def test_case_insensitive(self):
        assert exposure_for("tsm", config=CFG)["taiwan_exposed"] is True


class TestWorldFactor:
    WS = {"impacts": {"exposure_penalty": 0.25}}

    def test_no_world_state_is_neutral(self):
        assert world_factor(0.9, None) == 1.0
        assert world_factor(0.9, {"impacts": {"exposure_penalty": 0.0}}) == 1.0

    def test_penalty_scales_with_exposure(self):
        assert world_factor(0.9, self.WS) == 0.775        # 1 - 0.9×0.25
        assert world_factor(0.2, self.WS) == 0.95

    def test_floor(self):
        assert world_factor(1.0, {"impacts": {"exposure_penalty": 0.9}}) == 0.65


class TestApplyWorldWeightShifts:
    BASE = {"tech": 0.40, "fundamental": 0.30, "capital": 0.20, "reflexivity": 0.10}

    def test_shift_preserves_sum(self):
        ws = {"impacts": {"weight_shifts": [
            {"give_to": "reflexivity", "take_from": "capital", "amount": 0.05}]}}
        w = apply_world_weight_shifts(dict(self.BASE), ws)
        assert w["reflexivity"] == 0.15 and w["capital"] == 0.15
        assert abs(sum(w.values()) - 1.0) < 1e-9

    def test_donor_floor_005(self):
        ws = {"impacts": {"weight_shifts": [
            {"give_to": "tech", "take_from": "reflexivity", "amount": 0.50}]}}
        w = apply_world_weight_shifts(dict(self.BASE), ws)
        assert w["reflexivity"] == 0.05                   # 抽到地板就停
        assert abs(sum(w.values()) - 1.0) < 1e-9

    def test_none_world_state_noop(self):
        assert apply_world_weight_shifts(dict(self.BASE), None) == self.BASE

    def test_unknown_dim_ignored(self):
        ws = {"impacts": {"weight_shifts": [
            {"give_to": "nope", "take_from": "tech", "amount": 0.05}]}}
        assert apply_world_weight_shifts(dict(self.BASE), ws) == self.BASE


class TestWorldRulesEndToEnd:
    """世界事件旗標 → ctx → 宣告式規則(config/dna_rules.json 同款 inline 鏡像)。"""

    RULES = [
        {"id": "world-ts-high-taiwan-review",
         "when": {"world_event_TS_HIGH": True, "taiwan_exposed": True},
         "then": {"human_review": True, "world_note": "台海高風險"}},
        {"id": "world-gscpi-deepkill-caution",
         "when": {"world_event_GSCPI_SPIKE": True, "archetype": "deep_kill"},
         "then": {"world_note": "GSCPI 尖峰"}},
    ]

    def test_taiwan_review_fires(self):
        row = {"ticker": "COHR", "taiwan_exposed": True}
        ctx = {"market_state": "bull", "world_event_TS_HIGH": True}
        out = apply_rules(row, ctx, self.RULES)
        assert out["human_review"] is True
        assert out["rules_fired"] == ["world-ts-high-taiwan-review"]

    def test_no_flag_no_fire(self):
        row = {"ticker": "COHR", "taiwan_exposed": True}
        out = apply_rules(row, {"market_state": "bull"}, self.RULES)
        assert "rules_fired" not in out

    def test_non_taiwan_ticker_not_reviewed(self):
        row = {"ticker": "HUM", "taiwan_exposed": False}
        ctx = {"world_event_TS_HIGH": True}
        assert "rules_fired" not in apply_rules(row, ctx, self.RULES)

    def test_gscpi_deepkill_note(self):
        row = {"ticker": "ICHR", "archetype": "deep_kill"}
        ctx = {"world_event_GSCPI_SPIKE": True}
        out = apply_rules(row, ctx, self.RULES)
        assert out["world_note"] == "GSCPI 尖峰"
