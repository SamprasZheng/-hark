#!/usr/bin/env python3
"""
Trading Society -- bulk Polygon financials pull -> local parquet (review A + D)

PPST Declaration (this PROGRAM):
- PROJECT: Trading Society
- PROGRAM: simulation/data_pipeline/pull_financials.py
- SKILL:   bulk historical fundamentals pull + PIT local parquet cache
- TARGET:  Pull the REAL fields Polygon actually exposes (income statement,
           balance sheet, cash-flow aggregates) for a ticker list and store them
           to a dated parquet under data/financials/. PIT via filing_date.
           Maximise data captured during the paid window; reads come from the
           local parquet thereafter (reduces future API dependency).

IMPORTANT DATA REALITY (verified 2026-06-14 on the PAID tier):
- Polygon's standardized financials have **no capex line item** for any company
  (only operating/investing/financing cash-flow aggregates). So we capture what is
  real -- revenue, net_income, gross_profit, OCF, investing_cf, equity, assets,
  long_term_debt -- and derive capex-intensity from |investing_cf| downstream
  (clearly flagged). Pure capex is NOT available from Polygon.

Run:
  python -m simulation.data_pipeline.pull_financials            # default universe
  python -m simulation.data_pipeline.pull_financials NVDA KLAC  # specific tickers
"""

from __future__ import annotations

import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))
import simulation._env  # noqa: E402,F401  (loads .env)

SAVE_DIR = _ROOT / "data" / "financials"


def _src():
    try:
        from sharks.data.polygon_financials import BASE, _token
        return BASE, _token
    except Exception:
        sys.path.insert(0, str(_ROOT / "src"))
        from sharks.data.polygon_financials import BASE, _token
        return BASE, _token


def _v(fin: dict, section: str, *keys: str) -> Optional[float]:
    sec = fin.get(section) or {}
    for k in keys:
        cell = sec.get(k)
        if isinstance(cell, dict) and cell.get("value") is not None:
            try:
                return float(cell["value"])
            except Exception:
                pass
    return None


def parse_extended(result: dict) -> Dict[str, Any]:
    """Extract the REAL fields Polygon exposes (PIT anchor = filing_date)."""
    fin = result.get("financials") or {}
    return {
        "fiscal": f"{result.get('fiscal_year')}{result.get('fiscal_period')}",
        "end_date": result.get("end_date"),
        "filing_date": result.get("filing_date"),
        "revenue": _v(fin, "income_statement", "revenues"),
        "gross_profit": _v(fin, "income_statement", "gross_profit"),
        "net_income": _v(fin, "income_statement", "net_income_loss",
                         "net_income_loss_attributable_to_parent"),
        "ocf": _v(fin, "cash_flow_statement", "net_cash_flow_from_operating_activities",
                  "net_cash_flow_from_operating_activities_continuing"),
        "investing_cf": _v(fin, "cash_flow_statement",
                           "net_cash_flow_from_investing_activities"),
        "equity": _v(fin, "balance_sheet", "equity"),
        "assets": _v(fin, "balance_sheet", "assets"),
        "current_assets": _v(fin, "balance_sheet", "current_assets"),
        "current_liabilities": _v(fin, "balance_sheet", "current_liabilities"),
        "long_term_debt": _v(fin, "balance_sheet", "long_term_debt"),
        "fixed_assets": _v(fin, "balance_sheet", "fixed_assets"),
    }


def fetch_extended(ticker: str, limit: int = 20) -> List[Dict[str, Any]]:
    import requests
    BASE, _token = _src()
    params = {"ticker": ticker, "timeframe": "quarterly", "limit": limit,
              "order": "desc", "apiKey": _token()}
    for attempt in (1, 2, 3):
        try:
            r = requests.get(BASE, params=params, timeout=30)
            if r.status_code == 429:
                time.sleep(8 * attempt)
                continue
            r.raise_for_status()
            rows = [parse_extended(x) for x in r.json().get("results") or []]
            return [{"ticker": ticker, **row} for row in rows]
        except Exception:
            time.sleep(2 * attempt)
    return []


def default_universe() -> List[str]:
    try:
        from simulation.universe_competition import build_universe
        from sharks.scoring.fom import DEFAULT_UNIVERSE
        u = set(build_universe(max_names=400)["tickers"]) | set(DEFAULT_UNIVERSE)
        return sorted(u)
    except Exception:
        from simulation.universe_competition import build_universe
        return sorted(build_universe(max_names=300)["tickers"])


def pull(tickers: List[str], sleep_s: float = 0.7, limit: int = 20) -> Path:
    import pandas as pd
    SAVE_DIR.mkdir(parents=True, exist_ok=True)
    rows: List[Dict[str, Any]] = []
    ok = miss = 0
    for n, t in enumerate(tickers):
        if n:
            time.sleep(sleep_s)
        recs = fetch_extended(t, limit=limit)
        if recs:
            rows.extend(recs)
            ok += 1
        else:
            miss += 1
        if n % 25 == 0:
            print(f"  [{n}/{len(tickers)}] {t}: {len(recs)} quarters "
                  f"(ok={ok} miss={miss})", file=sys.stderr)
    df = pd.DataFrame(rows)
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    path = SAVE_DIR / f"financials-{stamp}.parquet"
    df.to_parquet(path, index=False)
    print(f"wrote {len(df)} rows ({ok} tickers, {miss} missing) -> {path}",
          file=sys.stderr)
    return path


def main(argv: Optional[List[str]] = None) -> int:
    args = (argv if argv is not None else sys.argv[1:])
    tickers = [a.upper() for a in args] if args else default_universe()
    print(f"Pulling Polygon financials for {len(tickers)} tickers "
          f"(real fields: rev/NI/gross/OCF/investing_cf/equity/assets/LT-debt; "
          f"NO capex line -- Polygon limitation)", file=sys.stderr)
    pull(tickers)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
