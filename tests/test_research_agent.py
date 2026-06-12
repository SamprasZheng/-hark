"""research_agent + risk-queue 測試 — 注入式 fake client,零網路零真實磁碟。"""

from __future__ import annotations

import json

from sharks.ai.research_agent import build_prompt, run
from sharks.daily_dna_routine import risk_queue_entries


class _FakeCall:
    def __init__(self, content="", error=None):
        self.content = content
        self.error = error
        self.model = "fake-model"
        self.backend = "fake"


class _FakeClient:
    def __init__(self, content="## 假設\n- x", error=None):
        self._ret = _FakeCall(content, error)
        self.seen = None

    def chat(self, role, messages, **kw):
        self.seen = (role, messages, kw)
        return self._ret


def _gather_stub(ticker, **kw):
    return {"ticker": ticker.upper(), "sector": "Technology",
            "world_events": ["TS_HIGH"], "dna_row": None}


class TestResearchAgent:
    def test_build_prompt_pure_and_grounded(self):
        msgs = build_prompt({"ticker": "COHR", "sector": "Technology"})
        assert msgs[0]["role"] == "system"
        assert "禁止編造" in msgs[0]["content"]
        assert "COHR" in msgs[1]["content"]

    def test_run_writes_grade_e_draft(self, tmp_path):
        c = _FakeClient(content="## 假設\n- 依 world_events:TS_HIGH …")
        env = run("cohr", client=c, out_dir=tmp_path, gather=_gather_stub)
        assert env["ok"] is True and env["grade"] == "E"
        assert "draft-only" in env["llm_involvement"]
        p = tmp_path / f"research-draft-COHR-{env['as_of']}.md"
        assert p.exists() and "grade-E" in p.read_text(encoding="utf-8")
        assert c.seen[0] == "executor"          # 用 executor role(本地 4b)

    def test_run_degrades_on_error_no_file(self, tmp_path):
        c = _FakeClient(content="", error="connection refused")
        env = run("cohr", client=c, out_dir=tmp_path, gather=_gather_stub)
        assert env["ok"] is False and "path" not in env
        assert list(tmp_path.glob("research-draft-*")) == []

    def test_dry_run_no_write(self, tmp_path):
        env = run("mu", client=_FakeClient(), write=False,
                  out_dir=tmp_path, gather=_gather_stub)
        assert env["ok"] and list(tmp_path.glob("*.md")) == []


class TestRiskQueue:
    ROWS = [
        {"ticker": "ONTO", "human_review": True,
         "rules_fired": ["world-ts-high-taiwan-review"]},
        {"ticker": "UNH", "human_review": None, "rules_fired": []},
        {"ticker": "DXCM", "human_review": True,
         "rules_fired": ["axti-similar-failures"]},
    ]

    def test_entries_priority_and_reasons(self):
        es = risk_queue_entries("2026-06-12", ["AMAT"], self.ROWS, ["TS_HIGH"])
        assert es[0] == {"date": "2026-06-12", "ticker": "AMAT", "priority": "high",
                         "reason": "持倉 × 反身性斷裂交集",
                         "source": "reflexivity ∩ holdings"}
        med = {e["ticker"]: e for e in es[1:]}
        assert set(med) == {"ONTO", "DXCM"}
        assert med["ONTO"]["reason"] == "world-ts-high-taiwan-review"
        assert med["ONTO"]["world_events"] == ["TS_HIGH"]

    def test_empty_inputs_empty_queue(self):
        assert risk_queue_entries("2026-06-12", [], [], []) == []

    def test_entries_are_json_serialisable(self):
        for e in risk_queue_entries("2026-06-12", ["A"], self.ROWS, None):
            json.dumps(e, ensure_ascii=False)
