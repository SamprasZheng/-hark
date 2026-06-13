# AGENTS.md — Cross-tool agent contract for `D:\DOT\$hark\`

> **For any non-Claude coding agent operating in this repo: Codex, Grok Build, Google Antigravity (Gemini), Cursor, OpenCode, etc.**
>
> Claude Code auto-loads `CLAUDE.md`. **You probably do not.** This file exists to close that gap. It is **not** a second rulebook — it is a thin pointer to the canonical ones plus the multi-agent discipline that the single-agent docs don't cover.
>
> **Canonical source of truth, in order:**
> 1. `sharks.md` — the constitution (read-only for all agents).
> 2. `CLAUDE.md` — the operating manual / schema document.
> 3. `philosophy/index.md` — map of the philosophy layer.
>
> If anything here ever disagrees with `sharks.md` or `CLAUDE.md`, **they win and this file is wrong** — flag it, don't follow it. Do not "upgrade" this file with new trading rules; new rules belong in the philosophy layer via a `philosophy/_proposals/*.md` draft, not here.

---

## 0. First action, every session — no exceptions

Before you read a single `raw/` file or write a single line:

1. Read `sharks.md` (constitution).
2. Read `CLAUDE.md` (full operating rulebook — roles, boundaries, frequency modes, source grading, the 10-signal contract).
3. Read `philosophy/index.md` and the last 10 entries of `wiki/log.md`.
4. Read `philosophy/09-point-in-time.md` **before touching anything that lands in a backtest or in `outputs/`.**

If you skip step 4 and write wiki content without an `as_of_timestamp`, you are silently corrupting every future backtest. That is the single most expensive mistake possible in this project.

---

## 1. The five hard boundaries (inlined so you can't miss them)

These are P0. Full text and rationale live in `CLAUDE.md §2` (document-evolution rule in `CLAUDE.md §9`); the short form:

1. **Never place trades.** No brokerage / exchange / wallet keys. The system emits *recommendations only*. Execution is a human action.
2. **Never modify `sharks.md`** (read-only; propose principle changes in a chat message). **Never edit `CLAUDE.md` directly** — propose changes as a chat-message diff (`CLAUDE.md §9`). The `philosophy/_proposals/*.md` draft mechanism is for `philosophy/` changes **only** — not for `sharks.md` or `CLAUDE.md`.
3. **Never modify files in `raw/`.** They are immutable inputs. To correct a source, add a dated `.v2` file and note the supersession in `wiki/log.md`.
4. **Never write to `wiki/` without `as_of_timestamp` frontmatter,** and **never import `as_of`-later data into an `as_of`-earlier analysis** (no lookahead — including "obvious" things like today's sector label on an old trade).
5. **Never invent tickers, prices, or earnings dates.** No source → write `TBD` and log a follow-up in `wiki/log.md`. **Never pad the daily 10-signal output** to hit 10 (`philosophy/05-decision-rubric.md`).

---

## 2. Declare your role on every writeback

The system runs three roles (full definitions in `CLAUDE.md §1`). Every wiki page must carry `author_role:`; every JSON output a `role:` field.

| Role | Job | May write | Must NOT write |
|---|---|---|---|
| **compiler** | `raw/` → `wiki/` pages | `wiki/01_macro_state`, `02_mag7_bottleneck`, `03_alpha_library`, `05_recommendations/*`, `log.md` | `sharks.md`, `philosophy/` |
| **researcher** | deep-dive an entity/bottleneck, extend wiki; web-sourced | `philosophy/entities/*`, new `wiki/` synthesis, `tech/<slug>.md` | `sharks.md`, the rest of `philosophy/` (only `entities/*` is writable; propose other changes via `_proposals/`) |
| **risk_officer** | gatekeeper before any `outputs/picks-*.json` or `wiki/05_recommendations/*` | inline `# [risk] …` comments, `wiki/positions.md` triggers | — |

The Risk Officer has **veto power**. Any pick that breaks the exclusion list (`philosophy/06-exclusions.md`), the position/sector caps or max-DD halt (`philosophy/08-risk-and-position.md`) is rejected — the Compiler rewrites, never overrides.

Mandatory wiki frontmatter minimum: `type`, `tags`, `as_of_timestamp`, `author_role`. Compiled pages additionally need `source_paths: [...]` and `confidence: 0..1`. Source-grade every ingested source `A`–`E` (`CLAUDE.md §5`); grade D/E may inform a watchlist but never open a position alone.

---

## 3. Multi-agent / worktree discipline (the part not in CLAUDE.md)

This is the only genuinely *new* content here — rules for running several agents in parallel across git worktrees.

- **Every agent loads its rulebook + §0 in every worktree before doing anything** — this file for non-Claude tools, `CLAUDE.md` for Claude Code. A worktree is a checkout, not an exemption. The shared memory is `sharks.md` + `CLAUDE.md`, full stop.
- **Commit small and often, with a role-tagged message.** A reviewing agent must be able to `git diff` a clean, attributable change. Suggested prefix: `[compiler] …`, `[researcher] …`, `[risk] …`.
- **Cross-review is mandatory before merge, not optional.** Have a *different* agent run `git diff main..<branch>` and check against `philosophy/06-exclusions.md`, `08-risk-and-position.md`, and — above all — `09-point-in-time.md`. A second model's read is worth more than a second pass by the author.
- **No output merges to `main` without passing the Risk Officer gate.** If the diff touches `outputs/picks-*.json` or `wiki/05_recommendations/*`, the Risk Officer role signs off or it does not merge. This gate is non-negotiable even under time pressure.
- **Parallelism never relaxes point-in-time.** Two agents racing on the same wiki page is exactly how an `as_of` timestamp gets clobbered. If two writebacks touch the same page, the later one adds a `## Contradiction (as_of YYYY-MM-DD)` section (`CLAUDE.md §3`) — it does not silently overwrite.
- **Suggested worktree layout** (rename freely; these are conventions, not law):

  | Worktree | Branch | Primary role | Typical agent |
  |---|---|---|---|
  | `research` | `research/<topic>` | researcher | web-strong model (Grok / Gemini) |
  | `compile`  | `compile/<date>`   | compiler   | reasoning-strong model (Claude) |
  | `review`   | `review/main`      | risk_officer | a *different* model than the author |

  Create with e.g. `git worktree add ../sharks-research -b research/<topic>`.

- **Tooling — `scripts/cross-review.ps1`.** The Main Orchestrator initiates a cross-review by running this script, which sends a target (a file / commit / git range / the working tree) to Grok headless (`grok --prompt-file`, read-only) and writes a timestamped report to `outputs/cross-review/`. Grok plays the Risk Officer reviewer; it never writes, commits, or trades. Usage: `.\scripts\cross-review.ps1 <target> [-Task "..."] [-Json] [-Effort high]` (default target `working`). This is the **read-only** path; it does **not** authorise a write-loop. See `wiki/25_cross_tool_agent_orchestration.md` for the fuller integration taxonomy.

- **Tooling — `scripts/grok-kol.ps1`.** Researcher-role pull of recent X/KOL chatter on a topic via Grok headless with web/X search on (`--permission-mode auto` — `default` blocks the search tool). Writes a **Grade-D** immutable capture to `raw/kol_signals/x-kol-<slug>-<date>.md` carrying `source_first_visible_at` + `ingested_at`. Value is **event detection + sentiment extremes only** — it can inform a watchlist but **never** triggers or sizes a position (CLAUDE.md §5; grade D never opens a position alone). `.\scripts\grok-kol.ps1 <topic> [-UseKolIndex] [-DryRun]`.

---

## 4. Frequency mode is set by market state, not the calendar

`low` (default) / `high` / `auto` — full rules in `philosophy/07-mode-switch.md` and `CLAUDE.md §4`. `high` requires VIX∈[12,18], no earnings within ±3d for any tier1/2 position, no Fed/CPI/NFP day, volume threshold met, **and** explicit opt-in (`SHARKS_HIGH_FREQ_OK=1`). A 5σ candle flips the mode back to `low` regardless of what the human's calendar says. "It's the weekend" is one input, not the trigger.

---

## 5. When in doubt

Re-read `sharks.md` → `philosophy/02-signal-taxonomy.md` conflict matrix → **ask the human.** Pausing beats committing a corrupted writeback.
