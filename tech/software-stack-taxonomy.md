---
type: synthesis
domain: method
tags: [software-taxonomy, ai-stack, value-capture, layered-stack, transmission-lag, classification, hardware-analogy]
as_of_timestamp: 2026-05-31T06:00:00+08:00
author_role: researcher
sources_grade_summary: "A: 8  B: 6  C: 3  D: 0  E: 0"
---
# 軟體 / AI 軟體供應鏈分層法 — 用硬體腦袋分類軟體 / Software-Stack Taxonomy for a Hardware Engineer

## 0. 一句話 + 分層表 / One-liner + the stack table
**把軟體當成一條「算力供應鏈」：跟你拆 晶片→元件→載板→PCB→散熱 一樣，軟體也是 L0 矽→L1 雲→L2 數據基建→L3 模型→L4 中介層→L5 橫向 SaaS→L6 垂直 SaaS 的七層堆疊。錢從上面(應用需求)拉、貨從下面(算力)推;但 2026 年的關鍵事實是——資本(capex)已大量灌到 L0/L1,營收與毛利卻塞在最底(NVDA 75% 毛利)與最頂(SaaS 75–85% 毛利)兩端,中間 L1/L3 反而被折舊與降價壓毛利。** 這是「微笑曲線」的軟體版,也是 principal 要的 lead-lag。

| 層 | 名稱 | 硬體類比 | 代表毛利 | 護城河型態 | 代表美股 | AI:吃 or 捕獲 |
|---|---|---|---|---|---|---|
| **L0** | 矽/算力 GPU·ASIC·HBM | 晶片本體 | ~75% (NVDA) [1] | 製程+CUDA 生態 | NVDA AMD AVGO MRVL MU | **捕獲**(賣鏟核心) |
| **L1** | 雲/IaaS + neocloud | 載板+電源(供電承載) | 60–70% 雲;neocloud 薄 | 規模+轉移成本 | MSFT AMZN GOOGL ORCL CRWV NBIS | 捕獲,但折舊吃毛利 |
| **L2** | 數據與基建 DB·向量·可觀測·網路軟體 | PCB+被動元件(走線/連結) | **73–81%** [4][5] | 數據重力+整合鎖定 | SNOW MDB DDOG NET CFLT ESTC | 捕獲(AI 放量用量) |
| **L3** | 模型層 基礎模型/API | 散熱/封裝(把算力變可用功) | 推理被砍 1000× [11] | RL數據飛輪(易輪動) | (多為私有)MSFT/GOOGL 代理曝險 | **既捕獲又被商品化** |
| **L4** | 編排/代理/開發工具/中介層 | 散熱模組+介面 | 兩極(轉售薄/平台厚) | 開發者表面+分發 | MSFT(GitHub) 私有:Cursor | 捕獲靠分發,wrapper 脆弱 |
| **L5** | 橫向應用 SaaS | 整機通用件 | **75–85%** [7][10] | 分發+系統紀錄鎖定 | CRM NOW ADBE HUBS | 分化:厚者捕獲薄者被吃 |
| **L6** | 垂直/產業 SaaS | 客製化整機 | 75–83% [9] | 產業數據+法規鎖定 | VEEV TOST PCOR SSNC | 最抗 AI(數據+合規) |

## 1. 逐層拆解 / Layer-by-layer
**L0 矽/算力**(類比:晶片本體)。AI 軟體的「原料矽」。經濟性最強:NVDA FY26Q4 GAAP 毛利 **75.0%**、Data Center 營收創高 **$62.3B(+75% YoY)** [1, A, primary-fetched];代工 TSMC 2025 全年毛利 **59.9%**(Q4 62.3%)[2, A]。護城河=製程+CUDA 生態,轉移成本極高、耐久性高。**AI read:賣鏟者核心,結構性捕獲**——但與 [[memory-supercycle]] 同調:HBM「毛利 5×」是假,漲價是供給紀律。

**L1 雲/IaaS + neocloud**(類比:載板+電源——承載並供電給矽)。2025 全球雲基建營收 **$419B**,Q4 單季 $119.1B、YoY+30%,連九季加速 [3, B, cross-confirmed]。三巨頭市占 AWS 28%/Azure 14%(Google 21%)[3]。傳統雲毛利約 60–70%、轉移成本高(資料出口費=鎖定)。**Neocloud(CRWV/NBIS/IREN)是新物種**:2025 全產業營收 >$25B、Q4 $9B(+223% YoY);CoreWeave 2025 約 $5.13B、backlog $66.8B [13, B]。但 neocloud 是**高資本密度、薄毛利的「GPU 房東」**,本質更像 REIT 而非軟體——這是分類陷阱(見 §6)。

**L2 數據與基建**(類比:PCB+被動元件——決定訊號怎麼走、元件怎麼連)。資料庫、向量庫、資料管線、可觀測性(observability)、網路軟體。經濟性是**全棧最甜的之一**:Snowflake FY26 product 毛利 75%(營收 $4.47B,+29%)[4, A]、MongoDB FY26Q4 73% GAAP/75% non-GAAP(訂閱 +27%)[5, A]、Datadog LTM 毛利 81%(2025 營收 $3.43B,+27.7%)[6, B]。護城河=**數據重力**(資料一旦進來就不搬)+整合鎖定。**AI read:淨捕獲**——模型要吞資料、agent 要記憶/檢索,L2 用量隨 AI 放大;2026 估值上「data infrastructure 領先所有 SaaS 類別」[8, C]。

**L3 模型層**(類比:散熱/封裝——把生矽算力轉成可用的「功」)。基礎模型/API。**矛盾層**:既捕獲(企業 GenAI 支出 $37B、其中 LLM API $8.4B、Anthropic $30B run-rate 反超 OpenAI——詳見 [[model-leadership-and-data]])又被商品化(達 GPT-4 級推理成本 2022 的 ~$20→2026 的 ~$0.40 /百萬 token,**約 1000× 崩跌**)[11, A]。護城河=RL 數據飛輪,但 18 個月內贏家輪動(OpenAI 企業市占腰斬)。**多數前沿模型廠私有**——listed 曝險只能透過 L1/L4 的 MSFT/GOOGL 間接持有。

**L4 編排/代理/開發工具/中介層**(類比:散熱模組+對外介面)。Agent 框架、orchestration、IDE、開發工具。經濟兩極化:**平台型厚**(MSFT 靠 GitHub/M365 分發),**轉售型薄**(Cursor 0→$2B ARR 卻在個人開發者上負毛利,Copilot 2026/6 改 token 計費因 flat-seat 經濟破裂)——完整拆解見 [[ai-coding-agents]]。**AI read:價值歸分發,wrapper 結構脆弱。**

**L5 橫向應用 SaaS**(類比:通用整機)。CRM/HR/協作等跨產業工具。毛利 75–85%(NOW 訂閱 non-GAAP ~83.5%、2026 指引 82%)[7, B];典型 pure-play SaaS >75%、>80% 才有營運槓桿信心 [10, B]。**AI 分化**:薄、單一功能、座位即產品者被吃(Chegg −99%);厚、有系統紀錄+分發者捕獲(CRM Agentforce、NOW Now Assist)——這是 [[ai-eats-software]] 的核心,**本頁不重複**,只定位其在堆疊中的層級。

**L6 垂直/產業 SaaS**(類比:客製化整機)。VEEV(生科 $2.45B)、TOST(餐飲)、PCOR(營建,GAAP 毛利 79%/non-GAAP 83%)、SSNC [9, B]。**全棧最抗 AI 的一層**:護城河=產業專屬數據+法規/合規鎖定,NRR 常 108–150%(vs B2B 中位 106%)[9]。垂直 SaaS 已佔 2025 Q3 SaaS M&A 的 54% [9]。**AI read:最難被通用 LLM 取代**(LLM 沒有你的合規工作流)。

## 2. 傳導與時滯 / Transmission & lag
**雙向,但 2026 是「資本由上而下承諾、貨由下而上交付、營收回填最慢」的失衡態。**
- **向下拉(需求側,慢):** 應用/agent 需求 → 燒 token → 拉 L3 推理 → 拉 L1 算力租用 → 拉 L0 GPU/HBM。Uber 的 Claude Code 採用 32%→84%、4 個月燒光年度 AI 預算,就是這條鏈的微觀證據([[ai-coding-agents]])。
- **向上推(資本側,快但前置):** Hyperscaler 2026 capex 合計約 **$700B(≈2025 的兩倍)**:AMZN $200B、GOOGL $175–185B、Meta $125–145B、MSFT $110–120B [12, B, cross-confirmed]。Capex 已佔其營收約 1/3,**超過 dotcom 高峰(~32%)** [14, B]。
- **時滯(principal 要的 lead-lag):** **L0 先吃到錢(即時,NVDA 已實現),L1 折舊滯後且侵蝕毛利(折舊年規從 3 年拉到 5 年),L3–L6 的營收回填要 2–3 年** [14, C]。產業折舊已約 **$400B/年,將超過四大合計 2025 利潤** [14, C]。換言之:**capex 修正領先營收修正**——這正是 hedge fund 的「capex fatigue」與 [[ai-eats-software]] §7 的 MIT NANDA「95% 試點無 ROI」同一個 air-pocket。

## 3. 價值在哪層累積 / Where value accrues
**軟體版「微笑曲線」:兩端高、中間被擠。**
- **最穩定捕獲:L0(賣鏟,75% 毛利、已實現)** 與 **L6/厚 L5(75–85% 毛利+數據/法規鎖定)**。
- **被擠的中段:L1**(neocloud 薄毛利+折舊)與 **L3**(推理 1000× 降價商品化)——這兩層「需求最大但定價權最弱」。
- **L2 是隱藏甜點**:75–81% 毛利、數據重力鎖定、AI 放大用量,卻不像 L0 那樣被「泡沫」標籤掃到。
- **錢流真相:capex(L0/L1)→ 折舊(L1 承擔)→ 應用營收(L5/L6 回填,滯後 2–3 年)。** 早期紅利全在 L0;中期(2026–28)勝負看 L5/L6 營收能否追上 L0 已收的 capex。

## 4. 30 秒分類法 / Classify any software ticker in 30 seconds
1. **它賣什麼?** 賣晶片/HBM=L0;賣租用算力(IaaS/GPU房東)=L1;賣資料庫/管線/監控/網路軟體=L2;賣模型/API=L3;賣 agent 框架/IDE/開發工具=L4;賣跨產業工具=L5;賣單一產業工具=L6。
2. **毛利落點?** 70–75% 且重資產→L0/L1;75–85% 輕資產→L2/L5/L6。**毛利 <60% 的「軟體」八成是偽裝的硬體/房東(neocloud)**,別當 SaaS 估值。
3. **護城河問一句:** 「換掉它要搬什麼?」搬不動的是**數據(L2/L6)**或**分發/系統紀錄(L5/L4-MSFT)**=捕獲方;只是「一層 UI+一個功能」=會被 AI 吃的薄 SaaS([[ai-eats-software]])。
4. **AI 對它是順風還逆風?** AI 放大其用量(L0/L2/算力)=順;AI 直接產出它賣的答案(Q&A、翻譯、薄工具)=逆。

## 5. 整合到 $hark / Integration
- **層級 = 新標籤,不是新評分。** 在 `src/sharks/scoring/tech_dd.py` 的 `TECH_DD` registry 為每個 node 加一個 **`stack_layer ∈ {L0..L6}`** annotation 欄位,與既有 `dd_verdict`/`dd_sleeve`/`milestone_score` 並列(**仍 observe-first,不進 `final_fom`**,遵守 [[fom-integration]] §3 已驗證的 DD-TILT-NEUTRAL 結論)。
- **層級 × bubble_guard 做集中度視圖:** 把現有 71 個 US node 按 L0–L6 分桶,讓 Risk Officer 一眼看出**書本是否過度壓在「微笑曲線中段」(L1/L3,定價權最弱)**——這是 capex-fatigue 風險的可投資翻譯。
- **lead-lag 餵 `HORIZON_PROFILES`:** L0=即時(3m 透鏡)、L1 折舊=滯後、L5/L6 回填=12–36m;與 §2 時滯對齊,讓 `fom_3m/12m/36m` 反映「錢先到哪層」。
- **連結而非重複:** 本頁是**分類骨架**;單層贏家輸家辯論交給 [[ai-eats-software]](L5/L6)、[[model-leadership-and-data]](L3)、[[ai-coding-agents]](L4)、[[memory-supercycle]](L0)。更新 [[index]] 與 [[00_framework]] 的 method 區塊各加一行指向本頁。

## 6. 同溫層風險 / 陷阱 / Echo-chamber traps
1. **把 neocloud 當高毛利 SaaS。** CRWV/NBIS 是**高 capex、薄毛利的 GPU 房東(類 REIT)**,backlog≠毛利。用 L5 的 SaaS 倍數套 L1 房東=最大估值錯位。
2. **以為「AI=軟體股全崩」。** 錯;是 L5 薄層被吃,L0/L2/L6 反而捕獲。整體軟體支出 2026 仍 +15.1% 到 $1.44T([[ai-eats-software]])。
3. **把 capex 當營收。** $700B capex 是**承諾/支出**,不是已實現回報;營收滯後 2–3 年、折舊先吃毛利 [14]。capex 修正會領先營收修正——別把鏟子訂單外推成終端獲利。
4. **重複計算「AI 受惠」。** 同一筆 AI 需求會被 L0/L1/L2/L3/L5 各說一次「我受惠」;堆疊視圖的用途就是**避免把一塊餅當五塊**——錢只在少數層真正落袋(§3)。
5. **模型層當成可投資純玩。** L3 多為私有且商品化(1000× 降價),listed 純模型曝險稀少;追「模型贏家」常踩 [[model-leadership-and-data]] 的三榜分裂陷阱。

## Sources
1. NVIDIA Q4 FY26 8-K (75.0% GAAP GM; DC $62.3B +75% YoY) — https://www.sec.gov/Archives/edgar/data/0001045810/000104581026000019/q4fy26cfocommentary.htm — retrieved 2026-05-31 — grade A — primary-fetched
2. TSMC 2025 record profit / 59.9% FY GM (Focus Taiwan) — https://focustaiwan.tw/business/202601150011 — retrieved 2026-05-31 — grade A — cross-confirmed
3. Synergy via DCD — cloud infra $419B 2025, Q4 $119.1B +30%, AWS 28%/Azure 14% — https://www.datacenterdynamics.com/en/news/synergy-enterprise-cloud-infrastructure-spend-jumps-12bn-in-q4-2025/ — retrieved 2026-05-31 — grade B — cross-confirmed
4. Snowflake FY26 (product rev $4.47B +29%, 75% non-GAAP product GM) — https://www.insidermonkey.com/blog/snowflake-snow-fy2026-revenue-hits-1-28b-as-product-revenue-rises-30-in-q4-1716845/ — retrieved 2026-05-31 — grade A — cross-confirmed
5. MongoDB FY26Q4 8-K (73% GAAP / 75% non-GAAP GM; sub rev +27%) — https://www.sec.gov/Archives/edgar/data/0001441816/000162828026013199/mdb-13126xex991xrelease.htm — retrieved 2026-05-31 — grade A — primary-fetched
6. Datadog FY25 ($3.43B rev +27.7%, LTM GM 81%) — https://www.tikr.com/blog/datadog-vs-snowflake-which-cloud-data-stock-is-the-better-growth-play — retrieved 2026-05-31 — grade B — single-source-pending
7. ServiceNow FY25 subscription GM ~83.5% non-GAAP, 2026 guide 82% (gurufocus/StockStory) — https://www.gurufocus.com/term/grossmargin/NOW/Gross%2BMargin/ServiceNow+Inc — retrieved 2026-05-31 — grade B — single-source-pending
8. Public software valuation multiples May 2026 (data-infra highest) — https://multiples.vc/insights/software-saas-valuation-multiples — retrieved 2026-05-31 — grade C — single-source-pending
9. Vertical SaaS metrics (Procore 79%/83% GM; Veeva $2.45B; NRR 108–150%; 54% of M&A) — https://tech-insider.org/the-rise-of-vertical-saas-why-industry-specific-software-is-winning/ — retrieved 2026-05-31 — grade B — cross-confirmed
10. SaaS gross-margin / Rule-of-40 benchmarks (>75% expected, 80% tipping point) — https://saasdb.app/learn/financials/gross-margin/ — retrieved 2026-05-31 — grade B — cross-confirmed
11. Inference cost ~1000× collapse 2022→2026 ($20→$0.40 /M tokens); H100 cloud −64% — https://www.liontrust.com/insights/blogs/2026/04/ai-revenue-evidence-pricing-dynamics-and-outlook — retrieved 2026-05-31 — grade A — cross-confirmed
12. Hyperscaler 2026 capex ~$700B (AMZN $200B/GOOGL $175–185B/Meta $125–145B/MSFT $110–120B) — https://finance.yahoo.com/news/big-tech-set-to-spend-650-billion-in-2026-as-ai-investments-soar-163907630.html — retrieved 2026-05-31 — grade B — cross-confirmed
13. Neocloud 2025 >$25B / Q4 $9B +223%; CoreWeave $5.13B, backlog $66.8B — https://www.tradingkey.com/analysis/stocks/us-stocks/251300415-coreweave-nebius-earnings-tradingkey — retrieved 2026-05-31 — grade B — cross-confirmed
14. Capex-monetization gap / $400B/yr depreciation > 2025 profits / 3→5yr depreciation / 2–3yr revenue lag — https://hedgeco.net/news/05/2026/ai-capex-fatigue-why-hedge-funds-are-questioning-the-hyperscaler-spending-boom.html — retrieved 2026-05-31 — grade C — single-source-pending
15. Palantir FY25 GM 82% GAAP / 84% ex-SBC (L5/L6 reference) — https://valueinvesting.io/PLTR/metric/gross-margin — retrieved 2026-05-31 — grade B — cross-confirmed
16. AI eats software (cross-link, L5/L6 winners-losers; software spend +15.1% to $1.44T) — [[ai-eats-software]] — retrieved 2026-05-31 — grade A — cross-confirmed
17. Enterprise GenAI $37B / LLM API $8.4B / Anthropic $30B run-rate (cross-link) — [[model-leadership-and-data]] — retrieved 2026-05-31 — grade B — cross-confirmed
