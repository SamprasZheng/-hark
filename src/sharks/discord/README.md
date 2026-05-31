# `sharks.discord` — PolkaSharks private Discord layer

A thin Discord skin on the Sharks brain for a **two-person private server**. It
adds **no** decision logic and inherits every hard boundary from [[sharks]] /
`CLAUDE.md §2`:

> **Recommend-only. Never trades, never connects a brokerage/exchange, never
> holds keys. `/ask` runs local Claude Code read-only. The bot never invites
> anyone.**

## Four capabilities (one process)

| Capability | Where | Backend |
|---|---|---|
| 晨會 / 午會 / 晚會 / 週會 digests | auto-post to `#晨會` / `#午會` / `#晚會` on a TPE schedule | `outputs/` + optional Claude narrative |
| **議會結論** (multi-persona 質疑→投票→結論) | appended to every meeting · `/council` | **local Ollama** (qwen2.5:7b) |
| `/ask` + `#問claude` | read-only Q&A over the whole `$hark` tree | **local Claude Code CLI** (the loopback) |
| `/persona` + `#分析師議會` | chat with an analyst voice | **local Ollama** |
| `/llm` + `/models` | pick any resource per question | **claude · local(any model) · wiki(RAG) · codex** |
| `/picks` `/meeting` `/status` `/personas` | manual controls | — |

Backend routing is the **hybrid** default: personas + council → local Ollama
(private, free, RTX 5070), deep `/ask` → Claude Code (reads the repo). The
council debate **always** runs on the local model. `/llm` exposes every resource
directly so Discord works even with no Claude:

| `/llm backend` | what it uses |
|---|---|
| `claude` | local Claude Code CLI, read-only over `$hark` |
| `local`  | any pulled Ollama model (`model:` arg; `/models` lists them) |
| `wiki`   | local keyword RAG over `$hark` markdown + local-model synthesis |
| `codex`  | OpenAI Codex CLI if installed (`SHARKS_DISCORD_CODEX_BIN`) |

**Local model note**: default is `qwen2.5:7b` (clean instruct, strong 繁中).
`nemotron-3-nano:4b` is a *reasoning* model — it returns empty `content` when the
token budget is spent thinking, so it's a poor default for many short debate
turns. Ollama runs in WSL; `scripts/check_ollama.ps1` boots it.

## Setup (once)

1. **Create the bot** at <https://discord.com/developers/applications>:
   - *New Application* → name it (e.g. `PolkaSharks`).
   - *Bot* tab → *Reset Token* → copy it.
   - *Bot* tab → enable **MESSAGE CONTENT INTENT** and **SERVER MEMBERS INTENT**.
   - *OAuth2 → URL Generator* → scopes `bot` + `applications.commands`;
     bot permissions: *View Channels, Send Messages, Embed Links, Read Message
     History, Manage Webhooks, Manage Channels, Connect, Speak*. **Not**
     Administrator. Open the generated URL and add the bot to your server.
2. **Configure**: copy `.env.example` → `.env`, set `DISCORD_BOT_TOKEN`
   (`.env` is gitignored). Adjust `SHARKS_DISCORD_*` as desired.
3. **Install deps**: `uv pip install -e ".[discord]"` (or
   `pip install discord.py python-dotenv`).
4. **Create channels**: `python -m sharks.discord.setup_guild` — builds the
   minimal layout and prints the **privacy lockdown checklist**. Do the checklist.
5. **Run**: `python -m sharks.discord.bot` (or `scripts/run_discord_bot.ps1`).

## Channels (精簡版)

`#bot-狀態 · #晨會 · #晚會 · #市場 · #每日選股 · #問claude · #分析師議會 · #雜談`

The bot resolves channels **by name** (see `config.py`), so rename freely and
update the constants if you do.

## Personas

Loaded from `analysts/*.md` (superset of the FOM voting roster): `huang`, `sam`
(structured) · `sharks` (house view / constitution) · `buffett`, `serenity`,
`crypto`, `yupupin` (prose voices). Design-critique archives (`codex`, `gemini`)
are excluded from chat. In `#分析師議會` type `huang: 你的問題`; default voice is
`sharks`.

## Meetings

TPE (fixed UTC+8). 晨會 `07:30` · 午會 `13:00` · 晚會 `22:30`; the weekly FOM
block folds into Monday's 晨會. Each meeting posts: (1) a **data digest** from
`outputs/`, (2) an optional **Claude narrative** covering 今日國際局勢 / 台美股行情
(`SHARKS_DISCORD_MEETING_RESEARCH=1`), and (3) a **議會結論** — the council
debate (多 personas 質疑 → 投票 → 主席結論) on the local model. Each meeting
refreshes `outputs/` via `sharks health-check` (`SHARKS_DISCORD_MEETING_REFRESH=1`).
Heavy weekly FOM scans are still produced by `scripts/daily_routine.ps1`.

Backfill / cron one-shot: `python -m sharks.discord.bot --run-meeting all`
(or `morning|noon|evening|weekly`) posts the meeting(s) once and exits.

## Safety notes

- `/ask` runs `claude -p` with `--permission-mode default`, an allowlist of
  **read-only** tools (`Read Grep Glob WebSearch WebFetch`), an explicit
  **deny** of `Write/Edit/Bash/NotebookEdit`, and a `--max-budget-usd` ceiling.
  It can read and explain, but cannot edit, commit, or run shell mutations.
- Wiki writeback is **not** automatic — anything that would mutate `wiki/` is
  surfaced for human review, never committed by the bot.
- `on_member_join` only **alerts** in `#bot-狀態`; it never kicks. Locking the
  server to two people is the Discord-side checklist from `setup_guild.py`.

## Files

```
config.py       env + channel map + schedule + validation
personas.py     analysts/*.md -> chat personas (guardrailed system prompts)
brains.py       backend router: Claude Code + local Ollama + wiki RAG + codex
council.py      multi-persona debate: stance -> 質疑+投票 -> 主席結論 (local model)
wiki_rag.py     local keyword RAG over $hark markdown (the LLM-wiki backend)
meetings.py     compose 晨會/午會/晚會/週會 digests from outputs/ (pure, testable)
bot.py          discord.py client: slash cmds + message routing + TPE scheduler
setup_guild.py  one-shot channel creation + privacy checklist
```

Tests: `tests/test_discord_bot.py` (offline — no token/network needed).
