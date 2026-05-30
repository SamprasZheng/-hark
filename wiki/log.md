# Wiki Log

Chronological record of activity in the compiled wiki layer. Append-only.

Format per [[../philosophy/09-point-in-time]] and [[../CLAUDE]]:

```
## [YYYY-MM-DD HH:MM TZ] <action> | <short title>
```

Where `<action>` ∈ `{ingest, query, lint, recommendation, halt, universe, raw_deletion, build}`.

---

## [2026-05-29 17:00 TW] proposal | AI-trading inspirations gap-fill — 3 accept-candidates + 2 rejections + matrix patch

- **Scope**: external market scan of open-source AI-trading projects (LOBSTER, DeepLOB, FinRobot, FinGPT, Qlib, Backtrader+Gym/RL) audited against the existing 8-project list in [[../philosophy/references/open-source-inspirations]]. Gap = 5 projects; FinRobot already covered as inspiration #3. Rejection scope = inherited from [[../README]] "does NOT do HFT on US equities" structural rule.
- **6 proposal pages dropped under `philosophy/_proposals/`** (agent-proposes / human-commits per [[../CLAUDE]] §1.2 + §9):
  - [[../philosophy/_proposals/inspiration-09-fingpt]] — finance-domain LLM sentiment scorer for Compiler role; Phase 4; replaces VADER (inspiration #8) for finance text; runs locally on operator's RTX 5070 with 4-bit LoRA; license check pending
  - [[../philosophy/_proposals/inspiration-10-qlib]] — Microsoft MIT-licensed AI quant platform; Alpha158 candidate factor pool + backtest engine + model zoo; ★★★★★ fit; Phase 4–5
  - [[../philosophy/_proposals/inspiration-11-backtrader-finrl]] — license-split paired inspiration: Backtrader (GPLv3) design-only + FinRL (expected MIT) integrated; RL agent restricted to **sizing critic**, never entries/exits per constitutional + sample-efficiency + interpretability arguments; Phase 4–5
  - [[../philosophy/_proposals/considered-and-rejected-lobster]] — NASDAQ microsecond LOB data; rejected on 5 grounds (README structural / horizon mismatch / cost / no interaction with bottleneck alpha / infra burden); falsifiability table for re-evaluation included
  - [[../philosophy/_proposals/considered-and-rejected-deeplob]] — Oxford-Man CNN+LSTM LOB classifier; rejection inherits from LOBSTER + 4 additional DeepLOB-specific reasons (tick-horizon mismatch / streaming-vs-EOD / no interpretability / research-not-signal)
  - [[../philosophy/_proposals/inspirations-matrix-patch]] — literal copy-paste diff blocks for Patch 1 (open-source-inspirations.md: 3 numbered entries + integration map update + see-also link), Patch 2 (docs/INSPIRATIONS.md: 3 matrix rows + 3 per-project notes), Patch 3 (new file philosophy/references/considered-and-rejected.md as rejection aggregator)
- **Direction question (operator asked LOB-direction vs LLM-agent-direction)**: answered by the codebase itself — `$hark` is already an LLM-agent + multi-source-fusion system per [[../docs/ROADMAP]] Phase 3. Real question is gap-fill in the chosen direction: a finance-LLM (FinGPT), a quant factor library + backtest engine (Qlib), an RL sizing layer (FinRL). LOB direction structurally excluded by [[../README]].
- **Hard constraints respected** (none crossed): zero edits to existing `$hark` files; zero writes outside `philosophy/_proposals/` and this log entry; no `sharks.md` touch; no `raw/` touch; no `src/sharks/` scaffold; no execution code; no brokerage / wallet integration; no autonomous-loop wiring.
- **Open verification work for the human reviewer**: (a) verify license files at FinGPT / Qlib / Backtrader / FinRL repos before any code copy; (b) Phase-4 sprint-0 backtest engine 3-way decision (Qlib vs vectorbt vs from-scratch Backtrader-design); (c) before training PPO sizing critic, benchmark a deterministic [[../philosophy/concepts/cycle-resonance]]-gated Kelly sizer.
- **Files**: 6 created under `philosophy/_proposals/`, 1 updated (this log entry). 0 wiki content pages, 0 philosophy/ commits (proposals only). Rate-limit hits: 0 (no web fetches; facts cited from training knowledge with `**Unconfirmed:**` markers where verification needed).

## [2026-05-29 05:30 ET] build | FOM scoring system + AI Bubble Audit + IPO verification + 5 concepts accepted

- **New code modules**:
  - `src/sharks/scoring/cycle_bias.py` — multi-scale cycle bias scorer (BTC halving + Presidential + Calendar + Sector → combined ∈ [-1, +1])
  - `src/sharks/scoring/fom.py` — Figure of Merit multi-dimensional scorer (Momentum / Contrarian / Cyclic / Quality / BubbleGuard), 5 dimensions weighted 25/25/15/15/20 with persistence boost
- **Universe expanded** to 59 tickers: Mag 7 + AI supply chain Phase 1/2/3 + power semis (Serenity-inspired) + contrarian software (CRM/NOW/NFLX) + bubble watch (ORCL/OKLO/SMCI/ARM/AVGO) + DC infra (VRT/ETN/GEV) + materials (GLW/AMKR/TER) + defense (LMT/RTX/NOC) + beta anchors (JNJ/PG/KO/WMT) + R2K alpha (RKLB/ACHR/CRSP) + IWM ETF for R2K broad
- **Pages written**:
  - [[05_recommendations/2026-05-29-fom-monthly]] — first monthly FOM 3-pick + top-50 watchlist + bubble alerts
  - [[07_ai_bubble_audit]] — comparison to 2000/2008/1970s; tier-1 to tier-3 early-warning indicators; "next-to-break" list (6 names at bubble_guard -95)
  - [[05_recommendations/2026-11-buy-the-dip-candidates]] — Nov 2026 staging list (7 sector buckets) for activation trigger
- **Key empirical findings**:
  1. **Top 3 picks: META + LMT + MSFT** (after ORCL Principal-override substitution)
  2. **ORCL discrepancy**: FOM ranks #3 (contrarian recovery) but principal flagged as bubble breakdown — Compiler defers to human
  3. **6 names at maximum bubble stress (-95)**: AXTI, MU, STX, AEHR, SIMO, WDC — all in SOXX, mostly Memory + SiPh. These are next-to-break BEFORE the principal's named ORCL/OKLO/SMCI
  4. **NVDA / TSM still healthy**: bubble_guard +15 / 0 respectively. Principal's "NVDA TSM still standing" empirically verified
  5. **OKLO / SMCI weak as principal said**: both in low FOM rank with weak momentum
- **IPO pipeline VERIFIED** (WebSearch 2026-05-29):
  - SpaceX S-1 filed 2026-05-20, roadshow June 4, $1.75T / $75B
  - OpenAI confidential S-1 filed ~May 22, targeting Sept 2026
  - Anthropic targeting Oct 2026 listing, $900B valuation, first profit Q2 2026 (~$559M)
  - **All three IPOs land in Y2-midterm weakest window** (May-Oct 2026) — canonical "IPO trap" risk; system applies 90-day post-IPO blackout
- **5 concepts moved from `_proposals/` to `philosophy/concepts/` (user authorisation "全做")**:
  - `multi-scale-cycles.md`, `btc-halving-cycle.md`, `election-cycle-year-2.md`, `seasonal-monthly.md`, `sector-seasonality.md`
  - `philosophy/index.md` updated with "Cyclical" sub-section
- **Serenity profile expanded** with 4 advanced techniques from `serenity.md` archive: pass-through structure (EWY/SK Hynix), volatility mispricing on long-dated options, government subsidy backing (Chips Act), low P/B + multi-optionality (XFAB 5-way thesis)
- **November 2026 staging list** prepared 5 months ahead: DHI/CAT/EQIX as highest-conviction; activation trigger = SPX -10% drawdown OR VIX spike+retreat OR post-midterm-Nov resolution

## [2026-05-28 22:00 ET] initialise | Phase 1 wiki scaffold

- All wiki pages created as stubs with `status: stub` in frontmatter
- Compiler will replace stubs with compiled content in Phase 2 as `raw/` sources arrive
- This log entry serves as the t=0 timestamp for all subsequent point-in-time references

## [2026-05-29 03:30 ET] ingest+verify | Multi-scale cycle framework (BTC halving + election Y2 + seasonality)

- **Sources**:
  - [[../raw/macro/principal-cycles-2026-05-29]] (Grade A, principal directive)
  - [[../outputs/cycle-validation-2026-05-29.json]] (yfinance BTC 2014+, SPX 1980+, sector ETFs 2005+)
  - WebSearch: Fidelity, US Bank, Capital Group, IBKR on BTC cycle + presidential cycle + seasonality
- **Compiler-side analytics**:
  - Built `src/sharks/backtest/cycle_validator.py` — pulls BTC + SPX + NDX + 17 sector ETFs monthly history
  - Computed: BTC halving-relative returns (h2012-h2024), SPX presidential-cycle returns (Y1/Y2/Y3/Y4), SPX/NDX monthly seasonality, sector-ETF monthly seasonality
- **Pages updated**:
  - [[06_cycle_framework]] — **NEW** major synthesis page with full empirical numbers
  - [[01_macro_state]] §4a + §4b — current cycle position + IPO pipeline catalysts
- **Key calibration findings**:
  1. **2026 triple-cycle alignment**: BTC h2024 +25m post-halving (bottoming window 2026-Q4 to 2027-Q1) + US Y2 midterm (historically weakest) + Sell-in-May window. **All three say "caution May-Oct 2026, buy late 2026, hold through 2027".**
  2. **Post-midterm-Nov +12m has been positive 100% of the time since 1938** — highest-conviction macro setup the system has documented
  3. Principal's BTC "2026 halving" claim is factually wrong (next halving is 2028), but underlying intuition correct via "halving + 32 month bottom" rule
  4. Principal's "Sell in May" partially wrong: May itself is SPX's 2nd-strongest month (79% positive); September is the actual weak month (only negative month at -0.90%)
  5. Principal's "solar Dec rally" WRONG: TAN best month is January (+3.85%)
  6. Principal's "gaming summer rally" WEAK: HERO best month is November (+4.6%)
  7. Principal's "11月+12月 消費季" ✅ CORRECT
  8. Principal's "秋絕" ✅ CORRECT (Sep -0.90%, 46% positive)
- **Proposals filed in `philosophy/_proposals/`** (5 new):
  - `multi-scale-cycles-concept.md` — aggregator framework
  - `election-cycle-year-2.md` — Y2 midterm sizing rules
  - `btc-halving-cycle.md` — 4-year halving cycle phases
  - `sell-in-may-and-september-weak.md` — monthly seasonality
  - `sector-seasonality.md` — per-sector month-by-month
- **Operational implications for next 6 months**:
  - Reduce tier 1 + tier 2 sizing to 60-70% of standard caps May-Oct 2026
  - No fresh 6m+ bucket entries until post-midterm trigger
  - Enable defensive sectors (XLP, XLU) for May-Oct hedging
  - No fresh BTC longs until late 2026 cycle bottom signal
  - Stage Nov 2026 buy-the-dip universe scout starting October 2026

## [2026-05-29 02:00 ET] ingest+verify | Serenity KOL profile + yfinance narrative backtest

- **Sources**:
  - [[../raw/kol_signals/serenity-aleabitoreddit-profile-2026-05-29]] (Grade C, KOL profile aggregated from WebSearch results)
  - [[../outputs/narrative-validation-2026-05-29.json]] (yfinance monthly bars 2019-12 to 2026-05, 36 tickers)
- **Compiler-side analytics**:
  - Built `src/sharks/backtest/narrative_validator.py` — Phase 2 early data-pull + per-phase return analysis
  - Validated 7-phase narrative arc against actual prices; principal's P1 (TSLA leader) and P3 (NVDA leader) **verified**; P6 (NVDA leader) **REFUTED** — NVDA ranked #26 in P6 (+57%), real leaders were AXTI/Memory/Optical
- **Pages updated**:
  - [[03_alpha_library]] §H (Serenity framework + empirical verification) + §I (Memory cycle 縮量也不下跌 exemplar)
  - [[05_recommendations/2026-05-29-narrative-validation]] — new recommendation page with candidate shortlist + Phase 4 hypotheses
- **Key calibration findings**:
  1. **Leadership saturation invalidates standard tier-1 sizing**: NVDA $5T saturation → alpha rotates to supply chain → dynamic tier-1 cap needed (proposed `src/sharks/risk/saturation.py`)
  2. **Cycle-resonance threshold misses policy-shock sub-cycles**: 2025 SPX max DD only -7.8% (below 10% floor) but P6 recovery was historic. Proposed `philosophy/concepts/policy-shock-sub-cycle.md`
  3. **Memory catch-up rule**: 2024 flat MU + Mag 7 capex confirmation → 2025 +214%. Reproducible via sector-dispersion + upstream demand confirmation
- **Proposed `philosophy/` updates** (human review required):
  - New concept page: `policy-shock-sub-cycle.md`
  - New entity pages: `intel.md`, `vrt-vertiv.md`, `eaton-etn.md`, `ge-vernova-gev.md`, `asmi.md`
  - `philosophy/08-risk-and-position.md` saturation-adjusted tier-1 sizing rule
- **Current standing for next daily output**:
  - **No new positions today** — Phase 3 names at high, NVDA at top of range ($213 vs $180-220), Phase 4 candidates need Researcher entity pages first
  - Watchlist build: ANET (-9.7% from high; consolidation watch), FN (Phase 2 laggard), INTC (Agent AI CPU)
  - Inoculation: AXTI 78× chart is the canonical 分別心 trap — system inoculated by Phase 1 calibration findings

## [2026-05-29 01:00 ET] ingest | Principal narrative: 2020-2026 macro arc + regime shift to Warsh-era

- **Source**: [[../raw/macro/principal-narrative-2026-05-29]] (Grade A, principal-directive)
- **Pages updated**:
  - [[01_macro_state]] — promoted from stub to live; documents two-factor (AI + Trump) regime under Warsh-era Fed
  - [[03_alpha_library]] — added §A (2020-2026 7-phase macro arc), §B (5 cycle-resonance instances), §F (supply-chain bottleneck plays)
  - [[02_mag7_bottleneck]] — added §6 (supply-chain breadth: optical comms + CPU/Agent AI + Mag 7 cloud partnerships)
- **Key regime claims** propagated:
  1. Kevin Warsh succeeded Powell as Fed Chair (May 2026) with stated market non-intervention
  2. NVDA at ~$5T market cap (world's largest), range-bound $180-$220
  3. AI rally has broadened beyond pure GPU to optical comms, CPU+Agent AI, Mag 7 cloud partners
  4. Trump-policy is now the dominant macro variance source
- **Proposed `philosophy/` updates** (Compiler cannot edit; human review required per [[../CLAUDE]] §1):
  - `philosophy/entities/federal-reserve.md` should note the Warsh regime change
  - `philosophy/entities/nvidia.md` should note current $5T market cap and 180-220 range
  - `philosophy/entities/trump-administration.md` should note December 2024 tariff cycle → April 2025 de-escalation arc
  - Consider adding `philosophy/entities/intel.md` (Agent AI CPU thesis)
  - Consider adding 5 optical communications entity pages
- **Outstanding research items** (flagged in [[01_macro_state]] §7):
  - BTC behaviour during Dec 2024 - April 2025 tariff drawdown (gap)
  - Warsh hand-off precise date + transitional FOMC composition
  - NVDA $5T milestone precise as_of date
  - Optical communications candidate vetting against [[../philosophy/concepts/supply-chain-bottleneck]] validation checklist


## 2026-05-30 11:00 ET — Streamlit Page 11 (Deep Research + AI)
- Added 11th page **🧠 Deep Research + AI** to [[../src/sharks/ui/streamlit_app.py]]
- Page consumes [[../outputs/deep-research-2026-05-29.json]] (14 tickers) and lazy-imports [[../src/sharks/ai/local_llm.py]]
- Buttons: 📝 generate_thesis / 😈 generate_devils_advocate → call local Ollama (llama3.2:3b default)
- Outputs stored in st.session_state so switching tickers preserves prior runs
- Added bring-up helper [[../scripts/setup_local_llm.ps1]] — wraps check_ollama.ps1 + ollama pull + smoke test
- New synthesis [[22_streamlit_page11_deep_research_ai]] documents UI flow, philosophy linkage, safety boundaries
- Verified: streamlit_app.py SYNTAX OK (584 lines); http://localhost:8501 HTTP 200; lazy import resolves; Ollama currently DOWN (waiting on user pull)
- Aligns with [[21_internalization_local_llm]] internalization > scraping principle

## [2026-05-29 22:50 ET] ingest | Principal trade fills 2026-05-29 (P1 de-leverage + P2 peripheral basket)

- **Source**: [[../raw/principal/2026-05-29-fills]] (Grade A, principal_trade_log) — new `raw/principal/` subdir for principal-personal trade artefacts (parallel to macro/earnings/market_data/kol_signals)
- **Account A (複委託 8840-0767262, P2)**: 9 BUYS — LPL 30, HPQ 40, TBCH 30, RIVN 20, UEC 30, NTLA 20, AOSL 3, ORCL 2, BLDP 100. Thematic basket built around US laptop-peripheral universe + diversified small caps
- **Account B (US direct broker, P1)**:
  - SELLS: ORCX 10 @ $52.97, QBTX 10 @ $22.02, QUBX 10 @ $17.54, RGTX 10 @ $34.91, SMCL 3 @ $115.46, DELL 0.0291 (dust)
  - BUYS: ALGM 10 @ $51.84, CRWG $500 @ $39.77, HPQ 20 @ $26.74
  - Pattern: partial execution of audit SELL verdicts on ORCX/RGTX/SMCL per [[../outputs/portfolio-audit-2026-05-30]]; leverage rotation quantum/SMCI → CRWV (CoreWeave)
- **State diff vs current PORTFOLIO_1 / PORTFOLIO_2 in [[../src/sharks/backtest/portfolio_audit]]**:
  - New tickers introduced: LPL, TBCH, RIVN, NTLA, AOSL, BLDP, CRWG (not currently in audit)
  - HPQ now dual-account (40 sh P2 + 20 sh P1)
  - QUBX sold but not in PORTFOLIO_1 — verification flag
- **Follow-up required** (does not happen automatically):
  - Capture full P1 + P2 snapshots with % → refresh PORTFOLIO_1 / PORTFOLIO_2 hardcoded dicts in portfolio_audit.py
  - Re-run `portfolio_audit.py` after refresh to produce next-day audit reflecting these adjustments
  - 7 new tickers need entity coverage under `philosophy/entities/` before they can carry invalidation triggers in [[positions]]
  - Verify QUBX origin (held outside the tracked set, or stale sell?)

## [2026-05-29 23:15 ET] ingest | Full P1 snapshot + new Taiwan 台股 account 9A92 + NVDA RSU framing review

- **Sources added**:
  - [[../raw/principal/2026-05-29-snapshot-p1]] (Grade A) — full 32-position US broker P1 snapshot, sorted by mkt val; reconciles 1:1 against current [[../src/sharks/backtest/portfolio_audit]] PORTFOLIO_1 dict
  - [[../raw/principal/2026-05-29-snapshot-tw-etf]] (Grade A) — newly observed third account 9A92-0316376 holding 5 台股 ETFs (~NT$41K ≈ $1.3K USD)
- **Resolved verification flag from prior log entry**: QUBX **is** in PORTFOLIO_1 (1.70% / $193.80); the prior raw file note was incorrect and has been corrected in [[../raw/principal/2026-05-29-fills]].
- **Reclassified today's 2x leveraged ETF sells**: not "partial trim" — five positions liquidated 85–100% (ORCX 100%, SMCL 100%, QUBX 90%, QBTX 87%, RGTX 85%). ~$1,620 sold, ~$1,553 bought (ALGM/HPQ/CRWG) — cash-neutral rotation; ~14% of P1 cycled in one day.
- **P1 total NAV inferred**: ~$11,374 USD (from TARK 13.04% = $1,483.20).
- **Concentration framing**: P1 ≈ $11.4K, Taiwan 台股 9A92 ≈ $1.3K, 複委託 8840 P2 not snapshotted but appears small from fill sizes, **NVDA RSU $130K** ≈ NT$4.08M dominates. P1 ≈ 8.7% of NVDA RSU. Today's rotation cycled ~1.2% of total exposure. Aligns with [[12_employee_concentration]] §1 thesis that RSU sale schedule is the real concentration lever, not active-book rebalancing.
- **Audit code follow-ups** (queued for human review before edit):
  - Refresh PORTFOLIO_1 pcts post-trade (zero ORCX/SMCL, reduce RGTX/QBTX/QUBX to residuals, add ALGM/HPQ/CRWG)
  - Add `PORTFOLIO_TW` (or equivalent) for the 9A92 台股 account if it should be in audit scope
  - Decide whether NVDA RSU should be added as a tracked exposure or remain "shown via [[12_employee_concentration]] only"

## [2026-05-30 01:10 ET] proposal | FOM regime gating (Fix A) + universe +28 (Fix D)

- **Proposal page**: [[../philosophy/_proposals/fom-regime-and-universe-2026-05-30]]
- **Code paths touched** (in working tree, included in same commit):
  - NEW: [[../src/sharks/regime/classifier]] — regime classifier reads breadth + liquidity outputs, emits weights + bubble_guard floor for 5 labels (`bull_trend` / `late_bull` / `neutral` / `risk_off` / `capitulation`)
  - MOD: [[../src/sharks/scoring/fom]] — `FOMScore` threads regime weights + floor; `score_ticker` / `rank_universe` / `main()` accept optional `regime=` (backward compatible — `None` → canonical 25/25/15/15/20). `DEFAULT_UNIVERSE` 59 → 87 across HARDWARE_OEM / SPECULATIVE_NARRATIVE / QUANTUM / THEMATIC_2026_BUYS / WIKI_16_THEMES groups; matching `IP_DEFENSIBILITY` entries
- **Validated outputs** (not git-tracked per `.gitignore`'s `outputs/*.json` rule — regeneratable from code):
  - `outputs/regime-classification-2026-05-30.json` → label = `late_bull` (breadth OVERHEATED + liquidity YELLOW + SPX +10.82% above 200dma)
  - `outputs/fom-monthly-2026-05-29.json` regenerated under schema_version 2; AMD #5, MU #7, INTC #10, DELL #3, NEM #4 in new top 10 (vs pre-Fix AMD #23, MU #34, INTC #31, DELL not in universe, NEM not in universe)
- **Out of scope** (separate proposals to follow): Fix B (multi-horizon FOM_3m/12m/36m), Fix E (sector flow via XL* rotation), Fix F (regime sensitivity report), `leveraged_etf_scorer`, Taiwan ticker suffix handling

## [2026-05-30 01:10 ET] proposal | AI-Quant-US roadmap merge — paper-trade-only + mandatory OSS small-model integration + LLM-pollution defence

- **Proposal page**: [[../philosophy/_proposals/ai-quant-us-roadmap-merge-2026-05-30]]
- **User direction captured**: no real-money trade; paper trading allowed; low frequency (daily / weekly default; 1h escalation only on entry timing); long-horizon swings + dividend + trend-reversal as strategic emphasis; 100-year macro-analog matching + funding-chain rupture detection as new strategic theme; BTC 4-year halving cycle thesis to be revised against institutional-ETF anchor counter-thesis; mandatory open-source small-model integration; [[../CLAUDE]] §2 may be amended (paper-trade allowance) but real-money execution remains forbidden until graduation criteria met.
- **Documentation-only scope** (this proposal authors no code in this commit; code lands phase by phase after human review):
  - [[../docs/ROADMAP]] patches across Phase 2-6 (mapping table in proposal §2)
  - [[../CLAUDE]] §2 amendment text (proposal §7)
  - 3 new concept pages (proposal §4): `funding-chain-rupture`, `macro-analog-matching`, `institutional-btc-anchor`
  - 2 new open-source-inspirations (proposal §5): #10 AutoAWQ INT4 + Ollama runtime; #11 RAG / few-shot retrieval over recommendations (replaces QLoRA at this data scale)
  - Strategy D long-horizon dividend cycle (proposal §6)
  - `docs/LLM-BACKTEST-PROTOCOL.md` runbook scheduled
- **Reviewer audit absorbed** (highest-priority foundational issue surfaced in plan review):
  - **LLM-in-the-loop backtest pollution** — any LLM trained through 2024-2026 has read every post-mortem of 1929/1973/2000/2008/2020; macro-analog "this resembles 1973" cannot be trusted because the model already knows the outcome. Defenses in proposal §11: role restriction (LLM may not output probability / direction in backtest path), walk-forward gating (only valid post model cutoff), non-LLM pre-cutoff baselines (rule-based scorers only), RAG isolation (PIT-enforceable), `llm_involvement` output marker. No LLM-involved backtest publishable without `docs/LLM-BACKTEST-PROTOCOL.md`.
  - **2026 time-relevance corrections**: FRA-OIS obsolete (USD LIBOR ceased mid-2023) → SOFR-OIS basis / term-SOFR-vs-OIS; raw SOFR-EFFR carries month-end collateral seasonality → SOFR-IORB or persistence-filtered; single-name bank CDS data inaccessible → CDX IG financials sub-index + KBW Banks + sub-debt spreads + bank put skew proxies; "FRED is lagging" too coarse → per-series classification (HY OAS / SOFR / NFCI are market-priced and timely).
  - **VRAM math corrected**: Llama-3-8B and Qwen-7B both use GQA (8 KV heads) → 4096-ctx K-V ≈ 0.5 GB (not 1.5-2 GB). Inference alone has headroom; QLoRA blows the budget due to optimizer state. Mutex is ops-level (kill Ollama, run QLoRA, restart), not code-level.
  - **Engine choice corrected**: Ollama / llama.cpp (GGUF) on Windows native; NOT vLLM (batched-serving overkill for single user + Windows requires WSL2). AWQ↔GGUF cannot be mixed; "GGML" is obsolete naming.
  - **QLoRA → RAG demotion**: at N≈10-50 pairs/week, fine-tuning is the wrong tool — labelling completions with realised forward returns burns lookahead + recent-winner-chasing directly into LoRA weights, invisible and irreversible. RAG over a PIT-honest example library dominates QLoRA until ≥ 500 pairs accumulated AND §11 LLM-pollution protocol in place.
  - **TimescaleDB rejected**: the real PIT lever is data vintage (FRED ALFRED), not storage engine. Storage architecture is content-hash manifests in Git + date-partitioned Parquet outside Git + DuckDB query layer.
  - **Macro-analog dimension reduction**: 3-4 axis regime cube (Growth / Inflation / Liquidity / Credit), mechanism-set output not single-year nearest neighbour, decision-support framing not predictive quant. ML clustering forbidden until ≥ 50 labelled events × ≥ 5 per archetype.
- **Constitutional impact** captured but NOT executed in this commit: ~~Do not place trades~~ → "Do not place real-money trades; paper trading allowed under Risk Officer audit; real-money graduation criteria documented". Human edits [[../CLAUDE]] after proposal approval per `_proposals/` workflow §3-4.
- **Post-commit execution sequence** (per [[~/claude/plans/working-tree-playful-map]] §5): (1) Fix A pytest suite; (2) RAG example library prototype (replaces QLoRA in priority); (3) `docs/LLM-BACKTEST-PROTOCOL.md` runbook; (4) vintage / DuckDB storage layer; (5) QLoRA deferred indefinitely.

## [2026-05-30 02:30 ET] build | Implementation session — git init + 7 commits (Fix A pytest, RAG, Serenity, LLM protocol, RSU overlay, macro-analog, Fix B)

Private local git initialised in `$hark` (`git init -b main`, no remote, no push). Seven commits on `main`, full test suite **230 passed / 0 failed** (started 189/8 pre-existing failures → all cleaned).

- `8cb8729` Initial — Phase 1 scaffold + Fix A regime classifier + Fix D universe 59→87 + 2 proposals + `raw/principal/` trade ingest.
- `ddf5f4d` Fix A pytest — `tests/test_classifier.py` (39 tests): 5 regime labels, weights sum to 1, canonical-neutral backward compat, bubble_guard floor mechanic. + repaired the 2 new proposals' wikilinks.
- `d70ebf7` RAG library — `src/sharks/ai/rag_library.py` + `rag_retrieve.py` + `data/recommendations_lake/` schema (22 tests). PIT-honest example retrieval, REPLACES QLoRA at current data scale.
- `7d6e9c9` Serenity integration — `watchlist/serenity-supply-chain.yaml` (CPO/HBM/passives map) + `philosophy/concepts/serenity-supply-chain-bottleneck.md` analyst model + universe 87→91 (TSEM/MRVL/VPG/VSH). Also cleaned all 8 pre-existing `test_philosophy_links` failures + added 3 missing concepts to `index.md`.
- `9ceba44` LLM-backtest pollution runbook (`docs/LLM-BACKTEST-PROTOCOL.md`, 5 defenses) + NVDA RSU `concentration_context` block in `portfolio_audit.py` (RSU 89.2% / P1 7.8% of true exposure; audit schema_version 1→2).
- `2f7ade0` Macro-analog matcher — `src/sharks/regime/macro_analog.py` mechanism-set overlap (decision-support, NOT prediction; banned-key guard) + `data/macro_analog_events/` (2000-dotcom, 2008-subprime) (15 tests).
- `c439b86` Fix B multi-horizon — `FOMScore.horizon_scores` → fom_3m/12m/36m via `HORIZON_PROFILES`; output JSON carries horizon breakdown (13 tests).

**Tag**: `baseline-2026-05-30` at the initial commit.

**Still open** (not built this session): Fix E sector-flow (needs yfinance live data — logic testable with synthetic), `src/sharks/regime/funding_chain.py` (needs FRED ALFRED + market-data clients — Phase 2), vintage/DuckDB storage layer (Phase 2), the human-review-then-promote step for both `_proposals/` (CLAUDE.md §2 paper-trade amendment, ROADMAP patches, concept-page promotion). **Folder rename `$hark`→`sharks` explicitly declined by principal.**

## [2026-05-30 14:00 TW] ingest | Personal financial-advisor system — `wiki/personal/` 8-page cluster + MOC

- **Scope**: net-new personal-finance / long-range-tax / risk planning system, extending `$hark/wiki/` per principal direction ("擴充 $hark"). Distinct from the trading wiki (01–22) — placed in new subfolder `wiki/personal/` to avoid the numeric trading namespace and keep finances separated.
- **Driver**: principal is NVIDIA TW employee; income + assets ~89% NVDA (salary+RSU+ESPP+personal); ~NT$4M unsecured debt (玉山/國泰/永豐) from early-2025 crypto wipeout; monthly fixed outflow > net salary (gap funded by selling vests); committed pre-sale home (三重市政帝景, ~1,788萬, 1400萬 mortgage, ~2030 交屋); upcoming life events (marriage/children/education/parents' health).
- **Master principle captured**: 房/債/稅 must hold on a fixed schedule WITHOUT relying on offense (trading/raises); Alpha = accelerator, loss = bounded local damage (anti-2025).
- **8 pages + MOC created** under `wiki/personal/`:
  - [[personal/01_financial_profile]] — hub / single source of truth (balance sheet, income statement, monthly cashflow gap −22~27K, life-stage roadmap, 2025 context)
  - [[personal/02_debt_and_consolidation]] — DBR-22x as 2030-mortgage gating risk; 聯徵 30-day rate-shopping; consolidate-vs-not (目標函數 = 核貸過關); cites 金管會 + 聯徵
  - [[personal/03_house_funding_plan]] — real pre-sale schedule (150萬 paid → 55/46/46萬 → 91萬 交屋 → 1400萬 loan); mortgage stress test 2.0/2.3/3.0/4.0% → 5.2/5.4/5.9/6.7萬; cites 央行
  - [[personal/04_long_range_tax_plan]] — **corrected to 750萬 基本所得額** (dropped stale 670萬); AMT = overseas≥100萬 AND 基本所得額>750萬; unremitted realized overseas income reportable; rolling per-sale ledger; cites 財政部
  - [[personal/05_equity_monetization_schedule]] — **default-monetization-machine hard rule** (強制變現 = 稅 + 6mo cashflow gap + next house payment + quarterly debt target; remainder → hold/rotate-to-$hark/Alpha)
  - [[personal/06_cashflow_offense_and_guardrails]] — offense levers (NVIDIA perf / ESPP $97 lock / overseas income) + Alpha sleeve ≤5% liquid NAV, ban margin/naked-options/crypto-leverage, monthly+annual loss caps + 30-day cooldown
  - [[personal/07_stress_tests]] — 5 scenarios (NVDA−50% / 6mo unemployment / 2030 rate 3.5–4% / low RSU refresh / family medical +20萬) with pass matrix
  - [[personal/08_insurance_and_family_risk]] — emergency fund ~78萬 (biggest gap), term-life/disability/critical-illness/實支實付 priority, avoid 儲蓄險/投資型, life events
  - [[personal/index]] — MOC + capital-flow reconciliation (4-year sources ~NT$8–10M vs uses ~NT$8.2M+ → tight, NVDA-dependent) + stress matrix + Phase-0 input checklist + advisory cadence
- **Existing file updates**: [[12_employee_concentration]] — added pointer banner to `personal/`, corrected 670→750萬 tax note, marked old house assumptions superseded by personal/03, added See-also links. `wiki/index.md` — added 個人財務諮詢 section. (No trading-side numbers altered.)
- **Open (Phase 0 inputs, marked `TBD`, not fabricated)**: loan balances/rates/terms; Gogoro payment; living expenses; cash buffer; net-salary confirm; bank-recognized income for DBR; 2025 crypto loss + harvestable US losses; immediately-sellable vested NVDA; existing insurance policies; life-event timeline/budgets; 其他小存股 holdings.
- **Boundaries respected**: no stock-pick advice, no order placement, no money movement; buying decisions deferred to $hark rubric. No edits to `src/`, `raw/`, `philosophy/`, `sharks.md`.

## [2026-05-30 03:30 ET] build | Continuation — Fix E, Fix A/D promotion, funding_chain (3 more commits)

Extends the 02:30 build entry. Full suite **258 passed / 0 failed** across 12 commits.

- `033df07` **Fix E sector-flow** — `src/sharks/regime/sector_flow.py`: rank XL* sector ETFs by relative strength vs benchmark, `detect_rotation` (leaders/laggards/rotating_in/rotating_out), `sector_flow_score` 0-100 FOM factor. Pure-logic, 14 tests with synthetic prices.
- `e7e9e35` **Fix A/D promotion** — `philosophy/concepts/regime-gated-scoring.md` (canonical concept), `watchlist/universe.yaml` `tier2b_fom_expansion` group + PIT snapshot `watchlist/history/universe-2026-05-28.yaml`, `docs/ROADMAP.md` Phase 3 §7 note, proposal status proposal→promoted.
- `bff2753` **funding_chain** — `src/sharks/regime/funding_chain.py`: tier-1/2/3 indicator taxonomy (SOFR-OIS / SOFR-IORB / ccy-basis / CDX-IG-fin / HY-OAS daily; NFCI/FSI weekly; SLOOS quarterly weight-0), `funding_stress_score` → CALM/WATCH/STRESS/RUPTURE. Logic complete + 14 tests; `fetch_funding_indicators` is an explicit Phase 2 stub (FRED ALFRED). FRA-OIS deliberately absent (LIBOR ceased 2023).

**regime/ modules now**: classifier, breadth_indicator, liquidity_signals, sector_flow, macro_analog, funding_chain.

**Gap audit — still open**:
- **3 concept pages from the ai-quant proposal NOT yet promoted**: `funding-chain-rupture.md`, `macro-analog-matching.md` (code exists → these would document it like regime-gated-scoring did), `institutional-btc-anchor.md` (thesis only, no code). ← natural next close-loop.
- **CLAUDE.md §2 paper-trade amendment** — constitutional change, needs human.
- **Strategy D (long-horizon dividend)** — proposal text only, no code.
- **Phase 2 data layer**: FRED ALFRED + DuckDB/Parquet + content-hash manifests; MCP server wrapper. Blocks funding_chain live values + RAG-lake population.
- **Deferred by design**: Fix F (regime sensitivity report), leveraged_etf_scorer (P1's 28 槓桿 ETF), Taiwan/Korea ticker suffix handling, QLoRA fine-tuning (until ≥500 RAG pairs + LLM-pollution protocol live).
- **Folder rename `$hark`→`sharks`**: declined by principal.

## [2026-05-31 00:30 ET] build | Position consume + leveraged scorer wired + 3 concept pages promoted

Continuation of the 2026-05-30 session. Full suite **282 passed / 0 failed**.

- **Position consume** — `raw/principal/2026-05-30-snapshot-full.md` (A-grade source): all 14 broker screenshots digested into 5 pools. P1 "Individual" (~$11.4K, 33 positions, TARK 13.3% + ~44% leveraged ETFs); P2 複委託 graveyard (Evergrande/Fisker/Farfetch/GreenGiant/IMTE/NU-Ride all −90~−100%, survivors WOLF +88%/AAPB +22%/ICLN); 台股 9A92 dividend sleeve (0056/00878/00929/00965/00983A, all green, the model sleeve); 海外 DCA (GOOG/TSLA/NFLX); NVDA RSU vest schedule overlay. Order-Status screen confirms principal already SOLD ORCX/QBTX/QUBX/RGTX/SMCL (2x single-stock names) — self-directed de-leveraging.
- **Leveraged scorer wired into audit** — `src/sharks/scoring/leveraged_etf.py` extended: added inverse-index (SOXS/SPXU/SDOW, −3x) + VIX-futures (UVXY 1.5x / UVIX 2x / VXX 1x long-vol; SVIX/SVXY short-vol) with `vix_futures` contango-aware branch (VOL-HEDGE-DECAY vs SHORT-VOL-TAIL-RISK) + `bear_hedge_menu()` for 也怕大空頭 defensive reference. `portfolio_audit.py` now emits `p1_leveraged_audit` (worst-decay first: LABU 3x → 60.8% decay → SELL; TARK 2x → TRIM on weak ARKK), `leveraged_underlying_foms`, `bear_hedge_menu`. schema_version 2→3. +6 tests.
- **3 concept pages PROMOTED** to `philosophy/concepts/` (canonical, indexed): `funding-chain-rupture.md` (latency-stratified Tier-1/2/3 indicators, SOFR-OIS not FRA-OIS), `macro-analog-matching.md` (3-4 axis regime cube, mechanism-set output, BANNED_OUTPUT_KEYS non-prediction guardrail), `institutional-btc-anchor.md` (4-year-cycle counter-thesis; `btc-halving-cycle.md` cross-referenced). ai-quant proposal gains a Promotion-status table.

**Still open**: daily health-check capability (next), Strategy D, CLAUDE.md §2 paper-trade amendment (human), Phase 2 data layer (FRED ALFRED + DuckDB), open-source-inspirations #10/#11 entries.

## [2026-05-31 01:15 ET] build | Daily health-check capability + evidence-gated rebalance discipline

Closes the 2026-05-30 request set. Full suite **307 passed / 0 failed**.

- **Daily health-check** — `src/sharks/daily_health_check.py` (+ `sharks health-check` CLI, real not stub). Composes regime classifier + funding_chain stress + latest portfolio-audit + leveraged-decay flags + sector_flow hotspots into a recommend-only daily report (`outputs/daily-health-check-<date>.json`). Governing posture is a 交易老手's: **default to inaction; offense needs 十足的證據; defense may move fast; systemic risk overrides to DEFENSIVE + activates the bear-hedge menu**. Today's run → regime late_bull → NEUTRAL-CAUTIOUS, funding CALM (stub), DEFAULT-HOLD + STRUCTURAL-DECAY trim on LABU (60.8%/yr), hedges on standby.
- **Evidence gate** — `evidence_gate(evidence, action, systemic_risk)` encodes the 5-dimension 十足的證據 quorum (消息/資金/交易量/進出口/營利). Asymmetry is mechanical: offense needs ≥4/5 incl. mandatory earnings + a primary catalyst; defense clears on a systemic trigger OR ≥2/5. Absence of evidence ≠ evidence (every dim defaults UNCONFIRMED; only A/B-grade sources clear). +21 tests.
- **Concept page** — `philosophy/concepts/evidence-gated-rebalance.md` (canonical, indexed) documents the discipline; cross-links regime-gated-scoring + funding-chain-rupture + farmer-mindset.

**Session deliverable summary (2026-05-30 → 05-31)**: position consume (5 pools), leveraged scorer wired into audit (+VIX/inverse hedges + bear-hedge menu), 3 macro concept pages promoted (funding-chain / macro-analog / institutional-btc), evidence-gated daily health-check built. All local-only, recommend-only, no real trades.

## [2026-05-31 02:30 ET] build | FOM IC validation (accountability) + analyst-persona ensemble + daily/weekly routine

Response to principal challenge: "昨天建議的股票沒大漲，FOM 是否失準?". Answered with measurement, not defence. Full suite **339 passed / 0 failed**.

- **FOM predictive-validity backtest** — `src/sharks/backtest/fom_validation_backtest.py`: walk-forward cross-sectional Spearman IC of FOM vs realised forward returns (PIT, no lookahead, llm_involvement=none → headline-eligible). First run (2016-2026, 106 tickers, 112 periods): mean IC 0.04-0.06, **IC_IR 2.6-3.85, best horizon 6m**. BUT quintile spread NEGATIVE & widening (-1.3%→-37.8%) → **verdict RANK-EDGE-BUT-TOP-TAIL-MEAN-REVERTS**. Honest read: FOM has a real-but-weak rank edge at 3-6m (in-band for an equity factor), it is NOT a 1-day timer, and the extreme-top tail mean-reverts (confirms the original bubble_guard complaint, now measured). Caveats logged: survivorship bias + mean-spread outlier sensitivity (hit_rate, the robust stat, is mildly +ve 0.53-0.59). Interpreter initially over-claimed "EDGE-CONFIRMED" off IC_IR alone → corrected to reconcile IC vs spread vs hit-rate. +15 tests.
- **Analyst-persona ensemble** — `src/sharks/analysts/persona.py` + `analysts/README.md` + `_TEMPLATE.md`. Each `analysts/*.md` with `type: analyst-persona` frontmatter contributes a bounded (±0.08/dim) `fom_weight_tilt`; `ensemble_weights()` conviction-blends active personas onto the regime base weights and renormalises. Regime decides, personas nudge. Retrofitted `huang` (momentum/early-theme) + `sam` (contrarian/patient) as opposed live examples → blend nets mild-contrarian. +15 tests.
- **Daily/weekly routine** — `scripts/daily_routine.ps1` (DAILY 倉位健檢 = audit+health-check; WEEKLY Mon = FOM scan + IC re-check; earnings-season exception flag) + `scripts/install_scheduled_tasks.ps1` (user-scope schtasks installer — NOT auto-registered; principal runs it). Cadence = 以周為單位，每日不過多操作.
- **Concept pages** (canonical, indexed): `fom-predictive-validity.md`, `analyst-persona-ensemble.md`.
- Committed the `analysts/` roster (principal confirmed it is the intentional persona home) + Serenity KOL research notes (`serenity.md`).

## [2026-05-31 03:30 ET] build | Hotspot-prediction backtest — seasonality beats momentum (measured)

The 預測下一個熱點+驗證 loop. Full suite **351 passed / 0 failed**.

- **Hotspot sector-rotation backtest** — `src/sharks/backtest/hotspot_backtest.py`: walk-forward predicts next-quarter sector leaders from momentum-persistence + PIT seasonality, grades each via rank IC + precision@k vs a random baseline, emits a live next-hotspot watchlist. llm_involvement=none. +11 tests.
- **Finding (2016-2026, 121 quarterly predictions, counter-intuitive)**: sector **momentum-persistence is ~NOISE** (IC_IR 0.52, beats random 54.5%) — chasing hot sectors does not predict next-quarter leaders. **Seasonality / 景氣循環 is the REAL edge** (IC_IR 2.78, beats random 65.3%). Blend sweep: IC_IR rises monotonically 0.54→2.78 as weight shifts mom→seasonality → DEFAULT_BLEND set seasonality-dominant (0.2/0.8), not overfit to 0.0/1.0. Verdict PREDICTIVE-EDGE. Current call (2026-05, Jun-Aug): SOXX / XLK / XBI (watchlist only, evidence-gated).
- **Concept page** `hotspot-sector-rotation.md` (canonical, indexed) — documents the seasonality>momentum finding; pairs with `sector-seasonality` as its walk-forward validation.
- Wired the hotspot backtest into the WEEKLY routine pass (`scripts/daily_routine.ps1`).

**Profit-max direction (next)**: the blend sweep IS the start of 回測獲利最大化 — reweighting toward the edge-bearing component. Full optimizer (holding period × cadence × sizing on the validated seasonality signal) is the natural follow-on.

## [2026-05-31 04:30 ET] build | NASDAQ-100 對答案 + train/test FOM calibration (honest, anti-overfit)

Principal test: 2000-2026 NDX TOP3 對答案 + 先校年再月 + 不同時間跨度參數可能不同. Refused the in-sample-fit-to-answer move; split time instead. Full suite **360 passed / 0 failed**.

- **`src/sharks/backtest/nasdaq100_calibration.py`** — answer key (actual top-3/period) vs FOM PIT top-3, year+month; calibrate 10 weight archetypes on 2000-2014 TRAIN, validate on held-out 2015-2026 TEST. llm_involvement=none. +8 tests.
- **Finding 1 — FOM does NOT pick moonshots**: mean overlap with actual annual top-3 = 0.36/3. Misses BKNG+343/TSLA+743/MU+240. Beats QQQ on average (+17%/yr, survivorship-inflated) via solid names, but gets CRUSHED at cycle tops (2000 -46/2001 -54/2007 -58/2021 -52) — the IC top-tail mean-reversion seen year by year.
- **Finding 2 — optimal weights INVERT with horizon (principal's hypothesis confirmed)**: ANNUAL → defensive_value/contrarian wins, momentum worst tier; MONTHLY → momentum_heavy wins. Validates existing HORIZON_PROFILES (3m momentum 0.55 / 36m contrarian+quality). 「不同時間跨度的參數可能不同」 = data-confirmed.
- **Finding 3 — tuning helped monthly, HURT annually (why we didn't overfit)**: OOS annual tuned-best +12.2% LOST to untuned canonical +15.1%; OOS monthly tuned momentum +2.25% beat canonical +0.90%. "Fit to the answer" would have made the annual book worse — the train/test split caught it. NO retune applied to fom.py (canonical robust OOS).
- **Week/Day withheld** (monthly bars; needs daily data + re-tuned lookbacks — separate build).
- **Concept page** `nasdaq100-calibration.md` (canonical, indexed).

## [2026-05-31 01:45 +08:00] research | tech/ deep-research Phase A — 9 tech-trend due-diligence pages (質變 vs 同溫層)

Principal request: deep, data/funding/authority-backed research across the year's hot tech + youth-culture trends, explicitly to separate real 質變 from his own 同溫層 (echo chamber), map technical 底蘊 + supply chains + cross-trend synergies. Created a NEW `tech/` due-diligence layer (sits upstream of the investment layer; recommend/research-only).

- **Method** — fanned out **9 parallel Researcher subagents**, each web-researching 2025–2026 sources under the non-negotiable rules: A–E source grading, point-in-time = 2026-05-31 (no lookahead), clinical/falsifiable tone, and an explicit anti-echo-chamber mandate (weight CAPITAL + ADOPTION + AUTHORITY over narrative; state the precise "echo-chamber gap"). Each wrote its own `$hark`-schema page. QC pass: frontmatter validated across all 10 files (type/as_of/author_role/confidence/verdict/rubric present + in-file rubric == returned block), hype-word scan clean (2 false positives = an article title + a debunked phrase).
- **Built** — `tech/00_framework.md` (the 5-axis 質變 rubric A1技術底蘊/A2需求真實性/A3資金權威/A4供應鏈可投資性/A5顛覆向量 + verdict taxonomy 質變/結構/過熱/太早, harmonised with the 5-dim 十足的證據 gate), `tech/scoreboard.md`, `tech/99_cross_synthesis.md`, `tech/index.md`, and 9 trend pages.
- **Verdicts** — model-leadership-and-data 結構(9/0.82), youth-culture-shifts 結構(9/0.78), memory-supercycle 結構(9/0.74), ai-pharma-glp1 結構*(9/0.74; GLP-1 sub=結構→質變 0.85, AI-drug-discovery sub=太早→結構 0.60), autonomous-driving 結構(8/0.74), ai-eats-software 結構(8/0.72), optical-interconnect-cpo 結構(8/0.72), ai-edge-devices **過熱**(7/0.72), quantum-vs-bitcoin **太早**(7/0.78).
- **Master finding** — ZERO page-level 質變: the AI cycle is real (A1=2 on 8/9, A3=2 on 9/9) but largely **already priced (結構)**; the cross-cutting risk is **equity-ahead-of-fundamental** in memory/CPO/model-layer/software-winners simultaneously → re-confirms `07_ai_bubble_audit` §6 late-cycle read. Two echo-chamber traps the data flags: **AI-PC supercycle (過熱** — marketing wrapper; real pull = memory/Win10 EOL) and **quantum-breaks-BTC (太早** — 105 physical qubits vs ~13M needed, Q-Day ~2033, BTC can soft-fork first → independently re-confirms `16_rally_themes` §4). Only cash-flow 質變 = **GLP-1**. Investable alpha = verifiable pricing-power chokepoints (SK Hynix HBM / InP-substrate+CW-laser / TSMC COUPE / LLY-NVO) + un-crowded second-derivative nodes (InP substrate, HBM metrology, CDMO). Corrected two echo-chamber myths: "HBM margin 5×" (real ~1.5×) and "Tesla pure-vision is technically superior" (it is cheaper/more scalable, not more capable — Waymo hybrid leads on peer-reviewed safety).
- **Caveats / open** — SEC EDGAR + some finance sites 403'd WebFetch → LLY/NVO/UBER/DASH GAAP lines cross-confirmed via secondary + cited to primary 8-K URLs (**manual spot-check recommended** before any of these inform a recommendation). Many chokepoints are non-US (000660.KS/2330.TW/8053.T/5801.T/HSAI) → blocked on Phase-2 ticker-suffix support. Verified + corrected `watchlist/serenity-supply-chain.yaml` CPO nodes (Broadcom timeline + VPEC label; flagged missing InP-substrate node).
- **Schema note (for human)** — `tech/` is a new top-level folder NOT yet in `CLAUDE.md` / lint config. Per the doc-evolution rule, proposing the human add `tech/` (type: synthesis, domain: tech-trend) to the schema; verdicts are screen outputs and do not bypass the Risk Officer or position caps.
- **Boundaries respected** — no buy/sell advice, no price targets, no trades; no edits to `sharks.md`, `raw/`, `philosophy/`, or `src/`.

## [2026-05-31 05:30 ET] build | Daily-K horizon calibration + return term-structure synthesis

Principal: 試做日K預測校正 + 撿菸頭 + 七月財報季 + 五六月大陽→七八月機率. Full suite **370 passed / 0 failed**.

- **`src/sharks/backtest/daily_horizon_backtest.py`** — daily-bar walk-forward IC of mom_60/mom_20/rev_5/rev_1 at 1d/5d/21d horizons (NDX-proxy daily 2015-2026). +9 tests. **Finding**: short-term REVERSAL (buy 5-day losers) wins at ALL daily horizons (IC_IR 2.36/3.53/2.71); fast MOMENTUM is strongly NEGATIVE (−0.99/−1.81/−2.71). Daily edges cost-fragile → research, not a low-freq strategy.
- **Term-structure synthesis** (`philosophy/concepts/return-horizon-structure.md`): across 4 backtests — 1-21d REVERSAL, 1-6m MOMENTUM (FOM), 12m+ CONTRARIAN+QUALITY (value). The sign flips with horizon = the measured answer to 不同時間跨度參數不同. Dictates **3 sleeves**: core FOM (3-6m) / value-cigar-butt (contrarian+quality 12m, the safe 撿菸頭) / ring-fenced moonshot (≤5%, FOM can't pick飆股).
- **Seasonality answer** (July anxiety): strong May+June has historically RAISED July-Aug odds, not lowered — SPX 84% vs 70% base (100% when 5-6月合計>5%, n=10); NASDAQ milder 71% vs 65%. Continuation > reversion at index level; small sample; size for earnings dispersion.
