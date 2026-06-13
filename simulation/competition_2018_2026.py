#!/usr/bin/env python3
"""
Trading Society -- 2018-2026 evolving competition + 2026 H2 forecast

PPST Declaration (this PROGRAM):
- PROJECT: Trading Society
- PROGRAM: simulation/competition_2018_2026.py
- SKILL:   long-horizon low-frequency competition + per-quarter evolution +
           forward pick generation
- TARGET:  Run a roster of LONG-HORIZON, LOW-FREQUENCY traders (monthly rebalance,
           <=3 names held -> well under "<=3 trades/week") over 2018-2026 real
           monthly lake prices; each quarter the worst traders EVOLVE (genome
           mutation); compare cumulative performance; then apply the evolutionary
           champion's final genome to today's universe to produce a 2026-H2
           pick list. Recommend-only. llm_involvement="none" (KPI-eligible).

Honest design:
- "<=3 trades/week, longer-term" -> a MONTHLY-rebalanced, top-3 book. Monthly
  rebalance with <=3 positions is far below 3 trades/week; this is the long-horizon
  interpretation the principal asked for.
- 2018-2026 needs monthly data (daily lake only reaches 2021); the competition
  therefore runs at monthly granularity.
- Returns are RELATIVE rankings, not realistic P&L (no slippage/sizing beyond a
  10bps cost). The 2026-H2 forecast is recommend-only research, gated by the
  regime guardrail + Risk-Officer (CLAUDE.md sec.10); it does NOT replace the
  canonical 10-signal pipeline.

Run: python simulation/competition_2018_2026.py
"""

from __future__ import annotations

import json
import random
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from simulation.historical_competition import (  # noqa: E402
    load_close_matrix, backtest_trader, _bucket_key, DEFENSIVE_BASKET,
    _lookback_return)

COST_BPS = 10.0
TRADES_PER_REBALANCE = 3   # <=3 names -> long-horizon, well under 3 trades/week
EVOLVE_BOTTOM_K = 2        # how many worst traders mutate each quarter

# Long-horizon, low-frequency roster (lookback in MONTHS; max_actions = top-K hold).
def _roster() -> List[Dict[str, Any]]:
    return [
        {"id": "LT_MOMENTUM",   "type": "momentum",  "lookback": 3, "threshold": 0.10, "max_actions": TRADES_PER_REBALANCE},
        {"id": "LT_TREND",      "type": "momentum",  "lookback": 6, "threshold": 0.15, "max_actions": TRADES_PER_REBALANCE},
        {"id": "LT_BREAKOUT",   "type": "momentum",  "lookback": 2, "threshold": 0.12, "max_actions": TRADES_PER_REBALANCE},
        {"id": "LT_REVERSION",  "type": "reversion", "lookback": 2, "threshold": 0.10, "max_actions": TRADES_PER_REBALANCE},
        {"id": "LT_DEEPVALUE",  "type": "reversion", "lookback": 4, "threshold": 0.20, "max_actions": TRADES_PER_REBALANCE},
        {"id": "LT_BALANCED",   "type": "momentum",  "lookback": 4, "threshold": 0.08, "max_actions": TRADES_PER_REBALANCE},
        {"id": "RISK_OFFICER",  "type": "defensive", "lookback": 3, "threshold": 0.0,  "max_actions": TRADES_PER_REBALANCE},
    ]


# Bounds for the evolving genome params. Min lookback 2 keeps the roster
# long-horizon (evolution may not collapse it back to high-frequency).
_BOUNDS = {"lookback": (2, 12), "threshold": (0.04, 0.40)}


def _mutate(trader: Dict[str, Any], rng: random.Random) -> Tuple[Dict[str, Any], str]:
    """Reflection-lite: perturb the weakest lever (a losing trader tries a new
    lookback / threshold). Returns (mutated copy, change description)."""
    t = dict(trader)
    if t["type"] == "defensive":
        return t, "no-op (defensive trader is fixed)"
    lever = rng.choice(["lookback", "threshold"])
    lo, hi = _BOUNDS[lever]
    if lever == "lookback":
        old = int(t["lookback"])
        new = int(min(hi, max(lo, old + rng.choice([-2, -1, 1, 2]))))
    else:
        old = float(t["threshold"])
        new = round(min(hi, max(lo, old + rng.choice([-0.04, -0.02, 0.02, 0.04]))), 3)
    t[lever] = new
    t["version"] = t.get("version", 1) + 1
    return t, f"{lever} {old}->{new}"


def _quarter_groups(dates: List[str]) -> List[Tuple[str, List[int]]]:
    groups: Dict[str, List[int]] = {}
    for i, d in enumerate(dates):
        groups.setdefault(_bucket_key(d, "quarter"), []).append(i)
    return [(q, groups[q]) for q in sorted(groups)]


def run(seed: int = 11) -> Dict[str, Any]:
    rng = random.Random(seed)
    dates, tickers, closes = load_close_matrix("1mo", "2018-01-01")
    defmask = np.array([t in set(DEFENSIVE_BASKET) for t in tickers])
    quarters = _quarter_groups(dates)

    population = _roster()
    cumulative: Dict[str, float] = {t["id"]: 1.0 for t in population}
    quarter_champ_tally: Dict[str, int] = {t["id"]: 0 for t in population}
    timeline: List[Dict[str, Any]] = []
    evolution_log: List[Dict[str, Any]] = []
    trailing: Dict[str, List[float]] = {t["id"]: [] for t in population}

    for qi, (q, idxs) in enumerate(quarters):
        if len(idxs) < 1:
            continue
        lo, hi = idxs[0], idxs[-1]
        q_returns: Dict[str, float] = {}
        for tr in population:
            port = backtest_trader(closes, tr, defmask, cost_bps=COST_BPS,
                                   long_only=True)
            seg = [port[i] for i in idxs if not np.isnan(port[i])]
            qret = float(np.prod([1 + x for x in seg]) - 1) if seg else 0.0
            q_returns[tr["id"]] = qret
            cumulative[tr["id"]] *= (1 + qret)
            trailing[tr["id"]].append(qret)
        champ = max(q_returns, key=q_returns.get)
        quarter_champ_tally[champ] += 1
        timeline.append({"quarter": q, "champion": champ,
                         "champion_qret": round(q_returns[champ], 4),
                         "returns": {k: round(v, 4) for k, v in q_returns.items()}})

        # --- per-quarter evolution: traders that are PERSISTENTLY weak (worst
        # trailing-4-quarter sum) mutate; a single down quarter is not enough. ---
        ranked = sorted(q_returns, key=lambda tid: sum(trailing[tid][-4:]))
        mutated = []
        for tid in ranked[:EVOLVE_BOTTOM_K]:
            idx = next(i for i, t in enumerate(population) if t["id"] == tid)
            if population[idx]["type"] == "defensive":
                continue
            new_genome, change = _mutate(population[idx], rng)
            population[idx] = new_genome
            mutated.append({"trader": tid, "change": change,
                            "new_genome": {k: new_genome[k] for k in ("lookback", "threshold")}})
        if mutated:
            evolution_log.append({"after_quarter": q, "mutations": mutated})

    leaderboard = sorted(
        ({"trader": tid, "cumulative_return": round(cumulative[tid] - 1, 4),
          "quarters_won": quarter_champ_tally[tid],
          "final_genome": next({k: t[k] for k in ("type", "lookback", "threshold")}
                               for t in population if t["id"] == tid)}
         for tid in cumulative),
        key=lambda r: r["cumulative_return"], reverse=True)

    champion = leaderboard[0]
    forecast = _forecast_h2_2026(closes, tickers, dates, population, champion["trader"])

    return {
        "type": "trading_society_2018_2026_competition",
        "as_of_timestamp": datetime.now(timezone.utc).isoformat(),
        "role": "writer", "project": "Trading Society",
        "program": "simulation/competition_2018_2026.py",
        "protocol_ref": "docs/LLM-BACKTEST-PROTOCOL.md", "llm_involvement": "none",
        "rules": {"frequency": "monthly rebalance, <=3 names held (long-horizon, "
                                "well under 3 trades/week)",
                  "cost_bps": COST_BPS, "evolution": "bottom-2 traders mutate each "
                  "quarter (genome lookback/threshold)"},
        "window": {"start": dates[0], "end": dates[-1], "n_quarters": len(quarters),
                   "n_names": len(tickers)},
        "leaderboard_cumulative_2018_2026": leaderboard,
        "quarter_champion_tally": dict(sorted(quarter_champ_tally.items(),
                                              key=lambda x: -x[1])),
        "quarter_timeline": timeline,
        "evolution_log": evolution_log,
        "forecast_2026_h2": forecast,
        "disclaimer": (
            "Cumulative returns are RELATIVE rankings, not realistic P&L (10bps cost, "
            "no slippage/sizing). 2026-H2 forecast is recommend-only research, gated "
            "by the regime guardrail + Risk-Officer (CLAUDE.md sec.10); it does NOT "
            "replace the canonical 10-signal pipeline. Monthly granularity (daily lake "
            "only reaches 2021)."),
    }


def _forecast_h2_2026(closes, tickers, dates, population, champion_id: str
                      ) -> Dict[str, Any]:
    """Apply the evolutionary champion's FINAL genome to the latest monthly bar to
    produce a 2026-H2 pick list, with the live regime/hedge context."""
    tr = next(t for t in population if t["id"] == champion_id)
    tick = np.array(tickers)
    t = closes.shape[0] - 1
    L = int(tr["lookback"])
    picks: List[Dict[str, Any]] = []
    if tr["type"] != "defensive" and t - L >= 0:
        lb = _lookback_return(closes, t, L)
        valid = ~np.isnan(lb)
        thr = float(tr["threshold"])
        if tr["type"] == "momentum":
            cand = np.where(valid & (lb > thr), lb, -np.inf)
        else:
            cand = np.where(valid & (lb < -thr), -lb, -np.inf)
        order = np.argsort(cand)[::-1]
        for i in order:
            if not np.isfinite(cand[i]):
                break
            picks.append({"ticker": str(tick[i]),
                          "signal": round(float(lb[i]), 3)})
            if len(picks) >= 8:
                break
    else:  # defensive champion -> defensive basket
        picks = [{"ticker": t2, "signal": None} for t2 in DEFENSIVE_BASKET
                 if t2 in tickers][:8]

    regime = None
    try:
        from simulation.regime_filter import from_live
        regime = from_live().to_dict()
    except Exception:
        regime = None

    return {
        "champion": champion_id,
        "champion_genome": {k: tr[k] for k in ("type", "lookback", "threshold")},
        "as_of_month": dates[-1],
        "picks": picks,
        "regime_context": ({"regime": regime["regime"],
                            "defensive_floor": regime["defensive_floor"],
                            "momentum_decoupling_lock": regime["momentum_decoupling_lock"]}
                           if regime else None),
        "note": "Champion genome applied to the latest monthly bar. Recommend-only; "
                "apply the regime guardrail + a hedge floor before any capital use. "
                "In a high-valuation tape the defensive floor still binds (CLAUDE sec.10).",
    }


def main() -> int:
    result = run()
    out = _ROOT / "outputs" / f"trading-society-2018-2026-{result['as_of_timestamp'][:10]}.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    _print(result)
    print(f"\nArtifact: {out.relative_to(_ROOT)}")
    return 0


def _print(r: Dict[str, Any]) -> None:
    print("=" * 74)
    print("TRADING SOCIETY -- 2018-2026 evolving competition (long-horizon, <=3/wk)")
    print("=" * 74)
    w = r["window"]
    print(f"Window: {w['start']}..{w['end']} ({w['n_quarters']} quarters, "
          f"{w['n_names']} names) | {r['rules']['frequency']}")
    print("\nCUMULATIVE LEADERBOARD 2018-2026 (relative ranking, not real P&L):")
    print(f"  {'#':<2} {'trader':<16} {'cum_return':>11} {'qtrs_won':>9} {'final_genome'}")
    for i, row in enumerate(r["leaderboard_cumulative_2018_2026"], 1):
        g = row["final_genome"]
        print(f"  {i:<2} {row['trader']:<16} {row['cumulative_return']:>+11.3f} "
              f"{row['quarters_won']:>9} {g['type']}/lb{g['lookback']}/th{g['threshold']}")
    print("\nQuarter champion tally:")
    for tid, n in r["quarter_champion_tally"].items():
        if n:
            print(f"  {tid:<16} {n}")
    print(f"\nEvolution events: {len(r['evolution_log'])} quarters had mutations")
    f = r["forecast_2026_h2"]
    print(f"\n=== 2026 H2 FORECAST (champion = {f['champion']}, "
          f"{f['champion_genome']['type']}/lb{f['champion_genome']['lookback']}) ===")
    rc = f.get("regime_context")
    if rc:
        print(f"  Regime: {rc['regime']} | defensive floor {rc['defensive_floor']} | "
              f"decoupling lock {rc['momentum_decoupling_lock']}")
    print(f"  Picks (recommend-only, as_of {f['as_of_month']}):")
    for p in f["picks"]:
        sig = f" (signal {p['signal']:+.2f})" if p["signal"] is not None else ""
        print(f"     {p['ticker']}{sig}")
    print("\n" + r["disclaimer"])


if __name__ == "__main__":
    raise SystemExit(main())
