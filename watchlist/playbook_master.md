---
type: playbook
tags: [playbook, master, dashboard, calendar, rotation, deployment]
as_of_timestamp: 2026-06-08
author_role: human
source: principal-directive
---

# 作戰總表(2026 H2)— 題材 × 時間軸 × 操作 × 指令

recommend-only 研究儀表板。整合所有 watchlist 論點 + Jun→Sep 部署計劃。
Discord 打 `/playbook`(或 `!作戰`)叫出精簡版。

## 主軸(一句話)
**頂底互換**:賣 NVDA 強勢(頂)→ 買錯殺底(太空/軟體/IPO代理/支付);**分批、信號驅動、
留彈藥到九月變盤**。底層紀律:**非2021、廣度小 → 只買有燃料(真賺錢/真題材)+ 連續起漲**。

## 時間軸 × 操作
| 時間 | 事件/狀態 | 操作 | 工具 |
|---|---|---|---|
| **現在→7月** | 盤整/小跌可能;埋伏 | 只動六月彈藥 **30–40%**,埋伏隱蔽吸籌 | `/stealth broadening` `/stealth ipo` |
| **Q3(7–9月)** | Databricks/Stripe IPO 窗口 | 佈局代理:`SNOW`(Databricks)、`V/MA`(Stripe 支付) | `/basecross ipo` `/basecross payments` |
| **8月** | 確認加碼 | 加碼**已連續起漲+有燃料**的;砍沒跟上的 | `/rally <題材>` |
| **9月** | **變盤點(牛/熊確定)** | 牛→打滿領頭;熊/盤整→**收手留現金** | `/rally all` + regime 健檢 |
| **Q3–Q4** | **SpaceX IPO**(>$1T) | 太空代理:`RKLB/IRDM/ASTS/LUNR` | `/basecross space` |
| **末'26–'27初** | OpenAI/Anthropic IPO | 持股受惠者 `MSFT/AMZN/GOOGL` + 算力 | `/basecross ipo` |
| **2027 H1** | **N1x / RTX / DGX Spark 上市開賣** | **AI-PC 換機潮才引爆** → 現在只佈局、別追 | `QCOM/DELL/MSFT/NVDA`(Computex 群) |

> **N1x 筆電換機是「明年初」的催化劑,不是現在**——現在佈局相關供應鏈、等上市放量再加碼。

## 題材池(每個都可 `/basecross|rally|stealth <scope>`)
| scope | 題材 | 代表 |
|---|---|---|
| `space` | 太空(SpaceX) | RKLB IRDM ASTS LUNR |
| `ipo` | 2026 IPO 超級年代理 | MSFT AMZN GOOGL SNOW V/MA |
| `payments` | Agentic 支付/金融科技 | V MA PYPL XYZ COIN CRCL |
| `ecommerce` | 電商 agentic-commerce | AMZN SHOP MELI PDD + 小型 |
| `ai_software` | AI 錯殺軟體 | NOW CRM ADBE SNOW … |
| `broadening` | 廣度錯殺(民生/消費/醫療) | KHC PFE NKE … |
| `diversified` / `midrisk` | 跨產業轉機 | KVUE/C/DE/LYB … |

## 風控閘(每次出手前全中)
1. **有燃料?** 真賺錢(quality)或真題材;否則 `🪨 缺燃料` 不追。
2. **連續起漲?** 非單根;最好先 🕵️吸籌 → 金叉 → 連漲。
3. **資金面沒 STRESS?** 翻 STRESS → 收手(防 2022 重演,小型先死)。
4. **分層 + 留彈藥**:核心(有營收)大、投機(pre-profit)小;≥1/3 留到九月。
5. **財報黑窗?** 標的 ≤3 交易日內財報 → **不開新倉 / 減倉防跳空**(見下「財報季閘」)。

## 財報季閘 (Earnings-Season Gate) — 注意事項
財報日是**每檔最強的單點催化劑**:跳空風險 + 隱波劇變。每年日期**季季循環、落在差不多的季節**,
所以本地建快取(免費,從 `data/lake/info` 的 `earningsTimestamp`)→ 可預測下一次。
```
python -m sharks.data.earnings_calendar     # 590 檔免費快取 → data/earnings/upcoming-<date>.json
```
- **黑窗(blackout)**:財報前 **≤3 日**(`EARNINGS_BLACKOUT_DAYS`,對齊 `risk_config.yaml`)→ **不開新倉**;
  既有倉位**減碼防黑天鵝跳空**,或留到財報後止穩再決定。
- **財報季節奏(輪盤)**:① **JPM/GS 開季**(每季首週,~1月/4月/7月/10月中)→ ② **大型科技週**
  (MSFT/GOOGL/AMZN/META,7月底/10月底)→ ③ **NVDA 壓軸**(2月底/5月底/**8/26**/11月中)。
  每段都是**資金與隱波重定價**窗口 → 對齊 [[../wiki/08_forward_calendar]] 月度事件列。
- **預測標 `(predicted)`** = 季線級推估、未經官方確認 → **下單前必用官方 IR / Finviz / Finnhub 覆蓋**。
- **本週黑窗範例(2026-06-10)**:`CHWY` `ORCL`(OpenAI 代理)`OXM` 今日、`ADBE`(Canva 代理)`RH` 明日;
  `MU` T-14、`FDX` T-13 — 黑窗內**不接刀**,等財報後再看連續起漲。

## 隱波套利觀察 (IV / 隱波 Arbitrage Watch) — 高度關注
**博弈的是隱含波動(IV),不是方向**。圍繞財報的兩種結構性 edge(recommend-only,**最高技術、最小倉位**):
- **財報前 IV 爬升 → 收斂**:event 前 IV 被買高;若你判定「波動會比市場定價小」→ **賣方策略**(賣價差/鐵兀鷹)賺
  時間+IV 收斂。反之判定「市場低估事件」→ **買方**(價差/跨式)賭超預期。
- **財報後 IV crush(隱波崩跌)**:財報一出,IV 從高位**瞬間崩**——裸買選擇權最常死在這:**猜對方向、仍賠錢**。
  所以 event 前**別裸買 premium**;要嘛賣方收 crush,要嘛用價差限縮 vega。
- **看什麼名單**:① **選擇權流動性高 + IV 夠高**(才有 premium 可收/可博)② **財報錨定**(用上面的 earnings 快取)
  ③ 你**有基本面/題材觀點**的(IV 博弈疊加方向觀點才有複利)。初篩池:`NVDA TSLA AMD MU AVGO PLTR COIN MSTR SMCI` 等
  高 β/高 IV 且財報前後波動劇烈者。
- **⚠️ 資料缺口(老實說)**:目前系統**沒有 options-chain / IV 資料源**(無 implied-vol、無 vega)——這節是**觀察方法論**,
  尚不能自動算。要落地需接一個**免費 IV 來源**(yfinance `Ticker.option_chain` 有逐鏈 IV;或 CBOE 個股 IV)→ 才能把
  「IV 百分位 / 財報前後 IV 變化 / 預期波動 vs 實際」做成像 FOM 一樣的 recommend-only 評分。**這是下一塊要建的。**

## 各論點全文
- `deployment_plan_jun_sep_2026.md`(分批計劃)
- `thesis_2026_ipo_wave.md`(IPO→代理)· `spacex_ipo_2026_event.md`(太空)
- `thesis_agentic_payments.md`(支付 + MCP/A2A/x402)
- `thesis_ecommerce_agentic.md`(電商)· `thesis_broadening_stealth.md`(廣度吸籌)
- `thesis_diversified_turnaround.md`(分散/中風險)· `dxyz_premium_special_situation.md`(DXYZ 溢價)
- `docs/regime_breadth_principle.md`(燃料閘底層邏輯)· `docs/finviz_screening_recipe.md`
