---
type: index
domain: tech-trend
tags: [index, moc, tech-trends]
as_of_timestamp: 2026-05-31T01:15:00+08:00
author_role: researcher
status: live
---

# tech/ — 科技趨勢盡職調查 / Tech-Trend Due-Diligence

The technology due-diligence layer of `$hark`. Each page screens one hot narrative for **質變 vs 同溫層** (real qualitative change vs echo chamber), scored on the [[00_framework]] rubric, hunting the bear case and the investable chokepoint. Sits upstream of the investment layer; **research/educational only — not buy/sell advice.**

## Navigation

- [[semiconductor-industry-map]] — **半導體/電子產業全圖** (垂直價值鏈 12 關卡 × 水平分段;edge↔cloud 連結縫;把所有頁掛上母圖) — the backbone MOC
- [[00_framework]] — the 質變-vs-同溫層 rubric (5 axes), anti-echo-chamber doctrine, verdict taxonomy
- [[scoreboard]] — scored matrix of all trends + verdicts + echo-chamber-gap/falsifier table
- [[99_cross_synthesis]] — cross-trend 綜效 lattice, culture→supply-chain map, consolidated chokepoints, master read
- [[cross-validation-quant]] — verdicts × `bubble_guard` × evidence-gate reconciliation (DD ↔ quant agreement)
- [[_weekly-watch]] — **weekly milestone tracker** (記錄→每周更新→里程碑是否完成) · [[_sourcing-protocol]] — 考證 discipline · [[fom-integration]] — verdict → FOM sleeve routing
- [[alpha-transmission-framework]] — **流動性傳導與未發現 alpha 框架** (lead-lag + early-attention + seasonality, NOT momentum-chasing). Inputs: [[software-stack-taxonomy]] · [[rotation-spillover-algos]] · [[social-attention-alpha]] · [[liquidity-concentration-flows]]. Code: `regime/lead_lag.py` · `regime/sector_flow.py` (broadening/spillover) · `scoring/attention_radar.py`
- [[bayesian-bottleneck-engine]] — **貝葉斯瓶頸引擎**: Serenity 的貝氏邏輯形式化 (prior=DD rubric · posterior=milestone LR 更新 · edge=posterior−market-implied · 序貫輪動=全概率). Code: `scoring/bayesian_update.py`

## Trend pages (Phase A — 2026-05-31)

| Trend | 判決 | Σ/10 | One-line |
|---|---|:--:|---|
| [[model-leadership-and-data]] | 結構 | 9 | 三套排行榜各說各話；純模型層幾乎不可投資，曝險在算力/記憶體與 coding |
| [[youth-culture-shifts]] | 結構 | 9 | 外送/社群/AI-native 是真質變(有財報)；戒酒/「AI殺搜尋」被敘事誇大 |
| [[memory-supercycle]] | 結構 | 9 | AI 缺貨其實是供給紀律；"HBM 毛利 5×" 是假；股價跑在基本面前 |
| [[ai-pharma-glp1]] | 結構* | 9 | GLP-1=已實現現金流(近質變)；AI 製藥=被當現金流定價的未實現選擇權 |
| [[autonomous-driving]] | 結構 | 8 | 純視覺是較便宜非較強；Waymo(hybrid)安全數據領先；雨天弱點真實 |
| [[ai-eats-software]] | 結構 | 8 | 是刀不是洪水；薄 SaaS 被吃(Chegg −99%)，但整體軟體支出 +15% |
| [[optical-interconnect-cpo]] | 結構 | 8 | CPO 殺 pluggable/長銅纜，但載板反增；瓶頸在 InP 基板+CW 雷射 |
| [[ai-edge-devices]] | 過熱 | 7 | AI PC 是行銷外殼；換機真因是 Win10 EOL；毛利歸記憶體 |
| [[quantum-vs-bitcoin]] | 太早 | 7 | 105 物理量子位元 vs 需 ~13M；Q-Day ~2033；BTC 可先 soft-fork |

\* composite: GLP-1 = 結構→質變 (0.85); AI-drug-discovery = 太早→結構 (0.60).

## Phase B trend pages (multi-horizon T0→T3)

| Trend | headline | T0 → T3 | One-line |
|---|---|---|---|
| [[ai-coding-agents]] | 結構 | 質變→open | Claude Code vs Codex：模型廠+通路贏，Cursor wrapper 負毛利脆弱 |
| [[ar-vr-smart-glasses]] | 結構 | 結構→質變(條件) | Ray-Ban 靠放棄 AR 才贏；真 AR 撞 etendue 物理 T2+ |
| [[luxury-and-apparel]] | 結構(分化) | 過熱出清→結構 | 非崩盤是品牌離散；Hermès 複利 vs Gucci −19%；Nike 分批抄底 |
| [[ip-economy-collectibles]] | 結構 | 過熱→質變 | POPMART：護城河是造星流水線非單一 Labubu；抄底 Disney 飛輪 |
| [[defense-tech]] | 結構 | 結構→質變 | 歐洲重整=NOW；軟體吃國防=T2-T3；受益者≠該價位(PLTR>85×) |
| [[satcom-future]] | 結構 | 結構→太早 | Starlink 已質變但已定價；D2C 物理封頂=補盲；台灣上游 |

## Phase C trend pages (multi-horizon T0→T3)

| Trend | headline | T0 → T3 | One-line |
|---|---|---|---|
| [[ai-datacenter-power]] | 結構 | 結構→質變→太早 | AI 電力瓶頸；電氣/核能 IPP 真實 P&L，froth 在 pre-rev SMR(OKLO/SMR/NNE) |
| [[china-ai-stack]] | 結構 | 結構→質變→質變 | 分流已是事實；開源中國贏，算力靠 TSMC die-bank+外購 HBM 撐到~2026末 |
| [[cybersecurity-ai]] | 結構 | 結構→質變→結構 | AI-PROOF(攻擊面擴大)，是 ai-eats-software 的反面；agentic SOC=T1-T2；PQC 2027 |
| [[stablecoins-tokenization]] | 結構 | 結構→過熱→太早 | 穩定幣結算是真質變；CRCL 是利率敏感單因子賭注；"全部代幣化"過頭 |
| [[space-economy]] | 結構 | 結構→質變→太早 | 發射成本崩跌是真質變(SpaceX 壟斷)；在軌經濟太早；RKLB ~90x P/S |
| [[humanoid-robotics]] | 結構 | 太早→質變 | 像 2019 的自駕；買鏟子(NVDA+減速機)，OEM 進 Moonshot；中國贏單位戰 |

## Phase D trend pages (multi-horizon T0→T3)

| Trend | headline | T0 → T3 | One-line |
|---|---|---|---|
| [[rf-connectivity]] | 結構 | 結構→質變(2029+) | RF=方向相反的 anti-bubble(基本面被忽略非敘事超前);手機前端便宜但結構受挑戰,成長已遷徙到 AI 電力縫/週期類比/國防 GaN/6G FR3;變數#15 急單訊號已確認(走工業門非手機門);擁瓶頸 KEYS/GFS |
| [[offshore-energy]] | 結構 | 結構→質變→太早 | 能源實體層 gap-fill;真瓶頸(無新造船+整併)但 phase-one 末段、2026 消化氣穴;日租金近端 <$40 萬滾降、稼動率滑向 82%;抄底 RIG/NE,鏟子 BKR(LNG) |
| [[copper-electrification]] | 結構 | 過熱→質變 | 物理資源層 gap-fill;需求(AI/電網/EV)+ 精礦瓶頸(TC=$0、Grasberg −35%)真實,**但變數#5 的 LME 庫存訊號已倒轉**(回補+contango=關稅搬倉假訊號);價格 ~20% 高於 Goldman fair value;對的資源、錯的價格 |

## Deep dives (二階供應鏈 / second-derivative)

- [[optical-supply-chain-deep]] — CPO picks-and-shovels: InP 基板 · CW 雷射/EML · **hybrid-bond 量測 (Auros/Onto/FormFactor) = 最未擁擠節點**；froth: AXTI/AEHR (−95)
- [[glp1-supply-chain]] — GLP-1 製造瓶頸: 胜肽 API (Bachem/PolyPeptide) · fill-finish (TMO) · 注射筆 (Ypsomed)；**去中介風險**: LLY/NVO 自建產能 + 口服 orforglipron 砍掉胜肽/針劑需求
- [[rf-deep-dives]] — RF 二階深掘:**QRVO+SWKS 合併套利**(監管賠率賭注,SAMR 是搖擺,R/R ~3:1–10:1 對你不利)+ **GFS vs TSEM**(TSEM 純但已定價、GFS 風險調整後更乾淨)

## Master conclusion (see [[99_cross_synthesis]] §5)

> 沒有一條評到頁面層級「質變」。熱門題目幾乎全是 **結構**（真實但已被定價），外加兩個陷阱（端側 AI **過熱**、量子破 BTC **太早**）。唯一最接近「有現金流的質變」是 **GLP-1**。可投資的 alpha 在「定價權瓶頸」與尚未擁擠的「二階節點」(InP 基板 / HBM 量測 / CDMO)。整體最大風險：**股價同時跑在記憶體、CPO、模型層、軟體贏家的基本面之前**——與 [[../wiki/07_ai_bubble_audit]] 晚週期論點一致。

## Schema

These pages follow the `$hark` constitution ([[../CLAUDE]]): point-in-time `as_of_timestamp`, A–E source grading, `author_role: researcher`, clinical/falsifiable tone, `[[wikilink]]` internal refs. Verdicts feed [[../philosophy/05-decision-rubric]] under the usual caps and the [[../philosophy/concepts/evidence-gated-rebalance]] 十足的證據 gate.
