# scripts/install_dna_schedule.ps1
# Register the TWO daily DNA routine tasks (SharksDNA-Morning / SharksDNA-PreOpen) with the
# Windows Task Scheduler, USER scope (no admin). Idempotent: deletes prior task of the same
# name first. Mirrors the ad-hoc tasks registered 2026-06-12 so the schedule is repo-tracked
# and reproducible (CLAUDE.md audit discipline). recommend-only -- the routine never trades.
#
# What runs (see src/sharks/daily_dna_routine.py):
#   morning 07:40 TUE-SAT (Taipei; hours after US close, EOD bars complete):
#     lake refresh -> ma-scan -> reflexivity -> world-monitor -> rally_dna -> failed-analogs
#     + gated steps: ABM supply-chain sim (Tue = after US Mon), case-store sync (daily),
#       world threshold recalibration suggestion (1st of month)
#   preopen 21:10 MON-FRI (Taipei; ~20 min before US open):
#     compose position brief -> outputs/position-brief-<date>.md
#
# Usage:
#   powershell -NoProfile -ExecutionPolicy Bypass -File scripts\install_dna_schedule.ps1
#   # optional: -MorningAt 07:40 -PreopenAt 21:10
param(
    [string]$MorningAt = "07:40",
    [string]$PreopenAt = "21:10"
)
$ErrorActionPreference = "Stop"
$root = "D:\DOT\`$hark"
$py = Join-Path $root ".venv\Scripts\python.exe"
if (-not (Test-Path $py)) { Write-Error "venv python not found: $py"; exit 1 }

$tasks = @(
    @{ Name = "SharksDNA-Morning"; Mode = "morning"; At = $MorningAt; Days = "TUE,WED,THU,FRI,SAT" },
    @{ Name = "SharksDNA-PreOpen"; Mode = "preopen"; At = $PreopenAt; Days = "MON,TUE,WED,THU,FRI" }
)

foreach ($t in $tasks) {
    # cmd /c cd /d 避開路徑中的 $ 符號問題;console 輸出附掛到 routine log
    $action = "cmd /c cd /d $root && .venv\Scripts\python.exe -m sharks.daily_dna_routine $($t.Mode) >> outputs\dna-routine-console.log 2>&1"
    try { schtasks /Delete /TN $($t.Name) /F 2>$null } catch {}
    schtasks /Create /TN $($t.Name) /TR $action /SC WEEKLY /D $($t.Days) /ST $($t.At) /F | Out-Null
    if ($LASTEXITCODE -eq 0) {
        Write-Output ("OK  {0,-20} @ {1} {2}  ({3})" -f $t.Name, $t.At, $t.Days, $t.Mode)
    } else {
        Write-Error "Failed to register $($t.Name) (exit $LASTEXITCODE)"
    }
}
Write-Output ""
Write-Output "Query : schtasks /Query /TN SharksDNA-Morning /V /FO LIST"
Write-Output "Test  : schtasks /Run   /TN SharksDNA-Morning"
Write-Output "Remove: schtasks /Delete /TN SharksDNA-Morning /F  (and SharksDNA-PreOpen)"
