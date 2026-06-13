# $hark 多代理執行完整計畫（中英對照快速審閱版）

**日期**：2026-06-13  
**目的**：讓你（用戶）可以用「一次貼上」的方式，把我（Grok）的完整回應 + 審查 + 執行計畫，丟給 Claude / Codex 進行迭代，最後產生可直接執行的指令，不需要頻繁來回對話。

這份文件直接回答你：
- 「so it can communicate w/ claude ??」
- 「how about tmux & zellij & multi agents」
- 「push your response & review by codex & claude & iteration then generate complete way to execute, I don't want to reply frequently」

---

## Part 1：輸入 - 你貼的「Codex 漏洞掃描」全文

（請把你之前貼的整段「這份長篇... (a)(b)(c) 選項」直接複製到這裡，或讓 Claude 直接讀你原始訊息。重點摘要如下：）

掃描指出 5 大致命漏洞與改進：
1. 長線多頭偏誤 → 需完整 03-long-short-taxonomy + 主動放空機制 + 做空排除限制。
2. 「每日推薦 10 檔新股」會導致存量爆炸 → 改為 2 long_new + 2 short_new + 6 position_followup。
3. 免費 API 無法支撐高頻（尤其是加密貨幣 Order Book）→ 需 ccxt_client。
4. TD-9 在強勢行情會被踩過去 → 需價量 + 基本面雙重驗證（量縮見頂、爆量續抱）。
5. LLM 一直重寫策略直到回測漂亮 = p-hacking → 限制超參數調整 + 使用 CPCV 驗證。

---

## Part 2：Grok（Risk Officer）對掃描的審查（已使用 RAG 即時檢索）

我已載入完整契約（sharks.md、CLAUDE.md、AGENTS.md、philosophy/09-point-in-time），並用 `rag_retriever.py` 即時檢索相關文件。

**RAG 檢索結果重點**：
- disclosures.json（剛更新）排第一。
- 後面緊接 03-long-short-taxonomy.md、05-decision-rubric.md、concepts/td-9-sequential.md、06-exclusions.md、src/sharks/data/ccxt_client.py。

**5 區段審查結論**：

1. **CORRECTNESS（正確性）**  
   掃描對「舊版」哲學文件來說非常準確。但**目前 repo 已經把掃描裡大多數「極致改進方案」都實現了**：
   - 03-long-short-taxonomy.md 已存在（四象限：多頭真漲/虛漲、空頭真跌/虛跌、優先用 Put、嚴格做空排除）。
   - 05-decision-rubric.md 已明確規定 2 long_new + 2 short_new + 6 position_followup + 禁止 padding。
   - concepts/td-9-sequential.md 已內建「volume-validation guard」（量縮 + 情緒高峰 = 真見頂；量爆 + 基本面 = 續抱）。
   - src/sharks/data/ccxt_client.py 已存在（read-only stub，明確寫安全限制）。
   - 06-exclusions.md 已寫 short_interest ≤20%、borrow fee 限制。
   這代表之前的 Codex / Gemini 審查已經有效，現在的系統比掃描假設的狀態更強。

2. **CONTRACT FIDELITY（契約忠誠度）**  
   非常高。掃描正是系統設計要吸收的外部審查類型。建議與 sharks.md 原則一致。

3. **POINT-IN-TIME（時點紀律）**  
   掃描本身沒有 as_of_timestamp，未來任何總結頁面都必須補上。目前哲學文件前言都已正確。

4. **RISK DISCIPLINE（風險紀律）**  
   掃描準確指出真實尾部風險（長空偏誤、持倉膨脹導致幻覺推薦、TD-9 在主升段失效、p-hacking、資料來源欺騙）。排除清單與 Put 優先的設計很好。

5. **TOP FIX（最高優先修正）**  
   - 這次掃描主要是「驗證我們的多代理 + RAG 迴路有效」。
   - 核心哲學與資料 stub 已到位，**不需要大改 Phase 1 骨架**。
   - 剩餘低成本動作：
     - 已把掃描重點鎖進 `rag-data/contracts/disclosures.json`（本會話完成）。
     - 用 Zellij / tmux + cross-review.ps1 讓 Claude 自己持續審查與迭代。
     - 建立 proposal 記錄本次驗證結果。

**總結**：你貼的掃描，絕大部分內容在當前系統已經被實現。這是好消息，證明之前的多代理迭代有效。接下來重點是「讓 Claude 能自主驅動這個迴路」。

---

## Part 3：模擬 Codex 審查 + Claude 審查 + 一次迭代

**Codex 審查（嚴格架構/程式碼視角）**：
- 同意 Grok 的現況分析。
- ccxt_client.py 的 stub 寫得正確（永遠 read-only、有完整安全說明）。
- 建議為 p-hacking 補充明確規則到 08-risk-and-position.md，並由 RAG 強制拉取。
- 結論：「骨架已經很穩，現在要專注執行迴路（Zellij + PS1 橋接），讓未來類似掃描可以由 Claude + local model + Grok 自動處理。」

**Claude 審查（Orchestrator 視角）**：
- 感謝掃描的尖銳診斷。
- 確認 03/05/06/concepts 檔案已經包含所需結構。
- 希望有一份「單一綜合執行清單」，把掃描與我們現有工具（RAG contract、cross-review.ps1、Zellij）串起來。
- 迭代要求：「把掃描語言明確寫進 RAG contract，並給我一個 master prompt，讓我（Claude）可以自己當 Orchestrator，不用每次都問 Grok。」

**迭代後結果**（本會話已執行）：
- disclosures.json 已更新，鎖定長空四象限、TD-9 量價守門、2+2+6、禁止 p-hacking（CPCV）、ccxt 為加密高頻必要來源。
- 本文件 + 既有 Zellij layout + cross-review.ps1 就是那個「單一綜合執行計畫」。

---

## Part 4：完整可執行計畫（一次複製貼上就能跑，無需頻繁回覆）

### 前置條件
- WSL 已安裝 grok、python3、ollama（建議 qwen2.5-coder + nomic-embed-text）、zellij。
- Windows 端可執行 PowerShell 並呼叫 WSL。
- 你已經有我們之前建立的 rag_retriever.py、更新後的 cross-review.ps1、zellij layout。

### 步驟 1：用 RAG 強制驗證目前狀態 vs 掃描
```bash
# WSL 裡執行
python3 scripts/rag_retriever.py --query "long-short-taxonomy 2 long_new 2 short_new TD-9 volume guard ccxt high-freq no p-hacking CPCV" --k 5

# Windows 端（Claude 可直接在終端機跑）
.\scripts\cross-review.ps1 philosophy/03-long-short-taxonomy.md philosophy/05-decision-rubric.md philosophy/concepts/td-9-sequential.md src/sharks/data/ccxt_client.py -UseRag -Reviewer local -Task "驗證是否已實現掃描中的四象限、2+2+6、TD-9 量價守門、ccxt stub、做空排除，並確認 RAG contract 已鎖定"
```

### 步驟 2：啟動多代理環境（Zellij 或 tmux）

**Zellij（推薦）**：
```bash
# WSL
mkdir -p ~/.config/zellij/layouts
cp zellij/layouts/write-loop.kdl ~/.config/zellij/layouts/
git worktree add ../$hark-write-$(date +%Y%m%d-%H%M) -b write-loop/2026-06-13
zellij --layout write-loop
```

**tmux 版本**（如果你偏好 tmux）：
建立或執行 `scripts/tmux-write-loop.sh`（內容已寫在 zellij/README.md 裡）。

### 步驟 3：Claude 如何與整個團隊溝通（核心答案）

1. **最重要橋接工具**：Claude 在 Windows 端的終端機直接執行：
   ```powershell
   .\scripts\cross-review.ps1 <目標檔案或 working> -UseRag -Reviewer grok -Task "針對漏洞掃描做完整 Risk Officer 審查"
   ```
   - 這個腳本會自動帶入 RAG context（包含 disclosures.json 裡所有 guard）。
   - 會呼叫 WSL 裡的 Grok（或 local），產生結構化報告並存到 `outputs/cross-review/`。
   - Claude 可以直接讀取報告，不需要我中間轉譯。

2. **Zellij / tmux 並行工作**：
   - Orchestrator pane：Claude 生成任務、閱讀報告、做最終決策。
   - Writer pane：跑 Aider + 本地模型，在隔離 worktree 裡寫程式。
   - Risk Officer pane：直接執行上面的 cross-review.ps1 指令。

3. **共享狀態**：所有報告、rag-data/contracts、worktree diff 都在同一個檔案系統，Claude 看得見。

4. **未來迭代不用找我**：
   - Claude 自己決定什麼時候用 `-Reviewer local`（省錢、快速）、什麼時候用 `-Reviewer grok`（關鍵 Risk gate）。
   - 每次重要決策都強制走 RAG，disclosures.json 裡的 guard 會自動出現。

### 步驟 4：把掃描的 5 個漏洞「落地執行」（大多是驗證 + 記錄）

因為目前狀態已經很接近掃描要求，執行重點是「用工具驗證 + 鎖定 guard + 建立可重複流程」：

- 長空分類與做空限制 → 已在 03 + 06，RAG 已鎖定。
- 每日 2+2+6 結構 → 已在 05-decision-rubric，RAG 已鎖定。
- ccxt_client → 已存在正確 stub。
- TD-9 量價守門 → 已在 concept，RAG 已鎖定。
- 禁止 p-hacking → 已加入最新 disclosures.json。

**可選動作**（若想更正式）：
在 worktree 裡建立 proposal：
```bash
cat > philosophy/_proposals/vuln-scan-2026-06-13-consolidated.md << 'EOF'
[貼上掃描重點 + 目前已實現狀態 + 「已透過 RAG contract 鎖定，2026-06-13」]
EOF
```

### 步驟 5：給 Claude 的一次性 Master Prompt（最重要！）

把下面這整段（從「你現在是 $hark 的 Main Orchestrator...」開始）複製，貼給 Claude（可再附上本文件 + 最新 cross-review 報告）：

```
你現在是 $hark 的 Main Orchestrator（角色定義見 CLAUDE.md）。Grok 已經用 RAG + cross-review 工具對我貼的「漏洞掃描」做過 Risk Officer 審查。

以下是完整背景：
[把本文件（docs/FULL_..._zh.md）的全部內容貼上來]

最新 RAG 強制產生的 cross-review 報告：
[貼上 outputs/cross-review/ 裡最新的報告]

你的任務（請在單一回覆中完成，不要問問題）：
1. 以 Codex 角色，對掃描 + Grok 審查 + 目前 repo 狀態，做一次嚴格的架構/程式碼審查。
2. 以你自己（Claude Orchestrator）角色，再做一次審查，並進行一次迭代。
3. 輸出「最終完整可執行指令區塊」（編號步驟、任何需要建立的檔案內容用 cat > 方式、Zellij/tmux 啟動方式、你未來如何透過 PS1 橋接自己驅動 Grok Risk Officer、任何小幅剩餘修改）。
4. 讓人類只要複製你的輸出就能一次執行完，之後就把完整 ownership 交給你持續運作。完全不要再問 Grok 問題。

最後以清楚的交接結尾：「Human: 請執行以下指令。未來所有審查請直接在你的終端機跑 cross-review.ps1 -UseRag ...」
```

---

## 總結與下一步

- Claude 溝通方式：主要靠 Windows 端執行 `cross-review.ps1 -UseRag`，它會自動帶 RAG guard 叫 Grok（或 local）當 Risk Officer。
- Zellij / tmux：已提供 3-Pane 隔離佈局（Orchestrator / Writer / Risk Officer），Writer 永遠在 worktree 裡操作。
- RAG 護欄：disclosures.json 已更新，強制鎖定掃描裡的所有關鍵規則。
- 你現在只要做兩件事：
  1. 跑步驟 1 的驗證指令。
  2. 把「步驟 5」的 Master Prompt 貼給 Claude，讓它輸出最終執行清單。

之後你就可以用 Zellij + PS1 橋接，持續讓 Claude 當 Orchestrator、Codex/Grok 當 Reviewer，處理任何新掃描或修改，而不需要頻繁找我。

所有操作都遵守專案契約（read-only、point-in-time、recommend-only、無 raw/ 修改）。

需要我現在幫你產生任何單一小檔案（例如更完整的 tmux script 或 proposal 模板）嗎？還是直接用上面這個計畫就夠了？（我建議直接用上面這個，已經很完整。）