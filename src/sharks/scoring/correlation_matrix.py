"""Daily correlation tracker — your portfolio vs hunting grounds.

Compute monthly-return correlations:
  - Your holdings (NVDA + portfolio 1 + portfolio 2)
  - Taiwan stocks (.TW, .TWO)
  - Commodities (gold, oil, copper, uranium)
  - Bear market proxies (TLT, VIX, gold/silver ratio)

Identify:
  - Highest diversifiers (lowest correlation with NVDA)
  - Confirming assets (highest correlation, leading indicators)
  - Bear market hedges
"""

from __future__ import annotations

import json
import sys
import warnings
from datetime import datetime, timezone
from pathlib import Path

warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)

import numpy as np
import pandas as pd
import yfinance as yf

# Your actual portfolio + key tracking tickers
PORTFOLIO_HOLDINGS = ["NVDA", "AAPL", "MSFT", "META", "DELL", "AESI", "UEC", "TSLA",
                      "NKE", "LULU", "PG", "PEP", "ORCL", "STZ", "NOW", "CRM",
                      "ARRY", "ENPH", "DIS", "BIRK", "GFS"]

HUNTING_GROUND = {
    "TSM": "TSMC ADR",
    "ASML": "ASML",
    "AVGO": "Broadcom",
    "LMT": "Lockheed Martin",
    # Taiwan large
    "2330.TW": "TSMC TW",
    "2454.TW": "MediaTek",
    "2317.TW": "Foxconn",
    "3008.TW": "LARGAN",
    "2308.TW": "Delta",
    "3231.TW": "Wistron (AI server)",
    "2382.TW": "Quanta",
    "3034.TW": "Novatek",
    "6669.TW": "Win Semi",
    # Taiwan OTC
    "6515.TWO": "Aspeed (BMC)",
    "8086.TWO": "King Slide (server rails)",
    # Commodities
    "GLD": "Gold",
    "SLV": "Silver",
    "USO": "Crude Oil",
    "COPX": "Copper Miners",
    "URA": "Uranium",
    "LIT": "Lithium",
    "DBA": "Agriculture",
    # Bear market proxies
    "TLT": "20+y Treasury",
    "VXX": "VIX Futures",
    "SH": "Inverse SPY",
    "BTC-USD": "Bitcoin",
}


def fetch_monthly(tickers, start, end):
    raw = yf.download(tickers, start=start, end=end, interval="1mo",
                     auto_adjust=True, progress=False, group_by="ticker", threads=True)
    closes = pd.DataFrame()
    for t in tickers:
        try:
            if isinstance(raw.columns, pd.MultiIndex):
                s = raw[t]["Close"]
            else:
                s = raw["Close"]
            closes[t] = s
        except (KeyError, ValueError):
            pass
    if closes.index.tz is not None:
        closes.index = closes.index.tz_localize(None)
    return closes.sort_index()


def main():
    out_dir = Path("outputs")
    today = pd.Timestamp("2026-05-30")
    print(f"Correlation matrix as of {today.date()}", file=sys.stderr)

    all_tickers = list(set(PORTFOLIO_HOLDINGS + list(HUNTING_GROUND.keys())))
    closes = fetch_monthly(all_tickers, "2023-01-01", "2026-05-30")
    print(f"  data: {len(closes.columns)} tickers", file=sys.stderr)

    # Monthly returns
    returns = closes.pct_change().dropna(how="all")

    # Full correlation
    corr = returns.corr()

    # NVDA correlation specifically (you're 80% NVDA)
    nvda_corr = corr.get("NVDA", pd.Series()).drop("NVDA", errors="ignore").sort_values(ascending=False)

    # Find diversifiers (correlation < 0.3 with NVDA, > 0 baseline)
    diversifiers = nvda_corr[nvda_corr < 0.3].sort_values()  # ascending: lowest first

    # Find confirmers (correlation > 0.7 = redundant exposure)
    confirmers = nvda_corr[nvda_corr > 0.7]

    # Sector-by-sector correlation
    portfolio_corr = corr.loc[PORTFOLIO_HOLDINGS, PORTFOLIO_HOLDINGS] if all(t in corr.index for t in PORTFOLIO_HOLDINGS) else pd.DataFrame()

    # Bear hedge effectiveness (negative correlation with NVDA = good hedge)
    bear_proxies = ["TLT", "VXX", "SH", "GLD"]
    bear_correls = {}
    for bp in bear_proxies:
        if bp in nvda_corr.index:
            bear_correls[bp] = round(float(nvda_corr[bp]), 3)

    # Taiwan correlation specifically
    taiwan_correls = {}
    for tw in [t for t in nvda_corr.index if ".TW" in t or ".TWO" in t]:
        taiwan_correls[tw] = round(float(nvda_corr[tw]), 3)

    # Commodity correlation
    commod_correls = {}
    for c in ["GLD", "SLV", "USO", "COPX", "URA", "LIT", "DBA"]:
        if c in nvda_corr.index:
            commod_correls[c] = round(float(nvda_corr[c]), 3)

    report = {
        "as_of": datetime.now(timezone.utc).isoformat(),
        "schema_version": 1,
        "data_window": "2023-01-01 to 2026-05-30 (monthly returns)",
        "nvda_correlation_full_sorted_desc": {t: round(float(v), 3) for t, v in nvda_corr.head(30).items()},
        "highest_diversifiers_vs_nvda": {t: round(float(v), 3) for t, v in diversifiers.head(15).items()},
        "redundant_correlated_with_nvda_above_70": {t: round(float(v), 3) for t, v in confirmers.head(10).items()},
        "bear_hedge_effectiveness": bear_correls,
        "taiwan_stocks_vs_nvda_correlation": taiwan_correls,
        "commodities_vs_nvda_correlation": commod_correls,
        "interpretation_guide": {
            "high_positive (>0.7)": "redundant - same direction as NVDA, adds risk not diversification",
            "moderate_positive (0.3-0.7)": "co-trend but some independence",
            "low (0-0.3)": "good diversifier; offsets NVDA-specific risk",
            "negative (<0)": "true hedge; gains when NVDA falls",
        },
    }
    out_path = out_dir / f"correlation-matrix-{today.date()}.json"
    out_path.write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")
    print(f"wrote {out_path}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
