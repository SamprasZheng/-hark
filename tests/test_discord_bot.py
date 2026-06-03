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
    """Drive the full cross-examination debate (開場→質詢→答辯→投票→正反方→主席)
    with a marker-branching stub LLM and assert each artifact is produced."""
    from sharks.discord import council as CO
    from sharks.discord.personas import ChatPersona

    def ask(system, user, max_tokens):
        if CO._M_CROSS in user:        # R2 交叉質詢: name an opponent + ask
            return "提問對象: sam·長線\n問題: 你忽略了估值過高的風險?", True
        if CO._M_DEFEND in user:       # R3 答辯
            return "我承認估值不低,但 AI 成長更快,本益比會被消化。", True
        if CO._M_VOTE in user:         # R4 最終投票
            return "聽完後我仍看多。\n投票: 多 | 信心: 4 | 動作: 持有 ARM", True
        if CO._M_LEDGER in user:       # R5 正反方對照
            return ("【正方·看多】\n- 半導體訂單強(數據: AI 訂單+30%)\n"
                    "【反方·看空】\n- 估值偏高(數據: 本益比 35x)\n"
                    "【關鍵分歧】成長能否消化估值\n【待驗證】下季財報", True)
        if CO._M_CHAIR in user:        # chair synthesis
            return "結論:整體偏多,最大分歧在估值。保持紀律。", True
        return "看多。半導體強勢,AI 訂單增 30%。", True   # R1 開場立場

    council = [ChatPersona("huang", "huang·黃", "SYS", "huang.md"),
               ChatPersona("sam", "sam·長線", "SYS", "sam.md")]
    chair = ChatPersona("sharks", "sharks", "SYS", "sharks.md")
    r = CO.run_council("今天偏多還偏空?", "regime late_bull",
                       council=council, chair=chair,
                       ask_maker=lambda model: (ask, "test"))
    assert r.ok and len(r.votes) == 2
    assert all(v.vote == "多" and v.conviction == 4 for v in r.votes)
    assert r.tally["多"] == 2 and r.lean() == "多"
    # cross-examination: huang questioned sam, sam answered (交叉辯論)
    assert any(ex.target == "sam" and ex.question and ex.answer for ex in r.exchanges)
    by = {v.persona: v for v in r.votes}
    assert by["sam"].answer and "估值" in by["sam"].answer
    # 正反方數據對照 parsed out of the 書記 ledger
    assert r.bull and r.bear and r.crux
    assert "結論" in r.conclusion


def test_council_ledger_and_question_parsers():
    from sharks.discord.council import _parse_ledger, _parse_question, Vote

    bull, bear, crux, unresolved = _parse_ledger(
        "【正方·看多】\n- 訂單強(數據: +30%)\n- 毛利升\n"
        "【反方·看空】\n- 估值貴(數據: 35x)\n【關鍵分歧】估值 vs 成長\n【待驗證】財報")
    assert bull and bear and "估值" in crux and unresolved
    # question target matches an opponent by title; question text extracted
    others = [Vote("sam", "sam·長線"), Vote("bear", "bear·空頭")]
    tgt, q = _parse_question("提問對象: bear·空頭\n問題: 你的停損點在哪?", others)
    assert tgt == "bear" and "停損" in q


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
