# scripts/daily_brief.ps1
# Generate the analyst-style (Yu Ting-hao) daily brief for ONE edition, as a
# cadence-correct CHAIN:
#   all editions : refresh free news RSS  (cheap; fills the overnight-headlines / quick-read slot)
#   evening      : refresh portfolio-audit DAILY (so the entry/exit picks are fresh)
#                  refresh fom-alpha picks ONLY on the weekly day (Monday) --
#                  FOM is a 3-6m tilt, not a daily timer (per daily_routine philosophy)
#   then         : render the brief (MD + HTML + Discord)
# Local file generation only -- NO outbound post.
#
# ASCII-ONLY per repo convention: PowerShell 5.1 (Task Scheduler default) reads a
# UTF-8 file as the system ANSI codepage and MIS-PARSES inline non-ASCII -- a CJK
# byte in a double-quoted string can swallow the closing quote and break the whole
# script. Keep every byte ASCII here; CJK lives in the Python layer, not this shim.
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
        Write-Output "[chain] weekly day -> refreshing FOM-alpha picks"
        & $py -m sharks.scoring.fom_alpha
    } else {
        Write-Output "[chain] non-weekly day -> keeping last weekly FOM picks (FOM = 3-6m tilt)"
    }
}

# 3) render the brief
& $py -m sharks.cli daily-brief --edition $Edition
exit $LASTEXITCODE
