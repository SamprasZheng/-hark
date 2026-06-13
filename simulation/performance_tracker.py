#!/usr/bin/env python3
"""
Trading Society -- Performance Tracker (B deliverable, part 1 of 2)

PPST Declaration (this PROGRAM):
- PROJECT: Trading Society
- PROGRAM: simulation/performance_tracker.py
- SKILL:   performance_evaluator (multi-dimensional, regime-aware, PIT-honest)
- TARGET:  Deterministic, dependency-light metrics + multi-dimensional fitness
           vector for ranking society members. No LLM, no lookahead, no capital
           outputs. Pure functions over already-realized (PIT) returns/trades.

What this is / is not
---------------------
- IS:   a scorer. You hand it realized per-period returns and/or a list of
        closed trades (all timestamped <= the simulated as_of of the run) and it
        returns risk/return/stability metrics + a weighted fitness scalar.
- NOT:  a price fetcher, a signal generator, or anything that decides. It never
        calls an LLM and never reads future data -- the caller is responsible
        for point-in-time correctness of the inputs it passes in.

Governance (CLAUDE.md / docs/LLM-BACKTEST-PROTOCOL.md):
- llm_involvement of THIS module is always "none": it computes arithmetic over
  numbers the caller already realized. No banned keys are produced.
- Fitness intentionally rewards regime stability and penalizes over-trading
  (the ~10 action/day society cap) so winner-take-all and curve-fitting are
  discouraged at the metric level (CLAUDE.md niche protection).

Run: python simulation/performance_tracker.py   (prints a self-test demo)
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Sequence

TRADING_DAYS = 252


# ---------------------------------------------------------------------------
# Low-level statistics (plain python; no numpy/pandas dependency required)
# ---------------------------------------------------------------------------
def _mean(xs: Sequence[float]) -> float:
    return sum(xs) / len(xs) if xs else 0.0


def _stdev(xs: Sequence[float], ddof: int = 1) -> float:
    n = len(xs)
    if n <= ddof:
        return 0.0
    m = _mean(xs)
    var = sum((x - m) ** 2 for x in xs) / (n - ddof)
    return math.sqrt(var)


def equity_curve(returns: Sequence[float], start: float = 1.0) -> List[float]:
    """Compound a series of fractional period returns into an equity curve."""
    eq = [start]
    for r in returns:
        eq.append(eq[-1] * (1.0 + r))
    return eq


def max_drawdown(curve: Sequence[float]) -> float:
    """Worst peak-to-trough fractional decline (returned as a negative number)."""
    peak = -math.inf
    mdd = 0.0
    for v in curve:
        peak = max(peak, v)
        if peak > 0:
            dd = (v - peak) / peak
            mdd = min(mdd, dd)
    return mdd


def total_return(returns: Sequence[float]) -> float:
    out = 1.0
    for r in returns:
        out *= (1.0 + r)
    return out - 1.0


def cagr(returns: Sequence[float], periods_per_year: int = TRADING_DAYS) -> float:
    if not returns:
        return 0.0
    growth = total_return(returns) + 1.0
    years = len(returns) / periods_per_year
    if years <= 0 or growth <= 0:
        return 0.0
    return growth ** (1.0 / years) - 1.0


def sharpe(returns: Sequence[float], rf: float = 0.0,
           periods_per_year: int = TRADING_DAYS) -> float:
    if len(returns) < 2:
        return 0.0
    sd = _stdev(returns)
    if sd == 0:
        return 0.0
    excess = _mean(returns) - rf / periods_per_year
    return (excess / sd) * math.sqrt(periods_per_year)


def sortino(returns: Sequence[float], rf: float = 0.0,
            periods_per_year: int = TRADING_DAYS) -> float:
    if len(returns) < 2:
        return 0.0
    target = rf / periods_per_year
    downside = [min(0.0, r - target) for r in returns]
    dd = math.sqrt(sum(d * d for d in downside) / len(downside))
    if dd == 0:
        return 0.0
    excess = _mean(returns) - target
    return (excess / dd) * math.sqrt(periods_per_year)


def calmar(returns: Sequence[float], periods_per_year: int = TRADING_DAYS) -> float:
    mdd = max_drawdown(equity_curve(returns))
    if mdd == 0:
        return 0.0
    return cagr(returns, periods_per_year) / abs(mdd)


def win_rate(trade_pnls: Sequence[float]) -> float:
    if not trade_pnls:
        return 0.0
    wins = sum(1 for p in trade_pnls if p > 0)
    return wins / len(trade_pnls)


def payoff_ratio(trade_pnls: Sequence[float]) -> float:
    wins = [p for p in trade_pnls if p > 0]
    losses = [-p for p in trade_pnls if p < 0]
    if not wins or not losses:
        return 0.0
    return _mean(wins) / _mean(losses)


def compute_metrics(
    returns: Sequence[float],
    trade_pnls: Optional[Sequence[float]] = None,
    periods_per_year: int = TRADING_DAYS,
    rf: float = 0.0,
) -> Dict[str, float]:
    """Bundle the standard return/risk metrics for one agent over one window."""
    curve = equity_curve(returns)
    trade_pnls = list(trade_pnls or [])
    return {
        "total_return": total_return(returns),
        "cagr": cagr(returns, periods_per_year),
        "volatility_ann": _stdev(returns) * math.sqrt(periods_per_year),
        "max_drawdown": max_drawdown(curve),
        "sharpe": sharpe(returns, rf, periods_per_year),
        "sortino": sortino(returns, rf, periods_per_year),
        "calmar": calmar(returns, periods_per_year),
        "win_rate": win_rate(trade_pnls),
        "payoff_ratio": payoff_ratio(trade_pnls),
        "n_periods": len(returns),
        "n_trades": len(trade_pnls),
    }


# ---------------------------------------------------------------------------
# Multi-dimensional fitness (used by Ranking + Reflection + Evolution)
# ---------------------------------------------------------------------------
# Weights are intentionally external + tunable (Ranking Program owns tuning).
# The spirit (CORE_AGENT_ROLES.md "Initial Fitness Vector"): reward risk-adjusted
# return and cross-regime stability; penalize over-trading and niche bleed.
DEFAULT_FITNESS_WEIGHTS: Dict[str, float] = {
    "risk_adjusted": 0.30,   # Calmar/Sortino blend (primary)
    "regime_stability": 0.20,  # consistency across regimes (anti curve-fit)
    "drawdown_control": 0.20,  # 1 - normalized maxDD
    "hit_quality": 0.15,       # win_rate x payoff (tactical roles)
    "turnover_discipline": 0.10,  # penalize exceeding action budget
    "niche_purity": 0.05,      # stays inside declared (freq x edge) slot
}


def _clip(x: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, x))


def _normalize_risk_adjusted(metrics: Dict[str, float]) -> float:
    # Map a Calmar/Sortino blend onto [0,1]. ~3.0 is treated as "excellent".
    blend = 0.6 * metrics.get("calmar", 0.0) + 0.4 * metrics.get("sortino", 0.0)
    return _clip(blend / 3.0)


def _normalize_drawdown(metrics: Dict[str, float]) -> float:
    # maxDD is negative; -0.40 (a 40% drawdown) -> 0 score, 0 DD -> 1.
    mdd = abs(metrics.get("max_drawdown", 0.0))
    return _clip(1.0 - mdd / 0.40)


def _normalize_hit_quality(metrics: Dict[str, float]) -> float:
    wr = metrics.get("win_rate", 0.0)
    payoff = metrics.get("payoff_ratio", 0.0)
    # Expectancy-like proxy in [0,1]: wr scaled by payoff, capped.
    return _clip(wr * _clip(payoff / 2.0, 0.0, 1.5))


def _turnover_discipline(action_count: int, action_budget: int) -> float:
    if action_budget <= 0:
        return 1.0
    if action_count <= action_budget:
        return 1.0
    overshoot = (action_count - action_budget) / action_budget
    return _clip(1.0 - overshoot)


def regime_stability(regime_metrics: Dict[str, Dict[str, float]],
                     key: str = "sharpe") -> float:
    """
    Stability across regimes = 1 - normalized dispersion of `key` across regime
    buckets. A role that is great in risk-on but collapses in risk-off scores low.
    regime_metrics: {"risk_on": {...metrics...}, "risk_off": {...}, ...}
    """
    vals = [m.get(key, 0.0) for m in regime_metrics.values()]
    if len(vals) < 2:
        return 0.5  # not enough regime coverage to judge -> neutral prior
    mean = _mean(vals)
    spread = _stdev(vals)
    if mean <= 0:
        return 0.0
    cv = spread / abs(mean)  # coefficient of variation
    return _clip(1.0 - cv)


def bubble_risk_score(
    buffett_indicator: Optional[float] = None,
    dalio_bubble_flag: bool = False,
    vix: Optional[float] = None,
    breadth_pct: Optional[float] = None,     # % of names above their 200d (lower = narrower)
    dist_from_high_pct: Optional[float] = None,  # index distance from ATH (0 = at highs)
) -> float:
    """
    Transparent 0..1 bubble-risk composite (NOT a learned model). Higher = more
    bubble-like. Used to tilt ranking/reflection toward protection in stretched
    tapes (Step 3). Components that are None are skipped and the score is
    renormalized over the components actually supplied.
    """
    parts: List[float] = []
    if buffett_indicator is not None:
        # 130% -> 0, 230% -> 1
        parts.append(_clip((buffett_indicator - 130.0) / 100.0))
    if dalio_bubble_flag:
        parts.append(1.0)
    if vix is not None:
        # complacency adds bubble risk: VIX 12 -> high, VIX 30 -> low
        parts.append(_clip((22.0 - vix) / 12.0))
    if breadth_pct is not None:
        # narrow breadth (few names carrying) is bubble-like
        parts.append(_clip((55.0 - breadth_pct) / 35.0))
    if dist_from_high_pct is not None:
        # pinned at highs is more bubble-like than well off them
        parts.append(_clip(1.0 - abs(dist_from_high_pct) / 15.0))
    if not parts:
        return 0.0
    return round(sum(parts) / len(parts), 4)


@dataclass
class FitnessResult:
    score: float
    components: Dict[str, float]
    weights: Dict[str, float]

    def as_dict(self) -> Dict[str, Any]:
        return {"fitness": self.score, "components": self.components,
                "weights": self.weights}


def compute_fitness(
    metrics: Dict[str, float],
    regime_metrics: Optional[Dict[str, Dict[str, float]]] = None,
    action_count: int = 0,
    action_budget: int = 10,
    niche_purity: float = 1.0,
    weights: Optional[Dict[str, float]] = None,
) -> FitnessResult:
    """
    Combine normalized components into a single fitness scalar in [0,1].
    niche_purity is supplied by the caller (1.0 = stayed in declared edge,
    lower = bled into other roles' slots).
    """
    w = dict(weights or DEFAULT_FITNESS_WEIGHTS)
    comp = {
        "risk_adjusted": _normalize_risk_adjusted(metrics),
        "regime_stability": regime_stability(regime_metrics or {}),
        "drawdown_control": _normalize_drawdown(metrics),
        "hit_quality": _normalize_hit_quality(metrics),
        "turnover_discipline": _turnover_discipline(action_count, action_budget),
        "niche_purity": _clip(niche_purity),
    }
    total_w = sum(w.values()) or 1.0
    score = sum(comp[k] * w.get(k, 0.0) for k in comp) / total_w
    return FitnessResult(score=round(score, 4), components=comp, weights=w)


# ---------------------------------------------------------------------------
# PerformanceTracker -- records agent runs, computes per-agent metrics/fitness
# ---------------------------------------------------------------------------
@dataclass
class AgentRecord:
    agent_id: str
    returns: List[float] = field(default_factory=list)
    trade_pnls: List[float] = field(default_factory=list)
    action_count: int = 0
    # returns segmented by regime label, e.g. {"risk_on": [...], "risk_off": [...]}
    regime_returns: Dict[str, List[float]] = field(default_factory=dict)
    niche_purity: float = 1.0


class PerformanceTracker:
    """In-memory ledger of agent realized results for a single (PIT) window."""

    def __init__(self, action_budget: int = 10,
                 periods_per_year: int = TRADING_DAYS) -> None:
        self.action_budget = action_budget
        self.periods_per_year = periods_per_year
        self.records: Dict[str, AgentRecord] = {}

    def ensure(self, agent_id: str) -> AgentRecord:
        return self.records.setdefault(agent_id, AgentRecord(agent_id=agent_id))

    def record_period(self, agent_id: str, period_return: float,
                      regime: Optional[str] = None, actions: int = 0) -> None:
        rec = self.ensure(agent_id)
        rec.returns.append(period_return)
        rec.action_count += actions
        if regime:
            rec.regime_returns.setdefault(regime, []).append(period_return)

    def record_trade(self, agent_id: str, pnl: float) -> None:
        self.ensure(agent_id).trade_pnls.append(pnl)

    def set_niche_purity(self, agent_id: str, purity: float) -> None:
        self.ensure(agent_id).niche_purity = purity

    def metrics_for(self, agent_id: str) -> Dict[str, float]:
        rec = self.ensure(agent_id)
        return compute_metrics(rec.returns, rec.trade_pnls, self.periods_per_year)

    def fitness_for(self, agent_id: str,
                    weights: Optional[Dict[str, float]] = None) -> FitnessResult:
        rec = self.ensure(agent_id)
        base = compute_metrics(rec.returns, rec.trade_pnls, self.periods_per_year)
        regime_m = {
            label: compute_metrics(rets, periods_per_year=self.periods_per_year)
            for label, rets in rec.regime_returns.items()
        }
        # The action budget is per-period (per simulated day); compare the agent's
        # cumulative action_count against the cumulative cap over the window, not
        # against a single day's cap.
        n_periods = max(1, len(rec.returns))
        cumulative_budget = self.action_budget * n_periods
        return compute_fitness(
            base, regime_m, action_count=rec.action_count,
            action_budget=cumulative_budget, niche_purity=rec.niche_purity,
            weights=weights,
        )

    def scoreboard(self, weights: Optional[Dict[str, float]] = None
                   ) -> List[Dict[str, Any]]:
        """Per-agent metrics + fitness, sorted by fitness descending."""
        rows = []
        for aid in self.records:
            m = self.metrics_for(aid)
            f = self.fitness_for(aid, weights)
            rows.append({
                "agent_id": aid,
                "fitness": f.score,
                "metrics": m,
                "fitness_components": f.components,
                "action_count": self.records[aid].action_count,
            })
        rows.sort(key=lambda r: r["fitness"], reverse=True)
        return rows


# ---------------------------------------------------------------------------
# Self-test demo (synthetic numbers; no market data, no LLM, no lookahead)
# ---------------------------------------------------------------------------
def _demo() -> int:
    print("=" * 72)
    print("PerformanceTracker self-test (synthetic returns, llm_involvement=none)")
    print("=" * 72)

    tracker = PerformanceTracker(action_budget=10)

    # Two synthetic agents with deterministic toy return streams.
    momentum = [0.012, -0.004, 0.018, 0.006, -0.011, 0.022, 0.003, -0.002, 0.015, 0.009]
    reverter = [0.004, 0.005, -0.020, 0.012, 0.003, -0.006, 0.011, 0.002, -0.003, 0.007]
    regimes = ["risk_on", "risk_on", "risk_off", "risk_off", "risk_on",
               "risk_on", "risk_off", "risk_off", "risk_on", "risk_on"]

    for r, g in zip(momentum, regimes):
        tracker.record_period("MOMENTUM_SWING", r, regime=g, actions=1)
    for r, g in zip(reverter, regimes):
        tracker.record_period("MEAN_REVERSION_SWING", r, regime=g, actions=1)

    for p in [0.012, 0.018, -0.011, 0.022, 0.015]:
        tracker.record_trade("MOMENTUM_SWING", p)
    for p in [-0.020, 0.012, 0.011, -0.006, 0.007]:
        tracker.record_trade("MEAN_REVERSION_SWING", p)

    tracker.set_niche_purity("MOMENTUM_SWING", 1.0)
    tracker.set_niche_purity("MEAN_REVERSION_SWING", 0.9)

    for row in tracker.scoreboard():
        m = row["metrics"]
        print(f"\n  {row['agent_id']}  fitness={row['fitness']}")
        print(f"    total_return={m['total_return']:.4f} "
              f"sharpe={m['sharpe']:.2f} sortino={m['sortino']:.2f} "
              f"calmar={m['calmar']:.2f} maxDD={m['max_drawdown']:.4f}")
        print(f"    win_rate={m['win_rate']:.2f} payoff={m['payoff_ratio']:.2f} "
              f"actions={row['action_count']}")
        print(f"    fitness_components={ {k: round(v,3) for k,v in row['fitness_components'].items()} }")

    print("\nNote: synthetic data only. Real runs require PIT prices from the "
          "data lake and the protocol-compliant backtest_runner.")
    return 0


if __name__ == "__main__":
    raise SystemExit(_demo())
