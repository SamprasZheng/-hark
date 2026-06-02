"""TWSE 完整台股 universe — 從 openapi.twse.com.tw + TPEx 拉 300+ 完整名單.

Sources:
  1. https://openapi.twse.com.tw/v1/exchangeReport/STOCK_DAY_ALL (上市每日)
  2. https://www.tpex.org.tw (上櫃)
  3. Fallback: hardcoded comprehensive list
"""

from __future__ import annotations

import json
import math
import sys
import urllib.request
import warnings
from datetime import datetime, timezone
from io import StringIO
from pathlib import Path

warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)

import numpy as np
import pandas as pd
import yfinance as yf


def fetch_twse_all_listed() -> dict:
    """Pull TWSE 上市 daily snapshot - all symbols."""
    url = "https://openapi.twse.com.tw/v1/exchangeReport/STOCK_DAY_ALL"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=30) as r:
            data = json.loads(r.read().decode("utf-8"))
        # data is list of {Code, Name, TradeVolume, ..., ClosingPrice}
        out = {}
        for row in data:
            code = row.get("Code", "").strip()
            name = row.get("Name", "").strip()
            if code and len(code) == 4 and code.isdigit():
                out[f"{code}.TW"] = name
        return out
    except Exception as e:
        print(f"  WARN: TWSE openapi failed: {e}", file=sys.stderr)
        return {}


def fetch_tpex_all() -> dict:
    """Pull TPEx 上櫃 — uses TPEx API."""
    url = "https://www.tpex.org.tw/openapi/v1/tpex_mainboard_quotes"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=30) as r:
            data = json.loads(r.read().decode("utf-8"))
        out = {}
        for row in data:
            code = row.get("SecuritiesCompanyCode", "").strip()
            name = row.get("CompanyName", "").strip()
            if code and len(code) == 4 and code.isdigit():
                out[f"{code}.TWO"] = name
        return out
    except Exception as e:
        print(f"  WARN: TPEx openapi failed: {e}", file=sys.stderr)
        return {}


# Hardcoded fallback if both APIs fail
TAIWAN_FALLBACK = {
    # 半導體 (covered in taiwan_universe already + more)
    "2330.TW": "台積電", "2454.TW": "聯發科", "2317.TW": "鴻海",
    "3008.TW": "大立光", "2382.TW": "廣達", "3231.TW": "緯創",
    "2308.TW": "台達電", "3034.TW": "聯詠", "2379.TW": "瑞昱",
    "5347.TW": "世界先進", "8046.TW": "南亞電", "3037.TW": "欣興",
    "6669.TW": "穩懋", "2449.TW": "京元電", "3563.TW": "聯茂",
    "3017.TW": "奇鋐", "3653.TW": "環球晶圓", "6147.TW": "頎邦",
    "4938.TW": "和碩", "2376.TW": "技嘉", "2353.TW": "宏碁",
    "2357.TW": "華碩", "3045.TW": "台灣大", "8081.TW": "致新",
    "3035.TW": "智原", "2408.TW": "南亞科", "2451.TW": "創見",
    # 重工
    "2882.TW": "國泰金", "2891.TW": "中信金", "2884.TW": "玉山金",
    "2880.TW": "華南金", "2885.TW": "元大金", "2890.TW": "永豐金",
    "2886.TW": "兆豐金", "2887.TW": "台新金", "2883.TW": "開發金",
    "5880.TW": "合庫金",
    # 塑化
    "1301.TW": "台塑", "1303.TW": "南亞", "1326.TW": "台化",
    "6505.TW": "台塑化",
    # 鋼鐵
    "2002.TW": "中鋼", "2027.TW": "大成鋼", "2014.TW": "中鴻",
    # 食品
    "1216.TW": "統一", "1227.TW": "佳格", "2912.TW": "統一超",
    # 電信
    "2412.TW": "中華電", "4904.TW": "遠傳",
    # 航運
    "2603.TW": "長榮", "2609.TW": "陽明", "2615.TW": "萬海",
    "2610.TW": "華航", "2618.TW": "長榮航",
    # 機械
    "1503.TW": "士電", "1504.TW": "東元", "1513.TW": "中興電",
    # 中型電子
    "2474.TW": "可成", "2392.TW": "正崴", "3406.TW": "玉晶光",
    "4958.TW": "臻鼎-KY", "5388.TW": "中磊",
    # OTC 上櫃
    "6643.TWO": "M31", "6230.TWO": "新唐", "5269.TWO": "祥碩",
    "6770.TWO": "力積電", "6515.TWO": "穎崴", "6488.TWO": "環球晶圓 OTC",
    "8086.TWO": "King Slide", "5274.TWO": "AcBel", "5483.TWO": "中美晶",
    "4966.TWO": "ParaWin", "6446.TWO": "藥華藥",
    # 太陽能 / 綠能
    "1722.TW": "台肥", "5371.TW": "中光電", "8011.TW": "台通",
    "6182.TW": "合晶",
    # 中型 AI 周邊
    "6285.TW": "啟碁", "4763.TW": "材料-KY", "2330.TW": "台積電",
    "3596.TW": "智易", "4977.TW": "眾達-KY", "8261.TW": "富鼎",
    # 醫材
    "4961.TW": "天鈺", "1762.TW": "中化生", "4174.TW": "浩鼎",
    # 房地產
    "2548.TW": "華固", "9945.TW": "潤泰新",
    # 紡織
    "1402.TW": "遠東新",
    # 自行車
    "9921.TW": "巨大", "9914.TW": "美利達",
    # 觀光
    "2731.TW": "雄獅", "5871.TW": "中租-KY",
}


def fetch_monthly_safe(tickers, start, end, batch_size=30):
    """Bulk pull with safe batching."""
    closes = {}
    for i in range(0, len(tickers), batch_size):
        batch = tickers[i:i+batch_size]
        try:
            raw = yf.download(batch, start=start, end=end, interval="1mo",
                             auto_adjust=True, progress=False, group_by="ticker", threads=True)
            for t in batch:
                try:
                    if isinstance(raw.columns, pd.MultiIndex):
                        s = raw[t]["Close"]
                    else:
                        s = raw["Close"]
                    if not s.dropna().empty:
                        closes[t] = s
                except (KeyError, ValueError):
                    pass
        except Exception:
            pass
        if i % 60 == 0:
            print(f"  progress: {i}/{len(tickers)} ({len(closes)} ok)", file=sys.stderr)
    df = pd.DataFrame(closes).sort_index()
    if df.index.tz is not None:
        df.index = df.index.tz_localize(None)
    return df


def fom_score(closes, ticker, as_of):
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
    out_dir.mkdir(parents=True, exist_ok=True)
    today = pd.Timestamp("2026-05-30")
    print(f"TWSE complete scan as of {today.date()}", file=sys.stderr)

    print("Fetching TWSE openapi...", file=sys.stderr)
    twse = fetch_twse_all_listed()
    print(f"  上市: {len(twse)} tickers", file=sys.stderr)

    print("Fetching TPEx openapi...", file=sys.stderr)
    tpex = fetch_tpex_all()
    print(f"  上櫃: {len(tpex)} tickers", file=sys.stderr)

    # Merge + fallback
    all_taiwan = {**TAIWAN_FALLBACK, **twse, **tpex}
    print(f"  Combined: {len(all_taiwan)} unique Taiwan stocks", file=sys.stderr)

    # Limit for tractability
    sample = list(all_taiwan.keys())[:500]
    print(f"  scoring sample of {len(sample)}", file=sys.stderr)

    closes = fetch_monthly_safe(sample, "2023-01-01", "2026-05-30", batch_size=25)
    print(f"  data: {len(closes.columns)} tickers", file=sys.stderr)

    results = []
    for t in closes.columns:
        sc = fom_score(closes, t, today)
        if sc:
            sc["name"] = all_taiwan.get(t, "")
            sc["board"] = "上市" if t.endswith(".TW") else "上櫃"
            results.append(sc)
    results.sort(key=lambda x: x["fom"], reverse=True)

    deep_value = [r for r in results
                   if 15 < r["dist_from_12m_high_pct"] < 40][:25]
    overheated = [r for r in results if r["bubble_guard"] < -20][:20]

    report = {
        "as_of": datetime.now(timezone.utc).isoformat(),
        "schema_version": 1,
        "sources": ["openapi.twse.com.tw", "tpex openapi", "hardcoded fallback"],
        "twse_listed": len(twse),
        "tpex_listed": len(tpex),
        "combined_universe": len(all_taiwan),
        "sample_scored": len(results),
        "top_50_taiwan_fom": [{"rank": i+1, **r} for i, r in enumerate(results[:50])],
        "deep_value_recovery": [{"rank": i+1, **r} for i, r in enumerate(deep_value)],
        "overheated_warning": [{"rank": i+1, **r} for i, r in enumerate(overheated)],
    }
    out_path = out_dir / f"twse-complete-{today.date()}.json"
    out_path.write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")
    print(f"wrote {out_path}", file=sys.stderr)
    print(f"  top 5: {[r['ticker'] for r in results[:5]]}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
