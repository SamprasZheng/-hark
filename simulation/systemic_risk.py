#!/usr/bin/env python3
"""
Trading Society -- Systemic-risk / black-swan-rhino layer (grok3.md 溶入憲法)

PPST Declaration (this PROGRAM):
- PROJECT: Trading Society
- PROGRAM: simulation/systemic_risk.py
- SKILL:   multi-type systemic-risk classifier -> risk_type + risk_level + a 0-100
           systemic score + a recommended defensive-floor step-up + a per-risk-type
           trader-weight tilt.
- TARGET:  Implement grok3.md's `classify_systemic_risk` / multi-type black-swan
           framework. The single HARD_DEFENSE regime over-collapses every crisis
           into "hold cash"; grok3 asks for a *typology* so different black swans
           get different octopus-legs (章魚腳). From REAL FRED inputs (HY OAS,
           IG OAS, TED/funding-stress, VIX, Buffett Indicator, M2 YoY, core-CPI YoY,
           10Y yield, WTI YoY) classify the active typology:
             LIQUIDITY_CRISIS   (2008/2020)  -> cash + cut leverage, Risk-Officer up
             VALUATION_BUBBLE   (2000)       -> Value/Quality up, momentum down
             GEOPOLITICAL_SHOCK (2022 RU/UA) -> Defense/Energy up, small-cap down
             INFLATION_SHOCK    (1970s/2022) -> Energy/Value up, long-duration growth down
             SYSTEMIC_RISK      (mixed)      -> broad de-risk
             NORMAL                          -> defer to the base regime

Governance (CLAUDE.md §2, §10):
- VETO-CLASS guardrail, Risk-Officer aligned. RECOMMEND-ONLY -- never writes
  outputs/picks-* or wiki/05_recommendations/*; capital use needs the human +
  Risk-Officer gate.
- POINT-IN-TIME: every FRED read takes ALFRED `vintage_date=as_of`. NEVER-RAISE:
  each fetch degrades to a flagged fallback, so a missing series lowers coverage
  rather than silently biasing the verdict.
- NO FABRICATION: GPR (geopolitical-risk index) and margin-debt have no clean free
  FRED series -> they are OPTIONAL Grade-D inputs (`None` when unavailable, and that
  detection branch simply does not fire). They never size a position on their own.

Score convention: 0..100, HIGHER = more systemic stress (more defense warranted).

Run: python simulation/systemic_risk.py   (synthetic typology cases + live)
"""

from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

# --- risk typology (grok3.md) ---
LIQUIDITY_CRISIS = "LIQUIDITY_CRISIS"
VALUATION_BUBBLE = "VALUATION_BUBBLE"
GEOPOLITICAL_SHOCK = "GEOPOLITICAL_SHOCK"
INFLATION_SHOCK = "INFLATION_SHOCK"
SYSTEMIC_RISK = "SYSTEMIC_RISK"
NORMAL = "NORMAL"

RISK_TYPES = [LIQUIDITY_CRISIS, VALUATION_BUBBLE, GEOPOLITICAL_SHOCK,
              INFLATION_SHOCK, SYSTEMIC_RISK, NORMAL]

# Extra FRED series beyond macro_risk's core set.
FRED_EXTRA = {
    "ig_oas": "BAMLC0A0CM",      # ICE BofA US Corporate (IG) OAS, %
    "ted": "TEDRATE",            # TED spread, % (discontinued 2022-01 -> usually None for recent)
    "core_cpi": "CPILFESL",      # core CPI index (YoY computed)
    "wti": "DCOILWTICO",         # WTI crude, $ (YoY computed -> energy stress)
}

# Recommended forced defensive-floor by typology (grok3.md octopus-leg table).
DEFENSIVE_FLOOR_BY_TYPE: Dict[str, float] = {
    LIQUIDITY_CRISIS: 0.50,
    VALUATION_BUBBLE: 0.40,
    GEOPOLITICAL_SHOCK: 0.40,
    INFLATION_SHOCK: 0.35,
    SYSTEMIC_RISK: 0.40,
    NORMAL: 0.0,            # 0 = defer to the base-regime floor (no step-up)
}

# Per-risk-type trader-weight tilt (multipliers on top of fitness/champion weights,
# applied AFTER the regime tilt; trader IDs match regime_filter.REGIME_TRADER_TILT
# + the next-phase additions LOW_VOL_DEFENDER / STAT_ARB_PAIRS).
SYSTEMIC_TRADER_TILT: Dict[str, Dict[str, float]] = {
    LIQUIDITY_CRISIS: {
        "RISK_OFFICER": 2.0, "VALUE_QUALITY_COMPOUNDER": 1.5,
        "DEFENSE_GEO_ANALYST": 1.3, "LOW_VOL_DEFENDER": 1.6,
        "SMALL_CAP_CATALYST_HUNTER": 0.3, "MOMENTUM_FAST": 0.3,
        "MOMENTUM_SWING": 0.4, "BREAKOUT_HUNTER": 0.3, "TREND_RIDER": 0.4,
        "MUSK_ECOSYSTEM": 0.3, "PELOSI_TRACKER": 0.5,
    },
    VALUATION_BUBBLE: {
        "VALUE_QUALITY_COMPOUNDER": 1.6, "LOW_VOL_DEFENDER": 1.4,
        "RISK_OFFICER": 1.3, "STAT_ARB_PAIRS": 1.2,
        "MOMENTUM_FAST": 0.6, "MOMENTUM_SWING": 0.6, "BREAKOUT_HUNTER": 0.6,
        "TREND_RIDER": 0.7, "MUSK_ECOSYSTEM": 0.5, "SMALL_CAP_CATALYST_HUNTER": 0.6,
    },
    GEOPOLITICAL_SHOCK: {
        "DEFENSE_GEO_ANALYST": 1.8, "VALUE_QUALITY_COMPOUNDER": 1.2,
        "RISK_OFFICER": 1.3, "LOW_VOL_DEFENDER": 1.3,
        "SMALL_CAP_CATALYST_HUNTER": 0.5, "MUSK_ECOSYSTEM": 0.6,
        "BREAKOUT_HUNTER": 0.7, "PELOSI_TRACKER": 0.7,
    },
    INFLATION_SHOCK: {
        "VALUE_QUALITY_COMPOUNDER": 1.5, "DEFENSE_GEO_ANALYST": 1.2,
        "RISK_OFFICER": 1.2, "LOW_VOL_DEFENDER": 1.2,
        "MOMENTUM_FAST": 0.7, "BREAKOUT_HUNTER": 0.7, "MUSK_ECOSYSTEM": 0.6,
        "SMALL_CAP_CATALYST_HUNTER": 0.7,
    },
    SYSTEMIC_RISK: {
        "RISK_OFFICER": 1.6, "VALUE_QUALITY_COMPOUNDER": 1.3,
        "LOW_VOL_DEFENDER": 1.4, "DEFENSE_GEO_ANALYST": 1.2,
        "SMALL_CAP_CATALYST_HUNTER": 0.5, "MOMENTUM_FAST": 0.6,
        "BREAKOUT_HUNTER": 0.6, "MUSK_ECOSYSTEM": 0.6,
    },
    NORMAL: {},
}


def _clip(x: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, x))


@dataclass
class SystemicVerdict:
    risk_type: str
    risk_level: str               # LOW | MEDIUM | HIGH
    score_0_100: float
    defensive_floor_step: float   # forced minimum defensive weight for this type (0 = none)
    trader_tilt: Dict[str, float]
    inputs: Dict[str, Optional[float]]
    sources: Dict[str, str]
    rationale: str
    is_point_in_time: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "risk_type": self.risk_type,
            "risk_level": self.risk_level,
            "score_0_100": round(self.score_0_100, 1),
            "defensive_floor_step": self.defensive_floor_step,
            "trader_tilt": self.trader_tilt,
            "inputs": self.inputs,
            "sources": self.sources,
            "rationale": self.rationale,
            "is_point_in_time": self.is_point_in_time,
            "source": "grok3.md classify_systemic_risk (multi-type black-swan layer)",
            "note": "Veto-class. Recommend-only; capital use needs the Risk-Officer "
                    "gate (CLAUDE.md §10). GPR/margin-debt are Grade-D optional inputs.",
        }


# ---------------------------------------------------------------------------
# Detection logic (grok3.md classify_systemic_risk), guarded for missing inputs.
# ---------------------------------------------------------------------------
def classify_systemic_risk(data: Dict[str, Optional[float]]) -> str:
    """Return the active systemic-risk typology. Faithful to grok3.md's priority
    order, with each branch guarded so a missing (None) input cannot mis-fire.
    Liquidity crisis carries a real-data fallback for when TED (discontinued) is
    unavailable: HY OAS *and* IG OAS both wide = funding stress."""
    hy_oas = data.get("hy_oas")
    ig_oas = data.get("ig_oas")
    ted = data.get("ted")
    vix = data.get("vix")
    bi = data.get("buffett_indicator")
    m2 = data.get("m2_yoy")
    cpi = data.get("core_cpi_yoy")
    gpr = data.get("gpr_index")
    wti = data.get("wti_yoy")
    net_liq = data.get("net_liq_delta")

    def gt(x, t):  # x > t with None-guard
        return x is not None and x > t

    def lt(x, t):
        return x is not None and x < t

    # 1. Liquidity crisis (priority). Primary = grok3 TED+HY; fallback = HY+IG wide
    #    + liquidity draining (real-data path when TED is discontinued/None).
    if (gt(ted, 0.8) and gt(hy_oas, 5.0)) or \
       (gt(hy_oas, 5.5) and gt(ig_oas, 2.5)) or \
       (gt(hy_oas, 5.0) and gt(ig_oas, 2.0) and lt(net_liq, 0.0)):
        return LIQUIDITY_CRISIS

    # 2. Valuation bubble: extreme valuation, calm vol, tight credit (no crisis yet).
    if gt(bi, 200) and lt(vix, 25) and lt(hy_oas, 4.5):
        return VALUATION_BUBBLE

    # 3. Geopolitical shock: GPR spike OR (credit widening AND energy spiking).
    if gt(gpr, 180) or (gt(hy_oas, 4.5) and gt(wti, 30)):
        return GEOPOLITICAL_SHOCK

    # 4. Inflation shock (grok3: hot core CPI + fast money).
    if gt(cpi, 5.5) and gt(m2, 7):
        return INFLATION_SHOCK

    # 5. Generic systemic risk: any single stress gauge extreme.
    if gt(hy_oas, 5.0) or gt(vix, 30) or gt(bi, 190):
        return SYSTEMIC_RISK

    return NORMAL


def systemic_score(data: Dict[str, Optional[float]]) -> float:
    """0-100 systemic stress score (grok3.md additive thresholds + graded steps +
    an IG OAS term). Higher = more stress."""
    hy_oas = data.get("hy_oas")
    ig_oas = data.get("ig_oas")
    ted = data.get("ted")
    vix = data.get("vix")
    bi = data.get("buffett_indicator")
    s = 0.0
    if hy_oas is not None:
        s += 30 if hy_oas > 5.0 else 15 if hy_oas > 4.0 else 0
    if ted is not None:
        s += 25 if ted > 0.8 else 12 if ted > 0.5 else 0
    if vix is not None:
        s += 20 if vix > 35 else 10 if vix > 28 else 0
    if bi is not None:
        s += 15 if bi > 200 else 8 if bi > 185 else 0
    if ig_oas is not None:
        s += 15 if ig_oas > 2.5 else 8 if ig_oas > 2.0 else 0
    return min(s, 100.0)


def risk_level(score: float) -> str:
    return "HIGH" if score >= 70 else "MEDIUM" if score >= 45 else "LOW"


# ---------------------------------------------------------------------------
# Live input gathering (real FRED; never-raise -> flagged fallback)
# ---------------------------------------------------------------------------
def gather_inputs(as_of: Optional[str] = None, pit: bool = True,
                  macro: Optional[Dict[str, Any]] = None,
                  gpr_index: Optional[float] = None,
                  margin_debt_yoy: Optional[float] = None) -> SystemicVerdict:
    """Assemble the systemic-risk inputs. Reuses macro_risk for the core composite
    (HY OAS, VIX, M2, net-liquidity, Buffett) and fetches the extra series
    (IG OAS, TED, core CPI YoY, WTI YoY) here. `macro` may be passed in to avoid a
    duplicate FRED pull. gpr_index / margin_debt_yoy are optional Grade-D inputs."""
    from simulation.macro_risk import gather_macro_inputs, _fetch, _fetch_series

    vintage = as_of if (pit and as_of) else None
    # Core inputs (HY OAS, VIX, M2, net-liq, Buffett): prefer a passed-in macro dict
    # that already carries "inputs" (avoids a duplicate FRED pull); otherwise pull
    # them directly so a thin/odd-shaped macro dict cannot blank the classifier.
    if macro is not None and macro.get("inputs"):
        mi = macro["inputs"]
        msrc = macro.get("sources", {}) or {}
    else:
        _mi = gather_macro_inputs(as_of, pit)
        mi = _mi.values
        msrc = _mi.sources

    values: Dict[str, Optional[float]] = {}
    sources: Dict[str, str] = {}

    def carry(name: str, key: Optional[str] = None):
        key = key or name
        values[name] = mi.get(key)
        sources[name] = msrc.get(key, "fallback" if mi.get(key) is None else "macro")

    carry("hy_oas")
    carry("vix")
    carry("m2_yoy")
    carry("net_liq_delta")
    carry("buffett_indicator")

    def put_extra(name: str, val, src: str):
        values[name] = val
        sources[name] = src if val is not None else "unavailable"

    live = "fred-vintage" if vintage else "fred-live"
    put_extra("ig_oas", _fetch(FRED_EXTRA["ig_oas"], vintage), live)
    put_extra("ted", _fetch(FRED_EXTRA["ted"], vintage), live)

    # core CPI YoY (needs ~13 monthly points)
    cpi = _fetch_series(FRED_EXTRA["core_cpi"], start="2024-01-01", vintage=vintage)
    if len(cpi) >= 13 and cpi[-13]["value"]:
        put_extra("core_cpi_yoy",
                  round((cpi[-1]["value"] / cpi[-13]["value"] - 1) * 100, 2), live)
    else:
        put_extra("core_cpi_yoy", None, live)

    # WTI YoY (~252 trading days)
    wti = _fetch_series(FRED_EXTRA["wti"], start="2024-01-01", vintage=vintage)
    if len(wti) >= 240 and wti[-240]["value"]:
        put_extra("wti_yoy",
                  round((wti[-1]["value"] / wti[-240]["value"] - 1) * 100, 1), live)
    else:
        put_extra("wti_yoy", None, live)

    # Grade-D optional inputs (no clean free source -> caller may inject; else None)
    put_extra("gpr_index", gpr_index, "grade-d-override")
    put_extra("margin_debt_yoy", margin_debt_yoy, "grade-d-override")

    return _verdict(values, sources, is_pit=bool(vintage))


def _verdict(values: Dict[str, Optional[float]], sources: Dict[str, str],
             is_pit: bool = False) -> SystemicVerdict:
    rtype = classify_systemic_risk(values)
    score = systemic_score(values)
    level = risk_level(score)
    floor = DEFENSIVE_FLOOR_BY_TYPE.get(rtype, 0.0)
    tilt = dict(SYSTEMIC_TRADER_TILT.get(rtype, {}))
    rationale = _RATIONALE.get(rtype, "No dominant systemic-risk typology.")
    return SystemicVerdict(
        risk_type=rtype, risk_level=level, score_0_100=score,
        defensive_floor_step=floor, trader_tilt=tilt,
        inputs=values, sources=sources, rationale=rationale,
        is_point_in_time=is_pit)


_RATIONALE = {
    LIQUIDITY_CRISIS: "TED/HY-IG funding stress + draining liquidity -> banks/repo "
                      "freeze (2008/2020). Cash + low leverage; Risk-Officer up, "
                      "small-cap/momentum hard-cut.",
    VALUATION_BUBBLE: "Extreme valuation with calm vol + tight credit (2000 analog). "
                      "Mean-revert toward Value/Quality; cut momentum/breakout/meme.",
    GEOPOLITICAL_SHOCK: "Geopolitical-risk spike or credit-widening + energy spike "
                        "(2022). Defense/Energy up; cut small-cap & high-beta.",
    INFLATION_SHOCK: "Hot core CPI + fast money -> forced hawkish repricing (1970s/"
                     "2022). Energy/Value up; cut long-duration growth.",
    SYSTEMIC_RISK: "Multiple stress gauges elevated without a single dominant cause "
                   "-> broad de-risk; Risk-Officer + Value up.",
    NORMAL: "No systemic-risk typology active -> defer to the base regime.",
}


def from_live(as_of: Optional[str] = None, pit: bool = True,
              macro: Optional[Dict[str, Any]] = None,
              gpr_index: Optional[float] = None,
              margin_debt_yoy: Optional[float] = None) -> SystemicVerdict:
    """Convenience: gather real inputs and classify in one call."""
    return gather_inputs(as_of, pit, macro, gpr_index, margin_debt_yoy)


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------
def _demo() -> int:
    import json
    print("=" * 72)
    print("systemic_risk self-test (synthetic typologies + live)")
    print("=" * 72)
    cases = [
        ("2008/2020 liquidity", dict(hy_oas=6.2, ig_oas=2.8, ted=1.1, vix=40,
                                     buffett_indicator=150, net_liq_delta=-0.3)),
        ("2000 valuation bubble", dict(hy_oas=3.4, ig_oas=1.3, ted=0.2, vix=18,
                                       buffett_indicator=225, net_liq_delta=0.05)),
        ("2022 geopolitical/energy", dict(hy_oas=4.8, ig_oas=2.1, vix=29,
                                          buffett_indicator=170, wti_yoy=55)),
        ("1970s/2022 inflation", dict(hy_oas=4.2, vix=26, buffett_indicator=165,
                                      core_cpi_yoy=6.2, m2_yoy=9)),
        ("calm tape", dict(hy_oas=2.8, ig_oas=1.1, ted=0.15, vix=15,
                           buffett_indicator=218, net_liq_delta=0.05)),
    ]
    for name, data in cases:
        v = _verdict(data, {k: "synthetic" for k in data})
        print(f"\n  [{name}] -> {v.risk_type} ({v.risk_level}, score {v.score_0_100})")
        print(f"    defensive_floor_step={v.defensive_floor_step}  "
              f"tilt_keys={list(v.trader_tilt)[:4]}...")

    print("\n  [live]")
    try:
        v = from_live()
        d = v.to_dict()
        d.pop("trader_tilt", None)  # keep the print compact
        print(json.dumps(d, indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"    live classification skipped: {e}")
    return 0


if __name__ == "__main__":
    raise SystemExit(_demo())
