# Wiki Log

Chronological record of activity in the compiled wiki layer. Append-only.

Format per [[../philosophy/09-point-in-time]] and [[../CLAUDE]]:

```
## [YYYY-MM-DD HH:MM TZ] <action> | <short title>
```

Where `<action>` ∈ `{ingest, query, lint, recommendation, halt, universe, raw_deletion, build}`.

---

## [2026-06-13 20:30 TW] research | SpaceX (SPCX) market-impact deep dive — capital siphon, Musk proxy split, valuation/bubble test case (researcher extension)

- **Scope**: Web + X-sourced deep dive on *how* the 2026-06-12 SPCX listing transmitted into the broader stock market (beyond the initial day-1 snapshot). Focused on observable channels: liquidity absorption, sector proxy rotation ("siphon effect"), Musk ecosystem bifurcation (TSLA vs. new high-beta vehicle), valuation regime stress test (extreme P/S on losses), and forward mechanical flows (gamma from June 16 options, eventual QQQ inclusion).
- **Sources (all graded & time-stamped)**: 
  - Primary reporting (Yahoo Finance, Business Insider, Forbes Jun-4/12-13 coverage, Reuters snippets) for price action ($135 price → $150 open → $160.95 close +19.22%, intraday high ~$176.5, $75B raise, ~$1.77T→$2.1T+ mkt cap).
  - Aswath Damodaran Substack (2026-06-13) — intrinsic equity value ~$1.25–1.3T anchor vs. market pricing.
  - SpotGamma (May 2026) — options launch June 16 and expected gamma amplification on low-float mega-cap.
  - X semantic results (2026-06-12/13 posts by verified/analyst accounts): contemporaneous documentation of proxy reversals (RKLB −10–17%, ASTS −10–14%, SPCE −24–37% etc.) and "siphon / sell-the-news" framing.
- **Added to wiki**: Extended `[[inbox/2026-06-13-spacex-ipo-market-impact]]` with new "Deep Dive" section (capital rotation data + falsifiable hooks tied to existing triggers). Light update to `[[../../philosophy/entities/spacex]]` (new "Observed post-debut dynamics" subsection + cross-link to the extended synthesis). No changes to blackout, tier, or any recommendation-bearing files.
- **Reconciliation with prior**: Fully consistent with initial compiler synthesis (index moves, TSLA halo, RKLB/SPCE displacement, P/S ~95× bubble flag, 90-day blackout, Y2-midterm IPO-trap timing). The siphon provides *live confirmation* of the exact falsifiable test already written in [[../wiki/07_sector_handoff]] §3 and the "AI IPO reception" case in [[../wiki/07_ai_bubble_audit]]. Strengthens liquidity-fishbowl and late-cycle IPO supply observations in [[../docs/ipo_wave_dotcom_analog]] without introducing lookahead or new position implications.
- **Point-in-time**: All new claims anchored to 2026-06-12/13 source visibility windows. as_of_timestamp discipline observed. Grade D (social/KOL) informs monitoring only — never standalone for any future signal.
- **No output impact**: Zero effect on picks, no raw/ touches, no philosophy/ principle changes. Pure researcher synthesis + entity extension.

## [2026-06-13 11:00 TW] ingest | Grok agent-integration conversation → cross-tool orchestration page (grade D, reconciled)

- **Source**: a single Grok conversation dump (`wiki/grok.md`, scratch paste, 1835 lines with literally duplicated blocks) in which Grok self-describes how to be wired as a headless cross-reviewer/Risk Officer under Claude — grok agent stdio/ACP, custom MCP server, Claude subagents, Zellij/tmux layouts, multi-agent orchestration patterns. **Grade D** (LLM self-description / opinion; per [[../CLAUDE]] §5 informs research only, never opens a position — N/A here, it's ops tooling).
- **Compiled** → [[25_cross_tool_agent_orchestration]] (synthesis, author_role compiler). Distilled the durable taxonomy (5 integration approaches, 3 orchestration patterns, + a worktree-isolation recipe for safe write-loops §3b with the git-hardlink `chmod`/watcher caveat) and **reconciled each claim against the operator's verified 2026-06-13 tests** rather than presenting Grok's speculation as fact.
- **Contradiction flagged**: the source's most-repeated recommendation — inline `grok -p "..."` — is the one method the operator found **broken** (truncates to the first word through the PowerShell→wsl→bash quoting layers). Verified method is `--prompt-file`; recorded in the `grok-headless-cross-review` memory + [[windows-env-quirks]]. Page §4 also flags a stale model id (`claude-3-5-sonnet-20241022`) and *nix/macOS env mismatch in the snippets.
- **Reconciliation**: no new rules — the patterns map onto existing [[../AGENTS]] §3 (multi-agent/worktree) + [[../CLAUDE]] §1 (roles). MCP-server / persistent-subagent / `grok agent stdio` ACP routes recorded as **research backlog**, not commitments.
- **Raw source archived** as an immutable snapshot at [[inbox/2026-06-13-grok-agent-integration-conversation]] (cited in the page's `source_paths`). The live scratch `wiki/grok.md` was left in place — it is open in the operator's editor and still being appended to (1835→3429 lines during this session), so it is **not** removed; the inbox copy is the frozen point-in-time source. `wiki/index.md` updated (new page #25). No signal slot, no position, no code change.

## [2026-06-13 08:00 TW] ingest | SpaceX IPO listed 2026-06-12 — entity page + market-impact synthesis + calendar update

- **Event**: SPCX (SpaceX) listed on Nasdaq 2026-06-12. IPO price $135, first-day close **$160.95 (+19.2%)**, $75B raised, day-1 market cap ~$2.1T — largest US IPO in history. xAI (Grok) merged in at IPO; no separate xAI listing. Operating loss; Starlink ~61% of ~$18.7B FY2025 revenue.
- **New entity page**: [[../philosophy/entities/spacex]] — tier `observation-only`; post-IPO 90-day blackout through **2026-10-08**; after blackout classify as Tier 3 pending profitability gating.
- **Synthesis**: [[inbox/2026-06-13-spacex-ipo-market-impact]] — macro impact (S&P +0.5%, Nasdaq +0.3%, Dow +0.7% on IPO day); TSLA +1.8% Musk-halo; RKLB/SPCE competitor displacement; bubble_guard flag (P/S ~95× on loss-making company); CFRA sell-rated at listing.
- **Forward calendar updated**: `wiki/08_forward_calendar.md` June 2026 block — SpaceX row marked ✓ DONE; blackout expiry, FOMC event-window, and QQQ inclusion watch-item added.
- **No signal slot populated** — 90-day blackout rule is active and FOMC event window (06-17) further restricts new position openings.
- **Contradiction / open item**: SPCX bubble_guard score cannot be computed until it clears the blackout and enters the FOM screener. Valuation at loss-making + P/S ~95× places it in the same risk tier as the names already on `wiki/07_ai_bubble_audit`'s at-risk list; flagged for post-blackout evaluation.

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

## 2026-06-10 — finviz schema 5 個 TO_ADD 欄位接線 (Forward P/E / Earnings / ATR / Inst·Insider Own)
- 主理人指令 (年度作戰表 / finviz_schema 後續): 把 `raw/metadata/finviz_schema.json` 標 TO_ADD 的 5 欄從文件落到 code。
- `data/finviz_elite.py`: (a) **Forward P/E** 接進 `finviz_row_to_dims` valuation (`pe_eff` = forward 優先、trailing 退而求其次 — 成長股 trailing 偏高)。(b) 新增 `finviz_row_to_flags()` — 維度不帶的閘門/水位: 財報黑窗 (`_days_to_earnings`, 窗 = risk_config `earnings_blackout_tier1_days`=3)、ATR/ATR%、Inst Own/Insider Own 水位、軋空預警 (Short Float≥10% ＋ Insider Own≥10%; breakout 由 rally 連續起漲確認)、200d 乖離 >30%。(c) 新增 `atr_position_size()` 純函式 (stop = entry−k·ATR; 股數 = equity·risk%÷(k·ATR), 受 `max_position_pct` 上限; risk%/上限由呼叫端給, **不讀 risk 政策檔**)。(d) `write_scan_recommendation` 嵌入 per-row `flags` + 頂層 earnings_blackout/squeeze_watch/overshoot_200d 清單 (向後相容)。(e) rally CLI 加 ⚠️E/🔥sq/⛔乖離 標記。
- `finviz_schema.json`: 5 欄 TO_ADD → active; `gates.earnings_blackout` / `short_squeeze_alert` 狀態翻 active; 補 `dimensions_consumed_now` flags 區; 註明 Custom view 要加的 5 個 header name。
- **未竟手動步驟**: 在 Finviz Custom view 勾選 'Forward P/E','Earnings','ATR','Inst Own','Insider Own' (帳號端 UI; 缺欄位優雅降級為 None)。
- `finviz_row_to_dims` 回傳 key 形狀不變 → `rally_signal.assess` (只取 DIMENSIONS keys) 不受影響。+6 tests; finviz/rally/basecross 相關 75 tests 綠燈。recommend-only, 永不下單。

## 2026-06-12 — P1 持倉更新(2 截圖,2026-06-11 收盤基準)
- 新 raw:`raw/principal/2026-06-11-snapshot-p1.md`(grade A)。可見 16 檔小計 ≈$6,696;清單 ~$202 截斷、現金不可見 → 下限快照。
- 寫回:`wiki/positions.md`(stub→live)、`portfolio/index.md` §1/§2、`portfolio_audit.py::PORTFOLIO_1`(32→16 檔)+ `CONCENTRATION_CONTEXT_USD.us_broker_p1` 11,374→6,696、`sleeve_classifier.py::P1_HOLDINGS_USD`。
- 結構:舊槓桿 TARK/LABU/SBIT/NOWL/AAPB/RBLU 已出(合 06-07 出清指令),**但新開 2x 單股一批(CRWG/MSFU/PTIR/CRMG/LULG ±NXPX)≈28% 可見部位** — 槓桿紀律問題換標的重現,待 Risk Officer 重審。
- **跟進(TBD)**:(1) SIVEF 解碼(OTC F 股,$891 = 13% 可見部位);(2) NXPX 驗證是否 2x NXPI;(3) 截斷列確認(推定 APA);(4) $202 以下尾部 + 現金需補截圖;(5) 16 檔的 entry/catalyst/invalidation 待 principal 補。
- audit 重跑:`portfolio-audit-2026-06-12.json` — P1 verdicts:**SELL ×5(MSFU/PTIR/CRMG/LULG 槓桿 decay + INTU low-FOM 36)、TRIM ×1(CRWG)**、HOLD ×10。槓桿紀律問題經 Risk-pipeline 確認。
- ⚠ 事故記錄:第一次重跑時 `main()` 的 `today` 硬編碼 2026-05-30,覆寫了歷史 `portfolio-audit-2026-05-30.json`;已從 6/1 的 .bak 還原(6/11 21:00 的後續微改不可復原),並把 `today` 參數化為執行日(檔名隨日期,不再覆寫歷史)。
- TBD#1 已解:**SIVEF = Sivers Semiconductors**(STO:SIVE,principal 2026-06-12 確認)。論點 = CPO 外部光源(ELS)咽喉點;6/11 +12% 催化 = GlobalFoundries 合作(B 級源 ×2 已查證)。新實體頁 `philosophy/entities/sivers-semiconductors.md`(researcher);positions/portfolio_audit/index.md 同步更新。財務體質 TBD(需 A 級財報源)。

## 2026-06-12(b)— P2 複委託 8840 全帳本入庫(3 截圖,06-11 收盤基準)
- 新 raw:`raw/principal/2026-06-11-snapshot-8840.md`(grade A,字母序 A→Z 完整 24 檔,≈$9,482;成本欄截斷僅近似)。
- 寫回:`portfolio_audit.py::PORTFOLIO_2`(舊 26 檔換新 24 檔)、`CONCENTRATION_CONTEXT_USD.complementary_p2` 3,000→9,482、`wiki/positions.md` 加 P2 段、`portfolio/index.md` §1/§3。
- ⚠ **舊 P2 清單(ZM/PEP/DIS/DOCN…26 檔,05-30)與 8840 實帳幾乎無交集** — 疑為另一容器或混帳;已被取代,出處待 principal 釐清。
- **OPITQ 1,000 股歸零(破產)→ 稅損收割候選**,健檢新增「市值歸零→清倉(稅損)」規則。
- UI 健檢擴成雙帳本(P1/P2/全部切換);audit 將以新 P2 重跑。

## 2026-06-12(c)— 上漲 DNA 研究 + 20 年回測 + 模型校準(rule-based,零 LLM 在環)
- 新引擎:`backtest/rally_dna.py`;月線湖補建(576 檔 period=max 1mo,先前為 0)。輸出 `outputs/rally-dna-2026-05-01.json`、寫回 `wiki/06_rally_dna.md`。
- **DNA 校準**:原 -55%/1.3×量 只抓 1/8 點名案例 → 網格後定案雙 preset:broad(-35%/無量閘,7/7 案例,超額+20.5%/筆)+ deep(-55%/1.3×,超額+49.8%/筆)。全網格 win 44-46% = 穩健。
- **九轉**:月線 sell-9 逃頂無效(≈基線);**buy-9 抄底有效**(12 月中位 +28.2% vs 基線 +14.0%)。
- **瘋狂延續**:blow-off 後 6 月續漲 62.6%、中位續漲 +61% vs 回撤 -17% → 持有者移動停利、未持有者不追(最後老鼠的解法是紀律不是預測)。
- **2026-27 推演**:QQQ 馬可夫+MC 中位 +27.9%、P(正)=85.8%;⚠ iid 抽樣低估尾巴,維持 evidence-gated。
- **每天買推薦(5y 日線近似)**:技術閘裸跑 2022 為負 → regime/燃料閘是系統的核心而非裝飾。揭露:倖存者偏差、9 維無歷史快照、僅價量下界近似。

## 2026-06-12(d)— DNA v2:底層證據貝葉斯 + 四態馬可夫 + 反身性監控上線
- `rally_dna.py` v2:(a) **經驗貝葉斯似然表** P(報酬|深殺/buy-9枯竭/量縮):勝率不隨證據變(≈43%)但**期望隨證據單調放大**(0證據+17% → 3證據+70.6%,超額+61.4%)→ 證據數定倉位不定勝負。(b) **觸發點基本面指紋**:MU=教科書錯殺(價-41%營收+62%);LITE/COHR 觸發時營收仍衰退=市場買前瞻拐點;FCF 觸發點普遍深負(這就是便宜的原因)。2019/2023 案例 out_of_window(yfinance 年報限制,Polygon 可補)。(c) **四態馬可夫**:當前=mania;mania→crisis 直接轉移=0%(瘋狂先降溫不直接崩);唯一負期望態=crisis;bear-非crisis 是抄底熱區。MC 至 2027 末中位+26.1%。
- 新 `scoring/reflexivity.py`:近高×Finviz 機構/內部人流向×FCF YoY。首掃 89 近高 → **15 斷裂警告**(GWW/HUM/SLAB/ICHR…多為防禦輪動領頭=輪動晚段訊號)。修了 finviz token 載入(.env 直讀)與 DIMENSION_VIEW 欄位。
- 寫回:wiki/06 加 §7-9 + 反身性段;新 `wiki/07_sector_handoff.md`(AI變現/加密/太空接棒的可證偽觸發器+監控排程)。

## 2026-06-12(e)— DNA v3:walk-forward 驗證通過 + 成本入帳 + 阿卡西匹配器 v1
- **Walk-forward**:broad 參數(2019-26 案例選定)在 2005-2018 OOS:3,216 筆、超額 +19.4%/筆 = 保住 IS 85%,非過擬合。
- **成本**:0.4% 來回對月線系統無感(mean 27.8→27.4%);日線近似被砍 32% → 低頻持倉方向確認。
- **`dna_match_today`(阿卡西記憶 v1)**:7 案例觸發月特徵質心(dd36 -13%/距MA10 +22%/buy9=10/r3m +37%)→ z-score 最近鄰。Top:ONTO/OKE★/RVTY/COLM★/ODFL★/UNH★/ELV★/CNC★(健保群聚=2025 醫療屠殺修復區)。參考專案(Danelfin/IKnowFirst/Qlib)定位:差異化在本地湖+紀律層+PIT 誠實,不重造。
- 質心洞見:**贏家觸發點都已強力修復(+37% 3 月動能),不是還在坑裡** — 抄底=買修復,再次驗證。

## 2026-06-12(f)— 案例庫 v2(60 檔自動發掘)推翻點名質心 + 匹配器三面化 + Qlib/Chroma 計畫
- `discover_bull_cases`:25+ 年全湖自動挖牛票(每時代 top10、板塊上限 3)→ 60 案例,中位 24mo +1294%(倖存偏差揭露)。**發現:點名 7 案是淺基少數型;系統質心=深殺 -58%+暴力修復 +65%;小型股 40/60;Healthcare 16≈Tech 18**。兩型質心並存。
- 匹配器 v2:質心換案例庫 + Finviz 三面(dna_plus=技術45/基本面25/買盤20/消息10)。Top:SMCI(買盤100★)/ESTC/HOOD/SWKS★/HUM★…健保群聚 6/15。⚠ HUM/UNH/ELV 同列斷裂警告 → 交叉剔除規則入 wiki。消息欄 TBD。
- `docs/QLIB-VECTORDB-PLAN.md` + pyproject `[akashic]` extras:Chroma 進入條件(案例>150 或文本檢索需求)、Qlib 先 WSL 驗證/vectorbt 輕量先行、Danelfin/IKF 定位 D 級旁證 watchlist-only。
- wiki/07 觸發器狀態更新(principal 供數):CapEx 🟢 / BTC ETF 🔴 -$1.67B週 / SPCX ⏳ / 斷裂未擴散科技核心 🟢 → 維持偏多+動態 sizing。

## 2026-06-12(g)— v2.1:權重誠實化 + 自動雙濾鏡 + Qlib 實測可跑
- **權重問題正面回答**:45/25/20/10 是先驗非擬合,且 Finviz 無歷史快照=無法誠實回測。補救:(1) 敏感度實測 Spearman 0.92-0.94/top10 重疊 9/10 → 排名對權重不敏感;(2) 評分落盤 `dna-scores-log.jsonl` 啟動前瞻校準;(3) v2.1 權重 40/30/20/10,消息(noisy+常None)→ 反身性負懲罰。
- **自動三欄分流**:斷裂警告無條件剔除;≥85 可入候補/≥75 watch。2026-05:可入 0 / watch 5(SMCI/ESTC/HOOD/SWKS/DXCM)/ 剔除 4(**HUM、ELV 自動剔除**:52w近高+機構流出+FCF -84%/-30%;UNH inst 仍流入留觀察)。修正:反身性近高判準從 dd36 改 52w(ma-scan)。
- **Qlib 實測:Windows + py3.12 可裝可 import(pyqlib 0.9.7)** — 編譯炸裂是過時資訊;剩 workflow 級驗證(lake→qlib bin 轉換器),計畫文件已更新。
- 分倉紀律入 wiki:deep-kill ≤10-15% 曝險、硬停 20-25%、時間停損 2 季無 FCF 改善;SMCI Type B 警示記錄(買盤滿分但 TTM FCF ~-$7B)。
- 待辦序(review 採納):(1) HUM/COHR Polygon PIT 季度序列;(2) 多源消息接通(Polygon news);(3) 案例庫月度排程累積。

## 2026-06-12(h)— 排程上線 + Polygon PIT 客戶端 + Danelfin 金礦交叉驗證
- **排程(Windows 工作排程器)**:SharksDNA-Morning(07:40 二~六:lake 刷新→EOD ma-scan→reflexivity→rally_dna 評分累積)+ SharksDNA-PreOpen(21:10 一~五:`position-brief-<date>.md` 艙位調整 brief)。新模組 `daily_dna_routine.py`;機器需開機。首份 brief 已產出(mania 態→不開新倉、換股×7、減碼×5、清倉 OPITQ)。
- **Polygon PIT 客戶端**(`data/polygon_financials.py` + 3 tests):季度 rev/OCF/CapEx/FCF,**filing_date 為 PIT 錨點**;429 退避;同季 YoY。⚠ **blocker:.env 的 POLYGON_API_KEY 是空值** — principal 填 key 後 HUM/SLAB/ICHR/COHR 序列立即可拉。
- **Danelfin 金礦群交叉(D 級旁證規則實戰)**:其 top10 有 9 檔金屬礦業(AI Score 9-10);我方引擎:全部距 52w 高 -27~-56%、RSI 32-44、零修復訊號、GLD RSI 24 → **被殺進行中、修復未確認 = 進 DNA watch 池等觸發,不接刀**。礦業 11 檔已入湖(BTG/KGC/VALE/EQX/CDE/B/AG/HL 新增)。

## 2026-06-12(i)— Polygon key 入庫,PIT 序列首拉成功(HUM/SLAB/ICHR/COHR ×20 季)
- key 已入 .env(gitignored 確認)。`pit-fundamentals-2026-06-12.json` 落盤,filing_date 錨點齊。
- **數據限制**:Polygon 標準化現金流表無 CapEx 細項 → FCF 無法直接導出;cash 腿先用 OCF 趨勢,FCF 補課走 yfinance 季表合併(TODO)。Q4 多無獨立 filing_date(包在 10-K);SLAB 會計年度偏移(2027Q1 filed 2026-05)。
- **PIT 發現**:(1) **HUM 基本面腿有爭議** — 營收加速(+8.4%→+23.5% YoY)且 2026Q1 OCF 1,254M >> 2025Q1 331M(年度 FCF -84% 主因 2025Q4 OCF -1.65B 保險季節性)→ 斷裂警告的基本面腿可能過早,維持剔除但下次申報後複核。(2) **COHR = Type B 教科書**:營收連 8 季 +9~28% 但 2026Q3 OCF 轉負 -94M(擴張燒現金)。(3) **ICHR 剔除獲 PIT 支持**:營收忽上忽下、OCF ~0。

## 2026-06-12(j)— v3 三件高價值迭代落地:PIT 合併器 + 可解釋評分 + 規則引擎
- **`data/pit_merger.py`**:Polygon(filing_date)× yfinance 季表(FCF/CapEx ±10 天對齊,fcf_source 標籤)。`pit_contested` 判定:**HUM=True**(營收加速+OCF 改善,年度負讀數疑季節性)、COHR=False(OCF 真惡化,Type B 確認)。
- **匹配器 v3 可解釋輸出**:SHAP 式分解(SMCI 83.8=技38.4+基19.2+買15.0+反11.2)+ 每檔附最相似 Top3 歷史案例與實際後續報酬(SMCI≈TRGP20/AEO96/BBY97,+1000~1900%)。狀態感知權重:mania → reflexivity 0.10→0.15。
- **規則引擎**(`config/dna_rules.json` + `apply_rules`,宣告式+rules_fired 留痕):**HUM 自動=剔除+🚩human_review**(break-hard-exclude → pit-overrule-human-review 兩條依序 fire)— 邊緣案例不再人工掃描。deep-kill sizing cap 註記自動掛。
- `docs/ARCHITECTURE.md`:五層映射(演進不翻修)、依賴採用準則、風險登記簿(failed-analogs 子庫 TODO)。

## 2026-06-12(k)— Failed-analogs 子庫 Phase 1:deep-kill 真實存活率 + sizing 數據化
- 新 `backtest/failed_analogs.py`(+3 tests):664 deep-kill 觸發 × 固定 24m 視窗 → monster 42.9% / ok 31.2% / dud 11.9% / **disaster 14.0%(中位 -50%)**;存活率 74.1%(倖存者宇宙=上界)。
- **AXTI 雙尾教材**:2001 觸發 -97% vs 2025 觸發 +4,907% — 同票同形態相反結局,sizing 是全部。失敗群聚 2000-01 → 與 markov 互鎖:crisis 態不開 deep-kill。
- **Sizing 公式透明化**:cap=拖累預算2%/(P損×損幅)=15%,壓力版 **11%(採用)**;規則 R4 更新為數據驅動。
- **Phase 2 上線**:Polygon delisted 收集器(`collect`,manifest 續收)掛進晨間排程(10 檔/日)→ 分母逐日誠實化。

## 2026-06-12(l)— Bootstrap CI + AXTI 型規則 + brief 系統健康區塊
- **Bootstrap(10k 重抽,seed 固定)**:存活率 74.1%,90% CI **71.2–77.0%**(n=664 → CI 窄);cap 公式加 CI 悲觀端(P損/損幅 95 分位)取低者 → 維持 11%。
- **失敗類比進相似度池**(成功 60 + 失敗 172 同池):新規則 `axti-similar-failures`(Top3 含 ≥2 失敗 → human_review+倉位減半)。首批 fire 12 檔:**DXCM 近鄰失敗×3、ESTC ×2** — watch 名單現在自帶死亡氣味偵測。
- **brief v2**:新倉名單帶 🚩/⚠近鄰失敗標記;新增「系統健康」區塊(存活率 CI、案例庫規模、規則觸發統計、數據新鮮度)。單筆風險 ≤1-2% 總資本寫進 sizing 行。
- review 採納記錄:樂透型=衛星倉原則、死亡原因標註(delisted/bankruptcy/FCF 永久惡化)待 Phase 2 分母成長後加欄位。

## 2026-06-12(m)— World Model v1:GSCPI/GPR 世界事件 → DNA 權重/分桶/sizing(上線首日三事件齊發)
- 設計輸入:watchlist/plan.md(外部顧問草案,untracked)— 已全面翻譯成 repo 原生架構;其 akashic/ 路徑、Mesa ABM、LanceDB 遷移不採納/延後(裁決見 wiki/23_world_model.md §6)。命名:外部稱「Phase 3」與 ROADMAP Phase 3 撞名 → 落地統一叫 World Model,掛 ROADMAP Phase 3 item 7 延伸。
- 新模組:`data/world_indicators.py`(GSCPI/GPR 免 key grade-A;BIFF .xls 需 xlrd → pyproject [world] extra;NY Fed 日期是文字 '31-Jan-1998' 已容)+ `regime/world_monitor.py`(metrics → config/world_events.json 數值條件求值成布林旗標;never-raise,單源失敗退 data/lake/world/ 快照標 stale)+ `scoring/global_exposure.py` + `config/world_exposure.json`(台鏈 0.9/光通訊 0.7/中國營收 0.6,靜態 git 版控=PIT 安全)。
- 閾值=分位數定錨(1985+ n=497:GPR p95/p99=169/330;GPRC_TWN p95/p99=0.25/0.37),非外部草案的虛構量綱;每月重校。TARIFF/CYBER 無免費機讀源 → manual_flags(D/E 級不得自動觸發,CLAUDE.md §5)。
- DNA 整合(最小侵入):`apply_world_weight_shifts`(沿 mania 先例,donor 不破 0.05、總調幅封頂 0.10)、`dna_plus × world_factor`(=1−exposure×penalty,地板 0.65;無事件=1.0 零行為差異,敏感度診斷在折減前計)、ctx_flags 進規則引擎(新規則 world-ts-high-taiwan-review / world-gscpi-deepkill-caution)、deep-kill cap 乘數在 brief 消費端套(failed-analogs 保持純存活統計)。dna-scores-log.jsonl 增 weights_effective/world_events/global_exposure/world_factor 欄。
- 排程:morning 新增 world-monitor 步(reflexivity 之後、rally_dna 之前);position brief 插「全球風險」區塊(§2,後段重編號)+ cap 行自動顯示乘數;daily_brief 三渲染器加 🌍 區塊;CLI `sharks world-monitor`。
- 實跑(2026-06-12):**TS_HIGH(GPRC_TWN 0.489 >p99,60月z 2.24)+ GSCPI_SPIKE(1.77,單月+1.15σ)+ GPR_ELEVATED(184.2)三事件齊發**。權重 40/30/20/10→35/30/15/20;deep-kill cap 11%×0.75=8.2%;煙測:ONTO(台鏈 0.9)70.4→54.6+human_review,UNH(0.15)63.4→61.1。
- 回寫:wiki/23_world_model.md(新,08 槽被 forward_calendar 占用)、wiki/01_macro_state.md §4c(us_china_tension_index=elevated — universe.yaml TSM 60% cap override 正式有機器供值;編輯前已 state snapshot 05-29 版)、wiki/07 監控排程表 +1 列、ARCHITECTURE 風險登記簿 +4 列(GEOPOL_TS/GSCPI_SPIKE/TARIFF_CASCADE/vintage 缺口)+ 層表、ROADMAP item 7 延伸註記。
- PIT:GSCPI/GPR 就地修訂無官方 vintage → 本地 vintage 自今日起前向累積 data/lake/world/(gitignored+.gitkeep);之前的回測不得用世界事件特徵。測試 +38(world_monitor 22 + global_exposure 16),全套 1037 綠。
## 2026-06-12(n)— World Model 全量衝刺:ABM + 向量案例庫 + UI 面板 + 曝險網證 + 排程全自動化(4 平行 agent)
- 主理人指令:不照外部草案分期時程,全部任務一次落地、全部加入排程、階段性 commit。4 個平行 agent(檔案互不重疊)+ 主 session 整合,5 個 commit。
- **ABM**(`regime/abm_supply_chain`,commit 4b288d1):純 Python+numpy 無 mesa(採用紀律,mesa_note 記錄引入條件)。情境 NONE/TS_HIGH(×0.65)/TS_BLOCKADE(×0.25 尾部)/TARIFF_NEW(×0.85),先驗依 GPRC_TWN 分位數分帶 — 全部顯式猜測含 _doc(1985+ 樣本內 0 次台海封鎖,無可擬合)。首跑:extreme 帶,預期斷供 2.09 季,deep-kill 折減全路徑中位 -0.21pp / TS_HIGH 條件式 -4.73pp(與 cap 乘數不疊乘)。24 tests。
- **向量案例庫**(`memory/case_store`,commit 4406eaf):QLIB-VECTORDB-PLAN v3a 入庫條件實際已達(212>150)→ Chroma/numpy 雙 backend、MATCH_FEATS z-score 同尺(norms.json)、冪等 sync(60 win+152 fail;20 筆 NaN fail 依不發明原則跳過)。SMCI 近鄰 TRGP/CRUS 與 rally_dna brute-force 交叉一致;brute-force 保留,store=持久化/檢索層。LanceDB 維持不採。13 tests。
- **UI**(`ui/server` /api/world + 🌍 卡片,commit 9b63eb7):live 驗證三事件 + cap ×0.75;任何失敗收斂「未啟用/無數據」。7 tests。
- **曝險網證**(researcher → wiki/24_exposure_validation.md):台鏈 20 檔逐檔網查 — 12 CONFIRMED-HIGH、7 PARTIAL、1 WRONG(SIVEF 自有廠在蘇格蘭 Glasgow!)。結構性發現:0.9 群組混淆一階生產斷供與二階需求遞延(設備商台灣營收 19-38%)→ config v2:SIVEF/COHR/LITE/ARM 移出台鏈(降 0.7/0.45)、AMAT/LRCX/KLAC/ASML/ONTO/TER 拆出 taiwan_demand_equipment 0.6(不觸發 human_review)、新增 AAPL/ASX/UMC(CONFIRMED-HIGH);optics_cpo _doc 修正(製造在泰/馬/蘇格蘭,真實軸=關稅+TSMC DSP 間接)。china_revenue 僅 2/12 驗證(TXN/INTC),其餘 TBD;AVGO ~99% TSMC 占比單源(Counterpoint)同溫層風險已標。
- **排程全自動化**:morning 鏈現為 lake→scan→reflexivity→world-monitor→rally_dna→failed-analogs→case-store sync(日)→ABM(週二 gated)→閾值重校建議(每月 1 日 gated);`world_monitor.recalibrate()` 建議制(drift>10% 標旗;live 首跑 4 建議 0 旗 = 校準健康)。`scripts/install_dna_schedule.ps1` 冪等註冊取代 ad-hoc 任務(已執行)。brief §2 增 ABM 行。
- 測試:全套 **1083 綠**(+46:ABM 24/store 13/UI 7/recalibrate 2);wiki lint 乾淨。
## 2026-06-12(o)— 即跑驗收:全管線生產實跑 + 曝險地圖 v3(Round 2 證據收割)
- 主理人指令:不等明早排程,現在就跑全部。`daily_dna_routine morning` 生產實跑:lake 584 檔(err 0)→ ma-scan → reflexivity → world-monitor(3 事件 live)→ rally_dna(scores logged)→ failed-analogs collect(Polygon 限速,長跑中)→ case-store sync(隨後自動)。
- **世界模型端到端生產驗證**:weights_effective 35/30/10/25(mania + 世界事件疊加,總和 1.0);world 規則實際開火 world-gscpi-deepkill-caution ×17、world-ts-high-taiwan-review ×1;**ESTC raw 87.1(本可入候補)被 world_factor 0.887 壓到 77.3 → watch — 世界模型實際在 TS_HIGH 期間擋新倉**;scores-log 新欄(dna_plus_raw/global_exposure/world_factor/world_events)全落盤。
- **preopen brief 即產**(21:10 排程外加跑):全球風險區塊 + ABM 行 + cap 11%×0.75=8.2% 全亮;新警訊:**持倉 AMAT 進反身性斷裂交集**。
- **曝險地圖 v3**(3 平行 researcher,Round 2 → wiki/24 §6):china_revenue 12 檔全驗畢(QCOM 45.9% ship-to/LVS 57% 澳門/WYNN 52%/ADI 26%/TSLA 22.1%/MCHP 17%/AAPL 15.5%;弱環 CAT ~5-10% 已標;SBUX Boyu JV 後通道=股權+權利金);**AVGO 升 A 級一手源**(自家 FY2025 10-K:~95% CM 晶圓 TSMC、封測 TSMC/ASE/SPIL — 同溫層一直在引 Counterpoint 而硬數字躺在 filing 裡);**ANET 入台鏈 0.9**(獨家 Broadcom 矽 ~95% TSMC、組裝馬/越/墨 — 與 NVDA 同款「命脈在投片」邏輯,庫存遞延通道已標);SIVEF WRONG 二次確認(Glasgow + GlobalFoundries CPO)。下版候選:china_revenue 拆兩層(≥25%/5-15%,CAT/LVS 同權重失真一個量級),需 Risk Officer 裁決。
## 2026-06-12(p)— Review 採納裁決 + 本地小模型線 + Risk 佇列 + 存活率動態化
- 外部 review 六項裁決:採納 4(存活率月→**週六全量重算** gated step;斷裂交集→Risk Officer 佇列;本地模型加速研究線;dashboard 已有=免做)、駁回 2(**ABM 斷供季數進 DNA 特徵=PIT 違規**,歷史案例無 ABM 值會汙染質心,sizing/規則通道維持;**brief 改 LLM 生成=違反 LLM-BACKTEST-PROTOCOL**,改為可選 grade-E 評論區)。LanceDB 時間旅行:world vintage 今日才開始累積,無歷史可回測,維持 state 快照路線。
- **`ai/research_agent.py`(nemoclaw 線)**:本地 nemotron-3-nano:4b(RTX 5070 12GB 誠實上限;顧問宣稱 32B/70B 不可行)— gather_context(lake info/reflexivity/dna row/world/案例庫近鄰)→ grade-E 草稿(假設/反方/待驗證+檢索詞)→ outputs/research-draft-*。never-raise 降級已 live 驗證(Ollama 未開);永不直寫 wiki、不觸發部位(CLAUDE.md §5)。
- **preopen 三件**:(a) 可選本地模型評論區(grade-E 標注,失敗靜默跳過);(b) `risk-review-queue.jsonl` append-only 冪等佇列 — 首日 15 筆:AMAT(high,持倉×斷裂)+ 14 檔 human_review(含 rules_fired 審計與 world 上下文,SMCI 帶台鏈規則);(c) brief 照舊 rule-based。
- **morning 新 gated**:週六(美股週五收盤後)`failed_analogs.main` 全量重算存活率+CI+cap — 分母隨每日 collect 成長,11% 上限變動態。collect 觀察:manifest 384 行多為 too_short 跳票,budget 計「可收」不計嘗試 → 長跑屬設計內(Polygon 5 req/min)。
- 測試 +7(research_agent 4 + risk_queue 3)= 全套 1090;wiki/23 §6 增 7-10 項裁決記錄。
## 2026-06-12(q)— 生產事故修復:collect 涓流懸掛(2.5h)→ 雙保險硬上限
- **事故**:morning 實跑中 failed-analogs collect 吊死 2.5h — manifest 停在 384 行(ARIZ),CPU 每小時僅 +6s,一條 ESTABLISHED socket 掛 198.44.194.59:443(無反解)。**根因**:requests scalar timeout=30 只管位元組間隔,伺服器涓流回應可無限延長;且 budget 只數「可收」票,掃 too_short 長段時嘗試數無上限。
- **處置**:kill 進程(所有上游輸出早已落盤;collect 為可續收累積器,零損失)。
- **修補**(`failed_analogs.collect`):(a) `max_seconds` 牆鐘預算(預設 20 分,晨間鏈永遠走得完);(b) 每筆抓取包 thread+future 硬性 60s,涓流也走得掉(超時棄置 worker 換新池);(c) 回傳加 `elapsed_s`。Live 驗證:budget=3/240s → 248.2s 乾淨退出,manifest 384→402 穿過卡點。
- **觀察**:manifest 402 行全為 too_short/err — 2010 後下市且 ≥48 根月線的票在字母序前段極稀,**failed-analogs 的下市票分母至今 = 0**,每日 20 分預算下會慢慢養;存活率 74.1% 仍是湖內倖存者宇宙上界(已知偏差,docs 已標)。
- 案例庫 re-sync(212 筆,吃進今晨新 rally-dna norms);全套 1090 綠。

## 2026-06-12(r)— [09:18 ET] recommendation | 首份 live 日度 10-signal(6/10 槽,mania 防守日)
- 產出:`wiki/05_recommendations/2026-06-12.md` + `outputs/picks-2026-06-12.json`(as_of 13:10:04Z = 09:10 ET 盤前,沿用 preopen brief 聚合時點;訊號依 PIT 規則於 09:30 開盤成交)。05-29 之後首份、新版管線(DNA+World Model+audit)下第一份正式日度輸出。
- **槽位**:long_new ×2 = null(mania + DNA 可入候補 0 檔;ESTC 87.1 被 world_factor 壓到 77.3)、short_new ×2 = null(無空頭真跌確認;FOMC 06-17 窗內)、followup ×6 全滿:AMAT trim25%(斷裂交集+bubble_guard −40)、CRWG trim34%+8%trail(held-winner 覆核)、INTU exit(趨勢破線)、MSFU/PTIR/CRMG exit(sleeve 不留槓桿)。
- **overflow(槽滿未入,仍有效)**:LULG exit、OPITQ 清倉 — 新欄位 `followup_overflow` 入 JSON,markdown §5 同步,確保不丟單。
- Risk Officer 同 session 切換覆核:無填充、全減碼方向與 mania+三世界事件一致、confidence 0.65–0.75 無虛高 — passed。Discarded 8 組含換股腿(MSFT/ASML/PLTR/CRM…一律走未來 long_new 過 DNA 濾鏡)。
- 跟進:followup 執行後 positions.md 須按 audit 結果更新;LULG/OPITQ overflow 若明日仍未執行應重新佔槽。
## 2026-06-12(r)— 夜班 wave1:時間旅行回放 + regime 轉移表 + 行為偏差層(plan2 裁決執行)
- plan2.md(94KB 外部草案)裁決:採納 歷史回填/短週期時間旅行(關鍵洞察:每次下載含全史 → 可離線重建任意過去時點的事件求值,vintage=synthetic-revised 誠實標注)、行為偏差分數、損失厭惡旗標;**LightGBM regime 預測改為先建經驗計數基線**(340 月樣本上 ML 是過擬合邀請函;未來模型必須先打贏這張表);LanceDB 索引優化再次駁回(Chroma/numpy,212 筆)。
- **頭條發現(backfill,QQQ 1999+ n=327)**:GSCPI_SPIKE 月份前向 3m +1.35%/6m **-0.18%** vs 基準 +4.16%/+8.37% — **唯一明確跑輸的事件**;TS_HIGH 46 個月不低於基準(地緣恐懼≠賣訊);GPR_EXTREME 僅 3 個月(911/伊拉克,軼事)。轉移表:GPR elevated 砍熊市出場機率 1/3;mania 在 GSCPI spike 下更黏;26 年唯一 bear→crisis 在 spike 下。
- **行為偏差層**(scoring/behavioral_bias,純函數顯式先驗):今日實時 **8.5/10**(TS_HIGH+GSCPI+TWN_Z60+VOL_PANIC+BREADTH_BREAK 全組件)→ **mania 過度自信警語在真實數據開火**進 brief。損失厭惡旗標已備,但 holdings_health 無 pnl/holding_days 欄(上游 entry TBD)→ 誠實緩接,不發明數據。
- **整合**:world_monitor 增 behavioral 區段(QQQ vol ratio + reflexivity 斷裂數自動取)+ 空快照防護(_payload_empty);brief §2 增三行(行為偏差/歷史鏡頭/下月態展望 — 全 observe-first);週六 gated 增 backfill+transitions 週更。
- **數據事故記錄(supersession)**:`data/lake/world/gscpi-2026-06-12.json` 為日期解析修復前寫入的空序列(首寫不可變)→ 依 CLAUDE.md §2 以 `gscpi-2026-06-12.v2.json` 接替(341 列,1998-01→2026-05;glob 排序自動選用);防護已加,此類事故不再。
- 測試 +48(backfill 13/transitions 19/bias 16),全套 1142 綠。commit ba84b4a(模組)+ 本條目隨整合 commit。

## 2026-06-12(s)— [09:30 ET] fix | UI「今日推薦」資料過舊 — /api/reco 改讀 canonical 日度
- **症狀**:dashboard 今日推薦面板停在 2026-06-10。**根因**:`/api/reco` 只 glob `outputs/daily-reco-*.md`,而該家族在 codebase 無產生器(06-10 是先前 session 的一次性 agent 手稿)— 監看了一條死水線。
- **修補**(`ui/server.py`):新 `latest_reco_file()` — canonical `wiki/05_recommendations/YYYY-MM-DD.md`(嚴格日度命名,README/archive/專題頁不參賽)與 legacy `daily-reco-*` 兩家族取日期最大、同日 canonical 優先;`strip_frontmatter()` 剝 YAML(marked 渲染醜)。+4 tests(ui_server 27 綠)。
- server 重啟(舊 PID 6772 系統 python → 44384 venv python,repo root cwd);`/api/reco` 實測回 2026-06-12。
- 註:screener 主表 as_of 2026-06-11 屬正常(lake = EOD,今日美股未收盤);log 撞名記錄:本日有兩條 (r)(日度 10-signal 與夜班 wave1),後續沿用字母續排。
## 2026-06-12(s)— 夜班 wave2 + 下市票分母「免費層結構性阻斷」實證(重要裁決待主理人)
- **wave2 落地**(commit 009e195):UI 世界面板補行為偏差(≥6 警示徽章+mania 註記)/下月態展望/歷史鏡頭三行(全 observe-first,缺源不破版,UI 測試 32 綠);collect 候選優先級(殼名/權證尾碼降權、2012-23 死亡年優先 — 純重排不丟棄)。wiki/index MOC 補齊 06-24(commit 2a390ca)。
- **結構性阻斷實證(夜間三連probe)**:(1) Polygon 免費層對 ABMD(Abiomed,2022-12 被併下市)aggs 回 **0 根**(status OK / resultsCount 0 — 免費 ~2 年窗 + 下市票無資料);(2) yfinance 對 ABMD/AAWW 回 0(Yahoo 清空下市票);(3) Stooq 有 JS 反爬牆。→ **48 根月線門檻在免費層永遠達不到,Phase 2 collect 照原設計不可能成功**。今晚 570 個 too_short 全是免費層假象(含真公司)。
- **處置**:夜間批次停止(再掃只是燒 API);失能原因寫進模組 docstring + 風險登記簿;**manifest 毒化警告**已記(付費升級後須清 too_short 條目重掃,否則永久跳過可用票)。
- **待主理人裁決**:deep-kill 真實存活率需要付費數據 — Polygon Starter $29/mo(5 年史)或 Sharadar 級 survivorship-free 源;這正是 plan.md「偶爾付費驗證」的標準場景。在此之前 74.1% 維持倖存者宇宙上界、cap 11% 取悲觀端、collect 排程保留(升級即自動恢復作用)。
## 2026-06-12(t)— 主理人「全部跑」指令裁決 + GSCPI_SPIKE 規則升級 + 晨間決策文件
- 指令三項裁決:(1) **GSCPI_SPIKE 升級採納**(config/world_events.json:cap ×0.85 + 罰則 0.10→0.15,_basis 引 27 年回放;今日與 TS_HIGH 疊加後 min(0.75,0.85)=0.75 實際 sizing 不變 — 變化在 GSCPI 單獨觸發日)。**TS_HIGH 不對等下調**:歷史均值不低於基準≠尾部安全(樣本內無封鎖),衝擊錨定 ABM 尾部。標主理人晨間覆核(philosophy/08 Risk Officer 轄區);(2) **方案 B(yfinance+Stooq)不重做** — 夜間已三連否證,證據入決策文件;(3) **collect 不重啟** — 結構性阻斷不因指令消失;改交付 `reset-thin` CLI(清免費層假 too_short,付費升級日一鍵啟用重掃,+2 tests)。
- `outputs/night-shift-summary-2026-06-12.md`:11 commit 帳 + 頭條發現 + 決策清單(A:Polygon Starter $29 單月衝刺,建議;B:已否證;C:維持上界)。
- monitor/preopen 已用新 config 重生;全套 1155 綠。
## 2026-06-12(u)— DataRouter 提案裁決:大抽象駁回、記帳內核採納
- 駁回理由:(1) 提案殺手賣點「yfinance 突破下市票 2 年限制」已被當夜實測否證(0 根)— 路由層救不了數據存在性;(2) lake 已是 local-first 層 + 各 client 自帶限速/fallback,再包 DataRouter = 983+ 測試付翻修稅換零新數據(演進不翻修);(3) 提案路由表本身有誤(rally_dna 跑在 yfinance 數十年月線湖上,非 Polygon)。
- 採納內核:`data/call_log`(per-source API 呼叫記帳,never-raise)— 接線 polygon financials/aggs-delisted、NY Fed、Iacoviello 四個受限呼叫點;brief 系統健康新增「API 用量(今日 UTC)」行。+5 tests。
- ARCHITECTURE 新增「數據源矩陣」表(裁決記錄 + 各引擎來源/限制/fallback 一覽)。
## 2026-06-12(v)— 「abc」指令:API 週累計 + curated 下市票清單(數據補強的不翻修版)
- **A**:call_log 增 summary_range(近 N 日累計);brief API 用量行升級「當日 ｜ 7 日累計」(週對週趨勢等記錄滿兩週才有意義,不發明)。
- **B**:`watchlist/delisted_candidates.yaml` — 17 檔 curated 高價值真亡者(BBBY/SIVB/FRC/SDC/FSR/TUP… 深殺後死亡型,每檔附 why;ABMD 留作可得性探針);`_candidate_queue` 升級 curated 永遠隊首(_load_curated 目標式解析,_yamlite 不支援列表故不用)。**作用日=阻斷解除日**(Polygon Starter 或 Tiingo key):reset-thin 清假條目 → curated 17 檔最先回填,每檔都是 deep-kill 分母的真貨。顧問提的 Stooq 已否證不採;Tiingo 需 key,留待主理人決策時一併考慮(免費 tier 是否服務下市票未驗證,不寫進承諾)。
- **C**:夜班續跑,23:05 巡檢輪不變。tests +5(curated 3 + summary_range 1 + 已有 reset-thin 2 計入前條),全套 1165 綠。
## 2026-06-12(w)— [10:39 ET] ingest | computer-hardware 看板截圖 digest:儲存複合體領漲 = mania 晚段確認
- 主理人傳入券商 watchlist 截圖(32 檔)→ raw/market_data/screenshot-hardware-board-2026-06-12.md(全表轉錄)+ wiki/inbox digest(grade D,盤中 ≈10:39 ET)。
- 結構:前五占四為 Phase 1 儲存(QMCO +9.2/STX +7.0/WDC +6.3/SNDK +4.9,真量)— 對照 alpha_library Phase 1(T12M 已 9-10×)與 bubble audit mania 分數(STX 77.1/WDC 73.3)= 晚段強勢確認非窪地;ANET +4.9(台鏈 0.9);quantum 分歧(RGTI/QUBT 漲 vs IONQ/QBTS 平);礦機/無人機/周邊收跌 = 魚缸只餵 AI-infra;6 檔成交 <10k 股屬噪音層(06-exclusions 閘下)。
- 裁決:不變更今日 10-signal(long_new/short_new 維持 null);持倉交集僅 HPQ(+1.3%,無動作);TBD:收盤後 lake 對賬價格、P/QCLS/BRAI/AMCI 身分未驗證不入 watchlist。

## 2026-06-13(a)— [12:30 TW] ingest | Finviz Elite live 全宇宙拉取 + header 比對 bug 修復(沉默殺死核心軸)
- 主理人指令「不要忘了 finvizapi 請繼續執行」→ 趁訂閱在線跑 live 全宇宙 rally 掃描(626 候選 → 603 rows)。**point-in-time 原始匯出落盤** `raw/market_data/finviz-export-universe-2026-06-13.csv`(自 06-10 以來首次新鮮 PIT 捕捉;06-10 主理人指令要求「訂閱在線時保存原始資料供日後離線回測」之兌現)。
- **發現並修復沉默 bug**(`data/finviz_elite.py` `_num`):Custom view(152)匯出用 Title Case 欄名(`52-Week High` / `EPS Growth Next Year` / `50-Day Simple Moving Average`),但 `_num` 用大小寫敏感的精確字串比對 → **`dist_ath_pct`(核心「深跌離高」軸)與 `growth` 自 06-09→06-12 全部 0/603 沉默歸零**;SMA50/200 貢獻亦被丟棄(`overshoot_200d` 連帶失能)。修法:`_num` 改大小寫不敏感(lowercased key map fallback)+ 補差異措辭別名(`52-Week High`/`50-Day`·`200-Day Simple Moving Average`)。覆蓋率 dist_ath 0→**603/603**、growth 0→**601/603**;overshoot_200d 現標 **111 檔**。`tests/test_finviz_elite.py` 25 綠,無回歸。
- **重掃結果**(`outputs/finviz-scan-2026-06-13.json`,source=universe,n=603):唯一 `buy_consider` = **OKTA**(連3,C63.7,🟢 連續起漲 3 期·分批/小倉);news 維持 0/603(Finviz 匯出無消息欄,設計使然)。recommend-only,永不下單。
- **重申帳號端未竟步驟(06-10 遺留,本次再證)**:Custom view 仍缺 `Forward P/E`/`Earnings`/`ATR`/`Inst Own`/`Insider Own` 五欄 → `earnings_blackout`(**風險閘**,[[../philosophy/06-exclusions]])、`squeeze_watch`、ATR sizing 三者仍暗(OKTA flags 全 null 佐證)。須主理人在 Finviz Custom view UI 勾選該 5 欄(缺欄優雅降級為 None,程式無法代勞)。
- **資料完整性註**:bug 期間 06-09→06-12 的 finviz-scan 排名低估 dist_ath/growth;唯 06-10 有原始 CSV 存檔可重評分(06-11/06-12 未經本 archive 路徑落盤,無法回補)。今起 live 路徑每跑必存原始,修復後分數誠實。

## 2026-06-13(b)— feat | Trading Society(矽基交易社會)ABCDE 全交付 + 溶入憲法(CLAUDE §10)+ wiki ingest
- 主理人指令「強力依照 grok.md 執行、自動選擇、溶入憲法、wiki ingest」。grok.md = 對話紀錄(402KB);可執行計劃 = 其中的 Trading Society ABCDE 規劃書。前次 session 已交付 **A**(`programs/trading_society/CORE_AGENT_ROLES.md` 7+1 角色)+ **E** 骨架(`simulation/society_orchestrator.py`)。本次補齊 **B/C/D** 並打通端到端。
- **B(Backtest+Tracker)**:`simulation/performance_tracker.py`(零依賴:total/CAGR/Sharpe/Sortino/Calmar/maxDD/win/payoff + 多維 fitness:風險調整·**regime 穩定度**·回撤控制·命中品質·周轉紀律·niche 純度;週/月/年權重 tilt)+ `simulation/backtest_runner.py`(**LLM-BACKTEST-PROTOCOL 五道防線寫進程式碼**:banned-key 拒收、walk-forward `model_cutoff` 閘、價格史 slice 到 `<= as_of`(回看結構性不可能)、`llm_involvement` marker、~10 action/society-day 截斷不填充)。湖內 PIT 價接線 `data_lake.load_prices`,缺票回空不捏造。
- **C(Debate)**:`programs/debate/DEBATE_PROGRAM.md`(狀態機/JSON 訊息 schema/終止條件,改編 grok.md 但 $hark 治理覆蓋:Verifier=Risk Officer 否決至上)+ `skills/multi_round_debate/SKILL.md` + `simulation/debate_engine.py`(2–4 輪、Proposer/Critic/Verifier/Synthesizer、consensus/veto/no-progress 終止、PIT 守衛、結構化 synthesis + 全 transcript;預設確定性 stub = `llm=none`)。
- **D(Ranking+Reflection+Mutation base)**:`simulation/ranking_system.py`(多時間框排名 + rank delta + bottom-K + niche 覆蓋警示)、`simulation/reflection_engine.py`(最弱 fitness 分量 → 確定性 cause→fix 提案,**避免 LLM 事後敘事汙染**)、`simulation/evolution/mutator.py`(有界可逆突變 + niche 新血注入,**一律 human_gate**)+ `programs/evolution/EVOLUTION_PROGRAM.md`。
- **端到端驗證**:`society_orchestrator.py` 新增 `run_integrated_cycle`(B→D→C compose,synthetic,`llm=none`):backtest→rank→reflect→mutation candidate(human-gated)→debate consensus 全綠;六模組各自 `python simulation/<m>.py` self-test 通過。修一處語意 bug(turnover 以「per-day budget × n_periods」累計比較,否則誤罰)。
- **溶入憲法**:`CLAUDE.md` 新增 **§10 Trading Society**(research 層,繼承 §2 全部 P0,額外綁定:永不繞過 §5 10-signal、human 最終選優、LLM-backtest protocol 強制、~10 action/day 不填充、niche 保護、grade D/E 只進 watch)。governance 變更依 §9 需 human sign-off — 本次由主理人「溶入憲法」明示授權,故記此 log 留痕。
- **wiki ingest**:新頁 `wiki/26_trading_society.md`(編譯總覽 + 角色表 + cycle 圖 + 誠實限制)+ index MOC 補 26 行。
- **誠實限制**:所有數字皆 synthetic self-test;真實驗證待湖內 PIT 價;debate/ranking/reflection/mutation 為確定性骨架,接真 LLM 即翻 `llm_involvement` 觸發 walk-forward 閘;Phase-3 EvolutionEngine(月度全循環 + 多 regime 重測)仍 TODO。AGENTS.md 未動(thin pointer,已指向 CLAUDE 為真源)。新模組獨立、不觸碰既有 1100+ 測試路徑。

## 2026-06-13(c)— feat | 傳奇投資人 persona roster + 高估值強制避險規則(Debate Step 1;Risk Officer 簽核方向)
- 主理人轉達 Risk Officer(Grok)建議:在 AI bubble 類 dot-com、Buffett Indicator ~220-232% 高檔環境下,辯論需同時上場「價值派 + 極端逆向派 + 宏觀 regime 派 + 專業避險派」。自動選擇執行 **Step 1** 全套。
- **5 個結構化 persona**(`simulation/personas.py` 引擎層 + `skills/multi_round_debate/personas/*.md` 5 份 LLM prompt + README):**Buffett**(安全邊際/現金即選擇權)、**Burry**(極端逆向/defined-risk put,禁裸空)、**Dalio**(經濟機器/債務週期/all-weather,「有泡沫不等於立刻賣」)、**Soros**(反身性/擇時參與)、**TailRisk_Hedger**(組合保險/封 MaxDD)。統一 JSON schema(thesis·key_risks·macro_linkage·suggested_hedge·position_sizing·confidence·regime_view·dotcom_parallel·interaction_note)。確定性 stub = `llm=none`;接真 LLM 用 .md prompt 即翻 marker 觸發 walk-forward 閘。
- **高估值強制避險規則**(寫進程式碼 + 憲法):`MarketContext.high_valuation`(Buffett Indicator > 200% 或 Dalio bubble flag)→ (a) `enforce_roster` 強制注入 TailRisk + 至少一 risk-off voice;(b) Verifier(Risk Officer 席)**否決任何缺乏明確 hedge 的加險共識**(veto→consensus=none,不被多數覆蓋);(c) Synthesizer 彙總 `mandated_hedges` + `risk_flags=[high_valuation, hedge_mandatory]`。recommend-only:persona `proposed_actions` 永遠空,只進 transcript。
- **端到端自測**(全綠):高估值 tape(BI 225%, bubble on)→ 4 防禦 vs 1 參與 → **防禦共識:停手新倉 + 攜 5 條 mandated hedge**;lone-bull roster → TailRisk 被強制注回;normal regime → partial、無強制。8 模組 self-test 全綠、wiki lint OK。
- **溶入憲法**:`CLAUDE.md §10` 新增「高估值強制避險條文」+ persona 工件入 canonical 清單。`DEBATE_PROGRAM.md` 新增 §6b(roster + 強制規則 + entry `run_persona_debate`);`multi_round_debate/SKILL.md` 補 personas input;`wiki/26` 補 persona 段。
- **下一步(Risk Officer 路線圖,未做)**:Step 2 `macro_data_provider.py`(US 10Y/2Y/real yield、WALCL/TGA/RRP 流動性 proxy、台美估值 spread,嚴格 PIT)→ 餵 `MarketContext`;Step 3 bubble risk score + dot-com 類比反省模板 + 高估值 regime 給 hedging/niche 更高排名權重。

## 2026-06-13(d)— feat | 演化引擎 + 競賽 + Step 2/3 + 真實 FOM 宇宙競賽(含 SpaceX sleeve)
- 主理人指令:「繼續做(Step 2/3)然後開始演化跟競賽」+「讓交易員在我的 FOM 全宇宙選股看績效排名,一定要納入 SpaceX」。
- **演化substrate**:`simulation/strategy_agent.py`(參數化 genome:lookback/entry_threshold/momentum_tilt/max_actions → 行為隨基因變,突變才有意義);`mutator.py` 加 `mutate_random`(seeded、有界)+ genome bounds。
- **競賽**:`simulation/tournament.py`(bull/bear/chop 多 regime,排名 = 0.5×平均 + 0.5×**最差 regime** fitness,結構性懲罰 curve-fit)。
- **演化引擎**:`simulation/evolution/evolution_engine.py`(世代循環:compete→選 elites→對最差者 reflection-mutate→繁殖 offspring→空 niche 注入新血→演化日誌;多 regime 強制、promotion 一律 human-gate;demo:offspring 把冠軍 0.630→0.683)。
- **Step 2**:`simulation/macro_data_provider.py`(Buffett Indicator/bubble flag/10Y-2Y-real yield/WALCL-TGA-RRP 淨流動性/台美估值 spread → `MarketContext`;synthetic 預設、FRED 選用 never-raise、`is_point_in_time` 誠實標注:synthetic 非 PIT、歷史回放須 ALFRED vintage)。
- **Step 3**:`performance_tracker.bubble_risk_score`(透明 0..1 composite,非學習模型);`ranking_system` 加 `HIGH_VALUATION_WEIGHTS`(高估值 regime 重 drawdown/regime-stability/niche、輕 hit-quality)+ `rank(regime=)`;`reflection_engine` 高估值 regime 對資本保全弱軸附 dot-com 30-50% 回撤壓測模板。
- **真實宇宙競賽(主菜)**:`simulation/universe_competition.py` — 6 trader genome 在 **130 檔 FOM 篩選宇宙 + SpaceX sleeve**、湖內 PIT 價、window 2026-02-04..06-12(90 交易日)、`llm=none`(規則策略 KPI-eligible)。**結果**(`outputs/trading-society-competition-2026-06-13.json`):**MEAN_REVERSION 奪冠 fit 0.717**、REVERSION_FAST 次;3 個 momentum trader 全虧(MOMENTUM_FAST/BREAKOUT/SWING/TREND_RIDER fit ~0.28)。**發現:此窗逢低承接完勝追突破**。冠軍今日訊號(recommend-only):DXYZ/ADBE/BLDP long;SpaceX sleeve:DXYZ/ASTS/RKLB long。
- **誠實警示(重要)**:報酬量級(+1.02 等)**非真實 P&L**(無手續費/滑價/部位 sizing、267 筆、next-bar naive 計分)——只作 trader **相對排名**,不承諾報酬。且冠軍=逢低承接,其 SpaceX 選股(DXYZ/ASTS/RKLB 皆深跌)正是 persona 避險層警告的「高估值接刀」——**社會內部張力本身就是價值**,由 human + Risk Officer 裁決。recommend-only,不取代 canonical 10-signal 與 Risk Officer 閘。
- **SpaceX 處理**:私有公司=monitor-only(不捏造 ticker/價,honors `watchlist/spacex_ipo_2026_event.md`);今日拉入 DXYZ(556)/IRDM(1256)/GSAT(1256)入湖(湖 gitignored);可交易 proxy = DXYZ/RKLB/ASTS/PL/LUNR/STRL/IRDM/GSAT/LMT/NOC/BA。
- 12 模組 self-test 全綠;wiki/26 增「Live result + 演化/競賽 + SpaceX」段;EVOLUTION_PROGRAM status 更新。

## 2026-06-13(e)— feat | Stage 1 歷史競賽:Risk Officer 變交易員 + 週/月/季冠軍 + 2018-2026 領漲領跌正確率
- 主理人指令:「Risk Officer 也變成一個交易員(不是最大的;若持現金/買防禦循環股贏了也能脫穎而出)→ 給我週冠軍月冠軍;用 2018-now 每季領漲領跌(grok.md 標準答案)回測演化調整,看誰正確率高/誰能抓到/誰績效好。這是第一階段。下一階段:預測下一季/下月 portfolio。」
- **答案鍵 ingest**:`simulation/data/quarterly_benchmark_2018_2026.json` — grok.md「2018-2026 逐季領漲領跌矩陣」(34 季、大/小資本多空)結構化落盤;標 **Grade-D**、provenance、**僅 post-hoc 評分用、絕不餵給交易員(無 lookahead)**。私有/泛指名(WeWork/「大量生技」)略去,只留具體 ticker。
- **引擎**:`simulation/historical_competition.py`(numpy 向量化)— 7 交易員含 **RISK_OFFICER(平等競爭:breadth<0 持現金、否則防禦籃 KO/PG/JNJ/LMT/GLD...;無否決特權)**。日線(2021-06→2026-06,587 檔)算週/月冠軍;月線(2018→2026,582 檔)算季冠軍 + 季領漲領跌(湖內實際 top/bottom decile)+ 對答案鍵正確率。`llm=none` KPI-eligible。
- **結果**(`outputs/trading-society-history-2026-06-13.json`):
  - **週冠軍 tally**:REVERSION_FAST 58 / MEAN_REVERSION 56 領先(逢低承接=短週期王);**月冠軍**:MEAN_REVERSION 15;**季冠軍**:MOMENTUM_SWING 9 / TREND_RIDER 6(動能=長週期王)。→ **結構發現:reversion 贏週、momentum 贏季,時間框各有其主。**
  - **正確率(抓到季領漲/避開季領跌/命中答案鍵)**:MOMENTUM_FAST & BREAKOUT_HUNTER catch 0.235 / **answer-key 0.235**(最會抓 NVDA/MSFT/AAPL/TSLA 等傳奇);reversion 幾乎抓不到。
  - **RISK_OFFICER 誠實結論**:週/月/季冠軍 = 1/0/0 **幾乎沒贏**(因其他交易員能放空、在跌勢照樣獲利,純現金/防禦難勝);但 **laggard 迴避 0.989 全場最高**——它幾乎不抱輸家。**防禦的價值在降風險、不在搶冠軍**——現在「看得到」而非假設。
- **演化調整(human-gated)**:引擎對最弱交易員(REVERSION_FAST,答案鍵命中 0)經 `reflection_engine`(高估值 regime → dot-com 壓測模板)診斷 regime_stability 弱 → 提 regime_filter +0.25(PROPOSAL,須多 regime 重測 + human gate)。
- **誠實警示**:報酬量級非真實 P&L(無成本/滑價/sizing);答案鍵 Grade-D 僅評分用;recommend-only,不取代 canonical pipeline。**下一階段(待辦)**:用此排名/正確率預測「下一季/下個月 portfolio」(forward,須嚴格 walk-forward + Risk Officer 閘 + human 選優)。
- wiki/26 增 Stage-1 段;`historical_competition` self-test 綠。

## 2026-06-13(f)— feat | Stage 2 前瞻 portfolio 產生器:全社會加權 + 冠軍加成 + Macro/Capex 動態防禦腿
- 主理人選定(經 AskUserQuestion):**引擎=全社會加權會議(選項2)**、walk-forward 當定期健檢非每次;**風險姿態=強制動態防禦腿**(Macro Risk Score + Capex 一二階 → 動態防禦比例 + Risk Officer 最終審 + 高估值 floor)。
- **`simulation/portfolio_generator.py`**(8 步,principal 流程):(1) 各 trader 由湖內 PIT 價產當下多單 →(2) 近期風險調整 fitness 為基礎權重 →(3) **冠軍加成**(近期前 ~30% ×1.40)→(4) **Macro Risk Environment Score** 0-100(由 buffett_indicator+bubble flag;`bubble_risk_score`)→(5) **Capex Momentum Score** 0-100 →(6) Macro+Capex → **動態防禦腿比例** →(7) Risk Officer 審(高估值 floor ≥35%,CLAUDE §10)→(8) 核心成長腿 + 防禦腿。產 next_month(63d)+ next_quarter(126d)。
- **首次輸出**(`outputs/trading-society-portfolio-2026-06-13.json`,as_of 2026-06-12):Macro risk **97.5/100**(BI 225/bubble)→ posture **risk_off**、防禦 **35%**(高估值 floor 強制)/ 成長 65%。冠軍加成=BREAKOUT_HUNTER+MOMENTUM_SWING/FAST。核心成長腿集中半導體設備+ARM/ROKU(KLAC/ONTO/UCTT/ICHR/FORM/AMKR,各 3-4 trader 背書);防禦腿 cash 17.5% + KO/PG/JNJ/LMT/NOC/RTX。
- **誠實 flag**:**Capex score=proxy**(AI-capex sleeve 3m 價格動能;真實 capex 一二階導數需接 financials,TODO,不捏造);Macro=synthetic 非 PIT(M2/BTC/Gold/CRB/credit-spread 待接);權重來自無成本相對回測;recommend-only,promotion 須 human + Risk Officer 閘 + cross-review。
- **內部一致性觀察**:Capex 動能 100(強)本應降防禦,但 Macro 97.5(極端)+ 高估值 floor 壓過 → 仍 35% 防禦;動態互動如設計。walk-forward 健檢=定期(跑 `historical_competition` 比對冠軍穩定度),非每次;自動排程化 TODO。
- wiki/26 增 Stage-2 段;`portfolio_generator` self-test 綠。**待辦**:真實 capex 一二階(financials)、PIT macro(FRED ALFRED + M2/BTC/Gold/CRB)、walk-forward 自動健檢排程。

## 2026-06-13(g)— feat | Stage 2 數據品質升級(cross-review B/A/C):真實 PIT Macro + 真實 Capex + 集中度上限/成本
- cross-review 裁決 proxy 數據是最大風險,排序 B(真實 PIT Macro)> A(真實 Capex)> C(成本+集中度)。三項全做。
- **B — 真實 PIT Macro**(`simulation/macro_risk.py`):透明 0-100 composite = **live FRED** HY OAS(信用利差)+ 殖利率曲線 + VIX + M2 成長 + 淨流動性 + 估值;逐 series never-raise fallback(標 source);ALFRED `vintage_date` 真 PIT;FRED 逾時降 max_retries=2/timeout=12 快速 fallback。**頭條發現:真實 macro ≈ 31/100(risk_ON)** — HY OAS **2.78%(極緊)**、M2 +4.72%(擴張)、淨流動性增 —— 與舊 synthetic 97.5 相反;**唯估值極端**,故高估值 floor(35%)才是強制避險來源而非 plumbing。證明估值紀律在信用平靜時仍守住。
- **A — 真實 Capex 一二階**(`simulation/capex_provider.py`):polygon 現金流量表 capex → YoY 成長(一階)+ 加速度(二階),**PIT via filing_date**,落 cache;無 cache/POLYGON_API_KEY 時降級 flagged 價格動能 proxy;`--refresh` 拉真實 sleeve(限速 ~13s/檔)。本次無 polygon key → 用 proxy(已標 source=proxy_price_momentum,不偽裝)。
- **C — 集中度上限 + 交易成本**(`portfolio_generator.py`):單一個股 **≤10%**、單一產業 **≤35%**(SECTOR_MAP;ai_semis 原 ~50% → 砍至剛好 35%)、fitness 回測收 **10bps** round-trip 成本(`backtest_trader` 加 cost_bps,預設 0 不動既有測試)、被上限裁掉的權重轉現金(防禦現金 17.5%→~26%)。
- **升級後輸出**(`outputs/trading-society-portfolio-2026-06-13.json`):Macro 31.3(risk_on,2-4 live FRED)、估值 floor 仍 35% 防禦 + 16-17% cap-shortfall 轉現金;成長腿 ROKU 8.2%/ARM/ICHR/KLAC/UCTT/ONTO/AMKR/FORM(ai_semis 鎖 35%、consumer_media 11%);防禦腿 cash ~26% + KO/PG/JNJ/LMT/NOC/RTX。
- **誠實 flag(殘留)**:估值(Buffett Indicator)仍 override 輸入(無乾淨免費 FRED 源);真實 capex 需 polygon key(否則 proxy);FRED live series 數每次浮動(逾時→flagged fallback)。17 模組 import-smoke 全綠。recommend-only。**待辦**:polygon key 後跑 capex --refresh;ALFRED vintage 歷史回放;walk-forward 自動排程。

## 2026-06-13(h)— feat | grok2.md 溶入憲法:真實數據源(Finviz/FRED/Polygon)+ 百年 regime 矩陣 + regime guardrails
- 主理人指令:「試 finviz elite api 或其他數據源可否抓到 + 閱讀消化 grok2.md 嚴重參考大力執行溶入憲法」。grok2.md(3637 行)經 subagent 全文消化:核心新內容 = 百年(1900-2026)regime 矩陣 + governance 級 regime 護欄 + ALFRED vintage 指令,且其 review 段正是回應我 Stage-2 的修正。
- **數據源實測(回答主理人)**:**Finviz Elite ✅**(key 真 36 字元)→ 真實 Industry/Sector/Market Cap/P/E(NVDA→Semiconductors、KLAC→Semiconductor Equipment、LMT→Aerospace & Defense;大型股 median P/E 25.4);**FRED ✅** → macro + **真實 Buffett Indicator = NCBEILQ027S/GDP ≈ 218.5%**(取代 synthetic 225);**Polygon ✅ 價格**但**免費層財報無 capex 科目**(NVDA 0 筆)→ capex 維持 flagged proxy;**Finnhub ❌**(.env 空 placeholder)。
- **新模組**:`simulation/_env.py`(.env 載入,bare 子程序也有 key)、`simulation/finviz_data.py`(真實 industry map + 估值,cache)、`simulation/regime_filter.py`(grok2.md `evaluate_market_regime` + Regime_Filter 硬規則)、`simulation/data/century_regimes.json`(7 期百年矩陣,Grade-D 參考)。
- **真實數據接線**:macro_risk 加 `real_buffett_indicator()`(FRED NCBEILQ027S/GDP);portfolio 集中度上限改吃**真實 Finviz industry**(fallback 硬編 map)→ 實測 sector mix 變真實產業名,「Semiconductor Equipment & Materials」鎖剛好 35%、與「Semiconductors」9% 分開。BI 改真實 218.5、6 live FRED。
- **Regime guardrails(溶入憲法)**:`regime_filter` 三態 self-test 全綠 — **HARD_DEFENSE**(流動性抽 + 金>幣 → 小盤 allocation_cap=0、防禦 floor≥60%、strict winsor)、**PARADIGM_BREAKTHROUGH**(capex>25% + 風險偏好 → **Momentum Decoupling Lock**:封 NVDA/SMCI/AVGO/ASML/TSM/ORCL 反向放空,反 Gamma 擠壓)、**MEAN_REVERSION**(其餘)。接入 portfolio:HARD_DEFENSE 抬防禦 floor;regime verdict 入輸出。今日 live = MEAN_REVERSION。
- **CLAUDE.md §10 溶入**:新增「Regime guardrails(veto-class)」+「3 Ground-Truth invariants(小盤 right-to-zero 截斷、主權/地緣免疫護欄、paradigm-squeeze 短鎖)」+「PIT data discipline(ALFRED vintage + 真實數據源清單 + 集中度紀律 + 估值 floor 覆蓋 risk-on macro)」+ canonical artifacts 補全新模組。governance 變更經主理人「溶入憲法」明示授權。
- **誠實 flag**:capex 仍 proxy(免費 polygon 無科目;需付費層或 finnhub key);century/quarterly 矩陣 Grade-D **僅評分/參考、絕不餵交易員**;btc/gold ratio 用相對強度定義(grok2 原文 raw 價格比不連貫,已誠實改寫並註記)。wiki/26 增 grok2 段。**待辦**:regime→trader 權重表、14-trader roster、capex 接付費源、ALFRED vintage 歷史回放、walk-forward 自動健檢。

## 2026-06-13(i)— feat | regime→trader 動態權重 tilt(grok2.md ②;自動續作)
- 255 退出排查:純 shell pipe artifact(`Select-Object -First` 提前關閉管線 → python broken-pipe → 255),非程式 bug;隔離測試 + no-pipe full run(exit 0)確認:regime line=MEAN_REVERSION、BI 218.5、5 live FRED、Finviz 真實產業(Semiconductor Equipment 鎖 35%)全綠。
- **② regime→trader weight tilt**(`regime_filter.REGIME_TRADER_TILT` + portfolio 套用):依 live regime 重塑全社會投票權重 — **HARD_DEFENSE**:RISK_OFFICER ×2.5(隔離測試:flat 權重下 RISK_OFFICER 升至 **0.41 居首**),momentum/breakout 砍至 0.3-0.4;**PARADIGM_BREAKTHROUGH**:trend/momentum/breakout ×1.3-1.6、MEAN_REVERSION/REVERSION 砍 0.5、RISK_OFFICER 0.6;**MEAN_REVERSION**:faders ×1.3-1.4。**直接解決前述「RISK_OFFICER 從不奪冠」**——危機 regime 下它拿到投票主導權。輸出加 `regime_trader_tilt_applied`。
- 仍 recommend-only、never-raise(regime 失敗則不 tilt)。**③ 14-trader roster(結構性擴編)留待主理人點頭**。

## 2026-06-13(j)— feat | Phase 1 specialist traders:Small Cap Catalyst Hunter + Power & AI Infra(grok2.md 14-trader ③)
- cross-review 核准分批擴編 14-trader roster,Phase 1 = 補兩大缺口(小盤 + AI 電力基建)。建 `simulation/specialist_traders.py`(確定性 0-100 評分卡 + position sizing + 當下選股),`programs/trading_society/TRADER_ROSTER.md`(完整 14-trader 藍圖 + 分批順序 + 多層權重架構)。
- **Small Cap Catalyst Hunter**(gate:真實 Finviz 市值 < $12B;市值/低基期/突破/催化加速 四維):live 選股 **RDW 90.7**(Redwire 太空 $3.6B)、**AI(C3.ai)86.4**、SEDG 80.3、SG、MOV — **補足「不只抓大型股」**,撈出大型動能交易員永遠看不到的真小盤。sizing 5/3/2%。
- **Power & AI Infrastructure Trader**(gate:AI 電力/電網/散熱/先進封裝 sleeve;3m 趨勢/相對強度/持續性):live **KLAC 88.3、UCTT 85.6(+98% 3m)**、NVMI、ICHR、ONTO、CRDO。sizing 6/4/2.5%。
- **整合**:portfolio 把兩 specialist 以 base_weight × regime_tilt 併入全社會投票後重正規化;`_core_growth_leg` 改 iterate weights keys(不再寫死 7 trader);regime_filter 加 specialist tilt(HARD_DEFENSE:SmallCap ×0.2 right-to-zero、AI-Infra ×0.5;PARADIGM_BREAKTHROUGH:×1.6/×1.7)。candidate_names 擴及 specialist 選股(吃真實 Finviz 產業);輸出加 `specialists`。
- recommend-only、never-raise(specialist 失敗不影響主流程)。import-smoke 全綠;specialist self-test live 全綠(159/160 市值解析)。**Phase 2(Value & Quality Compounders、Pelosi Tracker)+ Phase 3(其餘 8)已文件化未建**。**待辦**:cross-style fitness 公平比較、真實 capex(需 key)。

## 2026-06-13(k)— feat | 2018-2026 演化比賽(長線/低頻 ≤3 trades/週)+ 2026 H2 預測選股
- 主理人指令:「2018-2026 回測比賽、交易員每季演化、一週交易 ≤3 次(更長線)、比績效、給 2026 H2 預測選股」。建 `simulation/competition_2018_2026.py`(月線 2018-2026,582 名,7 長線交易員 monthly rebalance、持 ≤3 檔=遠低於 3 trades/週;10bps 成本;每季最弱 2 名演化 genome)。
- **方法論 bug 抓修(誠實)**:首跑出現 **-1.000 / -5.869 破表**——空頭部位可虧 >100% → 權益轉負 → 複利變垃圾(-587% 無意義)。修:(a) `backtest_trader` 加 `long_only`(權益恆 ≥0);(b) 演化 lookback 下限 2(不准退化成高頻 lb1,守長線);(c) 淘汰改看**近 4 季 trailing**(非單季噪音)。
- **修正後累積排行 2018-2026**(相對排名,**非真實 P&L**):LT_BREAKOUT +121×(冠軍,mom lb3)、LT_MOMENTUM +75×、LT_BALANCED +62×、LT_TREND +53×(**奪 9 季最多**)、LT_REVERSION +14×、RISK_OFFICER +0.47×(奪 5 季=2018Q4/2020Q1/2022 跌季,牛市整體墊底)、LT_DEEPVALUE -0.04×(深值逆勢此era 最差)。**動能完勝(前四全動能);防禦的價值在跌季存活非奪冠**。
- **2026 H2 預測**(冠軍 LT_BREAKOUT mom/lb3 套最新月 bar,recommend-only):**KLAC / MXL / ALAB / VSH / VPG / MU / MRVL / CRDO**(半導體/設備/被動元件突破清單)。**live regime=MEAN_REVERSION、高估值 → 35% 防禦 floor 仍綁**(CLAUDE §10)。社會內部張力續存:動能冠軍喊「買半導體」,避險層喊「這些是擁擠 AI 名單、攜 35% 防禦」——human + Risk Officer 裁決,非下單。
- 誠實 flag:報酬量級非可實現 P&L(top-3 集中、無真實 sizing);月線粒度(日線僅到 2021);動能優勢屬 2018-26 AI 牛市 regime-specific。artifact `outputs/trading-society-2018-2026-2026-06-13.json`。

## 2026-06-13(l)— feat | 多空規則(只在確定轉熊放空)+ 擴編 5 交易員(grok2.md roster → 14 voting)
- 主理人指令:「除非大環境真像 2022 或疫情確定轉熊才放空 + 參考 grok2.md 引入更多交易員」。
- **多空規則(溶入憲法 §10)**:**預設 long-biased**;放空**只在確定轉熊 regime**(HARD_DEFENSE = 近 6 月市場中位報酬 < -8%,PIT;2022/COVID analog)。`backtest_trader` 加 `allow_short_mask`(逐月 bear 才准空)+ 空頭單筆虧損封頂 -100%(停損,權益恆定);`regime_filter.shorts_allowed()`(僅 HARD_DEFENSE)。**比賽實證:2018-2026 僅 8 個 bear 月亮燈 = 2018-12、2020-03(COVID)、2022-04→07** —— 正是主理人點名的 2018Q4/疫情/2022。開放 bear 放空後冠軍 LT_BREAKOUT +231×(無早先破表)。
- **擴編 5 交易員**(grok2.md roster;`specialist_traders.py` 重構為統一 scorer(ticker,pts,ctx)):**Value & Quality Compounders**(便宜大型股 P/E + 低回撤;live FDX/TRGP)、**Defense & Geopolitical**(國防/太空 sleeve;IRDM/GSAT)、**Biotech & Healthcare**(LLY/HUM 96/GH)、**Nancy Pelosi Tracker**(Grade-D 公開申報持股 + 動能;PANW/CRWD)、**Elon Musk Ecosystem**(Grade-D;TSLA+SpaceX proxy,今日無票=不硬湊)。各有評分卡 + regime tilt;**全 long-only**。`finviz_data.get_fundamentals`(市值+P/E)餵 ctx。
- **整合**:portfolio 7 specialist + 7 core = **14 voting traders**;portfolio 套真實 Finviz fundamentals;regime tilt 補 5 新(HARD_DEFENSE:Value ×1.5/Defense ×1.3/Biotech ×1.1、Pelosi/Musk 砍;PARADIGM:Musk ×1.5/Pelosi ×1.3)。`TRADER_ROSTER.md` 狀態更新(14 voting;剩 Energy/Consumer/Event-Driven 低優先 TODO)。
- recommend-only、never-raise;specialist self-test live 全綠(170/170 fundamentals);import-smoke 綠。Pelosi/Musk 為 Grade-D curated 參考、非單獨觸發。

## 2026-06-13(m)— feat | 3 層比賽框架:Layer 1 短期配置 + Layer 3 十年潛力評分(主理人框架)
- 主理人提供 3 層框架(L1 短期可執行配置 ★★★★★、L2 中期演化比賽、L3 十年潛力);建議先做 L1。自動執行 **L1 + L3**(L2 即既有 2018-2026 比賽),文件化 `programs/trading_society/COMPETITION_FRAMEWORK.md`。
- **Layer 1**(`simulation/layer1_allocation.py`):把 14-trader 投票轉成「下季配置建議」—— **核心(大型股 80%)+ 衛星(小盤高 Beta 20%,Small Cap Hunter)+ 動態防禦腿**;**新增/繼續持有/減持**(對比上次 artifact diff,首跑=baseline 全新增);上限 核心 ≤12%、衛星 ≤6%、產業 ≤35%、§10 高估值 floor。**首跑 2026 Q3**(MEAN_REVERSION、BI 218.5%、防禦 35%):核心 ROKU/AMKR/ARM/FORM + semicap(52%)、衛星 RDW/AI/SEDG/SG(13%)、防禦 現金 19.5% + KO/PG/JNJ/LMT/NOC/RTX。中文 readout 寫 UTF-8 `.md`(cp950 console 不亂碼)。
- **Layer 3**(`simulation/layer3_potential.py`):0-100 七維潛力評分(產業趨勢 25% · **護城河 20% 真實=`fom.IP_DEFENSIBILITY`** · 資本配置 15% proxy · FCF 15% proxy · **估值 10% 真實 Finviz P/E** · 經營層 10% proxy · 地緣 5% curated)→ Top 30。**今日 Top 10:MSFT 71.8、NOC、NVDA、TSM、ASML、LMT、QCOM、GOOGL、RTX、CRM**(大型科技 + 國防 + 半導體);分 `core_long_term` / `high_growth_high_risk` 兩桶。**誠實:7 維中 3 維(資本配置/FCF/經營)為中性 proxy,待真實財報接線**。
- **編碼修正**:cp950 box 上 print 中文會亂碼 → L1 中文 readout 改寫 UTF-8 `.md`、console 只印 ASCII 摘要;L3 console driver/risk 改 ASCII(中文框架在 chat 呈現)。
- recommend-only、never-raise;import-smoke 綠。**L2 優化待辦**:每季 reset、風險調整 fitness、cross-style 公平比較。

## 2026-06-13(n)— feat | Layer 2 嚴謹化:分散持股(≤10檔 80/20 上限)+ cross-style 公平 fitness(review A+B)
- cross-review 評比賽可信度=中(方向可信、量級不可信),首要修「單股暴漲帶飛」+「跨風格不公平」。兩項全做。
- **A 分散持股**(`_diversified_quarter_return`):每月持 **≤10 檔**、**80% 大型 / 20% 小型**、單股上限 **12%/6%**、long-only。取代舊 top-3 集中。`LARGE_CAP` curated 穩定大型股集(歷史市值不在湖,curated 近似)。**效果:冠軍累積 +231× → +18.5×**(LT_BALANCED)—— 通膨式數字砍掉 ~12 倍,單股暴漲帶飛消失。
- **B 跨風格公平 fitness**(`_fair_fitness`):第二張排行榜按 風險調整 + regime-aware composite(40% 季 Sharpe + 30% 正規化累積 + 30% 回撤控制)排序,並報各 trader 牛季/熊季平均報酬 + 命中率。**Fair 冠軍 = LT_BALANCED**(Sharpe 1.50、命中 77%、maxDD -16%、**熊季近持平 -0.1%**)——與 raw 冠軍一致 = 其勝出是風險調整後的真本事、非單股運氣。**發現:LT_TREND 是唯一熊季正報酬(+2.8%);RISK_OFFICER 回撤控制最佳(-12.2%)但牛市墊底**。
- **2026 H2 預測**改由更穩健的 LT_BALANCED(mom/lb4)產出;regime=MEAN_REVERSION、§10 防禦 floor 35% 仍綁。`COMPETITION_FRAMEWORK.md` L2 段更新(優化完成);輸出加 `fair_leaderboard_risk_adjusted` + `fair_champion`。
- recommend-only、long-biased(分散書 long-only;放空仍鎖 HARD_DEFENSE 簡單路徑);import-smoke 綠。**待辦**:真實 Capex/FCF/ROIC 提升選股品質、多 regime out-of-sample 驗證。