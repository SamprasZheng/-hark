#!/usr/bin/env python3
"""
Trading Society -- Specialist traders, Phase 1 (grok2.md 14-trader roster)

PPST Declaration (this PROGRAM):
- PROJECT: Trading Society
- PROGRAM: simulation/specialist_traders.py
- SKILL:   sector/style specialist scorecards (0-100) + current picks
- TARGET:  Implement the two highest-value Phase-1 specialists from grok2.md:
             - Small Cap Catalyst Hunter (low-base small-cap breakout; fills the
               "not only large caps" gap; real market-cap filter via Finviz)
             - Power & AI Infrastructure Trader (the AI power/grid/cooling/
               advanced-packaging sleeve; the principal's top theme)
           Each emits a transparent 0-100 scorecard + position-size suggestion +
           ranked current picks from real lake prices. Recommend-only, no LLM.

Governance: recommend-only; picks join the society vote (portfolio_generator) and
are subject to the regime guardrail + concentration caps + Risk-Officer gate.
Scorecards are deterministic and auditable (no mysticism -- grok2.md "不依賴玄學").

Run: python simulation/specialist_traders.py   (live picks on the real universe)
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

# AI power / grid / cooling / advanced-packaging / networking sleeve.
AI_INFRA_SLEEVE = ["VRT", "GEV", "ETN", "VST", "CEG", "NRG", "PWR", "TLN", "CRWV",
                   "ANET", "COHR", "CRDO", "AMKR", "UCTT", "ICHR", "ENTG", "KLAC",
                   "ONTO", "FORM", "NVMI", "CAMT"]
SMALLCAP_MAX_BN = 12.0   # small/mid-cap ceiling (billions)


def _ret(pts, lag: int) -> Optional[float]:
    if len(pts) <= lag or pts[-1 - lag].close <= 0:
        return None
    return pts[-1].close / pts[-1 - lag].close - 1.0


def _clip(x: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, x))


def _max_drawdown(closes: List[float]) -> float:
    peak, mdd = -1e18, 0.0
    for c in closes:
        peak = max(peak, c)
        if peak > 0:
            mdd = min(mdd, c / peak - 1.0)
    return mdd


# ---------------------------------------------------------------------------
# Scorecards (0-100) -- transparent, documented dimensions
# ---------------------------------------------------------------------------
def small_cap_catalyst_score(pts, mcap_bn: Optional[float]) -> Tuple[float, Dict[str, float]]:
    """Low-base small-cap breakout. Gate: market cap < SMALLCAP_MAX_BN."""
    if mcap_bn is None or mcap_bn > SMALLCAP_MAX_BN or len(pts) < 63:
        return 0.0, {}
    closes = [p.close for p in pts]
    mom_1m = _ret(pts, 21) or 0.0
    mom_3m = _ret(pts, 63) or 0.0
    trail_high = max(closes[-120:]) if len(closes) >= 120 else max(closes)
    dist_from_high = closes[-1] / trail_high - 1.0 if trail_high > 0 else 0.0
    # smaller cap -> higher (0.3B..12B)
    cap = _clip((SMALLCAP_MAX_BN - mcap_bn) / (SMALLCAP_MAX_BN - 0.3)) * 25
    # low base: off the trailing high (a base to break out from)
    low_base = _clip(-dist_from_high / 0.45) * 25
    # breakout: recent positive momentum
    breakout = _clip((mom_1m + 0.03) / 0.25) * 30
    # catalyst proxy: 1m accelerating vs the 3m trend
    accel = _clip((mom_1m - mom_3m / 3.0 + 0.02) / 0.15) * 20
    score = round(cap + low_base + breakout + accel, 1)
    return score, {"mcap_bn": mcap_bn, "mom_1m": round(mom_1m, 3),
                   "dist_from_high": round(dist_from_high, 3),
                   "cap": round(cap, 1), "low_base": round(low_base, 1),
                   "breakout": round(breakout, 1), "accel": round(accel, 1)}


def power_ai_infra_score(ticker: str, pts) -> Tuple[float, Dict[str, float]]:
    """AI power/grid/cooling/packaging sleeve momentum + persistence. Gate: in sleeve."""
    if ticker not in AI_INFRA_SLEEVE or len(pts) < 63:
        return 0.0, {}
    closes = [p.close for p in pts]
    mom_3m = _ret(pts, 63) or 0.0
    mom_1m = _ret(pts, 21) or 0.0
    mdd = _max_drawdown(closes[-63:])
    trend = _clip((mom_3m + 0.10) / 0.40) * 40       # 3m trend strength
    rel = _clip((mom_1m + 0.05) / 0.25) * 30         # recent relative strength
    persistence = _clip(1.0 - abs(mdd) / 0.30) * 30  # low drawdown = durable
    score = round(trend + rel + persistence, 1)
    return score, {"mom_3m": round(mom_3m, 3), "mom_1m": round(mom_1m, 3),
                   "max_dd_3m": round(mdd, 3), "trend": round(trend, 1),
                   "rel": round(rel, 1), "persistence": round(persistence, 1)}


def _size_smallcap(score: float) -> float:
    return 0.05 if score >= 85 else 0.03 if score >= 70 else 0.02 if score >= 55 else 0.0


def _size_infra(score: float) -> float:
    return 0.06 if score >= 85 else 0.04 if score >= 70 else 0.025 if score >= 55 else 0.0


# ---------------------------------------------------------------------------
# Specialist trader definitions
# ---------------------------------------------------------------------------
@dataclass
class Specialist:
    trader_id: str
    niche: str
    best_regime: str
    base_weight: float
    scorer: Any
    sizer: Any

    def current_picks(self, series: Dict[str, List[Any]],
                      mcaps: Optional[Dict[str, float]] = None,
                      min_score: float = 55.0, top_k: int = 8
                      ) -> List[Dict[str, Any]]:
        picks = []
        for tkr, pts in series.items():
            if self.trader_id == "SMALL_CAP_CATALYST_HUNTER":
                score, dims = self.scorer(pts, (mcaps or {}).get(tkr))
            else:
                score, dims = self.scorer(tkr, pts)
            if score >= min_score:
                picks.append({"ticker": tkr, "score": score,
                              "suggested_size": self.sizer(score), "dims": dims})
        picks.sort(key=lambda x: x["score"], reverse=True)
        return picks[:top_k]


SMALL_CAP_CATALYST_HUNTER = Specialist(
    trader_id="SMALL_CAP_CATALYST_HUNTER", niche="small_cap_catalyst",
    best_regime="PARADIGM_BREAKTHROUGH", base_weight=0.10,
    scorer=small_cap_catalyst_score, sizer=_size_smallcap)

POWER_AI_INFRA_TRADER = Specialist(
    trader_id="POWER_AI_INFRA_TRADER", niche="ai_power_infra",
    best_regime="PARADIGM_BREAKTHROUGH", base_weight=0.12,
    scorer=power_ai_infra_score, sizer=_size_infra)

SPECIALISTS: List[Specialist] = [SMALL_CAP_CATALYST_HUNTER, POWER_AI_INFRA_TRADER]


def specialist_picks(series: Dict[str, List[Any]],
                     mcaps: Optional[Dict[str, float]] = None
                     ) -> Dict[str, List[Dict[str, Any]]]:
    """{trader_id: [ranked picks]} for all Phase-1 specialists."""
    return {s.trader_id: s.current_picks(series, mcaps) for s in SPECIALISTS}


# ---------------------------------------------------------------------------
# Demo -- live picks on the real universe
# ---------------------------------------------------------------------------
def _demo() -> int:
    import json
    print("=" * 72)
    print("specialist_traders self-test (Phase 1; live universe + Finviz mcaps)")
    print("=" * 72)
    from simulation.universe_competition import build_universe
    from simulation.backtest_runner import load_pit_series
    uni = build_universe(max_names=160)
    series = {t: pts for t, pts in load_pit_series(uni["tickers"]).items() if pts}
    mcaps = {}
    try:
        from simulation.finviz_data import get_market_caps
        mcaps = get_market_caps(list(series.keys()))
    except Exception as e:
        print(f"(market caps unavailable: {e})")
    print(f"universe priced: {len(series)}, market caps resolved: {len(mcaps)}\n")
    for s in SPECIALISTS:
        picks = s.current_picks(series, mcaps)
        print(f"--- {s.trader_id} (best regime {s.best_regime}, base {s.base_weight}) ---")
        for p in picks:
            extra = (f"mcap={p['dims'].get('mcap_bn')}B" if "mcap_bn" in p["dims"]
                     else f"mom3m={p['dims'].get('mom_3m')}")
            print(f"   {p['ticker']:<6} score={p['score']:>5} "
                  f"size={p['suggested_size']*100:.1f}%  ({extra})")
        if not picks:
            print("   (no qualifying picks today)")
        print()
    return 0


if __name__ == "__main__":
    raise SystemExit(_demo())
