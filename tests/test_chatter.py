"""Tests for the #雜談 chatter compose logic (pure; LLM injected, no network)."""

from __future__ import annotations

from sharks.discord.chatter import council_topic_from_news, quick_take


class TestQuickTake:
    def test_calls_llm_with_headlines(self):
        seen = {}

        def stub(system, user, max_tokens):
            seen["user"] = user
            seen["system"] = system
            return "因果鏈解讀內容", True

        out, ok = quick_take(["Fed holds rates steady", "Nvidia beats estimates"], stub)
        assert ok is True and out == "因果鏈解讀內容"
        assert "Fed holds rates steady" in seen["user"]
        assert "速解讀" in seen["system"] or "因果鏈" in seen["system"]

    def test_empty_headlines_skips_llm(self):
        called = []

        def stub(*a):
            called.append(1)
            return "x", True

        out, ok = quick_take([], stub)
        assert out == "" and ok is False
        assert not called  # no LLM call when there is nothing to interpret


class TestCouncilTopicFromNews:
    def test_topic_and_brief(self):
        topic, brief = council_topic_from_news(["Headline A", "Headline B"])
        assert ("偏多" in topic) or ("風險" in topic)
        assert "Headline A" in brief and "頭條" in brief
