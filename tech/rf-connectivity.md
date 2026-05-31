---
type: synthesis
domain: tech-trend
tags: [rf, rffe, 5g, 6g, nr, wifi, bluetooth, audio, mmwave, power-management, analog, gan, sic, rf-soi, baw, fbar, connectivity, anti-bubble]
as_of_timestamp: 2026-05-31T22:00:00+08:00
author_role: researcher
confidence: 0.75
verdict: 結構
rubric: {A1: 2, A2: 2, A3: 2, A4: 2, A5: 1}
sources_grade_summary: "A: 17 B: 20 C: 14 D: 1 E: 0"
phase: D
---
# 射頻與連結性半導體 — RF 是被冷落的 anti-bubble,但成長已從手機前端遷徙 / RF & Connectivity Semis: the Anti-Bubble, but the Growth Has Migrated

> **Principal's framing (RF 工程師本人):** "我們強化地端、強化雲端,但兩者之間的『連結』一定需要更大頻寬、更多 channel、更廣頻譜、更鬆綁的法規、更多 device、更縝密的網絡。RF 被嚴重低估。" 本頁就此論點作 質變-vs-同溫層 盡職調查,涵蓋 4G/5G/6G/NR、Wi-Fi/BT/Audio、毫米波,以及變數 #15 的另一半「電源管理 IC 急單」。

## 0. 一句話判決 + Desk view
**結構 (composite, conf 0.75)。** 這是全 [[scoreboard]] 22 條裡**同溫層落差方向相反**的一條:其他每一條的空方都是「受益者≠該價位、股價跑在基本面前」(memory/CPO/PLTR/Hermès);**RF/類比的落差是倒過來的——基本面(週期復甦 + 內容複雜度 + AI 電力)被忽略,因為這個板塊不時髦。** Principal 的「低估」直覺在**估值/情緒面是對的**:QRVO/SWKS ~15–16× fwd P/E、AOSL/DIOD 個位數~低雙位數,對比 MPWR ~50–67×、KEYS ~30–40×、MTSI ~73×。但 desk 的臨床修正有三點:(1) **手機 RFFE 便宜是有原因的**——內容已從「4G→5G +40%」攤平成「blended 大致持平」,RFFE TAM 幾乎不長($15.4B 2024→~$17B 2030),加上 Apple 自研 + 中國替代 + 2026 記憶體擠壓的手機**單位衰退 −12.9%**;這是「便宜但有真實的毛病」,不是免費午餐。(2) **變數 #15 的急單訊號是真的、現在進行式**——但它從**工業/分銷/AI 資料中心**那道門點火,不是從手機那道門:經銷商 book-to-bill 翻 >1、通路庫存創低、且 2023–24 的**價格戰已反轉成 2026 的漲價潮**(TI +15–85%、ADI 全線 +15%,連中國廠都在漲),這是去化完成 + 成熟製程被 AI 搶晶圓的鐵證。(3) **RF 真正的成長已遷徙**——離開手機前端,流向 (a) AI 資料中心的電力/互連縫(MPWR/VICR/KEYS/GFS),(b) 週期性類比復甦(已部分定價),(c) 國防/EW 的 GaN(MTSI/QRVO HPA,現在就有營收),(d) 2029+ 的 6G FR3 建設(太早)。**最乾淨的 alpha = 騎週期復甦 + 擁有「不管哪個頻段/標準贏都收過路費」的瓶頸(KEYS 測試、GFS RF-SOI),而非追結構受挑戰的手機在位者。**

兩個重塑地圖的事件:**QRVO + SWKS 合併**(2025-10-28 宣布,~$22B,~2027 初完成;QRVO 已暫停財測)——兩大 RF 純玩家合一,是「有機成長已盡、靠整併防守」的訊號;**TI 併購 Silicon Labs**($231/股 ~$7.5B,2026-02-04;SLAB 暫停財測)——最乾淨的 IoT 連結性指標股被吸收。

**研究/教育用途,非買賣建議。** Verdict 是螢幕輸出,交由 [[../philosophy/05-decision-rubric]] 在既有部位/集中度上限與 [[../philosophy/concepts/evidence-gated-rebalance]] 證據門檻下消化。

## 1. 技術底蘊 (A1) — ENGINEER-GRADE:為什麼「內容」會長,以及為什麼會卡
**手機 RF 內容的機制(真實但已攤平)。** 4G→5G 把 RF 問題乘上去:在 LTE legacy 之上疊 NR band group,載波聚合(CA)把一堆 FDD+TDD 組合堆在一起,每個新 band/CA 組合都要自己的濾波 + 常常自己的 PA path + 更多 switch 與天線孔徑/阻抗 tuner。旗艦 5G 機帶 **~15–20 顆聲波濾波器**(SAW/TC-SAW/BAW/FBAR),中階 ~8–12 顆;4G→5G 把濾波器內容拉高 **~50–70%**。金額層級:4G 旗艦 RFFE BoM ~$18 → 5G blended ~$25(+~40%)→ mmWave 每天線模組再 **+~$15–16**(且一支機帶多個模組)[S15][S21]。
**但 2026 的現實是內容成長攤平了**:SWKS 自己明說「明年 blended content 大致持平,Apple 轉內部 modem 反而可能開出新 socket 機會」[S14]。$18→$25 是**早期 5G 的舊數字**,方向對、非 2026 新鮮值。

**真正的護城河 = 高 Q 濾波器 + 基板,不是 PA。** SAW/TC-SAW 經濟地服務 ~2.5 GHz 以下;**~2.5 GHz 以上(n7/n41/n77/n79、Wi-Fi 共存)必須用 BAW/FBAR**——它在 SAW 滾降之處仍維持 Q 值與溫度穩定度與陡峭裙邊。這是結構性雙雄:**BAW 基本是兩匹馬——Broadcom(FBAR)與 Qorvo(BAW)**(Qorvo 稱出貨 >100 億顆 BAW)。中國在 switch/tuner/4G PA 很強(Maxscend 300782.SZ、Vanchip、Lansus 進濾波器 IP 前五),**但濾波器尤其 BAW 是最難在地化的節點**——這是中國替代的閘門 [S8][S9][S10][S21]。更深一層的基板:**RF-SOI 是天線開關/tuner 的主流基板**(業界 rule-of-thumb ~70% 開關建在 SOI 上,grade C;硬事實是 95% RF-SOI 用 200mm 製造)——GFS(22FDX)與 TSEM 是主要 foundry [S40]。

**6G 的物理(Principal 的論點接地處)。** 6G 的重心**不是 sub-THz,而是 upper-mid-band / FR3(7.125–24.25 GHz)**,ITU 聚焦 10–14.5 GHz、Ericsson 直接稱 **7–15 GHz 是 6G「essential」頻段** [S11]。FR3 給每運營商 >400 MHz(FR1 只 ~100 MHz),路徑損耗遠低於 mmWave,**但要靠激進的 massive-MIMO 補回對 sub-6 GHz 的覆蓋差**——這正是「每台 radio 更多 PA、更多天線路徑、結構性拉向 GaN-on-SiC」的機制,也就是 Principal 的「縫一定要長大」。sub-THz(92–300 GHz)在 Ericsson/Nokia 路線圖裡明確是**互補/利基**(FWA、熱點、回程),不是量的那層。**結論 A1=2**——BAW/FBAR 雙雄 + RF-SOI 基板 + GaN-on-SiC + FR3 massive-MIMO 都是真實、難複製的硬物理;弱點是手機 RFFE 低階在商品化、內容已攤平。

## 2. 需求數據 (A2) — 週期復甦是真的,但從工業/AI 那道門進來
| 指標 metric | 數值 value | 期間 period | 來源 (grade — verification) |
|---|---|---|---|
| 經銷商 book-to-bill | Arrow 三區皆 >1(2022 來首見全球零件 YoY 正成長);Avnet >1;Microchip 4 年新高 | 1H CY2026 | DSG/Digitimes (B — 多源交叉) |
| Microchip 通路庫存 | **26 天**(歷史低端),即將回補 | FQ4'26(3月) | MCHP 8-K (A — primary) |
| 漲價潮(取代價格戰) | TI **+15–85%**(4/1 起);ADI **全線 +15%**(2/1 起);中國廠(SG Micro/Novosense/3Peak)亦漲 | 2026 | Digitimes (C — 方向多源、SKU% paywalled) |
| 智慧手機單位(逆風) | **−12.9% 至 1.12B**(史上最大跌幅),記憶體擠壓 BoM 所致;2027 僅 +2% | 2026 | IDC via 多源 (B) |
| MPWR Enterprise Data(AI) | **+97.7% 至 $263M**(總營收 $804.2M,+26.1%) | Q1'26 | MPWR 8-K (A — primary) |
| ADI 復甦 | 總營收 $3.16B **+30%**,「broad-based recovery」,工業 B:B >1,AI ~20% 營收 | FQ1'26 | ADI 8-K (A — primary) |
| NXP Ind&IoT | **+24% YoY**(總 $3.18B +12%,Q2 指引 ~+18%) | Q1'26 | NXPI 8-K (A — primary) |
| SYNA Core IoT | **+31% YoY**;FY26 Core IoT 指引 **>$385M(+40%)** | FQ3'26 | SYNA 8-K (A — primary) |
| SLAB(IoT 指標股) | 總 +20%,**工業 +33%**,通路庫存下降、連兩季設計案新高 | Q1'26 | SLAB 8-K (A — primary) |
| DIOD(消費週期 proxy) | $405.5M **+22.1%**,連 6 季雙位數成長(2021 來最佳) | Q1'26 | DIOD 8-K (A — primary) |
| Keysight 訂單 | **+56% YoY 至 $2.05B**,點名 6G/NTN/AI 供應鏈;CSG 段 +35% | FQ2'26 | KEYS 8-K (A — primary) |

讀法:**「broad-line 類比/連結性在轉強」= 確認**(分銷、工業、汽車內容、AI 資料中心、IoT 工業端);**「手機特定」= 仍被封頂**(AOSL 中國手機弱、POWI/DIOD 消費線落後工業線、IDC −12.9% 單位 + 記憶體衝擊是約束)。變數 #15 的急單訊號正在點火,但走的是工業/分銷門,不是手機門。**A2=2**——AI/電力/類比層是 accelerating P&L、數據背書(非敘事);手機層真實但被供給面擠壓封頂。

## 3. 資金·權威 (A3)
M&A 與標準權威壓倒性:**QRVO+SWKS $22B 合併**(2025-10-28,$32.50 現金 + 0.960 SWKS/股,~2027 初完成,$500M+ 綜效)[S12][S13][S27];**TI 併 Silicon Labs $231/股 ~$7.5B**(2026-02-04)[S11b];**ADI 併 Empower Semiconductor $1.5B**(2026-05,切入 AI 垂直供電)[S3p];**MACOM 早於 2023-12 買下 Wolfspeed 的 RF 事業**($125M、RTP fab、1400+ 專利)[S15m]。標準/權威:**ITU IMT-2030 框架已發布(2023-12)**、**3GPP Rel-20 為 6G study(Stage-2 ~2026-09 凍結)**、**Rel-21 首版 normative 6G 規格 ~2028–29**;**Nvidia 親自推 AI 電力架構**(800V HVDC)[S6g]。反向訊號:**NXP 退出 5G RF-power、關閉 Chandler GaN 廠**(末批 GaN 晶圓 2027 Q1),comms-infra 營收連兩年 −20%/−25%——供應端在收斂,不是擴張 [S24]。**A3=2**——資本與權威全力押注;但要注意這裡的資金多是**整併/防守 + AI 轉向**,而非手機 RF 的有機擴張。

## 4. 受益 / 受損 / 抄底 (A4) — 依 Principal 的 taxonomy 拆
**(a) 4G/5G/NR 手機前端(Principal 的本行)。** 受益:**QRVO/SWKS**(合併中,~15–16× fwd P/E、non-GAAP GM 已逆勢上行至 52.6%/45%),**AVGO**(FBAR,但無線已是 AI 引擎旁的零頭),**QCOM**(modem+RFFE,~13–14× 但 Apple modem 在歸零路徑)。**這組是 anti-bubble 的核心,但也是結構受挑戰最深的一組**:合併本身就是「有機成長已盡」的告白。
**(b) 6G/NR 未來。** **太早(T0)**;**FR3 物理驗證 Principal 的縫論,但營收 ~2029+**;運營商現在在 capex 谷底(ERIC −10% reported、NOK 大致持平)。
**(c) Wi-Fi/BT/Thread/UWB(更多 device、更縝密網絡)。** 受益:**SYNA**(Core IoT +31%/FY26 +40%)、**NXPI**(UWB 龍頭 + 汽車數位鑰匙,Ind&IoT +24%)、**CEVA**(IP 授權,87% GM,**反而從 SoC 整併中受益**——把 IP 授權給整併者)、**AVGO/QCOM**(combo)。受損/被吸收:**SLAB**(被 TI 併,已暫停財測)。技術節奏:Wi-Fi 6E→7(320MHz、MLO)→**8(802.11bn UHR,重點從峰值速率轉向可靠度,~2028 認證)**;**到 2027 是 Wi-Fi 7 attach 的故事,不是 Wi-Fi 8**。Matter/Thread 採用**不如預期**(電池續航比 Zigbee 差、跨生態破碎),消費智慧家庭是 IoT 復甦裡的落後者。
**(d) Audio。** **CRUS**(Cirrus)~**91% Apple**,FY26 $2.0B、GM 53%,靠內容成長(custom amp、22nm codec、HPMS 相機控制器)抵銷單位疲軟;**Apple 音訊自研是潛伏(未宣布)風險**,非已知 design-out——但歷史顯示 Apple 最終會攻擊高價值類比 block。極端單一客戶集中。
**(e) 毫米波。** 手機 mmWave:**停滯/利基**(僅美國電信驅動);FWA 是真正的量,但在減速(失去美國農村補助);**mmWave 現在賺錢的地方是國防/EW/雷達**(MTSI、QRVO HPA 的 GaN)——是利潤/差異化故事,不是單位故事。
**(f) 電源管理 IC(變數 #15 的另一半)。** **MPWR**(+26%、AI Enterprise Data +97.7%,但 Nvidia socket 集中 + Infineon/Renesas/ADI 競爭 + ~50–67× P/E,且 2024 曾被砍掉約半個 Blackwell backlog)、**TXN**(broad 類比指標,+19%,capex/FCF 之爭未解、EV/S ~16× 高於十年中位 ~8×)、**ADI**(+30%、broad-based、買 Empower)、**ON**(SiC 仍軟、汽車 +5% 八季來首成長)、**MCHP**(底部確認、142 季連續獲利)、**POWI**(PowiGaN +40% 但基數小)、**VICR**(48V→PoL 垂直供電,backlog +70%、B:B >2,但有 ITC 訴訟)、**NVTS**(GaN 純玩家,僅 $8.6M、−38.6%、燒現金 ~6 季 runway)、**AOSL/DIOD**(消費/中國 proxy)。
**(g) Picks-and-shovels(最深的鏟子)。** **KEYS(Keysight)= 最乾淨的 6G 槓桿且現在就有營收**——「不測就出不了 radio」,訂單 +56% 點名 6G/NTN/AI,與 Qualcomm 做 RF digital twin、與 Samsung 做 AI-RAN;**GFS(GlobalFoundries)= RF-SOI/FDX 基板瓶頸**(手機 ~1/3 營收且在主動多元化);**TSEM** 把故事從 RF-SOI 旋向 AI 矽光子($1.3B SiPho 2027 承諾)——RF-SOI 成了被淡化的金牛。
**抄底 vs 價值陷阱判別:** QRVO/SWKS 合併 = RF 的深價值事件,但要先證實「合併綜效 + 非手機(國防/infra/power)$2.7B 業務」能抵銷手機侵蝕;AOSL 21% 毛利是商品類比利潤壓力的活證據(陷阱風險高)。**A4=2**——這是全部 22 條裡**可投資瓶頸最清楚、listed pure-play 最多**的一頁(BAW 雙雄、RF-SOI、測試 tollbooth、UWB、IP 授權)。

## 5. 多時程 (T0–T3)
- **T0(現在,0–1y)**:**結構**。週期性類比/電源復甦 = 真實且進行中(B:B>1、漲價、+20–30% YoY);AI 電力/互連 = 真實但已部分定價(MPWR/VICR/KEYS 多≥30–70×);手機 RFFE = 便宜但封頂(記憶體擠壓 + Apple 自研)。
- **T1(1–3y)**:Wi-Fi 7 attach 放量;IoT 復甦從工業擴散到消費;QRVO+SWKS 合併完成、Apple C-series modem 全面化(QCOM 手機歸零、QRVO/SWKS Apple 內容受壓);AI 垂直供電架構之爭(48V vs 800V)分出勝負。
- **T2(3–5y)**:6G 預商用試驗(2029,Nokia)→ FR3 massive-MIMO 開始拉 GaN/PA 內容;**這是 Principal 的「縫長大」真正兌現的起點**。
- **T3(5–10y)**:6G 規模商用(2030+)、ISAC(通感一體)/AI-native air interface 落地、NTN 與地面網融合——**RF 內容的時代級躍升候選(質變),但要熬過 capex 谷底與標準凍結**。

## 6. 爆發條件 + 里程碑階梯 (falsifiable, 每週追 [[_weekly-watch]])
1. **手機 RF 週期轉正**:verify = SWKS mobile 環比轉正 + QCOM 中國手機在 fiscal Q4 落底回升。status:手機單位 −12.9%、記憶體擠壓未解。next:每季財報。
2. **變數 #15 急單持續**:verify = Arrow/Avnet/Microchip B:B 是否續 >1 + 漲價是否守住(非一次性)。status:B:B>1、TI/ADI 已漲價。next:每季經銷商電話。
3. **QRVO+SWKS 合併過關**:verify = FTC Second Request + 中國 SAMR 結案。status:審查中,~2027 初。next:監看 425/SAMR。
4. **Apple 自研侵蝕量化**:verify = C2/C3 modem 進度 + Proxima Wi-Fi 全面化 + Cirrus 是否被點名 design-out。status:C1/C1X 已出、N1 已取代 Broadcom client Wi-Fi。next:iPhone 18 拆解。
5. **6G 規格凍結**:verify = 3GPP Rel-20 Stage-2(2026-09)、Rel-21 normative(~2028–29)。status:Rel-20 study 中。next:2026-06 Rel-21 工期決定。
6. **AI 垂直供電架構收斂**:verify = Nvidia Rubin/下一代採 48V→PoL 還是 800V→6V;ADI-Empower 整合。status:Vicor 公開稱 800V→6V「結構性錯誤」,未收斂。next:GTC / 各家供電 design win。

## 7. 時代影響與交互
與 [[ai-datacenter-power]]:RF/類比的**最大成長已遷徙到 AI 電力縫**(MPWR/VICR/ADI-Empower 的垂直供電、800V HVDC)——本頁只看 PMIC/power-semi 角,IPP/核能那層在該頁。與 [[optical-interconnect-cpo]] / [[optical-supply-chain-deep]]:TSEM/GFS 同時是 RF-SOI 與**矽光子** foundry,AI 互連把它們的成長從 RF 拉向 SiPho。與 [[satcom-future]]:LEO/D2C 共用同一條台廠上游(RF PA/濾波器/高頻 PCB),NTN 已進 6G(Rel-19+)與 Keysight 測試訂單;**「縫」在天上也在地上**。與 [[ai-edge-devices]]:端側裝置(過熱)的真實受益是記憶體;**而連結這些 device 的 RF/連結性層,才是 Principal 論點的承載**——但成長分散在工業 IoT、Wi-Fi 7 attach、UWB,不在被商品化的 combo 晶片。與 [[defense-tech]]:mmWave+GaN 現在賺錢的地方(MTSI/QRVO HPA 的雷達/EW/satcom T/R 模組)。

## 8. 同溫層 + 自我打臉
**Echo-chamber gap(本頁是倒的)**:這個板塊的落差不是「敘事 > 數據」,而是**「數據(週期復甦 + 內容複雜度 + AI 電力)被忽略,因為 RF/類比不時髦」**——這是 anti-bubble。Principal 的「低估」直覺在**估值/情緒面成立**:整個板塊被 AI 敘事的光芒蓋掉,multiples 在低位。**但這正是要自我打臉的地方:**
**自我打臉(打多頭)**:便宜 ≠ 低估。手機 RFFE 便宜是**結構性**的——(1) 內容已攤平(SWKS 自承「blended 持平」)、(2) RFFE TAM 幾乎不長($15.4B→$17B/2030)、(3) Apple 自研沿整條無線 BoM 推進(modem C1/C1X→QCOM、Wi-Fi/BT N1 Proxima→AVGO client、audio 是潛伏風險)、(4) 中國在 switch/tuner/4G PA 一路替代、(5) 2026 手機單位 −12.9%。QRVO+SWKS 合併是「有機成長已盡」的告白,不是成長故事。**所以 Principal 對了一半:RF 確實被冷落、估值便宜、且週期 + 變數 #15 急單訊號真實在轉——但「成長」已從他最熟的手機前端,遷徙到 AI 電力/互連縫、週期性類比、國防 GaN 與 2029+ 的 6G FR3。最乾淨的表達不是賭手機 RFFE 回春,而是 (i) 騎已確認的週期復甦、(ii) 擁有不管誰贏都收過路費的瓶頸(KEYS 測試、GFS RF-SOI)、(iii) 把 6G FR3 當你不為它付溢價的 2029+ 免費選擇權。**
**反向自我打臉(打空頭,即補回被低估的真質變)**:我說手機 RFFE「結構受挑戰」——但 (a) BAW/FBAR 在 >2.5 GHz 是真雙頭壟斷、中國啃不動濾波器;(b) Apple 自研 modem 仍需外部 RFFE,transceiver-to-RFFE 介面反而可能**開新 socket**(SWKS 自己這麼說);(c) FR3 物理保證每台 radio 的 RF 內容在 6G 世代結構性上升——這些把手機 RFFE 從「衰退」校正回「低成長但有護城河的週期股」。**淨結論:結構(composite),T0 騎週期 + 守瓶頸,T2–T3 才是 Principal 縫論的質變兌現。**

## Sources
A=primary filing/standards body; B=tier-1 press/transcript; C=secondary; D=forum; E=rumor. 全 point-in-time = 2026-05-31,無前視。
1. [S1] Qorvo Q4 FY2026 8-K (rev $808.3M, non-GAAP GM 52.6%) — https://www.sec.gov/Archives/edgar/data/0001604778/000162828026030523/earningsrelease20260328.htm — 2026-05-31 — A
2. [S12] CNBC — Skyworks/Qorvo to merge (2025-10-28) — https://www.cnbc.com/2025/10/28/skyworks-qorvo-to-merge.html — 2026-05-31 — B
3. [S13] TrendForce — Skyworks+Qorvo $22B combination (63/37, Apple exposure) — https://www.trendforce.com/news/2025/10/29/news-apple-suppliers-skyworks-and-qorvo-unite-to-form-22-b-u-s-rf-chip-powerhouse/ — 2026-05-31 — B
4. [S27] Skyworks/Qorvo combination PR — https://investors.skyworksinc.com/news-releases/news-release-details/skyworks-and-qorvo-combine-create-22-billion-us-based-leader — 2026-05-31 — A
5. [S14] Skyworks Q2 FY2026 transcript (Apple ~60%, content "flat", $1B Android win, B:B>1) — https://finance.yahoo.com/markets/stocks/articles/skyworks-swks-q2-2026-earnings-214348362.html — 2026-05-31 — B
6. [S22q] Qualcomm Q2 FY2026 transcript (rev $10.6B −3%, handsets $6.0B −13%, Apple "20% share, no relationship beyond", China bottom fiscal Q3) — https://www.fool.com/earnings/call-transcripts/2026/04/29/qualcomm-qcom-q2-2026-earnings-transcript/ — 2026-05-31 — B
7. [S23] MacRumors — Apple N1 "Proxima" Wi-Fi 7/BT/Thread in iPhone 17, displaces Broadcom — https://www.macrumors.com/2025/09/09/iphone-17-n1-chip/ — 2026-05-31 — B
8. [S8] Electronics Weekly — "China coming for the RFFE market" (Yole: TAM $15.4B→$17B, shares) — https://www.electronicsweekly.com/news/business/china-coming-for-the-rf-front-end-module-market-2025-09/ — 2026-05-31 — B
9. [S9] Yole — RF Front-End Modules for Mobile 2025 — https://www.yolegroup.com/press-release/rf-front-end-modules-for-mobile-how-chinese-oems-are-driving-innovation-and-disruption/ — 2026-05-31 — B
10. [S10] Knowmade — Q4 2025 RFFE IP (Lansus enters top-5 filters) — https://www.knowmade.com/technology-news/press-release/q4-2025-rf-front-end-ip-stable-leaders-china-accelerates-lansus-enters-top-five-filters-dominate — 2026-05-31 — B
11. [S21] Electronics360 — Galaxy S20 Ultra 5G teardown (mmWave module ≈$16.01; QRVO/SWKS module IDs; BAW) — https://electronics360.globalspec.com/article/15093/teardown-samsung-galaxy-s20-ultra-5g — 2026-05-31 — B
12. [S15] Skyworks $18→$25 content figure (dated mgmt figure) — https://seekingalpha.com/article/4388724-skyworks-solutions-lifted-5g-revolution — 2026-05-31 — C
13. [S18] Distribution Strategy Group — Arrow recovery (B:B>1 all regions, first YoY component growth since 2022) — https://distributionstrategy.com/2026/03/arrow-electronics-sees-semiconductor-recovery-taking-hold-as-services-expand/ — 2026-05-31 — B
14. [S20] IDC via Prism — smartphones −12.9% to 1.12B 2026 (memory-driven) — https://www.prismnews.com/news/idc-warns-smartphone-shipments-will-plunge-129-to-112-billion-units-in-2026 — 2026-05-31 — B
15. [S19] Counterpoint — 2026 forecasts revised down (memory/BoM) — https://counterpointresearch.com/en/insights/2026-smartphone-shipment-forecasts-revised-down-as-memory-shortage-drives-bom-costs-up — 2026-05-31 — B
16. [MPWR] Monolithic Power Q1'26 (rev $804.2M +26.1%, Enterprise Data +97.7%) — https://www.stocktitan.net/news/MPWR/monolithic-power-systems-reports-first-quarter-results-on-april-30-skf5kfr0uvrm.html — 2026-05-31 — B
17. [TXN] Texas Instruments Q1'26 transcript (rev $4.83B +19%, Analog $3.92B +22%) — https://www.fool.com/earnings/call-transcripts/2026/04/22/txn-q1-2026-earnings-transcript/ — 2026-05-31 — B
18. [ADI] Analog Devices FQ1'26 8-K (rev $3.16B +30%, 71.2% NG GM, broad-based recovery) — https://www.sec.gov/Archives/edgar/data/0000006281/000000628126000015/adi1q26exhibit991earnings.htm — 2026-05-31 — A
19. [S3p] ADI–Empower $1.5B acquisition PR — https://www.prnewswire.com/news-releases/analog-devices-to-acquire-empower-semiconductor-expanding-its-next-generation-high-density-power-portfolio-for-the-ai-era-302776701.html — 2026-05-31 — A/B
20. [ON] onsemi Q1'26 8-K (rev $1.51B, GM 38.5%, auto +5% first growth in 8 qtrs, AI-DC +30% QoQ) — https://www.sec.gov/Archives/edgar/data/0001097864/000114036126018868/ef20072220_ex99-1.htm — 2026-05-31 — A
21. [MCHP] Microchip FQ4'26 8-K (rev $1.311B, dist inventory 26 days, restocking expected) — https://www.sec.gov/Archives/edgar/data/0000827054/000082705426000012/exhibit991q4fy26.htm — 2026-05-31 — A
22. [POWI] Power Integrations Q1'26 (rev $108.3M, PowiGaN +>40%, industrial +23%) — https://www.stocktitan.net/sec-filings/POWI/8-k-power-integrations-inc-reports-material-event-fb0ac2a2262a.html — 2026-05-31 — B
23. [NVTS] Navitas Q1'26 (rev $8.6M −38.6%, GaN+SiC pivot, Nvidia 800V demo, ~$221M cash) — https://www.globenewswire.com/news-release/2026/05/05/3288263/0/en/Navitas-Semiconductor-Announces-First-Quarter-2026-Financial-Results.html — 2026-05-31 — A/B
24. [VICR] Vicor Q1'26 transcript (rev $113M +20.2%, backlog +70%, B:B>2, 48V→PoL VPD) — https://www.fool.com/earnings/call-transcripts/2026/05/03/vicor-vicr-q1-2026-earnings-transcript/ — 2026-05-31 — B
25. [DIOD] Diodes Q1'26 (rev $405.5M +22.1%, 6th straight double-digit qtr) — https://www.stocktitan.net/sec-filings/DIOD/8-k-diodes-inc-del-reports-material-event-44dc186965ff.html — 2026-05-31 — B
26. [AOSL] Alpha & Omega FQ3'26 (rev $163.8M, GM 21.1%, China handset weak) — https://www.stocktitan.net/sec-filings/AOSL/8-k-alpha-omega-semiconductor-ltd-reports-material-event-0e4b53b9195e.html — 2026-05-31 — B
27. [SLAB] Silicon Labs Q1'26 8-K (rev $213.5M +20%, industrial +33%, bookings accel) — https://www.sec.gov/Archives/edgar/data/0001038074/000103807426000018/slab-20260505q1earningsrel.htm — 2026-05-31 — A
28. [S11b] TI to acquire Silicon Labs ($231/sh, ~$7.5B) — https://www.ti.com/about-ti/newsroom/news-releases/2026/2026-02-04-texas-instruments-to-acquire-silicon-labs.html — 2026-05-31 — A
29. [SYNA] Synaptics FQ3'26 8-K (rev $294.2M +10.4%, Core IoT +31%, FY26 >$385M) — https://www.sec.gov/Archives/edgar/data/0000817720/000081772026000035/syna-q3268kexx991.htm — 2026-05-31 — A
30. [NXPI] NXP Q1'26 8-K (rev $3.18B +12%, Ind&IoT +24%, UWB) — https://www.sec.gov/Archives/edgar/data/0001413447/000141344726000032/nxp1q26exhibit991.htm — 2026-05-31 — A
31. [CRUS] Cirrus Logic FY26 PR (rev $2.0B, GM 53%, ~91% Apple) — https://www.sec.gov/Archives/edgar/data/0000772406/000077240626000012/pressrelease_fullyear.htm — 2026-05-31 — A
32. [CEVA] CEVA Q1'26 (rev $27.0M +11%, 87% GM, record Wi-Fi units, Wi-Fi 7/UWB wins) — https://www.ceva-ip.com/press/ceva-inc-announces-first-quarter-2026-financial-results/ — 2026-05-31 — A
33. [S11] Ericsson — 6G spectrum 7–15 GHz "essential", sub-THz complementary — https://www.ericsson.com/en/reports-and-papers/white-papers/6g-spectrum-enabling-the-future-mobile-life-beyond-2030 — 2026-05-31 — B
34. [3GPP] 3GPP Release 20 / Release 21 (Rel-20 6G study, Stage-2 freeze Sep 2026) — https://www.3gpp.org/specifications-technologies/releases/release-20 — 2026-05-31 — A
35. [ITU] ITU IMT-2030 (6G) framework Rec. M.2160 (2023-12) — https://www.itu.int/en/ITU-R/study-groups/rsg5/rwp5d/imt-2030/pages/default.aspx — 2026-05-31 — A
36. [S8spec] arXiv 2502.17914 — Upper Mid-Band (FR3) Spectrum for 6G — https://arxiv.org/pdf/2502.17914 — 2026-05-31 — A/C
37. [MTSI] MACOM FQ2 FY26 8-K (rev $289M +22%, adj GM 58.5%, B:B 1.5) — https://www.sec.gov/Archives/edgar/data/0001493594/000149359426000024/ex99_1earningsreleaseq2fy26.htm — 2026-05-31 — A
38. [S15m] MACOM completes acquisition of Wolfspeed's RF business (2023-12) — https://www.macom.com/updates/news/2023/macom-completes-acquisition-of-wolfspeed-s-rf-business — 2026-05-31 — B
39. [S24] Bits&Chips — NXP exits 5G radio power, shutters Arizona GaN fab — https://bits-chips.com/article/nxp-exits-5g-radio-power-market-shutters-arizona-gan-fab/ — 2026-05-31 — B
40. [GFS] GlobalFoundries Q1'26 (rev $1.634B, non-IFRS GM 29.0%, smart-mobile ~1/3) — https://www.sec.gov/Archives/edgar/data/0001709048/000170904826000111/globalfoundries1q2026earni.htm — 2026-05-31 — A
41. [S40] SemiEngineering — RF-SOI dominant antenna-switch substrate (95% on 200mm) — https://semiengineering.com/rf-soi-wars-begin/ — 2026-05-31 — C
42. [TSEM] Tower Semi Q1'26 6-K (rev $414M +15%, $1.3B SiPho 2027 commitments) — https://www.sec.gov/Archives/edgar/data/0000928876/000117891326002607/exhibit_99-1.htm — 2026-05-31 — A
43. [WOLF] Wolfspeed exits Chapter 11 (2025-09-29, cut $4.6B debt) — https://spectrumlocalnews.com/nys/central-ny/business/2025/10/01/wolfspeed-exits-chapter-11-bankruptcy — 2026-05-31 — B
44. [KEYS] Keysight FQ2 FY26 8-K (rev $1.72B +31%, orders +56%, 6G/NTN/AI) — https://www.sec.gov/Archives/edgar/data/0001601046/000160104626000019/exhibit991-q226pressrelease.htm — 2026-05-31 — A
45. [ERIC] Ericsson Q1 2026 results (−10% reported, RAN flat) — https://www.ericsson.com/en/press-releases/2026/4/ericsson-reports-first-quarter-results-2026 — 2026-05-31 — A
46. [NOK] Nokia Q1 2026 interim report (€4.50B +2%) — https://www.nokia.com/newsroom/nokia-corporation-interim-report-for-q1-2026/ — 2026-05-31 — A
47. [S6g] Navitas/Nvidia 800V HVDC + Vicor 48V→PoL architecture clash — https://photoncap.net/p/the-last-15mm-of-ai-power-three-numbers — 2026-05-31 — B/C
