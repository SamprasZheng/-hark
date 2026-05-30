"""Full SP500 + R2K Scan — true 500+ name coverage.

Pulls:
  1. SP500 constituents from Wikipedia (503 names)
  2. R2K sample from common small-cap watchlists (100+ names)
  3. Runs FOM-equivalent scoring on each
  4. Outputs 100-stock internal watchlist sorted by alpha potential

This addresses the principal's concern that we were only scanning 130 / 2500 tickers (5% coverage).
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


def fetch_sp500_tickers() -> list[str]:
    """Pull SP500 constituents from Wikipedia."""
    try:
        url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
        tables = pd.read_html(url)
        df = tables[0]
        tickers = df["Symbol"].tolist()
        # Clean: replace . with - for yfinance (BRK.B → BRK-B)
        tickers = [t.replace(".", "-") for t in tickers]
        return tickers
    except Exception as e:
        print(f"  WARN: SP500 fetch failed: {e}", file=sys.stderr)
        # Fallback minimal list
        return ["AAPL", "MSFT", "NVDA", "GOOGL", "META", "AMZN", "TSLA"]


def fetch_r2k_sample() -> list[str]:
    """R2K sample — high-coverage small caps across sectors."""
    return [
        # Specialty semis micro
        "AOSL", "POWI", "NVTS", "WOLF", "MPWR", "HIMX", "IMOS", "MX",
        "ACMR", "AMBA", "INDI", "QUIK", "ALGM", "AEHR", "AXTI", "POET",
        "ALAB", "CRDO", "SIMO", "FN",
        # Crypto miners
        "RIOT", "MARA", "WULF", "CIFR", "BTBT", "HUT", "CLSK", "BITF", "IREN",
        # Nuclear small
        "UEC", "URG", "DNN", "NXE", "OKLO", "SMR", "BWXT", "LEU", "CCJ",
        # Solar / clean
        "ENPH", "FSLR", "SEDG", "RUN", "NOVA", "ARRY", "SHLS", "PLUG",
        "BLDP", "BE", "FCEL", "BLNK", "CHPT", "EVGO",
        # EV / aerospace
        "RIVN", "LCID", "NKLA", "WKHS", "ACHR", "JOBY", "RKLB", "ASTS",
        "LUNR", "PL", "BKSY", "MNTS", "RDW", "VSAT",
        # Biotech speculative
        "CRSP", "BEAM", "NTLA", "VERV", "EDIT", "PRME", "VKTX", "RXRX",
        "SDGR", "ABSI", "RGNX", "RNA", "MIRM", "AKRO",
        # AI micro
        "BBAI", "AI", "SOUN", "GFAI", "INOD", "CXAI",
        # Quantum
        "IONQ", "RGTI", "QBTS", "QUBT",
        # Energy mid
        "AESI", "FANG", "DVN", "RIG", "VAL", "HP", "PUMP",
        # Materials small
        "NEM", "FCX", "MP", "AA",
        # Industrials small
        "GFS", "SKYT", "GLW", "AMKR", "TER", "VRT",
        # Healthcare small
        "PHAT", "AVDL", "RZLT", "CYTK", "DCTH",
        # SaaS/tech mid
        "DOCN", "PATH", "APPN", "EXTR", "GRPN", "PD", "MNDY", "DDOG", "ZS",
        "CRWD", "PANW", "MDB", "SPLK", "OKTA",
        # Misc
        "BIRK", "SHAK", "CRSR", "AMPX", "RPID", "VLN", "NBIS",
    ]


def fetch_monthly(tickers, start, end):
    raw = yf.download(tickers, start=start, end=end, interval="1mo",
                     auto_adjust=True, progress=False, group_by="ticker", threads=True)
    closes = {}
    for t in tickers:
        try:
            if isinstance(raw.columns, pd.MultiIndex):
                s = raw[t]["Close"]
            else:
                s = raw["Close"]
            if not s.dropna().empty:
                closes[t] = s
        except (KeyError, ValueError):
            pass
    df = pd.DataFrame(closes)
    if df.index.tz is not None:
        df.index = df.index.tz_localize(None)
    return df.sort_index()


def fom_simple_score(closes, ticker, as_of):
    """Simplified FOM for fast batch scoring."""
    s = closes.get(ticker)
    if s is None or s.dropna().empty:
        return None
    s = s.dropna()
    pre = s.loc[:as_of]
    if len(pre) < 13:
        return None

    last = float(pre.iloc[-1])
    if last <= 0:
        return None

    # Momentum
    r1 = float(pre.iloc[-1] / pre.iloc[-2] - 1) if len(pre) > 1 else 0
    r3 = float(pre.iloc[-1] / pre.iloc[-4] - 1) if len(pre) > 3 else 0
    r6 = float(pre.iloc[-1] / pre.iloc[-7] - 1) if len(pre) > 6 else 0
    r12 = float(pre.iloc[-1] / pre.iloc[-13] - 1) if len(pre) > 12 else 0
    momentum = max(0, min(100, ((r6 + 0.3) / 1.0 * 100)))

    # Distance from 12m high
    window = pre.iloc[-13:]
    high = float(window.max())
    dist_high = (high - last) / high if high > 0 else 0

    # Contrarian sweet spot: 15-30% below 12m high
    if dist_high < 0.05:
        contrarian = 30
    elif dist_high < 0.15:
        contrarian = 50
    elif dist_high < 0.30:
        contrarian = 85
    elif dist_high < 0.50:
        contrarian = 70
    else:
        contrarian = 40

    # Realised vol
    lr = np.log(pre.iloc[-13:] / pre.iloc[-13:].shift(1)).dropna()
    rvol = float(lr.std() * math.sqrt(12)) if len(lr) > 1 else 0.3
    quality = max(0, 100 - rvol * 100) * 0.4 + max(0, min(100, (r12 + 0.5) / 2.5 * 100)) * 0.6

    # Bubble guard
    bubble = 0
    if r6 > 2.0:
        bubble -= 50
    elif r6 > 1.0:
        bubble -= 25
    elif r6 > 0.5:
        bubble -= 10
    if dist_high < 0.03 and r12 > 1.0:
        bubble -= 15
    if 0.15 < dist_high < 0.35 and r12 > -0.1:
        bubble += 30

    # FOM
    base = (0.25 * momentum + 0.25 * contrarian + 0.20 * quality
            + 0.30 * ((bubble + 100) / 2))

    return {
        "ticker": ticker,
        "fom": round(base, 1),
        "momentum": round(momentum, 1),
        "contrarian": round(contrarian, 1),
        "quality": round(quality, 1),
        "bubble_guard": round(bubble, 1),
        "r1m_pct": round(r1 * 100, 1),
        "r6m_pct": round(r6 * 100, 1),
        "r12m_pct": round(r12 * 100, 1),
        "dist_from_12m_high_pct": round(dist_high * 100, 1),
        "rvol_annual_pct": round(rvol * 100, 1),
    }


def main():
    out_dir = Path("outputs")
    out_dir.mkdir(parents=True, exist_ok=True)
    today = pd.Timestamp("2026-05-30")

    print("Pulling SP500 constituents from Wikipedia...", file=sys.stderr)
    sp500 = fetch_sp500_tickers()
    print(f"  SP500: {len(sp500)} tickers", file=sys.stderr)
    r2k = fetch_r2k_sample()
    print(f"  R2K sample: {len(r2k)} tickers", file=sys.stderr)

    all_universe = sorted(set(sp500 + r2k))
    print(f"  Combined universe: {len(all_universe)} tickers", file=sys.stderr)

    print("Fetching monthly bars...", file=sys.stderr)
    closes = fetch_monthly(all_universe, "2022-01-01", "2026-05-30")
    print(f"  data: {len(closes.columns)} tickers", file=sys.stderr)

    print("Scoring...", file=sys.stderr)
    results = []
    for t in all_universe:
        score = fom_simple_score(closes, t, today)
        if score:
            score["bucket"] = "sp500" if t in sp500 else "r2k_sample"
            results.append(score)

    results.sort(key=lambda x: x["fom"], reverse=True)

    # Categorize
    top_100 = results[:100]
    top_50_sp500 = [r for r in results if r["bucket"] == "sp500"][:50]
    top_50_r2k = [r for r in results if r["bucket"] == "r2k_sample"][:50]
    deep_value_candidates = [r for r in results
                              if 0.20 < r["dist_from_12m_high_pct"] / 100 < 0.40 and r["r1m_pct"] > 0][:30]
    overheated_warning = [r for r in results if r["bubble_guard"] < -30][:30]

    report = {
        "as_of": datetime.now(timezone.utc).isoformat(),
        "schema_version": 1,
        "universe_attempted": len(all_universe),
        "tickers_with_data": len(closes.columns),
        "tickers_scored": len(results),
        "sp500_count_in_universe": len(sp500),
        "r2k_sample_count": len(r2k),
        "top_100_overall_watchlist": [{"rank": i+1, **r} for i, r in enumerate(top_100)],
        "top_50_sp500": [{"rank": i+1, **r} for i, r in enumerate(top_50_sp500)],
        "top_50_r2k_sample": [{"rank": i+1, **r} for i, r in enumerate(top_50_r2k)],
        "deep_value_recovery_candidates": [{"rank": i+1, **r} for i, r in enumerate(deep_value_candidates)],
        "overheated_warning_list": [{"rank": i+1, **r} for i, r in enumerate(overheated_warning)],
    }
    out_path = out_dir / f"sp500-r2k-full-scan-{today.date()}.json"
    out_path.write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")
    print(f"wrote {out_path}", file=sys.stderr)
    print(f"  top 3 overall: {[r['ticker'] for r in top_100[:3]]}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
