---
type: synthesis
tags: [world-model, geopolitical, supply-chain, gscpi, gpr, taiwan, dna-engine]
title: World Model — 全球供應鏈 + 地緣反身性感測層
as_of_timestamp: 2026-06-12T17:50:00+08:00
author_role: compiler
source_paths:
  - outputs/world-monitor-2026-06-12.json
  - config/world_events.json
  - config/world_exposure.json
  - src/sharks/regime/world_monitor.py
  - src/sharks/data/world_indicators.py
  - src/sharks/scoring/global_exposure.py
  - watchlist/plan.md
confidence: 0.7
status: live
schema_version: 1
---

# World Model — 世界模型 v1(2026-06-12 上線)

把 [[06_rally_dna]] 的個股 DNA 引擎接上**全球供應鏈壓力 + 地緣政治風險**的前瞻感測。
設計輸入來自外部顧問草案(`watchlist/plan.md`,untracked),已全面翻譯成 repo 原生
架構(ARCHITECTURE「演進不翻修」:不開新層,模組按層歸位;外部草案的 `akashic/`
路徑、Mesa ABM、LanceDB 遷移均不採納或延後,見 §6 技術債)。

## 1. 數據源(皆 grade A、免 key、零成本)

| 指標 | 來源 | 頻率 | 量綱 | 抓取 |
|---|---|---|---|---|
| GSCPI | NY Fed Global Supply Chain Pressure Index | 月 | 全史 z-score | `data/world_indicators.fetch_gscpi`(2026-06-12 起每晨) |
| GPR / GPRT | Caldara-Iacoviello 地緣風險指數 | 月 | 基準~100 | `fetch_gpr_monthly` |
| GPRC_TWN / GPRC_CHN | GPR 台灣/中國分項(文章占比) | 月 | ~0-2 | 同上 |
| GPRD_MA30 | GPR 每日 30 日均(1-3 天滯後) | 日 | 基準~100 | `fetch_gpr_daily` |

PIT:兩來源每次發布**就地修訂全史、無官方 vintage 庫** — 本地 vintage 自
2026-06-12 起前向累積於 `data/lake/world/<series>-<date>.json`(不可變,首寫為準)。
在此之前的歷史回測**不得**使用本模組輸出([[../philosophy/09-point-in-time]])。

## 2. 事件引擎(閾值=分位數定錨,非虛構量綱)

`config/world_events.json` 宣告數值條件 → `regime/world_monitor` 每晨求值成布林旗標。
校準基礎(1985-01 起 n=497,2026-06-12 計):GPR p90/p95/p99 = 146/169/330;
GPRC_TWN p90/p95/p99 = 0.17/0.25/0.37。每月重算,漂移 >10% 才動閾值。

| 事件 | 條件(any) | 衝擊 |
|---|---|---|
| **TS_HIGH**(high) | GPRC_TWN 60月z ≥2 或 ≥p95(0.25) | reflexivity 權重 +0.05(從 capital 挪)、deep-kill cap ×0.75、台鏈曝險折減 25%、taiwan_chain 票 human_review |
| **GSCPI_SPIKE**(med-high) | GSCPI ≥1.5σ 或(≥1.0 且單月 +0.8) | reflexivity +0.05(從 tech 挪)、曝險折減 10%、deep-kill 加註 OCF 順延警語 |
| **GPR_EXTREME**(high) | GPR ≥p99(330) | deep-kill cap ×0.85、曝險折減 15% |
| **GPR_ELEVATED**(info) | GPR ≥p95(169) | 旗標 + brief 顯示,不動分 |
| TARIFF_NEW / CYBER_TSMC | 手動旗(`manual_flags`,需 A/B 級源確認) | 曝險折減 / cap 乘數 / review |

多事件疊加:cap 乘數取 **min**(最保守)、曝險罰則取 **max**、權重總調幅封頂 0.10
(權重=顯式先驗,事件只准微調;沿用 mania 先例「從 donor 挪、總和=1」)。

## 3. Global Exposure(個股曝險)

`config/world_exposure.json`(靜態、git 版控=PIT 安全):taiwan_chain 0.9 /
optics_cpo 0.7 / china_revenue 0.6,無命中退板塊底線再退 default 0.25。
曝險只在事件活躍時生效:`dna_plus × world_factor`,`factor = 1 − exposure × penalty`
(地板 0.65;**無事件 = 1.0,平時零行為差異**,保住既有前瞻校準連續性)。
`dna_plus_raw`、`global_exposure`、`world_factor` 全部落 `outputs/dna-scores-log.jsonl`。

## 4. 當前狀態(as_of 2026-06-12)— 上線首日三事件齊發

- **TS_HIGH**:GPRC_TWN = 0.489(**>p99**,60月z 2.24)、GPRC_CHN = 1.55(>p99)。
- **GSCPI_SPIKE**:GSCPI 2026-04/05 = 1.82/1.77(3 月才 0.68 — 單月 +1.15σ 跳升)。
- **GPR_ELEVATED**:GPR = 184.2(>p95;2026-03 曾 329.7 ≈ p99)。

實際效果(煙霧測試 + brief 驗證):權重 40/30/20/10 → **35/30/15/20**;
deep-kill 袖上限 11% × 0.75 = **8.2%**;ONTO(台鏈,曝險 0.9)70.4 → 54.6 分
+ human_review;UNH(曝險 0.15)63.4 → 61.1 幾乎不動。張力狀態已回寫
[[01_macro_state]] §4c(universe.yaml 的 TSM 60% cap override 正式有了機器供值來源)。

## 5. 監控排程(接 [[07_sector_handoff]] §4 註冊表)

| 觸發器 | 引擎 | 頻率 |
|---|---|---|
| 世界事件(TS/GSCPI/GPR) | `regime/world_monitor`(SharksDNA-Morning 07:40,rally_dna 之前) | 日 |
| 事件閾值分位數重校 | 手動 `sharks world-monitor --dry-run` + 本頁更新 | 月 |
| 曝險名單 ↔ universe.yaml 對帳 | 人工(Risk Officer) | 月 |

## 6. 技術債 / 明確不做(外部草案的裁決)

1. **Mesa ABM 供應鏈模擬** — 延後:免費數據已給出可落地訊號;ABM 需先有曝險—營收
   的實證鏈才不是玩具。入庫條件:world 事件與個股報酬的前瞻相關性累積 ≥6 個月。
2. **LanceDB 遷移** — 不採:repo 已有 Chroma 決策(`docs/QLIB-VECTORDB-PLAN.md`,
   入庫條件案例 >150,現 60)。PIT 需求由 state 快照 + lake vintage + dated outputs 滿足;
   LanceDB time-travel 重評條件:案例庫破門檻**且**需要跨版本向量查詢時。
3. **Streamlit 世界儀表板** — 延後:brief(§2 全球風險區塊)先驗證讀者價值。
4. **GPRC_TWN 歷史 vintage 缺口** — 無解(來源限制);只能前向累積,文件已標注。
5. **曝險地圖是專家先驗** — 未用 10-K 地理營收驗證;Researcher 後續用
   `polygon_financials`(filing_date 錨)抽驗 taiwan_chain 名單的台灣營收占比。
6. **TARIFF/CYBER 手動旗** — 無免費機讀源;依 CLAUDE.md §5,D/E 級訊號不得自動觸發。

## See also

- [[06_rally_dna]] — 被本層調整的 DNA 匹配器(權重/分桶/sizing)
- [[07_sector_handoff]] — 觸發器註冊表模板
- [[01_macro_state]] §4c — 地緣張力狀態的 live 欄位
- [[../philosophy/09-point-in-time]] — vintage 紀律
- [[../philosophy/08-risk-and-position]] — cap 乘數仍受 Risk Officer 否決權管轄
- [[../philosophy/concepts/supply-chain-bottleneck]] — alpha 源框架(本層是它的風險鏡像)
