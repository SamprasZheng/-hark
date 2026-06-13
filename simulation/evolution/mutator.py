#!/usr/bin/env python3
"""
Trading Society -- Mutator (D deliverable, part 3 of 3; base / Phase 2-3 bridge)

PPST Declaration (this PROGRAM):
- PROJECT: Trading Society
- PROGRAM: simulation/evolution/mutator.py
- SKILL:   agent_mutator (apply a reflection proposal as a bounded, reversible
           config delta; niche-aware new-agent injection)
- TARGET:  Deterministic base mutator: given an agent config + a Reflection
           proposal, produce a *candidate* mutated config (never auto-promoted),
           clamp deltas to safe bounds, and support occasional novelty injection
           into an empty niche. Every promotion is human-gated. No LLM, no
           capital output.

Controlled evolution (CLAUDE.md): mutations are small, bounded, reversible, and
logged. Nothing here becomes "active" for any capital-facing use without human
selection + Risk Officer gate (programs/evolution/EVOLUTION_PROGRAM.md).

Run: python simulation/evolution/mutator.py   (synthetic demo)
"""

from __future__ import annotations

import copy
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

# Safe bounds for the tunable params a Reflection proposal may touch, plus the
# strategy-genome params the Evolution/Tournament layers perturb.
PARAM_BOUNDS: Dict[str, tuple] = {
    "position_size_scale": (0.25, 2.0),
    "stop_tightness": (0.0, 1.0),
    "regime_filter_strictness": (0.0, 1.0),
    "entry_threshold": (0.0, 0.10),
    "trail_exit": (0.0, 1.0),
    "min_holding_periods": (0, 30),
    "max_concurrent": (1, 20),
    "niche_lock": (0, 1),
    # strategy genome (simulation/strategy_agent.py)
    "lookback": (1, 20),
    "momentum_tilt": (-1.0, 1.0),
    "max_actions": (1, 5),
}
# Params that are integers (rounded after perturbation).
_INT_PARAMS = {"min_holding_periods", "max_concurrent", "niche_lock",
               "lookback", "max_actions"}
# Max fractional change applied per mutation step (controlled evolution).
MAX_STEP = 0.25


@dataclass
class AgentConfig:
    agent_id: str
    niche: str
    params: Dict[str, float] = field(default_factory=dict)
    prompt_addenda: List[str] = field(default_factory=list)
    version: int = 1
    lineage: List[str] = field(default_factory=list)  # parent agent_ids

    def clone(self) -> "AgentConfig":
        return copy.deepcopy(self)

    def to_dict(self) -> Dict[str, Any]:
        return {"agent_id": self.agent_id, "niche": self.niche,
                "params": self.params, "prompt_addenda": self.prompt_addenda,
                "version": self.version, "lineage": self.lineage}


def _clamp(name: str, value: float) -> float:
    lo, hi = PARAM_BOUNDS.get(name, (-1e9, 1e9))
    return max(lo, min(hi, value))


def apply_reflection(config: AgentConfig, reflection: Dict[str, Any]
                     ) -> Dict[str, Any]:
    """
    Produce a CANDIDATE mutated config by applying a reflection report's deltas.
    Returns {candidate, change_log, requires_human_gate=True}. Never mutates in
    place; never marks the candidate active.
    """
    cand = config.clone()
    change_log: List[str] = []

    deltas = reflection.get("proposed_param_delta", {}) or {}
    for name, delta in deltas.items():
        old = cand.params.get(name, _default_for(name))
        # interpret delta as an additive step but clamp the per-step magnitude
        step = delta
        if abs(step) > MAX_STEP and name in ("position_size_scale", "stop_tightness",
                                             "regime_filter_strictness",
                                             "entry_threshold", "trail_exit"):
            step = MAX_STEP if step > 0 else -MAX_STEP
        new = _clamp(name, old + step)
        cand.params[name] = round(new, 4)
        change_log.append(f"{name}: {old} -> {cand.params[name]} (delta {delta})")

    addendum = reflection.get("proposed_prompt_delta")
    if addendum and addendum not in cand.prompt_addenda:
        cand.prompt_addenda.append(addendum)
        change_log.append(f"prompt += '{addendum[:48]}...'")

    cand.version = config.version + 1
    cand.lineage = config.lineage + [config.agent_id]

    return {
        "type": "mutation_candidate",
        "role": "writer",
        "parent": config.agent_id,
        "candidate": cand.to_dict(),
        "change_log": change_log,
        "source_reflection": reflection.get("weakest_component"),
        "requires_human_gate": True,
        "active": False,
        "note": ("Candidate only. Backtest across multiple regimes, then human "
                 "selection + Risk Officer gate before any capital-facing use "
                 "(EVOLUTION_PROGRAM.md)."),
    }


def _default_for(name: str) -> float:
    lo, hi = PARAM_BOUNDS.get(name, (0.0, 1.0))
    if name == "position_size_scale":
        return 1.0
    if name in ("min_holding_periods",):
        return 1
    if name in ("max_concurrent",):
        return 5
    return round((lo + hi) / 2.0, 4)


def mutate_random(config: AgentConfig, rng, magnitude: float = 0.20,
                  n_params: int = 2) -> "AgentConfig":
    """
    Produce a CANDIDATE offspring by perturbing up to n_params genome params
    within bounds, using the supplied seeded rng (random.Random) for
    reproducibility. Bounded (controlled evolution). Returns a new AgentConfig
    (active state is the caller's concern; nothing here is capital-active).
    """
    cand = config.clone()
    tunable = [k for k in cand.params.keys() if k in PARAM_BOUNDS] or \
        ["entry_threshold", "lookback"]
    rng.shuffle(tunable)
    for name in tunable[:max(1, n_params)]:
        lo, hi = PARAM_BOUNDS[name]
        old = cand.params.get(name, _default_for(name))
        span = (hi - lo)
        delta = rng.uniform(-magnitude, magnitude) * span
        new = _clamp(name, old + delta)
        if name in _INT_PARAMS:
            new = int(round(new))
        else:
            new = round(new, 4)
        cand.params[name] = new
    cand.version = config.version + 1
    cand.lineage = config.lineage + [config.agent_id]
    return cand


def propose_novelty_injection(filled_niches: List[str],
                              candidate_niches: List[str]) -> Optional[Dict[str, Any]]:
    """
    Anti winner-take-all: if a declared niche is empty, propose injecting a fresh
    agent there (deterministic pick = first unfilled, to stay reproducible).
    Returns a proposal dict or None if all niches are covered.
    """
    empty = [n for n in candidate_niches if n not in set(filled_niches)]
    if not empty:
        return None
    target = empty[0]
    return {
        "type": "novelty_injection_candidate",
        "role": "writer",
        "new_agent_niche": target,
        "rationale": f"Niche '{target}' is unoccupied; inject diversity rather "
                     f"than let leaders crowd existing niches.",
        "requires_human_gate": True,
        "active": False,
    }


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------
def _demo() -> int:
    import json
    print("=" * 72)
    print("mutator self-test (controlled, reversible, human-gated)")
    print("=" * 72)
    cfg = AgentConfig(
        agent_id="MEAN_REVERSION_SWING", niche="counter_trend",
        params={"position_size_scale": 1.0, "regime_filter_strictness": 0.3},
    )
    reflection = {
        "agent_id": "MEAN_REVERSION_SWING",
        "weakest_component": "regime_stability",
        "proposed_param_delta": {"regime_filter_strictness": +0.25},
        "proposed_prompt_delta": "Add: 'check the current regime label; stand "
                                 "down when your edge underperforms it.'",
    }
    print(json.dumps(apply_reflection(cfg, reflection), indent=2, ensure_ascii=False))

    print("\n--- novelty injection ---")
    proposal = propose_novelty_injection(
        filled_niches=["daily_momentum", "counter_trend"],
        candidate_niches=["daily_momentum", "counter_trend", "intraday",
                          "event_catalyst"],
    )
    print(json.dumps(proposal, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(_demo())
