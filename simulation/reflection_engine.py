#!/usr/bin/env python3
"""
Trading Society -- Reflection Engine (D deliverable, part 2 of 3)

PPST Declaration (this PROGRAM):
- PROJECT: Trading Society
- PROGRAM: simulation/reflection_engine.py
- SKILL:   reflection_engine (diagnose weak fitness -> structured adjustment proposal)
- TARGET:  For each bottom-ranked agent, produce a deterministic, falsifiable
           Reflection Report: its weakest fitness component, the likely cause,
           and a *proposed* adjustment (param delta and/or prompt delta) for the
           Mutator to consider. Research only. No self-modification, no LLM, no
           capital output. The adjustment is a PROPOSAL -- a human/Evolution gate
           decides whether to apply it.

Why deterministic: a Reflection step that itself used an LLM to "explain" past
performance would invite hindsight narration (docs/LLM-BACKTEST-PROTOCOL.md
spirit). Here, cause->fix is a transparent lookup keyed on the measured weakest
component, so the reasoning is auditable.

Run: python simulation/reflection_engine.py   (synthetic demo)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

# Map each weak fitness component to a likely cause + a concrete, reversible
# adjustment proposal. Keep deltas small (controlled evolution, CLAUDE.md).
COMPONENT_PLAYBOOK: Dict[str, Dict[str, Any]] = {
    "risk_adjusted": {
        "cause": "Raw return is fine but risk-adjusted (Calmar/Sortino) is weak: "
                 "drawdowns or volatility are eating the edge.",
        "param_delta": {"position_size_scale": -0.20, "stop_tightness": +0.15},
        "prompt_delta": "Add: 'state an explicit invalidation/stop level for every "
                        "proposal; prefer asymmetric reward/risk >= 2:1.'",
    },
    "regime_stability": {
        "cause": "Edge is regime-fitted: strong in one regime, collapses in "
                 "others (curve-fit risk).",
        "param_delta": {"regime_filter_strictness": +0.25},
        "prompt_delta": "Add: 'before proposing, check the current regime label; "
                        "stand down when your edge historically underperforms it.'",
    },
    "drawdown_control": {
        "cause": "Max drawdown too deep: sizing or correlation risk unmanaged.",
        "param_delta": {"position_size_scale": -0.25, "max_concurrent": -1},
        "prompt_delta": "Add: 'cap concurrent correlated exposure; halve size after "
                        "two consecutive losing periods.'",
    },
    "hit_quality": {
        "cause": "Win rate x payoff is weak: entries are low-quality or exits cut "
                 "winners / let losers run.",
        "param_delta": {"entry_threshold": +0.15, "trail_exit": +0.10},
        "prompt_delta": "Add: 'raise the entry bar; only act on the top-quartile "
                        "setups; let winners trail, cut losers fast.'",
    },
    "turnover_discipline": {
        "cause": "Over-trading: action count exceeds its share of the society "
                 "budget (noise-chasing).",
        "param_delta": {"min_holding_periods": +1, "entry_threshold": +0.20},
        "prompt_delta": "Add: 'fewer, higher-conviction actions; respect the "
                        "society daily action budget; default to no_action.'",
    },
    "niche_purity": {
        "cause": "Niche bleed: acting outside the declared (frequency x edge) slot.",
        "param_delta": {"niche_lock": +1},
        "prompt_delta": "Add: 'only generate ideas inside your declared horizon "
                        "and edge; route out-of-niche names to the owning role.'",
    },
}


@dataclass
class ReflectionReport:
    agent_id: str
    fitness: float
    weakest_component: str
    weakest_value: float
    cause: str
    param_delta: Dict[str, float]
    prompt_delta: str
    confidence: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "reflection_report",
            "role": "writer",
            "agent_id": self.agent_id,
            "fitness": self.fitness,
            "weakest_component": self.weakest_component,
            "weakest_value": round(self.weakest_value, 3),
            "diagnosed_cause": self.cause,
            "proposed_param_delta": self.param_delta,
            "proposed_prompt_delta": self.prompt_delta,
            "confidence": self.confidence,
            "status": "PROPOSAL",
            "note": ("Proposal only. Mutator + human/Evolution gate decides "
                     "whether to apply. Reversible by design."),
        }


# Step 3: structured dot-com analog appended when an agent is bleeding on the
# capital-preservation axes during a high-valuation regime.
_DOTCOM_TEMPLATE = (
    " [dot-com analog] In a high-valuation regime this failure mode mirrors "
    "1999-2000: chasing extended, narrative-driven names into a repricing. "
    "Stress-test the thesis against a 30-50% drawdown and prefer protection over "
    "participation."
)
_DOTCOM_WEAK = {"risk_adjusted", "drawdown_control", "regime_stability"}


def reflect_one(agent_id: str, fitness: float,
                components: Dict[str, float],
                regime: Optional[str] = None) -> ReflectionReport:
    """Diagnose the single weakest fitness component and propose a fix.

    In a high-valuation regime a dot-com structured analog is appended to the
    cause + prompt when the weak axis is a capital-preservation one (Step 3).
    """
    if not components:
        weakest, val = "risk_adjusted", 0.0
    else:
        weakest = min(components, key=components.get)
        val = components[weakest]
    play = COMPONENT_PLAYBOOK.get(weakest, COMPONENT_PLAYBOOK["risk_adjusted"])
    cause = play["cause"]
    prompt_delta = play["prompt_delta"]
    if regime == "high_valuation" and weakest in _DOTCOM_WEAK:
        cause = cause + _DOTCOM_TEMPLATE
        prompt_delta = prompt_delta + " Add a dot-com 30-50% drawdown stress test."
    # Confidence in the diagnosis scales with how clearly one component is worst.
    sorted_vals = sorted(components.values()) if components else [0.0, 0.0]
    gap = (sorted_vals[1] - sorted_vals[0]) if len(sorted_vals) > 1 else 0.0
    confidence = round(0.5 + min(0.4, gap), 3)
    return ReflectionReport(
        agent_id=agent_id, fitness=fitness, weakest_component=weakest,
        weakest_value=val, cause=cause,
        param_delta=dict(play["param_delta"]), prompt_delta=prompt_delta,
        confidence=confidence,
    )


def reflect_bottom(ranking_rows: List[Dict[str, Any]],
                   regime: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Given ranking rows (from ranking_system.report()['ranking'], already the
    bottom set or full set), produce a reflection report for each.
    Each row needs: agent_id, fitness, components. Pass regime="high_valuation"
    to attach the dot-com analog where relevant (Step 3).
    """
    reports = []
    for row in ranking_rows:
        comps = row.get("components", {})
        rep = reflect_one(row["agent_id"], row.get("fitness", 0.0), comps, regime)
        reports.append(rep.to_dict())
    return reports


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------
def _demo() -> int:
    import json
    print("=" * 72)
    print("reflection_engine self-test (deterministic cause->fix)")
    print("=" * 72)
    # Two synthetic under-performers with different weak spots.
    rows = [
        {"agent_id": "MEAN_REVERSION_SWING", "fitness": 0.41,
         "components": {"risk_adjusted": 0.6, "regime_stability": 0.16,
                        "drawdown_control": 0.9, "hit_quality": 0.2,
                        "turnover_discipline": 1.0, "niche_purity": 0.9}},
        {"agent_id": "HF_SCALPER", "fitness": 0.38,
         "components": {"risk_adjusted": 0.5, "regime_stability": 0.5,
                        "drawdown_control": 0.7, "hit_quality": 0.4,
                        "turnover_discipline": 0.15, "niche_purity": 1.0}},
    ]
    print(json.dumps(reflect_bottom(rows), indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(_demo())
