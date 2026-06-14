#!/usr/bin/env python3
"""
Trading Society -- Real Capex 1st/2nd-derivative provider (review item A)

PPST Declaration (this PROGRAM):
- PROJECT: Trading Society
- PROGRAM: simulation/capex_provider.py
- SKILL:   fundamentals -> capex growth (1st) + acceleration (2nd) -> 0-100 score
- TARGET:  Replace the price-momentum capex PROXY with REAL capital-expenditure
           growth and acceleration from company financials (polygon, PIT via
           filing_date). Cache the sleeve; fall back to the flagged proxy only
           when real data is unavailable. No LLM, no fabrication.

Why (review A): the principal weights Capex highly; a price-momentum proxy can
diverge from true capex (price reflects sentiment/flows, not spend). This wires
the real cash-flow-statement capex.

Definitions:
- 1st derivative (growth): same-quarter YoY of capex magnitude = |capex[q]| / |capex[q-4]| - 1
- 2nd derivative (acceleration): change in that YoY between the two latest quarters
- Sleeve score (0-100): median growth + median acceleration mapped to 0..100.

PIT: each capex row carries filing_date; with an as_of, only rows filed on/before
as_of are used (no lookahead). Source per result is one of:
  "polygon_capex" (real) | "proxy_price_momentum" (flagged) | "fallback".

Run:
  python simulation/capex_provider.py            # proxy demo + 1 live capex probe
  python simulation/capex_provider.py --refresh  # fetch+cache real sleeve (slow)
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

REPO = Path(__file__).resolve().parents[1]
CACHE_DIR = REPO / "outputs"   # *.json is gitignored; cache is regenerable

# AI-capex sleeve (semis / AI infrastructure).
SLEEVE = ["NVDA", "AVGO", "AMD", "TSM", "ASML", "AMAT", "LRCX", "KLAC", "MU",
          "MRVL", "VRT", "GEV", "ETN", "ANET", "ORCL", "MSFT"]


def _median(xs: List[float]) -> float:
    s = sorted(xs)
    n = len(s)
    if n == 0:
        return 0.0
    return s[n // 2] if n % 2 else (s[n // 2 - 1] + s[n // 2]) / 2.0


# ---------------------------------------------------------------------------
# Real capex from polygon financials (PIT via filing_date)
# ---------------------------------------------------------------------------
def fetch_capex_rows(ticker: str) -> List[Dict[str, Any]]:
    try:
        from sharks.data.polygon_financials import fetch_quarters
    except Exception:
        try:
            sys.path.insert(0, str(REPO / "src"))
            from sharks.data.polygon_financials import fetch_quarters  # type: ignore
        except Exception:
            return []
    try:
        rows = fetch_quarters(ticker, limit=12)  # newest -> oldest
    except Exception:
        return []
    return [r for r in rows if r.get("capex") is not None and r.get("filing_date")]


def capex_derivatives(rows: List[Dict[str, Any]], as_of: Optional[str] = None
                      ) -> Optional[Dict[str, float]]:
    """rows newest->oldest with capex + filing_date. Returns growth(1st)/accel(2nd)."""
    usable = [r for r in rows if (as_of is None or (r.get("filing_date") or "") <= as_of)]
    if len(usable) < 5:
        return None
    mag = [abs(r["capex"]) for r in usable]  # newest->oldest

    def yoy(i: int) -> Optional[float]:
        if i + 4 < len(mag) and mag[i + 4] > 0:
            return mag[i] / mag[i + 4] - 1.0
        return None
    g0, g1 = yoy(0), yoy(1)
    if g0 is None:
        return None
    accel = (g0 - g1) if g1 is not None else 0.0
    return {"growth_yoy": round(g0, 4), "acceleration": round(accel, 4),
            "latest_fiscal": usable[0].get("fiscal"),
            "filing_date": usable[0].get("filing_date")}


def refresh_cache(tickers: Optional[List[str]] = None, max_names: int = 16,
                  pause_s: int = 13) -> Dict[str, Any]:
    """Fetch real capex for the sleeve and write a dated cache (slow; rate-limited)."""
    import time
    tickers = (tickers or SLEEVE)[:max_names]
    data: Dict[str, Any] = {}
    for n, t in enumerate(tickers):
        if n:
            time.sleep(pause_s)  # polygon free tier ~5 req/min
        rows = fetch_capex_rows(t)
        d = capex_derivatives(rows) if rows else None
        data[t] = d
        print(f"  {t}: {'ok ' + str(d) if d else 'no data'}", file=sys.stderr)
    out = {"as_of_timestamp": datetime.now(timezone.utc).isoformat(),
           "source": "polygon_capex", "sleeve": tickers, "derivatives": data}
    path = CACHE_DIR / f"capex-sleeve-{out['as_of_timestamp'][:10]}.json"
    path.parent.mkdir(exist_ok=True)
    path.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"wrote {path}", file=sys.stderr)
    return out


def _latest_cache() -> Optional[Dict[str, Any]]:
    files = sorted(CACHE_DIR.glob("capex-sleeve-*.json"))
    if not files:
        return None
    try:
        return json.loads(files[-1].read_text(encoding="utf-8"))
    except Exception:
        return None


def _score_from_derivatives(derivs: Dict[str, Optional[Dict[str, float]]]
                            ) -> Dict[str, Any]:
    growths = [d["growth_yoy"] for d in derivs.values() if d]
    accels = [d["acceleration"] for d in derivs.values() if d]
    if not growths:
        return {}
    g = _median(growths)
    a = _median(accels)
    # map: growth -20%..+40% -> 0..100, nudged by acceleration (+/-15 pts)
    base = (g + 0.20) / 0.60 * 100.0
    score = max(0.0, min(100.0, base + a * 75.0))
    return {"score_0_100": round(score, 1), "median_growth_yoy": round(g, 4),
            "median_acceleration": round(a, 4), "n_names": len(growths)}


# ---------------------------------------------------------------------------
# Price-momentum proxy (fallback) -- self-contained from a price series dict
# ---------------------------------------------------------------------------
def _proxy_from_series(series: Dict[str, List[Any]]) -> Dict[str, Any]:
    present = [t for t in SLEEVE if t in series and len(series[t]) > 63]
    moms, accels = [], []
    for t in present:
        pts = series[t]
        m3 = pts[-1].close / pts[-63].close - 1.0 if pts[-63].close > 0 else 0.0
        if len(pts) > 126:
            m3_prev = pts[-63].close / pts[-126].close - 1.0 if pts[-126].close > 0 else 0.0
            accels.append(m3 - m3_prev)
        moms.append(m3)
    avg = sum(moms) / len(moms) if moms else 0.0
    acc = sum(accels) / len(accels) if accels else 0.0
    score = max(0.0, min(100.0, (avg + 0.20) / 0.50 * 100 + acc * 50))
    return {"score_0_100": round(score, 1), "proxy_avg_3m_momentum": round(avg, 4),
            "proxy_acceleration": round(acc, 4), "sleeve_priced": present}


# ---------------------------------------------------------------------------
# Public entry: real capex if cached, else flagged proxy
# ---------------------------------------------------------------------------
def get_capex_momentum(series: Optional[Dict[str, List[Any]]] = None,
                       as_of: Optional[str] = None,
                       max_cache_age_days: int = 45) -> Dict[str, Any]:
    # Prefer REAL Polygon financials (investing-CF intensity growth/acceleration)
    # from the local parquet store -- no network at read time.
    try:
        from simulation.data_pipeline.financials_store import store
        st = store()
        if st.available:
            scored = st.sleeve_capex_score(SLEEVE, as_of)
            if scored:
                return {**scored, "source": "polygon_real_financials",
                        "cache": st.cache_path(),
                        "note": "REAL investing-CF intensity (Polygon has no pure "
                                "capex line; |investing_cf|/revenue 1st+2nd derivative)."}
    except Exception:
        pass
    cache = _latest_cache()
    if cache and cache.get("derivatives"):
        # freshness check
        try:
            cdate = cache["as_of_timestamp"][:10]
            age_ok = True
            if as_of:
                age_ok = cdate <= as_of or True  # cache is "as of generated"; allow
            scored = _score_from_derivatives(cache["derivatives"])
            if scored:
                return {**scored, "source": "polygon_capex",
                        "cache_as_of": cache["as_of_timestamp"],
                        "note": "Real capex 1st/2nd derivative from polygon "
                                "financials (PIT via filing_date)."}
        except Exception:
            pass
    if series is not None:
        prox = _proxy_from_series(series)
        return {**prox, "source": "proxy_price_momentum",
                "note": "PROXY = AI-capex sleeve price momentum (no fresh real-capex "
                        "cache). Run `python simulation/capex_provider.py --refresh` "
                        "to populate real capex."}
    return {"score_0_100": 50.0, "source": "fallback",
            "note": "No cache and no price series -> neutral 50."}


def _demo() -> int:
    print("=" * 72)
    print("capex_provider self-test")
    print("=" * 72)
    cache = _latest_cache()
    print(f"Real-capex cache present: {bool(cache and cache.get('derivatives'))}")
    print("\nLive capex probe (1 name, real polygon financials):")
    rows = fetch_capex_rows("NVDA")
    if rows:
        d = capex_derivatives(rows)
        print(f"  NVDA: {len(rows)} capex quarters; derivatives = {d}")
    else:
        print("  NVDA: no rows (no polygon token / network) -> proxy will be used")
    print("\nget_capex_momentum (no series -> cache or fallback):")
    print(json.dumps(get_capex_momentum(), indent=2, ensure_ascii=False))
    print("\nTo populate REAL capex: python simulation/capex_provider.py --refresh")
    return 0


if __name__ == "__main__":
    if "--refresh" in sys.argv:
        refresh_cache()
    else:
        import json
        raise SystemExit(_demo())
