# CLAUDE.md — Operating rulebook

> Operating rules for any LLM agent (Claude / Codex / Grok / Gemini / Cursor / OpenCode) working in `D:\DOT\$hark\`.
> This is an **engineering** rulebook. The execution model is **PPST** — `skills/project-program-skill-target/`.
> No philosophy framing: the legacy strategy/philosophy layer is archived under `_legacy/` for reference only, not active governance.

---

## 0. First read, every session

1. This file (`CLAUDE.md`) — the operating rulebook.
2. `skills/project-program-skill-target/SKILL.md` — the PPST execution model.
3. The last 10 entries of `wiki/log.md` — recent state.
4. §2 point-in-time — before anything that lands in a backtest or in `outputs/`.

---

## 1. Roles (PPST)

Every writeback declares its role (`author_role:` on markdown frontmatter, `role:` in JSON output).

- **Orchestrator** — owns the PROJECT; decomposes it into TARGETs; routes `[CALL SKILL]` handoffs; integrates results. Carries no long chat state — uses the four PPST layers + explicit `CONTEXT`.
- **Writer** — receives one PROGRAM + one TARGET; implements **only** inside that PROGRAM; writes tests; self-reviews before handoff.
- **Risk Officer** — gatekeeper before any capital-impacting artifact (`outputs/picks-*.json`, `wiki/05_recommendations/*`). Veto power. Full mandate, veto triggers, and the mandatory 5-section review format live in `RISK_OFFICER_SLA.md`. On veto the Writer rewrites — it never overrides.

---

## 2. Hard boundaries — P0, never cross

- **No trades.** No brokerage / exchange / wallet keys. The system emits *recommendations*; execution is a human action.
- **No lookahead.** Anything compiled into `wiki/` or consumed by a backtest carries an `as_of_timestamp`; never use `as_of`-later data in an `as_of`-earlier analysis (e.g. today's sector label on an old trade). This is the most expensive class of bug in a quant system — it makes backtests look brilliant and live results bleed. (Detail archived: `_legacy/philosophy/09-point-in-time.md`.)
- **`raw/` is immutable.** Inputs are never edited. Correct a source by adding a dated `.v2` file and logging the supersession in `wiki/log.md`.
- **No fabrication.** No invented tickers, prices, or earnings dates → write `TBD` and log a follow-up in `wiki/log.md`.
- **No padding** the 10-signal output (§5). Unfilled slots are `null` / `no_action`.
- **No ingest-edits to governance.** `CLAUDE.md`, `AGENTS.md`, and `RISK_OFFICER_SLA.md` change only via a reviewed diff with human sign-off — never as a side effect of a run. `_legacy/` is read-only history.

---

## 3. PPST execution contract

Full spec: `skills/project-program-skill-target/SKILL.md`. In short:

- Declare all four layers at the top of any work block:
  `PROJECT:` / `PROGRAM:` / `SKILL:` / `TARGET:`.
- Work **only** inside the declared PROGRAM. **One TARGET at a time.**
- Hand off (or call yourself / another agent) with a `[CALL SKILL]` block + minimal `CONTEXT:`.
- A TARGET is **done** only when: the artifact exists, review passed (self-review or a `CALL SKILL` to the Risk Officer), and the next handoff (if any) is stated with the four layers.
- Outputs are **structured artifacts** — JSON / JSONL wherever a schema exists.

---

## 4. Source grading A–E

| Grade | Description | Example |
|---|---|---|
| `A` | Primary, official, timestamped, archivable | Fed FOMC statement, SEC 10-Q, company press release |
| `B` | Reputable second-hand with source links | Bloomberg piece linking the primary |
| `C` | Reputable second-hand without links | WSJ analysis, tier-1 analyst summary |
| `D` | Social / KOL / opinion | X post, Telegram channel |
| `E` | Unverified rumour / low-confidence scrape | forum thread, sourceless screenshot |

- Tier-1 theses (> 3 months) require **≥ 2 A-grade** sources.
- Grade **D/E may inform a watchlist but never opens a position on its own**.

---

## 5. The 10-signal artifact contract

`outputs/picks-YYYY-MM-DD.json` (+ the `wiki/05_recommendations/YYYY-MM-DD.md` readout) carries exactly:

- **2 `long_new`**, **2 `short_new`**, **6 `position_followup`**.

Unfilled slots → `null`, listed in `no_action_buckets`. **Padding is a Risk-Officer veto trigger.** The producing PROGRAM is `src/sharks/daily_picks.py`.

---

## 6. Frequency modes

`low` (default) / `high` / `auto`, set by **market state**, not the calendar. `high` requires VIX ∈ [12, 18], no earnings within ±3 trading days on a held name, no Fed/CPI/NFP day, the 60-day dollar-volume threshold, and explicit opt-in (`SHARKS_HIGH_FREQ_OK=1`). A volatility spike reverts to `low`. (Detail archived: `_legacy/philosophy/07-mode-switch.md`.)

---

## 7. Artifacts, provenance & layout

- `wiki/` and `outputs/` artifacts carry frontmatter: `type`, `as_of_timestamp`, `author_role`/`role`; compiled pages also `source_paths: [...]` and `confidence: 0..1`.
- Markdown; clinical and falsifiable; no marketing language.
- Data flow: `raw/` (immutable inputs) → compiled `wiki/` state → `outputs/` daily artifacts. Integrate into existing pages before adding new ones.
- `tech/` is the technology due-diligence research layer (recommend-only; `tech/index.md`). `_legacy/` holds the archived strategy/philosophy reference.

---

## 8. Multi-agent discipline

See `AGENTS.md`: worktree isolation, **mandatory cross-review before merge**, and the **Risk-Officer gate** on anything touching `outputs/picks-*` or `wiki/05_recommendations/*`. Local-first (Ollama) for volume; Grok at high-stakes review gates via `scripts/cross-review.ps1`.

---

## 9. Change control

`CLAUDE.md`, `AGENTS.md`, and `RISK_OFFICER_SLA.md` are governance: changed only by a reviewed diff with human sign-off, logged in `wiki/log.md` — not by an unprompted agent ingest. The legacy strategy/philosophy layer is frozen in `_legacy/` (reference only).
