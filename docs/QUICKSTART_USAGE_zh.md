# $hark 實用快速上手指南（Discord Bot + Web GUI + 多代理整合）

這份文件讓你「好用一點」，不用每次都開一堆終端機。重點整合你已經有的 Discord bot、Streamlit GUI，以及我們之前建的 **Zellij 多代理 + RAG + cross-review.ps1（Claude 當 Orchestrator，Grok 當 Risk Officer）**。

所有操作嚴格遵守憲法：**recommend-only，絕不持金鑰、絕不下單、執行永遠是人類動作**。

---

## 1. 最推薦日常介面：Discord Bot（被動通知 + 互動查詢）

Bot 已經非常成熟：
- 自動在台灣時間發 **晨會 / 午會 / 晚會** 簡報（包含 FOM 選股、議會結論、本地 LLM 辯論）。
- `/council <主題>`：多人格議會（用本地 Ollama 辯論 + 投票 + 結論），非常適合 Risk Officer 審查。
- `/ask`、`/llm wiki`：直接對整個 $hark 知識庫問問題（內建 RAG）。
- `/llm claude` / `local` / `wiki` / `codex`：切換後端。
- 已經有 `wiki_rag.py`，可以查詢我們剛更新的 `disclosures.json` 護欄（Momentum Decoupling Lock、worktree RAG、資金硬截斷等）。

### 啟動方式（Windows，最簡單）

```powershell
# 第一次要設定 .env（複製範例）
copy .env.example .env
# 編輯 .env，填入 DISCORD_BOT_TOKEN（從 Discord Developer Portal 拿）

# 一鍵啟動 bot（會自動檢查 Ollama、本地模型、安裝 discord.py）
.\scripts\run_discord_bot.ps1
```

Bot 啟動後會常駐，自動發簡報。你可以在 Discord 頻道直接打指令。

**好用小技巧**：
- 把 bot 設成 Windows 登入自動啟動（Task Scheduler "At log on" 跑上面 ps1）。
- 在 Discord 用 `/council 檢查這個改動的 conflict_resolver 是否有問題` 來觸發本地多模型 Risk 審查。
- 用 `/llm wiki 黃靖哲動能 + TD-9 衝突怎麼解` 直接拉 RAG 護欄。

---

## 2. Web GUI 前端：Streamlit Dashboard（視覺化 + 手動操作）

已經有完整的 dashboard：
- 今日 Top Picks
- Bubble Chart、Filter Table
- Portfolio Risk
- Deep Research + 本地 LLM
- Bubble Watch、System Audit 等

### 啟動方式

```powershell
# 確保有 venv（第一次會自動建立）
# 在專案根目錄執行：
.\.venv\Scripts\python.exe -m streamlit run src/sharks/ui/streamlit_app.py --server.port 8501
```

打開瀏覽器：`http://localhost:8501`

**整合建議（讓它更好用）**：
- 在 Streamlit 裡加一個按鈕 "Run Risk Officer Review"，背後呼叫 `cross-review.ps1 -UseRag` 並把報告顯示在頁面上。
- 頁面上可以直接輸入 worktree 路徑，讓 RAG 掃描 Writer 的最新改動。
- 目前已有 `src/sharks/ui/server.py` + 靜態 HTML/JS，可以做成更輕量的 dashboard。

---

## 3. 進階多代理工作流：Zellij + Claude 當總指揮 + Skills 互相呼叫 Review（我們之前建的最強部分）

當你想要「Claude 規劃 → Writer (Aider + local) 在隔離 worktree 寫 code → Grok Risk Officer 用 RAG 嚴格審查」這種閉環時，用這個。

### 啟動方式（最接近「好用」的視覺化多代理）

```powershell
# Windows 端先建立 worktree（Writer 專用，永遠不碰 main）
git worktree add ..\hark-write-$(Get-Date -Format "yyyyMMdd-HHmm") -b write-loop/2026-06-13

# 切到 WSL 啟動 Zellij（推薦）
# 在 WSL 裡：
cd /mnt/d/DOT/\$hark
zellij --layout write-loop
```

Zellij 會開 3 個 pane：
- **Orchestrator**：貼 Claude 的任務、閱讀 Risk 報告、做最終決策。
- **Writer**：跑 `aider --model ollama:qwen2.5-coder:32b` 在 worktree 裡寫東西（包含剛加的 conflict_resolver）。
- **Risk Officer**：直接打 
  ```bash
  ./scripts/cross-review.ps1 <目標> -UseRag -Worktree "../hark-write-..." -Reviewer grok -Task "檢查 Momentum Decoupling + 資金 clipping"
  ```
  （或用 local）

**Claude 如何溝通**（最重要）：
- Claude 在它自己的 Windows 終端機（VSCode / Claude Code / Cursor）直接執行上面的 PowerShell 指令。
- PS1 會自動帶 RAG（包含我們剛更新的 disclosures.json 所有護欄），呼叫 WSL Grok 當 Risk Officer。
- 報告自動存到 `outputs/cross-review/`，大家（包含 Discord bot）都看得到。
- 你可以把 Zellij 視窗分享，或把報告內容貼給 Claude 繼續迭代。

### Skills 讓 Claude / Grok 互相呼叫 Review（結構化、無痛）

我們已經把 review 機制變成 **skills**，讓 Claude Code / Grok Build 可以像呼叫工具一樣互相要求對方做 Risk Officer 審查：

- **.claude/skills/grok-risk-review/SKILL.md**：Claude 載入這個 skill 後，會得到精確的 PS1 指令（自動帶 -UseRag -Worktree + disclosures 護欄），執行後把 Grok 的 5-section 報告拿回來繼續規劃。
- **.grok/skills/risk-review/SKILL.md**：Grok 載入後，會用正確的 RAG + 契約 prompt 自己擔任 Risk Officer，輸出報告（或透過 cross-review 橋接）。

**使用方式**：
- 在 Claude Code 裡，當你需要 Grok 審查時，直接說「Use the grok-risk-review skill on target: ... Task: ... Worktree: ...」
- 在 Grok Build 裡，說「Use the risk-review skill ...」
- 兩個 skill 都會強制注入最新 contracts（Momentum Decoupling Lock、worktree RAG、資金 clipping、TD-9 guard 等），完全符合我們的所有 P0/P1 修正。

這樣 Claude 和 Grok 可以結構化互相呼叫 review，不用每次手動 copy prompt。

### Discord 激烈辯論（大家都在 Discord）

bot 已經超適合「激烈辯論」：
- `/council <主題>` 就是開場 → 交叉質詢 → 答辯 → 投票 → 正反方 → 主席結論 的多代理 debate（本地多模型 + 人格，如 huang, bear, fomquant...）。
- 我已經幫你加了新 command：

**`/grok_review <target> [task]`**

範例：
`/grok_review working 對照 disclosures.json 檢查 conflict_resolver + worktree 改動`
`/grok_review src/sharks/decision/conflict_resolver.py 驗證 Momentum Decoupling Lock 是否正確`

它會呼叫 cross-review.ps1 -UseRag， 把 Grok 的完整 Risk Officer 報告（含 RAG 護欄）貼到 Discord。

之後你可以立刻接 `/council 根據剛剛的 Grok review，這個改動該不該 merge？` 

讓本地人格 + 任何「grok-risk-officer」風格的討論在 Discord 激烈進行（報告可以直接餵給 council 當 context）。

`/llm wiki` 或 `/llm claude` 也可以直接問 RAG / Claude 關於 review 的意見。

**讓辯論更完整**：
- 先 `/grok_review` 拿 Grok 的 guardrail 報告。
- 再 `/council <把報告重點當主題>` 讓多個人格（包含你自訂的「grok-risk」風格）交叉辯論。
- 結果可以再餵回 Zellij 的 Orchestrator 或 Writer 繼續迭代。

Discord 現在就是全團隊（Claude via skill/terminal、Grok via review、local models via council、RAG via wiki）的激烈辯論場地。 

重啟 bot 後新 command 就會出現（用 run_discord_bot.ps1 即可）。

---

## 4. 一鍵 / 半自動整合建議（讓日常更順）

### 推薦日常流程（好用版）
1. 早上開 Discord bot（或讓它常駐）。
2. Bot 自動發晨會簡報到 Discord。
3. 有疑問時在 Discord 打 `/council` 或 `/llm wiki` 快速查（RAG 立刻回答）。
4. 需要深度多代理工作（例如實作某個 proposal）時 → 開 Zellij → 讓 Claude 當 Orchestrator 指揮 Writer + Risk Officer。
5. 想看漂亮圖表 → 開 Streamlit GUI。
6. 重要決定前，一定用 `-UseRag -Worktree` 跑 cross-review 當 Risk gate。

### 如何把新工具（conflict_resolver + worktree RAG）整合進 bot/GUI

已經有基礎（discord/wiki_rag.py）：
- Bot 的 `/llm wiki` 已經能查 disclosures。
- 可以請 Writer 在 worktree 裡擴充 bot command，例如新增 `/riskreview <target>`，背後呼叫 cross-review.ps1 並把結果貼回 Discord 頻道。

簡單擴充指令（可丟給 Aider）：
在 discord 裡加一個 command，執行 PowerShell 並抓輸出發訊息。

---

## 5. 實用小工具與設定

- **檢查 Ollama**（bot 和 council 都需要）：`.\scripts\check_ollama.ps1`
- **每日自動簡報**：`.\scripts\daily_am.ps1` 和 `daily_pm.ps1`（bot 會自己用）。
- **RAG 單獨測試**：`python3 scripts/rag_retriever.py --query "Momentum Decoupling Lock" --k 5`
- **設定 .env**：複製 `.env.example`，至少填 `DISCORD_BOT_TOKEN` 和本地模型相關。

**讓它更「一鍵」**：
你可以建立一個 `scripts/launch-all.ps1`，裡面依序檢查 Ollama、啟動 bot（背景）、提醒你開 Streamlit、開 Zellij。

---

## 總結：怎麼開始用（今天就能跑）

1. 先跑 `.\scripts\run_discord_bot.ps1`（最快看到價值）。
2. 同時開 `streamlit run src/sharks/ui/streamlit_app.py` 看 dashboard。
3. 有需要深度工作時，用上面 Zellij + `-Worktree` + `-UseRag` 的流程，讓 Claude 當大腦、Grok 當 Risk Officer。
4. 所有新護欄（剛修的 P0 衝突 + 資金 clipping + worktree RAG）已經自動被 RAG 吃進去，任何 review 都會被提醒。

想更進一步整合（例如讓 Discord 直接有「Run Full Risk Review」按鈕、或 Streamlit 內嵌 cross-review 結果），直接把需求丟給 Claude + Writer 在 worktree 裡實作，然後用 Risk Officer gate 確認就行。

有任何具體卡住的地方（例如 .env 怎麼設、某個指令出錯），把錯誤訊息貼上來，我可以給精準下一步。

這個系統現在已經「好用」到可以日常靠 Discord 被動接收 + 需要時開 GUI + 深度時開多代理閉環的程度了。去用吧！🦈

（完整背景與 master prompt 見 `docs/FULL_CLAUDE_CODEX_GROK_ZELLIJ_TMUX_MULTI_AGENT_EXECUTION_PLAN_zh.md`）