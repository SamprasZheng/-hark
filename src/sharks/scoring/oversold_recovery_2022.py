"""2022 升息錯殺股回升偵測器.

時代背景:2022 Fed 激進升息(0% → 5.25%),導致:
  - 軟體 SaaS / 高估值科技股 -50~-80%
  - 中小型生技 -60~-90%
  - 高 P/E 消費 -40~-60%
  - 房地產 / REIT -30~-50%

掃描條件:
  1. 從 2021 Q4 / 2022 H1 高點 → 2022 Q4 / 2023 Q1 低點 跌幅 ≥ 50%
  2. 從 2022/2023 低點以來 反彈 ≥ 20%
  3. 目前股價 < 2021 高點 50%(仍有 100%+ 上升空間到回到舊高)
  4. 突破 12 月 MA(月線)= 真實回升訊號
  5. 量能確認(本月 vs 6 月平均 volume)

輸出:深度錯殺 + 剛開始爬升的標的(教科書 deep value recovery)
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


# 候選池:歷史 2021/22 高估值受傷股 + 用戶 portfolio
WATCHLIST = [
    # SaaS 大跌(2021 高估值)
    "ZM", "DOCN", "PATH", "APPN", "EXTR", "ZS", "OKTA", "CRWD", "PANW",
    "DDOG", "MDB", "SNOW", "MNDY", "GTLB", "TWLO", "SQ", "ROKU", "PINS",
    "SHOP", "ETSY", "TDOC", "TWTR",
    # 高貝塔生技
    "BEAM", "NTLA", "CRSP", "EDIT", "PRME", "VERV", "REGN", "VRTX",
    "VKTX", "RXRX", "SDGR", "ABSI", "RGNX", "ALEC", "ABOS", "ALLO",
    "MRNA", "BNTX", "NVAX",
    # 中小型 EV / 自駕
    "RIVN", "LCID", "NKLA", "WKHS", "GOEV", "FFIE", "MULN", "BLNK",
    "CHPT", "EVGO", "QS",
    # 中小型空間
    "RKLB", "ASTS", "ACHR", "JOBY", "LUNR", "PL", "SPCE", "BKSY",
    "MNTS", "RDW", "VSAT",
    # 中小型氫能 / 燃料電池
    "PLUG", "BLDP", "FCEL", "BE",
    # 房地產 REIT
    "EQIX", "DLR", "AMT", "PLD", "CCI", "SBAC",
    # 太陽能
    "ENPH", "FSLR", "SEDG", "RUN", "NOVA", "ARRY", "SHLS", "TAN",
    # 中型科技
    "DELL", "HPQ", "INTC", "AMD",
    # 消費高 P/E
    "LULU", "NKE", "VFC", "VSCO", "RH", "WSM",
    # 跨境零售
    "CRSR", "BBY", "TGT", "AMZN",
    # 中國 ADR
    "BABA", "BIDU", "PDD", "JD", "NIO", "XPEV", "LI", "TME",
    # 媒體
    "DIS", "NFLX", "PARA", "WBD", "T", "VZ",
    # 通訊小型
    "LITE", "COHR", "CIEN", "AAOI",
    # 你 portfolio 內的
    "ORCL", "ENPH", "ARRY", "TAC", "GFS", "SKYT",
    "QBTS", "QUBT", "RGTI", "IONQ",
    "RIOT", "MARA", "WULF", "BTBT", "CIFR", "CLSK",
    "MSTR", "COIN",
    # 其他 deep value
    "GE", "BA", "PFE", "MRK", "ABBV",
    "DOW", "FCX", "NEM", "AGRO",
    # User-specific
    "NVDA", "MSFT", "META", "AAPL", "GOOGL", "TSLA",
    "LMT", "NOC", "RTX",
    "UEC", "AESI", "DNN", "VAL", "TPL", "GEV", "AEIS",
]


def fetch_monthly(tickers, start, end):
    raw = yf.download(tickers, start=start, end=end, interval="1mo",
                     auto_adjust=True, progress=False, group_by="ticker", threads=True)
    closes = {}
    volumes = {}
    for t in tickers:
        try:
            if isinstance(raw.columns, pd.MultiIndex):
                closes[t] = raw[t]["Close"]
                volumes[t] = raw[t]["Volume"]
            else:
                closes[t] = raw["Close"]
                volumes[t] = raw["Volume"]
        except (KeyError, ValueError):
            pass
    cdf = pd.DataFrame(closes).sort_index()
    vdf = pd.DataFrame(volumes).sort_index()
    if cdf.index.tz is not None:
        cdf.index = cdf.index.tz_localize(None)
        vdf.index = vdf.index.tz_localize(None)
    return cdf, vdf


def oversold_recovery_score(closes, volumes, ticker, as_of):
    s = closes.get(ticker)
    v = volumes.get(ticker)
    if s is None or s.dropna().empty:
        return None
    s = s.dropna()
    pre = s.loc[:as_of]
    if len(pre) < 36:  # need ~3 years of data
        return None
    last = float(pre.iloc[-1])
    if last <= 0:
        return None

    # 2021 Q4 high — peak of pre-rate-hike bubble
    h2021_window = pre.loc["2021-01-01":"2022-06-30"]
    if h2021_window.empty:
        return None
    h2021_high = float(h2021_window.max())
    h2021_high_date = str(h2021_window.idxmax().date())

    # 2022 Q4 / 2023 Q1 low — bottom after rate hikes
    low_window = pre.loc["2022-07-01":"2023-12-31"]
    if low_window.empty:
        return None
    low_2022 = float(low_window.min())
    low_2022_date = str(low_window.idxmin().date())

    # Drawdown from 2021 high to 2022 low
    drawdown = (h2021_high - low_2022) / h2021_high if h2021_high > 0 else 0
    # Recovery from low to now
    recovery_from_low = (last - low_2022) / low_2022 if low_2022 > 0 else 0
    # Still down from 2021 high
    dist_below_2021_high = (h2021_high - last) / h2021_high if h2021_high > 0 else 0

    # 12-month MA
    if len(pre) < 12:
        return None
    ma_12m = float(pre.iloc[-12:].mean())
    above_ma_12m = last > ma_12m

    # Recent momentum
    r3 = float(pre.iloc[-1] / pre.iloc[-4] - 1) if len(pre) > 3 else 0
    r6 = float(pre.iloc[-1] / pre.iloc[-7] - 1) if len(pre) > 6 else 0

    # Volume confirmation
    vol_confirmation = False
    if v is not None and not v.dropna().empty:
        v_clean = v.dropna()
        v_pre = v_clean.loc[:as_of]
        if len(v_pre) > 6:
            recent_vol = float(v_pre.iloc[-1])
            avg_vol_6m = float(v_pre.iloc[-7:-1].mean())
            if avg_vol_6m > 0:
                vol_confirmation = recent_vol > 1.3 * avg_vol_6m

    # Scoring (0-100)
    score = 0
    flags = []
    notes = []

    # Deep drawdown requirement (oversold)
    if drawdown >= 0.50:
        score += 25
        flags.append(f"OVERSOLD_DD_{drawdown*100:.0f}%")
        if drawdown >= 0.70:
            score += 10
            flags.append("DEEP_OVERSOLD")
    else:
        return None  # Not an "oversold" case

    # Recovery started
    if recovery_from_low >= 0.20:
        score += 15
        flags.append(f"RECOVERY_FROM_LOW_+{recovery_from_low*100:.0f}%")
    if recovery_from_low >= 0.50:
        score += 10
        flags.append("STRONG_RECOVERY")

    # Still has upside (not back to 2021 high)
    if dist_below_2021_high > 0.40:
        score += 15
        flags.append(f"STILL_DOWN_-{dist_below_2021_high*100:.0f}%_FROM_2021_HIGH")
    if dist_below_2021_high > 0.65:
        score += 5
        flags.append("MASSIVE_UPSIDE_TO_2021_HIGH")

    # Trend confirmation
    if above_ma_12m:
        score += 10
        flags.append("ABOVE_12M_MA")

    # Recent momentum
    if r6 > 0.15:
        score += 10
        flags.append(f"6M_MOMENTUM_+{r6*100:.0f}%")
    if r3 > 0.10:
        score += 5

    # Volume
    if vol_confirmation:
        score += 10
        flags.append("VOLUME_CONFIRMATION")

    # Notes
    notes.append(f"2021 high ${h2021_high:.2f} @ {h2021_high_date}")
    notes.append(f"2022/23 low ${low_2022:.2f} @ {low_2022_date}")
    notes.append(f"Now ${last:.2f}")

    return {
        "ticker": ticker,
        "score": score,
        "flags": flags,
        "drawdown_from_2021_high_pct": round(drawdown * 100, 1),
        "recovery_from_low_pct": round(recovery_from_low * 100, 1),
        "dist_below_2021_high_pct": round(dist_below_2021_high * 100, 1),
        "current_price": round(last, 2),
        "h2021_high": round(h2021_high, 2),
        "h2021_high_date": h2021_high_date,
        "low_2022": round(low_2022, 2),
        "low_2022_date": low_2022_date,
        "ma_12m": round(ma_12m, 2),
        "above_ma_12m": above_ma_12m,
        "r3m_pct": round(r3 * 100, 1),
        "r6m_pct": round(r6 * 100, 1),
        "notes": " | ".join(notes),
    }


def main():
    out_dir = Path("outputs")
    out_dir.mkdir(parents=True, exist_ok=True)
    today = pd.Timestamp("2026-05-30")
    print(f"Oversold 2022 recovery scanner — {today.date()}", file=sys.stderr)
    print(f"  watchlist: {len(set(WATCHLIST))} tickers", file=sys.stderr)
    closes, vols = fetch_monthly(list(set(WATCHLIST)), "2020-01-01", "2026-05-30")
    print(f"  data: {len(closes.columns)} tickers", file=sys.stderr)

    results = []
    for t in closes.columns:
        try:
            sc = oversold_recovery_score(closes, vols, t, today)
            if sc:
                results.append(sc)
        except Exception:
            pass
    results.sort(key=lambda x: x["score"], reverse=True)

    # Categorize
    just_breakout = [r for r in results
                      if r["above_ma_12m"] and r["recovery_from_low_pct"] < 80
                      and r["dist_below_2021_high_pct"] > 50][:25]
    deep_correction_still_low = [r for r in results
                                   if r["dist_below_2021_high_pct"] > 70
                                   and r["recovery_from_low_pct"] < 30][:25]
    strong_recovery_winners = [r for r in results
                                 if r["recovery_from_low_pct"] > 100][:25]

    report = {
        "as_of": datetime.now(timezone.utc).isoformat(),
        "schema_version": 1,
        "context": "2022 升息錯殺股回升偵測 — 找剛從谷底爬起來的中型股",
        "watchlist_attempted": len(set(WATCHLIST)),
        "tickers_with_data": len(closes.columns),
        "tickers_scored": len(results),
        "criteria": {
            "drawdown_from_2021_high_min": "≥50%",
            "recovery_from_low_min": "≥20%",
            "trend": "above 12-month MA",
            "volume_confirmation": "current month > 1.3× 6-month avg",
        },
        "top_25_overall": [{"rank": i+1, **r} for i, r in enumerate(results[:25])],
        "just_breaking_out": just_breakout,
        "still_deep_buy_zone": deep_correction_still_low,
        "strong_recovery_already_winners": strong_recovery_winners,
    }
    out_path = out_dir / f"oversold-2022-recovery-{today.date()}.json"
    out_path.write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")
    print(f"wrote {out_path}", file=sys.stderr)
    print(f"  top 5: {[r['ticker'] for r in results[:5]]}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
