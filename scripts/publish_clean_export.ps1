# scripts/publish_clean_export.ps1  (pure-ASCII source; Chinese built at runtime
# via char-codes so Windows PowerShell 5.1 never hits a codepage parse error)
#
# Publish a CLEAN, framework-only snapshot of $hark to a GitHub repo, EXCLUDING
# all personal/financial data, with a fresh history (so the private git history
# never leaves your machine). YOU run this; you perform the push.
#
# Publishes: src/ tests/ philosophy/ tech/ analysts/ docs/ scripts/ watchlist/
#   + sharks.md buffet.md gemini.md codex.md serenity.md README.md pyproject.toml
#     risk_config.yaml .env.example .gitignore
# Excludes (never copied): wiki/ raw/ data/ outputs/ crypto/ .env
# Scrubs residual refs (account numbers, sub-brokerage term, fills/RSU/$ amounts),
# then PII-greps the export and STOPS if anything suspicious remains.
#
# Usage (ordinary PowerShell; gh logged in):
#   powershell -NoProfile -ExecutionPolicy Bypass -File 'D:\DOT\$hark\scripts\publish_clean_export.ps1'
#   ... -Push -RemoteUrl 'https://github.com/SamprasZheng/-hark.git'
#   ... -Push -Public -RemoteUrl '...'         (push to existing repo; visibility set on GitHub)
#   ... -Push                                  (no RemoteUrl -> gh creates a new repo)

param(
    [string]$RepoName  = "sharks",
    [string]$Owner     = "SamprasZheng",
    [string]$RemoteUrl = "",
    [switch]$Public,
    [switch]$Push,
    [switch]$Force
)

$ErrorActionPreference = "Stop"
$src = "D:\DOT\`$hark"
$exp = "D:\DOT\sharks-public"
# sub-brokerage term (U+8907 U+59D4 U+8A17) built from codes -> ASCII-only source
$fz = [string]::new([char[]](0x8907, 0x59D4, 0x8A17))

if (Test-Path $exp) { Remove-Item -Recurse -Force $exp }
New-Item -ItemType Directory -Force $exp | Out-Null

# 1) copy ONLY the framework allow-list (tracked files), preserving structure
Push-Location $src
$dirs  = @("src", "tests", "philosophy", "tech", "analysts", "docs", "scripts", "watchlist")
$files = @("sharks.md", "buffet.md", "gemini.md", "codex.md", "serenity.md",
           "README.md", "pyproject.toml", "risk_config.yaml", ".env.example", ".gitignore")
$allow = @()
foreach ($d in $dirs) { $allow += (git ls-files $d) }
foreach ($f in $files) { if (git ls-files --error-unmatch $f 2>$null) { $allow += $f } }
foreach ($rel in $allow) {
    if (-not $rel) { continue }
    $dest = Join-Path $exp $rel
    New-Item -ItemType Directory -Force (Split-Path $dest) | Out-Null
    Copy-Item -LiteralPath (Join-Path $src $rel) -Destination $dest -Force
}
Pop-Location
# don't publish the publish-helpers themselves
Remove-Item (Join-Path $exp "scripts\publish_clean_export.ps1") -Force -ErrorAction SilentlyContinue
Remove-Item (Join-Path $exp "scripts\discord_audit.py") -Force -ErrorAction SilentlyContinue

# 2) scrub residual personal references (generic; no literal account numbers here)
Get-ChildItem $exp -Recurse -File -Include *.py, *.md, *.yaml, *.yml, *.toml | ForEach-Object {
    $t = Get-Content $_.FullName -Raw -Encoding utf8
    $orig = $t
    $t = $t -replace '[0-9A-Za-z]{4}-\d{7}', '[redacted-acct]'   # account-number format
    $t = $t -replace '\(\s*\d{4}\s*\)', '(redacted)'             # bare 4-digit acct in (...)
    $t = $t -replace $fz, '(speculative sleeve)'
    $t = $t -replace 'principal P2', 'P2'
    $t = $t -replace 'fills basket', 'watchlist basket'
    $t = $t -replace 'NVDA RSU', 'employer RSU'
    $t = $t -replace 'NVDA-RSU-dominated', 'RSU-dominated'
    $t = $t -replace '(NT\$4\.08M|\$130K|130K|11\.4K|4\.08M)', '[redacted-amt]'
    # anonymise the author + the employer/net-worth concentration framing
    $t = $t -replace '[A-Za-z0-9._%+-]+@gmail\.com', '[redacted-email]'
    $t = $t -replace 'NVDA employee', 'a mega-cap-tech employee'
    $t = $t -replace '~?89%', '[redacted]%'
    if ($t -ne $orig) { Set-Content -Path $_.FullName -Value $t -Encoding utf8 }
}

# 3) PII gate -- stop if anything suspicious remains
$patterns = '[0-9A-Za-z]{4}-\d{7}|' + $fz + '|NVDA RSU|NVDA employee|@gmail\.com|130K|4\.08M|11\.4K|principal P2|fills basket'
$hits = Get-ChildItem $exp -Recurse -File | Select-String -Pattern $patterns -ErrorAction SilentlyContinue
Write-Output "=== PII grep on export ($exp) ==="
if ($hits) {
    $hits | ForEach-Object { Write-Output ("  " + $_.Path.Replace($exp, "") + ":" + $_.LineNumber + "  " + $_.Line.Trim()) }
    if (-not $Force) { Write-Warning "Found $($hits.Count) possible-PII line(s) above. Review/scrub, then re-run (or -Force). NOT pushing."; exit 1 }
} else {
    Write-Output "  clean - no residual PII patterns found."
}

$n = (Get-ChildItem $exp -Recurse -File | Measure-Object).Count
Write-Output "Export ready at $exp ($n files)."
if (-not $Push) { Write-Output "Review $exp, then re-run with -Push (and -RemoteUrl or -Public)."; exit 0 }

# 4) fresh git history + push (you run this -> you perform the push)
Set-Location $exp
git init -q
git add -A
git commit -q -m "Sharks - dual-frequency multi-factor LLM-wiki trading system (framework + methodology; personal data excluded)"
git branch -M main
if ($RemoteUrl) {
    Write-Output "Pushing clean export to: $RemoteUrl"
    git remote add origin $RemoteUrl
    # always force: this is a fresh-history clean snapshot replacing the repo's main
    git push -u origin main --force
    Write-Output "Done — clean snapshot now replaces main on the remote."
} else {
    $vis = $(if ($Public) { "--public" } else { "--private" })
    Write-Output "Creating $Owner/$RepoName ($vis) and pushing..."
    gh repo create "$Owner/$RepoName" $vis --source=. --remote=origin --push
}
