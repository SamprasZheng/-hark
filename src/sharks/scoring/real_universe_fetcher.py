"""Real universe fetcher using multiple data sources.

Sources tried (free, no API key):
  1. iShares IVV ETF holdings (SP500 — ~500 names)
  2. iShares IWM ETF holdings (R2K — ~2000 names)
  3. SEC EDGAR — 13F filings (institutional positioning)
  4. openinsider.com — Form 4 insider trades (web scrape)
"""

from __future__ import annotations

import json
import sys
import warnings
from datetime import datetime, timezone
from io import StringIO
from pathlib import Path

warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)

import urllib.request

import pandas as pd


def fetch_ishares_ivv() -> list[str]:
    """Pull SP500 via iShares IVV holdings CSV."""
    url = "https://www.ishares.com/us/products/239726/ishares-core-sp-500-etf/1467271812596.ajax?fileType=csv&fileName=IVV_holdings&dataType=fund"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=30) as r:
            text = r.read().decode("utf-8", errors="ignore")
        # iShares CSV has metadata header — find row with "Ticker"
        lines = text.splitlines()
        header_idx = None
        for i, line in enumerate(lines):
            if "Ticker" in line and "Name" in line:
                header_idx = i
                break
        if header_idx is None:
            return []
        csv_text = "\n".join(lines[header_idx:])
        df = pd.read_csv(StringIO(csv_text))
        tickers = df["Ticker"].dropna().astype(str).tolist()
        # Clean — only equity (skip cash, futures)
        tickers = [t.replace(".", "-").strip() for t in tickers if t and len(t) <= 6 and t.isalnum() or "-" in t]
        return list(set(tickers))[:520]
    except Exception as e:
        print(f"  WARN: iShares IVV fetch failed: {e}", file=sys.stderr)
        return []


def fetch_ishares_iwm() -> list[str]:
    """Pull R2K via iShares IWM holdings CSV."""
    url = "https://www.ishares.com/us/products/239710/ishares-russell-2000-etf/1467271812596.ajax?fileType=csv&fileName=IWM_holdings&dataType=fund"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=30) as r:
            text = r.read().decode("utf-8", errors="ignore")
        lines = text.splitlines()
        header_idx = None
        for i, line in enumerate(lines):
            if "Ticker" in line and "Name" in line:
                header_idx = i
                break
        if header_idx is None:
            return []
        csv_text = "\n".join(lines[header_idx:])
        df = pd.read_csv(StringIO(csv_text))
        tickers = df["Ticker"].dropna().astype(str).tolist()
        tickers = [t.replace(".", "-").strip() for t in tickers if t and len(t) <= 6]
        return list(set(tickers))[:2100]
    except Exception as e:
        print(f"  WARN: iShares IWM fetch failed: {e}", file=sys.stderr)
        return []


def fetch_openinsider_recent_buys(days: int = 7) -> list[dict]:
    """Scrape openinsider.com for recent insider buys."""
    # Top insider buy/sell from openinsider
    url = f"http://openinsider.com/screener?s=&o=&pl=&ph=&ll=&lh=&fd=0&fdr=&td=0&tdr=&fdlyl=&fdlyh=&daysago={days}&xp=1&xs=1&vl=&vh=&ocl=&och=&sic1=-1&sicl=100&sich=9999&grp=0&nfl=&nfh=&nil=&nih=&nol=&noh=&v2l=&v2h=&oc2l=&oc2h=&sortcol=0&cnt=100&page=1"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=30) as r:
            html = r.read().decode("utf-8", errors="ignore")
        # Try to parse table
        try:
            tables = pd.read_html(StringIO(html))
            for tbl in tables:
                if "Insider" in str(tbl.columns).lower() or "Ticker" in str(tbl.columns):
                    # Found it
                    cols = list(tbl.columns)
                    rows = []
                    for _, row in tbl.head(50).iterrows():
                        rows.append({c: str(row.get(c, "")) for c in cols})
                    return rows
        except Exception:
            pass
        return []
    except Exception as e:
        print(f"  WARN: openinsider fetch failed: {e}", file=sys.stderr)
        return []


def fetch_sec_13f_recent_change(cik: str) -> list[dict]:
    """SEC EDGAR — pull most recent 13F filing for a CIK.

    Common 13F filers to track:
      0001067983 - Berkshire Hathaway (Buffett)
      0001029160 - Bridgewater
      0001037389 - Renaissance
      0001603466 - Citadel
      0001540531 - Two Sigma
    """
    url = f"https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={cik}&type=13F&dateb=&owner=include&count=10"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Sharks research@example.com"})
        with urllib.request.urlopen(req, timeout=30) as r:
            html = r.read().decode("utf-8", errors="ignore")
        return [{"cik": cik, "raw_html_length": len(html), "note": "Filing list fetched — need detailed parse for holdings"}]
    except Exception as e:
        return [{"cik": cik, "error": str(e)}]


def main():
    out_dir = Path("outputs")
    out_dir.mkdir(parents=True, exist_ok=True)
    today = datetime.now().strftime("%Y-%m-%d")
    print(f"Real universe fetcher — {today}", file=sys.stderr)

    print("Fetching iShares IVV (SP500)...", file=sys.stderr)
    ivv = fetch_ishares_ivv()
    print(f"  IVV: {len(ivv)} tickers", file=sys.stderr)

    print("Fetching iShares IWM (R2K)...", file=sys.stderr)
    iwm = fetch_ishares_iwm()
    print(f"  IWM: {len(iwm)} tickers", file=sys.stderr)

    print("Fetching openinsider recent buys (7 days)...", file=sys.stderr)
    insider = fetch_openinsider_recent_buys(7)
    print(f"  openinsider: {len(insider)} rows", file=sys.stderr)

    print("Probing SEC 13F (Berkshire CIK 0001067983)...", file=sys.stderr)
    buffett = fetch_sec_13f_recent_change("0001067983")

    # Save universe
    universe = {
        "as_of": datetime.now(timezone.utc).isoformat(),
        "schema_version": 1,
        "ivv_sp500_tickers": ivv,
        "iwm_r2k_tickers": iwm,
        "total_unique": len(set(ivv + iwm)),
        "openinsider_recent_buys_sample": insider[:20],
        "openinsider_count": len(insider),
        "berkshire_13f_probe": buffett,
    }
    out_path = out_dir / f"real-universe-{today}.json"
    out_path.write_text(json.dumps(universe, indent=2, default=str), encoding="utf-8")
    print(f"wrote {out_path}", file=sys.stderr)
    print(f"  total unique universe: {len(set(ivv + iwm))}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
