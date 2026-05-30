"""FOM Alpha variant — small/mid-cap focus, exclude mega-cap.

Per principal directive 2026-05-29:
- No mega-cap (> $500B market cap)
- 3 SP500 picks + 3 R2K picks daily
- 100-name watchlist
- Sectors with most explosive potential
- Golden cross + Trump policy + data-backed
- Alpha + upside (not stability)

Differences from main FOM:
1. Excludes mega-caps (NVDA, AAPL, MSFT, etc.)
2. Weight shuffle: momentum 30 / bubble_guard 25 / cyclic 20 / contrarian 15 / buffett 10
3. Adds golden_cross_bonus (+10 to final FOM)
4. Adds trump_policy_proximity_bonus (Compiler-tagged for specific names)
5. Splits output into SP500-eligible vs R2K-eligible buckets
"""

from __future__ import annotations

import json
import sys
import warnings
from dataclasses import asdict
from datetime import date, datetime, timezone
from pathlib import Path

warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)

import numpy as np
import pandas as pd

from sharks.scoring.fom import (
    fetch_monthly, momentum_score, contrarian_score, cyclic_score,
    quality_score, bubble_guard,
    IP_DEFENSIBILITY, INDICES, SECTOR_ETFS, CRYPTO,
)
from sharks.scoring.cycle_bias import TICKER_SECTOR

# Inline Buffett scoring (since fom.py v2 not yet deployed)
BUFFETT_3M = {
    "AAPL": 75, "KO": 75, "JNJ": 76, "PG": 73, "WMT": 71,
    "MSFT": 73, "GOOGL": 73, "META": 75, "NFLX": 69,
    "AMZN": 73, "BRK-B": 81, "MA": 69, "V": 69,
    "LMT": 79, "NOC": 78, "RTX": 76, "CAT": 72, "DE": 73,
    "GE": 67, "HON": 71, "LIN": 74, "APD": 73,
    "NVDA": 67, "TSM": 75, "ASML": 73, "AVGO": 66,
    "AMD": 57, "AMAT": 63, "LRCX": 61, "KLAC": 63,
    "ARM": 57, "CRM": 77, "NOW": 74, "ORCL": 63,
    "TSLA": 50, "INTC": 55, "OKLO": 33, "SMCI": 42,
    "VRT": 60, "ETN": 69, "GEV": 62, "EQIX": 73, "DLR": 73,
    "DHI": 68, "LEN": 68, "NEM": 63, "FCX": 65,
    "VRTX": 72, "REGN": 72, "GILD": 72,
}
def buffett_value_score(ticker):
    return BUFFETT_3M.get(ticker, 40)

# ─── Mega-cap exclusion list (rough $500B+ market cap as of 2026-05) ───
MEGACAP_EXCLUDE = {"NVDA", "AAPL", "MSFT", "GOOGL", "GOOG", "AMZN", "META", "TSLA",
                    "BRK-B", "TSM", "ORCL", "AVGO", "JPM", "V", "WMT", "MA", "ASML"}

# ─── Trump policy proximity tags (Compiler-curated) ───
# +1 = direct beneficiary of Trump policy direction; -1 = direct casualty
TRUMP_POLICY_BIAS = {
    # Defense / homeland — Trump-positive
    "LMT": +0.6, "NOC": +0.6, "RTX": +0.5, "GD": +0.5, "BA": +0.3,
    # Domestic energy — Trump-positive
    "XOM": +0.5, "CVX": +0.4, "COP": +0.4, "FCX": +0.3, "NEM": +0.3,
    # Frac/oil services
    "AESI": +0.4, "FANG": +0.4, "DVN": +0.4,
    # Nuclear / energy independence
    "UEC": +0.5, "OKLO": +0.4, "CCJ": +0.5, "NXE": +0.4, "URA": +0.4,
    # US Reshoring / specialty foundry
    "GFS": +0.7, "SKYT": +0.6, "TSMC-direct via TSM": +0.0,
    "INTC": +0.5,  # US chip manufacturing positive
    # Steel / aluminum (tariff beneficiary)
    "X": +0.5, "NUE": +0.5, "STLD": +0.5, "CLF": +0.5,
    # Container / trucking (deregulation)
    "UPS": +0.2, "FDX": +0.2, "JBHT": +0.2,
    # China / Taiwan exposed — Trump-negative
    "TSM": -0.4, "ASML": -0.3,  # export control casualty
    "BABA": -0.7, "BIDU": -0.7, "PDD": -0.7, "JD": -0.7,
    "LULU": -0.2,  # China supply chain
    # Big Tech antitrust risk — Trump-negative
    "GOOGL": -0.3, "AMZN": -0.3, "META": -0.3,
    # Healthcare reform exposure
    "UNH": -0.2, "CI": -0.2, "HUM": -0.2,
    # Bitcoin / crypto — Trump-positive
    "MSTR": +0.5, "COIN": +0.4, "RIOT": +0.4, "MARA": +0.4,
}

# ─── Expanded universe ───
# Goal: 200-300 names covering SP500-eligible mid-caps + R2K alpha candidates + consumer recovery + portfolio names + Serenity scouts
EXPANDED = list({
    # SP500 mid-cap candidates (focus on supply chain + AI infra not mega)
    "AMD", "ARM", "MU", "AMAT", "LRCX", "KLAC", "AVGO",
    # Optical / SiPh
    "LITE", "COHR", "CIEN", "ANET", "AAOI", "FN", "AXTI", "ALAB", "CRDO", "AEHR", "POET",
    # Power semis
    "NVTS", "POWI", "WOLF", "ON", "MPWR",
    # Memory
    "WDC", "STX", "SIMO",
    # Software contrarian
    "CRM", "NOW", "NFLX",
    # Defense
    "LMT", "RTX", "NOC", "GD", "BA",
    # Specialty foundry
    "GFS", "SKYT",
    # Materials
    "GLW", "AMKR", "TER",
    # Nuclear
    "UEC", "OKLO", "CCJ", "NXE", "URA",
    # Energy
    "XOM", "CVX", "COP", "AESI", "FANG", "DVN", "FCX", "NEM",
    # Industrials
    "VRT", "ETN", "GEV", "CAT", "DE", "GE", "HON",
    # Datacenter REITs
    "EQIX", "DLR", "AMT", "PLD",
    # Homebuilders
    "DHI", "LEN", "PHM", "TOL",
    # Biotech
    "VRTX", "REGN", "GILD",
    # Materials Q4
    "LIN", "APD", "DD", "ECL",
    # Consumer recovery
    "LULU", "NKE", "VFC", "VSCO", "DELL", "HPQ", "BIRK",
    # Other consumer
    "DIS", "PG", "PEP", "WMT", "KO",
    # Speciality semis
    "ALGM", "QUIK", "AOSL",
    # Other tech (portfolio)
    "ZM", "DOCN", "PATH", "APPN", "EXTR", "GRPN", "RELY",
    # Space
    "LUNR", "RKLB", "ACHR",
    # Biotech / genome
    "CRSP",
    # Industrials portfolio
    "UPS", "RRX", "IP", "SHAK",
    # Steel/Aluminum
    "X", "NUE", "STLD", "CLF",
    # Solar / clean energy
    "ARRY", "TAN", "SHLS",
    # Renewables
    "TAC",
    # Misc
    "MSTR", "COIN", "RIOT", "MARA",
    # Serenity scouts (small-cap chokepoint candidates)
    "SOI",  # Soitec
    "VLN",  # Valens Semi
    "NBIS", # Nebius Group
    "RPID", # Raspberry Pi
    # Other Serenity-style small-cap
    "SIVB",  # Note: SIVB was acquired (SVB collapse); just for hist
    # Crypto miners
    "BTBT", "CIFR", "WULF", "BITF",
    # SaaS contrarian
    "CRWD", "ZS", "PANW", "DDOG", "MDB",
})


def market_cap_filter(closes: pd.DataFrame, ticker: str, as_of: pd.Timestamp) -> bool:
    """Exclude tickers in MEGACAP_EXCLUDE list. (yfinance lookup for true MC is slow; use list.)"""
    return ticker not in MEGACAP_EXCLUDE


def golden_cross_bonus(closes: pd.DataFrame, ticker: str, as_of: pd.Timestamp) -> float:
    """+10 if 20MA × 60MA golden cross within last 3 months."""
    s = closes.get(ticker)
    if s is None or s.dropna().empty:
        return 0.0
    s = s.dropna().loc[:as_of]
    if len(s) < 6:
        return 0.0
    # Use monthly bars; roughly: 5-month-MA vs 12-month-MA as proxies for 20d/60d
    ma_short = s.rolling(5).mean()
    ma_long = s.rolling(12).mean()
    # Check if MA_short crossed above MA_long in last 3 months
    recent_short = ma_short.iloc[-3:]
    recent_long = ma_long.iloc[-3:]
    older_short = ma_short.iloc[-4] if len(ma_short) > 3 else None
    older_long = ma_long.iloc[-4] if len(ma_long) > 3 else None
    if older_short is None or older_long is None or pd.isna(older_short) or pd.isna(older_long):
        return 0.0
    if (recent_short.iloc[-1] > recent_long.iloc[-1]) and (older_short <= older_long):
        return 10.0
    return 0.0


def trump_policy_bonus(ticker: str) -> float:
    """Trump policy proximity bonus, scaled."""
    bias = TRUMP_POLICY_BIAS.get(ticker, 0.0)
    return bias * 10  # +1 bias → +10 to FOM


def score_ticker_alpha(closes, ticker, as_of):
    mom = momentum_score(closes, ticker, as_of)
    con = contrarian_score(closes, ticker, as_of)
    cyc, cyc_b = cyclic_score(ticker, as_of)
    qual = quality_score(closes, ticker, as_of)
    bub = bubble_guard(closes, ticker, as_of)
    buf = buffett_value_score(ticker)
    gc = golden_cross_bonus(closes, ticker, as_of)
    trump = trump_policy_bonus(ticker)
    # Alpha weights: momentum 30 / bubble_guard 25 / cyclic 20 / contrarian 15 / buffett 10
    base = (
        0.30 * mom + 0.25 * ((bub + 100) / 2) + 0.20 * cyc
        + 0.15 * con + 0.10 * buf
    )
    final = base + gc + trump
    return {
        "ticker": ticker, "as_of": as_of.isoformat()[:10],
        "sector_etf": TICKER_SECTOR.get(ticker),
        "momentum": round(mom, 1), "contrarian": round(con, 1),
        "cyclic": round(cyc, 1), "quality": round(qual, 1),
        "bubble_guard": round(bub, 1), "buffett_value": round(buf, 1),
        "golden_cross_bonus": gc, "trump_policy_bonus": round(trump, 1),
        "base_score": round(base, 2), "final_fom_alpha": round(final, 2),
        "ip_defensibility": IP_DEFENSIBILITY.get(ticker, 50),
    }


def rank_alpha(closes, universe, as_of):
    results = []
    for t in universe:
        if not market_cap_filter(closes, t, as_of):
            continue
        if t not in closes.columns or closes[t].dropna().empty:
            continue
        r = score_ticker_alpha(closes, t, as_of)
        results.append(r)
    results.sort(key=lambda x: x["final_fom_alpha"], reverse=True)
    return results


def main(out_dir: Path) -> int:
    out_dir.mkdir(parents=True, exist_ok=True)
    today = pd.Timestamp("2026-05-29")
    print(f"FOM Alpha scoring as of {today.date()}, universe {len(EXPANDED)} tickers", file=sys.stderr)
    closes = fetch_monthly(EXPANDED + INDICES, "2019-12-01", "2026-05-29")
    print(f"  data: {len(closes.columns)} tickers", file=sys.stderr)
    results = rank_alpha(closes, EXPANDED, today)

    # Split SP500 vs R2K (rough: large = "SP500 eligible", small = "R2K eligible")
    # Without true market-cap data, use a heuristic: top-1/3 by 12m return = larger; bottom-2/3 may include smaller
    # In practice, all in our universe could be SP500 or R2K members
    # Compiler-curated split for now:
    SP500_HINT = {"AMD", "AVGO", "ARM", "MU", "AMAT", "LRCX", "KLAC", "ANET", "TSM",
                   "CRM", "NOW", "NFLX", "LMT", "RTX", "NOC", "GD", "CAT", "DE", "GE", "HON",
                   "EQIX", "DLR", "AMT", "PLD", "DHI", "LEN", "VRTX", "REGN", "GILD",
                   "LIN", "APD", "VRT", "ETN", "GEV", "DELL", "HPQ", "DIS", "PG", "PEP", "KO",
                   "FCX", "NEM", "XOM", "CVX", "COP", "WMT", "MA", "V", "UPS", "BA", "IP", "RRX",
                   "X", "NUE", "STLD", "LULU", "NKE", "GFS", "PANW", "DDOG", "MDB", "CRWD", "ZS",
                   "CCJ", "INTC", "PHM", "TOL"}
    R2K_HINT = {t for t in [r["ticker"] for r in results] if t not in SP500_HINT}

    top3_sp500 = [r for r in results if r["ticker"] in SP500_HINT][:3]
    top3_r2k = [r for r in results if r["ticker"] in R2K_HINT][:3]
    top_100 = results[:100]

    report = {
        "as_of": datetime.now(timezone.utc).isoformat(),
        "schema_version": 1,
        "universe_size": len(EXPANDED),
        "scoring_method": "alpha — momentum 30 / bubble 25 / cyclic 20 / contrarian 15 / buffett 10 + golden_cross + trump_policy bonuses",
        "exclusions": list(MEGACAP_EXCLUDE),
        "top_3_sp500_eligible": top3_sp500,
        "top_3_r2k_eligible": top3_r2k,
        "top_100_candidates": top_100,
        "trump_positive_top10": sorted(
            [r for r in results if r.get("trump_policy_bonus", 0) > 0],
            key=lambda x: x["final_fom_alpha"], reverse=True)[:10],
        "golden_cross_recent": [r for r in results if r.get("golden_cross_bonus", 0) > 0],
    }
    out_path = out_dir / f"fom-alpha-{today.date()}.json"
    out_path.write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")
    print(f"wrote {out_path}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main(Path("outputs")))
