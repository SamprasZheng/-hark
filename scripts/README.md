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

The daily scripts **stage TODO files** for the human's next chat session with the Compiler agent. The system does NOT autonomously scrape news (Phase 2 will add this via Finnhub + RSS). Until then, the human + Compiler agent process each day's TODO file manually each session.

This is **the deliberate slow-loop design** — automation handles quant; humans + LLM handle qualitative news synthesis. Per [[../CLAUDE]] §2 SAFETY boundaries, the system never auto-trades.
