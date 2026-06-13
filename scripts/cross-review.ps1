<#
.SYNOPSIS
  Cross-review a file, commit, or diff with Grok (headless) as a Risk Officer reviewer.

.DESCRIPTION
  scripts/cross-review.ps1 -- the quality-control layer for the Sharks multi-agent setup.
  Sends a target (a file / a git commit / a git range / the working tree) to Grok Build
  running headless in WSL, captures the review, and writes a timestamped report.

  READ-ONLY by design: Grok only reads the repo and emits text -- it never writes, never
  commits, never trades. This is the "Main Orchestrator initiates cross-review" step from
  wiki/grok.md; Grok plays the Risk Officer cross-reviewer (AGENTS.md sections 2 and 3).
  A WRITE-loop (Grok editing in a worktree) is deliberately OUT OF SCOPE here -- that needs
  worktree isolation plus the Risk Officer merge gate.

  Mechanism (see memory grok-headless-cross-review):
    - Grok is invoked via `grok --prompt-file <rel>`. The inline `-p "..."` form gets
      TRUNCATED to its first word through the PowerShell -> wsl -> bash quoting layers, so
      we always pass the prompt as a file (referenced by a relative, '$'-free path).
    - It runs INSIDE the repo so Grok auto-loads sharks.md / CLAUDE.md / AGENTS.md
      (AGENTS.md first-action protocol). Bare dirs (/tmp) produce empty output.

.PARAMETER Target
  What to review (default "working"). One of:
    <path>      a file (absolute, or relative to repo root) -> review its content
    working     uncommitted working-tree changes            -> git diff
    staged      staged changes                              -> git diff --cached
    <sha>       a single commit                             -> git show <sha>
    <a>..<b>    a commit range                              -> git diff <a>..<b>

.PARAMETER Task
  Extra focus instruction appended to the default review rubric. Optional.

.PARAMETER Json
  Request --output-format json from Grok (best-effort parse; raw is saved either way).

.PARAMETER Model
  Optional Grok model id (passed as -m).

.PARAMETER Effort
  Optional reasoning effort: low | medium | high | xhigh | max.

.PARAMETER MaxTurns
  Max Grok agent turns (default 12).

.PARAMETER KeepPrompt
  Keep the temp prompt file under .scratch/ for debugging.

.EXAMPLE
  .\scripts\cross-review.ps1
  .\scripts\cross-review.ps1 HEAD
  .\scripts\cross-review.ps1 main..HEAD
  .\scripts\cross-review.ps1 AGENTS.md -Task "Check fidelity vs CLAUDE.md"
  .\scripts\cross-review.ps1 src\sharks\scoring\fom.py -Effort high -Json
#>
[CmdletBinding()]
param(
    [Parameter(Position = 0)] [string]$Target = "working",
    [string]$Task = "",
    [switch]$Json,
    [string]$Model = "",
    [string]$Effort = "",
    [int]$MaxTurns = 12,
    [switch]$KeepPrompt
)

$ErrorActionPreference = "Continue"

# UTF-8 everywhere: this is a cp950 (Big5) Windows box, so default decoding mangles
# non-ASCII (em-dash, section sign, en-dash A-E, etc.) in both file reads and the
# stdout we capture from git / wsl. Force UTF-8 before reading anything.
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

# --- paths -----------------------------------------------------------------
$repoRoot   = Split-Path $PSScriptRoot -Parent
$stamp      = Get-Date -Format "yyyy-MM-dd-HHmmss"
$scratchDir = Join-Path $repoRoot ".scratch\cross-review"
$reportDir  = Join-Path $repoRoot "outputs\cross-review"
New-Item -ItemType Directory -Force -Path $scratchDir | Out-Null
New-Item -ItemType Directory -Force -Path $reportDir  | Out-Null

$promptName = "task-$stamp.txt"
$promptWin  = Join-Path $scratchDir $promptName
$promptRel  = ".scratch/cross-review/$promptName"   # relative + forward slashes => no '$' in the grok arg
$reportWin  = Join-Path $reportDir "cross-review-$stamp.md"

# --- WSL repo path (manual drive-letter mapping; avoids wslpath backslash mangling) --
if ($repoRoot -match '^([A-Za-z]):\\(.*)$') {
    $drive   = $matches[1].ToLower()
    $rest    = $matches[2] -replace '\\', '/'
    $repoWsl = "/mnt/$drive/$rest"
}
else {
    throw "Unexpected repo path '$repoRoot' (expected a drive path like D:\...)."
}

# --- grok present on WSL PATH? ---------------------------------------------
$grokBin = (wsl -e bash -lc "command -v grok 2>/dev/null" | Out-String).Trim()
if ([string]::IsNullOrWhiteSpace($grokBin)) {
    throw "grok not found on the WSL PATH. Install Grok Build in WSL first (curl -fsSL https://x.ai/cli/install.sh | bash)."
}

# --- gather the target content ---------------------------------------------
function Get-TargetBlock {
    param([string]$t)
    Push-Location $repoRoot
    try {
        $candidate = Join-Path $repoRoot $t
        if (Test-Path -LiteralPath $t)         { $candidate = (Resolve-Path -LiteralPath $t).Path }
        if (Test-Path -LiteralPath $candidate) {
            $kind = "FILE: $t"
            $body = (Get-Content -LiteralPath $candidate -Raw -Encoding UTF8)
        }
        elseif ($t -eq "working") {
            $kind = "WORKING-TREE DIFF (uncommitted vs HEAD)"
            $body = (git diff 2>$null | Out-String)
        }
        elseif ($t -eq "staged") {
            $kind = "STAGED DIFF (git diff --cached)"
            $body = (git diff --cached 2>$null | Out-String)
        }
        elseif ($t -match "\.\.") {
            $kind = "DIFF RANGE: $t"
            $body = (git diff $t 2>$null | Out-String)
        }
        else {
            $kind = "COMMIT: $t"
            $body = (git show $t 2>$null | Out-String)
        }
    }
    finally { Pop-Location }

    if ([string]::IsNullOrWhiteSpace($body)) {
        $body = "(empty -- nothing to review for target '$t')"
    }
    # cap so the prompt stays sane
    $lines = $body -split "`n"
    $cap = 1600
    if ($lines.Count -gt $cap) {
        $body = ($lines[0..($cap - 1)] -join "`n") + "`n... [truncated $($lines.Count - $cap) more lines]"
    }
    return @{ kind = $kind; body = $body }
}

$tb = Get-TargetBlock -t $Target

# --- build the prompt (double-quoted here-string: escape the literal $hark) -
$rubric = @"
This is a COMPLETE, self-contained, READ-ONLY task. You have everything you need.
Do NOT ask for clarification. Do NOT defer to a human. Do NOT say the task is underspecified.
Do NOT edit, create, or write any files. Output text only.

You are the Risk Officer cross-reviewer for the Sharks (`$hark) project (AGENTS.md sections 2 and 3).
You have already loaded sharks.md, CLAUDE.md and AGENTS.md per the AGENTS.md first-action protocol;
apply those rules.

REVIEW TARGET -- $($tb.kind)
------------------------------------------------------------------------------
$($tb.body)
------------------------------------------------------------------------------

Review the target above. Produce EXACTLY these numbered sections, then stop:

1. CORRECTNESS - logic errors, bugs, or claims that do not hold. Cite line/section, or write NONE.
2. CONTRACT FIDELITY - any violation or drift vs sharks.md, CLAUDE.md, AGENTS.md, or the philosophy
   layer (roles, source grading A-E, the 10-signal contract). Cite the rule, or write NONE.
3. POINT-IN-TIME - any lookahead, missing as_of_timestamp, or backtest-integrity risk
   (philosophy/09-point-in-time). Write NONE if clean.
4. RISK DISCIPLINE - exclusion-list, position/sector-cap, or max-DD concerns
   (philosophy/06-exclusions, philosophy/08-risk-and-position). Write NONE or N/A if not applicable.
5. TOP FIX - the single highest-priority change, or state plainly that the target is sound.
"@

if (-not [string]::IsNullOrWhiteSpace($Task)) {
    $rubric += "`n`nADDITIONAL FOCUS FROM ORCHESTRATOR:`n$Task`n"
}

# write prompt as UTF-8 without BOM so grok parses it cleanly
[System.IO.File]::WriteAllText($promptWin, $rubric, (New-Object System.Text.UTF8Encoding($false)))

# --- build + run the grok command ------------------------------------------
$fmt = "plain"; if ($Json) { $fmt = "json" }
$bash = "cd '$repoWsl' && grok --prompt-file '$promptRel' --output-format $fmt --permission-mode default --max-turns $MaxTurns --no-memory --disable-web-search --no-alt-screen"
if (-not [string]::IsNullOrWhiteSpace($Model))  { $bash += " -m '$Model'" }
if (-not [string]::IsNullOrWhiteSpace($Effort)) { $bash += " --reasoning-effort '$Effort'" }

Write-Host "[cross-review] target : $($tb.kind)"
Write-Host "[cross-review] grok   : $grokBin (mode=$fmt, max-turns=$MaxTurns)"
Write-Host "[cross-review] running headless review (this spends Grok credits, read-only)..."

$raw = (wsl -e bash -lc $bash | Out-String)

# --- best-effort JSON extraction -------------------------------------------
$reviewText = $raw
if ($Json) {
    try {
        $obj = $raw | ConvertFrom-Json -ErrorAction Stop
        foreach ($f in @("result", "response", "text", "content", "message")) {
            if (($obj.PSObject.Properties.Name -contains $f) -and $obj.$f) {
                $reviewText = [string]$obj.$f; break
            }
        }
    }
    catch {
        Write-Host "[cross-review] JSON parse failed; keeping raw output." -ForegroundColor Yellow
    }
}

if ([string]::IsNullOrWhiteSpace($reviewText)) {
    $reviewText = "(no output returned by grok -- re-run with -KeepPrompt and inspect $promptRel)"
}

# --- write the report ------------------------------------------------------
$gitBranch = (git -C $repoRoot rev-parse --abbrev-ref HEAD 2>$null | Out-String).Trim()
$gitHead   = (git -C $repoRoot rev-parse --short HEAD       2>$null | Out-String).Trim()
$report = @"
# Cross-review report

- generated : $stamp (local)
- target    : $($tb.kind)
- repo      : $repoRoot @ $gitBranch ($gitHead)
- reviewer  : Grok headless ($grokBin), mode=$fmt, max-turns=$MaxTurns
- note      : READ-ONLY -- Grok did not write to the repo. Recommend-only; verify before acting.

---

$reviewText
"@
[System.IO.File]::WriteAllText($reportWin, $report, (New-Object System.Text.UTF8Encoding($false)))

if (-not $KeepPrompt) {
    Remove-Item -LiteralPath $promptWin -Force -ErrorAction SilentlyContinue
}

Write-Host ""
Write-Host "[cross-review] report saved: $reportWin" -ForegroundColor Green
Write-Host ("-" * 78)
Write-Output $reviewText
