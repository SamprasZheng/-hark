"""Sector-flow detector (Fix E) — "資金到底吹捧哪個板塊".

Ranks the sector ETFs by relative strength vs a benchmark and detects rotation
(which sectors money is flowing INTO vs OUT OF) by comparing short- vs
medium-horizon relative strength. Exposes a 0-100 `sector_flow_score` that the
FOM scorer can fold in as a sector-momentum factor.

Design mirrors `src/sharks/scoring/fom.py`: every function takes a `closes`
DataFrame (monthly close series, columns = tickers) + an `as_of` Timestamp and
slices `closes.loc[:as_of]` so there is no lookahead. No network here — the
caller supplies prices, which keeps the logic unit-testable with synthetic data.
"""

from __future__ import annotations

from typing import Optional

import numpy as np
import pandas as pd

# The sector ETF set (XL* GICS sectors + small-cap IWM + semis SOXX, since most
# of the $hark universe maps to SOXX per cycle_bias.TICKER_SECTOR).
SECTOR_ETFS = [
    "XLK", "XLY", "XLI", "XLB", "XLF", "XLV", "XLU", "XLE",
    "XHB", "XBI", "XLRE", "XLC", "XLP", "IWM", "SOXX",
]

DEFAULT_BENCHMARK = "SPY"


def _total_return(closes: pd.DataFrame, ticker: str, as_of: pd.Timestamp, months: int) -> Optional[float]:
    """Total return of `ticker` over the trailing `months`, as of `as_of`.
    Returns None when data is missing/insufficient (caller decides how to treat)."""
    s = closes.get(ticker)
    if s is None:
        return None
    s = s.dropna()
    pre = s.loc[:as_of]
    if len(pre) < months + 1:
        return None
    last = float(pre.iloc[-1])
    prev = float(pre.iloc[-(months + 1)])
    if prev <= 0:
        return None
    return last / prev - 1.0


def relative_strength(
    closes: pd.DataFrame,
    etf: str,
    benchmark: str,
    as_of: pd.Timestamp,
    months: int = 3,
) -> Optional[float]:
    """Sector return minus benchmark return over the window. Positive = the
    sector is outperforming the index (money preferentially flowing in)."""
    sector = _total_return(closes, etf, as_of, months)
    bench = _total_return(closes, benchmark, as_of, months)
    if sector is None or bench is None:
        return None
    return sector - bench


def rank_sectors(
    closes: pd.DataFrame,
    as_of: pd.Timestamp,
    sector_etfs: Optional[list[str]] = None,
    benchmark: str = DEFAULT_BENCHMARK,
    months: int = 3,
) -> list[dict]:
    """Rank sectors by relative strength (descending). Sectors with missing data
    are dropped. Each entry: {etf, ret, rs, rank, rs_percentile}."""
    sector_etfs = sector_etfs or SECTOR_ETFS
    rows: list[dict] = []
    for etf in sector_etfs:
        rs = relative_strength(closes, etf, benchmark, as_of, months)
        if rs is None:
            continue
        ret = _total_return(closes, etf, as_of, months)
        rows.append({"etf": etf, "ret": round(ret, 4) if ret is not None else None,
                     "rs": round(rs, 4)})
    rows.sort(key=lambda r: r["rs"], reverse=True)
    n = len(rows)
    for i, row in enumerate(rows):
        row["rank"] = i + 1
        # percentile: rank 1 (best) -> ~100, last -> ~0
        row["rs_percentile"] = round((n - i - 1) / (n - 1) * 100, 1) if n > 1 else 50.0
    return rows


def detect_rotation(
    closes: pd.DataFrame,
    as_of: pd.Timestamp,
    sector_etfs: Optional[list[str]] = None,
    benchmark: str = DEFAULT_BENCHMARK,
    short_months: int = 1,
    long_months: int = 3,
) -> dict:
    """Compare short-horizon vs long-horizon relative strength to classify flow.

    - `rotating_in`  : short RS > long RS AND short RS > 0 — money accelerating in.
    - `rotating_out` : short RS < long RS AND short RS < 0 — money accelerating out.
    - `leaders`      : top-3 by long-horizon RS.
    - `laggards`     : bottom-3 by long-horizon RS.
    """
    sector_etfs = sector_etfs or SECTOR_ETFS
    long_ranked = rank_sectors(closes, as_of, sector_etfs, benchmark, long_months)
    detail: list[dict] = []
    for row in long_ranked:
        etf = row["etf"]
        rs_short = relative_strength(closes, etf, benchmark, as_of, short_months)
        rs_long = row["rs"]
        accel = (rs_short - rs_long) if rs_short is not None else None
        detail.append({
            "etf": etf, "rs_long": rs_long,
            "rs_short": round(rs_short, 4) if rs_short is not None else None,
            "accel": round(accel, 4) if accel is not None else None,
        })

    def _in(d):
        return d["rs_short"] is not None and d["accel"] is not None and d["accel"] > 0 and d["rs_short"] > 0

    def _out(d):
        return d["rs_short"] is not None and d["accel"] is not None and d["accel"] < 0 and d["rs_short"] < 0

    return {
        "as_of": as_of.isoformat()[:10],
        "benchmark": benchmark,
        "leaders": [r["etf"] for r in long_ranked[:3]],
        "laggards": [r["etf"] for r in long_ranked[-3:]],
        "rotating_in": [d["etf"] for d in detail if _in(d)],
        "rotating_out": [d["etf"] for d in detail if _out(d)],
        "detail": detail,
    }


def sector_flow_score(
    closes: pd.DataFrame,
    etf: str,
    as_of: pd.Timestamp,
    benchmark: str = DEFAULT_BENCHMARK,
) -> float:
    """0-100 sector-flow score for a single sector ETF, for use as a FOM factor.
    Blends the medium-horizon RS percentile (70%) with a short-horizon
    acceleration bonus (30%). Neutral 50 when data is missing."""
    ranked = rank_sectors(closes, as_of, benchmark=benchmark, months=3)
    pct = next((r["rs_percentile"] for r in ranked if r["etf"] == etf), None)
    if pct is None:
        return 50.0
    rs_short = relative_strength(closes, etf, benchmark, as_of, 1)
    rs_long = relative_strength(closes, etf, benchmark, as_of, 3)
    if rs_short is not None and rs_long is not None:
        accel = rs_short - rs_long
        # map accel in roughly [-0.1, +0.1] to [0, 100]
        accel_score = max(0.0, min(100.0, (accel + 0.1) / 0.2 * 100))
    else:
        accel_score = 50.0
    return round(0.7 * pct + 0.3 * accel_score, 1)


def ticker_sector_flow_score(
    closes: pd.DataFrame,
    ticker: str,
    as_of: pd.Timestamp,
    ticker_sector: dict[str, str],
    benchmark: str = DEFAULT_BENCHMARK,
) -> float:
    """Resolve a ticker to its sector ETF via the supplied mapping (e.g.
    cycle_bias.TICKER_SECTOR) and return that sector's flow score. Neutral 50
    when the ticker has no sector mapping."""
    etf = ticker_sector.get(ticker)
    if etf is None:
        return 50.0
    return sector_flow_score(closes, etf, as_of, benchmark)
