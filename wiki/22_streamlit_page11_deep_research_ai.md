---
type: synthesis
tags: [streamlit, deep-research, local-llm, ollama, ui, page-11]
title: Streamlit Page 11 — Deep Research + AI(本地 LLM)
as_of_timestamp: 2026-05-30T11:00:00-04:00
author_role: compiler
status: live
schema_version: 1
---

# Page 11 — Deep Research + AI

> 「投影片從 10 升 11 — 最後一頁讓觀眾看到「**本地 LLM 怎麼接上系統 evidence**」」

---

## §1. 新增了什麼

`src/sharks/ui/streamlit_app.py` 加入第 11 頁 **🧠 Deep Research + AI**:

1. **Ticker 選單** — 從 `outputs/deep-research-*.json` 載入 14 隻已完成 evidence check 的股票
2. **Verdict header card** — STRONG_BUY / BUY / WATCH / AVOID + evidence_score
3. **四象限佈局**:
   - 🏰 護城河 / Buffett 3M
   - 💰 基本面(8 指標表)
   - 📊 技術面(MA / Golden Cross / TD-9 / Bollinger)
   - 📉 籌碼面(機構 / Short / Insider)
4. **Evidence / Risk 對照欄** — 系統列出的所有 ✅ 證據 vs ⚠️ 風險
5. **🧠 本地 LLM 增強區**(關鍵新功能):
   - 偵測 Ollama 是否啟動 → 顯示綠色 OK 或黃色設定提示
   - 顯示已下載的 local models → 讓使用者切換(llama3.2:3b / qwen2.5:7b / deepseek-r1:7b)
   - 📝 「生成 Thesis」按鈕 → 呼叫 `local_llm.generate_thesis(ticker, deep_research_data)`
   - 😈 「反方論點」按鈕 → 呼叫 `local_llm.generate_devils_advocate(...)`
   - 📰 新聞摘要(目前 disabled,等 Finnhub key)
6. 輸出渲染在分色 callout block(thesis 藍色、devil's 紅色)

---

## §2. 哲學連結

對應 [[21_internalization_local_llm]] 的「**內化 > 抓取**」原則:

```
網路抓資料  → 商品化   → 無 alpha
本地 evidence + 本地 LLM 處理 → 獨家洞察 → 真 alpha
```

Page 11 把這個哲學「**物質化**」成 UI:
- 系統 evidence 來自 `deep_research.py`(本地計算,不依賴新聞)
- LLM 推理在 Ollama 本地跑(隱私 + 無 API 配額)
- thesis 文字是「**你內化過的觀點**」,不是 ChatGPT 通用回答

---

## §3. 啟動方式

### 一鍵 bring-up

```powershell
pwsh D:\DOT\$hark\scripts\setup_local_llm.ps1
# 預設拉 llama3.2:3b;可加 -Model qwen2.5:7b 換中文強的
```

腳本會:
1. 透過 `check_ollama.ps1` 啟動 WSL Ollama daemon
2. 拉模型(已有則跳過)
3. 跑 `python -m sharks.ai.local_llm` smoke test

### 手動

```powershell
# 1. 啟 Ollama
pwsh D:\DOT\$hark\scripts\check_ollama.ps1

# 2. 拉模型
wsl ollama pull llama3.2:3b

# 3. 啟動 Streamlit
cd D:\DOT\$hark
.\.venv\Scripts\Activate.ps1
streamlit run src\sharks\ui\streamlit_app.py
```

Streamlit auto-reload — 改檔不用重啟。

---

## §4. UI 流程(錄影建議)

| 秒 | 動作 | 觀眾看到什麼 |
|---|---|---|
| 0-10 | 選 NVDA | verdict STRONG_BUY,evidence 8、risk 1 |
| 10-30 | 滑過四象限 | 護城河 92、ROE 119%、Bollinger 上軌 |
| 30-40 | 點 📝 生成 Thesis | 本地 llama3.2 跑出來推薦理由 |
| 40-50 | 點 😈 反方論點 | 系統自己打臉 — 透明度 |
| 50-60 | 切到 DNN | verdict AVOID,evidence 2、risk 3 |
| 60-70 | 點 📝 生成 Thesis | LLM 也要承認「這個系統不推薦」 |

5-10 分鐘可拍完整集。

---

## §5. 程式碼結構

### `streamlit_app.py` 變更

```python
# Top of file: ensure src/ on sys.path so lazy imports work
_PROJECT_ROOT = Path("D:/DOT/$hark")
_SRC = _PROJECT_ROOT / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

# Sidebar adds:
"🧠 11. Deep Research + AI"

# Page body uses lazy import to avoid breaking pages 1-10 if Ollama is down:
try:
    from sharks.ai import local_llm as _llm
    LLM_AVAILABLE = True
except Exception as e:
    LLM_AVAILABLE = False
```

### 為什麼 lazy import

- 第 1-10 頁完全不依賴 Ollama
- 萬一 `local_llm.py` 改壞或環境壞,其他頁仍可用
- 使用者沒裝 Ollama 時,頁面顯示黃色提示而不是炸掉

---

## §6. Session state 設計

按鈕輸出存在 `st.session_state[f"{ticker}_thesis_text"]` / `..._devils_text`:
- 切 ticker 不會洗掉前一個的輸出(可比較)
- 重點:**LLM 呼叫很慢**(3-10 秒),不能每次 rerun 都重跑

---

## §7. 安全性

對齊 `CLAUDE.md` SAFETY 邊界:
- ✅ 純讀取 `outputs/deep-research-*.json`(本地檔)
- ✅ LLM 呼叫走 `http://localhost:11434`(本地 Ollama)
- ✅ 不接券商 API
- ✅ 不送 portfolio 到任何外部端點
- ✅ 不修改 `andysharks.md`
- ⚠️ 輸出 disclaimer:「LLM 輸出為研究輔助,非投資建議。系統 verdict + evidence 才是主軸。」

---

## §8. 下一步

### 短期(這週)
- 把 `deep_research.py` 跑出來的 ticker 範圍從 14 → 50(整個 fom-alpha top 50)
- 加 sidebar slider「LLM temperature」與「max_tokens」
- thesis 輸出可以 → Markdown 一鍵存到 `wiki/05_recommendations/`

### 中期(本月)
- LoRA fine-tune `llama3.2:3b` 用本地 14 隻 deep-research 報告當 training data
- 加「比較兩隻 ticker」模式(side-by-side thesis)
- 把 Finnhub 新聞接上,新聞摘要按鈕可用

### 長期
- 加「**Compiler-Principal 對話模式**」— 多輪詢問,LLM 用本地 wiki RAG 回答

---

## See also

- [[21_internalization_local_llm]] — 內化哲學 + Ollama setup
- [[19_streamlit_finnhub_famafrench]] — Streamlit MVP 起源(原 10 頁)
- [[09_postmortem_log]] — 為何要保留「反方論點」按鈕(自我打臉)

## Sources

- [Streamlit session_state docs](https://docs.streamlit.io/library/api-reference/session-state)
- [Ollama API reference](https://github.com/ollama/ollama/blob/main/docs/api.md)
