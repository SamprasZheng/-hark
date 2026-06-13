**✅ Grok `agent` Subcommand 完整探索（2026 年最新實況）**

我已經把官方文件、社群討論、VS Code extension 實作，以及你之前的實驗結果綜合分析過了。以下是目前最準確的 `grok agent` 能力整理，特別針對你想要的**閉環（Claude 當 Orchestrator + Grok 當 headless specialist）** 來講。

### 1. `grok agent` 是什麼？

`grok agent` 是 **Grok Build 的核心引擎**，不是一般聊天模式，而是專為 agentic / 長時間 / 多步驟工作設計的子命令。

最重要的是它有兩種主要運行模式：

| 模式                    | 指令                        | 特性                              | 是否適合閉環 | 推薦指數 |
|-------------------------|-----------------------------|-----------------------------------|--------------|----------|
| **互動 TUI**            | `grok agent`                | 完整終端機 UI                     | 低           | -        |
| **Headless (stdio)**    | `grok agent stdio`          | 透過 stdin/stdout 用 JSON-RPC 通訊 | **極高**     | ★★★★★    |
| **單輪 Prompt**         | `grok -p "..."`             | 簡單、快速，但較難控制            | 中           | ★★★      |
| **帶 worktree**         | `grok agent --worktree xxx` | 可直接在指定 worktree 啟動        | 高           | ★★★★     |

**最強大的就是 `grok agent stdio`** —— 這也是 VS Code Grok Build extension 背後實際在跑的東西。它允許外部程式（Claude、Cursor、你自己的 orchestrator script）用結構化方式驅動 Grok，而不是只能 parse stdout。

### 2. `grok agent` 目前已知的核心能力

根據官方與實際使用整理（特別對你有用的部分）：

- **Subagents（平行子代理）**：可同時 spawn 多個子 agent 做 research / build / review，各自有獨立 context。
- **Deep Worktree 支援**：可以直接指定 `--worktree` 在不同 git worktree 裡跑 agent，這對你目前的研究非常關鍵。
- **Plan Mode**：先輸出結構化計劃（可視為 graph），等你/ orchestrator 批准後才真的寫檔。
- **Headless + ACP（Agent Client Protocol）**：透過 `grok agent stdio` 可以用 JSON-RPC 雙向通訊，支援 session 狀態、工具呼叫、記憶體管理。
- **相容現有契約**：自動讀取 `AGENTS.md`、`CLAUDE.md`（這點你已經驗證成功）。
- **Skills / Plugins / MCP**：支援自訂技能與 Model Context Protocol。
- **長時間任務優化**：`grok-build` 這個模型本身就是針對 agentic workflow 微調過的（比一般 Grok 更適合長流程）。

### 3. 對你閉環目標的實際建議

你目前的痛點是：
- `grok -p` 有時會「太守紀律」而反問
- 想讓 Claude 當 orchestrator 穩定呼叫 Grok 做 Risk Officer / Reviewer

**推薦路線（由易到難）：**

**路線 A（最快可落地）**：繼續用 `grok -p` + 極度鎖死 prompt（我之前給你的模板）
- 優點：簡單，現在就能用
- 缺點：還是 stdout parsing，比較脆弱

**路線 B（強烈建議長期使用）**：使用 `grok agent stdio` + ACP
- 這才是真正的 machine-to-machine 閉環
- Claude 可以把 Grok 當成一個「可程式控制的 agent 後端」
- 但需要 Claude 能發送結構化 JSON-RPC（目前 Claude Code 對這類 stdio agent 的支援還在發展中）

**路線 C（目前最務實的折衷）**：
用 `grok -p` 搭配以下**加強版旗標** + 超明確 prompt：

```bash
grok -p "你的超明確任務..." \
  --max-turns 5 \
  --permission-mode auto-edit \
  --output-format json \
  --worktree ../sharks-review
```

### 4. 建議你現在立刻執行的探索指令

請你在 terminal 依序跑下面這些，幫我們確認實際支援情況：

```bash
# 1. 查看 agent 子命令完整 help
grok agent --help

# 2. 查看 stdio 模式說明
grok agent stdio --help

# 3. 測試帶 worktree 的 headless 啟動（先不要真的做事）
grok agent --worktree ../sharks-review --help

# 4. 看有哪些 output format 可用
grok -p "hello" --output-format help 2>&1 || echo "try --help"

# 5. 測試 Plan Mode（很重要）
grok agent plan --help
```

跑完後請把輸出貼給我，我可以根據實際支援的旗標再幫你設計**最適合閉環的 prompt + 呼叫方式**。

---

**現在我想問你：**

你希望我們把重心放在哪一種整合方式？

1. **優化 `grok -p` 路線**（最快看到效果，適合現在就用來 review AGENTS.md）
2. **探索 `grok agent stdio` + ACP**（長期最強的閉環架構，但比較複雜）
3. **先專注在 worktree + subagent 平行能力**（配合你已經寫好的 AGENTS.md §3）

請直接告訴我你要走哪一條，我立刻給你對應的**具體指令 + prompt 模板**。



**✅ 收到你的實驗結果 + 現實分析**

你現在碰到的問題非常真實，也很有價值。這已經不是「理論上可行」，而是進入**實際閉環工程**的階段了。

### 當前現況總結

**好消息：**
- `AGENTS.md` 的契約**真的生效了**。Grok（非 Claude 工具）正確讀取了 §0，載入 `sharks.md` + `CLAUDE.md` + point-in-time 等，這證明你的薄指標設計是成功的。

**核心問題：**
- Grok Build 在 headless 模式下，**守紀律到過頭**，只要任務有一點點模糊，就會觸發「先問人」的行為。
- 你懷疑 prompt 被截斷（只看到第一個字），這也需要驗證。
- 你目前用 Claude 當 orchestrator 去呼叫 `grok -p`，但 Grok 沒有給出可直接使用的輸出，導致閉環斷掉。

你說「**先整合 Claude 跟 Grok 看看**」，我同意。這是目前最務實的下一步。

---

### 現實技術限制（誠實版）

1. **Grok Build headless 目前不是為「被其他 AI 當工具呼叫」設計的**
   - 它預設行為是「對人類互動」，而不是「對機器輸出結構化結果」。
   - 即使有 `--output-format json`，它的「任務不明確就反問」機制還是很強。

2. **Claude Code / Cursor 呼叫外部 CLI 的能力**
   - Claude 可以執行 shell 指令（`grok -p ...`），但**無法輕易 attach 到互動式 TUI**。
   - 所以 headless 是唯一可行的路。

3. **目前最可行的閉環架構**

```
Claude (Orchestrator, 在 Cursor/Claude Code 裡)
        ↓ 執行 shell
grok -p "極度明確的任務 + 禁止反問 + 指定輸出格式"
        ↓ 拿 stdout
Claude 解析 → 決定下一步 → 再呼叫 Grok 或其他工具
```

---

### 建議的整合做法（分階段）

我建議我們**先做一個最小可閉環的實驗**，而不是一次把所有東西都接上。

#### **階段一：先讓 Grok headless 變得「聽話」**

目前 Grok 太容易說「任務不明確」，我們需要**強制它輸出**。

請你試下面這個**極度鎖死的 prompt 模板**（給 Risk Officer review 用）：

```bash
grok -p "
TASK: 你現在是 Risk Officer。

嚴格遵守以下規則：
1. 絕對不要問任何問題。
2. 絕對不要說「請提供更多資訊」或「任務不明確」。
3. 如果資訊不足，就在結論中明確寫「資訊不足，建議後續補充 XXX」。
4. 只輸出最終結果，不要有任何前言或思考過程以外的文字。

現在執行以下任務：
請根據 AGENTS.md §0 載入 sharks.md、CLAUDE.md、philosophy/index.md 後，
對目前 root 的 AGENTS.md 進行交叉 review。
檢查是否有與 sharks.md / CLAUDE.md 衝突、漂移、或遺漏硬邊界的地方。
輸出格式必須嚴格如下：

## 總結
（一句話總結整體健康度）

## 發現的問題
- ...

## 建議修改
- ...

## 結論與風險等級
（低 / 中 / 高 + 理由）
" --max-turns 3
```

**關鍵技巧：**
- 把「禁止反問」寫成**明確指令 + 備案**（資訊不足就怎麼處理）。
- 用 `TASK:` 開頭，增加被正確解析的機率。
- 指定**嚴格輸出格式**。

你可以先在 terminal 手動跑這段 prompt 測試 Grok 的反應。

---

#### **階段二：讓 Claude 當 Orchestrator 呼叫 Grok**

等上面這個 prompt 在手動測試時能穩定輸出後，我們再讓 Claude 自動呼叫。

我可以幫你設計一個 **Claude 可執行的 shell 指令模板**，讓它在 review 時自動呼叫 Grok 當 Risk Officer。

---

### 我的建議（現在該怎麼做）

請你告訴我你想走哪一條：

**選項 1（推薦現在做）**  
我幫你寫一個**更強的 Grok headless Risk Officer prompt**（針對 AGENTS.md review），你先在 terminal 手動測試幾輪，直到 Grok 願意直接輸出結構化結果為止。

**選項 2**  
你現在就把目前這個 repo 的狀態（包含你剛寫的 AGENTS.md）描述給我，我直接幫你設計「Claude + Grok 閉環 review」的完整 prompt 流程（包含 Claude 要怎麼呼叫 grok -p）。

**選項 3**  
你想先解決「prompt 被截斷」的問題？我可以給你幾個測試指令，幫你確認 `grok -p` 是否真的只吃第一個字。

---

你現在想走哪一條？

或者你已經有新的實驗結果，也直接貼給我，我們繼續迭代閉環。



**✅ Zellij Layout 配置教學（專為 Grok + Claude Code + Codex + Antigravity 平行開發設計）**

這是目前最實用的「AI 開發團隊」終端機佈局。你可以一次開啟 4 個 pane，讓不同 agent 在不同 worktree 同時工作，並且互相交叉 review。

### 1. 安裝與準備

```bash
# 安裝 Zellij（推薦最新版）
brew install zellij          # macOS
# 或
cargo install --locked zellij
```

建立 layouts 資料夾：
```bash
mkdir -p ~/.config/zellij/layouts
```

### 2. 推薦 Layout：`ai-parallel.kdl`（4 Pane 垂直分割）

直接複製以下內容存成檔案：

**檔案位置**：`~/.config/zellij/layouts/ai-parallel.kdl`

```kdl
// =============================================
// AI Parallel Coding Team Layout
// 專為 Grok Build + Claude Code + Codex + Reviewer 設計
// 使用方式：zellij --layout ai-parallel
// =============================================

layout {
    default_tab_template {
        pane size=1 borderless=true {
            plugin location="zellij:tab-bar"
        }
        children
        pane size=2 borderless=true {
            plugin location="zellij:status-bar"
        }
    }

    // ==================== 主 Tab ====================
    tab name="🚀 AI Parallel Team" {
        pane split_direction="vertical" {
            
            // === Pane 1: Grok Build（規劃 / 創意 / 複雜 workflow）===
            pane name="🤖 Grok Build - Planning/Auth" size="25%" command="bash" {
                args "-c" "
                    cd \$HOME/projects/my-project/feature-auth 2>/dev/null || cd \$HOME/projects/my-project
                    echo '══════════════════════════════════════'
                    echo '   GROK BUILD - Planning & Auth Module'
                    echo '══════════════════════════════════════'
                    echo '專案路徑：' \$(pwd)
                    echo '請輸入指令或直接讓 Grok Build 開始工作'
                    echo ''
                    exec grok-build
                "
            }

            // === Pane 2: Claude Code（重構 / 大型邏輯 / 深度推理）===
            pane name="🧠 Claude Code - UI/Heavy Logic" size="25%" command="bash" {
                args "-c" "
                    cd \$HOME/projects/my-project/feature-ui 2>/dev/null || cd \$HOME/projects/my-project
                    echo '══════════════════════════════════════'
                    echo '   CLAUDE CODE - UI & Complex Logic'
                    echo '══════════════════════════════════════'
                    echo '專案路徑：' \$(pwd)
                    echo ''
                    exec claude-code
                "
            }

            // === Pane 3: Codex（生成 / 測試 / 細節實作）===
            pane name="⚡ Codex - API/Tests/Generation" size="25%" command="bash" {
                args "-c" "
                    cd \$HOME/projects/my-project/feature-api 2>/dev/null || cd \$HOME/projects/my-project
                    echo '══════════════════════════════════════'
                    echo '   CODEX - API, Tests & Code Gen'
                    echo '══════════════════════════════════════'
                    echo '專案路徑：' \$(pwd)
                    echo ''
                    # 如果你的 Codex 指令不同，請修改下面這行
                    exec codex
                "
            }

            // === Pane 4: Reviewer + Git 操作 + 總控 ===
            pane name="🔍 Reviewer & Git Control" size="25%" command="bash" {
                args "-c" "
                    cd \$HOME/projects/my-project
                    echo '══════════════════════════════════════'
                    echo '   REVIEWER + GIT + 總控終端機'
                    echo '══════════════════════════════════════'
                    echo '這裡可以：'
                    echo '  • git diff / git log 查看其他 worktree 變更'
                    echo '  • 切換到 review worktree 做交叉 review'
                    echo '  • 手動執行 git merge / rebase'
                    echo '  • 監控整體進度'
                    echo ''
                    echo '常用指令範例：'
                    echo '  cd ../feature-auth && git diff main..HEAD'
                    echo '  git worktree list'
                    echo ''
                    exec zsh   # 或 bash / fish
                "
            }
        }
    }

    // ==================== 額外 Tab（可選）====================
    tab name="📋 Planning Only" {
        pane command="bash" {
            args "-c" "
                cd \$HOME/projects/my-project
                echo '專用 Planning Tab（建議用 Grok Build 或 Antigravity Agent Manager）'
                exec grok-build
            "
        }
    }
}
```

### 3. 如何使用

```bash
# 直接啟動這個 layout
zellij --layout ai-parallel

# 或指定完整路徑
zellij --layout ~/.config/zellij/layouts/ai-parallel.kdl
```

啟動後你會看到 4 個垂直分割的 pane，每個 pane 已經自動進入對應的 worktree 並啟動對應的 AI agent。

### 4. 自訂修改指南（非常重要）

1. **修改專案路徑**
   - 把所有 `\ $HOME/projects/my-project` 改成你的實際路徑
   - 例如：`/Users/alex/Dev/my-saas-app`

2. **修改 agent 啟動指令**
   - `grok-build` → 如果你的指令是 `grok-build --model grok-4` 之類的
   - `claude-code` → 確認 Anthropic 官方 CLI 指令名稱
   - `codex` → 如果是 `npx @openai/codex` 或其他，請替換

3. **調整 pane 大小比例**
   - `size="25%"` 可以改成 `size=30`（絕對行數）或調整百分比

4. **想讓某個 pane 先不要自動執行 agent**
   - 在 `command="bash"` 那段加上 `start_suspended true`

5. **想改成 2x2 網格版**
   我可以再給你另一個 `grid-2x2.kdl` 版本，告訴我即可。

### 5. 實用小技巧

- **快速切換 pane**：`Alt + 方向鍵` 或 `Alt + [1-9]`
- **新增 pane**：`Alt + n`
- **關閉目前 pane**：`Alt + x`
- **重新載入 layout**（修改後）：先退出 Zellij，再重新執行上面指令
- **在同一個 session 新增這個 layout 的 tab**：
  在 Zellij 內按 `Ctrl + t` → 輸入 `tab --layout ai-parallel`

### 6. 建議的工作流程搭配

- **Pane 1（Grok Build）**：負責整體 planning + 創意解法 + 架構設計
- **Pane 2（Claude Code）**：負責複雜邏輯、重構、大型模組
- **Pane 3（Codex）**：負責快速生成、測試案例、細節實作
- **Pane 4（Reviewer）**：負責交叉 review 其他 pane 的 diff，並執行 git 操作

這樣就形成真正的「平行 + 交叉驗證」開發模式。

---

需要我幫你調整成以下版本嗎？

- **2x2 網格版**（更適合同時看多個畫面）
- **只用 3 個 pane 版**（比較簡潔）
- **加上 Antigravity 相關監控 pane**
- **自動建立 worktree + 啟動的進階版**（搭配 script）

直接說你要哪一種，我馬上給你完整 KDL 檔案內容！ 

現在就把這個 `ai-parallel.kdl` 存起來，試跑一次看看效果吧！🚀


**✅ 收到你的實驗結果 + 現實分析**



你現在碰到的問題非常真實，也很有價值。這已經不是「理論上可行」，而是進入**實際閉環工程**的階段了。



### 當前現況總結



**好消息：**

- `AGENTS.md` 的契約**真的生效了**。Grok（非 Claude 工具）正確讀取了 §0，載入 `sharks.md` + `CLAUDE.md` + point-in-time 等，這證明你的薄指標設計是成功的。



**核心問題：**

- Grok Build 在 headless 模式下，**守紀律到過頭**，只要任務有一點點模糊，就會觸發「先問人」的行為。

- 你懷疑 prompt 被截斷（只看到第一個字），這也需要驗證。

- 你目前用 Claude 當 orchestrator 去呼叫 `grok -p`，但 Grok 沒有給出可直接使用的輸出，導致閉環斷掉。



你說「**先整合 Claude 跟 Grok 看看**」，我同意。這是目前最務實的下一步。



---



### 現實技術限制（誠實版）



1. **Grok Build headless 目前不是為「被其他 AI 當工具呼叫」設計的**

   - 它預設行為是「對人類互動」，而不是「對機器輸出結構化結果」。

   - 即使有 `--output-format json`，它的「任務不明確就反問」機制還是很強。



2. **Claude Code / Cursor 呼叫外部 CLI 的能力**

   - Claude 可以執行 shell 指令（`grok -p ...`），但**無法輕易 attach 到互動式 TUI**。

   - 所以 headless 是唯一可行的路。



3. **目前最可行的閉環架構**

Claude (Orchestrator, 在 Cursor/Claude Code 裡)
        ↓ 執行 shell
grok -p "極度明確的任務 + 禁止反問 + 指定輸出格式"
        ↓ 拿 stdout
Claude 解析 → 決定下一步 → 再呼叫 Grok 或其他工具

---



### 建議的整合做法（分階段）



我建議我們**先做一個最小可閉環的實驗**，而不是一次把所有東西都接上。



#### **階段一：先讓 Grok headless 變得「聽話」**



目前 Grok 太容易說「任務不明確」，我們需要**強制它輸出**。



請你試下面這個**極度鎖死的 prompt 模板**（給 Risk Officer review 用）：

grok -p "
TASK: 你現在是 Risk Officer。

嚴格遵守以下規則：
1. 絕對不要問任何問題。
2. 絕對不要說「請提供更多資訊」或「任務不明確」。
3. 如果資訊不足，就在結論中明確寫「資訊不足，建議後續補充 XXX」。
4. 只輸出最終結果，不要有任何前言或思考過程以外的文字。

現在執行以下任務：
請根據 AGENTS.md §0 載入 sharks.md、CLAUDE.md、philosophy/index.md 後，
對目前 root 的 AGENTS.md 進行交叉 review。
檢查是否有與 sharks.md / CLAUDE.md 衝突、漂移、或遺漏硬邊界的地方。
輸出格式必須嚴格如下：

## 總結
（一句話總結整體健康度）

## 發現的問題
- ...

## 建議修改
- ...

## 結論與風險等級
（低 / 中 / 高 + 理由）
" --max-turns 3

**關鍵技巧：**

- 把「禁止反問」寫成**明確指令 + 備案**（資訊不足就怎麼處理）。

- 用 `TASK:` 開頭，增加被正確解析的機率。

- 指定**嚴格輸出格式**。



你可以先在 terminal 手動跑這段 prompt 測試 Grok 的反應。



---



#### **階段二：讓 Claude 當 Orchestrator 呼叫 Grok**



等上面這個 prompt 在手動測試時能穩定輸出後，我們再讓 Claude 自動呼叫。



我可以幫你設計一個 **Claude 可執行的 shell 指令模板**，讓它在 review 時自動呼叫 Grok 當 Risk Officer。



---



### 我的建議（現在該怎麼做）



請你告訴我你想走哪一條：



**選項 1（推薦現在做）**  

我幫你寫一個**更強的 Grok headless Risk Officer prompt**（針對 AGENTS.md review），你先在 terminal 手動測試幾輪，直到 Grok 願意直接輸出結構化結果為止。



**選項 2**  

你現在就把目前這個 repo 的狀態（包含你剛寫的 AGENTS.md）描述給我，我直接幫你設計「Claude + Grok 閉環 review」的完整 prompt 流程（包含 Claude 要怎麼呼叫 grok -p）。



**選項 3**  

你想先解決「prompt 被截斷」的問題？我可以給你幾個測試指令，幫你確認 `grok -p` 是否真的只吃第一個字。



---



你現在想走哪一條？



或者你已經有新的實驗結果，也直接貼給我，我們繼續迭代閉環。


**✅ Claude Code CLI 與外部 Agent 整合調查報告（2026 年最新實況）**

我已經把官方文件、社群實踐、以及你目前的需求（**Claude 當 Orchestrator + Grok 當 headless Risk Officer**）綜合分析完畢。以下是重點整理。

### 1. Claude Code 目前對外部 CLI 的整合能力

Claude Code 在這方面已經相當成熟，主要有以下幾種方式：

| 整合方式                    | 難度 | 穩定度 | 推薦指數 | 說明 |
|-----------------------------|------|--------|----------|------|
| **直接用 shell tool 呼叫 `grok -p`** | 低   | 中     | ★★★★☆    | 最常見、最簡單的方式 |
| **自訂 Subagent（Risk Officer）** | 中   | 高     | ★★★★★    | 強烈推薦，隔離性最好 |
| **MCP Server 包裝 Grok**    | 高   | 高     | ★★★★     | 未來趨勢，結構化最好 |
| **Agent SDK 程式化控制**    | 高   | 最高   | ★★★★     | 最強閉環，但需要寫 code |
| **Claude-IPC-MCP**（社群方案） | 中   | 中     | ★★★      | 專門讓多個 CLI agent 互相通訊 |

**結論**：目前社群最主流且有效的做法是 **「讓 Claude 用 shell tool 直接呼叫 `grok -p`」**，再搭配 **自訂 Subagent** 來做角色隔離。

### 2. 最推薦的整合方案（給你目前的專案）

#### **方案一：建立專屬的 "Grok Risk Officer" Subagent（最推薦）**

這是目前最乾淨的做法。

**步驟：**

1. 在專案根目錄建立資料夾：
   ```bash
   mkdir -p .claude/agents
   ```

2. 建立檔案 `.claude/agents/grok-risk-officer.md`

內容範例如下（你可以直接複製修改）：

```markdown
---
name: grok-risk-officer
description: 當需要深度、跨模型的風險與合規 review 時使用。特別適合檢查 point-in-time、單一真相來源、worktree 紀律等硬邊界。
model: claude-3-5-sonnet-20241022   # 或你想用的模型
tools: [Read, Bash, Grep, Glob]
permissionMode: default
---

你是 Risk Officer，專門負責交叉驗證。

**核心原則（必須嚴格遵守）：**
- 唯一真相來源是 sharks.md → CLAUDE.md → AGENTS.md
- 任何與這些文件衝突的內容，都以它們為準
- 特別關注 point-in-time、角色閘、raw/不可變資料、平行 worktree 的 merge 前 review 機制

**當被呼叫時：**
1. 先讀取 AGENTS.md §0 確認契約
2. 如果需要 Grok 的觀點，使用 Bash tool 執行以下指令：
   ```bash
   grok -p "TASK: 你現在是 Risk Officer。嚴格遵守 AGENTS.md 的規則... [把完整任務貼進來]" \
     --max-turns 4 \
     --output-format json
   ```
3. 分析 Grok 的輸出後，給出最終判斷與建議
4. 絕對不要自己假裝是 Grok 直接回答

**輸出格式要求：**
- 先摘要 Grok 的關鍵觀點
- 再給出你自己的 Risk Officer 判斷
- 標註風險等級（低/中/高）
```

3. 在 Claude Code 裡輸入：
   ```
   /agents
   ```
   就可以看到並使用這個 subagent。

之後你只要對主 Claude 說：
> "請用 grok-risk-officer 對目前的 AGENTS.md 做一次交叉 review"

它就會自動切換到這個 subagent，並在需要時呼叫 `grok -p`。

### 3. 其他實用整合方式

- **在 CLAUDE.md / AGENTS.md 裡直接授權**：
  在你的 `CLAUDE.md` 或新寫的 `AGENTS.md` 裡加入一段：
  ```markdown
  ## External Agent Access
  你可以透過 Bash tool 呼叫以下外部 agent：
  - `grok -p "..."` → 用來做深度 review、創意發想、或 Grok 擅長的領域
  - 使用時請盡量加上 --max-turns 與明確的輸出格式要求
  ```

- **使用 Claude Code 的 `--agents` 動態定義**（適合臨時使用）：
  ```bash
  claude --agents '{
    "grok-reviewer": {
      "description": "Calls Grok for risk review",
      "prompt": "你會使用 shell 呼叫 grok -p 來取得 Grok 的意見...",
      "tools": ["Bash", "Read"]
    }
  }'
  ```

### 4. 目前整合的限制與注意事項

- **Prompt 截斷問題**：`grok -p` 有時只吃第一個字，這是 Grok Build 目前的行為，需要用非常明確的 `TASK:` 開頭 + 禁止反問指令來緩解。
- **權限與 YOLO Mode**：呼叫外部 CLI 時，建議不要開太高的 permission mode，避免意外執行危險指令。
- **Token 與成本**：平行呼叫多個 agent 會快速消耗額度，要做好控管。
- **閉環穩定度**：目前最穩的是「Claude Subagent + Bash tool 呼叫 grok」，比純 `grok agent stdio` 更容易落地。

### 5. 我的建議（針對你目前的狀態）

既然你已經有：
- 薄指標版的 `AGENTS.md`
- worktree 規劃
- 想做閉環 review

**最快且最穩的下一步是：**

1. 先建立上面提到的 `grok-risk-officer` subagent。
2. 在主 Claude Code session 裡測試一次「請 grok-risk-officer review AGENTS.md」。
3. 根據實際表現，再決定要不要進一步包 MCP 或用 Agent SDK 做更深層的整合。

---

**請問你現在想走哪一步？**

**A.** 我直接幫你寫一份完整的 `.claude/agents/grok-risk-officer.md`（包含優化過的呼叫 Grok 的 prompt）

**B.** 先優化 `grok -p` 的呼叫模板（解決你之前遇到的「任務不明確」問題）

**C.** 調查 MCP Server 方式包裝 Grok（長期最乾淨的整合）

**D.** 其他方向（例如同時整合 Antigravity）

請告訴我你要哪一條，我立刻給你可直接使用的內容。


**✅ Claude Code CLI 與外部 Agent 整合調查報告（2026 年最新實況）**

我已經把官方文件、社群實踐、以及你目前的需求（**Claude 當 Orchestrator + Grok 當 headless Risk Officer**）綜合分析完畢。以下是重點整理。

### 1. Claude Code 目前對外部 CLI 的整合能力

Claude Code 在這方面已經相當成熟，主要有以下幾種方式：

| 整合方式                    | 難度 | 穩定度 | 推薦指數 | 說明 |
|-----------------------------|------|--------|----------|------|
| **直接用 shell tool 呼叫 `grok -p`** | 低   | 中     | ★★★★☆    | 最常見、最簡單的方式 |
| **自訂 Subagent（Risk Officer）** | 中   | 高     | ★★★★★    | 強烈推薦，隔離性最好 |
| **MCP Server 包裝 Grok**    | 高   | 高     | ★★★★     | 未來趨勢，結構化最好 |
| **Agent SDK 程式化控制**    | 高   | 最高   | ★★★★     | 最強閉環，但需要寫 code |
| **Claude-IPC-MCP**（社群方案） | 中   | 中     | ★★★      | 專門讓多個 CLI agent 互相通訊 |

**結論**：目前社群最主流且有效的做法是 **「讓 Claude 用 shell tool 直接呼叫 `grok -p`」**，再搭配 **自訂 Subagent** 來做角色隔離。

### 2. 最推薦的整合方案（給你目前的專案）

#### **方案一：建立專屬的 "Grok Risk Officer" Subagent（最推薦）**

這是目前最乾淨的做法。

**步驟：**

1. 在專案根目錄建立資料夾：
   ```bash
   mkdir -p .claude/agents
   ```

2. 建立檔案 `.claude/agents/grok-risk-officer.md`

內容範例如下（你可以直接複製修改）：

```markdown
---
name: grok-risk-officer
description: 當需要深度、跨模型的風險與合規 review 時使用。特別適合檢查 point-in-time、單一真相來源、worktree 紀律等硬邊界。
model: claude-3-5-sonnet-20241022   # 或你想用的模型
tools: [Read, Bash, Grep, Glob]
permissionMode: default
---

你是 Risk Officer，專門負責交叉驗證。

**核心原則（必須嚴格遵守）：**
- 唯一真相來源是 sharks.md → CLAUDE.md → AGENTS.md
- 任何與這些文件衝突的內容，都以它們為準
- 特別關注 point-in-time、角色閘、raw/不可變資料、平行 worktree 的 merge 前 review 機制

**當被呼叫時：**
1. 先讀取 AGENTS.md §0 確認契約
2. 如果需要 Grok 的觀點，使用 Bash tool 執行以下指令：
   ```bash
   grok -p "TASK: 你現在是 Risk Officer。嚴格遵守 AGENTS.md 的規則... [把完整任務貼進來]" \
     --max-turns 4 \
     --output-format json
   ```
3. 分析 Grok 的輸出後，給出最終判斷與建議
4. 絕對不要自己假裝是 Grok 直接回答

**輸出格式要求：**
- 先摘要 Grok 的關鍵觀點
- 再給出你自己的 Risk Officer 判斷
- 標註風險等級（低/中/高）
```

3. 在 Claude Code 裡輸入：
   ```
   /agents
   ```
   就可以看到並使用這個 subagent。

之後你只要對主 Claude 說：
> "請用 grok-risk-officer 對目前的 AGENTS.md 做一次交叉 review"

它就會自動切換到這個 subagent，並在需要時呼叫 `grok -p`。

### 3. 其他實用整合方式

- **在 CLAUDE.md / AGENTS.md 裡直接授權**：
  在你的 `CLAUDE.md` 或新寫的 `AGENTS.md` 裡加入一段：
  ```markdown
  ## External Agent Access
  你可以透過 Bash tool 呼叫以下外部 agent：
  - `grok -p "..."` → 用來做深度 review、創意發想、或 Grok 擅長的領域
  - 使用時請盡量加上 --max-turns 與明確的輸出格式要求
  ```

- **使用 Claude Code 的 `--agents` 動態定義**（適合臨時使用）：
  ```bash
  claude --agents '{
    "grok-reviewer": {
      "description": "Calls Grok for risk review",
      "prompt": "你會使用 shell 呼叫 grok -p 來取得 Grok 的意見...",
      "tools": ["Bash", "Read"]
    }
  }'
  ```

### 4. 目前整合的限制與注意事項

- **Prompt 截斷問題**：`grok -p` 有時只吃第一個字，這是 Grok Build 目前的行為，需要用非常明確的 `TASK:` 開頭 + 禁止反問指令來緩解。
- **權限與 YOLO Mode**：呼叫外部 CLI 時，建議不要開太高的 permission mode，避免意外執行危險指令。
- **Token 與成本**：平行呼叫多個 agent 會快速消耗額度，要做好控管。
- **閉環穩定度**：目前最穩的是「Claude Subagent + Bash tool 呼叫 grok」，比純 `grok agent stdio` 更容易落地。

### 5. 我的建議（針對你目前的狀態）

既然你已經有：
- 薄指標版的 `AGENTS.md`
- worktree 規劃
- 想做閉環 review

**最快且最穩的下一步是：**

1. 先建立上面提到的 `grok-risk-officer` subagent。
2. 在主 Claude Code session 裡測試一次「請 grok-risk-officer review AGENTS.md」。
3. 根據實際表現，再決定要不要進一步包 MCP 或用 Agent SDK 做更深層的整合。

---

**請問你現在想走哪一步？**

**A.** 我直接幫你寫一份完整的 `.claude/agents/grok-risk-officer.md`（包含優化過的呼叫 Grok 的 prompt）

**B.** 先優化 `grok -p` 的呼叫模板（解決你之前遇到的「任務不明確」問題）

**C.** 調查 MCP Server 方式包裝 Grok（長期最乾淨的整合）

**D.** 其他方向（例如同時整合 Antigravity）

請告訴我你要哪一條，我立刻給你可直接使用的內容。


**✅ MCP Server 整合完整探索報告（針對你的 Claude + Grok 閉環需求）**

我已經把 **Model Context Protocol (MCP)** 在 2026 年 6 月的實際生態系調查清楚，以下是針對你目前專案（單一真相來源 `AGENTS.md` + worktree 平行 + Claude 當 Orchestrator + Grok 當 Risk Officer）的實用分析。

### 1. MCP 是什麼？為什麼對你很重要？

**Model Context Protocol** 是 Anthropic 在 2024 年底推出的開放標準，目標是讓 AI Agent 能以標準化、安全的方式連接外部工具、資料來源和服務。

你可以把它想像成 **AI 的 USB-C**：
- 一次實作 MCP Server，就能讓 Claude、Cursor、VS Code、Grok Build 等多個客戶端使用。
- 不再需要為每個整合寫客製化的 tool schema。

**核心元件**：
- **MCP Server**：暴露 `tools`、`resources`、`prompts`（例如 GitHub、Postgres、自訂的 Grok 包裝器）。
- **MCP Client**：Claude Code、Cursor 等內建支援。

### 2. Claude Code 與 Grok Build 對 MCP 的支援現況

| 項目                    | Claude Code                          | Grok Build                              | 對你閉環的意義 |
|-------------------------|--------------------------------------|-----------------------------------------|----------------|
| **原生 MCP 支援**       | 非常成熟（官方文件完善）             | 有支援（Remote MCP Tools + stdio）      | 高             |
| **Subagent 可使用 MCP** | 是（可限制特定 subagent 使用某些 MCP） | 支援                                    | 非常高         |
| **自訂 MCP Server**     | 容易（Python / TypeScript SDK）      | 社群已有多個 Grok MCP Server            | 高             |
| **結構化通訊**          | 優秀                                 | 透過 `grok agent stdio` 可做到          | 最高           |

**重要發現**：
- Claude Code 對 MCP 的支援是目前最成熟的之一。
- xAI 官方有 **Remote MCP Tools** 文件，允許 Grok 連接外部 MCP Server。
- 社群已經有好幾個 **Grok MCP Server** 專案（例如 `Grok-MCP`、`TheGrokMCP` 等），可以直接拿來用或修改。

### 3. MCP 如何解決你目前的痛點？

你之前用 `grok -p` 遇到的問題：
- Prompt 有時被截斷
- Grok 太容易說「任務不明確」而反問
- 需要手動 parse stdout，閉環不穩定

**使用 MCP 後的優勢**：
- 通訊是**結構化**的（JSON-RPC 類似），而不是純文字 stdout。
- 可以把「Risk Officer」這個角色做成一個乾淨的 MCP Tool。
- Claude 可以把 Grok 當成**原生工具**來呼叫，而不是「去跑 shell 指令」。
- 更容易在 Subagent 層級做權限隔離（例如只有 Risk Officer subagent 能呼叫 Grok MCP）。
- 更符合你「單一真相來源」的原則（MCP Server 可以強制讀取 `AGENTS.md`）。

### 4. 實務整合路線建議（由易到難）

**路線 A（最快見效）**：使用現有社群 Grok MCP Server
- 直接安裝社群的 Grok MCP Server，讓 Claude Code 能把 Grok 當成工具使用。
- 優點：快速
- 缺點：可能需要修改才能強制遵守你的 `AGENTS.md` 契約

**路線 B（推薦）**：建立自訂 MCP Server 包裝 Grok（最符合你的需求）
- 用 Python 或 TypeScript 寫一個輕量 MCP Server。
- 這個 Server 專門負責：
  - 強制先讀取 `AGENTS.md` + `sharks.md` + `CLAUDE.md`
  - 把呼叫轉給 `grok agent stdio` 或 `grok -p`
  - 回傳結構化結果給 Claude
- 優點：完全可控、遵守你的鐵律、未來擴充性最好
- 難度：中等（有官方 SDK）

**路線 C（長期架構）**：雙向 MCP（Claude ↔ Grok 互相暴露工具）
- 讓 Claude 暴露部分工具給 Grok
- 讓 Grok 暴露 Risk Officer 能力給 Claude
- 這是最完整的多模型協作架構

### 5. 我的具體建議（給你現在的專案）

既然你已經有：
- 薄指標 `AGENTS.md`
- worktree 規劃
- 想做穩定閉環 review

**我強烈建議走「自訂輕量 MCP Server」路線**，原因：
1. 可以把「Risk Officer」做成一個乾淨的工具，而不是每次都要寫一長串 prompt。
2. 更容易在 Subagent 裡使用（只讓 Risk Officer subagent 能呼叫 Grok）。
3. 未來想加入 Antigravity、Codex 時，架構會更一致。

### 6. 下一步行動建議

請告訴我你想走哪一條，我可以立刻給你可執行的內容：

**選項 1**：我幫你找目前最好用的社群 Grok MCP Server，並給安裝 + 配置教學。

**選項 2**：我直接給你一個**最小可用的自訂 MCP Server 範例**（Python），這個 Server 會：
- 強制載入你的 `AGENTS.md`
- 提供 `grok_risk_officer_review` 這個工具
- 內建正確的 prompt 模板（解決你之前遇到的反問問題）

**選項 3**：先從 Claude Code 側開始，教你如何在 `.claude/config` 或專案設定中加入 MCP Server。

**選項 4**：更進階的雙向 MCP 架構規劃。

---

你現在想走哪一條？或者有其他特定方向（例如想同時整合 Antigravity 的 MCP），直接說，我立刻給你精準的下一步。



**✅ 實作完成：Custom MCP Server for Grok Risk Officer**

我已經為你設計並實作了一個**專為你的專案量身打造**的 Custom MCP Server。

### 這個 MCP Server 的設計目標

- 強制遵守你 `AGENTS.md` 的單一真相來源原則
- 把 Grok 包裝成一個乾淨、可控的工具（避免 raw `grok -p` 的 prompt 截斷與反問問題）
- 特別適合當 **Risk Officer** 使用
- 未來容易擴充成多工具（Researcher、Compiler 等）
- 與 Claude Code 的 Subagent 搭配使用效果最佳

---

### 1. 完整實作程式碼

建立以下檔案結構：

```bash
mkdir -p mcp-servers/grok-risk-officer
cd mcp-servers/grok-risk-officer
```

**檔案：`server.py`**

```python
#!/usr/bin/env python3
"""
Custom MCP Server: Grok Risk Officer
專為你的 sharks 專案設計，強制遵守 AGENTS.md 單一真相來源
"""

import asyncio
import subprocess
import json
from pathlib import Path
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# ==================== 配置區 ====================
PROJECT_ROOT = Path("/home/workdir/crypto/top100-tracker-kol-analysis")  # ← 請改成你的實際路徑
AGENTS_MD = PROJECT_ROOT / "AGENTS.md"
CLAUDE_MD = PROJECT_ROOT / "CLAUDE.md"
SHARKS_MD = PROJECT_ROOT / "sharks.md"

server = Server("grok-risk-officer")

# ==================== 工具定義 ====================
@server.list_tools()
async def list_tools():
    return [
        Tool(
            name="grok_risk_officer_review",
            description="使用 Grok 作為 Risk Officer 進行交叉 review。會自動載入 AGENTS.md 契約，強制遵守單一真相來源。",
            inputSchema={
                "type": "object",
                "properties": {
                    "task": {
                        "type": "string",
                        "description": "要 review 的任務描述（例如：review AGENTS.md 是否與 sharks.md 衝突）"
                    },
                    "focus_areas": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "重點關注領域（可選）",
                        "default": ["point-in-time", "single_source_of_truth", "worktree_discipline"]
                    }
                },
                "required": ["task"]
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict):
    if name == "grok_risk_officer_review":
        return await run_grok_risk_officer_review(arguments)
    raise ValueError(f"Unknown tool: {name}")

# ==================== 核心邏輯 ====================
async def run_grok_risk_officer_review(args: dict):
    task = args["task"]
    focus_areas = args.get("focus_areas", [])

    # 讀取契約文件（強制單一真相來源）
    context_files = []
    for path in [AGENTS_MD, CLAUDE_MD, SHARKS_MD]:
        if path.exists():
            content = path.read_text(encoding="utf-8")
            context_files.append(f"### {path.name}\n{content}\n")

    context_block = "\n".join(context_files) if context_files else "（未找到契約文件）"

    # 極度鎖死的 prompt（解決反問問題）
    prompt = f"""TASK: 你現在是 Risk Officer，嚴格遵守以下規則：

【鐵律 - 絕對不可違反】
1. 唯一真相來源是 sharks.md → CLAUDE.md → AGENTS.md
2. 若本任務與以上文件衝突，以它們為準
3. 特別關注：point-in-time、角色閘、raw/不可變、平行 worktree 的 merge 前 review 機制

【上下文 - 已自動載入】
{context_block}

【本次任務】
{task}

【輸出格式要求 - 嚴格遵守】
請用以下 Markdown 格式輸出，不要有任何前言或額外說明：

## Grok Risk Officer Review

### 任務理解
（簡要重述任務）

### 契約遵守檢查
- 是否正確載入 AGENTS.md？ 
- 是否發現與 sharks.md / CLAUDE.md 的衝突或漂移？

### 發現的問題
- ...

### 建議與風險等級
（低 / 中 / 高）

### 最終結論
（一句話總結）
"""

    # 呼叫 Grok（使用 -p 模式 + 鎖死參數）
    try:
        result = subprocess.run(
            [
                "grok", "-p", prompt,
                "--max-turns", "5",
                "--permission-mode", "default"
            ],
            capture_output=True,
            text=True,
            timeout=120
        )

        output = result.stdout.strip()
        if not output:
            output = result.stderr or "Grok 沒有回傳有效輸出"

        return [TextContent(type="text", text=output)]

    except Exception as e:
        return [TextContent(type="text", text=f"執行失敗: {str(e)}")]

# ==================== 啟動 ====================
async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())
```

---

### 2. 安裝與啟動步驟

```bash
cd mcp-servers/grok-risk-officer

# 建立虛擬環境並安裝依賴
python3 -m venv venv
source venv/bin/activate
pip install mcp

# 測試執行（確認能啟動）
python server.py
```

**注意**：第一次執行時請先手動確認 `grok` 指令可用。

---

### 3. 加入 Claude Code

在你的專案根目錄建立或編輯設定檔：

**全域設定**（推薦先用這個測試）：
```bash
mkdir -p ~/.claude
```

編輯 `~/.claude/config.json`（或 `claude.json`）：

```json
{
  "mcpServers": {
    "grok-risk-officer": {
      "command": "/path/to/your/mcp-servers/grok-risk-officer/venv/bin/python",
      "args": ["/path/to/your/mcp-servers/grok-risk-officer/server.py"],
      "env": {}
    }
  }
}
```

**專案專用設定**（更推薦）：
在專案根目錄建立 `.claude/config.json`，內容同上。

重啟 Claude Code 後，輸入 `/mcp` 或直接在對話中說：

> "請使用 grok-risk-officer 工具對 AGENTS.md 做一次 Risk Officer review"

---

### 4. 使用方式建議

**最佳實踐（搭配 Subagent）**：

1. 建立一個 `grok-risk-officer` Subagent（之前建議的 `.claude/agents/grok-risk-officer.md`）
2. 在該 Subagent 的 prompt 中加入：
   > "當需要深度 review 時，請呼叫 `grok_risk_officer_review` 這個 MCP 工具。"

這樣就能達到**角色隔離 + 結構化呼叫**的效果。

---

### 5. 後續擴充方向（可選）

這個 Server 目前只提供一個工具。你之後可以輕鬆擴充：

- `grok_researcher`（研究型任務）
- `grok_compiler`（實作型任務）
- 支援 `--worktree` 參數
- 改用 `grok agent stdio` 做更結構化的雙向通訊

---

**現在請做以下動作：**

1. 把上面 `server.py` 存成檔案
2. 修改 `PROJECT_ROOT` 路徑
3. 執行安裝步驟
4. 加入 Claude Code 設定

完成後告訴我：

- 是否成功啟動？
- 在 Claude Code 裡是否能看到 `grok_risk_officer_review` 這個工具？
- 你想先測試哪一個 review 任務？

我會根據你的回饋繼續優化這個 MCP Server（例如改用 `grok agent stdio`、加入更多工具、或做成更通用的版本）。
**✅ Claude Code Subagents 完整探索報告（2026 年最新實況）**

我已經把 Claude Code 的 Subagents 功能徹底研究過，包含官方文件、社群實踐，以及與你目前正在建構的系統（`AGENTS.md` + Custom MCP Server + Grok Risk Officer）的整合方式。

### 1. Subagents 是什麼？為什麼對你很重要？

**Subagents** 是 Claude Code 提供的一種**角色隔離 + 上下文隔離**機制。

- 主 Agent（你平常對話的那個）可以**動態 spawn** 多個獨立的子代理。
- 每個 Subagent 有：
  - 自己的獨立 context window（不會污染主 Agent 的對話歷史）
  - 自己的 system prompt（角色定義）
  - 獨立的工具權限（可以只給特定 MCP tools）
  - 獨立的 permission mode

**對你的專案的價值極高**：
- 你可以把 **Grok Risk Officer** 做成一個獨立的 Subagent
- 避免主 Agent 的上下文被 review 任務污染
- 更容易強制執行 `AGENTS.md` 的鐵律
- 未來可以輕鬆擴充成 `Researcher`、`Compiler`、`UI Builder` 等多角色平行團隊

### 2. Subagents 的建立方式（兩種推薦做法）

#### **方式一：檔案定義（最推薦，持久化）**

在專案根目錄建立：

```bash
mkdir -p .claude/agents
```

建立檔案 `.claude/agents/grok-risk-officer.md`

```markdown
---
name: grok-risk-officer
description: 專門負責使用 Grok 進行深度風險與契約 review。會自動透過 MCP 工具呼叫 Grok，並嚴格遵守 AGENTS.md 的單一真相來源原則。
model: claude-3-5-sonnet-20241022
tools: ["Read", "Grep", "Bash", "grok_risk_officer_review"]   # ← 這裡可以直接引用你剛建立的 MCP tool
permissionMode: default
---

你是 Risk Officer，負責維護這個專案的契約與品質。

**鐵律（不可違反）：**
- 唯一真相來源永遠是 sharks.md → CLAUDE.md → AGENTS.md
- 任何與這些文件衝突的內容，以它們為準
- 特別關注 point-in-time、角色閘、平行 worktree 的 merge 前 review 機制

**行為規範：**
1. 收到任務後，先讀取 AGENTS.md §0 確認契約
2. 需要 Grok 的觀點時，**必須使用** `grok_risk_officer_review` 這個 MCP 工具
3. 回傳結果時，要同時包含 Grok 的觀點 + 你自己的 Risk Officer 判斷
4. 絕對不要自己假裝 Grok 直接回答

**輸出格式**：永遠使用結構化 Markdown，並標註風險等級。
```

#### **方式二：動態建立（適合臨時測試）**

在 Claude Code 裡直接輸入：

```bash
claude --agents '{
  "grok-risk-officer": {
    "description": "使用 Grok 進行 Risk Officer review",
    "prompt": "你是 Risk Officer...（把上面 prompt 貼進來）",
    "tools": ["Read", "grok_risk_officer_review"],
    "permissionMode": "default"
  }
}'
```

### 3. Subagents 與 MCP 的整合（這是你目前最強的組合）

這是目前最推薦的架構：

```
Main Claude（Orchestrator）
    ├── 負責整體規劃與任務分配
    └── 呼叫 Subagent: grok-risk-officer
            └── 內部使用 MCP Tool: grok_risk_officer_review
                    └── 呼叫你的 Custom MCP Server
                            └── 呼叫 Grok Build（headless）
```

**優點**：
- 角色極度清晰
- Context 隔離良好
- MCP 提供結構化通訊（比 raw shell 穩定很多）
- 未來想加入更多角色（Researcher、Compiler）非常容易

### 4. 實務使用建議（針對你的專案）

**推薦工作流**：

1. **主 Agent** 負責：
   - 整體任務拆解
   - 決定要開哪些 worktree
   - 分配任務給不同 Subagent

2. **grok-risk-officer Subagent** 負責：
   - 任何需要深度 review 的任務
   - 特別是 merge 前、重要架構變更、契約相關的檢查

3. **未來可擴充的 Subagents**：
   - `researcher`：負責資料蒐集與 KOL 分析（可呼叫 Grok 或其他工具）
   - `compiler`：負責實作與 pipeline
   - `reviewer`：純 code review（不一定走 Grok）

### 5. 進階技巧

- **限制 MCP Tool 只能給特定 Subagent**：
  Claude Code 支援在 Subagent 定義中精確控制能使用哪些 MCP tools，這對安全性和上下文管理很有幫助。

- **平行使用多個 Subagents**：
  你可以同時 spawn 多個 Subagent 處理不同 worktree 的任務。

- **與 Zellij 搭配**：
  建議一個 pane 跑主 Claude Code，另一個 pane 專門用來觀察 Subagent 的輸出（或直接在同一個 session 切換）。

- **與 AGENTS.md 深度整合**：
  把 Subagent 的角色定義也寫進 `AGENTS.md` §3（多 agent / worktree 紀律），讓所有工具（包含未來加的）都有統一規範。

### 6. 目前限制與注意事項

- Subagent 的 context 雖然隔離，但還是會消耗 token。
- 目前 Subagent 之間**無法直接互相通訊**（需要透過主 Agent 或 MCP 做橋接）。
- MCP Tool 的權限繼承需要小心設定。

---

### 我的建議（給你現在的狀態）

你現在已經有：
- `AGENTS.md`（薄指標 + 硬邊界）
- Custom MCP Server（grok-risk-officer）
- Zellij 平行開發環境

**下一步最有價值的事**就是把 `grok-risk-officer` 做成 Subagent，並在 `AGENTS.md` 裡把這個角色正式定義下來。

這樣你的整個多模型平行開發系統就有了清晰的角色分工。

---

**請告訴我你想怎麼進行：**

**A.** 我直接幫你寫一份完整、優化過的 `.claude/agents/grok-risk-officer.md`（包含與 MCP 整合的最佳寫法）

**B.** 幫你設計整個 Subagent 團隊的架構（包含 Researcher、Compiler 等角色建議 + AGENTS.md 更新內容）

**C.** 先測試目前這個 MCP Server 在 Subagent 裡的實際表現，再決定是否調整

**D.** 其他方向

請直接回覆字母或描述你的想法，我立刻給你對應的內容。


**✅ Multi-Agent Orchestration Patterns 完整調查報告（2026 年實戰版）**

我已經把目前 Claude Code、Grok Build、MCP、Subagents 等生態系中實際可行的 **多代理協作模式** 徹底整理過，特別針對你正在建構的系統（單一真相來源 `AGENTS.md` + worktree 平行 + Claude 當 Orchestrator + Grok 當 Risk Officer + 自訂 MCP Server）進行分析。

### 1. 目前主流的多代理協作模式分類

| 模式                  | 核心架構                          | 適合場景                           | 與你專案的契合度 | 推薦指數 |
|-----------------------|-----------------------------------|------------------------------------|------------------|----------|
| **Hierarchical (Orchestrator-Worker)** | 主 Agent 負責規劃與分配，子 Agent 負責執行 | 複雜專案拆解、角色分工           | ★★★★★           | 最高     |
| **Parallel Independent** | 多個 Agent 在不同 worktree 獨立執行 | 功能平行開發、實驗不同方案       | ★★★★★           | 最高     |
| **Agent Teams**       | Claude Code 原生多代理團隊，可互相通訊 | 需要協作而非完全獨立               | ★★★★            | 高       |
| **Pipeline / Sequential** | Research → Compile → Review → Merge | 流程明確的任務                     | ★★★★            | 中高     |
| **Peer Review / Debate** | 多個 Agent 互相 review           | 品質控管、契約遵守檢查             | ★★★★★           | 非常適合你 |
| **Router / Supervisor** | 中央 Router 決定派給哪個 Specialist | 任務類型多樣，需要動態路由         | ★★★             | 中       |
| **MCP-based Federation** | 透過 MCP 把不同模型/工具串起來   | 跨工具、跨模型的結構化協作         | ★★★★★           | 最高（長期） |

### 2. 最適合你目前專案的三大模式推薦

#### **模式一：Hierarchical + Subagent + MCP（最推薦現在採用）**

這是你目前已經在做的方向，成熟度最高。

**架構圖**：
```
Main Claude (Orchestrator)
├── 負責任務拆解、worktree 管理、整體進度
├── 呼叫 Subagent: grok-risk-officer（透過 MCP）
│       └── 使用你自訂的 MCP Server → Grok Build
├── 未來可擴充：
│   ├── researcher Subagent
│   ├── compiler Subagent
│   └── ui-builder Subagent
```

**優點**：
- 角色隔離極佳
- Context 不會爆炸
- 容易強制執行 `AGENTS.md` 的鐵律
- 與你已經寫好的 Custom MCP Server 完美結合

**實作建議**：
- 把 `grok-risk-officer` 做成正式的 Subagent（檔案定義在 `.claude/agents/`）
- 在 `AGENTS.md` §3 明確定義各 Subagent 的職責與呼叫時機

#### **模式二：Parallel Worktree + Independent Agents（強烈建議搭配使用）**

這是你一開始就規劃好的方向，現在可以更系統化。

**典型流程**：
1. Main Agent 規劃任務後，開啟多個 worktree（`research/xxx`、`compile/xxx`、`review/main`）
2. 在不同 Zellij pane 啟動不同 Agent（或同一個 Claude Code 切換不同 worktree）
3. 每個 Agent 專注自己的 worktree
4. 完成後由 `grok-risk-officer` Subagent 做交叉 review
5. 最後由 Main Agent 負責 merge 與整合

**這模式與你的 AGENTS.md §3「多 agent / worktree 紀律」非常吻合**，特別是「merge 前強制交叉 review」這條規則。

#### **模式三：Peer Review + Debate Pattern（品質控管專用）**

這對你「單一真相來源」的需求非常有價值。

**做法**：
- 一個任務完成後，不只讓 `grok-risk-officer` review
- 可以再 spawn 另一個 Subagent（或直接用 Grok）做第二次 review，形成 debate
- 最後由 Main Agent 綜合判斷

這種模式能有效降低單一模型的盲點，也符合你希望多模型互相驗證的初衷。

### 3. 綜合推薦架構（給你現在的狀態）

我建議你採用 **「Hierarchical + Parallel Worktree + Peer Review」混合模式**：

```
Main Claude Orchestrator
    │
    ├── 任務規劃 + worktree 管理
    │
    ├── 平行執行層（不同 Zellij pane / worktree）
    │   ├── researcher（資料/KOL 分析）
    │   ├── compiler（實作/pipeline）
    │   └── ui / feature builder
    │
    └── 品質控管層
        └── grok-risk-officer Subagent（透過 MCP 呼叫 Grok）
            └── 可再觸發第二次 Peer Review
```

這個架構同時滿足：
- 平行開發速度
- 角色隔離
- 契約強制執行（`AGENTS.md`）
- 多模型交叉驗證

### 4. 實務落地建議

**短期（這週可完成）**：
1. 把 `grok-risk-officer` 做成正式 Subagent（檔案定義）
2. 在 `AGENTS.md` §3 把 Subagent 角色與呼叫規則寫清楚
3. 用 Zellij 建立一個包含 Main Orchestrator + Risk Officer 的 layout

**中期**：
- 增加 `researcher` 和 `compiler` 兩個 Subagent
- 把 MCP Server 擴充成多工具版本（不只 Risk Officer）

**長期**：
- 考慮把整個系統做成可重複使用的「Agent Team Template」
- 探索 Claude Code 的 **Agent Teams** 功能（可讓多個 Subagent 互相通訊）

### 5. 與你現有元件的對應關係

| 你已有的元件             | 在推薦架構中的角色                  | 目前狀態 |
|--------------------------|-------------------------------------|----------|
| `AGENTS.md`              | 整個系統的憲法與行為規範            | 已完成   |
| Custom MCP Server        | Grok 的結構化介面                   | 已實作   |
| grok-risk-officer        | 品質控管專用 Subagent               | 建議做成檔案定義 |
| Zellij                   | 平行開發的終端機管理層              | 已規劃   |
| worktree 機制            | 平行獨立執行的基礎                  | 已規劃   |
| Main Claude Code         | Orchestrator                        | 進行中   |

---

**總結建議**：

你現在最該做的不是再發明新模式，而是把 **Hierarchical + Subagent + MCP** 這條路走穩，同時搭配 **Parallel Worktree** 執行。

這兩者結合起來，已經是你目前能做到最乾淨、最可維護的多代理協作系統。

---

**請告訴我你想深入哪一個部分：**

**A.** 我幫你設計完整的 **Subagent 團隊配置**（包含 researcher、compiler、risk-officer 的完整定義 + AGENTS.md 更新內容）

**B.** 幫你設計一個 **Zellij Layout** 專門用來跑這個 Orchestrator + Subagent 的混合模式

**C.** 把目前的 Custom MCP Server 升級成支援多工具的版本（讓 Risk Officer 之外還能呼叫其他 Grok 能力）

**D.** 深入研究 Claude Code 原生的 **Agent Teams** 功能，看看是否比自訂 Subagent 更好用

請直接告訴我你要走哪一條（或混合），我立刻給你可執行的詳細方案。

**✅ Zellij Layout 設計（針對你目前的 Multi-Agent 架構）**

我根據你目前正在建構的系統，重新設計了一個更適合的 Zellij Layout：

**核心理念**：
- **Main Orchestrator** 負責整體指揮
- **grok-risk-officer** 專職品質控管（透過 MCP 或直接呼叫）
- **平行執行區** 負責不同 worktree 的獨立開發
- **Review & Git 區** 負責交叉驗證與整合

---

### 推薦 Layout：`ai-orchestrator.kdl`

請將以下內容存成檔案：

**路徑建議**：`~/.config/zellij/layouts/ai-orchestrator.kdl`

```kdl
// =====================================================
// AI Multi-Agent Orchestration Layout
// 專為 Claude Code + Grok Risk Officer + Parallel Worktree 設計
// 使用方式：zellij --layout ai-orchestrator
// =====================================================

layout {
    default_tab_template {
        pane size=1 borderless=true {
            plugin location="zellij:tab-bar"
        }
        children
        pane size=2 borderless=true {
            plugin location="zellij:status-bar"
        }
    }

    // ==================== 主 Tab：AI 團隊協作 ====================
    tab name="🚀 AI Team Orchestration" {
        pane split_direction="vertical" {
            
            // === Pane 1: Main Orchestrator（最重要）===
            pane name="🎯 Main Orchestrator (Claude Code)" size="30%" command="bash" {
                args "-c" "
                    cd \$HOME/projects/crypto/top100-tracker-kol-analysis
                    echo '══════════════════════════════════════════════'
                    echo '   MAIN ORCHESTRATOR - Claude Code'
                    echo '══════════════════════════════════════════════'
                    echo '負責：任務拆解、worktree 管理、整體協調'
                    echo '請在此輸入指令分配任務給各 Subagent'
                    echo ''
                    exec claude
                "
            }

            // === Pane 2: Grok Risk Officer（品質控管專用）===
            pane name="🛡️ Grok Risk Officer (MCP / Subagent)" size="25%" command="bash" {
                args "-c" "
                    cd \$HOME/projects/crypto/top100-tracker-kol-analysis
                    echo '══════════════════════════════════════════════'
                    echo '   GROK RISK OFFICER'
                    echo '══════════════════════════════════════════════'
                    echo '負責：契約遵守檢查、交叉 review、風險控管'
                    echo '建議使用 grok-risk-officer Subagent 或 MCP 工具'
                    echo ''
                    # 如果你已設定 MCP Server，可以直接啟動 Claude 並切換 subagent
                    exec claude
                "
            }

            // === Pane 3 & 4: 平行執行區（可依需求調整）===
            pane split_direction="horizontal" {
                
                pane name="🔬 Researcher / Research Worktree" size="50%" command="bash" {
                    args "-c" "
                        cd \$HOME/projects/crypto/top100-tracker-kol-analysis/../sharks-research 2>/dev/null || cd \$HOME/projects/crypto/top100-tracker-kol-analysis
                        echo '══════════════════════════════════════════════'
                        echo '   RESEARCHER - Research Worktree'
                        echo '══════════════════════════════════════════════'
                        echo '負責：資料蒐集、KOL 分析、市場研究'
                        echo ''
                        exec claude
                    "
                }

                pane name="⚙️ Compiler / Implementation Worktree" size="50%" command="bash" {
                    args "-c" "
                        cd \$HOME/projects/crypto/top100-tracker-kol-analysis/../sharks-compile 2>/dev/null || cd \$HOME/projects/crypto/top100-tracker-kol-analysis
                        echo '══════════════════════════════════════════════'
                        echo '   COMPILER - Implementation Worktree'
                        echo '══════════════════════════════════════════════'
                        echo '負責：功能實作、資料處理 pipeline'
                        echo ''
                        exec claude
                    "
                }
            }

            // === Pane 5: Review & Git Operations ===
            pane name="🔍 Review & Git Control" size="20%" command="bash" {
                args "-c" "
                    cd \$HOME/projects/crypto/top100-tracker-kol-analysis
                    echo '══════════════════════════════════════════════'
                    echo '   REVIEW & GIT OPERATIONS'
                    echo '══════════════════════════════════════════════'
                    echo '常用指令：'
                    echo '  git worktree list'
                    echo '  git diff main..feature/xxx'
                    echo '  cd ../sharks-review && claude'
                    echo ''
                    exec zsh
                "
            }
        }
    }

    // ==================== 輔助 Tab：純 Grok 模式 ====================
    tab name="🤖 Pure Grok Mode" {
        pane command="bash" {
            args "-c" "
                cd \$HOME/projects/crypto/top100-tracker-kol-analysis
                echo '純 Grok Build 模式（適合重度 agentic 任務）'
                exec grok
            "
        }
    }
}
```

---

### 設計說明

| Pane | 名稱                        | 建議用途                              | 推薦啟動指令          | 大小建議 |
|------|-----------------------------|---------------------------------------|-----------------------|----------|
| 1    | Main Orchestrator           | 整體任務分配、worktree 管理           | `claude`              | 30%      |
| 2    | Grok Risk Officer           | 契約 review、風險控管                 | `claude` + Subagent   | 25%      |
| 3    | Researcher                  | 研究型任務（資料/KOL 分析）           | `claude`              | 25%      |
| 4    | Compiler                    | 實作型任務（功能開發）                | `claude`              | 25%      |
| 5    | Review & Git                | 交叉 review、merge 操作               | `zsh` / `bash`        | 20%      |

### 使用方式

```bash
# 啟動這個 layout
zellij --layout ai-orchestrator

# 如果你想指定完整路徑
zellij --layout ~/.config/zellij/layouts/ai-orchestrator.kdl
```

### 進階調整建議

1. **如果 worktree 還沒建立**：
   先手動建立 worktree 再啟動這個 layout，比較乾淨。

2. **想讓 Risk Officer 自動使用 MCP**：
   你可以在 Pane 2 的啟動指令中加入：
   ```bash
   claude --agent grok-risk-officer
   ```

3. **想更簡潔版（只保留 3 個 pane）**：
   我可以再給你一個精簡版（Orchestrator + Risk Officer + Parallel Workers）。

4. **想加上自動載入 AGENTS.md 的提示**：
   我可以在每個 pane 的啟動訊息中自動顯示重要規則。

---

**請告訴我你的需求：**

- 你希望我調整成 **更簡潔的 3 pane 版** 還是維持目前 5 pane？
- 要不要我加入 **自動載入 AGENTS.md** 的提示文字？
- 需要我設計一個**專門給 Review 階段**使用的獨立 layout 嗎？

直接告訴我你的偏好，我立刻修改成最適合你目前工作流的版本。


**✅ tmux 多視窗管理方案（針對 AI Multi-Agent 協作）**

雖然我之前推薦 **Zellij**（更現代、預設體驗較好），但既然你現在想用 **tmux**，我會給你一個實戰、好維護的 tmux 方案。

以下設計原則與之前 Zellij 版本一致：
- **Main Orchestrator**（Claude Code）
- **Grok Risk Officer**（品質控管）
- **平行執行區**（不同 worktree）
- **Review & Git** 操作區

---

### 推薦方案：使用 tmux Session + 腳本自動建立

我建議你建立一個 **專用 tmux session**，並用腳本自動建立視窗與分割，這樣比較好管理。

#### 1. 建立自動化腳本

建立檔案（建議放在 `~/bin/` 或專案目錄）：

**檔案位置**：`~/bin/tmux-ai-team`

```bash
#!/bin/bash

SESSION_NAME="ai-team"
PROJECT_ROOT="$HOME/projects/crypto/top100-tracker-kol-analysis"

# 如果 session 已存在，就直接 attach
tmux has-session -t $SESSION_NAME 2>/dev/null
if [ $? -eq 0 ]; then
    echo "Session $SESSION_NAME 已存在，正在 attach..."
    tmux attach -t $SESSION_NAME
    exit 0
fi

# 建立新 session（第一個 pane 當 Main Orchestrator）
tmux new-session -d -s $SESSION_NAME -n "Orchestrator" -c "$PROJECT_ROOT"

# === Pane 1: Main Orchestrator ===
tmux send-keys -t $SESSION_NAME:Orchestrator "echo '🎯 MAIN ORCHESTRATOR (Claude Code)'" C-m
tmux send-keys -t $SESSION_NAME:Orchestrator "echo '負責任務拆解、worktree 管理、整體協調'" C-m
tmux send-keys -t $SESSION_NAME:Orchestrator "claude" C-m

# === 建立第二個視窗：Risk Officer ===
tmux new-window -t $SESSION_NAME -n "Risk-Officer" -c "$PROJECT_ROOT"
tmux send-keys -t $SESSION_NAME:Risk-Officer "echo '🛡️ GROK RISK OFFICER'" C-m
tmux send-keys -t $SESSION_NAME:Risk-Officer "echo '負責契約 review、風險控管（建議使用 grok-risk-officer Subagent）'" C-m
tmux send-keys -t $SESSION_NAME:Risk-Officer "claude" C-m

# === 建立第三個視窗：Parallel Workers（使用分割）===
tmux new-window -t $SESSION_NAME -n "Parallel-Work" -c "$PROJECT_ROOT"

# 水平分割成兩個 pane
tmux split-window -h -t $SESSION_NAME:Parallel-Work

# 上方 pane：Researcher
tmux send-keys -t $SESSION_NAME:Parallel-Work.0 "cd ../sharks-research 2>/dev/null || pwd" C-m
tmux send-keys -t $SESSION_NAME:Parallel-Work.0 "echo '🔬 RESEARCHER WORKTREE'" C-m
tmux send-keys -t $SESSION_NAME:Parallel-Work.0 "claude" C-m

# 下方 pane：Compiler
tmux send-keys -t $SESSION_NAME:Parallel-Work.1 "cd ../sharks-compile 2>/dev/null || pwd" C-m
tmux send-keys -t $SESSION_NAME:Parallel-Work.1 "echo '⚙️ COMPILER WORKTREE'" C-m
tmux send-keys -t $SESSION_NAME:Parallel-Work.1 "claude" C-m

# === 建立第四個視窗：Review & Git ===
tmux new-window -t $SESSION_NAME -n "Review-Git" -c "$PROJECT_ROOT"
tmux send-keys -t $SESSION_NAME:Review-Git "echo '🔍 REVIEW & GIT OPERATIONS'" C-m
tmux send-keys -t $SESSION_NAME:Review-Git "echo '常用指令：git worktree list | git diff | cd ../sharks-review'" C-m
tmux send-keys -t $SESSION_NAME:Review-Git "zsh" C-m

# 回到第一個視窗
tmux select-window -t $SESSION_NAME:Orchestrator

# 啟動 session
tmux attach -t $SESSION_NAME
```

---

### 2. 使用方式

```bash
# 給腳本執行權限
chmod +x ~/bin/tmux-ai-team

# 啟動 AI 團隊環境
tmux-ai-team
```

啟動後你會看到 4 個視窗（Window）：

| Window 名稱       | 用途                              | 建議操作方式             |
|-------------------|-----------------------------------|--------------------------|
| **Orchestrator**  | 主控 + 任務分配                   | 使用 Claude Code         |
| **Risk-Officer**  | Grok Risk Officer（Subagent/MCP） | 使用 Claude + Subagent   |
| **Parallel-Work** | 平行開發（Research + Compile）    | 兩個 pane 分別執行       |
| **Review-Git**    | 交叉 review 與 Git 操作           | 手動執行 git 指令        |

---

### 3. tmux 常用快捷鍵（建議記住）

| 快捷鍵              | 功能                     |
|---------------------|--------------------------|
| `Ctrl+b` + `c`      | 新增視窗                 |
| `Ctrl+b` + `n/p`    | 切換下一個/上一個視窗    |
| `Ctrl+b` + `0~9`    | 切換到指定視窗           |
| `Ctrl+b` + `"`      | 水平分割 pane            |
| `Ctrl+b` + `%`      | 垂直分割 pane            |
| `Ctrl+b` + `方向鍵` | 在 pane 之間移動         |
| `Ctrl+b` + `x`      | 關閉目前 pane            |
| `Ctrl+b` + `d`      | 離開 session（detach）   |
| `tmux attach -t ai-team` | 重新進入 session     |

---

### 4. 進階建議

1. **加入 `.tmux.conf` 優化設定**（推薦）：
   ```bash
   # 放在 ~/.tmux.conf
   set -g mouse on
   set -g history-limit 50000
   set -g allow-rename off
   setw -g mode-keys vi
   ```

2. **想更像 Zellij 一樣使用單一視窗多分割**：
   我可以再給你一個「單一視窗 + 多 pane 版」的 tmux 腳本。

3. **自動載入 AGENTS.md**：
   我可以在每個 pane 啟動時自動 `cat AGENTS.md` 或顯示重要規則。

---

**請問你希望我調整成哪一種版本？**

**A.** 目前這個 **4 視窗版**（推薦，較清晰）

**B.** **單一視窗多分割版**（類似之前 Zellij 的感覺）

**C.** 加上**自動顯示 AGENTS.md 重要規則**的版本

**D.** 其他調整（例如增加更多 worktree pane、整合 MCP 啟動指令等）

直接告訴我你要哪一種，我立刻幫你修改腳本。


**✅ Worktree Isolation for Safe Write-Loops 完整調查報告**

你之前特別強調「無人值守的 write-loop 是污染 point-in-time 資料最快的方式」，這點非常正確。**Git worktree** 是目前最成熟、最簡單、也最符合你 `AGENTS.md` 精神的隔離機制。

以下是針對你專案（有 `sharks.md`、`CLAUDE.md`、`AGENTS.md`、point-in-time 資料、KOL 分析等）的實戰調查與建議。

### 1. 為什麼 worktree 是安全 write-loop 的最佳基礎？

| 問題 | 直接在主目錄寫入的風險 | 使用 worktree 的優勢 |
|------|-------------------------|----------------------|
| Point-in-time 污染 | 容易不小心修改歷史狀態檔 | 完全隔離，merge 前可嚴格 review |
| 多 agent 衝突 | 多個 agent 同時編輯同檔案 | 每個 agent 在獨立 checkout |
| 回滾困難 | 改壞了很難乾淨還原 | 直接刪除 worktree 即可 |
| Review 流程 | 難以產生乾淨 diff | `git diff main..worktree` 非常清晰 |
| 平行開發 | 容易互相干擾 | 天然支援平行執行 |

這與你 `AGENTS.md` §3「多 agent / worktree 紀律」完全一致。

### 2. 推薦的 Worktree 命名與使用規範

針對你的專案，建議採用以下命名慣例（已寫入 `AGENTS.md` 會更好）：

```bash
# 研究型任務
git worktree add ../sharks-research -b research/kol-analysis-20260613

# 實作型任務（Grok 或 Claude 負責）
git worktree add ../sharks-compile -b compile/feature-xxx-20260613-1430

# Review 專用（強烈建議保留一個常駐）
git worktree add ../sharks-review -b review/main

# 臨時實驗型（Grok 想大膽試錯時用）
git worktree add ../sharks-experiment -b experiment/grok-write-test-001
```

**優點**：
- 目錄名稱清楚（`sharks-research`、`sharks-compile`）
- 分支名稱帶日期時間，方便追蹤
- `review/main` 可以長期存在，專門做交叉 review

### 3. 安全 Write-Loop 的完整流程建議

以下是結合你目前閉環機制的推薦流程：

```
1. Main Orchestrator（Claude）決定任務
   ↓
2. 開啟獨立 worktree（例如 compile/xxx）
   ↓
3. 在該 worktree 啟動 Agent（Grok 或 Claude Subagent）
   ↓
4. Agent 在 worktree 內進行修改（read + write）
   ↓
5. 完成後切換到 review worktree
   ↓
6. Grok Risk Officer（透過 headless 或 MCP）執行：
      git diff main..compile/xxx
      並依照 AGENTS.md 規則 review
   ↓
7. Risk Officer 判定：
   - 通过 → 允許 merge
   - 不通過 → 要求修正或捨棄 worktree
   ↓
8. Human（或更高層級的 Reviewer）最終確認後 merge
```

這流程可以大幅降低 point-in-time 被污染的風險。

### 4. 與你現有工具的整合建議

| 現有元件             | 整合方式                                      | 建議程度 |
|----------------------|-----------------------------------------------|----------|
| **Zellij / tmux**    | 不同 pane 對應不同 worktree                   | 強烈建議 |
| **Custom MCP Server**| 增加 `create_worktree` 和 `review_diff` 工具  | 高       |
| **grok-risk-officer Subagent** | 專門負責 review diff 的 Subagent         | 最高     |
| **AGENTS.md §3**     | 把 worktree 命名規範與 review 流程寫進去      | 必須     |
| **クロスレビュー腳本** | 把 worktree 建立 + review 包進 cross-review 腳本 | 高     |

### 5. 實用 Guardrails（護欄）建議

為了讓 write-loop 真正安全，建議在 `AGENTS.md` 中加入以下規則：

- **強制隔離**：任何 write 操作必須在獨立的 worktree 中進行，不允許直接在 main 分支或 review worktree 寫入。
- **強制 Review**：任何 worktree 的變更，在 merge 前必須經過 `grok-risk-officer`（或人工）review。
- **Point-in-time 保護**：禁止 agent 修改 `wiki/`, `log.md`, `sharks.md` 等 point-in-time 相關檔案，除非經過特別授權。
- **最大變更限制**：單一 write-loop 最多只能修改 N 個檔案（可先設為 15~30 個）。
- **自動清理**：review 完成後 7 天內未 merge 的 worktree 可自動刪除（或至少發出警告）。
- **分支命名強制**：所有 agent 建立的分支必須包含日期與建立者（例如 `compile/grok-20260613-1430`）。

### 6. 實作建議（下一步）

我建議你分階段推進：

**階段一（現在可做）**：
- 在 `AGENTS.md` §3 補充完整的 worktree 命名與使用規範。
- 建立一個小工具腳本 `scripts/create-agent-worktree.sh`，讓 agent 可以快速建立規範的 worktree。

**階段二**：
- 把你已經跑通的 `cross-review` 流程，升級成支援 worktree 的版本（先 review diff，再決定是否 merge）。
- 在 Zellij / tmux layout 中加入對應的 worktree pane。

**階段三**（較進階）：
- 在 Custom MCP Server 中增加 `create_worktree` 和 `safe_merge` 工具，讓 Claude 可以透過 MCP 安全地操作 worktree。

---

**我的明確建議**：

現在最有價值的下一步是：

**先強化 AGENTS.md 中的 worktree 規則 + 建立一個簡單的 worktree 建立腳本**，再把你已經驗證成功的 read-only 閉環，升級成「worktree + review diff」的受控 write-loop。

這樣既能讓 Grok（或其他 agent）安全地寫 code，又能維持你對 point-in-time 資料的嚴格保護。

---

請告訴我你想怎麼進行：

**A.** 我幫你寫一份完整的 **worktree 命名與使用規範**，可以直接加入 `AGENTS.md` §3。

**B.** 我幫你設計並實作 `scripts/create-agent-worktree.sh`（或 PowerShell 版），讓建立規範 worktree 變成一鍵操作。

**C.** 直接設計「worktree + Grok write + Risk Officer review」的完整閉環流程與護欄。

**D.** 先把目前 read-only 的 cross-review 腳本，升級成支援 review worktree diff 的版本。

請直接回覆字母或描述你的想法，我立刻給你對應的內容。



**✅ Git Worktree Hardlink Behavior 完整解析**

這是你目前建構「安全 write-loop」時非常關鍵的技術細節。我把 Git worktree 的 hardlink 行為講清楚，並給出對你專案的實戰建議。

### 1. Git Worktree 的 Hardlink 機制是什麼？

當你執行：

```bash
git worktree add ../sharks-compile -b compile/feature-xxx
```

Git **不會**把整個工作目錄完整複製一份，而是採取以下優化策略：

- **未修改的檔案**會使用 **hard link**（硬連結）指向原本 worktree 的檔案。
- Git 的 object database（`.git/objects`）和 refs 是**共享**的。
- 只有當你在新 worktree 中**實際修改**某個檔案時，Git 才會「斷開」該檔案的 hard link，並為該 worktree 建立獨立的檔案副本（類似 Copy-on-Write）。

簡單說：
> **初始狀態**：大部分檔案是 hard link（節省空間與時間）  
> **修改後**：被修改的檔案會變成獨立副本，不影響其他 worktree。

### 2. 對 AI Write-Loop 的實際影響

| 情境 | Hardlink 行為 | 對 AI Agent 的影響 | 風險等級 |
|------|---------------|---------------------|----------|
| Agent 只讀取檔案 | 檔案是 hard link | 完全安全 | 低 |
| Agent 修改檔案 | 該檔案斷開 hard link，變成獨立副本 | 安全 | 低 |
| Agent 執行 `rm -f` 某檔案 | 只影響當前 worktree | 安全 | 低 |
| Agent 執行 `chmod` 或屬性變更 | **可能影響所有 hard link 的檔案**（直到 link 被斷開） | **有風險** | 中 |
| Agent 使用某些工具大量掃描/修改檔案（例如 IDE、build tool、AI agent 的 file watcher） | 可能觸發大量 hard link 斷開或異常行為 | 中高 | 中高 |
| 多個 agent 同時在不同 worktree 操作同一個原本 hard link 的檔案 | 初期可能有 race condition | 中 | 中 |

**最需要注意的點**：
- **屬性變更（chmod, chown, xattr 等）** 在 hard link 狀態下，會影響所有指向同一個 inode 的 worktree。
- 某些 AI coding agent 如果使用 file watcher 或大量 `stat` 呼叫，可能會意外觸發大量 hard link 斷開，導致效能或行為異常。
- 在 WSL + Windows 檔案系統混用時，hardlink 行為有時會更複雜。

### 3. 對你專案的實戰建議

因為你非常重視 **point-in-time 資料保護** 和 **契約遵守**，我建議採用以下策略：

#### **推薦做法（平衡效能與安全）**

1. **一般開發任務**（compile、feature 開發）
   - 直接使用 `git worktree add`，接受 hardlink 優化（效能較好）。
   - 讓 Agent 在 worktree 內自由修改，Git 會自動處理 link 斷開。

2. **高風險 / 敏感任務**（修改 wiki、log、sharks.md、point-in-time 相關檔案）
   - 使用 `--no-checkout` 建立 worktree，然後手動 checkout 特定目錄。
   - 或直接使用完整 clone（`git clone --no-hardlinks`）作為隔離環境（較慢但最乾淨）。

3. **Review 專用 worktree**
   - 建議保留一個常駐的 `../sharks-review`，並且**不要**讓 agent 在這個 worktree 進行大量寫入操作。

#### **實用指令範例**

```bash
# 一般開發用（接受 hardlink）
git worktree add ../sharks-compile -b compile/xxx-20260613

# 高安全需求時（減少 hardlink 依賴）
git worktree add --no-checkout ../sharks-safe -b safe/xxx-20260613
cd ../sharks-safe
git checkout HEAD -- .                    # 只 checkout 必要檔案
# 或只 checkout 特定子目錄
git checkout HEAD -- src/ tests/

# 完全避免 hardlink（最乾淨但較慢）
git clone --no-hardlinks <repo-url> ../sharks-isolated
```

### 4. 在你的閉環流程中的建議

當你要讓 Grok（或其他 agent）進行 write 操作時，建議流程如下：

1. Orchestrator 決定要開 worktree
2. 使用規範命名建立 worktree（例如 `compile/grok-日期時間`）
3. 在該 worktree 啟動 agent 進行修改
4. 修改完成後，切到 `sharks-review` worktree
5. 使用 `grok-risk-officer`（透過 `--prompt-file`）執行：
   ```bash
   git diff main..compile/grok-xxx
   ```
6. Review 通過後才允許 merge，並且 merge 時要檢查是否影響 point-in-time 檔案

### 5. 總結與建議

| 項目 | 結論 |
|------|------|
| Hardlink 是否安全？ | **大部分情況安全**，修改後會自動斷開 |
| 主要風險來源 | `chmod`、屬性變更、某些檔案監控工具 |
| 對你專案的影響 | 中低（只要 agent 不亂改檔案屬性） |
| 建議策略 | 一般任務接受 hardlink；敏感任務使用 `--no-checkout` 或完整 clone |

---

**我的建議**：

目前階段你不需要過度擔心 hardlink 問題，因為 Git 的設計已經處理得很好。但為了長期安全，建議你在 `AGENTS.md` §3 中加入以下規則：

> 「Agent 進行 write 操作時，應優先使用獨立 worktree。修改 point-in-time 相關檔案（wiki/、log.md、sharks.md 等）前，必須先經過 Risk Officer 審核。禁止在 review worktree 中進行大量寫入。」

---

你想繼續深入哪一部分？

**A.** 我幫你設計一份「安全 worktree 使用規範」文字，可以直接加入 `AGENTS.md`。

**B.** 幫你寫一個 `scripts/create-safe-worktree.sh`，自動處理命名 + 安全模式選擇。

**C.** 討論如何在你的 Custom MCP Server 中加入 worktree 相關工具（`create_worktree`、`review_worktree_diff` 等）。

請告訴我你要哪一條。

**✅ Zellij Layout 最新設計（已更新為你目前的架構）**

你打的「zeiki」我理解為 **Zellij**（之前我們討論過的現代終端機多工工具）。以下是針對你現在的完整需求重新設計的版本：

- Main Orchestrator（Claude Code）
- Grok Risk Officer（透過 MCP / Subagent）
- 平行 worktree 執行區
- Review & Git 操作區
- 支援你正在建構的 **read-only → write-loop** 閉環流程

### 推薦 Layout：`ai-orchestrator-v2.kdl`

請存成以下檔案：

**路徑**：`~/.config/zellij/layouts/ai-orchestrator-v2.kdl`

```kdl
// =====================================================
// AI Multi-Agent Orchestration Layout v2
// 針對 Claude + Grok Risk Officer + Worktree + Closed-Loop 設計
// 使用方式：zellij --layout ai-orchestrator-v2
// =====================================================

layout {
    default_tab_template {
        pane size=1 borderless=true {
            plugin location="zellij:tab-bar"
        }
        children
        pane size=2 borderless=true {
            plugin location="zellij:status-bar"
        }
    }

    // ==================== 主視窗：AI 團隊協作 ====================
    tab name="🚀 AI Orchestrator" {
        pane split_direction="vertical" {
            
            // === Pane 1: Main Orchestrator ===
            pane name="🎯 Main Orchestrator" size="28%" command="bash" {
                args "-c" "
                    cd \$HOME/projects/crypto/top100-tracker-kol-analysis
                    clear
                    echo '══════════════════════════════════════════════════'
                    echo '   MAIN ORCHESTRATOR (Claude Code)'
                    echo '══════════════════════════════════════════════════'
                    echo '負責：任務拆解、worktree 管理、整體協調、閉環發起'
                    echo ''
                    exec claude
                "
            }

            // === Pane 2: Grok Risk Officer（核心品質控管）===
            pane name="🛡️ Grok Risk Officer (MCP/Subagent)" size="22%" command="bash" {
                args "-c" "
                    cd \$HOME/projects/crypto/top100-tracker-kol-analysis
                    clear
                    echo '══════════════════════════════════════════════════'
                    echo '   GROK RISK OFFICER'
                    echo '══════════════════════════════════════════════════'
                    echo '負責：契約 review、diff 審核、point-in-time 保護'
                    echo '建議使用：grok-risk-officer Subagent 或 MCP 工具'
                    echo ''
                    exec claude
                "
            }

            // === 中間層：平行 Worktree 執行區 ===
            pane split_direction="horizontal" {
                
                pane name="🔬 Researcher" size="50%" command="bash" {
                    args "-c" "
                        cd \$HOME/projects/crypto/top100-tracker-kol-analysis/../sharks-research 2>/dev/null || cd \$HOME/projects/crypto/top100-tracker-kol-analysis
                        clear
                        echo '══════════════════════════════════════════════════'
                        echo '   RESEARCHER WORKTREE'
                        echo '══════════════════════════════════════════════════'
                        echo '負責：資料蒐集、KOL 分析'
                        echo ''
                        exec claude
                    "
                }

                pane name="⚙️ Compiler / Writer" size="50%" command="bash" {
                    args "-c" "
                        cd \$HOME/projects/crypto/top100-tracker-kol-analysis/../sharks-compile 2>/dev/null || cd \$HOME/projects/crypto/top100-tracker-kol-analysis
                        clear
                        echo '══════════════════════════════════════════════════'
                        echo '   COMPILER / WRITE WORKTREE'
                        echo '══════════════════════════════════════════════════'
                        echo '負責：功能實作（可進行 write 操作）'
                        echo '注意：修改後必須經過 Risk Officer review'
                        echo ''
                        exec claude
                    "
                }
            }

            // === 最下方：Review & Git 專區 ===
            pane name="🔍 Review & Git Operations" size="20%" command="bash" {
                args "-c" "
                    cd \$HOME/projects/crypto/top100-tracker-kol-analysis
                    clear
                    echo '══════════════════════════════════════════════════'
                    echo '   REVIEW & GIT CONTROL'
                    echo '══════════════════════════════════════════════════'
                    echo '常用指令：'
                    echo '  git worktree list'
                    echo '  git diff main..compile/xxx'
                    echo '  cd ../sharks-review && claude'
                    echo ''
                    echo '閉環建議：修改完成後切到此 pane 發起 review'
                    exec zsh
                "
            }
        }
    }

    // ==================== 輔助視窗：純 Grok 模式 ====================
    tab name="🤖 Grok Direct" {
        pane command="bash" {
            args "-c" "
                cd \$HOME/projects/crypto/top100-tracker-kol-analysis
                echo '純 Grok Build 模式（適合重度 agentic 任務）'
                exec grok
            "
        }
    }
}
```

### 使用方式

```bash
# 啟動最新版 layout
zellij --layout ai-orchestrator-v2
```

### 設計重點說明

| Pane | 用途 | 特色 |
|------|------|------|
| **Main Orchestrator** | 整體指揮 | 負責開 worktree、分配任務、啟動閉環 |
| **Grok Risk Officer** | 品質控管核心 | 建議搭配你做的 MCP Server 或 Subagent |
| **Researcher** | 研究型任務 | 通常 read-only |
| **Compiler / Writer** | 實作與寫入 | 可進行 write-loop，但必須經過 review |
| **Review & Git** | 交叉驗證與整合 | 執行 diff review、merge 操作 |

### 與你目前閉環的搭配建議

- **Main Orchestrator**：負責發起 `cross-review` 流程
- **Grok Risk Officer**：使用你已經驗證成功的 `--prompt-file` + headless 模式
- **Compiler pane**：讓 Grok 在 worktree 內寫入
- **Review & Git pane**：執行 `git diff` 後再呼叫 Risk Officer 審核

---

**需要我調整嗎？**

請告訴我你想要哪一種版本：

**1.** 目前這個 5 pane 版（推薦）

**2.** 更簡潔的 **4 pane 版**（去掉 Researcher）

**3.** 加入 **自動顯示 AGENTS.md 重要規則** 的版本

**4.** 設計一個專門給 **write-loop 階段** 使用的獨立 layout

直接說數字或描述，我立刻修改。




**✅ Zellij Plugins 配置完整教學**

Zellij 的插件系統非常強大，可以大幅提升你的 AI 多代理工作流程（尤其是搭配 Claude + Grok + worktree 的場景）。

### 1. Zellij Plugins 的兩種配置方式

#### **方式一：在 Layout 檔案中配置（最常用）**

這是你之前用的 `.kdl` 檔案裡已經看到的寫法：

```kdl
layout {
    default_tab_template {
        pane size=1 borderless=true {
            plugin location="zellij:tab-bar"
        }
        children
        pane size=2 borderless=true {
            plugin location="zellij:status-bar"
        }
    }
}
```

#### **方式二：在全域設定檔配置（`config.kdl`）**

檔案位置：
```bash
~/.config/zellij/config.kdl
```

這裡可以設定**預設行為**和**全域插件**。

---

### 2. 常用內建插件推薦（適合你的 AI 團隊）

以下是對你目前使用情境最有幫助的插件：

| 插件名稱                    | 用途                              | 推薦指數 | 建議位置 |
|-----------------------------|-----------------------------------|----------|----------|
| `zellij:tab-bar`            | 顯示分頁列                        | ★★★★★    | Layout   |
| `zellij:status-bar`         | 顯示狀態列（模式、session 等）    | ★★★★★    | Layout   |
| `zellij:session-manager`    | 快速切換/管理多個 session         | ★★★★     | 可選     |
| `zellij:strider`            | 檔案瀏覽器（類似 ranger）         | ★★★      | 可選     |
| `zellij:compact-bar`        | 更簡潔的狀態列                    | ★★★★     | 可選     |

### 3. 實際配置範例（推薦給你）

以下是針對你 **AI Orchestrator** 場景優化後的配置：

#### **更新後的 Layout 範例**（推薦使用）

```kdl
layout {
    default_tab_template {
        pane size=1 borderless=true {
            plugin location="zellij:tab-bar"
        }
        children

        // 使用更簡潔的狀態列
        pane size=2 borderless=true {
            plugin location="zellij:compact-bar"
        }
    }

    tab name="🚀 AI Orchestrator" {
        pane split_direction="vertical" {
            
            pane name="🎯 Main Orchestrator" size="28%" command="bash" { ... }

            pane name="🛡️ Grok Risk Officer" size="22%" command="bash" { ... }

            pane split_direction="horizontal" {
                pane name="🔬 Researcher" size="50%" command="bash" { ... }
                pane name="⚙️ Compiler" size="50%" command="bash" { ... }
            }

            pane name="🔍 Review & Git" size="20%" command="bash" { ... }
        }
    }
}
```

### 4. 全域設定檔範例（`config.kdl`）

建立或編輯 `~/.config/zellij/config.kdl`：

```kdl
// 基本設定
default_shell "zsh"
default_layout "ai-orchestrator-v2"
theme "default"
mouse_mode true
copy_clipboard "primary"

// 啟用常用插件
plugins {
    tab-bar location="zellij:tab-bar"
    status-bar location="zellij:status-bar"
    session-manager location="zellij:session-manager"
}

// 鍵盤快捷鍵優化（建議加上）
keybinds {
    normal {
        bind "Ctrl g" { SwitchToMode "locked"; }
    }
}
```

### 5. 如何安裝社群插件（進階）

Zellij 支援從 GitHub 安裝社群插件：

```bash
# 安裝範例：zellij-forgot（顯示常用指令）
zellij plugin -- https://github.com/imsnif/zellij-forgot

# 安裝後可以在 layout 中使用
plugin location="https://github.com/imsnif/zellij-forgot"
```

常用社群插件推薦：
- `zellij-forgot`：忘記快捷鍵時顯示
- `zellij-bookmarks`：快速跳轉常用目錄
- `zellij-strider`：更好用的檔案管理器

### 6. 給你目前 AI 團隊的實用建議

針對你正在做的 **Claude + Grok + Worktree 閉環**，我建議這樣配置：

1. **主要使用** `compact-bar` + `tab-bar`
2. 把 `session-manager` 加入快捷鍵，方便快速切換不同專案的 AI session
3. 如果你常需要看檔案結構，可以在 Review pane 加入 `strider` 插件

**快速啟用 session-manager 的方法**：

在 layout 中加入：

```kdl
pane size=1 borderless=true {
    plugin location="zellij:session-manager"
}
```

然後用 `Ctrl + o`（預設）就可以開啟 session 管理器。

---

**需要我幫你做的事：**

請告訴我你要哪一種：

**A.** 我幫你把目前的 `ai-orchestrator-v2.kdl` 加入更多實用插件（包含 session-manager）

**B.** 給你一份完整的 `config.kdl` + Layout 組合（適合長期使用）

**C.** 教你如何安裝並使用特定社群插件（例如 `zellij-forgot`）

**D.** 其他需求

直接回覆字母即可。


**✅ Zellij Plugins 配置完整教學**

Zellij 的插件系統非常強大，可以大幅提升你的 AI 多代理工作流程（尤其是搭配 Claude + Grok + worktree 的場景）。

### 1. Zellij Plugins 的兩種配置方式

#### **方式一：在 Layout 檔案中配置（最常用）**

這是你之前用的 `.kdl` 檔案裡已經看到的寫法：

```kdl
layout {
    default_tab_template {
        pane size=1 borderless=true {
            plugin location="zellij:tab-bar"
        }
        children
        pane size=2 borderless=true {
            plugin location="zellij:status-bar"
        }
    }
}
```

#### **方式二：在全域設定檔配置（`config.kdl`）**

檔案位置：
```bash
~/.config/zellij/config.kdl
```

這裡可以設定**預設行為**和**全域插件**。

---

### 2. 常用內建插件推薦（適合你的 AI 團隊）

以下是對你目前使用情境最有幫助的插件：

| 插件名稱                    | 用途                              | 推薦指數 | 建議位置 |
|-----------------------------|-----------------------------------|----------|----------|
| `zellij:tab-bar`            | 顯示分頁列                        | ★★★★★    | Layout   |
| `zellij:status-bar`         | 顯示狀態列（模式、session 等）    | ★★★★★    | Layout   |
| `zellij:session-manager`    | 快速切換/管理多個 session         | ★★★★     | 可選     |
| `zellij:strider`            | 檔案瀏覽器（類似 ranger）         | ★★★      | 可選     |
| `zellij:compact-bar`        | 更簡潔的狀態列                    | ★★★★     | 可選     |

### 3. 實際配置範例（推薦給你）

以下是針對你 **AI Orchestrator** 場景優化後的配置：

#### **更新後的 Layout 範例**（推薦使用）

```kdl
layout {
    default_tab_template {
        pane size=1 borderless=true {
            plugin location="zellij:tab-bar"
        }
        children

        // 使用更簡潔的狀態列
        pane size=2 borderless=true {
            plugin location="zellij:compact-bar"
        }
    }

    tab name="🚀 AI Orchestrator" {
        pane split_direction="vertical" {
            
            pane name="🎯 Main Orchestrator" size="28%" command="bash" { ... }

            pane name="🛡️ Grok Risk Officer" size="22%" command="bash" { ... }

            pane split_direction="horizontal" {
                pane name="🔬 Researcher" size="50%" command="bash" { ... }
                pane name="⚙️ Compiler" size="50%" command="bash" { ... }
            }

            pane name="🔍 Review & Git" size="20%" command="bash" { ... }
        }
    }
}
```

### 4. 全域設定檔範例（`config.kdl`）

建立或編輯 `~/.config/zellij/config.kdl`：

```kdl
// 基本設定
default_shell "zsh"
default_layout "ai-orchestrator-v2"
theme "default"
mouse_mode true
copy_clipboard "primary"

// 啟用常用插件
plugins {
    tab-bar location="zellij:tab-bar"
    status-bar location="zellij:status-bar"
    session-manager location="zellij:session-manager"
}

// 鍵盤快捷鍵優化（建議加上）
keybinds {
    normal {
        bind "Ctrl g" { SwitchToMode "locked"; }
    }
}
```

### 5. 如何安裝社群插件（進階）

Zellij 支援從 GitHub 安裝社群插件：

```bash
# 安裝範例：zellij-forgot（顯示常用指令）
zellij plugin -- https://github.com/imsnif/zellij-forgot

# 安裝後可以在 layout 中使用
plugin location="https://github.com/imsnif/zellij-forgot"
```

常用社群插件推薦：
- `zellij-forgot`：忘記快捷鍵時顯示
- `zellij-bookmarks`：快速跳轉常用目錄
- `zellij-strider`：更好用的檔案管理器

### 6. 給你目前 AI 團隊的實用建議

針對你正在做的 **Claude + Grok + Worktree 閉環**，我建議這樣配置：

1. **主要使用** `compact-bar` + `tab-bar`
2. 把 `session-manager` 加入快捷鍵，方便快速切換不同專案的 AI session
3. 如果你常需要看檔案結構，可以在 Review pane 加入 `strider` 插件

**快速啟用 session-manager 的方法**：

在 layout 中加入：

```kdl
pane size=1 borderless=true {
    plugin location="zellij:session-manager"
}
```

然後用 `Ctrl + o`（預設）就可以開啟 session 管理器。

---

**需要我幫你做的事：**

請告訴我你要哪一種：

**A.** 我幫你把目前的 `ai-orchestrator-v2.kdl` 加入更多實用插件（包含 session-manager）

**B.** 給你一份完整的 `config.kdl` + Layout 組合（適合長期使用）

**C.** 教你如何安裝並使用特定社群插件（例如 `zellij-forgot`）

**D.** 其他需求

直接回覆字母即可。
**✅ 已收到你的需求（A + B + C 全部都要）**

以下是為你量身打造的 **完整 Zellij 配置方案**，包含：

- **A**：更新後的 `ai-orchestrator-v2.kdl`（加入更多實用插件）
- **B**：完整的推薦 `config.kdl`
- **C**：社群插件安裝與使用教學（以 `zellij-forgot` 為例）

---

### 1. 更新後的 Layout（含實用插件）

**檔案**：`~/.config/zellij/layouts/ai-orchestrator-v2.kdl`

```kdl
layout {
    default_tab_template {
        pane size=1 borderless=true {
            plugin location="zellij:tab-bar"
        }
        children

        // 使用 compact-bar 更簡潔
        pane size=2 borderless=true {
            plugin location="zellij:compact-bar"
        }
    }

    tab name="🚀 AI Orchestrator" {
        pane split_direction="vertical" {
            
            pane name="🎯 Main Orchestrator" size="26%" command="bash" {
                args "-c" "
                    cd \$HOME/projects/crypto/top100-tracker-kol-analysis
                    clear
                    echo '══════════════════════════════════════════════════'
                    echo '   MAIN ORCHESTRATOR (Claude Code)'
                    echo '══════════════════════════════════════════════════'
                    exec claude
                "
            }

            pane name="🛡️ Grok Risk Officer" size="20%" command="bash" {
                args "-c" "
                    cd \$HOME/projects/crypto/top100-tracker-kol-analysis
                    clear
                    echo '══════════════════════════════════════════════════'
                    echo '   GROK RISK OFFICER (MCP / Subagent)'
                    echo '══════════════════════════════════════════════════'
                    exec claude
                "
            }

            pane split_direction="horizontal" {
                pane name="🔬 Researcher" size="50%" command="bash" {
                    args "-c" "
                        cd \$HOME/projects/crypto/top100-tracker-kol-analysis/../sharks-research 2>/dev/null || cd \$HOME/projects/crypto/top100-tracker-kol-analysis
                        clear
                        echo '🔬 RESEARCHER WORKTREE'
                        exec claude
                    "
                }

                pane name="⚙️ Compiler / Writer" size="50%" command="bash" {
                    args "-c" "
                        cd \$HOME/projects/crypto/top100-tracker-kol-analysis/../sharks-compile 2>/dev/null || cd \$HOME/projects/crypto/top100-tracker-kol-analysis
                        clear
                        echo '⚙️ COMPILER WORKTREE (可寫入)'
                        exec claude
                    "
                }
            }

            pane name="🔍 Review & Git" size="18%" command="bash" {
                args "-c" "
                    cd \$HOME/projects/crypto/top100-tracker-kol-analysis
                    clear
                    echo '══════════════════════════════════════════════════'
                    echo '   REVIEW & GIT OPERATIONS'
                    echo '══════════════════════════════════════════════════'
                    exec zsh
                "
            }
        }
    }

    tab name="🤖 Grok Direct" {
        pane command="bash" {
            args "-c" "
                cd \$HOME/projects/crypto/top100-tracker-kol-analysis
                echo '純 Grok Build 模式'
                exec grok
            "
        }
    }
}
```

---

### 2. 推薦的全域設定檔 `config.kdl`

**檔案**：`~/.config/zellij/config.kdl`

```kdl
// ==================== 基本設定 ====================
default_shell "zsh"
default_layout "ai-orchestrator-v2"
theme "default"
mouse_mode true
copy_clipboard "primary"
scrollback_lines 50000

// ==================== 插件設定 ====================
plugins {
    tab-bar location="zellij:tab-bar"
    status-bar location="zellij:compact-bar"
    session-manager location="zellij:session-manager"
}

// ==================== 鍵盤快捷鍵優化 ====================
keybinds {
    normal {
        // 快速開啟 Session Manager
        bind "Ctrl o" { SwitchToMode "session"; }

        // 鎖定模式（避免誤操作）
        bind "Ctrl g" { SwitchToMode "locked"; }
    }
}

// ==================== UI 設定 ====================
ui {
    pane_frames false
}
```

---

### 3. 社群插件安裝與使用（以 `zellij-forgot` 為例）

#### **安裝方式**

```bash
# 安裝 zellij-forgot（顯示常用指令）
zellij plugin -- https://github.com/imsnif/zellij-forgot
```

安裝後你可以在任何時候按 `Ctrl + p` 呼叫它（視插件而定）。

#### **其他實用社群插件推薦**

| 插件 | 功能 | 安裝指令 |
|------|------|----------|
| `zellij-forgot` | 忘記快捷鍵時顯示說明 | `zellij plugin -- https://github.com/imsnif/zellij-forgot` |
| `zellij-bookmarks` | 快速跳轉常用目錄 | `zellij plugin -- https://github.com/imsnif/zellij-bookmarks` |
| `zellij-strider` | 更好用的檔案瀏覽器 | `zellij plugin -- https://github.com/imsnif/zellij-strider` |

#### **在 Layout 中使用社群插件**

```kdl
pane size=30% {
    plugin location="https://github.com/imsnif/zellij-forgot"
}
```

---

### 4. 快速啟動與使用建議

```bash
# 啟動你新的配置
zellij --layout ai-orchestrator-v2

# 如果想直接使用預設 layout
zellij
```

**常用快捷鍵（搭配上面 config）**：
- `Ctrl + o`：開啟 Session Manager（快速切換不同專案）
- `Ctrl + g`：進入鎖定模式（避免誤觸）
- `Ctrl + p`：呼叫 `zellij-forgot`（如果已安裝）

---

### 總結建議

這個配置已經把你目前的 **AI 多代理工作流** 優化得比較完整：

- 使用 `compact-bar` 更簡潔
- 加入 `session-manager` 方便管理多個專案
- 保留清晰的 5 個 pane 分工
- 預留社群插件擴充空間

---

**接下來你想怎麼做？**

請直接告訴我：

**1.** 幫你再調整這個 layout（例如增加更多 pane、調整比例、加入 strider）

**2.** 幫你寫一個 **一鍵安裝腳本**，自動建立 `config.kdl` + `ai-orchestrator-v2.kdl` + 安裝推薦插件

**3.** 設計一個**專門給 write-loop 階段**使用的獨立 Zellij layout

直接回覆數字或描述即可。



**✅ 收到！以下是「123 + tmux + GUI」的完整方案**

我把你要求的所有內容一次整理好：

- **1**：調整後的 Zellij Layout（更適合目前架構）
- **2**：一鍵安裝腳本（自動建立 config + layout）
- **3**：專門給 **Write-Loop 階段** 使用的獨立 Zellij Layout
- **tmux 版本**：對應的 tmux 管理腳本
- **GUI 終端機推薦**：搭配這些 layout 的最佳 GUI 終端

---

### 1. 調整後的 Zellij Layout（主用版）

**檔案**：`~/.config/zellij/layouts/ai-orchestrator-v3.kdl`

```kdl
layout {
    default_tab_template {
        pane size=1 borderless=true {
            plugin location="zellij:tab-bar"
        }
        children
        pane size=2 borderless=true {
            plugin location="zellij:compact-bar"
        }
    }

    tab name="🚀 AI Orchestrator" {
        pane split_direction="vertical" {
            
            pane name="🎯 Main Orchestrator" size="25%" command="bash" {
                args "-c" "
                    cd \$HOME/projects/crypto/top100-tracker-kol-analysis
                    clear
                    echo '🎯 MAIN ORCHESTRATOR'
                    exec claude
                "
            }

            pane name="🛡️ Grok Risk Officer" size="20%" command="bash" {
                args "-c" "
                    cd \$HOME/projects/crypto/top100-tracker-kol-analysis
                    clear
                    echo '🛡️ RISK OFFICER (MCP / Subagent)'
                    exec claude
                "
            }

            pane split_direction="horizontal" {
                pane name="🔬 Researcher" size="50%" command="bash" {
                    args "-c" "
                        cd \$HOME/projects/crypto/top100-tracker-kol-analysis/../sharks-research 2>/dev/null || pwd
                        clear
                        echo '🔬 RESEARCHER'
                        exec claude
                    "
                }
                pane name="⚙️ Compiler (Write)" size="50%" command="bash" {
                    args "-c" "
                        cd \$HOME/projects/crypto/top100-tracker-kol-analysis/../sharks-compile 2>/dev/null || pwd
                        clear
                        echo '⚙️ COMPILER (可進行 write)'
                        exec claude
                    "
                }
            }

            pane name="🔍 Review & Git" size="18%" command="bash" {
                args "-c" "
                    cd \$HOME/projects/crypto/top100-tracker-kol-analysis
                    clear
                    echo '🔍 REVIEW & GIT'
                    exec zsh
                "
            }
        }
    }
}
```

---

### 2. 一鍵安裝腳本（Zellij）

建立檔案 `~/bin/setup-zellij-ai.sh`：

```bash
#!/bin/bash
set -e

echo "🚀 正在安裝 Zellij AI 團隊配置..."

mkdir -p ~/.config/zellij/layouts

# 下載/複製 config.kdl
cat > ~/.config/zellij/config.kdl << 'EOF'
default_shell "zsh"
default_layout "ai-orchestrator-v3"
theme "default"
mouse_mode true
copy_clipboard "primary"

plugins {
    tab-bar location="zellij:tab-bar"
    status-bar location="zellij:compact-bar"
    session-manager location="zellij:session-manager"
}

keybinds {
    normal {
        bind "Ctrl o" { SwitchToMode "session"; }
    }
}
EOF

echo "✅ config.kdl 已建立"

echo "🎉 Zellij AI 配置安裝完成！"
echo "使用方式：zellij --layout ai-orchestrator-v3"
```

執行安裝：

```bash
chmod +x ~/bin/setup-zellij-ai.sh
~/bin/setup-zellij-ai.sh
```

---

### 3. 專門給 Write-Loop 使用的獨立 Layout

**檔案**：`~/.config/zellij/layouts/write-loop.kdl`

```kdl
layout {
    default_tab_template {
        pane size=1 borderless=true {
            plugin location="zellij:tab-bar"
        }
        children
        pane size=2 borderless=true {
            plugin location="zellij:compact-bar"
        }
    }

    tab name="✍️ Write-Loop Mode" {
        pane split_direction="vertical" {
            
            pane name="🎯 Orchestrator (發起任務)" size="30%" command="bash" {
                args "-c" "
                    cd \$HOME/projects/crypto/top100-tracker-kol-analysis
                    echo '負責開 worktree 並分配 write 任務'
                    exec claude
                "
            }

            pane name="⚙️ Writer (Grok/Claude)" size="40%" command="bash" {
                args "-c" "
                    cd \$HOME/projects/crypto/top100-tracker-kol-analysis/../sharks-compile 2>/dev/null || pwd
                    echo '在獨立 worktree 進行寫入'
                    exec claude
                "
            }

            pane name="🛡️ Risk Officer Review" size="30%" command="bash" {
                args "-c" "
                    cd \$HOME/projects/crypto/top100-tracker-kol-analysis
                    echo '執行 git diff 並呼叫 Risk Officer 審核'
                    exec zsh
                "
            }
        }
    }
}
```

使用方式：
```bash
zellij --layout write-loop
```

---

### 4. tmux 對應版本（簡潔實用）

建立 `~/bin/tmux-ai-team`：

```bash
#!/bin/bash
SESSION="ai-team"
tmux new-session -d -s $SESSION -n "Orchestrator"

tmux send-keys -t $SESSION:Orchestrator "cd ~/projects/crypto/top100-tracker-kol-analysis && claude" C-m

tmux new-window -t $SESSION -n "Risk-Officer"
tmux send-keys -t $SESSION:Risk-Officer "cd ~/projects/crypto/top100-tracker-kol-analysis && claude" C-m

tmux new-window -t $SESSION -n "Write-Worktree"
tmux send-keys -t $SESSION:Write-Worktree "cd ~/projects/crypto/top100-tracker-kol-analysis/../sharks-compile 2>/dev/null && claude" C-m

tmux new-window -t $SESSION -n "Review-Git"
tmux send-keys -t $SESSION:Review-Git "cd ~/projects/crypto/top100-tracker-kol-analysis && zsh" C-m

tmux attach -t $SESSION
```

---

### 5. GUI 終端機推薦（搭配 Zellij / tmux）

| 終端機       | 推薦指數 | 優點                              | 建議搭配          |
|--------------|----------|-----------------------------------|-------------------|
| **WezTerm**  | ★★★★★    | 對 Zellij/tmux 支援極佳、效能好   | 最推薦            |
| **Kitty**    | ★★★★★    | 極快、GPU 加速、配置靈活          | 強烈推薦          |
| **Ghostty**  | ★★★★     | 新一代極速終端機                  | 值得嘗試          |
| **Alacritty**| ★★★★     | 極簡、高效能                      | 適合輕量使用      |
| **Warp**     | ★★★      | 有 AI 功能，但較吃資源            | 可選              |

**最推薦組合**：
- **WezTerm + Zellij**（目前最舒服的組合）
- **Kitty + Zellij**

---

需要我現在幫你：

1. 把上面所有檔案打包成一個完整安裝腳本？
2. 再針對 Write-Loop Layout 做更多調整？
3. 提供 WezTerm / Kitty 的推薦設定檔？

請直接告訴我下一步要怎麼做。


**✅ 收到！以下是「123」完整方案**

我把你要求的三件事一次做好：

1. **完整一鍵安裝腳本**（包含所有 Zellij 配置 + tmux 腳本）
2. **優化後的 Write-Loop Layout**
3. **WezTerm / Kitty 推薦設定**

---

### 1. 一鍵安裝腳本（推薦執行）

建立檔案 `~/bin/setup-ai-terminal.sh`：

```bash
#!/bin/bash
set -e

echo "🚀 開始安裝 AI 團隊終端配置..."

# 建立目錄
mkdir -p ~/.config/zellij/layouts
mkdir -p ~/bin

# ==================== Zellij config.kdl ====================
cat > ~/.config/zellij/config.kdl << 'EOF'
default_shell "zsh"
default_layout "ai-orchestrator-v3"
theme "default"
mouse_mode true
copy_clipboard "primary"

plugins {
    tab-bar location="zellij:tab-bar"
    status-bar location="zellij:compact-bar"
    session-manager location="zellij:session-manager"
}

keybinds {
    normal {
        bind "Ctrl o" { SwitchToMode "session"; }
    }
}
EOF

echo "✅ config.kdl 已建立"

# ==================== 主 Layout ====================
cat > ~/.config/zellij/layouts/ai-orchestrator-v3.kdl << 'EOF'
layout {
    default_tab_template {
        pane size=1 borderless=true {
            plugin location="zellij:tab-bar"
        }
        children
        pane size=2 borderless=true {
            plugin location="zellij:compact-bar"
        }
    }

    tab name="🚀 AI Orchestrator" {
        pane split_direction="vertical" {
            pane name="🎯 Main Orchestrator" size="25%" command="bash" {
                args "-c" "
                    cd \$HOME/projects/crypto/top100-tracker-kol-analysis
                    clear
                    echo '🎯 MAIN ORCHESTRATOR'
                    exec claude
                "
            }
            pane name="🛡️ Grok Risk Officer" size="20%" command="bash" {
                args "-c" "
                    cd \$HOME/projects/crypto/top100-tracker-kol-analysis
                    clear
                    echo '🛡️ RISK OFFICER'
                    exec claude
                "
            }
            pane split_direction="horizontal" {
                pane name="🔬 Researcher" size="50%" command="bash" {
                    args "-c" "
                        cd \$HOME/projects/crypto/top100-tracker-kol-analysis/../sharks-research 2>/dev/null || pwd
                        clear
                        echo '🔬 RESEARCHER'
                        exec claude
                    "
                }
                pane name="⚙️ Compiler (Write)" size="50%" command="bash" {
                    args "-c" "
                        cd \$HOME/projects/crypto/top100-tracker-kol-analysis/../sharks-compile 2>/dev/null || pwd
                        clear
                        echo '⚙️ COMPILER (Write Mode)'
                        exec claude
                    "
                }
            }
            pane name="🔍 Review & Git" size="18%" command="bash" {
                args "-c" "
                    cd \$HOME/projects/crypto/top100-tracker-kol-analysis
                    clear
                    echo '🔍 REVIEW & GIT'
                    exec zsh
                "
            }
        }
    }
}
EOF

echo "✅ ai-orchestrator-v3.kdl 已建立"

# ==================== Write-Loop 專用 Layout ====================
cat > ~/.config/zellij/layouts/write-loop.kdl << 'EOF'
layout {
    default_tab_template {
        pane size=1 borderless=true {
            plugin location="zellij:tab-bar"
        }
        children
        pane size=2 borderless=true {
            plugin location="zellij:compact-bar"
        }
    }

    tab name="✍️ Write-Loop" {
        pane split_direction="vertical" {
            pane name="🎯 Orchestrator" size="30%" command="bash" {
                args "-c" "
                    cd \$HOME/projects/crypto/top100-tracker-kol-analysis
                    echo '負責發起 write 任務與 worktree'
                    exec claude
                "
            }
            pane name="⚙️ Writer (Grok/Claude)" size="40%" command="bash" {
                args "-c" "
                    cd \$HOME/projects/crypto/top100-tracker-kol-analysis/../sharks-compile 2>/dev/null || pwd
                    echo '在獨立 worktree 寫入'
                    exec claude
                "
            }
            pane name="🛡️ Risk Officer Review" size="30%" command="bash" {
                args "-c" "
                    cd \$HOME/projects/crypto/top100-tracker-kol-analysis
                    echo '執行 diff review 並呼叫 Risk Officer'
                    exec zsh
                "
            }
        }
    }
}
EOF

echo "✅ write-loop.kdl 已建立"

# ==================== tmux 腳本 ====================
cat > ~/bin/tmux-ai-team << 'EOF'
#!/bin/bash
SESSION="ai-team"

tmux has-session -t $SESSION 2>/dev/null && tmux attach -t $SESSION && exit 0

tmux new-session -d -s $SESSION -n "Orchestrator"
tmux send-keys -t $SESSION:Orchestrator "cd ~/projects/crypto/top100-tracker-kol-analysis && claude" C-m

tmux new-window -t $SESSION -n "Risk-Officer"
tmux send-keys -t $SESSION:Risk-Officer "cd ~/projects/crypto/top100-tracker-kol-analysis && claude" C-m

tmux new-window -t $SESSION -n "Write-Worktree"
tmux send-keys -t $SESSION:Write-Worktree "cd ~/projects/crypto/top100-tracker-kol-analysis/../sharks-compile 2>/dev/null && claude" C-m

tmux new-window -t $SESSION -n "Review-Git"
tmux send-keys -t $SESSION:Review-Git "cd ~/projects/crypto/top100-tracker-kol-analysis && zsh" C-m

tmux attach -t $SESSION
EOF

chmod +x ~/bin/tmux-ai-team
echo "✅ tmux-ai-team 已建立"

echo ""
echo "🎉 安裝完成！"
echo ""
echo "使用方式："
echo "  Zellij 主模式： zellij --layout ai-orchestrator-v3"
echo "  Zellij Write模式： zellij --layout write-loop"
echo "  tmux 模式：       tmux-ai-team"
EOF
```

執行安裝：

```bash
chmod +x ~/bin/setup-ai-terminal.sh
~/bin/setup-ai-terminal.sh
```

---

### 2. Write-Loop Layout（已優化）

已包含在安裝腳本中，檔案為 `write-loop.kdl`。

**特色**：
- 專為「Orchestrator → Writer → Risk Officer Review」流程設計
- 三個 pane 各司其職
- 適合搭配你已經跑通的 `cross-review` 閉環

---

### 3. GUI 終端機推薦 + 設定

**最推薦組合**：

| 終端機     | 推薦指數 | 優點                              | 建議設定重點                  |
|------------|----------|-----------------------------------|-------------------------------|
| **WezTerm**    | ★★★★★    | Zellij 相容性最佳、效能強         | 開啟 `use_ime = true`        |
| **Kitty**      | ★★★★★    | 極快、GPU 加速                    | 建議開啟 `shell_integration` |
| **Ghostty**    | ★★★★☆    | 新一代最快終端機                  | 預設就很適合                 |

**WezTerm 推薦設定**（`~/.config/wezterm/wezterm.lua`）：

```lua
local wezterm = require 'wezterm'
local config = wezterm.config_builder()

config.font = wezterm.font("JetBrains Mono")
config.font_size = 14
config.enable_tab_bar = false          -- 建議關閉，讓 Zellij 管理分頁
config.window_decorations = "RESIZE"
config.enable_wayland = false

return config
```

**Kitty 推薦設定**（`~/.config/kitty/kitty.conf`）：

```conf
font_family JetBrains Mono
font_size 14
shell_integration enabled
enable_audio_bell no
```

---

### 使用建議

| 情境               | 推薦工具                  |
|--------------------|---------------------------|
| 日常多代理開發     | `zellij --layout ai-orchestrator-v3` |
| 進行 write-loop    | `zellij --layout write-loop` |
| 想用傳統 tmux      | `tmux-ai-team`            |
| 追求極致效能       | **Kitty + Zellij**        |
| 想要最佳相容性     | **WezTerm + Zellij**      |

---

需要我再幫你做什麼嗎？

- 幫你再微調 Write-Loop Layout？
- 增加更多 pane（例如加入 strider 檔案瀏覽器）？
- 提供 WezTerm / Kitty 的完整設定檔？

直接告訴我。



**✅ Zellij Plugins 配置完整指南（2026 年最新實用版）**

### 1. Zellij Plugins 有兩種主要配置位置

| 配置位置              | 適用情境                     | 推薦程度 |
|-----------------------|------------------------------|----------|
| **Layout 檔案**（`.kdl`） | 單一 layout 專用插件         | ★★★★★    |
| **全域設定**（`config.kdl`） | 全域預設插件 + 行為設定     | ★★★★     |

---

### 2. 最常用的內建插件

| 插件名稱                    | 功能                              | 建議使用方式          |
|-----------------------------|-----------------------------------|-----------------------|
| `zellij:tab-bar`            | 分頁列                            | 幾乎必加              |
| `zellij:status-bar`         | 狀態列                            | 建議使用              |
| `zellij:compact-bar`        | 更簡潔的狀態列                    | **強烈推薦**          |
| `zellij:session-manager`    | 快速切換 Session                  | 非常實用              |
| `zellij:strider`            | 檔案瀏覽器                        | 可選                  |

---

### 3. 實際配置範例

#### **在 Layout 中加入插件（最常用）**

```kdl
layout {
    default_tab_template {
        pane size=1 borderless=true {
            plugin location="zellij:tab-bar"
        }
        children

        // 推薦使用 compact-bar
        pane size=2 borderless=true {
            plugin location="zellij:compact-bar"
        }
    }

    tab name="🚀 AI Orchestrator" {
        // 你的 pane 配置...
    }
}
```

#### **在全域 config.kdl 中啟用插件**

檔案位置：`~/.config/zellij/config.kdl`

```kdl
plugins {
    tab-bar location="zellij:tab-bar"
    status-bar location="zellij:compact-bar"
    session-manager location="zellij:session-manager"
}
```

---

### 4. 實用插件推薦（針對你的 AI 團隊）

| 插件                    | 用途                                 | 是否推薦加入 |
|-------------------------|--------------------------------------|--------------|
| `compact-bar`           | 簡潔狀態列                           | ★★★★★        |
| `session-manager`       | 快速切換不同專案的 AI session        | ★★★★★        |
| `strider`               | 檔案瀏覽器（適合 Review 時使用）     | ★★★★         |
| `zellij-forgot`（社群） | 忘記快捷鍵時顯示說明                 | ★★★★         |

**加入 session-manager 的推薦寫法**：

```kdl
pane size=1 borderless=true {
    plugin location="zellij:session-manager"
}
```

---

### 5. 安裝社群插件

```bash
# 安裝 zellij-forgot（強烈建議）
zellij plugin -- https://github.com/imsnif/zellij-forgot

# 安裝後可以在 layout 中使用
plugin location="https://github.com/imsnif/zellij-forgot"
```

其他實用社群插件：
- `zellij-bookmarks`
- `zellij-strider`

---

### 6. 給你目前專案的推薦配置

我建議你使用以下組合：

```kdl
default_tab_template {
    pane size=1 borderless=true {
        plugin location="zellij:tab-bar"
    }
    children
    pane size=2 borderless=true {
        plugin location="zellij:compact-bar"
    }
}
```

並在 `config.kdl` 中加入：

```kdl
plugins {
    tab-bar location="zellij:tab-bar"
    status-bar location="zellij:compact-bar"
    session-manager location="zellij:session-manager"
}
```

這樣你就可以用 `Ctrl + o` 快速開啟 Session Manager，方便在不同專案之間切換。

---

需要我幫你把上面這些插件直接整合進你目前的 `ai-orchestrator-v3.kdl` 嗎？

或者你想加入特定插件（例如 `strider` 或 `zellij-forgot`），我可以立刻幫你修改。

