# scripts/install_autostart.ps1
# Boot autostart (NO admin) for the whole local stack: on every logon, run
# restart_bot.ps1 which brings up local Ollama + the Discord bot. The bot then fires
# 晨/午/晚會 + the hourly #雜談 速解讀 on its own internal TPE schedule.
#
# The daily BRIEF (早/午/晚報) and portfolio AUDIT run as separate Windows Scheduled
# Tasks (install_brief_schedule.ps1 / install_scheduled_tasks.ps1) -- Task Scheduler
# survives reboots on its own, so those need no autostart entry.
#
# Run it yourself (ordinary PowerShell, no admin):
#   powershell -NoProfile -ExecutionPolicy Bypass -File 'D:\DOT\$hark\scripts\install_autostart.ps1'
#
# Remove later: delete the Startup .cmd printed below.
param([switch]$NoStartNow)
$ErrorActionPreference = "Stop"
$root = "D:\DOT\`$hark"
$restart = Join-Path $root "scripts\restart_bot.ps1"
if (-not (Test-Path $restart)) { Write-Error "not found: $restart"; exit 1 }

$startup = [Environment]::GetFolderPath('Startup')
$cmdPath = Join-Path $startup "SharksDiscordBot.cmd"   # same name -> supersedes the old run-only entry (no double bot)
$line = 'start "" /min powershell -NoProfile -ExecutionPolicy Bypass -File "' + $restart + '"'
Set-Content -Path $cmdPath -Value "@echo off`r`n$line" -Encoding ascii
Write-Output "Autostart written: $cmdPath"
Write-Output "  -> runs restart_bot.ps1 (Ollama + bot) at every logon."

if (-not $NoStartNow) {
    Write-Output "Starting the stack now..."
    & $restart
}
Write-Output ""
Write-Output "Scheduled tasks already cover the rest (survive reboot on their own):"
Write-Output "  brief : SharksBriefMorning/Midday/Evening  (07:30 / 13:00 / 21:00)"
Write-Output "  audit : SharksDailyRoutine"
Write-Output "Remove autostart with:  Remove-Item `"$cmdPath`""
