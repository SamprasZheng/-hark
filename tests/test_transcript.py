"""Offline tests for the Discord transcript + response cache (discord/transcript.py)."""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone

from sharks.discord import transcript as tx


class TestKey:
    def test_case_and_whitespace_insensitive(self):
        assert tx.make_key("ask", "What  is NVDA?") == tx.make_key("ask", "what is nvda?")

    def test_kind_separates(self):
        assert tx.make_key("ask", "q") != tx.make_key("persona", "q")


class TestLog:
    def test_writes_jsonl(self, tmp_path):
        p = tx.log_interaction(kind="ask", prompt="hi", response="yo", backend="claude",
                               cost_usd=0.01, transcript_dir=tmp_path)
        assert p is not None and p.exists()
        rec = json.loads(p.read_text(encoding="utf-8").splitlines()[-1])
        assert rec["kind"] == "ask" and rec["response"] == "yo" and rec["cost_usd"] == 0.01


class TestCache:
    def test_put_get_roundtrip(self, tmp_path):
        c = tmp_path / "cache.jsonl"
        tx.put_cached("ask", "q1", response="answer1", backend="claude", cache_path=c)
        got = tx.get_cached("ask", "q1", cache_path=c)
        assert got is not None and got["response"] == "answer1"

    def test_miss_returns_none(self, tmp_path):
        assert tx.get_cached("ask", "nope", cache_path=tmp_path / "cache.jsonl") is None

    def test_stale_returns_none(self, tmp_path):
        c = tmp_path / "cache.jsonl"
        old = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
        c.write_text(json.dumps({"ts": old, "key": tx.make_key("ask", "q"),
                                 "response": "stale"}) + "\n", encoding="utf-8")
        assert tx.get_cached("ask", "q", cache_path=c) is None          # older than 6h TTL
        assert tx.get_cached("ask", "q", cache_path=c, max_age_s=10 ** 9)["response"] == "stale"

    def test_last_write_wins(self, tmp_path):
        c = tmp_path / "cache.jsonl"
        tx.put_cached("ask", "q", response="v1", cache_path=c)
        tx.put_cached("ask", "q", response="v2", cache_path=c)
        assert tx.get_cached("ask", "q", cache_path=c)["response"] == "v2"


class TestSearch:
    def test_substring_search(self, tmp_path):
        tx.log_interaction(kind="ask", prompt="tell me about SpaceX IPO",
                           response="SPCX trades 6/12", transcript_dir=tmp_path)
        tx.log_interaction(kind="ask", prompt="unrelated", response="nothing",
                           transcript_dir=tmp_path)
        hits = tx.search("spcx", transcript_dir=tmp_path)
        assert len(hits) == 1 and "SPCX" in hits[0]["response"]
