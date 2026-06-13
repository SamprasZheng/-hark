# scripts/

Automation scripts for Sharks.

## Daily routine scripts

### `daily_am.ps1` — morning run (pre-market)
- Re-run FOM with overnight data
- Stage `outputs/daily_todo_<date>.md` for Compiler agent (news scan agenda)
- Run via Windows Task Scheduler at 06:00 local

### `daily_pm.ps1` — evening run (post-close)
- Re-run FOM with EOD prices
- Update `data/persistence_state.json`
- Git commit changes
- Stage `outputs/evening_summary_<date>.md`
- Run via Windows Task Scheduler at 22:00 local

## Setup

### Install as Windows Task Scheduler tasks

```powershell
# AM task
schtasks /create /tn "Sharks Daily AM" /tr "powershell.exe -NoProfile -ExecutionPolicy Bypass -File 'D:\DOT\`$hark\scripts\daily_am.ps1'" /sc DAILY /st 06:00

# PM task
schtasks /create /tn "Sharks Daily PM" /tr "powershell.exe -NoProfile -ExecutionPolicy Bypass -File 'D:\DOT\`$hark\scripts\daily_pm.ps1'" /sc DAILY /st 22:00
```

Or use the Task Scheduler GUI:
1. Open Task Scheduler (taskschd.msc)
2. Create Basic Task → name "Sharks Daily AM" / "PM"
3. Trigger: Daily at 06:00 / 22:00
4. Action: Start a program
5. Program: `powershell.exe`
6. Arguments: `-NoProfile -ExecutionPolicy Bypass -File "D:\DOT\$hark\scripts\daily_am.ps1"` (or `_pm.ps1`)

## Note on Compiler agent collaboration

The daily scripts **stage TODO files** for the human's next chat session with the Compiler agent. ...

This is **the deliberate slow-loop design** — automation handles quant; humans + LLM handle qualitative news synthesis. Per [[../CLAUDE]] §2 SAFETY boundaries, the system never auto-trades.

## Cross-review + RAG (Risk Officer guardrail)

`cross-review.ps1` is the bridge for Claude (orchestrator) ↔ Grok/local (Risk Officer).

New flags (2026-06 RAG upgrade):
- `-Reviewer grok|local|codex`  (default grok)
- `-UseRag` — calls `scripts/rag_retriever.py` (LlamaIndex/Chroma + nomic-embed-text via Ollama, or keyword fallback). Injects `rag-data/contracts/disclosures.json` (tail +500% winsorization + TD-9 sell hard-disable) + PIT/raw rules into every prompt.
- Always uses `--prompt-file` (the only reliable path through PS→WSL).

Example (from Windows, Claude-driven):
```powershell
.\scripts\cross-review.ps1 src\sharks\scoring\fom.py -UseRag -Task "對照 disclosures.json 檢查 tail risk 與 TD-9 sell 禁令" -Effort high
.\scripts\cross-review.ps1 -Reviewer local -UseRag -Target "working"
```

The retriever is the concrete implementation of the "本地 RAG 知識庫 + 雙軌隔離 + 唯讀審查閘" steel guardrail described in the long 2026-06 evolution log. It prevents the Finviz DNA / FOM from being overfitted by future Aider or LLM automation.

See also: `rag-data/contracts/disclosures.json`, `scripts/rag_retriever.py`, `wiki/25_cross_tool_agent_orchestration.md`, previous `outputs/cross-review/`.
