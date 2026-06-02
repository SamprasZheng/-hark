# scripts/crypto_top100.ps1
# Sharks crypto Marketcap Top-100 tracker — daily breadth snapshot + structure analysis.
#
# Mirrors scripts/daily_am.ps1 (venv activate + Tee logging). RECOMMEND-ONLY; does NOT
# auto-trade and does NOT auto-commit. Writes:
#   crypto/data/top100-<DATE>.json   (immutable raw snapshot)
#   crypto/analysis/top100-<DATE>.md (human structure analysis)
#   outputs/crypto-top100-<DATE>.json (machine handoff)
#
# Schedule via Task Scheduler (or scripts/install_scheduled_tasks.ps1) if wanted — NOT
# auto-registered by default. Weekend is the natural crypto window
# (philosophy/07-mode-switch.md).
#
#   Program:   powershell.exe
#   Arguments: -NoProfile -ExecutionPolicy Bypass -File "D:\DOT\$hark\scripts\crypto_top100.ps1"

$ErrorActionPreference = "Continue"
$projectRoot = "D:\DOT\`$hark"
Set-Location $projectRoot
& '.\.venv\Scripts\Activate.ps1'

$today = Get-Date -Format "yyyy-MM-dd"
$log = Join-Path $projectRoot "outputs\crypto_top100_$today.log"

Write-Output "=== Sharks crypto Top-100 tracker $today ===" | Tee-Object -FilePath $log
Write-Output "[$(Get-Date -Format 'HH:mm:ss')] CoinGecko snapshot + structure analysis..." | Tee-Object -FilePath $log -Append
python -m sharks.scoring.crypto_top100 2>&1 | Tee-Object -FilePath $log -Append
Write-Output "[$(Get-Date -Format 'HH:mm:ss')] Done. (RECOMMEND-ONLY; de-risk/observation-first)" | Tee-Object -FilePath $log -Append
