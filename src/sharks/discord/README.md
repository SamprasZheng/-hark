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
| **議會辯論** (多人格 立場→交叉質詢→投票→主席結論;結論回寫 wiki 記憶) | appended to every meeting · `/council <主題>` | **local Ollama**, multi-model |
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
/picks                      最近一次選股 / 訊號（只貼快取，不重跑）
/rescan <fom|signals|health|all>  重跑選股/訊號/健檢掃描（本地）→ 貼最新結果
                            fom=FOM 全宇宙掃描 · signals=籌碼 FSM→每日10訊號 · health=持倉+姿態
/content <x|blog|youtube|all> [主題]      自媒體草稿 → #自媒體（不代發）
/status                     bot 設定與狀態
/cmd                        指令教學範例（情境→指令→會發生什麼;主打議會閉環）
!cmd / !help                指令表（任何頻道可用）· !教學 / !tutorial = /cmd 範例
```

## Council debate

The headline feature: a meeting's conclusion isn't one voice but a **bench that
disagrees on the record** — each seat runs on its own local model (so it's
genuinely different "brains", not one model role-playing).

**Multi-layer flow** (`SHARKS_DISCORD_COUNCIL_CROSSEXAM=1`, default):

```
立場 → 交叉質詢 → 投票(多/空/中性 + 信心) → 主席綜合票數與分歧做出結論
```

The 交叉質詢 layer is its own round: each seat **指名道姓** challenges the
positions it least agrees with (具體數據/邏輯, no vote yet); the vote round then
makes each seat **answer the challenges aimed at it** before committing. Set
`…CROSSEXAM=0` to fall back to the faster combined 質疑+投票 round.

**Closed loop — the council remembers** (`SHARKS_DISCORD_COUNCIL_MEMORY=1` /
`…WRITEBACK=1`, default): every conclusion is written back to
`wiki/council/<ts>-<topic>.md` (RAG-searchable, human-readable) plus an
append-only `_history.jsonl`. The next council reads it back as:

- **近期議會結論** — so the bench 延續 or explicitly 反轉 prior views (the chair
  states which), instead of restarting from scratch → each round is more efficient;
- **per-persona memory** — each seat is reminded of what *it* argued (`你最近的
  紀錄…`) and is held to it (延續 or 認錯修正) → every persona has memory;
- **topic RAG** over `wiki/` + `philosophy/` (底層邏輯) + anything you `/ingest`
  into `wiki/inbox/` (web articles) → it reasons over **本機 + 已注入(網路) 文檔**.

`結論 → wiki → RAG → 下一場 council 的記憶 → 新結論` is the multi-layer閉環.
Writeback lands in the working tree only — never auto-committed (the human commits).

Default bench = **4 objective quant voices + 6 KOL/subjective voices**:

| Seat | Grounded in | Model |
|---|---|---|
| `fomquant` | FOM 5 維 + regime 權重 + bubble_guard floor + persistence | qwen2.5:7b |
| `bayes` | log-odds 後驗、EDGE vs 市場隱含、observe-first、十足證據≥4/5 | llama3.1:8b |
| `valuation` | 被打趴的好公司:dd_52w + 5y 倖存過濾(剔落刀) + 低波動 + 止穩 | qwen2.5:7b |
| `regimequant` | 五體制閘門 + 資金面;防守快、進攻慢 | llama3.1:8b |
| `huang` | 供應鏈撿便宜(多) | qwen2.5:7b |
| `serenity` | 總經狙擊(KOL) | llama3.1:8b |
| `sam` | 長線與時間交朋友(KOL) | qwen2.5:7b |
| `yupupin` | 抓底層邏輯(KOL) | llama3.1:8b |
| `bear` | 空方 / 風控 | qwen2.5:7b |
| `momentum` | 動能 / 價量 | llama3.1:8b |
| chair `sharks` | 綜合結論 | qwen2.5:7b |

Add more KOLs (e.g. `buffet,crypto`) via `SHARKS_DISCORD_COUNCIL_PERSONAS`; models
round-robin via `SHARKS_DISCORD_COUNCIL_MODELS`. Larger bench / cross-exam = more
local calls (each seat ≈ 3 calls in cross-exam mode) → longer debates. Engine:
`council.py` (pure; LLM call + memory injected so it's unit-tested offline).
Memory I/O: `council_memory.py`.

## Personas

Loaded from `analysts/*.md`. **Objective quant** voices: `fomquant`, `bayes`,
`valuation`, `regimequant` (reason only from the repo's signals/methods).
**Subjective / KOL** voices: `huang`, `sam`, `buffet`, `serenity`, `crypto`,
`yupupin`, `bear`, `momentum`, plus `sharks` (house view / constitution). The
default council bench now seats `serenity` (總經狙擊), `sam` (長線), and `yupupin`
(底層邏輯) alongside `huang`; `buffet`/`crypto` are one env-var away. Design-critique
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
- Wiki writeback: `/ingest` notes and **council conclusions** write to the
  working tree (`wiki/inbox/`, `wiki/council/`) — searchable immediately, but
  **never auto-committed to git** (the human reviews and commits). No curated
  page is ever edited.
- `on_member_join` only **alerts** in `#bot-狀態`; it never kicks. Locking the
  server to two people is the Discord-side checklist from `setup_guild.py`.

## Files

```
config.py       env + channel map + schedule + council roster/models + validation
personas.py     analysts/*.md -> chat personas (guardrailed system prompts)
brains.py       backend router: Claude Code + local Ollama + wiki RAG + codex
council.py      multi-persona, multi-model debate: 立場 -> 交叉質詢 -> 投票 -> 主席結論
council_memory.py  closed loop: 結論 -> wiki/council/*.md + _history.jsonl; recall as memory_brief + per-persona memory + topic RAG
wiki_rag.py     local keyword RAG over $hark markdown (the LLM-wiki backend)
content.py      strict-format self-media drafts (X / blog / YouTube), drafts-only
meetings.py     compose 晨會/午會/晚會/週會 digests from outputs/ (pure, testable)
bot.py          discord.py client: slash cmds + !cmd + message routing + scheduler
setup_guild.py  one-shot channel creation + privacy checklist
```

Tests: `tests/test_discord_bot.py` (offline — no token/network needed).
New objective council voices: `analysts/{fomquant,bayes,valuation,regimequant}.md`.
