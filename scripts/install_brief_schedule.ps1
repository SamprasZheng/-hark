# scripts/install_brief_schedule.ps1
# Register THREE daily 游庭澔-style brief tasks (morning / midday / evening) with the
# Windows Task Scheduler, USER scope (no admin). Idempotent: deletes any prior task of
# the same name first. Local file generation only -- NO outbound Discord/social post.
#
# Times are LOCAL (Taipei). Defaults reflect the US-market clock:
#   morning 07:30  - reflects last night's US close (the classic morning brief, pre TW open)
#   midday  13:00  - intraday / around TW close
#   evening 21:00  - as the US session opens (actionable picks for the US day ahead)
#
# Usage:
#   powershell -NoProfile -ExecutionPolicy Bypass -File scripts\install_brief_schedule.ps1
#   # optional: -MorningAt 07:00 -MiddayAt 12:30 -EveningAt 21:30
param(
    [string]$MorningAt = "07:30",
    [string]$MiddayAt  = "13:00",
    [string]$EveningAt = "21:00"
)
$ErrorActionPreference = "Stop"
$root = "D:\DOT\`$hark"
$script = Join-Path $root "scripts\daily_brief.ps1"
if (-not (Test-Path $script)) { Write-Error "Runner not found: $script"; exit 1 }

$editions = @(
    @{ Name = "SharksBriefMorning"; Ed = "morning"; At = $MorningAt },
    @{ Name = "SharksBriefMidday";  Ed = "midday";  At = $MiddayAt },
    @{ Name = "SharksBriefEvening"; Ed = "evening"; At = $EveningAt }
)

foreach ($e in $editions) {
    $action = "powershell -NoProfile -ExecutionPolicy Bypass -File `"$script`" -Edition $($e.Ed)"
    try { schtasks /Delete /TN $($e.Name) /F 2>$null } catch {}
    schtasks /Create /TN $($e.Name) /TR $action /SC DAILY /ST $($e.At) /F | Out-Null
    if ($LASTEXITCODE -eq 0) {
        Write-Output ("OK  {0,-20} @ {1}  ({2})" -f $e.Name, $e.At, $e.Ed)
    } else {
        Write-Error "Failed to register $($e.Name) (exit $LASTEXITCODE)"
    }
}
Write-Output ""
Write-Output "Query : schtasks /Query /TN SharksBriefEvening /V /FO LIST"
Write-Output "Test  : schtasks /Run   /TN SharksBriefEvening"
Write-Output "Remove: schtasks /Delete /TN SharksBriefMorning /F  (and Midday/Evening)"
