"""Market Breadth Indicator — 市場寬度過熱 / 衰竭偵測.

Adds 4th macro signal alongside M2 / BTC / Gold:

Breadth signals:
  1. NDTW (proxy) — NDX index vs 200MA (rough breadth proxy)
  2. R2TW (proxy) — RUT index vs 200MA
  3. NDX vs RUT ratio — concentration warning when NDX > RUT >> historical
  4. % of MAG7 above 50/200 MA (real breadth on top-weighted names)

Per principal directive 2026-05-30: 「市場寬度過大 = 過熱」
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


def fetch_daily(tickers, start, end):
    raw = yf.download(tickers, start=start, end=end, interval="1d",
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


def above_ma_percent(closes: pd.DataFrame, ma_days: int, as_of: pd.Timestamp) -> dict:
    """For a sample of tickers, return % above their N-day MA at as_of."""
    pre = closes.loc[:as_of]
    if len(pre) < ma_days + 5:
        return {"pct": None, "tickers_above": [], "tickers_below": []}
    last_row = pre.iloc[-1]
    ma_row = pre.iloc[-ma_days:].mean()
    above = []
    below = []
    for ticker in closes.columns:
        last_p = last_row.get(ticker)
        ma_p = ma_row.get(ticker)
        if pd.isna(last_p) or pd.isna(ma_p):
            continue
        if last_p > ma_p:
            above.append(ticker)
        else:
            below.append(ticker)
    total = len(above) + len(below)
    pct = (len(above) / total * 100) if total > 0 else None
    return {"pct": round(pct, 1) if pct else None,
            "above_count": len(above), "below_count": len(below),
            "tickers_above": above, "tickers_below": below}


def index_vs_ma(closes: pd.Series, ma_days: int, as_of: pd.Timestamp) -> dict:
    pre = closes.loc[:as_of].dropna()
    if len(pre) < ma_days + 5:
        return None
    last_p = float(pre.iloc[-1])
    ma_p = float(pre.iloc[-ma_days:].mean())
    dist_pct = (last_p - ma_p) / ma_p * 100
    above = last_p > ma_p
    return {
        "last_price": round(last_p, 2),
        "ma_price": round(ma_p, 2),
        "dist_pct": round(dist_pct, 2),
        "above_ma": above,
    }


def main():
    out_dir = Path("outputs")
    out_dir.mkdir(parents=True, exist_ok=True)
    today = pd.Timestamp("2026-05-30")
    print(f"Breadth indicator as of {today.date()}", file=sys.stderr)

    # Indices
    indices = ["^NDX", "^RUT", "^GSPC"]
    # Sample NDX components (top weighted)
    ndx_sample = ["AAPL", "MSFT", "NVDA", "GOOGL", "META", "AMZN", "TSLA",
                   "AVGO", "ORCL", "COST", "ADBE", "NFLX", "PEP", "AMD",
                   "INTC", "QCOM", "TXN", "AMAT", "ASML", "LRCX", "MU",
                   "BKNG", "GILD", "INTU", "ARM"]
    # Sample RUT components
    rut_sample = ["IWM", "AOSL", "CRSR", "NVTS", "POWI", "ARM", "MU", "WDC",
                   "STX", "POET", "AXTI", "AEHR", "ALAB", "CRDO", "SIMO"]

    all_pull = list(set(indices + ndx_sample + rut_sample))
    closes = fetch_daily(all_pull, "2024-01-01", "2026-05-30")
    print(f"  data: {len(closes.columns)} tickers", file=sys.stderr)

    # Index vs MA
    ndx = closes.get("^NDX")
    rut = closes.get("^RUT")
    spx = closes.get("^GSPC")
    indices_vs_ma = {}
    for name, s in [("NDX", ndx), ("RUT", rut), ("SPX", spx)]:
        if s is not None:
            indices_vs_ma[name] = {
                "vs_50ma": index_vs_ma(s, 50, today),
                "vs_200ma": index_vs_ma(s, 200, today),
            }

    # % above MA for samples
    ndx_breadth = {}
    rut_breadth = {}
    if ndx_sample:
        ndx_closes = closes[[t for t in ndx_sample if t in closes.columns]]
        ndx_breadth = {
            "above_50ma": above_ma_percent(ndx_closes, 50, today),
            "above_200ma": above_ma_percent(ndx_closes, 200, today),
        }
    if rut_sample:
        rut_closes = closes[[t for t in rut_sample if t in closes.columns]]
        rut_breadth = {
            "above_50ma": above_ma_percent(rut_closes, 50, today),
            "above_200ma": above_ma_percent(rut_closes, 200, today),
        }

    # NDX/RUT ratio — concentration metric
    ratio_history = None
    if ndx is not None and rut is not None:
        valid = pd.concat([ndx, rut], axis=1).dropna()
        valid.columns = ["NDX", "RUT"]
        valid["ratio"] = valid["NDX"] / valid["RUT"]
        last_ratio = float(valid["ratio"].iloc[-1])
        # 12-month percentile of ratio
        last_year = valid.iloc[-252:] if len(valid) > 252 else valid
        ratio_pct_rank = float((last_year["ratio"] < last_ratio).sum() / len(last_year) * 100)
        ratio_history = {
            "current_ratio": round(last_ratio, 4),
            "percentile_in_12m": round(ratio_pct_rank, 1),
            "interpretation": (
                "極度集中 — NDX 超漲於 RUT 12 月 90%ile+;市場過熱訊號" if ratio_pct_rank > 90
                else "高度集中 — 大型科技概念股拉抬" if ratio_pct_rank > 75
                else "均衡 — Mag 7 跟 R2K 相對平衡" if ratio_pct_rank > 25
                else "RUT 強勢於 NDX — 風險偏好回到小型股 / 妖股年訊號"
            ),
        }

    # Compose alert
    ndx_above_50 = ndx_breadth.get("above_50ma", {}).get("pct") or 0
    ndx_above_200 = ndx_breadth.get("above_200ma", {}).get("pct") or 0
    rut_above_50 = rut_breadth.get("above_50ma", {}).get("pct") or 0
    rut_above_200 = rut_breadth.get("above_200ma", {}).get("pct") or 0

    # Overheated criteria
    is_overheated = False
    overheated_reasons = []
    if ndx_above_50 > 85:
        is_overheated = True
        overheated_reasons.append(f"NDX {ndx_above_50}% > 50MA 過熱")
    if ndx_above_200 > 85:
        is_overheated = True
        overheated_reasons.append(f"NDX {ndx_above_200}% > 200MA 過熱")
    if rut_above_50 > 90:
        is_overheated = True
        overheated_reasons.append(f"RUT {rut_above_50}% > 50MA 極度過熱")
    if ratio_history and ratio_history["percentile_in_12m"] > 90:
        is_overheated = True
        overheated_reasons.append("NDX/RUT 比值 12 月 90%ile+,極度集中")

    # Capitulation criteria (opposite)
    is_capitulation = False
    capitulation_reasons = []
    if ndx_above_50 < 30:
        is_capitulation = True
        capitulation_reasons.append(f"NDX 只 {ndx_above_50}% > 50MA 接近底")
    if rut_above_50 < 25:
        is_capitulation = True
        capitulation_reasons.append(f"RUT 只 {rut_above_50}% > 50MA 衰竭底")

    if is_overheated:
        verdict = "OVERHEATED"
    elif is_capitulation:
        verdict = "CAPITULATION_BOTTOM"
    else:
        verdict = "NORMAL"

    report = {
        "as_of": datetime.now(timezone.utc).isoformat(),
        "schema_version": 1,
        "indices_vs_ma": indices_vs_ma,
        "ndx_breadth_sample": {
            "above_50ma_pct": ndx_above_50,
            "above_200ma_pct": ndx_above_200,
            "sample_size": ndx_breadth.get("above_50ma", {}).get("above_count", 0) +
                            ndx_breadth.get("above_50ma", {}).get("below_count", 0),
        },
        "rut_breadth_sample": {
            "above_50ma_pct": rut_above_50,
            "above_200ma_pct": rut_above_200,
            "sample_size": rut_breadth.get("above_50ma", {}).get("above_count", 0) +
                            rut_breadth.get("above_50ma", {}).get("below_count", 0),
        },
        "ndx_rut_concentration_ratio": ratio_history,
        "verdict": verdict,
        "overheated_reasons": overheated_reasons,
        "capitulation_reasons": capitulation_reasons,
        "interpretation": {
            "OVERHEATED": "市場寬度過大 = 過熱;預期 3-6 月內回調機率上升",
            "NORMAL": "市場寬度健康;繼續正常操作",
            "CAPITULATION_BOTTOM": "市場寬度衰竭 = 接近底;準備加碼 alpha 機會",
        }.get(verdict, "?"),
        "thresholds_used": {
            "overheated_ndx_above_50ma": 85,
            "overheated_rut_above_50ma": 90,
            "capitulation_ndx_below_50ma": 30,
            "capitulation_rut_below_50ma": 25,
            "concentration_percentile": 90,
        },
    }
    out_path = out_dir / f"breadth-indicator-{today.date()}.json"
    out_path.write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")
    print(f"wrote {out_path}", file=sys.stderr)
    print(f"  verdict: {verdict}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
