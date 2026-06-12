---
type: synthesis
tags: [alpha-library, case-studies, historical, training, macro-arc]
title: Alpha Library — Historical Cases for Calibration
as_of_timestamp: 2026-05-29T00:00:00-04:00
author_role: compiler
source_paths:
  - raw/macro/principal-narrative-2026-05-29.md
status: live
schema_version: 1
---

# Alpha Library

Per Karpathy's [[../philosophy/references/karpathy-llm-wiki]] "Tips and Tricks" — this library compounds: each historical case the system files makes future judgments better.

## §A. The 2020-2026 macro arc (principal-narrated)

Filed from principal narrative ingest on 2026-05-29. This case provides the **regime framework** all subsequent narrower cases hang off.

### A.1. Phase 1 — Covid emergency rally (2020 Q1 → 2021 Q4)

- **Trigger**: March 2020 Covid circuit-breaker + Fed zero-rate emergency response
- **Leadership**: TSLA, the canonical 2021 representative stock
- **Driving thesis**: zero-rate + digital acceleration + EV / robotics narrative; TSLA's robot-driven production was less Covid-disrupted than peers
- **Outcome**: 2-year rally; Musk briefly the world's wealthiest individual
- **Calibration use**: zero-rate-driven, narrative-led rallies are **fragile to rate-cycle reversal** (confirmed in A.2 below). Such rallies are 多頭真漲 only while the rate environment is supportive; the Compiler must re-classify on rate-cycle inflection.

### A.2. Phase 2 — Aggressive tightening drawdown (2022 full year)

- **Trigger**: CPI hitting low-teens %; Powell-led aggressive Fed hikes
- **Severity**: tech stocks broadly drew down 50-75% (per principal: "打了九折,打了二五折" ≈ down 50-75%)
- **Duration**: ~12 months (Jan to Dec 2022)
- **Bottom timing**: late 2022 (December)
- **Calibration use**: this is the canonical **Last Snow** ([[../philosophy/concepts/last-snow]]) and **cycle-resonance** ([[../philosophy/concepts/cycle-resonance]]) co-occurrence instance. Macro headlines remained bearish (CPI prints, Fed hawkish forward guidance) but the structural bottom printed in October/November 2022. The 6-month-correction / 2-month-advance pattern compressed to ~10-2 here because of the depth.

### A.3. Phase 3 — AI revolution narrative emerges (2022 Q4 → 2024 Q4)

- **Trigger**: late 2022 narrative pivot toward generative AI capability; NVDA as the named leadership
- **Co-leadership**: Mag 7 names with AI-cloud capex (MSFT, GOOGL, META, AMZN) participated; META's "Year of Efficiency" mass layoff cycle compounded the earnings-margin-expansion thesis
- **Magnitude**: NVDA up ~10×+ over the cycle (principal: "漲了十幾倍" — 10-20× range)
- **Co-asset**: BTC ran from ~$10K to ~$60K through this window
- **Calibration use**: this is the canonical **narrative-led structural bull** — fundamentals confirmed the narrative through earnings (CoWoS-bottlenecked NVDA shipments, hyperscale capex acceleration). 多頭真漲 throughout per [[../philosophy/03-long-short-taxonomy]]. Several TD-9 sell signals on NVDA during this window (e.g. Jul 2023) were correctly overridden by the volume-validation guard per [[../philosophy/concepts/td-9-sequential]].

### A.4. Phase 4 — Trump-election BTC extension (2024 Q3 → 2024 Q4)

- **Trigger**: Trump election + pro-crypto policy posture
- **Magnitude**: BTC $60K → $120K (2× in single cycle)
- **Calibration use**: policy-narrative-driven asset rerating is a 1-2 quarter window phenomenon. The system should treat policy-bump rallies as **Strategy B momentum** with strict TD-9 + volume-validation exits — they decay fast when the policy-cycle attention shifts.

### A.5. Phase 5 — Trump tariff drawdown (2024 Dec → 2025 April)

- **Trigger**: December 2024 tariff announcements
- **Duration**: ~4 months
- **Recovery trigger**: Trump pivot to negotiation, tariff de-escalation announcements
- **Calibration use**: this is the first **cycle-resonance instance under the new Trump-policy-dominated regime**. Duration (4 months) is shorter than the canonical ~6 months. The detector in [[../philosophy/concepts/cycle-resonance]] should consider whether policy-driven drawdowns systematically run shorter than rate-driven ones (open research question for Phase 4 backtest study).

### A.6. Phase 6 — AI rally resumption + supply chain breadth (2025 May → present)

- **Trigger**: tariff de-escalation removes the macro overhang; AI capex cycle continues
- **NVDA trajectory**: pulled to ~$190, advanced to ~$220, now range-bound $180-$220
- **NVDA market cap**: ~$5T, world's largest by market cap
- **Supply chain extension**: rally broadens beyond pure GPU to:
  - Optical communications (CIEN, ANET, COHR, LITE, FN — Phase 2 vetting required)
  - CPU + Agent AI (AMD, Intel both participating — Agent AI workloads drive CPU demand independent of GPU)
  - Mag 7 AI-cloud partners (AMZN, MSFT, GOOGL, META all participating)
- **Calibration use**: when the leadership name (NVDA here) reaches market-cap saturation ($5T) and enters consolidation, the **second-derivative trade is in supply-chain breadth**. This is the canonical [[../philosophy/concepts/supply-chain-bottleneck]] alpha extraction window.

### A.7. Phase 7 — Fed regime transition (2026 May)

- **Trigger**: Kevin Warsh succeeds Powell as Fed Chair
- **Policy posture**: stated market non-intervention
- **Implication**: collapses the historical three-factor (Fed + AI + Trump) macro model toward **two-factor (AI + Trump)** with Fed as low-variance background
- **Calibration use**: Phase 4 backtest must re-evaluate whether the Fed-day exclusion rule in [[../philosophy/06-exclusions]] (no new entries on FOMC days) should attenuate under a non-interventionist Fed. Recommended: keep the rule as a conservative default for 4 FOMC cycles, then evaluate Fed-day realised vol; if it drops materially below historical, relax the rule.

## §B. Cycle-resonance instances (cumulative)

Per [[../philosophy/concepts/cycle-resonance]]:

| Instance date | Drawdown duration | Drawdown depth | Forward 2-month return | Notes |
|---|---|---|---|---|
| 2020 March | ~3 months | -34% (SPX) | +24% | Fed-intervention compressed cycle |
| 2022 October | ~10 months | -25% (SPX) | +14% | Last Snow co-occurrence (§A.2) |
| 2023 January | ~12 months | -25% (peak-to-trough; ratification leg) | +10% | Cleanest example per [[../philosophy/concepts/cycle-resonance]] |
| 2024 August | ~3 weeks | -10% (NDX) | +15% | Yen carry unwind; abbreviated |
| 2025 April | ~4 months | -15% (NDX) (estimate; Phase 2 verify) | +20%+ (cumulative through 2026 May) | First Trump-policy-driven instance (§A.5) |

## §C. Last Snow co-occurrences (cumulative)

Per [[../philosophy/concepts/last-snow]]:

- 2009 March (Great Financial Crisis bottom) — historical reference, before this system existed
- 2020 March (Covid bottom)
- 2022 October (FOMC-rate-hike peak; SPX low printed within 2 weeks of peak recession-talk)
- 2023 January (recession-talk peak; SPX rallied 25% over next 7 months)
- **(future instances tracked prospectively)**

## §D. TD-9 calibration cases

Per [[../philosophy/concepts/td-9-sequential]]:

- **True top exemplars (sell / short with volume contraction)**:
  - AAPL Jan 2022 (Last Snow co-occurrence pre-cursor)
  - TSLA Nov 2021 (zero-rate cycle exhaustion)
  - SOXL Mar 2024 (semis chasing TD-13 extension)
- **Trend-continuation overrides (ignore TD-9 sell, keep holding)**:
  - NVDA Jul 2023 (per principal narrative §A.3 — the volume validation guard prevented false exit during the canonical AI rally)
  - MSFT 2024 H1 (Copilot ARPU expansion thesis)
  - NVDA multiple instances 2024 H2 - 2025 (during the 5T market-cap run)

## §E. Sentiment-virtual-bull (多頭虛漲) cases

- GME 2021 — the canonical short-squeeze deterrent ([[../philosophy/03-long-short-taxonomy]] iron rule motivation)
- AMC 2021
- BBBY 2022
- Selected biotech runs 2023-2024 (Phase 2 specific case research)

## §F. Supply-chain bottleneck plays

Per [[../philosophy/concepts/supply-chain-bottleneck]]:

- **2023 H2**: NVDA vs. SK Hynix (HBM bottleneck) — Hynix outperformed on a relative-volatility basis
- **2024 H1**: NVDA vs. AVGO (custom ASIC for hyperscalers) — AVGO captured the breadth
- **2024 H2**: TSMC capacity announcements driving sector
- **2025 May - present (§A.6)**: optical communications + CPU + Mag 7 cloud partners as the second-derivative trade while NVDA consolidates 180-220

## §G. Failed-thesis postmortems

Phase 1 status: no failed-thesis postmortems yet (no live trading). The first entries arrive when Phase 3 closes its first trades.

## §H. Serenity 3-phase supply-chain rotation framework (empirically verified)

Filed from `raw/kol_signals/serenity-aleabitoreddit-profile-2026-05-29.md` + empirical verification in `outputs/narrative-validation-2026-05-29.json`.

### Framework

Per X-account `@aleabitoreddit` (Serenity), the 2024-2026 AI supply-chain alpha rotated through three discrete phases:

| Phase | Theme | Empirical evidence (our backtest) |
|---|---|---|
| **Phase 1** | HBM / Memory | MU +895%, WDC +963%, STX +668% trailing 12m as of 2026-05 (most ran 2025 specifically; 2024 was flat) |
| **Phase 2** | Optical transceivers | LITE +1140%, AAOI +1016%, CIEN +619%, COHR +408% trailing 12m; **all at 52w high** as of 2026-05 |
| **Phase 3** | Silicon Photonics + external light sources | AXTI +7771% trailing 12m (extreme); AEHR +961%; ALAB / CRDO / POET all triple-digit; **all at 52w high** as of 2026-05 |

### Calibration significance for the system

1. **Phase 1 Memory pattern** is the canonical Strategy A consolidation-breakout case at the sector level. The 2024-flat-then-2025-explode profile (MU went from -2% YTD 2024 to +214% YTD 2025) is reproducible by sector-dispersion + upstream-demand-confirmation logic. Phase 3 implementation will codify this as the **catch-up rule**:
   > "When SOX YTD > 20% but sub-sector X is flat AND upstream Mag 7 capex guides up by [N], add sub-sector X names to candidate pool."

2. **Phase 2 Optical pattern** validates the [[concepts/supply-chain-bottleneck]] framework — as AI cluster scale moved from "10k GPU" to "100k+ GPU" through 2024-2025, the binding constraint shifted from compute to interconnect.

3. **Phase 3 Light Sources** is the upstream-of-the-upstream play: the SiPh transceivers (Phase 2) themselves depend on indium phosphide (InP) laser diodes from AXTI and adjacent compound semis. This is **three levels of supply-chain depth** from the end-buyer (NVDA → GPU → Optical interconnect → InP laser source).

### NVDA saturation observation (most important regime finding)

The Phase 1 → Phase 2 → Phase 3 rotation **completely bypassed NVDA**. NVDA returned only **+57% trailing 12m vs SOX +171%** during P6 (2025-05 to 2026-05). NVDA ranked #26 of the 36-ticker universe.

**This is the [[../philosophy/concepts/supply-chain-bottleneck]] "leadership saturation → second-derivative trade" scenario in pure form**. The system MUST update its tier-1 default sizing to account for this:

- When tier-1 leadership (NVDA, etc.) saturates by market cap or P/E expansion, the standard 8% tier-1 cap is too high. Recommended: dynamic cap = `8% × (1 - tier1_leader_saturation_score)`.
- The saturation score is a function of: market cap rank, P/E percentile, capex-share-of-cycle, and price-to-supply-chain-revenue gap.
- Phase 3 implementation in `src/sharks/risk/saturation.py`.

### Hypothetical Phase 4 (not yet named by Serenity)

Compiler hypothesis based on supply-chain logic:

| Candidate Phase 4 theme | Rationale | Watch tickers |
|---|---|---|
| **Data center power + cooling** | AI cluster power density is the next binding constraint as cluster size scales | VRT (Vertiv), ETN (Eaton), GEV (GE Vernova) |
| **Advanced packaging equipment** | CoWoS expansion creates equipment-vendor demand pull | ASMI (ASM International), KLAC, AMAT (already in universe) |
| **European AI chipmakers** | Serenity's recent XFAB call + EU Chips Act 2.0 thesis | XFAB (German listing), STM (STMicroelectronics), IFX (Infineon) |
| **PCB / advanced substrates** | Next-gen packaging substrates gating fab output | Most candidates non-US-listed; ADR coverage limited |

Researcher action items in [[05_recommendations/2026-05-29-narrative-validation#5]].

### Discipline reminder

Per [[../CLAUDE]] source grading: Serenity is grade-C source. His individual posts are grade D. The framework above is **informational**, not authoritative. Independent verification by upstream-demand-confirmation logic is required before any position open.

## §I. Memory cycle 2024-2025 — the "縮量也不下跌" exemplar

This case anchors the [[../philosophy/concepts/price-volume-divergence]] bullish divergence detection.

Pattern recap:
- **2024 full year**: MU flat at -2% YTD. SOX up moderately. Volume in MU was contracting through Q2-Q3 2024.
- **2024 Q4 - 2025 Q1**: capex commentary from Mag 7 hyperscalers explicitly named HBM allocation as binding. SK Hynix raised guidance; Micron's forward orders book filled.
- **2025 H1 - 2025 H2**: MU broke out on volume; rally extended throughout 2025; ended +214% YTD.
- **The entry signal that worked**: a Strategy A breakout on the first month MU exceeded its prior consolidation high on volume > 1.5× 20m avg. Entry zone roughly Q1 2025.

**Filed for [[concepts/price-volume-divergence]] case-study expansion**: a textbook bullish-divergence + Strategy A breakout, with the catalyst (Mag 7 capex guidance) externally observable months ahead of the spot move. Calibrates the "縮量也不下跌" sharks principle 5 to the memory sub-sector.

## Compiler maintenance notes

- This page is updated on every major narrative ingest, every cycle-resonance trigger, and every closed-position postmortem
- §A is the **regime-level** library — when it changes, propagate to `wiki/01_macro_state.md`
- §B-§F are **calibration libraries** — used by Phase 4 backtest to validate detector outputs against historical instances
- §G is the **mistake library** — most expensive content per byte; treated with the highest discipline
