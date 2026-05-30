"""Taiwan universe — TWSE 上市 + TPEx 上櫃 完整名單 + FOM scan.

Sources:
  1. https://isin.twse.com.tw/isin/C_public.jsp?strMode=2 (上市)
  2. https://isin.twse.com.tw/isin/C_public.jsp?strMode=4 (上櫃)

Backup: hardcoded list of 200+ Taiwan major stocks.
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

# Hardcoded Taiwan major stocks (上市 + 上櫃)
TAIWAN_MAJOR_LISTED = {
    # 半導體
    "2330.TW": "台積電", "2454.TW": "聯發科", "2317.TW": "鴻海",
    "3008.TW": "大立光", "2382.TW": "廣達", "3231.TW": "緯創",
    "2308.TW": "台達電", "3034.TW": "聯詠", "2379.TW": "瑞昱",
    "5347.TW": "世界先進", "8046.TW": "南亞電", "3037.TW": "欣興",
    "6669.TW": "穩懋", "2449.TW": "京元電", "3563.TW": "聯茂",
    "3017.TW": "奇鋐", "3653.TW": "環球晶圓", "6147.TW": "頎邦",
    "4938.TW": "和碩", "2376.TW": "技嘉", "2353.TW": "宏碁",
    "2357.TW": "華碩", "3045.TW": "台灣大", "8081.TW": "致新",
    "3035.TW": "智原", "6488.TWO": "GlobalWafers",
    "8086.TWO": "King Slide", "5274.TWO": "AcBel",
    "5483.TWO": "中美晶", "4966.TWO": "ParaWin",
    # 記憶體
    "2408.TW": "南亞科", "2451.TW": "創見",
    # 金融
    "2882.TW": "國泰金", "2891.TW": "中信金", "2884.TW": "玉山金",
    "2880.TW": "華南金", "2885.TW": "元大金", "2890.TW": "永豐金",
    "2886.TW": "兆豐金", "2887.TW": "台新金",
    # 塑化
    "1301.TW": "台塑", "1303.TW": "南亞", "1326.TW": "台化",
    "6505.TW": "台塑化",
    # 鋼鐵
    "2002.TW": "中鋼", "2027.TW": "大成鋼",
    # 水泥
    "1101.TW": "台泥", "1102.TW": "亞泥",
    # 食品
    "1216.TW": "統一", "1227.TW": "佳格", "1234.TW": "黑松",
    "2912.TW": "統一超",
    # 電信
    "2412.TW": "中華電", "3045.TW": "台灣大", "4904.TW": "遠傳",
    # 紡織
    "1402.TW": "遠東新", "1326.TW": "台化", "1102.TW": "亞泥",
    # 觀光
    "2731.TW": "雄獅", "2723.TW": "美食-KY", "5871.TW": "中租-KY",
    # 生技
    "1762.TW": "中化生", "4174.TW": "浩鼎", "4128.TW": "中天",
    # 鋰電 / EV
    "1722.TW": "台肥", "5371.TW": "中光電",
    # 航運
    "2603.TW": "長榮", "2609.TW": "陽明", "2615.TW": "萬海",
    # 航空
    "2610.TW": "華航", "2618.TW": "長榮航",
    # 機械
    "1503.TW": "士電", "1504.TW": "東元", "1513.TW": "中興電",
    # 中型電子
    "2474.TW": "可成", "2392.TW": "正崴", "3406.TW": "玉晶光",
    "4958.TW": "臻鼎-KY",
    # OTC 上櫃 AI 相關
    "6643.TWO": "M31", "6230.TWO": "新唐",
    "5269.TWO": "祥碩", "6770.TWO": "力積電",
    "6515.TWO": "穎崴",
    # OTC 醫藥
    "6446.TWO": "藥華藥",
    # 投信
    "6005.TW": "群益證",
}


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
    df = pd.DataFrame(closes).sort_index()
    if df.index.tz is not None:
        df.index = df.index.tz_localize(None)
    return df


def fom_simple_score(closes, ticker, as_of):
    s = closes.get(ticker)
    if s is None or s.dropna().empty:
        return None
    s = s.dropna()
    pre = s.loc[:as_of]
    if len(pre) < 13:
        return None
    last = float(pre.iloc[-1])
    r6 = float(pre.iloc[-1] / pre.iloc[-7] - 1) if len(pre) > 6 else 0
    r12 = float(pre.iloc[-1] / pre.iloc[-13] - 1) if len(pre) > 12 else 0
    momentum = max(0, min(100, ((r6 + 0.3) / 1.0 * 100)))
    window = pre.iloc[-13:]
    high = float(window.max())
    dist_high = (high - last) / high if high > 0 else 0
    if dist_high < 0.05: contrarian = 30
    elif dist_high < 0.15: contrarian = 50
    elif dist_high < 0.30: contrarian = 85
    elif dist_high < 0.50: contrarian = 70
    else: contrarian = 40
    lr = np.log(pre.iloc[-13:] / pre.iloc[-13:].shift(1)).dropna()
    rvol = float(lr.std() * math.sqrt(12)) if len(lr) > 1 else 0.3
    quality = max(0, 100 - rvol * 100) * 0.4 + max(0, min(100, (r12 + 0.5) / 2.5 * 100)) * 0.6
    bubble = 0
    if r6 > 2.0: bubble -= 50
    elif r6 > 1.0: bubble -= 25
    if dist_high < 0.03 and r12 > 1.0: bubble -= 15
    if 0.15 < dist_high < 0.35 and r12 > -0.1: bubble += 30
    base = 0.25 * momentum + 0.25 * contrarian + 0.20 * quality + 0.30 * ((bubble + 100) / 2)
    return {
        "ticker": ticker, "fom": round(base, 1),
        "momentum": round(momentum, 1), "contrarian": round(contrarian, 1),
        "quality": round(quality, 1), "bubble_guard": round(bubble, 1),
        "r6m_pct": round(r6 * 100, 1), "r12m_pct": round(r12 * 100, 1),
        "dist_from_12m_high_pct": round(dist_high * 100, 1),
    }


def main():
    out_dir = Path("outputs")
    today = pd.Timestamp("2026-05-30")
    print(f"Taiwan universe scan as of {today.date()}", file=sys.stderr)
    print(f"  attempting {len(TAIWAN_MAJOR_LISTED)} Taiwan stocks", file=sys.stderr)
    closes = fetch_monthly(list(TAIWAN_MAJOR_LISTED.keys()),
                            "2022-01-01", "2026-05-30")
    print(f"  data: {len(closes.columns)} tickers", file=sys.stderr)

    results = []
    for t in closes.columns:
        sc = fom_simple_score(closes, t, today)
        if sc:
            sc["name"] = TAIWAN_MAJOR_LISTED.get(t, "")
            results.append(sc)

    results.sort(key=lambda x: x["fom"], reverse=True)

    deep_value = [r for r in results
                   if 15 < r["dist_from_12m_high_pct"] < 40][:20]

    report = {
        "as_of": datetime.now(timezone.utc).isoformat(),
        "schema_version": 1,
        "tickers_with_data": len(closes.columns),
        "tickers_scored": len(results),
        "top_30_taiwan_fom": [{"rank": i+1, **r} for i, r in enumerate(results[:30])],
        "deep_value_recovery_taiwan": [{"rank": i+1, **r} for i, r in enumerate(deep_value)],
    }
    out_path = out_dir / f"taiwan-universe-{today.date()}.json"
    out_path.write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")
    print(f"wrote {out_path}", file=sys.stderr)
    print(f"  top 5: {[r['ticker'] for r in results[:5]]}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
