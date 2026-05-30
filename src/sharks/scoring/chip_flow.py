"""Chip Flow (籌碼面) — Institutional ownership + smart money + short interest proxy.

5 sub-signals(自由免費 API 可取得的範圍):
  1. Volume burst — 量爆(機構進場代理)
  2. Price-volume divergence — 量價背離(主力出貨 / 入貨)
  3. Block trade proxy — 大單估算(單日量 > 3× 平均 + 小幅 price move = 累積)
  4. Short interest(若 yfinance 有提供)
  5. Institutional ownership %(yfinance 機構持股比)

Note: 真正籌碼面需要 Finnhub Premium / SEC Form 4 直接抓 — Phase 3 升級
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

# Tickers to analyse (your portfolio + key candidates)
DEFAULT_TICKERS = [
    # Your holdings of interest
    "NVDA", "AAPL", "MSFT", "META", "DELL", "AESI", "UEC", "TSLA",
    "NKE", "LULU", "ORCL", "STZ", "NOW", "CRM",
    # FOM-Alpha picks
    "LMT", "NOC", "ARM",
    # Serenity scout
    "RPID", "NTLA", "RGTI",
    # Bubble watch
    "OKLO", "SMCI",
    # Defense / hedge
    "GLD", "SH",
]


def fetch_yf_quote_info(ticker: str) -> dict:
    """Pull institutional / short data from yfinance."""
    try:
        t = yf.Ticker(ticker)
        info = t.info or {}
        return {
            "shortPercentOfFloat": info.get("shortPercentOfFloat"),
            "sharesShort": info.get("sharesShort"),
            "sharesShortPriorMonth": info.get("sharesShortPriorMonth"),
            "shortRatio": info.get("shortRatio"),
            "heldPercentInstitutions": info.get("heldPercentInstitutions"),
            "heldPercentInsiders": info.get("heldPercentInsiders"),
            "floatShares": info.get("floatShares"),
            "marketCap": info.get("marketCap"),
        }
    except Exception as e:
        return {"error": str(e)}


def fetch_daily_ohlcv(ticker: str, days: int = 90) -> pd.DataFrame:
    """Get last N days OHLCV."""
    end = pd.Timestamp.now()
    start = end - pd.Timedelta(days=days + 10)
    try:
        df = yf.download(ticker, start=start, end=end, interval="1d",
                         auto_adjust=True, progress=False, threads=False)
        if df.empty:
            return pd.DataFrame()
        if isinstance(df.columns, pd.MultiIndex):
            df = df.droplevel(1, axis=1)
        return df
    except Exception as e:
        print(f"  warn {ticker}: {e}", file=sys.stderr)
        return pd.DataFrame()


def volume_burst_detection(df: pd.DataFrame) -> dict:
    """Detect days with significantly elevated volume."""
    if df.empty or "Volume" not in df.columns or len(df) < 20:
        return {"status": "no_data"}
    vol = df["Volume"].dropna()
    if len(vol) < 20:
        return {"status": "insufficient_data"}
    avg_20d = float(vol.tail(20).mean())
    last_5d = vol.tail(5)
    bursts = []
    for date, v in last_5d.items():
        if v > 2.0 * avg_20d:
            bursts.append({"date": str(date.date()), "volume": int(v),
                           "ratio_vs_20d_avg": round(v / avg_20d, 2)})
    return {"avg_20d_volume": int(avg_20d),
            "recent_bursts": bursts,
            "burst_count_5d": len(bursts)}


def price_volume_divergence(df: pd.DataFrame) -> dict:
    """Detect bullish/bearish divergence."""
    if df.empty or len(df) < 20:
        return {"status": "no_data"}
    closes = df["Close"]
    vols = df["Volume"]
    # 20-day price change
    if len(closes) < 21:
        return {"status": "insufficient_data"}
    price_chg = float(closes.iloc[-1] / closes.iloc[-21] - 1)
    # 20-day avg vol vs prior 20-day avg
    recent_vol_avg = float(vols.tail(20).mean())
    prior_vol_avg = float(vols.iloc[-40:-20].mean()) if len(vols) > 40 else recent_vol_avg
    vol_chg = (recent_vol_avg - prior_vol_avg) / prior_vol_avg if prior_vol_avg > 0 else 0
    # Divergence classification
    divergence = "neutral"
    if price_chg > 0.05 and vol_chg < -0.20:
        divergence = "bearish (price up + volume down) — distribution"
    elif price_chg < -0.05 and vol_chg < -0.20:
        divergence = "bullish (price down + volume drying up) — selling exhausted"
    elif price_chg < -0.05 and vol_chg > 0.20:
        divergence = "bearish (price down + volume up) — active selling"
    elif price_chg > 0.05 and vol_chg > 0.20:
        divergence = "bullish (price up + volume up) — accumulation"
    return {
        "price_chg_20d_pct": round(price_chg * 100, 2),
        "vol_chg_pct": round(vol_chg * 100, 2),
        "divergence_class": divergence,
    }


def block_trade_proxy(df: pd.DataFrame) -> dict:
    """Estimate block accumulation: big vol + small price move."""
    if df.empty or len(df) < 30:
        return {"status": "no_data"}
    last_30 = df.tail(30).copy()
    avg_vol_pre = float(df["Volume"].iloc[-60:-30].mean()) if len(df) > 60 else float(df["Volume"].mean())
    accumulation_days = []
    for date, row in last_30.iterrows():
        v = row.get("Volume", 0)
        c = row.get("Close", 0)
        o = row.get("Open", 0)
        if v > 2.5 * avg_vol_pre and o > 0:
            price_range_pct = abs(c - o) / o * 100
            if price_range_pct < 1.5:  # small move + huge volume = accumulation
                accumulation_days.append({
                    "date": str(date.date()),
                    "volume_ratio": round(v / avg_vol_pre, 2),
                    "price_move_pct": round(price_range_pct, 2),
                })
    return {"accumulation_signal_days": accumulation_days,
            "count": len(accumulation_days)}


def chip_flow_score(ticker: str) -> dict:
    info = fetch_yf_quote_info(ticker)
    df = fetch_daily_ohlcv(ticker, 90)

    score = 50  # neutral start
    flags = []

    # Short interest
    short_pct = info.get("shortPercentOfFloat")
    if short_pct is not None:
        if short_pct > 0.20:
            score -= 20
            flags.append(f"HIGH_SHORT_INTEREST_{short_pct*100:.0f}%")
        elif short_pct > 0.10:
            score -= 5
            flags.append(f"MODERATE_SHORT_{short_pct*100:.0f}%")
        elif short_pct < 0.03:
            score += 5
            flags.append(f"LOW_SHORT_{short_pct*100:.0f}%")

    # Institutional ownership
    inst_pct = info.get("heldPercentInstitutions")
    if inst_pct is not None:
        if inst_pct > 0.80:
            score += 5
            flags.append(f"HIGH_INSTITUTIONAL_{inst_pct*100:.0f}%")
        elif inst_pct < 0.30:
            score -= 5
            flags.append(f"LOW_INSTITUTIONAL_{inst_pct*100:.0f}%")

    # Volume burst
    vb = volume_burst_detection(df)
    if vb.get("burst_count_5d", 0) >= 2:
        score += 10
        flags.append(f"MULTI_VOL_BURST")
    elif vb.get("burst_count_5d", 0) == 1:
        score += 5
        flags.append("SINGLE_VOL_BURST")

    # Divergence
    div = price_volume_divergence(df)
    div_class = div.get("divergence_class", "neutral")
    if "bullish" in div_class:
        score += 10
        flags.append("BULLISH_DIVERGENCE")
    elif "bearish" in div_class:
        score -= 10
        flags.append("BEARISH_DIVERGENCE")

    # Block accumulation
    block = block_trade_proxy(df)
    block_count = block.get("count", 0)
    if block_count >= 3:
        score += 15
        flags.append("STRONG_BLOCK_ACCUMULATION")
    elif block_count >= 1:
        score += 8
        flags.append("MILD_BLOCK_ACCUMULATION")

    return {
        "ticker": ticker,
        "chip_flow_score": max(0, min(100, score)),
        "flags": flags,
        "raw": {
            "shortPercentOfFloat": short_pct,
            "heldPercentInstitutions": inst_pct,
            "marketCap": info.get("marketCap"),
            "volume_burst": vb,
            "divergence": div,
            "block_accumulation": block,
        },
    }


def main():
    out_dir = Path("outputs")
    out_dir.mkdir(parents=True, exist_ok=True)
    today = datetime.now().strftime("%Y-%m-%d")
    print(f"Chip flow analysis as of {today}", file=sys.stderr)

    results = []
    for t in DEFAULT_TICKERS:
        try:
            r = chip_flow_score(t)
            results.append(r)
            print(f"  {t}: score {r['chip_flow_score']}, flags: {','.join(r['flags'])}", file=sys.stderr)
        except Exception as e:
            print(f"  {t}: error {e}", file=sys.stderr)

    results.sort(key=lambda x: x.get("chip_flow_score", 0), reverse=True)

    report = {
        "as_of": datetime.now(timezone.utc).isoformat(),
        "schema_version": 1,
        "ticker_count": len(results),
        "top_15_chip_flow": results[:15],
        "bottom_10_distribution_warning": [r for r in results
                                             if "BEARISH_DIVERGENCE" in r.get("flags", [])
                                             or "HIGH_SHORT_INTEREST" in str(r.get("flags", []))][:10],
        "strong_accumulation": [r for r in results
                                  if "STRONG_BLOCK_ACCUMULATION" in r.get("flags", [])],
        "squeeze_candidates": [r for r in results
                                if r["raw"].get("shortPercentOfFloat") and r["raw"]["shortPercentOfFloat"] > 0.15][:10],
    }
    out_path = out_dir / f"chip-flow-{today}.json"
    out_path.write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")
    print(f"wrote {out_path}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
