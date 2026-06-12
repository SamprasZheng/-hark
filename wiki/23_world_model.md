---
type: synthesis
tags: [world-model, geopolitical, supply-chain, gscpi, gpr, taiwan, dna-engine]
title: World Model — 全球供應鏈 + 地緣反身性感測層
as_of_timestamp: 2026-06-12T18:40:00+08:00
author_role: compiler
source_paths:
  - outputs/world-monitor-2026-06-12.json
  - outputs/abm-supply-chain-2026-06-12.json
  - config/world_events.json
  - config/world_exposure.json
  - src/sharks/regime/world_monitor.py
  - src/sharks/regime/abm_supply_chain.py
  - src/sharks/data/world_indicators.py
  - src/sharks/scoring/global_exposure.py
  - src/sharks/memory/case_store.py
  - wiki/24_exposure_validation.md
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

`config/world_exposure.json`(靜態、git 版控=PIT 安全;v2 經 [[24_exposure_validation]]
網證覆核):taiwan_chain 0.9(一階生產斷供)/ taiwan_demand_equipment 0.6(二階需求
遞延,不觸發 human_review)/ optics_cpo 0.7 / china_revenue 0.6,無命中退板塊底線
再退 default 0.25。
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

## 5. 監控排程(接 [[07_sector_handoff]] §4 註冊表;2026-06-12 全部自動化落定)

| 觸發器 | 引擎 | 頻率 |
|---|---|---|
| 世界事件(TS/GSCPI/GPR) | `regime/world_monitor`(SharksDNA-Morning 07:40,rally_dna 之前) | 日 |
| ABM 供應鏈情境 | `regime/abm_supply_chain`(morning gated:週二 TPE=美股週一收盤後) | 週 |
| 案例庫向量 sync | `memory/case_store.sync_from_outputs`(morning,rally_dna 之後) | 日 |
| 事件閾值分位數重校 | `world_monitor.recalibrate` → `outputs/world-thresholds-suggest-*`(morning gated:每月 1 日;建議制,人工套用) | 月 |
| 曝險名單 ↔ universe.yaml 對帳 | 人工(Risk Officer)+ [[24_exposure_validation]] 更新 | 月 |

排程本體已 repo 版控:`scripts/install_dna_schedule.ps1`(冪等註冊
SharksDNA-Morning/PreOpen,2026-06-12 已執行替換 ad-hoc 任務)。

## 6. 技術債裁決(2026-06-12 全量衝刺後狀態)

1. **ABM 供應鏈模擬** — ✅ 已落地(`regime/abm_supply_chain`,純 Python+numpy 無 mesa;
   情境先驗依 GPRC_TWN 分位數分帶,首跑 extreme 帶:預期斷供 2.09 季、TS_HIGH 條件式
   deep-kill 折減 -4.73pp)。mesa 引入條件記錄於模組 mesa_note。
2. **向量案例庫** — ✅ 已落地(`memory/case_store`,Chroma/numpy 雙 backend;入庫條件
   實際已達:212 案例 > 150 門檻)。LanceDB 仍不採(PIT 由 state 快照 + lake vintage 滿足);
   重評條件:需要跨版本向量查詢時。rally_dna 的 brute-force Top3 保留,store 為持久化/
   檢索層(SMCI 近鄰交叉一致)。
3. **世界儀表板** — ✅ 已落地(`ui/server` `/api/world` + 🌍 卡片;Starlette 版,
   streamlit 維持不動)。
4. **GPRC_TWN 歷史 vintage 缺口** — 無解(來源限制);只能前向累積,文件已標注。
5. **曝險地圖驗證** — ✅ 人工網證已做([[24_exposure_validation]]:SIVEF 蘇格蘭廠移出
   台鏈、設備商拆出二階群組 0.6、新增 AAPL/ASX/UMC → config v2)。仍開:10-K 地理營收
   的機器驗證(`polygon_financials` filing_date 錨)、china_revenue 其餘 10 檔證據、
   ANET 組裝地驗證。
6. **TARIFF/CYBER 手動旗** — 維持手動;無免費機讀源,D/E 級訊號不得自動觸發(CLAUDE.md §5)。

## See also

- [[06_rally_dna]] — 被本層調整的 DNA 匹配器(權重/分桶/sizing)
- [[07_sector_handoff]] — 觸發器註冊表模板
- [[01_macro_state]] §4c — 地緣張力狀態的 live 欄位
- [[../philosophy/09-point-in-time]] — vintage 紀律
- [[../philosophy/08-risk-and-position]] — cap 乘數仍受 Risk Officer 否決權管轄
- [[../philosophy/concepts/supply-chain-bottleneck]] — alpha 源框架(本層是它的風險鏡像)
