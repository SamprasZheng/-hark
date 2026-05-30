---
type: synthesis
domain: tech-trend
tags: [cpo, supply-chain, second-derivative, optical, bottleneck]
as_of_timestamp: 2026-05-31T01:15:00+08:00
author_role: researcher
confidence: 0.6
parent: "[[optical-interconnect-cpo]]"
sources_grade_summary: "A: 5 B: 4 C: 4 D: 1 E: 0"
---
# CPO/光互連 二階供應鏈深掘 / Optical second-derivative deep-dive

## 0. 一句話 / What this adds beyond the parent page
The parent [[optical-interconnect-cpo]] establishes *that* InP substrate + CW/EML laser are the chokepoints. This page goes one layer deeper and ranks the **un-crowded** pick-and-shovel nodes per [[../philosophy/concepts/serenity-supply-chain-bottleneck]], and—crucially—surfaces the node the CPO narrative ignores entirely: **hybrid-bonding metrology**, where CPO and the HBM4 supercycle ([[memory-supercycle]]) demand the *same* tool from the *same* ~3-4 vendors. The single most actionable insight: the loudest InP/test names (AXTI, AEHR) are already parabolic froth, while the *equipment* and *metrology* layer that must scale to make any of it ship is still priced like a normal cap-equipment cycle.

## 1. 節點排名表 / Ranked bottleneck nodes
| 節點 | 代表公司+ticker | 供需/產能/ASP/前置期數據(grade) | 二供難度=定價權 | 擁擠度 |
|---|---|---|---|---|
| **InP 基板** | Sumitomo 8053.T, AXT AXTI, NTT(unlisted) | 2025 需求 ~2M vs 產能 ~600k = **~70% 缺口** [S1]B; 4家 >95% 全球產能 [S1]B | 極高（單晶良率低、>2yr 認證） | **混合**: AXTI 已拋物線, Sumitomo 未擁擠 |
| **CW/EML 雷射** | Lumentum LITE, Coherent COHR, Furukawa 5801.T | EML <5 供應商, 200G **缺口 36%**, lead time **>2027** [S2]B; NVIDIA $4B 鎖定 [S2]B | 極高（NVIDIA 包產能） | 偏擁擠（LITE/COHR backlog 已到 2028） |
| **混合鍵合量測** | Auros 322310.KQ, Onto ONTO, Camtek CAMT | HBM4 hybrid-bond overlay 是新需求；KLA HBM3E 近壟斷但難快速補位 [S3]C; Onto Dragonfly G5 2026 +>50% [S6]B | 高（換線成本逐步累積） | **未擁擠**（CPO 敘事沒提到） |
| **光學晶圓燒機/探針** | AEHR, FormFactor FORM | AEHR FY26 rev **$45-50M**, book-to-bill **3.5×** [S7]A; FORM CPO 2026 rev 上看 **$10-20M** 高端 [S8]B | 中-高（製程鎖定） | **混合**: AEHR 已拋物線(+~5000%/1y), FORM 未擁擠 |
| **InP 磊晶代工** | Landmark 3081.TWO, VPEC 2455.TW, IntelliEPI | EML 級 InP epi 良率關鍵；CPO/DFB 基底晶圓 [S9]C | 中（少數能做 defect-free epi） | 未擁擠（小型、流動性差） |
| **耦合/組裝/測試設備** | ASMPT 0522.HK, All Ring 6187.TWO, Fabrinet FN | ASMPT sub-micron CPO 鍵合機 (AMICRA) [S4]B; FN Q3-26 rev **$1.21B**, DCI +90% YoY [S5]A | 中（精度門檻高但多供應商） | 未擁擠（ASMPT/FN 估值溫和） |

## 2. InP 基板 / InP substrate
深度低於雷射的真瓶頸。2025 全球 InP 需求約 **2M 片 vs 產能僅 ~600k 片，缺口近 70%**；Sumitomo (8053.T)、AXT、II-VI、JX Metals 四家合計 **>95% 全球產能**，order book **滿到 2026 以後** [S1]B。份額需校正母頁：Sumitomo **~60%**(部分資料 ~42%/~800k 片產能)、AXT **~35%**（西方商用龍頭，非 60-70%）[S1]B[S10]C。AXT Q1-26 營收僅 **$26.9M**(+39% YoY)、InP backlog **$100M**、毛利率跳升至 **29.9%**(前季 21.5%)、目標 2026 底季產能 **$35M**、2027/28 **$65-70M** [S10]C[S11]A。技術轉折：4吋→**6吋** InP（AXT 已量產 6吋，每片 >400 顆晶粒）是降本關鍵，也是中國(Xinyao/九峰山)切入點，CEO 稱 China 2030 上看全球 **30%** [S1]B。**Sumitomo 是未擁擠者**（大型、垂直整合自用 EML，股價未拋物線）；AXTI 是已拋物線者（見 §6）。

## 3. CW 雷射 / EML
全球 **<5 家** 商用 EML：Lumentum、Coherent、Mitsubishi、Sumitomo、Broadcom [S2]B。200G EML **缺口 36%**、2026 雙位數漲價、**Lumentum 是唯一量產 200G/lane 者**（1.6T 必需件）[S2]B。McKinsey：800G transceiver **2027 前短缺 40-60%**、1.6T **2029 前短缺 30-40%** [S2]B。NVIDIA $4B（$2B Lumentum + $2B Coherent, 2026-03-02）把非-NVIDIA 買家 lead time 推到 **2027 之後**；光纖 lead time 大買家 20 週、小買家近一年 [S2]B。台日小型純玩：**Furukawa 5801.T**（DFB CW，+500% 產能到 2028）、磊晶端 **Landmark 3081.TWO / VPEC 2455.TW / IntelliEPI**。定價權極高但**已偏擁擠**（LITE/COHR backlog 已喊到 2028）。

## 4. 量測 + 混合鍵合 / Metrology + hybrid bonding (HBM crossover)
**本頁最被忽略的節點。** HBM4 / HBM4e 從 micro-bump 轉向 **hybrid bonding**，需要全新的 **overlay/對準量測**——這正是 CPO 矽光子鍵合需要的同一類工具，HBM 與 CPO 在此**共用瓶頸**。
- **Auros 322310.KQ**（韓, 市值 ~**$269M**）：十年磨一劍的 hybrid-bond overlay 量測，同時在 Samsung + SK Hynix 認證；KLA HBM3E **近壟斷但無法快速/低價補位**新缺口；2026E EV/Rev **3.8×** vs 同業 9.2× [S3]C。**最純、最未被定價的二階節點**，但 grade-C(單一深度多頭分析)+ 流動性風險。
- **Onto ONTO**：Dragonfly G5 取得 2.5D AI 封裝 + HBM 2D/3D 認證，Q1-26 rev **$292M**，Dragonfly 2026 **+>50%** [S6]B。
- **Camtek CAMT**：2025 rev **$496.1M**(+16%, ~50% AI)，HBM4 參考量測工具；HBM4/CoWoS 整線量測資本可達 **$30-80M** [S12]C。
這層是「CPO 要出貨就必須先擴的產能」，卻不在 CPO 多頭名單裡。

## 5. 耦合/組裝/測試設備 / Coupling-assembly-test equipment
- **ASMPT 0522.HK**：OFC 2026 展出 **AMICRA NANO**（sub-micron CPO 鍵合）、NOVA、MEGA，同時做 TCB/hybrid bonding（HBM crossover）[S4]B。設備龍頭、估值溫和、**未擁擠**。
- **Fabrinet FN**：CPO/光模組代工，Q3-26 rev **$1.21B**(record)、Optical $889M(+35%)、**DCI +90% YoY**；$32M 入股 Raytec 切 CPO 封裝 [S5]A。
- **AEHR**（wafer-level burn-in 龍頭，矽光子 transceiver 燒機）+ **FormFactor FORM**（探針卡；併 Keystone Photonics，CPO 2026 rev 上看 $10-20M 高端，HBM probe card +>50% YoY）[S7]A[S8]B。
- **All Ring 6187.TWO**：自動化組裝設備，CPO 曝險屬籃子級、資料薄、流動性差——僅 watchlist。

## 6. 擁擠度 vs bubble_guard 對照 / Crowding cross-check
對照 [[../wiki/07_ai_bubble_audit]]：FOM bubble_guard 給 **AXTI 與 AEHR 最高泡沫壓力分 −95**（同組還有 MU/STX/WDC/SIMO 記憶體）[S13]內部。AXTI 過去一年 **~+5000%**、5/1 創 $96 新高、近期 ~$115（52週低 $1.45）[S14]C——故事 A 級、**估值 D 級**（$26.9M 營收 vs ~$50B 想像）。AEHR FY26 營收僅 **$45-50M** 卻 +~5000%/1y、rvol >1 [S7]A[S13]內部。**區分**：同樣 InP/test 主題，**已拋物線=AXTI、AEHR**；**結構但未擁擠=Sumitomo 8053.T(垂直整合自用)、ASMPT 0522.HK、FormFactor FORM、Onto ONTO、Auros 322310.KQ**——後者多在量測/設備層，股價未走到 vertical。母頁的 NVDA/TSM/AVGO bubble_guard 仍 ≥0，領導層與投機層結構分離 [S13]內部。

## 7. 同溫層風險 + 空方 / Echo-chamber + bear case
- **同溫層缺口**：CPO 多頭把 InP「缺口 70%」「EML 5 家」喊成顯學，但 **hybrid-bonding 量測**（Auros/Onto/Camtek）幾乎沒人連到 CPO——這是 AUTHORITY/CAPITAL 已動、ADOPTION-narrative 尚未跟上的**真正未擁擠**處；反之 AXTI/AEHR 是 narrative 已遠超基本面的反例。
- **空方**：(1) **缺口會自癒**——AXT 6吋量產 + 中國 Xinyao/九峰山 6吋過驗 + Sumitomo +40% 產能，2027 後 InP 缺口可能收斂，毀掉定價權（Serenity 失效條件：二供出現）[S1]B[S10]C。(2) **量測護城河可被 KLA 反撲**——Auros 的窗口靠 KLA「無法快速補位」，一旦 KLA 推 hybrid-bond overlay，$269M 小廠無還手之力 [S3]C。(3) **CPO 量產仍 ~2 年外**（母頁），設備/磊晶營收確認落在 2027-28；(4) 小型台日韓名（Landmark/All Ring/Auros）流動性與單客戶風險高，per [[../philosophy/concepts/serenity-supply-chain-bottleneck]] 僅能進 watchlist，不可單獨建倉。

## Sources
1. [Indium Phosphide Takes the Spotlight (Sumitomo 60% / AXT 35% / 70% deficit / China 30% by 2030) — eu.36kr.com/en/p/3651344579993989 — retrieved 2026-05-31 — grade B]
2. [AI Data Center Optical Component Shortage: Nvidia's $4B Laser Lockup (EML <5, 36% short, 200G, McKinsey 40-60%) — techtimes.com/articles/317281/20260527/ai-data-center-optical-component-shortage-nvidias-4b-laser-lockup-pushes-rivals-past-2027.htm — retrieved 2026-05-31 — grade B]
3. [$AUROS: The Last Unpriced Moat in the HBM4 Supply Chain (322310.KQ $269M, KLA gap, Samsung+SK Hynix qual, EV/Rev 3.8×) — threadingontheedge.substack.com/p/auros-the-last-unpriced-moat-in-the — retrieved 2026-05-31 — grade C]
4. [ASMPT at OFC 2026 — AMICRA NANO/NOVA, CPO + TCB/hybrid bonding — semi.asmpt.com/en/news-center/press-releases/asmpt-at-ofc-2026-los-angeles-enabling-scalable-co-packaged-optics-and-photonic-integration/ — retrieved 2026-05-31 — grade B]
5. [Fabrinet Q3 FY2026 8-K (rev $1.21B, Optical $889M +35%, DCI +90%, Raytec $32M) — sec.gov/Archives/edgar/data/0001408710/000140871026000014/fn-2026504xex991q326.htm — retrieved 2026-05-31 — grade A]
6. [Onto Innovation Q1-2026 8-K / Dragonfly G5 (rev $292M, Dragonfly +>50%, HBM 2D/3D + 2.5D qual) — sec.gov/Archives/edgar/data/0000704532/000119312526059380/onto-ex99_1.htm — retrieved 2026-05-31 — grade A]
7. [Aehr Test Systems FY2026 results / silicon-photonics WLBI ($45-50M rev, $37.2M bookings, 3.5× b-t-b) — aehr.com/2026/04/aehr-test-systems-reports-over-37-million-in-quarterly-bookings-driven-by-strong-ai-and-data-center-infrastructure-demand/ — retrieved 2026-05-31 — grade A]
8. [FormFactor Q1 2026 (rev $226.1M, HBM probe +>50%, Keystone Photonics, CPO $10-20M high-end) — finance.yahoo.com/markets/stocks/articles/formfactor-inc-q1-2026-earnings-001809274.html — retrieved 2026-05-31 — grade B]
9. [LandMark Optoelectronics (3081.TWO) InP/GaAs epi for CPO/DFB — grokipedia.com/page/LandMark_Optoelectronics_Corporation — retrieved 2026-05-31 — grade D]
10. [AXT Q1-2026 earnings detail (rev $26.9M, backlog $100M, GM 29.9%, $35M→$65-70M capacity, China 40%) — finance.biggo.com/news/US_AXTI_2026-04-30 — retrieved 2026-05-31 — grade C]
11. [AXT Inc Q1-2026 8-K (financials, $632.5M raise, 6-inch InP) — sec.gov/Archives/edgar/data/0001051627/000143774926014204/ex_906119.htm — retrieved 2026-05-31 — grade A]
12. [Camtek/Onto advanced-packaging metrology (CAMT 2025 $496.1M, HBM4 reference, $30-80M line capital) — semiconductorx.com/wlp-inspection-metrology.php — retrieved 2026-05-31 — grade C]
13. [$hark FOM bubble_guard — AXTI/AEHR −95 froth, NVDA/TSM/AVGO ≥0 — [[../wiki/07_ai_bubble_audit]] — retrieved 2026-05-31 — grade internal]
14. [AXTI stock price action (~+5000% 1y, $96 ATH 5/1, ~$115, 52w low $1.45) — investing.com/equities/axt-inc — retrieved 2026-05-31 — grade C]
