<#
.SYNOPSIS
  Batch the Grade-D X/KOL pull (grok-kol.ps1) over a candidate universe built from the
  quant systems' current outputs (finviz / rally / fom / serenity), consensus-ranked.

.DESCRIPTION
  scripts/grok-kol-batch.ps1 -- productionises the X/KOL overlay. Instead of brute-forcing
  the whole watchlist (100+ web-search Grok calls = expensive + slow + flaky), it pulls the
  UNION of names the quant stack already flagged, weights each by how many systems flag it
  (cross-system consensus), caps at -Max, and runs grok-kol.ps1 per ticker.

  This is the disciplined reading of "loop over the watchlist combined with
  finviz/rally/dipbuy/serenity/fom/stealth": those systems define WHICH names are worth a
  Grade-D sentiment overlay. KOL output stays observation-only -- it never triggers or sizes
  a position (CLAUDE.md section 5).

  Sources (machine-readable, newest dated file auto-picked):
    finviz   outputs/finviz-scan-*.json        .buy_consider[]
    rally    outputs/rally-state-*.jsonl        per-line .ticker where .buy_consider
    fom      outputs/fom-monthly-*.json         .ranked_full[].ticker  (top -FomTopN)
    serenity outputs/serenity-scout-*.json      .top_15_with_staging_bonus[].ticker
    dipbuy   watchlist/thesis_dipbuy.yaml       (regex ticker extract; theme adder)
    watchlist watchlist/universe.yaml           (regex ticker extract; broad)
  Crypto mode (-Crypto): crypto/data/top100-*.json .coins[].symbol (top -CryptoTopN).
  stealth is NOT a source: it ranks basecross candidates in-memory and emits no list.

.PARAMETER Max         Cap on tickers to pull (cost control). Default 12.
.PARAMETER Sources     Which equity sources to union. Default finviz,rally,fom,serenity.
.PARAMETER MinConsensus Only pull tickers flagged by >= N sources. Default 1.
.PARAMETER FomTopN     How many FOM ranked names to take. Default 20.
.PARAMETER Crypto      Build the universe from crypto top100 instead of equity sources.
.PARAMETER CryptoTopN  Crypto symbols to take (by mcap rank). Default 10.
.PARAMETER Effort      grok-kol reasoning effort. Default high.
.PARAMETER MaxTurns    grok-kol max turns. Default 16.
.PARAMETER ListOnly    Print the assembled universe and exit (FREE -- no Grok calls).
.PARAMETER DryRun      Pass -DryRun to grok-kol (no raw/ writes); still spends Grok credits.

.EXAMPLE
  .\scripts\grok-kol-batch.ps1 -ListOnly
  .\scripts\grok-kol-batch.ps1 -Max 8 -MinConsensus 1
  .\scripts\grok-kol-batch.ps1 -Sources finviz,rally,fom,serenity,dipbuy -Max 15
  .\scripts\grok-kol-batch.ps1 -Crypto -CryptoTopN 8
#>
[CmdletBinding()]
param(
    [int]$Max = 12,
    [string[]]$Sources = @("finviz", "rally", "fom", "serenity"),
    [int]$MinConsensus = 1,
    [int]$FomTopN = 20,
    [switch]$Crypto,
    [int]$CryptoTopN = 10,
    [string]$Effort = "high",
    [int]$MaxTurns = 16,
    [switch]$ListOnly,
    [switch]$DryRun
)

$ErrorActionPreference = "Continue"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8   # cp950 box

$repoRoot = Split-Path $PSScriptRoot -Parent
$now      = Get-Date
$stamp    = $now.ToString("yyyy-MM-dd-HHmmss")
$date     = $now.ToString("yyyy-MM-dd")

# --- helpers ---------------------------------------------------------------
function Get-Newest([string]$pattern) {
    $hits = Get-ChildItem -Path (Join-Path $repoRoot $pattern) -ErrorAction SilentlyContinue |
        Sort-Object Name -Descending
    if ($hits) { return $hits[0].FullName }
    return $null
}

function Read-Json([string]$path) {
    return (Get-Content -LiteralPath $path -Raw -Encoding UTF8 | ConvertFrom-Json)
}

function Get-YamlTickers([string]$path) {
    $txt = Get-Content -LiteralPath $path -Raw -Encoding UTF8
    $out = New-Object System.Collections.Generic.List[string]
    foreach ($m in [regex]::Matches($txt, '\[([^\]]*)\]')) {
        foreach ($tok in ($m.Groups[1].Value -split ',')) {
            $c = $tok.Trim().Trim('"').Trim("'")
            if ($c -match '^[A-Z][A-Z0-9.\-]{0,6}$') { $out.Add($c) }
        }
    }
    foreach ($m in [regex]::Matches($txt, '(?m)^\s*-\s*([A-Z][A-Z0-9.\-]{0,6})\s*$')) {
        $out.Add($m.Groups[1].Value.Trim())
    }
    return $out
}

function Get-SummaryLine([string]$path) {
    if (-not (Test-Path -LiteralPath $path)) { return "" }
    $lines = Get-Content -LiteralPath $path -Encoding UTF8
    $start = -1
    for ($k = 0; $k -lt $lines.Count; $k++) { if ($lines[$k] -match '^\s*##\s+Summary') { $start = $k + 1; break } }
    if ($start -lt 0) { return "" }
    $buf = @()
    for ($j = $start; $j -lt $lines.Count; $j++) {
        if ($lines[$j] -match '^\s*##\s') { break }
        if ($lines[$j].Trim()) { $buf += $lines[$j].Trim() }
    }
    $s = ($buf -join ' ')
    if ($s.Length -gt 240) { $s = $s.Substring(0, 240) + '...' }
    return $s
}

# --- assemble candidate universe -------------------------------------------
$flag = @{}   # TICKER -> List[string] of sources
function Add-Ticker([string]$t, [string]$src) {
    if ([string]::IsNullOrWhiteSpace($t)) { return }
    $key = $t.Trim().ToUpper()
    if (-not $flag.ContainsKey($key)) { $flag[$key] = New-Object System.Collections.Generic.List[string] }
    if (-not $flag[$key].Contains($src)) { $flag[$key].Add($src) }
}

$mode = ($Sources -join "+")
if ($Crypto) {
    $mode = "crypto-top100"
    $f = Get-Newest "crypto\data\top100-*.json"
    if (-not $f) { throw "No crypto/data/top100-*.json found." }
    Write-Host "[batch] crypto universe <- $f"
    (Read-Json $f).coins | Select-Object -First $CryptoTopN | ForEach-Object { Add-Ticker $_.symbol "crypto-top100" }
}
else {
    foreach ($s in $Sources) {
        switch ($s.ToLower()) {
            "finviz" {
                $f = Get-Newest "outputs\finviz-scan-*.json"
                if ($f) { Write-Host "[batch] finviz   <- $f"; (Read-Json $f).buy_consider | ForEach-Object { Add-Ticker $_ "finviz" } }
                else { Write-Host "[batch] finviz   (no file)" -ForegroundColor DarkYellow }
            }
            "rally" {
                $f = Get-Newest "outputs\rally-state-*.jsonl"
                if ($f) {
                    Write-Host "[batch] rally    <- $f"
                    Get-Content -LiteralPath $f -Encoding UTF8 | ForEach-Object {
                        if ($_.Trim()) { $o = $_ | ConvertFrom-Json; if ($o.buy_consider) { Add-Ticker $o.ticker "rally" } }
                    }
                }
                else { Write-Host "[batch] rally    (no file)" -ForegroundColor DarkYellow }
            }
            "fom" {
                $f = Get-Newest "outputs\fom-monthly-*.json"
                if ($f) { Write-Host "[batch] fom      <- $f"; (Read-Json $f).ranked_full | Select-Object -First $FomTopN | ForEach-Object { Add-Ticker $_.ticker "fom" } }
                else { Write-Host "[batch] fom      (no file)" -ForegroundColor DarkYellow }
            }
            "serenity" {
                $f = Get-Newest "outputs\serenity-scout-*.json"
                if ($f) { Write-Host "[batch] serenity <- $f"; (Read-Json $f).top_15_with_staging_bonus | ForEach-Object { Add-Ticker $_.ticker "serenity" } }
                else { Write-Host "[batch] serenity (no file)" -ForegroundColor DarkYellow }
            }
            "dipbuy" {
                $f = Join-Path $repoRoot "watchlist\thesis_dipbuy.yaml"
                if (Test-Path -LiteralPath $f) { Write-Host "[batch] dipbuy   <- $f"; Get-YamlTickers $f | ForEach-Object { Add-Ticker $_ "dipbuy" } }
                else { Write-Host "[batch] dipbuy   (no watchlist/thesis_dipbuy.yaml)" -ForegroundColor DarkYellow }
            }
            "watchlist" {
                $f = Join-Path $repoRoot "watchlist\universe.yaml"
                if (Test-Path -LiteralPath $f) { Write-Host "[batch] watchlist<- $f"; Get-YamlTickers $f | ForEach-Object { Add-Ticker $_ "watchlist" } }
                else { Write-Host "[batch] watchlist (no watchlist/universe.yaml)" -ForegroundColor DarkYellow }
            }
            default { Write-Host "[batch] unknown source '$s' (skipped)" -ForegroundColor DarkYellow }
        }
    }
}

$ranked = $flag.GetEnumerator() |
    ForEach-Object { [pscustomobject]@{ Ticker = $_.Key; Consensus = $_.Value.Count; Sources = ($_.Value -join "+") } } |
    Where-Object { $_.Consensus -ge $MinConsensus } |
    Sort-Object @{ Expression = { $_.Consensus }; Descending = $true }, Ticker
$universe = @($ranked | Select-Object -First $Max)

Write-Host ""
Write-Host "[batch] mode=$mode  candidates=$($ranked.Count)  selected=$($universe.Count) (cap $Max, min-consensus $MinConsensus)"
($universe | Format-Table Ticker, Consensus, Sources -AutoSize | Out-String).TrimEnd() | Write-Host
Write-Host ""

if ($universe.Count -eq 0) { Write-Host "[batch] nothing to pull. Check that the source files exist for today." -ForegroundColor Yellow; return }
if ($ListOnly) { Write-Host "[batch] -ListOnly: no Grok calls made (free)." -ForegroundColor Green; return }

# --- cost gate -------------------------------------------------------------
Write-Host "[batch] about to make up to $($universe.Count) Grok web-search pulls (spends credits). Ctrl+C to abort..." -ForegroundColor Cyan
Start-Sleep -Seconds 3

# --- run per-ticker --------------------------------------------------------
$grokKol = Join-Path $PSScriptRoot "grok-kol.ps1"
$rows = @()
$n = 0
foreach ($u in $universe) {
    $n++
    Write-Host ""
    Write-Host ("=" * 78)
    Write-Host "[batch $n/$($universe.Count)] $($u.Ticker)  (sources: $($u.Sources))"
    $status = "ok"; $capRel = ""; $summary = ""
    try {
        $kolArgs = @{ Topic = $u.Ticker; Effort = $Effort; MaxTurns = $MaxTurns }
        if ($DryRun) { $kolArgs['DryRun'] = $true }
        & $grokKol @kolArgs | Out-Null
        if (-not $DryRun) {
            $slug = ($u.Ticker.ToLower() -replace '[^a-z0-9]+', '-').Trim('-')
            $cap = Join-Path $repoRoot "raw\kol_signals\x-kol-$slug-$date.md"
            if (Test-Path -LiteralPath $cap) {
                $capRel = "raw/kol_signals/x-kol-$slug-$date.md"
                $summary = Get-SummaryLine $cap
            }
            else { $status = "no-capture" }
        }
    }
    catch {
        $status = "failed: $($_.Exception.Message -replace '\s+', ' ')"
        Write-Host "[batch] $($u.Ticker) failed: $status" -ForegroundColor Red
    }
    $rows += [pscustomobject]@{ Ticker = $u.Ticker; Sources = $u.Sources; Status = $status; Capture = $capRel; Summary = $summary }
}

# --- digest ----------------------------------------------------------------
if (-not $DryRun) {
    $digestWin = Join-Path $repoRoot "outputs\kol-batch-$date.md"
    $d = "# KOL batch digest -- $date`n`n"
    $d += "- generated: $stamp (local)`n"
    $d += "- mode: $mode | universe: $($universe.Count) (cap $Max, min-consensus $MinConsensus)`n"
    $d += "- Grade D / observation only -- NEVER a position trigger (CLAUDE.md section 5). Captures live in raw/kol_signals/.`n`n"
    $d += "| ticker | flagged by | status | sentiment summary | capture |`n|---|---|---|---|---|`n"
    foreach ($r in $rows) {
        $sm = ($r.Summary -replace '\|', '/')
        $cap = if ($r.Capture) { "[capture]($($r.Capture))" } else { "-" }
        $d += "| $($r.Ticker) | $($r.Sources) | $($r.Status) | $sm | $cap |`n"
    }
    [System.IO.File]::WriteAllText($digestWin, $d, (New-Object System.Text.UTF8Encoding($false)))
    Write-Host ""
    Write-Host ("=" * 78)
    Write-Host "[batch] digest saved: $digestWin" -ForegroundColor Green
    Write-Host "[batch] $($rows.Count) tickers; captures in raw/kol_signals/ (Grade D, uncommitted, observation-only)."
}
else {
    Write-Host ""
    Write-Host "[batch] DRY RUN complete -- no captures or digest written."
}
