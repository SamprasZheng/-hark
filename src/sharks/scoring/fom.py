"""Figure of Merit (FOM) — multi-dimensional ticker scoring.

Five dimensions blended into a single 0-100 FOM score per ticker per as_of:

  1. momentum    — 順勢 / AI cycle alignment, 1-3-12m return, supply-chain depth
  2. contrarian  — 逆勢 / mispricing, distance from 52w high (positive = correction)
  3. cyclic      — 週期 / from cycle_bias module, scaled to 0-100
  4. quality     — alpha+beta blend, realised vol (lower=quality), liquidity
  5. bubble_guard — -100 to +100, negative = late-cycle bubble stress

Persistence boost: tickers appearing in N consecutive weekly outputs get +5%
per week capped at +30%, weighted into final FOM.

Output: ranked list with full breakdown for human review.
"""

from __future__ import annotations

import json
import math
import sys
import warnings
from dataclasses import dataclass, asdict, field
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Optional

warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)

import numpy as np
import pandas as pd
import yfinance as yf

from .cycle_bias import combined_cycle_bias, TICKER_SECTOR
from ..regime.classifier import classify_regime, REGIME_PROFILES

# ─── Universe definitions (expanded with R2K + new names) ───

INDICES = ["^GSPC", "^NDX", "^SOX", "^VIX", "^RUT"]

MAG7 = ["NVDA", "AAPL", "MSFT", "GOOGL", "META", "AMZN", "TSLA"]

SUPPLY_TIER2 = ["TSM", "ASML", "AVGO", "AMD", "ARM", "MU", "AMAT", "LRCX", "INTC"]

# Memory (Phase 1 per Serenity)
MEMORY = ["MU", "WDC", "STX", "SIMO"]

# Optical (Phase 2)
OPTICAL = ["LITE", "COHR", "CIEN", "ANET", "AAOI", "FN"]

# SiPh / external light sources (Phase 3)
SIPH = ["AXTI", "ALAB", "CRDO", "AEHR", "POET"]

# Power semis (Serenity-XFAB inspired)
POWER_SEMI = ["NVTS", "POWI", "WOLF", "ON", "MPWR"]

# Contrarian software (principal-named: AI cannot replace IP)
CONTRARIAN_SW = ["CRM", "NOW", "NFLX"]

# Bubble-stress watchlist (principal-named: ORCL, OKLO, SMCI started falling)
BUBBLE_WATCH = ["ORCL", "OKLO", "SMCI", "ARM", "AVGO"]

# Datacenter infrastructure (Phase 4 hypothesis from prior session)
DC_INFRA = ["VRT", "ETN", "GEV", "ASMI", "KLAC"]

# Materials / packaging
MATERIALS = ["GLW", "AMKR", "TER"]

# Defense (Trump-policy hedge)
DEFENSE = ["LMT", "RTX", "NOC"]

# Beta anchors (boring large caps for portfolio stability)
BETA_ANCHORS = ["JNJ", "PG", "KO", "WMT"]

# R2K alpha candidates (small-cap AI-supply-chain or other secular)
R2K_AI = ["RKLB", "ACHR", "CRSP"]

# Russell 2000 ETF for broad small-cap exposure
SECTOR_ETFS = ["IWM", "XLK", "XLY", "XLI", "XLB", "XLF", "XLV", "XLU", "XLE", "XHB", "XBI", "XLRE", "XLC", "XLP"]

# Crypto co-asset
CRYPTO = ["BTC-USD", "ETH-USD"]

# ─── Fix D additions (2026-05-30): expand universe to cover principal's
# actual holdings, historical 飆股 missed by prior universe, and 2026
# thesis names from wiki/14 + wiki/16. Audit was previously blind to ~92%
# of the principal's 2026-05-29 fills and to MSTR/QBTS/IONQ/PLTR/COIN/HOOD
# which historically were飆股 candidates.

# Server / PC OEMs in AI cycle (DELL = AI server hardware; HPE = enterprise
# AI infra; HPQ = PC + peripherals via Poly).
HARDWARE_OEM = ["DELL", "HPE", "HPQ"]

# Narrative + retail squeeze pool — high vol, often cycle out of phase with
# fundamental scorers. Includes Bitcoin proxy MSTR, crypto rails COIN/HOOD,
# enterprise AI software story PLTR, ad-tech AppLovin APP, used-car CVNA.
SPECULATIVE_NARRATIVE = ["MSTR", "COIN", "HOOD", "PLTR", "APP", "CVNA"]

# Quantum computing pure plays (RGTI already proxied via BUBBLE_WATCH-adjacent
# instruments; add the underlyings + IONQ + QBTS).
QUANTUM = ["QBTS", "IONQ", "RGTI"]

# 2026-05-29 watchlist basket (P2 / (speculative sleeve) + P1 buys not in any other
# group). LPL/HPQ already covered by HARDWARE_OEM/MATERIALS; remaining new
# tickers below. CRWV = CoreWeave neocloud.
THEMATIC_2026_BUYS = ["RIVN", "NTLA", "UEC", "BLDP", "AOSL", "LPL", "TBCH", "CRWV", "ALGM"]

# Wiki/16 §3 forward themes (uranium / biotech / gold / energy) — names not
# already in other groups. Mirrors principal's identified 2026 thesis themes.
WIKI_16_THEMES = ["DNN", "CCJ", "BEAM", "NEM", "VAL", "AESI", "GLD"]

# Serenity (@aleabitoreddit) supply-chain bottleneck names — US-listed subset
# only. The bulk of the CPO / SiPh chain is already covered by OPTICAL + SIPH
# groups above (those were themselves Serenity-XFAB inspired). These are the
# remaining US names from watchlist/serenity-supply-chain.yaml +
# philosophy/concepts/serenity-supply-chain-bottleneck.md. Non-US bottleneck
# pure plays (Taiwan/Japan/Korea/China small caps) await Phase 2 suffix support.
SERENITY_SUPPLY_CHAIN = ["TSEM", "MRVL", "VPG", "VSH"]

# ── 2026-05-30 expansion (user heatmap + theme directives) ──────────────────
# Space / SpaceX-IPO theme — sub-segmented along the value chain (2026-06-08).
# Most are 2021-SPAC survivors crushed in 2022 → 錯殺大底 profile; the SpaceX IPO
# is the narrative catalyst that can re-rate them. Double-edged: Starlink competes
# with the satcom names, so 持續性 needs real contracts/revenue, not just hype.
SPACE_LAUNCH = ["RKLB"]                          # 發射(SpaceX 最純的對標)
SPACE_SATCOM = ["ASTS", "IRDM", "GSAT", "VSAT"]  # 衛星通訊 / direct-to-cell(Starlink 對標)
SPACE_IMAGERY = ["PL", "BKSY", "SPIR"]           # 對地觀測 / 數據
SPACE_INFRA = ["RDW", "LUNR"]                     # 製造 / 月球 / 政府合約
SPACE = sorted(set(SPACE_LAUNCH + SPACE_SATCOM + SPACE_IMAGERY + SPACE_INFRA))

# Agentic-AI software pure plays (distinct from the infra names already covered).
AGENTIC_AI = ["AI", "BBAI", "SOUN", "PLTR"]

# Computex N1x laptop launch cohort (US-listed). MSFT/NVDA/ARM/DELL/AAPL already
# in other groups; QCOM (Snapdragon X) is the missing AI-PC SoC name. MediaTek
# (2454.TW) + Lenovo (0992.HK) await Phase 2 suffix support.
COMPUTEX_LAPTOP = ["QCOM"]

# Granular semis visible in the user's Finviz heatmap — timing/connectivity/
# analog names not yet in the coarser groups.
SEMI_GRANULAR = ["SITM", "RMBS", "MXL", "SLAB", "SMTC", "SYNA"]

# ── 2026-05-31 tech/ DD integration ─────────────────────────────────────────
# The US-listed investable-node basket from tech/cross-validation-quant.md §3, so
# the "live FOM scan" that page asks for can actually run (DD verdict × FOM ×
# bubble_guard split). Names already covered elsewhere (MSFT/CRM/NOW/META/NFLX/
# ARM/AVGO/COHR/LITE/AXTI/FN/QCOM/IONQ/QBTS/RGTI/PLTR) are deduped by set().
# Non-US nodes (SK Hynix/Samsung/TSMC/Sumitomo/Bachem/Ypsomed…) await Phase-2
# ticker-suffix support and are NOT added here.
TECH_DD_NODES = [
    "INTU", "ADBE",          # ai-eats-software captors (thick SaaS)
    "LLY", "NVO",            # GLP-1 realized-cashflow 質變 (the one near-質變)
    "UBER", "DASH", "SPOT",  # youth-culture platforms (real P&L)
    "HSAI", "MBLY",          # autonomous-driving sensing/ADAS
    "RXRX", "SDGR",          # AI-drug-discovery (太早→結構 option)
]

# ── 2026-06-08: "Intel 領漲 → 補炒 2022 殺下來 + AI 錯殺軟體股" 輪動論點 ──────────
# Multi-year-base names (Boeing/Snowflake 形態) the principal wants in the FOM
# universe so /basecross gets a 盈利(quality) dimension and the 起漲 tracker can
# fuse fundamentals. Mirrors KILLED_2022 + AI_OVERSOLD_SOFTWARE in
# src/sharks/discord/basecross.py + watchlist/thesis_basecross.yaml. Names already
# covered above (CRM/NOW/NFLX/INTU/ADBE/INTC/MU/AI/PLTR/RIVN…) dedupe via set().
ROTATION_2022_AI = [
    "BA", "SNOW", "PYPL", "NKE", "DIS", "ROKU", "TWLO", "DDOG", "NET", "OKTA",
    "ZS", "MDB", "SHOP", "U", "PATH", "RBLX", "PINS", "SE", "ABNB", "DOCU",
    "WDAY", "TEAM", "BILL", "CFLT", "GTLB", "ESTC", "DOCN", "HUBS", "ZI", "S",
    "BRZE", "CHGG",
]

# ── 2026-06-08: 電商 / agentic-commerce 題材 ─────────────────────────────────────
# AI 代理(自動比價/下單,如 agentic checkout)利好「agent-readable」的電商平台 +
# 金流/物流基建。富邦媒(8454.TW)Momo 大漲是端倪;台股(8454/8044.TW)需 Phase-2
# suffix,放 watchlist/thesis_ecommerce_agentic.md。這裡為 US/ADR(AMZN/SHOP/SE 已在
# 別群,set() 去重)。注意:agentic 比價是**雙面刃**——基建/規模平台受惠,subscale
# 純比價平台反而被商品化,所以仍靠 FOM quality(盈利)維度過濾。
ECOMMERCE_AGENTIC = [
    "MELI", "BABA", "PDD", "CPNG", "ETSY", "EBAY", "W", "CHWY", "GLBE", "BIGC", "JD",
    # 小型 / 長尾(主理人點名 Jumia/Wayfair/Etsy + 同型小型電商)— 高賠率高風險,
    # 仍靠盈利(quality)維度過濾。mirrored in discord/basecross.ECOMMERCE_SMALL.
    "JMIA", "RVLV", "VIPS", "REAL", "SFIX", "WRBY", "MYTE", "CART", "FIGS", "RENT",
]

# ── 2026-06-08: 廣度輪動 / 錯殺非-AI 民生消費醫療(broadening 論點)─────────────
# 若行情擴散,華爾街輪動到落後的民生/消費/醫療。納入宇宙讓 /stealth(隱蔽吸籌:
# 資金先進、價未動)能在這些「大家還沒看到」的票上找指紋。mirrored in
# discord/basecross.BROADENING_LAGGARDS.
BROADENING_LAGGARDS = [
    "KHC", "CAG", "CL", "HSY", "GIS", "K", "KVUE", "CLX", "SJM", "BG",
    "NKE", "SBUX", "LULU", "EL", "TGT", "DG", "DLTR", "FIVE", "MCD",
    "PFE", "MRNA", "BMY", "CVS", "HUM", "GILD", "DXCM",
]

# 跨產業分散轉機股(非-科技為主)— 補進宇宙讓 /basecross diversified 有盈利維度。
# mirrored in discord/basecross.DIVERSIFIED_TURNAROUND. 多數已在他群,新增的:
# ALB(鋰/材料)、MMM(工業)、F(汽車)、WBD(媒體)、PYPL(金融)。
DIVERSIFIED_TURNAROUND = ["ALB", "MMM", "F", "WBD", "PYPL", "DIS"]

# 更多中風險轉機股(週期/公司轉機,有真營收)— mirrored in
# discord/basecross.MID_RISK_TURNAROUND. 金融/生技/醫材/農機/化工/銅/通訊/車/油服。
MID_RISK_TURNAROUND = ["C", "BIIB", "MDT", "DE", "LYB", "FCX",
                       "CMCSA", "APTV", "GM", "SLB", "DPZ", "GPC"]

# 2026 IPO 超級年的上市代理/受惠者 — mirrored in discord/basecross.IPO_PROXIES.
# 新增的(其餘已在他群):FI/GPN/XYZ(金流)、SOFI/NU(neobank)。
IPO_PROXIES = ["FI", "GPN", "XYZ", "SOFI", "NU"]

# ── Master universe assembly ───────────────────────────────────────────────
DEFAULT_UNIVERSE = sorted(set(
    MAG7 + SUPPLY_TIER2 + MEMORY + OPTICAL + SIPH + POWER_SEMI +
    CONTRARIAN_SW + BUBBLE_WATCH + DC_INFRA + MATERIALS + DEFENSE +
    BETA_ANCHORS + R2K_AI +
    HARDWARE_OEM + SPECULATIVE_NARRATIVE + QUANTUM +
    THEMATIC_2026_BUYS + WIKI_16_THEMES + SERENITY_SUPPLY_CHAIN +
    SPACE + AGENTIC_AI + COMPUTEX_LAPTOP + SEMI_GRANULAR + TECH_DD_NODES +
    ROTATION_2022_AI + ECOMMERCE_AGENTIC + BROADENING_LAGGARDS +
    DIVERSIFIED_TURNAROUND + MID_RISK_TURNAROUND + IPO_PROXIES
))

# ─── IP defensibility (qualitative Compiler input) ───
# Ranked 0-100 for AI-substitution resistance / IP moat strength
IP_DEFENSIBILITY = {
    # Strong IP moat — recurring revenue, switching cost, customer data
    "MSFT": 95, "GOOGL": 90, "META": 85, "AAPL": 90,
    "NFLX": 80, "CRM": 88, "NOW": 90,
    # Strong industrial moats
    "TSM": 95, "ASML": 98, "NVDA": 92, "AVGO": 85,
    # Defensible but not differentiated
    "AMD": 70, "AMAT": 78, "LRCX": 78, "KLAC": 80, "ASMI": 75,
    # Modest IP — commodity-ish but switching-cost
    "MU": 60, "WDC": 55, "STX": 55,
    # Optical primes (Phase 2 — supply chain depth but commodity-prone)
    "LITE": 60, "COHR": 65, "CIEN": 65, "ANET": 80, "AAOI": 55, "FN": 55,
    # Phase 3 specialty
    "AXTI": 70, "ALAB": 75, "CRDO": 70, "AEHR": 65, "POET": 50,
    # Power semi
    "NVTS": 55, "POWI": 70, "WOLF": 60, "ON": 65, "MPWR": 75,
    # Bubble watch — weak IP / high narrative
    "ORCL": 75, "OKLO": 30, "SMCI": 40,
    # ARM ambiguous — strong IP but valuation rich
    "ARM": 85,
    # DC infrastructure — strong moats in their niches
    "VRT": 75, "ETN": 80, "GEV": 70,
    # Materials
    "GLW": 80, "AMKR": 55, "TER": 75,
    # Defense
    "LMT": 90, "RTX": 88, "NOC": 88,
    # Beta anchors — classic moats
    "JNJ": 90, "PG": 85, "KO": 88, "WMT": 80,
    # Misc
    "TSLA": 70, "AMZN": 88, "INTC": 60,
    "RKLB": 60, "ACHR": 35, "CRSP": 55,
    # ── Fix D (2026-05-30) additions ──
    # Hardware OEMs — operating moats but commodity-prone
    "DELL": 55, "HPE": 55, "HPQ": 50,
    # Speculative narrative bucket — moat varies widely
    "MSTR": 20,  # Bitcoin levered proxy, no operating IP
    "COIN": 70,  # crypto exchange, regulated scale moat
    "HOOD": 55,  # retail broker, scale moat
    "PLTR": 80,  # enterprise Foundry stickiness
    "APP":  70,  # AppLovin ad tech + game studios
    "CVNA": 25,  # used-car retail, no IP
    # Quantum pure plays — narrative > IP for now
    "QBTS": 20, "IONQ": 25, "RGTI": 20,
    # 2026-05-29 buys
    "RIVN": 35,  # EV + Amazon contract; scale uncertain
    "NTLA": 55,  # CRISPR gene editing
    "UEC":  35,  # uranium miner
    "BLDP": 25,  # hydrogen fuel cell — narrative-heavy
    "AOSL": 55,  # auto/industrial power semi
    "LPL":  35,  # LG Display panels — commodity-ish
    "TBCH": 45,  # gaming headset brand
    "CRWV": 65,  # CoreWeave neocloud
    "ALGM": 65,  # Allegro Micro auto power
    # Wiki 16 themes
    "DNN":  35, "CCJ": 50, "BEAM": 55, "NEM": 60,
    "VAL":  30, "AESI": 35, "GLD": 75,
    # Serenity supply-chain (US-listed subset)
    "TSEM": 72,  # Tower Semi — specialty/SiPh foundry ("photonics TSMC")
    "MRVL": 80,  # Marvell — custom silicon + optical DSP
    "VPG":  60,  # Vishay Precision Group — foil sensors niche
    "VSH":  50,  # Vishay — commodity passives
    # 2026-05-30 expansion — space
    "LUNR": 40,  # Intuitive Machines — lunar lander, gov-contract revenue
    "RDW":  40,  # Redwire — space infra components
    "ASTS": 45,  # AST SpaceMobile — direct-to-cell, high-narrative
    "PL":   45,  # Planet Labs — earth-observation data recurring
    "RKLB": 60,  # Rocket Lab — launch + space systems, the space pure-play leader
    # agentic AI
    "AI":   45,  # C3.ai — enterprise AI apps, narrative-heavy
    "BBAI": 30,  # BigBear.ai — small, gov AI, low moat
    "SOUN": 35,  # SoundHound — voice AI, high-narrative
    "PLTR": 80,  # Palantir — sticky gov+commercial data platform, strong moat
    # Computex AI-PC SoC
    "QCOM": 75,  # Qualcomm — Snapdragon X AI-PC SoC + mobile modem moat
    # granular semis
    "SITM": 70,  # SiTime — MEMS timing, niche leader
    "RMBS": 65,  # Rambus — memory interface IP
    "MXL":  55,  # MaxLinear — broadband/connectivity analog
    "SLAB": 65,  # Silicon Labs — IoT/wireless MCUs
    "SMTC": 60,  # Semtech — LoRa + signal integrity
    "SYNA": 55,  # Synaptics — edge-AI human interface (Serenity-flagged)
    # tech/ DD nodes (2026-05-31)
    "INTU": 78,  # Intuit — entrenched SMB/tax workflow, AI-captor not -victim
    "ADBE": 70,  # Adobe — creative moat, GenAI both threat and tool
    "LLY":  82,  # Eli Lilly — GLP-1 manufacturing + patent moat (近質變現金流)
    "NVO":  78,  # Novo Nordisk — GLP-1 duopoly; orals/去中介 risk noted
    "UBER": 68,  # Uber — two-sided network, real FCF; AV is the swing factor
    "DASH": 62,  # DoorDash — delivery network density; thin margins
    "SPOT": 58,  # Spotify — scale + podcasts; label-pricing dependency
    "HSAI": 45,  # Hesai — LiDAR volume leader but commoditising sensor
    "MBLY": 50,  # Mobileye — ADAS incumbent; vision-vs-hybrid contested
    "RXRX": 35,  # Recursion — AI-drug platform, 太早, optionality not cashflow
    "SDGR": 38,  # Schrodinger — physics-based drug sim; long-dated option
}

# ─── Data pull ───
def fetch_monthly(tickers: list[str], start: str, end: str) -> pd.DataFrame:
    """Pull monthly close series."""
    raw = yf.download(
        tickers=tickers, start=start, end=end, interval="1mo",
        auto_adjust=True, progress=False, group_by="ticker", threads=True,
    )
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


# ─── Per-dimension scorers ───
def momentum_score(closes: pd.DataFrame, ticker: str, as_of: pd.Timestamp) -> float:
    """0-100, blends 1m + 3m + 12m return percentiles vs universe."""
    s = closes.get(ticker)
    if s is None or s.dropna().empty:
        return 50.0  # neutral if missing
    s = s.dropna()
    pre = s.loc[:as_of]
    if len(pre) < 3:
        return 50.0
    last = pre.iloc[-1]
    # Returns
    rets = {}
    for n_months, weight in [(1, 0.20), (3, 0.30), (12, 0.50)]:
        if len(pre) > n_months:
            r = float(last / pre.iloc[-(n_months + 1)] - 1)
        else:
            r = 0.0
        rets[n_months] = (r, weight)
    # Convert each return to a score: -50%→0, 0%→50, +100%→100, clipped
    score = 0.0
    for n, (r, w) in rets.items():
        clipped = max(-0.5, min(2.0, r))  # cap at +200%
        normalized = (clipped + 0.5) / 2.5 * 100  # -50%→0, +200%→100
        score += w * normalized
    return float(max(0, min(100, score)))


def contrarian_score(closes: pd.DataFrame, ticker: str, as_of: pd.Timestamp) -> float:
    """0-100, higher = bigger 'mispricing' opportunity.
    Inputs: distance from 52w high + IP defensibility + magnitude of correction.
    """
    s = closes.get(ticker)
    if s is None or s.dropna().empty:
        return 50.0
    s = s.dropna()
    last = s.loc[:as_of].iloc[-1] if not s.loc[:as_of].empty else None
    if last is None:
        return 50.0
    window = s.loc[as_of - pd.Timedelta(days=365):as_of]
    if window.empty:
        return 50.0
    high = window.max()
    dist_from_high = float((high - last) / high) if high > 0 else 0.0
    # Contrarian sweet spot: 10-40% below 52w high (real correction, not crash)
    if dist_from_high < 0.05:
        dist_score = 20  # too close to high, no opportunity
    elif dist_from_high < 0.15:
        dist_score = 50
    elif dist_from_high < 0.30:
        dist_score = 85  # sweet spot
    elif dist_from_high < 0.50:
        dist_score = 70
    else:
        dist_score = 40  # might be crash, not correction
    # IP defensibility modulates the score
    ip = IP_DEFENSIBILITY.get(ticker, 50)
    # Final: weighted blend (dist contributes 60%, IP 40%)
    score = 0.6 * dist_score + 0.4 * ip
    return float(max(0, min(100, score)))


def cyclic_score(ticker: str, as_of: pd.Timestamp) -> tuple[float, dict]:
    """0-100 from cycle_bias, with breakdown."""
    res = combined_cycle_bias(as_of.date(), ticker)
    # Convert [-1, +1] → [0, 100]
    score = (res.combined + 1.0) / 2.0 * 100
    return float(max(0, min(100, score))), asdict(res)


def quality_score(closes: pd.DataFrame, ticker: str, as_of: pd.Timestamp) -> float:
    """0-100, alpha+beta blend: low vol = quality; positive 36m return = alpha."""
    s = closes.get(ticker)
    if s is None or s.dropna().empty:
        return 50.0
    s = s.dropna()
    pre = s.loc[:as_of]
    if len(pre) < 12:
        return 50.0
    # 36m total return
    if len(pre) > 36:
        r36 = float(pre.iloc[-1] / pre.iloc[-37] - 1)
    else:
        r36 = float(pre.iloc[-1] / pre.iloc[0] - 1)
    # 24m realised vol (monthly log returns)
    lr = np.log(pre.iloc[-25:] / pre.iloc[-25:].shift(1)).dropna()
    rvol_ann = float(lr.std() * math.sqrt(12)) if len(lr) > 1 else 0.5
    # Score: low vol better, positive return better
    vol_score = max(0, 100 - rvol_ann * 100)  # 0% vol→100, 100% vol→0
    return_score = max(0, min(100, (r36 + 0.5) / 2.5 * 100))  # -50%→0, +200%→100
    score = 0.4 * vol_score + 0.6 * return_score
    return float(max(0, min(100, score)))


def bubble_guard(closes: pd.DataFrame, ticker: str, as_of: pd.Timestamp) -> float:
    """-100 to +100. Negative = bubble stress, positive = healthy.
    Inputs:
      - momentum >> long-term avg → bubble risk
      - parabolic 6m pattern → bubble risk
      - distance from 52w high < 5% + high vol → late stage
      - solid IP + reasonable valuation → positive
    """
    s = closes.get(ticker)
    if s is None or s.dropna().empty:
        return 0.0
    s = s.dropna()
    pre = s.loc[:as_of]
    if len(pre) < 12:
        return 0.0
    last = pre.iloc[-1]
    # 6m return
    if len(pre) > 6:
        r6 = float(last / pre.iloc[-7] - 1)
    else:
        r6 = 0.0
    # 12m return
    r12 = float(last / pre.iloc[-13] - 1) if len(pre) > 12 else 0.0
    # 36m avg monthly return as baseline
    if len(pre) > 36:
        baseline = float(pre.iloc[-37:].pct_change().mean() * 12)
    else:
        baseline = 0.10
    # Distance from 52w high
    window = s.loc[as_of - pd.Timedelta(days=365):as_of]
    high = window.max() if not window.empty else last
    dist = float((high - last) / high) if high > 0 else 0.0
    score = 0.0
    # Parabolic warning
    if r6 > 2.0:  # +200% in 6 months
        score -= 50
    elif r6 > 1.0:
        score -= 25
    elif r6 > 0.5:
        score -= 10
    # Overextension warning
    if r12 > baseline * 5 and r12 > 1.5:
        score -= 30
    # At-the-top warning
    if dist < 0.03 and r12 > 1.0:
        score -= 15
    # Healthy correction (recovery candidate)
    if 0.15 < dist < 0.35 and r12 > -0.1:
        score += 30
    # Solid trend with breath
    if 0.0 < r6 < 0.3 and 0.05 < dist < 0.20:
        score += 20
    # IP defensibility bonus
    ip = IP_DEFENSIBILITY.get(ticker, 50)
    if ip >= 85:
        score += 15
    elif ip <= 40:
        score -= 15
    return float(max(-100, min(100, score)))


# ─── FOM aggregation ───
# Default weights when no regime override is supplied. Matches the canonical
# 25/25/15/15/20 from the original FOM doc-string. The regime classifier
# (regime/classifier.py) supplies alternative weights when applied.
_DEFAULT_WEIGHTS = REGIME_PROFILES["neutral"]["weights"]
_DEFAULT_BUB_FLOOR = REGIME_PROFILES["neutral"]["bubble_guard_floor"]

# ─── Fix B (2026-05-30): multi-horizon weight profiles ───
# A regime-INDEPENDENT lens that re-weights the same five dimension scores under
# short / medium / long emphasis, so a name carries three side-by-side FOMs:
#   - 3m  (短打 / breakout): momentum-heavy, bubble_guard floored at -50 so a
#          strong-momentum extension is not drowned (same insight as late_bull).
#   - 12m (balanced): identical to the canonical neutral weights.
#   - 36m (長壓 / value-mean-revert): contrarian + quality heavy, full bubble
#          penalty (no floor) because long-horizon entries care about extension.
# Each weights table sums to 1.0 (asserted at module load below).
HORIZON_PROFILES: dict[str, dict] = {
    "3m": {
        "weights": {"momentum": 0.55, "contrarian": 0.05, "cyclic": 0.15,
                    "quality": 0.05, "bubble_guard": 0.20},
        "bubble_guard_floor": -50,
    },
    "12m": {
        "weights": {"momentum": 0.25, "contrarian": 0.25, "cyclic": 0.15,
                    "quality": 0.15, "bubble_guard": 0.20},
        "bubble_guard_floor": -100,
    },
    "36m": {
        "weights": {"momentum": 0.15, "contrarian": 0.30, "cyclic": 0.10,
                    "quality": 0.30, "bubble_guard": 0.15},
        "bubble_guard_floor": -100,
    },
}

for _h, _prof in HORIZON_PROFILES.items():
    _t = round(sum(_prof["weights"].values()), 6)
    if _t != 1.0:
        raise ValueError(f"HORIZON_PROFILES[{_h!r}] weights sum to {_t}, not 1.0")


@dataclass
class FOMScore:
    ticker: str
    as_of: str
    sector_etf: Optional[str]
    momentum: float
    contrarian: float
    cyclic: float
    quality: float
    bubble_guard_val: float
    persistence_weeks: int = 0
    cyclic_breakdown: dict = field(default_factory=dict)
    ip_defensibility: int = 50
    # Regime-aware scoring (defaults reproduce canonical FOM behaviour).
    regime_label: str = "neutral"
    weights: dict = field(default_factory=lambda: dict(_DEFAULT_WEIGHTS))
    bubble_guard_floor: int = _DEFAULT_BUB_FLOOR

    @property
    def bubble_guard_clamped(self) -> float:
        """Bubble guard reading after regime-supplied floor is applied."""
        return float(max(self.bubble_guard_val, self.bubble_guard_floor))

    def _weighted_base(self, weights: dict, bub_floor: float) -> float:
        """Blend the five dimension scores under an arbitrary weights table +
        bubble_guard floor. Shared by the regime-gated base_score and the
        multi-horizon lens so they can never drift apart."""
        bub = max(self.bubble_guard_val, bub_floor)
        return (
            weights["momentum"] * self.momentum
            + weights["contrarian"] * self.contrarian
            + weights["cyclic"] * self.cyclic
            + weights["quality"] * self.quality
            # normalise the floored bubble_guard from [-100, +100] to [0, 100]
            + weights["bubble_guard"] * ((bub + 100) / 2)
        )

    @property
    def base_score(self) -> float:
        return self._weighted_base(self.weights, self.bubble_guard_floor)

    @property
    def persistence_boost(self) -> float:
        return min(self.persistence_weeks * 0.05, 0.30)

    @property
    def final_fom(self) -> float:
        return float(self.base_score * (1.0 + self.persistence_boost))

    @property
    def horizon_scores(self) -> dict[str, float]:
        """Regime-independent multi-horizon lens (Fix B). Returns fom_3m / fom_12m
        / fom_36m computed from the same dimension scores under the short /
        medium / long weight profiles, each carrying the persistence boost so the
        numbers are comparable to final_fom. This is an analytical breakdown for
        '短打 vs 長壓' signal separation, NOT a replacement for the regime-gated
        final_fom (which remains the primary single number)."""
        boost = 1.0 + self.persistence_boost
        return {
            f"fom_{h}": round(
                self._weighted_base(prof["weights"], prof["bubble_guard_floor"]) * boost, 2
            )
            for h, prof in HORIZON_PROFILES.items()
        }


def score_ticker(
    closes: pd.DataFrame,
    ticker: str,
    as_of: pd.Timestamp,
    persistence_weeks: int = 0,
    regime: Optional[dict] = None,
) -> FOMScore:
    """Score a single ticker. If ``regime`` is supplied, its weights and
    bubble_guard floor are stamped onto the FOMScore; otherwise the canonical
    neutral weights apply (backward compatible with pre-regime callers)."""
    mom = momentum_score(closes, ticker, as_of)
    con = contrarian_score(closes, ticker, as_of)
    cyc, cyc_breakdown = cyclic_score(ticker, as_of)
    qual = quality_score(closes, ticker, as_of)
    bub = bubble_guard(closes, ticker, as_of)
    ip = IP_DEFENSIBILITY.get(ticker, 50)

    if regime is None:
        regime_label = "neutral"
        weights = dict(_DEFAULT_WEIGHTS)
        bub_floor = _DEFAULT_BUB_FLOOR
    else:
        regime_label = regime["label"]
        weights = dict(regime["weights"])
        bub_floor = int(regime["bubble_guard_floor"])

    return FOMScore(
        ticker=ticker,
        as_of=as_of.isoformat()[:10],
        sector_etf=TICKER_SECTOR.get(ticker),
        momentum=mom,
        contrarian=con,
        cyclic=cyc,
        quality=qual,
        bubble_guard_val=bub,
        persistence_weeks=persistence_weeks,
        cyclic_breakdown=cyc_breakdown,
        ip_defensibility=ip,
        regime_label=regime_label,
        weights=weights,
        bubble_guard_floor=bub_floor,
    )


def rank_universe(
    closes: pd.DataFrame,
    universe: list[str],
    as_of: pd.Timestamp,
    persistence: dict[str, int] = None,
    regime: Optional[dict] = None,
) -> list[FOMScore]:
    persistence = persistence or {}
    scores = []
    for t in universe:
        if t not in closes.columns or closes[t].dropna().empty:
            continue
        s = score_ticker(closes, t, as_of, persistence_weeks=persistence.get(t, 0), regime=regime)
        scores.append(s)
    scores.sort(key=lambda x: x.final_fom, reverse=True)
    return scores


def main(out_dir: Path, use_regime: bool = True) -> int:
    out_dir.mkdir(parents=True, exist_ok=True)
    today = pd.Timestamp("2026-05-29")
    regime = classify_regime() if use_regime else None
    if regime is not None:
        print(
            f"Regime: {regime['label']} ({', '.join(regime['reasons']) or 'no reasons'})",
            file=sys.stderr,
        )
    print(f"FOM scoring as of {today.date()}, universe {len(DEFAULT_UNIVERSE)} tickers", file=sys.stderr)
    closes = fetch_monthly(DEFAULT_UNIVERSE + INDICES + SECTOR_ETFS + CRYPTO, "2019-12-01", "2026-05-29")
    print(f"  data: {len(closes.columns)} tickers with data", file=sys.stderr)
    scores = rank_universe(closes, DEFAULT_UNIVERSE, today, regime=regime)

    if regime is not None:
        scoring_method = (
            f"regime={regime['label']} weights="
            + "/".join(f"{int(round(v*100))}%" for v in regime["weights"].values())
            + " (momentum/contrarian/cyclic/quality/bubble_guard); "
            + f"bubble_guard_floor={regime['bubble_guard_floor']}"
        )
    else:
        scoring_method = "weighted 25%/25%/15%/15%/20% momentum/contrarian/cyclic/quality/bubble_guard"

    report = {
        "as_of": datetime.now(timezone.utc).isoformat(),
        "schema_version": 2,
        "scoring_window": {"start": "2019-12-01", "end": "2026-05-29"},
        "universe_size": len(DEFAULT_UNIVERSE),
        "tickers_scored": len(scores),
        "regime": regime,
        "scoring_method": scoring_method,
        "horizon_profiles": {h: prof["weights"] for h, prof in HORIZON_PROFILES.items()},
        "ranked_full": [
            asdict(s) | {"base_score": s.base_score, "final_fom": s.final_fom,
                         "horizon_scores": s.horizon_scores}
            for s in scores
        ],
        "top_3_picks": [
            {"rank": i + 1, "ticker": s.ticker, "final_fom": round(s.final_fom, 2),
             "momentum": round(s.momentum, 1), "contrarian": round(s.contrarian, 1),
             "cyclic": round(s.cyclic, 1), "quality": round(s.quality, 1),
             "bubble_guard": round(s.bubble_guard_val, 1), "sector": s.sector_etf,
             "ip_defensibility": s.ip_defensibility,
             "horizon_scores": s.horizon_scores}
            for i, s in enumerate(scores[:3])
        ],
        "top_50_watchlist": [
            {"rank": i + 1, "ticker": s.ticker, "final_fom": round(s.final_fom, 2),
             "momentum": round(s.momentum, 1), "contrarian": round(s.contrarian, 1),
             "cyclic": round(s.cyclic, 1), "quality": round(s.quality, 1),
             "bubble_guard": round(s.bubble_guard_val, 1), "sector": s.sector_etf,
             "horizon_scores": s.horizon_scores}
            for i, s in enumerate(scores[:50])
        ],
        "bubble_alerts_negative_guard": [
            {"ticker": s.ticker, "bubble_guard": round(s.bubble_guard_val, 1),
             "momentum": round(s.momentum, 1), "final_fom": round(s.final_fom, 2)}
            for s in scores if s.bubble_guard_val <= -20
        ],
    }
    out_path = out_dir / f"fom-monthly-{today.date()}.json"
    out_path.write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")
    print(f"wrote {out_path}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main(Path("outputs")))

