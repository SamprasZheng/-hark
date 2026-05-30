# INSPIRATIONS.md

Implementation-side mirror of `philosophy/references/open-source-inspirations.md`. The philosophy page explains **what** we borrow; this page tracks **when**, **into which module**, and **how** the borrowed code is adapted.

The 8 projects come from the Gemini-side discussion in `D:\DOT\$hark\gemini.md`.

---

## Borrow integration matrix

| # | Upstream | Phase | `$hark` module | Adaptation work | Status |
|---|---|---|---|---|---|
| 1 | `Ss1024sS/LLM-wiki` | 2 | `src/sharks/compile/` | Add `as_of_timestamp` discipline on top of Compile-first runtime; integrate with our `wiki/log.md` format | not started |
| 2 | `OpenClaw` + Awesome Finance Skills | 2 (intel) + 3 (orchestration) | `src/sharks/agents/macro_intel.py`, `src/sharks/agents/kol_intel.py` | Replace upstream Slack / Discord outputs with `raw/` file writes; apply our source grading rules | not started |
| 3 | `FinRobot` | 3 | `src/sharks/research/equity_report.py` | Adapt report template to our [[../philosophy/concepts/supply-chain-bottleneck]] framework; output to `wiki/02_mag7_bottleneck.md` | not started |
| 4 | `sdchen53/Sleipnir` | 3 | `src/sharks/retrieve/time_aware_rag.py`, `src/sharks/mode/router.py` | Time-Aware RAG enforces our [[../philosophy/09-point-in-time]] discipline; Dynamic Router maps to our `07-mode-switch` low/high/auto | not started |
| 5 | `TauricResearch/TradingAgents` | 3 | `src/sharks/agents/{fundamental,technical,sentiment,news}_analyst.py`, `src/sharks/agents/risk_team.py` | 4 analyst agents map to 4 dimensions in `02-signal-taxonomy`; Risk Team is our Risk Officer | not started |
| 6 | `FinStep-AI/ContestTrade` | 3 (Data Team) + 4 (Research scoring) | `src/sharks/compress/text_factors.py`, `src/sharks/scoring/authentic_feedback.py` | Compression layer keeps `wiki/` page sizes manageable; Authentic Feedback feeds [[../philosophy/concepts/td-9-sequential]] calibration | not started |
| 7 | `mariostoev/finviz` | 2 | `src/sharks/data/finviz_client.py` | Wrap upstream library; add `as_of_timestamp` (Finviz returns "current" — must caveat); apply [[../philosophy/06-exclusions]] post-filter | not started |
| 8 | `awoo424/algotrading` | 4 | `src/sharks/scoring/sentiment_fusion.py`, `src/sharks/backtest/multi_source.py` | VADER for headline / KOL sentiment scoring; multi-source feature fusion into backtest engine | not started |

---

## Licensing & legal

Before integration, each upstream is reviewed for:

- License type (MIT, Apache 2.0, GPL, AGPL, proprietary)
- Attribution requirements
- Patent grants

The default integration mode is "read, understand, adapt and rewrite to fit our discipline". Direct copy-paste of upstream code is **only acceptable when**:
1. License explicitly permits (MIT, Apache 2.0)
2. The function is small, well-defined, and adaptation would be substantively identical
3. Attribution is added in module docstring

GPL / AGPL upstream → we treat as design-inspiration only and write our own implementation. No code copying.

---

## Per-project integration notes

### #1 `Ss1024sS/LLM-wiki` (Phase 2)

The Compile-first runtime is the cleanest expression of Karpathy's pattern in Python. Their key abstraction is the "compile pass" — given a new source, the runtime:
1. Reads existing `wiki/` index
2. Identifies entity / concept pages that may need updates
3. Proposes diffs
4. Applies diffs (with optional human-in-the-loop approval)

For `$hark` we add:
- Mandatory `as_of_timestamp` on every diff
- Source-grade tagging on the diff record
- The Risk Officer gate before any diff that touches `wiki/positions.md` or `wiki/05_recommendations/`

### #2 OpenClaw + Awesome Finance Skills (Phase 2-3)

OpenClaw's SubAgent pattern matters because our `CLAUDE.md` decomposes agents by role (Compiler / Researcher / Risk Officer). The Finance Skills package provides ready aggregators that we can route into `raw/macro/` and `raw/kol_signals/`.

Caveat: many of the Chinese-language finance feeds (華爾街見聞, 財聯社) require careful source-grading: they're often C-grade republication of A-grade sources. Compiler should de-dup against the A-grade original where possible.

### #3 FinRobot (Phase 3)

The equity research report template is the most directly portable artefact. We use it to auto-generate the quarterly `wiki/02_mag7_bottleneck.md` regeneration pass after each Mag 7 earnings cycle.

Adaptation: rather than producing a free-form analyst report, output is structured to match our [[../philosophy/concepts/supply-chain-bottleneck]] framework (demand-pull, upstream wafer + packaging, memory, equipment, substitution map, trade ideas).

### #4 Sleipnir (Phase 3)

The Time-Aware RAG implementation is the canonical answer to our point-in-time problem. Their abstraction: every retrieval query carries an `as_of` parameter, and the retrieval index is structured so that documents not visible at `as_of` are filtered out.

For `$hark`: we already enforce `as_of_timestamp` in our wiki page frontmatter. Sleipnir's retrieval index implementation gives us the runtime that respects it at query time.

The Dynamic Router pattern — routing different reasoning tasks to different LLMs — maps to our cost-efficiency goal. The challenge: we don't yet have a clear taxonomy of which model fits which task. Phase 3 implementation starts with a simple rule (Compiler = Sonnet 4.6, Risk Officer = Opus 4.7, Researcher = Sonnet 4.6 with extended thinking) and iterates.

### #5 TradingAgents (Phase 3)

The cleanest mapping. The 4 analyst agents (Fundamental / Technical / Sentiment / Risk Team) match our 4 signal dimensions almost 1:1. The structured Debate pattern complements our matrix-based arbitration: the matrix gives the final answer, but the Debate process surfaces the disagreement clearly for the human reading the daily output.

Adaptation: our matrix in `02-signal-taxonomy.md` is more prescriptive than TradingAgents' free-form debate. We use the matrix as the binding rule, but record the analyst-agent reasoning in the daily output's `Discarded candidates` section for the post-hoc study mentioned in [[../philosophy/05-decision-rubric]].

### #6 ContestTrade (Phase 3-4)

The Data Team / Research Team split is brilliant for noise resistance. The Data Team's compression layer keeps wiki page sizes manageable as months of news flow accumulate.

For `$hark`: the Data Team output is the structured `wiki/01_macro_state.md` and `wiki/02_mag7_bottleneck.md` updates. The Research Team's "Authentic Market Feedback" scoring (only top-historical-accuracy agent outputs reach the final decision) is the Phase 4 addition — we score each scorer's track record from `wiki/05_recommendations/archive.md` and weight accordingly in future runs.

### #7 finviz library (Phase 2)

Direct wrap. The library does the HTTP + parsing; we add point-in-time discipline (Finviz returns current values; our wrapper records the timestamp and saves the CSV to `raw/market_data/finviz-*.csv`).

### #8 algotrading (Phase 4)

VADER sentiment scoring on KOL feeds is the cleanest sentiment signal we have access to (free, well-validated, documented). Their multi-source feature fusion code shows how to combine technical + sentiment cleanly into backtest features.

Caveat: VADER was trained on social-media text generally; it does not specialise in finance. We may need to retrain a smaller finance-specific sentiment model in Phase 5+.

---

## Adoption discipline (project-wide)

For each Phase that introduces a new borrowed integration:

1. **Read the upstream README + at least 2 representative source files**
2. **Write an integration spec page** in `philosophy/references/integration-spec-<project>.md`
3. **Cite the upstream in the module docstring** of any borrowed code
4. **Add a test that exercises the borrowed path** with our `as_of_timestamp` discipline applied
5. **Track upstream for material updates** (e.g. set a quarterly review reminder; the user has GitHub stars / RSS to monitor)

---

## What we do not borrow

Specifically rejected from open-source:

- **Trading-execution code**: there is no shortage of Python brokerage wrappers, but `CLAUDE.md` Section 2 prohibits brokerage integration. No execution code is borrowed.
- **Wallet / signing libraries**: same reason. The system does not custody private keys.
- **Pump-and-dump signal libraries** (some exist in the meme-stock space): explicitly antithetical to our [[../philosophy/concepts/farmer-mindset]] discipline.
- **Highly tuned scoring weights from unrelated domains**: starting weights must come from `$hark`'s own backtest, not from imported, unrelated calibrations. (Imported architecture: good. Imported numbers: usually bad.)
