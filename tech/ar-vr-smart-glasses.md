---
type: synthesis
domain: tech-trend
phase: B
tags: [ar, vr, smart-glasses, meta-ray-ban, waveguide, microdisplay, micro-led, lcos, vision-pro, android-xr, essilorluxottica, qualcomm-ar]
as_of_timestamp: 2026-05-31T02:30:00+08:00
author_role: researcher
confidence: 0.78
verdict: 結構
verdict_by_horizon: {T0: 結構, T1: 結構, T2: 太早, T3: 質變}
rubric: {A1: 2, A2: 2, A3: 2, A4: 2, A5: 1}
sources_grade_summary: "A: 6 B: 7 C: 3 D: 0 E: 0"
---
# AR / VR / 智慧眼鏡 — Meta Ray-Ban vs Vision Pro，光學物理 gate 真 AR

## 0. 一句話判決 + 桌邊觀點 / Verdict + desk view
**結構 (display-less AI camera-glasses 已是真質變、已被定價中；true all-day AR 仍 太早), confidence 0.78.** 最尖銳的可證偽事實：**Meta + EssilorLuxottica 在 2025 全年賣出 >7M 副智慧眼鏡，較 2024 翻三倍以上，累計約 9M 副自 2023 上市以來** [CNBC/UploadVR — uploadvr.com/meta-essilorluxottica-sold-7-million... — retrieved 2026-05-31 — B — cross-confirmed by EssilorLuxottica FY2025 PR (A)]。這把「智慧眼鏡=失敗的 Google Glass 重演」的同溫層直接打臉。**桌邊觀點(caveated)**：贏家不是「會顯示的 AR 眼鏡」，而是**沒有顯示器的 AI 相機眼鏡**——Ray-Ban 賣的是 €300 級的相機+喇叭+語音助理時尚框，重量~50g、全天可戴、殺手級 app 是「拍照/問 AI/翻譯」；Vision Pro 賣的是 $3,499、~600–650g、需要外接電池的「空間運算」,2025 假期季只出貨 **45k 副**(2024 全年 390k) [IDC via PYMNTS — pymnts.com/apple/2026/apple-retreats-on-vision-pro — retrieved 2026-05-31 — A]。Ray-Ban 贏在它**先放棄了 AR**;真 AR 仍被 etendue 物理(FOV×eyebox×亮度三選二)+ 成本曲線卡在 T2–T3。Ray-Ban Display ($799, 2025-09-30 上市, 20° FOV) 是「能用但不是科幻」的過渡品,不是拐點。cf. [[ai-edge-devices]] (VP 已判 disruption-vector 失敗)。

## 1. 技術與產品底蘊 (A1 — ENGINEER-GRADE)
**為什麼 Ray-Ban 贏、VP 卡住=SWAP 物理。** Ray-Ban Display 的 iFixit/KGOnTech 拆解給出工程實況:
- **波導 waveguide**: **Lumus 幾何反射式 (geometric/reflective)**,玻璃基板由 **Schott** 製,非繞射式 (diffractive)。幾何波導對同樣 FOV/eyebox **光效率高 3–7×、色均勻度遠優、eye-glow 僅 ~1.5%** [KGOnTech — kguttag.com/2025/10/30/meta-ray-ban-display-part-1 — retrieved 2026-05-31 — A]。代價:幾何波導是「一片昂貴的玻璃」,材料與製程成本遠高於塑膠光學,良率是瓶頸 [iFixit/Hackaday — hackaday.com/2025/10/09 — retrieved 2026-05-31 — B]。
- **微顯示 microdisplay**: **OmniVision OPO3010 LCoS**,600×600(有效解析 ~400×400),pixel pitch 3.8µm,對比 600:1(系統),90fps RGB field-sequential [KGOnTech — A]。投影引擎由 **Goertek** 組裝(紅藍 LED+綠通道、fly-eye 勻光、PBS+四分之一波片)。
- **效能/功耗**: **到眼亮度 ~5,000 nits**,display+audio 僅 **0.38W**(拍照 1.0W、錄影 1.7W)[KGOnTech — A]。**單眼、20° 對角 FOV**(實用~16°)——這是刻意的工程取捨:小 FOV 才能在 ~70g 眼鏡裡同時達到全天電池+戶外可讀亮度。
- **物理 gate**: true wide-FOV AR 撞上 **etendue 守恆**——擴大 eyebox 或 FOV 必然犧牲亮度;最大 FOV 又受波導折射率與 TIR 臨界角硬限制 [Nature Photonics 2025 / arXiv 2401.06900 — nature.com/articles/s41566-025-01718-w — retrieved 2026-05-31 — A]。這是為何 50° FOV + 全天電池 + <50g + 戶外亮度「四角同時滿足」在 2026 仍做不到。
- **微顯示路線之爭**: micro-OLED(Sony ECX350F **10,000 nits**、5,000+ PPI;VP 用 Sony 0.7" 3840×3840、2,200 nits peak)亮度足但波導耦合後室外掉到 ~3,000 nits;micro-LED(JBD 唯一量產、2.5µm pixel 2025 送樣;Porotech 原生紅光 InGaN)亮度最高但**全彩量產未解** [MicroLED-Info/KGOnTech/PanoxDisplay — microled-info.com/jbd — retrieved 2026-05-31 — B]。**A1 = 2**:Lumus 幾何波導 + LCoS/micro-LED 是真硬技術門檻(IP 集中於 Lumus/DigiLens/JBD/Sony),非行銷。

## 2. 需求數據 (A2)
| 指標 Metric | 數值 Value | 期間 Period | 來源 (grade — verification) |
|---|---|---|---|
| Meta+EL 智慧眼鏡出貨 | **>7M 副** | FY2025 全年 | EssilorLuxottica PR (A — primary-fetched) |
| YoY 成長 | **>3×** (翻三倍) | FY2025 vs FY2024 | EssilorLuxottica (A — cross-confirmed) |
| 累計出貨(自上市) | ~9M 副 | 2023-10 → 2025 | UploadVR (B — single-source) |
| 全球智慧眼鏡出貨成長 | **+139% YoY** | H2 2025 | Counterpoint (B — primary-fetched) |
| Meta 全球市佔 | **82%** | H2 2025 | Counterpoint (B — primary-fetched) |
| 全球 AR/VR+眼鏡出貨 | 14.3M (+39.2%);眼鏡 +247.5% | 2025 | IDC (A — cross-confirmed) |
| 中國 AI 眼鏡出貨 | ~950k(35×↑) | 2025 | macaonews/36kr (C — single-source) |
| 中國市佔: 小米/Rokid/阿里 | 32% / 29% / 16% | 2025 | SCMP via Yahoo (B) |
| **Vision Pro 出貨** | **45k**(假期季) vs 390k(2024全年) | Q4 2025 / FY2024 | IDC via PYMNTS (A) |
| Snap Specs 消費版 | $2,500,2026 秋 | (未上市) | RoadtoVR/PPC.land (C) |

需求是**真實的、可在財報驗證的單位數**(非調查意向),且加速度集中在 H2(新機帶動)。**A2 = 2**。

## 3. 資金權威 (A3)
全棧背書且資金真金白銀:**Meta** 2024 以 **€3B 收購 EssilorLuxottica ~3% 股權**(擬增至 5%)[Modaes/Nasdaq — retrieved 2026-05-31 — B];Reality Labs **FY2025 營業虧損 ~$19.19B**(累計 >$80B),Meta 明示 2026 虧損維持相近——這是 hyperscaler 等級的長線豪賭 [Auganix/SEC 10-K — auganix.org/xr-news-meta-reality-labs-2025 — retrieved 2026-05-31 — B — cross-confirmed by Meta FY2025 ARS (A)]。**EssilorVilux FY2025 營收 €28.49B(+11.2% cc)、調整營業利益 €4.5B、FCF €2.8B 創高**,AI 眼鏡帶動 Ray-Ban/Oakley 雙位數成長 [EssilorLuxottica PR — essilorluxottica.com/cap/content/283060 — retrieved 2026-05-31 — A — primary-fetched]。平台側:**Google Android XR**(2024-12 發布,深度綁 Gemini)+ **Samsung Galaxy XR / Project Moohan**($1,800,2025-10 上市)+ Gentle Monster/Warby Parker 眼鏡;**Qualcomm** 與 Snap 簽多年 AR 晶片約(新平台 AI +2.5×、功耗 −50% vs XR2 Gen1)[blog.google / RoadtoVR — retrieved 2026-05-31 — B]。**A3 = 2**:資金+權威皆無爭議。

## 4. 受益 / 受損 / 抄底 (A4)
**贏家(可投資節點)**:
- **EssilorLuxottica (EL.PA/ESLOF)** — 唯一兼具品牌+全球眼鏡通路+組裝的 pure-ish play;但見 §8 margin 風險。
- **Meta (META)** — 軟體/AI 助理層 + 生態,非硬體毛利。
- **波導**: **Lumus**(幾何波導 IP,未上市)、**DigiLens**(繞射,未上市)、玻璃 **Schott**(未上市);組裝 **Goertek**(002241.SZ)。
- **微顯示**: **OmniVision**(LCoS,已併入 韋爾股份 603501.SS)、**Sony (SONY)** micro-OLED、**Himax (HIMX)** LCoS、**Kopin (KOPN)**、**JBD/Porotech** micro-LED(未上市)。
- **SoC**: **Qualcomm (QCOM)** AR/XR 平台(Snap/Samsung/多數安卓眼鏡)。
- 光學鏡片: **Largan/大立光 (3008.TW)**、感測 **OmniVision/Himax**。cf. [[autonomous-driving]] 共用邊緣感知矽。

**受損 / 抄底候選(研究觀察,非建議)**: **Apple (AAPL)** Vision Pro 線——產線停、行銷砍 95%、gen-2 暫停,但這對 AAPL 整體是 rounding error,真正被證偽的是「空間運算=下一平台」敘事(cf. [[ai-edge-devices]] §6)。**抄底邏輯**只在「Apple 改推輕量 AI 眼鏡」兌現時才成立——目前是 thesis 非數據。純 VR 頭顯(整體出貨雙位數衰退)是結構性逆風。**A4 = 2**:瓶頸明確(波導 IP + 微顯示),但多數 pure-play 未上市,listed 曝險偏組合型。

## 5. 多時程 (T0–T3)
- **T0 (now)**: **結構**。display-less AI 相機眼鏡是已實現現金流(EL FY2025 財報實證),7M 副/年、Meta 82% 市佔。已被定價中(EL 股價 2025 反因 margin 與競爭走弱)。
- **T1 (1–3y)**: **結構**。產能擴至 20–30M/年的路線圖 + 安卓 XR/中國群雄入場 → 單位續增,但仍是「AI 眼鏡」(audio/camera 為主),非寬 FOV AR;競爭壓縮 margin。
- **T2 (3–5y)**: **太早**。寬 FOV(>40°)+ 全天電池 + <50g + 戶外亮度的「真 AR」受 etendue + micro-LED 全彩良率 + 成本曲線卡關;dev 平台(Android XR/Snap OS)尚在播種。
- **T3 (5–10y)**: **質變**(條件式)。若 micro-LED 全彩量產 + 波導成本/良率破線 + on-device AI agent 成熟(cf. [[model-leadership-and-data]]),眼鏡有望接棒手機成為主運算介面。**verdict 隨時程明顯不同**。

## 6. 爆發條件 + 里程碑階梯 / Milestone ladder
1. **Meta 眼鏡年出貨 ≥15M (2026)** — verify: EL Q4/FY2026 財報(2027-02) + Counterpoint 季報。status: on-track (FY2025 7M, 產能擴至 20M+)。next check: EL Q1-2026 (2026-04)。
2. **波導+微顯示成本/良率破線** — verify: 下一代 Ray-Ban Display 售價 <$799 或 BOM teardown(iFixit/KGOnTech)顯示幾何波導良率上行。status: 未達(現價疑似補貼/虧本賣)。next check: Connect 2026 (2026-09)。
3. **出現非 Meta 的 hit(單一機型 >1M)** — verify: Counterpoint/IDC 廠商別出貨;候選=小米/Alibaba Quark/Samsung Android XR 眼鏡。status: 未達(中國總量 ~950k 分散多家)。next check: 2026-H1 季報。
4. **AR dev 平台牽引** — verify: Android XR / Snap OS 第三方 app 數、開發者大會 SDK 採用。status: 早期。next check: Google I/O 2026 + Snap Specs 秋季上市。
5. **真 AR SWAP 達標(>40° FOV + <50g + 全天電池同機)** — verify: 任一量產機規格表。status: 未達(Ray-Ban Display 20° FOV/單眼)。next check: 持續。
6. **EL 智慧眼鏡 margin 止跌** — verify: EL 調整毛利率(FY2025 −2.6pp 至 60.9%)是否回升。status: 惡化中。next check: EL FY2026。

## 7. 時代影響與交互 / Era impact & interactions
- 與 [[model-leadership-and-data]]: **on-device AI agent 是殺手級 app 的前提**——眼鏡的價值=「隨身、第一人稱、免掏手機」的 AI 入口;模型小型化(SLM)+雲端 escalate 的 hybrid 直接決定眼鏡體驗。
- 與 [[ai-edge-devices]]: 眼鏡是 VP「空間運算」失敗後的真實 edge 形態;記憶體/SoC 含量是共同 BOM 槓桿。
- 與 [[autonomous-driving]]: 共用**邊緣感知矽**(攝影機 ISP、低功耗 NPU、SLAM/VIO)——OmniVision/Himax/Qualcomm 橫跨兩域。
- 與 [[luxury-and-apparel]] (Phase-B sibling): EssilorLuxottica 是時尚×科技交叉點,眼鏡的「時尚框」屬性是 Ray-Ban 勝出主因之一(消費者買的是 Ray-Ban,順帶 AI)。

## 8. 同溫層 + 自我打臉 / Echo-chamber + self-rebuttal
**同溫層 gap(敘事跑在數據前的精確位置)**:工程圈/科技媒體把「Ray-Ban 大賣」直接外推成「**真 AR 即將到來**」——這是錯置。Ray-Ban 大賣的是**沒有 AR 的 AI 相機眼鏡**;Ray-Ban Display(有顯示)仍是 20° 單眼、$799、疑似虧本賣的小眾品。把 7M 副的成功讀成「寬 FOV AR 的需求驗證」是把 A2 數據貼到 A5 結論上。
**自我打臉(打 §0 的 bull case)**:(a) **退貨/留存未知**——7M 是 sell-in/出貨,EL 未拆 sell-through 與退貨;display-less 眼鏡的「拍照新鮮感後續用率」缺數據(類比智慧手錶早期)。(b) **Margin 在惡化**——EL 調整毛利率 FY2025 −2.6pp 至 60.9%,智慧眼鏡元件成本拖累;Meta 與 EL **公開為定價/策略角力**(Bloomberg 2026-02-24)——夥伴關係張力是真 [Bloomberg — bloomberg.com/news/features/2026-02-24 — retrieved 2026-05-31 — B — single-source-pending]。(c) **Reality Labs FY2025 虧 $19B 且 2026 不收斂**——若眼鏡硬體在補貼賣,「結構」是靠 Meta 燒錢撐出來的,撤補貼後需求彈性未驗證。(d) **中國群雄=價格戰**:950k 分散小米/阿里/Rokid,單機未見 hit,恐把 ASP/margin 一起打下去。**綜合**:單位需求是真(故 結構),但「投資=穩賺」被 margin 壓縮、補貼依賴、true-AR 仍 太早 三點打臉。

## Sources
1. EssilorLuxottica — Q4/FY2025 Results Press Release (rev €28.49B +11.2% cc; adj op profit €4.5B; FCF €2.8B; >7M smart glasses, >3× YoY) — https://www.essilorluxottica.com/cap/content/283060/ — retrieved 2026-05-31 — grade A — primary-fetched
2. IDC via PYMNTS — Apple Retreats on Vision Pro (45k Q4-2025 vs 390k FY2024; marketing cut >95%) — https://www.pymnts.com/apple/2026/apple-retreats-on-vision-pro-as-consumer-demand-falls-short/ — retrieved 2026-05-31 — grade A
3. Counterpoint Research — Global Smart Glasses Shipments Grew 139% YoY in H2 2025; Meta 82% share — https://counterpointresearch.com/en/insights/Global-Smart-Glasses-Shipments-Grew-139-Percent-YoY-in-H2-2025 — retrieved 2026-05-31 — grade B — primary-fetched
4. KGOnTech (Karl Guttag) — Meta Ray-Ban Display Part 1: Lumus Waveguide, OmniVision LCoS, Goertek Engine (20° FOV, 600×600, 5,000 nits, 0.38W, geometric 3-7× efficiency) — https://kguttag.com/2025/10/30/meta-ray-ban-display-part-1-lumus-waveguide-omnivision-lcos-and-goertek-projection-engine/ — retrieved 2026-05-31 — grade A — primary-fetched
5. iFixit / Hackaday — Groundbreaking Waveguide Tech Inside Meta's $800 AR Glasses (Lumus geometric, Schott glass, likely sold at a loss) — https://hackaday.com/2025/10/09/the-fascinating-waveguide-technology-inside-metas-ray-ban-display-glasses/ — retrieved 2026-05-31 — grade B
6. Nature Photonics 2025 / arXiv 2401.06900 — Synthetic aperture waveguide holography; etendue conservation limits FOV×eyebox×brightness; TIR critical-angle FOV cap — https://www.nature.com/articles/s41566-025-01718-w — retrieved 2026-05-31 — grade A
7. UploadVR — Meta & EssilorLuxottica Sold 7 Million Smart Glasses In 2025 (~9M cumulative since 2023) — https://www.uploadvr.com/meta-essilorluxottica-sold-7-million-smart-glasses-in-2025/ — retrieved 2026-05-31 — grade B
8. CNBC — Ray-Ban maker EssilorLuxottica more than tripled Meta AI glasses sales in 2025 (capacity to 10M by 2026) — https://www.cnbc.com/2026/02/11/ray-ban-maker-essilorluxottica-triples-sales-of-meta-ai-glasses.html — retrieved 2026-05-31 — grade B
9. Bloomberg — Meta and EssilorLuxottica Spar Over Ray-Ban AI Glasses Pricing (adj gross margin −2.6pp to 60.9%; pricing/strategy tension) — https://www.bloomberg.com/news/features/2026-02-24/meta-and-essilorluxottica-spar-over-ray-ban-ai-glasses-pricing — retrieved 2026-05-31 — grade B
10. Auganix / Meta FY2025 10-K (SEC ARS) — Reality Labs ~$19.19B FY2025 operating loss; 2026 similar — https://www.auganix.org/xr-news-meta-reality-labs-2025-financial-report/ — retrieved 2026-05-31 — grade B (primary: https://www.sec.gov/Archives/edgar/data/1326801/000162828026025534/meta-12312025x10kars.htm — A)
11. Meta Store Blog — Meta Ray-Ban Display launched $799, 2025-09-30, w/ Neural Band (6h mixed-use, 30h w/ case) — https://www.meta.com/blog/meta-ray-ban-display-ai-glasses-connect-2025/ — retrieved 2026-05-31 — grade A
12. Modaes / Nasdaq — Meta acquires ~3% of EssilorLuxottica for €3B (2024); may raise to 5% — https://www.nasdaq.com/articles/meta-holds-about-3-stake-essilorluxottica-reports — retrieved 2026-05-31 — grade B
13. RoadtoVR — Snap & Qualcomm partnership, 2026 'Specs' consumer AR ($2,500; Snapdragon multi-chip +2.5× AI, −50% power vs XR2 Gen1) — https://www.roadtovr.com/snap-qualcomm-partnership-specs-2026-ar-glasses/ — retrieved 2026-05-31 — grade C
14. blog.google — Android XR intelligent eyewear w/ Gemini (audio + display glasses; Gentle Monster, Warby Parker; Samsung Galaxy XR $1,800) — https://blog.google/products-and-platforms/platforms/android/android-xr-io-2026/ — retrieved 2026-05-31 — grade B
15. MicroLED-Info / PanoxDisplay — JBD micro-LED (2.5µm, 2025 sampling), Porotech native-red InGaN; Sony ECX350F micro-OLED 10,000 nits; AR brightness 3,000–10,000 nits outdoor — https://www.microled-info.com/jbd — retrieved 2026-05-31 — grade B
16. macaonews / 36kr — China AI glasses ~950k units 2025 (35× YoY); Xiaomi 32% / Rokid 29% / Alibaba 16%; Quark G1 ¥1,899 / S1 ¥3,799 — https://macaonews.org/features/ai-glasses-china-brands-driving-sales-surge/ — retrieved 2026-05-31 — grade C
