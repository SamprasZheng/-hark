# scripts/daily_routine.ps1
# Sharks unified daily/weekly routine — mature-analyst cadence.
#
#   DAILY  : 倉位健檢 (portfolio_audit + health-check). Recommend-only, default-hold.
#   WEEKLY : on the WEEKLY_DAY (default Monday) also run 選股建議 (FOM scan) +
#            the FOM predictive-validity IC re-check (recalibration heartbeat).
#   EARNINGS SEASON: flagged as an exception window where more attention/turnover
#            is acceptable (財報季波動大).
#
# Philosophy: 基本以周為單位，每日不過多操作. The daily pass is a health read; the
# real rebalancing thinking happens weekly, and only on 十足的證據.
#
# Schedule via Task Scheduler (or scripts/install_scheduled_tasks.ps1):
#   Trigger: Daily — pick a local time after the US close you care about.
#
# Does NOT auto-trade and does NOT auto-commit; it writes a digest to outputs/.

$ErrorActionPreference = "Continue"
$projectRoot = "D:\DOT\`$hark"
Set-Location $projectRoot
& '.\.venv\Scripts\Activate.ps1'

$today = Get-Date -Format "yyyy-MM-dd"
$dow   = (Get-Date).DayOfWeek            # Monday, Tuesday, ...
$month = (Get-Date).Month
$log   = Join-Path $projectRoot "outputs\daily_routine_$today.log"

# Weekly cadence + earnings-season windows (Jan/Apr/Jul/Oct = US reporting peaks)
$WEEKLY_DAY = "Monday"
$earningsSeason = @(1, 4, 7, 10) -contains $month
$isWeekly = ($dow -eq $WEEKLY_DAY)

function Log($msg) { Write-Output "[$(Get-Date -Format 'HH:mm:ss')] $msg" | Tee-Object -FilePath $log -Append }

Write-Output "=== Sharks daily routine $today ($dow) ===" | Tee-Object -FilePath $log
Log "weekly_pass=$isWeekly  earnings_season=$earningsSeason"

# ── DAILY: 倉位健檢 ──────────────────────────────────────────────────────────
Log "Portfolio audit (FOM + leveraged decay + concentration)..."
python -m sharks.backtest.portfolio_audit 2>&1 | Tee-Object -FilePath $log -Append

Log "Daily health-check (regime + funding + posture + hotspots)..."
python -m sharks.cli health-check 2>&1 | Tee-Object -FilePath $log -Append

Log "RF/PM/analog rush-order cycle (variable #15, two-door: leading vs handset)..."
python -m sharks.cli rf-cycle --as-of $today 2>&1 | Tee-Object -FilePath $log -Append

# ── WEEKLY: 選股建議 + FOM recalibration heartbeat ───────────────────────────
if ($isWeekly) {
    Log "WEEKLY: FOM universe scan (選股建議)..."
    python -m sharks.scoring.fom 2>&1 | Tee-Object -FilePath $log -Append

    Log "WEEKLY: FOM predictive-validity IC re-check (recalibration)..."
    python -m sharks.backtest.fom_validation_backtest 2>&1 | Tee-Object -FilePath $log -Append

    Log "WEEKLY: hotspot prediction (next-quarter sector leaders, seasonality-led)..."
    python -m sharks.backtest.hotspot_backtest 2>&1 | Tee-Object -FilePath $log -Append
} else {
    Log "Not the weekly day ($WEEKLY_DAY) — skipping FOM scan + IC re-check (不過多操作)."
}

if ($earningsSeason) {
    Log "NOTE: earnings season (財報季) — higher-volatility exception window; closer watch + larger evidence-backed turnover acceptable."
}

# ── WEEKEND (optional): crypto Top-100 tracker ───────────────────────────────
# Weekend is the crypto window (philosophy/07-mode-switch.md); posture is
# de-risk/observation-first. Uncomment to fold the daily crypto breadth snapshot
# into the routine (RECOMMEND-ONLY; writes crypto/data + crypto/analysis):
# Log "Crypto Top-100 tracker (breadth snapshot + structure)..."
# python -m sharks.scoring.crypto_top100 2>&1 | Tee-Object -FilePath $log -Append

# ── Digest ───────────────────────────────────────────────────────────────────
$digest = Join-Path $projectRoot "outputs\routine_digest_$today.md"
@"
# Sharks routine digest — $today ($dow)

- weekly_pass: $isWeekly   (weekly day = $WEEKLY_DAY)
- earnings_season: $earningsSeason
- posture / recommendations: outputs/daily-health-check-$today.json
- portfolio audit: outputs/portfolio-audit-$today.json
- RF/PM cycle (變數#15, leading vs handset door): outputs/rfpm-cycle-$today.json
$(if ($isWeekly) { "- FOM scan: outputs/fom-monthly-*.json`n- IC re-check: outputs/fom-validation-2016-to-2026.json (verdict + best horizon)" })

## Discipline reminder
- Default to HOLD. Offense needs 十足的證據 (>=4/5: 消息/資金/交易量/進出口/營利, incl. earnings + a primary).
- Defense may move fast on a systemic trigger (regime risk_off/capitulation OR funding STRESS/RUPTURE).
- FOM is a 3-6m TILT, not a daily timer (IC strongest at 6m; 1m ~noise). Do not judge picks on next-day moves.
- Leveraged ETFs are tactical only; trim worst-decay first. SBIT/UVXY/SQQQ are standby hedges (也怕大空頭), deploy on trigger.
"@ | Out-File -FilePath $digest -Encoding utf8

Log "Wrote digest: $digest"
Log "Done."
