# AGENTS.md — Cross-tool agent contract for `D:\DOT\$hark\`

> **For any non-Claude agent: Codex, Grok, Google Antigravity (Gemini), Cursor, OpenCode, etc.**
> Claude Code auto-loads `CLAUDE.md`. You probably don't. This file is a thin pointer to the canonical docs plus the multi-agent discipline they don't cover.
>
> **Canonical source of truth, in order:**
> 1. `CLAUDE.md` — the operating rulebook (roles, boundaries, source grading, the 10-signal contract).
> 2. `skills/project-program-skill-target/` — the **PPST** execution model (Project / Program / Skill / Target).
> 3. `RISK_OFFICER_SLA.md` — the review-gate spec.
>
> `_legacy/` holds the archived strategy/philosophy reference (history only, not active governance). If anything here disagrees with `CLAUDE.md`, **it wins and this file is wrong** — flag it, don't follow it.

---

## 0. First action, every session — no exceptions

1. Read `CLAUDE.md` (the operating rulebook).
2. Read `skills/project-program-skill-target/SKILL.md` (the PPST execution model).
3. Read the last 10 entries of `wiki/log.md`.
4. Apply point-in-time discipline (`CLAUDE.md §2`) before anything that lands in a backtest or in `outputs/`.

---

## 1. Hard boundaries (mirror of `CLAUDE.md §2`)

P0 — never cross:

1. **No trades.** No brokerage / exchange / wallet keys. Recommendations only; execution is a human action.
2. **No lookahead.** Anything compiled into `wiki/` or consumed by a backtest carries an `as_of_timestamp`; never use `as_of`-later data in an `as_of`-earlier analysis.
3. **`raw/` is immutable.** Correct a source with a dated `.v2` + a `wiki/log.md` note — never edit in place.
4. **No fabrication** (tickers / prices / earnings dates) → `TBD` + a `wiki/log.md` follow-up.
5. **No padding** the 10-signal output — unfilled slots are `null` / `no_action`.
6. **No ingest-edits to governance.** `CLAUDE.md`, `AGENTS.md`, `RISK_OFFICER_SLA.md` change only via a reviewed diff with human sign-off. `_legacy/` is read-only.

---

## 2. Roles & declaration

Three PPST roles (full definitions in `CLAUDE.md §1`). Declare your role on every writeback (`author_role:` on markdown, `role:` in JSON).

| Role | PROGRAM scope | Must NOT touch |
|---|---|---|
| **Orchestrator** | PROJECT decomposition, `[CALL SKILL]` routing, integrating results | — |
| **Writer** | the single declared PROGRAM + its tests | other files; governance docs |
| **Risk Officer** | review reports (`outputs/cross-review/`), inline `# [risk] …` comments, `wiki/positions.md` triggers | — |

The Risk Officer has **veto power** over any capital-impacting artifact; the full trigger list + 5-section review format is in `RISK_OFFICER_SLA.md`. On veto the Writer rewrites — it never overrides.

---

## 3. Multi-agent / worktree discipline (the part not in `CLAUDE.md`)

- **Every agent loads `CLAUDE.md` + §0 in every worktree before doing anything.** A worktree is a checkout, not an exemption. The shared memory is `CLAUDE.md`, full stop.
- **Commit small and often, role-tagged.** A reviewer must be able to `git diff` a clean, attributable change. Prefix: `[orchestrator] …`, `[writer] …`, `[risk] …`.
- **Cross-review is mandatory before merge.** A *different* agent runs `git diff main..<branch>` and checks against the §1 boundaries — above all point-in-time. A second model's read beats a second pass by the author.
- **No output merges to `main` without the Risk-Officer gate.** If the diff touches `outputs/picks-*.json` or `wiki/05_recommendations/*`, the Risk Officer signs off or it does not merge — non-negotiable, even under time pressure.
- **Parallelism never relaxes point-in-time.** If two writebacks touch the same page, the later one adds a `## Contradiction (as_of YYYY-MM-DD)` section — it does not silently overwrite.
- **Suggested worktree layout** (conventions, not law):

  | Worktree | Branch | Role | Typical agent |
  |---|---|---|---|
  | `write`  | `write/<target>` | Writer | reasoning-strong model (Claude) or local Ollama for volume |
  | `review` | `review/main`    | Risk Officer | a *different* model than the author (Grok at high-stakes) |

  Create with e.g. `git worktree add ../hark-write -b write/<target>`.

- **Tooling — `scripts/cross-review.ps1`.** The Orchestrator initiates a cross-review: sends a target (file / commit / range / working tree) to Grok headless (`grok --prompt-file`, read-only) and writes a 5-section report to `outputs/cross-review/`. Grok plays the Risk Officer; it never writes, commits, or trades. `.\scripts\cross-review.ps1 <target> [-Reviewer grok|local] [-UseRag] [-Effort high]`. Read-only path; does not authorise a write-loop.
- **Tooling — `scripts/grok-kol.ps1` / `grok-kol-batch.ps1`.** Researcher-role pull of recent X/KOL chatter via Grok headless (web search on). Writes a **Grade-D** capture to `raw/kol_signals/`. Observation / sentiment-extreme only — **never** triggers or sizes a position (`CLAUDE.md §4`; grade D never opens a position alone). The batch variant runs a consensus universe from the quant outputs.

---

## 4. Frequency mode

`low` / `high` / `auto`, set by **market state**, not the calendar. `high` needs the VIX/earnings/macro/volume conditions **and** explicit opt-in (`SHARKS_HIGH_FREQ_OK=1`); a volatility spike reverts to `low`. See `CLAUDE.md §6`.

---

## 5. When in doubt

Re-read `CLAUDE.md` → **ask the human.** Pausing beats committing a corrupted writeback.

---

## 6. Operating discipline (privacy · commits · sources)

- **Privacy by default.** Portfolio holdings, KOL/social data (`raw/kol_signals/`), and personal-finance content are PRIVATE. Never push, publish, or send them to a public repo or external service without an explicit per-action human "yes".
- **Canonical source first.** For any trading/stock/portfolio question, read existing repo state (`wiki/`, `outputs/`, `watchlist/`, `portfolio/`) BEFORE any web/API pull. Grade-D web/KOL never overrides repo A/B/C analysis.
- **Scoped commits.** Stage only the files a change intends (`git add <paths>`); never `git add .` / `-A`. Commit only when asked; never `git push` private data; don't nag about `gh auth` (the human handles it).
- **PowerShell scripts ASCII-only** (this is a cp950 box); put non-ASCII content in a separate UTF-8 data file. Target PS 5.1; force `[Console]::OutputEncoding = UTF8` + `Get-Content -Encoding UTF8`.


# AGENTS.md — Multi-Agent Tournament & Skinner Box Contract

> System Governance: Multi-Agent Evolutionary Tournament (Layer 2).
> Target: Force agents to evolve higher risk-adjusted compounding returns through relentless Darwinian elimination.

---

## 0. Evolutionary Tournament Loop (Layer 2)
The framework operates as a continuous Skinner Box. Individual trader genomes are judged by their quarterly performance, reset to a base capital configuration each epoch to eliminate survivorship luck.

---

## 1. Agent Lineup & Personality Parameters

### A. Momentum Breakout Specialist (`LT_BREAKOUT`)
- **Core Intent**: Exploit price waves, platform extensions, and institutional trend-following loops (H黃靖哲飆股 DNA).
- **Hard weights**: Price-based = 0.55, Fundamental = 0.20, Sharpe = 0.25.
- **Guardrail Rule**: When market classification registers `AI_BULL_MOMENTUM`, override all TD-9 overbought signals. Ride the gamma squeeze to the absolute apex.

### B. Small-Cap Catalyst Hunter (`SMALL_CAP_HUNTER`)
- **Core Intent**: Scan low-base market capitalization names with sudden earnings/orders acceleration (Computex 2026 setups).
- **Hard weights**: Price-based = 0.40, Fundamental = 0.35, Sharpe = 0.25.
- **Pre-Filter Hook**: Block micro-cap assets with negative ROIC or declining gross margin trends to prevent luck-driven distortions.

### C. Risk & Frictional Analyst (`RISK_OFFICER`)
- **Core Intent**: Measure portfolio health and mathematical expectations.
- **Hard weights**: Price-based = 0.20, Fundamental = 0.35, Sharpe = 0.45.
- **Mandate**: Calculate execution drag. Apply sharp penalty multipliers $e^{-5 \cdot (MDD - 0.20)}$ if max drawdown breaches 20% barrier.

---

## 2. Dynamic Fitness Engine Formula
Genomes are evaluated at the end of each quarterly epoch via the unified hybrid score:

$$\text{Final Fitness} = (\text{Price Fitness} \times W_p) + (\text{Fundamental Score} \times W_f) + (\text{Sharpe Score} \times W_s)$$

- **Hard Clipping Trigger**: If an agent's projected monthly returns fall below the annualized opportunity cost of active capital leverage, the genome fitness is immediately clipped by 90%, forcing rapid generational replacement.

---

## 3. Autonomous Handoff Protocol (`grok agent stdio`)
When agents trigger a cross-review or state mutation debate, they must communicate via structured standard schemas:

```json
{
  "call_skill": "simulation.society_orchestrator.execute_society_epoch",
  "meta": {
    "author_role": "Orchestrator",
    "regime_context": "MEAN_REVERSION_HIGH_VAL"
  },
  "target": "outputs/recommendations.json",
  "payload": {
    "year": 2026,
    "quarter": "Q4",
    "allocation_leverage_allowed": true
  }
}
