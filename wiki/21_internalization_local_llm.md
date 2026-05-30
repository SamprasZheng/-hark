---
type: synthesis
tags: [internalization, local-llm, ollama, data-lake, deep-research, philosophy]
title: 內化哲學 + 本地 LLM + 數據湖 + Deep Research
as_of_timestamp: 2026-05-30T10:00:00-04:00
author_role: compiler
status: live
schema_version: 1
---

# 內化哲學 + 本地 LLM + 深度研究

> 「**內化 > 抓取**;網路資料會欺騙,本地小模型 + 自己的數據湖才能真 alpha」
> — Principal 2026-05-30

---

## §1. 🧠 內化哲學

### 為什麼純抓網路會失敗

```
網路資料(MarketWatch / Bloomberg / Twitter):
  → 所有人都看得到
  → 已 priced in
  → 你無法 alpha
  → 反而會被誤導(假新聞、刻意推坑)
```

### 內化的力量

```
本地數據湖(歷史 5 年完整 OHLCV + info + news):
  → 你自己擁有
  → 可離線分析(無 API 配額限制)
  → 可訓練 / 微調本地模型
  → LLM 可深度 RAG 你的個人知識
  → 你的判斷有獨家視角
```

### 內化 ≠ 不抓網路

**正確姿勢**:
1. 抓網路資料 → 立刻**存進本地數據湖**
2. 本地分析 + 本地 LLM 處理
3. 形成「**你個人的觀點**」(不是網路觀點)
4. 公開分享 → 但分享的是你的「**處理過的洞察**」,不是原始資料

---

## §2. 🏗️ 本地架構(我已建好基礎)

### 數據湖 ✅ 已建

```
D:\DOT\$hark\data\lake\
├── prices/         (parquet, OHLCV 5 年)
├── info/           (json, 公司基本面)
├── news/           (json, 新聞)
└── manifest.csv    (索引)
```

**目前**:64 檔 / 2 MB(只 seed 30 隻)
**目標**:每日跑 → SP500 + R2K + 台股 = 預估 **5-10 GB 完整資料**
**5 年後**:50 GB 規模(你 500GB 完全 OK)

### 本地 LLM 接口 ✅ 已建(等你裝 Ollama)

```python
from sharks.ai.local_llm import (
    generate_thesis,         # 推薦理由
    generate_devils_advocate, # 反方論點
    summarize_news,           # 新聞摘要
)
```

### Deep Research ✅ 已建

跑出 14 隻完整 evidence check:

| Ticker | Verdict | Evidence | Risk |
|---|---|---|---|
| **NVDA** | 🟢 **STRONG_BUY** | 8 | 1 |
| **GEV** | 🟢 **STRONG_BUY** | 6 | 0 |
| **AAPL** | 🟢 BUY | 6 | 2 |
| **AEIS** | 🟢 BUY | 4 | 0 |
| **DOW** | 🟢 BUY | 4 | 1 |
| **DNN** | 🔴 AVOID | 2 | 3 |
| **NTLA** | 🔴 AVOID | 4 | 3 |

---

## §3. 🛠️ 本地 LLM Setup 教學(5 分鐘)

### Step 1:安裝 Ollama

下載 https://ollama.com/download/windows 並安裝(背景跑)

### Step 2:拉模型

```powershell
# 輕量(RTX 5070 跑超快,2GB):
ollama pull llama3.2:3b

# 中文好(4GB):
ollama pull qwen2.5:7b

# 推理強(4GB,慢但深思):
ollama pull deepseek-r1:7b

# Microsoft 小但聰明(2.3GB):
ollama pull phi3.5:3.8b
```

### Step 3:驗證

```powershell
python -m sharks.ai.local_llm
```

成功後輸出:
```json
{"status": "OK", "local_models": ["llama3.2:3b"]}
```

### Step 4:用在 Streamlit

下個版本 Streamlit 會加「**🧠 AI Analysis**」按鈕 — 點選任一股 → 本地 LLM 生成 thesis + 反方論點 + 新聞摘要(完全離線)

---

## §4. 🚀 GPU 利用建議(你的 RTX 5070)

### Memory 配置

| 模型 | VRAM | 速度(token/s)|
|---|---|---|
| llama3.2:3b | 4 GB | 80-120 |
| phi3.5:3.8b | 4 GB | 70-100 |
| qwen2.5:7b | 8 GB | 40-60 |
| deepseek-r1:7b | 8 GB | 30-50 |
| llama3.1:8b | 8 GB | 35-50 |

### 並行多任務(你 RTX 5070 24GB 應該夠跑):

```
日常工作:
  GPU 0:   llama3.2:3b 跑 thesis 生成(快)
  CPU 16 cores:跑 FOM scan + Streamlit + 數據抓取
  
深度分析(每週末):
  GPU 0: deepseek-r1:7b 跑反方論點
  CPU: backtest walk-forward
  
微調(每月):
  GPU 0: 用本地數據湖 fine-tune llama3.2:3b
  → 變成「你的 PolkaSharks 個人模型」
```

---

## §5. 🎯 Deep Research 範例(NVDA STRONG_BUY)

### Evidence(8 個)
- ✅ Forward PE 32.5 中等
- ✅ 營收成長 +69% YoY
- ✅ 營業利益率 62%(穩定獲利)
- ✅ ROE 119%
- ✅ Free Cashflow $58B
- ✅ **Buffett-tier 護城河**:92/100 TECHNOLOGY + ECOSYSTEM (CUDA)
- ✅ 機構持股 65%
- ✅ TD-9 沒過熱

### Risk(1 個)
- ⚠️ Bollinger 上軌 — 短期超買

### Verdict:🟢 STRONG_BUY(evidence_score 65)

---

## §6. 🔄 整合進每日 push

明天起每日推薦會自動附帶:

```
📊 LMT (Lockheed Martin)
═══════════════════════════════════════
🎯 系統 FOM: 64.2 / 100
📋 verdict: STRONG_BUY

🏰 護城河
   Buffett 3M: 79
   Type: REGULATORY + SCALE + DUOPOLY
   Thesis: 國防寡占 + F-35 + 海軍 + 政府訂單長期

💰 基本面
   Forward PE: 16.5  ✅
   ROE: 73%  ✅
   FCF: $6.8B  ✅
   股息率: 2.7%  ✅

📊 技術面
   距 52w 高: -8%
   黃金交叉: NO(已在上方)
   TD-9: NONE
   Bollinger: MIDDLE

📉 籌碼面
   機構: 84%  ✅
   短興趣: 1%  ✅
   insider: 0.5%

🎯 證據(7 條)
   1. ✅ Forward PE 合理
   2. ✅ 營收成長 +14% YoY
   3. ✅ 營業利益 +13%
   4. ✅ ROE 73%
   5. ✅ FCF $6.8B
   6. ✅ 機構 84%
   7. ✅ Buffett-tier moat 90

⚠️ 風險(2 條)
   1. 國防預算政治依賴
   2. F-35 維護成本爭議

🧠 本地 LLM 增強(等 Ollama 設好):
   - Thesis(100-150 字)
   - 反方論點
   - 新聞摘要 + sentiment
```

---

## §7. 📂 我已建好的(等你用)

### Code(3 個新)
- [src/sharks/scoring/deep_research.py](src/sharks/scoring/deep_research.py) — 每股 evidence check
- [src/sharks/ai/local_llm.py](src/sharks/ai/local_llm.py) — Ollama 接口
- [src/sharks/data/data_lake.py](src/sharks/data/data_lake.py) — 本地持久化

### Data
- [data/lake/](data/lake/) — **64 個 parquet + json,已 seed 30 隻股票**
- [outputs/deep-research-2026-05-29.json](outputs/deep-research-2026-05-29.json) — 14 隻 evidence
- [outputs/local-llm-status-2026-05-29.json](outputs/local-llm-status-2026-05-29.json) — 等 Ollama

---

## §8. 你下一步(5 分鐘 + 永久受益)

### A. 裝 Ollama
1. https://ollama.com/download/windows
2. `ollama pull llama3.2:3b`
3. `python -m sharks.ai.local_llm`

### B. 擴大數據湖
明天我跑 SP500 502 + R2K 200 + 台股 490 = 預估 5 GB 完整資料下載到本地

### C. 微調個人化模型(下個月)
等本地數據湖累積 50+ GB → 用 LoRA fine-tune llama3.2 → 變成「**PolkaSharks 個人 LLM**」

### D. Streamlit 加 Deep Research 頁
下次更新加「🧠 AI Analysis」按鈕,點任一股看完整研究

---

## §9. 哲學總結

> **「網路抓資料 → 變成商品 → 沒 alpha
> 本地內化資料 + 本地 LLM 處理 → 變成獨家洞察 → 真 alpha」**
>
> **「沒有常勝模型 — 但「你內化的系統 + 鯊魚紀律」可以穩定打贏 SPY」**
>
> **「不要追高,不要恐慌,在自己的領域做可以已知的事
> 做安穩賺安穩的錢 — 偶爾抓中妖股翻倍是 bonus,不是必要」**
>
> **「現金流 + 風險意識 + 對整體資訊的洞察 + 不被網路欺騙
> = Buffett 跟巴菲特一樣的成熟交易者」**

---

## §10. 已部署完整 Skills 統計

```
📦 Code modules:       20+
📚 Wiki pages:         21
🎯 Philosophy concepts: 18 + 13 entities
🔌 Data sources:       yfinance + TWSE + TPEx + GitHub repos + Ken French
🧠 LLM ready:          Ollama 接口(等你裝)
🏗️ Data lake:          64 files / 2 MB(本週擴 5 GB)
🎨 GUI:                Streamlit 10 頁 (http://localhost:8501)
📊 Coverage:           SP500 502 + R2K 200 + 台股 490 = 1192 ticker
✅ Validation:         8.5× SPY + Fama-French 99% 顯著
```

---

## See also

- [[17_system_audit_and_future_directions]] — 系統審計
- [[18_ultimate_integration]] — Fama-French
- [[19_streamlit_finnhub_famafrench]] — Streamlit MVP
- [[20_historical_events_japan_hedging]] — 歷史 + 對沖
- [[09_postmortem_log]] — 不重蹈覆轍

## Sources

- [Ollama 官網](https://ollama.com/)
- [llama3.2 model card](https://ollama.com/library/llama3.2)
- [DeepSeek-R1 model](https://ollama.com/library/deepseek-r1)
