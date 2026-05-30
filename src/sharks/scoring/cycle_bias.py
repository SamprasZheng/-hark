"""Multi-scale cycle bias scorer.

Inputs: as_of date (and optionally sector ETF).
Output: combined_cycle_bias ∈ [-1, +1] with component breakdown.

Empirical bases:
  - BTC halving phases — wiki/06_cycle_framework.md §1
  - Presidential cycle Y1/Y2/Y3/Y4 — wiki/06_cycle_framework.md §2
  - Calendar seasonality (SPX monthly) — wiki/06_cycle_framework.md §3
  - Sector seasonality — wiki/06_cycle_framework.md §4

Default weights heavy on Presidential + Calendar; BTC + Sector are modifiers.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import date, datetime
from typing import Optional

# ─── BTC halving cycle ───
# Most recent halving and projected next
BTC_LAST_HALVING = date(2024, 4, 19)
BTC_NEXT_HALVING = date(2028, 4, 1)  # estimated

def btc_cycle_bias(as_of: date) -> float:
    """+0.8 cycle bull, 0 peak, -0.6 bear, +0.4 pre-halving accumulation."""
    months_post = (as_of.year * 12 + as_of.month) - (
        BTC_LAST_HALVING.year * 12 + BTC_LAST_HALVING.month
    )
    if months_post < 0:  # before halving (shouldn't happen given hardcoded)
        return 0.4
    if months_post < 12:
        return -0.2  # range-bound staging
    if months_post < 20:
        return 0.8  # Phase B cycle bull
    if months_post < 30:
        return 0.0  # Phase C peak window
    if months_post < 42:
        return -0.6  # Phase D bear market
    return 0.4  # Phase E pre-next-halving accumulation


# ─── Presidential cycle ───
PRES_CYCLE = {
    2017: ("Trump_1", 1), 2018: ("Trump_1", 2), 2019: ("Trump_1", 3), 2020: ("Trump_1", 4),
    2021: ("Biden", 1), 2022: ("Biden", 2), 2023: ("Biden", 3), 2024: ("Biden", 4),
    2025: ("Trump_2", 1), 2026: ("Trump_2", 2), 2027: ("Trump_2", 3), 2028: ("Trump_2", 4),
}

def presidential_cycle_bias(as_of: date) -> float:
    """Y1 +0.6 / Y2 -0.4 pre-Nov, +0.8 post-Nov / Y3 +0.7 / Y4 +0.2"""
    cycle = PRES_CYCLE.get(as_of.year)
    if cycle is None:
        return 0.0
    _, cy = cycle
    if cy == 1:
        return 0.6
    if cy == 2:
        # Pre-midterm caution; post-midterm-Nov bounce (100% historical since 1938)
        return 0.8 if as_of.month >= 11 else -0.4
    if cy == 3:
        return 0.7
    if cy == 4:
        return 0.2
    return 0.0


# ─── Calendar seasonality (SPX-derived) ───
SPX_MONTH_BIAS = {
    1: 0.1, 2: 0.0, 3: 0.1, 4: 0.5, 5: 0.5, 6: 0.0,
    7: 0.5, 8: -0.3, 9: -0.6, 10: 0.2, 11: 0.7, 12: 0.5,
}

def calendar_bias(as_of: date) -> float:
    return SPX_MONTH_BIAS[as_of.month]


# ─── Sector ETF best/worst months ───
# Format: ETF -> (best_month, best_bias, worst_month, worst_bias)
SECTOR_MONTH_BIAS = {
    "XLK":  {"best": (7, 0.7), "worst": (9, -0.4)},  # Tech
    "XLY":  {"best": (7, 0.6), "worst": (6, -0.1)},  # Discretionary
    "XLP":  {"best": (7, 0.5), "worst": (9, -0.4)},  # Staples
    "XLE":  {"best": (4, 0.6), "worst": (8, -0.4)},  # Energy
    "XLF":  {"best": (7, 0.7), "worst": (6, -0.4)},  # Financials
    "XLI":  {"best": (11, 0.7), "worst": (6, -0.4)}, # Industrials
    "XLV":  {"best": (7, 0.6), "worst": (9, -0.4)},  # Healthcare
    "XLU":  {"best": (7, 0.7), "worst": (9, -0.4)},  # Utilities
    "XLB":  {"best": (11, 0.7), "worst": (9, -0.5)}, # Materials
    "XLRE": {"best": (7, 0.8), "worst": (9, -0.6)},  # Real Estate
    "XLC":  {"best": (11, 0.6), "worst": (9, -0.5)}, # Communications
    "SOXX": {"best": (5, 0.7), "worst": (9, -0.3)},  # Semis
    "XBI":  {"best": (11, 0.6), "worst": (3, -0.3)}, # Biotech
    "ITA":  {"best": (11, 0.5), "worst": (3, -0.2)}, # Defense
    "TAN":  {"best": (1, 0.6), "worst": (10, -0.5)}, # Solar
    "HERO": {"best": (11, 0.6), "worst": (9, -0.5)}, # Gaming
    "XHB":  {"best": (11, 0.8), "worst": (6, -0.4)}, # Homebuilders
}

# Ticker → primary sector ETF (rough mapping; expand as needed)
TICKER_SECTOR = {
    # Mag 7
    "NVDA": "SOXX", "AAPL": "XLK", "MSFT": "XLK", "GOOGL": "XLC",
    "META": "XLC", "AMZN": "XLY", "TSLA": "XLY",
    # Supply chain tier 2
    "TSM": "SOXX", "ASML": "SOXX", "AVGO": "SOXX", "AMD": "SOXX",
    "ARM": "SOXX", "MU": "SOXX", "AMAT": "SOXX", "LRCX": "SOXX", "INTC": "SOXX",
    # Memory
    "WDC": "SOXX", "STX": "SOXX", "SIMO": "SOXX",
    # Optical
    "LITE": "SOXX", "COHR": "SOXX", "CIEN": "XLK", "ANET": "XLK",
    "AAOI": "SOXX", "FN": "SOXX",
    # SiPh / Phase 3
    "AXTI": "SOXX", "ALAB": "SOXX", "CRDO": "SOXX", "AEHR": "SOXX", "POET": "SOXX",
    # Power semis (Serenity-inspired adds)
    "NVTS": "SOXX", "POWI": "SOXX", "WOLF": "SOXX", "ON": "SOXX", "MPWR": "SOXX",
    # Contrarian software
    "CRM": "XLK", "NOW": "XLK", "NFLX": "XLC",
    # Bubble watchlist
    "ORCL": "XLK", "OKLO": "XLU", "SMCI": "XLK",
    # Datacenter infrastructure
    "VRT": "XLI", "ETN": "XLI", "GEV": "XLI", "ASMI": "SOXX", "KLAC": "SOXX",
    # Materials / substrates
    "GLW": "XLK",  # Corning (glass)
    "AMKR": "SOXX",  # Amkor (packaging)
    # Defense
    "LMT": "ITA", "RTX": "ITA", "NOC": "ITA",
    # Defensive / Beta anchors
    "JNJ": "XLV", "PG": "XLP", "KO": "XLP", "WMT": "XLP",
    # Misc strong R2K candidates
    "RKLB": "ITA",  # Rocket Lab
    "ACHR": "ITA",  # Archer Aviation
    "CRSP": "XBI",  # CRISPR
}


def sector_bias(ticker: str, as_of: date) -> float:
    """Return sector-month bias for a ticker."""
    sector_etf = TICKER_SECTOR.get(ticker)
    if sector_etf is None:
        return 0.0
    rules = SECTOR_MONTH_BIAS.get(sector_etf)
    if rules is None:
        return 0.0
    if as_of.month == rules["best"][0]:
        return rules["best"][1]
    if as_of.month == rules["worst"][0]:
        return rules["worst"][1]
    # Soft September across most sectors
    if as_of.month == 9 and sector_etf not in ("XLE",):
        return -0.2
    return 0.0


# ─── Aggregation ───
@dataclass
class CycleBiasResult:
    as_of: str
    ticker: Optional[str]
    sector_etf: Optional[str]
    btc: float
    presidential: float
    calendar: float
    sector: float
    combined: float
    weights: dict


def combined_cycle_bias(
    as_of: date,
    ticker: Optional[str] = None,
    weights: dict = None,
) -> CycleBiasResult:
    """Combine all four scales into a single bias ∈ [-1, +1]."""
    if weights is None:
        weights = {"btc": 0.15, "presidential": 0.30, "calendar": 0.30, "sector": 0.25}

    btc = btc_cycle_bias(as_of)
    pres = presidential_cycle_bias(as_of)
    cal = calendar_bias(as_of)
    sec = sector_bias(ticker, as_of) if ticker else 0.0

    combined = (
        btc * weights["btc"]
        + pres * weights["presidential"]
        + cal * weights["calendar"]
        + sec * weights["sector"]
    )
    # Clip
    combined = max(-1.0, min(1.0, combined))

    sector_etf = TICKER_SECTOR.get(ticker) if ticker else None
    return CycleBiasResult(
        as_of=as_of.isoformat(),
        ticker=ticker,
        sector_etf=sector_etf,
        btc=btc,
        presidential=pres,
        calendar=cal,
        sector=sec,
        combined=combined,
        weights=weights,
    )


if __name__ == "__main__":
    # Smoke test: print current bias for sample tickers
    today = date(2026, 5, 29)
    print(f"Cycle bias as of {today}:\n")
    for t in ["NVDA", "TSLA", "ORCL", "XHB", "MU", "CRM"]:
        r = combined_cycle_bias(today, t)
        print(f"  {t:6} ({r.sector_etf or '—':4}): "
              f"BTC={r.btc:+.2f} Pres={r.presidential:+.2f} Cal={r.calendar:+.2f} "
              f"Sec={r.sector:+.2f} → combined={r.combined:+.3f}")
