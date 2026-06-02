# `sharks.discord` — PolkaSharks private Discord layer

A thin Discord skin on the Sharks brain for a **two-person private server**. It
adds **no** decision logic and inherits every hard boundary from [[sharks]] /
`CLAUDE.md §2`:

> **Recommend-only. Never trades, never connects a brokerage/exchange, never
> holds keys. `/ask` runs local Claude Code read-only. The bot never invites
> anyone, and never auto-publishes content.**

## Capabilities (one process)

| Capability | Where | Backend |
|---|---|---|
| 晨會 / 午會 / 晚會 / 週會 digests | auto-post to `#晨會` / `#午會` / `#晚會` on a TPE schedule | `outputs/` + Claude narrative + 議會結論 |
| **議會辯論** (多人格 質疑→投票→主席結論) | appended to every meeting · `/council <主題>` | **local Ollama**, multi-model |
| `/ask` + `#問claude` | read-only Q&A over the whole `$hark` tree | **local Claude Code CLI** (the loopback) |
| `/persona` + `#分析師議會` | chat with one analyst voice | **local Ollama** |
| `/llm` + `/models` | pick any resource per question | **claude · local · wiki(RAG) · codex** |
| `/content` → `#自媒體` | strict-format X / blog / YouTube drafts (no auto-post) | **local Ollama** |
| `!cmd` / `!help` · `/picks` `/meeting` `/status` `/personas` | help + manual controls | — |

`/llm` exposes every resource directly, so Discord works **even with no Claude**:

| `/llm backend` | what it uses |
|---|---|
| `claude` | local Claude Code CLI, read-only over `$hark` |
| `local`  | any pulled Ollama model (`model:` arg; `/models` lists them) |
| `wiki`   | local keyword RAG over `$hark` markdown + local-model synthesis |
| `codex`  | OpenAI Codex CLI if installed (`SHARKS_DISCORD_CODEX_BIN`) |

**Local models**: Ollama runs in WSL; `scripts/check_ollama.ps1` boots it. The
council + personas default to **`qwen2.5:7b`** and **`llama3.1:8b`** (both strong
繁中, and both fit in 12 GB together so they stay resident — no load churn).
Avoid as defaults: `nemotron-3-nano:4b` / `deepseek-r1:7b` / `qwen3:4b` (reasoning
models → empty `content` when truncated), `phi3.5` (simplified), `llama3.2:3b`
(mixes languages).

## Commands

```
/ask <問題>                 本地 Claude Code 唯讀讀 $hark（或在 #問claude 直接打字）
/llm <backend> <問題> [model]  claude | local | wiki | codex
/models                     列出本地 Ollama 模型
/persona <名> <訊息>         跟人格聊（或在 #分析師議會 打「huang: …」）
/personas                   列出全部人格
/council <主題>             召開議會辯論（多人格、多模型、投票、結論）
/meeting <morning|noon|evening|weekly>   手動開會
/picks                      最近一次選股 / 訊號
/content <x|blog|youtube|all> [主題]      自媒體草稿 → #自媒體（不代發）
/status                     bot 設定與狀態
!cmd / !help                指令表（任何頻道可用）
```

## Council debate

The headline feature: a meeting's conclusion isn't one voice but a **bench that
disagrees on the record** — each seat runs on its own local model (so it's
genuinely different "brains", not one model role-playing). Flow: 立場 → 質疑+投票
(多/空/中性 + 信心) → 主席綜合票數與分歧做出結論.

Default bench = **4 objective quant voices + 3 subjective voices**:

| Seat | Grounded in | Model |
|---|---|---|
| `fomquant` | FOM 5 維 + regime 權重 + bubble_guard floor + persistence | qwen2.5:7b |
| `bayes` | log-odds 後驗、EDGE vs 市場隱含、observe-first、十足證據≥4/5 | llama3.1:8b |
| `valuation` | 被打趴的好公司:dd_52w + 5y 倖存過濾(剔落刀) + 低波動 + 止穩 | qwen2.5:7b |
| `regimequant` | 五體制閘門 + 資金面;防守快、進攻慢 | llama3.1:8b |
| `huang` | 供應鏈撿便宜(多) | qwen2.5:7b |
| `bear` | 空方 / 風控 | llama3.1:8b |
| `momentum` | 動能 / 價量 | qwen2.5:7b |
| chair `sharks` | 綜合結論 | qwen2.5:7b |

Tune with `SHARKS_DISCORD_COUNCIL_PERSONAS` and `SHARKS_DISCORD_COUNCIL_MODELS`
(per-seat, round-robin). `~1–1.5 min` per debate. Engine: `council.py` (pure;
the LLM call is injected so it's unit-tested offline).

## Personas

Loaded from `analysts/*.md`. **Objective quant** voices: `fomquant`, `bayes`,
`valuation`, `regimequant` (reason only from the repo's signals/methods).
**Subjective** voices: `huang`, `sam`, `buffet`, `serenity`, `crypto`, `yupupin`,
`bear`, `momentum`, plus `sharks` (house view / constitution). Design-critique
archives (`codex`, `gemini`) are excluded. New objective voices are `type: voice`
so they debate but do **not** perturb the FOM voting ensemble in
`sharks.analysts.persona`. In `#分析師議會` type `huang: 你的問題`; default `sharks`.

## Meetings

TPE (fixed UTC+8). 晨會 `07:30` · 午會 `13:00` · 晚會 `22:30`; the weekly FOM
block folds into Monday's 晨會. Each meeting posts (1) a **data digest** from
`outputs/`, (2) an optional **Claude narrative** (今日國際局勢 / 台美股行情,
`SHARKS_DISCORD_MEETING_RESEARCH=1`), and (3) a **議會結論** (the council debate).
`SHARKS_DISCORD_MEETING_REFRESH=1` refreshes `outputs/` via `sharks health-check`
first. Weekly FOM scans are still produced by `scripts/daily_routine.ps1`.

Backfill / cron one-shot: `python -m sharks.discord.bot --run-meeting all`
(or `morning|noon|evening|weekly`) posts once and exits.

## Setup (once)

1. **Create the bot** at <https://discord.com/developers/applications>: *New
   Application* → *Bot* → *Reset Token* (into `.env`); enable **MESSAGE CONTENT**
   + **SERVER MEMBERS** intents; *OAuth2 URL Generator* → scopes `bot` +
   `applications.commands`, perms *View/Manage Channels, Send Messages, Embed
   Links, Read History, Manage Webhooks, Connect, Speak* (**not** Administrator)
   → open URL, add to server.
2. **Configure**: copy `.env.example` → `.env`, set `DISCORD_BOT_TOKEN` (gitignored).
3. **Install deps**: `uv pip install -e ".[discord]"` (or `pip install discord.py python-dotenv`).
4. **Channels**: `python -m sharks.discord.setup_guild` — builds the layout +
   prints the **privacy lockdown checklist**. Do the checklist.
5. **Run**: `scripts/run_discord_bot.ps1` (boots Ollama, then the bot).

## Channels (精簡版)

`#bot-狀態 · #晨會 · #午會 · #晚會 · #市場 · #每日選股 · #問claude · #分析師議會 · #自媒體 · #雜談`
(resolved **by name** — rename freely and update `config.py`).

## Persistence (autostart, no admin)

The bot runs only while its process is alive. To keep it listening + firing
meetings across logons, run yourself (no admin — uses the Startup folder, since
`schtasks /SC ONLOGON` needs elevation here):

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File 'D:\DOT\$hark\scripts\install_discord_autostart.ps1'
```

Remove: delete `…\Start Menu\Programs\Startup\SharksDiscordBot.cmd`.

## Safety notes

- `/ask` runs `claude -p` in `default` permission mode with a **read-only** tool
  allowlist (`Read Grep Glob WebSearch WebFetch`), explicit **deny** of
  `Write/Edit/Bash/NotebookEdit`, and a `--max-budget-usd` ceiling. Reads and
  explains; cannot edit, commit, or run shell mutations.
- `/content` only **drafts** to `#自媒體`; publishing to X / YouTube / the blog
  stays a human action.
- Wiki writeback is **not** automatic.
- `on_member_join` only **alerts** in `#bot-狀態`; it never kicks. Locking the
  server to two people is the Discord-side checklist from `setup_guild.py`.

## Files

```
config.py       env + channel map + schedule + council roster/models + validation
personas.py     analysts/*.md -> chat personas (guardrailed system prompts)
brains.py       backend router: Claude Code + local Ollama + wiki RAG + codex
council.py      multi-persona, multi-model debate: stance -> 質疑+投票 -> 主席結論
wiki_rag.py     local keyword RAG over $hark markdown (the LLM-wiki backend)
content.py      strict-format self-media drafts (X / blog / YouTube), drafts-only
meetings.py     compose 晨會/午會/晚會/週會 digests from outputs/ (pure, testable)
bot.py          discord.py client: slash cmds + !cmd + message routing + scheduler
setup_guild.py  one-shot channel creation + privacy checklist
```

Tests: `tests/test_discord_bot.py` (offline — no token/network needed).
New objective council voices: `analysts/{fomquant,bayes,valuation,regimequant}.md`.
