"""GitHub-sourced universe fetcher.

Uses well-maintained GitHub repositories instead of unstable web scraping:
  - datasets/s-and-p-500-companies (SP500)
  - rreichel3/US-Stock-Symbols (full Nasdaq/NYSE/AMEX)
  - shilewenuw/get_all_tickers (combined US)

Runs FOM scan on result.
"""

from __future__ import annotations

import json
import math
import sys
import warnings
from datetime import datetime, timezone
from io import StringIO
from pathlib import Path

warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)

import urllib.request

import numpy as np
import pandas as pd
import yfinance as yf

GITHUB_URLS = {
    "sp500_constituents": "https://raw.githubusercontent.com/datasets/s-and-p-500-companies/main/data/constituents.csv",
    "sp500_constituents_alt": "https://raw.githubusercontent.com/datasets/s-and-p-500-companies/master/data/constituents.csv",
    # rreichel3 maintains comprehensive US tickers
    "nasdaq_full": "https://raw.githubusercontent.com/rreichel3/US-Stock-Symbols/main/nasdaq/nasdaq_full_tickers.json",
    "nyse_full": "https://raw.githubusercontent.com/rreichel3/US-Stock-Symbols/main/nyse/nyse_full_tickers.json",
    "amex_full": "https://raw.githubusercontent.com/rreichel3/US-Stock-Symbols/main/amex/amex_full_tickers.json",
}


def fetch_url(url: str, timeout: int = 30) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8", errors="ignore")


def fetch_sp500() -> list[dict]:
    """Returns list of {symbol, name, sector}."""
    for url in [GITHUB_URLS["sp500_constituents"], GITHUB_URLS["sp500_constituents_alt"]]:
        try:
            text = fetch_url(url)
            df = pd.read_csv(StringIO(text))
            # Common column names
            sym_col = next((c for c in df.columns if c.lower() in ("symbol", "ticker")), None)
            name_col = next((c for c in df.columns if c.lower() in ("security", "name", "company")), None)
            sec_col = next((c for c in df.columns if "sector" in c.lower()), None)
            if not sym_col:
                continue
            out = []
            for _, row in df.iterrows():
                sym = str(row[sym_col]).strip().replace(".", "-")
                if sym and len(sym) <= 6:
                    out.append({
                        "symbol": sym,
                        "name": str(row[name_col]) if name_col else "",
                        "sector": str(row[sec_col]) if sec_col else "",
                    })
            return out
        except Exception as e:
            print(f"  WARN: SP500 fetch from {url[:60]}... failed: {e}", file=sys.stderr)
            continue
    return []


def fetch_us_full() -> list[dict]:
    """Pull NASDAQ + NYSE + AMEX full tickers (rreichel3)."""
    all_out = []
    for exchange, url in [("NASDAQ", GITHUB_URLS["nasdaq_full"]),
                           ("NYSE", GITHUB_URLS["nyse_full"]),
                           ("AMEX", GITHUB_URLS["amex_full"])]:
        try:
            text = fetch_url(url)
            data = json.loads(text)
            for item in data:
                sym = str(item.get("symbol", "")).strip().replace(".", "-")
                if sym and len(sym) <= 6:
                    all_out.append({
                        "symbol": sym,
                        "name": item.get("name", ""),
                        "sector": item.get("sector", ""),
                        "industry": item.get("industry", ""),
                        "exchange": exchange,
                        "market_cap": item.get("marketCap", ""),
                    })
        except Exception as e:
            print(f"  WARN: {exchange} fetch failed: {e}", file=sys.stderr)
    return all_out


def fetch_monthly_safe(tickers: list[str], start: str, end: str,
                        batch_size: int = 30) -> pd.DataFrame:
    """Bulk pull with safe batching."""
    closes_all = {}
    for i in range(0, len(tickers), batch_size):
        batch = tickers[i:i+batch_size]
        try:
            raw = yf.download(batch, start=start, end=end, interval="1mo",
                             auto_adjust=True, progress=False, group_by="ticker",
                             threads=True)
            for t in batch:
                try:
                    if isinstance(raw.columns, pd.MultiIndex):
                        s = raw[t]["Close"]
                    else:
                        s = raw["Close"]
                    if not s.dropna().empty:
                        closes_all[t] = s
                except (KeyError, ValueError):
                    pass
        except Exception as e:
            print(f"  WARN: batch {i//batch_size} failed: {e}", file=sys.stderr)
        if i % 60 == 0:
            print(f"  progress: {i}/{len(tickers)} ({len(closes_all)} success)", file=sys.stderr)
    df = pd.DataFrame(closes_all)
    if df.index.tz is not None:
        df.index = df.index.tz_localize(None)
    return df.sort_index()


def fom_simple_score(closes, ticker, as_of):
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
    r1 = float(pre.iloc[-1] / pre.iloc[-2] - 1) if len(pre) > 1 else 0
    r3 = float(pre.iloc[-1] / pre.iloc[-4] - 1) if len(pre) > 3 else 0
    r6 = float(pre.iloc[-1] / pre.iloc[-7] - 1) if len(pre) > 6 else 0
    r12 = float(pre.iloc[-1] / pre.iloc[-13] - 1) if len(pre) > 12 else 0
    momentum = max(0, min(100, ((r6 + 0.3) / 1.0 * 100)))
    window = pre.iloc[-13:]
    high = float(window.max())
    dist_high = (high - last) / high if high > 0 else 0
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
    lr = np.log(pre.iloc[-13:] / pre.iloc[-13:].shift(1)).dropna()
    rvol = float(lr.std() * math.sqrt(12)) if len(lr) > 1 else 0.3
    quality = max(0, 100 - rvol * 100) * 0.4 + max(0, min(100, (r12 + 0.5) / 2.5 * 100)) * 0.6
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
    base = (0.25 * momentum + 0.25 * contrarian + 0.20 * quality
            + 0.30 * ((bubble + 100) / 2))
    return {
        "ticker": ticker, "fom": round(base, 1),
        "momentum": round(momentum, 1), "contrarian": round(contrarian, 1),
        "quality": round(quality, 1), "bubble_guard": round(bubble, 1),
        "r1m_pct": round(r1 * 100, 1), "r6m_pct": round(r6 * 100, 1),
        "r12m_pct": round(r12 * 100, 1),
        "dist_from_12m_high_pct": round(dist_high * 100, 1),
        "rvol_annual_pct": round(rvol * 100, 1),
    }


def main():
    out_dir = Path("outputs")
    out_dir.mkdir(parents=True, exist_ok=True)
    today = pd.Timestamp("2026-05-30")

    print("Fetching SP500 from GitHub (datasets repo)...", file=sys.stderr)
    sp500 = fetch_sp500()
    print(f"  SP500: {len(sp500)} names", file=sys.stderr)

    print("Fetching full US listings (rreichel3)...", file=sys.stderr)
    us_full = fetch_us_full()
    print(f"  Full US: {len(us_full)} names", file=sys.stderr)

    # Build ticker → metadata dict
    meta = {item["symbol"]: item for item in us_full}
    for item in sp500:
        meta[item["symbol"]] = {**meta.get(item["symbol"], {}), **item, "is_sp500": True}

    sp500_set = {item["symbol"] for item in sp500}
    all_tickers = sorted(meta.keys())

    # Limit to manageable scope for first run
    # Strategy: All SP500 + sample of R2K (market cap-based)
    sample_size = 800  # Manageable for batch yfinance
    if len(all_tickers) > sample_size:
        # Prioritize SP500, then add others up to sample_size
        sp500_in = [t for t in all_tickers if t in sp500_set]
        others = [t for t in all_tickers if t not in sp500_set]
        sample = sp500_in + others[:sample_size - len(sp500_in)]
    else:
        sample = all_tickers
    print(f"  scoring sample: {len(sample)} tickers", file=sys.stderr)

    print("Fetching monthly bars (batched)...", file=sys.stderr)
    closes = fetch_monthly_safe(sample, "2022-01-01", "2026-05-30", batch_size=30)
    print(f"  data: {len(closes.columns)} tickers", file=sys.stderr)

    print("Scoring...", file=sys.stderr)
    results = []
    for t in closes.columns:
        sc = fom_simple_score(closes, t, today)
        if sc:
            md = meta.get(t, {})
            sc["name"] = md.get("name", "")
            sc["sector"] = md.get("sector", "")
            sc["is_sp500"] = md.get("is_sp500", False)
            sc["exchange"] = md.get("exchange", "")
            results.append(sc)

    results.sort(key=lambda x: x["fom"], reverse=True)

    # Split SP500 vs non-SP500
    sp500_results = [r for r in results if r.get("is_sp500")]
    non_sp500 = [r for r in results if not r.get("is_sp500")]

    # Find deep value recovery (15-40% off high + recent green)
    deep_value = [r for r in results if 15 < r["dist_from_12m_high_pct"] < 40
                   and r["r1m_pct"] > 0][:30]

    # Overheated
    overheated = [r for r in results if r["bubble_guard"] < -30][:30]

    # By sector
    by_sector = {}
    for r in results:
        s = r.get("sector") or "Unknown"
        by_sector.setdefault(s, []).append(r["ticker"])

    report = {
        "as_of": datetime.now(timezone.utc).isoformat(),
        "schema_version": 1,
        "sources": ["datasets/s-and-p-500-companies", "rreichel3/US-Stock-Symbols"],
        "sp500_total_in_universe": len(sp500),
        "us_full_listings_total": len(us_full),
        "sample_attempted": len(sample),
        "tickers_with_data": len(closes.columns),
        "tickers_scored": len(results),
        "top_100_overall": [{"rank": i+1, **r} for i, r in enumerate(results[:100])],
        "top_50_sp500": [{"rank": i+1, **r} for i, r in enumerate(sp500_results[:50])],
        "top_30_non_sp500": [{"rank": i+1, **r} for i, r in enumerate(non_sp500[:30])],
        "deep_value_recovery_top30": [{"rank": i+1, **r} for i, r in enumerate(deep_value)],
        "overheated_warning_top30": [{"rank": i+1, **r} for i, r in enumerate(overheated)],
        "sector_counts": {k: len(v) for k, v in by_sector.items()},
    }
    out_path = out_dir / f"github-universe-fom-{today.date()}.json"
    out_path.write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")
    print(f"wrote {out_path}", file=sys.stderr)
    print(f"  top 5 overall: {[r['ticker'] for r in results[:5]]}", file=sys.stderr)
    print(f"  total SP500 scored: {len(sp500_results)}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
