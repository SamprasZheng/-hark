#!/usr/bin/env python3
"""
Trading Society -- Specialist traders (grok2.md 14-trader roster)

PPST Declaration (this PROGRAM):
- PROJECT: Trading Society
- PROGRAM: simulation/specialist_traders.py
- SKILL:   sector/style/13F-imitation specialist scorecards (0-100) + current picks
- TARGET:  Implement the grok2.md roster specialists. Phase 1: Small Cap Catalyst
           Hunter + Power & AI Infrastructure. Phase 2+: Value & Quality
           Compounders, Nancy Pelosi Tracker, Defense & Geopolitical, Biotech &
           Healthcare, Elon Musk Ecosystem. Each emits a transparent 0-100
           scorecard + position-size suggestion + ranked current picks from real
           lake prices (+ Finviz fundamentals where needed). Recommend-only, no LLM.

All scorers share one signature: score(ticker, pts, ctx) -> (score, dims), where
ctx = {"mcap_bn", "pe", "sector", "industry"} from Finviz (any may be None).

Governance: recommend-only; picks join the society vote (portfolio_generator) under
the regime guardrail + concentration caps + Risk-Officer gate. LONG-BIASED -- these
specialists only go long (the principal's "short only in a confirmed bear" rule is
enforced at the backtest/portfolio layer, not here). Curated lists (Pelosi/Musk)
are Grade-D references from public disclosures, never trade triggers on their own.

Run: python simulation/specialist_traders.py   (live picks on the real universe)
"""

from __future__ import annotations

import statistics
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

# --- sleeves / curated universes ---
AI_INFRA_SLEEVE = ["VRT", "GEV", "ETN", "VST", "CEG", "NRG", "PWR", "TLN", "CRWV",
                   "ANET", "COHR", "CRDO", "AMKR", "UCTT", "ICHR", "ENTG", "KLAC",
                   "ONTO", "FORM", "NVMI", "CAMT"]
DEFENSE_SLEEVE = ["LMT", "NOC", "RTX", "GD", "BA", "LHX", "HII", "KTOS", "AVAV",
                  "HEI", "TDG", "RKLB", "ASTS", "LUNR", "PL", "IRDM", "GSAT"]
BIOTECH_SLEEVE = ["LLY", "UNH", "ISRG", "VRTX", "REGN", "ABBV", "AMGN", "GILD",
                  "HUM", "NVCR", "ARWR", "RXRX", "CRSP", "NTLA", "BEAM", "MRNA", "GH"]
# Curated public-disclosure congressional tech/quality holdings (Grade-D).
PELOSI_HOLDINGS = ["NVDA", "AAPL", "MSFT", "GOOGL", "AVGO", "AMZN", "CRM", "NFLX",
                   "PANW", "CRWD", "VST", "TEM", "PLTR"]
# Elon Musk ecosystem: Tesla + public SpaceX proxies + adjacent.
MUSK_ECO = ["TSLA", "RKLB", "DXYZ", "PLTR", "NVDA"]

SMALLCAP_MAX_BN = 12.0
VALUE_MIN_MCAP_BN = 20.0   # value/quality = large-cap compounders


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
# Scorecards (0-100) -- unified signature score(ticker, pts, ctx)
# ---------------------------------------------------------------------------
def small_cap_catalyst_score(ticker, pts, ctx) -> Tuple[float, Dict[str, float]]:
    mcap = (ctx or {}).get("mcap_bn")
    if mcap is None or mcap > SMALLCAP_MAX_BN or len(pts) < 63:
        return 0.0, {}
    closes = [p.close for p in pts]
    mom_1m, mom_3m = _ret(pts, 21) or 0.0, _ret(pts, 63) or 0.0
    trail_high = max(closes[-120:]) if len(closes) >= 120 else max(closes)
    dist = closes[-1] / trail_high - 1.0 if trail_high > 0 else 0.0
    cap = _clip((SMALLCAP_MAX_BN - mcap) / (SMALLCAP_MAX_BN - 0.3)) * 25
    low_base = _clip(-dist / 0.45) * 25
    breakout = _clip((mom_1m + 0.03) / 0.25) * 30
    accel = _clip((mom_1m - mom_3m / 3.0 + 0.02) / 0.15) * 20
    return round(cap + low_base + breakout + accel, 1), {"mcap_bn": mcap,
            "mom_1m": round(mom_1m, 3), "dist_from_high": round(dist, 3)}


def power_ai_infra_score(ticker, pts, ctx) -> Tuple[float, Dict[str, float]]:
    if ticker not in AI_INFRA_SLEEVE or len(pts) < 63:
        return 0.0, {}
    closes = [p.close for p in pts]
    mom_3m, mom_1m = _ret(pts, 63) or 0.0, _ret(pts, 21) or 0.0
    mdd = _max_drawdown(closes[-63:])
    score = (_clip((mom_3m + 0.10) / 0.40) * 40 + _clip((mom_1m + 0.05) / 0.25) * 30
             + _clip(1.0 - abs(mdd) / 0.30) * 30)
    return round(score, 1), {"mom_3m": round(mom_3m, 3), "mom_1m": round(mom_1m, 3)}


def value_quality_score(ticker, pts, ctx) -> Tuple[float, Dict[str, float]]:
    """Large-cap value + quality compounder: cheap P/E + low drawdown + steady
    (not a falling knife)."""
    ctx = ctx or {}
    pe, mcap = ctx.get("pe"), ctx.get("mcap_bn")
    if not pe or pe <= 0 or pe > 60 or not mcap or mcap < VALUE_MIN_MCAP_BN or len(pts) < 126:
        return 0.0, {}
    closes = [p.close for p in pts]
    mom_6m, mom_3m = _ret(pts, 126) or 0.0, _ret(pts, 63) or 0.0
    mdd = _max_drawdown(closes[-126:])
    value = _clip((30.0 - pe) / 22.0) * 40        # PE 8 -> ~1.0, 30 -> 0
    quality = _clip(1.0 - abs(mdd) / 0.30) * 30   # low drawdown = durable
    # steady positive trend, penalize falling knife
    trend = (_clip((mom_6m + 0.05) / 0.30) * 30) if mom_3m > -0.10 else 0.0
    return round(value + quality + trend, 1), {"pe": pe, "mcap_bn": mcap,
            "mom_6m": round(mom_6m, 3), "max_dd_6m": round(mdd, 3)}


def low_vol_score(ticker, pts, ctx) -> Tuple[float, Dict[str, float]]:
    """Low-volatility defender (next phase, grok3.md roster expansion): low realized
    volatility + shallow drawdown + steady (not falling-knife) drift. The anti-
    fragile sleeve that earns its keep when the systemic-risk layer flags stress.
    Works on any priced name with >=126 days -- no ctx gate."""
    if len(pts) < 126:
        return 0.0, {}
    closes = [p.close for p in pts]
    rets = [closes[i] / closes[i - 1] - 1.0
            for i in range(1, len(closes)) if closes[i - 1] > 0]
    if len(rets) < 63:
        return 0.0, {}
    vol = statistics.pstdev(rets[-63:]) * (252 ** 0.5)   # annualized realized vol
    mom_6m = _ret(pts, 126) or 0.0
    mdd = _max_drawdown(closes[-126:])
    lowvol = _clip((0.50 - vol) / 0.35) * 45              # 15% vol -> ~1.0, 50% -> 0
    quality = _clip(1.0 - abs(mdd) / 0.30) * 30          # shallow drawdown = durable
    drift = (_clip((mom_6m + 0.05) / 0.30) * 25) if mom_6m > -0.05 else 0.0
    return round(lowvol + quality + drift, 1), {"ann_vol": round(vol, 3),
            "mom_6m": round(mom_6m, 3), "max_dd_6m": round(mdd, 3)}


def _sleeve_momentum_score(ticker, pts, sleeve) -> Tuple[float, Dict[str, float]]:
    if ticker not in sleeve or len(pts) < 63:
        return 0.0, {}
    closes = [p.close for p in pts]
    mom_3m, mom_1m = _ret(pts, 63) or 0.0, _ret(pts, 21) or 0.0
    mdd = _max_drawdown(closes[-63:])
    score = (_clip((mom_3m + 0.08) / 0.40) * 45 + _clip((mom_1m + 0.04) / 0.22) * 30
             + _clip(1.0 - abs(mdd) / 0.30) * 25)
    return round(score, 1), {"mom_3m": round(mom_3m, 3), "mom_1m": round(mom_1m, 3)}


def defense_geo_score(ticker, pts, ctx):
    return _sleeve_momentum_score(ticker, pts, DEFENSE_SLEEVE)


def biotech_health_score(ticker, pts, ctx):
    return _sleeve_momentum_score(ticker, pts, BIOTECH_SLEEVE)


def pelosi_score(ticker, pts, ctx):
    return _sleeve_momentum_score(ticker, pts, PELOSI_HOLDINGS)


def musk_eco_score(ticker, pts, ctx):
    return _sleeve_momentum_score(ticker, pts, MUSK_ECO)


def _size_smallcap(s): return 0.05 if s >= 85 else 0.03 if s >= 70 else 0.02 if s >= 55 else 0.0
def _size_infra(s):    return 0.06 if s >= 85 else 0.04 if s >= 70 else 0.025 if s >= 55 else 0.0
def _size_value(s):    return 0.06 if s >= 80 else 0.04 if s >= 65 else 0.025 if s >= 50 else 0.0
def _size_sleeve(s):   return 0.05 if s >= 80 else 0.035 if s >= 65 else 0.02 if s >= 55 else 0.0
def _size_lowvol(s):   return 0.06 if s >= 80 else 0.04 if s >= 65 else 0.025 if s >= 50 else 0.0


# ---------------------------------------------------------------------------
@dataclass
class Specialist:
    trader_id: str
    niche: str
    best_regime: str
    base_weight: float
    scorer: Callable
    sizer: Callable
    grade_note: str = ""

    def current_picks(self, series: Dict[str, List[Any]],
                      ctx_map: Optional[Dict[str, Dict[str, Any]]] = None,
                      min_score: float = 55.0, top_k: int = 8
                      ) -> List[Dict[str, Any]]:
        ctx_map = ctx_map or {}
        picks = []
        for tkr, pts in series.items():
            score, dims = self.scorer(tkr, pts, ctx_map.get(tkr))
            if score >= min_score:
                picks.append({"ticker": tkr, "score": score,
                              "suggested_size": self.sizer(score), "dims": dims})
        picks.sort(key=lambda x: x["score"], reverse=True)
        return picks[:top_k]


SMALL_CAP_CATALYST_HUNTER = Specialist("SMALL_CAP_CATALYST_HUNTER", "small_cap_catalyst",
    "PARADIGM_BREAKTHROUGH", 0.10, small_cap_catalyst_score, _size_smallcap)
POWER_AI_INFRA_TRADER = Specialist("POWER_AI_INFRA_TRADER", "ai_power_infra",
    "PARADIGM_BREAKTHROUGH", 0.12, power_ai_infra_score, _size_infra)
VALUE_QUALITY_COMPOUNDER = Specialist("VALUE_QUALITY_COMPOUNDER", "value_quality",
    "HARD_DEFENSE", 0.10, value_quality_score, _size_value)
DEFENSE_GEO_ANALYST = Specialist("DEFENSE_GEO_ANALYST", "defense_geopolitical",
    "HARD_DEFENSE", 0.08, defense_geo_score, _size_sleeve)
BIOTECH_HEALTH_SPECIALIST = Specialist("BIOTECH_HEALTH_SPECIALIST", "biotech_health",
    "MEAN_REVERSION", 0.08, biotech_health_score, _size_sleeve)
PELOSI_TRACKER = Specialist("PELOSI_TRACKER", "congress_13f",
    "PARADIGM_BREAKTHROUGH", 0.08, pelosi_score, _size_sleeve,
    grade_note="Grade-D curated public-disclosure holdings; momentum-gated.")
MUSK_ECOSYSTEM = Specialist("MUSK_ECOSYSTEM", "musk_ecosystem",
    "PARADIGM_BREAKTHROUGH", 0.07, musk_eco_score, _size_sleeve,
    grade_note="Grade-D curated ecosystem list.")
LOW_VOL_DEFENDER = Specialist("LOW_VOL_DEFENDER", "low_volatility",
    "HARD_DEFENSE", 0.08, low_vol_score, _size_lowvol,
    grade_note="Next-phase (grok3) defensive sleeve; low realized vol + shallow DD.")

SPECIALISTS: List[Specialist] = [
    SMALL_CAP_CATALYST_HUNTER, POWER_AI_INFRA_TRADER, VALUE_QUALITY_COMPOUNDER,
    DEFENSE_GEO_ANALYST, BIOTECH_HEALTH_SPECIALIST, PELOSI_TRACKER, MUSK_ECOSYSTEM,
    LOW_VOL_DEFENDER,
]


def specialist_picks(series: Dict[str, List[Any]],
                     ctx_map: Optional[Dict[str, Dict[str, Any]]] = None
                     ) -> Dict[str, List[Dict[str, Any]]]:
    return {s.trader_id: s.current_picks(series, ctx_map) for s in SPECIALISTS}


def _demo() -> int:
    print("=" * 72)
    print("specialist_traders self-test (live universe + Finviz fundamentals)")
    print("=" * 72)
    from simulation.universe_competition import build_universe
    from simulation.backtest_runner import load_pit_series
    uni = build_universe(max_names=170)
    series = {t: pts for t, pts in load_pit_series(uni["tickers"]).items() if pts}
    ctx_map = {}
    try:
        from simulation.finviz_data import get_fundamentals
        ctx_map = get_fundamentals(list(series.keys()))
    except Exception as e:
        print(f"(fundamentals unavailable: {e})")
    print(f"universe priced: {len(series)}, fundamentals: {len(ctx_map)}\n")
    for s in SPECIALISTS:
        picks = s.current_picks(series, ctx_map)
        tag = f" [{s.grade_note}]" if s.grade_note else ""
        print(f"--- {s.trader_id} (best {s.best_regime}, base {s.base_weight}){tag}")
        if not picks:
            print("   (no qualifying picks today)")
        for p in picks[:6]:
            print(f"   {p['ticker']:<6} score={p['score']:>5} size={p['suggested_size']*100:.1f}%")
        print()
    return 0


if __name__ == "__main__":
    raise SystemExit(_demo())
