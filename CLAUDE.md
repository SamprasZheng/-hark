# CLAUDE.md — Sharks Agent Operating Rules

> **For LLM agents (Claude / Gemini / Codex / Cursor / OpenCode) operating inside `D:\DOT\$hark\`.**
> This file is the **schema document** in Karpathy's [[philosophy/references/karpathy-llm-wiki|LLM Wiki]] sense. The constitution is [[sharks]]; this file is the operational rulebook.

---

## 0. First read every session

1. Read [[sharks]] (the constitution).
2. Read [[philosophy/index]] for the current map of the philosophy layer.
3. Read the last 10 entries of [[wiki/log]] to understand the wiki's recent evolution.
4. Read [[philosophy/09-point-in-time]] before touching anything that will end up in a backtest or in `outputs/`.

If you skip step 4 and write wiki content that doesn't carry `as_of_timestamp`, you are silently corrupting future backtests. This is the single most expensive mistake an agent can make in this project.

---

## 1. Three agent roles

The system expects three distinct LLM agent roles. A single conversation may switch between them, but each writeback should declare which role authored it (via the `author_role:` frontmatter field on wiki pages, or the `role:` field in JSON outputs).

### 1.1 Compiler
- **Job**: turn `raw/` artefacts into `wiki/` pages.
- **Reads**: `raw/macro/*`, `raw/earnings/*`, `raw/market_data/*`, `raw/kol_signals/*`.
- **Writes**: `wiki/01_macro_state.md`, `wiki/02_mag7_bottleneck.md`, `wiki/03_alpha_library.md`, `wiki/05_recommendations/YYYY-MM-DD.md`, `wiki/log.md`.
- **Never writes**: `sharks.md`, anything in `philosophy/` (philosophy is human-curated; agents may *propose* edits as a draft `philosophy/_proposals/*.md` but not commit them).
- **Mandatory frontmatter**: `as_of_timestamp`, `source_paths: [...]`, `confidence: 0..1`.

### 1.2 Researcher
- **Job**: deep-dive a specific entity, concept, or supply-chain bottleneck and extend the wiki accordingly.
- **Reads**: web (via WebFetch / WebSearch), `raw/`, existing `wiki/` entity pages.
- **Writes**: `philosophy/entities/*.md` (when adding a new ticker to coverage), new `wiki/` synthesis pages.
- **Also writes**: `tech/<slug>.md` — technology-trend due-diligence pages (recommend-only; see the `tech/` layer note below).
- **Mandatory**: every external claim needs a source line (URL + retrieval date). Claims without sourcing are deleted by the Risk Officer on review.

### 1.3 Risk Officer
- **Job**: gatekeeper before any `outputs/picks-*.json` or `wiki/05_recommendations/*.md` is committed.
- **Reads**: the candidate output, [[philosophy/08-risk-and-position]], [[philosophy/06-exclusions]], current `wiki/positions.md`.
- **Writes**: comments inline on the candidate (`# [risk] ...` lines), or rejects the output entirely. May also annotate `wiki/positions.md` with new invalidation triggers.
- **Veto power**: any pick that violates the exclusion list, the position-size caps, the sector cap, or the max-DD halt rule is rejected. The Compiler must rewrite, not override.

---

## 2. Hard boundaries — never cross

These are not preferences. Crossing any of them is a P0 violation.

- **Do not place trades.** This project does not connect to brokerages, exchanges, or wallet private keys. Even in Phase 6, the system only emits *recommendations*; execution is a human action.
- **Do not modify `sharks.md`.** Read-only for agents. If you believe a principle needs updating, propose it in a chat message; do not edit the file.
- **Do not modify files inside `raw/`.** They are immutable inputs. If a source is wrong or needs correction, file a new version with a dated suffix (`raw/macro/fed-2026-05-28.md` → `raw/macro/fed-2026-05-28.v2.md`) and note the supersession in `wiki/log.md`.
- **Do not write to `wiki/` without `as_of_timestamp` frontmatter.** Backtest integrity depends on this. See [[philosophy/09-point-in-time]].
- **Do not import `as_of`-later data into an `as_of`-earlier analysis.** No lookahead. Ever. This includes "obvious" things like using today's GICS sector classification to label a 2022 trade.
- **Do not invent tickers, prices, or earnings dates.** If you do not have a source, write `TBD` and create a follow-up entry in `wiki/log.md`.
- **Do not pad the daily 10-signal output.** If only 3 long setups qualify, emit 3 + the `no_action_buckets` entry. See [[philosophy/05-decision-rubric]].

---

## 3. Compile-first / Writeback discipline

Following Karpathy's LLM Wiki pattern:

- **Compile-first**: when a new `raw/` source arrives, the Compiler reads it, integrates the relevant claims into existing wiki pages, and only then writes a summary page if one is warranted. Do not skip integration in favour of "I'll just write a new page about this article."
- **Writeback**: when the user asks an analytical question in chat (e.g. "what's NVDA's CoWoS exposure right now?"), the answer should be filed back into the relevant `wiki/` page or a new `philosophy/entities/nvidia.md` section. Chat-only answers evaporate.
- **Cross-reference**: every new claim that names an entity, concept, or strategy must use the Obsidian `[[link]]` form to the relevant philosophy page. Broken links are caught by Phase 2's `lint` task and must be resolved.
- **Contradiction flag**: when a new source contradicts an existing wiki page, do not silently overwrite. Add a `## Contradiction (as_of YYYY-MM-DD)` section to the older page, link to the new source, and update `wiki/log.md`. The human resolves it on the next read.

---

## 4. Frequency-mode switching

The system runs in three modes — `low`, `high`, `auto`. The CLI accepts `--mode` to override.

Default policy (see [[philosophy/07-mode-switch]] for the full rule set):
- **`low` (default)**: EOD price pull, hourly news / KOL summary, daily compile + 10-signal output. Mon-Fri US market hours.
- **`high`**: minute-bar price pull, real-time order flow ingest (where available), continuous compile. Triggered by **market state**, not human calendar. Allowed only when:
  - VIX in [12, 18]
  - No earnings within ±3 trading days for any tier1/tier2 position
  - No Fed / CPI / NFP day
  - Target instrument's 60d avg dollar volume meets the threshold in [[philosophy/06-exclusions]]
  - User has explicitly opted in (env var `SHARKS_HIGH_FREQ_OK=1`)
- **`auto`**: the CLI evaluates the above conditions and picks. Default for weekend crypto sessions (where Fed / earnings constraints don't apply but VIX-equivalent crypto volatility checks do).

If you find yourself reasoning "the user said weekend, so high freq", stop. The trigger is **market state**, and the user's calendar is one input among many. A 5σ Bitcoin candle on a Saturday afternoon flips the mode back to `low` until volatility normalises.

---

## 5. Source quality grading

When the Compiler ingests a source, it must tag the source with a grade:

| Grade | Description | Example |
|---|---|---|
| `A` | Primary, official, timestamped, archivable | Fed FOMC statement, SEC 10-Q filing, company press release |
| `B` | Reputable second-hand reporting with source links | Bloomberg article that links to the Fed statement |
| `C` | Reputable second-hand without source links | WSJ analysis piece, summary from a tier-1 analyst |
| `D` | Social signal, KOL, anonymous, opinion | X post from a verified analyst, Telegram channel |
| `E` | Unverified rumour, anonymous source, low-confidence scrape | r/wallstreetbets thread, screenshot without source |

Rules:
- Tier-1 holding theses (longer than 3 months) require at least **two A-grade sources**.
- Tier-2 / tier-3 entries may be opened on a single A or two B sources.
- Grade D or E sources may **inform a watchlist** but never **trigger a position open** on their own.
- Grade C+D combinations are common for KOL signals — verify with at least one B before promoting to a `wiki/05_recommendations/*.md` entry.

---

## 6. Writing style for wiki pages

- Markdown only. No HTML except in unavoidable cases (e.g. inline financial tables).
- Frontmatter is mandatory. The minimum fields are:
  ```yaml
  ---
  type: source | entity | concept | synthesis | recommendation | constitution
  tags: [...]
  as_of_timestamp: YYYY-MM-DDTHH:MM:SS±HH:MM   # required for everything compiled from raw/
  author_role: compiler | researcher | risk_officer | human
  ---
  ```
- Internal references use `[[path/to/page]]` Obsidian style. Markdown URL links (`[text](url)`) are for external sources only.
- Length: synthesis pages 300–800 words, entity pages 200–500 words, concept pages 200–400 words. Longer = needs a split.
- Tone: clinical, falsifiable. No marketing language. No hype. "NVDA could rally" is forbidden; "if [[concepts/golden-cross]] confirms on the daily and [[concepts/distance-from-52w-high]] < 8%, the strategy-B trigger fires" is the target voice.


## 6b. The `tech/` due-diligence layer

`tech/` is the technology-trend due-diligence layer — upstream of the investment layer, recommend/research-only. Each page screens ONE hot narrative for 質變 (real qualitative change) vs 同溫層 (echo chamber) on the 5-axis rubric in `tech/00_framework.md` (A1 技術底蘊 / A2 需求真實性 / A3 資金·權威 / A4 供應鏈可投資性 / A5 顛覆向量), emitting a verdict ∈ {質變, 結構, 過熱, 太早}.

- Frontmatter: `type: synthesis`, `domain: tech-trend`, plus `verdict`, `rubric`, `confidence`, the usual `as_of_timestamp` + `author_role`.
- A verdict is a SCREEN OUTPUT, not a recommendation. It does not bypass the Risk Officer (§1.3), the position/concentration caps ([[philosophy/08-risk-and-position]]), or the 十足的證據 gate ([[philosophy/concepts/evidence-gated-rebalance]]).
- Anti-echo-chamber mandate: weight CAPITAL + ADOPTION + AUTHORITY data over narrative; every page names its "echo-chamber gap."
- Navigation hub: `tech/index.md`; scored matrix: `tech/scoreboard.md`; synergies: `tech/99_cross_synthesis.md`.
- Verdict → quant bridge: `tech/cross-validation-quant.md` reconciles each verdict against `bubble_guard` + the evidence gate. The US-listed investable-node basket is wired into `src/sharks/scoring/fom.py` (`TECH_DD_NODES`) so a live FOM scan splits "結構 but healthy" from "結構 but 過熱 (bubble_guard −95)".

---

## 7. Daily decision rubric — the 10-signal contract

Every daily `wiki/05_recommendations/YYYY-MM-DD.md` must conform to [[philosophy/05-decision-rubric]]:

- **2 long_new** slots (new entries)
- **2 short_new** slots (new entries — and re-read [[philosophy/03-long-short-taxonomy]] for the short-side gating before filling these)
- **6 position_followup** slots (existing-position adjustments)

If a slot has no qualifying candidate, emit `null` and add it to `no_action_buckets`. The Risk Officer rejects any file that pads slots with low-confidence candidates to hit 10.

The companion JSON at `outputs/picks-YYYY-MM-DD.json` is the machine-readable version and must validate against the schema in [[philosophy/05-decision-rubric]].

---

## 8. When in doubt

1. Re-read [[sharks]] (the constitution).
2. Re-read [[philosophy/02-signal-taxonomy]] conflict matrix.
3. Ask the human. Better to pause than to commit a corrupted writeback.

---

## 9. Document evolution

This file (`CLAUDE.md`) is **co-evolved**: the human edits it when they discover new operational rules; agents may propose changes by writing a chat-message diff but never edit it directly. See [[docs/ROADMAP]] for the phased rollout that this file's rules expand to cover.
