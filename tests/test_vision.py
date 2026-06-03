"""Tests for the Discord screenshot-vision helpers — pure/offline only.

The Ollama vision CALL is network and exercised live; here we validate model
selection, the chatty-JSON parser, percent extraction, scam-language detection,
the portfolio risk read, and the fact-check red-flag heuristics.
"""
from __future__ import annotations

from sharks.discord.vision import (
    pick_vision_model, parse_json_block, extract_pct, detect_scam_language,
    assess_portfolio, factcheck_flags, claim_vs_reality_flags,
)


class TestPickVisionModel:
    def test_prefers_exact_preferred(self):
        assert pick_vision_model(["qwen2.5:7b", "llava:13b"], "llava:13b") == "llava:13b"

    def test_family_match(self):
        assert pick_vision_model(["qwen2.5vl:7b-q4"], "qwen2.5vl") == "qwen2.5vl:7b-q4"

    def test_preference_order_when_no_pref(self):
        assert pick_vision_model(["llava:13b", "qwen2.5vl:7b"]) == "qwen2.5vl:7b"

    def test_hint_fallback(self):
        assert pick_vision_model(["my-custom-vision-model"]) == "my-custom-vision-model"

    def test_none_when_no_vision_model(self):
        assert pick_vision_model(["qwen2.5:7b", "llama3.1:8b"]) is None
        assert pick_vision_model([]) is None


class TestParseJsonBlock:
    def test_plain(self):
        assert parse_json_block('{"a": 1}') == {"a": 1}

    def test_fenced(self):
        assert parse_json_block('```json\n{"a": 1, "b": "x"}\n```') == {"a": 1, "b": "x"}

    def test_prose_wrapped(self):
        assert parse_json_block('Sure! Here:\n{"holdings": []}\nhope it helps') == {"holdings": []}

    def test_nested_braces_and_strings(self):
        out = parse_json_block('{"t":"a{b}c","n":{"x":1}}')
        assert out == {"t": "a{b}c", "n": {"x": 1}}

    def test_garbage_is_none(self):
        assert parse_json_block("no json here") is None
        assert parse_json_block("") is None


class TestExtractPct:
    def test_percent(self):
        assert extract_pct("+12.5%") == 12.5
        assert extract_pct("-3%") == -3.0

    def test_multiplier(self):
        assert extract_pct("10x") == 900.0
        assert extract_pct("翻5倍") == 400.0

    def test_number_passthrough(self):
        assert extract_pct(42) == 42.0

    def test_none(self):
        assert extract_pct("no number") is None
        assert extract_pct(None) is None


class TestScamLanguage:
    def test_hits(self):
        hits = detect_scam_language("保證穩賺,加我私訊進群跟單")
        assert "保證" in hits and "穩賺" in hits and "跟單" in hits

    def test_english(self):
        assert "guaranteed" in detect_scam_language("guaranteed risk-free returns")

    def test_clean(self):
        assert detect_scam_language("我覺得這檔基本面不錯") == []


class TestAssessPortfolio:
    def test_concentration_and_breadth(self):
        a = assess_portfolio({"holdings": [
            {"ticker": "AAA", "weight_pct": 30, "pnl_pct": 12},
            {"ticker": "BBB", "weight_pct": 10},
            {"ticker": "CCC", "weight_pct": 5},
        ]})
        assert a["n_holdings"] == 3
        assert a["top"]["ticker"] == "AAA" and a["top"]["weight_pct"] == 30
        joined = " ".join(a["flags"])
        assert "集中" in joined            # top >= 15%
        assert "檔數過少" in joined          # n <= 3

    def test_extreme_pnl_flagged(self):
        a = assess_portfolio({"holdings": [
            {"ticker": "AAA", "weight_pct": 8, "pnl_pct": 900},
            {"ticker": "BBB", "weight_pct": 8},
            {"ticker": "CCC", "weight_pct": 8},
            {"ticker": "DDD", "weight_pct": 8},
        ]})
        assert any("異常高報酬" in f for f in a["flags"])

    def test_structure_keys(self):
        a = assess_portfolio({"holdings": []})
        assert {"n_holdings", "top", "leveraged", "leveraged_weight_pct", "flags"} <= set(a)
        assert a["n_holdings"] == 0


class TestFactcheckFlags:
    def test_high_credibility_concern(self):
        fc = factcheck_flags({
            "numbers": ["+1200%", "$5,000"],
            "text_ocr": "保證穩賺 加我私訊",
            "claims": ["我一週賺一倍"],
            "tickers": ["TSLA"],
            "time_refs": ["2026-06-01"],
        })
        assert fc["verdict"].startswith("🔴")          # >= 3 red flags
        assert any("過高" in f for f in fc["red_flags"])  # extreme return
        assert any("跟單" in f or "保證" in f for f in fc["red_flags"])  # scam language
        # the "screenshot is not proof" flag is always present
        assert any("截圖" in f for f in fc["red_flags"])
        assert fc["checkable"]                          # tickers + claims + time

    def test_clean_post_only_baseline_flag(self):
        fc = factcheck_flags({"numbers": ["3.2%"], "text_ocr": "財報優於預期", "claims": [], "tickers": []})
        # only the always-on "a screenshot is not proof" flag → not high-concern
        assert not fc["verdict"].startswith("🔴")
        assert len(fc["red_flags"]) == 1


class TestClaimVsReality:
    def test_extreme_claim_vs_flat_reality(self):
        flags = claim_vs_reality_flags(
            {"numbers": ["+500%"]},
            {"rows": [{"ticker": "AAA", "found": True, "m3_pct": 12.0}]},
        )
        assert any("遠高於實際" in f for f in flags)

    def test_unknown_ticker_flag(self):
        flags = claim_vs_reality_flags(
            {"numbers": []}, {"rows": [{"ticker": "ZZZ", "found": False}]})
        assert any("查無此標的" in f for f in flags)

    def test_consistent_claim_no_flag(self):
        flags = claim_vs_reality_flags(
            {"numbers": ["+8%"]},
            {"rows": [{"ticker": "AAA", "found": True, "m3_pct": 10.0}]})
        assert flags == []
