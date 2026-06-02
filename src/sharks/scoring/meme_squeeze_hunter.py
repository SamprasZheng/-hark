"""Meme + Squeeze + Mean-Reversion Hunter — 妖股獵手.

Adds dimensions traditional FOM lacks:
  1. squeeze_potential — high short interest proxy via price-volume dislocation
  2. sentiment_burst — recent acceleration in returns (proxy for social pump)
  3. volume_explosion — vol multiplier vs trailing avg (institutional accumulation)
  4. deep_value_reversal — distance from multi-year low (deeper = more upside)
  5. broken_uptrend_recovery — 50%+ drawdown then green month

Anti-Buffett mode: pure upside hunting; risk is bounded by position sizing
not by quality filters.
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

# ─── Expanded universe — 300+ tickers across all 妖股 categories ───

# US small / micro / meme historical
US_MEME_HISTORICAL = {
    "GME": "GameStop", "AMC": "AMC Theatres", "BBBY": "Bed Bath",
    "BBIG": "Vinco Ventures", "ATER": "Aterian", "PROG": "Progenity",
    "SPRT": "Greenidge",
}

# US space / aerospace small
US_SPACE = {
    "RKLB": "Rocket Lab", "ASTS": "AST SpaceMobile", "ACHR": "Archer",
    "JOBY": "Joby Aviation", "LUNR": "Intuitive Machines", "PL": "Planet Labs",
    "SPCE": "Virgin Galactic", "BKSY": "BlackSky", "MNTS": "Momentus",
    "RDW": "Redwire", "VSAT": "Viasat",
}

# US AI specialty / micro
US_AI_MICRO = {
    "BBAI": "BigBear.ai", "AI": "C3.ai", "PLTR": "Palantir",
    "SOUN": "SoundHound", "GFAI": "Guardforce AI", "INOD": "Innodata",
    "VRAR": "Glimpse Group VR/AR", "AGFY": "Agrify",
    "PRSR": "Prospero", "CXAI": "CXApp",
}

# US Bitcoin miners + crypto
US_CRYPTO = {
    "RIOT": "Riot", "MARA": "Marathon", "WULF": "TeraWulf",
    "CIFR": "Cipher", "BTBT": "Bit Digital", "HUT": "Hut 8",
    "CLSK": "CleanSpark", "BITF": "Bitfarms", "GREE": "Greenidge",
    "CORZ": "Core Scientific", "IREN": "Iris Energy",
    "MSTR": "MicroStrategy", "COIN": "Coinbase",
}

# US clean energy / solar small
US_CLEAN_ENERGY = {
    "ENPH": "Enphase", "FSLR": "First Solar", "SEDG": "SolarEdge",
    "RUN": "Sunrun", "NOVA": "Sunnova", "ARRY": "Array",
    "SHLS": "Shoals", "PLUG": "Plug Power", "BLDP": "Ballard",
    "BE": "Bloom Energy", "FCEL": "FuelCell",
}

# US nuclear small
US_NUCLEAR = {
    "UEC": "Uranium Energy", "URG": "Ur-Energy", "DNN": "Denison",
    "NXE": "NexGen", "CCJ": "Cameco", "OKLO": "Oklo",
    "SMR": "NuScale", "BWXT": "BWXT", "LEU": "Centrus Energy",
    "URA": "Uranium ETF", "URNM": "Uranium Mining ETF",
}

# US biotech speculative
US_BIOTECH_SPEC = {
    "CRSP": "CRISPR", "BEAM": "Beam", "NTLA": "Intellia",
    "VERV": "Verve", "EDIT": "Editas", "PRME": "Prime Medicine",
    "VKTX": "Viking Therapeutics", "RXRX": "Recursion",
    "SDGR": "Schrodinger", "ABSI": "Absci", "RGNX": "Regenxbio",
    "RNA": "Avidity Bio", "MIRM": "Mirum",
}

# US EV / autonomous
US_EV = {
    "RIVN": "Rivian", "LCID": "Lucid", "NKLA": "Nikola",
    "WKHS": "Workhorse", "GOEV": "Canoo", "FFIE": "Faraday Future",
    "MULN": "Mullen", "BLNK": "Blink", "CHPT": "ChargePoint",
    "EVGO": "EVgo",
}

# US specialty semis small
US_SEMI_SMALL = {
    "AEHR": "AEHR Test", "AOSL": "Alpha Omega", "AXTI": "AXT",
    "POET": "POET", "ALAB": "Astera Labs", "CRDO": "Credo",
    "NVTS": "Navitas", "POWI": "Power Integrations",
    "QUIK": "QuickLogic", "ACMR": "ACM Research", "HIMX": "Himax",
    "IMOS": "ChipMOS", "MX": "MagnaChip", "AMBA": "Ambarella",
    "INDI": "indie Semi", "ALGM": "Allegro",
}

# US gaming / metaverse
US_GAMING = {
    "RBLX": "Roblox", "U": "Unity", "TTWO": "Take-Two",
    "EA": "EA", "DKNG": "DraftKings",
}

# US weight loss / GLP-1 sympathy
US_GLP1_SYMPATHY = {
    "LLY": "Eli Lilly", "NVO": "Novo Nordisk", "VKTX": "Viking",
    "AMGN": "Amgen", "AKRO": "Akero",
}

# Taiwan additional sectors
TW_TRADITIONAL = {
    # Finance
    "2882.TW": "Cathay 國泰金", "2891.TW": "CTBC 中信金", "2884.TW": "Yuanta 玉山金",
    "2880.TW": "Hua Nan 華南金", "2883.TW": "China Dev 中華開發",
    # Plastics / chemicals
    "1301.TW": "Formosa 台塑", "1303.TW": "Nan Ya 南亞", "1326.TW": "Formosa Chem 台化",
    # Steel
    "2002.TW": "China Steel 中鋼",
    # Cement
    "1101.TW": "Taiwan Cement 台泥", "1102.TW": "Asia Cement 亞泥",
    # Telecom
    "3045.TW": "Taiwan Mobile 台灣大",
    # Retail
    "2912.TW": "President 統一超",
    # Pharma
    "1762.TW": "Genelinx 中化生", "4174.TW": "Pharmoss 浩鼎",
    # Bio
    "4128.TW": "Microbio 中天",
}

# Taiwan additional small AI / supply chain
TW_SMALL_AI_SUPPLY = {
    "6182.TW": "Topsearch (PCB)",
    "3596.TW": "Smartisan 智易",
    "4977.TW": "Eltek 眾達",
    "8261.TW": "TaiTech 富鼎",
    "3105.TW": "Win Semi 穩懋(已大)",
    "5347.TW": "Vanguard 世界先進(成熟製程)",
    "3045.TW": "Taiwan Mobile",
    "6285.TW": "Khlife 啟碁",
    "4958.TW": "Cleader 臻鼎-KY (FPC 軟板)",
    "3023.TW": "Sinmag 信音",
    "8081.TW": "PixArt 原相",
    "4763.TW": "Mertek 米泰",
    # AI-specific specialty
    "6643.TWO": "M31 智原相關",
    "6147.TWO": "Lotes 大億",
    "6230.TWO": "新唐 Nuvoton",
}

# Japan ADRs (Nikkei key)
JP_ADRS = {
    "TM": "Toyota Motor", "SONY": "Sony", "NTDOY": "Nintendo",
    "HMC": "Honda", "MUFG": "Mitsubishi UFJ", "MFG": "Mizuho",
    "SMFG": "Sumitomo Mitsui",
}

# EU specialty
EU_ADRS = {
    "ASML": "ASML", "STM": "STMicro", "BUD": "AB InBev",
    "SAP": "SAP", "TM": "Toyota", "RACE": "Ferrari", "NVO": "Novo Nordisk",
    "BABA": "Alibaba (China)",
}


ALL_HUNTING = {**US_MEME_HISTORICAL, **US_SPACE, **US_AI_MICRO, **US_CRYPTO,
                **US_CLEAN_ENERGY, **US_NUCLEAR, **US_BIOTECH_SPEC, **US_EV,
                **US_SEMI_SMALL, **US_GAMING, **US_GLP1_SYMPATHY,
                **TW_TRADITIONAL, **TW_SMALL_AI_SUPPLY,
                **JP_ADRS, **EU_ADRS}


def fetch_monthly(tickers, start, end):
    raw = yf.download(tickers, start=start, end=end, interval="1mo",
                     auto_adjust=True, progress=False, group_by="ticker", threads=True)
    closes = pd.DataFrame()
    volumes = pd.DataFrame()
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
    if closes.index.tz is not None:
        closes.index = closes.index.tz_localize(None)
        volumes.index = volumes.index.tz_localize(None)
    return closes.sort_index(), volumes.sort_index()


def squeeze_signal(closes, volumes, ticker, as_of):
    s = closes.get(ticker)
    v = volumes.get(ticker)
    if s is None or s.dropna().empty:
        return None
    s = s.dropna()
    pre = s.loc[:as_of]
    if len(pre) < 18:
        return None
    last = float(pre.iloc[-1])
    # 12m high / low
    window = pre.iloc[-13:]
    high = float(window.max())
    low = float(window.min())
    # Recent month return
    r1 = float(pre.iloc[-1] / pre.iloc[-2] - 1) if len(pre) > 1 else 0.0
    r3 = float(pre.iloc[-1] / pre.iloc[-4] - 1) if len(pre) > 3 else 0.0
    r6 = float(pre.iloc[-1] / pre.iloc[-7] - 1) if len(pre) > 6 else 0.0
    r12 = float(pre.iloc[-1] / pre.iloc[-13] - 1) if len(pre) > 12 else 0.0
    # Volume burst (if data avail)
    vol_burst = 0
    if v is not None and not v.dropna().empty:
        v_clean = v.dropna()
        v_pre = v_clean.loc[:as_of]
        if len(v_pre) > 6:
            recent_vol = float(v_pre.iloc[-1])
            avg_vol = float(v_pre.iloc[-7:-1].mean())
            if avg_vol > 0:
                vol_burst = recent_vol / avg_vol
    # Distance from 12m high / low
    dist_high = (high - last) / high if high > 0 else 0
    dist_low = (last - low) / low if low > 0 else 0
    # Realised vol
    lr = np.log(pre.iloc[-13:] / pre.iloc[-13:].shift(1)).dropna()
    rvol = float(lr.std() * math.sqrt(12)) if len(lr) > 1 else 0.3

    # SQUEEZE: deeply down (dist_high > 50%) but recent month +20%+
    is_squeezing = dist_high > 0.5 and r1 > 0.20
    # MEAN REVERSION: dist_high > 30% AND r3 starting to turn positive
    is_reverting = dist_high > 0.30 and -0.05 < r3 < 0.20 and r1 > 0.05
    # PARABOLIC PUMP: r3 > 100% AND vol_burst > 1.5
    is_pumping = r3 > 1.0 and vol_burst > 1.5
    # DEEP VALUE: dist_low < 50% (near 12m low) AND rvol > 0.5
    is_deep_value = dist_low < 0.50 and rvol > 0.5
    # BROKEN UPTREND RECOVERY: r12 > 0% but dist_high > 30% (rebound from correction)
    is_recovering = r12 > 0 and dist_high > 0.30 and r1 > 0

    # Score
    score = 0
    flags = []
    if is_squeezing:
        score += 40
        flags.append("SQUEEZE_CANDIDATE")
    if is_reverting:
        score += 30
        flags.append("MEAN_REVERSION")
    if is_pumping:
        score += 25
        flags.append("PUMP_IN_PROGRESS")
    if is_deep_value:
        score += 35
        flags.append("DEEP_VALUE_NEAR_LOW")
    if is_recovering:
        score += 25
        flags.append("BROKEN_UPTREND_RECOVERY")
    if vol_burst > 2.5:
        score += 15
        flags.append("VOLUME_BURST")
    if rvol > 0.8:
        score += 10
        flags.append("HIGH_VOLATILITY")

    return {
        "ticker": ticker,
        "last_price": round(last, 2),
        "r1m_pct": round(r1 * 100, 1),
        "r3m_pct": round(r3 * 100, 1),
        "r6m_pct": round(r6 * 100, 1),
        "r12m_pct": round(r12 * 100, 1),
        "dist_from_12m_high_pct": round(dist_high * 100, 1),
        "dist_from_12m_low_pct": round(dist_low * 100, 1),
        "rvol_annual_pct": round(rvol * 100, 1),
        "volume_burst_ratio": round(vol_burst, 2),
        "squeeze_score": min(100, score),
        "flags": flags,
    }


def main():
    out_dir = Path("outputs")
    today = pd.Timestamp("2026-05-30")
    print(f"Meme/Squeeze Hunter as of {today.date()}, {len(ALL_HUNTING)} tickers", file=sys.stderr)
    closes, volumes = fetch_monthly(list(ALL_HUNTING.keys()), "2022-01-01", "2026-05-30")
    print(f"  data: {len(closes.columns)} tickers", file=sys.stderr)

    results = []
    for t, name in ALL_HUNTING.items():
        sig = squeeze_signal(closes, volumes, t, today)
        if sig:
            sig["name"] = name
            results.append(sig)

    results.sort(key=lambda x: x["squeeze_score"], reverse=True)

    # Categorize
    by_flag = {"SQUEEZE_CANDIDATE": [], "MEAN_REVERSION": [], "DEEP_VALUE_NEAR_LOW": [],
                "BROKEN_UPTREND_RECOVERY": [], "PUMP_IN_PROGRESS": []}
    for r in results:
        for f in r["flags"]:
            if f in by_flag:
                by_flag[f].append(r["ticker"])

    report = {
        "as_of": datetime.now(timezone.utc).isoformat(),
        "schema_version": 1,
        "methodology": "Squeeze + Mean-Reversion + Pump + Deep-Value + Recovery scoring",
        "tickers_scored": len(results),
        "top_25_by_score": results[:25],
        "deep_value_near_low_top10": [r for r in results if "DEEP_VALUE_NEAR_LOW" in r["flags"]][:10],
        "mean_reversion_candidates_top10": [r for r in results if "MEAN_REVERSION" in r["flags"]][:10],
        "squeeze_candidates_top10": [r for r in results if "SQUEEZE_CANDIDATE" in r["flags"]][:10],
        "broken_uptrend_recovery_top10": [r for r in results if "BROKEN_UPTREND_RECOVERY" in r["flags"]][:10],
        "by_flag_counts": {k: len(v) for k, v in by_flag.items()},
    }
    out_path = out_dir / f"meme-squeeze-hunter-{today.date()}.json"
    out_path.write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")
    print(f"wrote {out_path}", file=sys.stderr)
    print(f"  top score: {results[0]['ticker']} = {results[0]['squeeze_score']}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
