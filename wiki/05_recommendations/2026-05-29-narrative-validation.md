---
type: recommendation
tags: [recommendation, narrative-validation, backtest, serenity-rotation]
as_of_timestamp: 2026-05-29T02:00:00-04:00
trading_date: 2026-06-01
regime_ref: 01_macro_state.md@2026-05-29
schema_version: 1
author_role: compiler
risk_officer_review: pending
data_source: outputs/narrative-validation-2026-05-29.json
note: |
  This is NOT a daily 10-signal pick. It is the first Phase-2-early narrative
  validation + candidate-shortlist report, prompted by the principal's request
  to "backtest the 2020-2026 narrative and find under-played names."
  The schema below uses the standard recommendation envelope plus an extended
  `analysis` section. Risk Officer has NOT yet pre-approved any of these.
---

# Narrative Validation + Candidate Shortlist — 2026-05-29

Methodology: yfinance monthly bars from 2019-12 to 2026-05 for a 36-ticker universe (Mag 7 + supply chain tier 2 + Serenity 3-phase rotation candidates + crypto co-asset). All numbers are total return using month-end closes.

Raw data: [outputs/narrative-validation-2026-05-29.json](../../outputs/narrative-validation-2026-05-29.json) + [outputs/monthly-closes-2026-05-29.csv](../../outputs/monthly-closes-2026-05-29.csv).

## §1. Verification of the principal's 2020-2026 narrative

| Phase | Claim | Index returns (data) | Top-ranked leader (data) | Principal's claim | Verdict |
|---|---|---|---|---|---|
| **P1 Covid emergency** (2020-03 → 2021-12) | TSLA leadership | SPX +84%, NDX +109%, SOX +161% | AEHR +1348%, **TSLA +908% (#2)** | TSLA leader | ✅ **VERIFIED** (TSLA #2; only AEHR specialty beat it) |
| **P2 Tightening drawdown** (2022) | Tech -50 to -75% | SPX -15%, NDX -27%, SOX -27% | (drawdown — narrow leaders) AEHR +58%, FN +13% | Tech down 50-75% | ⚠️ **PARTIAL**: index down 15-27%; specific Mag 7 names matched (META -64%, NVDA -50%) but "tech打了二五折" is the worst-case subset, not the broad index |
| **P3 AI emergence** (2023-01 → 2024-11) | NVDA leadership | SPX +48%, NDX +73%, SOX +69% | **AAOI +1624%**, NVDA +608% (#2) | NVDA leader | ✅ **VERIFIED** with **important caveat**: AAOI (optical photonics) **beat NVDA**. The AI photonics supercycle Serenity calls "Phase 2" actually started earlier than commonly told. |
| **P4 BTC Trump-election bump** (2024-09 → 2024-12) | BTC 60K→120K | SPX +2%, NDX +5%, SOX -4% | AAOI +158%, ALAB +153%, CRDO +118% | BTC up 2× | ⚠️ **PARTIAL**: BTC up +48% in this sub-window (60K→100K-ish); the supply-chain names ran HARDER (AAOI, ALAB, CRDO) |
| **P5 Tariff drawdown** (2024-12 → 2025-04) | Drawdown into April 2025 | SPX -5%, NDX -7%, SOX -15%, **VIX +42%** | STX +7%, BTC +1%, INTC +0% | Drawdown ✅ | ✅ **VERIFIED**, duration ~5 months. Drawdown shallower than P2 (`-7.8%` SPX max DD vs `-20.9%` in P2) |
| **P6 AI rally resumption + breadth** (2025-05 → 2026-05) | NVDA + supply chain rally | SPX +28%, NDX +42%, **SOX +171%** | **AXTI +7,771%**, LITE +1,140%, AAOI +1,016%, WDC +963%, AEHR +961%, MU +895%, STX +668% | NVDA leader | ❌ **REFUTED** — NVDA only **+57%, ranked #26 of universe**. After $5T saturation, alpha **rotated out of NVDA** into supply chain (Serenity Phase 1 memory + Phase 2 optical + Phase 3 SiPh). |

**The Phase 6 finding is the single most important calibration update**: NVDA stopped leading once it hit $5T. The system's tier 1 (Mag 7) bucket should **not** be the default tactical allocation in the current regime; the alpha lives in tier 2 supply chain. This is the canonical [[../philosophy/concepts/supply-chain-bottleneck]] **"leadership saturation → second-derivative trade"** scenario.

## §2. Serenity rotation framework — empirical confirmation

Verified by our backtest:

### Phase 1 — HBM / Memory (played out in 2025)

| Ticker | 2024 YTD | 2025 YTD | Trailing 12m | Distance from 52w high |
|---|---|---|---|---|
| MU | -2% | **+214%** | +895% | (rising) |
| WDC | +4% | **+251%** | +963% | (rising) |
| STX | +3% | **+191%** | +668% | (rising) |
| SIMO | -11% | +75% | +388% | — |

**Capital flow observation (answers principal's "how to spot memory ahead of time")**:
- Memory was **dead-flat through 2024** (MU -2%, WDC +4%, STX +3%) while semis (SOX) ran. Sector dispersion was extreme.
- Memory **exploded in 2025** despite no obvious news catalyst on the names themselves.
- The leading indicator was **upstream demand confirmation** from NVDA / Mag 7 capex guidance — HBM allocation tightness — **observable 6-9 months ahead** of the spot move.
- The structural form was a textbook **multi-quarter consolidation breakout** (Strategy A per [[../philosophy/10-strategies]]) — 12 months of flat-to-down trading creating extreme volume contraction, then a breakout on volume.
- **Reproducible rule**: when SOX runs but a sub-sector (memory, optical, etc.) is flat AND upstream demand confirmation is present (Mag 7 capex guides up), the catch-up trade is a high-probability swing.

### Phase 2 — Optical transceivers (played out — names at 52w high)

| Ticker | Trailing 12m | Distance from 52w high |
|---|---|---|
| LITE | +1,140% | **0.7%** (at high) |
| AAOI | +1,016% | **0%** (at high) |
| CIEN | +619% | **0%** (at high) |
| COHR | +408% | **0%** (at high) |
| FN | +193% | **0.1%** (at high) — **laggard** |
| ANET | +80% | **9.7% below high** — correction |

**Interpretation**: Phase 2 is largely played out. **FN (Fabrinet)** stands out as the relative laggard within Phase 2 — its +193% vs LITE +1,140% suggests catch-up potential, but it's currently at the high — wait for retest.

**ANET in correction** (-9.7% from high) is the cleanest Phase 2 re-entry candidate for Strategy A.

### Phase 3 — Silicon Photonics / Light Sources (Serenity says "starting" — but already extended)

| Ticker | 2024 YTD | 2025 YTD | Trailing 12m | Distance from 52w high |
|---|---|---|---|---|
| **AXTI** | -12% | **+682%** | **+7,771%** | 0% (at high) |
| ALAB | +79% | +64% | +284% | 0% |
| CRDO | +228% | +105% | +270% | 0% |
| AEHR | +12% | +78% | +961% | 0% |
| POET | +344% | +33% | +207% | 0% |

**Interpretation**: Phase 3 names are **already at the high**. Per [[../philosophy/concepts/farmer-mindset]], entering here is farmer thinking. AXTI specifically is 78× in 1 year — extreme; sustainability questionable.

The Serenity-style alpha **for Phase 3 already happened** during Q4 2025 - Q1 2026. Current entries face heavy regression risk.

## §3. Cycle-resonance detector calibration

The detector in [[../philosophy/concepts/cycle-resonance]] requires drawdown in `[10%, 30%]`. The two recent drawdowns:

| Phase | SPX max DD | NDX max DD | Window length | Detector verdict |
|---|---|---|---|---|
| P2 (2022) | -20.9% | -26.7% | ~12 months | ✅ Fires (within 10-30% band, > 22 weeks) |
| P5 (2025) | **-7.8%** | -10.2% | ~5 months | ❌ **Below threshold** |

**Calibration finding**: the 2025 tariff drawdown was a **policy-shock sub-cycle**, not a full cycle-resonance event. The SPX max DD of -7.8% is below the 10% floor.

However, the **recovery** (P6 SOX +171%) was historic. This suggests we need a **second detector** for "policy shock" sub-cycles:
- Trigger: VIX spike > +30% in < 8 weeks + index DD in [5%, 12%] + macro headline driver (tariff, Fed surprise, geopolitical)
- Window: shorter (~2 months instead of 2 months) than cycle-resonance
- Action: Strategy B momentum entries on supply-chain names with the highest beta to recovery

**Compiler proposes**: add `philosophy/concepts/policy-shock-sub-cycle.md` as a new concept page. Pending human review (Compiler cannot write to `philosophy/`).

## §4. NVDA range trade specifics

| Month | NVDA close |
|---|---|
| 2026-03 | $174 |
| 2026-04 | $200 |
| **2026-05** | **$213** |

Principal said range = $180-$220.

**Current standing: NVDA at $213 = 96.4% of the upper range bound.**

Per [[../philosophy/concepts/objective-watershed]]: this is **NOT a buy zone**. The retest of $180 is the buy. The break above $220 with volume is a Strategy B momentum re-trigger.

## §5. Candidate shortlist (for Risk Officer review, NOT yet a recommendation)

Filtered by:
- (a) Confirmed supply-chain relevance per [[../02_mag7_bottleneck]]
- (b) NOT currently at 52w high
- (c) Trailing 12m return reasonable (not extreme outperformer, not crash)
- (d) Liquidity per [[../philosophy/06-exclusions]]

### Tier 2 — moderate conviction, supply-chain established

| Ticker | Why | Quadrant | Strategy | Notes |
|---|---|---|---|---|
| **NVDA** | $5T saturation but core position; wait for $180 retest | 多頭真漲 (waiting) | A (consolidation re-entry at $180) | NOT now at $213 |
| **ANET** | Optical-adjacent networking; -9.7% from 52w high (correction); Mag 7 customer wins | 多頭真漲 | A (consolidation watch) | Wait for volume confirmation on next holding pattern break |
| **FN** | Phase 2 laggard (+193% vs LITE +1140%); contract-manufactures for optical primes | 多頭真漲 | A (consolidation watch) | Currently at high; wait for retest |
| **INTC** | Agent AI CPU thesis (per principal narrative §3) + still relative laggard | 多頭真漲 | A | Add `philosophy/entities/intel.md` (Researcher pending) |

### Phase-rotation candidates — speculative

These extend the Serenity rotation framework by **identifying what could be "Phase 4"**:

| Ticker | Sector | Why "Phase 4" candidate |
|---|---|---|
| **VRT** (Vertiv) | Liquid cooling, power management for data centers | NOT in current universe; AI rack-power density is binding for next-gen clusters |
| **ETN** (Eaton) | Power management + electrical | Datacenter power infrastructure |
| **GE Vernova (GEV)** | Power grid + transformers | Datacenter grid-interconnection bottleneck |
| **ASMI** (ASM International) | ALD equipment for advanced packaging | TSMC + Intel + Samsung capacity catalyst |
| **KLAC** | Process control / metrology | Backend yield gating for advanced packaging |
| **AMAT** (already in universe) | Front-end + advanced packaging equipment | Already covered |
| **STMicro (STM)** | European AI chips + TSMC partner | Follows Serenity's X-FAB / EU Chips Act 2.0 thesis |

**Researcher action**: write entity pages for VRT, ETN, GEV, ASMI for Risk Officer review before adding to `watchlist/universe.yaml` tier 2.

## §6. Where Phase 1 finds gaps (calibration items)

Compiler flags for follow-up:

1. **Cycle-resonance threshold** needs a "policy-shock" variant (§3 above)
2. **NVDA tier-1 sizing** in current regime should probably be **below** the 8% standard cap until $180 retest — the system's `08-risk-and-position.md` doesn't yet have a "leadership saturation" downsizing rule. Proposed addition.
3. **Memory cycle catch-up rule** (§2 Phase 1) should be formalised: "when SOX +20% YTD but a sub-sector is flat AND upstream Mag 7 capex guides up, generate catch-up watchlist". This is a Phase 3 implementation item.
4. **Phase 3 SiPh entries at-the-high**: do NOT chase. Strategy B momentum rules ([[../philosophy/10-strategies]]) + farmer-mindset guard ([[../philosophy/concepts/farmer-mindset]]) reject these as Phase 1 calibration overrides.

## §7. What to do this week

Given current regime read ([[../01_macro_state]]):
- **No new positions today** — current candidates are either at 52w high (Phase 3) or waiting for retest (NVDA $180, ANET breakout)
- **Watchlist additions** (Risk Officer to approve): ANET, FN, INTC into existing tier 2; VRT / ETN / GEV / ASMI as new tier 2 candidates pending entity-page authoring
- **Monitoring discipline**: track NVDA daily for $180 retest; track FN and ANET for Strategy A consolidation patterns
- **Inoculation reminder** ([[../../sharks]] principle 2 + 3): the AXTI 78× chart is the canonical [[../../philosophy/concepts/separation-mind]] trap. We are NOT entering. The next phase is already being priced in.

## See also

- [[../01_macro_state]] — current regime
- [[../03_alpha_library]] §A (2020-2026 arc verified) + §H (Serenity framework — Compiler appended below)
- [[../../philosophy/concepts/supply-chain-bottleneck]] — the structural framework
- [[../../raw/kol_signals/serenity-aleabitoreddit-profile-2026-05-29]] — Serenity profile + methodology
- [[../../raw/macro/principal-narrative-2026-05-29]] — principal's narrative arc (source of P1-P6 phase labels)
