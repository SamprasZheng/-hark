---
type: plan
tags: [plan, annual, calendar, 2026h2, 2027h1, catalysts, policy, ipo, crypto, fed, congress, fact-checked]
as_of_timestamp: 2026-06-10
author_role: assistant-research
source: principal-directive + web-verified-catalysts (2026-06-10)
---

# 未來一年作戰行事曆 (2026-06 中 → 2027-06 中) — 標的 × 事件 × 操作 × 風險

> 主理人指令(2026-06-10):評估社會消息 / IPO / 政經 / FED / 營收 / 川普政策(Section 232、CHIPS、
> CLARITY),制定**未來一年每週標的 + 需關注數據 + 可能操作 + 可能事件 + 已知風險消化**;
> 點名:OpenAI IPO、BTC 減半週期、Pelosi 國會跟單。
>
> 本檔由 Claude 以「**本地系統現況 + 即時網路查證(2026-06-10)**」合成。recommend-only —— 系統只
> 建議、永不下單。**日期/事件以官方為準**;下方第 2 節催化劑已逐筆查證並附日期。

## 0. 與既有檔案的關係(承接、不重複)
- **W1–W13(6/中 → 9/中)細節**見 `weekly_plan_q3_2026.md`;本檔承接 **W14 → W52(9/中 → 2027/6/中)** 並補全年催化劑。
- 操作紀律/指令見 `playbook_master.md`、`deployment_plan_jun_sep_2026.md`。
- **政策維度(新)**:`thesis_policy_regime_2026.md` —— Section 232 / CHIPS-Intel / CLARITY / GENIUS / AI EO。
- **國會跟單(新)**:`thesis_congress_tracking.md` —— Pelosi / NANC 共振訊號。
- **數據抓取 schema(新)**:`raw/metadata/finviz_schema.json` —— Finviz 每週要拉的欄位。
- 題材論點:`thesis_2026_ipo_wave.md`、`spacex_ipo_2026_event.md`、`thesis_crypto_cycle_2026.md`、
  `thesis_agentic_payments.md`、`thesis_ecommerce_agentic.md`、`thesis_broadening_stealth.md`。

---

## 1. ⚠️ 查證後的事實校正(把幻覺擋在系統外)
> 你貼進來那份外部 AI 規劃有多處**過時/錯誤**;以下為 2026-06-10 網路查證後的修正,務必以此為準。

| 外部 plan 的說法 | 查證結果(2026-06-10) | 對操作的影響 |
|---|---|---|
| OpenAI/Anthropic「6 月初遞 S-1」 | ✅ **正確**:Anthropic 6/1、OpenAI 6/8 機密遞件;OpenAI 目標 ~9月掛、Anthropic ~10月 | IPO 代理佈局時序成立 |
| Anthropic 估值 $230–300B | ❌ **過時**:已是 **~$965B**(Series H,$65B),目標近兆 | 代理(AMZN 21% / GOOGL 14%)重估幅度更大 |
| 「xAI / X」獨立 IPO ~$113B | ❌ **錯**:xAI 已於 **2026-02 併入 SpaceX**;價值內含於 SPCX | 不存在獨立 xAI 標的;玩 SPCX/TSLA |
| SpaceX IPO「~6/12(主理人估)」 | ✅ **正確且即將發生**:S-1 5/20、roadshow 6/4、**6/11 盤後定價、6/12 那斯達克掛牌 SPCX,$135、$1.75T(史上最大)** | 本週 W1 頭號事件;太空代理 sell-the-news |
| Circle(CRCL)未來上市 | ❌ **已上市**(2026-01-24 NYSE);USDC 純曝險已可直接買 | 穩定幣軌標的=現成 |
| Section 232「25% 砍 NVDA/TSM 毛利」 | ⚠️ **半對**:確有 25% 關稅(**2026-01-15** 簽,非 1/14),但**美國 >100MW 資料中心用晶片豁免**(HTS 9903.79.03)+ 台灣框架讓 TSMC 美廠免稅;且 **H200 對中銷售 1/13 重啟(case-by-case,上限 ~85萬顆)** | NVDA/AMD 是**淨利多偏多/中性**,非 plan 說的「受害者」;**INTC 才是政策最大贏家**(政府 10% 股 +~300%) |
| BTC「2026 中週期結構性累積」 | ❌ **與現實相反**:BTC 2025-10-06 觸頂 **$126,210**,2026-06 已 **~$62–63K(-50%)**;late-cycle/早熊 | COIN/HOOD/MSTR/礦工**正在下跌趨勢**;CLARITY 利多必須**硬性 regime 閘**,別當新牛 |
| AMD 6GW 用「MI325X」 | ⚠️ 6GW 大單是 **MI450 系列**(MI325X 是現世代、被列入關稅清單);1GW **H2 2026** 部署、160M 認股權 @$0.01 | AMD 營收驗證落在 **AMD Q4'26/Q1'27 財報**;每週追 |
| Mag7 capex「$660–690B」 | ⚠️ **偏低**:big4 已 **~$725B**(GOOGL 180–190、AMZN ~200、MSFT ~190、META 125–145),+ORCL ~50 → **~$775B** | 算力/電力瓶頸論點**更強**,不是更弱 |
| CLARITY「年底前正式立法」 | ⚠️ **未過**:眾院已過(2025-07-17,294-134),參院銀行委 **2026-05-14 以 15-9 出委**;仍需參院農業委+全院+協商+簽署,**樂觀也要 2026 末/2027** | COIN/HOOD 是「預期交易」,落地前最強;別賭確定時程 |
| GENIUS(穩定幣) | ✅ **已是法律**:2025-07-18 簽;過渡上限 **~2027-01**(非 plan 說的「2026 末」) | CRCL/合規穩定幣受惠已在進行 |

---

## 2. 已查證催化劑時間軸(全年;✅=已發生/已排定 · ⏳=預期窗口 · ⚠️=未定/條件)
> 來源:Fed(FOMC 行事曆)、BLS/BEA(CPI/PCE/NFP)、KC Fed(Jackson Hole)、SEC/CNBC/Reuters(IPO)、
> 公司 IR(財報);皆於 2026-06-10 查證。市場定價(FedWatch)隨時變,進場前覆蓋官方。

### 2026 H2
- **6/11 盤後定價 → 6/12** ✅ **SpaceX(SPCX)那斯達克掛牌**,$135、$1.75T、史上最大 IPO。
- **6/16–17** ✅ **FOMC + SEP(點陣圖)**;現利率 **3.50–3.75%**,市場 ~78% 押不變。
- **6/19** ✅ 季度三巫日(期權到期、流動性抽動)。
- **7/2** ✅ 6 月非農。 **7/14** ✅ 6 月 CPI **+ JPM/GS 開財報季**。
- **7/22** ⏳ GOOGL 財報。 **7/28** ✅ MSFT 財報 **+ 7/28–29 FOMC(無 SEP)**。 **7/29** ✅ META。 **7/30** ✅ AMZN/AAPL **+ 6 月 PCE**。
- **8/7** ✅ 7 月非農。 **8/12** ✅ 7 月 CPI。
- **8/26** ⏳ **NVDA Q2 FY27 財報(盤後)** —— AI capex 敘事總驗收;**8/26** 7 月 PCE。
- **8/27–29** ✅ **Jackson Hole**(2026 主題:**金融創新對支付與政策的意涵** → 與穩定幣/加密高度相關)。
- **9/4** ✅ 8 月非農。 **9/11** ✅ 8 月 CPI。
- **9/15–16** ✅ **FOMC + SEP(秋季關鍵)**。 **9/18** ✅ 三巫日。 → **主理人定義的「九月變盤」決勝點**。
- **~9月** ⏳ **OpenAI 掛牌窗口**(S-1 6/8;估 ~$852B,可能破 $1T)。
- **~10月** ⏳ **Anthropic 掛牌窗口**(S-1 6/1;~$965B)。
- **10/13–15** ⏳ 銀行開 Q3 財報;**10/26–30** ⏳ 大型科技 Q3 財報。 **10/27–28** ✅ FOMC(無 SEP);**10/29** 9 月 PCE。
- **Q4(10–12月)** ⚠️ **BTC 週期潛在打底窗口**(空方情境 $50–55K);與 Q3 財報、年底 FOMC 共振。
- **11/6** ✅ 10 月非農。 **11/10** ✅ 10 月 CPI。
- **12/4** ✅ 11 月非農。 **12/8–9** ✅ **FOMC + SEP(2026 最後一次)**。 **12/10** 11 月 CPI。 **12/18** 三巫日。

### 2027 H1
- **~1月** ⏳ **GENIUS Act 過渡上限(~2027-01)**;**AMD MI450 1GW(H2'26 部署)營收驗證**落在 AMD Q4'26/Q1'27 財報。
- **1/26–27** ✅ FOMC(無 SEP)。
- **Q1'27** ⚠️ **CLARITY Act 可能進參院全院/協商**(PENDING);**Section 232 Phase-2**(半導體設備 SME 關稅)可能落地。
- **3/16–17** ✅ FOMC + SEP。
- **2027 H1** ⏳ **AI-PC 換機潮**(N1x / DGX Spark 上市放量)催化(見 playbook);⚠️ **加密/股市 2027 熊年情境**(2018/2022 週期類比)。
- **4/27–28** ✅ FOMC。 **6/8–9** ✅ FOMC + SEP(本 horizon 末)。

---

## 3. 每週作戰表 W14–W52(承接 Q3 的 W1–W13)
> scope = `/basecross|rally|stealth <scope>`。固定流程:`/stealth → /basecross → /rally`(+ Finviz 拉資金/基本/技術),
> 只動 **有燃料 + 連續起漲**;**九月變盤前留 ≥1/3 彈藥**;資金面 STRESS → 收手。

### 2026 年 9 月(變盤決勝)
| 週 | 期間 | 主題/事件 | 標的 scope | 可能操作 | 已知風險 |
|---|---|---|---|---|---|
| W14 | 9/14–9/18 | **FOMC+SEP(9/15–16)· 三巫(9/18)** | `all`(regime 健檢優先) | 點陣圖定調前控倉;**牛確認→九月彈藥打滿領頭;熊/盤整→收手留現金** | 九月變盤+鷹派+三巫到期;季節性最弱 |
| W15 | 9/21–9/25 | **OpenAI 掛牌窗口** | `ipo`(MSFT/AMZN/NVDA) | 掛牌前佈局受惠股、**別追掛牌首日**;噴出減碼 | IPO 抽水;sell-the-news |
| W16 | 9/28–10/2 | 季底再平衡+9月非農(10/2) | `diversified` `broadening` | 汰弱;依九月 regime 結論定 Q4 基調 | 季底調倉雜訊;就業數據 |

### 2026 年 10 月(IPO 高峰 + Q3 財報 + 加密風險窗)
| 週 | 期間 | 主題/事件 | 標的 scope | 可能操作 | 已知風險 |
|---|---|---|---|---|---|
| W17 | 10/5–10/9 | Q3 財報前哨 | `ai_software` `payments` | Finviz 拉成長/ROE,排有燃料的；小倉 | 財報前震盪 |
| W18 | 10/12–10/16 | **銀行開 Q3 財報**(10/13–15)+ CPI | `payments` `diversified` | 看金融/支付基本面;V/MA 鏈 | 財報雷 |
| W19 | 10/19–10/23 | **Anthropic 掛牌窗口** | `ipo`(AMZN/GOOGL) | 受惠股佈局;別追首日 | IPO 抽水;軟體 SaaS 失血 |
| W20 | 10/26–10/30 | **大型科技 Q3 財報 + FOMC(10/27–28)+ PCE** | `ai_software` `all` | 用財報驗 capex 敘事;FOMC 前不重押 | 財報後暴漲暴跌;利率指引 |

### 2026 年 11–12 月(加密打底窗 · 年底 FOMC)
| 週 | 期間 | 主題/事件 | 標的 scope | 可能操作 | 已知風險 |
|---|---|---|---|---|---|
| W21 | 11/2–11/6 | 10月非農(11/6) | `broadening` `stealth` | `/stealth` 找輪動吸籌 | 廣度不擴散=牛疲弱 |
| W22 | 11/9–11/13 | 10月 CPI(11/10) | `crypto`(觀察) | **BTC 若破前低→確認熊,crypto 收手**;反之只小注最強燃料 | BTC 打底失敗(空方 $50–55K) |
| W23 | 11/16–11/20 | 廣度檢查 | `diversified` `ecommerce` | 加碼連續起漲+有燃料;砍沒跟上 | 高估值回測 |
| W24 | 11/23–11/27 | 感恩節短週(11/26 休) | `broadening` | 低量、別追;檢視倉位 | 假期跳空、低流動性 |
| W25 | 11/30–12/4 | 11月非農(12/4) | `ai_software` `payments` | 年底 window dressing 佈局領頭 | 數據意外 |
| W26 | 12/7–12/11 | **FOMC+SEP(12/8–9,2026 末)+ CPI(12/10)** | `all`(regime 優先) | 末次點陣圖定 2027 路徑;依結論調倉 | 鷹派 = 高估值/小型先殺 |
| W27 | 12/14–12/18 | 三巫日(12/18) | `all` | 到期前控倉;鎖利/換股 | 到期波動 |
| W28 | 12/21–12/31 | 年末低量+稅損賣壓 | `stealth` | 低量埋伏;tax-loss 錯殺撿有燃料的 | 低流動性、年末雜訊 |

### 2027 年 Q1(政策落地觀察 · AMD 驗證 · 換機潮前夜)
| 週 | 期間 | 主題/事件 | 標的 scope | 可能操作 | 已知風險 |
|---|---|---|---|---|---|
| W29 | 1/4–1/8 | 開年+12月非農 | `all` | 重設年度 regime;檢視 Q4 倉 | 開年波動 |
| W30 | 1/11–1/15 | **AMD Q4'26 財報窗(MI450 1GW 驗證)** | `ipo`/算力(AMD/AVGO) | 驗 AMD 6GW 單兌現度 → 強則加碼算力鏈 | AMD 不如預期→算力敘事鬆動 |
| W31 | 1/18–1/22 | **GENIUS 過渡上限(~1月)** | `payments`(CRCL/COIN) | 穩定幣合規受惠;regime 沒 STRESS 才動 | 法規細則延後 |
| W32 | 1/25–1/29 | **FOMC(1/26–27)** | `all` | FOMC 前控倉 | 2027 路徑轉鷹 |
| W33–W36 | 2/1–2/26 | 財報尾聲+**CLARITY 參院全院/協商觀察** | `payments` `crypto` `broadening` | CLARITY 推進=COIN/HOOD 預期交易;**落地即防利多出盡** | crypto 晚期/熊年風險;法案卡關 |

### 2027 年 Q2–H1 末(SEP 季 · 換機潮 · 熊年防線)
| 週 | 期間 | 主題/事件 | 標的 scope | 可能操作 | 已知風險 |
|---|---|---|---|---|---|
| W37–W38 | 3/1–3/12 | Q1'27 財報季+**Section 232 Phase-2(SME 關稅)觀察** | `all` `ai_software` | 用財報驗基本面;政策受害/受惠調權重 | 設備關稅衝擊半導體設備(AMAT/LRCX/ASML) |
| W39 | 3/15–3/19 | **FOMC+SEP(3/16–17)· 三巫(3/19)** | `all`(regime 優先) | 點陣圖定 2027 上半路徑 | 鷹派;到期波動 |
| W40–W41 | 3/22–4/2 | **AI-PC 換機潮放量觀察** | Computex 群(QCOM/DELL/MSFT/NVDA) | N1x/DGX Spark 放量→佈局換機鏈 | 換機不如預期=偽催化 |
| W42–W44 | 4/5–4/23 | 季中盤整 | `broadening` `diversified` | 廣度檢查;留彈藥 | 季節性轉弱 |
| W45 | 4/26–4/30 | **FOMC(4/27–28)** | `all` | FOMC 前控倉 | 利率指引 |
| W46–W49 | 5/3–5/28 | 「Sell in May」季節性 | `stealth` `broadening` | 降 beta;吸籌埋伏 | 季節性弱 + 2027 熊年情境升溫 |
| W50–W52 | 5/31–6/18 | **FOMC+SEP(6/8–9)· 三巫(6/18)· horizon 末** | `all` | 全年結算;依 regime 重訂下一年度作戰表 | 變盤;年中再平衡 |

---

## 4. 全年「已知風險消化」清單(貫穿全期)
1. **IPO 洪峰抽水**:SpaceX(6/12,$75B 募資)→ OpenAI(~9月)→ Anthropic(~10月)接力,新供給排擠流動性 → 大盤/小型逆風。**事件噴出減碼、別追首日;玩持股受惠者(MSFT/AMZN/GOOGL)勝過高溢價載具(DXYZ)**。
2. **加密晚週期/熊年**:BTC 已 -50%(2025-10 觸頂)→ **2026 是後段/早熊,不是新牛**。COIN/HOOD/MSTR/礦工高 beta 在下跌趨勢;CLARITY 利多是「預期交易」,**硬性 regime 閘 + 噴出減碼**;核心曝險用 IBIT、MSTR/礦工只投機小倉。Alpha sleeve ≤5%、BTC ≤4% 不破。
3. **Fed/利率**(6/17、7/29、9/16、10/28、12/9 + Jackson Hole 8/28):轉鷹 = 高估值 + 小型先殺;每次 SEP(3、6、9、12月)會重設路徑。
4. **政策雙面刃**(見 `thesis_policy_regime_2026.md`):Section 232 對 NVDA/AMD 是**淨中性偏多**(>100MW 豁免 + H200 對中重啟),**INTC 是最大贏家**;但 Phase-2 設備關稅(2027)可能傷 AMAT/LRCX/ASML。CLARITY/GENIUS 利好合規交易所/穩定幣。
5. **資金面 STRESS = 全面收手**(health-check 監控)—— 2022 重演防線,小型/高 beta 先死。
6. **領頭鈍化**(NVDA 8/26 財報):若 AI capex 敘事鬆動(Mag7 ~$725–775B 是否續增是關鍵),頂底互換的「頂」會先垮。
7. **九月變盤 + 2027 熊年情境**:把「2027 級回檔」當基準情境,留現金是選擇權。

---

## 5. 每週固定動作(SOP;在 Q3 SOP 上加政策/國會兩維)
```
1) python -m sharks.data.finviz_elite <preset>     # 拉資金/基本/技術 + 新增 Earnings Date/ATR(見 finviz_schema.json)
2) python -m sharks.discord.ecom_screens <scope>   # 四張表:綜合/起漲/隱蔽吸籌/月線金叉
3) 只動 🟢(有燃料+連續起漲);🪨缺燃料/🚫墓園 跳過
4) regime/資金面健檢:STRESS → 收手
5) [新] 政策維度:本週有 Section232/CLARITY/CHIPS 進展? → 受惠/受害調權重(thesis_policy_regime_2026)
6) [新] 國會共振:NANC/Pelosi 新揭露 vs 我的候選有重疊? → Tier-1 加碼信心(thesis_congress_tracking)
7) [新] 財報日閘:Earnings Date 前 3 天的標的 → 動態減倉,防跳空黑天鵝
8) 記錄:本週投了什麼、為什麼、認賠線在哪
```

> **免責**:recommend-only 研究;非個人化投資建議;系統只建議、永不下單。RSU/ESPP 套現之稅務與雇主
> 持股集中度自行評估。所有日期進場前以官方 IPO calendar / Fed 行事曆 / 公司 IR 覆蓋。
