# scripts/daily_am.ps1
# Sharks daily AM run (pre-market US time / morning TPE time)
#
# Schedule via Task Scheduler:
#   Action: Start a program
#   Program: powershell.exe
#   Arguments: -NoProfile -ExecutionPolicy Bypass -File "D:\DOT\$hark\scripts\daily_am.ps1"
#   Trigger: Daily at 06:00 local time
#
# Tasks:
#   1. Pull latest macro news (delegated to Compiler agent on next chat session — for now logs the date)
#   2. Re-run FOM (refreshes top-50 and persistence)
#   3. Append to daily output ledger

$ErrorActionPreference = "Continue"
$projectRoot = "D:\DOT\`$hark"
Set-Location $projectRoot
& '.\.venv\Scripts\Activate.ps1'

$today = Get-Date -Format "yyyy-MM-dd"
$amLog = Join-Path $projectRoot "outputs\daily_am_$today.log"

Write-Output "=== Sharks daily AM run $today ===" | Tee-Object -FilePath $amLog
Write-Output "" | Tee-Object -FilePath $amLog -Append

# Step 1: Re-run FOM
Write-Output "[$(Get-Date -Format 'HH:mm:ss')] FOM scoring..." | Tee-Object -FilePath $amLog -Append
python -m sharks.scoring.fom 2>&1 | Tee-Object -FilePath $amLog -Append

# Step 2: Stage daily macro-check todo (Compiler agent picks up on next session)
$todoPath = Join-Path $projectRoot "outputs\daily_todo_$today.md"
@"
# Daily AM TODO — $today

## Compiler agent: please process these on next session

### Macro news to check
- [ ] Trump Truth Social posts (last 24h)
- [ ] Fed officials' speeches (last 24h, Powell + Warsh especially)
- [ ] CPI / NFP / FOMC if today
- [ ] Iran / Taiwan geopolitical updates
- [ ] Mag 7 pre-market earnings preannouncements

### AI industry dynamics
- [ ] NVDA / TSM / Mag 7 hyperscaler capex commentary
- [ ] Supply-chain bottleneck status (CoWoS / HBM allocation news)
- [ ] AI regulation (EU AI Act / US export controls)

### KOL aggregation (Grade C/D)
- [ ] Serenity (@aleabitoreddit) — new posts
- [ ] TheValueist (@TheValueist) — Serenity follower endorsements
- [ ] Other tracked Macro KOLs

### Action items if triggered
- VIX > 30 → enable Buffett "fearful → greedy" boost
- SPX -10% drawdown → activate cycle-resonance trigger + Nov candidates
- Mag 7 earnings within 3 days → tier 1/2 sizing reduce 30%

### Today's FOM top-3 picks
See: outputs/fom-v2-monthly-$today.json (just generated)
"@ | Out-File -FilePath $todoPath -Encoding utf8

Write-Output "[$(Get-Date -Format 'HH:mm:ss')] Wrote daily TODO: $todoPath" | Tee-Object -FilePath $amLog -Append
Write-Output "Done." | Tee-Object -FilePath $amLog -Append
