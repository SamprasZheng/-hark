---
type: synthesis
domain: tech-trend
tags: [cross-validation, fom, bubble-guard, evidence-gate, reconciliation]
as_of_timestamp: 2026-05-31T01:45:00+08:00
author_role: researcher
status: live
schema_version: 1
---

# tech/ 判決 × 量化系統交叉驗證 / Verdicts × Quant-System Reconciliation

Bridges the [[scoreboard]] due-diligence verdicts to the existing `$hark` quant signals — the FOM `bubble_guard` ([[../wiki/07_ai_bubble_audit]]) and the 十足的證據 gate ([[../philosophy/concepts/evidence-gated-rebalance]]). Goal: does the qualitative 質變-vs-同溫層 screen AGREE with the mechanical scorer? **Research only; not advice.**

## §1. Verdict ↔ bubble_guard 對照

`bubble_guard` values are the documented run from [[../wiki/07_ai_bubble_audit]] §5 (2026-05-29; −95 = max bubble-stress). Tickers outside that run are marked **TBD (needs live FOM scan)** — not invented.

| tech/ trend | 判決 | key US ticker | bubble_guard | 一致性 / read |
|---|---|---|:--:|---|
| [[memory-supercycle]] | 結構 | MU | **−95** | ✅ 強一致 — DD 的「股價跑在基本面前」= bubble_guard 最高壓力 |
| [[optical-interconnect-cpo]] | 結構 | AXTI | **−95** | ✅ 強一致 — InP 基板 froth；CPO「故事領先出貨 1–2 年」被機械分數確認 |
| [[optical-supply-chain-deep]] | (深掘) | AEHR | **−95** | ✅ 二階測試/量測節點同屬 SOXX 過熱帶 |
| [[ai-edge-devices]] | **過熱** | MU / 半導體 | −95 (MU) | ✅ 一致 — 「行銷外殼、毛利歸記憶體」+ 記憶體節點過熱 |
| [[model-leadership-and-data]] | 結構 | NVDA / AVGO | **+15 / +15** | ⚠️ 分歧 — 領導層健康(bubble_guard 正)；DD 說「純模型層不可投資」指的是 OpenAI/Anthropic(未上市)，非 NVDA。曝險落在健康的算力層 |
| [[autonomous-driving]] | 結構 | NVDA / TSM | **+15 / 0** | ✅ 一致 — DRIVE 算力節點健康；LiDAR 個股(LAZR)已自爆，與 DD 的「零件贏≠股票贏」一致 |
| [[ai-eats-software]] | 結構 | MSFT / CRM / NOW | TBD | 需 live scan — 07_ai_bubble_audit 未列；DD 點名「捕獲者 vs 薄 SaaS」待機械分數驗證 |
| [[ai-pharma-glp1]] | 結構* | LLY / NVO | TBD (非美/非當前 universe) | 需 scan / 多為非 SOXX；GLP-1 現金流質變不靠 bubble_guard |
| [[glp1-supply-chain]] | (深掘) | CDMO/裝置 | TBD | 多為歐洲(BANB.SW/YPSN.SW)，待 Phase-2 後綴支援 |
| [[youth-culture-shifts]] | 結構 | UBER / DASH / META | TBD | 需 scan — 平台股不在 07 的 SOXX 樣本 |
| [[quantum-vs-bitcoin]] | **太早** | IONQ / QBTS / RGTI | TBD (低 momentum) | ✅ 一致 — [[../wiki/16_rally_themes_and_coverage_audit]] §4 已列「不要追」 |

**核心交叉確認**：tech/ DD 最重要的橫向結論——「**股價同時跑在記憶體、CPO 的真實基本面之前**」——被獨立的 `bubble_guard −95`（MU / AXTI / AEHR 全在 SOXX 過熱帶）**機械性確認**。兩套方法、同一結論 = 高可信。反之，領導層（NVDA/TSM/AVGO，bubble_guard ≥0）兩套方法都說「結構健康」。

## §2. 證據閘套用 / Evidence-gate application

Per [[../philosophy/concepts/evidence-gated-rebalance]]: 進攻需 ≥4/5 維（消息/資金/交易量/進出口/營利，含強制 earnings + 一個 primary catalyst）；防守在系統性風險或 ≥2/5 即可動。把 9 條判決對映成「進攻 / 預設持有 / 防守」姿態：

| 姿態 | 趨勢 | 理由 |
|---|---|---|
| **預設持有 (default-hold)** | memory / CPO / autonomous / ai-eats-software / model-leadership | 判決皆 **結構**＝真實但已被定價；無「未被定價的進攻證據」，且 bubble_guard 對過熱節點示警 → 預設不追高，等回檔或二階節點 |
| **可選擇性進攻 (selective offense, 需逐檔過閘)** | ai-pharma-glp1 (GLP-1 側) | 唯一有「加速中的已實現 P&L + FDA 權威 catalyst」的現金流質變；仍須逐檔過 4/5 維 + 倉位上限 |
| **明確不進攻 (avoid offense)** | ai-edge-devices (過熱) / quantum-vs-bitcoin (太早) | 過熱＝同溫層風險高；太早＝無近期 P&L／時間表。兩者皆不符進攻證據門檻 |

**注意**：所有姿態仍受 Risk Officer + 倉位/集中度上限 + 板塊上限約束（[[../philosophy/08-risk-and-position]]）。tech/ 判決是「篩選輸出」，不繞過任何閘門。

## §3. 尚待的 live 驗證 / What still needs a live scan

`bubble_guard` 只覆蓋 [[../wiki/07_ai_bubble_audit]] 的 SOXX 樣本。要完成全面交叉驗證，需對 tech/ 的可投資節點籃跑一次 live FOM：

- **US-listed 待 scan**：MSFT, CRM, NOW, PLTR, INTU, ADBE, LLY, NVO, UBER, DASH, META, NFLX, SPOT, ARM, AVGO, COHR, LITE, AXTI, FN, HSAI, MBLY, QCOM, IONQ, QBTS, RGTI, RXRX, SDGR
- **非 US（待 Phase-2 後綴支援）**：SK Hynix 000660.KS, Samsung 005930.KS, TSMC 2330.TW, Sumitomo 8053.T, Furukawa 5801.T, VPEC 2455.TW, Auros 322310.KQ, ASMPT 0522.HK, BANB.SW, YPSN.SW, GXI.DE
- **產出**：每檔 FOM final + bubble_guard，疊到 [[scoreboard]] 旁，標出「DD 結構 但 bubble_guard 仍健康」（較佳進場）vs「DD 結構 且 bubble_guard −95」（過熱、等回檔）。

> 可由 `sharks fom-scan`（[[../wiki/22_streamlit_page11_deep_research_ai|deep-research]] / `src/sharks/scoring/fom.py`）對上述籃子執行；非美標的須等 [[../wiki/log]] 記錄的 ticker-suffix 支援。

## §4. 一句話 / Bottom line

DD 與量化在**最關鍵處一致**：AI 週期真實、但記憶體/CPO 的**股價已過熱**（bubble_guard −95 獨立確認 DD 的 equity-ahead-of-fundamental）；領導算力層健康；量子/端側不進攻。唯一進攻候選是 GLP-1，且仍須逐檔過 5 維證據閘。下一步＝對節點籃跑 live FOM 把「結構但健康」與「結構但過熱」分流。

## See also

- [[scoreboard]] · [[00_framework]] · [[99_cross_synthesis]]
- [[../wiki/07_ai_bubble_audit]] — bubble_guard 來源
- [[../philosophy/concepts/evidence-gated-rebalance]] — 5 維 十足的證據 閘
- [[../philosophy/concepts/fom-predictive-validity]] — FOM 是 3–6m rank-edge、非 1-day timer（套用判決時的校準）
