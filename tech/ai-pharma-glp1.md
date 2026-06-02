---
type: synthesis
domain: tech-trend
tags: [ai-drug-discovery, glp1, obesity, fda, alphafold, pharma]
as_of_timestamp: 2026-05-31T01:15:00+08:00
author_role: researcher
confidence: 0.74
verdict: 結構
rubric: {A1: 2, A2: 2, A3: 2, A4: 2, A5: 1}
sources_grade_summary: "A: 6 B: 7 C: 3 D: 1 E: 0"
---
# AI 製藥 vs GLP-1 減肥藥：兩條被混為一談的曲線 / AI Drug Discovery vs GLP-1: Two Curves the Narrative Conflates

## 0. 一句話判決 / Verdict
- **Thread 1 — AI drug discovery + FDA gate: 太早偏結構 (太早→結構過渡), conf 0.6.** AI 已壓縮臨床前（標靶ID、結構、苗頭化合物），且 2025 出現「首個全 AI 設計分子」Phase IIa 陽性讀數 [12]；但 AI 至今**沒有證明能提高臨床成功率**——BCG 樣本顯示 AI 分子 Phase 1 成功率 80–90%，Phase 2 即跌回產業平均 ~40% [11]，且 0 個 AI-discovered 新分子實體獲 FDA 核准上市 [10]。資金與權威背書是真的（Isomorphic $3B 藥廠合約 [1][2]），但收入仍是里程碑款而非藥品銷售。
- **Thread 2 — GLP-1 obesity: 結構性質變 (確定結構，逼近質變), conf 0.85.** 這是當下生技最硬的需求曲線：LLY 單季 Mounjaro $8.7B(+125%, 全球)、Zepbound(US) $4.1B(+79%)、總營收 $19.8B(+56%) [4][5]；口服 orforglipron(Foundayo) 2026/4 獲 FDA 核准、ATTAIN-1 12.4% 減重 [7][8]；NVO 口服 Wegovy 首季 130 萬張處方 [6]。需求、收入、權威(FDA labels)、供應鏈全部對齊。
- **Combined: 結構 (structural), conf 0.74.** 兩主題都「真」，但驅動力不同：GLP-1 是已實現的現金流引擎；AI 製藥是真實但未兌現的選擇權。「AI+GLP-1」的綜效在今天**主要是敘事黏貼**（見 §5、§7）。

## 1. 技術底蘊 / Technical moat (A1) — 2/2
AlphaFold2/3 把蛋白結構預測準確度推到 ~90%(1Å backbone)，AlphaFold3(redacted) 進一步預測蛋白與 DNA/RNA/配體/離子的複合體 [9]；Hassabis 與 Jumper 因此獲 2024 諾貝爾化學獎，與蛋白設計的 David Baker 共享 [13]——這是**權威等級**的技術背書，不是行銷詞。護城河在於專有資料規模：Recursion 宣稱 >23PB 生物/化學資料、3 兆基因-化合物關係 [3]。但關鍵限制：AI 強在「設計能結合標靶的分子」，弱在「預測該分子在人體是否安全有效」——後者正是 Phase II/III 與 FDA 的閘門 [11]。

## 2. 需求真實性 — 數據 / Demand reality (A2) — 2/2
| 指標 | 數值 | 日期 | 來源(grade) |
|---|---|---|---|
| LLY Mounjaro 季營收 | $8.7B (+125% YoY) | Q1 2026 | [4]B [5]A |
| LLY Zepbound 季營收(US) | $4.1B (+79% YoY) | Q1 2026 | [4]B [5]A |
| LLY 總營收 / 2026 指引 | $19.8B (+56%); 指引上調至 $82–85B | Q1 2026 | [5]B |
| NVO 口服 Wegovy 首季 | 1.3M 處方 / DKK2.26B(~$354M) | Q1 2026 | [6]B |
| NVO 注射 Wegovy | DKK18.2B (+12% YoY) | Q1 2026 | [6]B |
| orforglipron ATTAIN-1 減重 | 12.4% (~27.3 lbs) @72wk | 2025 | [8]A |
| GLP-1 用量 YoY 增幅 (Gen Z 15–28歲) | +67.8% | 2023→2024 | [15]C |
| SDGR 藥物探索收入 | $22.9M(vs $10.2M YoY)，惟軟體 -21% | Q1 2026 | [14]B |
| AI 分子 Phase 2 成功率 | ~40%（≈產業平均） | 2024 study | [11]B |

GLP-1 側：處方、營收、處方量增速全部可驗證且加速。AI 側：唯一可量化的「需求」是藥廠付的里程碑款與軟體 ACV——SDGR 軟體收入甚至 YoY 衰退 21% [14]，顯示企業端對 AI 探索工具的付費意願尚未爆發。

## 3. 資金與權威背書 / Capital & authority (A3) — 2/2
- Isomorphic Labs(DeepMind 分拆)：與 Lilly($45M 預付/$1.7B 里程碑) 及 Novartis($37.5M/$1.2B) 合約合計近 $3B；2025/3 由 Thrive Capital 領投募 $600M；目標 2026 下半年首個臨床候選 [1][2]。
- NVIDIA BioNeMo：對 Recursion $50M PIPE + DGX Cloud；Recursion 全合作里程碑/預付累計 >$500M [3]。
- 權威面：FDA 已核准 orforglipron(Foundayo, 2026/4) 與口服 Wegovy(2025/12)；CagriSema NDA 審查中，預計 2026 底決定 [6][7]。AI 側的權威里程碑是 Nature Medicine 刊登 Insilico Phase IIa [12] + 2024 諾獎 [13]——但**沒有一個 FDA 藥品核准是「AI-discovered」**。

## 4. 供應鏈與可投資節點 / Supply chain & investable nodes (A4) — 2/2
- **LLY / NVO**：GLP-1 雙寡頭，現金流引擎；風險是頭對頭數據（Zepbound 勝 CagriSema [clinicaltrialsarena]）與口服世代的市佔重分配。
- **CDMO/Catalent、筆型注射器/auto-injector 供應商**：產能即護城河；503B 複方禁令(redacted) 把灰色市場 $150–300/月 的供給擠回品牌藥(>$1000/月) [16][17]，需求回流正規供應鏈。
- **RXRX / SDGR**：AI 探索平台，目前是「賣鏟子+自有管線選擇權」，估值靠敘事而非藥品收入 [14][3]。
- **NVDA**：BioNeMo 是 AI-bio 的算力收費站，但對 NVDA 整體營收占比微小，屬主題曝險非核心 [3]。
- 投資性排序：GLP-1 製造端(LLY/NVO/CDMO) 可投資性 > AI 平台(RXRX/SDGR 偏選擇權)。

## 5. 大模型 vs 小模型 / Model angle — 相關
這是 [[model-leadership-and-data]] 的延伸：蛋白結構/設計模型(AlphaFold3、RoseTTAFold、ESM、Recursion Phenom、Schrödinger 物理基礎模型 + AI co-scientist "Bunsen" [14]) 是**領域專用模型**，不是通用 LLM。價值在「lab-in-the-loop」：模型生成假設→濕實驗驗證→回饋訓練。但**直接回答綜效問題**：GLP-1 類(incretin/amylin) 多為胜肽，過去靠藥物化學迭代而非 AI 從頭設計；orforglipron 是非胜肽小分子但由 Chugai/Lilly 傳統發現。目前無公開證據顯示主流 GLP-1 資產由 AI 平台發現——「AI 加速代謝藥物發現」在今天是**前瞻假設**，非已實現事實。

## 6. 顛覆 / 取代向量 / Disruption vector (A5) — 1/2
GLP-1 的顛覆是**確定且廣譜**：減重外延伸至 MASH、睡眠呼吸中止、CKD、心血管終點，正重塑製藥最大單一品類（Mounjaro 預計 2030 前後超越 Keytruda 成第一大藥 [drugdiscoverytrends]）。AI 製藥的顛覆向量**真實但未證實**：它縮短臨床前時程(Recursion 標靶ID→IND <18 月 [GEN])，理論上把 e2e 成功率從 5–10% 拉到 9–18% [11]——但這仍是早期、小樣本推估，Phase II 牆尚未被打破。給 A5=1 因為「壓縮成本」已發生、「提高臨床成功率（真顛覆）」尚未被資料證實。

## 7. 同溫層風險 + 空方論點 / Echo-chamber flags + bear case
- **最大同溫層缺口（Thread 1）**：散戶把「AI 設計分子」等同於「AI 會做出更好的藥」。事實：AI 今天**只壓縮臨床前**；AI 分子 Phase 1 看似亮眼(80–90%)，但這多反映「best-in-class 模仿已驗證標靶」的低風險選擇，到 Phase 2 即回落產業平均 ~40% [11]；**FDA 至今 0 個 AI-discovered 新分子實體核准上市** [10]。Recursion 2025 砍掉 ≥4–5 個管線(REC-2282/994/3964)、股價單日 -13% [GEN][biopharmadive]；Exscientia 多個 AI 設計分子(EXS-21546、Sumitomo OCD 標的)臨床失敗或被棄 [drugtargetreview]。SDGR 軟體收入 YoY -21% [14]。空方一句話：**AI 製藥目前是「便宜的臨床前」+「昂貴的選擇權」，不是「更高的臨床勝率」。**
- **Thread 2 空方**：(a) Goldman 已將 GLP-1 2030 TAM 從 $130B 下修至 $95B（美國 $70B），理由是訂價壓力、Medicare 不確定、續用率 [18]；(b) 續用率/停藥反彈是真實侵蝕；(c) 口服世代(orforglipron 12.4% < 注射 tirzepatide ~20%+) 效力較低，恐壓縮 ASP [7]；(d) CagriSema 頭對頭輸 Zepbound，NVO 競爭力受質疑 [clinicaltrialsarena]。
- **青年文化風險**：Gen Z 用量增速最猛(+67.8%)、37% 列入新年目標 [15]，但近 1/4 使用者無醫療指導 [19]——這是**美觀性 off-label 濫用**的監管/品牌風險，亦是 [[youth-culture-shifts]] 的鉤子（減肥藥成社群身分符號）。

## 8. 跨主題綜效 / Cross-synergies
- [[model-leadership-and-data]]：蛋白/結構基礎模型 + 2024 諾貝爾化學獎，是「資料護城河 > 模型」論點的最佳生技範例。
- [[youth-culture-shifts]]：GLP-1 在 Gen Z/年輕族群的美觀性採用（TikTok 化、37% 新年目標 [15]）是消費行為質變鉤子。
- [[ai-eats-software]]：SDGR「軟體授權→hosted + AI co-scientist」轉型，是 AI 重寫 SaaS 商業模式的縮影 [14]。

## Sources
1. Fortune — Isomorphic Labs first human trials — https://fortune.com/2025/07/06/deepmind-isomorphic-labs-cure-all-diseases-ai-now-first-human-trials/ — retrieved 2026-05-31 — grade B
2. ClinicalTrialsArena — Isomorphic prepares trials for AI-designed drugs — https://www.clinicaltrialsarena.com/news/isomorphic-labs-prepares-trials-ai-designed-drugs/ — retrieved 2026-05-31 — grade B
3. FierceBiotech — Recursion $50M NVIDIA collab / BioNeMo — https://www.fiercebiotech.com/medtech/recursion-lines-50m-nvidia-collab-ai-powered-drug-discovery — retrieved 2026-05-31 — grade B
4. Pharmaceutical Technology — Eli Lilly lifts 2026 guidance, Q1 2026 — https://www.pharmaceutical-technology.com/news/eli-lilly-lifts-2026-revenue-guidance-as-q1-marks-dominant-opening/ — retrieved 2026-05-31 — grade B
5. Eli Lilly 8-K Q1 2026 sales & earnings (SEC) — https://www.sec.gov/Archives/edgar/data/0000059478/000005947826000043/q126lillysalesandearningsp.htm — retrieved 2026-05-31 — grade A
6. CNBC — Novo Nordisk Q1 2026 earnings, Wegovy pill — https://www.cnbc.com/2026/05/06/wegovy-glp1-weight-loss-novo-nordisk-earnings-stock-nvo-ozempic.html — retrieved 2026-05-31 — grade B
7. Eli Lilly IR — FDA approves Foundayo (orforglipron) — https://investor.lilly.com/news-releases/news-release-details/fda-approves-lillys-foundayotm-orforglipron-only-glp-1-pill — retrieved 2026-05-31 — grade A
8. Eli Lilly IR — orforglipron ATTAIN-1 complete results (NEJM) — https://lilly.gcs-web.com/news-releases/news-release-details/lillys-oral-glp-1-orforglipron-demonstrated-meaningful-weight — retrieved 2026-05-31 — grade A
9. Nature — Chemistry Nobel to AlphaFold developers (AF3 capabilities) — https://www.nature.com/articles/d41586-024-03214-7 — retrieved 2026-05-31 — grade A
10. Fortune — race to first AI-discovered drug to market (none approved yet) — https://fortune.com/2025/04/03/recursion-pharmaceuticals-ai-drug-discovery/ — retrieved 2026-05-31 — grade B
11. ResearchGate/BCG — How successful are AI-discovered drugs in clinical trials (Phase1 80-90%, Phase2 ~40%) — https://www.researchgate.net/publication/380223979_How_successful_are_AI-discovered_drugs_in_clinical_trials_A_first_analysis_and_emerging_lessons — retrieved 2026-05-31 — grade B
12. PRNewswire/Insilico — Nature Medicine Phase IIa Rentosertib (ISM001-055) IPF — https://www.prnewswire.com/news-releases/insilico-medicine-announces-nature-medicine-publication-of-phase-iia-results-evaluating-rentosertib-the-novel-tnik-inhibitor-for-idiopathic-pulmonary-fibrosis-ipf-discovered-and-designed-with-a-pioneering-ai-appr[redacted-acct]70.html — retrieved 2026-05-31 — grade A
13. GEN — Baker, Hassabis, Jumper 2024 Nobel Prize in Chemistry — https://www.genengnews.com/topics/artificial-intelligence/baker-hassabis-jumper-awarded-nobel-prize-in-chemistry-for-protein-design-and-structure-prediction/ — retrieved 2026-05-31 — grade B
14. Motley Fool — Schrödinger (SDGR) Q1 2026 earnings transcript — https://www.fool.com/earnings/call-transcripts/2026/05/05/schrodinger-sdgr-q1-2026-earnings-transcript/ — retrieved 2026-05-31 — grade C
15. WRAL — GLP-1 use growing fastest among younger groups (Evernorth) — https://www.wral.com/lifestyle/health/glp-1-use-increase-youth-2025-study-finds/ — retrieved 2026-05-31 — grade C
16. Pharmacy Times — FDA moves to permanently close compounded GLP-1s — https://www.pharmacytimes.com/view/fda-moves-to-permanently-close-the-door-on-compounded-glp-1s — retrieved 2026-05-31 — grade B
17. FDA — proposes to exclude semaglutide/tirzepatide/liraglutide from 503B bulks list — https://www.fda.gov/news-events/press-announcements/fda-proposes-exclude-semaglutide-tirzepatide-and-liraglutide-503b-bulks-list — retrieved 2026-05-31 — grade A
18. Goldman Sachs — anti-obesity market may be smaller than expected ($95B 2030) — https://www.goldmansachs.com/insights/articles/the-anti-obesity-drug-market-may-prove-smaller-than-expected — retrieved 2026-05-31 — grade B
19. Dermatology Times — survey: rise in GLP-1 patients seeking cosmetic care / unsupervised use — https://www.dermatologytimes.com/view/new-survey-reveals-rise-in-glp-1-patients-seeking-cosmetic-care — retrieved 2026-05-31 — grade C

