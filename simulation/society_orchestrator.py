#!/usr/bin/env python3
"""
Trading Society — Minimal Main Flow / Orchestrator Skeleton (E deliverable)

PPST Declaration (this PROGRAM):
- PROJECT: Trading Society
- PROGRAM: simulation/society_orchestrator.py (thin orchestrator demonstrating flow + PPST handoff contract)
- SKILL: PPST routing + role loading + phase dispatch (Debate / Backtest / Ranking / Evolution)
- TARGET: Runnable stub that:
  1. Declares the four layers on start.
  2. Loads (or stubs) the 7+1 core roles from CORE_AGENT_ROLES.
  3. Demonstrates a trivial "society step" (no real prices, no LLM calls yet).
  4. Prints compliance reminders (LLM-BACKTEST-PROTOCOL, PIT, daily action cap ~10, human veto).
  5. Shows example [CALL SKILL] handoff format for the next real TARGET.

This is research scaffolding only. It produces zero signals, zero backtest numbers, and zero capital recommendations.
Run: python simulation/society_orchestrator.py

Constraints observed:
- Respects docs/LLM-BACKTEST-PROTOCOL.md (this stub is llm_involvement="none").
- No lookahead possible (no data at all).
- Global daily_action_budget = 10.
- All real work must occur inside a declared PROGRAM via explicit handoff.
"""

from __future__ import annotations
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

# === PPST Four Layers (mandatory at start of any work block) ===
PROJECT = "Trading Society"
PROGRAM = "simulation/society_orchestrator.py (initial E skeleton)"
SKILL = "PPST routing + role loading + phase dispatch"
TARGET = "Demonstrate main flow stub; load roles; emit example handoff; print governance reminders. No data, no numbers, no LLM."


def declare_layers() -> None:
    print("=" * 72)
    print("PPST LAYERS (this execution)")
    print(f"PROJECT: {PROJECT}")
    print(f"PROGRAM: {PROGRAM}")
    print(f"SKILL:   {SKILL}")
    print(f"TARGET:  {TARGET}")
    print("=" * 72)
    print()


# === Role loading (stub — real version will parse CORE_AGENT_ROLES.md or a compiled JSON) ===
CORE_ROLES: List[Dict[str, Any]] = [
    {"name": "HF_SCALPER", "freq": "intraday", "model_size": "small", "niche": "high-frequency momentum scalps"},
    {"name": "MOMENTUM_SWING", "freq": "daily 1-5d", "model_size": "medium", "niche": "breakout/continuation swing"},
    {"name": "MEAN_REVERSION_SWING", "freq": "daily 2-10d", "model_size": "medium", "niche": "counter-trend overextension"},
    {"name": "MACRO_REGIME", "freq": "weekly+", "model_size": "large", "niche": "regime / cycle / strategic allocation"},
    {"name": "EVENT_CATALYST", "freq": "event-window", "model_size": "medium-large", "niche": "catalyst timing (earnings, M&A...)"},
    {"name": "VALUE_CONTRARIAN", "freq": "multi-month+", "model_size": "large", "niche": "deep value / long-horizon contrarian"},
    {"name": "OVERLAY_RISK", "freq": "continuous oversight", "model_size": "medium", "niche": "sizing, caps, DD halts, society action budget"},
    {"name": "SYNTHESIZER", "freq": "debate + final synthesis", "model_size": "largest", "niche": "cross-role debate, consensus, structured readout"},
]


def load_core_roles() -> List[Dict[str, Any]]:
    # In real impl: parse programs/trading_society/CORE_AGENT_ROLES.md frontmatter + sections,
    # or a compiled agents/roles.json. For now return the declared set.
    print("[Orchestrator] Loaded core roles (stub):")
    for r in CORE_ROLES:
        print(f"  - {r['name']:<22} freq={r['freq']:<18} model={r['model_size']:<12} niche={r['niche']}")
    print()
    return CORE_ROLES


# === Global society constraints ===
DAILY_ACTION_BUDGET = 10
LLM_PROTOCOL_NOTE = (
    "All future backtest paths involving LLMs MUST declare llm_involvement in {none, narration_only, decision_input, decision_output} "
    "and obey docs/LLM-BACKTEST-PROTOCOL.md (banned historical decision keys, walk-forward post-cutoff gating, before_as_of for RAG, etc.). "
    "This stub is llm_involvement='none'."
)


def simulate_society_step(as_of: str, active_roles: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Trivial stand-in for a full society cycle. No prices, no models, no P&L."""
    print(f"[Orchestrator] Simulated society step @ as_of={as_of}")
    print(f"  Active roles: {len(active_roles)}")
    print(f"  Global daily action budget: {DAILY_ACTION_BUDGET}")
    print(f"  {LLM_PROTOCOL_NOTE}")
    print()

    # In real flow:
    # 1. (optional) MACRO_REGIME emits regime context (narration)
    # 2. Tactical roles propose (respecting their niche + as_of)
    # 3. Debate Program runs 2-3 rounds if needed (SYNTHESIZER + Critics + Verifier)
    # 4. OVERLAY_RISK filters + sizes against caps + budget
    # 5. Performance Tracker records the "decisions" for later ranking
    # 6. Reflection (if poor recent fitness) produces adjustment proposals
    #
    # Here we just emit a skeleton readout.

    readout = {
        "as_of_timestamp": as_of,
        "project": PROJECT,
        "program": PROGRAM,
        "society_step": "stub_only",
        "roles_participated": [r["name"] for r in active_roles],
        "daily_action_budget": DAILY_ACTION_BUDGET,
        "actions_proposed_total": 0,  # would be sum of proposals after debate/overlay
        "no_action_buckets": ["long_new", "short_new", "position_followup"],  # example alignment with 10-signal spirit
        "llm_involvement": "none",
        "notes": [
            "This is scaffolding. Real step would invoke Debate Program or Backtest Program.",
            "Human retains winner selection.",
            "Any output that could affect capital decisions later requires Risk Officer gate + cross-review per AGENTS.md §3.",
        ],
    }
    print("[Orchestrator] Society step readout (stub):")
    print(json.dumps(readout, indent=2, ensure_ascii=False))
    print()
    return readout


def emit_call_skill_example(next_program: str, next_skill: str, next_target: str) -> None:
    """Print a ready-to-paste [CALL SKILL] block for the next real TARGET."""
    print("[Handoff Example — copy/paste for next agent or self]")
    print("[CALL SKILL]")
    print(f"PROJECT: {PROJECT}")
    print(f"PROGRAM: {next_program}")
    print(f"SKILL: {next_skill}")
    print(f"TARGET: {next_target}")
    print("CONTEXT: Core roles defined in programs/trading_society/CORE_AGENT_ROLES.md. Start with Debate Program skeleton or Backtest Program protocol wiring. Use only PIT data. Declare layers on every block. No capital outputs without gate.")
    print()


def run_integrated_cycle(as_of: str = "2026-06-13") -> Optional[Dict[str, Any]]:
    """
    End-to-end demonstration that the A/B/C/D/E pieces compose:
      backtest_runner (B) -> ranking_system (D) -> reflection_engine (D)
      -> mutator (D), plus a debate_engine (C) pass. Deterministic, synthetic,
      llm_involvement='none'. Never emits a capital recommendation.

    Degrades gracefully (never-raise) if any module is unavailable.
    """
    try:
        # Ensure the repo root is importable when run as a bare script.
        _root = str(Path(__file__).resolve().parents[1])
        if _root not in sys.path:
            sys.path.insert(0, _root)
        from simulation.backtest_runner import (
            AgentSpec, BacktestConfig, run_backtest, result_to_artifact,
            _synthetic_series, _momentum_agent, _reversion_agent,
        )
        from simulation.reflection_engine import reflect_bottom
        from simulation.evolution.mutator import AgentConfig, apply_reflection
        from simulation.debate_engine import make_default_engine, Message
    except Exception as e:  # pragma: no cover
        print(f"[Orchestrator] integrated cycle skipped (import): {e}")
        return None

    print("=" * 72)
    print("INTEGRATED SOCIETY CYCLE (B->D->C compose; synthetic; llm=none)")
    print("=" * 72)

    # --- B: backtest two deterministic agents on a synthetic PIT series ---
    series = _synthetic_series()
    agents = [
        AgentSpec("MOMENTUM_SWING", _momentum_agent, niche_purity=1.0),
        AgentSpec("MEAN_REVERSION_SWING", _reversion_agent, niche_purity=0.95),
    ]
    cfg = BacktestConfig(start="2025-01-06", end="2025-01-31",
                         llm_involvement="none",
                         regime_labeler=lambda d: "risk_on")
    res = run_backtest(agents, series, cfg)
    art = result_to_artifact(res)
    print(f"[B] backtest: {art['window']['n_trading_dates']} dates, "
          f"kpi_eligible={art['kpi_eligible']}, "
          f"top={art['scoreboard'][0]['agent_id'] if art['scoreboard'] else None}")

    # --- D: rank, then reflect on the bottom, then mutate (candidate only) ---
    # The runner already scored every agent; build ranking rows from its
    # scoreboard directly (a full RankingSystem re-rank is shown in its own demo).
    ranking_rows = [
        {"agent_id": r["agent_id"], "fitness": r["fitness"],
         "components": r["fitness_components"]}
        for r in res.scoreboard
    ]
    ranking_rows.sort(key=lambda r: r["fitness"])
    bottom = ranking_rows[:1]
    reflections = reflect_bottom(bottom)
    print(f"[D] ranking: leader={ranking_rows[-1]['agent_id']}, "
          f"reflecting on={[r['agent_id'] for r in bottom]}")
    if reflections:
        rf = reflections[0]
        cfg_agent = AgentConfig(agent_id=rf["agent_id"], niche="counter_trend",
                                params={"regime_filter_strictness": 0.3})
        cand = apply_reflection(cfg_agent, rf)
        print(f"[D] reflection: weakest={rf['weakest_component']} -> "
              f"mutation candidate v{cand['candidate']['version']} "
              f"(human_gate={cand['requires_human_gate']})")

    # --- C: debate "add a long today?" with role proposals ---
    proposals = [
        Message(debate_id="", round=0, from_agent="MOMENTUM_SWING",
                message_type="proposal", as_of_timestamp=as_of,
                content="Breakout; small long.", confidence=0.72, stance="support",
                extra={"proposed_actions": [{"ticker": "AAA", "side": "long",
                                             "size_hint": "small"}]}),
        Message(debate_id="", round=0, from_agent="MACRO_REGIME",
                message_type="proposal", as_of_timestamp=as_of,
                content="Regime supportive.", confidence=0.6, stance="support"),
        Message(debate_id="", round=0, from_agent="MEAN_REVERSION_SWING",
                message_type="proposal", as_of_timestamp=as_of,
                content="Extended; poor reward/risk.", confidence=0.55,
                stance="oppose"),
    ]
    debate = make_default_engine().run(
        "debate-integrated-001", topic="Add a long_new today?", as_of=as_of,
        proposals=proposals, max_rounds=3, llm_involvement="none")
    print(f"[C] debate: consensus={debate['consensus']}, "
          f"actions={len(debate.get('proposed_actions', []))}, "
          f"confidence={debate['confidence']}, veto={debate['verifier_veto']}")
    print("[E] cycle complete. All artifacts are research; promotion needs human "
          "selection + Risk Officer gate + cross-review.")
    print()
    return {"backtest": art, "ranking": ranking_rows, "debate_consensus":
            debate["consensus"]}


def main() -> int:
    declare_layers()

    print(f"Trading Society orchestrator stub — {datetime.now(timezone.utc).isoformat()}")
    print("Research only. Zero production signals. Governance first.")
    print()

    roles = load_core_roles()

    # Example "today" — in real use this comes from the simulation clock or lake as_of
    today = "2026-06-13"
    _ = simulate_society_step(today, roles)

    # Integrated demonstration that A/B/C/D/E now compose (additive; never-raise).
    if "--stub-only" not in sys.argv:
        run_integrated_cycle(today)

    print("Governance reminders (never relax):")
    print("  - Point-in-time discipline (CLAUDE §2): as_of_timestamp on everything.")
    print("  - LLM backtest protocol: docs/LLM-BACKTEST-PROTOCOL.md is mandatory for any historical decisioning.")
    print("  - ~10 action cap per society-day (aligns with 10-signal contract).")
    print("  - Human chooses winners; evolution is assistive.")
    print("  - Niche protection + novelty injection to avoid winner-take-all.")
    print("  - Raw/ immutable; benchmark lists (incl. 1980-2026 leaders in grok.md) require fresh PIT reconstruction.")
    print("  - No direct writes to outputs/picks-* or wiki/05_recommendations/* without Risk Officer + cross-review.")
    print()

    # Show the handoff pattern for the *actual* next work
    emit_call_skill_example(
        next_program="programs/debate/DEBATE_PROGRAM.md (or simulation/backtest_runner.py)",
        next_skill="multi_round_debate (adapt from grok.md) OR backtest_harness + protocol_compliance",
        next_target="Implement 2-3 round Debate Engine that accepts role proposals (from CORE_AGENT_ROLES), runs Critic/Verifier, produces structured synthesis. Or wire first role into a protocol-compliant backtest step on a tiny recent window.",
    )

    print("Stub complete. To extend: implement a real PROGRAM TARGET and hand off with the four layers.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
