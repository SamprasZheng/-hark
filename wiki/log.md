# Wiki Log

Chronological record of activity in the compiled wiki layer. Append-only.

Format per [[../philosophy/09-point-in-time]] and [[../CLAUDE]]:

```
## [YYYY-MM-DD HH:MM TZ] <action> | <short title>
```

Where `<action>` ∈ `{ingest, query, lint, recommendation, halt, universe, raw_deletion, build}`.

---

## [2026-05-31 03:35 TW] build | crypto Part B content — cycle reconciliation (B4) + DOT postmortem (B3)

- **B4 [[../crypto/cycle-and-institutional]]** (live-data reconciliation): the [[../philosophy/concepts/btc-halving-cycle]] page's peak is **stale** — live ATH is **$126,080 @ 2025-10-06** (higher + 3 months later than the cited "2025-07 $115,758 monthly close"); BTC now **−41.3%** from ATH (not −37%), peak multiple ~+97%/~1.9× (not 1.7×). The falsification trigger *technically* fired but on a wording artifact (that high WAS the cycle peak, not a post-bear reclaim) → proposed a trigger rewrite. To-date the shallow −41% (vs prior −77%/−84%) **leans weakly toward the [[../philosophy/concepts/institutional-btc-anchor]] thesis**, but the 2026Q4-2027Q1 bottoming window is still ahead → unresolved. **Contradiction flag added to the older btc-halving-cycle page** per wiki rules.
- **B3 [[../crypto/dot-postmortem]]**: DOT **−97.83%** from $54.98 ATH (2021-11-04) → $1.20, rank #44, mcap $2.02B; `max_supply 2.1B` (hard cap live, 80.3% issued). Postmortem of the 2025 loss (narrative/dev-mindshare decay, dilution, weak value capture, structural underperformance) + the honest hard-cap read ("less dilution ≠ more demand"). Forward stance is a **trigger-conditional template**; position cost-basis left BLANK (`position_status: COST_BASIS_UNKNOWN`) — ask-at-execution, never fabricated. Default lean: hold-or-exit, NOT accumulate.
- **wiki/index** updated with a crypto-tracker pointer. No position opened; RECOMMEND-ONLY.

## [2026-05-31 03:10 TW] ingest | crypto/web3 KOL 底層邏輯性格 profiles (22 KOLs) + watchlist RWA refinement

- **KOL profiles**: 4 parallel web-research agents profiled **22 crypto/web3 KOLs** (verified handles + 2025-26 positioning + conflicts of interest) → `raw/kol_signals/crypto-kol-profiles-2026-05-31.md` + `raw/kol_signals/crypto-kol-index.tsv`. All grade **D or below** (KOL price calls never A/B per [[../CLAUDE]]); **C** for data-driven Cowen/Woo; **E** for falsified PlanB S2F + grift 寶二爺; **趙東 rejected** (7yr prison conviction, no verified live handle). Filed to `raw/kol_signals/` (sentiment layer), deliberately NOT `analysts/` (the FOM-ensemble persona layer) so KOL noise never tilts the stock scorer.
- **DOT corroboration** (feeds the future [[../crypto/dot-postmortem]]): the Gavin Wood profile surfaced The Defiant (May 2026) data — Polkadot DeFi **TVL ~$81M** vs ETH $48B / SOL $6.8B; **MAU 230K→43K**; **JAM slipped to late-2026/2027**; DOT **~−98%** from ATH. "Vision shipped as whitepapers faster than usage or price"; the 2026-03 hard cap is tokenomics, not demand.
- **Saylor watch** (feeds [[../philosophy/concepts/institutional-btc-anchor]]): May-2026 reversal of "never sell" → "may sell BTC to fund dividends" after a $12.5B Q1 loss — the largest corporate BTC buyer may turn into a supply source.
- **yxz sync**: same 22 KOLs + 11 crypto keywords added to yxz `kol-tracker` (`D:\DOT\yxz\.claude\skills\kol-tracker\kol-list.yaml`) — PUBLIC, neutral whys only; the candid analysis stays $hark-private.
- **Watchlist refinement**: `crypto/watchlist.yaml` snapshotted to `crypto/watchlist_history/`; added `rwa` + `perp_dex` tags + 7 stablecoins (the first live snapshot's `uncategorized=41` was saturated with RWA / tokenized-treasuries). `scoring/crypto_top100.py` `compute_movers` gained a top-50 `max_rank` liquidity filter to cut microcap noise (+1 test). Full suite **454 green**.

## [2026-05-31 02:47 TW] build | crypto Marketcap Top-100 tracker (Phase A infra) + first live snapshot

- **Scope**: zero-dep crypto Top-100 tracker, compile-first. Code in `src/sharks/` (importable + tested); state/content in `crypto/`. RECOMMEND-ONLY; no trading, no leverage.
- **New code**: `src/sharks/data/coingecko_client.py` (stdlib `urllib` CoinGecko `/coins/markets` client — retry/backoff, `Retry-After`, `CoinGeckoError`, never invents prices) + `src/sharks/scoring/crypto_top100.py` (orchestration mirroring `daily_health_check.py`: `categorize` / `market_structure` / `compute_movers` / `rank_churn` / `render_markdown`, graceful stale-fallback). YAML read WITHOUT pyyaml by reusing [[../src/sharks/analysts/persona]] `_parse_frontmatter` (watchlist authored as a `---`-fenced doc).
- **Tests**: `tests/test_coingecko_client.py` + `tests/test_crypto_top100.py` — 23 offline tests (mock opener / BytesIO, monkeypatched sleep, stale-fallback degrade). Full suite **453 green**, no regressions.
- **State/content**: `crypto/watchlist.yaml` (`category_tags` + mandatory DOT/BTC `human_overrides`), `crypto/README.md`, dir keepers; `scripts/crypto_top100.ps1`; `.gitignore` (`crypto/data/*.json`) + `daily_routine.ps1` (commented weekend hook).
- **First live pull (2026-05-30 18:47 UTC, live_data=true, 100 coins)**: total tracked cap $2.52T; **BTC $73,967 (−41.3% from $126,080 ATH), dominance 58.81%**; ETH −59% / SOL −72% from ATH; **DOT $1.20, −97.8% from its $54.98 ATH, rank #44**. Alts bleeding to BTC → Phase-D-consistent. `uncategorized=41` surfaced a real RWA / tokenized-treasury + new-stablecoin rotation (BUIDL, USYC, USTB, RLUSD, USDG, WLFI, HYPE, PUMP…) not yet in the watchlist tags.
- **⚠ Reconciliation flag for Part B4**: live ATH **$126,080** exceeds the cited 2025-07 monthly-close peak **$115,758** in [[../philosophy/concepts/btc-halving-cycle]]; the model's "1.7× / −37%" figures are stale. Resolve halving-vs-institutional-anchor against live data; flag the contradiction on the older page per wiki rules. (Content deferred — this build is the GATE pull only.)
- **Guardrails baked in**: BTC ≤4% notional (core macro, OUTSIDE the ≤5% Alpha sleeve, mechanical DCA); alts ≤5% Alpha sleeve, SPOT ONLY; empty slots null; de-risk/observation-first.

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

## [2026-05-31 06:30 ET] build | 4-sleeve classifier applied to real P1 (FOM40/Value30/Moonshot20/Hedge10)

Principal set target FOM40/Value30/Moonshot20/Hedge10; classify real holdings. Full suite **384 passed / 0 failed**.

- **`src/sharks/backtest/sleeve_classifier.py`** — tags each holding into FOM_CORE/VALUE/MOONSHOT/HEDGE/DEAD via leveraged registry + Buffett quality + curated beaten-quality/value-trap/dead sets; rolls up vs target, emits trim(over-cap)+add(under) actions. +12 tests. Also added TSLL (2x TSLA) to leveraged registry (was mis-classified FOM_CORE).
- **Applied to real P1 (investable ~$10k)**: MOONSHOT **59.9%** (target 20% → OVER +39.9pp / +$4,013), VALUE 6.7% (target 30% → UNDER −$2,343), FOM_CORE 28.6% (−$1,141), HEDGE 4.7% (−$529). Trim order (worst-decay first): LABU(3x)/TARK(2x)/NOWL/AAPB/LULG/RBLU/OKLL/TSLL. Value-sleeve現有 NKE/LULU/STZ/MRNA; value-traps飆股化 UAA/VFC. Persisted outputs/sleeve-classification-p1.json.
- Headline: P1 是「飆股 sleeve 爆表 ~3×上限、價值 sleeve 幾乎空」→ 縮槓桿換跌深品質股是主軸。

## [2026-05-31 07:15 ET] build | tech/ DD layer integration (消化整合)

Digest + integrate the tech/ technology-trend due-diligence layer. Full suite **384 passed / 0 failed**.

- **FOM universe**: added `TECH_DD_NODES` (11 US-listed investable nodes from tech/cross-validation-quant §3: INTU/ADBE/LLY/NVO/UBER/DASH/SPOT/HSAI/MBLY/RXRX/SDGR) + IP_DEFENSIBILITY entries → universe 105→116. Lets the "live FOM scan" that page asked for actually run.
- **Live scan executed** (tech/cross-validation-quant §3.1, as_of 2026-05-31): split the basket 結構但過熱 (MU −95 / LITE −55 / COHR −40 = memory/optical froth, DD confirmed) vs 結構但健康 (UBER/SPOT/DASH platforms + LLY/NVO GLP-1 all bubble_guard 0 = real cashflow). Mapped to sleeves: LLY/UBER/AVGO=FOM-core watch; MU/LITE/COHR=wait-for-pullback; RXRX/SDGR=ring-fenced moonshot.
- **CLAUDE.md**: fixed orphan code-fence in §6b; added verdict→quant-bridge pointer (TECH_DD_NODES + the 結構健康/過熱 split).
- tech/ master read (no page-level 質變; most hot themes 結構=已被定價; only GLP-1 near-質變現金流) is consistent with wiki/07_ai_bubble_audit late-cycle thesis + my term-structure work.

## [2026-05-31 08:00 ET] build | Value-sleeve screener (跌深品質股) — beaten-down quality watchlist

Resumed after tech/ integration. Full suite **390 passed / 0 failed**.

- **`src/sharks/backtest/value_screener.py`** — beaten-down-QUALITY screen for the value sleeve: dd −20..−70% + survivor (5y in [−25%,+250%], so NOT a momentum monster) + stabilising (3m>−20%) + vol≤55% (value=stable, not moonshot), ranked by IP-led quality-weighted value_score. +6 tests. Universe = DEFAULT_UNIVERSE + curated QUALITY_COMPOUNDERS (281 names; honest note: full S&P500/R2000 needs a vendor — lxml absent, iShares anti-bot — and scanning 2000 junk micro-caps is the wrong tool for a QUALITY screen).
- **Result (as_of 2026-05-29)**: top low-vol cigar-butts = RSG/PAYX/ADP/CTAS/VRSK/TMUS/SPGI/KMB/BJ/BKNG/HD (vol 18-25%, beaten 20-44%); high-IP beaten = NOW(ip90,−40%,+15% 3m)/INTU(−58%)/CRM(ip88,−29%)/ISRG/NVO/UBER/SNPS. Filtered OUT momentum-in-pullback (PLTR vol65/CRWV vol179/UEC) — those are FOM/moonshot not value. outputs/value-screen.json.
- These are the rotation targets for the P1 value-sleeve shortfall (~$2,343 under target) once moonshots are trimmed. WATCHLIST only — each must clear 十足的證據 + fundamentals confirm.

## [2026-05-31 09:00 ET] build | 飆股獵手 moonshot hunter + universe→415 + OTC handling + value-candidate FOM scan

Full suite **430 passed / 0 failed**.

- **Value candidates FOM+bubble_guard** (Tier1+Tier2): ALL 18 healthy bubble_guard (0..+30), NONE overheated (beaten names already corrected). By 36m value-horizon: UBER 56.7 / BKNG 53.9 / CRM 52.8 / RSG 52.7 / CTAS 51.9 / TMUS 51.8 / NOW 51.1 / SNPS 51.1 / ISRG 50.9 → stage-in cleared (not 過熱).
- **`src/sharks/scoring/moonshot_hunter.py`** — 飆股獵手: deliberate INVERSE of FOM (hype_score rewards the parabola bubble_guard penalises). Signals = volume_surge + hype (price) + insider_buying/bigtech_partnership/supply_chain_design_win (A/B-grade evidence). PURE-HYPE-NO-EVIDENCE warning (= 複委託 graveyard pattern) when price-heat high but 0 confirmed catalysts; EVIDENCE-BACKED-MOONSHOT only with ≥1 A/B catalyst. +25 tests. Concept `moonshot-hunter.md`.
- **Leveraged registry**: +MSTX(2x MSTR)/CONL(2x COIN)/FBL(2x META)/MSFU(2x MSFT) per principal's moonshot ETF list (TSLL/LULG/CRWG/AAPB/UVIX/UVXY/SQQQ/TQQQ already in).
- **`src/sharks/scoring/universe.py`** — full_universe() 415 (DEFAULT 116 + EXTENDED ~300), OTC OFF by default (OTC_WATCH genuine pink ADRs only), `buy_warning()` fires before any OTC/leveraged buy (如果真的要買就提醒我), `data/universe_extra.txt` drop-in = path to 1000 via vendor CSV. +14 tests. Honest: clean 500-1000 needs a vendor list (lxml absent, iShares anti-bot).

## [2026-05-31 03:30 +08:00] research | tech/ Phase B — 6 multi-horizon trends + framework upgrade (時間軸/里程碑/考證/FOM 整合)

Principal directive: 拉高維度·加深·擴展·拉長時間·拆分細化·給建議 + 如何整合到 FOM + 強化數據考證 + explore 服裝/精品/娛樂-IP(POPMART·電影重生)/AR-VR/Claude Code vs Codex/satcom/國防 + 映射投資(受益受損·抄底·爆發條件) + 每周里程碑追蹤.

- **6 Phase-B deep-dives** (parallel Researcher fan-out; upgraded template = 4-horizon verdict + falsifiable milestone ladder + winners/losers/抄底 + 自我打臉 + Grade×Verification sourcing): luxury-and-apparel (結構分化; Hermès 複利 vs Gucci −19%; Nike 分批抄底), ip-economy-collectibles (結構; POPMART 護城河=造星流水線非單一 Labubu 38.1%; 抄底 Disney 飛輪), ai-coding-agents (結構, T0 質變; 模型廠+MSFT 通路贏, Cursor wrapper 負毛利; SWE-bench <2pt 商品化), ar-vr-smart-glasses (結構; Ray-Ban 靠放棄 AR 贏, 真 AR 撞 etendue T2+), satcom-future (結構; Starlink 已質變已定價, D2C 物理封頂=補盲, 台灣上游), defense-tech (結構, T2-T3 質變; 歐洲重整 NOW, 受益者≠該價位 PLTR>85×). All headline 結構; T3 質變候選 = IP/defense/AR(條件)/ai-coding.
- **Framework upgrade**: 00_framework +time-axis(T0-T3 maps FOM HORIZON_PROFILES); _sourcing-protocol (Grade×Verification + Q/FY label + 2-source rule + 打臉自己 of Phase-A Uber Q-vs-FY + HBM-5x errors); _weekly-watch (weekly milestone board, gates FOM promotion, couples daily_routine WEEKLY); fom-integration (verdict×bubble_guard→sleeve router + bounded ±0.06 tilt + milestone-gate + observe-first-until-IC-validated; builds on TECH_DD_NODES+IP_DEFENSIBILITY already in fom.py + cross-validation-quant §3.1 live scan).
- **GAAP spot-check (考證)** on Phase A: DASH exact; LLY Zepbound→US $4.1B/+79%; UBER FY24 corrected (FCF $6.9B / AdjEBITDA ~$6.5B, the Q4-as-FY mislabel fixed); NVO confirmed.
- **Cross-trend desk call** (99_cross_synthesis §B, all 15 trends): 受益者≠該價位的股票; alpha in un-crowded second-derivatives (optical metrology Auros/Onto, GLP-1 API/fill-finish, AR microdisplay, Taiwan satcom upstream), condition-gated 抄底 (Nike/Disney/Viasat/US-primes), wait-for-pullback (MU/LITE/COHR/PLTR/Pop Mart).
- **Boundaries**: recommend-only, no trades; did NOT edit CLAUDE.md (schema proposal only) nor fom.py (the TECH_DD_NODES wiring is the principal's own). Staged tech/ only.

## [2026-05-31 10:30 ET] proposal | computex_2026_low_base.md (external spec, reconciled) + moonshot demo scan

- **`watchlist/computex_2026_low_base.md`** — captured the principal's pasted cross-domain integration spec (event-driven arch + long/short algo + COMPUTEX 2026 伏兵 + 2026-2030 tax 防空洞) per "new file, don't touch code". Added §0 RECONCILIATION flagging conflicts with committed decisions: TimescaleDB→DuckDB (rejected), Pinecone→local-RAG, Kafka/high-freq vs the low-freq mandate, LLM→LightGBM direct-feed vs LLM-pollution protocol, and the FACTUAL ERROR 670萬→750萬 AMT threshold. Adopted: structured-JSON/sentiment-continuous, vol-targeting, short-exclusions, CPCV. Personal-finance kept as POINTER to D:/DOT/finance (private, not git) — only公開原則 + the 750萬 correction recorded.
- **Moonshot demo scan** (SYNA/ALAB/TSLL/MSTX/CONL/AAPB, as_of 2026-05-29): ALL AVOID — nothing ignited pre-COMPUTEX. SYNA heat 13 only; leveraged names flat. SYNA's COMPUTEX-Astra catalyst graded C (public demo, no named customer) → 0 confirmed A/B evidence → would be PURE-HYPE even if hot. Correct discipline: wait for the event-week volume surge + an A/B catalyst (named design-win / insider Form-4) before acting.

## [2026-05-31 04:15 +08:00] build | tech_dd.py — tech/ DD → FOM sleeve overlay (implemented, observe-first)

Principal authorized implementing the fom-integration design + broadening the universe.

- src/sharks/scoring/tech_dd.py — broad DD registry (71 US-listed + 21 documented non-US), per-ticker verdict{質變/結構/過熱/太早/受損}+flags traced to the 15 tech/ pages. dd_verdict_tilt (bounded ±0.06, reuses analysts.persona machinery), dd_sleeve (verdict×bubble_guard → FOM_CORE/VALUE/MOONSHOT + posture), annotate_ticker (cross-checks backtest.sleeve_classifier), build_report, main → outputs/tech-dd-overlay.json. OBSERVE-FIRST: never folded into final_fom.
- CLI `sharks tech-dd [--dry-run]` wired (mirrors health-check); tests/test_tech_dd.py +29 (registry/tilt/routing/observe-first/CLI). Full suite green (cli-smoke + dispatcher intact).
- First live run vs latest FOM scan: FOM_CORE 33 / VALUE 17 / MOONSHOT 21; 36 DD-vs-structural disagreements (expected — classifier defaults uncovered names to core; DD adds the froth/太早/front-run lens).
- Guardrails: recommend-only, no trades; tilt stays out of final_fom until walk-forward IC-validated (fom-predictive-validity / nasdaq100-calibration). 太早/過熱/front-run → Moonshot ring-fence only.

## [2026-05-31 05:00 +08:00] research+build | tech/ Phase C (6 trends) + tech_dd 100-name + Phase-2 後綴 + 時間軸路由 + DD-tilt IC 回測

Principal: 全部做 — 開新趨勢 + Phase-2 後綴支援 + 時間軸路由進 code + DD-tilt walk-forward IC + 美股擴廣到 100.

- **6 Phase-C deep-dives** (multi-horizon + milestone + winners/losers/抄底 + 自我打臉 + 考證): humanoid-robotics (結構/7; 像2019自駕, 買鏟子 NVDA+減速機, 中國贏單位戰), ai-datacenter-power (結構/9; AI 瓶頸鏈 compute→interconnect→電力; 電氣/核能IPP 真P&L, pre-rev SMR froth), stablecoins-tokenization (結構/8; 結算真質變, CRCL 利率單因子賭注), cybersecurity-ai (結構/8; AI-PROOF, ai-eats-software 的反面), china-ai-stack (結構/9; 分流已成事實, HBM 封頂), space-economy (結構/8; 發射成本崩跌質變, 在軌太早, RKLB ~90x). 全 headline 結構; T2-T3 質變候選 = power/cyber/china/humanoid.
- **tech_dd 升級**: 美股節點 71→**103**; dd_horizon_routing (verdict_by_horizon × FOM 3m/12m/36m — 同一檔 3m過熱不追/36m質變佈局); 非美支援 via 新 ticker_suffix.py (Phase-2 後綴: .TW/.KS/.T/.HK/.SW/.PA/.DE → exchange/currency/region + FX caveat).
- **DD-tilt walk-forward IC 回測** (tech_dd_validation.py, 2016-2026, 112 periods): tilt ΔIC_IR −0.02..−0.11 每個 horizon → **DD-TILT-NEUTRAL**; tilt 不進 final_fom (observe-first 實證得證); 判決僅作 router/annotation. Lookahead caveat (static verdicts on history) 已記錄.
- **Tests**: +test_ticker_suffix (14), +test_tech_dd_validation (7), test_tech_dd 擴充 (horizon+non-us+100-name). 全套件綠燈.
- **Nav**: scoreboard Phase-C 矩陣, index Phase-C 6 列, 99_cross_synthesis §C (compute→interconnect→電力 + DD-tilt-neutral 結果), _weekly-watch Phase-C 里程碑, fom-integration 驗證註記.
- **Boundaries**: recommend-only, 無交易; src/ 是 principal-authorized 的 tech_dd 實作; observe-first (tilt 不進 final_fom).

## [2026-05-31 06:45 +08:00] research+build | alpha-transmission framework — 供應鏈傳導/輪動/集中度/social-attention + lead_lag.py

Principal: 趨勢追蹤探究未發現 alpha + 供應鏈深化 + 資金買盤數據 + 分化集中頻率 + 半導體流動性是否外溢從哪傳導 + 軟體怎麼分類 + Reddit/GoogleTrend/X + 交易演算法參考.

- **4 research inputs** (method pages, 考證-sourced): software-stack-taxonomy (L0 silicon→L6 vertical SaaS 微笑曲線; capex 領先 revenue 的 air-pocket), rotation-spillover-algos (8 家族; lead-lag/economic-link 是真 edge、動能追逐是噪音; semis 外溢用 Granger/Diebold-Yilmaz + 二線供應商), social-attention-alpha (Reddit/GoogleTrends/X = 短期反向羊群, 唯一正向 edge=主題早期偵測; 免費棧+lookahead 陷阱), liquidity-concentration-flows (集中度 50 年極值 top-10 40.7%/semis~18%/corr<10; 外溢已啟動但邊際脆弱; 傳導序 semis→電力→cooling→工業→公用; 小型股平行非下游).
- **3 agents 獨立收斂同一傳導鏈**: capex→晶片→記憶體→光通訊→電力→工業→breadth.
- **alpha-transmission-framework.md** — 整合 供應鏈地圖(HW+SW) + 偵測棧(集中度→flow→lead-lag→attention→seasonality, 接 breadth_indicator/chip_flow/sector_flow/hotspot) + 未發現 alpha funnel(下游×未動×attention加速未擁擠×季節性確認→人工DD) + 半導體外溢具體答案+證偽觸發 + 演算法參考.
- **NEW regime/lead_lag.py** (zero-dep numpy, PIT, observe-first): lead_lag_score(net>0=leader leads)、net_transmitter_rank(Diebold-Yilmaz-style)、transmission_candidates(leader→未動的下游=未擁擠標的). +12 tests. Live demo 寫 outputs/lead-lag-transmission.json.
- **核心紀律**: 未發現 alpha 在 lead-lag + 早期 attention + 季節性, NOT 追逐已熱 sector(自測 IC_IR 0.52≈擲銅板). observe-first, watchlist only, 過證據閘.
- 全套件綠燈. Boundaries: recommend-only, 無交易.

## [2026-05-31 07:45 +08:00] research+build | 貝葉斯瓶頸引擎形式化 + lead_lag daily + sector_flow spillover + attention_radar (全部做)

Principal: 全部做 + 消化 Serenity 貝氏邏輯 + 「我的系統能整合貝葉斯推理嗎/能數學理論化嗎」.

- **貝葉斯形式化** (答「能整合+能理論化」= YES, 系統本來就隱性貝氏): tech/bayesian-bottleneck-engine.md 把 Serenity 四步對映既有模組 (prior=DD rubric/confidence; P(H|E)=_weekly-watch milestone 的 log-odds LR 更新; 序貫輪動=全概率; edge=posterior−market-implied). + scoring/bayesian_update.py (純函式、observe-first: prior_from_rubric/verdict、milestone_logodds_update 含相關性 shrinkage、edge_vs_market 用 bubble_guard 當市場隱含機率、posterior_for_ticker). +15 tests. Serenity 報酬數字標 grade D/E (匿名未審計)；採方法不錨數字.
- **lead_lag 接 daily** (lead-lag 日線訊號遠強於月線); **sector_flow 擴充** broadening_score (% sectors RS>0) + semis_spillover_flag (SOXX leader AND 下游 XLI/XLU/XLB rotating_in). +tests.
- **attention_radar.py** (社群早期主題雷達): abnormal_attention(trailing z、無 lookahead) + acceleration + attention_score(crowded flag) + 免費 ApeWisdom fetch(stdlib urllib、離線優雅降級) → _weekly-watch 🆕 人工 DD 候選. observe-first、極端反向. +tests.
- 全套件綠燈. 紀律: 全部 observe-first/watchlist-only/過證據閘; 貝氏 posterior 是 annotation, 校準(reliability/Brier)前不進 final_fom.

## [2026-05-31 08:30 +08:00] build | 貝葉斯吃 rubric (品質差異化) + SOXX lead-lag 驗證 + NKE/AMZN 上漲條件 (ABC)

- (A) tech_dd 加 TREND_RUBRIC (每趨勢 5 軸)；bayesian_update.posterior_for_ticker 改用 trend rubric 當 prior → Mag7 現在能差異化 (AAPL 最低 0.750 因 ai-edge rubric 最弱/過熱；META/MSFT edge 最高 +0.67/+0.65). +AMZN 進 registry；bayesian_update 加 main().
- (B) lead_lag 餵全 SOXX 30 檔 (日線): 乾淨多了 — TER/NVDA/TXN/TSM 領先；設備(AMAT/KLAC/LRCX)+類比(ADI/MCHP)是 NVDA 下游補漲一棒 (vs ETF 版防禦股當頭=雜訊). 證實「餵結構化個股池才有用」.
- NKE/AMZN 上漲條件梯加進 _weekly-watch: NKE 鑰匙=毛利 YoY 轉正(現 −130bps、mgmt 指 FY27)；AMZN 鑰匙=AWS 維持 20%+(✅+28%) + capex air-pocket 風險(FCF −95%). 皆 grade-B 季報數據.
- 全部 observe-first/watchlist；affected tests 綠燈.

## [2026-05-31 09:00 +08:00] build | 基本面追蹤器 + 基本面 Bayesian prior + P1 portfolio scan

Principal: 更重基本面、抓關注標的財報關鍵數字以免錯過扭轉條件；用貝葉斯 scan portfolio.
- `scoring/fundamentals.py`: fetch_fundamentals (yfinance .info + quarterly → rev-growth YoY, gross/op/profit margin, **gross-margin YoY Δ = 扭轉鐵證**, EPS growth, FCF, fwd P/E, analyst upside) + inflection_flags (turnaround_score 0-5) + scan + main. grade-C/D, monitoring only.
- `bayesian_update.prior_from_fundamentals`: 讓貝葉斯能 scan 任何標的 (不需 DD verdict) — rev 成長 + GM 拐點(最重權重) + 營業獲利 + FCF → prior. +test_fundamentals (10).
- P1 portfolio scan (24/26 有資料): 改善中 ALGM(0.75)/TSLA/AMZN/CRM/APA (毛利Δ 正); 惡化 WOLF(營業利潤 −72%, edge −0.27)/ENPH/UAA/LULU(GM −6%); **NKE 毛利Δ −1% → 毛利未轉正、扭轉條件未達成 (與 Q3 −130bps 一致)**. edge 多數 n/a (不在 FOM universe). 警示: AMPX/MRNA 高成長是基期假象 (營業利潤仍負).
- observe-first / watchlist-only. 全套件綠燈.

## 2026-05-31 — Regime-conditioned valuation system + ABC + SP500 scan
Principal: ABC都做 + 掃SP500更多個股 + 建立估值系統(動態目標價/預估收益/回測/準確度) + 基於 variables/20260531.md 判斷環境.
- `scoring/valuation.py`: 5 環境 (積極樂觀/寬鬆/中性/保守/悲觀恐慌) 從 `regime/classifier` 映射; 動態目標價 = 分析師 [low,mean,high] band 以環境 tilt (中性=共識均值); est_return **校正自 SPX 2008-2026 regime 回測 base rate** (非臆測). +12 tests.
- **關鍵校正發現 (反直覺)**: SPX 前瞻報酬在 保守/悲觀恐慌 (跌破200dma) 最高 (63d +6.4%/+3.9%), 在 積極樂觀 最低 (63d +2.4%) → 系統是**逆勢工具**, 在 積極樂觀 加碼=歷史上報酬最差時點.
- 分析師目標價是 grade-C: NKE/CRM/NVDA gap +80% 是樂觀/落後 (NKE 連 analyst-low 都 >現價), 非 base case.
- (A) `fundamentals.detect_flips` 週對週翻正告警 (翻正才通知) + dated snapshots; baseline 已建 (AMZN/HPQ/TSLA turn=5). (B) bayesian scan 104 DD nodes (41 有 market-implied): top edge = **防禦三雄 LMT+0.73/NOC+0.65/RTX+0.60** (結構但未被當泡沫定價=未擁擠) + META/MSFT/ETN/CCJ/NVDA; bottom = ALAB/AEHR/AXTI/IONQ/RGTI (市場已信過頭). 30-name SP500 sampler 動態目標表已產出. (C) main 已同步 (cherry-pick 4 tech commits, 乾淨; crypto commit 留在分支).
- 全套件綠燈. observe-first / watchlist-only.

## 2026-05-31 — NVDA bull/bear tracker + AI-monetization reckoning + exposure gauge
- `tech/nvda-bull-bear-tracker.md`: 可證偽週更追蹤器 (capex 指引/ASIC 市佔/HBM-CoWoS/**人才流動**/毛利-氣穴 + 留-跳決策框). 現讀: capex BULL (~$725B 2026 +77%), ASIC BEAR-WATCH (~27.8% 已近 25% 門檻; GS 估 2027 平價), HBM BULL (售罄到2027), 人才 BULL (NVDA 投資離職創業者), 毛利 BULL (74.9%) 但 10-K 採購義務語言=2022 庫存前兆. 修正 agent 誤植市值 → ~$5T. 多數 capex/ASIC/人才數字 grade B/C single-source, 待 primary 驗證.
- `tech/ai-monetization-reckoning.md`: 主軸轉換 DD (結構, conf 0.68) — capex 建設期 → ROI 清算; 計分板 4 BULL / 1 BEAR (pilot 轉化率僅 ~5-12%) / 1 SPLIT (推論成本 vs 變現). 觸發 = 任一雲廠砍 2027 capex >10%. Cisco-2000 類比.
- `scoring/exposure.py` (前一 commit): 真實總曝險儀表 (RSU+本業+債相關打擊). 校準 finance/01: NVDA 89% 資產 + ~半收入 + 月現金流負(靠 vest 補)= 四重相關. −35% → 淨值 −$95K + 收入 −$70K. 留-紀律(賣到50%) vs 跳谷歌(脫鉤收入)拆解.
- observe-first. 全套件綠燈.
