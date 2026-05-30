---
type: synthesis
domain: tech-trend
tags: [quantum-computing, post-quantum-crypto, bitcoin, nist-pqc, echo-chamber]
as_of_timestamp: 2026-05-31T01:15:00+08:00
author_role: researcher
confidence: 0.78
verdict: 太早
rubric: {A1: 2, A2: 1, A3: 2, A4: 1, A5: 1}
sources_grade_summary: "A: 7 B: 5 C: 3 D: 1 E: 0"
---
# 量子運算 vs 比特幣 + PQC 遷移 / Quantum vs Bitcoin and the PQC Migration

## 0. 一句話判決 / Verdict
- **"量子電腦即將破解比特幣?" → 太早 (echo-chamber).** The largest *real* quantum attack on elliptic-curve crypto to date is a **15-bit** key (April 2026); Bitcoin's secp256k1 is **256-bit**, and the difficulty scales exponentially. Authority-backed median "Q-Day" is **2033** (range 2030–2042). This is multi-year-to-decade, not imminent. [1][7]
- **"PQC 遷移是真的嗎?" → 結構 (real, but diffuse).** NIST finalized FIPS-203/204/205 in **Aug 2024**; "harvest-now-decrypt-later" + federal mandates (CNSA 2.0 → 2035) make migration a genuine multi-year enterprise spend — but it is hard to monetise as a pure-play. [4][9]

## 1. 技術底蘊 / Technical moat (A1)
The core distinction the hype erases: **logical vs physical qubits**. Breaking secp256k1 via Shor needs ~**2,330 logical qubits** (Roetteler 2017). [5] But each *logical* qubit requires hundreds-to-thousands of error-corrected *physical* qubits. Webber et al. (2022) mapped this to **~13 million physical qubits to break secp256k1 in 24h, ~317M for 1h** at 0.1% gate error. [5] Today's best chip — **Google Willow (Dec-2024)** — has **105 physical qubits** and just crossed the *below-threshold* milestone, the first proof that adding qubits *lowers* logical error. But its logical error is still **~0.14%/cycle**, ~3-4 orders of magnitude above the ~10⁻⁶ needed for deep algorithms; demos remain quantum *memory*, not fault-tolerant logic gates. [2] The honest 2025 *downward* revision (Gidney/Google) cut **RSA-2048** to **<1M physical qubits / 1,399 logical** (20× below his 2019 20M estimate) — but the paper explicitly does **not** claim buildability and assumes a 1M-qubit machine that does not exist; even <1M is ~10,000× today's hardware. [3]

## 2. 需求真實性 — 數據 / Demand reality (A2)
| 指標 | 數值 | 日期 | 來源(grade) |
|---|---|---|---|
| Largest real quantum ECC break | **15-bit** key (vs 256-bit needed) | Apr 2026 | [1] A |
| Best chip physical qubits (Willow) | **105** | Dec 2024 | [2] A |
| Willow logical error / cycle | ~0.14% (need ~10⁻⁶) | Dec 2024 | [2] A |
| Logical qubits to break secp256k1 | ~2,330 | 2017 | [5] A |
| Physical qubits to break secp256k1 (24h) | ~13,000,000 | 2022 | [5] A |
| Gidney RSA-2048 (revised down) | <1,000,000 physical / 1,399 logical | May 2025 | [3] A |
| IBM fault-tolerant target (Starling, 200 logical) | 2029 | 2025 | [6] A |
| Authority Q-Day baseline (CRQC) | **2033** (2030–2042) | 2026 | [7] B |

The "demand" for a Bitcoin-breaking machine is a *future projection*, not a current market. The gap between 105 physical qubits and 13M is the whole story.

## 3. 資金與權威背書 / Capital & authority (A3)
Authority weight sits with **NIST** (8-year process; FIPS-203 ML-KEM, FIPS-204 ML-DSA, FIPS-205 SLH-DSA finalized 2024-08-13) and **NSA CNSA 2.0** (national-security systems migrated by 2035; new-equipment compliance from 2027). [4][9] Capital is real on the *defensive* side: every federal agency + contractor must migrate, yet **<5% of firms have started**. [9] On hardware, **IBM** committed a dated roadmap to a fault-tolerant Starling by **2029** (200 logical qubits / 100M gates), with Nighthawk (120 qubits) in 2026 — credible engineering, but pre-revenue at scale. [6] Google/Caltech 2026 papers keep cutting resource estimates (Google <500k physical qubits; a Caltech/neutral-atom paper floated ~10,000 — heavily caveated, architecture-dependent, not peer-validated as buildable). [7]

## 4. 供應鏈與可投資節點 / Supply chain & investable nodes (A4)
This **reconciles directly with $hark's existing warning** — see [[../wiki/16_rally_themes_and_coverage_audit]] §4: "量子計算商業化 — 2030 前無營收; QBTS/QUBT/RGTI 純敘事." The 2026 financials confirm it:
- **IONQ**: Q4-25 rev $61.9M; 2026 guide $225–245M (first pure-play >$100M GAAP rev). But Q3-25 **GAAP net loss ~$1.1B** (dominated by *non-cash* warrant remeasurement), adj-EBITDA loss $48.9M; ~$19B market cap = pure narrative multiple. [8]
- **RGTI (Rigetti)**: 2025 rev **$7.1M** (−34% YoY), net loss **$216M**. [8]
- **QBTS (D-Wave)**: 2025 rev **$24.6M** (+179%), but annealing ≠ Shor-capable gate QC; ~$885M cash cushion. [8]
- **QUBT**: micro-revenue, narrative-only (per $hark audit). [10]
PQC-exposed *incumbents* (cybersecurity: PQShield/Entrust private; listed names like crypto-agility vendors) are the more defensible — but PQC is a feature bundled into existing security stacks, **not a pure-play TAM**. Investable conclusion: hardware = lottery ticket with no near-term revenue; PQC = diffuse margin uplift for incumbents.

## 5. 大模型 vs 小模型 / Model angle
N/A in the LLM sense. Quantum-classical note: near-term value is *hybrid* (annealing/optimization, e.g. D-Wave) and **classical** post-quantum math (lattice-based ML-KEM/ML-DSA) — software, not qubits. The frontier-compute *narrative* overlaps the AI compute story (see synergies).

## 6. 顛覆 / 取代向量 / Disruption vector (A5)
Realistic timeline to a **cryptographically-relevant quantum computer (CRQC)**: authority baseline **2033**, optimistic 2030, pessimistic 2042. [7] Even at Q-Day, Bitcoin's exposure is *partial and mitigable*: ~**4M BTC (~25% supply)** sit in quantum-vulnerable form — ~2M in original **P2PK** outputs (Satoshi-era) + ~2.5M in **reused P2PKH** with exposed public keys; Glassnode puts total exposed nearer **6M BTC**. [11] Funds in *unused* modern addresses (hashed pubkey) are only exposed in the ~10-min window between spend-broadcast and confirmation. The live mitigation is the **BIP-360 / QRAMP** debate: a proposed 5-year sunset that would **freeze** un-migrated vulnerable coins (Lopp: "least-worst" vs legitimising theft) vs Adam Back's optional-upgrade camp — comment threads ~95% against forced freeze. [12] Disruption vector is therefore *slow and governable*, not a sudden break.

## 7. 同溫層風險 + 空方論點 / Echo-chamber flags + bear case
**Echo-chamber gap (large):** crypto-Twitter/KOL framing = "Q-Day breaks BTC soon / IONQ to the moon"; the AUTHORITY + peer-reviewed reality = 105 physical qubits vs 13M needed, a 15-bit real break vs 256-bit, Q-Day ~2033. The gap is the difference between a *headline-friendly logical-qubit count* and the *physical-qubit + error-correction tax*. Vendors (and some 2026 press) amplify each downward resource-estimate paper as if buildable now — they are dated projections. **Bear case on the trade:** (a) IONQ/RGTI/QBTS burn cash with sub-$250M revenue against multi-billion caps → multiple compression risk; (b) if PQC migrates *before* CRQC (the likely order), the "BTC breaks" thesis never pays; (c) Bitcoin can soft-fork to PQC signatures, neutralising the catalyst. **Bull tail:** any surprise jump in logical-gate fidelity or a validated neutral-atom shortcut compresses the timeline — low probability, high impact.

## 8. 跨主題綜效 / Cross-synergies
- [[model-leadership-and-data]] — shared "compute-frontier / Q-Day" narrative cycle; both prone to logical-vs-physical-style hype inflation.
- [[../wiki/16_rally_themes_and_coverage_audit]] §4 — pre-existing $hark "do-not-chase quantum" call (this note confirms & sources it).
- [[memory-supercycle]] / [[optical-interconnect-cpo]] — quantum control electronics ride the same advanced-packaging/cryo supply chain at the margin.

## Sources
1. Researcher wins 1 BTC for largest quantum attack on elliptic curve (15-bit) — https://www.coindesk.com/tech/2026/04/24/researcher-wins-1-bitcoin-bounty-for-largest-quantum-attack-on-underlying-tech — retrieved 2026-05-31 — grade B
2. Google "Quantum error correction below the surface code threshold" (Willow, 105 qubits) — https://www.nature.com/articles/d41586-024-04028-3 — retrieved 2026-05-31 — grade A
3. Gidney, "How to factor 2048-bit RSA integers with less than a million noisy qubits" — https://arxiv.org/abs/2505.15917 — retrieved 2026-05-31 — grade A
4. NIST releases first 3 finalized PQC standards (FIPS-203/204/205) — https://www.nist.gov/news-events/news/2024/08/nist-releases-first-3-finalized-post-quantum-encryption-standards — retrieved 2026-05-31 — grade A
5. Resource estimates secp256k1 (Roetteler 2017 logical; Webber 2022 physical) — https://postquantum.com/post-quantum/quantum-cryptocurrencies-bitcoin/ — retrieved 2026-05-31 — grade C
6. IBM lays out path to fault-tolerant quantum computing (Starling 2029, 200 logical) — https://www.ibm.com/quantum/blog/large-scale-ftqc — retrieved 2026-05-31 — grade A
7. Project Eleven "Quantum Threat to Blockchains 2026" — Q-Day baseline 2033 — https://www.prnewswire.com/news-releases/project-eleven-publishes-quantum-report-with-q-day-baseline-scenario-in-2033-302764188.html — retrieved 2026-05-31 — grade B
8. Quantum earnings Q4/FY25: IonQ, D-Wave, Rigetti — https://www.datacenterdynamics.com/en/news/quantum-computing-earnings-q4-and-fy25-ionq-d-wave-rigetti-results/ — retrieved 2026-05-31 — grade B
9. CNSA 2.0 & NIST PQC deadlines 2026–2035; <5% started — https://www.entrust.com/resources/learn/what-is-cnsa-2-0 — retrieved 2026-05-31 — grade B
10. $hark internal coverage audit §4 (quantum = no revenue pre-2030, pure narrative) — D:/DOT/$hark/wiki/16_rally_themes_and_coverage_audit.md — retrieved 2026-05-31 — grade A
11. Deloitte: ~4M BTC (~25%) quantum-vulnerable (P2PK + reused P2PKH); Glassnode ~6M — https://www.deloitte.com/nl/en/services/consulting-risk/perspectives/quantum-computers-and-the-bitcoin-blockchain.html — retrieved 2026-05-31 — grade C
12. BIP-360/QRAMP coin-freeze debate (Lopp vs Adam Back) — https://www.coindesk.com/tech/2026/04/16/bitcoin-s-quantum-debate-splits-as-adam-back-pushes-optional-upgrades-over-forced-freeze — retrieved 2026-05-31 — grade B
13. IonQ Q3-25 8-K (net loss driven by non-cash warrant remeasurement) — https://www.sec.gov/Archives/edgar/data/0001824920/000095017025104021/ionq-ex99_1.htm — retrieved 2026-05-31 — grade A
