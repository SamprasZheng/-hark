#!/usr/bin/env python3
"""
Trading Society -- Ranking System (D deliverable, part 1 of 3)

PPST Declaration (this PROGRAM):
- PROJECT: Trading Society
- PROGRAM: simulation/ranking_system.py
- SKILL:   performance_evaluator -> ranking (multi-horizon, niche-aware)
- TARGET:  Turn per-agent fitness (from performance_tracker) into Weekly /
           Monthly / Yearly rankings with rank deltas, a bottom-K selection for
           Reflection, and a niche-coverage report. Deterministic, no LLM, no
           capital output.

Anti "big-get-bigger" design (CLAUDE.md niche protection): ranking carries a
niche-coverage view so the Evolution Program can protect empty niches rather
than let one winner crowd the book.

Run: python simulation/ranking_system.py   (synthetic demo)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Sequence

try:
    from simulation.performance_tracker import PerformanceTracker, FitnessResult
except Exception:  # pragma: no cover
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from simulation.performance_tracker import PerformanceTracker, FitnessResult

HORIZONS = ("weekly", "monthly", "yearly")

# Horizon-specific weight tilts (sum is normalized inside compute_fitness).
# Short horizons weight hit quality + turnover; long horizons weight stability.
HORIZON_WEIGHTS: Dict[str, Dict[str, float]] = {
    "weekly": {"risk_adjusted": 0.25, "regime_stability": 0.10,
               "drawdown_control": 0.20, "hit_quality": 0.30,
               "turnover_discipline": 0.10, "niche_purity": 0.05},
    "monthly": {"risk_adjusted": 0.30, "regime_stability": 0.20,
                "drawdown_control": 0.20, "hit_quality": 0.15,
                "turnover_discipline": 0.10, "niche_purity": 0.05},
    "yearly": {"risk_adjusted": 0.30, "regime_stability": 0.30,
               "drawdown_control": 0.25, "hit_quality": 0.05,
               "turnover_discipline": 0.05, "niche_purity": 0.05},
}

# Step 3: in a high-valuation regime, reward capital preservation + cross-regime
# robustness and de-emphasize raw hit quality (CLAUDE.md sec.10 spirit). Niche
# purity gets extra weight so the dedicated hedger / risk-off voices count more.
HIGH_VALUATION_WEIGHTS: Dict[str, float] = {
    "risk_adjusted": 0.20, "regime_stability": 0.28, "drawdown_control": 0.30,
    "hit_quality": 0.05, "turnover_discipline": 0.07, "niche_purity": 0.10,
}


@dataclass
class RankRow:
    rank: int
    agent_id: str
    fitness: float
    components: Dict[str, float]
    niche: Optional[str] = None
    prev_rank: Optional[int] = None

    @property
    def rank_delta(self) -> Optional[int]:
        if self.prev_rank is None:
            return None
        return self.prev_rank - self.rank  # positive = moved up

    def to_dict(self) -> Dict[str, Any]:
        return {"rank": self.rank, "agent_id": self.agent_id,
                "fitness": self.fitness, "rank_delta": self.rank_delta,
                "niche": self.niche,
                "weakest_component": min(self.components, key=self.components.get)
                if self.components else None,
                "components": {k: round(v, 3) for k, v in self.components.items()}}


class RankingSystem:
    """Builds horizon rankings from a PerformanceTracker."""

    def __init__(self, niches: Optional[Dict[str, str]] = None) -> None:
        # niches: {agent_id: niche_label}, e.g. {"HF_SCALPER": "intraday"}
        self.niches = niches or {}
        self._prev: Dict[str, Dict[str, int]] = {h: {} for h in HORIZONS}

    def rank(self, tracker: PerformanceTracker, horizon: str = "monthly",
             regime: Optional[str] = None) -> List[RankRow]:
        if horizon not in HORIZONS:
            raise ValueError(f"horizon must be one of {HORIZONS}")
        # In a high-valuation regime, override the horizon tilt with the
        # capital-preservation weighting (Step 3).
        if regime == "high_valuation":
            weights = HIGH_VALUATION_WEIGHTS
        else:
            weights = HORIZON_WEIGHTS[horizon]
        scored = []
        for aid in tracker.records:
            f: FitnessResult = tracker.fitness_for(aid, weights=weights)
            scored.append((aid, f))
        scored.sort(key=lambda t: t[1].score, reverse=True)

        rows: List[RankRow] = []
        for i, (aid, f) in enumerate(scored, start=1):
            rows.append(RankRow(
                rank=i, agent_id=aid, fitness=f.score, components=f.components,
                niche=self.niches.get(aid),
                prev_rank=self._prev[horizon].get(aid),
            ))
        # remember for next call's rank_delta
        self._prev[horizon] = {r.agent_id: r.rank for r in rows}
        return rows

    def bottom_k(self, rows: Sequence[RankRow], k: Optional[int] = None,
                 fraction: float = 0.30) -> List[RankRow]:
        """Bottom-K (default bottom 30%) selected for Reflection."""
        n = len(rows)
        if n == 0:
            return []
        kk = k if k is not None else max(1, round(n * fraction))
        return list(rows[-kk:])

    def niche_coverage(self, rows: Sequence[RankRow]) -> Dict[str, Any]:
        """Which (declared) niches are filled, and is any single niche dominating?"""
        by_niche: Dict[str, List[str]] = {}
        for r in rows:
            by_niche.setdefault(r.niche or "unassigned", []).append(r.agent_id)
        top_niche = rows[0].niche if rows else None
        return {
            "filled_niches": sorted(by_niche.keys()),
            "members_per_niche": {n: len(a) for n, a in by_niche.items()},
            "leader_niche": top_niche,
            "warning": ("multiple agents collapsing into one niche -- protect "
                        "diversity" if any(len(a) > 1 for a in by_niche.values())
                        else None),
        }

    def report(self, tracker: PerformanceTracker, horizon: str = "monthly"
               ) -> Dict[str, Any]:
        rows = self.rank(tracker, horizon)
        return {
            "type": "trading_society_ranking",
            "role": "writer",
            "horizon": horizon,
            "ranking": [r.to_dict() for r in rows],
            "bottom_k_for_reflection": [r.agent_id for r in self.bottom_k(rows)],
            "niche_coverage": self.niche_coverage(rows),
            "disclaimer": "Research ranking. No capital action implied.",
        }


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------
def _demo() -> int:
    import json
    print("=" * 72)
    print("ranking_system self-test (synthetic, multi-horizon)")
    print("=" * 72)

    tracker = PerformanceTracker(action_budget=10)
    streams = {
        "MOMENTUM_SWING":      ([0.012, -0.004, 0.018, 0.006, -0.011, 0.022, 0.015],
                                ["risk_on", "risk_on", "risk_off", "risk_on",
                                 "risk_off", "risk_on", "risk_on"]),
        "MEAN_REVERSION_SWING": ([0.004, 0.005, -0.020, 0.012, 0.003, -0.006, 0.007],
                                 ["risk_on", "risk_on", "risk_off", "risk_on",
                                  "risk_off", "risk_on", "risk_on"]),
        "MACRO_REGIME":        ([0.002, 0.003, 0.001, 0.004, 0.002, 0.003, 0.002],
                                ["risk_on", "risk_on", "risk_off", "risk_on",
                                 "risk_off", "risk_on", "risk_on"]),
    }
    for aid, (rets, regs) in streams.items():
        for r, g in zip(rets, regs):
            tracker.record_period(aid, r, regime=g, actions=1)
            tracker.record_trade(aid, r)

    niches = {"MOMENTUM_SWING": "daily_momentum",
              "MEAN_REVERSION_SWING": "counter_trend",
              "MACRO_REGIME": "strategic_allocation"}
    rk = RankingSystem(niches=niches)
    for h in HORIZONS:
        print(f"\n----- {h} -----")
        print(json.dumps(rk.report(tracker, h), indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(_demo())
