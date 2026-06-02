# scripts/install_discord_autostart.ps1
# Persist the Sharks Discord bot at logon WITHOUT admin, via the user's Startup
# folder. (schtasks /SC ONLOGON needs elevation on this machine — "Access is
# denied" — so we use the Startup folder, which any user can write.)
#
# Run it YOURSELF (ordinary PowerShell, no admin):
#   powershell -NoProfile -ExecutionPolicy Bypass -File 'D:\DOT\$hark\scripts\install_discord_autostart.ps1'
#
# It writes a .cmd to your Startup folder (runs run_discord_bot.ps1 minimized at
# every logon) and starts the bot now. The bot boots local Ollama first, then
# listens on channels + fires 晨會/午會/晚會 on its internal TPE scheduler.
#
# Remove later: delete  %APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\SharksDiscordBot.cmd

param([switch]$NoStartNow)

$ErrorActionPreference = "Stop"
$projectRoot = "D:\DOT\`$hark"
$runScript = Join-Path $projectRoot "scripts\run_discord_bot.ps1"
if (-not (Test-Path $runScript)) { Write-Error "Bot run script not found: $runScript"; exit 1 }

$startup = [Environment]::GetFolderPath('Startup')
$cmdPath = Join-Path $startup "SharksDiscordBot.cmd"
$line = 'start "" /min powershell -NoProfile -ExecutionPolicy Bypass -File "' + $runScript + '"'
Set-Content -Path $cmdPath -Value "@echo off`r`n$line" -Encoding ascii
Write-Output "Autostart entry written: $cmdPath  (runs at every logon)"

if (-not $NoStartNow) {
    Start-Process -FilePath "powershell" -ArgumentList @(
        '-NoProfile', '-ExecutionPolicy', 'Bypass', '-WindowStyle', 'Hidden', '-File', $runScript
    ) -WorkingDirectory $projectRoot
    Write-Output "Bot started now (detached, minimized)."
}
Write-Output "Remove with:  Remove-Item `"$cmdPath`""
