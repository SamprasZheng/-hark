# scripts/check_ollama.ps1
#
# Preflight + boot for the local Ollama daemon used by the Nemotron client.
# Intended to be invoked at the top of daily_am.ps1 / daily_pm.ps1 (or any
# pipeline that wants the local LLM up).
#
# Behaviour:
#   1. Probe http://127.0.0.1:11434/api/tags. If it answers in <3s, we're up;
#      list the loaded models and exit 0.
#   2. If it does not answer and -Boot is passed (default), invoke the WSL
#      bring-up script in the sibling yxz repo:
#        wsl bash -c "cd /mnt/d/DOT/yxz && bash scripts/start-ollama.sh"
#      Then re-probe with a short backoff. Exit 0 if up, 1 if still down.
#   3. With -NoBoot, only probe; exit 0 / 1.
#
# Usage:
#   pwsh scripts/check_ollama.ps1                # probe + boot if needed
#   pwsh scripts/check_ollama.ps1 -NoBoot        # probe only
#   pwsh scripts/check_ollama.ps1 -Verbose       # show probe payload
#
# Exit codes: 0 = Ollama reachable; 1 = unreachable (and could not be booted).

[CmdletBinding()]
param(
    [switch]$NoBoot
)

$ErrorActionPreference = "Continue"
$probeUrl = "http://127.0.0.1:11434/api/tags"
$ywsl     = "/mnt/d/DOT/yxz"

function Test-Ollama {
    try {
        $r = Invoke-WebRequest -Uri $probeUrl -TimeoutSec 3 -UseBasicParsing -ErrorAction Stop
        if ($r.StatusCode -eq 200) { return ($r.Content | ConvertFrom-Json) }
    } catch {
        return $null
    }
    return $null
}

# 1. Initial probe.
$tags = Test-Ollama
if ($null -ne $tags) {
    $names = @($tags.models | ForEach-Object { $_.name })
    Write-Output "Ollama UP at $probeUrl ($($names.Count) model(s): $($names -join ', '))"
    exit 0
}

if ($NoBoot) {
    Write-Output "Ollama DOWN at $probeUrl (boot suppressed by -NoBoot)"
    exit 1
}

# 2. Try to boot via WSL using the yxz bring-up script.
Write-Output "Ollama DOWN — attempting WSL bring-up..."
$bootCmd = "cd $ywsl && bash scripts/start-ollama.sh"
try {
    wsl bash -c "$bootCmd" 2>&1 | Tee-Object -Variable bootOut | Out-Null
    Write-Verbose ($bootOut -join "`n")
} catch {
    Write-Output "  wsl invocation failed: $_"
    exit 1
}

# 3. Re-probe with brief backoff (daemon takes ~2-4s to bind on cold WSL start).
$tags = $null
foreach ($wait in 2, 3, 4) {
    Start-Sleep -Seconds $wait
    $tags = Test-Ollama
    if ($null -ne $tags) { break }
}

if ($null -ne $tags) {
    $names = @($tags.models | ForEach-Object { $_.name })
    Write-Output "Ollama UP after WSL boot ($($names.Count) model(s): $($names -join ', '))"
    exit 0
} else {
    Write-Output "Ollama STILL DOWN after WSL bring-up — check that yxz/scripts/start-ollama.sh is present and WSL has GPU access"
    exit 1
}
