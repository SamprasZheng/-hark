---
type: reference
status: proposal
tags: [roadmap, ai-quant-us, llm, rag, paper-trading, macro-analog, funding-chain, btc-cycle, proposal]
title: AI-Quant-US roadmap merge — paper-trade-only mode + mandatory OSS small-model integration
author_role: compiler
proposed_destinations:
  - docs/ROADMAP.md
  - CLAUDE.md
  - philosophy/concepts/funding-chain-rupture.md
  - philosophy/concepts/macro-analog-matching.md
  - philosophy/concepts/institutional-btc-anchor.md
  - philosophy/_proposals/btc-halving-cycle.md
  - philosophy/references/open-source-inspirations.md
  - philosophy/10-strategies.md
  - docs/LLM-BACKTEST-PROTOCOL.md
proposed_at: 2026-05-30T01:10:00-04:00
source_user_input: 2026-05-30 chat session — Project AI-Quant-US plan paste + clarification + reviewer-2 deep audit
---

# AI-Quant-US roadmap merge — PROPOSAL

> Draft proposal — a documentation-only merge of a user-supplied AI-quant trading architecture into the existing `$hark` Phase 2-6 roadmap. **No code is written in this proposal**; the proposal records direction, identifies overlap with the existing roadmap, flags constitutional conflict, and absorbs a second reviewer's audit which surfaced one foundational issue (LLM-in-the-loop backtest pollution) and several 2026-time-relevance corrections to the original draft.

## Promotion status (updated 2026-05-31)

Tracking which proposed destinations have landed as the proposal is incrementally executed:

| Proposed destination | Status | Note |
|---|---|---|
| `philosophy/concepts/funding-chain-rupture.md` | ✅ PROMOTED 2026-05-31 | concept page live; `src/sharks/regime/funding_chain.py` implemented (fetch is Phase-2 stub) |
| `philosophy/concepts/macro-analog-matching.md` | ✅ PROMOTED 2026-05-31 | concept page live; `src/sharks/regime/macro_analog.py` + `data/macro_analog_events/` implemented |
| `philosophy/concepts/institutional-btc-anchor.md` | ✅ PROMOTED 2026-05-31 | concept page live; `btc-halving-cycle.md` cross-referenced |
| `docs/LLM-BACKTEST-PROTOCOL.md` | ✅ DONE | runbook written (§11 defenses) |
| `philosophy/references/open-source-inspirations.md` | ⏳ pending | RAG (#11) + AWQ/Ollama (#10) entries — `rag_library.py`/`rag_retrieve.py` already coded |
| `philosophy/10-strategies.md` (Strategy D) | ⏳ pending | long-horizon dividend-cycle strategy — human-edit step |
| `docs/ROADMAP.md` Phase 2-6 patches | ⏳ pending | human-edit step |
| `CLAUDE.md` §2 paper-trade amendment | ⏳ pending | human-edit step (constitutional) |

The three concept pages above are now canonical (`type: concept`, not `status: proposal`) and indexed in `philosophy/index.md`. Their implementation modules already exist under `src/sharks/regime/`. The remaining destinations are deliberately human-edit steps (constitution, roadmap, strategies) per the `_proposals/` workflow.

## 1. Background

User supplied a "Project AI-Quant-US" architecture (OpenClaw agent cluster + NemoClaw guardrails + MCP data server + QLoRA Llama-3-8B + AutoAWQ INT4 + vectorbt real-time backtest + Alpaca/IBKR execution). The proposal sits behind several user-clarified constraints:

- **No real-money execution** — paper-trading proposals and zero-cost simulators only.
- **Low frequency** — daily / weekly cadence, never tick / minute-bar scalping.
- **Long-horizon swing + dividend + trend-reversal** as the strategic emphasis.
- **100-year macro-analog pattern matching + funding-chain rupture detection** as a new strategic theme — dotcom / subprime / 2025-style.
- **BTC 4-year halving cycle thesis may be broken** by institutional ETF accumulation; requires update.
- **Open-source small-model integration is mandatory**.
- [[../../CLAUDE]] may be amended to accommodate the paper-trade allowance.

A second-pass reviewer audit (2026-05-30) corrected several time-sensitive errors and surfaced one previously-omitted foundational risk. Both rounds of input are integrated below.

## 2. Mapping — AI-Quant-US module → existing $hark Phase

| AI-Quant-US module | Existing $hark home | Status |
|---|---|---|
| MCP data server | Phase 2 (yfinance / polygon / finnhub / finviz / ccxt) | OVERLAP — add MCP façade |
| 基本面 / 情緒 / 技術 agents | Phase 3 4-dim scorers (`fundamental.py` / `news.py` / `technical.py` / `sentiment.py`) + Compiler role per [[../../CLAUDE]] §1 | OVERLAP — "OpenClaw agent cluster" ≈ existing role split |
| vectorbt real-time backtest | Phase 4 backtest framework | OVERLAP |
| Walk-forward training automation | Phase 4 walk-forward statement | EXTENDS — automation new |
| Hard constraint check on trade size | [[../08-risk-and-position]] | OVERLAP |
| Kill switch (NAV drawdown) | Phase 4 max-DD halt + [[../08-risk-and-position]] | OVERLAP |
| Importance filter (Reuters / Bloomberg only) | Source grading A-E per [[../../CLAUDE]] §5 | OVERLAP |
| Llama-3-8B QLoRA | Beyond-Phase-6 open question | PROMOTE — BUT see §5 #11 (RAG-first, QLoRA deferred) |
| AutoAWQ INT4 quantization | nothing | NEW |
| TimescaleDB | nothing | REJECTED — see §3 Phase 2 |
| Alpaca / IBKR auto-execution | [[../../CLAUDE]] §2 forbids | CONFLICT — replaced by paper-trade allowance in §7 |
| 1h / 1m bar high freq | Phase 6 high-freq mode | SOFTEN — user wants low frequency |

## 3. ROADMAP patches (specific edits proposed)

### Phase 2 — storage discipline

Skip the TimescaleDB question entirely. The point-in-time correctness lever is **data vintage**, not storage engine. Macro series (GDP, payrolls, NFP, etc.) are revised multiple times after first publication; storing only the latest value introduces silent lookahead.

Mandatory at Phase 2:

1. **FRED ALFRED integration** — for every FRED series, pull from the ALFRED endpoint with `vintage_date`; store each `(series, vintage_date, observation_date, value)` tuple as immutable.
2. **Storage architecture** — Git tracks code + small JSON configs; bulk time-series lives in date-partitioned Parquet under `data/lake/` (already exists in repo). Git does NOT track Parquet payloads (would balloon history); only commit **content-hash manifests** (`path / sha256 / row_count / vintage_date_range / ingested_at`). Payload lives in local-only / off-Git storage.
3. **Query layer** — **DuckDB over Parquet**, zero-server, queries partitions directly. Matches `$hark`'s file-based purity. The right answer regardless of whether performance demands a DB.
4. **TimescaleDB explicitly rejected as primary store**.

### Phase 3 — local small-model integration (RAG-first)

PROMOTE the local-small-model capability from Beyond-Phase-6 to a Phase 3 hard deliverable. `src/sharks/ai/local_llm.py` (already exists per [[../../wiki/21_internalization_local_llm]]) extended for **retrieval-augmented generation over past recommendations**, NOT for QLoRA fine-tuning at this stage. Rationale in §5 #11 below.

Base-model selection — bench at least three before committing:
- **DeepSeek-R1-Distill-Qwen-7B** (Qwen base is empirically more reliable for strict-JSON structured output in 2026 than Llama-distill).
- **DeepSeek-R1-Distill-Llama-8B**.
- **Llama-3-8B-Instruct**.

R1-Distill emits `<think>...</think>` reasoning before the answer; conflicts with grammar-constrained JSON. Mitigation: **two-stage prompting** — first call produces the `<think>` block freely, second call (or schema-constrained continuation) produces the strict JSON. Do not force grammar constraints onto R1 in a single shot.

Inference backend: **Ollama / llama.cpp (native Windows, GGUF format)**. NOT vLLM (high-concurrency batched serving is irrelevant for single-user single-machine; vLLM on Windows requires WSL2). Quantization–engine binding is hard — **vLLM consumes AWQ; llama.cpp consumes GGUF; the two cannot be mixed**. ("GGML" mentioned in the source plan is obsolete; current name is GGUF.)

`src/sharks/ai/local_llm.py` is a thin OpenAI-format HTTP client against the local Ollama daemon, NOT a hand-rolled AWQ inference loop.

RTX 5070 VRAM budget (12 GB total): Llama-3-8B and Qwen-7B both use GQA (8 KV heads), so 4096-ctx K-V cache ≈ **0.5 GB** (not 1.5–2 GB). Pure inference: INT4 weights ≈ 5 GB + K-V 0.5 GB + OS overhead ≈ **6 GB peak**. Inference alone has plenty of headroom.

QLoRA training blows the budget: optimizer state (8-bit Adam) ≈ 16 GB + activations ≈ 10-11 GB even with grad checkpointing + bs=1. Training and inference cannot coexist on the same GPU. Mitigation is **operations-level serialization (NOT code-level mutex)** — the weekly training job stops the Ollama daemon, runs QLoRA to completion, persists the adapter, then restarts Ollama. Documented as a Phase 4 deployment runbook. (Note: QLoRA itself is deferred per §5 #11; the runbook applies if/when fine-tuning is revisited.)

### Phase 4 — walk-forward + paper-trade outcomes

Add deliverable "walk-forward fine-tuning automation IF re-enabled" — gated behind §5 #11 thresholds. NON-NEGOTIABLE: walk-forward boundary respects [[../09-point-in-time]].

Add deliverable "paper-trade outcome ingest" — Alpaca Paper API fills, when used, write `wiki/05_recommendations/<date>-<slot>-fills.json` with realised forward returns. These outcomes feed the RAG library per §5 #11.

### Phase 5 — paper-trading allowance

SOFTEN the "No execution capabilities" line. Replace with: *"No real-money execution. Paper-trading via Alpaca Paper API (or equivalent zero-cost simulator) is permitted, gated by Risk Officer audit per [[../08-risk-and-position]] and the kill switch in [[../../wiki/10_defensive_hedging]]. All paper-trade outcomes are logged into `wiki/05_recommendations/` 30-day forward returns for the RAG library."*

### Phase 6 — high-freq mode softened

Cadence per user: daily / weekly evaluation; 1h cadence only for paper-trade entry timing after a multi-day thesis fires. Real-money execution remains forbidden (deferred until paper-trade KPIs validate).

### Beyond Phase 6

Add open question "When (if ever) does paper-trade graduate to real-money?". Answer template: requires (a) Sharpe > 1.0 on out-of-sample test, (b) MDD < 25 % on test, (c) win rate > 50 % on Strategy A's signal set, (d) explicit human authorisation entered into [[../../wiki/log]] with `recommendation` action. None are met.

## 4. New strategic theme — macro-analog matching + funding-chain rupture detection

### `philosophy/concepts/macro-analog-matching.md`

Methodology for matching the current macro state against 100-year historical analogs. Case studies: 1929, 1937, 1969, 1973, 1987, 2000 (dotcom), 2008 (subprime), 2020 (covid + reflation).

**Dimension reduction via human-defined economic axes, not learned embeddings**. Collapse all candidate features into a **3-4 axis regime cube** — Growth, Inflation, Liquidity, Credit. Each axis = a small handful of intuitive sub-indicators (e.g. Growth = real GDP YoY + ISM + ADP; Inflation = headline CPI + 5y BEI; Liquidity = M2 YoY + NFCI; Credit = HY OAS + IG-HY divergence + SLOOS). Humans define the axes; dimensionality stays ≤ 4. Sidesteps the high-dim distance-concentration problem.

**Output as mechanism set, not single-year nearest neighbour**. Replace "you are 87 % similar to 1973" (over-fits the 1-of-10 problem) with "the following mechanisms are simultaneously present: yield curve inversion ✓, real-rate tightening ✓, credit-spread widening ✓, currency tail strain ✗ — closest historical episodes where this combination held: 1929 Q3, 1969 Q4, 2000 Q1; what happened next in those episodes …". Distribution of analogues, not winner-take-all label.

**Decision-support framing, NOT predictive quant**. Module's purpose: generate hypotheses + checklists ("1973 trigger was X; is X present today?"). Forbidden to convert output into a probability or directional signal. Risk-Officer veto trigger if violated.

Storage: `philosophy/concepts/macro-analog-events/<year>.md` — one immutable, human-curated file per labelled episode, carrying the (G, I, L, C) classification + mechanism set + T+1y / T+3y / T+5y outcome + a "what was actually visible at the time" notes section.

ML clustering gate: forbidden until ≥ 50 labelled events with ≥ 5 per archetype (boom-top / deflation-bust / stagflation / exogenous-shock / policy-pivot). Even then, only as a prior over the human axis labels.

Implementation hook: `src/sharks/regime/macro_analog.py` — body is a lookup + mechanism-set-intersection function; no clustering, no embeddings.

### `philosophy/concepts/funding-chain-rupture.md`

Leading-indicator framework for "why bubbles pop". Stratified by latency.

**Tier-1 (daily, market-priced, leading)**:
- **SOFR-OIS basis / term-SOFR vs OIS** — replaces FRA-OIS, which is obsolete (USD LIBOR ceased mid-2023, so the classic 3m-LIBOR-FRA-vs-OIS series no longer exists).
- **SOFR vs IORB (or share of SOFR volume above IORB)** — replaces raw SOFR-EFFR, which carries month-end / quarter-end collateral seasonality that is NOT systemic stress. Filter for persistent (≥ 5 day) elevation, or use SOFR-IORB.
- **Cross-currency basis (EUR-USD, JPY-USD 3m)** — canary for global USD funding stress.
- **CDX IG financials sub-index + KBW Banks relative performance + sub-debt spreads + bank put skew** — replaces single-name bank CDS, which has thin post-2008 daily liquidity and is licensed (Markit / IHS) data inaccessible to an individual project.
- **HY OAS** (FRED `BAMLH0A0HYM2`) — daily, ~1 trading-day lag. Market-priced and timely, despite living on FRED.

**Tier-2 (weekly, baseline)**: **Chicago Fed NFCI** + **St. Louis Fed FSI** as composite anchors; MMF outflows; CP outstanding (FRED H.15 / DTCC).

**Tier-3 (quarterly, confirmatory only — NEVER trigger entry/exit alone)**: SLOOS bank lending standards.

The previous "FRED is all lagging" framing was too coarse: it conflated FRED's survey/aggregate data (lagging — SLOOS, H.8 deposits, CP totals) with FRED's market-priced mirrors (timely — HY OAS, SOFR, Treasury yields, NFCI). The fix is per-series classification.

Implementation hook: `src/sharks/regime/funding_chain.py`. Case studies: 2000 (CMBS + dotcom margin debt), 2007-2008 (ABCP + Bear Stearns hedge funds), 2023 (SVB), 2025 (per [[../../wiki/01_macro_state]] Warsh-era policy shock sub-cycle).

### `philosophy/concepts/institutional-btc-anchor.md`

Hypothesis: institutional spot-ETF accumulation + corporate treasury holding (MSTR-style) has dampened the 4-year halving cycle's amplitude. Test: compare 2024-2026 BTC drawdowns vs 2014-2018 / 2018-2022 cycles, normalised for institutional vs retail share of float. If supported, [[btc-halving-cycle]] requires amendment or supersession.

## 5. Open-source small-model integration recipes — additions to `philosophy/references/open-source-inspirations.md`

### #10: AutoAWQ INT4 quantization + Ollama runtime

Recipe for compressing the chosen base model to ~5-6 GB so it fits on RTX 5070 with headroom. Inference served via **Ollama** behind an OpenAI-compatible HTTP API; `src/sharks/ai/local_llm.py` is a thin OpenAI-client wrapper. Verification: benchmark inference latency, target < 500 ms / signal on 4096-context. (vLLM as alternative path on Linux deployments only; AWQ format binds to vLLM, GGUF binds to Ollama / llama.cpp — they don't mix.)

### #11: RAG / few-shot retrieval over past recommendations — PRIMARY APPROACH (replaces QLoRA at this data scale)

**Why the original QLoRA recipe was wrong tool**: the system produces ~10-50 recommendation pairs per *week*. For an 8B base, weekly QLoRA at that signal-to-noise ratio is below the threshold where gradient distinguishes signal from sample-specific noise. No holdout large enough to detect silent regression. Worse: labelling completions with realised forward returns burns lookahead AND recent-winner-chasing directly into LoRA weights — **invisible and irreversible**. This is the closed-loop self-training → model collapse / belief calcification failure mode.

Fact-correction: LR 2e-5 is full-fine-tune territory; LoRA typical range is **1e-4 to 3e-4** — the original draft confused method with magnitude.

**Instead**: build a **RAG example library** of past recommendations and retrieve k-most-similar at decision time.

Schema (`data/recommendations_lake/<YYYY-MM-DD>-<slot>-<ticker>.json`):
- `as_of_timestamp` (PIT-honest — what was visible at recommendation time)
- prompt snapshot (compressed: regime label, top-N FOM, breadth verdict, key wiki paragraph citations)
- the recommendation (verdict, position size, invalidation triggers)
- **realised 30 / 60 / 90-day forward outcome** (populated post-hoc)
- **lookahead-safe embedding** (computed only from the as-of-time prompt)

Retrieval: at decision time for as-of T, retrieve k=5 historical recommendations whose embedded prompt is closest to the current prompt (cosine over a small local sentence encoder — BGE-small-en or similar; no external API). Few-shot context: "here is what we recommended when the macro state looked similar, and what happened afterward".

Why this dominates QLoRA at N≲1000: (a) zero training risk, (b) fully auditable — decision log shows exactly which past examples drove the answer, (c) instant rollback (delete bad examples), (d) base-model reasoning preserved unchanged, (e) no LoRA-version backtest-replay parameter.

When to revisit fine-tune: only after the lake accumulates **≥ 500 PIT-honest pairs** AND §11 LLM-pollution isolation protocol is in place AND retrieval-augmented prompting demonstrably underperforms what fine-tuning can deliver. Until then, fine-tune is the wrong tool.

Implementation hook: `src/sharks/ai/rag_library.py` (embed + write), `src/sharks/ai/rag_retrieve.py` (query). Integrate with `src/sharks/ai/local_llm.py`.

(Existing inspiration #9 FinGPT supplies finance-domain sentiment LLM weights to start from. Together: #9 weights → #10 quantization → #11 retrieval protocol.)

## 6. Strategic shift — long-horizon + dividend + trend-reversal emphasis

Patches to [[../10-strategies]]:

- **Strategy A** (consolidation-breakout) — keep, target horizon already months.
- **Strategy B** (momentum / short-side) — de-emphasise HFT short setups; emphasise **multi-quarter trend-reversal entries** (2022 ARK-style washout buy, 2018 Q4 reflation buy).
- **Strategy C** (cycle-resonance crypto) — downgrade per `institutional-btc-anchor` concept above.
- **NEW Strategy D — long-horizon dividend cycle capture** — enters dividend-aristocrat ETF / individual names when (a) macro-analog signals risk-off AND (b) dividend yield > 10-year UST + risk premium threshold; exits when reverse. Backtest target: Sharpe > 0.7, MDD < 15 %, window 1990-2026.

## 7. CLAUDE.md §2 amendment (proposed text)

Replacement for the current `Do not place trades.` bullet:

> - **Do not place real-money trades.** This project does not connect to brokerages, exchanges, or wallet private keys with execution privileges. The system may emit trade *proposals* and may execute *paper trades* via zero-cost simulators (Alpaca Paper API or equivalent) gated by the Risk Officer role per [[philosophy/08-risk-and-position]]. Real-money execution remains forbidden until the Beyond-Phase-6 graduation criteria (Sharpe > 1.0 / MDD < 25 % / win > 50 % on out-of-sample test) are met AND explicit human authorisation is logged in [[wiki/log]] as a `recommendation` action with the operator's signature.

Other §2 bullets unchanged (no sharks.md modification; raw/ immutability; no lookahead; no invented tickers; no padding).

## 8. Frequency / cadence policy

- **Default cadence**: daily evaluation at US EOD; weekly recommendation file.
- **Allowed escalation**: 1h cadence ONLY for paper-trade entry timing after a multi-day thesis fires.
- **Forbidden**: minute-bar / tick / order-book scalping.

## 9. Risks & open questions

- **Auto-execution temptation** — quarterly log review; `git grep -E 'submit_order|place_order'` must return zero hits outside paper-trading paths.
- **AWQ INT4 reasoning degradation** — Phase 3 deliverable includes per-quantization regression test on a held-out 50-prompt suite (macro reasoning, conflict arbitration, JSON output validity). Fall back: Q8_0 GGUF; final fall-back FP16 on a smaller model.
- **R1-Distill `<think>` vs strict JSON conflict** — mitigated by two-stage prompting protocol in §3 Phase 3.
- **Macro-analog dimension curse** — mitigated by 3-4 axis regime cube in §4.
- **Macro-analog "winner-take-all" misuse** — mitigated by decision-support framing + Risk-Officer veto trigger.
- **Vintage-honest macro storage** — mitigated by FRED ALFRED + content-hash manifest discipline in §3 Phase 2.
- **Storage engine purity** — mitigated by DuckDB-over-Parquet conclusion (TimescaleDB rejected).
- **Funding-chain indicator currency** — mitigated by SOFR-OIS / SOFR-IORB / CDX IG financials replacements + per-series FRED classification.
- **Closed-loop self-training / belief calcification** — mitigated by deferring QLoRA in favour of RAG.
- **Open-source model licenses** — Llama 2/3 community licence, DeepSeek MIT/Apache, Qwen Apache/conditional, etc. — re-verified at adoption per [[../../docs/INSPIRATIONS]] §Licensing.

## 11. LLM-in-the-loop backtest pollution — HIGHEST-PRIORITY foundational issue

> The original proposal omitted this entirely. Without resolving it, every ML/backtest claim downstream is invalid.

**The problem**: any LLM trained on data through 2024-2026 has read the post-mortems of 1929, 1937, 1973, 1987, 2000, 2008, 2020. A backtest that asks "would the model have correctly classified the 1973 regime?" is poisoned by training-set lookahead — the model is *recalling*, not *predicting*. The macro-analog system in §4 directly inherits this: "the current state most resembles 1973" may be true because 1973's outcome is in the model's weights, not because the model independently detected a 1973-like pattern.

**Why this matters more than any other ML detail**: an unsolved LLM-pollution problem makes every backtest run-able but uninterpretable. Sharpe / MDD numbers will look great because the model is silently leaking outcome information. The temptation to ship based on these numbers is precisely why this must be resolved before fine-tuning, before paper-trading graduation, before strategy promotion.

**Defenses** (mandatory before any LLM-involved historical backtest is reportable):

1. **Role restriction**. LLM is allowed to *generate hypotheses, build checklists, summarise mechanisms*. LLM is NOT allowed to output probability or direction signals on historical periods. Hard schema check: any LLM call invoked from the backtest path must return a structured object whose schema excludes `probability`, `direction`, `verdict`, `target`, `forecast`. Risk Officer rejects backtest runs whose LLM outputs contain any banned key.
2. **Walk-forward gating**. An LLM-involved backtest is valid ONLY on the time window *strictly after the base model's training cutoff* AND on prompts not subsequently fine-tuned. For DeepSeek-R1-Distill / Llama-3 / Qwen-7B, that yields a usable window of months to ~2 years. Backtest module's README declares the model cutoff used and the resulting valid window; runs outside that window are marked `cutoff_polluted: true` in output JSON and excluded from headline KPIs.
3. **Pre-training-cutoff baselines must be non-LLM**. For 1929-2024 portions of any historical study, the system uses ONLY the rule-based FOM scorer (Fix A + Fix D), the regime classifier (`src/sharks/regime/classifier.py`), and the to-be-built funding-chain + macro-analog modules — which are themselves human-curated lookup tables, not learned LLM functions. The LLM may *narrate* what these rule-based outputs imply, but the headline numbers come from the deterministic scorers.
4. **RAG isolation**. The RAG library (§5 #11) is exempt because retrieval at time T returns only examples with `as_of_timestamp ≤ T`, enforceable. Vintage-honest storage (§3 Phase 2) makes this auditable.
5. **Output marker**. Every backtest JSON output gains a top-level `llm_involvement` field: one of `none`, `narration_only`, `decision_input`, `decision_output`. Only `none` and `narration_only` runs are eligible for headline KPI reporting; the other two are exploratory only.

**Acceptance criterion**: a `docs/LLM-BACKTEST-PROTOCOL.md` runbook documents the protocol above. No LLM-involved backtest result is publishable without explicit reference to this runbook.

## 10. Acceptance checklist for human reviewer

- [ ] [[../../CLAUDE]] §2 amendment matches §7 above (or human-edited equivalent).
- [ ] Phase 2 storage section adopts FRED ALFRED vintage + content-hash manifest in Git + DuckDB-over-Parquet (no TimescaleDB, no raw Parquet in Git history).
- [ ] Phase 3 base-model bench includes Qwen-7B distill alongside Llama distill; R1-Distill two-stage prompting protocol documented.
- [ ] Phase 3 inference path uses Ollama / llama.cpp (GGUF), not vLLM (AWQ); the AWQ↔GGUF mutual exclusion is noted.
- [ ] Phase 3 VRAM analysis: GQA → 4096-ctx K-V ≈ 0.5 GB; mutex repositioned as ops-level serialization, not code-level mutex.
- [ ] Phase 5 "no real-money" language is unambiguous; paper-trading differentiated.
- [ ] New concept pages (`funding-chain-rupture`, `macro-analog-matching`, `institutional-btc-anchor`) approved or rewritten before move out of `_proposals/`.
- [ ] `funding-chain-rupture` uses SOFR-OIS basis (not FRA-OIS), SOFR-IORB (not raw SOFR-EFFR), CDX IG financials proxy (not single-name CDS), HY OAS via FRED `BAMLH0A0HYM2`, NFCI / FSI as baselines.
- [ ] `macro-analog-matching` uses 3-4 axis regime cube, outputs mechanism sets, framed as decision-support not predictive quant.
- [ ] Inspirations #10 (AWQ + Ollama) and #11 (RAG-first, QLoRA deferred) approved before move out of `_proposals/`.
- [ ] #11 RAG library schema includes PIT-honest `as_of_timestamp`, lookahead-safe embedding, post-hoc forward-return outcome; QLoRA gating threshold ≥ 500 pairs + §11 isolation protocol documented.
- [ ] Strategy D dividend-cycle long-horizon strategy approved before module skeleton commit.
- [ ] [[btc-halving-cycle]] amended to note institutional-anchor counter-thesis OR superseded.
- [ ] §11 LLM-in-the-loop backtest pollution defences documented; backtest output JSON carries the `llm_involvement` field; `docs/LLM-BACKTEST-PROTOCOL.md` runbook scheduled.
- [ ] No auto-execution wiring sneaked in. `git grep -E 'submit_order|place_order|alpaca.*trade|ibkr.*execute'` → zero hits outside paper-trading paths.

## 12. Out of scope

Tracked in the session plan file at `~/.claude/plans/working-tree-playful-map.md` (outside this repo) §4 and §5 (post-commit execution sequence): the actual code for any of the above. This proposal is documentation-only. Code lands phase by phase after human review per the `_proposals/` workflow in [[README]].
