<#
.SYNOPSIS
  Pull recent X (Twitter) / KOL social signals on a topic via Grok (headless), as a
  Grade-D raw capture. Observation-only -- NEVER a position trigger.

.DESCRIPTION
  scripts/grok-kol.ps1 -- the Researcher-role Grok integration for the Sharks project.
  Grok Build (xAI) can read X directly, where plain WebFetch gets HTTP 402. This script
  uses that: it runs Grok headless WITH web/X search ON, asks for recent KOL chatter on a
  topic, and writes the result as an immutable raw capture under raw/kol_signals/ with the
  project's standard frontmatter (source_grade: D, source_first_visible_at, ingested_at).

  HARD DISCIPLINE (CLAUDE.md section 5 + sharks constitution):
    - The output is Grade D (social / KOL / sentiment). It can inform a WATCHLIST but never
      opens or sizes a position on its own. The frontmatter + banner state this.
    - Grok is told not to invent handles/posts/dates; unverifiable items are marked
      [unverified]. Value is EVENT detection + sentiment extremes, not price calls.
    - Recommend-only. Never auto-commits. Never trades.

  Mechanism notes (see memory grok-headless-cross-review): prompt is passed via
  --prompt-file (inline -p truncates through PowerShell->wsl->bash); UTF-8 is forced because
  this is a cp950 box; the repo path is mapped manually to /mnt/<drive>/... .

.PARAMETER Topic
  The ticker / asset / theme to pull, e.g. "DOT", "BTC", "NVDA", "AI infrastructure".

.PARAMETER UseKolIndex
  Seed the prompt with the tracked handles from raw/kol_signals/crypto-kol-index.tsv so Grok
  prioritises the principal's watched KOLs (and applies their "how to read" contra lenses).

.PARAMETER Handles
  Explicit comma-separated X handles to prioritise (overrides -UseKolIndex).

.PARAMETER Effort
  Grok reasoning effort (default high).

.PARAMETER MaxTurns
  Max Grok agent turns (default 16; web research needs headroom).

.PARAMETER DryRun
  Print the assembled capture to console only; do NOT write into raw/.

.EXAMPLE
  .\scripts\grok-kol.ps1 DOT -DryRun
  .\scripts\grok-kol.ps1 BTC -UseKolIndex
  .\scripts\grok-kol.ps1 "AI infrastructure" -Handles "@dnvolz,@SemiAnalysis_"
#>
[CmdletBinding()]
param(
    [Parameter(Position = 0, Mandatory = $true)] [string]$Topic,
    [switch]$UseKolIndex,
    [string]$Handles = "",
    [string]$Effort = "high",
    [int]$MaxTurns = 16,
    [switch]$DryRun
)

$ErrorActionPreference = "Continue"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8   # cp950 box: force UTF-8

# --- paths / time ----------------------------------------------------------
$repoRoot = Split-Path $PSScriptRoot -Parent
$now      = Get-Date
$stamp    = $now.ToString("yyyy-MM-dd-HHmmss")
$date     = $now.ToString("yyyy-MM-dd")
$iso      = $now.ToString("yyyy-MM-ddTHH:mm:sszzz")

$scratchDir = Join-Path $repoRoot ".scratch\grok-kol"
New-Item -ItemType Directory -Force -Path $scratchDir | Out-Null
$promptName = "kol-$stamp.txt"
$promptWin  = Join-Path $scratchDir $promptName
$promptRel  = ".scratch/grok-kol/$promptName"

$slug = ($Topic.ToLower() -replace '[^a-z0-9]+', '-').Trim('-')
if ([string]::IsNullOrWhiteSpace($slug)) { $slug = "topic" }
$outWin = Join-Path $repoRoot "raw\kol_signals\x-kol-$slug-$date.md"

# --- WSL repo path (manual drive mapping; avoids wslpath backslash mangling) -
if ($repoRoot -match '^([A-Za-z]):\\(.*)$') {
    $drive   = $matches[1].ToLower()
    $rest    = $matches[2] -replace '\\', '/'
    $repoWsl = "/mnt/$drive/$rest"
}
else { throw "Unexpected repo path '$repoRoot' (expected a drive path like D:\...)." }

# --- grok present? ---------------------------------------------------------
$grokBin = (wsl -e bash -lc "command -v grok 2>/dev/null" | Out-String).Trim()
if ([string]::IsNullOrWhiteSpace($grokBin)) {
    throw "grok not found on the WSL PATH. Install Grok Build in WSL first."
}

# --- optional: seed tracked KOL handles ------------------------------------
if ([string]::IsNullOrWhiteSpace($Handles) -and $UseKolIndex) {
    $idx = Join-Path $repoRoot "raw\kol_signals\crypto-kol-index.tsv"
    if (Test-Path -LiteralPath $idx) {
        $h = Get-Content -LiteralPath $idx -Encoding UTF8 |
            Select-Object -Skip 1 |
            ForEach-Object { ($_ -split "`t")[0] } |
            Where-Object { $_ -like '@*' }
        if ($h) { $Handles = ($h -join ", ") }
    }
}
$trackedNote = ""
if (-not [string]::IsNullOrWhiteSpace($Handles)) {
    $trackedNote = "Prioritise signals from these tracked KOL handles where relevant: $Handles. For any of them apply a skeptical 'how to read this person' lens -- most monetise your engagement."
}

# --- build prompt (escape literal `$hark in the double-quoted here-string) --
$prompt = @"
This is a COMPLETE, self-contained research task. Do NOT ask for clarification.
You are the Researcher for the Sharks (`$hark) project (AGENTS.md). You have already loaded
sharks.md, CLAUDE.md and AGENTS.md per the first-action protocol.

Use your X (Twitter) and web access to surface RECENT (roughly the last 7 days) KOL / social
chatter about: $Topic

HARD RULES (CLAUDE.md section 5 + sharks constitution):
- This is a Grade D (social / KOL / sentiment) signal. It is OBSERVATION ONLY -- it can inform
  a watchlist but NEVER triggers or sizes a position on its own.
- Do NOT invent handles, posts, dates, or prices. Mark anything you cannot verify [unverified].
  If there is no meaningful recent signal, say so plainly rather than padding.
- Value the X access for EVENT DETECTION and SENTIMENT-EXTREME reading, not for price targets.
$trackedNote

Produce a markdown BODY only (no title, no frontmatter -- the orchestrator adds those).
Structure it EXACTLY as:

## Summary
2-4 sentences: net sentiment (bull / bear / mixed), any shift vs the usual baseline, and any
concrete EVENT (launch, listing, filing, unlock) versus pure narrative.

## Signals
A markdown table with columns: handle | approx date | stance | one-line claim | how to read (contra/confirm) | grade
One row per distinct signal. grade is D unless it is a verifiable EVENT (then mark B-event / A-event).

## Sentiment extremes / contra flags
Bullet any euphoria or capitulation worth watching as a REVERSE indicator.

## Sources
Bullet the X posts / articles you actually used (handle + approx date + link if available).
Mark [unverified] anything you could not confirm directly.
"@

[System.IO.File]::WriteAllText($promptWin, $prompt, (New-Object System.Text.UTF8Encoding($false)))

# --- run grok (web/X search ON -- the whole point) -------------------------
# permission-mode 'auto' (not 'default'): in headless 'default' the web/X search tool is
# blocked for lack of an approver and grok returns nothing. 'auto' lets read-only research
# tools run; the prompt forbids writes and grok never edits unprompted.
$bash = "cd '$repoWsl' && grok --prompt-file '$promptRel' --output-format plain --permission-mode auto --max-turns $MaxTurns --no-memory --no-alt-screen"
if (-not [string]::IsNullOrWhiteSpace($Effort)) { $bash += " --reasoning-effort '$Effort'" }

Write-Host "[grok-kol] topic : $Topic"
Write-Host "[grok-kol] grok  : $grokBin (X/web search ON, effort=$Effort, max-turns=$MaxTurns)"
Write-Host "[grok-kol] pulling X / KOL signals (spends Grok credits)..."

# the headless web-research path is intermittent (sometimes spends all turns searching and
# returns no final text, esp. if an interactive `grok` TUI is also open) -- retry on empty
$raw = ""
$attempts = 3
for ($i = 1; $i -le $attempts; $i++) {
    if ($i -gt 1) {
        Write-Host "[grok-kol] empty result; retry $i/$attempts ..." -ForegroundColor Yellow
        Start-Sleep -Seconds 2
    }
    $raw = (wsl -e bash -lc $bash | Out-String).Trim()
    if (-not [string]::IsNullOrWhiteSpace($raw)) { break }
}

if ([string]::IsNullOrWhiteSpace($raw)) {
    Remove-Item -LiteralPath $promptWin -Force -ErrorAction SilentlyContinue
    throw "grok returned no output after $attempts attempts. If an interactive 'grok' TUI is open, close it (leader-session contention); else inspect the prompt at $promptRel."
}

# grok sometimes wraps markdown headers in bold (**## Summary**); unwrap them
$raw = (($raw -split "`n") | ForEach-Object {
        if ($_ -match '^\*\*(#{1,6}\s.*?)\*\*\s*$') { $matches[1] } else { $_ }
    }) -join "`n"

# --- assemble the immutable raw capture ------------------------------------
$frontmatter = @"
---
type: source
source_class: kol_post
source_grade: D
source_first_visible_at: $iso
ingested_at: $iso
topic: "$Topic"
tags: [kol, x-twitter, sentiment, grok-x-pull]
provenance: Grok Build headless X/web pull via scripts/grok-kol.ps1 ($stamp local). Grade-D social signal -- observation / sentiment-extreme reading only, NEVER a position trigger (CLAUDE.md section 5).
author_role: researcher
---

> Grade-D X/KOL capture. KOL price opinions NEVER rate A/B (CLAUDE.md section 5). Use for EVENT
> detection and sentiment extremes only; never size a position off a tweet. Verify any
> [unverified] item before it informs even a watchlist entry.

"@
$doc = $frontmatter + $raw + "`n"

Write-Host ""
if ($DryRun) {
    Remove-Item -LiteralPath $promptWin -Force -ErrorAction SilentlyContinue
    Write-Host "[grok-kol] DRY RUN -- nothing written to raw/. Preview:" -ForegroundColor Yellow
    Write-Host ("-" * 78)
    Write-Output $doc
}
else {
    New-Item -ItemType Directory -Force -Path (Split-Path $outWin -Parent) | Out-Null
    [System.IO.File]::WriteAllText($outWin, $doc, (New-Object System.Text.UTF8Encoding($false)))
    Remove-Item -LiteralPath $promptWin -Force -ErrorAction SilentlyContinue
    Write-Host "[grok-kol] capture saved (Grade D, immutable raw): $outWin" -ForegroundColor Green
    Write-Host "[grok-kol] NOT committed. Observation-only; never a position trigger."
    Write-Host ("-" * 78)
    Write-Output $doc
}
