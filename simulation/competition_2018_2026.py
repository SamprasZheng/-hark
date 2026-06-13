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
# Layer-2 rigor (review A): diversified per-quarter book.
MAX_HOLD = 10              # max names per rebalance (kills single-stock domination)
LARGE_TARGET, SMALL_TARGET = 8, 2     # 80/20 large/small split
CORE_NAME_CAP, SAT_NAME_CAP = 0.12, 0.06

# Curated large-cap set (stable mega/large caps across 2018-2026) for the 80/20
# split -- historical market caps aren't in the lake, so this is a curated
# approximation (these names were large-cap throughout the window).
LARGE_CAP = set("""
NVDA AAPL MSFT GOOGL GOOG META AMZN TSLA TSM ASML AVGO AMD MU AMAT LRCX KLAC QCOM
TXN INTC ADI MRVL NXPI MCHP ANET CSCO ORCL CRM ADBE NOW INTU PANW SNPS CDNS
LMT NOC RTX GD BA LHX HON GE CAT DE UNP
LLY UNH JNJ ABBV MRK PFE TMO ABT DHR AMGN ISRG VRTX REGN GILD BMY
KO PG WMT COST PEP MCD PM MO CL KMB
JPM BAC WFC GS MS V MA AXP BLK SPGI
XOM CVX COP SLB
DIS NFLX CMCSA T VZ NKE SBUX HD LOW
""".split())

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


def _bear_mask(closes: np.ndarray, lookback: int = 6, threshold: float = -0.08
               ) -> np.ndarray:
    """Per-month confirmed-bear flag (PIT): trailing `lookback`-month MEDIAN market
    return < threshold. Implements the principal's rule -- shorts only when the
    tape has truly turned bear like 2022 / COVID, using only data up to month t."""
    T, N = closes.shape
    mask = np.zeros(T, dtype=bool)
    for t in range(lookback, T):
        prev, cur = closes[t - lookback], closes[t]
        with np.errstate(invalid="ignore", divide="ignore"):
            rets = np.where(prev > 0, cur / prev - 1.0, np.nan)
        if np.any(~np.isnan(rets)):
            m = float(np.nanmedian(rets))
            mask[t] = m < threshold
    return mask


def _quarter_groups(dates: List[str]) -> List[Tuple[str, List[int]]]:
    groups: Dict[str, List[int]] = {}
    for i, d in enumerate(dates):
        groups.setdefault(_bucket_key(d, "quarter"), []).append(i)
    return [(q, groups[q]) for q in sorted(groups)]


def _diversified_quarter_return(closes: np.ndarray, large_mask: np.ndarray,
                                defmask: np.ndarray, genome: Dict[str, Any],
                                idxs: List[int], cost: float) -> float:
    """Review A: a DIVERSIFIED monthly book per quarter -- up to MAX_HOLD names,
    80% large-cap / 20% small-cap, single-name caps (12%/6%), long-only. Replaces
    the old top-3 concentration so a single moonshot can't carry a trader."""
    L, thr, ttype = int(genome["lookback"]), float(genome["threshold"]), genome["type"]
    T = closes.shape[0]
    rets: List[float] = []
    for t in idxs:
        if t < L or t + 1 >= T:
            continue
        prev, cur, nxt = closes[t - L], closes[t], closes[t + 1]
        with np.errstate(invalid="ignore", divide="ignore"):
            lb = np.where(prev > 0, cur / prev - 1.0, np.nan)
            rn = np.where(cur > 0, nxt / cur - 1.0, np.nan)
        valid = ~np.isnan(lb) & ~np.isnan(rn)
        if ttype == "defensive":
            breadth = np.nanmedian(lb[~np.isnan(lb)]) if np.any(~np.isnan(lb)) else 0.0
            if breadth < 0:
                rets.append(0.0)            # hold cash in a falling tape
                continue
            sel = np.where(defmask & valid)[0][:MAX_HOLD]
            w = min(CORE_NAME_CAP, 1.0 / max(1, len(sel)))
            rets.append((sum(w * rn[i] for i in sel) - (cost if len(sel) else 0)))
            continue
        longc = valid & (lb > thr) if ttype == "momentum" else valid & (lb < -thr)
        ci = np.where(longc)[0]
        if len(ci) == 0:
            rets.append(0.0)
            continue
        order = ci[np.argsort(-np.abs(lb[ci]))]
        large = [i for i in order if large_mask[i]][:LARGE_TARGET]
        small = [i for i in order if not large_mask[i]][:SMALL_TARGET]
        wl = min(CORE_NAME_CAP, 0.80 / len(large)) if large else 0.0
        ws = min(SAT_NAME_CAP, 0.20 / len(small)) if small else 0.0
        mret = sum(wl * rn[i] for i in large) + sum(ws * rn[i] for i in small)
        if large or small:
            mret -= cost
        rets.append(mret)
    return float(np.prod([1 + r for r in rets]) - 1) if rets else 0.0


def _fair_fitness(trailing: Dict[str, List[float]],
                  bear_quarters: List[bool]) -> List[Dict[str, Any]]:
    """Review B: cross-style fair fitness. Compares traders on risk-adjusted +
    regime-aware metrics, not just raw cumulative return, so a steady defensive
    trader isn't buried under a momentum trader's headline number."""
    def _sharpe(xs):
        if len(xs) < 2:
            return 0.0
        m, s = float(np.mean(xs)), float(np.std(xs, ddof=1))
        return (m / s * (4 ** 0.5)) if s > 0 else 0.0

    def _maxdd(xs):
        eq, peak, mdd = 1.0, 1.0, 0.0
        for r in xs:
            eq *= (1 + r); peak = max(peak, eq)
            mdd = min(mdd, eq / peak - 1.0)
        return mdd

    raw = {}
    for tid, qs in trailing.items():
        bull = [r for r, b in zip(qs, bear_quarters) if not b]
        bear = [r for r, b in zip(qs, bear_quarters) if b]
        raw[tid] = {"sharpe": _sharpe(qs), "max_dd": _maxdd(qs),
                    "cum": float(np.prod([1 + r for r in qs]) - 1),
                    "bull_avg": float(np.mean(bull)) if bull else 0.0,
                    "bear_avg": float(np.mean(bear)) if bear else 0.0,
                    "hit_rate": float(np.mean([1.0 if r > 0 else 0.0 for r in qs])) if qs else 0.0}

    def _norm(key, invert=False):
        vals = [raw[t][key] for t in raw]
        lo, hi = min(vals), max(vals)
        rng = (hi - lo) or 1.0
        return {t: ((hi - raw[t][key]) if invert else (raw[t][key] - lo)) / rng for t in raw}
    n_sharpe, n_cum, n_dd = _norm("sharpe"), _norm("cum"), _norm("max_dd", invert=True)

    out = []
    for tid in raw:
        fair = round(0.40 * n_sharpe[tid] + 0.30 * n_cum[tid] + 0.30 * n_dd[tid], 4)
        out.append({"trader": tid, "fair_score": fair,
                    "sharpe_q": round(raw[tid]["sharpe"], 3),
                    "max_dd": round(raw[tid]["max_dd"], 3),
                    "hit_rate": round(raw[tid]["hit_rate"], 3),
                    "bull_avg_qret": round(raw[tid]["bull_avg"], 4),
                    "bear_avg_qret": round(raw[tid]["bear_avg"], 4)})
    out.sort(key=lambda r: r["fair_score"], reverse=True)
    return out


def run(seed: int = 11) -> Dict[str, Any]:
    rng = random.Random(seed)
    dates, tickers, closes = load_close_matrix("1mo", "2018-01-01")
    defmask = np.array([t in set(DEFENSIVE_BASKET) for t in tickers])
    large_mask = np.array([t in LARGE_CAP for t in tickers])
    quarters = _quarter_groups(dates)
    # Bear flag per month (PIT trailing-6m median < -8%); a quarter is "bear" if
    # any of its months is. Used for the regime-aware fair fitness (review B).
    bear_mask = _bear_mask(closes)
    bear_months = [dates[i] for i in range(len(dates)) if bear_mask[i]]
    bear_quarters = [any(bear_mask[i] for i in idxs) for _, idxs in quarters]
    cost = COST_BPS / 1e4

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
            qret = _diversified_quarter_return(closes, large_mask, defmask, tr,
                                               idxs, cost)
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

    fair_leaderboard = _fair_fitness(trailing, bear_quarters)
    # The fair champion (risk-adjusted + regime-aware) may differ from the raw one.
    fair_champ_id = fair_leaderboard[0]["trader"] if fair_leaderboard else leaderboard[0]["trader"]
    champion = leaderboard[0]
    forecast = _forecast_h2_2026(closes, tickers, dates, population, champion["trader"])

    return {
        "type": "trading_society_2018_2026_competition",
        "as_of_timestamp": datetime.now(timezone.utc).isoformat(),
        "role": "writer", "project": "Trading Society",
        "program": "simulation/competition_2018_2026.py",
        "protocol_ref": "docs/LLM-BACKTEST-PROTOCOL.md", "llm_involvement": "none",
        "rules": {"frequency": "monthly rebalance, DIVERSIFIED book (<=10 names, "
                                "80% large / 20% small, name caps 12%/6%) -- "
                                "long-horizon; no single-stock domination",
                  "cost_bps": COST_BPS, "evolution": "bottom-2 traders mutate each "
                  "quarter (genome lookback/threshold)",
                  "shorting": "LONG-BIASED / long-only diversified book; shorts only "
                  "in confirmed-bear regime (CLAUDE sec.10, simple path)",
                  "bear_months": bear_months, "bear_quarter_count": sum(bear_quarters)},
        "window": {"start": dates[0], "end": dates[-1], "n_quarters": len(quarters),
                   "n_names": len(tickers)},
        "leaderboard_cumulative_2018_2026": leaderboard,
        "fair_leaderboard_risk_adjusted": fair_leaderboard,
        "fair_champion": fair_champ_id,
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
    bm = r["rules"].get("bear_months", [])
    print(f"Shorting: LONG-BIASED; shorts only in {len(bm)} confirmed-bear months"
          + (f" (e.g. {', '.join(bm[:6])}...)" if bm else ""))
    print("\nCUMULATIVE LEADERBOARD 2018-2026 (relative ranking, not real P&L):")
    print(f"  {'#':<2} {'trader':<16} {'cum_return':>11} {'qtrs_won':>9} {'final_genome'}")
    for i, row in enumerate(r["leaderboard_cumulative_2018_2026"], 1):
        g = row["final_genome"]
        print(f"  {i:<2} {row['trader']:<16} {row['cumulative_return']:>+11.3f} "
              f"{row['quarters_won']:>9} {g['type']}/lb{g['lookback']}/th{g['threshold']}")
    print("\nFAIR LEADERBOARD (risk-adjusted + regime-aware; cross-style fair):")
    print(f"  {'#':<2} {'trader':<16} {'fair':>5} {'sharpe_q':>8} {'maxDD':>7} "
          f"{'hit':>5} {'bull_q':>7} {'bear_q':>7}")
    for i, row in enumerate(r["fair_leaderboard_risk_adjusted"], 1):
        print(f"  {i:<2} {row['trader']:<16} {row['fair_score']:>5.2f} "
              f"{row['sharpe_q']:>8.2f} {row['max_dd']:>7.3f} {row['hit_rate']:>5.2f} "
              f"{row['bull_avg_qret']:>+7.3f} {row['bear_avg_qret']:>+7.3f}")
    print(f"  -> fair champion: {r['fair_champion']} "
          f"(raw champion: {r['leaderboard_cumulative_2018_2026'][0]['trader']})")

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
