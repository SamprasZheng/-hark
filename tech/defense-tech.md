---
type: synthesis
domain: tech-trend
tags: [defense-tech, software-defined-warfare, autonomy, drones, counter-uas, golden-dome, europe-rearmament, primes, attritable-mass]
phase: B
as_of: 2026-05-31T02:30:00+08:00
author_role: researcher
confidence: 0.78
verdict: 結構
verdict_by_horizon: {T0: 結構, T1: 結構, T2: 質變, T3: 質變}
rubric: {A1: 2, A2: 2, A3: 2, A4: 1, A5: 1}
sources_grade_summary: "A: 9 B: 7 C: 3 D: 0 E: 0"
cross_interact: [satcom-future, model-leadership-and-data, autonomous-driving, quantum-vs-bitcoin]
---
# 國防科技 — AI×自主×太空 的結構轉折 / Defense Tech: The AI×Autonomy×Space Inflection

## 0. 判決 + Desk View / Verdict
**結構 (structural, conf 0.78)** — 但要拆成兩條獨立曲線。**(A) 歐洲再武裝是「現在進行式的結構」**：NATO 在 2025-06 海牙峰會承諾 2035 年前 5% GDP（3.5% 核心 + 1.5% 廣義），訂單已經實打實落地——Rheinmetall FY2025 backlog €63.8B、指引 2026 backlog 翻倍到 €135B [Rheinmetall FY2025 — rheinmetall.com — retrieved 2026-05-31 — grade A — primary-fetched]。**(B) 「軟體吃國防 / 可消耗自主大量化」是 T1–T3 的質變**：Palantir Q1 2026 營收 +85% YoY、Anduril 估值一年內從 $30.5B → $61B，但 DoD Replicator 在 2025-08 只交付「數百」而非「數千」套，烏克蘭一年卻造 ~240 萬架 FPV——**真正的 attritable mass 不在矽谷，在第聶伯河**。Desk view：歐洲 primes（RHM/Hensoldt/Renk）是**已確認**的結構性受益、現金流可見度最高；Palantir/Anduril 是**正確方向但估值已先行透支**（PLTR 遠期 P/S >85x）；美國 primes 不是被「殺死」而是被「邊際稀釋」——backlog 仍在創高（RTX $251B），但 attritable 浪潮把估值天花板從它們身上移走。**最大盲點**：同溫層把「Palantir/Anduril = 未來」當信仰，卻忽略採購制度（不是技術）才是瓶頸，且這兩檔的勝利已被定價。

## 1. 技術底蘊 / Technical moat (A1) — software-defined warfare
三條技術主軸正在重寫「戰力 = 平台」的舊公式。**(1) 軟體定義戰爭**：Palantir 的 AIP / Maven Smart System、Anduril 的 **Lattice OS**（開放式 C2，把異質感測器+自主系統整合成單一指管層）——軟體成為跨平台的「作業系統」，硬體退化為可替換節點 [Anduril Series H / Lattice Army battle-manager — TechCrunch — retrieved 2026-05-31 — grade B — primary-fetched]。**(2) 自主/AI 瞄準**：CCA（協同作戰飛機）從 exquisite 有人機外溢到無人僚機——USAF 選定 General Atomics YFQ-42A + Anduril **YFQ-44A**；USMC 選 Northrop+Kratos **MQ-58 Valkyrie**（OTA 初始 $231.5M，2029 入列）[Northrop/Kratos USMC CCA — TheAviationist — retrieved 2026-05-31 — grade B — cross-confirmed]。**(3) 無人機蜂群 + counter-UAS**：Replicator 第二線（Replicator 2）轉向反小型無人機（C-sUAS），呼應烏克蘭「development→combat-test→modify」週期以「週/月」計，而西方傳統採購以「年」計 [Ukraine drone lessons — OSW — retrieved 2026-05-31 — grade B]。**A1=2**：技術底蘊真實且可投資，但「軟體層」moat（資料+整合）與「攬子+量產」moat 是兩種不同護城河，且開源化（Lattice 開放）反而削弱單一鎖定。

## 2. 需求數據 / Demand reality (A2) — budgets & backlog（標 Q/FY）
| 指標 metric | 數值 value | 期間 period | 來源 source (grade — verification) |
|---|---|---|---|
| NATO 防衛承諾 | 5% GDP by 2035 (3.5%核心+1.5%廣義) | 2025-06 海牙峰會 | NATO official text (A — primary-fetched) |
| Rheinmetall backlog | **€63.8B** (FY24: €46.9B) | FY2025 | rheinmetall.com (A — primary) |
| Rheinmetall 2026 指引 | 營收 €14.0–14.5B (+40–45%); backlog→~€135B | FY2026 guidance | rheinmetall.com (A — primary) |
| Hensoldt order backlog | €9.80B (+41% YoY) | Q1 2026 | Hensoldt PR (A — primary) |
| Renk order backlog | €6.68B (營收 €1.37B, +19.8%) | FY2025 | Capital.com / Renk (B) |
| Saab order backlog | SEK 274B (訂單入帳 SEK ~138B) | FY2025 | Saab year-end (A — primary) |
| RTX backlog | **$251B** | Q1 2026 | Globe&Mail / RTX (B) |
| Lockheed (LMT) backlog | $186.4B | Q1 2026 | sci-tech-today / LMT (B) |
| Northrop (NOC) backlog | $95.6B | Q1 2026 (3/31) | NOC 8-K (A — primary) |
| Palantir 營收 | **$1.633B (+85% YoY)**；政府 $687M (+84%)、美商業 $595M (+133%) | Q1 2026 | Palantir 8-K / Businesswire (A — primary) |
| Palantir FY2026 指引 | $7.65–7.66B (+71% YoY) | FY2026 guidance | Businesswire (A — primary) |
| AeroVironment (AVAV) 營收 | $408M；funded backlog $1.1B；bookings $2.1B | Q3 FY2026 | AVAV 8-K (A — primary) |
| 烏克蘭 FPV 採購 | **~240萬架** (計畫 2026 ~800萬) | 2025 全年 | Kyiv Independent / RNBO (B) |

**A2=2**：需求是真實預算+已簽 backlog，不是 projection。歐洲 backlog 普遍 book-to-bill >1.5x；Palantir 美商業 +133% 證明「軟體吃國防」外溢到企業端。注意：backlog 是天花板/可見度，非已認列營收——Rheinmetall €135B 是**指引上限**，CCA 的 $231.5M 是**OTA 上限非已交付**。

## 3. 資金與權威 / Capital & authority (A3)
**民間資本暴衝**：Anduril Series H **$5B @ $61B**（2026-05-13，Thrive+a16z 領投；2025 營收倍增至 **$2.2B**；累計募資 >$11B）[Anduril — TechCrunch — grade B — primary-fetched]。Saronic（自主艦艇）Series D **$1.75B @ $9.25B**（2026-03-31，Kleiner Perkins 領投），興建 Port Alpha 新世代造船廠 [Saronic — PRNewswire — grade B — cross-confirmed]。**政府權威**：Golden Dome 經 FY2025 reconciliation（OBBBA, P.L.119-21）撥 **$24.4B**，FY2026 計畫再 obligate ~$20.5B；官方總估 $185B，但 CBO 估完整建置達 **$1.2T** [Golden Dome — Wikipedia/SpaceNews/Defense One — grade B — cross-confirmed]。Anduril 已切入 Golden Dome 太空攔截層、AVAV 完成 **$4.1B** 併購 BlueHalo（2025-05-01，跨足太空+網電）[AVAV/BlueHalo — GovConWire — grade B]。**A3=2**：資金與權威雙重背書（私募+國會撥款+DoD 合約）齊備，是這個 cluster 最硬的證據。

## 4. 受益 / 受損 / 抄底 / Beneficiaries (A4)
- **結構受益（已確認）**：**歐洲 primes**——Rheinmetall（陸戰彈藥/裝甲，backlog 翻倍）、Hensoldt（國防電子/感測，book-to-bill 1.5–2.0x）、Renk（傳動，backlog €6.68B）、Saab（防空/Gripen，SEK 274B）。現金流可見度最高、被「再武裝」這個結構直接驅動。
- **方向對但估值透支**：**Palantir（PLTR）**——基本面無可挑剔（+85% YoY、調整營益率 60%），但遠期 P/S >85x、遠期 P/E ~108x，已把數年成長定價 [PLTR valuation — GuruFocus/AInvest — grade C]。**Anduril**（未上市，$61B；IPO watch）同理：估值年增一倍，本身已是「未來已定價」。
- **被邊際稀釋（非被殺，de-rate 風險）**：**美國 primes（LMT/RTX/NOC/GD/L3Harris）**——backlog 仍創高（RTX $251B），但 attritable/軟體浪潮把「成長溢價」從它們身上移走，估值更像公用事業而非成長股。能否**adapt**？NOC/Kratos 做 Valkyrie、LMT 投自主——有適應動作，但組織慣性大。**抄底邏輯**：若 de-rate 過頭（殖利率回升+backlog 可見度仍在），美國 primes 是「現金流防禦性抄底」而非成長抄底。
- **受損/value trap 警示**：純靠單一 exquisite 平台、無自主/軟體轉型的次級承包商；以及把「contract-award ceiling」當營收的高估值小型股。**A4=1**：節點清楚，但最性感的兩檔（PLTR/Anduril）估值已先行，純 primes 又缺成長溢價——可投資性被「估值 vs 確定性」的剪刀差壓抑。

## 5. 多時程 / Multi-horizon
- **T0（now）結構**：歐洲再武裝已落地——backlog、預算、book-to-bill 全部 >1，這是**現在式**不是預測。
- **T1（1–3y）結構**：Replicator 2（C-sUAS）+ CCA 原型試飛 + Anduril/Palantir 合約放量；attritable 從「PPT」走向「小量產」。
- **T2（3–5y）質變**：CCA 入列（USMC 2029）、Golden Dome 太空層初始能力、軟體 C2 成為跨軍種標準——「平台中心」正式讓位「軟體+可消耗節點中心」。
- **T3（5–10y）質變**：AI×太空×自主×國防四向收斂；攬子有人平台數量見頂，戰力由「軟體更新速度 + 量產 attritable」決定。**裁決：結構（T0–T1）→ 質變（T2–T3）。**

## 6. 爆發條件 + 里程碑階梯 / Milestone ladder
1. **NATO 各國國防預算法案通過**（不只承諾）。how-to-verify：各國 2027 budget 是否寫入 3.5% 路徑 + NATO 年度 report。status：承諾已立（2025-06），國家立法**進行中**。next check：2026 各國秋季預算季。
2. **Replicator 實際 fielding 數字**（數百→數千）。verify：CRS / DefenseScoop 更新交付數。status：2025-08 僅「數百」(未達標)。next check：2026-08 一年後檢視 + FY26 obligation。
3. **Anduril/Palantir 合約放量 + Anduril IPO**。verify：DoD 合約公告、Anduril S-1。status：Lattice 拿下 Army battle-manager + Golden Dome 太空層；IPO 未定。next check：每季 DoD 大單 + IPO 申報。
4. **Golden Dome 資金真正撥付+架構定案**。verify：FY26 obligation 執行率、MDA 架構文件。status：$24.4B(FY25)+~$20.5B(FY26) 已撥但「怎麼花」國會仍質疑。next check：FY27 預算請求。
5. **歐洲國防法案落地**（EU ReArm / 各國採購）。verify：歐盟/德國採購合約。status：Rheinmetall 指引 backlog 翻倍即落地證據。next check：RHM/Hensoldt 下兩季 order intake。
6. **CCA 程序里程碑**（YFQ-44A/MQ-58 試飛→入列）。verify：USAF/USMC 試飛公告。status：原型階段，USMC 2029 入列目標。next check：2026 試飛節點。

## 7. 時代影響與交互 / Era-impact & synergies
這是 **AI×太空×自主×國防** 的四向收斂：戰力公式從「誰有最貴的平台」變成「誰的軟體更新最快 + 誰能最便宜地大量消耗」。烏克蘭證明了 attritable mass 的戰略價值，但也暴露**西方瓶頸是採購制度不是技術**——DOT-Chain Defence 讓旅級直接下單 FPV，週期以週計，這才是真正的顛覆。Cross-interact：
- [[satcom-future]] — Golden Dome 太空攔截層 + 戰場通訊高度依賴 LEO 星座；太空成為國防新戰域。
- [[model-leadership-and-data]] — Lattice/AIP 的 AI 瞄準與自主決策直接吃模型能力；軍用 world-model 是下一個前沿。
- [[autonomous-driving]] — 自主導航/感測融合 stack 與無人機/無人艦同源（同樣的 edge 推論 + 感測融合問題）。
- [[quantum-vs-bitcoin]] — PQC（後量子密碼）是國防通訊/指管的下一個必要升級向量。

## 8. 同溫層 + 自我打臉 / Echo-chamber + self-rebuttal
**同溫層 gap**：X/retail 把「Palantir/Anduril = 國防未來」當信仰，但 (1) 這兩檔的勝利**已被定價**（PLTR >85x P/S，Anduril 一年估值翻倍）——買對方向 ≠ 買對價格；(2) 真正的 attritable mass 不在矽谷而在烏克蘭，瓶頸是**採購制度**不是技術，而制度改革慢且不可投資；(3) 「美國 primes 被殺死」是誇張——backlog 仍創高（RTX $251B），它們是被**de-rate**不是被取代。**自我打臉（打我自己的 bull case）**：(a) 歐洲 5% GDP 是 2035 目標+2029 才檢討，政治意願可能在 backlog 認列前就退潮（西班牙已豁免）；(b) Golden Dome 官方 $185B vs CBO $1.2T 的巨大缺口意味多數錢「還沒撥、怎麼花國會也不知道」——別把 announce 當 booked；(c) Replicator 連「數千」都做不到，說明 DoD 把 attritable 規模化的執行力存疑，新創訂單可能 contract-award ceiling 遠大於 booked revenue；(d) Palantir 若估值回歸 20x，市值可跌 80%——基本面對但下檔風險巨大；(e) 歐洲 backlog 翻倍指引本身是 guidance（天花板），book-to-bill 可能在產能瓶頸下無法全數轉化。**淨判決維持結構，但把「軟體/attritable 受益者」與「其股價」嚴格分開——前者確定，後者已透支。**

## Sources
1. NATO Hague Summit Declaration & 5% commitment — https://www.nato.int/en/what-we-do/introduction-to-nato/defence-expenditures-and-natos-5-commitment — retrieved 2026-05-31 — grade A — primary-fetched
2. Rheinmetall FY2025 annual report (backlog €63.8B, 2026 guidance) — https://www.rheinmetall.com/en/media/news-watch/news/2026/03/2026-03-11-rheinmetall-presents-annual-report-for-2025 — retrieved 2026-05-31 — grade A — primary-fetched
3. Hensoldt FY2025 / Q1 2026 record order intake (backlog €9.80B) — https://www.hensoldt.net/news/hensoldt-starts-financial-year-2026-with-record-order-intake-and-rising-profitability — retrieved 2026-05-31 — grade A — primary-fetched
4. Saab year-end report 2025 (backlog SEK 274B) — https://www.saab.com/newsroom/press-releases/2026/saab-year-end-report-2025record-order-bookings---building-for-growth — retrieved 2026-05-31 — grade A — primary-fetched
5. Renk FY2025 (backlog €6.68B) — https://capital.com/en-int/market-updates/renk-group-stock-forecast-10-04-2026 — retrieved 2026-05-31 — grade B — cross-confirmed
6. Palantir Q1 2026 8-K / press release (rev $1.633B +85%) — https://www.businesswire.com/news/home/20260503338048/en/ — retrieved 2026-05-31 — grade A — primary-fetched
7. Northrop Grumman FY2025/Q1 2026 8-K (backlog $95.6B) — https://www.sec.gov/Archives/edgar/data/0001133421/000113342126000002/noc-12312025xearningsrelea.htm — retrieved 2026-05-31 — grade A — cross-confirmed
8. RTX / Lockheed Q1 2026 backlog ($251B / $186.4B) — https://www.theglobeandmail.com/investing/markets/stocks/RTX/pressreleases/1649544/ — retrieved 2026-05-31 — grade B — cross-confirmed
9. Anduril Series H $5B @ $61B (rev $2.2B 2025) — https://techcrunch.com/2026/05/13/anduril-raises-5b-doubles-valuation-to-61b/ — retrieved 2026-05-31 — grade B — primary-fetched
10. Saronic Series D $1.75B @ $9.25B (Port Alpha) — https://www.prnewswire.com/news-releases/saronic-closes-1-75b-series-d-at-9-25b-valua[redacted-acct]98.html — retrieved 2026-05-31 — grade B — cross-confirmed
11. AeroVironment Q3 FY2026 8-K (rev $408M, backlog $1.1B) — https://www.sec.gov/Archives/edgar/data/1368622/000110465926042388/tm2611632d1_ex99-1.htm — retrieved 2026-05-31 — grade A — cross-confirmed
12. AeroVironment $4.1B BlueHalo acquisition close — https://www.govconwire.com/articles/aerovironment-closes-bluehalo-acquisition — retrieved 2026-05-31 — grade B — cross-confirmed
13. Golden Dome funding ($24.4B FY25, $185B est, CBO $1.2T) — https://www.defenseone.com/defense-systems/2026/05/golden-dome-cost-trillion-cbo/413485/ — retrieved 2026-05-31 — grade B — cross-confirmed
14. Golden Dome FY26 appropriations / Space Force $26B — https://spacenews.com/defense-appropriations-bill-for-2026-funds-space-force-at-26-billion-presses-pentagon-on-golden-dome/ — retrieved 2026-05-31 — grade B — cross-confirmed
15. DoD Replicator status (hundreds not thousands by Aug 2025) — https://defensescoop.com/2025/09/03/dod-replicator-drone-tech-transition-fielding-questions-linger/ — retrieved 2026-05-31 — grade B — cross-confirmed
16. CRS Replicator background — https://www.congress.gov/crs-product/IF12611 — retrieved 2026-05-31 — grade A — cross-confirmed
17. Northrop/Kratos USMC MQ-58 Valkyrie CCA ($231.5M OTA) — https://theaviationist.com/2026/01/08/northrop-grumman-kratos-xq-58-valkyrie-cca-usmc/ — retrieved 2026-05-31 — grade B — cross-confirmed
18. Ukraine ~2.4M FPV drones 2025 — https://kyivindependent.com/ukraine-on-track-to-receive-total-of-3-million-fpv-drones-in-2025/ — retrieved 2026-05-31 — grade B — cross-confirmed
19. Ukraine drone production/procurement lessons — https://www.osw.waw.pl/en/publikacje/osw-commentary/2025-10-14/game-drones-production-and-use-ukrainian-battlefield-unmanned — retrieved 2026-05-31 — grade B — single-source-pending
20. Palantir valuation (forward P/S >85x, P/E ~108x) — https://www.gurufocus.com/term/forward-pe-ratio/PLTR — retrieved 2026-05-31 — grade C — single-source-pending

