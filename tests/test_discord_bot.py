"""Offline smoke tests for the Discord layer.

These touch only the pure modules (config / personas / meetings / brains JSON
parsing). They deliberately do NOT import sharks.discord.bot (which needs the
discord.py dependency) so the suite runs in the dep-free core environment.
"""

from __future__ import annotations

import json
from datetime import datetime

from sharks.discord import brains as B
from sharks.discord import meetings as M
from sharks.discord import personas as P
from sharks.discord.config import TPE, Settings


def _settings(tmp_path) -> Settings:
    s = Settings.load()
    s.outputs_dir = tmp_path
    return s


# ── config ─────────────────────────────────────────────────────────────────--
def test_config_missing_flags_empty_token():
    problems = Settings(token="").missing()
    assert any("DISCORD_BOT_TOKEN" in p for p in problems)


def test_config_rejects_bad_backend_and_time():
    s = Settings(token="x", backend="nope", morning_hhmm="7am")
    problems = s.missing()
    assert any("BACKEND" in p for p in problems)
    assert any("MORNING" in p for p in problems)


# ── personas ───────────────────────────────────────────────────────────────--
def test_personas_load_includes_voices_excludes_archives():
    personas = P.load_personas()
    assert {"huang", "sam", "sharks"} <= set(personas)        # voting + house view
    assert "codex" not in personas and "gemini" not in personas  # design archives
    # the recommend-only guardrail is baked into every system prompt
    assert "下單" in personas["huang"].system_prompt


def test_resolve_persona_prefix_and_default():
    personas = P.load_personas()
    p, q = P.resolve_persona("huang: CoWoS 還能追嗎", personas, "sharks")
    assert p is not None and p.name == "huang" and "CoWoS" in q

    p2, q2 = P.resolve_persona("大盤怎麼看", personas, "sharks")
    assert p2 is not None and p2.name == "sharks" and q2 == "大盤怎麼看"


# ── meetings ───────────────────────────────────────────────────────────────--
def test_meeting_handles_missing_outputs(tmp_path):
    d = M.compose_morning(_settings(tmp_path), datetime(2026, 5, 31, 7, 30, tzinfo=TPE))
    assert "晨會" in d.title
    assert "health-check" in d.to_markdown()   # the missing-file hint


def test_meeting_renders_real_shaped_outputs(tmp_path):
    (tmp_path / "daily-health-check-2026-05-31.json").write_text(json.dumps({
        "as_of": "2026-05-31T00:30:00-04:00",
        "regime": {"label": "late_bull", "reasons": ["breadth OVERHEATED"]},
        "funding_stress": {"verdict": "CALM", "live_data": False},
        "posture": {"posture": "NEUTRAL-CAUTIOUS", "systemic_risk": False,
                    "deploy_bear_hedges": False, "sizing_guidance": "ride the trend"},
        "recommendations": [{"type": "DEFAULT-HOLD", "action": "hold", "detail": "no trigger"}],
        "position_health": {"available": True,
                            "sell_candidates": [{"ticker": "LABU"}],
                            "trim_candidates": [{"ticker": "CRSR"}]},
    }, ensure_ascii=False), encoding="utf-8")
    (tmp_path / "fom-monthly-2026-05-29.json").write_text(json.dumps({
        "as_of": "2026-05-30",
        "top_3_picks": [{"rank": 1, "ticker": "ARM", "final_fom": 61.65, "sector": "SOXX",
                         "momentum": 83.4, "quality": 72.5, "bubble_guard": -55.0}],
    }, ensure_ascii=False), encoding="utf-8")

    md = M.compose_morning(_settings(tmp_path),
                           datetime(2026, 5, 31, 7, 30, tzinfo=TPE)).to_markdown()
    assert "late_bull" in md and "ARM" in md and "LABU" in md


def test_research_prompt_variants():
    assert "晨會" in M.research_prompt("morning")
    assert "晚會" in M.research_prompt("evening")


# ── brains: claude JSON parsing ──────────────────────────────────────────────-
def test_parse_claude_success_error_and_raw():
    txt, cost = B._parse_claude_json(
        '{"type":"result","is_error":false,"result":"hej","total_cost_usd":0.012}')
    assert txt == "hej" and cost == 0.012

    err_txt, _ = B._parse_claude_json('{"is_error":true,"result":"x"}')
    assert err_txt is None

    raw, _ = B._parse_claude_json("plain text, not json")
    assert raw == "plain text, not json"


# ── council debate engine (stubbed LLM) ──────────────────────────────────────-
def test_council_engine_with_stub_ask():
    from sharks.discord import council as CO
    from sharks.discord.personas import ChatPersona

    def ask(system, user, max_tokens):
        if "其他分析師的立場" in user:          # round 2: 質疑 + 投票
            return "我反駁 sam。\n投票: 多 | 信心: 4 | 動作: 持有 ARM", True
        if "議會票數" in user:                   # chair synthesis
            return "結論:整體偏多,最大分歧在風險控管。保持紀律。", True
        return "看多。半導體強勢。", True         # round 1: 立場

    council = [ChatPersona("huang", "huang·黃", "SYS", "huang.md"),
               ChatPersona("sam", "sam·長線", "SYS", "sam.md")]
    chair = ChatPersona("sharks", "sharks", "SYS", "sharks.md")
    r = CO.run_council("今天偏多還偏空?", "regime late_bull",
                       council=council, chair=chair,
                       ask_maker=lambda model: (ask, "test"))
    assert r.ok and len(r.votes) == 2
    assert all(v.vote == "多" and v.conviction == 4 for v in r.votes)
    assert r.tally["多"] == 2 and r.lean() == "多"
    assert "結論" in r.conclusion


def test_council_multimodel_assignment():
    """Per-seat models are assigned positionally and recorded on each Vote."""
    from sharks.discord import council as CO
    from sharks.discord.personas import ChatPersona

    seen_models = []

    def ask_maker(model):
        def ask(system, user, mx):
            seen_models.append(model)
            return "看多。\n投票: 多 | 信心: 3 | 動作: 持有", True
        return ask, "test"

    council = [ChatPersona("huang", "huang", "S", "f"),
               ChatPersona("bear", "bear", "S", "f")]
    r = CO.run_council("t", "b", council=council,
                       models={"huang": "qwen2.5:7b", "bear": "mistral:7b"},
                       default_model="qwen2.5:7b", ask_maker=ask_maker)
    assert {v.model for v in r.votes} == {"qwen2.5:7b", "mistral:7b"}
    assert "mistral:7b" in seen_models and "qwen2.5:7b" in seen_models


def test_council_vote_parser():
    from sharks.discord.council import _parse_vote
    assert _parse_vote("投票: 空 | 信心: 5 | 動作: 減碼 LABU")[:2] == ("空", 5)
    assert _parse_vote("沒有結構化投票")[0] == "中性"   # tolerant default


def test_council_cross_exam_layer_runs_distinct_round():
    """cross_exam=True inserts a 交叉質詢 round that fills Vote.crossexam without a vote."""
    from sharks.discord import council as CO
    from sharks.discord.personas import ChatPersona

    prompts: list[str] = []

    def ask(system, user, max_tokens):
        prompts.append(user)
        if "交叉質詢" in user and "最終投票" not in user:   # the dedicated cross-exam round
            return "我質疑 bear:你的下行情境忽略了庫存回補。", True
        if "其他分析師的立場" in user:                       # final vote round
            return "投票: 多 | 信心: 4 | 動作: 持有 NVDA", True
        if "議會票數" in user:
            return "結論:整體偏多。", True
        return "看多。", True

    council = [ChatPersona("huang", "huang", "S", "f"),
               ChatPersona("bear", "bear", "S", "f")]
    r = CO.run_council("偏多偏空?", "regime late_bull", council=council,
                       ask_maker=lambda m: (ask, "test"), cross_exam=True)
    assert any("交叉質詢" in p for p in prompts)           # the layer actually ran
    assert all(v.crossexam and "質疑" in v.crossexam for v in r.votes)
    assert all(v.vote == "多" for v in r.votes)


def test_council_memory_injected_into_prompts():
    """memory + persona_memory are threaded into the round-1 prompt."""
    from sharks.discord import council as CO
    from sharks.discord.personas import ChatPersona

    seen: list[str] = []

    def ask(system, user, max_tokens):
        seen.append(user)
        if "其他分析師的立場" in user:
            return "投票: 空 | 信心: 3 | 動作: 觀望", True
        if "議會票數" in user:
            return "結論。", True
        return "看空。", True

    council = [ChatPersona("huang", "huang", "S", "f")]
    CO.run_council("t", "b", council=council, ask_maker=lambda m: (ask, "test"),
                   cross_exam=False, memory="【近期議會記憶】上次偏多",
                   persona_memory={"huang": "你上次投多"})
    r1 = seen[0]
    assert "近期議會記憶" in r1 and "你上次投多" in r1


# ── council memory: write-back + recall (the closed loop) ─────────────────────-
def _fake_result(topic="今晚美股偏多偏空", lean_votes=("多", "空")):
    from sharks.discord.council import CouncilResult, Vote
    votes = [Vote(persona="huang", title="huang·黃", model="qwen2.5:7b",
                  stance="看多半導體", vote=lean_votes[0], conviction=4, action="持有 NVDA"),
             Vote(persona="bear", title="bear·空", model="llama3.1:8b",
                  stance="風險未除", vote=lean_votes[1], conviction=3, action="減碼")]
    r = CouncilResult(topic=topic, votes=votes, ok=True,
                      conclusion="整體偏多但留意資金面。")
    r.tally = {"多": 1, "空": 1, "中性": 0, "avg_conviction": 3.5}
    return r


def test_council_memory_record_writes_md_and_jsonl_and_is_searchable(tmp_path):
    from sharks.discord import council_memory as CM, wiki_rag
    s = Settings(token="x")
    s.project_root = tmp_path
    res = CM.record(_fake_result(), s, topic="今晚美股偏多偏空")
    assert res["ok"]
    md = tmp_path / res["path"]
    assert md.exists()
    body = md.read_text(encoding="utf-8")
    assert "type: council-conclusion" in body and "主席結論" in body and "huang" in body
    assert (tmp_path / "wiki" / "council" / "_history.jsonl").exists()
    # conclusion is now searchable knowledge (RAG cache was invalidated)
    hits = wiki_rag.search("美股偏多偏空", tmp_path, 5)
    assert any("council" in h.path for h in hits)


def test_council_memory_brief_and_persona_memories_recall(tmp_path):
    from sharks.discord import council_memory as CM
    s = Settings(token="x")
    s.project_root = tmp_path
    CM.record(_fake_result(topic="昨日結論"), s, topic="昨日結論")
    brief = CM.memory_brief(s, "昨日結論", with_rag=False)
    assert "近期議會記憶" in brief and "昨日結論" in brief
    pmem = CM.persona_memories(s)
    assert "huang" in pmem and "bear" in pmem
    assert "你最近的紀錄" in pmem["huang"]


def test_run_council_local_closes_the_loop(tmp_path):
    """run_council_local writes each conclusion back AND feeds prior memory in."""
    from sharks.discord import council as CO
    from sharks.discord.personas import ChatPersona

    s = Settings(token="x")
    s.project_root = tmp_path
    personas = {"huang": ChatPersona("huang", "huang", "S", "f"),
                "sharks": ChatPersona("sharks", "sharks", "S", "f")}

    seen: list[str] = []

    def ask_maker(model):
        def ask(system, user, max_tokens):
            seen.append(user)
            if "其他分析師的立場" in user:
                return "投票: 多 | 信心: 4 | 動作: 持有", True
            if "議會票數" in user:
                return "結論:偏多。", True
            return "看多。", True
        return ask, "test"

    common = dict(council_names=("huang",), chair_name="sharks",
                  personas=personas, settings=s, cross_exam=False, ask_maker=ask_maker)

    # 1st council → conclusion written back to wiki/council/
    CO.run_council_local("第一題", "brief", **common)
    hist = tmp_path / "wiki" / "council" / "_history.jsonl"
    assert hist.exists() and "第一題" in hist.read_text(encoding="utf-8")

    # 2nd council → the 1st conclusion is recalled into this debate's prompts
    seen.clear()
    CO.run_council_local("第二題", "brief", **common)
    assert any("近期議會記憶" in p and "第一題" in p for p in seen)
    assert hist.read_text(encoding="utf-8").count("第二題") == 1


# ── wiki ingest + RAG (local NotebookLM write/read sides) ─────────────────────-
def test_wiki_ingest_writes_note_and_is_searchable(tmp_path):
    from sharks.discord import wiki_ingest, wiki_rag
    s = Settings(token="x")
    s.project_root = tmp_path
    res = wiki_ingest.ingest("CoWoS 是台積電的先進封裝,2026 產能吃緊;HBM 同步吃緊。",
                             title="CoWoS note", settings=s)
    assert res["ok"]
    note = tmp_path / res["path"]
    assert note.exists()
    body = note.read_text(encoding="utf-8")
    assert "type: note" in body and "as_of_timestamp:" in body and "CoWoS" in body
    hits = wiki_rag.search("CoWoS 封裝", tmp_path, 5)   # ingest cleared the cache
    assert any("CoWoS" in h.text for h in hits)


def test_wiki_ingest_recent_lists_newest(tmp_path):
    from sharks.discord import wiki_ingest
    s = Settings(token="x")
    s.project_root = tmp_path
    wiki_ingest.ingest("note one", settings=s)
    wiki_ingest.ingest("note two", settings=s)
    assert len(wiki_ingest.recent(s, 5)) == 2


# ── performance-feedback rotation throttle ────────────────────────────────────-
def _write_feedback_fixtures(tmp_path, regime, funding, systemic):
    (tmp_path / "portfolio-audit-2026-06-01.json").write_text(json.dumps({
        "as_of": "2026-06-01",
        "portfolio_1_audit": [
            {"ticker": "NOW", "pct": 10.0, "verdict": "HOLD", "category": "cash_equity",
             "fom_breakdown": {"final_fom": 62, "momentum": 80, "quality": 70}},
            {"ticker": "PG", "pct": 6.0, "verdict": "HOLD-Buffett-tier", "category": "cash_equity",
             "fom_breakdown": {"final_fom": 55, "momentum": 50, "quality": 78}},
            {"ticker": "LABU", "pct": 5.0, "verdict": "SELL", "category": "leveraged_etf",
             "leveraged_scorer": {"annual_decay_pct": 60.8}},
        ],
    }, ensure_ascii=False), encoding="utf-8")
    (tmp_path / "daily-health-check-2026-06-01.json").write_text(json.dumps({
        "regime": {"label": regime}, "funding_stress": {"verdict": funding},
        "posture": {"systemic_risk": systemic, "deploy_bear_hedges": systemic},
    }, ensure_ascii=False), encoding="utf-8")


def test_feedback_hold_and_deepen_when_strong_no_reversal(tmp_path):
    from sharks.discord.feedback import compose_feedback
    _write_feedback_fixtures(tmp_path, "late_bull", "CALM", False)
    r = compose_feedback(tmp_path, "great")
    assert r.verdict == "HOLD_AND_DEEPEN" and not r.reversal
    assert any(h.ticker == "NOW" for h in r.support)        # winner surfaced for deep-dive
    assert any(h.ticker == "LABU" for h in r.rotation)      # decay hygiene still listed


def test_feedback_rotate_on_real_reversal(tmp_path):
    from sharks.discord.feedback import compose_feedback
    _write_feedback_fixtures(tmp_path, "risk_off", "STRESS", True)
    r = compose_feedback(tmp_path, "great")                 # even if perf great
    assert r.verdict == "ROTATE" and r.reversal
    assert r.reversal_reasons


# ── 抄底起漲 dip-buy screener (stubbed price fetch) ───────────────────────────-
def test_dipbuy_screen_classifies(tmp_path):
    from sharks.discord import dipbuy

    def fetch(tickers):
        series = {
            # ~30% off high and turning up over the last month → 起漲候選
            "RISE": [100] * 200 + [60] * 40 + [62, 64, 66, 68, 70] * 4,
            # ~40% off high but flat at the lows → 抄底待起漲
            "WAIT": [100] * 200 + [60] * 60,
            # pressed against the highs → 近高不抄
            "HIGH": list(range(50, 300)),
        }
        return {t: series[t] for t in tickers if t in series}

    rows = dipbuy.screen(["RISE", "WAIT", "HIGH"], fetch=fetch,
                         quality_by_ticker={"RISE": 70.0})
    by = {c.ticker: c for c in rows}
    assert by["RISE"].rising and by["RISE"].verdict.startswith("🟢")
    assert (not by["WAIT"].rising) and "待起漲" in by["WAIT"].verdict
    assert "近高" in by["HIGH"].verdict
    assert rows[0].ticker == "RISE"      # highest dip_score ranks first
