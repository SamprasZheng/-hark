#!/usr/bin/env python3
"""
Trading Society -- Forward Portfolio Generator (Stage 2)

PPST Declaration (this PROGRAM):
- PROJECT: Trading Society
- PROGRAM: simulation/portfolio_generator.py
- SKILL:   whole-society weighted vote -> champion boost -> macro/capex dynamic
           defensive leg -> Risk-Officer review -> forward portfolio
- TARGET:  Produce a NEXT-MONTH and NEXT-QUARTER portfolio (core growth leg +
           dynamic defensive leg) from the society of traders, per the principal's
           chosen flow (society weighting as the main mechanism; walk-forward as a
           periodic health check). Recommend-only research. No capital order.

The 8-step flow (principal-specified):
  1. each trader produces current signals (longs) from real lake prices (PIT)
  2. recent fitness -> base trader weights
  3. champion boost (recent top ~30% get +40% weight)
  4. Macro Risk Environment Score (0-100)
  5. Capex Momentum Score (0-100)         [proxy until real capex wired -- flagged]
  6. Macro + Capex -> dynamic defensive-leg ratio
  7. Risk-Officer review (high-valuation hedge floor, CLAUDE.md sec.10)
  8. final portfolio = core growth leg (society-weighted) + defensive leg (RO)

Governance:
- llm_involvement="none" (deterministic). PIT: signals use only data <= as_of.
- Recommend-only. Does NOT place orders and does NOT replace the canonical
  10-signal pipeline (src/sharks/daily_picks.py) or the Risk-Officer gate.
- High-valuation regime forces a minimum defensive floor (CLAUDE.md sec.10).
- Capex score is a flagged PROXY (price momentum of the AI-capex sleeve) until
  real 1st/2nd-derivative capex from financials is wired (no fabrication).

Run: python simulation/portfolio_generator.py
"""

from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

REPO = Path(__file__).resolve().parents[1]

try:
    from simulation.backtest_runner import load_pit_series, PricePoint
    from simulation.historical_competition import (
        TRADERS, DEFENSIVE_BASKET, backtest_trader, _lookback_return)
    from simulation.universe_competition import build_universe, SPACE_SLEEVE
    from simulation.performance_tracker import sharpe as sharpe_of, bubble_risk_score
    from simulation.macro_data_provider import get_market_context, synthetic_snapshot
except Exception:  # pragma: no cover
    import sys
    sys.path.insert(0, str(REPO))
    from simulation.backtest_runner import load_pit_series, PricePoint
    from simulation.historical_competition import (
        TRADERS, DEFENSIVE_BASKET, backtest_trader, _lookback_return)
    from simulation.universe_competition import build_universe, SPACE_SLEEVE
    from simulation.performance_tracker import sharpe as sharpe_of, bubble_risk_score
    from simulation.macro_data_provider import get_market_context, synthetic_snapshot

# AI-capex sleeve used as the Capex-momentum PROXY (semis / AI infra).
CAPEX_SLEEVE = ["NVDA", "AVGO", "AMD", "TSM", "ASML", "AMAT", "LRCX", "KLAC",
                "MU", "MRVL", "VRT", "GEV", "ETN", "ANET", "CRWV", "ORCL"]
CHAMPION_FRACTION = 0.30
CHAMPION_BOOST = 1.40
HIGH_VALUATION_DEFENSIVE_FLOOR = 0.35  # CLAUDE.md sec.10 hedge floor


# ---------------------------------------------------------------------------
# Matrix helper
# ---------------------------------------------------------------------------
def _matrix(series: Dict[str, List[PricePoint]], lookback_days: int
            ) -> Tuple[List[str], List[str], np.ndarray]:
    all_dates = sorted({p.as_of for pts in series.values() for p in pts})
    dates = all_dates[-lookback_days:]
    dset = set(dates)
    tickers = sorted(series.keys())
    mat = np.full((len(dates), len(tickers)), np.nan)
    didx = {d: i for i, d in enumerate(dates)}
    for j, t in enumerate(tickers):
        for p in series[t]:
            if p.as_of in dset:
                mat[didx[p.as_of], j] = p.close
    return dates, tickers, mat


# ---------------------------------------------------------------------------
# Steps 1-3: trader signals + fitness weights + champion boost
# ---------------------------------------------------------------------------
def _trader_recent_fitness(mat: np.ndarray, defmask: np.ndarray
                           ) -> Dict[str, float]:
    out: Dict[str, float] = {}
    for tr in TRADERS:
        port = backtest_trader(mat, tr, defmask)
        rets = [x for x in port.tolist() if not math.isnan(x)]
        out[tr["id"]] = sharpe_of(rets) if len(rets) >= 5 else 0.0
    return out


def _trader_current_longs(mat: np.ndarray, tickers: List[str], top_k: int = 8
                          ) -> Dict[str, List[str]]:
    tick = np.array(tickers)
    T = mat.shape[0]
    t = T - 1
    longs: Dict[str, List[str]] = {}
    for tr in TRADERS:
        if tr["type"] == "defensive":
            longs[tr["id"]] = [x for x in DEFENSIVE_BASKET if x in tickers][:top_k]
            continue
        L = int(tr["lookback"])
        if t - L < 0:
            longs[tr["id"]] = []
            continue
        lb = _lookback_return(mat, t, L)
        valid = ~np.isnan(lb)
        thr = float(tr["threshold"])
        if tr["type"] == "momentum":
            cand = np.where(valid & (lb > thr), lb, -np.inf)
        else:
            cand = np.where(valid & (lb < -thr), -lb, -np.inf)
        order = np.argsort(cand)[::-1]
        longs[tr["id"]] = [tick[i] for i in order if np.isfinite(cand[i])][:top_k]
    return longs


def _weights_with_champion_boost(fitness: Dict[str, float]) -> Dict[str, Any]:
    # base weight = positive part of recent risk-adjusted fitness, floored
    base = {k: max(0.05, v) for k, v in fitness.items()}
    ranked = sorted(fitness, key=fitness.get, reverse=True)
    n_champ = max(1, round(len(ranked) * CHAMPION_FRACTION))
    champions = ranked[:n_champ]
    boosted = {k: base[k] * (CHAMPION_BOOST if k in champions else 1.0) for k in base}
    total = sum(boosted.values()) or 1.0
    weights = {k: round(v / total, 4) for k, v in boosted.items()}
    return {"weights": weights, "champions": champions}


# ---------------------------------------------------------------------------
# Steps 4-6: macro + capex -> defensive ratio
# ---------------------------------------------------------------------------
def macro_risk_score(stressed: bool = True) -> Dict[str, Any]:
    snap = synthetic_snapshot("2026-06-14", stressed=stressed)
    score = bubble_risk_score(buffett_indicator=snap.buffett_indicator,
                              dalio_bubble_flag=snap.dalio_bubble_flag,
                              vix=snap.extra.get("vix") if hasattr(snap, "extra") else None)
    return {"score_0_100": round(score * 100, 1),
            "buffett_indicator": snap.buffett_indicator,
            "bubble_flag": snap.dalio_bubble_flag,
            "regime": snap.regime_label, "source": snap.source,
            "is_point_in_time": snap.is_point_in_time,
            "note": "M2/BTC/Gold/CRB/credit-spread wires are TODO; current score "
                    "from buffett-indicator + bubble flag (synthetic, not PIT)."}


def capex_momentum_score(series: Dict[str, List[PricePoint]]) -> Dict[str, Any]:
    """PROXY: 3-month price momentum of the AI-capex sleeve, mapped to 0-100.
    Flagged as a proxy until real 1st/2nd-derivative capex from financials is wired."""
    present = [t for t in CAPEX_SLEEVE if t in series and len(series[t]) > 63]
    moms = []
    for t in present:
        pts = series[t]
        m = pts[-1].close / pts[-63].close - 1.0 if pts[-63].close > 0 else 0.0
        moms.append(m)
    avg = float(np.mean(moms)) if moms else 0.0
    # map -20%..+30% momentum onto 0..100
    score = max(0.0, min(100.0, (avg + 0.20) / 0.50 * 100))
    return {"score_0_100": round(score, 1), "proxy_avg_3m_momentum": round(avg, 4),
            "sleeve_priced": present,
            "note": "PROXY = AI-capex sleeve 3m price momentum. Real capex 1st/2nd "
                    "derivative from financials (polygon/finnhub) is TODO -- no "
                    "fabrication of capex figures."}


def defensive_leg_ratio(macro_0_100: float, capex_0_100: float,
                        high_valuation: bool) -> Dict[str, Any]:
    """Map (Macro risk, Capex momentum) -> defensive ratio per the principal table."""
    # Higher macro risk -> more defensive; higher capex momentum -> less defensive.
    base = 0.20 + (macro_0_100 / 100.0) * 0.30 - (capex_0_100 / 100.0) * 0.15
    base = max(0.10, min(0.60, base))
    floored = max(base, HIGH_VALUATION_DEFENSIVE_FLOOR) if high_valuation else base
    if floored >= 0.45:
        regime = "high_uncertainty"
    elif floored >= 0.35:
        regime = "risk_off"
    elif floored >= 0.22:
        regime = "neutral"
    else:
        regime = "risk_on"
    return {"defensive_ratio": round(floored, 3),
            "core_growth_ratio": round(1 - floored, 3),
            "posture": regime,
            "high_valuation_floor_applied": bool(high_valuation and floored == HIGH_VALUATION_DEFENSIVE_FLOOR and base < HIGH_VALUATION_DEFENSIVE_FLOOR)}


# ---------------------------------------------------------------------------
# Steps 7-8: assemble portfolio
# ---------------------------------------------------------------------------
def _core_growth_leg(longs: Dict[str, List[str]], weights: Dict[str, float],
                     growth_ratio: float, max_names: int = 12) -> List[Dict[str, Any]]:
    score: Dict[str, float] = {}
    backers: Dict[str, List[str]] = {}
    for tr in TRADERS:
        if tr["type"] == "defensive":
            continue
        w = weights.get(tr["id"], 0.0)
        for tk in longs.get(tr["id"], []):
            score[tk] = score.get(tk, 0.0) + w
            backers.setdefault(tk, []).append(tr["id"])
    if not score:
        return []
    top = sorted(score, key=score.get, reverse=True)[:max_names]
    tot = sum(score[t] for t in top) or 1.0
    leg = []
    for t in top:
        leg.append({"ticker": t,
                    "weight": round(growth_ratio * score[t] / tot, 4),
                    "n_backers": len(backers[t]),
                    "backers": backers[t][:4]})
    return leg


def _defensive_leg(tickers_present: List[str], defensive_ratio: float
                   ) -> Dict[str, Any]:
    holds = [t for t in DEFENSIVE_BASKET if t in tickers_present]
    # split defensive leg: half cash, half across the defensive basket
    cash = round(defensive_ratio * 0.5, 4)
    per = (defensive_ratio - cash) / len(holds) if holds else 0.0
    return {"cash_pct": cash,
            "holdings": [{"ticker": t, "weight": round(per, 4)} for t in holds[:8]]}


def generate_portfolio(horizon: str, lookback_days: int,
                       series: Dict[str, List[PricePoint]],
                       universe_meta: Dict[str, Any]) -> Dict[str, Any]:
    dates, tickers, mat = _matrix(series, lookback_days)
    defmask = np.array([t in set(DEFENSIVE_BASKET) for t in tickers])

    fitness = _trader_recent_fitness(mat, defmask)
    wb = _weights_with_champion_boost(fitness)
    longs = _trader_current_longs(mat, tickers)

    macro = macro_risk_score(stressed=True)
    capex = capex_momentum_score(series)
    high_val = bool(macro["bubble_flag"] or macro["buffett_indicator"] > 200)
    dleg = defensive_leg_ratio(macro["score_0_100"], capex["score_0_100"], high_val)

    core = _core_growth_leg(longs, wb["weights"], dleg["core_growth_ratio"])
    defensive = _defensive_leg(tickers, dleg["defensive_ratio"])

    space_in_core = [c["ticker"] for c in core if c["ticker"] in SPACE_SLEEVE]
    ro_note = (
        f"High-valuation regime: defensive floor {HIGH_VALUATION_DEFENSIVE_FLOOR:.0%} "
        f"enforced (CLAUDE sec.10). Final defensive leg {dleg['defensive_ratio']:.0%}."
        if high_val else
        f"Normal regime: defensive leg {dleg['defensive_ratio']:.0%} (macro+capex driven).")

    return {
        "horizon": horizon,
        "as_of": dates[-1] if dates else None,
        "lookback_days": lookback_days,
        "trader_weights": wb["weights"],
        "recent_champions_boosted": wb["champions"],
        "macro_risk_environment": macro,
        "capex_momentum": capex,
        "defensive_decision": dleg,
        "core_growth_leg": core,
        "defensive_leg": defensive,
        "spacex_exposure_in_core": space_in_core,
        "risk_officer_note": ro_note,
    }


def main() -> int:
    uni = build_universe(max_names=160)
    series = load_pit_series(uni["tickers"])
    series = {t: pts for t, pts in series.items() if pts}

    monthly = generate_portfolio("next_month", 63, series, uni)
    quarterly = generate_portfolio("next_quarter", 126, series, uni)

    result = {
        "type": "trading_society_forward_portfolio",
        "as_of_timestamp": datetime.now(timezone.utc).isoformat(),
        "role": "writer", "project": "Trading Society",
        "program": "simulation/portfolio_generator.py",
        "protocol_ref": "docs/LLM-BACKTEST-PROTOCOL.md",
        "llm_involvement": "none", "stage": 2,
        "method": "society weighted vote + champion boost + macro/capex dynamic "
                  "defensive leg + Risk-Officer hedge floor",
        "universe": {"n": uni["n"], "n_priced": len(series),
                     "space_sleeve": uni["sources"]["space_sleeve_in_lake"]},
        "portfolios": {"next_month": monthly, "next_quarter": quarterly},
        "walk_forward_health_check": (
            "Periodic check (not every run): verify portfolios built from past-N "
            "weighting were effective out-of-sample next period; run "
            "simulation/historical_competition.py and compare champion stability. "
            "TODO: automate as a scheduled gated step."),
        "disclaimer": (
            "Stage 2 forward portfolio. Recommend-only RESEARCH. Not a capital order; "
            "does not replace the canonical 10-signal pipeline or the Risk-Officer "
            "gate. Weights from relative (cost-free) backtests; Capex score is a "
            "flagged proxy; macro is synthetic (not PIT). Promotion to capital use "
            "requires human selection + Risk-Officer gate + cross-review."),
    }

    out = REPO / "outputs" / f"trading-society-portfolio-{result['as_of_timestamp'][:10]}.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    _print_summary(result)
    print(f"\nArtifact: {out.relative_to(REPO)}")
    return 0


def _print_summary(r: Dict[str, Any]) -> None:
    print("=" * 74)
    print("TRADING SOCIETY -- Stage 2 forward portfolio (society vote + dynamic hedge)")
    print("=" * 74)
    u = r["universe"]
    print(f"Universe: {u['n_priced']} priced | method: {r['method']}")
    for hz in ("next_month", "next_quarter"):
        p = r["portfolios"][hz]
        print(f"\n----- {hz.upper()} (as_of {p['as_of']}, lookback {p['lookback_days']}d) -----")
        print(f"  Macro risk score: {p['macro_risk_environment']['score_0_100']}/100 "
              f"(BI {p['macro_risk_environment']['buffett_indicator']}, "
              f"bubble={p['macro_risk_environment']['bubble_flag']})")
        print(f"  Capex momentum (proxy): {p['capex_momentum']['score_0_100']}/100")
        dd = p["defensive_decision"]
        print(f"  Posture: {dd['posture']} -> defensive {dd['defensive_ratio']:.0%} / "
              f"growth {dd['core_growth_ratio']:.0%}")
        champs = p["recent_champions_boosted"]
        print(f"  Champion-boosted traders: {champs}")
        print(f"  Core growth leg (top names):")
        for c in p["core_growth_leg"][:8]:
            tag = " [SpaceX]" if c["ticker"] in ("DXYZ", "RKLB", "ASTS", "PL", "LUNR",
                                                 "STRL", "IRDM", "GSAT", "LMT", "NOC", "BA") else ""
            print(f"     {c['ticker']:<6} {c['weight']*100:>5.1f}%  "
                  f"(x{c['n_backers']} {','.join(c['backers'][:3])}){tag}")
        dl = p["defensive_leg"]
        print(f"  Defensive leg: cash {dl['cash_pct']*100:.1f}% + "
              f"{', '.join(h['ticker'] for h in dl['holdings'][:6])}")
        print(f"  RO: {p['risk_officer_note']}")
    print("\n" + r["disclaimer"])


if __name__ == "__main__":
    raise SystemExit(main())
