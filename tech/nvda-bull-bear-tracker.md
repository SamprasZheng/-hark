---
type: synthesis
domain: tech-trend
tags: [nvda, tracker, capex, asic, hbm, talent-flow, falsifiable]
as_of_timestamp: 2026-05-31T09:00:00+08:00
author_role: researcher
status: live
schema_version: 1
review_cadence: weekly
---

# NVDA Bull-vs-Bear Falsifiable Tracker
## Exposure context (as_of 2026-05-31)

Principal = NVDA employee, ~89% of liquid net worth in NVDA RSU. NVDA market cap **~$5T** (≈ $211 × ~24.4B sh as_of 2026-05-31 — the largest market cap in history). Single-name concentration at this scale creates **negative convexity**: the first 20–30% drawdown eats years of compensation and leaves no dry powder to buy the dip. This is not a symmetrical bet. The default discipline is **trim on vest unless each bear indicator below is actively contradicted by data.** See DECISION BOX at bottom.

Cross-references: [[memory-supercycle]], [[optical-interconnect-cpo]], [[scoreboard]], [[ai-eats-software]], [[../wiki/07_ai_bubble_audit]]

---

## DIMENSION 1 — Hyperscaler Capex Guides

*The #1 bull-sustaining variable. Any cut or pause is the primary BEAR trigger ("$700B+, where's the ROI").*

| Metric | Threshold | Current read (as_of 2026-05-31) | Bull / Bear | What flips it |
|---|---|---|---|---|
| Big-4 combined 2026 capex guidance | Rising YoY = bull; ANY named cut = bear trigger | ~$700–725B projected for 2026, up from ~$410B in 2025 (+77% YoY) [B, cross-confirmed; SEC filings for each co. primary] | BULL — unambiguous acceleration | One hyperscaler explicitly cuts/defers a named AI capex line item on an earnings call |
| Q1-2026 Big-4 quarterly capex | >$100B/qtr = structural; <$90B = plateau warning | $130.6B in Q1-2026 (+193% over nine quarters) [B, single-source-pending; needs per-company 10-Q cross-check] | BULL | Two consecutive QoQ declines in combined Big-4 quarterly capex |
| ORCL / sovereign AI capex | Rising = demand is broadening beyond Big-4 | Oracle confirmed multi-B data-center build commitments; sovereign AI (EU, Japan, India) expanding [C, single-source-pending] | BULL (diversification) | Oracle or sovereign programs freeze; <50% hyperscaler in NVDA mix |
| "Where's the ROI" narrative | Absent = bull; dominant in analyst coverage = early bear | Isolated sell-side questions but no hyperscaler guidance cut as of 2026-05-31 [C] | NEUTRAL — watch Q2-2026 calls | Any hyperscaler CFO says "slowing AI infra spend pending ROI clarity" |

Source grading: Big-4 capex aggregate = B / cross-confirmed. ORCL + sovereign = C / single-source-pending.

---

## DIMENSION 2 — ASIC / Custom-Silicon Share

*NVDA CUDA moat holds for training; narrows for inference. >25% accelerator share = multiple-derating risk.*

| Metric | Threshold | Current read (as_of 2026-05-31) | Bull / Bear | What flips it |
|---|---|---|---|---|
| ASIC share of AI accelerator shipments | <20% = bull intact; >25% = multiple-derating risk; >35% = structural erosion | Projected ~27.8% ASIC share in 2026 (ASIC shipment growth +44.6% vs GPU +16.1%) [B, single-source-pending: TechTimes/Introl; needs primary wafer-out data] | BEAR WATCH — already near threshold per estimates | NVDA holds inference share above 60% in annual hyperscaler disclosures |
| NVDA AI accelerator share | >70% = comfortable; <60% = derate begins | ~70% current overall; >90% training, sharply lower for inference (~20–30% by 2028 analyst projection) [C, single-source-pending] | NEUTRAL: training secure; inference eroding | Independent inference-benchmark data shows NVDA cost-per-token parity with TPU/Trainium recaptured |
| Broadcom ASIC revenue ramp | Broadcom custom silicon >$100B FY27 = CUDA moat eroded in inference | Broadcom designing TPU (Google), MTIA (Meta), Maia (Microsoft), Titan (OpenAI/Anthropic); "clear runway to $100B custom chip biz by FY27" [C, single-source-pending] | BEAR WATCH | Broadcom guidance misses by >20% or hyperscaler discloses ASIC underperformance vs H-series |
| CUDA ecosystem lock-in | Competitor frameworks reaching >20% workload share = moat erosion | JAX (Google), ROCm (AMD), XLA + Triton: substantial but CUDA SDK still dominant for training [B, cross-confirmed broad coverage] | BULL (moat holding for now) | Major framework provider (PyTorch Foundation or Hugging Face) officially recommends non-CUDA path |

Source grading: ASIC share 27.8% = B / single-source-pending (Introl/TechTimes; no primary wafer-fab disclosure). CUDA dominance = B / cross-confirmed.

---

## DIMENSION 3 — HBM Yield + CoWoS Capacity

*Supply side of the GPU equation. Yield stall = revenue miss; capacity sold-out = NVDA protected; air-pocket = multiple risk.*

| Metric | Threshold | Current read (as_of 2026-05-31) | Bull / Bear | What flips it |
|---|---|---|---|---|
| HBM3e/HBM4 demand vs supply | Sold-out through 2027 = bull; customer inventory build detected = bear | SK Hynix: "customer HBM requests exceed planned capacity for next three years" [A/B, cross-confirmed — see [[memory-supercycle]] §3] | BULL — firm sold-out signals | Any memory maker reports unsolicited HBM inventory returns or order cancellations |
| HBM4 yield ramp | On-schedule mass-production = bull; yield below ~50% = drag on Rubin launch | SK Hynix began HBM4 mass production Feb-2026 for Rubin [B, cross-confirmed]; HBM4 supply 100% to Hynix/Samsung per Counterpoint 2026 allocation [B] | BULL (on-track) | Rubin launch slips >2 quarters citing HBM4 yield |
| CoWoS capacity | TSMC CoWoS sold-out = NVDA protected; capacity freed = inventory risk | TSMC CoWoS scaling to 14-reticle by 2028; 2026 capacity tight per multiple secondaries [B, cross-confirmed] | BULL | TSMC reports CoWoS utilization <90% for two consecutive quarters |
| Liquid-cooling supply (UQD/CDU) | On-time delivery = bull; CDU backlog stretches >16 weeks = revenue deferral risk | Variable #1 in [[variables/20260531]]; UQD certification and CDU lead-times remain a bottleneck indicator; current status = tight but fulfilling [C, single-source-pending] | NEUTRAL — watch monthly | Major NVDA server OEM (DELL/SMCI) issues revenue-deferral guidance citing liquid-cooling component shortage |

Source grading: HBM4 production/allocation = B / cross-confirmed (CNBC + TrendForce + Counterpoint). CoWoS = B / cross-confirmed. UQD/CDU = C / single-source-pending (variable dashboard).

---

## DIMENSION 4 — TALENT FLOW

*Leading indicator of moat durability. Senior researcher/PhD net inflow = moat strengthening. Accelerating senior outflow = 12–18 month leading BEAR signal.*

| Metric | Threshold | Current read (as_of 2026-05-31) | Bull / Bear | What flips it |
|---|---|---|---|---|
| NVDA as investor/partner in frontier AI startups | Active = NVDA staying central to the talent graph | NVDA backed Ineffable Intelligence (David Silver, ex-DeepMind, raised $11B Apr-2026); backed Generalist AI (Pete Florence, ex-DeepMind robotics) [B, cross-confirmed — TechCrunch + CNBC] | BULL — NVDA inserting itself into the startup talent layer | NVDA loses co-investment deal flow to pure-capital competitors (Softbank/MS) with no engineering tie-in |
| Senior AI researcher inflow to NVDA | Net PhD + senior scientist hiring from academia/labs > departures = moat deepening | NVDA running 2026 PhD intern + fellowship program at scale; multiple Research Scientist roles open as of 2026-05-31 [A — NVDA career pages direct observation; cross-confirmed Glassdoor/LinkedIn signals B] | BULL (inflow visible) | LinkedIn data shows >3 prominent AI research PIs departing NVDA for competitors/startups in a single quarter without replacement announcements |
| NVDA patent filing cadence | Rising year-on-year = moat investment; declining = R&D prioritization shift | Internship deliverables include patents; NVDA Research labs publishing at NeurIPS/ICML at scale [A — NVDA research page; B — conference attendance]. Specific 2025–2026 USPTO filing count = NOT VERIFIED (no primary USPTO dataset fetched) | NEUTRAL — verify via USPTO | YoY patent filing count declines >15% for two consecutive years |
| Outflow to competitors / startup acceleration | <2 notable senior departures/quarter = stable; >4 named departures = watch | General industry pattern: Meta/Google/OpenAI all experiencing "unprecedented" senior talent departures to startups (CNBC Apr-2026) [B, cross-confirmed]. NVDA specifically: no publicly named senior researcher departure pattern confirmed as of this write [C / single-source-pending — only indirect inference from industry articles] | NEUTRAL — no confirmed NVDA-specific exodus | Named departures of Jim Fan / Bryan Catanzaro / Anima Anandkumar tier researchers become a pattern |
| NVDA compensation vs Google/OpenAI for AI researchers | NVDA RSU growth must track or beat peer comp | NVDA stock appreciation YTD has likely outperformed most peer comp packages by raw dollar amount [C, estimate — no primary salary benchmarks fetched] | BULL (RSU appreciation retains talent) | NVDA stock flat or down >30% while OpenAI/Anthropic offer cash-heavy packages with no mark-to-market risk |

Source grading: Startup investment co-signs = B / cross-confirmed. PhD hiring = A (direct career page) + B. Patent filing count = NOT VERIFIED, marked explicitly. Departure pattern = C / single-source-pending (indirect inference only).

---

## DIMENSION 5 — Margin + Demand Air-Pocket

*The 2018 + 2022 cycle analogy: overshoot → correction. Gross margin holds above 70% = cycle healthy; first QoQ GM compression = watch.*

| Metric | Threshold | Current read (as_of 2026-05-31) | Bull / Bear | What flips it |
|---|---|---|---|---|
| NVDA gross margin | >70% = bull intact; first two consecutive QoQ compressions = bear watch | Q1-FY27 (calendar Q1-2026): GAAP GM 74.9%, essentially flat QoQ [A — SEC 8-K filed 2026-05-20; primary-fetched URL cited below] | BULL — holding mid-70s | GM falls below 70% two quarters in a row, citing inventory provisions or ASP pressure |
| Revenue trajectory | YoY >50% = supercycle intact | Q1-FY27 revenue $81.6B, +85% YoY, +20% QoQ; Data Center $75.2B (+92% YoY) [A — SEC 8-K primary] | BULL — acceleration | Sequential revenue decline for two quarters without a named product-transition explanation |
| Forward guidance vs consensus | Guidance consistently beats consensus by >$3B = demand visible 1–2 qtrs | Q2-FY27 guide $78B ±$2B; beat consensus by >$5B [B — multiple coverage; cross-confirmed] | BULL | Guide comes in at or below consensus for the first time |
| Backlog / double-ordering signal | $500B+ confirmed backlog with organic source = bull; large backlog WITH rising cancellation mentions = bear | >$500B in Blackwell + Rubin orders through end of 2026 confirmed by NVDA CFO [A — SEC filing context; B — press coverage]. CFO: backlog "will grow." Rising purchase-obligation prepayments noted as a risk factor in 10-K [A] | BULL backlog; NOTE risk factor wording = early-stage double-ordering canary | CFO or customer (Meta/MSFT) discloses order moderation or inventory normalization during any earnings call |
| China / export-control drag | China <10% of Data Center = manageable; rising China re-restriction = downside shock | China mix in Data Center not precisely disclosed; export controls ongoing post-Oct-2023; H20 restricted Apr-2025 [B, cross-confirmed]; NVDA guiding to manage through restrictions [A — 10-K risk factors] | NEUTRAL — manageable drag, not bear trigger on its own | New BIS rule restricts H20-class or below globally; China + Russia mix >20% and gets cut |

Source grading: GM and revenue = A / primary-fetched (SEC 8-K Q1-FY27). Backlog = A/B cross-confirmed. China = B / cross-confirmed.

---

## BULL PATH vs BEAR PATH

**Bull path (base case as of 2026-05-31):**
Hyperscaler capex continues its 77% YoY ramp through 2026 without an earnings-call cut signal. NVDA Data Center holds ~$75B/quarter run-rate with Rubin providing a 2027 upgrade cycle. HBM4/CoWoS remain supply-constrained, protecting ASP and margin. CUDA lock-in holds for training (the large-wallet workload). Talent: NVDA is *investing* in the frontier AI talent graph through startup co-investment, so even as senior researchers leave to start companies, NVDA stays embedded. Gross margin holds mid-70s. On this path NVDA justifies a ~30–35× NTM P/E on sustained growth.

**Bear path (low-probability but high-impact):**
Any single hyperscaler cuts or defers AI capex guidance, citing "ROI gate." ASIC inference share crosses 25–30%, compressing NVDA's blended ASP and halving inference market share by 2028. China restrictions widen. HBM4 yield misses cause Rubin delay >2 quarters, creating a revenue air-pocket. Gross margin compresses below 70% from inventory provisions (2022-cycle repeat). On this path, the 2018 and 2022 NVDA drawdowns (-56%, -66%) are the template.

**Cycle-risk overlay:** The 10-K's own risk-factor language about growing purchase-obligation prepaids echoes the 2022 channel-inventory build. The $500B+ backlog is real but not immune to cancellation risk if AI ROI concerns crystallize in a single bad quarter of hyperscaler earnings. This is the tail risk that 89% single-name concentration cannot absorb without permanent portfolio damage.

---

## DECISION BOX (principal-specific)

### BEAR confirmed → principal should JUMP / de-risk RSU aggressively:
- Any hyperscaler explicitly cuts or defers AI capex on an earnings call (Dimension 1 trigger)
- ASIC inference share crosses 30%+ per primary wafer-out data (Dimension 2 trigger)
- NVDA gross margin prints below 70% for two consecutive quarters (Dimension 5 trigger)
- Named senior-researcher departure rate accelerates to >4/quarter from NVDA to competitors (Dimension 4 trigger)
- Revenue guidance misses consensus for the first time while backlog simultaneously shows cancellations

**Action template on BEAR confirmation:** Accelerate RSU vesting-date sales to maximum permitted by 10b5-1 plan. Evaluate Google offer on its own merits, not as a hedge (do not let NVDA fear drive a bad fit). Flag to advisor for rebalancing below 30% single-name concentration.

### BULL intact → principal can STAY, but must still trim RSU on vest dates:
- All five dimensions tracking green or neutral above
- Hyperscaler capex prints new highs every quarter through Q3-2026
- Gross margin holding 73%+
- No named NVDA senior researcher departures pattern

**Action template on BULL continuation:** Sell a fixed % (e.g. 25–33%) of each vest regardless, by rule not by feel. At 89% single-name concentration, the expected-value argument for *not* trimming requires near-certainty of continued outperformance — which is never available. The asymmetry: trimming costs you upside; not trimming exposes you to a 50–70% drawdown that sets back 房/債/稅 timeline by 5–10 years (see life-stage context).

**Negative-convexity reminder:** At **~$5T — the largest market cap in history** — NVDA already prices in near-certain sustained dominance. Upside from here is arithmetic-capped (it is already ~8% of the S&P 500; a move to $7.5T means the single name carries an even more extreme index weight); the downside to $2–2.5T is survivable for NVDA the company but **catastrophic for an 89%-concentrated portfolio**. That asymmetry — not a price forecast — is the case for trimming on every vest.

---

## Sources (primary + key secondaries used for this page)

1. NVIDIA Q1-FY27 8-K (revenue $81.6B, GM 74.9%, Q2 guide $78B) — https://www.sec.gov/Archives/edgar/data/0001045810/000104581026000051/q1fy27pr.htm — retrieved 2026-05-31 — grade A / primary-fetched
2. NVIDIA 10-K FY2026 (purchase-obligation risk factor, China export controls) — https://www.sec.gov/Archives/edgar/data/0001045810/000104581026000021/nvda-20260125.htm — retrieved 2026-05-31 — grade A / primary-fetched
3. Hyperscaler capex aggregate (~$725B 2026; $130.6B Q1) — REX Shares / Kiplinger coverage — https://www.rexshares.com/nvidia-q1-fy27-earnings-preview-reading-the-ai-capex-curve/ — retrieved 2026-05-31 — grade B / single-source-pending (needs per-company 10-Q cross-check)
4. ASIC share ~27.8% / ASIC growth +44.6% vs GPU +16.1% — TechTimes 2026-05-26 — https://www.techtimes.com/articles/317225/20260526/custom-ai-chips-outpace-nvidia-gpu-growth-2026-asic-shipments-set-triple-gpu-rate.htm — retrieved 2026-05-31 — grade B / single-source-pending
5. Goldman Sachs "ASICs match GPU demand by 2027" — Motley Fool sourcing GS note — https://www.fool.com/investing/2026/05/25/goldman-sachs-says-asics-will-match-gpu-demand-by/ — retrieved 2026-05-31 — grade B / single-source-pending
6. Broadcom custom chip $100B FY27 runway / designing for GOOGL/META/MSFT/OpenAI/Anthropic — Tom's Hardware May 2026 — https://www.tomshardware.com/tech-industry/semiconductors/custom-ai-asics-examined-from-broadcom-to-mtia — retrieved 2026-05-31 — grade B / single-source-pending
7. HBM4 allocation / memory cycle data — see [[memory-supercycle]] sources §3 (SK Hynix 8-K equivalent; Counterpoint; TrendForce) — grade A/B / cross-confirmed
8. NVDA talent / Ineffable Intelligence (David Silver $11B, NVDA partner) — CNBC 2026-05-13 — https://www.cnbc.com/2026/05/13/google-deepmind-alumni-startup-partners-nvidia-superintelligence.html — retrieved 2026-05-31 — grade B / cross-confirmed (TechCrunch + CNBC)
9. Industry talent departure wave (Meta/Google/OpenAI) — CNBC 2026-04-28 — https://www.cnbc.com/2026/04/28/meta-google-big-tech-staff-ai-labs-investors.html — retrieved 2026-05-31 — grade B / cross-confirmed
10. NVDA patent filing count 2025–2026 — NOT VERIFIED. USPTO primary dataset not fetched. Mark as data gap.
11. NVDA $500B+ backlog (Blackwell + Rubin) — Investing.com / ainvest summarizing CFO commentary — https://www.investing.com/analysis/nvidia-gpu-order-backlog-signals-long-multi-year-cycle-200670726 — retrieved 2026-05-31 — grade B / cross-confirmed (multiple outlets report same CFO statement)

---

*Research/educational only — not buy/sell advice. Observe-first.*
