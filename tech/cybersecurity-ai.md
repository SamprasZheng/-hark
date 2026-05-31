---
type: synthesis
domain: tech-trend
tags: [cybersecurity, ai-security, platform-consolidation, agentic-soc, edr-xdr, sase, zero-trust, identity, non-human-identity, pqc, crwd, panw, zs, ftnt, net, okta, s, msft, winners-losers]
phase: C
as_of: 2026-05-31T04:30:00+08:00
author_role: researcher
confidence: 0.74
verdict: 結構
verdict_by_horizon: {T0: 結構, T1: 質變, T2: 質變, T3: 結構}
rubric: {A1: 2, A2: 2, A3: 2, A4: 1, A5: 1}
sources_grade_summary: "A: 9  B: 8  C: 5  D: 0  E: 0"
cross_interact: [ai-eats-software, quantum-vs-bitcoin, model-leadership-and-data]
---
# 資安 × AI — 平台整併 vs 自主 SOC / Cybersecurity in the AI Era

## 0. 判決 + Desk View / Verdict
**結構 (structural, conf 0.74)**，但要拆成三條相位不同的曲線。**(A) 平台整併 = 現在進行式的結構**：CrowdStrike FY2026 ARR 衝到 **$5.25B (+24% YoY)**，成為首家破 $5B 的純資安軟體公司 [CRWD FY2026 — fool.com transcript — retrieved 2026-05-31 — grade B — cross-confirmed];Palo Alto 的「platformization」把 NGS ARR 推到 **$6.33B (+33% YoY, Q2 FY2026)**，並用 $25B 併 CyberArk 正式踩進身分安全 [PANW Q2 FY26 — futurumgroup — retrieved 2026-05-31 — grade B — cross-confirmed][CyberArk deal — paloaltonetworks.com — grade A — primary-fetched]。**(B) Agentic SOC（自主資安分析師）= T1–T2 的質變**:CRWD Charlotte AI 用量年增 6×、相關 ARR 翻三倍;Microsoft 的 Security Copilot 報出 MTTR 降 30%——但 GA 產品多在 2025–26 才放量,真實 P&L 占比仍小 [CRWD FY26 — grade B][MS agentic SOC — microsoft.com — grade B]。**(C) AI 代理人的身分(machine/agent identity)= 剛萌芽**:非人類身分(NHI)已以 40–100:1 壓過人類帳號,78% 組織沒有 AI 身分政策——攻擊面正在爆炸,但變現載體尚未定型 [NHI crisis — IANS/Token — grade C]。Desk view:**資安是「攻擊面擴張 > AI 商品化偵測」的少數淨受益題目**——AI 同時放大攻擊(80%+ 攻擊已用 AI,deepfake vishing Q1'25 +1600%)與防禦,但攻擊面隨 AI 代理、雲、機器身分指數成長,結構性把資安支出往上推(Gartner 2026 資安支出 $240B,+12.5%)[Gartner 2026 — grade A]。這與 [[ai-eats-software]] 的「薄 SaaS 被吃」相反:資安的工作量(alert、身分、攻擊面)正在被 AI **做大**而非做小。**最大盲點**:同溫層把 CRWD/PANW 的勝利當信仰,卻忽略 (1) Microsoft 用 bundle 從 $20B+ 安全營收往上輾壓專業廠的毛利;(2) 平台龍頭遠期估值(CRWD ~20× 營收)已把數年整併定價;(3) CrowdStrike 自己 2024-07 的全球當機事件證明「單一 kernel agent = 系統性風險」,Delta 求償 $500M 的訴訟仍在進行——資安龍頭自身就是 tail risk [CRWD-Delta — CNBC/ITPro — grade B]。

## 1. 技術底蘊 / Technical moat (A1) — EDR→XDR→agentic、SASE/zero-trust
三條技術主軸正在重寫資安架構。**(1) 端點偵測的演進鏈 EDR→XDR→agentic SOC**:從單點端點偵測(EDR)→跨層關聯(XDR)→現在的「自主分析師」(agentic SOC),AI 代理人能自動 triage、調查、跨環境關聯證據並執行回應,而非執行固定 playbook [Omdia agentic SOC — grade C]。Microsoft 2026-04 直接喊「the agentic SOC」是 SecOps 未來十年的重寫,Google Cloud、CRWD(Charlotte AI)、Torq(2026-01 Series D $140M @ $1.2B unicorn)全押這條 [MS agentic SOC — microsoft.com — grade B]。**(2) 架構從邊界轉向 SASE/zero-trust**:Zscaler/Cloudflare 把安全從「資料中心邊界」搬到「雲端身分閘道」,Gartner 報雲端安全是 2026 成長最快子類(+28.8%)[Gartner 2026 — grade A]。**(3) 平台化 = 把點工具縫成 OS**:PANW 三平台(Strata 網路、Prisma 雲/SASE、Cortex AI-SOC)靠 ~33 筆併購組成,用 bundle 逼客戶整併到單一供應商 [PANW platformization — futurumgroup — grade B]。**A1=2**:技術底蘊真實且難複製(資料規模 + 單一 agent 通路 + 整併飛輪),但要注意——agentic 偵測本身正被多家同時做,「AI 偵測」會逐步商品化,真正的護城河是**遙測資料規模 + 端點安裝基數 + 整併後的鎖定**,不是模型本身(呼應 [[model-leadership-and-data]]:價值在資料/通路非模型)。

## 2. 需求數據 / Demand reality (A2) — ARR/seats/breach cost（標 Q/FY）
| 指標 metric | 數值 value | 期間 period | 來源 source (grade — verification) |
|---|---|---|---|
| Gartner 全球資安支出 | **$240B (+12.5%)**;2025 = $213B | FY2026 forecast | Gartner / LinkedIn-Columbus (A — cross-confirmed) |
| CrowdStrike ending ARR | **$5.25B (+24% YoY)** | FY2026 (1/31/26) | CRWD IR/transcript (B — cross-confirmed) |
| CRWD 淨新增 ARR | Q4 **$331M (+47%)**;FY **$1.01B (+25%)** | Q4 / FY2026 | CRWD transcript (B — cross-confirmed) |
| CRWD 營收 / DBNR / 毛留存 | Q4 $1.31B (+23%);DBNR 115%;GRR 97% | Q4 FY2026 | CRWD transcript (B — cross-confirmed) |
| CRWD Falcon Flex ARR | **$1.69B (+120%+)**;Charlotte 用量 6×、ARR 3× | FY2026 | CRWD transcript (B — single-source-pending) |
| Palo Alto NGS ARR | **$6.33B (+33% YoY)** | Q2 FY2026 | PANW slides/Futurum (B — cross-confirmed) |
| PANW NGS ARR 指引 | $8.52–8.62B(+53–54%);**含 CyberArk+Chronosphere ~$1.47B** | FY2026 guide | Investing.com/PANW (B — cross-confirmed) |
| Zscaler ARR / 營收 | ARR **$3.525B (+25%)**;營收 $850.5M (+25%) | Q3 FY2026 | ZS 8-K/CNBC (A — primary-fetched) |
| ZS 有機 ARR(扣 Red Canary) | $3.398B (+21%);Red Canary 貢獻 $127M ARR | Q3 FY2026 | ZS 8-K (A — primary) |
| Fortinet 營收 / billings | 營收 **$1.85B (+20%)**;billings $2.09B (+31%) | Q1 2026 | FTNT PR (A — primary) |
| Cloudflare 營收 / RPO | 營收 **$639.8M (+34%)**;RPO $2.543B (+36%);>$100K 客戶 +25% | Q1 2026 | NET 10-Q/StockTitan (A — cross-confirmed) |
| SentinelOne ARR / 營收 | ARR **$1.119B (+22%)**;FY 營收 $1.001B (+22%) | Q4 FY2026 (1/31/26) | S PR/8-K (A — primary) |
| Okta 營收 | $765M (+11%);訂閱 $750M (+11%);FY27 指引 +9–10% | Q1 FY2027 (4/30/26) | OKTA 8-K (A — primary) |
| Microsoft 安全營收 | $20B+(里程碑);analyst 估 FY2025 ~$37B(~14% 營收) | FY2023→FY2025 | Cybersecurity Dive (A) / Investing.com 分析 (C) |
| AI 相關資料外洩平均成本 | **$5.72M**(+13% YoY);全球均值 $4.44M(五年首降) | 2025 | IBM/secondaries (B — cross-confirmed) |
| AI 攻擊普及 / deepfake vishing | 80%+ 攻擊用 AI;deepfake vishing Q1'25 **+1600%** | 2025 | sqmagazine/right-hand (C) |

**A2=2**:需求是已認列營收 + 已簽 ARR,不是 survey-intent。平台龍頭 ARR 普遍 +20–33% 且 CRWD 淨新增 ARR 首破 $1B、DBNR 115%——擴張真實。**但三個 Q/FY 警示**:(i) PANW 的 NGS ARR 從 $6.33B 跳到指引 $8.5B+ 有 **~$1.47B 來自 CyberArk/Chronosphere 併購**,不是純有機;(ii) ZS 的 ARR +25% 裡有 Red Canary($127M)的無機貢獻,有機只有 +21%;(iii) Microsoft 安全營收的 $20B 是 FY2023 官方里程碑(A 級),~$37B(FY2025)是 **C 級分析師估算**,因為 MSFT 不單獨揭露安全 line item——兩者差距大,標 `contradicted` 待解。

## 3. 資金與權威 / Capital & authority (A3)
**權威支出背書**:Gartner 把 2026 資安支出抬到 **$240B(+12.5%)**,雲端安全 +28.8% 為最快子類,驅動力明列為 AI 攻擊、勒索升級、新法規(CMMC 2.0、CIRCIA)[Gartner 2026 — grade A — cross-confirmed]。**法規強制需求(PQC)**:NIST 2024-08 定稿後量子標準(ML-KEM/ML-DSA),NSA CNSA 2.0 + 行政命令 EO 14144 設定**強制時程**——2027-01 新採購須量子抗性、2030 網路設備、2033 OS/雲、2035 全面 [NIST/CNSA 2.0 — qusecure/thequantuminsider — grade B — cross-confirmed],這是政府用法令創造的需求,直接連 [[quantum-vs-bitcoin]] 的 PQC 遷移市場。**民間資本**:資安 AI 新創熱錢明顯——Torq Series D **$140M @ $1.2B**(2026-01,agentic SOC unicorn)[Torq — stellarcyber — grade C];**M&A 整併潮**:PANW 砸 **$25B 併 CyberArk**(2025-07-30,formal entry into identity,$45 現金 + 2.2005 股)[CyberArk — paloaltonetworks.com — grade A — primary-fetched],ZS 併 Red Canary、PANW 併 Chronosphere——平台龍頭用併購把點工具收編。**A3=2**:支出(Gartner)、法規(NIST/NSA 強制時程)、資本(M&A + VC)三重背書齊備,是本 cluster 最硬的證據;尤其 PQC 是少數「政府用 deadline 強制買單」的結構需求。

## 4. 受益 / 受損 / 抄底 / Beneficiaries (A4)
- **結構受益(平台整併者,已確認)**:**CrowdStrike(CRWD)**——ARR $5.25B、淨新增 ARR 首破 $1B、FCF 利潤率 26%,單一 agent + 模組交叉銷售(Falcon Flex ARR +120%)的飛輪最強;**Palo Alto(PANW)**——platformization + CyberArk 把網路/雲/SASE/身分/AI-SOC 縫成一站式;**Cloudflare(NET)**——+34% 營收、邊緣安全 + zero-trust,但 Q1'26 宣布裁 20% 人力(效率轉骨)[NET Q1'26 — TIKR — grade B]。**Fortinet(FTNT)**——billings +31%、防火牆換機 + SASE,硬體 + 軟體雙引擎,估值最便宜的大型整併者。
- **被結構威脅(legacy / point-solution / seat-based)**:單一功能點工具廠(被平台 bundle 收編或邊緣化);傳統簽章式防毒;以及「一個 AI 代理人取代多個分析師席位」時,**seat-based 定價的 SOC 工具**面臨與 [[ai-eats-software]] 同款的 seat→outcome 重訂價壓力。
- **方向對但 bundle 受壓**:**Microsoft Security**——安全營收 $20B+(可能 ~$37B FY25),用 E5 bundle 近零 CAC 輾壓,是專業廠最大的**毛利**威脅(不是技術威脅);專業廠的反擊是「best-of-breed + 跨雲中立」。
- **抄底候選(turnaround,高風險)**:**Okta(OKTA)**——身分龍頭但成長砍到 FY27 +9–10%,管理層開 **$1B 回購**喊「股價被低估」;若 agent identity(NHI 治理)需求接棒,身分層可能重新加速——但這是「成長已失速、賭再加速」的逆向倉 [OKTA FY27 — okta-8K — grade A — primary]。**SentinelOne(S)**——2025 股價 −32.4%、2026 再跌,2026-05 裁員轉骨拚 path-to-profitability,剛破 $1B 營收但成長落後 CRWD;典型「流血成長股 → 賭轉骨」的深度逆向,**未確認觸底**,風險高 [S 2026 — Motley Fool/CNBC — grade B]。
- **A4=1**:節點清楚(CRWD/PANW/NET/FTNT 是確定的整併贏家),但**最性感的龍頭估值已先行**(CRWD ~20× 營收已把整併定價),抄底股(OKTA/S)又**未確認觸底**——可投資性被「贏家貴、便宜的沒觸底」的剪刀差壓抑。

## 5. 多時程 / Multi-horizon
- **T0(now)結構**:平台整併已落地——CRWD ARR $5.25B、PANW platformization、Gartner $240B 支出全是**現在式**;這是真實但已被定價的結構。
- **T1(1–3y)質變**:agentic SOC 從「demo + 早期 ARR」走向標準配備(Omdia 估 1–2 年內成 CISO 標準,73% 已用或開發中);AI 攻擊規模化(deepfake、自動化釣魚)把資安支出再往上推;**自主分析師正式重寫 SecOps 成本結構**。
- **T2(3–5y)質變**:AI 代理人身分(NHI/agent identity)成為治理剛需(身分=agentic AI 的控制平面);PQC 遷移進入 2030 網路設備強制期,密碼學被「從地基重建」。
- **T3(5–10y)結構**:攻防 AI 軍備競賽進入新均衡——攻擊面隨 AI 代理持續擴張,但偵測商品化壓低單點定價;價值集中於少數握有遙測資料 + 通路 + 整併鎖定的平台。**裁決:結構(T0)→ 質變(T1–T2,agentic SOC + agent identity)→ 結構(T3,新均衡)。**

## 6. 爆發條件 + 里程碑階梯 / Milestone ladder
1. **PANW platformization ARR 是否如指引兌現**。verify:PANW Q3/Q4 FY2026 8-K 的 NGS ARR vs $8.52–8.62B 指引,且**扣除 CyberArk/Chronosphere ~$1.47B 後的有機數**。status:Q2 FY26 NGS ARR $6.33B(+33%),指引含大量無機。next check:Q3 FY2026 財報(~2026-08)。
2. **Agentic SOC 產品 GA + 採用率**。verify:CRWD Charlotte AI / MS Security Copilot / Google 的付費 ARR 與部署數;73% 「使用或開發中」是否轉成已付費。status:Charlotte 用量 6×、ARR 3×(基數小);MS 報 MTTR −30%。next check:各家 FY2026 下半年財報的 agentic ARR 揭露。
3. **一次重大 AI 驅動的資安事件**(deepfake/agent 供應鏈大規模外洩)。verify:CISA/廠商事件報告 + IBM 年度 breach cost。status:2026-02 Moltbook 型 NHI 供應鏈外洩已現端倪;deepfake vishing Q1'25 +1600%。next check:IBM Cost of a Data Breach 2026 版 + 重大事件揭露。
4. **PQC 強制時程是否真正咬合**。verify:NSS 2027-01 新採購量子抗性落地率、FIPS 203/204/205 採用、廠商 PQC 產品出貨。status:NIST 標準已定稿(2024-08),CNSA 2.0 時程在跑(2027/2030/2033/2035)。next check:2027-01 首道強制門檻執行率。
5. **CRWD 當機事件的 echo / 訴訟結果**。verify:Delta v. CrowdStrike 判決或和解金額、是否再有大規模 agent 當機。status:Delta 求償 $500M,法院准其推進過失/電腦侵入主張,訴訟進行中。next check:訴訟里程碑 + CRWD 是否再出包。
6. **抄底股觸底訊號(OKTA/S)**。verify:OKTA NRR 是否止跌回升、agent identity 是否帶動再加速;S 轉骨後營益率轉正 + 成長止跌。status:OKTA FY27 指引 +9–10% 仍在減速;S 裁員拚轉骨未確認觸底。next check:OKTA/S 接下來兩季財報。

## 7. 時代影響與交互 / Era-impact & synergies
這是 **AI 攻防軍備競賽 + 平台整併 + 身分重構** 的三向收斂:資安從「邊界防禦 + 點工具堆疊」變成「自主 SOC + 單一遙測平台 + 機器/代理身分治理」。與其他 cluster 的交互:
- [[ai-eats-software]] — **核心張力**:資安是被 AI 吃還是 AI-proof?判決偏 **AI-proof / 受益**——AI 把攻擊面(代理、雲、機器身分)做**大**,工作量上升 → 支出上升(Gartner +12.5%),與薄 SaaS 被吃相反;但 seat-based SOC 工具仍面臨 seat→outcome 重訂價,且「AI 偵測」會逐步商品化,故不是無條件免疫。
- [[quantum-vs-bitcoin]] — **PQC 遷移市場**:NIST/NSA 的 2030–2035 強制時程創造一個政府買單的密碼學重建市場(2025 ~$0.4–1.7B → 2030–34 高個位數至數十億美元,各家估值分歧大);這是 quantum 主題在資安的**可投資**落點。
- [[model-leadership-and-data]] — agentic SOC 的護城河是**遙測資料規模 + 通路**,不是模型本身;模型是上游燃料,價值沉澱在握有端點資料 + 安裝基數 + 整併鎖定的平台(與「價值從模型遷移到資料/工作流」同構)。

## 8. 同溫層 + 自我打臉 / Echo-chamber + self-rebuttal
**同溫層 gap**:X/retail 把「CRWD/PANW = 資安必勝」當信仰,但 (1) 這些龍頭的整併勝利**已被定價**(CRWD ~20× 遠期營收已把數年成長吃進去)——買對賽道 ≠ 買對價格;(2) **Microsoft 的 bundle 威脅被低估**——$20B+(可能 ~$37B)安全營收用 E5 近零 CAC 輾壓,專業廠面臨的是**毛利侵蝕**而非市占消滅,這條同溫層很少談;(3) 「agentic SOC 馬上取代分析師」被誇大——MS 報 MTTR −30% 是輔助不是取代,且 [[ai-eats-software]] 引用的 MIT NANDA「95% GenAI pilot 無 P&L 效果」同樣適用於資安 AI,多數仍是 intent。**自我打臉(打我自己的 bull case)**:(a) **資安 AI-proof 論的裂縫**——若 agentic 偵測商品化夠快,點工具偵測的定價權會被壓縮,「攻擊面變大 = 支出變大」可能被「單位偵測成本崩跌」抵銷,淨支出未必線性上升;(b) **CRWD 當機事件**證明單一 kernel-level agent = 系統性 tail risk,Delta $500M 訴訟若判賠,龍頭的「安裝基數護城河」反成負債;(c) **PANW/ZS 的 ARR 成長有無機灌水**(CyberArk $1.47B、Red Canary $127M),扣掉後有機成長明顯較慢,別把 M&A 當有機質變;(d) **PQC 市場各家估值分歧 10×+**($0.4B vs $1.7B 2025 基數),且強制 deadline 常被展延,別把 announce 當 booked;(e) **抄底股(OKTA/S)是 value trap 風險**——成長失速 + 未確認觸底,$1B 回購/裁員是管理層信號不是基本面拐點。**淨判決維持結構,但嚴格分開「整併贏家」與「其股價」(前者確定、龍頭已透支),並把 agentic SOC 的質變定在 T1–T2 而非 now。**

## Sources
1. Gartner 2026 information security spending $240B (+12.5%), cloud security +28.8% — https://www.gartner.com/en/newsroom/press-releases/2025-07-29-gartner-forecasts-worldwide-end-user-spending-on-information-security-to-total-213-billion-us-dollars-in-2025 — retrieved 2026-05-31 — grade A — cross-confirmed
2. CrowdStrike Q4/FY2026 results (ARR $5.25B, net new ARR, DBNR, FCF, Charlotte AI, Falcon Flex) — https://www.fool.com/earnings/call-transcripts/2026/03/03/crowdstrike-crwd-q4-2026-earnings-transcript/ — retrieved 2026-05-31 — grade B — cross-confirmed
3. CrowdStrike Q4 FY2026 IR press release (ARR/revenue/retention) — https://ir.crowdstrike.com/news-releases/news-release-details/crowdstrike-reports-fourth-quarter-and-fiscal-year-2026 — retrieved 2026-05-31 — grade A — single-source-pending (IR page timed out; figures cross-confirmed via transcript)
4. Palo Alto Networks Q2 FY2026 (NGS ARR $6.33B +33%, platformization) — https://futurumgroup.com/insights/palo-alto-networks-q2-fy-2026-arr-accelerates-as-platform-strategy-scales/ — retrieved 2026-05-31 — grade B — cross-confirmed
5. PANW Q2 FY2026 slides / Q3 + FY26 NGS ARR guidance incl. CyberArk+Chronosphere ~$1.47B — https://www.investing.com/news/company-news/palo-alto-networks-q2-2026-slides-ngs-arr-jumps-33-stock-falls-5-93CH-4511827 — retrieved 2026-05-31 — grade B — cross-confirmed
6. PANW $25B acquisition of CyberArk (identity security, formal entry) — https://www.paloaltonetworks.com/company/press/2025/palo-alto-networks-announces-agreement-to-acquire-cyberark--the-identity-security-leader — retrieved 2026-05-31 — grade A — primary-fetched
7. Zscaler Q3 FY2026 8-K (ARR $3.525B +25%, organic +21%, Red Canary $127M) — https://www.sec.gov/Archives/edgar/data/0001713683/000171368326000095/zs-04302026_991.htm — retrieved 2026-05-31 — grade A — primary-fetched
8. Fortinet Q1 2026 results (revenue $1.85B +20%, billings $2.09B +31%) — https://www.fortinet.com/corporate/about-us/newsroom/press-releases/2026/fortinet-reports-first-quarter-2026-financial-results — retrieved 2026-05-31 — grade A — primary-fetched
9. Cloudflare Q1 2026 (revenue $639.8M +34%, RPO $2.543B, 20% layoff) — https://www.stocktitan.net/sec-filings/NET/10-q-cloudflare-inc-quarterly-earnings-report-580158f0de78.html — retrieved 2026-05-31 — grade A — cross-confirmed
10. SentinelOne Q4 FY2026 (ARR $1.119B +22%, FY rev $1.001B) + stock decline/restructuring — https://www.stocktitan.net/sec-filings/S/8-k-sentinel-one-inc-reports-material-event-d6ac7b1bc0e4.html — retrieved 2026-05-31 — grade A — cross-confirmed
11. SentinelOne 2025 −32.4%, 2026 layoffs/turnaround — https://www.cnbc.com/2026/05/29/sentinelone-s-stock-earnings-ai-layoffs.html — retrieved 2026-05-31 — grade B — cross-confirmed
12. Okta Q1 FY2027 (rev $765M +11%, FY27 guide +9–10%, $1B buyback) — https://www.sec.gov/Archives/edgar/data/0001660134/000166013426000050/okta-4302026_ex991.htm — retrieved 2026-05-31 — grade A — primary-fetched
13. Microsoft Security surpasses $20B revenue (FY2023 milestone) — https://www.cybersecuritydive.com/news/microsoft-20b-security-revenue/641498/ — retrieved 2026-05-31 — grade A — cross-confirmed
14. Microsoft security ~$37B FY2025 analyst estimate (~14% of revenue) — https://www.investing.com/analysis/microsoft-why-its-security-business-rivals-crowdstrike-and-palo-alto-200665840 — retrieved 2026-05-31 — grade C — single-source-pending (contradicts #13 scope; MSFT no separate line item)
15. Microsoft "the agentic SOC" + Security Copilot MTTR −30% — https://www.microsoft.com/en-us/security/blog/2026/04/09/the-agentic-soc-rethinking-secops-for-the-next-decade/ — retrieved 2026-05-31 — grade B — single-source-pending
16. Agentic SOC market (Omdia 1–2y to standard, 73% adopting, Torq $140M/$1.2B) — https://omdia.tech.informa.com/blogs/2025/nov/the-agentic-soc-secops-evolution-into-agentic-platforms — retrieved 2026-05-31 — grade C — single-source-pending
17. IBM Cost of a Data Breach 2025 (global $4.44M; AI breach $5.72M; shadow AI +$670K) — https://www.ibm.com/reports/data-breach — retrieved 2026-05-31 — grade B — cross-confirmed
18. AI cyberattack stats (80%+ use AI; deepfake vishing Q1'25 +1600%) — https://deepstrike.io/blog/ai-cyber-attack-statistics-2025 — retrieved 2026-05-31 — grade C — single-source-pending
19. Non-human / agent identity crisis (40–100:1, 78% no AI-identity policy) — https://www.iansresearch.com/resources/all-blogs/post/security-blog/2026/02/24/ai-agents-are-creating-an-identity-security-crisis-in-2026 — retrieved 2026-05-31 — grade C — single-source-pending
20. NIST PQC standards + CNSA 2.0 deadlines (2027/2030/2033/2035) — https://www.qusecure.com/cnsa-2-0-pqc-requirements-timelines-federal-impact/ — retrieved 2026-05-31 — grade B — cross-confirmed
21. CrowdStrike–Delta outage litigation ($500M claim, ongoing) — https://www.cnbc.com/2024/10/25/delta-suit-against-crowdstrike-after-it-outage-caused-cancellations.html — retrieved 2026-05-31 — grade B — cross-confirmed
22. PQC market size forecasts (range $0.4–1.7B 2025 → high-single-digit to ~$30B 2030–34) — https://www.marketsandmarkets.com/Market-Reports/post-quantum-cryptography-market-126986626.html — retrieved 2026-05-31 — grade C — contradicted (wide methodology spread)
