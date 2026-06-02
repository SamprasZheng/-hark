# scripts/restart_bot.ps1
# One-click: stop any running Sharks Discord bot, then (re)start it via
# run_discord_bot.ps1 (which brings up local Ollama + installs deps + runs the bot),
# detached + hidden, logging to outputs\discord_bot.log. Safe to run anytime
# (idempotent) and at logon. Use this after changing .env or bot code.
# ASCII-only per repo convention.
$ErrorActionPreference = "Continue"
$root = "D:\DOT\`$hark"
Set-Location $root
$log = Join-Path $root "outputs\discord_bot.log"

# 1) stop any existing bot process (match the module on the command line)
Write-Output "Stopping any running Sharks Discord bot..."
Get-CimInstance Win32_Process -Filter "Name='python.exe'" |
    Where-Object { $_.CommandLine -and ($_.CommandLine -match 'sharks\.discord\.bot') } |
    ForEach-Object {
        try { Stop-Process -Id $_.ProcessId -Force; Write-Output "  stopped PID $($_.ProcessId)" } catch {}
    }
Start-Sleep -Seconds 1

# 2) (re)start via the existing runner (it brings up Ollama + deps), detached + logged
$run = Join-Path $root "scripts\run_discord_bot.ps1"
if (-not (Test-Path $run)) { Write-Error "not found: $run"; exit 1 }
Write-Output "Starting bot (Ollama + bot) detached; log -> $log"
# PYTHONUNBUFFERED so the bot's log (logged-in / errors) flushes live to the file.
$inner = "`$env:PYTHONUNBUFFERED='1'; & '$run' *> '$log'"
Start-Process -FilePath "powershell" -ArgumentList @(
    '-NoProfile', '-ExecutionPolicy', 'Bypass', '-WindowStyle', 'Hidden', '-Command', $inner
) -WorkingDirectory $root
Start-Sleep -Seconds 2
Write-Output "Done. Confirm with:  Get-Content '$log' -Tail 25"
