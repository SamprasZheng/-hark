"""Chokepoint screen — supply-chain bottleneck (卡脖子) analysis, scored by $hark FOM.

For a hot end-system, decompose the build into a stack, ask "if demand doubles, what
breaks first?", and surface the companies that own the true constraint — then RE-SCORE
them through the owner's own FOM engine (momentum / contrarian / quality / moat), never
borrowed scores. The methodology (7 bottleneck types + a stack/bottleneck/thesis-breaker
framing) is reimplemented in-house — no third-party text/data copied.

Curated lanes cover the main themes deterministically (high quality, verified tickers);
an unmatched topic falls back to a local-LLM decomposition whose named tickers are then
verified + FOM-scored. Recommend-only / research; never trades.

Discord: /chokepoint <topic>.
"""
from __future__ import annotations

import re
from typing import Optional

import pandas as pd

from sharks.scoring.fom import fetch_monthly, INDICES, SECTOR_ETFS
from sharks.scoring.fom_alpha import score_ticker_alpha

# The 7 bottleneck archetypes (own wording).
BOTTLENECK_TYPES = {
    "physical": "原料/實體短缺",
    "fab_capacity": "晶圓/封裝產能與前置期",
    "qualification": "認證/驗證卡關",
    "yield": "良率/製程難度",
    "thermal_power": "散熱/供電上限",
    "geo_single": "地緣單一來源",
    "single_customer": "單一大客戶集中",
}

# Curated chokepoint lanes — verified US-listed candidates; FOM re-scores them at runtime.
CHOKEPOINT_LANES: dict[str, dict] = {
    "ai_factory": {
        "label": "AI 算力工廠 — 先進封裝/測試",
        "supertrend": "AI 資本支出爆量,加速器需求逐代翻倍",
        "bottleneck": "CoWoS 先進封裝產能 + 晶片/HBM 測試",
        "bottleneck_type": "fab_capacity",
        "stack": ["電力/散熱", "測試/檢測", "封裝(OSAT)", "載板/材料", "HBM", "GPU/ASIC"],
        "candidates": ["AMKR", "FORM", "CAMT", "AEHR", "ICHR", "UCTT", "ONTO", "KLAC", "TER"],
        "thesis_breaker": "CoWoS 過度擴產轉供過於求,或加速器需求急凍",
    },
    "hbm": {
        "label": "高頻寬記憶體(HBM)鏈",
        "supertrend": "每張加速器吃的 HBM 容量/層數逐代上升",
        "bottleneck": "HBM 產能 + 堆疊良率 + 測試",
        "bottleneck_type": "yield",
        "stack": ["DRAM die", "TSV 堆疊", "測試/檢測", "封裝整合"],
        "candidates": ["MU", "FORM", "ONTO", "CAMT", "TER", "KLAC"],
        "thesis_breaker": "三大廠 HBM 產能同步開出 → 價格/毛利反轉",
    },
    "power_thermal": {
        "label": "資料中心 供電/散熱",
        "supertrend": "機櫃功率密度飆升,液冷成標配",
        "bottleneck": "電力配送設備 + 液冷前置期",
        "bottleneck_type": "thermal_power",
        "stack": ["電網介接", "UPS/配電", "電源(PSU)", "液冷/CDU", "機櫃"],
        "candidates": ["VRT", "ETN", "GEV", "NVT", "PWR", "ATKR"],
        "thesis_breaker": "資料中心 capex 放緩 / 電力併網瓶頸壓抑出貨",
    },
    "optics_cpo": {
        "label": "AI 互連 — 矽光子 / 共封裝光學(CPO)",
        "supertrend": "GPU 叢集互連頻寬瓶頸,光逐步取代銅",
        "bottleneck": "矽光子/CPO 光引擎與高速光元件產能/認證",
        "bottleneck_type": "qualification",
        "stack": ["雷射/光源", "矽光子引擎", "DSP/retimer", "光模組", "交換器"],
        "candidates": ["COHR", "LITE", "CRDO", "ALAB", "AAOI", "POET", "MRVL", "CIEN", "SIVEF"],
        "thesis_breaker": "CPO 採用慢於預期 / 可插拔光模組維持主流",
    },
    "rf_frontend": {
        "label": "RF 前端 — 波束成型/功率放大",
        "supertrend": "LEO 衛星 + 相位陣列 + 高頻段需求",
        "bottleneck": "GaN PA / beamformer IC / 濾波器整合 + 空間級認證",
        "bottleneck_type": "qualification",
        "stack": ["GaN/GaAs 磊晶", "PA/LNA", "beamformer IC", "濾波器", "模組整合"],
        "candidates": ["QRVO", "SWKS", "MTSI", "AOSL", "SITM", "WOLF"],
        "thesis_breaker": "手機 RF 內容停滯 + LEO 量產遞延",
    },
}

LANE_KEYWORDS: dict[str, tuple[str, ...]] = {
    "ai_factory": ("ai factory", "ai 工廠", "cowos", "封裝", "packaging", "osat", "算力", "gpu", "加速器", "先進封裝"),
    "hbm": ("hbm", "高頻寬", "記憶體", "memory", "dram"),
    "power_thermal": ("散熱", "液冷", "cooling", "thermal", "power", "電力", "供電", "資料中心", "datacenter", "data center"),
    "optics_cpo": ("cpo", "矽光子", "silicon photonics", "photonic", "光通訊", "光模組", "互連", "interconnect", "optic"),
    "rf_frontend": ("rf", "射頻", "beamformer", "波束", "相位陣列", "phased array", "gan", "前端", "衛星", "satellite", "leo"),
}


# ─── Pure helpers ───────────────────────────────────────────────────────────────
def match_lanes(topic: str) -> list[str]:
    """Curated lanes whose keywords appear in the topic. Pure."""
    t = (topic or "").lower()
    return [k for k, kws in LANE_KEYWORDS.items() if any(kw in t for kw in kws)]


def lane_meta(key: str, topic: str = "") -> dict:
    """Lane metadata (curated, or a synthetic header for an LLM-proposed lane). Pure."""
    if key in CHOKEPOINT_LANES:
        return {**CHOKEPOINT_LANES[key], "key": key}
    return {"key": key, "label": f"LLM 提名:{topic}", "supertrend": topic,
            "bottleneck": "(本地 LLM 拆解,需查證)", "bottleneck_type": None,
            "stack": [], "thesis_breaker": None}


# ─── Scoring (network) ──────────────────────────────────────────────────────────
def score_candidates(closes, tickers: list[str], as_of: pd.Timestamp) -> list[dict]:
    """FOM-score the candidates we have price data for; sort by FOM-alpha desc."""
    rows: list[dict] = []
    for t in tickers:
        if t not in getattr(closes, "columns", []) or closes[t].dropna().empty:
            continue
        try:
            r = score_ticker_alpha(closes, t, as_of)
        except Exception:
            continue
        s = closes[t].dropna()
        r["ret_3m"] = round(float(s.iloc[-1] / s.iloc[-4] - 1) * 100, 1) if len(s) >= 4 else None
        rows.append(r)
    rows.sort(key=lambda x: x.get("final_fom_alpha", 0), reverse=True)
    return rows


def _llm_candidates(topic: str, settings) -> list[str]:
    """Best-effort local-LLM proposal of US tickers for an unmatched topic's chokepoint."""
    try:
        from sharks.discord.brains import ask_local_model
    except Exception:
        return []
    q = (f"供應鏈卡脖子分析。主題:{topic}。"
         "如果這個需求翻倍,最先卡住的環節是什麼?哪些『美股上市』公司握有那個瓶頸?"
         "只回 6-8 個美股代碼,逗號分隔、全大寫,不要解釋、不要其他字。")
    rep = ask_local_model(q, settings)
    if not getattr(rep, "ok", False):
        return []
    cands = re.findall(r"\b[A-Z]{1,5}\b", rep.text or "")
    drop = {"AI", "US", "ETF", "GPU", "HBM", "CPO", "RF", "AND", "THE", "USD"}
    return list(dict.fromkeys(c for c in cands if c not in drop))[:8]


def analyze(topic: str, settings=None, *, network: bool = True,
            as_of: Optional[pd.Timestamp] = None) -> dict:
    """Full chokepoint analysis for a topic: match lane(s) (or LLM-propose), then
    FOM-score the candidates. Returns {topic, matched, llm_used, lanes:[...]}."""
    as_of = as_of or pd.Timestamp.today().normalize()
    keys = match_lanes(topic)
    llm_used = False
    cand_sets: dict[str, list[str]] = {}
    if keys:
        cand_sets = {k: list(CHOKEPOINT_LANES[k]["candidates"]) for k in keys}
    elif settings is not None and network:
        names = _llm_candidates(topic, settings)
        if names:
            cand_sets = {"_llm": names}
            llm_used = True

    all_tickers = sorted({t for v in cand_sets.values() for t in v})
    scored: dict[str, list[dict]] = {}
    if all_tickers and network:
        start = (as_of - pd.Timedelta(days=6 * 365)).strftime("%Y-%m-%d")
        try:
            closes = fetch_monthly(all_tickers + INDICES + SECTOR_ETFS, start, as_of.strftime("%Y-%m-%d"))
            for k, tickers in cand_sets.items():
                scored[k] = score_candidates(closes, tickers, as_of)
        except Exception:
            scored = {}

    order = keys if keys else (["_llm"] if llm_used else [])
    lanes = [{**lane_meta(k, topic), "candidates": scored.get(k, [])} for k in order]
    return {"topic": topic, "matched": bool(keys), "llm_used": llm_used, "lanes": lanes}
