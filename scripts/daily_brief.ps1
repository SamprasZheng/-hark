# scripts/daily_brief.ps1
# Generate the 游庭澔-style daily brief for ONE edition, as a cadence-correct CHAIN:
#   all editions : refresh free news RSS  (cheap; fills the 隔夜頭條 / 速解讀 slot)
#   evening       : refresh portfolio-audit DAILY (so 進出場建議 is fresh)
#                   refresh fom-alpha 潛力股 ONLY on the weekly day (Monday) --
#                   FOM is a 3-6m tilt, not a daily timer (per daily_routine philosophy)
#   then          : render the brief (MD + HTML + Discord)
# Local file generation only -- NO outbound post. ASCII-only per repo convention.
#
# Usage:
#   powershell -NoProfile -ExecutionPolicy Bypass -File scripts\daily_brief.ps1 -Edition morning
param(
    [ValidateSet("morning", "midday", "evening")]
    [string]$Edition = "morning"
)
$ErrorActionPreference = "Continue"   # a failed refresh step must not block the brief
$root = "D:\DOT\`$hark"
Set-Location $root
$env:PYTHONPATH = "src"
$py = ".venv\Scripts\python.exe"
if (-not (Test-Path $py)) { Write-Error "venv python not found: $py (run from $root)"; exit 1 }

# 1) news (all editions) -- best-effort; never fatal
& $py -m sharks.cli news-fetch

# 2) evening freshness chain: audit daily, FOM weekly (Monday only)
if ($Edition -eq "evening") {
    & $py -m sharks.backtest.portfolio_audit
    if ((Get-Date).DayOfWeek -eq "Monday") {
        Write-Output "[chain] weekly day -> refreshing FOM-alpha 潛力股"
        & $py -m sharks.scoring.fom_alpha
    } else {
        Write-Output "[chain] non-weekly day -> keeping last weekly FOM picks (FOM = 3-6m tilt)"
    }
}

# 3) render the brief
& $py -m sharks.cli daily-brief --edition $Edition
exit $LASTEXITCODE
