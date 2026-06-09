"""Tests for the chokepoint screen — pure logic only (lane matching + integrity).

The FOM scoring of candidates is network and exercised live; here we validate the
keyword→lane matching, the curated-lane data integrity, and the synthetic meta for
an LLM-proposed lane.
"""
from __future__ import annotations

import re

from sharks.scoring.chokepoint import (
    match_lanes, lane_meta, CHOKEPOINT_LANES, LANE_KEYWORDS, BOTTLENECK_TYPES,
)


class TestMatchLanes:
    def test_ai_factory(self):
        assert "ai_factory" in match_lanes("AI 工廠 CoWoS 封裝")

    def test_cpo(self):
        assert "optics_cpo" in match_lanes("CPO 矽光子 互連")

    def test_rf(self):
        assert "rf_frontend" in match_lanes("RF 前端 衛星 beamformer")

    def test_hbm_english(self):
        assert "hbm" in match_lanes("the HBM memory bottleneck")

    def test_multiple_lanes(self):
        ls = match_lanes("AI 工廠 加上 液冷")
        assert "ai_factory" in ls and "power_thermal" in ls

    def test_no_match(self):
        assert match_lanes("珍珠奶茶 加 椰果") == []


class TestLaneIntegrity:
    def test_every_lane_well_formed(self):
        req = {"label", "supertrend", "bottleneck", "bottleneck_type", "stack",
               "candidates", "thesis_breaker"}
        for k, lane in CHOKEPOINT_LANES.items():
            assert req <= set(lane), f"{k} missing keys"
            assert lane["bottleneck_type"] in BOTTLENECK_TYPES
            assert lane["candidates"], f"{k} has no candidates"
            assert all(re.fullmatch(r"[A-Z]{1,5}", t) for t in lane["candidates"]), k
            assert k in LANE_KEYWORDS, f"{k} has no keywords"

    def test_lane_meta_curated(self):
        m = lane_meta("ai_factory")
        assert m["key"] == "ai_factory" and m["candidates"]

    def test_lane_meta_llm_synthetic(self):
        m = lane_meta("_llm", "量子運算")
        assert m["key"] == "_llm" and "量子運算" in m["label"]
        assert m["bottleneck_type"] is None
