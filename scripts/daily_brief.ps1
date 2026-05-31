# scripts/daily_brief.ps1
# Generate the 游庭澔-style daily brief for ONE edition (morning/midday/evening).
# Local file generation only (MD + HTML + Discord txt under outputs/). No outbound post.
# ASCII-only per repo convention; routes through the venv python.
#
# Usage:
#   powershell -NoProfile -ExecutionPolicy Bypass -File scripts\daily_brief.ps1 -Edition morning
param(
    [ValidateSet("morning", "midday", "evening")]
    [string]$Edition = "morning"
)
$ErrorActionPreference = "Stop"
$root = "D:\DOT\`$hark"
Set-Location $root
$env:PYTHONPATH = "src"
$py = ".venv\Scripts\python.exe"
if (-not (Test-Path $py)) { Write-Error "venv python not found: $py (run from $root)"; exit 1 }
& $py -m sharks.cli daily-brief --edition $Edition
exit $LASTEXITCODE
