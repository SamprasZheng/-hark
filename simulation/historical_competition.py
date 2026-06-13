#!/usr/bin/env python3
"""
Trading Society -- Historical competition + accuracy (Stage 1)

PPST Declaration (this PROGRAM):
- PROJECT: Trading Society
- PROGRAM: simulation/historical_competition.py
- SKILL:   multi-trader historical competition; weekly/monthly/quarterly champions;
           leader-catch accuracy vs lake-derived AND the principal answer key
- TARGET:  Run 7 traders -- including a RISK_OFFICER that competes as an equal
           (holds cash / a defensive basket, wins on merit when defense wins) --
           over real lake prices. Report weekly + monthly champions (daily data,
           2021->2026), and quarterly leaders/laggards + per-trader accuracy
           (monthly data, 2018->2026) graded against lake reality and the
           grok.md answer key. Evolution-adjust the worst. No LLM, no capital order.

Governance:
- The RISK_OFFICER here is a COMPETING TRADER, not the governance veto. The
  Risk-Officer *gate* on real capital artifacts (CLAUDE.md sec.5/10) is separate
  and unchanged. Holding cash that beats a drawdown is a legitimate way to win.
- llm_involvement="none": deterministic rule strategies over historical prices =>
  protocol KPI-eligible (docs/LLM-BACKTEST-PROTOCOL.md). The answer key is used
  ONLY for post-hoc grading, never as a trader input (no lookahead).
- Returns are RELATIVE rankings, not realistic P&L (no costs/slippage/sizing).
- Recommend-only research. Does not replace the canonical 10-signal pipeline.

Run: python simulation/historical_competition.py
"""

from __future__ import annotations

import glob
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[1]
LAKE = REPO / "data" / "lake" / "prices"
BENCHMARK = REPO / "simulation" / "data" / "quarterly_benchmark_2018_2026.json"
PROTOCOL_PATH = "docs/LLM-BACKTEST-PROTOCOL.md"

# --- The society's competing traders (RISK_OFFICER is one of them) ---
TRADERS: List[Dict[str, Any]] = [
    {"id": "MOMENTUM_SWING",   "type": "momentum",  "lookback": 3, "threshold": 0.04, "max_actions": 5},
    {"id": "MOMENTUM_FAST",    "type": "momentum",  "lookback": 1, "threshold": 0.03, "max_actions": 5},
    {"id": "TREND_RIDER",      "type": "momentum",  "lookback": 6, "threshold": 0.08, "max_actions": 5},
    {"id": "MEAN_REVERSION",   "type": "reversion", "lookback": 2, "threshold": 0.05, "max_actions": 5},
    {"id": "REVERSION_FAST",   "type": "reversion", "lookback": 1, "threshold": 0.04, "max_actions": 5},
    {"id": "BREAKOUT_HUNTER",  "type": "momentum",  "lookback": 2, "threshold": 0.06, "max_actions": 5},
    # The Risk Officer competes as an equal: cash when the tape is weak, else a
    # defensive/cyclical-conservative basket. No special powers here.
    {"id": "RISK_OFFICER",     "type": "defensive", "lookback": 3, "threshold": 0.0,  "max_actions": 8},
]

# Defensive / low-beta / cyclical-conservative basket (intersected with the lake).
DEFENSIVE_BASKET = ["KO", "PG", "JNJ", "WMT", "PEP", "MCD", "COST", "LMT", "NOC",
                    "RTX", "GLD", "NEM", "CVX", "XOM", "VZ", "SO", "DUK", "NEE",
                    "CL", "MDT", "MMC", "BRK-B"]


# ---------------------------------------------------------------------------
# Lake loading -> aligned close matrix
# ---------------------------------------------------------------------------
def load_close_matrix(interval: str, start_date: str
                      ) -> Tuple[List[str], List[str], np.ndarray]:
    files = sorted(glob.glob(str(LAKE / f"*_{interval}.parquet")))
    series: Dict[str, pd.Series] = {}
    for f in files:
        tkr = Path(f).name.replace(f"_{interval}.parquet", "")
        try:
            df = pd.read_parquet(f)
        except Exception:
            continue
        if df.empty:
            continue
        col = "Close" if "Close" in df.columns else ("close" if "close" in df.columns else None)
        if col is None:
            continue
        s = df[col].copy()
        s.index = pd.to_datetime(s.index).tz_localize(None)
        s = s[s.index >= pd.Timestamp(start_date)]
        if len(s) >= 12:
            series[tkr] = s
    if not series:
        return [], [], np.empty((0, 0))
    frame = pd.DataFrame(series).sort_index()
    dates = [d.strftime("%Y-%m-%d") for d in frame.index]
    tickers = list(frame.columns)
    closes = frame.to_numpy(dtype=float)  # [T, N], NaN where missing
    return dates, tickers, closes


# ---------------------------------------------------------------------------
# Per-trader numpy backtest -> dated next-period return series
# ---------------------------------------------------------------------------
def _lookback_return(closes: np.ndarray, t: int, L: int) -> np.ndarray:
    prev = closes[t - L]
    cur = closes[t]
    with np.errstate(invalid="ignore", divide="ignore"):
        return np.where((prev > 0), cur / prev - 1.0, np.nan)


def backtest_trader(closes: np.ndarray, trader: Dict[str, Any],
                    defensive_mask: np.ndarray) -> np.ndarray:
    T, N = closes.shape
    L = int(trader["lookback"])
    thr = float(trader["threshold"])
    k = int(trader["max_actions"])
    ttype = trader["type"]
    port = np.full(T, np.nan)

    for t in range(L, T - 1):
        nxt = closes[t + 1]
        cur = closes[t]
        with np.errstate(invalid="ignore", divide="ignore"):
            ret_next = np.where((cur > 0), nxt / cur - 1.0, np.nan)
        if ttype == "defensive":
            lb = _lookback_return(closes, t, L)
            breadth = np.nanmedian(lb) if np.any(~np.isnan(lb)) else 0.0
            if breadth < 0:
                port[t] = 0.0  # hold cash -> 0 beats a drawdown
            else:
                mask = defensive_mask & ~np.isnan(ret_next)
                port[t] = float(np.nanmean(ret_next[mask])) if np.any(mask) else 0.0
            continue
        lb = _lookback_return(closes, t, L)
        valid = ~np.isnan(lb) & ~np.isnan(ret_next)
        if ttype == "momentum":
            long_sig = valid & (lb > thr)
            short_sig = valid & (lb < -thr)
        else:  # reversion
            long_sig = valid & (lb < -thr)
            short_sig = valid & (lb > thr)
        # rank by signal magnitude, keep top-k across long+short
        strength = np.where(long_sig | short_sig, np.abs(lb), -np.inf)
        if not np.any(np.isfinite(strength) & (strength > -np.inf)):
            port[t] = 0.0
            continue
        order = np.argsort(strength)[::-1]
        picks = [i for i in order if (long_sig[i] or short_sig[i])][:k]
        if not picks:
            port[t] = 0.0
            continue
        scores = []
        for i in picks:
            r = ret_next[i]
            scores.append(r if long_sig[i] else -r)
        port[t] = float(np.mean(scores))
    return port


# ---------------------------------------------------------------------------
# Champions (bucket by week / month / quarter)
# ---------------------------------------------------------------------------
def _bucket_key(date: str, gran: str) -> str:
    ts = pd.Timestamp(date)
    if gran == "week":
        iso = ts.isocalendar()
        return f"{iso.year}-W{int(iso.week):02d}"
    if gran == "month":
        return date[:7]
    if gran == "quarter":
        return f"{ts.year}Q{(ts.month - 1) // 3 + 1}"
    raise ValueError(gran)


def champions(dates: List[str], per_trader: Dict[str, np.ndarray], gran: str
              ) -> Tuple[List[Dict[str, Any]], Dict[str, int]]:
    buckets: Dict[str, Dict[str, List[float]]] = {}
    for ti, (tid, arr) in enumerate(per_trader.items()):
        for t, d in enumerate(dates):
            r = arr[t]
            if np.isnan(r):
                continue
            buckets.setdefault(_bucket_key(d, gran), {}).setdefault(tid, []).append(r)
    timeline: List[Dict[str, Any]] = []
    tally: Dict[str, int] = {tid: 0 for tid in per_trader}
    for bk in sorted(buckets):
        comp = {tid: float(np.prod([1 + x for x in rs]) - 1)
                for tid, rs in buckets[bk].items()}
        champ = max(comp, key=comp.get)
        tally[champ] += 1
        timeline.append({"period": bk, "champion": champ,
                         "champion_return": round(comp[champ], 4),
                         "returns": {k: round(v, 4) for k, v in comp.items()}})
    return timeline, tally


# ---------------------------------------------------------------------------
# Quarterly leaders/laggards + per-trader accuracy (monthly data)
# ---------------------------------------------------------------------------
def _quarter_indices(dates: List[str]) -> Dict[str, List[int]]:
    out: Dict[str, List[int]] = {}
    for i, d in enumerate(dates):
        out.setdefault(_bucket_key(d, "quarter"), []).append(i)
    return out


def quarterly_accuracy(dates: List[str], tickers: List[str], closes: np.ndarray,
                       benchmark: Dict[str, Any], top_k: int = 8
                       ) -> Dict[str, Any]:
    qidx = _quarter_indices(dates)
    tick_arr = np.array(tickers)
    bench_q = benchmark.get("quarters", {})

    per_q: List[Dict[str, Any]] = []
    acc: Dict[str, Dict[str, List[float]]] = {
        t["id"]: {"catch": [], "avoid": [], "akey": []} for t in TRADERS}

    quarters = sorted(qidx)
    for q in quarters:
        idxs = qidx[q]
        if len(idxs) < 2:
            continue
        first, last = idxs[0], idxs[-1]
        start_px, end_px = closes[first], closes[last]
        with np.errstate(invalid="ignore", divide="ignore"):
            qret = np.where((start_px > 0), end_px / start_px - 1.0, np.nan)
        priced = ~np.isnan(qret)
        if priced.sum() < 20:
            continue
        order = np.argsort(np.where(priced, qret, -np.inf))[::-1]
        n_lead = max(5, int(priced.sum() * 0.10))
        leaders_lake = set(tick_arr[order[:n_lead]])
        laggards_lake = set(tick_arr[order[-n_lead:]])

        bench = bench_q.get(q, {})
        akey_leaders = set(bench.get("large_lead", []) + bench.get("small_lead", []))
        akey_in_lake = sorted(akey_leaders & set(tickers))

        # each trader's top-k longs decided at quarter start (PIT)
        trader_longs: Dict[str, List[str]] = {}
        for tr in TRADERS:
            L = int(tr["lookback"])
            if first - L < 0:
                trader_longs[tr["id"]] = []
                continue
            if tr["type"] == "defensive":
                longs = [t for t in DEFENSIVE_BASKET if t in tickers]
                trader_longs[tr["id"]] = longs[:top_k]
                continue
            lb = _lookback_return(closes, first, L)
            valid = ~np.isnan(lb)
            thr = float(tr["threshold"])
            if tr["type"] == "momentum":
                cand = np.where(valid & (lb > thr), lb, -np.inf)
                ranked = np.argsort(cand)[::-1]
            else:
                cand = np.where(valid & (lb < -thr), -lb, -np.inf)  # most oversold first
                ranked = np.argsort(cand)[::-1]
            picks = [tick_arr[i] for i in ranked if np.isfinite(cand[i])][:top_k]
            trader_longs[tr["id"]] = list(picks)

        q_rows = {}
        for tr in TRADERS:
            longs = set(trader_longs[tr["id"]])
            if longs:
                catch = len(longs & leaders_lake) / len(longs)
                avoid = 1.0 - len(longs & laggards_lake) / len(longs)
            else:
                catch, avoid = 0.0, 1.0
            akey_hit = (1.0 if (akey_in_lake and (longs & set(akey_in_lake)))
                        else (0.0 if akey_in_lake else np.nan))
            acc[tr["id"]]["catch"].append(catch)
            acc[tr["id"]]["avoid"].append(avoid)
            if not np.isnan(akey_hit):
                acc[tr["id"]]["akey"].append(akey_hit)
            q_rows[tr["id"]] = {"longs": trader_longs[tr["id"]][:5],
                                "catch": round(catch, 3), "avoid": round(avoid, 3)}

        per_q.append({
            "quarter": q,
            "regime": bench.get("regime"),
            "answer_key_leaders_in_lake": akey_in_lake,
            "lake_leaders_top": sorted(leaders_lake)[:8],
            "lake_laggards_bottom": sorted(laggards_lake)[:8],
            "trader_picks": q_rows,
        })

    # aggregate accuracy leaderboard
    leaderboard = []
    for tr in TRADERS:
        a = acc[tr["id"]]
        leaderboard.append({
            "trader": tr["id"], "type": tr["type"],
            "leader_catch_rate": round(float(np.mean(a["catch"])), 3) if a["catch"] else 0.0,
            "laggard_avoidance": round(float(np.mean(a["avoid"])), 3) if a["avoid"] else 0.0,
            "answer_key_hit_rate": round(float(np.mean(a["akey"])), 3) if a["akey"] else 0.0,
            "quarters_scored": len(a["catch"]),
        })
    leaderboard.sort(key=lambda r: (r["leader_catch_rate"] + r["answer_key_hit_rate"]),
                     reverse=True)
    return {"per_quarter": per_q, "accuracy_leaderboard": leaderboard,
            "n_quarters": len(per_q)}


# ---------------------------------------------------------------------------
# Evolution adjustment -- reflect on the weakest trader (reuses reflection_engine)
# ---------------------------------------------------------------------------
def evolution_adjustment(qacc: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    try:
        from simulation.reflection_engine import reflect_one
    except Exception:
        import sys
        sys.path.insert(0, str(REPO))
        from simulation.reflection_engine import reflect_one
    rows = [r for r in qacc["accuracy_leaderboard"] if r["type"] != "defensive"]
    if not rows:
        return None
    worst = min(rows, key=lambda r: r["leader_catch_rate"] + r["answer_key_hit_rate"])
    # Map accuracy metrics onto fitness components so the existing reflection
    # playbook (incl. the high-valuation dot-com template) can diagnose it.
    comps = {
        "hit_quality": worst["leader_catch_rate"],
        "drawdown_control": worst["laggard_avoidance"],
        "regime_stability": worst["answer_key_hit_rate"],
        "risk_adjusted": (worst["leader_catch_rate"] + worst["laggard_avoidance"]) / 2,
        "turnover_discipline": 0.8,
        "niche_purity": 1.0,
    }
    rep = reflect_one(worst["trader"], 0.0, comps, regime="high_valuation").to_dict()
    return {"target": worst["trader"], "diagnosis": rep,
            "status": "PROPOSAL", "human_gate": True,
            "note": "Adjustment proposal only; multi-regime re-test + human gate "
                    "before any change goes active (EVOLUTION_PROGRAM.md)."}


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> int:
    benchmark = json.loads(BENCHMARK.read_text(encoding="utf-8"))
    defensive_present = [t for t in DEFENSIVE_BASKET]

    # --- Daily competition (weekly + monthly champions, ~2021->2026) ---
    d_dates, d_tickers, d_closes = load_close_matrix("1d", "2021-01-01")
    d_defmask = np.array([t in set(defensive_present) for t in d_tickers])
    daily_ret = {tr["id"]: backtest_trader(d_closes, tr, d_defmask) for tr in TRADERS}
    weekly_tl, weekly_tally = champions(d_dates, daily_ret, "week")
    monthly_tl, monthly_tally = champions(d_dates, daily_ret, "month")

    # --- Monthly competition (quarterly leaders/laggards + accuracy, 2018->2026) ---
    m_dates, m_tickers, m_closes = load_close_matrix("1mo", "2018-01-01")
    m_defmask = np.array([t in set(defensive_present) for t in m_tickers])
    monthly_ret_q = {tr["id"]: backtest_trader(m_closes, tr, m_defmask) for tr in TRADERS}
    quarterly_tl, quarterly_tally = champions(m_dates, monthly_ret_q, "quarter")
    qacc = quarterly_accuracy(m_dates, m_tickers, m_closes, benchmark)

    result = {
        "type": "trading_society_historical_competition",
        "as_of_timestamp": datetime.now(timezone.utc).isoformat(),
        "role": "writer", "project": "Trading Society",
        "program": "simulation/historical_competition.py",
        "protocol_ref": PROTOCOL_PATH, "llm_involvement": "none", "kpi_eligible": True,
        "stage": 1,
        "traders": [{"id": t["id"], "type": t["type"]} for t in TRADERS],
        "data_windows": {
            "daily_for_weekly_monthly": {"start": d_dates[0] if d_dates else None,
                                         "end": d_dates[-1] if d_dates else None,
                                         "n_tickers": len(d_tickers)},
            "monthly_for_quarterly": {"start": m_dates[0] if m_dates else None,
                                      "end": m_dates[-1] if m_dates else None,
                                      "n_tickers": len(m_tickers)},
        },
        "weekly_champion_tally": dict(sorted(weekly_tally.items(), key=lambda x: -x[1])),
        "monthly_champion_tally": dict(sorted(monthly_tally.items(), key=lambda x: -x[1])),
        "quarterly_champion_tally": dict(sorted(quarterly_tally.items(), key=lambda x: -x[1])),
        "weekly_champions_recent": weekly_tl[-8:],
        "monthly_champions_recent": monthly_tl[-6:],
        "quarterly_champions": quarterly_tl,
        "quarterly_accuracy": qacc,
        "evolution_adjustment": evolution_adjustment(qacc),
        "answer_key": {"source": benchmark["_meta"]["source"],
                       "grade": benchmark["_meta"]["grade"],
                       "n_quarters": len(benchmark["quarters"])},
        "disclaimer": (
            "Stage 1. Returns are RELATIVE rankings, not realistic P&L (no costs / "
            "slippage / sizing). RISK_OFFICER competes as an equal trader, not the "
            "governance veto. Answer key (grok.md, Grade-D) used only for post-hoc "
            "grading, never as a trader input. Recommend-only; does not replace the "
            "canonical 10-signal pipeline."),
    }

    out = REPO / "outputs" / f"trading-society-history-{result['as_of_timestamp'][:10]}.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    _print_summary(result)
    print(f"\nArtifact: {out.relative_to(REPO)}")
    return 0


def _print_summary(r: Dict[str, Any]) -> None:
    print("=" * 74)
    print("TRADING SOCIETY -- Stage 1 historical competition (RISK_OFFICER = a trader)")
    print("=" * 74)
    dw = r["data_windows"]
    print(f"Daily window (weekly/monthly champs): {dw['daily_for_weekly_monthly']['start']}"
          f"..{dw['daily_for_weekly_monthly']['end']} "
          f"({dw['daily_for_weekly_monthly']['n_tickers']} names)")
    print(f"Monthly window (quarterly):           {dw['monthly_for_quarterly']['start']}"
          f"..{dw['monthly_for_quarterly']['end']} "
          f"({dw['monthly_for_quarterly']['n_tickers']} names)")

    print("\nWEEKLY champion wins (who won the most weeks):")
    for tid, n in r["weekly_champion_tally"].items():
        print(f"  {tid:<16} {n}")
    print("\nMONTHLY champion wins:")
    for tid, n in r["monthly_champion_tally"].items():
        print(f"  {tid:<16} {n}")
    print("\nQUARTERLY champion wins (2018-2026, monthly):")
    for tid, n in r["quarterly_champion_tally"].items():
        print(f"  {tid:<16} {n}")

    print("\nACCURACY leaderboard (caught quarter leaders / avoided laggards):")
    print(f"  {'trader':<16} {'type':<10} {'catch':>6} {'avoid':>6} {'answerKey':>9} {'#q':>4}")
    for row in r["quarterly_accuracy"]["accuracy_leaderboard"]:
        print(f"  {row['trader']:<16} {row['type']:<10} {row['leader_catch_rate']:>6.3f} "
              f"{row['laggard_avoidance']:>6.3f} {row['answer_key_hit_rate']:>9.3f} "
              f"{row['quarters_scored']:>4}")

    print("\nMost recent monthly champions:")
    for m in r["monthly_champions_recent"]:
        print(f"  {m['period']}: {m['champion']} ({m['champion_return']:+.3f})")
    ea = r.get("evolution_adjustment")
    if ea:
        d = ea["diagnosis"]
        print(f"\nEvolution adjustment (PROPOSAL, human-gated): weakest = "
              f"{ea['target']}; weakest axis = {d['weakest_component']}; "
              f"proposed param delta = {d['proposed_param_delta']}")
    print("\n" + r["disclaimer"])


if __name__ == "__main__":
    raise SystemExit(main())
