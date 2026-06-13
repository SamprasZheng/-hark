#!/usr/bin/env python3
"""
Trading Society -- Macro Sentinel / data provider (Step 2)

PPST Declaration (this PROGRAM):
- PROJECT: Trading Society
- PROGRAM: simulation/macro_data_provider.py
- SKILL:   regime_detector inputs -> MarketContext for the persona debate
- TARGET:  Provide the macro inputs the persona roster needs (Buffett Indicator,
           Dalio bubble flag, 10Y/2Y/real yield, net-liquidity proxy, TW/US
           valuation spread) as a MarketContext. Synthetic by default (offline,
           green); optional FRED wiring (never-raise -> synthetic fallback).

PIT honesty (CLAUDE.md sec.2 / docs/LLM-BACKTEST-PROTOCOL.md):
- The synthetic snapshot is a *current-state* convenience for wiring/tests, NOT a
  point-in-time historical series. A backtest that replays the persona debate
  historically MUST supply vintage-honest macro (FRED ALFRED vintages), never the
  live "latest" value. This is flagged in `is_point_in_time` on every snapshot.
- The live FRED path returns the latest print (vintage=live); do not feed it into
  an as_of-earlier analysis.

Run: python simulation/macro_data_provider.py   (synthetic snapshots demo)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

try:
    from simulation.personas import MarketContext, BUFFETT_INDICATOR_HIGH
except Exception:  # pragma: no cover
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from simulation.personas import MarketContext, BUFFETT_INDICATOR_HIGH

# FRED series ids for the optional live path.
FRED_SERIES = {
    "ten_year": "DGS10",
    "two_year": "DGS2",
    "real_yield": "DFII10",       # 10Y TIPS real yield
    "walcl": "WALCL",             # Fed balance sheet (net liquidity numerator)
    "tga": "WTREGEN",             # Treasury General Account
    "rrp": "RRPONTSYD",           # Overnight reverse repo
}


@dataclass
class MacroSnapshot:
    as_of: str
    buffett_indicator: Optional[float] = None     # market cap / GDP, percent
    dalio_bubble_flag: bool = False
    ten_year: Optional[float] = None              # percent
    two_year: Optional[float] = None              # percent
    real_yield: Optional[float] = None            # percent
    net_liquidity_tn: Optional[float] = None      # WALCL - TGA - RRP, USD trillions
    tw_us_valuation_spread: Optional[float] = None  # TW vs US fwd-PE spread (pts)
    regime_label: str = "unknown"
    source: str = "synthetic"
    is_point_in_time: bool = False

    def to_market_context(self, topic: str = "") -> MarketContext:
        return MarketContext(
            as_of=self.as_of, topic=topic,
            buffett_indicator=self.buffett_indicator,
            dalio_bubble_flag=self.dalio_bubble_flag,
            regime_label=self.regime_label, ten_year_yield=self.ten_year,
            extra={"two_year": self.two_year, "real_yield": self.real_yield,
                   "net_liquidity_tn": self.net_liquidity_tn,
                   "tw_us_valuation_spread": self.tw_us_valuation_spread,
                   "macro_source": self.source,
                   "is_point_in_time": self.is_point_in_time})

    def to_dict(self) -> Dict[str, Any]:
        d = self.__dict__.copy()
        d["high_valuation"] = self.derive_high_valuation()
        return d

    def derive_high_valuation(self) -> bool:
        bi_hi = (self.buffett_indicator is not None
                 and self.buffett_indicator > BUFFETT_INDICATOR_HIGH)
        return bool(bi_hi or self.dalio_bubble_flag)


def _bubble_flag_from(buffett_indicator: Optional[float],
                      net_liquidity_tn: Optional[float],
                      prev_net_liquidity_tn: Optional[float]) -> bool:
    """Simple, transparent rule (not a learned model)."""
    if buffett_indicator is not None and buffett_indicator > 215.0:
        return True
    if (net_liquidity_tn is not None and prev_net_liquidity_tn is not None
            and net_liquidity_tn < prev_net_liquidity_tn):
        # contracting liquidity at already-rich valuations
        if buffett_indicator is not None and buffett_indicator > 190.0:
            return True
    return False


def synthetic_snapshot(as_of: str, stressed: bool = True) -> MacroSnapshot:
    """
    A labeled current-state snapshot for wiring/tests. `stressed=True` reflects
    the 2026 high-valuation backdrop described in the Risk Officer advisory.
    NOT point-in-time historical data.
    """
    if stressed:
        bi = 225.0
        snap = MacroSnapshot(
            as_of=as_of, buffett_indicator=bi, ten_year=4.5, two_year=4.2,
            real_yield=2.0, net_liquidity_tn=5.8, tw_us_valuation_spread=-6.0,
            regime_label="high_valuation", source="synthetic")
    else:
        bi = 150.0
        snap = MacroSnapshot(
            as_of=as_of, buffett_indicator=bi, ten_year=3.8, two_year=3.6,
            real_yield=1.4, net_liquidity_tn=6.4, tw_us_valuation_spread=-2.0,
            regime_label="neutral", source="synthetic")
    snap.dalio_bubble_flag = _bubble_flag_from(bi, snap.net_liquidity_tn,
                                               snap.net_liquidity_tn + 0.1)
    return snap


def fred_snapshot(as_of: str, buffett_indicator: Optional[float] = None,
                  tw_us_valuation_spread: Optional[float] = None) -> MacroSnapshot:
    """
    Optional live path: pull yields + net-liquidity proxy from FRED. Never raises
    -> falls back to a synthetic snapshot if the client/network is unavailable.
    Buffett Indicator + TW/US spread are passed in (no clean free FRED source);
    if omitted, the synthetic stressed value is used.
    """
    try:
        from sharks.data.fred_client import fetch_latest  # type: ignore
    except Exception:
        try:
            from src.sharks.data.fred_client import fetch_latest  # type: ignore
        except Exception:
            base = synthetic_snapshot(as_of, stressed=True)
            base.source = "synthetic(fred-unavailable)"
            return base

    def latest(sid: str) -> Optional[float]:
        try:
            row = fetch_latest(FRED_SERIES[sid])
            return float(row["value"]) if row and row.get("value") is not None else None
        except Exception:
            return None

    ten = latest("ten_year")
    two = latest("two_year")
    real = latest("real_yield")
    walcl = latest("walcl")    # millions USD
    tga = latest("tga")        # billions USD
    rrp = latest("rrp")        # billions USD
    net_liq = None
    if walcl is not None and tga is not None and rrp is not None:
        net_liq = round((walcl / 1e6) - (tga / 1e3) - (rrp / 1e3), 3)  # -> trillions

    bi = buffett_indicator if buffett_indicator is not None else 225.0
    snap = MacroSnapshot(
        as_of=as_of, buffett_indicator=bi, ten_year=ten, two_year=two,
        real_yield=real, net_liquidity_tn=net_liq,
        tw_us_valuation_spread=tw_us_valuation_spread,
        regime_label="high_valuation" if bi > BUFFETT_INDICATOR_HIGH else "neutral",
        source="fred(live, vintage=live; NOT pit)", is_point_in_time=False)
    snap.dalio_bubble_flag = _bubble_flag_from(bi, net_liq, None)
    return snap


def get_market_context(as_of: str, topic: str = "", use_fred: bool = False,
                       stressed: bool = True) -> MarketContext:
    """Single entry point used by the persona debate / orchestrator."""
    snap = fred_snapshot(as_of) if use_fred else synthetic_snapshot(as_of, stressed)
    return snap.to_market_context(topic)


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------
def _demo() -> int:
    import json
    print("=" * 72)
    print("macro_data_provider self-test (synthetic; not point-in-time)")
    print("=" * 72)
    for stressed in (True, False):
        snap = synthetic_snapshot("2026-06-13", stressed=stressed)
        print(f"\n  stressed={stressed}:")
        print(json.dumps(snap.to_dict(), indent=2, ensure_ascii=False))
    print("\nNote: synthetic current-state only. Historical replay must use FRED "
          "ALFRED vintages (is_point_in_time stays false here).")
    return 0


if __name__ == "__main__":
    raise SystemExit(_demo())
