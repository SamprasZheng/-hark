---
type: recommendation
tags: [recommendation, fom-monthly, multi-dimensional, contrarian-momentum-cyclic]
as_of_timestamp: 2026-05-29T05:00:00-04:00
trading_date: 2026-06-01
regime_ref: 01_macro_state.md@2026-05-29
schema_version: 1
author_role: compiler
risk_officer_review: pending
data_source: outputs/fom-monthly-2026-05-29.json
cadence: monthly
note: |
  First FOM (Figure of Merit) multi-dimensional scoring output.
  Universe: 59 tickers including Mag 7, AI supply chain (Phase 1/2/3),
  contrarian software (CRM/NOW/NFLX), bubble watchlist (ORCL/OKLO/SMCI),
  datacenter infra (VRT/ETN/GEV), defense (LMT/RTX/NOC), beta anchors
  (JNJ/PG/KO/WMT), R2K alpha picks (RKLB/ACHR/CRSP).
  Russell 2000 broad exposure via IWM (rank check only).
---

# Monthly FOM Top-3 Picks + Top-50 Watchlist — 2026-05-29

## §1. Three high-conviction picks for June 2026

### #1 — META (Final FOM 59.4)
- **Thesis**: 多頭真漲, contrarian sweet spot. Per [[../../sharks]] principle + principal's call ("CRM/NOW/MSFT/META/NFLX 全部都錯殺").
- **Why now**: momentum 19.5 (corrected from highs), **contrarian 85**, IP defensibility **85**, bubble_guard **+45** (healthy).
- **Catalyst path**: Reality Labs spending discipline + AI ad targeting + Llama enterprise monetisation
- **Bucket**: 6m core (tier 1)
- **Size**: 7-8% (within tier-1 cap from [[../../philosophy/08-risk-and-position]])
- **Entry**: market at open; consider scale-in on weekly close
- **Stop**: thesis-invalidating earnings miss + 18% drop from entry
- **Falsification**: ad revenue YoY < +8% for 2 consecutive Qs; Reality Labs operating loss > $20B annualised

### #2 — LMT (Final FOM 58.2)
- **Thesis**: defense + Trump-policy hedge + Y2-midterm anti-Trump tailwind (deficit spend on defense remains bipartisan); ITA seasonal Nov peak ahead.
- **Why now**: contrarian **87**, IP **90**, bubble_guard **+65** (cleanest of universe), quality 47
- **Catalyst path**: Q4 budget cycle + November ITA seasonal (+3.2%, 75% positive); Iran/geopolitical risk premium
- **Bucket**: 6m-12m core (tier 2)
- **Size**: 5%
- **Entry**: market at open; add on >5% pullback
- **Stop**: -12% from entry or thesis invalidation by major Pentagon contract loss
- **Falsification**: defense budget cut > 5% in any FY2026 CR

### #3 — ORCL (Final FOM 57.2) **WITH PRINCIPAL OVERRIDE**
- **FOM says**: contrarian 81, bubble_guard +30, IP 75 — model treats this as "錯殺 + recovery candidate"
- **Principal flagged**: "ORCL 已經開始下跌" — bubble breakdown stress
- **Compiler verdict**: **DEFER**. The discrepancy is real and important. The FOM's "contrarian" signal triggers because ORCL corrected from a high, but the principal's qualitative read sees ORCL's AI-cloud narrative as overpriced. The Risk Officer should not authorise this pick until either:
  - (a) ORCL prints 2 consecutive Q earnings with cloud growth re-acceleration, OR
  - (b) ORCL's drawdown extends to a structural bottoming pattern ([[../../philosophy/concepts/cycle-resonance]] criteria)
- **Replacement candidate**: **MSFT (Final FOM 57.1)** — contrarian 89, IP 95, bubble_guard +45 — same contrarian software thesis but cleaner bubble profile
- **Recommended action**: substitute MSFT for ORCL in slot #3

### Three final picks after Risk Officer review: META, LMT, MSFT

## §2. Top 25 watchlist (after substitution)

| Rank | Ticker | FOM | Mom | Contrarian | Cyclic | Quality | BubbleGuard | Sector | Note |
|---|---|---|---|---|---|---|---|---|---|
| 1 | **META** | 59.4 | 19.5 | 85.0 | 51.5 | 73.5 | **+45** | XLC | **PICK** |
| 2 | **LMT** | 58.2 | 20.8 | 87.0 | 51.5 | 46.8 | **+65** | ITA | **PICK** |
| 3 | ~~ORCL~~ | 57.2 | 31.7 | 81.0 | 51.5 | 55.7 | +30 | XLK | ⚠️ Principal-flagged, **deferred** |
| 4 | **MSFT** | 57.1 | 20.1 | 89.0 | 51.5 | 50.7 | **+45** | XLK | **PICK (sub for ORCL)** |
| 5 | ANET | 56.8 | 36.8 | 62.0 | 51.5 | 82.4 | +20 | XLK | Quality leader; Phase 2 lagged within optical |
| 6 | TSM | 56.3 | 46.5 | 50.0 | 60.2 | 87.5 | 0 | SOXX | Quality 88 (top); cyclic boost from SOXX-May |
| 7 | NOC | 56.3 | 20.3 | 86.2 | 51.5 | 49.6 | +45 | ITA | Same as LMT; pair for defense theme |
| 8 | CRDO | 56.2 | 74.6 | 40.0 | 60.2 | 67.0 | **-15** | SOXX | ⚠️ Bubble-flag mild |
| 9 | ARM | 56.2 | **81.0** | 46.0 | 60.2 | 72.9 | **-55** | SOXX | ⚠️ HIGH momentum but bubble-stress -55; avoid |
| 10 | AMAT | 55.4 | 61.9 | 43.2 | 60.2 | 84.2 | -25 | SOXX | Healthy quality but bubble-mild |
| 11 | GEV | 54.9 | 44.0 | 58.0 | 51.5 | 84.3 | -10 | XLI | Phase 4 power infra |
| 12 | GOOGL | 54.8 | 48.7 | 48.0 | 51.5 | 86.2 | 0 | XLC | Quality 86; antitrust overhang |
| 13 | LRCX | 54.7 | 66.2 | 43.2 | 60.2 | 82.3 | **-40** | SOXX | ⚠️ Bubble-flag |
| 14 | KLAC | 54.5 | 55.6 | 44.0 | 60.2 | 87.3 | -25 | SOXX | Quality 87 |
| 15 | **NVDA** | 54.5 | 34.6 | 48.8 | 60.2 | 87.4 | **+15** | SOXX | Still standing; not in top 3 (waiting $180 retest) |
| 16 | RTX | 54.4 | 25.7 | 65.2 | 51.5 | 69.7 | +35 | ITA | Defense pair |
| 17 | ALAB | 54.3 | **89.7** | 42.0 | 60.2 | 62.4 | **-70** | SOXX | ⚠️⚠️ Highest momentum + steepest bubble |
| 18 | AVGO | 54.3 | 40.0 | 46.0 | 60.2 | 81.8 | +15 | SOXX | Quality 82 |
| 19 | JNJ | 54.3 | 30.1 | 66.0 | 51.5 | 60.3 | +35 | XLV | Beta anchor |
| 20 | FN | 54.2 | 60.5 | 34.0 | 60.2 | 86.7 | -15 | SOXX | Phase 2 laggard |
| 21 | VRT | 54.1 | 61.2 | 42.0 | 51.5 | 77.4 | -10 | XLI | Phase 4 |
| 22 | POET | 54.1 | 81.3 | 32.0 | 60.2 | 71.5 | -40 | SOXX | ⚠️ |
| 23 | AMD | 53.7 | 82.9 | 40.0 | 60.2 | 72.6 | **-70** | SOXX | ⚠️⚠️ |
| 24 | GLW | 53.5 | 63.9 | 44.0 | 51.5 | 85.3 | -40 | XLK | Glass-substrate thesis |
| 25 | COHR | 53.4 | 67.1 | 36.0 | 60.2 | 80.5 | -40 | SOXX | Phase 2 at high |

## §3. Bubble-stress watchlist (the next-to-break)

These names have FOM bubble_guard ≤ -65 — system-flagged as parabolic-stress. **Strict no-new-entry**, existing positions should consider trim:

| Ticker | Bubble Guard | Momentum | Note |
|---|---|---|---|
| **AXTI** | **-95** | 87.7 | Phase 3 SiPh; up 78× in 1y per Serenity calls |
| **MU** | **-95** | 81.9 | Phase 1 memory; principal said memory already played |
| **STX** | **-95** | 77.1 | Same memory cycle |
| **AEHR** | **-95** | 81.2 | SiPh test equipment |
| **SIMO** | **-95** | 77.9 | Memory adjacent |
| **WDC** | **-95** | 73.3 | Memory cycle peaked |
| ALAB | -70 | 89.7 | SiPh recent IPO |
| AMD | -70 | 82.9 | AI GPU peak |
| INTC | -70 | 82.2 | Agent-AI CPU pop |
| CIEN | -70 | 68.3 | Optical |
| LITE | -70 | 62.9 | Optical |
| TER | -70 | 63.2 | Test equipment |
| ON | -70 | 71.7 | Power semi |
| NVTS | -65 | 89.7 | Power semi (Serenity-named) |
| AAOI | -65 | 72.5 | Optical |
| RKLB | -65 | 79.8 | Space momentum |

**Pattern**: 13 of the 16 most bubble-stressed names are in **SOXX**. The semiconductor cycle peak signal is broad-based across the entire downstream supply chain. **Only NVDA (+15), TSM (0), AVGO (+15), KLAC (-25) hold "non-extreme" bubble_guard scores in SOXX** — they remain the survivor tier.

## §4. The principal's bubble watchlist — FOM verdict

The principal named **ORCL, OKLO, SMCI** as "已經開始下跌". Empirical FOM:

| Ticker | FOM rank | Final FOM | Momentum | BubbleGuard | Verdict |
|---|---|---|---|---|---|
| ORCL | 3 | 57.2 | 31.7 | **+30** | FOM disagrees; treats as healthy correction. **Compiler defers to principal's override.** Replaced with MSFT in slot #3. |
| SMCI | ~30 | mid-40s | 29.0 | +15 | FOM agrees: low momentum, but bubble not yet flagged. **Correction in progress.** |
| OKLO | ~50 | low-40s | 26.6 | -15 | FOM agrees mildly: low momentum + bubble-flag. **Correction confirmed.** |

The principal's calibration is **correct on SMCI / OKLO** (FOM picks them up as weakened). **Disagrees on ORCL** — the FOM treats it as still in early-correction-pre-bottom; principal sees it as bubble-broken. Compiler defers to human, but flags this for future FOM calibration: ORCL is the **canonical test case** for whether bubble_guard needs a "drawdown-acceleration" sub-component.

## §5. Bucket assignment + sizing for next 30 days

Given current macro position ([[../01_macro_state]] §4a — Y2 midterm pre-Nov, Sell-in-May entering):

| Slot | Ticker | Bucket | Size | Quadrant | Strategy |
|---|---|---|---|---|---|
| long_new_1 | META | 6m core | 7% | 多頭真漲 | A consolidation re-entry |
| long_new_2 | LMT | 6m-12m | 5% | 多頭真漲 | A + ITA Nov seasonal carry |
| long_new_3 | MSFT | 6m core | 7% | 多頭真漲 | A consolidation re-entry |
| short_new_1-2 | null | — | — | — | No high-conviction short setup |
| position_followup_1-6 | TBD | — | — | — | None yet (Phase 1 system has no priors) |

Total new long deployment: **19%** of portfolio. **Below the 35% per-week max-new-money cap** ([[../../philosophy/08-risk-and-position]]) — fits comfortably.

## §6. Persistence tracking (Phase 3+ feature)

This is the first FOM run. **Persistence_weeks = 0 for all candidates**. Future cadence:
- Weekly: re-run FOM; persistence count incremented for any ticker appearing in top 50 for consecutive weeks
- +5% FOM boost per consecutive week (capped at +30% = 6 weeks)
- A ticker appearing 4+ weeks consecutive earns "high-conviction" tag
- A pick that **drops out of top 50** resets persistence to 0

Phase 3 implementation builds `data/persistence_state.json` for cross-run tracking.

## §7. Open questions / Researcher follow-up

1. **ORCL discrepancy** — explore why FOM differs from principal. Add bubble-guard "drawdown-acceleration" sub-component? Or trust principal qualitative override and document?
2. **Russell 2000 broad exposure** — IWM is in universe as ETF only; full R2K screening across 2000 names is not yet implemented. Phase 4 will add `screener/r2k.py`.
3. **Persistence tracking** — needs cross-run state file
4. **Backtest from 2016** — verify FOM would have identified the actual leaders in Trump-1 era and Biden era. Phase 4 work.
5. **Serenity name verification** — XFAB is European-listed (not in yfinance US format), POWI / NVTS in universe; ASMI failed pull (also European-listed). Need ADR-aware data source.

## See also

- [[../01_macro_state]] — current regime (BTC cycle bottoming + Y2 midterm pre-Nov + Sell-in-May)
- [[../06_cycle_framework]] — multi-scale cycle inputs to FOM cyclic score
- [[../07_ai_bubble_audit]] — comprehensive bubble audit (see next page)
- [[../../philosophy/_proposals/]] — multi-scale cycles concept proposals
- [[../../raw/macro/principal-narrative-2026-05-29]] — principal sector intuitions
- [[../../raw/macro/principal-cycles-2026-05-29]] — principal cycle directive
- [[../../raw/kol_signals/serenity-aleabitoreddit-profile-2026-05-29]] — Serenity methodology
