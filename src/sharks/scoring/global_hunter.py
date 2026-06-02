"""Global Hunter — Taiwan + OTC + Commodities + High-Excitement Small Cap.

Anti-Buffett variant:
  - Embraces volatility (high realised vol bonus)
  - Catalyst-driven (event proximity)
  - Microcap upside ($100M - $2B preferred)
  - Sympathy / supply-chain mapping
  - Earnings inflection (revenue +50% YoY proxy)

Universe spans:
  - Taiwan listed (2330.TW etc.)
  - Taiwan OTC (.TWO)
  - US-listed Taiwan ADRs
  - Commodity ETFs (oil, copper, gold, uranium, lithium, agriculture)
  - Microcap US specialty plays
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

# ─── Taiwan stock universe (yfinance .TW suffix) ───
TAIWAN_LARGE = {
    "2330.TW": "TSMC 台積電",
    "2454.TW": "MediaTek 聯發科",
    "2317.TW": "Foxconn 鴻海",
    "3008.TW": "LARGAN 大立光(光學)",
    "2308.TW": "Delta Electronics 台達電(電源)",
    "2382.TW": "Quanta 廣達(伺服器代工)",
    "2376.TW": "Gigabyte 技嘉",
    "3037.TW": "Unimicron 欣興(載板)",
    "6669.TW": "Win Semi 穩懋(化合半導)",
    "3231.TW": "Wistron 緯創(AI 伺服器代工)",
    "2353.TW": "Acer 宏碁",
    "2357.TW": "Asus 華碩",
    "2474.TW": "Catcher 可成",
    "2392.TW": "Cheng Uei 正崴",
    "6505.TW": "Formosa Petro 台塑化",
    "2412.TW": "Chunghwa Telecom 中華電",
    "2408.TW": "Nanya Tech 南亞科(記憶體)",
}

TAIWAN_MID_AI = {
    "3231.TW": "Wistron",
    "2382.TW": "Quanta",
    "2376.TW": "Gigabyte",
    "3017.TW": "Asia Vital Components 奇鋐(散熱)",
    "3653.TW": "GlobalWafers 環球晶圓(矽晶圓)",
    "3034.TW": "Novatek 聯詠(顯示驅動)",
    "2379.TW": "Realtek 瑞昱(IC)",
    "5347.TW": "Vanguard 世界先進(成熟製程)",
    "2449.TW": "King Yuan 京元電(測試)",
    "8046.TW": "Nan Ya PCB 南亞電(PCB)",
    "3563.TW": "Iteq 聯茂(銅箔基板)",
}

# Taiwan OTC (.TWO suffix) — small/mid cap higher excitement
TAIWAN_OTC = {
    "6515.TWO": "Aspeed 信驊(BMC 晶片,AI 伺服器隱形要角)",
    "5269.TWO": "Asmedia 祥碩(USB 控制 IC)",
    "6770.TWO": "AP Memory 力積電(記憶體)",
    "5483.TWO": "Sino-American Silicon 中美晶(矽晶圓)",
    "6271.TWO": "TPK Holding 宸鴻(觸控面板)",
    "6446.TWO": "PharmaEssentia 藥華藥(罕病藥)",
    "6488.TWO": "GlobalWafers TWO listing",
    "4966.TWO": "ParaWin 高僑(載板)",
    "8086.TWO": "King Slide 川湖(伺服器滑軌)",
    "5274.TWO": "AcBel 信邦(伺服器電源)",
}

# Commodity ETFs (high excitement, macro catalysts)
COMMODITY = {
    # Oil
    "USO": "Crude Oil",
    "BNO": "Brent Oil",
    "XLE": "Energy Sector",
    "XOP": "Oil & Gas Production",
    # Gold/Silver
    "GLD": "Gold",
    "GDX": "Gold Miners",
    "GDXJ": "Jr Gold Miners",
    "SLV": "Silver",
    "SIL": "Silver Miners",
    # Industrial metals
    "COPX": "Copper Miners",
    "JJC": "Copper",
    # Uranium
    "URA": "Uranium ETF",
    "URNM": "Uranium Mining",
    "CCJ": "Cameco (uranium)",
    # Lithium
    "LIT": "Lithium ETF",
    "ALB": "Albemarle (lithium)",
    # Agriculture
    "DBA": "Agriculture Basket",
    "CORN": "Corn",
    "WEAT": "Wheat",
    "SOYB": "Soybeans",
    # Natural gas
    "UNG": "Natural Gas",
    # Carbon
    "KRBN": "Carbon Allowances",
}

# US-listed small-cap high excitement (anti-Buffett, alpha)
US_SMALL_EXCITING = {
    # Quantum (speculative)
    "IONQ": "IonQ quantum",
    "RGTI": "Rigetti",
    "QBTS": "D-Wave Quantum",
    "QUBT": "Quantum Computing Inc",
    # Space
    "RKLB": "Rocket Lab",
    "ACHR": "Archer Aviation",
    "ASTS": "AST SpaceMobile",
    "PL": "Planet Labs",
    "LUNR": "Intuitive Machines",
    # Robotics
    "SYM": "Symbotic",
    "PATH": "UiPath",
    "BBAI": "BigBear.ai",
    # Crypto miners
    "RIOT": "Riot Platforms",
    "MARA": "Marathon Digital",
    "BTBT": "Bit Digital",
    "CIFR": "Cipher Mining",
    "WULF": "TeraWulf",
    # Nuclear small-cap
    "NXE": "NexGen Energy",
    "LEU": "Centrus Energy",
    "SMR": "NuScale Power",
    "OKLO": "Oklo Inc",
    "BWXT": "BWX Technologies",
    # Specialty semis
    "AEHR": "AEHR Test",
    "AOSL": "Alpha Omega Semi",
    "AXTI": "AXT Inc",
    "POET": "POET Technologies",
    # EV / Battery
    "RIVN": "Rivian",
    "LCID": "Lucid",
    "AMPX": "Amprius",
    # AI software (small)
    "AI": "C3.ai",
    "BBAI": "BigBear.ai",
    # Frontier biotech
    "CRSP": "CRISPR",
    "BEAM": "Beam Therapeutics",
    "NTLA": "Intellia",
    # Specialty pharma sympathy
    "MNMD": "Mind Medicine",
    # Speciality industrials
    "VRT": "Vertiv",
}

ALL_HUNT = list({**TAIWAN_LARGE, **TAIWAN_MID_AI, **TAIWAN_OTC, **COMMODITY, **US_SMALL_EXCITING}.keys())


def fetch_monthly(tickers, start, end):
    raw = yf.download(tickers, start=start, end=end, interval="1mo",
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


def excitement_score(closes, ticker, as_of):
    """Score 0-100 based on: realised vol (high = exciting), momentum, distance from 12m high.

    Anti-Buffett: high vol REWARDS, not penalises.
    """
    s = closes.get(ticker)
    if s is None or s.dropna().empty:
        return None
    s = s.dropna()
    pre = s.loc[:as_of]
    if len(pre) < 12:
        return None
    # Realised vol (higher = more exciting)
    lr = np.log(pre.iloc[-13:] / pre.iloc[-13:].shift(1)).dropna()
    rvol = float(lr.std() * math.sqrt(12)) if len(lr) > 1 else 0.3
    vol_score = min(100, rvol * 100)  # +100% vol → 100
    # Momentum
    r6 = float(pre.iloc[-1] / pre.iloc[-7] - 1) if len(pre) > 6 else 0.0
    r12 = float(pre.iloc[-1] / pre.iloc[-13] - 1) if len(pre) > 12 else 0.0
    mom_score = max(0, min(100, ((r6 + 0.3) / 1.0 * 100)))
    # Recovery bonus: deep correction + recent bounce
    window = pre.iloc[-13:]
    high = float(window.max())
    last = float(pre.iloc[-1])
    dist = float((high - last) / high) if high > 0 else 0.0
    # Sweet spot: 20-40% below 12m high (deep correction, bouncable)
    if 0.20 < dist < 0.40 and r6 > -0.05:
        recovery_score = 80
    elif dist > 0.40 and r6 > 0.05:
        recovery_score = 100  # Deeply discounted + just bounced
    elif dist < 0.05:
        recovery_score = 20  # too close to top
    else:
        recovery_score = 50
    final = 0.35 * vol_score + 0.35 * mom_score + 0.30 * recovery_score
    return {
        "ticker": ticker,
        "rvol_annual_pct": round(rvol * 100, 1),
        "r6m_pct": round(r6 * 100, 1),
        "r12m_pct": round(r12 * 100, 1),
        "dist_from_12m_high_pct": round(dist * 100, 1),
        "excitement_final": round(final, 1),
        "vol_score": round(vol_score, 1),
        "momentum_score": round(mom_score, 1),
        "recovery_score": round(recovery_score, 1),
    }


def main():
    out_dir = Path("outputs")
    out_dir.mkdir(parents=True, exist_ok=True)
    today = pd.Timestamp("2026-05-30")
    print(f"Global Hunter as of {today.date()}", file=sys.stderr)
    closes = fetch_monthly(ALL_HUNT, "2022-01-01", "2026-05-30")
    print(f"  data: {len(closes.columns)} tickers", file=sys.stderr)

    results = {"taiwan_large": [], "taiwan_mid_ai": [], "taiwan_otc": [],
                "commodity": [], "us_small_exciting": []}
    for t, name in TAIWAN_LARGE.items():
        s = excitement_score(closes, t, today)
        if s:
            s["name"] = name
            results["taiwan_large"].append(s)
    for t, name in TAIWAN_MID_AI.items():
        s = excitement_score(closes, t, today)
        if s:
            s["name"] = name
            results["taiwan_mid_ai"].append(s)
    for t, name in TAIWAN_OTC.items():
        s = excitement_score(closes, t, today)
        if s:
            s["name"] = name
            results["taiwan_otc"].append(s)
    for t, name in COMMODITY.items():
        s = excitement_score(closes, t, today)
        if s:
            s["name"] = name
            results["commodity"].append(s)
    for t, name in US_SMALL_EXCITING.items():
        s = excitement_score(closes, t, today)
        if s:
            s["name"] = name
            results["us_small_exciting"].append(s)

    # Sort each bucket
    for k in results:
        results[k].sort(key=lambda x: x["excitement_final"], reverse=True)

    # Cross-bucket top-15 excitement
    all_scored = []
    for k, items in results.items():
        for it in items:
            it_copy = dict(it)
            it_copy["bucket"] = k
            all_scored.append(it_copy)
    all_scored.sort(key=lambda x: x["excitement_final"], reverse=True)

    report = {
        "as_of": datetime.now(timezone.utc).isoformat(),
        "schema_version": 1,
        "methodology": "Excitement = 0.35 vol + 0.35 momentum + 0.30 recovery (Anti-Buffett)",
        "by_bucket": {
            "taiwan_large_top5": results["taiwan_large"][:5],
            "taiwan_mid_ai_top5": results["taiwan_mid_ai"][:5],
            "taiwan_otc_top5": results["taiwan_otc"][:5],
            "commodity_top5": results["commodity"][:5],
            "us_small_exciting_top10": results["us_small_exciting"][:10],
        },
        "cross_bucket_top_15": all_scored[:15],
        "deep_corrections_above_30pct_dist": [
            it for it in all_scored if it["dist_from_12m_high_pct"] > 30 and it["r6m_pct"] > -10
        ][:10],
    }
    out_path = out_dir / f"global-hunter-{today.date()}.json"
    out_path.write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")
    print(f"wrote {out_path}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
