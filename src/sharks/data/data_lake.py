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


# ── info 衍生欄位 sanity lint(EUR/ADR 換算汙染防護)──
# yfinance 對部分外幣計帳的 ADR(ASML、TSM、DEO、LPL…)會把 enterpriseValue /
# priceToBook / floatShares 用錯誤的本幣↔ADR 比例放大數十倍(ASML 實測 55.5x)。
# 閾值刻意保守:真實高負債(JACK)或微薄帳面值(CL、BOX)也會中標,所以只
# **標記** derived_fields_suspect、不清空欄位 —— 由下游 scorer 自行決定棄用。
SUSPECT_PB = 100.0        # priceToBook 上限
SUSPECT_EV_MC = 10.0      # enterpriseValue / marketCap 倍數上限
SUSPECT_FLOAT_SO = 3.0    # floatShares / sharesOutstanding 倍數上限


def lint_info_fields(info: dict) -> list[str]:
    """檢查 info 快照的衍生估值欄位是否疑似損毀,回傳原因清單(空 = 乾淨)。
    純函式(不碰磁碟),供測試直接餵 dict。"""
    def num(key: str):
        v = info.get(key)
        return float(v) if isinstance(v, (int, float)) and not isinstance(v, bool) else None

    reasons = []
    pb = num("priceToBook")
    if pb is not None and pb > SUSPECT_PB:
        reasons.append(f"priceToBook={pb:.0f} > {SUSPECT_PB:.0f}")
    mc, ev = num("marketCap"), num("enterpriseValue")
    if mc and ev and ev > SUSPECT_EV_MC * mc:
        reasons.append(f"enterpriseValue={ev / mc:.1f}x marketCap")
    fs, so = num("floatShares"), num("sharesOutstanding")
    if fs and so and fs > SUSPECT_FLOAT_SO * so:
        reasons.append(f"floatShares={fs / so:.1f}x sharesOutstanding")
    return reasons


def _apply_info_lint(info: dict) -> dict:
    reasons = lint_info_fields(info)
    if reasons:
        info["derived_fields_suspect"] = True
        info["derived_fields_suspect_reasons"] = reasons
    else:
        info.pop("derived_fields_suspect", None)
        info.pop("derived_fields_suspect_reasons", None)
    return info


def lint_lake_info(write: bool = True) -> dict:
    """掃描既有 info 快照,標記/清除 derived_fields_suspect。回傳 {ticker: reasons}。"""
    flagged: dict[str, list[str]] = {}
    for p in sorted((LAKE / "info").glob("*.json")):
        try:
            info = json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            continue
        before = (info.get("derived_fields_suspect"), info.get("derived_fields_suspect_reasons"))
        _apply_info_lint(info)
        after = (info.get("derived_fields_suspect"), info.get("derived_fields_suspect_reasons"))
        if info.get("derived_fields_suspect"):
            flagged[p.stem] = info["derived_fields_suspect_reasons"]
        if write and before != after:
            p.write_text(json.dumps(info, indent=2, default=str), encoding="utf-8")
    return flagged


def store_info(ticker: str) -> dict:
    """Store ticker.info snapshot."""
    try:
        t = yf.Ticker(ticker)
        info = t.info or {}
        info["_snapshot_time"] = datetime.now(timezone.utc).isoformat()
        _apply_info_lint(info)
        path = LAKE / "info" / f"{ticker}.json"
        path.write_text(json.dumps(info, indent=2, default=str), encoding="utf-8")
        return {"ticker": ticker, "path": str(path), "fields": len(info),
                "derived_fields_suspect": bool(info.get("derived_fields_suspect"))}
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


_SEED_TICKERS = [
    "NVDA", "AAPL", "MSFT", "META", "GOOGL", "AMZN", "TSLA",
    "LMT", "NOC", "RTX", "UEC", "AESI", "NEM", "DNN",
    "ORCL", "DELL", "CRM", "NOW", "NKE", "LULU",
    "NVAX", "BLDP", "ZM", "ROKU", "NTLA", "BEAM",
    "GLD", "TLT", "VXX", "SH", "FXY", "YCS",
]


def universe_to_store() -> list[str]:
    """Tickers to cache to the lake. Default = the FULL FOM scan universe (offline-first
    per principal directive 2026-06-10 — build the local cache while the APIs are still
    available); env LAKE_UNIVERSE=seed keeps the small legacy seed."""
    import os
    if os.environ.get("LAKE_UNIVERSE", "full").strip().lower() == "seed":
        return _SEED_TICKERS
    try:
        from sharks.scoring.fom import scan_universe
        u = scan_universe()
        if u:
            return sorted(set(u) | set(_SEED_TICKERS))
    except Exception as e:
        print(f"(full universe unavailable: {e}; using seed)", file=sys.stderr)
    return _SEED_TICKERS


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "lint":
        # python -m sharks.data.data_lake lint — 離線重掃既有快照(不打 API)
        flagged = lint_lake_info()
        for t, reasons in flagged.items():
            print(f"  {t}: {'; '.join(reasons)}")
        print(f"{len(flagged)} suspect info snapshots flagged (derived_fields_suspect)")
        return 0

    today = datetime.now().strftime("%Y-%m-%d")
    print(f"Data lake building — {today}", file=sys.stderr)

    seed_tickers = universe_to_store()
    print(f"  caching {len(seed_tickers)} tickers (LAKE_UNIVERSE) -> prices + info...", file=sys.stderr)

    storage_log = []
    for n, t in enumerate(seed_tickers, 1):
        p = store_prices(t, period="5y", interval="1d")          # short-horizon signals
        # Decades of MONTHLY bars — the 季線/年線 大波段 horizon (principal directive
        # 2026-06-10). yfinance 1mo history goes back to listing; cheap + tiny parquet.
        pm = store_prices(t, period="max", interval="1mo")
        i = store_info(t)
        storage_log.append({"ticker": t, "prices": p, "prices_monthly": pm, "info": i})
        if n % 25 == 0:
            print(f"    ...{n}/{len(seed_tickers)}", file=sys.stderr)

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
