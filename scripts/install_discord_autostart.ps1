# scripts/install_discord_autostart.ps1
# Register the Sharks Discord bot to start at LOG ON (USER scope — no admin).
# Idempotent. Once registered, the bot:
#   - listens on channels (#問claude, #分析師議會) 24/7 while you're logged in
#   - fires 晨會 07:30 / 午會 13:00 / 晚會 22:30 (TPE) on its internal scheduler
# It boots local Ollama first (scripts/check_ollama.ps1) so the council + persona
# chat have the local model available.
#
# Usage (ordinary PowerShell — no admin):
#   powershell -NoProfile -ExecutionPolicy Bypass -File scripts\install_discord_autostart.ps1
#   schtasks /Run /TN SharksDiscordBot     # start immediately
#   schtasks /Delete /TN SharksDiscordBot /F   # remove

param([string]$TaskName = "SharksDiscordBot")

$ErrorActionPreference = "Stop"
$projectRoot = "D:\DOT\`$hark"
$script = Join-Path $projectRoot "scripts\run_discord_bot.ps1"

if (-not (Test-Path $script)) {
    Write-Error "Bot run script not found: $script"
    exit 1
}

$action = "powershell -NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File `"$script`""

Write-Output "Registering '$TaskName' to start the Discord bot at log on ..."
try { schtasks /Delete /TN $TaskName /F 2>$null } catch {}
schtasks /Create /TN $TaskName /TR $action /SC ONLOGON /RL LIMITED /F

if ($LASTEXITCODE -eq 0) {
    Write-Output "OK. '$TaskName' registered (starts at next log on)."
    Write-Output "Start now:  schtasks /Run /TN $TaskName"
    Write-Output "Status:     schtasks /Query /TN $TaskName /V /FO LIST"
    Write-Output "Remove:     schtasks /Delete /TN $TaskName /F"
} else {
    Write-Error "schtasks /Create failed (exit $LASTEXITCODE)."
}
