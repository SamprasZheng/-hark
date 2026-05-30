---
type: synthesis
domain: tech-trend
tags: [glp1, supply-chain, second-derivative, cdmo, biopharma]
as_of_timestamp: 2026-05-31T01:15:00+08:00
author_role: researcher
confidence: 0.62
parent: "[[ai-pharma-glp1]]"
sources_grade_summary: "A: 6 B: 6 C: 2 D: 0 E: 0"
---

# GLP-1 製造/供應鏈 二階深掘 / GLP-1 manufacturing supply-chain deep-dive

## 0. 一句話 / What this adds beyond the parent page

The parent thesis is "demand for GLP-1s is huge." This page asks the only question that matters for the pick-and-shovel trade: **who actually holds a bottleneck with pricing power, and who is being disintermediated as Lilly/Novo build their own walls?** The headline answer is uncomfortable for the merchant-supplier bull case: the two biggest spenders are spending to *insource*. Novo bought its main fill-finish CDMO (Catalent) [1], and Lilly is building >$50B of its own API + injectable plants [3][9]. The durable merchant chokepoints are narrowing to (a) solid-phase **peptide API** (where a 2-supplier world genuinely exists) and (b) **auto-injector devices** (where capital and tooling are scarce but customer concentration is dangerous). Oral small-molecule GLP-1 (orforglipron) breaks the peptide bottleneck entirely and reshuffles the map.

## 1. 節點排名表 / Ranked bottleneck nodes

| 節點 / Node | 代表公司 + ticker | 產能 / capex / 數據 (grade) | 二供難度 = 定價權 / 2nd-source difficulty = pricing power | 注射 vs 口服 |
|---|---|---|---|---|
| Solid-phase peptide API (SPPS) | Bachem BANB.SW; PolyPeptide PPGN.SW | Bachem >EUR 400M capex FY25; CHF 1bn 5-yr (2025–29) take-or-pay [4][8] | **High** — duopoly of merchant scale, regulated process, multi-yr qualification | 注射 + oral semaglutide |
| Sterile fill-finish (merchant) | Thermo Fisher TMO | +$1.5bn US capex over 4yr; bought Sanofi Ridgefield site Sep 2025 [10] | **High & rising** — Catalent exit "takes an option off the table" [11] | 注射 only |
| Captive fill-finish | Novo (ex-Catalent); Lilly in-house | Novo paid $11bn for 3 sites (Anagni/Bloomington/Brussels), capacity from 2026 [1] | n/a — captive, NOT for sale to rivals | 注射 only |
| API tonnage (captive) | Lilly LLY | >$50bn US capex since 2020; 3 of 4 new sites = API for tirzepatide [3][9] | n/a — insourced | both |
| Auto-injector / pen devices | Ypsomed YPSN.SW; Gerresheimer GXI.DE; SHL; BD | Ypsomed $248M NC plant (Novo-funded), live 2027 [6]; market ~1.5bn devices/yr [7] | **Medium** — tooling/validation scarce, but single-customer risk is acute [5] | 注射 only |
| Permeation enhancer / excipient (SNAC) | Merchant chemical suppliers | Rybelsus ≈400 mg SNAC vs 7–14 mg peptide per tablet [2] | **Low-Med** — high tonnage but simpler chemistry [2] | oral semaglutide only |

## 2. 胜肽 API 合成 / Peptide API synthesis

This is the cleanest bottleneck. Semaglutide/tirzepatide are made by solid-phase peptide synthesis (SPPS), and at commercial scale the API costs roughly **$70,000–$100,000 per kg** [2] — a number that signals process scarcity, not commodity. Merchant capacity is effectively a duopoly: **Bachem** (BANB.SW) is pouring **>EUR 400M of capex in 2025**, much of it into "Building K" at Bubendorf to more-than-double that site, and has locked a **minimum CHF 1bn, 5-year (2025–2029) take-or-pay supply contract** (customer undisclosed, almost certainly GLP-1-driven) [4][8]. **PolyPeptide** (PPGN.SW) is running a **EUR 100M (~$113M) doubling of SPPS capacity in Malmö** plus new large-scale lines in Braine-l'Alleud ramping through 2025 [4]. Pricing power here is real because qualifying a second peptide source takes years of regulatory work; the risk is that the *recombinant/enzymatic* route (cheaper at volume) erodes the SPPS moat over time, and that Lilly/Novo's own API plants [3][9] cap merchant upside.

## 3. 充填/CDMO 產能 / Fill-finish + CDMO

The single most important supply-chain event of the cycle: **Novo Holdings closed its ~$16.5bn acquisition of Catalent on 18 Dec 2024**, then immediately sold **three fill-finish sites (Anagni IT, Bloomington IN, Brussels BE) to Novo Nordisk for $11bn**, with added filling capacity coming online "from 2026 onwards" for Ozempic/Wegovy [1]. The second-order effect is the actual trade: Catalent's merchant sterile capacity left the open market. Thermo Fisher's CEO Marc Casper called it out directly — *"it takes an option off the table, which I think is ultimately very positive for us"* [11]. **Thermo Fisher** (TMO) is positioning to absorb the displaced demand, adding **$1.5bn of US capex over four years**, four high-speed prefilled-syringe lines in Greenville NC, and the **acquired Sanofi Ridgefield NJ sterile site (Sep 2025)** [10]. Lilly, meanwhile, refuses to rent: of its four new US sites, the fourth is a **$3.5bn Pennsylvania parenteral/injectables plant** [3][9]. Net: merchant fill-finish is tight and TMO has pricing power, but the two largest end-users are deliberately self-supplying.

## 4. 注射筆/自動注射器 / Pen + auto-injector devices

Device assembly is a genuine physical constraint — an analyst estimate cited ~**1.5 billion devices per year for ~30 million patients** as the GLP-1 delivery requirement [7]. **Ypsomed** (YPSN.SW) is the cleanest play: it signed a long-term, "large-quantity" autoinjector supply deal with Novo Nordisk (Sep 2023, deliveries from 2025), with **Novo funding a significant part of the new infrastructure**, and is building its **first US plant in Holly Springs NC for ~$248M (CHF 200M), operational 2027** [5][6]. **Gerresheimer** (GXI.DE) is the cautionary tale: its specialty dual-chamber syringe for Novo's CagriSema was pitched as up to **EUR 250M of 2027 revenue**, but Novo's Dec-2024 CagriSema trial disappointment plus reported syringe quality issues fed a **guidance cut in Oct 2025 (organic revenue -2% to -4%)** and a short-seller report [5]. Pricing power is medium and fragile: tooling is scarce, but single-customer concentration on a single drug program is the bear case in microcosm.

## 5. 口服 GLP-1 的供應鏈差異 / Oral GLP-1 supply-chain shift

**Orforglipron** (Lilly, FDA-approved for obesity **April 2026** as Foundayo) is a **small molecule**, not a peptide [the page assumes parent covers efficacy]. That single fact rewires the bottleneck: small-molecule synthesis scales like ordinary chemistry, so Lilly states confidence it can "launch worldwide without supply constraints" [no SPPS, no fill-finish, no injector] — which means it **disrupts the peptide-API duopoly, the sterile fill-finish chokepoint, and the auto-injector node all at once** for the oral share of the market. The losers if oral takes share: Bachem/PolyPeptide (no peptide), TMO sterile lines, and Ypsomed/Gerresheimer (no device). Note oral *semaglutide* (Rybelsus) is the exception — still a peptide and still needs **~400 mg of SNAC permeation enhancer per 7–14 mg dose** [2], a high-tonnage excipient demand, but that does not rescue the injectable-device suppliers.

## 6. 503B 複方禁令影響 / Compounding crackdown impact

The FDA declared the tirzepatide shortage resolved **19 Dec 2024** and semaglutide resolved **21 Feb 2025**, triggering enforcement deadlines: 503A pharmacies had to stop compounding tirzepatide by **19 Feb 2025** and semaglutide by **22 Apr 2025**; 503B outsourcing facilities by **19 Mar 2025** and **22 May 2025** respectively [12]. On **30 Apr 2026** the FDA went further, proposing to **exclude semaglutide, tirzepatide and liraglutide from the 503B bulks list**, finding no clinical need — effectively closing large-scale compounding permanently [13]. Supply-chain read-through: demand that was leaking to grey-market compounders is rerouted back into the *brand* supply chain (Lilly/Novo and their qualified API + fill-finish + device suppliers), structurally tightening the legitimate nodes above and adding volume to the merchant chokepoints that survive.

## 7. 同溫層風險 + 空方 / Echo-chamber + bear case

**Echo-chamber gap:** the popular "shovels" narrative treats every named supplier as a guaranteed toll-collector. The CAPITAL/ADOPTION signal says otherwise — the actors with the most capital (Novo $11bn fill-finish buy [1]; Lilly >$50bn capex [9]) are spending precisely to *not* pay merchants. **Vertical integration / disintermediation is the core bear case:** (1) Novo internalised its fill-finish, removing itself as a customer and *also* the merchant capacity; (2) Lilly is building captive API + injectable plants, so its incremental GLP-1 growth may bypass merchant CDMOs entirely; (3) orforglipron, if it wins oral share, deletes peptide-API, sterile-fill and device demand simultaneously [Lilly's own "no supply constraints" claim]. **Counter-bear (why merchants still survive):** Novo still signed a 5-yr Rovi manufacturing deal starting 2026, proving in-house capacity is insufficient near-term; peptide-API qualification lead times protect Bachem/PolyPeptide for several years; and the compounding crackdown reroutes volume into the brand chain. Device makers carry the worst single-customer risk (Gerresheimer/CagriSema [5]). Net confidence is moderate (0.62): the bottleneck is real today but its half-life is being actively shortened by the two end-users' own capex.

## Sources

1. Novo Holdings completes $16.5B acquisition of Catalent (and Novo Nordisk $11bn purchase of 3 fill-finish sites) — https://www.pharmamanufacturing.com/industry-news/news/55250428/novo-holdings-completes-165b-acquisition-of-catalent — retrieved 2026-05-31 — grade B
2. The Quest for Oral GLP-1s (semaglutide $70k–100k/kg; Rybelsus ~400 mg SNAC per 7–14 mg dose) — https://www.asimov.press/p/oral-glp1s — retrieved 2026-05-31 — grade C
3. Eli Lilly plans at least $27 billion in new U.S. manufacturing (4 sites; 3 API for tirzepatide; $3.5bn PA injectables) — https://www.cnbc.com/2025/02/26/eli-lilly-to-invest-27-billion-in-new-us-manufacturing.html — retrieved 2026-05-31 — grade B
4. CDMO/CMO Expansion Update: Riding the Strength of TIDES (Bachem >EUR 400M FY25 capex / Building K; PolyPeptide EUR 100M Malmö doubling) — https://www.dcatvci.org/features/cdmo-cmo-expansion-update-riding-the-strength-of-tides/ — retrieved 2026-05-31 — grade C
5. Gerresheimer AG — A Conflicted Acquisition... Key Weight-Loss Driver At Risk (CagriSema dual-chamber syringe, ~EUR 250M 2027, quality issues) — https://www.morpheus-research.com/gerresheimer/ — retrieved 2026-05-31 — grade C
6. Ypsomed spends $248M to gain its first US manufacturing site (Holly Springs NC, operational 2027) — https://endpoints.news/ypsomed-spends-248m-to-gain-its-first-us-manufacturing-site/ — retrieved 2026-05-31 — grade B
7. Disruption Potential of Injectable Anti-Obesity Therapies (≈1.5bn devices/yr for ~30M patients) — https://www.pda.org/pda-letter-portal/home/full-article/disruption-potential-of-injectable-anti-obesity-therapies-and-beyond — retrieved 2026-05-31 — grade C
8. Bachem Group secures CHF 1 billion peptide supply contract (5-yr 2025–2029 take-or-pay) — https://www.s-ge.com/en/article/news/202301-chemicals-bachem-group-secures-chf-1-billion-peptide-supply-contract — retrieved 2026-05-31 — grade B
9. Lilly plans to more than double U.S. manufacturing investment since 2020 exceeding $50 billion (PR Newswire / Lilly IR) — https://www.prnewswire.com/news-releases/lilly-plans-to-more-than-double-us-manufacturing-investment-since-2020-exceeding-50-billion-302385372.html — retrieved 2026-05-31 — grade A
10. THERMO FISHER SCIENTIFIC INC. — Form 8-K FY2025 (sterile fill-finish expansion; $1.5bn US capex; Greenville PFS lines; Ridgefield) — https://www.sec.gov/Archives/edgar/data/0000097745/000009774525000150/q32025earnings8kex99_1.htm — retrieved 2026-05-31 — grade A
11. JPM 2025: Thermo Fisher 'very positive' on sterile demand as Catalent takes capacity out of market (Casper "takes an option off the table") — https://www.pharmaceutical-technology.com/analyst-comment/jpm-2025-thermo-fisher-very-positive-on-sterile-demand-as-catalent-takes-capacity-out-of-market/ — retrieved 2026-05-31 — grade B
12. FDA clarifies policies for compounders as national GLP-1 supply begins to stabilize (shortage resolved dates; 503A/503B enforcement deadlines) — https://www.fda.gov/drugs/drug-alerts-and-statements/fda-clarifies-policies-compounders-national-glp-1-supply-begins-stabilize — retrieved 2026-05-31 — grade A
13. FDA Proposes to Exclude Semaglutide, Tirzepatide, and Liraglutide on 503B Bulks List (30 Apr 2026) — https://www.fda.gov/news-events/press-announcements/fda-proposes-exclude-semaglutide-tirzepatide-and-liraglutide-503b-bulks-list — retrieved 2026-05-31 — grade A
14. Lilly Increases Manufacturing Investment to $9 Billion at Newest Indiana (Lebanon) Site for tirzepatide API — https://investor.lilly.com/news-releases/news-release-details/lilly-increases-manufacturing-investment-9-billion-newest — retrieved 2026-05-31 — grade A
