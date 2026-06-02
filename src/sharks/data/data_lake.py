"""本地數據湖 — 持久化所有抓取的資料,離線使用.

優勢:
  - 不重複抓取(節省 API 配額)
  - 離線分析
  - 歷史快照(point-in-time)
  - 可餵給本地 LLM 微調 / RAG

儲存格式:
  - data/lake/prices/<ticker>.parquet(月 / 日 K)
  - data/lake/info/<ticker>.json(基本面快照)
  - data/lake/news/<ticker>_<date>.json(新聞)
  - data/lake/manifest.csv(索引)
"""

from __future__ import annotations

import json
import sys
import warnings
from datetime import datetime, timezone
from pathlib import Path

warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)

import pandas as pd
import yfinance as yf

LAKE = Path("data/lake")
LAKE.mkdir(parents=True, exist_ok=True)
(LAKE / "prices").mkdir(exist_ok=True)
(LAKE / "info").mkdir(exist_ok=True)
(LAKE / "news").mkdir(exist_ok=True)


def store_prices(ticker: str, period: str = "5y", interval: str = "1d") -> dict:
    """Store OHLCV to parquet."""
    try:
        t = yf.Ticker(ticker)
        df = t.history(period=period, interval=interval)
        if df.empty:
            return {"ticker": ticker, "status": "no_data"}
        # Save parquet
        path = LAKE / "prices" / f"{ticker}_{interval}.parquet"
        df.to_parquet(path)
        return {"ticker": ticker, "rows": len(df), "path": str(path),
                 "first": str(df.index[0].date()), "last": str(df.index[-1].date())}
    except Exception as e:
        return {"ticker": ticker, "error": str(e)}


def store_info(ticker: str) -> dict:
    """Store ticker.info snapshot."""
    try:
        t = yf.Ticker(ticker)
        info = t.info or {}
        info["_snapshot_time"] = datetime.now(timezone.utc).isoformat()
        path = LAKE / "info" / f"{ticker}.json"
        path.write_text(json.dumps(info, indent=2, default=str), encoding="utf-8")
        return {"ticker": ticker, "path": str(path), "fields": len(info)}
    except Exception as e:
        return {"ticker": ticker, "error": str(e)}


def load_prices(ticker: str, interval: str = "1d") -> pd.DataFrame:
    """Load from lake — fast offline."""
    path = LAKE / "prices" / f"{ticker}_{interval}.parquet"
    if not path.exists():
        return pd.DataFrame()
    return pd.read_parquet(path)


def load_info(ticker: str) -> dict:
    """Load info snapshot."""
    path = LAKE / "info" / f"{ticker}.json"
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def build_manifest() -> pd.DataFrame:
    """Index all lake content."""
    rows = []
    for f in (LAKE / "prices").glob("*.parquet"):
        ticker, _, _ = f.stem.partition("_")
        try:
            stat = f.stat()
            rows.append({"type": "prices", "ticker": ticker, "file": f.name,
                         "size_kb": round(stat.st_size / 1024, 1),
                         "mtime": datetime.fromtimestamp(stat.st_mtime).isoformat()})
        except Exception:
            pass
    for f in (LAKE / "info").glob("*.json"):
        ticker = f.stem
        try:
            stat = f.stat()
            rows.append({"type": "info", "ticker": ticker, "file": f.name,
                         "size_kb": round(stat.st_size / 1024, 1),
                         "mtime": datetime.fromtimestamp(stat.st_mtime).isoformat()})
        except Exception:
            pass
    df = pd.DataFrame(rows)
    if not df.empty:
        df.to_csv(LAKE / "manifest.csv", index=False)
    return df


def main():
    today = datetime.now().strftime("%Y-%m-%d")
    print(f"Data lake building — {today}", file=sys.stderr)

    # Sample seed: store key tickers
    seed_tickers = [
        # Mag 7
        "NVDA", "AAPL", "MSFT", "META", "GOOGL", "AMZN", "TSLA",
        # FOM picks
        "LMT", "NOC", "RTX", "UEC", "AESI", "NEM", "DNN",
        # User portfolio
        "ORCL", "DELL", "CRM", "NOW", "NKE", "LULU",
        # 2022 oversold
        "NVAX", "BLDP", "ZM", "ROKU", "NTLA", "BEAM",
        # Hedges
        "GLD", "TLT", "VXX", "SH", "FXY", "YCS",
    ]

    storage_log = []
    for t in seed_tickers:
        p = store_prices(t, period="5y", interval="1d")
        i = store_info(t)
        storage_log.append({"ticker": t, "prices": p, "info": i})

    manifest = build_manifest()

    report = {
        "as_of": datetime.now(timezone.utc).isoformat(),
        "lake_path": str(LAKE.absolute()),
        "tickers_seeded": len(seed_tickers),
        "total_files": len(manifest) if not manifest.empty else 0,
        "total_size_mb": round(manifest["size_kb"].sum() / 1024, 2) if not manifest.empty else 0,
        "storage_summary": storage_log[:5],  # sample
    }
    out_path = Path("outputs") / f"data-lake-status-{today}.json"
    out_path.parent.mkdir(exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")
    print(f"  files: {report['total_files']}, size: {report['total_size_mb']} MB", file=sys.stderr)
    print(f"  lake: {LAKE.absolute()}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
