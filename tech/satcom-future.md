---
type: synthesis
domain: tech-trend
tags: [satcom, direct-to-device, d2c, starlink, leo, ast-spacemobile, kuiper, geo-incumbents, spectrum]
as_of_timestamp: 2026-05-31T02:30:00+08:00
author_role: researcher
confidence: 0.78
verdict: 結構
rubric: {A1: 2, A2: 2, A3: 2, A4: 1, A5: 1}
sources_grade_summary: "A: 8 B: 5 C: 2 D: 0 E: 0"
phase: B
---
# 衛星通訊的未來 — Starlink 結構勝、D2C 物理瓶頸、GEO 拆解中 / Satcom Future: Starlink Structural, D2C Physics-Capped, GEO Being Dismantled

## 0. 一句話判決 + Desk view
**結構 (structural, conf 0.78).** Starlink 的 LEO 寬頻已是「現在進行式的結構性質變」——2025 年營收 $11.4B、營業利益 $4.4B(SpaceX 唯一的利潤中心),2026/2 已破 1,000 萬用戶 [Sacra SpaceX — sacra.com — retrieved 2026-05-31 — grade C — cross-confirmed][Starlink 10.3M subs Q1 2026 — Wikipedia/SpaceX — retrieved 2026-05-31 — grade B]。但本主題的真正裁決在三條獨立軸線:(1) **寬頻 = 結構、已大致 priced-in**(SpaceX 私募估值已 ~$1.25T,2026 IPO 喊 $1.75T);(2) **D2C(直連手機)= 物理受限的真實需求,T1–T2 才成 mass-market**;(3) **GEO 在位者正在被「拆零件」變現**——EchoStar 把頻譜賣給 SpaceX/AT&T(合計 ~$42B),Amazon $11.57B 收購 Globalstar。Desk view(謹慎):這不是「衛星打敗地面」的故事,而是**頻譜(MSS/低頻)正在被重新定價成 D2C 的稀缺資產**;真正贏家是握有頻譜+發射成本+規模的 SpaceX,以及若能融資完成星座的 ASTS。「D2C 取代基地台」在 2026 仍屬**太早**。

## 1. 技術底蘊 (A1) — ENGINEER-GRADE:D2C 物理、頻譜、LEO vs GEO
D2C 的核心是一條極端不對稱的 link budget:從 ~550 km LEO 對一支**未改裝手機**收發,而手機上行功率被 FCC 與電池硬性限制在 **< 0.25 W**,距離由軌道力學固定——「再多軟體優化也跨不過」[Direct-to-cell link budget — KeepTrack — retrieved 2026-05-31 — grade C]。閉合鏈路只剩兩條路:**衛星端做超大相位陣列**(提高 G/T 與 EIRP),或**犧牲吞吐**。兩家路線正好對照:
- **Starlink DTC**:每顆衛星約 **25 m²** 蜂巢陣列,借 **T-Mobile 中頻 PCS** 直打標準手機;現實吞吐目前是「數百 kbps/beam」級,夠簡訊/email、不夠串流;次世代喊到 150 Mbps 目標 [SpaceX 150Mbps target — Tesery — retrieved 2026-05-31 — grade C]。
- **ASTS BlueBird Block 2**:單星陣列達 **~223 m²(≈2,400 sq ft)**——LEO 史上最大商用相位陣列,較 Block 1 大 3.5×、容量 10×,設計速率達 **120 Mbps**,目標電壓是「用 MNO 自家低頻授權頻譜做寬頻級 D2C」[ASTS BlueBird 6 largest array — SatNews — retrieved 2026-05-31 — grade B][Next-Gen BlueBird 120 Mbps — ast-science.com — retrieved 2026-05-31 — grade A]。

物理結論:**陣列面積≈容量**。Doppler(LEO 相對速度 ~7.5 km/s 造成數十 kHz 頻偏)與每 beam 容量上限,使 D2C 在可見未來都是**補盲/低速**為主,而非取代地面寬頻。**LEO vs GEO**:GEO 單跳延遲 ~600 ms、固定波束,適合廣播/海事航空;LEO 延遲 20–40 ms、可動態指向但需數百~數千顆 + 光學星間鏈路。**A1=2**——D2C 是真實且難複製的工程躍遷(超大可展開陣列 + 頻譜 + 發射),但物理天花板也真實。

## 2. 需求數據 (A2)
| 指標 metric | 數值 value | 期間 period | 來源 (grade — verification) |
|---|---|---|---|
| Starlink 用戶 | 10.3M(160+ 國) | 2026-03-31 | Wikipedia/SpaceX (B — cross-confirmed) |
| Starlink 營收 | $11.4B | FY2025 | Sacra (C — cross-confirmed w/ $11B 多源) |
| Starlink 營業利益 | $4.4B | FY2025 | Sacra (C — single-source-pending) |
| Starlink ARPU | $81/月(-18% vs 2023) | 2025 | The Information/Sacra (B) |
| Globalstar 營收(Apple 佔 66%) | $71.96M(+18% YoY) | Q1 2026 | GSAT 10-Q via StockTitan (B — primary-fetched) |
| ASTS 營收 | $14.7M | Q1 2026 | ASTS 8-K (A — primary-fetched) |
| ASTS 2026 全年 guidance | $150–200M | FY2026 | ASTS 8-K (A — primary-fetched) |
| Amazon Leo 在軌衛星 | 302 顆(production) | 2026-04 | Wikipedia/Orbital Radar (B) |

Starlink 是**已加速的 P&L**(月增曾達 2 萬戶/日,2025 寬頻營收 +48% 至 $11.4B);D2C 仍是 early revenue(ASTS Q1 僅 $14.7M,主要靠政府里程碑+閘道硬體;Globalstar 的「需求」其實 66% 是 Apple 一張包機合約)。**A2=2**——寬頻需求是 accelerating P&L;D2C 需求真實但量級小兩個數量級。

## 3. 資金·權威 (A3)
資金壓倒性:SpaceX 2025/7 估值 $400B → 2025/12 tender ~$800B → 2026/2 隨 xAI 交易 ~$1.25T,2026 IPO 目標 $1.75T(且 Starlink 留在母體內)[SpaceX $800B / 2026 IPO — Fortune — retrieved 2026-05-31 — grade B][SpaceX $1.75T IPO — Bloomberg — retrieved 2026-05-31 — grade B]。權威/監管面更關鍵:**FCC 已核准 SpaceMobile 商用 D2C(至多 248 顆)**[ASTS FCC commercial auth — ASTS 8-K — grade A];ASTS 綁定 AT&T(6 年延長)+ Verizon(2025/10 確定性商用協議)。最戲劇性的是**頻譜被資本重新定價**:EchoStar 2025/9 把 AWS-4+H-block 賣給 SpaceX ~$17B(現金 $8.5B + SpaceX 股票 $8.5B,另 SpaceX 代付 ~$2B 利息至 2027/11),再加 AWS-3 ~$2.6B;另把 3.45GHz+600MHz 賣給 AT&T ~$23B [EchoStar–SpaceX $17B — PRNewswire 2025-09-08 — grade A — primary-fetched]。**A3=2**——資金與監管權威壓倒性押注 LEO/D2C;頻譜成為被天價收購的標的本身就是最強背書。

## 4. 受益 / 受損 / 抄底 (A4)
- **受益(WINNERS)**:**SpaceX/Starlink**(現金牛 + 即將 IPO + 用頻譜換 EchoStar/AWS);**ASTS**(若能用 $3.5B 現金燒到 ~45 顆在軌的正現金流);供應鏈上游——台廠 LEO 上游(RF PA、濾波器、高頻 PCB)是 Starlink/Kuiper 雙鏈受益,見 [[../wiki/synthesis/leo-taiwan-odc-gap]] 與 [[../watchlist/serenity-supply-chain]]。
- **受損(LOSERS)**:**GEO 寬頻**結構性受壓;**EchoStar/DISH (SATS)** 已對「going concern」示警、實質靠賣頻譜續命——這是**價值實現而非經營翻身**(把資產拆給對手)。
- **抄底候選 vs 價值陷阱**:**Viasat (VSAT)** 是這組裡最像「真 turnaround」者——FY2026 創紀錄 backlog、FCF ~$600M、淨負債/EBITDA 朝 <3x、提前贖回 $442.6M 債,ViaSat-3 F3 已發射 [Viasat FY2026 8-K — SEC — grade A]。**Eutelsat (ETL.PA)** 屬「政府續命」型——法國政府持股升至 ~29.65%、$1.56B 增資 + €975M 出口信貸造 340 顆 OneWeb,但全球 LEO 服務可能延到 2026 底 [Eutelsat $1.56B — SpaceNews — grade B]:這是**國家戰略對沖 Starlink,不是純財務抄底**。**A4=1**——瓶頸清楚(頻譜、超大陣列、發射),但純標的稀少:SpaceX 未上市、ASTS 仍稀釋燒錢、GEO 在位者多為陷阱;最乾淨的 listed exposure 反而是台廠上游零組件。

## 5. 多時程 (T0–T3)
- **T0(現在)**:Starlink 寬頻 = **結構**(已 priced-in);D2C 簡訊/數據 = beta→早商用(T-Satellite 2025/7 商用簡訊、2025/10 加數據)。
- **T1(1–3y)**:D2C 走向 **mass-market 補盲**(ASTS 連續覆蓋、Verizon/AT&T 上線;Kuiper/Amazon Leo 2026 中商用 beta);SpaceX IPO 事件落地。
- **T2(3–5y)**:D2C **寬頻級**(Block 2 120 Mbps、Starlink 次世代);Amazon–Globalstar 2027 收尾後 Leo+D2D 整合。
- **T3(5–10y)**:「D2C 取代 rural tower」論點才可能局部成立——**現在說此論 = 太早**(物理容量/每 beam 上限未解)。

## 6. 爆發條件 + 里程碑階梯 (falsifiable)
1. **Starlink DTC 全功能商用(語音+數據,非 beta)**：how-to-verify = T-Mobile/Starlink 官網服務頁 + FCC 准照。status：簡訊+數據已商用、語音 beta(2025 末)。next check：每月查 t-mobile.com/coverage/satellite-phone-service。
2. **ASTS 達成「正營運現金流 + ~45 顆在軌」**：verify = ASTS 季度 8-K 現金流 + 在軌數。status：Q1 2026 在軌 BB6/7、現金 $3.5B、淨損 $191M。next check：Q2 2026 8-K(BB8/9/10 6 月發射後)。
3. **SpaceX/Starlink IPO 定價**：verify = S-1/交易所公告。status：2026 計畫、目標 $1.75T、Starlink 不分拆。next check：監看 S-1 申報。
4. **Amazon Leo 訂閱放量**：verify = Amazon 公告用戶/覆蓋國數(需 ≥578 顆初始覆蓋)。status：302 顆、2026/4 企業 beta。next check：2026 中商用 launch 公告。
5. **Amazon–Globalstar 交割**：verify = 反壟斷核准/closing PR。status：2026/4/14 簽署 $11.57B、預計 2027 closing。next check：HSR/FCC 進度。
6. **GEO 抄底證偽點**：verify = VSAT 淨負債/EBITDA 是否 <3x 且 ViaSat-3 F3 入服(2026/8–9)。status：FCC/SEC 在追。

## 7. 時代影響與交互
與 [[defense-tech]]:LEO/D2C 是主權通訊與戰場 resilient comms 的核心(EchoStar 頻譜流向、Starlink 軍用 Starshield),頻譜=國安資產。與 [[autonomous-driving]]:衛星補盲為 connected/自駕車提供 always-on 後援連線(但延遲/容量使其僅為 fallback,非主鏈)。與既有 yxz LEO/ODC wiki:本主題的「通訊星座」與 [[../wiki/synthesis/leo-taiwan-odc-gap]] 的「軌道資料中心(ODC)」共用同一條台廠上游(RF/濾波器/高頻 PCB)與發射/頻譜稀缺邏輯——頻譜與軌道位「先佔先贏」是兩者共同護城河。

## 8. 同溫層 + 自我打臉
**Echo-chamber gap**:多頭把「Starlink 用戶 10M + ASTS 大陣列」直接外推成「衛星即將取代電信」。數據打臉:Starlink ARPU **-18%**(規模換單價)、D2C 真實吞吐仍是數百 kbps 級、ASTS Q1 營收僅 $14.7M 且淨損 $191M、靠發債+稀釋(Q1 增發 ~1,300 萬股)續命。
**自我打臉(打我自己的空)**:我說 D2C「太早」——但 (a) FCC 已給 ASTS 商用准照、(b) Apple/AT&T/Verizon/Amazon 四大買單者同時下場、(c) EchoStar 把 ~$42B 頻譜變現給 SpaceX/AT&T 證明「頻譜稀缺」是真金白銀——這些都比我的「物理天花板」論更早地把 D2C 從敘事推進到合約。結論校正:**寬頻=結構(現在)、D2C 補盲=結構化中(T1)、D2C 寬頻取代=太早(T2–T3)**;最大未知是 ASTS 融資執行與 SpaceX IPO 後的資本行為。

## Sources
1. SpaceX/Starlink financials — https://sacra.com/c/spacex/ — retrieved 2026-05-31 — grade C (cross-confirmed: $11.4B FY2025 rev, $4.4B op profit, 10M+ subs)
2. Starlink subscribers 10.3M Q1 2026 — https://en.wikipedia.org/wiki/Starlink — retrieved 2026-05-31 — grade B
3. ASTS Q1 2026 8-K (cash $3.5B, rev $14.7M, net loss $191M, FCC commercial auth, 45-sat 2026 target) — https://www.stocktitan.net/sec-filings/ASTS/8-k-ast-space-mobile-inc-reports-material-event-75ced08d18a6.html — retrieved 2026-05-31 — grade A — primary-fetched
4. ASTS BlueBird 6 largest commercial array (223 m²) — https://satnews.com/2025/12/24/ast-spacemobile-deploys-bluebird-6-largest-commercial-array-in-leo/ — retrieved 2026-05-31 — grade B
5. Next-Gen BlueBird (120 Mbps, 10x capacity) — https://ast-science.com/next-gen-bluebird/ — retrieved 2026-05-31 — grade A
6. Globalstar Q1 2026 ($71.96M rev, Apple 66%) — https://www.stocktitan.net/sec-filings/GSAT/10-q-globalstar-inc-quarterly-earnings-report-ece8438691c1.html — retrieved 2026-05-31 — grade B
7. Apple $1.5B Globalstar investment / Emergency SOS $450M — https://www.apple.com/newsroom/2022/11/emergency-sos-via-satellite-made-possible-by-450m-apple-investment/ — retrieved 2026-05-31 — grade A
8. Amazon $11.57B Globalstar acquisition (2026-04-14) — https://www.sec.gov/Archives/edgar/data/1366868/000114036126014528/ef20070409_8k.htm — retrieved 2026-05-31 — grade A
9. EchoStar–SpaceX $17B AWS-4/H-block spectrum sale (2025-09-08) — https://www.prnewswire.com/news-releases/echostar-announces-spectrum-sale-and-commercial-agreement-with-sp[redacted-acct]50.html — retrieved 2026-05-31 — grade A — primary-fetched
10. EchoStar going-concern + AT&T $23B / SpaceX deals — https://www.stocktitan.net/sec-filings/SATS/10-q-echo-star-corp-quarterly-earnings-report-e8bdf47b1303.html — retrieved 2026-05-31 — grade B
11. T-Mobile/Starlink T-Satellite commercial launch (2025-07-23, data Oct-2025) — https://www.t-mobile.com/coverage/satellite-phone-service — retrieved 2026-05-31 — grade A
12. Starlink Direct to Cell service sheet — https://www.starlink.com/public-files/DIRECT_TO_CELL_SERVICE_FEB_25.pdf — retrieved 2026-05-31 — grade A
13. D2C link-budget physics (<0.25W phone, 550km, 25 m² array) — https://keeptrack.space/deep-dive/starlink-direct-to-cell — retrieved 2026-05-31 — grade C
14. SpaceX $800B / 2026 IPO plan — https://fortune.com/2025/12/13/spacex-ipo-plan-2026-secondary-offering-insider-share-sale-800-billion-valuation/ — retrieved 2026-05-31 — grade B
15. SpaceX $1.75T IPO target — https://www.bloomberg.com/graphics/2026-spacex-ipo-stock-market-nasdaq-listings/ — retrieved 2026-05-31 — grade B
16. Viasat FY2026 results (FCF ~$600M, debt redemption, ViaSat-3 F3) — https://www.sec.gov/Archives/edgar/data/0000797721/000119312526245304/d133220dex992.htm — retrieved 2026-05-31 — grade A
17. Eutelsat $1.56B capital raise / French govt 29.65% — https://spacenews.com/french-government-to-lead-eutelsats-1-56-billion-capital-boost/ — retrieved 2026-05-31 — grade B
18. Amazon Leo 302 satellites / enterprise beta 2026-04 — https://en.wikipedia.org/wiki/Amazon_Leo — retrieved 2026-05-31 — grade B

