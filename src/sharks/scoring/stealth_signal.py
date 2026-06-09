"""隱蔽吸籌偵測 — Stealth-accumulation detector (catch it BEFORE it's obvious).

Principal edge (2026-06): 行情可能未完,華爾街會把**錯殺的股票悄悄炒起來**(像今年的
INTC/MU),挑「大家還沒看到」的。要抓的不是已經噴的票,而是**資金先進、價格還沒動**的
吸籌指紋——也就是 rally_signal「連續起漲」的**上游一步**。

吸籌指紋(和追高相反):
  資金(量) 高   ← 成交量相對放大 = 有人在收
  距高 深       ← 被錯殺、還沒回去(有空間、非近高)
  價還沒表態     ← 月線**還沒**金叉突破(量進價未動 = 還在收貨,不是已表態)
  低關注(可選) ← 大家還沒看到(attention 低 → 越隱蔽)

刻意 REWARD「低動能」:價已經垂直 = 已經不隱蔽了(大家都看到),分數反而降。這正是
「抓他們想炒、但還沒炒上去的」的數學表達。

純邏輯、duck-typed(吃 basecross 候選的欄位:vol_surge / dist_ath_pct / golden_cross /
bottom_zone),不 import basecross,離線可測。recommend-only,永不下單。
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Optional

CAP_MIN = 45.0          # 資金(量能)分數低於此 = 沒有明顯吸籌跡象
BEATEN_MIN = 15.0       # 距高低於此 = 近高,不是錯殺吸籌
SWEET = 48.0            # 距高甜蜜中心(深跌收貨區 ~48% off high)


@dataclass
class StealthResult:
    ticker: str
    score: float = 0.0
    capital: Optional[float] = None     # 資金(量能)分數 0..100
    dist_ath_pct: Optional[float] = None
    broke_out: bool = False             # 月線是否已金叉突破(已表態)
    stealth: bool = False               # 隱蔽吸籌(量進價未動)
    verdict: str = ""
    note: str = ""


def _capital_from_volsurge(vs: Optional[float]) -> Optional[float]:
    """量能放大倍數 → 0..100(與 rally_signal 同一條 log 映射)。"""
    if vs is None:
        return None
    return max(0.0, min(100.0, 30.0 + 55.0 * math.log2(max(vs, 1e-9))))


def stealth_score(c, attention: Optional[float] = None) -> StealthResult:
    """吸籌分數:資金先進 + 距高深 + 價還沒突破(+ 低關注)。c = basecross 候選。"""
    r = StealthResult(ticker=getattr(c, "ticker", ""))
    r.dist_ath_pct = getattr(c, "dist_ath_pct", None)
    cap = _capital_from_volsurge(getattr(c, "vol_surge", None))
    r.capital = round(cap, 1) if cap is not None else None
    r.broke_out = bool(getattr(c, "golden_cross", False) and getattr(c, "bottom_zone", False))
    d = r.dist_ath_pct or 0.0

    if cap is None:
        r.verdict, r.note = "⚪ 無量能資料", "沒有成交量,無法判斷吸籌"
        return r
    beaten = max(0.0, 1 - abs(d - SWEET) / SWEET)          # 距高甜蜜區 0..1
    quiet = 0.0 if r.broke_out else 1.0                    # 還沒突破 = 還在收貨
    overlooked = (100 - attention) / 100 if attention is not None else 0.5
    r.score = round(0.45 * cap + 25 * beaten + 18 * quiet + 12 * overlooked, 1)

    if cap < CAP_MIN:
        r.verdict, r.note = "⚪ 無明顯資金", f"量×不足(資金分 {cap:.0f})"
    elif d < BEATEN_MIN:
        r.verdict, r.note = "〽️ 近高·非吸籌", f"距高僅 {d:.0f}%"
    elif r.broke_out:
        r.verdict, r.note = "🟡 已啟動(非隱蔽)", f"量已表態、月線已金叉(距高 {d:.0f}%)"
    elif beaten >= 0.4:
        r.stealth = True
        r.verdict = "🕵️ 隱蔽吸籌(量進價未動)"
        r.note = f"資金 {cap:.0f} 進場、距高 {d:.0f}% 深、月線**還沒**突破 = 疑似收貨中"
    else:
        r.verdict, r.note = "🔵 疑似吸籌(續觀察)", f"量增但距高 {d:.0f}% 偏淺"
    return r


def stealth_rank(candidates, attention_by_ticker: Optional[dict] = None) -> list[StealthResult]:
    """Score + rank: 隱蔽吸籌優先,再按分數。"""
    attention_by_ticker = attention_by_ticker or {}
    out = [stealth_score(c, attention_by_ticker.get(getattr(c, "ticker", ""))) for c in candidates]
    out.sort(key=lambda r: (r.stealth, r.score), reverse=True)
    return out
