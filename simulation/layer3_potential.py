#!/usr/bin/env python3
"""
Trading Society -- Layer 3: 10-year long-term potential scorecard

PPST Declaration (this PROGRAM):
- PROJECT: Trading Society
- PROGRAM: simulation/layer3_potential.py
- SKILL:   structured 0-100 long-term potential scorecard -> Top-30 ranking
- TARGET:  Score the universe on 7 long-horizon dimensions (industry trend 25%,
           moat 20%, capital allocation 15%, FCF quality 15%, valuation 10%,
           management 10%, geopolitical 5%) and rank the Top 30 ten-year potential
           names, each with its main driver + risk flag. Recommend-only, no LLM.

Layer 3 of the 3-layer framework (long-term strategic, yearly update).

DATA HONESTY (important):
- Industry trend: curated long-term structural-growth map by Finviz industry
  (AI/semis/power/defense/space/biotech high; legacy low). Grade-D judgement.
- Moat: REAL -- reuses the repo's hand-ranked IP_DEFENSIBILITY (src/sharks/scoring/fom.py).
- Valuation: REAL -- Finviz P/E.
- Geopolitical: curated sovereign/geo-immunity (US-domestic high, China-exposed low).
- Capital allocation / FCF quality / management: currently NEUTRAL PROXIES (50),
  flagged -- they need real financials (polygon FCF/ROIC) + governance data, which
  are TODO. The score is transparent about which dimensions are real vs proxy.

Run: python simulation/layer3_potential.py
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

WEIGHTS = {"industry_trend": 0.25, "moat": 0.20, "capital_allocation": 0.15,
           "fcf_quality": 0.15, "valuation": 0.10, "management": 0.10,
           "geopolitical": 0.05}

# Curated long-term structural-growth score (0-100) by Finviz industry.
INDUSTRY_TREND: Dict[str, float] = {
    "Semiconductors": 92, "Semiconductor Equipment & Materials": 95,
    "Software - Infrastructure": 88, "Software - Application": 78,
    "Information Technology Services": 65, "Computer Hardware": 72,
    "Communication Equipment": 80, "Electronic Components": 75,
    "Aerospace & Defense": 82, "Utilities - Regulated Electric": 72,
    "Utilities - Independent Power Producers": 85, "Utilities - Renewable": 70,
    "Specialty Industrial Machinery": 70, "Electrical Equipment & Parts": 78,
    "Biotechnology": 72, "Drug Manufacturers - General": 66,
    "Drug Manufacturers - Specialty & Generic": 58, "Diagnostics & Research": 72,
    "Medical Devices": 68, "Medical Instruments & Supplies": 62,
    "Healthcare Plans": 55, "Internet Content & Information": 74,
    "Internet Retail": 70, "Asset Management": 55, "Credit Services": 58,
    "Auto Manufacturers": 60, "Solar": 62, "Oil & Gas E&P": 45,
    "Oil & Gas Integrated": 42, "Oil & Gas Midstream": 48,
    "Beverages - Non-Alcoholic": 45, "Household & Personal Products": 40,
    "Discount Stores": 48, "Restaurants": 45, "Entertainment": 52,
    "Telecom Services": 40, "Banks - Diversified": 45, "REIT - Specialty": 50,
}
DEFAULT_TREND = 48.0

# China / geopolitically-exposed names (lower sovereign-immunity score).
CHINA_EXPOSED = {"BABA", "NIO", "JD", "PDD", "BIDU", "LI", "XPEV", "TCEHY", "TME"}
# High-immunity domestic / defense / sovereign-aligned (higher).
HIGH_IMMUNITY = {"LMT", "NOC", "RTX", "GD", "PLTR", "MSFT", "GOOGL", "AMZN",
                 "AAPL", "META", "NVDA"}


def _valuation_score(pe: Optional[float]) -> float:
    if pe is None or pe <= 0:
        return 50.0  # unknown/loss-making -> neutral
    if pe < 18:
        return 82.0
    if pe < 28:
        return 66.0
    if pe < 45:
        return 48.0
    if pe < 70:
        return 32.0
    return 18.0


def _geo_score(ticker: str) -> float:
    if ticker in CHINA_EXPOSED:
        return 25.0
    if ticker in HIGH_IMMUNITY:
        return 85.0
    return 60.0


def _moat_map() -> Dict[str, float]:
    try:
        from sharks.scoring.fom import IP_DEFENSIBILITY  # type: ignore
        return dict(IP_DEFENSIBILITY)
    except Exception:
        try:
            sys.path.insert(0, str(_ROOT / "src"))
            from sharks.scoring.fom import IP_DEFENSIBILITY  # type: ignore
            return dict(IP_DEFENSIBILITY)
        except Exception:
            return {}


def _real_fundamental_scores(ticker: str, fin: Optional[Dict[str, Any]]
                             ) -> Tuple[float, float]:
    """Return (capital_allocation, fcf_quality) 0-100 from REAL Polygon financials
    when available, else neutral 50. ROIC + ROIC trend -> capital allocation;
    OCF margin + OCF growth -> FCF quality."""
    if not fin or fin.get("source") != "polygon_real":
        return 50.0, 50.0
    roic, roic_tr = fin.get("roic"), fin.get("roic_trend")
    ocf_m, ocf_g = fin.get("ocf_margin"), fin.get("ocf_yoy")
    # capital allocation: ROIC level (10% ROIC -> ~70) nudged by its trend
    cap = 50.0
    if roic is not None:
        cap = max(0.0, min(100.0, 40 + roic * 200))       # ROIC 0.10 -> 60, 0.25 -> 90
        if roic_tr is not None:
            cap = max(0.0, min(100.0, cap + roic_tr * 150))
    fcf = 50.0
    if ocf_m is not None:
        fcf = max(0.0, min(100.0, 35 + ocf_m * 120))      # OCF margin 0.30 -> 71
        if ocf_g is not None:
            fcf = max(0.0, min(100.0, fcf + ocf_g * 40))
    return round(cap, 1), round(fcf, 1)


def score_name(ticker: str, fund: Dict[str, Any], moat_map: Dict[str, float],
               fin: Optional[Dict[str, Any]] = None
               ) -> Tuple[float, Dict[str, float], str, str]:
    industry = (fund or {}).get("industry") or ""
    pe = (fund or {}).get("pe")
    cap_alloc, fcf_q = _real_fundamental_scores(ticker, fin)
    comp = {
        "industry_trend": INDUSTRY_TREND.get(industry, DEFAULT_TREND),
        "moat": moat_map.get(ticker, 50.0),               # REAL where known
        "capital_allocation": cap_alloc,                  # REAL (ROIC) if data, else 50
        "fcf_quality": fcf_q,                             # REAL (OCF margin) if data, else 50
        "valuation": _valuation_score(pe),                # REAL (Finviz P/E)
        "management": 50.0,                               # PROXY (neutral) -- TODO
        "geopolitical": _geo_score(ticker),               # curated
    }
    score = sum(comp[k] * WEIGHTS[k] for k in WEIGHTS)
    # main driver = highest weighted contribution; risk = lowest
    contrib = {k: comp[k] * WEIGHTS[k] for k in WEIGHTS}
    driver = max(contrib, key=contrib.get)
    risk_dim = min(comp, key=lambda k: comp[k] if k in ("valuation", "geopolitical",
                                                        "moat") else 999)
    driver_txt = {"industry_trend": f"10yr industry trend ({industry})",
                  "moat": "moat", "valuation": "valuation",
                  "geopolitical": "geo-immunity"}.get(driver, driver)
    risk_txt = ("rich valuation" if comp["valuation"] < 40 else
                "geo / China exposure" if comp["geopolitical"] < 40 else
                "weak moat" if comp["moat"] < 45 else
                "capital-alloc / FCF need real data")
    return round(score, 1), comp, driver_txt, risk_txt


def run(top_n: int = 30) -> Dict[str, Any]:
    from simulation.universe_competition import build_universe
    from simulation.finviz_data import get_fundamentals
    uni = build_universe(max_names=200)
    funds = get_fundamentals(uni["tickers"])
    moat_map = _moat_map()
    fin_store = None
    try:
        from simulation.data_pipeline.financials_store import store
        fin_store = store() if store().available else None
    except Exception:
        fin_store = None

    rows = []
    for tkr in uni["tickers"]:
        f = funds.get(tkr)
        if not f:
            continue
        fin = fin_store.metrics(tkr) if fin_store else None
        score, comp, driver, risk = score_name(tkr, f, moat_map, fin)
        rows.append({"ticker": tkr, "potential_score": score,
                     "industry": f.get("industry"), "pe": f.get("pe"),
                     "main_driver": driver, "risk_flag": risk,
                     "components": {k: round(v, 1) for k, v in comp.items()}})
    rows.sort(key=lambda r: r["potential_score"], reverse=True)
    top = rows[:top_n]
    # split "core long-term hold" vs "high-growth high-risk"
    for r in top:
        r["bucket"] = ("core_long_term" if r["components"]["moat"] >= 70
                       and r["components"]["valuation"] >= 45 else "high_growth_high_risk")

    return {
        "type": "trading_society_layer3_potential",
        "as_of_timestamp": datetime.now(timezone.utc).isoformat(),
        "role": "writer", "project": "Trading Society",
        "program": "simulation/layer3_potential.py",
        "llm_involvement": "none", "layer": 3, "horizon": "10-year",
        "weights": WEIGHTS,
        "data_honesty": {
            "real": ["moat (IP_DEFENSIBILITY)", "valuation (Finviz P/E)",
                     "capital_allocation (REAL ROIC=NI/(equity+debt) where Polygon data)",
                     "fcf_quality (REAL OCF margin+growth where Polygon data)"],
            "curated": ["industry_trend", "geopolitical"],
            "proxy_neutral_TODO": ["management (no governance data source)"],
            "financials_cache": (fin_store.cache_path() if fin_store else None),
            "note": "capital_allocation + fcf_quality now use REAL Polygon financials "
                    "(ROIC, OCF) where available, else neutral 50. management stays a "
                    "neutral proxy (no governance data). Pure capex unavailable on "
                    "Polygon -> investing-CF intensity used elsewhere."},
        "top_potential": top,
        "n_scored": len(rows),
        "disclaimer": ("Layer-3 10-year potential ranking. Recommend-only RESEARCH; "
                       "strategic context, not a capital order. Three of seven "
                       "dimensions are neutral proxies (flagged) pending real "
                       "fundamentals. Not a substitute for the canonical pipeline."),
    }


def main() -> int:
    r = run()
    out = _ROOT / "outputs" / f"layer3-potential-{r['as_of_timestamp'][:10]}.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(r, indent=2, ensure_ascii=False), encoding="utf-8")
    print("=" * 74)
    print("TRADING SOCIETY -- Layer 3: 10-year potential Top 30 (recommend-only)")
    print("=" * 74)
    print(f"Scored {r['n_scored']} names | real dims: moat + valuation; curated: "
          f"industry+geo; PROXY: capital-alloc/FCF/mgmt (flagged)")
    print(f"\n  {'#':<3}{'ticker':<7}{'score':>6}  {'bucket':<22}{'driver / risk'}")
    for i, x in enumerate(r["top_potential"], 1):
        print(f"  {i:<3}{x['ticker']:<7}{x['potential_score']:>6}  "
              f"{x['bucket']:<22}{x['main_driver']} | risk: {x['risk_flag']}")
    print("\n" + r["disclaimer"])
    print(f"\nArtifact: {out.relative_to(_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
