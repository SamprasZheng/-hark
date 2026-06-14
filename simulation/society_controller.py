#!/usr/bin/env python3
"""
Trading Society -- Unified Controller (grok3.md TradingSocietyController)

PPST Declaration (this PROGRAM):
- PROJECT: Trading Society
- PROGRAM: simulation/society_controller.py
- SKILL:   one read-only entry point that composes the macro / regime / systemic-risk
           layers into a single, auditable "society posture": final regime, final
           defensive floor, combined trader tilt, and the shorting permission.
- TARGET:  Implement grok3.md's unified controller so the macro composite
           (macro_risk.py), the regime guardrail (regime_filter.py), and the
           multi-type systemic-risk / black-swan layer (systemic_risk.py) are read
           ONCE and reconciled deterministically:
             1. macro composite (0-100) + real Buffett Indicator (PIT via ALFRED)
             2. regime guardrail -> HARD_DEFENSE / PARADIGM_BREAKTHROUGH / MEAN_REVERSION
             3. systemic-risk typology -> LIQUIDITY_CRISIS / VALUATION_BUBBLE / ...
             4. combine: final_regime (acute systemic stress can FORCE HARD_DEFENSE),
                defensive_floor = max(regime floor, systemic step), combined tilt =
                regime tilt x systemic tilt, shorts permitted only in a bear regime.

Governance (CLAUDE.md §2, §10): READ-ONLY, RECOMMEND-ONLY. Composes existing
veto-class guardrails; it does NOT place orders, does NOT write outputs/picks-* or
wiki/05_recommendations/*, and does NOT replace the canonical 10-signal pipeline or
the Risk-Officer gate. PIT throughout (vintage=as_of). never-raise on every layer.

Run: python simulation/society_controller.py   (live posture; portfolio optional)
"""

from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from simulation import regime_filter as RF
from simulation import systemic_risk as SR

# Systemic typologies whose HIGH reading forces a defensive regime override.
_FORCE_DEFENSE_ON_HIGH = {SR.LIQUIDITY_CRISIS, SR.SYSTEMIC_RISK,
                          SR.GEOPOLITICAL_SHOCK, SR.INFLATION_SHOCK}


@dataclass
class SocietyPosture:
    as_of: Optional[str]
    is_point_in_time: bool
    macro: Dict[str, Any]
    regime: Dict[str, Any]
    systemic: Dict[str, Any]
    final_regime: str
    defensive_floor: float
    combined_trader_tilt: Dict[str, float]
    shorts_allowed: bool
    overrides: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "as_of": self.as_of,
            "is_point_in_time": self.is_point_in_time,
            "macro": {"score_0_100": self.macro.get("score_0_100"),
                      "posture": self.macro.get("posture"),
                      "buffett_indicator": self.macro.get("inputs", {}).get("buffett_indicator"),
                      "n_live_series": self.macro.get("n_live_series")},
            "regime": self.regime,
            "systemic": self.systemic,
            "final_regime": self.final_regime,
            "defensive_floor": round(self.defensive_floor, 3),
            "shorts_allowed": self.shorts_allowed,
            "overrides": self.overrides,
            "combined_trader_tilt": {k: round(v, 3)
                                     for k, v in self.combined_trader_tilt.items()},
            "source": "grok3.md TradingSocietyController (macro x regime x systemic)",
            "note": "Read-only, recommend-only. Veto-class composition; capital use "
                    "needs the human + Risk-Officer gate (CLAUDE.md §10).",
        }


def _combine_tilts(regime_tilt: Dict[str, float],
                   systemic_tilt: Dict[str, float]) -> Dict[str, float]:
    keys = set(regime_tilt) | set(systemic_tilt)
    return {k: regime_tilt.get(k, 1.0) * systemic_tilt.get(k, 1.0) for k in keys}


class TradingSocietyController:
    """Composes the macro / regime / systemic-risk layers into one posture."""

    def assess(self, as_of: Optional[str] = None, pit: bool = True,
               gpr_index: Optional[float] = None,
               margin_debt_yoy: Optional[float] = None,
               capex: Optional[Dict[str, Any]] = None) -> SocietyPosture:
        # 1. macro composite (single FRED pull, reused by the layers below)
        from simulation.macro_risk import macro_risk_score
        macro = macro_risk_score(as_of=as_of, pit=pit)

        # 2. regime guardrail
        regime_v = RF.from_live(macro=macro, capex=capex)
        regime = regime_v.to_dict()

        # 3. systemic-risk typology (reuses macro; adds IG OAS / TED / CPI / WTI)
        sys_v = SR.from_live(as_of=as_of, pit=pit, macro=macro,
                             gpr_index=gpr_index, margin_debt_yoy=margin_debt_yoy)
        systemic = sys_v.to_dict()

        # 4. combine
        overrides: List[str] = []
        final_regime = regime_v.regime
        if (sys_v.risk_level == "HIGH" and sys_v.risk_type in _FORCE_DEFENSE_ON_HIGH
                and final_regime != RF.HARD_DEFENSE):
            final_regime = RF.HARD_DEFENSE
            overrides.append(f"systemic {sys_v.risk_type} (HIGH) -> HARD_DEFENSE")

        defensive_floor = max(regime_v.defensive_floor, sys_v.defensive_floor_step)
        if sys_v.defensive_floor_step > regime_v.defensive_floor:
            overrides.append(
                f"systemic floor {sys_v.defensive_floor_step:.0%} > regime floor "
                f"{regime_v.defensive_floor:.0%}")

        combined = _combine_tilts(RF.trader_tilt(final_regime), sys_v.trader_tilt)
        shorts = RF.shorts_allowed(final_regime)

        return SocietyPosture(
            as_of=as_of, is_point_in_time=bool(pit and as_of),
            macro=macro, regime=regime, systemic=systemic,
            final_regime=final_regime, defensive_floor=defensive_floor,
            combined_trader_tilt=combined, shorts_allowed=shorts,
            overrides=overrides)

    def run_portfolio(self, horizon: str = "next_quarter", lookback_days: int = 126,
                      max_names: int = 160) -> Dict[str, Any]:
        """Optional: build the forward portfolio (delegates to portfolio_generator,
        which already applies the regime + systemic overlays internally)."""
        from simulation.portfolio_generator import generate_portfolio
        from simulation.universe_competition import build_universe
        from simulation.backtest_runner import load_pit_series
        uni = build_universe(max_names=max_names)
        series = {t: pts for t, pts in load_pit_series(uni["tickers"]).items() if pts}
        return generate_portfolio(horizon, lookback_days, series, uni)


def _demo() -> int:
    import json
    print("=" * 74)
    print("society_controller self-test -- unified posture (macro x regime x systemic)")
    print("=" * 74)
    ctrl = TradingSocietyController()
    try:
        posture = ctrl.assess()
        d = posture.to_dict()
        # compact print
        print(f"\n  macro: {d['macro']['score_0_100']}/100 ({d['macro']['posture']}, "
              f"BI {d['macro']['buffett_indicator']}, {d['macro']['n_live_series']} live)")
        print(f"  regime: {d['regime']['regime']}  (floor {d['regime']['defensive_floor']})")
        print(f"  systemic: {d['systemic']['risk_type']} ({d['systemic']['risk_level']}, "
              f"score {d['systemic']['score_0_100']})")
        print(f"  -> FINAL regime: {d['final_regime']}  "
              f"defensive_floor: {d['defensive_floor']}  shorts_allowed: {d['shorts_allowed']}")
        if d["overrides"]:
            print(f"     overrides: {d['overrides']}")
        top_tilt = sorted(d["combined_trader_tilt"].items(),
                          key=lambda kv: kv[1], reverse=True)[:5]
        bot_tilt = sorted(d["combined_trader_tilt"].items(),
                          key=lambda kv: kv[1])[:4]
        print(f"     tilt up:   {top_tilt}")
        print(f"     tilt down: {bot_tilt}")
    except Exception as e:
        import traceback
        print(f"  live posture skipped: {e}")
        traceback.print_exc()
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(_demo())
