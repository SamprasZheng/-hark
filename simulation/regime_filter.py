#!/usr/bin/env python3
"""
Trading Society -- Regime Filter & hard guardrails (grok2.md 溶入憲法)

PPST Declaration (this PROGRAM):
- PROJECT: Trading Society
- PROGRAM: simulation/regime_filter.py
- SKILL:   century-regime classification -> capital-impacting hard guardrails
- TARGET:  Implement grok2.md's evaluate_market_regime() + the Regime_Filter hard
           cases as machine-readable, falsifiable guardrails:
             HARD_DEFENSE          -> small-cap allocation cap = 0, defensive floor,
                                      strict winsorization (1929/1987/2008/2020/2018Q4/2022)
             PARADIGM_BREAKTHROUGH -> Momentum Decoupling Lock + reverse-short lock on
                                      AI leaders (RCA/CSCO/NVDA analog; anti-Gamma-squeeze)
             MEAN_REVERSION        -> traditional oversold play
           No LLM. Recommend-only. These are veto-class risk rules (Risk-Officer
           aligned, CLAUDE.md sec.10).

The 3 Ground-Truth invariants (grok2.md, codified):
  1. Small-cap melt-ups are asymmetric "right-to-zero" -> strict dynamic truncation.
  2. Sovereign/geopolitical paradigm faults break all backtests -> immunity guardrail.
  3. Paradigm squeeze -> block mean-reversion shorts on leaders until TD-9 / Sharpe
     haircut decays (Momentum Decoupling Lock).

Run: python simulation/regime_filter.py   (synthetic demo of all 3 regimes + live)
"""

from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

HARD_DEFENSE = "HARD_DEFENSE"
PARADIGM_BREAKTHROUGH = "PARADIGM_BREAKTHROUGH"
MEAN_REVERSION = "MEAN_REVERSION"

# AI leaders that get a reverse-short lock during a paradigm-breakthrough regime
# (anti-Gamma-squeeze, account survival -- grok2.md TD-9 / Momentum Decoupling Lock).
LEADER_SHORT_LOCK = ["NVDA", "SMCI", "AVGO", "ASML", "TSM", "ORCL", "MSFT", "META"]


# grok2.md regime -> trader weight tilt: which traders to up/down-weight per regime.
# Multipliers applied on top of fitness + champion-boost weights, then renormalized.
REGIME_TRADER_TILT: Dict[str, Dict[str, float]] = {
    # Liquidity shock: lean hard on the defensive trader; punish chasing. Small
    # caps die in shocks (right-to-zero invariant) -> SCCH cut hard.
    HARD_DEFENSE: {"RISK_OFFICER": 2.5, "MEAN_REVERSION": 1.1, "REVERSION_FAST": 1.0,
                   "MOMENTUM_SWING": 0.4, "MOMENTUM_FAST": 0.3, "TREND_RIDER": 0.4,
                   "BREAKOUT_HUNTER": 0.3, "SMALL_CAP_CATALYST_HUNTER": 0.2,
                   "POWER_AI_INFRA_TRADER": 0.5},
    # Paradigm breakthrough: ride leaders + AI infra + small-cap catalysts.
    PARADIGM_BREAKTHROUGH: {"TREND_RIDER": 1.6, "MOMENTUM_SWING": 1.5,
                            "BREAKOUT_HUNTER": 1.5, "MOMENTUM_FAST": 1.3,
                            "MEAN_REVERSION": 0.5, "REVERSION_FAST": 0.5,
                            "RISK_OFFICER": 0.6, "SMALL_CAP_CATALYST_HUNTER": 1.6,
                            "POWER_AI_INFRA_TRADER": 1.7},
    # Mean reversion: favor the faders; specialists neutral-ish.
    MEAN_REVERSION: {"MEAN_REVERSION": 1.4, "REVERSION_FAST": 1.3,
                     "MOMENTUM_SWING": 1.0, "MOMENTUM_FAST": 1.0, "TREND_RIDER": 0.9,
                     "BREAKOUT_HUNTER": 0.9, "RISK_OFFICER": 1.0,
                     "SMALL_CAP_CATALYST_HUNTER": 0.8, "POWER_AI_INFRA_TRADER": 1.0},
}


def trader_tilt(regime: str) -> Dict[str, float]:
    return dict(REGIME_TRADER_TILT.get(regime, {}))


@dataclass
class RegimeVerdict:
    regime: str
    smallcap_allocation_cap: float       # 0.0 in HARD_DEFENSE
    defensive_floor: float               # forced minimum defensive weight
    winsorization: str                   # "strict" | "normal"
    momentum_decoupling_lock: bool       # block reverse shorts on leaders
    short_lock_names: List[str]          # leaders that may not be shorted
    rationale: str
    inputs: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "regime": self.regime,
            "smallcap_allocation_cap": self.smallcap_allocation_cap,
            "defensive_floor": self.defensive_floor,
            "winsorization": self.winsorization,
            "momentum_decoupling_lock": self.momentum_decoupling_lock,
            "short_lock_names": self.short_lock_names,
            "rationale": self.rationale,
            "inputs": self.inputs,
            "source": "grok2.md evaluate_market_regime + Regime_Filter hard cases",
            "note": "Veto-class guardrails. Recommend-only; capital use needs the "
                    "Risk-Officer gate (CLAUDE.md sec.10).",
        }


def evaluate_market_regime(
    net_liquidity_delta: float,
    btc_gold_ratio: float,
    capex_growth: float,
    macro_score: float = 50.0,
    buffett_indicator: Optional[float] = None,
) -> RegimeVerdict:
    """
    grok2.md core classifier + hard cases.

    - net_liquidity_delta: weekly change in Fed net liquidity (trillions; <0 = draining).
    - btc_gold_ratio: BTC vs gold RELATIVE strength (1.0 = equal; <1 gold winning =
      risk-off; >1.05 btc winning = risk appetite). [raw price ratio is incoherent,
      so we adapt grok2.md's thresholds to relative strength.]
    - capex_growth: AI-capex sleeve YoY growth (fraction; >0.25 = strong expansion).
    """
    inputs = {"net_liquidity_delta": net_liquidity_delta,
              "btc_gold_ratio": round(btc_gold_ratio, 3),
              "capex_growth": capex_growth, "macro_score": macro_score,
              "buffett_indicator": buffett_indicator}

    high_val = bool(buffett_indicator is not None and buffett_indicator > 200)
    val_floor = 0.35 if high_val else 0.20  # CLAUDE sec.10 high-valuation floor

    # HARD_DEFENSE: liquidity draining AND gold winning -> 1929/2008/2020/2018Q4 analog
    if net_liquidity_delta < 0 and btc_gold_ratio < 1.0:
        return RegimeVerdict(
            regime=HARD_DEFENSE, smallcap_allocation_cap=0.0,
            defensive_floor=max(0.60, val_floor), winsorization="strict",
            momentum_decoupling_lock=False, short_lock_names=[],
            rationale="Net liquidity draining + gold outperforming BTC -> liquidity "
                      "shock regime. Small-cap longs hard-capped at 0; force defense; "
                      "strict winsorization (small-cap right-to-zero invariant).",
            inputs=inputs)

    # PARADIGM_BREAKTHROUGH: strong capex AND btc strongly winning -> 1999/2024-26 analog
    if capex_growth > 0.25 and btc_gold_ratio > 1.5:
        return RegimeVerdict(
            regime=PARADIGM_BREAKTHROUGH, smallcap_allocation_cap=0.50,
            defensive_floor=val_floor, winsorization="strict",
            momentum_decoupling_lock=True, short_lock_names=list(LEADER_SHORT_LOCK),
            rationale="Capex breakthrough + risk appetite -> AI paradigm regime. "
                      "Momentum Decoupling Lock ON: block reverse shorts on leaders "
                      "(anti-Gamma-squeeze). Long AI hardware/digital; small-cap "
                      "momentum still strictly winsorized.",
            inputs=inputs)

    # MEAN_REVERSION: traditional oversold play (e.g. INTC bounce)
    return RegimeVerdict(
        regime=MEAN_REVERSION, smallcap_allocation_cap=0.25,
        defensive_floor=val_floor, winsorization="strict" if high_val else "normal",
        momentum_decoupling_lock=False, short_lock_names=[],
        rationale="No liquidity shock, no breakthrough crowding -> traditional "
                  "mean-reversion regime; standard caps; valuation floor applies.",
        inputs=inputs)


# ---------------------------------------------------------------------------
# Live input gathering (real data; never-raise -> conservative defaults)
# ---------------------------------------------------------------------------
def _btc_gold_ratio() -> float:
    """BTC vs gold 3-month relative strength. BTC from FRED, gold from lake (GLD)."""
    btc_now = btc_prev = gold_now = gold_prev = None
    try:
        from simulation.macro_risk import _fetch_series
        btc = _fetch_series("CBBTCUSD", start="2026-01-01", vintage=None)
        if len(btc) >= 64:
            btc_now, btc_prev = btc[-1]["value"], btc[-64]["value"]
    except Exception:
        pass
    try:
        from simulation.backtest_runner import load_pit_series
        s = load_pit_series(["GLD"]).get("GLD", [])
        if len(s) >= 64:
            gold_now, gold_prev = s[-1].close, s[-64].close
    except Exception:
        pass
    if btc_now and btc_prev and gold_now and gold_prev and btc_prev > 0 and gold_prev > 0:
        btc_ret = btc_now / btc_prev
        gold_ret = gold_now / gold_prev
        return btc_ret / gold_ret if gold_ret > 0 else 1.0
    return 1.0  # neutral default when data missing


def from_live(macro: Optional[Dict[str, Any]] = None,
              capex: Optional[Dict[str, Any]] = None) -> RegimeVerdict:
    """Gather real inputs and classify. macro/capex may be passed in (from the
    portfolio generator) to avoid duplicate fetches."""
    if macro is None:
        from simulation.macro_risk import macro_risk_score
        macro = macro_risk_score()
    net_liq = macro.get("inputs", {}).get("net_liq_delta")
    if net_liq is None:
        net_liq = -0.05  # conservative: assume mild drain if unknown
    bi = macro.get("inputs", {}).get("buffett_indicator") or macro.get("buffett_indicator")
    capex_growth = 0.0
    if capex is not None:
        capex_growth = capex.get("median_growth_yoy")
        if capex_growth is None:  # proxy path reports momentum, not growth
            capex_growth = capex.get("proxy_avg_3m_momentum", 0.0) * 2  # rough scale
    return evaluate_market_regime(
        net_liquidity_delta=net_liq, btc_gold_ratio=_btc_gold_ratio(),
        capex_growth=capex_growth or 0.0,
        macro_score=macro.get("score_0_100", 50.0), buffett_indicator=bi)


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------
def _demo() -> int:
    import json
    print("=" * 72)
    print("regime_filter self-test (3 synthetic regimes + live)")
    print("=" * 72)
    cases = [
        ("liquidity shock", dict(net_liquidity_delta=-0.2, btc_gold_ratio=0.85,
                                 capex_growth=0.05, buffett_indicator=218.5)),
        ("AI breakthrough", dict(net_liquidity_delta=0.05, btc_gold_ratio=1.8,
                                 capex_growth=0.35, buffett_indicator=218.5)),
        ("calm tape", dict(net_liquidity_delta=0.02, btc_gold_ratio=1.05,
                           capex_growth=0.10, buffett_indicator=218.5)),
    ]
    for name, kw in cases:
        v = evaluate_market_regime(**kw)
        print(f"\n  [{name}] -> {v.regime}")
        print(f"    smallcap_cap={v.smallcap_allocation_cap} "
              f"defensive_floor={v.defensive_floor} winsor={v.winsorization} "
              f"mom_decoupling_lock={v.momentum_decoupling_lock}")
        if v.short_lock_names:
            print(f"    short-locked leaders: {v.short_lock_names[:6]}")

    print("\n  [live]")
    try:
        v = from_live()
        print(json.dumps(v.to_dict(), indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"    live classification skipped: {e}")
    return 0


if __name__ == "__main__":
    raise SystemExit(_demo())
