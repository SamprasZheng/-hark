"""Global Exposure — 個股全球供應鏈/地緣曝險評分(world model Layer 3).

純函式設計(同 reflexivity_state):曝險 = max(所屬群組權重, 板塊底線, default),
配置住 config/world_exposure.json(靜態、git 版控 → PIT 安全)。世界事件活躍時
由 ``world_factor`` 給出乘法折減(無事件 = 1.0,不動分 — 平時零行為差異,
保住既有校準連續性);折減地板 0.65。

消費端:backtest/rally_dna.dna_match_today(dna_plus 乘法折減 + taiwan_exposed
規則旗標)、daily_dna_routine position brief。

recommend-only;曝險是篩選輸入,非倉位指令。
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

EXPOSURE_CONFIG = Path("config/world_exposure.json")
FACTOR_FLOOR = 0.65          # 乘法折減地板(再高的曝險×再重的事件也不把分數砍超過 35%)

_cfg_cache: Optional[dict] = None


def load_exposure_config(path: Path = EXPOSURE_CONFIG) -> dict:
    global _cfg_cache
    if _cfg_cache is None:
        try:
            _cfg_cache = json.loads(Path(path).read_text(encoding="utf-8"))
        except Exception:
            _cfg_cache = {}
    return _cfg_cache


def exposure_for(ticker: str, sector: Optional[str] = None,
                 config: Optional[dict] = None) -> dict:
    """→ {ticker, global_exposure 0..1, groups, taiwan_exposed}。純函式(config 可注入)。"""
    cfg = config if config is not None else load_exposure_config()
    t = (ticker or "").upper()
    hit_groups, weights = [], []
    for name, g in (cfg.get("groups") or {}).items():
        if t in (g.get("tickers") or []):
            hit_groups.append(name)
            weights.append(float(g.get("weight", 0.5)))
    base = (cfg.get("sector_base") or {}).get(sector) if sector else None
    candidates = weights + ([float(base)] if isinstance(base, (int, float)) else [])
    score = max(candidates) if candidates else float(cfg.get("default", 0.25))
    return {"ticker": t,
            "global_exposure": round(min(max(score, 0.0), 1.0), 3),
            "groups": hit_groups,
            "taiwan_exposed": "taiwan_chain" in hit_groups}


def world_factor(exposure: float, world_state: Optional[dict]) -> float:
    """事件活躍時的 dna_plus 乘法折減:1 - exposure × exposure_penalty(取事件 max),
    地板 FACTOR_FLOOR;無事件/無 world_state → 1.0(零行為差異)。"""
    pen = ((world_state or {}).get("impacts") or {}).get("exposure_penalty") or 0.0
    if not pen or not isinstance(pen, (int, float)):
        return 1.0
    return round(max(1.0 - float(exposure) * float(pen), FACTOR_FLOOR), 3)
