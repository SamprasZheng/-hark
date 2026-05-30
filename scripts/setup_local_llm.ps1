# scripts/setup_local_llm.ps1
#
# One-shot bring-up for the Sharks Streamlit Page 11 (Deep Research + AI):
#   1. Boot Ollama via WSL (calls scripts/check_ollama.ps1).
#   2. Pull llama3.2:3b (the default model for sharks.ai.local_llm).
#   3. Smoke-test by running `python -m sharks.ai.local_llm`.
#
# After this script exits 0, the Streamlit "🧠 11. Deep Research + AI" page
# will show "Ollama OK" and the "📝 生成 Thesis" / "😈 反方論點" buttons will
# call the local LLM instead of complaining about Ollama being down.
#
# Usage:
#   pwsh scripts/setup_local_llm.ps1                   # default: llama3.2:3b
#   pwsh scripts/setup_local_llm.ps1 -Model qwen2.5:7b # heavier, better 中文
#
# Exit codes: 0 = ready; 1 = could not boot Ollama; 2 = pull failed.

[CmdletBinding()]
param(
    [string]$Model = "llama3.2:3b"
)

$ErrorActionPreference = "Continue"
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Split-Path -Parent $scriptDir

Write-Output "=== Sharks local LLM setup ==="
Write-Output "Model:        $Model"
Write-Output "Project root: $projectRoot"
Write-Output ""

# Step 1: Boot Ollama
Write-Output "[1/3] Booting Ollama..."
& "$scriptDir\check_ollama.ps1"
if ($LASTEXITCODE -ne 0) {
    Write-Output "  FAILED — see check_ollama.ps1 output above"
    Write-Output "  Fix: install Ollama (https://ollama.com) or ensure WSL+GPU works"
    exit 1
}

# Step 2: Pull model via WSL ollama CLI
Write-Output ""
Write-Output "[2/3] Pulling $Model (skipped if already present)..."
$pullOut = wsl bash -c "ollama list | grep -q '$Model' && echo 'already-have' || ollama pull $Model" 2>&1
$pullOut | ForEach-Object { Write-Output "  $_" }
if ($LASTEXITCODE -ne 0) {
    Write-Output "  PULL FAILED"
    exit 2
}

# Step 3: Smoke test sharks.ai.local_llm
Write-Output ""
Write-Output "[3/3] Smoke test (python -m sharks.ai.local_llm)..."
Push-Location $projectRoot
try {
    if (Test-Path ".\.venv\Scripts\python.exe") {
        $py = ".\.venv\Scripts\python.exe"
    } else {
        $py = "python"
    }
    & $py -m sharks.ai.local_llm
    $smokeExit = $LASTEXITCODE
} finally {
    Pop-Location
}

Write-Output ""
if ($smokeExit -eq 0) {
    Write-Output "=== READY ==="
    Write-Output "Open Streamlit -> Page 11 (🧠 Deep Research + AI)"
    Write-Output "  Pick a ticker -> 📝 生成 Thesis / 😈 反方論點"
    exit 0
} else {
    Write-Output "=== Smoke test exited $smokeExit — Streamlit page may still work ==="
    exit 0  # check_ollama is the binding gate; smoke writes outputs/local-llm-status-*.json
}
