#!/usr/bin/env python3
"""
Trading Society -- Debate Engine (C deliverable)

PPST Declaration (this PROGRAM):
- PROJECT: Trading Society
- PROGRAM: simulation/debate_engine.py
- SKILL:   multi_round_debate (skills/multi_round_debate/SKILL.md)
- TARGET:  Runnable, bounded (2-4 round) structured debate engine. Proposer/
           Critic/Verifier/Synthesizer roles, JSON message schema, consensus/
           veto/no-progress termination, structured synthesis + full transcript.
           Default agents are deterministic stubs -> llm_involvement="none".
           Produces research only; never a capital recommendation.

Design source: programs/debate/DEBATE_PROGRAM.md (which adapts grok.md to $hark
governance). Governance bindings live there; this file implements them.

Run: python simulation/debate_engine.py   (runs a 3-round demo debate)
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

# Reuse the protocol guard from the backtest runner so a debate replayed inside
# a backtest path is held to the same standard (Defense 1).
try:
    from simulation.backtest_runner import (
        assert_no_banned_keys, VALID_LLM_INVOLVEMENT,
    )
except Exception:  # pragma: no cover - path fallback for direct script run
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from simulation.backtest_runner import (
        assert_no_banned_keys, VALID_LLM_INVOLVEMENT,
    )

MESSAGE_TYPES = {"proposal", "challenge", "rebuttal", "verification", "synthesis"}


# ---------------------------------------------------------------------------
# Message schema (DEBATE_PROGRAM.md sec.4)
# ---------------------------------------------------------------------------
@dataclass
class Message:
    debate_id: str
    round: int
    from_agent: str
    message_type: str
    as_of_timestamp: str
    content: str = ""
    to_agent: Optional[str] = None
    evidence: List[str] = field(default_factory=list)
    severity: str = "low"            # low|medium|high
    confidence: float = 0.5
    stance: str = "neutral"          # support|oppose|neutral
    extra: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        d = {
            "debate_id": self.debate_id, "round": self.round,
            "from_agent": self.from_agent, "to_agent": self.to_agent,
            "message_type": self.message_type,
            "as_of_timestamp": self.as_of_timestamp, "content": self.content,
            "evidence": self.evidence, "severity": self.severity,
            "confidence": self.confidence, "stance": self.stance,
        }
        d.update(self.extra)
        return d


# Agent callable signatures. Each receives the running transcript + context and
# returns a Message. Defaults below are deterministic (no LLM).
AgentFn = Callable[["DebateState"], Message]


@dataclass
class DebateState:
    debate_id: str
    topic: str
    as_of: str
    max_rounds: int
    llm_involvement: str
    round: int = 0
    transcript: List[Message] = field(default_factory=list)
    proposals: List[Message] = field(default_factory=list)

    def add(self, m: Message) -> Message:
        if m.message_type not in MESSAGE_TYPES:
            raise ValueError(f"invalid message_type: {m.message_type}")
        # PIT guard: a message may not cite evidence postdating as_of by label.
        for e in m.evidence:
            if isinstance(e, str) and e[:10].count("-") == 2 and e[:10] > self.as_of:
                raise ValueError(
                    f"[PIT] message from {m.from_agent} cites future evidence "
                    f"'{e}' > as_of {self.as_of} (DEBATE_PROGRAM.md sec.5)."
                )
        # Defense 1 (protocol): banned keys only matter for LLM-involved runs.
        assert_no_banned_keys(m.to_dict(), llm_involvement=self.llm_involvement,
                              agent_id=m.from_agent)
        self.transcript.append(m)
        return m


# ---------------------------------------------------------------------------
# Engine
# ---------------------------------------------------------------------------
class DebateEngine:
    def __init__(
        self,
        critic: AgentFn,
        verifier: AgentFn,
        synthesizer: AgentFn,
        consensus_threshold: float = 2 / 3,
    ) -> None:
        self.critic = critic
        self.verifier = verifier
        self.synthesizer = synthesizer
        self.consensus_threshold = consensus_threshold

    def run(
        self,
        debate_id: str,
        topic: str,
        as_of: str,
        proposals: List[Message],
        max_rounds: int = 3,
        llm_involvement: str = "none",
    ) -> Dict[str, Any]:
        if llm_involvement not in VALID_LLM_INVOLVEMENT:
            raise ValueError(f"llm_involvement must be in {VALID_LLM_INVOLVEMENT}")
        max_rounds = max(1, min(max_rounds, 4))  # cap at 4 for capital topics

        st = DebateState(debate_id=debate_id, topic=topic, as_of=as_of,
                         max_rounds=max_rounds, llm_involvement=llm_involvement)

        # S1 PROPOSE
        for p in proposals:
            p.message_type = "proposal"
            p.debate_id, p.round, p.as_of_timestamp = debate_id, 0, as_of
            st.proposals.append(st.add(p))

        veto = False
        consensus = False
        no_progress = 0
        prev_evidence_count = -1

        # S2-S5 loop
        while st.round < max_rounds:
            st.round += 1

            # S2 CHALLENGE (critic names a target)
            challenge = self.critic(st)
            st.add(challenge)

            # S3 REBUTTAL (challenged agent responds; stubbed via synthesizer-side
            # rebuttal helper for determinism -- a real impl routes to to_agent)
            rebuttal = _default_rebuttal(st, challenge)
            st.add(rebuttal)

            # S4 VERIFY
            verification = self.verifier(st)
            st.add(verification)
            veto = bool(verification.extra.get("veto", False))
            consensus = bool(verification.extra.get("consensus_reached", False))

            # No-progress detection: did this round add any new evidence?
            ev_now = sum(len(m.evidence) for m in st.transcript)
            no_progress = no_progress + 1 if ev_now == prev_evidence_count else 0
            prev_evidence_count = ev_now

            # S5 DECIDE
            if veto or consensus or no_progress >= 2:
                break

        # S6 SYNTHESIZE
        synthesis = self.synthesizer(st)
        synthesis.extra.setdefault("verifier_veto", veto)
        synthesis.extra.setdefault(
            "consensus", "reached" if consensus else ("none" if veto else "partial"))
        synthesis.extra.setdefault("rounds_used", st.round)
        synthesis.extra.setdefault("llm_involvement", llm_involvement)
        st.add(synthesis)

        out = synthesis.to_dict()
        out["transcript"] = [m.to_dict() for m in st.transcript]
        out["disclaimer"] = ("Research artifact. Not a capital recommendation. "
                             "Promotion requires human selection + Risk Officer "
                             "gate + cross-review (AGENTS.md sec.3).")
        return out


# ---------------------------------------------------------------------------
# Default deterministic agents (no LLM). Real roles plug in via AgentFn.
# ---------------------------------------------------------------------------
def _default_rebuttal(st: DebateState, challenge: Message) -> Message:
    target = challenge.to_agent or (st.proposals[0].from_agent if st.proposals else "?")
    return Message(
        debate_id=st.debate_id, round=st.round, from_agent=target,
        to_agent=challenge.from_agent, message_type="rebuttal",
        as_of_timestamp=st.as_of,
        content=f"{target} acknowledges the {challenge.severity}-severity point "
                f"and narrows its claim accordingly.",
        evidence=[], severity=challenge.severity, confidence=0.55, stance="neutral",
    )


def _default_critic(st: DebateState) -> Message:
    """Attack the highest-confidence proposal's weakest link (deterministic)."""
    if not st.proposals:
        target = "?"
        sev = "low"
    else:
        top = max(st.proposals, key=lambda m: m.confidence)
        target = top.from_agent
        sev = "high" if top.confidence > 0.8 else "medium"
    return Message(
        debate_id=st.debate_id, round=st.round, from_agent="CRITIC",
        to_agent=target, message_type="challenge", as_of_timestamp=st.as_of,
        content=f"Is {target}'s edge robust across regimes, or fitted to the "
                f"current one? Name the invalidation level.",
        evidence=[], severity=sev, confidence=0.6, stance="oppose",
    )


def _default_verifier(st: DebateState) -> Message:
    """
    Risk-Officer seat. Deterministic consensus rule for the stub:
      - consensus if >= threshold of proposals are 'support' stance AND no
        'high' severity challenge is open this round.
      - veto if any proposal carries a banned/padding flag (none in stub).
    """
    supports = sum(1 for p in st.proposals if p.stance == "support")
    frac = supports / max(1, len(st.proposals))
    open_high = any(m.message_type == "challenge" and m.severity == "high"
                    and m.round == st.round for m in st.transcript)
    consensus = (frac >= 2 / 3) and not open_high
    return Message(
        debate_id=st.debate_id, round=st.round, from_agent="VERIFIER",
        to_agent=None, message_type="verification", as_of_timestamp=st.as_of,
        content=("PIT + grade gate checked; no padding; "
                 + ("consensus reached." if consensus else "no consensus yet.")),
        evidence=[], severity="low", confidence=0.7, stance="neutral",
        extra={"consensus_reached": consensus, "veto": False,
               "support_fraction": round(frac, 3)},
    )


def _default_synthesizer(st: DebateState) -> Message:
    """Merge proposals into a structured, no-padding synthesis."""
    # Collect any actions the proposals carried (stub proposals may carry none).
    actions: List[Dict[str, Any]] = []
    for p in st.proposals:
        actions.extend(p.extra.get("proposed_actions", []) or [])
    actions = actions[:2]  # respect the 10-signal spirit; no padding
    avg_conf = round(sum(p.confidence for p in st.proposals)
                     / max(1, len(st.proposals)), 3)
    final_view = ("Society leans to action." if actions
                  else "No high-conviction action survived critique; stand down.")
    return Message(
        debate_id=st.debate_id, round=st.round, from_agent="SYNTHESIZER",
        to_agent=None, message_type="synthesis", as_of_timestamp=st.as_of,
        content=final_view, evidence=[], severity="low",
        confidence=avg_conf, stance="neutral",
        extra={
            "final_view": final_view,
            "proposed_actions": actions,
            "no_action_buckets": [] if actions else ["long_new", "short_new"],
            "risk_flags": [],
        },
    )


def make_default_engine() -> DebateEngine:
    return DebateEngine(_default_critic, _default_verifier, _default_synthesizer)


# ---------------------------------------------------------------------------
# Demo: 3-round debate, deterministic, llm_involvement="none"
# ---------------------------------------------------------------------------
def _demo() -> int:
    print("=" * 72)
    print("debate_engine self-test (3-round, deterministic, llm_involvement=none)")
    print("=" * 72)
    as_of = "2026-06-13"
    proposals = [
        Message(debate_id="", round=0, from_agent="MOMENTUM_SWING",
                message_type="proposal", as_of_timestamp=as_of,
                content="AAA breaking out on volume; propose small long.",
                evidence=["raw/market_data/finviz-export-universe-2026-06-13.csv"],
                confidence=0.72, stance="support",
                extra={"proposed_actions": [{"ticker": "AAA", "side": "long",
                                             "size_hint": "small"}]}),
        Message(debate_id="", round=0, from_agent="MACRO_REGIME",
                message_type="proposal", as_of_timestamp=as_of,
                content="Regime risk_on_moderate; breakouts have tailwind.",
                evidence=["outputs (PIT)"], confidence=0.6, stance="support"),
        Message(debate_id="", round=0, from_agent="MEAN_REVERSION_SWING",
                message_type="proposal", as_of_timestamp=as_of,
                content="AAA extended vs 50d; chasing has poor reward/risk.",
                evidence=[], confidence=0.55, stance="oppose"),
    ]
    engine = make_default_engine()
    result = engine.run("debate-2026-06-13-001",
                        topic="Add a long_new (AAA) to the society book today?",
                        as_of=as_of, proposals=proposals, max_rounds=3,
                        llm_involvement="none")
    # Trim transcript for readable demo output.
    compact = dict(result)
    compact["transcript_len"] = len(result["transcript"])
    compact["transcript"] = [f"{m['round']}:{m['from_agent']}:{m['message_type']}"
                             for m in result["transcript"]]
    print(json.dumps(compact, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(_demo())
