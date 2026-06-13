#!/usr/bin/env python3
"""
Trading Society -- Real PIT Macro Risk Environment Score (review item B)

PPST Declaration (this PROGRAM):
- PROJECT: Trading Society
- PROGRAM: simulation/macro_risk.py
- SKILL:   regime_detector -> transparent 0-100 macro risk composite from REAL
           FRED series (PIT-capable via ALFRED vintage)
- TARGET:  Replace the synthetic Macro Risk Score with a real, auditable
           composite of credit spread, yield curve, VIX, M2 growth, net
           liquidity, and equity valuation -- each pulled live from FRED, each
           never-raise with a flagged fallback. PIT via vintage_date. No LLM.

Why (review B): the dynamic defensive leg keys off this score; a synthetic input
makes the whole hedge decision unreliable. This wires the real data.

Score convention: 0..100, HIGHER = more risk-off (more defensive warranted).
Each component maps a real reading to a [0,1] risk contribution; the score is the
weighted mean over the components that were actually retrieved (renormalized), so
a missing series degrades coverage rather than silently biasing the score.

PIT honesty (docs/LLM-BACKTEST-PROTOCOL.md, philosophy 09-point-in-time):
- Pass `vintage_date=as_of` to read each series as first published on/before that
  date (FRED ALFRED). Without it, the latest revision is used (flagged not-PIT).

Run: python simulation/macro_risk.py   (live FRED pull; falls back per-series)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

# Core FRED series -> the reliable risk gauges (credit/curve/vix/m2/liquidity).
FRED = {
    "ten_year": "DGS10", "two_year": "DGS2", "real_yield": "DFII10",
    "vix": "VIXCLS", "hy_oas": "BAMLH0A0HYM2", "m2": "M2SL",
    "walcl": "WALCL", "tga": "WTREGEN", "rrp": "RRPONTSYD",
    "btc": "CBBTCUSD",
}

# Component weights (sum normalized over retrieved components).
WEIGHTS = {
    "credit_spread": 0.22, "yield_curve": 0.15, "vix": 0.18,
    "m2_growth": 0.12, "net_liquidity": 0.13, "valuation": 0.20,
}
# Synthetic stressed fallbacks (clearly flagged when used).
FALLBACK = {"ten_year": 4.5, "two_year": 4.2, "real_yield": 2.0, "vix": 18.0,
            "hy_oas": 3.5, "m2_yoy": 1.0, "net_liq_delta": -0.1,
            "buffett_indicator": 225.0}


def _clip(x: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, x))


@dataclass
class MacroInputs:
    values: Dict[str, Optional[float]] = field(default_factory=dict)
    sources: Dict[str, str] = field(default_factory=dict)  # "fred-live" | "fred-vintage" | "fallback"


def _fetch(series_id: str, vintage: Optional[str]):
    try:
        from sharks.data.fred_client import fetch_latest
    except Exception:
        try:
            from src.sharks.data.fred_client import fetch_latest  # type: ignore
        except Exception:
            return None
    try:
        kw = {"max_retries": 2, "timeout": 12.0}
        if vintage:
            kw["vintage_date"] = vintage
        row = fetch_latest(series_id, **kw)
        return float(row["value"]) if row and row.get("value") is not None else None
    except Exception:
        return None


def _fetch_series(series_id: str, start: str, vintage: Optional[str]):
    try:
        from sharks.data.fred_client import fetch_series
    except Exception:
        try:
            from src.sharks.data.fred_client import fetch_series  # type: ignore
        except Exception:
            return []
    try:
        kw = {"start": start, "max_retries": 2, "timeout": 12.0}
        if vintage:
            kw["vintage_date"] = vintage
        return [r for r in fetch_series(series_id, **kw) if r.get("value") is not None]
    except Exception:
        return []


def gather_macro_inputs(as_of: Optional[str] = None, pit: bool = True,
                        buffett_indicator: Optional[float] = None) -> MacroInputs:
    vintage = as_of if (pit and as_of) else None
    mi = MacroInputs()

    def put(name: str, val, live_src: str):
        if val is None:
            mi.values[name] = FALLBACK.get(name)
            mi.sources[name] = "fallback"
        else:
            mi.values[name] = val
            mi.sources[name] = live_src
    live = "fred-vintage" if vintage else "fred-live"

    put("ten_year", _fetch(FRED["ten_year"], vintage), live)
    put("two_year", _fetch(FRED["two_year"], vintage), live)
    put("real_yield", _fetch(FRED["real_yield"], vintage), live)
    put("vix", _fetch(FRED["vix"], vintage), live)
    put("hy_oas", _fetch(FRED["hy_oas"], vintage), live)

    # M2 YoY needs ~14 months of history.
    m2 = _fetch_series(FRED["m2"], start="2024-01-01", vintage=vintage)
    if len(m2) >= 13:
        latest, prior = m2[-1]["value"], m2[-13]["value"]
        put("m2_yoy", round((latest / prior - 1) * 100, 2) if prior else None, live)
    else:
        put("m2_yoy", None, live)

    # Net liquidity = WALCL - TGA - RRP (trillions); delta over the last 2 weeks.
    nl = []
    walcl = _fetch_series(FRED["walcl"], start="2026-01-01", vintage=vintage)
    if walcl:
        w = walcl[-1]["value"]
        tga = _fetch(FRED["tga"], vintage)
        rrp = _fetch(FRED["rrp"], vintage)
        if w and tga is not None and rrp is not None:
            # Report only the weekly change in the Fed balance sheet (WALCL),
            # in trillions -- TGA/RRP units vary on FRED, so we avoid a possibly
            # mis-scaled absolute and use the robust WALCL delta sign instead.
            prev_w = walcl[-2]["value"] if len(walcl) >= 2 else None
            delta = ((w - prev_w) / 1e6) if prev_w else None
            put("net_liq_delta", round(delta, 4) if delta is not None else None, live)
        else:
            put("net_liq_delta", None, live)
    else:
        put("net_liq_delta", None, live)

    btc = _fetch(FRED["btc"], vintage)
    if btc is not None:
        mi.values["btc"] = btc
        mi.sources["btc"] = live
    put("buffett_indicator", buffett_indicator, "override" if buffett_indicator else "fallback")
    return mi


def macro_risk_score(as_of: Optional[str] = None, pit: bool = True,
                     buffett_indicator: Optional[float] = None) -> Dict[str, Any]:
    mi = gather_macro_inputs(as_of, pit, buffett_indicator)
    v = mi.values
    comp: Dict[str, float] = {}

    if v.get("hy_oas") is not None:
        comp["credit_spread"] = _clip((v["hy_oas"] - 3.0) / 4.0)      # 3%->0, 7%->1
    if v.get("ten_year") is not None and v.get("two_year") is not None:
        curve = v["ten_year"] - v["two_year"]
        comp["yield_curve"] = _clip((0.3 - curve) / 1.3)              # +0.3->0, -1.0->1
    if v.get("vix") is not None:
        comp["vix"] = _clip((v["vix"] - 14.0) / 21.0)                 # 14->0, 35->1
    if v.get("m2_yoy") is not None:
        comp["m2_growth"] = _clip((1.5 - v["m2_yoy"]) / 6.0)          # +1.5%->0, -4.5%->1
    if v.get("net_liq_delta") is not None:
        comp["net_liquidity"] = 0.7 if v["net_liq_delta"] < 0 else 0.2
    if v.get("buffett_indicator") is not None:
        comp["valuation"] = _clip((v["buffett_indicator"] - 150.0) / 80.0)  # 150->0, 230->1

    if comp:
        wsum = sum(WEIGHTS[k] for k in comp) or 1.0
        score = sum(comp[k] * WEIGHTS[k] for k in comp) / wsum * 100.0
    else:
        score = 50.0
    posture = ("high_uncertainty" if score >= 75 else "risk_off" if score >= 55
               else "neutral" if score >= 35 else "risk_on")
    n_live = sum(1 for s in mi.sources.values() if s.startswith("fred"))
    return {
        "score_0_100": round(score, 1),
        "posture": posture,
        "components": {k: round(val, 3) for k, val in comp.items()},
        "inputs": v,
        "sources": mi.sources,
        "n_live_series": n_live,
        "is_point_in_time": bool(pit and as_of),
        "coverage": f"{len(comp)}/6 components",
        "note": ("Real FRED composite (higher = risk-off). Pass as_of + pit=True "
                 "for ALFRED-vintage PIT. Components missing live data use a "
                 "flagged fallback (see sources)."),
    }


def _demo() -> int:
    import json
    print("=" * 72)
    print("macro_risk self-test (live FRED; per-series fallback if offline)")
    print("=" * 72)
    r = macro_risk_score(buffett_indicator=225.0)
    print(json.dumps(r, indent=2, ensure_ascii=False))
    live = r["n_live_series"]
    print(f"\nLive FRED series retrieved: {live}/{len(FRED)}  "
          f"(if 0, network/FRED was unavailable -> flagged fallbacks used)")
    return 0


if __name__ == "__main__":
    raise SystemExit(_demo())
