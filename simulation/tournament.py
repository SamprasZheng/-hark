#!/usr/bin/env python3
"""
Trading Society -- Tournament / Competition (競賽)

PPST Declaration (this PROGRAM):
- PROJECT: Trading Society
- PROGRAM: simulation/tournament.py
- SKILL:   cross-regime competition + leaderboard (anti curve-fit selection)
- TARGET:  Run a population of parameterized agents across MULTIPLE regime
           windows (bull / bear / chop), score each per window via the
           protocol-compliant backtest_runner, and produce a leaderboard ranked
           by a blend of average AND worst-regime fitness -- so a single-regime
           winner cannot top a robust all-weather agent. No LLM, no capital output.

This is the substrate the Evolution Engine competes on each generation. Multi-
regime evaluation is mandatory (CLAUDE.md sec.10 / EVOLUTION_PROGRAM.md): worst-
regime fitness is half the score, which is the metric-level defense against
over-fitting to the recent tape.

Run: python simulation/tournament.py   (synthetic 3-regime competition demo)
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

try:
    from simulation.backtest_runner import (
        PricePoint, BacktestConfig, run_backtest)
    from simulation.strategy_agent import make_agent_spec
    from simulation.evolution.mutator import AgentConfig
except Exception:  # pragma: no cover
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from simulation.backtest_runner import (
        PricePoint, BacktestConfig, run_backtest)
    from simulation.strategy_agent import make_agent_spec
    from simulation.evolution.mutator import AgentConfig

# Weight on worst-regime fitness vs average fitness (anti curve-fit).
WORST_REGIME_WEIGHT = 0.5


@dataclass
class RegimeWindow:
    label: str            # e.g. "bull", "bear", "chop"
    series: Dict[str, List[PricePoint]]
    start: str
    end: str


def _series_from_closes(closes: Dict[str, List[float]], start_day: int = 6
                        ) -> Dict[str, List[PricePoint]]:
    from datetime import date
    out: Dict[str, List[PricePoint]] = {}
    for tkr, cs in closes.items():
        pts = []
        for i, c in enumerate(cs):
            d = date(2025, 1, start_day + i).isoformat()
            pts.append(PricePoint(as_of=d, close=round(float(c), 4)))
        out[tkr] = pts
    return out


def make_synthetic_regimes(seed: int = 7, n_bars: int = 22) -> List[RegimeWindow]:
    """Deterministic bull / bear / chop windows (two tickers each)."""
    rng = random.Random(seed)

    def walk(drift: float, vol: float, osc: float = 0.0) -> List[float]:
        price = 100.0
        out = [price]
        for i in range(1, n_bars):
            shock = rng.uniform(-vol, vol)
            mean_rev = -osc * (price / 100.0 - 1.0)  # pull back toward 100
            price *= (1.0 + drift + shock + mean_rev)
            out.append(price)
        return out

    bull = _series_from_closes({"AAA": walk(0.010, 0.008), "BBB": walk(0.008, 0.010)})
    bear = _series_from_closes({"AAA": walk(-0.010, 0.010), "BBB": walk(-0.008, 0.012)})
    chop = _series_from_closes({"AAA": walk(0.000, 0.012, osc=0.05),
                                "BBB": walk(0.000, 0.014, osc=0.06)})
    end = bull["AAA"][-1].as_of
    return [
        RegimeWindow("bull", bull, bull["AAA"][0].as_of, end),
        RegimeWindow("bear", bear, bear["AAA"][0].as_of, bear["AAA"][-1].as_of),
        RegimeWindow("chop", chop, chop["AAA"][0].as_of, chop["AAA"][-1].as_of),
    ]


@dataclass
class CompetitorResult:
    agent_id: str
    cross_regime_score: float
    avg_fitness: float
    worst_fitness: float
    worst_regime: str
    per_window: Dict[str, float] = field(default_factory=dict)
    niche: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {"agent_id": self.agent_id,
                "cross_regime_score": round(self.cross_regime_score, 4),
                "avg_fitness": round(self.avg_fitness, 4),
                "worst_fitness": round(self.worst_fitness, 4),
                "worst_regime": self.worst_regime,
                "per_window": {k: round(v, 4) for k, v in self.per_window.items()},
                "niche": self.niche}


def compete(population: List[AgentConfig], windows: List[RegimeWindow],
            action_budget: int = 10) -> List[CompetitorResult]:
    """Run every agent across every regime window; rank by cross-regime score."""
    results: List[CompetitorResult] = []
    for cfg in population:
        per_window: Dict[str, float] = {}
        for w in windows:
            spec = make_agent_spec(cfg)
            bcfg = BacktestConfig(start=w.start, end=w.end, llm_involvement="none",
                                  action_budget=action_budget,
                                  regime_labeler=lambda d, _l=w.label: _l)
            res = run_backtest([spec], w.series, bcfg)
            fit = res.scoreboard[0]["fitness"] if res.scoreboard else 0.0
            per_window[w.label] = fit
        avg = sum(per_window.values()) / max(1, len(per_window))
        worst_label = min(per_window, key=per_window.get) if per_window else "n/a"
        worst = per_window.get(worst_label, 0.0)
        score = (1 - WORST_REGIME_WEIGHT) * avg + WORST_REGIME_WEIGHT * worst
        results.append(CompetitorResult(
            agent_id=cfg.agent_id, cross_regime_score=score, avg_fitness=avg,
            worst_fitness=worst, worst_regime=worst_label, per_window=per_window,
            niche=cfg.niche))
    results.sort(key=lambda r: r.cross_regime_score, reverse=True)
    return results


def leaderboard_dict(results: List[CompetitorResult]) -> Dict[str, Any]:
    return {
        "type": "trading_society_tournament",
        "role": "writer",
        "worst_regime_weight": WORST_REGIME_WEIGHT,
        "leaderboard": [r.to_dict() for r in results],
        "disclaimer": ("Cross-regime competition. Research only; worst-regime "
                       "fitness is half the score to penalize curve-fitting. "
                       "No capital action implied."),
    }


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------
def _seed_population() -> List[AgentConfig]:
    return [
        AgentConfig("MOM_fast", "daily_momentum",
                    params={"momentum_tilt": 1.0, "lookback": 2, "entry_threshold": 0.006}),
        AgentConfig("MOM_slow", "daily_momentum",
                    params={"momentum_tilt": 1.0, "lookback": 5, "entry_threshold": 0.010}),
        AgentConfig("REV_fast", "counter_trend",
                    params={"momentum_tilt": -1.0, "lookback": 1, "entry_threshold": 0.006}),
        AgentConfig("REV_slow", "counter_trend",
                    params={"momentum_tilt": -1.0, "lookback": 3, "entry_threshold": 0.012}),
    ]


def _demo() -> int:
    import json
    print("=" * 72)
    print("tournament self-test -- 3-regime competition (bull/bear/chop, llm=none)")
    print("=" * 72)
    windows = make_synthetic_regimes()
    results = compete(_seed_population(), windows)
    print(json.dumps(leaderboard_dict(results), indent=2, ensure_ascii=False))
    print(f"\nWinner: {results[0].agent_id} (robust across regimes); "
          f"worst-regime for winner = {results[0].worst_regime} "
          f"@ {results[0].worst_fitness:.3f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(_demo())
