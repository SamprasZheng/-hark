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
    from simulation.performance_tracker import sharpe as sharpe_of
    from simulation.macro_risk import macro_risk_score as real_macro_risk
    from simulation.capex_provider import get_capex_momentum as real_capex
except Exception:  # pragma: no cover
    import sys
    sys.path.insert(0, str(REPO))
    from simulation.backtest_runner import load_pit_series, PricePoint
    from simulation.historical_competition import (
        TRADERS, DEFENSIVE_BASKET, backtest_trader, _lookback_return)
    from simulation.universe_competition import build_universe, SPACE_SLEEVE
    from simulation.performance_tracker import sharpe as sharpe_of
    from simulation.macro_risk import macro_risk_score as real_macro_risk
    from simulation.capex_provider import get_capex_momentum as real_capex

CHAMPION_FRACTION = 0.30
CHAMPION_BOOST = 1.40
HIGH_VALUATION_DEFENSIVE_FLOOR = 0.35  # CLAUDE.md sec.10 hedge floor
TRANSACTION_COST_BPS = 10.0            # round-trip, charged in fitness backtests
MAX_NAME_WEIGHT = 0.10                 # concentration cap: single name (review item)
MAX_SECTOR_WEIGHT = 0.35               # concentration cap: single sector

# Sector map (review: industry-concentration cap). Default sector = "other".
_SECTORS: Dict[str, List[str]] = {
    "ai_semis": ["NVDA", "AMD", "AVGO", "MRVL", "ARM", "MU", "TSM", "ASML",
                 "AMAT", "LRCX", "KLAC", "ONTO", "UCTT", "ICHR", "FORM", "NVMI",
                 "CAMT", "ENTG", "COHU", "KLIC", "ACMR", "AEHR", "ALAB", "CRDO",
                 "AXTI", "POET", "MPWR", "ON", "NVTS", "POWI", "WOLF", "AMKR",
                 "TER", "GLW", "SIMO", "WDC", "STX", "AOSL", "ADI", "NXPI",
                 "MCHP", "MXL", "DIOD", "SLAB", "LSCC", "SWKS", "QRVO", "INTC"],
    "megacap_software": ["AAPL", "MSFT", "GOOGL", "META", "AMZN", "ORCL", "CRM",
                         "NOW", "NFLX", "ADBE", "PANW", "CRWD", "FTNT", "DDOG",
                         "NET", "SNOW", "PLTR", "APP", "OKTA"],
    "optical_net": ["LITE", "COHR", "CIEN", "ANET", "AAOI", "FN"],
    "dc_power": ["VRT", "ETN", "GEV", "PWR", "CEG", "VST", "NRG", "ASMI"],
    "defense_space": ["LMT", "RTX", "NOC", "GD", "BA", "RKLB", "ASTS", "LUNR",
                      "PL", "RDW", "IRDM", "GSAT", "STRL", "DXYZ"],
    "defensive_staples": ["KO", "PG", "JNJ", "WMT", "PEP", "MCD", "COST", "CL",
                          "MDT", "MMC", "VZ", "SO", "DUK", "NEE", "GLD", "NEM",
                          "BRK-B"],
    "speculative": ["MSTR", "COIN", "HOOD", "CVNA", "QBTS", "IONQ", "RGTI", "AI",
                    "BBAI", "SOUN"],
    "consumer_media": ["ROKU", "DIS", "ABNB", "CROX", "CAVA", "CMG"],
}
SECTOR_OF: Dict[str, str] = {t: s for s, names in _SECTORS.items() for t in names}


def sector_of(ticker: str) -> str:
    return SECTOR_OF.get(ticker, "other")


def _finviz_industry_map(tickers: List[str]) -> Dict[str, str]:
    """Real Finviz Elite industry labels for the candidate names; {} on failure."""
    if not tickers:
        return {}
    try:
        from simulation.finviz_data import get_sector_map
        return get_sector_map(tickers, use_industry=True)
    except Exception:
        return {}


def _finviz_market_caps(tickers: List[str]) -> Dict[str, float]:
    """Real Finviz market caps ($bn) for the small-cap specialist; {} on failure."""
    if not tickers:
        return {}
    try:
        from simulation.finviz_data import get_market_caps
        return get_market_caps(tickers)
    except Exception:
        return {}


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
        port = backtest_trader(mat, tr, defmask, cost_bps=TRANSACTION_COST_BPS)
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
def macro_risk_score(as_of: Optional[str] = None,
                     buffett_indicator: Optional[float] = None) -> Dict[str, Any]:
    """Real FRED-based macro risk (review item B). Valuation now uses a REAL
    Buffett Indicator (FRED NCBEILQ027S / GDP) when buffett_indicator is None."""
    r = real_macro_risk(as_of=as_of, pit=bool(as_of), buffett_indicator=buffett_indicator)
    bi = r["inputs"].get("buffett_indicator", buffett_indicator)
    return {"score_0_100": r["score_0_100"], "posture": r["posture"],
            "buffett_indicator": bi, "bubble_flag": bool(bi > 200),
            "components": r["components"], "sources": r["sources"],
            "n_live_series": r["n_live_series"],
            "is_point_in_time": r["is_point_in_time"],
            "note": "Real FRED composite (credit/curve/vix/M2/liquidity); "
                    "valuation input is an override (flagged). Higher = risk-off."}


def capex_momentum_score(series: Dict[str, List[PricePoint]],
                         as_of: Optional[str] = None) -> Dict[str, Any]:
    """Real capex 1st/2nd derivative if a cache exists, else flagged price proxy
    (review item A). See simulation/capex_provider.py."""
    return real_capex(series=series, as_of=as_of)


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
                     growth_ratio: float, max_names: int = 14,
                     sector_fn=None
                     ) -> Tuple[List[Dict[str, Any]], float, Dict[str, float]]:
    """Society-weighted vote -> growth leg, with single-name and single-sector
    concentration caps (review item). Returns (leg, realized_weight, sector_mix).
    Weight clipped away by caps is reported so the caller routes it to cash.
    sector_fn(ticker)->label defaults to the hardcoded map; pass a real Finviz
    industry map for a finer, data-driven sector cap."""
    sec = sector_fn or sector_of
    # Iterate every voting trader in `weights` (base 7 + any specialists), skipping
    # the defensive trader (its weight feeds the defensive leg, not growth).
    defensive_ids = {t["id"] for t in TRADERS if t["type"] == "defensive"}
    score: Dict[str, float] = {}
    backers: Dict[str, List[str]] = {}
    for tid, w in weights.items():
        if tid in defensive_ids:
            continue
        for tk in longs.get(tid, []):
            score[tk] = score.get(tk, 0.0) + w
            backers.setdefault(tk, []).append(tid)
    if not score:
        return [], 0.0, {}
    top = sorted(score, key=score.get, reverse=True)[:max_names]
    tot = sum(score[t] for t in top) or 1.0
    # raw absolute weights summing to growth_ratio
    wt = {t: growth_ratio * score[t] / tot for t in top}
    # cap 1: single name
    wt = {t: min(w, MAX_NAME_WEIGHT) for t, w in wt.items()}
    # cap 2: single sector -- scale an over-weight sector's names down
    sec_sum: Dict[str, float] = {}
    for t, w in wt.items():
        sec_sum[sec(t)] = sec_sum.get(sec(t), 0.0) + w
    for sname, s in sec_sum.items():
        if s > MAX_SECTOR_WEIGHT and s > 0:
            scale = MAX_SECTOR_WEIGHT / s
            for t in wt:
                if sec(t) == sname:
                    wt[t] *= scale
    realized = sum(wt.values())
    leg = []
    for t in sorted(wt, key=wt.get, reverse=True):
        leg.append({"ticker": t, "weight": round(wt[t], 4), "sector": sec(t),
                    "n_backers": len(backers[t]), "backers": backers[t][:4]})
    sector_mix = {}
    for c in leg:
        sector_mix[c["sector"]] = round(sector_mix.get(c["sector"], 0.0) + c["weight"], 4)
    return leg, round(realized, 4), sector_mix


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

    as_of = dates[-1] if dates else None
    fitness = _trader_recent_fitness(mat, defmask)
    wb = _weights_with_champion_boost(fitness)
    longs = _trader_current_longs(mat, tickers)

    macro = macro_risk_score(as_of=None)  # live FRED (set as_of for ALFRED PIT)
    capex = capex_momentum_score(series, as_of=as_of)
    high_val = bool(macro["bubble_flag"] or macro["buffett_indicator"] > 200)
    dleg = defensive_leg_ratio(macro["score_0_100"], capex["score_0_100"], high_val)

    # grok2.md regime guardrail (veto-class). HARD_DEFENSE raises the defensive
    # floor; PARADIGM_BREAKTHROUGH locks reverse-shorts on AI leaders.
    regime = None
    regime_tilt_applied = None
    try:
        from simulation.regime_filter import from_live as _regime_from_live
        from simulation.regime_filter import trader_tilt as _trader_tilt
        regime = _regime_from_live(macro, capex).to_dict()
        floor = regime.get("defensive_floor", 0.0)
        if floor > dleg["defensive_ratio"]:
            dleg = {**dleg, "defensive_ratio": round(floor, 3),
                    "core_growth_ratio": round(1 - floor, 3),
                    "regime_floor_applied": regime["regime"]}
        # grok2.md regime -> trader weight tilt: reshape the society vote by regime.
        tilt = _trader_tilt(regime["regime"])
        if tilt:
            tw = {k: wb["weights"][k] * tilt.get(k, 1.0) for k in wb["weights"]}
            tot = sum(tw.values()) or 1.0
            wb = {"weights": {k: round(v / tot, 4) for k, v in tw.items()},
                  "champions": wb["champions"]}
            regime_tilt_applied = regime["regime"]
    except Exception:
        regime = None

    # Phase-1 specialists (grok2.md roster): Small Cap Catalyst Hunter +
    # Power & AI Infrastructure Trader join the vote with base weight x regime
    # tilt; everything renormalizes. Their picks come from the full series.
    specialist_info = None
    try:
        from simulation.specialist_traders import SPECIALISTS, specialist_picks
        from simulation.regime_filter import trader_tilt as _stilt
        spec_mcaps = _finviz_market_caps(tickers)
        spicks = specialist_picks(series, spec_mcaps)
        rtilt = _stilt(regime["regime"]) if regime else {}
        spec_w: Dict[str, float] = {}
        chosen: Dict[str, Any] = {}
        for s in SPECIALISTS:
            names = [p["ticker"] for p in spicks.get(s.trader_id, [])]
            if names:
                longs[s.trader_id] = names
                spec_w[s.trader_id] = round(s.base_weight * rtilt.get(s.trader_id, 1.0), 4)
                chosen[s.trader_id] = [{"ticker": p["ticker"], "score": p["score"],
                                        "suggested_size": p["suggested_size"]}
                                       for p in spicks[s.trader_id][:6]]
        if spec_w:
            combined = {**wb["weights"], **spec_w}
            tot = sum(combined.values()) or 1.0
            wb = {"weights": {k: round(v / tot, 4) for k, v in combined.items()},
                  "champions": wb["champions"]}
            specialist_info = {"weights": spec_w, "top_picks": chosen}
    except Exception:
        specialist_info = None

    # Real Finviz industry map for every voting trader's names -> finer
    # concentration cap; fall back to the hardcoded sector map where Finviz has none.
    voting_ids = [k for k in wb["weights"] if k != "RISK_OFFICER"]
    candidate_names = sorted({t for tid in voting_ids for t in longs.get(tid, [])})
    finviz_map = _finviz_industry_map(candidate_names)
    sector_source = "finviz_industry" if finviz_map else "hardcoded"

    def _sec(t: str) -> str:
        return finviz_map.get(t) or sector_of(t)

    core, realized_growth, sector_mix = _core_growth_leg(
        longs, wb["weights"], dleg["core_growth_ratio"], sector_fn=_sec)
    # weight clipped by concentration caps is routed to cash (conservative)
    cap_shortfall = round(max(0.0, dleg["core_growth_ratio"] - realized_growth), 4)
    defensive = _defensive_leg(tickers, dleg["defensive_ratio"] + cap_shortfall)

    space_in_core = [c["ticker"] for c in core if c["ticker"] in SPACE_SLEEVE]
    ro_note = (
        f"High-valuation regime: defensive floor {HIGH_VALUATION_DEFENSIVE_FLOOR:.0%} "
        f"enforced (CLAUDE sec.10). Macro plumbing posture={macro['posture']} "
        f"(score {macro['score_0_100']}). Defensive leg {dleg['defensive_ratio']:.0%}"
        + (f" + {cap_shortfall:.0%} cap-shortfall to cash" if cap_shortfall else "") + "."
        if high_val else
        f"Macro posture={macro['posture']} (score {macro['score_0_100']}); "
        f"defensive leg {dleg['defensive_ratio']:.0%} (macro+capex driven).")

    return {
        "horizon": horizon,
        "as_of": as_of,
        "lookback_days": lookback_days,
        "trader_weights": wb["weights"],
        "recent_champions_boosted": wb["champions"],
        "regime_trader_tilt_applied": regime_tilt_applied,
        "specialists": specialist_info,
        "transaction_cost_bps": TRANSACTION_COST_BPS,
        "macro_risk_environment": macro,
        "capex_momentum": capex,
        "regime_guardrail": regime,
        "defensive_decision": dleg,
        "concentration_caps": {"max_name": MAX_NAME_WEIGHT,
                               "max_sector": MAX_SECTOR_WEIGHT,
                               "sector_source": sector_source,
                               "realized_growth_weight": realized_growth,
                               "cap_shortfall_to_cash": cap_shortfall,
                               "sector_mix": sector_mix},
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
            "gate. Macro = real FRED composite incl. a real Buffett Indicator "
            "(NCBEILQ027S/GDP); sector cap uses real Finviz industries; weights "
            "include a 10bps round-trip cost; single-name <=10% / single-sector "
            "<=35% caps; grok2.md regime guardrail applied (HARD_DEFENSE floor / "
            "Momentum-Decoupling-Lock). Capex is real (polygon) when cached, else a "
            "flagged price proxy. Promotion needs human + Risk-Officer gate + review."),
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
        mr = p["macro_risk_environment"]
        print(f"  Macro risk: {mr['score_0_100']}/100 ({mr['posture']}, "
              f"{mr['n_live_series']} live FRED series; BI {mr['buffett_indicator']})")
        cx = p["capex_momentum"]
        print(f"  Capex momentum: {cx['score_0_100']}/100 (source={cx['source']})")
        rg = p.get("regime_guardrail")
        if rg:
            lock = " MOM-DECOUPLING-LOCK" if rg.get("momentum_decoupling_lock") else ""
            print(f"  Regime guardrail: {rg['regime']} "
                  f"(smallcap_cap={rg['smallcap_allocation_cap']}, "
                  f"floor={rg['defensive_floor']}, winsor={rg['winsorization']}){lock}")
        dd = p["defensive_decision"]
        cc = p["concentration_caps"]
        print(f"  Posture: {dd['posture']} -> defensive {dd['defensive_ratio']:.0%} / "
              f"growth {dd['core_growth_ratio']:.0%} "
              f"(caps: name<={cc['max_name']:.0%}, sector<={cc['max_sector']:.0%}; "
              f"sectors={cc['sector_mix']})")
        champs = p["recent_champions_boosted"]
        print(f"  Champion-boosted traders: {champs}")
        sp = p.get("specialists")
        if sp:
            for tid, picks in sp["top_picks"].items():
                names = ", ".join(f"{q['ticker']}({q['score']})" for q in picks[:4])
                print(f"  {tid} (w={sp['weights'].get(tid)}): {names}")
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
