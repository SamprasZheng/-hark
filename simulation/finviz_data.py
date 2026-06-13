#!/usr/bin/env python3
"""
Trading Society -- Finviz Elite data source (real sector / industry / valuation)

PPST Declaration (this PROGRAM):
- PROJECT: Trading Society
- PROGRAM: simulation/finviz_data.py
- SKILL:   pull REAL sector/industry + valuation from Finviz Elite export API
- TARGET:  Replace the hardcoded sector map with REAL Finviz Industry/Sector
           labels (for the concentration cap) and provide a real valuation
           snapshot (market cap, P/E). Cached; never-raise -> empty on failure.

Probe result (2026-06-14): Finviz Elite key is live; the export returns
Ticker / Company / Sector / Industry / Country / Market Cap / P/E / Volume /
Price / Change for the requested tickers. That gives real industry buckets for
the concentration cap and real per-name valuation.

Governance: recommend-only data layer. The token comes only from .env
(FINVIZ_ELITE_API_KEY), is never printed, and is redacted from any surfaced URL
(the repo's finviz_elite.redact()).

Run: python simulation/finviz_data.py        # live probe (sector map + valuation)
"""

from __future__ import annotations

import json
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))
import simulation._env  # noqa: E402,F401  (loads .env on import)
CACHE_DIR = REPO / "outputs"
_UA = {"User-Agent": "Mozilla/5.0"}


def _src():
    try:
        from sharks.data.finviz_elite import build_export_url, parse_csv, _token
        return build_export_url, parse_csv, _token
    except Exception:
        import sys
        sys.path.insert(0, str(REPO / "src"))
        from sharks.data.finviz_elite import build_export_url, parse_csv, _token
        return build_export_url, parse_csv, _token


def fetch_rows(tickers: Optional[List[str]] = None, filters: str = "",
               view: str = "152") -> List[Dict[str, Any]]:
    """Fetch Finviz export rows for a ticker list or a filter screen. never-raise."""
    try:
        build_export_url, parse_csv, _token = _src()
        kw: Dict[str, Any] = {"token": _token(), "view": view}
        if tickers:
            kw["tickers"] = ",".join(tickers)
        url = build_export_url(filters, **kw)
        req = urllib.request.Request(url, headers=_UA)
        txt = urllib.request.urlopen(req, timeout=40).read().decode("utf-8", "ignore")
        return parse_csv(txt)
    except Exception:
        return []


def _num(s: Any) -> Optional[float]:
    try:
        return float(str(s).replace(",", "").replace("%", "").strip())
    except Exception:
        return None


def get_sector_map(tickers: List[str], use_industry: bool = True
                   ) -> Dict[str, str]:
    """{ticker: industry-or-sector} from real Finviz data. {} on failure.
    Industry is finer (e.g. 'Semiconductors' vs 'Technology') -> better for an
    industry concentration cap (review item)."""
    rows = fetch_rows(tickers=tickers)
    out: Dict[str, str] = {}
    for r in rows:
        tk = (r.get("Ticker") or "").strip()
        if not tk:
            continue
        label = (r.get("Industry") if use_industry else r.get("Sector")) or \
            r.get("Sector") or "Unknown"
        out[tk] = label.strip()
    if out:
        try:
            path = CACHE_DIR / f"finviz-sectors-{datetime.now(timezone.utc).strftime('%Y-%m-%d')}.json"
            path.parent.mkdir(exist_ok=True)
            path.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
        except Exception:
            pass
    return out


def get_market_caps(tickers: List[str]) -> Dict[str, float]:
    """{ticker: market_cap_in_billions} from real Finviz data. {} on failure.
    (Finviz 'Market Cap' export is already in $millions for most views.)"""
    rows = fetch_rows(tickers=tickers)
    out: Dict[str, float] = {}
    for r in rows:
        tk = (r.get("Ticker") or "").strip()
        mc = _num(r.get("Market Cap"))
        if tk and mc:
            # Finviz export Market Cap is in $millions -> convert to billions.
            out[tk] = round(mc / 1000.0, 3)
    return out


def get_valuation_snapshot(filters: str = "cap_largeover") -> Dict[str, Any]:
    """Real valuation context from a large-cap screen: median P/E, aggregate
    market cap of the screen, count. Not a true Buffett Indicator (would need the
    whole market), but a real, auditable valuation signal."""
    rows = fetch_rows(filters=filters)
    pes = [v for v in (_num(r.get("P/E")) for r in rows) if v and v > 0]
    caps = [v for v in (_num(r.get("Market Cap")) for r in rows) if v and v > 0]
    pes.sort()
    median_pe = pes[len(pes) // 2] if pes else None
    return {
        "n_names": len(rows),
        "median_pe": round(median_pe, 1) if median_pe else None,
        "high_pe_share": round(sum(1 for v in pes if v > 30) / len(pes), 3) if pes else None,
        "aggregate_market_cap_screen_bn": round(sum(caps), 1) if caps else None,
        "filters": filters,
        "source": "finviz_elite" if rows else "unavailable",
        "note": "Real per-name valuation from Finviz Elite. Aggregate is the screen "
                "only, not total-market (use FRED Wilshire/GDP for a true Buffett "
                "Indicator).",
    }


def _demo() -> int:
    print("=" * 72)
    print("finviz_data self-test (live Finviz Elite)")
    print("=" * 72)
    sample = ["NVDA", "KLAC", "ONTO", "ARM", "ROKU", "KO", "LMT", "DXYZ", "RKLB"]
    smap = get_sector_map(sample)
    print(f"\nSector/Industry map ({len(smap)} resolved):")
    for t in sample:
        print(f"  {t:<6} {smap.get(t, '(not resolved)')}")
    print("\nValuation snapshot (large-cap screen):")
    print(json.dumps(get_valuation_snapshot(), indent=2, ensure_ascii=False))
    if not smap:
        print("\n(Empty -> Finviz key/network unavailable; callers fall back.)")
    return 0


if __name__ == "__main__":
    raise SystemExit(_demo())
