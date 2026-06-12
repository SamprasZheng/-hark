"""行為偏誤層 — 前景理論(prospect theory)在本倉的純函式落地(plan2.md 行為金融採納).

三個純函式,零 I/O、零網路、零隨機,由父層接線進 world_monitor / 風險佇列 / 晨報:

  1. behavioral_deviation_score — 行為偏離強度 0..10:世界事件(TS_HIGH /
     GSCPI_SPIKE / GPR_EXTREME,id 對齊 config/world_events.json)+ 結構指標
     (GPRC_TWN z60 / 恐慌放量代理 / 反身性斷裂擴散)的顯式先驗加權和,封頂 10。
  2. loss_aversion_flags — 持倉層級前景理論檢查:損失厭惡死守(crisis 下已虧損
     部位傾向不砍)與成本錨定(久持 + 虧損 + 高偏離 → 錨在買入成本不認錯)。
  3. mania_overconfidence_note — mania 狀態 + 高偏離 → 一行過度自信/從眾警語
     (晨報顯示用)。

紀律:
  - llm_involvement: none — 全規則式;權重/閾值為顯式先驗(各自帶 _doc 依據),
    非歷史擬合,月度人工覆核(同 config/world_events.json calibration.review 精神)。
  - observe-first / recommend-only — 輸出只進 brief / 風險佇列「文案」,
    不得 gate KPI、不得進 sizing 算術。plan2.md 的 dynamic_sizing 段落
    (behavioral_score 直接乘 size)刻意不採納:Risk Officer 審核是人 + 規則,
    不是這個分數;本模組永不下單。
  - 缺輸入 → 對應 component 跳過並列入 missing,絕不發明值(CLAUDE.md §2)。
  - VIX 蓄意不用:data/lake 無 VIX 序列(無已建立的免費、可 PIT 快照的來源;
    plan2.md 範例的 vix_spike 無法在不發明值的前提下落地)。恐慌放量改由
    caller 供給的 qqq_vol_ratio(QQQ 近 6 個月已實現波動 / trailing 基準,
    同 rally_dna.classify_states4 的 vol6 口徑精神)代理。
"""

from __future__ import annotations

from typing import Optional

# ── 偏離分數顯式先驗(0..10 封頂;權重 = 顯式猜測,非擬合)──

SCORE_CAP = 10.0    # plan2.md 範例同款 0~10 標準化;六 component 全亮恰為 10.0

DEVIATION_PRIORS: dict = {
    "_doc": ("行為偏離分數先驗(plan2.md 行為金融層採納)。每項 = 市場處於"
             "「行為偏差時期」(事件驅動 + 結構性壓力)而非「有效市場時期」的"
             "一票證據;權重相對大小反映本倉尾部排序(台海 > 供應鏈 > 全球地緣),"
             "絕對值為顯式猜測。observe-first:分數只進 brief / 風險佇列文案。"),
    "_vix_excluded": ("VIX 蓄意不用 — lake 無 VIX 序列(無免費 PIT 快照源),"
                      "不發明值;恐慌放量由 qqq_vol_ratio 代理(見 VOL_PANIC)。"),
    "TS_HIGH": {
        "weight": 2.8,
        "_doc": ("world_events 含 TS_HIGH(台海事件,config/world_events.json:"
                 "gprc_twn_z60≥2σ 或 gprc_twn≥p95)。plan2.md 範例先驗 2.5,"
                 "上調至 2.8:台海是本倉最大單一尾部(taiwan_chain 集中)。"),
    },
    "GSCPI_SPIKE": {
        "weight": 2.0,
        "_doc": ("world_events 含 GSCPI_SPIKE(GSCPI≥1.5σ 或 ≥1.0 且單月 +0.8σ)。"
                 "缺事件清單時退回 raw gscpi≥1.5 同口徑判定(不另設新閾值)。"
                 "供應鏈壓力 = 有限注意力偏誤的溫床(反應不足 → 補跌)。"),
    },
    "GPR_EXTREME": {
        "weight": 1.5,
        "_doc": ("world_events 含 GPR_EXTREME(GPR≥p99=330,1985+)。全球地緣"
                 "極端期從眾/恐慌主導 — 權重低於台海(對本倉持股鏈衝擊較間接)。"),
    },
    "TWN_Z60": {
        "weight": 1.2, "min": 2.0,
        "_doc": ("gprc_twn_z60 ≥ 2.0(60 月滾動 z,world_monitor.trailing_z 口徑)。"
                 "與 TS_HIGH 事件可疊加:事件可由 p95 水準路徑觸發,z 路徑同時"
                 "確認時代表「升速」而非僅「水準」,額外 +1.2 強度。"),
    },
    "VOL_PANIC": {
        "weight": 1.5, "min": 1.5,
        "_doc": ("qqq_vol_ratio ≥ 1.5 — 恐慌放量代理(QQQ 近 6 個月已實現波動 / "
                 "trailing 基準,caller 供給;classify_states4 vol6 口徑精神)。"
                 "對應 plan2.md 的 vix_spike +1.5(損失厭惡:下跌時量能異常放大)。"),
    },
    "BREADTH_BREAK": {
        "weight": 1.0, "min": 10,
        "_doc": ("breadth_break_count ≥ 10 — 反身性斷裂擴散(scoring/reflexivity "
                 "斷裂股數,caller 供給)。窄市斷裂擴散 = 從眾解體的早期訊號。"),
    },
}


def behavioral_deviation_score(*, world_events: Optional[list[str]],
                               gprc_twn_z60: Optional[float] = None,
                               gscpi: Optional[float] = None,
                               qqq_vol_ratio: Optional[float] = None,
                               breadth_break_count: Optional[int] = None) -> dict:
    """行為偏離強度 0..10(純函式;高分 = 事件驅動的行為偏差時期).

    Args:
        world_events: 已觸發世界事件 id 清單(world_monitor events_triggered 的
            id 欄,如 ["TS_HIGH", "GPR_ELEVATED"])。None = 來源缺席(degraded),
            事件 component 全跳過並記 missing;[] = 求值過且無事件(0 分,非缺)。
        gprc_twn_z60: GPRC_TWN 60 月滾動 z(world_monitor metrics 的 gprc_twn_z60)。
        gscpi: GSCPI 最新值(z 單位)。僅當 world_events 缺席時作 GSCPI_SPIKE
            的同口徑退路(≥1.5);事件清單在場時以事件為準,不重複計分。
        qqq_vol_ratio: QQQ 近 6 個月已實現波動 / trailing 基準(caller 計算供給)。
        breadth_break_count: 反身性斷裂股數(caller 供給)。

    Returns:
        {"score": 0..10, "components": {亮起項: 權重}, "missing": [缺席輸入],
         "llm_involvement": "none", "disclaimer": ...} — 全 JSON 可序列化。
        缺輸入 → component 跳過 + 列入 missing,絕不發明值。
    """
    p = DEVIATION_PRIORS
    components: dict[str, float] = {}
    missing: list[str] = []

    if world_events is None:
        missing.append("world_events")
        events: set = set()
    else:
        events = set(world_events)
        for ev in ("TS_HIGH", "GSCPI_SPIKE", "GPR_EXTREME"):
            if ev in events:
                components[ev] = p[ev]["weight"]

    if gprc_twn_z60 is None:
        missing.append("gprc_twn_z60")
    elif gprc_twn_z60 >= p["TWN_Z60"]["min"]:
        components["TWN_Z60"] = p["TWN_Z60"]["weight"]

    if gscpi is None:
        missing.append("gscpi")
    elif (world_events is None and "GSCPI_SPIKE" not in components
          and gscpi >= 1.5):    # 退路口徑 = world_events.json GSCPI_SPIKE 主閾值
        components["GSCPI_SPIKE"] = p["GSCPI_SPIKE"]["weight"]

    if qqq_vol_ratio is None:
        missing.append("qqq_vol_ratio")
    elif qqq_vol_ratio >= p["VOL_PANIC"]["min"]:
        components["VOL_PANIC"] = p["VOL_PANIC"]["weight"]

    if breadth_break_count is None:
        missing.append("breadth_break_count")
    elif breadth_break_count >= p["BREADTH_BREAK"]["min"]:
        components["BREADTH_BREAK"] = p["BREADTH_BREAK"]["weight"]

    score = min(round(sum(components.values()), 2), SCORE_CAP)
    return {
        "score": score,
        "components": components,
        "missing": missing,
        "llm_involvement": "none",
        "disclaimer": "observe-first:分數只進 brief/風險佇列文案,不 gate KPI、不進 sizing 算術。",
    }


# ── 前景理論持倉檢查閾值(顯式猜測,非擬合)──

FLAG_PRIORS: dict = {
    "_doc": ("前景理論檢查閾值 — 顯式猜測(Kahneman-Tversky 1979 損失厭惡 λ≈2:"
             "等額損失的痛感約 2 倍於獲利 → disposition effect 賣贏不賣輸)。"
             "flags 只進風險佇列文案供人工覆核,不自動砍倉。"),
    "LOSS_AVERSION_PNL_MAX": {
        "value": -8.0,
        "_doc": ("帳損 ≤ -8%(λ≈2 ⇒ 心理上等同 +16% 獲利的權重,死守誘因已"
                 "顯著)且 crisis 訊號在場 → 高優先覆核。顯式猜測。"),
    },
    "ANCHORING_HOLDING_DAYS_MIN": {
        "value": 45,
        "_doc": ("持有 ≥45 天(約 2 個月交易日)仍虧損 — 超過事件型交易的正常"
                 "驗證窗,錨定買入成本不認錯的嫌疑升高。顯式猜測。"),
    },
    "ANCHORING_DEVIATION_MIN": {
        "value": 5.5,
        "_doc": ("行為偏離分數 ≥5.5(滿分 10 過半,至少兩個主 component 亮起)"
                 "時,「再等等」的機會成本明顯升高。顯式猜測。"),
    },
}


def loss_aversion_flags(*, ticker: str,
                        pnl_pct: Optional[float] = None,
                        holding_days: Optional[int] = None,
                        regime_state: Optional[str] = None,
                        crisis_signal: bool = False,
                        deviation_score: Optional[float] = 0.0) -> list[dict]:
    """單一持倉的前景理論檢查 → 風險佇列 flag 清單(純函式).

    Args:
        ticker: 持倉代號(只回填進 flag,不查任何外部資料)。
        pnl_pct: 帳面損益(百分比單位,-8 = -8%)。None = 缺值 → 兩檢查皆跳過。
        holding_days: 持有日數(自然日)。None → 錨定檢查跳過。
        regime_state: classify_states4 四態之一(mania/bull/bear/crisis)或 None。
            regime_state == "crisis" 與 crisis_signal 同義(任一在場即視為 crisis)。
        crisis_signal: 外部 crisis 訊號(如 world_monitor 高嚴重度事件聚合)。
        deviation_score: behavioral_deviation_score 的 score。None → 錨定檢查跳過。

    Returns:
        list[dict] — 0..2 個 flag,每個含 type/priority/ticker/reason/observed,
        JSON 可序列化。空清單 = 無行為偏誤疑慮(或輸入不足,寧缺勿濫)。
    """
    flags: list[dict] = []
    in_crisis = bool(crisis_signal) or regime_state == "crisis"

    la_max = FLAG_PRIORS["LOSS_AVERSION_PNL_MAX"]["value"]
    if in_crisis and pnl_pct is not None and pnl_pct <= la_max:
        flags.append({
            "type": "LOSS_AVERSION",
            "priority": "high",
            "ticker": ticker,
            "reason": (f"損失厭惡死守風險 — crisis 訊號下已虧損 {pnl_pct:.1f}% 的部位"
                       f"傾向不砍(K-T λ≈2:損失痛感約 2 倍,賣贏不賣輸);"
                       f"請人工覆核停損/失效條件,observe-first 非自動砍倉。"),
            "observed": {"pnl_pct": pnl_pct, "threshold_pnl_pct": la_max,
                         "crisis_signal": bool(crisis_signal),
                         "regime_state": regime_state},
        })

    hd_min = FLAG_PRIORS["ANCHORING_HOLDING_DAYS_MIN"]["value"]
    dev_min = FLAG_PRIORS["ANCHORING_DEVIATION_MIN"]["value"]
    if (holding_days is not None and holding_days >= hd_min
            and pnl_pct is not None and pnl_pct < 0
            and deviation_score is not None and deviation_score >= dev_min):
        flags.append({
            "type": "ANCHORING",
            "priority": "medium",
            "ticker": ticker,
            "reason": (f"成本錨定風險 — 持有 {holding_days} 天仍虧損 {pnl_pct:.1f}%,"
                       f"且行為偏離分數 {deviation_score:.1f} ≥ {dev_min}:評價應錨定"
                       f"當下證據而非買入成本;覆核論點是否已失效。"),
            "observed": {"pnl_pct": pnl_pct, "holding_days": holding_days,
                         "deviation_score": deviation_score,
                         "thresholds": {"holding_days": hd_min,
                                        "deviation_score": dev_min}},
        })
    return flags


# ── mania 過度自信警語(brief 顯示用)──

MANIA_NOTE_DEVIATION_MIN = 6.0
"""mania + 偏離 ≥6/10(plan2.md:behavioral_deviation_score >6 → 強制 human_review
的同款閾值)才出警語 — 低於此視為正常牛市,不洗版。顯式猜測。"""


def mania_overconfidence_note(regime_state: Optional[str],
                              deviation_score: Optional[float]) -> Optional[str]:
    """mania 狀態 + 行為偏離 ≥6 → 一行過度自信/從眾警語,否則 None(純函式).

    regime_state 取 classify_states4 四態(mania/bull/bear/crisis);
    deviation_score 取 behavioral_deviation_score 的 score。任一缺 → None。
    """
    if regime_state != "mania" or deviation_score is None:
        return None
    if deviation_score < MANIA_NOTE_DEVIATION_MIN:
        return None
    return (f"mania 狀態 + 行為偏離 {deviation_score:.1f}/10 ≥ "
            f"{MANIA_NOTE_DEVIATION_MIN:.0f}:過度自信/從眾風險升高 — "
            f"漲勢共識最擁擠時新倉寧缺勿濫、既有倉覆核失效條件"
            f"(observe-first,非倉位指令)。")
