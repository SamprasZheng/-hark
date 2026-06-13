<#
.SYNOPSIS
  Cross-review a file, commit, or diff with Grok (headless) OR local LLM as Risk Officer reviewer.
  Supports RAG-augmented context from local Chroma/LlamaIndex (rag_retriever.py).

.DESCRIPTION
  scripts/cross-review.ps1 -- the quality-control layer for the Sharks multi-agent setup.
  Sends a target to the chosen reviewer (Grok cloud / local Ollama / codex) running headless,
  optionally injects saturated RAG context (wiki/ + philosophy/ + cross-review reports +
  rag-data/contracts/disclosures.json), and writes a timestamped report.

  The RAG path pulls the contractualized overfitting guards (tail winsorization + TD-9 sell
  hard-disable) so that future AI automation of the Finviz DNA / FOM cannot chase survivor
  bias or invalid top-calling.

  READ-ONLY by design. This is the Main Orchestrator → Risk Officer cross-review step from
  wiki/grok.md + the RAG injection pattern described in the 2026-06 evolution log.

  Mechanism:
    - Always uses --prompt-file (inline -p truncates through PS→WSL→bash).
    - Runs inside repo so AGENTS.md §0 + sharks.md/CLAUDE.md load.
    - -UseRag calls scripts/rag_retriever.py (LlamaIndex/Chroma/Ollama or keyword fallback)
      and prepends a 【RAG 檢索之專案歷史與契約上下文】 block.

.PARAMETER Target
  What to review (default "working"). One of:
    <path>      a file ... | working | staged | <sha> | <a>..<b>

.PARAMETER Reviewer
  "grok" (default, cloud), "local" (Ollama qwen2.5-coder:32b or similar), "codex".

.PARAMETER UseRag
  Call scripts/rag_retriever.py first and inject 【RAG ...】 context block containing
  disclosures.json (tail winsorization + TD-9 sell disable), PIT rules, etc.

.PARAMETER Task
  Extra focus for the reviewer (e.g. "對照 disclosures.json 檢查 tail risk").

.PARAMETER Json
  Request json output (best effort).

.PARAMETER Model
  Model override (for grok: -m; for local may be passed to ollama).

.PARAMETER Effort
  Reasoning effort for grok.

.PARAMETER MaxTurns
  Max turns (default 12 for grok).

.PARAMETER KeepPrompt
  Keep the generated prompt under .scratch for debugging.

.EXAMPLE
  .\scripts\cross-review.ps1 -UseRag -Task "檢查 fom.py 的 tail winsorization 與 TD-9 sell 硬禁"
  .\scripts\cross-review.ps1 src\sharks\scoring\fom.py -Reviewer local -UseRag
  .\scripts\cross-review.ps1 -Target "main..HEAD" -Reviewer grok -Effort high
#>
[CmdletBinding()]
param(
    [Parameter(Position = 0)] [string]$Target = "working",
    [ValidateSet("grok", "local", "codex")][string]$Reviewer = "grok",
    [switch]$UseRag,
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

# --- WSL python / ollama presence (for RAG and local reviewer) -------------
$pythonBin = (wsl -e bash -lc "command -v python3 2>/dev/null || command -v python 2>/dev/null" | Out-String).Trim()
$ollamaBin = (wsl -e bash -lc "command -v ollama 2>/dev/null" | Out-String).Trim()

# --- RAG context injection (if -UseRag) ------------------------------------
$ContextBlock = ""
if ($UseRag) {
    Write-Host "🔍 [RAG] 正在調用 Chroma + LlamaIndex 檢索合規上下文 (disclosures.json + PIT + 契約)..." -ForegroundColor Cyan
    $ragCmd = "cd '$repoWsl' && python3 scripts/rag_retriever.py --query `"$Task`" --k 6"
    if ($Model) { $ragCmd += " --model `"$Model`"" }
    $ragRaw = (wsl -e bash -lc $ragCmd 2>&1 | Out-String).Trim()
    if ($ragRaw) {
        $ContextBlock = "`n【RAG 檢索之專案歷史與契約上下文】`n$ragRaw`n"
    } else {
        $ContextBlock = "`n【RAG】檢索無回傳或失敗，繼續使用純提示。`n"
    }
}

# --- grok present on WSL PATH? ---------------------------------------------
$grokBin = (wsl -e bash -lc "command -v grok 2>/dev/null" | Out-String).Trim()
if ($Reviewer -eq "grok" -and [string]::IsNullOrWhiteSpace($grokBin)) {
    throw "grok not found on the WSL PATH (needed for -Reviewer grok). Install first."
}
if ($UseRag -and [string]::IsNullOrWhiteSpace($pythonBin)) {
    Write-Host "[RAG] Warning: python3 not found in WSL; RAG may have fallen back to keyword mode." -ForegroundColor Yellow
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

# --- build the prompt (double-quoted here-string) ----------------------------
$rubric = @"
This is a COMPLETE, self-contained, READ-ONLY task. You have everything you need.
Do NOT ask for clarification. Do NOT defer to a human. Do NOT say the task is underspecified.
Do NOT edit, create, or write any files. Output text only.

You are the Risk Officer cross-reviewer for the Sharks (`$hark) project (AGENTS.md sections 2 and 3).
You have already loaded sharks.md, CLAUDE.md and AGENTS.md per the AGENTS.md first-action protocol;
apply those rules.

核心 DNA 護欄（來自 rag-data/contracts/disclosures.json，RAG 必須強制 surfaced）：
- 單筆最大收益平滑閘門（Winsorization）：任何 EV / FOM / backtest 計算中，單一 ticker 實現收益上限 +500%。
  尾部事件 (AXTI ~+4907%, RKLB ~+2214%) 不得主導系統期望值。
- TD-9 / magic nine SELL 訊號硬禁：完全閹割 sell-9 觸發。逃頂只允許「拒絕棒 + 破月線 MA（例如 monthly MA10）」移動停利。
  買 9 有效，賣 9 無效。嚴禁任何「猜頂」的反身性預測。

$ContextBlock

REVIEW TARGET -- $($tb.kind)
------------------------------------------------------------------------------
$($tb.body)
------------------------------------------------------------------------------

Review the target above. Produce EXACTLY these numbered sections, then stop:

1. CORRECTNESS - logic errors, bugs, or claims that do not hold. Cite line/section, or write NONE.
2. CONTRACT FIDELITY - any violation or drift vs sharks.md, CLAUDE.md, AGENTS.md, rag-data/contracts/disclosures.json,
   philosophy/09-point-in-time, or the philosophy layer (roles, source grading, 10-signal contract, raw/ immutability).
   Cite the rule, or write NONE.
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

# --- write prompt (UTF-8 no BOM, required for reliable parse) ---------------
[System.IO.File]::WriteAllText($promptWin, $rubric, (New-Object System.Text.UTF8Encoding($false)))

# --- dispatch by reviewer --------------------------------------------------
$fmt = "plain"; if ($Json) { $fmt = "json" }
$reviewerLabel = $Reviewer
$raw = ""

if ($Reviewer -eq "local") {
    Write-Host "⚡ [local] 啟動本地開源模型進行扛量審查 (ollama)..." -ForegroundColor Green
    if ([string]::IsNullOrWhiteSpace($ollamaBin)) {
        throw "ollama not found in WSL. Run setup_local_llm.ps1 or 'ollama serve' first."
    }
    $localModel = if ($Model) { $Model } else { "qwen2.5-coder:32b" }
    # Pipe the already-written prompt file (more reliable than huge inline)
    $bashLocal = "cd '$repoWsl' && cat '$promptRel' | ollama run $localModel"
    Write-Host "[cross-review] target : $($tb.kind) | local model=$localModel"
    $raw = (wsl -e bash -lc $bashLocal | Out-String)
    $reviewerLabel = "local ($localModel)"
}
elseif ($Reviewer -eq "codex") {
    Write-Host "[codex] (placeholder) routing to codex-style local or other; falling back to grok behavior for now." -ForegroundColor Yellow
    $Reviewer = "grok"   # fallthrough
}

if ($Reviewer -eq "grok") {
    $bash = "cd '$repoWsl' && grok --prompt-file '$promptRel' --output-format $fmt --permission-mode default --max-turns $MaxTurns --no-memory --disable-web-search --no-alt-screen"
    if (-not [string]::IsNullOrWhiteSpace($Model))  { $bash += " -m '$Model'" }
    if (-not [string]::IsNullOrWhiteSpace($Effort)) { $bash += " --reasoning-effort '$Effort'" }

    Write-Host "[cross-review] target : $($tb.kind)"
    Write-Host "[cross-review] grok   : $grokBin (mode=$fmt, max-turns=$MaxTurns, rag=$UseRag)"
    Write-Host "[cross-review] running headless review (this spends Grok credits, read-only)..."

    $raw = (wsl -e bash -lc $bash | Out-String)
}

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

# --- best-effort JSON extraction (for grok json mode) -----------------------
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
    $reviewText = "(no output returned by reviewer -- re-run with -KeepPrompt and inspect $promptRel)"
}

# --- write the report ------------------------------------------------------
$gitBranch = (git -C $repoRoot rev-parse --abbrev-ref HEAD 2>$null | Out-String).Trim()
$gitHead   = (git -C $repoRoot rev-parse --short HEAD       2>$null | Out-String).Trim()
$ragNote = if ($UseRag) { " + RAG (disclosures + PIT)" } else { "" }
$report = @"
# Cross-review report

- generated : $stamp (local)
- target    : $($tb.kind)
- repo      : $repoRoot @ $gitBranch ($gitHead)
- reviewer  : $reviewerLabel ($grokBin), mode=$fmt, max-turns=$MaxTurns$ragNote
- note      : READ-ONLY -- reviewer did not write to the repo. Recommend-only; verify before acting.
              RAG (when enabled) forces disclosures.json (tail-winsor + TD-9 sell hard-disable) + philosophy/09-point-in-time.

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
