"""Long-cycle validator: BTC 4yr halving cycle + US Presidential cycle + monthly seasonality.

Pulls extended history via yfinance (free, key-less) and validates:
  - BTC halving-relative returns (months 0, 12, 18, 24 post each halving)
  - SPX returns by Presidential cycle year (Y1, Y2/midterm, Y3, Y4)
  - SPX monthly-of-year average returns (Sell in May, Santa rally, Sept weakness)
  - Sector ETF monthly seasonality
"""

from __future__ import annotations

import json
import math
import sys
import warnings
from datetime import datetime, timezone
from pathlib import Path

warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)

import numpy as np
import pandas as pd
import yfinance as yf

OUT = Path("outputs")
TODAY = "2026-05-29"

# ─── Bitcoin halving cycle ─────────────────────────────────────────
HALVINGS = {
    "h2012": "2012-11-28",
    "h2016": "2016-07-09",
    "h2020": "2020-05-11",
    "h2024": "2024-04-19",
    "h2028_est": "2028-04-01",  # estimated
}

# ─── US Presidential cycle (Year 1 = inauguration year) ────────────
# Year 1 = post-election (inauguration); Year 2 = midterm; Year 3 = pre-election; Year 4 = election
PRES_CYCLE_YEARS = {
    # election: (Y1, Y2_midterm, Y3, Y4)
    "Reagan_1": (1981, 1982, 1983, 1984),
    "Reagan_2": (1985, 1986, 1987, 1988),
    "GHW_Bush": (1989, 1990, 1991, 1992),
    "Clinton_1": (1993, 1994, 1995, 1996),
    "Clinton_2": (1997, 1998, 1999, 2000),
    "GW_Bush_1": (2001, 2002, 2003, 2004),
    "GW_Bush_2": (2005, 2006, 2007, 2008),
    "Obama_1": (2009, 2010, 2011, 2012),
    "Obama_2": (2013, 2014, 2015, 2016),
    "Trump_1": (2017, 2018, 2019, 2020),
    "Biden": (2021, 2022, 2023, 2024),
    "Trump_2": (2025, 2026, 2027, 2028),  # current
}

# ─── Sector ETFs for seasonality ────────────────────────────────────
SECTOR_ETFS = {
    "XLK": "Technology",
    "XLY": "Consumer Discretionary",
    "XLP": "Consumer Staples",
    "XLE": "Energy",
    "XLF": "Financials",
    "XLI": "Industrials",
    "XLV": "Healthcare",
    "XLU": "Utilities",
    "XLB": "Materials",
    "XLRE": "Real Estate",
    "XLC": "Communication Services",
    "SOXX": "Semiconductors",
    "XBI": "Biotech",
    "ITA": "Aerospace/Defense",
    "TAN": "Solar",
    "HERO": "Gaming/Esports",
    "XHB": "Homebuilders",
}


def fetch_monthly(ticker: str, start: str, end: str) -> pd.Series:
    """Return monthly close series."""
    try:
        df = yf.download(
            ticker, start=start, end=end, interval="1mo",
            auto_adjust=True, progress=False, threads=False,
        )
        if df.empty:
            return pd.Series(dtype=float, name=ticker)
        s = df["Close"]
        if isinstance(s, pd.DataFrame):
            s = s.iloc[:, 0]
        if s.index.tz is not None:
            s.index = s.index.tz_localize(None)
        s.name = ticker
        return s
    except Exception as e:
        print(f"  WARN {ticker}: {e}", file=sys.stderr)
        return pd.Series(dtype=float, name=ticker)


def btc_halving_cycle_returns(btc: pd.Series) -> dict:
    """For each halving, compute return at +12, +18, +24, +30, +36 months."""
    out = {}
    for label, date_str in HALVINGS.items():
        if label == "h2028_est":
            continue
        h_date = pd.Timestamp(date_str)
        # Find closest month-end on or after halving
        try:
            entry_idx = btc.index.searchsorted(h_date)
            if entry_idx >= len(btc):
                continue
            entry = btc.iloc[entry_idx]
            cycle = {"halving_date": date_str, "entry_close": float(entry)}
            for months in (6, 12, 18, 24, 30, 36, 42):
                target = h_date + pd.DateOffset(months=months)
                idx = btc.index.searchsorted(target)
                if idx < len(btc):
                    cycle[f"month_{months}_close"] = float(btc.iloc[idx])
                    cycle[f"month_{months}_return"] = float(btc.iloc[idx] / entry - 1)
                else:
                    cycle[f"month_{months}_close"] = None
                    cycle[f"month_{months}_return"] = None
            # Find cycle peak: max within +6 to +24 months
            window_start = btc.index.searchsorted(h_date + pd.DateOffset(months=6))
            window_end = btc.index.searchsorted(h_date + pd.DateOffset(months=24))
            if window_end > window_start and window_end <= len(btc):
                peak_in_window = btc.iloc[window_start:window_end]
                cycle["cycle_peak_close"] = float(peak_in_window.max())
                cycle["cycle_peak_date"] = str(peak_in_window.idxmax().date())
                cycle["cycle_peak_return"] = float(peak_in_window.max() / entry - 1)
            # Find cycle bottom: min within +24 to +42 months
            window_start = btc.index.searchsorted(h_date + pd.DateOffset(months=24))
            window_end = btc.index.searchsorted(h_date + pd.DateOffset(months=42))
            if window_end > window_start and window_end <= len(btc):
                trough_in_window = btc.iloc[window_start:window_end]
                cycle["post_peak_bottom_close"] = float(trough_in_window.min())
                cycle["post_peak_bottom_date"] = str(trough_in_window.idxmin().date())
                cycle["post_peak_bottom_dd_from_entry"] = float(trough_in_window.min() / entry - 1)
            out[label] = cycle
        except Exception as e:
            out[label] = {"error": str(e)}
    return out


def presidential_cycle_returns(spx: pd.Series) -> dict:
    """Average SPX calendar-year return by cycle year (Y1, Y2, Y3, Y4)."""
    yearly = spx.resample("YE").last()
    yearly_returns = yearly.pct_change()
    yearly_returns.index = yearly_returns.index.year

    by_cycle_year = {1: [], 2: [], 3: [], 4: []}
    cycle_year_detail = {}
    for cycle_label, (y1, y2, y3, y4) in PRES_CYCLE_YEARS.items():
        for cy, year in enumerate([y1, y2, y3, y4], start=1):
            ret = yearly_returns.get(year)
            if ret is not None and not math.isnan(ret):
                by_cycle_year[cy].append(float(ret))
                cycle_year_detail[year] = {"cycle_label": cycle_label, "cycle_year": cy, "spx_return": float(ret)}

    summary = {}
    for cy, rets in by_cycle_year.items():
        if rets:
            summary[f"Y{cy}_count"] = len(rets)
            summary[f"Y{cy}_mean"] = float(np.mean(rets))
            summary[f"Y{cy}_median"] = float(np.median(rets))
            summary[f"Y{cy}_positive_rate"] = float(sum(1 for r in rets if r > 0) / len(rets))
    summary["year_detail"] = cycle_year_detail
    summary["Y_labels"] = {
        "Y1": "post-election (inauguration year)",
        "Y2": "midterm year — historically weakest",
        "Y3": "pre-election year — historically strongest",
        "Y4": "election year",
    }
    return summary


def monthly_of_year_returns(series: pd.Series, label: str) -> dict:
    """Average return per calendar month (1=Jan ... 12=Dec)."""
    mret = series.pct_change()
    by_month = mret.groupby(mret.index.month).agg(["mean", "median", "std", "count"])
    by_month["positive_rate"] = mret.groupby(mret.index.month).apply(lambda x: (x > 0).mean())
    out = {"label": label}
    for month_num, row in by_month.iterrows():
        out[f"M{month_num:02d}"] = {
            "mean": float(row["mean"]),
            "median": float(row["median"]),
            "std": float(row["std"]),
            "count": int(row["count"]),
            "positive_rate": float(row["positive_rate"]),
        }
    return out


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    report = {
        "as_of": datetime.now(timezone.utc).isoformat(),
        "schema_version": 1,
    }

    # ── BTC halving cycle ──
    print("Fetching BTC history from 2014-01-01...", file=sys.stderr)
    btc = fetch_monthly("BTC-USD", "2014-01-01", TODAY)
    if not btc.empty:
        report["btc_halving_cycles"] = btc_halving_cycle_returns(btc)
        report["btc_monthly_seasonality"] = monthly_of_year_returns(btc, "BTC-USD")
    else:
        report["btc_halving_cycles"] = {"error": "no data"}

    # ── SPX presidential cycle + monthly seasonality ──
    print("Fetching SPX history from 1980-01-01...", file=sys.stderr)
    spx = fetch_monthly("^GSPC", "1980-01-01", TODAY)
    if not spx.empty:
        report["spx_presidential_cycle"] = presidential_cycle_returns(spx)
        report["spx_monthly_seasonality"] = monthly_of_year_returns(spx, "^GSPC since 1980")

    # ── NDX seasonality ──
    print("Fetching NDX history from 1990-01-01...", file=sys.stderr)
    ndx = fetch_monthly("^NDX", "1990-01-01", TODAY)
    if not ndx.empty:
        report["ndx_monthly_seasonality"] = monthly_of_year_returns(ndx, "^NDX since 1990")

    # ── Sector ETF monthly seasonality ──
    print("Fetching sector ETFs...", file=sys.stderr)
    sector_seas = {}
    for etf, name in SECTOR_ETFS.items():
        s = fetch_monthly(etf, "2005-01-01", TODAY)
        if not s.empty and len(s.dropna()) > 24:
            sector_seas[etf] = {
                "sector": name,
                "data_start": str(s.dropna().index[0].date()),
                "data_end": str(s.dropna().index[-1].date()),
                "monthly": monthly_of_year_returns(s, etf),
            }
        else:
            sector_seas[etf] = {"sector": name, "error": "insufficient data"}
    report["sector_seasonality"] = sector_seas

    # ── Current cycle position read (where are we now in each cycle) ──
    today_ts = pd.Timestamp(TODAY)
    report["current_position_2026_05"] = {
        "btc_months_since_2024_halving": (today_ts.year * 12 + today_ts.month) - (2024 * 12 + 4),
        "presidential_cycle_year": "Y2 (midterm — Trump 2, 2nd year)",
        "month_of_year": 5,
        "month_of_year_label": "May (entering Sell-in-May window)",
        "btc_peak_recent": "2025-10-06 ~$126,198",
        "btc_consensus_bottom_expected": "Q4 2026 to Q1 2027 per multiple analysts",
        "spx_seasonal_outlook_next_6m": "Weakest part of year (May-Oct); historical SPX worst 6 months",
    }

    out_path = OUT / f"cycle-validation-{TODAY}.json"
    out_path.write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")
    print(f"wrote {out_path}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
