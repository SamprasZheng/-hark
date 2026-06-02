# scripts/daily_pm.ps1
# Sharks daily PM run (post-market US close / evening TPE time)
#
# Schedule via Task Scheduler:
#   Trigger: Daily at 22:00 local time (post US close)
#
# Tasks:
#   1. Re-run FOM with end-of-day data
#   2. Update persistence_state.json
#   3. Commit to git if there are changes
#   4. Generate evening summary

$ErrorActionPreference = "Continue"
$projectRoot = "D:\DOT\`$hark"
Set-Location $projectRoot
& '.\.venv\Scripts\Activate.ps1'

$today = Get-Date -Format "yyyy-MM-dd"
$pmLog = Join-Path $projectRoot "outputs\daily_pm_$today.log"

Write-Output "=== Sharks daily PM run $today ===" | Tee-Object -FilePath $pmLog
Write-Output "" | Tee-Object -FilePath $pmLog -Append

# Step 1: Re-run FOM with EOD data
Write-Output "[$(Get-Date -Format 'HH:mm:ss')] FOM EOD scoring..." | Tee-Object -FilePath $pmLog -Append
python -m sharks.scoring.fom 2>&1 | Tee-Object -FilePath $pmLog -Append

# Step 2: Git commit if changes
Write-Output "" | Tee-Object -FilePath $pmLog -Append
Write-Output "[$(Get-Date -Format 'HH:mm:ss')] Git status..." | Tee-Object -FilePath $pmLog -Append
git status --porcelain | Tee-Object -FilePath $pmLog -Append
$changes = git status --porcelain
if ($changes) {
    git add outputs/ data/persistence_state.json wiki/05_recommendations/
    git commit -m "auto: daily PM FOM update $today

Co-Authored-By: Sharks daily run"
    Write-Output "[$(Get-Date -Format 'HH:mm:ss')] Committed changes." | Tee-Object -FilePath $pmLog -Append
} else {
    Write-Output "[$(Get-Date -Format 'HH:mm:ss')] No changes to commit." | Tee-Object -FilePath $pmLog -Append
}

# Step 3: Evening summary — TODO for next chat session
$summaryPath = Join-Path $projectRoot "outputs\evening_summary_$today.md"
@"
# Daily PM summary — $today

## What changed today (EOD)
- FOM re-ranked: see outputs/fom-v2-monthly-$today.json
- Persistence state updated: data/persistence_state.json
- Git committed: auto commit if changes detected

## Tomorrow's AM agenda
- Pre-market news scan via Compiler agent
- Trump policy / Mag 7 earnings preview
- Macro calendar check (Fed / CPI / NFP days within 5 days)

## This week's high-conviction picks
See: most recent outputs/fom-v2-monthly-*.json top_3_picks section

## Open postmortem items
See: wiki/09_postmortem_log.md
"@ | Out-File -FilePath $summaryPath -Encoding utf8

Write-Output "[$(Get-Date -Format 'HH:mm:ss')] Wrote evening summary: $summaryPath" | Tee-Object -FilePath $pmLog -Append
Write-Output "Done." | Tee-Object -FilePath $pmLog -Append
