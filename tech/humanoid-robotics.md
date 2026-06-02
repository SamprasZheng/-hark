---
type: synthesis
domain: tech-trend
phase: C
tags: [humanoid-robotics, optimus, figure, vla, reducers, china-supply-chain]
as_of_timestamp: 2026-05-31T04:30:00+08:00
author_role: researcher
confidence: 0.71
verdict: 結構
verdict_by_horizon: {T0: 太早, T1: 結構, T2: 質變, T3: 質變}
rubric: {A1: 1, A2: 1, A3: 2, A4: 2, A5: 1}
sources_grade_summary: "A: 8 B: 6 C: 4 D: 0 E: 0"
---
# 人形機器人 — Demo ≠ Deployment 的真實裁決 / Humanoid Robotics: Adjudicating the Hype

## 0. 一句話判決 + desk view / Verdict
**結構 (structural, conf 0.71)** — but the verdict splits hard by horizon. The narrative ("humanoids are here, millions coming") is running ~3-5 years ahead of the physics. The decisive 2026 fact: **the most credible operator, Tesla, admitted on its Q4-2025 call that ~0 Optimus units are doing useful autonomous factory work — "still in the R&D phase"** [Tesla Q4-2025 call / Optimus R&D admission — webpronews — retrieved 2026-05-31 — grade C — cross-confirmed]. Meanwhile real *paid* deployment is happening — but it is **caged, repetitive logistics work (Agility Digit moving totes; UBTECH/Figure on auto lines), mostly teleop-seeded, not general-purpose autonomy.** Desk view: this is **autonomous-driving circa 2019** — a genuine structural build-out where the *picks-and-shovels (NVDA brain, Japanese/Chinese reducer & actuator makers) are investable now*, the *binary humanoid-OEM bets are a Moonshot ring-fence*, and the *general-purpose home robot is 太早 today, plausibly 質變 by T2-T3 only if the VLA autonomy curve and the BOM-cost curve both cross.* The single most under-priced fact: **China already ships ~90% of global humanoid units and builds them at ~1/3 the Western BOM cost** — the value chain is being decided in Hangzhou/Shenzhen, and most of it is not US-listed.

## 1. 技術與產品底蘊 (A1, engineer-grade)
The hard problems are **hands and brains, not legs.** Locomotion is largely solved (Atlas does parkour; actuators now beat human muscle on speed/power-density) — the bottleneck is **dexterous manipulation + tactile perception, still well below human level** [PatSnap / dexterous manipulation 2026 — retrieved 2026-05-31 — grade C — single-source-pending]. Three sub-problems gate deployment:

1. **Actuators & reducers.** Each humanoid needs ~28 rotary+linear actuators plus ~20 coreless motors for the hands; **drives/motors/reducers/ball-screws/bearings = ~55% of BOM**, vs sensors 17% and AI compute/software ~13% [Optimus BOM breakdown / 55% hardware — 36Kr — retrieved 2026-05-31 — grade C — single-source-pending]. The precision joint = **harmonic (strain-wave) reducer** — the highest-value, hardest-to-commoditize part. This is the genuine engineering moat and the cleanest investable node (§4).
2. **The VLA brain (vision-language-action) + sim-to-real.** The 2024-26 leap is dual-system VLA models — a slow "reasoning" VLM + a fast reactive policy. Figure **Helix** (7B backbone), NVIDIA **GR00T N1.x** (2.2B), Physical Intelligence **π0** (3B) all share this architecture [VLA architectures / params — codesota + Wikipedia — retrieved 2026-05-31 — grade C — cross-confirmed]. The unsolved part is **generalization**: policies transfer poorly off-distribution, and dexterous-manipulation training data with real industrial parts is scarce — which is *why* almost every "autonomous" demo is teleop-seeded.
3. **Teleoperation vs autonomy — the credibility crux.** Tesla's 2024 "We, Robot" bots were human-teleoperated (Adam Jonas/Morgan Stanley flagged it); the Dec-2025 Miami Optimus demo fell over in a way observers read as a VR-teleop artifact [Optimus teleop / Miami demo — interestingengineering + futurism — retrieved 2026-05-31 — grade C — cross-confirmed]. **Rule for this page: unless a deployment is explicitly labelled autonomous, assume teleop.** A demo video is marketing; *hours of unattended useful work* is the only real metric. **A1=1** — deep, real engineering, but the core autonomy + dexterity problem is unsolved, so product底蘊 is "promising R&D," not a finished product.

## 2. 需求真實性 — 數據 (A2, Q/FY + verification)

| 指標 metric | 數值 value | 期間 period | 來源 (grade — verification) |
|---|---|---|---|
| China share of global humanoid shipments | ~90% | entering 2026 | TechCrunch / Rest of World (B — cross-confirmed) |
| Global humanoid shipments 2026 (forecast) | >50,000 (+700% YoY) | CY2026e *projection* | TrendForce (B — single-source-pending) |
| Unitree shipments | ~5,500 (redacted) → 20,000 target | CY2025 / CY2026e | SCMP / Rest of World (B — cross-confirmed) |
| Figure 03 delivered | >350; rate 1/day→1/hr | as of Apr-29-2026 | Figure IR (A — primary-fetched) |
| UBTECH Walker S2 cumulative orders | >¥800M (~US$112M) | since early-2025, PR Nov-17-2025 | UBTECH PR Newswire (A — primary-fetched) |
| Agility Digit totes moved (GXO) | >100,000 | cumulative to 2026 | Agility / Robot Report (B — single-source-pending) |
| Tesla Optimus units doing useful autonomous work | ~0 ("R&D phase") | Q4-2025 call (Jan-28-2026) | Tesla call coverage (C — cross-confirmed) |
| Tesla Optimus produced 2025 vs promise | few hundred vs 10,000 promised | CY2025 | coverage (C — cross-confirmed) |

The asymmetry is the story: **real, paid demand exists — but it is narrow logistics/auto-line work, dominated by China on units, and Tesla (the marquee Western name) has the *fewest* productive units of the lot.** UBTECH's ¥800M is the largest hard *order book* primary I could verify; Figure's 350 units at 1/hour is the most credible Western *production* primary. Everything labelled "millions" is a dated projection. **A2=1** — demand is real and accelerating but tiny, narrow, and teleop-assisted; "general-purpose" demand is unproven.

## 3. 資金與權威 (A3)
Capital is *overwhelmingly* validating the theme — this is the strongest axis. Robotics startups raised **~$14B in 2025** (vs $8.2B 2024) [Crunchbase / robotics funding — retrieved 2026-05-31 — grade B — cross-confirmed]. **Figure** ~$1.9B raised, **$39B** valuation (Series C, Sep-2025); **Apptronik** $935M raised at ~$5.3B (Feb-2026), backers include **Google + Mercedes-Benz**; **1X** sought $1B at $10B+ [Apptronik $935M/$5.3B — TechCrunch — retrieved 2026-05-31 — grade B — cross-confirmed]. Strategic authority: **Hyundai (owns Boston Dynamics) committing to 25,000-30,000 Atlas units/yr** for its own US plants by ~2028, with Google DeepMind as the other 2026 Atlas customer [Hyundai 30k Atlas / RMAC — TechTimes + Automate.org — retrieved 2026-05-31 — grade B — cross-confirmed]; **Unitree filed a ~¥4.2B (~US$608M) Shanghai STAR IPO** — China's first listed humanoid pure-play, on 335% revenue growth and ~60% gross margin [Unitree STAR IPO ¥4.2B — Rest of World + SCMP — retrieved 2026-05-31 — grade B — cross-confirmed]. **A3=2** — capital and corporate-strategic backing are unambiguous and rising; this is a real, funded build-out, not vapor. (Caveat: $39B for Figure on <400 units shipped is itself an echo-chamber datapoint — §8.)

## 4. 受益 vs 受損 vs 抄底 (A4)

| 類別 | 名稱 (ticker) | 為何 / why | 投資性 |
|---|---|---|---|
| **Picks-and-shovels — 真受益** | NVIDIA (NVDA) | The robot "brain": Jetson AGX **Thor** devkit **$3,499**, T5000 modules; GR00T VLA + Isaac sim — "the Android of robots." Sells to *every* OEM regardless of who wins [NVIDIA Jetson Thor $3,499 / GR00T — NVIDIA + TechCrunch — retrieved 2026-05-31 — grade A — primary-fetched] | Already monetizing; diversified |
| **Reducer/actuator — 結構受益** | Harmonic Drive (6324.T, JP) | Strain-wave reducer leader; FY03/26 sales ~¥59.7B (+7.3%), 3-yr target ¥90B by FY03/27; GS sees humanoid TAM +5-10× [Harmonic Drive FY26 ¥59.7B — Quartr/IR — retrieved 2026-05-31 — grade B — cross-confirmed] | Pure-play, **non-US** |
| **China actuator/reducer** | Leaderdrive, Sanhua, Tuopu (CN/HK) | China's largest harmonic-reducer maker (Leaderdrive); Sanhua won a **~$685M (¥5B)** Optimus actuator order (Oct-2025); Tuopu planning ~$5B robot-drive capex [Sanhua $685M Optimus order — 36Kr — retrieved 2026-05-31 — grade C — single-source-pending] | **Mostly non-US** |
| **OEM binary bets — Moonshot** | Tesla (TSLA), Figure (pvt), Apptronik (pvt), Unitree (CN IPO) | Optionality, not cashflow; Tesla Optimus is a TSLA sub-thesis, not a separate ticker | Ring-fence only |
| **受損 / at risk** | Pure-vision teleop-demo names; high-labor-cost OEMs; Western-only BOM builders | China BOM ~$46k vs non-China ~[redacted-amt] (MS, 2025) → ~3× cost penalty for Western-only chains | Avoid |
| **抄底候選 (on pullback)** | NVDA on AI-capex drawdown; 6324.T on industrial-robot cycle trough | Picks-and-shovels with real revenue, bought when the *theme* (not the *fundamentals*) corrects | Value-on-pullback |

The investable truth mirrors [[autonomous-driving]]: **buy the shovel (NVDA brain + reducer/actuator makers), not the binary OEM.** The cruel catch — the best reducer/actuator pure-plays (Harmonic Drive, Leaderdrive, Sanhua, Tuopu) are **Japanese/Chinese, not US-listed**, so the FOM registry can only really hold NVDA + Tesla-as-sub-thesis. **A4=2** — clear, durable chokepoints exist (reducers, actuators, edge compute); that they're largely non-US is the key constraint for a US book.

## 5. 多時程 / Multi-horizon
- **T0 (0-1y) 太早.** Few thousand units globally, mostly caged logistics + teleop-seeded auto-line work; Tesla ~0 productive units. Only NVDA monetizes today. General-purpose autonomy not delivered.
- **T1 (1-3y) 結構.** **Factory/warehouse pilots → multi-thousand-unit fleets** (Hyundai 30k Atlas line, UBTECH/Unitree 10-20k/yr, Figure BotQ 12k→100k). Structural, datable, but narrow-task and capital-heavy. The reducer/actuator demand becomes a real revenue line for suppliers.
- **T2 (3-5y) 質變 (conditional).** If VLA generalization + BOM cost both cross (toward ~$20-30k/unit, near-human dexterity), humanoids become a genuine new labor category in semi-structured settings. This is the qualitative-change horizon — *conditional, not guaranteed.*
- **T3 (5-10y) 質變.** General-purpose + home humanoids plausible if T2 conditions hold; Morgan Stanley's $5T-by-2050 TAM lives here — a dated long-range projection, not a base case [MS humanoid TAM $5T-2050 — Tiger Brokers — retrieved 2026-05-31 — grade C — single-source-pending].

## 6. 爆發條件 + 里程碑階梯 / Milestone ladder (weekly-trackable)
1. **Tesla Optimus external/paid deployment count > 0.** How: Tesla 8-K/earnings calls. Status ❌ (Q4-2025: ~0 useful units, "R&D phase"). Next check: Q2-2026 call.
2. **A non-Tesla commercial humanoid order > 1,000 units (single contract).** How: company PRs/filings. Status ⏳ (UBTECH ¥800M *cumulative* across many buyers; no single >1,000-unit autonomous order confirmed). Next check: Unitree IPO prospectus + UBTECH/Figure PRs.
3. **Reducer/actuator cost break + supplier revenue inflection.** How: Harmonic Drive (6324.T) / Leaderdrive quarterly sales attributing growth to humanoid (not just industrial/semi). Status ⏳ (6324.T Q3-FY26 +4.5%, cited "AI robots" — but humanoid not yet separable). Next check: 6324.T FY03/26 full-year (May-2026).
4. **VLA autonomy benchmark crosses + a labelled-autonomous multi-hour deployment.** How: RoboArena/RobotArena∞ leaderboards (ICLR-2026) + a vendor publishing *unattended* runtime hours. Status ⏳ (benchmarks maturing; GR00T N2 "#1 RoboArena" claim is vendor, single-source). Next check: quarterly.
5. **China BOM < $30k confirmed by teardown.** How: teardown/analyst BOM. Status ⏳ (MS: ~$46k 2025e). Next check: semi-annual.
6. **Dexterous-hand cycle-life / tactile spec reaches industrial reliability.** How: vendor MTBF/yield disclosures (Figure cited >80% EOL first-pass yield). Status ⏳. Next check: quarterly.

## 7. 時代影響 + 跨主題 / Era impact & cross-links
Humanoids are the **embodied frontier of the same AI stack** that powers everything else in Phase-C — the synergies are unusually tight:
- [[model-leadership-and-data]] — VLA = the embodied frontier model; whoever owns the largest *real-world manipulation* dataset + best world-model wins the policy. The data moat, not the chassis, decides it.
- [[autonomous-driving]] — **shared autonomy + world-model + edge silicon.** A robot is "a car that walks"; NVIDIA's Thor (robot) and DRIVE Thor (car) are the *same* chip family, and the sim-to-real / teleop-data playbook is identical. The "demo ≠ deployment" lesson transfers 1:1.
- [[ai-datacenter-power]] — every VLA + sim-to-real pipeline (Isaac/Cosmos, Dojo) is trained in the same GPU datacenters; humanoid training adds to the same compute/power demand curve.
- [[china-ai-stack]] — the humanoid supply chain *is* a China-AI-stack story: ~90% of units, ~1/3 the BOM cost, vertically integrated motors/reducers — the most concrete place China leads the West in applied AI hardware.

## 8. 同溫層 + 自我打臉 / Echo-chamber + self-refutation
**Echo-chamber gap:** Western retail/X equates "Optimus reveal" + "Figure $39B" with *imminent autonomous humanoids*. The data refutes it on two fronts: (1) **autonomy is teleop-assisted** — Tesla itself said ~0 useful units; (2) **the West is losing the unit race** — China ships ~36× more units than Tesla+Figure combined and at ~1/3 the cost. The consensus is *long the wrong geography and early on autonomy.*

**打臉我自己的 bull case** (the dangerous, thesis-confirming claims, primary-checked):
- *"NVDA is the safe shovel"* — true today, but Jetson Thor robot revenue is a rounding error vs datacenter; if humanoids stall at T1, the "robot brain" TAM is years out. The shovel thesis is real but *small* near-term.
- *"Reducers are the chokepoint"* — yes, but Harmonic Drive's growth is still mostly **industrial robots + semicap**, not humanoid; I cannot yet separate humanoid revenue from the cycle. Tagging it "humanoid beneficiary" risks the [[memory-supercycle]]-style narrative-outruns-filing error.
- *"China wins the value chain"* — China wins *units and cost*, but the highest-margin precision parts (best strain-wave reducers, force-torque/tactile sensors) and the *brain* (NVDA) are still Japan/US — China's "win" is volume, not yet the margin pool.
- *Forward TAMs ($38B-2035, $5T-2050) are dated projections*, not facts — and humanoid forecasts have a long history of slipping (Tesla promised 10k units in 2025, shipped a few hundred).

**Bear case (the falsifiable core):** if VLA generalization plateaus and dexterous manipulation stays sub-human, humanoids stay stuck as expensive single-task teleop machines — and the $39B/$5.3B private marks compress hard. The whole thesis is **gated on the autonomy curve, which is the one thing no one has yet shown unattended at scale.**

## Sources
1. Figure — Ramping Figure 03 Production (>350 units, 1/hr, >80% yield) — https://www.figure.ai/news/ramping-figure-03-production — retrieved 2026-05-31 — grade A — primary-fetched
2. UBTECH PR — Walker S2 mass production, orders >¥800M (~$112M), 5k/2026 → 10k/2027 — https://www.prnewswire.com/news-releases/ubtech-humanoid-robot-walker-s2-begins-mass-production-and-delivery-with-orders-exceeding-800-million-[redacted-acct]24.html — retrieved 2026-05-31 — grade A — primary-fetched
3. NVIDIA — Jetson Thor / Isaac GR00T platform — https://www.nvidia.com/en-us/autonomous-machines/embedded-systems/jetson-thor/ — retrieved 2026-05-31 — grade A — primary-fetched
4. NVIDIA Investor — New Physical AI Models / partners' robots — https://investor.nvidia.com/news/press-release-details/2026/NVIDIA-Releases-New-Physical-AI-Models-as-Global-Partners-Unveil-Next-Generation-Robots/default.aspx — retrieved 2026-05-31 — grade A — primary-fetched
5. NVIDIA blog — Introducing Jetson Thor ($3,499 devkit, 2k TFLOPS) — https://developer.nvidia.com/blog/introducing-nvidia-jetson-thor-the-ultimate-platform-for-physical-ai/ — retrieved 2026-05-31 — grade A — cross-confirmed
6. Tesla Q1-2026 Form 8-K (shareholder deck, Optimus mass-production goal) — https://www.sec.gov/Archives/edgar/data/0001318605/000162828026026551/exhibit991.htm — retrieved 2026-05-31 — grade A — primary-fetched
7. TechCrunch — NVIDIA wants to be the Android of generalist robotics — https://techcrunch.com/2026/01/05/nvidia-wants-to-be-the-android-of-generalist-robotics/ — retrieved 2026-05-31 — grade B — cross-confirmed
8. TechCrunch — Why China's humanoid industry is winning the early market (~90% share) — https://techcrunch.com/2026/02/28/why-chinas-humanoid-robot-industry-is-winning-the-early-market/ — retrieved 2026-05-31 — grade B — cross-confirmed
9. Rest of World — China winning humanoid race / Unitree ~36× Tesla+Figure — https://restofworld.org/2026/china-humanoid-robots-unitree-agibot-tesla-optimus/ — retrieved 2026-05-31 — grade B — cross-confirmed
10. SCMP — Inside Unitree's landmark ~$608M STAR IPO (335% rev growth, ~60% GM) — https://www.scmp.com/tech/article/3347611/inside-unitrees-landmark-ipo-what-know-about-chinas-humanoid-giant — retrieved 2026-05-31 — grade B — cross-confirmed
11. TechCrunch — Apptronik $935M raised at ~$5.3B (Google, Mercedes) — https://techcrunch.com/2026/02/11/humanoid-robot-startup-apptronik-has-now-raised-935m-at-a-5b-valuation/ — retrieved 2026-05-31 — grade B — cross-confirmed
12. Crunchbase News — record robotics funding ~$14B 2025; Apptronik $520M — https://news.crunchbase.com/venture/ai-humanoid-robot-funding-apptronik/ — retrieved 2026-05-31 — grade B — cross-confirmed
13. TechTimes — Hyundai commits 25,000 Atlas; union block — https://www.techtimes.com/articles/317005/20260522/hyundai-commits-25000-atlas-robots-own-factories-union-blocks-deployment-without-labor-deal.htm — retrieved 2026-05-31 — grade B — cross-confirmed
14. Automate.org — Boston Dynamics to ship first Atlas in 2026 (Hyundai + DeepMind) — https://www.automate.org/robotics/industry-insights/boston-dynamics-to-begin-production-on-redesigned-atlas-humanoid-in-2026 — retrieved 2026-05-31 — grade B — cross-confirmed
15. Quartr — Harmonic Drive Systems (redacted) FY26 ¥59.7B guide / ¥90B FY03/27 target — https://quartr.com/companies/harmonic-drive-systems-inc_15793 — retrieved 2026-05-31 — grade B — cross-confirmed
16. TrendForce — 2026 humanoid shipments >50k (+700%); Japan core-components vs US/China systems — https://www.trendforce.com/presscenter/news/20251209-12825.html — retrieved 2026-05-31 — grade B — single-source-pending
17. 36Kr — Musk's 1M-robot plan: motors/reducers/lead-screws made in China; BOM ~55% hardware; Sanhua $685M order — https://eu.36kr.com/en/p/3780414717129481 — retrieved 2026-05-31 — grade C — single-source-pending
18. interestingengineering — Optimus Miami demo fall / teleop debate — https://interestingengineering.com/ai-robotics/teslas-optimus-falls-in-miami-demo — retrieved 2026-05-31 — grade C — cross-confirmed
19. webpronews — Optimus skepticism / Q4-2025 "R&D phase" admission — https://www.webpronews.com/tesla-optimus-robot-tumbles-in-demo-ignites-skepticism-on-musks-vision/ — retrieved 2026-05-31 — grade C — cross-confirmed
20. PatSnap — Humanoid dexterous manipulation 2026 (manipulation/tactile = bottleneck) — https://www.patsnap.com/resources/blog/rd-blog/humanoid-robot-dexterous-manipulation-2026-patsnap-eureka/ — retrieved 2026-05-31 — grade C — single-source-pending
21. codesota — VLA leaderboard / model params (Helix 7B, π0 3B, GR00T 2.2B) — https://www.codesota.com/robotics — retrieved 2026-05-31 — grade C — cross-confirmed
22. Morgan Stanley (via Tiger Brokers) — humanoid TAM $38B-2035 / $5T-2050; China-US gap — https://www.itiger.com/news/1124207069 — retrieved 2026-05-31 — grade C — single-source-pending

