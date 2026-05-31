# scripts/run_discord_bot.ps1
# Start the Sharks Discord bot (long-running). This is NOT a scheduled task — it
# stays running and posts 晨會/晚會 on its own internal TPE schedule.
#
# First run will install discord.py + python-dotenv into the venv if missing.
# To autostart on login: Task Scheduler → trigger "At log on" → this script,
# or drop a shortcut in shell:startup.

$ErrorActionPreference = "Stop"
$projectRoot = "D:\DOT\`$hark"
Set-Location $projectRoot
& '.\.venv\Scripts\Activate.ps1'

# Ensure Discord deps are present (core repo stays dep-free by design).
python -c "import discord, dotenv" 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "Installing discord.py + python-dotenv into .venv ..."
    uv pip install "discord.py>=2.3" "python-dotenv>=1.0"
}

if (-not (Test-Path ".env")) {
    Write-Warning ".env not found. Copy .env.example to .env and set DISCORD_BOT_TOKEN."
}

# Bring up local Ollama (council debate + persona chat run on the local model).
& (Join-Path $projectRoot "scripts\check_ollama.ps1")

Write-Host "Starting Sharks Discord bot (Ctrl+C to stop)..."
python -m sharks.discord.bot
