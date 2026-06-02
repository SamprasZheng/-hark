# scripts/install_scheduled_tasks.ps1
# Register the Sharks daily routine with Windows Task Scheduler (USER scope — no
# admin needed). Idempotent: deletes any prior task of the same name first.
#
# Usage (from an ordinary PowerShell prompt):
#   powershell -NoProfile -ExecutionPolicy Bypass -File scripts\install_scheduled_tasks.ps1
#   # optional: -At "09:30"  to change the run time (local)
param(
    [string]$At = "09:30",          # local time to run the daily routine
    [string]$TaskName = "SharksDailyRoutine"
)

$ErrorActionPreference = "Stop"
$projectRoot = "D:\DOT\`$hark"
$script = Join-Path $projectRoot "scripts\daily_routine.ps1"

if (-not (Test-Path $script)) {
    Write-Error "Routine script not found: $script"
    exit 1
}

$action  = "powershell -NoProfile -ExecutionPolicy Bypass -File `"$script`""

Write-Output "Registering scheduled task '$TaskName' to run daily at $At ..."
Write-Output "  command: $action"

# Remove any existing task with this name (ignore error if absent).
try { schtasks /Delete /TN $TaskName /F 2>$null } catch {}

# /SC DAILY user task; runs whether or not the user is logged on requires a
# password, so we use the default (runs only when logged on) for a no-admin setup.
schtasks /Create /TN $TaskName /TR $action /SC DAILY /ST $At /F

if ($LASTEXITCODE -eq 0) {
    Write-Output "OK. Task '$TaskName' registered. Inspect with:  schtasks /Query /TN $TaskName /V /FO LIST"
    Write-Output "Run once now to test:  schtasks /Run /TN $TaskName"
    Write-Output "Remove with:           schtasks /Delete /TN $TaskName /F"
} else {
    Write-Error "schtasks /Create failed (exit $LASTEXITCODE)."
}
