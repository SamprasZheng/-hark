# 無 Finviz 訂閱的數據來源策略(離線優先 + 免費替代)

> 主理人(2026-06-10):假設**下個月起不續訂 Finviz Elite(~$40/mo)**。現在趁有訂閱/網路,
> 把原始數據**儘量存到 local**,供離線推演/回測/強化模型;並規劃免費替代源。
>
> recommend-only 研究基礎建設。本文記錄:① 系統實際需要哪些數據、② 各欄位的免費替代源、
> ③ 已建好的離線機制(怎麼用)、④ 切換步驟。

---

## 0. 核心策略:三層防線
1. **趁有訂閱 → 歸檔原始數據(point-in-time)**:每次掃描把 Finviz **原始欄位** CSV 存到
   `raw/market_data/finviz-export-*.csv`。訂閱到期後,這批就是**離線回測/重算的歷史數據集**。
2. **離線優先回讀**:沒 token / 設 `FINVIZ_OFFLINE=1` / 抓取失敗 → 自動讀最近一次本地存檔,
   pipeline 照跑(只是數據不是即時)。
3. **免費替代源接管**:going-forward 用 **yfinance(已接)+ Wallmine 免費 CSV 匯出 + TradingView**
   餵同一條管線(`finviz_row_to_dims` **以欄位名比對**,任何 header 對得上的 CSV 都能用)。

---

## 1. 系統實際需要的數據(來自 `raw/metadata/finviz_schema.json`)
| 維度 | 欄位(Finviz header) | 用途 |
|---|---|---|
| 技術 | Perf Month, SMA20/50/200, RSI | 動能/均線/過熱 |
| 資金 | Rel Volume, Insider Trans, Inst Trans | 量能/內部人/法人買盤 |
| 基本面 | ROE, Gross Margin, Sales growth, Profit Margin | quality 燃料閘 |
| 估值 | P/E, Forward P/E, P/S, PEG | 便宜/上檔空間 |
| 成長 | EPS growth next year, Sales growth | 成長強度 |
| 風險 | Beta, Short Float, Volatility | 波動/擁擠空單 |
| 閘/旗標 | **Earnings**(財報日), **ATR**(倉位), Inst/Insider Own(持股水位) | 財報靜默/止損/軋空 |
| 流動性 | Avg Volume, Price, Market Cap | 存活/流動性閘 |

> ⚠️ 實測(2026-06-10):目前的 Custom view(152 + column-ids)回傳了 P/E、PEG、P/S、EPS/Sales
> Growth、Perf、SMA,但 **沒帶 RSI / Earnings / ATR**。要讓新的「財報靜默/ATR」旗標生效,
> 需在你的 Finviz Custom view **加上 Earnings、RSI、ATR、Inst Own、Insider Own** 五欄(見
> finviz_schema.json 的 `delta_*`)。沒訂閱後這些改由下方替代源補。

---

## 2. 各欄位 → 免費替代源對照
| 需要的數據 | 最佳免費源 | 系統接法 |
|---|---|---|
| **價格 / OHLCV / 月線** | **yfinance**(已接,免費無限) | `data_lake.store_prices` → `data/lake/prices/*.parquet`;FOM 用 `fom.fetch_monthly` |
| **基本面**(P/E, ROE, margin, 成長) | **yfinance `.info`** / **Wallmine** / **Koyfin** | yfinance:`data_lake.store_info`;Wallmine:免費 CSV 匯出 |
| **篩選 + CSV 匯出**(Finviz Elite 殺手鐧) | **Wallmine**(免費下載 CSV)/ **ChartMill**(TA 評分) | 下載 CSV → `python -m sharks.data.finviz_elite rally csv:<path>` |
| **即時報價 / 圖表 / 警示** | **TradingView**(免費即時、Screener 2.0) | 手動;或未來裝 `tradingview-screener`/`tvdatafeed`(目前**未安裝**) |
| **多圖 Dashboard / 總經** | **Koyfin**(窮人版彭博) | 手動監控 |
| **盤前/盤後** | **Webull 網頁 / Yahoo** | 手動 |
| **內部人交易** | **Wallmine** / OpenInsider | CSV / 手動 |
| **國會交易** | CapitolTrades / Quiver / NANC・GOP ETF holdings | 見 `watchlist/thesis_congress_tracking.md`(本就免費,不靠 Finviz) |

> **省錢組合(覆蓋 Finviz ~85%)**:yfinance(價格/基本面,自動)+ Wallmine(篩選+CSV 匯出)
> + TradingView(看盤/技術/警示)+ Koyfin(總經 dashboard)。

---

## 3. 已建好的離線機制(怎麼用)
### (a) 原始數據歸檔(每次掃描自動)
`finviz_elite` 掃描時自動把**原始 rows** 存 `raw/market_data/finviz-export-<source>-<date>.csv`。
→ 趁有訂閱,每天累積;到期後就是離線數據集。
```
python -m sharks.data.finviz_elite rally universe   # 掃 + 自動歸檔全宇宙原始欄位
```

### (b) 離線回讀(沒訂閱/沒網路時)
```
$env:FINVIZ_OFFLINE=1                                 # 強制離線
python -m sharks.data.finviz_elite rally power        # 自動讀最近一次本地存檔來算
```
無 token / 抓取失敗也會**自動 fallback** 到本地存檔(不必手動設)。

### (c) 外部免費 CSV 直餵(Wallmine / TradingView / ChartMill)
`finviz_row_to_dims` **以欄位名(header)比對**,所以任何欄位名對得上的免費 CSV 都能走同一管線:
```
python -m sharks.data.finviz_elite rally csv:downloads/wallmine-screen.csv
```
> CSV 的欄位名需對上第 1 節的 Finviz header(如 `P/E`、`RSI`、`Gross Margin`…)。Wallmine/TV
> 若用不同欄名,加一層 header remap(見 §5 待辦)。

### (d) yfinance 本地湖(價格 + 基本面)
```
python -m sharks.data.data_lake                       # 預設快取「全宇宙」(LAKE_UNIVERSE=full)
$env:LAKE_UNIVERSE='seed'; python -m sharks.data.data_lake   # 只快取小清單(快)
```
存到 `data/lake/prices/*.parquet`(5y 日 K)+ `data/lake/info/*.json`(基本面快照)。
離線讀:`data_lake.load_prices(t)` / `load_info(t)`。

### (e) 宇宙擴增 drop-in
`data/universe_extra.txt`(一行一檔)→ 貼 vendor 千檔清單,FOM 掃描自動納入,零改 code。

---

## 4. 切換步驟(訂閱到期當天)
1. 確認 `raw/market_data/` 已有足夠歷史歸檔(每天一份 `finviz-export-universe-*.csv`)。
2. 設 `FINVIZ_OFFLINE=1`(或直接讓抓取失敗 auto-fallback)→ 掃描改吃本地存檔。
3. 日常即時數據改用 **TradingView**(看盤/警示);需要篩選清單時用 **Wallmine** 下載 CSV →
   `rally csv:<file>`。
4. 價格/基本面持續由 **yfinance 湖**自動更新(把 `data_lake` 排進每日 routine)。

---

## 5. 待辦 / 強化(可選,問主理人)
- [ ] **yfinance → finviz-row 轉接器**:用 yfinance `.info` 產生與 `finviz_row_to_dims` 相同的
      dict keys(P/E、ROE、Gross Margin…),讓「完全無 Finviz/無 CSV」也能自動算 dims。
      映射:`trailingPE→P/E`、`forwardPE→Forward P/E`、`returnOnEquity→ROE`、
      `grossMargins→Gross Margin`、`profitMargins→Profit Margin`、`revenueGrowth→Sales Q/Q`、
      `pegRatio→PEG`、`beta→Beta`、`shortPercentOfFloat→Short Float`、`heldPercentInstitutions→Inst Own`。
- [ ] **Wallmine/TradingView header remap**:一個 `HEADER_ALIASES` dict 把替代源欄名 → Finviz 欄名。
- [ ] **TradingView 函式庫**(`tradingview-screener` / `tvdatafeed`)——目前未安裝;裝了可程式化拉
      即時 screener,但需評估 ToS / 穩定性(避免被封)。
- [ ] 把 `data_lake`(yfinance 湖)+ 全宇宙 Finviz 歸檔排進 `scripts/daily_routine.ps1`,每天自動存。

> 相關:`raw/metadata/finviz_schema.json`(欄位 schema)· `src/sharks/data/finviz_elite.py`
> (archive/offline/csv 入口)· `src/sharks/data/data_lake.py`(yfinance 湖)· `data/universe_extra.txt`。
