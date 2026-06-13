# $hark 推進計劃書下一步 + CLAUDE.md 憲法改進

**日期**：2026-06-13 | **Risk Officer**：Grok (shark-risk-officer skill) | **目的**：給 Claude Orchestrator 與你（Alex）清晰、可執行的下一步 + 強化憲法

---

## 一、推進計劃書下一步（分階段，可直接給 Claude 參考）

### Phase 0（今天完成）— 基礎收斂
1. 你把 `shark-daily-catalyst-workflow-proposal.md` **整份** 貼給 Claude，並附上指示：
   > 你是 Orchestrator，請使用 grok-risk-review skill 嚴格審查本 workflow v2，輸出 fine-tune 版本 + 更完整的 Discord 整合方案 + 下一步可執行的 Writer 任務清單。
2. Claude 回覆後，與我（Risk Officer）一起 review 最終版本，確認 guardrails 無缺口。
3. 你手動把之前 Claude 提供的 **5 段 CLAUDE.md diff** 貼進 CLAUDE.md（§2 附近）。

### Phase 1（1-2 天內）— Discord 戰情室 + 新 Skill 落地
1. 在 Discord bot 實作以下新指令（後端呼叫 skill 或本地 LLM + RAG）：
   - `/grok_review <ticker> <catalyst>`
   - `/supply_chain_hunter <ticker>`
   - `/council <agent-list>` （自動注入 guardrails + 10-signal 格式）
2. 建立 `supply-chain-hunter` skill 初始版本（我可立即產出 skeleton）。
3. 建立 `macro-shield`、`kol-validator`、`personal-guardrail` 的 prompt 模板（放在 `shark-agents/` 資料夾）。
4. 更新 `launch-daily.ps1` 或新增 `launch-catalyst-review.ps1`，把新指令與 council 模式納入日常啟動。

### Phase 2（3-5 天內）— 端到端測試 + Risk Gate 強化
1. 選一個真實 catalyst（例如 NVDA 近期事件）進行完整演練：
   - Claude 呼叫 skills → Grok 回報 → Discord /council 辯論 → Zellij Writer 在 worktree 實作 → Risk gate 審查 → 輸出 10-signal
2. 把 `cross-review.ps1` 與新 skills 整合（讓 Claude 也能輕鬆呼叫 `grok-risk-review`）。
3. 定義並強制執行 **10-signal 標準輸出格式**（JSON + Markdown 雙格式，寫入 `outputs/catalyst/`）。
4. 在 AGENTS.md 或新 `OPERATING-DISCIPLINE.md` 中加入 council 辯論紀律（限時、結構化輸出、必須自報已通過 Risk gate）。

### Phase 3（1 週內）— 系統化與文件化
1. 把新 agents 與 skills 註冊進現有 RAG（disclosures.json + 新 guardrails）。
2. 更新 `docs/QUICKSTART_USAGE_zh.md` 與 `FULL_..._EXECUTION_PLAN_zh.md`，加入 catalyst workflow。
3. 建立 Task Scheduler 任務，讓每天固定時間自動觸發「晨會 catalyst review」。
4. 進行第一次「多 agent 壓力測試」（故意給有風險的 catalyst，觀察 council 是否能正確拒絕或降級）。

### Phase 4（持續）— 擴展與優化
- 新增更多垂直 agent（例如 earnings-whisperer、options-flow-hunter、geopolitics-shield）。
- 把 10-signal 與現有 Portfolio Risk / Bubble Chart 儀表板串接（Streamlit 更新）。
- 建立「Agent Performance Review」機制（每週由 Risk Officer 審查各 agent 輸出品質與 guardrail 遵守度）。

**Risk Officer 建議優先序**：Phase 0 → Phase 1（先讓 Discord 戰情室跑起來）→ Phase 2（端到端閉環最重要）。

---

## 二、CLAUDE.md 憲法改進建議（可直接貼的追加段落）

以下是針對新 workflow 與多 agent 系統，建議追加到 CLAUDE.md 的段落（放在之前 5 段之後，或獨立成新章節 §10+）。

**請你手動貼進 CLAUDE.md**（遵守 §9 規則，我只出 diff）。

```markdown
## Multi-Agent Governance & New Skills
- All new agents and skills (supply-chain-hunter, macro-shield, kol-validator, personal-guardrail, grok-risk-review, etc.) must be reviewed by Risk Officer (Grok using shark-risk-officer skill) before activation.
- New skills must follow the established pattern: clear single responsibility, injected Core Guardrails, communication via outputs/ folder or Discord, and mandatory Risk gate before any capital-related output.
- Claude (Orchestrator) may propose new agents/skills, but final approval and guardrail injection must go through Risk Officer review. Direct self-modification of agent behavior (hooks, settings, core prompts) without explicit user + Risk Officer authorization is prohibited.

## Council Debate & 10-Signal Protocol
- When /council or multi-agent debate is triggered, every participating agent must first declare "Risk Officer gate passed" and reference the specific guardrails checked.
- All council outputs must follow the standardized 10-signal format:
  1. Catalyst Strength
  2. Supply Chain Risk Score
  3. Macro Shield Alignment
  4. KOL/On-chain Validator Consensus
  5. Personal Guardrail Fit
  6. Momentum Decoupling Confirmation
  7. Capital Allocation Safety (under hard cutoff)
  8. Worktree Isolation Verified
  9. Conflict Resolver Status
  10. Overall Recommend Score + Rationale
- Debate must be time-boxed. If no clear consensus after 2 rounds, default to "No action — escalate to Risk Officer for deeper review".
- Personal-guardrail agent has veto power on any signal that conflicts with user memory (privacy, risk tolerance, capital rules).

## Discord Integration & Command Governance
- Discord commands that trigger agents or skills (/grok_review, /supply_chain_hunter, /council, etc.) must log the full request + agent outputs to outputs/discord-logs/ with timestamps.
- Commands that could influence capital decisions must include explicit "RECOMMEND ONLY" disclaimer in the response.
- Bot must never auto-execute trades or expose keys. All execution paths remain disabled or mocked.
- New Discord commands or bot features require Risk Officer review of the implementation diff before deployment.

## Risk Gate Enforcement
- Every significant output (10-signal, council conclusion, new strategy code, backtest result that may affect allocation) must pass through Risk Officer (via cross-review.ps1 -Reviewer grok or direct grok-risk-review skill call) before being presented to user or written to final outputs/.
- Writer (aider in worktree) must never bypass Risk gate. Any attempt to do so must be logged and escalated.
- If Risk Officer flags high-severity issues, the output is blocked until resolved or explicitly overridden by user with written confirmation.

## Continuous Improvement of Constitution
- Any proposed change to this CLAUDE.md or core guardrails must be submitted as a diff by the proposer (never direct edit).
- Risk Officer maintains the authoritative interpretation of these rules during active operations.
- Weekly (or after major incidents), Risk Officer + Orchestrator shall jointly review whether new guardrails or agent rules need to be added to this constitution.
```

---

## 三、Risk Officer 總結與立即行動建議

**已準備好的文件（可直接使用）**：
- `shark-daily-catalyst-workflow-proposal.md`（已 review 通過）
- 本文件（推進計劃書 + CLAUDE.md 追加段落）
- `shark-agents/agent-prompt-templates.md`（現成 4 個新 agent 模板）

**你現在可以做的 3 件事（建議順序）**：
1. 把 `shark-daily-catalyst-workflow-proposal.md` 整份貼給 Claude，啟動迭代。
2. 把上面「CLAUDE.md 追加段落」手動貼進你的 CLAUDE.md。
3. 告訴我「產出 supply-chain-hunter skill skeleton」或「產出 Discord command 實作草稿」，我立刻繼續幫你建。

這套系統現在有清晰的推進 roadmap + 更強的憲法護欄，已經可以安全地往前走了。

需要我現在就產出下一個具體檔案（skill、script、或更細的 Phase 1 任務清單）嗎？🦈

直接說需求，我繼續把關與產出。