---
type: synthesis
tags: [sector-handoff, ai-monetization, crypto, space, falsifiable-triggers]
title: 2026-27 板塊接棒推演 — 可證偽觸發器(非預言)
as_of_timestamp: 2026-06-12T16:00:00+08:00
author_role: compiler
source_paths:
  - wiki/06_rally_dna.md
  - outputs/reflexivity-2026-06-10.json
confidence: 0.55
---

# 板塊接棒推演(2026-27)— 觸發器不是預言

## 觸發器狀態(2026-06-12,principal 供數,grade C 待 A 級源覆核)

| 觸發器 | 狀態 | 讀數 |
|---|---|---|
| AI CapEx 指引 | 🟢 未觸發修正 | 2026 ~$650-700B,仍上修/高位,無 >10% 下修 |
| BTC ETF 淨流 | 🔴 接棒未確認 | 6 月單週 **-$1.67B**,累計多週淨流出 |
| SPCX 機構建倉 | ⏳ 觀察中 | 上市後 13F/Inst Trans 待數據 |
| 防禦斷裂擴散到科技核心 | 🟢 未擴散 | 斷裂仍集中防禦股(reflexivity 06-10 掃描) |

**2026/6 總結判斷**(principal + 系統一致):主旋律回饋鏈健康、mania 態持續但近高位
→ **維持偏多 + 動態 sizing + 降溫警報減碼**;防禦輪動晚段確認,HUM 多重警訊看擴散。

> 原則:接棒成立與否由**資金數據**裁決,敘事不算數([[../tech/00_framework]] 反同溫層
> 紀律)。每條推演掛可證偽觸發器,由現有引擎監控,不另造輪子。

## 1. AI 硬體 → 變現驗收期(主旋律的內部交接)

2022-25 主升段 = 算力底層(GPU/HBM/CPO)。2026-27 資金開始驗收**變現能力**。
- **看多延續觸發**:軟體/應用層營收增速 > 硬體層(用 `fundamentals.scan` 的
  IGV 成分 vs 半導體成分 rev_yoy 差);CapEx 指引不下修([[02_mag7_bottleneck]])。
- **修正觸發**:Mag7 CapEx 指引下修 >10% / [[06_rally_dna]] §9 markov 態轉 crisis /
  reflexivity 斷裂警告擴散到 AI 硬體核心(現在斷裂集中在防禦股 — 尚未擴散)。
- 光通訊 CPO(SIVEF/LITE/COHR 持倉相關):觸發點營收仍衰退、買的是前瞻拐點
  (§8)— **下一次財報季 = 拐點驗收**,營收不翻正且 backlog 不增 = DNA 失效訊號。

## 2. 加密貨幣接棒 — 機構資本實質流入才算數

- **接棒成立觸發**:(a) crypto 題材池(basecross scope `crypto`)rally streak≥2 密度
  連續 4 週上升;(b) BTC ETF 淨流入轉正且擴大(grade A 數據);(c) Web3 基建協議
  (JAM/Coretime/DePIN 類)出現**傳統機構**級資本配置公告(≥2 個 A 級源)。
- **證偽**:BTC 維持 $60k 下 base-building 但題材池 streak 密度不升 = 只有投機資金,
  不是接棒。現狀(06-12):BTC 跌破 $60k 後盤整,**接棒未確認**。

## 3. 太空接棒 — 低軌通訊 + 射頻陣列商業化

- **接棒成立觸發**:space 題材池(RDW/RKLB/ASTS/LUNR)streak 密度 + SpaceX IPO(6/12
  SPCX 上市)後 30 天**機構建倉數據**(13F/Finviz Inst Trans 轉正);射頻/高頻寬供應鏈
  營收拐點(`hotspot_backtest` 板塊預測進前三)。
- 持倉相關:P2 已有 RDW(太空)— 論點部位已在,加碼等觸發。
- **證偽**:SPCX 上市後太空代理股「利好出盡」回落 >30% 且機構流出 = 此輪是 IPO 炒作。

## 4. 監控排程(全部接現有引擎)

| 觸發器 | 引擎 | 頻率 |
|---|---|---|
| markov 態(mania/crisis) | `rally_dna.regime_markov4` | 月 |
| 反身性斷裂擴散 | `scoring.reflexivity` | 週 |
| 題材池 streak 密度 | `/rally` × scope(crypto/space) | 週 |
| 板塊輪動預測 | `hotspot_backtest` | 月 |
| 錯殺候選 | DNA broad 觸發 + `detect_flips` | 月 |
| 世界事件(台海/GSCPI/GPR;2026-06-12 加入) | `regime/world_monitor` → [[23_world_model]] | 日 |
