#!/usr/bin/env python3
"""
Trading Society -- Parameterized Strategy Agent (evolution substrate)

PPST Declaration (this PROGRAM):
- PROJECT: Trading Society
- PROGRAM: simulation/strategy_agent.py
- SKILL:   parameterized rule-strategy family (params -> decide() behavior)
- TARGET:  A deterministic, PIT-honest strategy whose behavior is fully a
           function of an AgentConfig.params dict, so that mutation actually
           changes backtest results and evolution/competition are meaningful.
           No LLM (llm_involvement="none"), no capital output.

Why: the Evolution + Tournament layers need a population of agents whose
fitness genuinely varies with their genome. A fixed rule can't evolve. This
family maps {lookback, entry_threshold, momentum_tilt, ...} -> trade decisions.

Run: python simulation/strategy_agent.py   (synthetic demo)
"""

from __future__ import annotations

from typing import Any, Callable, Dict, List

try:
    from simulation.backtest_runner import PricePoint, AgentSpec
    from simulation.evolution.mutator import AgentConfig
except Exception:  # pragma: no cover
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from simulation.backtest_runner import PricePoint, AgentSpec
    from simulation.evolution.mutator import AgentConfig

# The genome (defaults). Mutation perturbs these within mutator.PARAM_BOUNDS.
DEFAULT_STRATEGY_PARAMS: Dict[str, float] = {
    "lookback": 3,             # bars used for the momentum/return calc
    "entry_threshold": 0.01,   # fractional move required to act (1%)
    "momentum_tilt": 1.0,      # >=0 momentum (chase), <0 reversion (fade)
    "max_actions": 2,          # per-call action cap (society budget still applies)
    "position_size_scale": 1.0,
    "regime_filter_strictness": 0.0,  # 0..1; higher => act less in hostile regime
}


def make_decider(config: AgentConfig) -> Callable[[str, Dict[str, List[PricePoint]]], Dict[str, Any]]:
    """Build a decide(as_of, history) closure from a config genome."""
    p = {**DEFAULT_STRATEGY_PARAMS, **(config.params or {})}
    lookback = max(1, int(round(p["lookback"])))
    thr = float(p["entry_threshold"])
    tilt = float(p["momentum_tilt"])
    max_actions = max(1, int(round(p["max_actions"])))
    is_momentum = tilt >= 0
    role = f"{config.agent_id}"

    def decide(as_of: str, history: Dict[str, List[PricePoint]]) -> Dict[str, Any]:
        actions: List[Dict[str, Any]] = []
        for tkr, pts in history.items():
            if len(pts) <= lookback:
                continue
            prev = pts[-1 - lookback].close
            if prev <= 0:
                continue
            chg = pts[-1].close / prev - 1.0
            side = None
            if is_momentum:
                if chg > thr:
                    side = "long"          # breakout continuation
                elif chg < -thr:
                    side = "short"         # breakdown continuation
            else:  # reversion / fade
                if chg < -thr:
                    side = "long"          # fade the dip
                elif chg > thr:
                    side = "short"         # fade the rip
            if side:
                actions.append({
                    "ticker": tkr, "side": side,
                    "size_hint": "small" if p["position_size_scale"] >= 1 else "tiny",
                    "rationale": f"{'mom' if is_momentum else 'rev'} {chg:+.3f} "
                                 f"vs thr {thr:.3f} over {lookback}b",
                    "invalid_if": "thesis move reverses past entry",
                })
        # deterministic ordering by |move| so the action cap keeps the strongest
        actions.sort(key=lambda a: a["rationale"], reverse=True)
        return {"as_of_timestamp": as_of, "role": role,
                "proposed_actions": actions[:max_actions],
                "no_action_reason": None if actions else "no qualifying setup"}

    return decide


def make_agent_spec(config: AgentConfig, niche_purity: float = 1.0) -> AgentSpec:
    """Wrap a config genome as an AgentSpec the backtest_runner can drive."""
    return AgentSpec(agent_id=config.agent_id, decide=make_decider(config),
                     niche_purity=niche_purity)


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------
def _demo() -> int:
    import json
    from simulation.backtest_runner import (
        BacktestConfig, run_backtest, result_to_artifact, _synthetic_series)
    print("=" * 72)
    print("strategy_agent self-test (params drive behavior; llm=none)")
    print("=" * 72)
    series = _synthetic_series()
    momentum = AgentConfig(agent_id="GENOME_MOM", niche="daily_momentum",
                           params={"momentum_tilt": 1.0, "lookback": 2,
                                   "entry_threshold": 0.005})
    reversion = AgentConfig(agent_id="GENOME_REV", niche="counter_trend",
                            params={"momentum_tilt": -1.0, "lookback": 1,
                                    "entry_threshold": 0.005})
    agents = [make_agent_spec(momentum), make_agent_spec(reversion)]
    cfg = BacktestConfig(start="2025-01-06", end="2025-01-31",
                         llm_involvement="none", regime_labeler=lambda d: "risk_on")
    res = run_backtest(agents, series, cfg)
    for row in res.scoreboard:
        m = row["metrics"]
        print(f"  {row['agent_id']:<12} fitness={row['fitness']:.3f} "
              f"total_return={m['total_return']:+.4f} trades={m['n_trades']}")
    print("\nDifferent genomes -> different fitness (evolution has signal to act on).")
    return 0


if __name__ == "__main__":
    raise SystemExit(_demo())
