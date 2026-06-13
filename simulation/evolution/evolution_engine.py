#!/usr/bin/env python3
"""
Trading Society -- Evolution Engine (演化; Phase 3)

PPST Declaration (this PROGRAM):
- PROJECT: Trading Society
- PROGRAM: simulation/evolution/evolution_engine.py
- SKILL:   selection + mutation + reflection + novelty injection over generations
- TARGET:  A reproducible generational loop -- compete (cross-regime tournament)
           -> select elites -> reflect+mutate the worst -> breed offspring ->
           novelty-inject empty niches -> next generation -> evolution log.
           Multi-regime evaluation mandatory; every promotion is human-gated.
           No LLM, no capital output.

Governance (CLAUDE.md sec.10 / EVOLUTION_PROGRAM.md):
- Niche protection: declared niches are kept filled (novelty injection on empty).
- Anti winner-take-all: elites carry over but offspring + novelty keep diversity.
- Multi-regime: fitness is the tournament's cross-regime score (worst-regime is
  half), so single-regime winners cannot dominate -- the metric-level defense
  against curve-fitting.
- Human is the final selector: nothing here becomes "active" for capital-facing
  use. The whole output is a research evolution log.

Run: python simulation/evolution/evolution_engine.py   (3-generation demo)
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

try:
    from simulation.tournament import (
        compete, make_synthetic_regimes, RegimeWindow, CompetitorResult)
    from simulation.strategy_agent import make_agent_spec
    from simulation.backtest_runner import BacktestConfig, run_backtest
    from simulation.evolution.mutator import (
        AgentConfig, mutate_random, apply_reflection, propose_novelty_injection)
    from simulation.reflection_engine import reflect_one
except Exception:  # pragma: no cover
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    from simulation.tournament import (
        compete, make_synthetic_regimes, RegimeWindow, CompetitorResult)
    from simulation.strategy_agent import make_agent_spec
    from simulation.backtest_runner import BacktestConfig, run_backtest
    from simulation.evolution.mutator import (
        AgentConfig, mutate_random, apply_reflection, propose_novelty_injection)
    from simulation.reflection_engine import reflect_one

import math


def _ceil(x: float) -> int:
    return int(math.ceil(x))


def _components_for(cfg: AgentConfig, window: RegimeWindow,
                    action_budget: int) -> Dict[str, float]:
    """Run one backtest in a given window to recover an agent's fitness components."""
    spec = make_agent_spec(cfg)
    bcfg = BacktestConfig(start=window.start, end=window.end, llm_involvement="none",
                          action_budget=action_budget,
                          regime_labeler=lambda d, _l=window.label: _l)
    res = run_backtest([spec], window.series, bcfg)
    if res.scoreboard:
        return res.scoreboard[0].get("fitness_components", {})
    return {}


@dataclass
class EvolutionEngine:
    windows: List[RegimeWindow]
    action_budget: int = 10
    elite_frac: float = 0.34
    seed: int = 7
    declared_niches: Optional[List[str]] = None

    def __post_init__(self):
        self._rng = random.Random(self.seed)

    def _window_by_label(self, label: str) -> RegimeWindow:
        for w in self.windows:
            if w.label == label:
                return w
        return self.windows[0]

    def evolve(self, population: List[AgentConfig], generations: int = 3
               ) -> Dict[str, Any]:
        pop = [c.clone() for c in population]
        N = len(pop)
        declared = self.declared_niches or sorted({c.niche for c in pop})
        gen_logs: List[Dict[str, Any]] = []

        for g in range(generations):
            board = compete(pop, self.windows, self.action_budget)
            by_id = {c.agent_id: c for c in pop}
            n_elite = max(1, _ceil(self.elite_frac * N))
            elites = [by_id[r.agent_id].clone() for r in board[:n_elite]
                      if r.agent_id in by_id]

            # Reflection-guided mutation of the single worst competitor.
            worst = board[-1]
            worst_cfg = by_id.get(worst.agent_id)
            reflection_note = None
            refl_cand: Optional[AgentConfig] = None
            if worst_cfg is not None:
                comps = _components_for(worst_cfg,
                                        self._window_by_label(worst.worst_regime),
                                        self.action_budget)
                refl = reflect_one(worst_cfg.agent_id, worst.worst_fitness, comps).to_dict()
                cand = apply_reflection(worst_cfg, refl)["candidate"]
                refl_cand = AgentConfig(
                    agent_id=f"{worst_cfg.agent_id}~refl.g{g+1}", niche=cand["niche"],
                    params=cand["params"], prompt_addenda=cand["prompt_addenda"],
                    version=cand["version"], lineage=cand["lineage"])
                reflection_note = {"target": worst_cfg.agent_id,
                                   "weakest": refl["weakest_component"],
                                   "param_delta": refl["proposed_param_delta"]}

            # Breed offspring from elites to refill the population.
            next_pop: List[AgentConfig] = [e.clone() for e in elites]
            if refl_cand is not None:
                next_pop.append(refl_cand)
            oi = 0
            while len(next_pop) < N:
                parent = elites[oi % len(elites)]
                child = mutate_random(parent, self._rng)
                child.agent_id = f"{parent.agent_id}~g{g+1}o{oi}"
                next_pop.append(child)
                oi += 1
            next_pop = next_pop[:N]

            # Novelty injection: keep declared niches filled (anti winner-take-all).
            present = {c.niche for c in next_pop}
            novelty_note = propose_novelty_injection(sorted(present), declared)
            if novelty_note is not None and next_pop:
                target_niche = novelty_note["new_agent_niche"]
                fresh = AgentConfig(
                    agent_id=f"NOVEL.{target_niche}.g{g+1}", niche=target_niche,
                    params={"momentum_tilt": self._rng.choice([1.0, -1.0]),
                            "lookback": self._rng.randint(1, 8),
                            "entry_threshold": round(self._rng.uniform(0.004, 0.02), 4),
                            "max_actions": 2},
                    lineage=["<novelty>"])
                next_pop[-1] = fresh  # replace the weakest offspring slot

            gen_logs.append({
                "generation": g + 1,
                "population_size": N,
                "leaderboard_top": [r.to_dict() for r in board[:3]],
                "elites": [e.agent_id for e in elites],
                "reflection_mutation": reflection_note,
                "novelty_injection": novelty_note,
                "next_population": [c.agent_id for c in next_pop],
            })
            pop = next_pop

        # Final competition on the evolved population.
        final_board = compete(pop, self.windows, self.action_budget)
        return {
            "type": "trading_society_evolution_log",
            "role": "writer",
            "seed": self.seed,
            "generations": generations,
            "regimes": [w.label for w in self.windows],
            "elite_frac": self.elite_frac,
            "generation_logs": gen_logs,
            "final_leaderboard": [r.to_dict() for r in final_board],
            "final_champion": final_board[0].agent_id if final_board else None,
            "requires_human_gate_for_promotion": True,
            "active": False,
            "disclaimer": ("Research evolution log. Nothing here is capital-active. "
                           "Promotion of any evolved agent requires human selection "
                           "+ Risk Officer gate + cross-review (AGENTS.md sec.3)."),
        }


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------
def _seed_population() -> List[AgentConfig]:
    return [
        AgentConfig("MOM_fast", "daily_momentum",
                    params={"momentum_tilt": 1.0, "lookback": 2, "entry_threshold": 0.006, "max_actions": 2}),
        AgentConfig("MOM_slow", "daily_momentum",
                    params={"momentum_tilt": 1.0, "lookback": 5, "entry_threshold": 0.010, "max_actions": 2}),
        AgentConfig("REV_fast", "counter_trend",
                    params={"momentum_tilt": -1.0, "lookback": 1, "entry_threshold": 0.006, "max_actions": 2}),
        AgentConfig("REV_slow", "counter_trend",
                    params={"momentum_tilt": -1.0, "lookback": 3, "entry_threshold": 0.012, "max_actions": 2}),
        AgentConfig("MOM_mid", "daily_momentum",
                    params={"momentum_tilt": 1.0, "lookback": 3, "entry_threshold": 0.008, "max_actions": 2}),
        AgentConfig("REV_mid", "counter_trend",
                    params={"momentum_tilt": -1.0, "lookback": 2, "entry_threshold": 0.009, "max_actions": 2}),
    ]


def _demo() -> int:
    import json
    print("=" * 72)
    print("evolution_engine self-test -- 3 generations x 3 regimes (llm=none)")
    print("=" * 72)
    windows = make_synthetic_regimes()
    engine = EvolutionEngine(windows, action_budget=10, elite_frac=0.34, seed=7)
    log = engine.evolve(_seed_population(), generations=3)

    for gl in log["generation_logs"]:
        top = gl["leaderboard_top"][0]
        print(f"\n  Gen {gl['generation']}: champion={top['agent_id']} "
              f"score={top['cross_regime_score']} (worst={top['worst_regime']})")
        print(f"    elites={gl['elites']}")
        if gl["reflection_mutation"]:
            rm = gl["reflection_mutation"]
            print(f"    reflect: {rm['target']} weakest={rm['weakest']} "
                  f"delta={rm['param_delta']}")
        if gl["novelty_injection"]:
            print(f"    novelty: {gl['novelty_injection']['new_agent_niche']}")
    fb = log["final_leaderboard"][0]
    print(f"\n  FINAL champion: {log['final_champion']} "
          f"score={fb['cross_regime_score']} "
          f"(human-gate for promotion: {log['requires_human_gate_for_promotion']})")
    return 0


if __name__ == "__main__":
    raise SystemExit(_demo())
