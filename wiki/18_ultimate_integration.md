---
type: synthesis
tags: [fama-french, worldmonitor, multi-model, gui, api, oversold-2022]
title: 終極整合 — Fama-French + worldmonitor + 多模型 + 2022 錯殺
as_of_timestamp: 2026-05-30T07:00:00-04:00
author_role: compiler
status: live
schema_version: 1
sources:
  - outputs/oversold-2022-recovery-2026-05-30.json
---

# 終極整合 wiki

> 一次回答:Fama-French、worldmonitor、多模型、GUI、更多 API、2022 錯殺

---

## §1. 🎯 2022 升息錯殺股回升 — Top 10 直接結果

### 規則:跌幅 ≥50% / 反彈 ≥20% / 突破 12 月 MA / 量能確認

| Rank | Ticker | 2021 高 | 2022/23 低 | 現價 | 跌幅 | 反彈 | 距 2021 高 | 注意 |
|---|---|---|---|---|---|---|---|---|
| 1 | **BLDP** | $34 | $3.33 | $6.19 | **-90%** | +86% | -82% | 氫能;極深修 + 大反彈 |
| 2 | **ZM** | $387 | $60 | $100 | -85% | +68% | **-74%** | 經典 Covid 受傷股 |
| 3 | **BKSY** | $93 | $9 | $51 | -90% | **+452%** | -45% | 衛星;已大彈 |
| 4 | **NVAX** | $238 | **$4.80** | $10.32 | **-98%** | +115% | **-96%** | 🔥 **最深 + 最多上行空間** |
| 5 | **ROKU** | $459 | $41 | $131 | -91% | +222% | -71% | 流媒體;已大彈 |
| 6 | **BEAM** | $129 | $21 | $33 | -84% | +55% | -75% | 基因編輯 |
| 7 | **MARA** | (高)| (低)| — | -93% | **+311%** | -73% | BTC miner;已大彈 |

### 解讀框架

| 標的類型 | 動作 |
|---|---|
| **已大彈型**(BKSY/ROKU/MARA)| 觀察 pullback 再進;不追 |
| **深修中型彈**(BLDP/ZM/BEAM)| 等突破關鍵阻力(50MA)+ 量爆 |
| **🔥 仍接近底**(NVAX -96% 距高)| 小注賭翻倍機會 — **歸零風險也高** |

### NVAX 特例(我個人意見)
- 從 $238 跌到 $4.80(2023/12)= -98% 史詩級錯殺
- 現在 $10.32 = 從底 +115%
- 若回到 2021 高還要漲 **23×**
- 風險:疫苗市場死、財務壓力
- 機會:任何疫苗合約 / 收購

---

## §2. 📚 Fama-French 解釋(白話文)

### 是什麼

Fama-French 是 **諾貝爾獎學者** Eugene Fama 跟 Kenneth French 提出的「**股票超額報酬 3+ 因子模型**」。

### 你之前以為單一因子是「市場 beta」
傳統 CAPM 說:**股票超額報酬 = β × 市場超額報酬**

### Fama-French 說:**「市場 beta 不夠,還有 2 個因子」**

| Factor | 意義 | 哪種股票賺 |
|---|---|---|
| **Market(MKT)** | 市場本身 | 任何上漲市場 |
| **SMB**(Small Minus Big)| **小型股 vs 大型股** | 小型股 long-run 跑贏大型股 |
| **HML**(High Minus Low)| **高 P/B 價值 vs 低 P/B 成長** | 價值股 long-run 跑贏 |

### 5 因子版進階(2015 升級)
- **RMW**(Robust Minus Weak)— 高獲利能力 vs 低
- **CMA**(Conservative Minus Aggressive)— 保守投資 vs 激進

### 對你系統的意義

我的 FOM 跑出 **8.5× SPY** alpha,但**我沒拆解這個 alpha 是來自哪個因子**:
- 是因為抓對小型股?(SMB)
- 是因為抓對價值股?(HML)
- 是因為抓對品質?(RMW)
- 還是真的有獨家 alpha(超越因子)?

### 怎麼用 Fama-French 「驗證」我系統

**步驟**:
1. 跑 FOM 推薦 → 計算每月報酬
2. 跟 Fama-French 3 因子做迴歸(用 Ken French 網站免費資料)
3. 看 **「alpha 截距」**:若 > 0 且顯著 = 真實 alpha
4. 看 **factor loadings**:我系統哪些 bet 上,哪些沒上

### 為什麼這對 PolkaSharks 內容重要

「我系統不只跑贏 SPY,**還跑贏 Fama-French 5 因子模型**」= 學術級可信度

---

## §3. 🌍 koala73/worldmonitor 維度借鏡

### 該專案在做什麼

**Real-time global intelligence dashboard** — 65+ 數據源跨越:
- 地緣政治
- 金融
- 能源
- 氣候
- 航空
- 網路
- 軍事
- 基礎設施
- 新聞

### 對我系統有用的「維度」

| worldmonitor 維度 | 對應我系統 | 是否值得加 |
|---|---|---|
| 92 stock exchanges tracker | 我的 universe(本週升 80%)| ✅ 已有方向 |
| BIS 央行政策比較 | 我的 macro_state | 🟡 待加 |
| ETF flows | 待加(Phase 3)| 🟢 高優先 |
| Stablecoin monitor | 加密流動性訊號 | 🟡 中等 |
| EIA 能源(4 指標)| 大宗商品 deepening | 🟢 高優先 |
| Country Intelligence Index | **12 訊號 composite risk score** | 🟢 框架可借鏡 |
| Military activity tracker | 黑天鵝早警 | 🟡 中等 |
| Disaster events | 黑天鵝早警 | 🟡 中等 |

### 我會借鏡的 3 個東西

1. **多維度 composite risk score**(類似 worldmonitor 12 訊號)→ 升級我的「警報等級系統」(目前 M2/BTC/GLD 三訊號,可擴 12+)
2. **EIA 能源 4 指標**(原油庫存、天然氣、煉油廠利用、戰略儲備)→ 升級 commodity dim
3. **BIS 央行政策數據**(各國央行立場比較)→ 全球流動性訊號

### 對「預測回測效益」誠實看法

**worldmonitor 為 situational awareness(情境覺察)**,**非預測模型**:
- 提供大量訊號但不告訴你「該買什麼」
- **適合補充我系統 → 不能取代**
- 用處:幫我發現黑天鵝,不是找 alpha

---

## §4. 💰 更多 API 候選(WebSearch 2026)

### Tier 1:真正值得考慮(免費 tier 強)

| API | 免費 tier | 強項 |
|---|---|---|
| **Alpha Vantage** | 25 req/day | 含 SP500 fundamentals + 50+ TA + crypto + 經濟 + **news sentiment** |
| **Finnhub** | 60 req/min | 即時報價 + **13F** + insider + congressional trading + ESG + patent + earning revision |
| **Polygon.io** | 5 req/min | 真實 tick-level + WebSocket(免費 50 symbols 即時)|
| **Financial Modeling Prep (FMP)** | 250 req/day | **完整 13F + insider transactions** + financial statements |
| **SecuritiesDB** | 免費 | **單一 API** 同時抓 Form 4 insider + 13F |
| **EODHD** | 20 req/day | 新聞 sentiment + 60+ exchanges |

### Tier 2:Google Finance / 其他 free

| 來源 | 用途 | 限制 |
|---|---|---|
| Google Finance(網頁)| **無公開 API**(Google 關閉了 2017)| 只能爬,容易被 ban |
| Google Sheets `GOOGLEFINANCE()` | 你個人用沒問題 | 不能 programmatic 大量 |
| Yahoo Finance(yfinance)| ✅ 我已在用 | 大量請求易失敗 |
| StockAnalysis.com | 免費 web | 爬蟲 OK |
| Wisesheets | 免費 tier | API 有限 |
| **MacroMicro** | 部分免費 | **台灣製,適合台股**! |
| Stockdex | 免費 | 偏 Indian 市場 |
| Marketstack | 1000 req/月 free | 主要 EOD |

### 我會優先試的順序

1. **Finnhub free tier**(60 req/min,夠用)— **insider + 13F + earning revision + news**
2. **FMP**(250 req/day)— **完整 13F + insider** 補充
3. **MacroMicro 台股**(若有 API)— **台股完整**
4. **Alpha Vantage**(25 req/day)— **news sentiment 補強**

### 升級 SecuritiesDB 模組

明天我會試:
```python
import urllib.request, json
url = "https://securitiesdb.com/api/insider/{ticker}"  # 假設端點
# 替代:openinsider 爬蟲 + SEC EDGAR
```

---

## §5. 🎨 GUI 視覺化計畫(Phase 5)

### 技術選擇

| 選項 | 優劣 |
|---|---|
| **Streamlit**(Python)| 🥇 最快;原生 Python;適合 dashboard;部署 Vercel/Heroku;**推薦** |
| Dash(Plotly)| 互動強;學習曲線高 |
| Gradio | 適合 LLM agent UI |
| React + FastAPI | 最強但工程量大;考慮 Phase 6 |
| Jupyter + ipywidgets | 開發中用 |

### 必有元素

1. **Filter table** — sortable / filterable 所有股票(FOM / sector / market cap)
2. **Bubble chart** — X=momentum, Y=contrarian, size=market cap, color=sector
3. **Heatmap** — 你 portfolio vs benchmark 相關性
4. **Time series chart** — 個股 + 系統訊號 overlay(警報、進場、賣出)
5. **Alert panel** — 即時警報等級 + reason
6. **Multi-model comparison** — 7 模型 top picks 並列
7. **One-click drill-down** — 點任一股 → 全維度 detail
8. **CSV export** — 結果出檔

### 開發路線

**Week 1**: Streamlit MVP (3 個 view)
**Week 2**: Bubble chart + heatmap
**Week 3**: Multi-model side-by-side
**Week 4**: Deploy on Streamlit Cloud(免費)

---

## §6. 🎲 多模型 ensemble 設計

### 7 個模型並列(避免 overfitting)

| 模型 | 權重 | 適用場景 |
|---|---|---|
| **Aggressive**(積極)| Momentum 50% + Bubble -25% + Cyclic 25% | 牛市末段 / 妖股年 |
| **Conservative**(保守)| Buffett 40% + Quality 30% + Bubble +30% | 熊市 / 升息 |
| **Trend**(追漲)| Pure momentum + Golden cross | 強勢市場 |
| **Smart Money**(主力)| Chip_flow 50% + Institutional change 30% + Volume 20% | 多空轉折 |
| **Technical**(技術派)| TD-9 + Bollinger + MA crossover + Distance from 52w | 短線 swing |
| **Fundamental**(基本)| Buffett 3M 50% + Sector growth 25% + EPS revision 25% | 長線投資 |
| **Ensemble**(綜合)| Voting across 6 + 我目前 FOM | 全市況 |

### Overfitting 防止

- 每月只調權重一次(非每日)
- Walk-forward validation(train 60% / val 20% / test 20%)
- 多模型一致性投票(7 個都看好 = 最強訊號)
- Information Coefficient(IC)監測 — 若 IC 持續低,該模型休眠

### Ensemble decision rule

```
if 6+ models agree: STRONG_BUY (max position)
if 4-5 agree:        BUY (standard position)
if 2-3 agree:        WATCH
if 0-1 agree:        SKIP
```

---

## §7. 🌏 台股完整覆蓋現狀

### 我已嘗試

- **yfinance 拉 .TW / .TWO** — 部分成功(40-60% 成功率)
- **手動 hardcoded list** — 約 50 隻台股大型 + 25 隻 OTC

### 為何台股難

1. **無維護良好的 GitHub 全名單**(美股有 rreichel3,台股沒有)
2. **yfinance 對台股支援不穩**(`.TW` `.TWO` `.TWS` 規則混亂)
3. **MacroMicro / Goodinfo 台股 API 需付費或爬**

### 我下一步

**本週修**:
1. 爬 **Goodinfo.tw** 台股全名單(免費)
2. 或用 **MacroMicro 部分免費**
3. 加台股 ~200-300 隻完整 FOM scan
4. 整合台股 + 美股共 1500+ 進每日 push

---

## §8. 🎯 YTD 2026 事件 ↔ 股價關係(本月可補)

### 我會做的「歷史事件 vs 股價」分析

從 2026/1/1 起每個重大事件 → 看對應股票漲跌:

| 事件 | 日期 | 主要受影響股 |
|---|---|---|
| Warsh 任命 Fed Chair 公佈 | 2026-03 | TLT / GLD / SPX 反應 |
| Trump 關稅升級 | 2026-04 | TSM / FXI / IWM 反應 |
| 中美關係波動 | 2026 全年 | TSM 個別事件 |
| SpaceX S-1 申報 | 2026-05-20 | TSLA 反應 |
| BTC 從 $126K 高跌 | 2026-Q1 | MSTR / COIN / 整體 risk-on |
| 黃金漲 +36% YoY | 2026 全年 | GLD / NEM / DNN 反應 |

### 寫成 wiki

明天會寫 `wiki/19_ytd_event_market_response.md`,把今年所有大事件對應股價反應抓出來,作為**模型校準依據**(不是日調參,是每月歸納)

---

## §9. 🤖 量化進階方向

### 立即(2 週)
- Fama-French 因子迴歸驗證
- IC(Information Coefficient)per dim 月度測量
- Walk-forward backtest(去除 survivor bias)

### 中期(1-2 月)
- XGBoost 學最佳權重
- 多模型 ensemble + 投票機制
- Streamlit GUI MVP

### 長期(3-6 月)
- RL 動態權重
- 完整 dashboard 上線
- Interactive Brokers read-only(只看部位,不下單)

---

## §10. 本週優先順序(我自己 commit)

1. ✅ **2022 錯殺回升 scanner**(剛跑出來)— 推薦 NVAX 觀察
2. 🟡 **台股 200+ 隻完整 FOM**(爬 Goodinfo)— 本週四前
3. 🟡 **Finnhub 整合**(insider + 13F + news)— 本週六前
4. 🟡 **Fama-French 3 因子驗證**(用 Ken French 資料)— 下週前
5. 🟡 **Streamlit GUI MVP**(filter table + bubble chart)— 下下週前
6. 🟡 **YTD 事件 ↔ 股價分析 wiki** — 下週前

---

## 一句話

> **「Fama-French 是 70 年代諾貝爾學者的因子模型,我系統 8.5× alpha 需要它驗證真實性;
> worldmonitor 是 dashboard 不是預測模型,但可借鏡多維度 risk score 概念;
> 2022 NVAX -98% 跌幅 + 現在剛開始爬 = 教科書深度錯殺。」**

---

## See also

- [[17_system_audit_and_future_directions]] — 系統審計
- [[15_polkasharks_content_template]] — 內容 SOP
- [[14_2026_outlook_and_meme_year]] — 妖股年
- [[09_postmortem_log]] — 自我打臉
- 未來 wiki:`19_ytd_event_market_response.md`,`20_taiwan_universe_complete.md`,`21_streamlit_gui_design.md`

## Sources

- [koala73/worldmonitor](https://github.com/koala73/worldmonitor)
- [worldmonitor FINANCE_DATA.md](https://github.com/koala73/worldmonitor/blob/main/docs/FINANCE_DATA.md)
- [Alpha Vantage](https://www.alphavantage.co/)
- [Finnhub](https://finnhub.io/)
- [Polygon.io](https://polygon.io)
- [Financial Modeling Prep](https://site.financialmodelingprep.com/developer/docs)
- [SecuritiesDB](https://securitiesdb.com/developers/insider-trading-api)
- [EODHD](https://eodhd.com/financial-apis/)
- [Ken French Data Library](https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/data_library.html) — Fama-French free factors
