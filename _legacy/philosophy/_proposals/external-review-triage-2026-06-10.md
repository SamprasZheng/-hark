---
type: proposal
tags: [proposal, external-review, triage, data-sources, scanner, roadmap]
as_of_timestamp: 2026-06-10
author_role: assistant-research
source: principal-pasted external AI review (README+ROADMAP only) — verified against actual code 2026-06-10
---

# 外部 review 裁決(2026-06-10)— 照「外部計畫當 delta 查證別照做」慣例

> 結論:review 基於舊快照(只讀 README/ROADMAP),**~70% 指控已過時**。真正值得採納的 delta
> 只有 4 項;其餘已存在或違反 minimalist moat(stdlib-first、no heavy deps)。

## 逐點裁決

| Review 主張 | 裁決 | 現況證據 |
|---|---|---|
| 「Phase 1 全是 stub,先打通最小垂直鏈」 | ❌ **過時** | finviz_elite 每日掃 11,262 檔→9維→rally JSON;FOM 掃 582 檔;daily brief 三班produces。stub 只剩 finviz_client.py(舊版,已被 finviz_elite 取代) |
| 「PIT 紀律只是文件,要 pytest 強制」 | ✅ **已做**(今日) | `src/sharks/state/`(_frontmatter/lint/resolve/snapshot)+ `tests/test_state_pit.py` |
| 「universe 只有 Mag7+15 支」 | ❌ **過時**(今日擴) | DEFAULT 116 → `full_universe()` 582 → `fom_universe()` 626;`data/universe_extra.txt` drop-in 千檔 |
| 「缺資料快取層(DuckDB/Parquet)」 | ✅ **已做**(今日);DuckDB **拒** | `data/lake/` 573 檔 5y parquet + 590 info(42MB);`raw/market_data/` Finviz 原始歸檔 603 檔。pandas+parquet 夠用,DuckDB=多餘依賴 |
| 免費源:FRED/ALFRED | ✅ **已接** | `fred_client.py` + `regime/liquidity.py`(fishbowl L) |
| 免費源:Finnhub | ✅ **已有 client** | `finnhub_client.py` + `finnhub_integration.py` |
| 免費源:**SEC EDGAR** | 🟢 **採納(真缺口)** | data/ 無 edgar client;官方免費基本面/filings,= 無 Finviz 時最硬的基本面源 |
| 免費源:Stooq/Tiingo/AlphaVantage | ⚪ 略過 | yfinance+Finnhub+Polygon client 已覆蓋;多接=維護負擔 |
| 情緒:Reddit/StockTwits/pytrends | ⚠️ 緩 | 已有 news_sentiment.py;爬社群有封鎖風險(CLAUDE.md 規則),不主動接 |
| 「Ollama 跑 Qwen 7B 省 90% API」 | ✅ **早已做** | `ai/dispatcher.py`(router)+ `local_llm.py` + bot 上的 qwen2.5:7b personas |
| FinBERT 情緒 | ❌ **拒** | 要 torch/transformers 重依賴,違反 moat;Ollama 已覆蓋 |
| 配對交易/PEAD/指數事件/資金費率 | 🟢 **採納為研究 proposal** | 系統無此策略;指數事件今日已實戰用過(MRVL 6/22 納 S&P sell-the-news)。需過 walk-forward 才上 |
| 「千股均線掃描(越線/連線/騎線/大底)+ 板塊熱度」 | 🟢 **採納(最高價值)** | basecross 只掃題材池月線金叉;**全市場本地 MA 掃描器不存在**。今日剛建好的 lake(573 parquet)正是為此;純 pandas 向量化、零新依賴、完全離線 |
| vectorbt | ❌ **拒** | pandas 向量化即可,不加依賴 |
| 財報 transcript 分析/新聞→影響鏈 | ⚠️ 緩 | 有價值但要新抓取面;先用現有 news_sentiment + wiki 流程 |
| 多 agent 辯論 | ✅ **已有** | discord personas + balanced bench 4 quant voices;bull/bear 由 Risk Officer 裁決即現行設計 |
| Embedding RAG | ✅ **已有** | `ai/rag_library.py` + `rag_retrieve.py`(本地,非 vector-DB 服務) |
| 板塊輪動/廣度偵測 | ✅ **大半已有** | `regime/breadth_indicator.py` + daily brief 類股資金流;缺的是「板塊內 %>MA50」細粒度→併入掃描器 |
| 類似產品(TradingAgents/ai-hedge-fund/FinRL/Qlib/OpenBB) | ⚪ 參考 | 差異化判斷正確(compile-first 知識庫+憲法層);不改架構 |

## 採納清單(僅 4 項,依價值排序)
1. **本地千股均線掃描器**(`scoring/ma_scanner.py`):吃 `data/lake/prices/*.parquet`(離線、零 API),
   向量化算 越線(close 上穿 MA20/60)/ 連線(MA5>MA20>MA60 多頭排列+斜率)/ 騎線(N 日 low 貼 MA 不破)/
   大底(距 52w 低 <15% + 量縮 + RSI 底背離);輸出 `outputs/ma-scan-<date>.json` + **板塊 %>MA50 熱度表**
   (餵 regime_breadth)。= 把今天建的 lake 變成推演引擎。
2. **SEC EDGAR client**(`data/edgar_client.py`):官方免費,companyfacts API → 離線基本面
   (無 Finviz 時的 ROE/margin 來源,接進 docs/data_sources_no_finviz.md §5 的 yfinance 轉接器同層)。
3. **PEAD / 配對交易 / 指數事件**:各開一頁 `philosophy/_proposals/`,過 Phase-4 walk-forward 才升級。
4. **每日數據保存排程**:`data_lake` + finviz 全宇宙歸檔進 `scripts/daily_routine.ps1`(訂閱到期前最大化累積)。

## 拒絕清單(守 moat)
DuckDB、vectorbt、FinBERT(torch)、外部 vector-DB、Stooq/Tiingo/AV 多接、社群爬蟲。
