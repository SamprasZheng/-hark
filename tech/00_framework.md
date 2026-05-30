---
type: synthesis
domain: tech-trend
tags: [framework, rubric, due-diligence, anti-echo-chamber, screening]
as_of_timestamp: 2026-05-31T01:15:00+08:00
author_role: researcher
status: live
schema_version: 1
---

# tech/ — 科技趨勢盡職調查框架 (質變 vs 同溫層)

`tech/` is the **technology due-diligence layer** of the Sharks system. It sits *upstream* of the investment layer: the principal's question here is not "what do I buy" but —

> **"Which of these hot narratives is a real 質變 (qualitative change) backed by data, capital and authority — and which is just my 同溫層 (echo chamber)?"**

Each trend page scores one narrative on the rubric below, actively hunts the bear case, and maps the investable chokepoint **only if** demand is shown to be real. The pages feed [[scoreboard]] (the scored matrix) and [[99_cross_synthesis]] (cross-trend 綜效 + the culture→supply-chain map).

This layer obeys the same constitution as the rest of `$hark`: point-in-time `as_of_timestamp` ([[../philosophy/09-point-in-time]]), A–E source grading ([[../CLAUDE]] §5), clinical/falsifiable tone, **no buy/sell advice**. It harmonises with the daily 5-dimension evidence gate ([[../philosophy/concepts/evidence-gated-rebalance]] — 消息 / 資金 / 交易量 / 進出口 / 營利): a trend's *demand-reality* axis is the 營利+交易量 view; its *capital & authority* axis is the 資金+消息 view.

## The anti-echo-chamber doctrine

A narrative counts **only when hard data backs it.** For every trend we separately hunt three evidence classes and weight them *above* story:

1. **Capital** — capex / VC / M&A / order-book dollars. Who is putting real money in.
2. **Adoption** — units shipped, DAU/MAU, revenue, attach rates. **Not** survey-intent.
3. **Authority** — regulators, primary filings, Nobel committees, standards bodies, tier-1 sell-side.

Every page must name its **echo-chamber gap**: the precise place where the narrative currently outruns the data. That gap *is* the falsifier the principal watches. The opposite failure — dismissing a real 質變 because it is unfamiliar — is guarded against by forcing the capital+authority hunt even on narratives the desk instinctively distrusts.

## The 5-axis 質變 rubric (each scored 0 / 1 / 2)

| Axis | Question | 0 → 1 → 2 |
|---|---|---|
| **A1 技術底蘊** Technical moat | a real, hard-to-replicate physical/architectural step-change? | marketing → real-but-replicable → durable moat |
| **A2 需求真實性** Demand reality | units, revenue, capex — not intent | narrative → early real revenue → accelerating P&L |
| **A3 資金·權威** Capital & authority | capital flows + regulatory/Nobel/primary backing | KOL-only → some institutional → heavy capital + authority |
| **A4 供應鏈可投資性** Investability | identifiable bottleneck with listed exposure | none → diffuse → clear chokepoint pure-play |
| **A5 顛覆向量** Disruption vector | replaces a market / unstoppable, on a datable timeline | far/speculative → partial-slow → imminent structural |

**Verdict taxonomy** (sum out of 10):

- **質變** — real qualitative change, data-backed (typically A2+A3 ≥ 3 and total ≥ 7). Where the principal wants to be *early*.
- **結構** — real and structural but largely priced-in; own the chokepoint, not the story.
- **過熱** — narrative outruns data; high echo-chamber risk (the 同溫層 trap). Cross-checks [[../wiki/07_ai_bubble_audit]] `bubble_guard`.
- **太早** — technically real but no near-term P&L or datable timeline (the `$hark` "no revenue before 20XX" bucket — see [[../wiki/16_rally_themes_and_coverage_audit]] §4).

A verdict is **not** a recommendation. It is a screen output that the Risk Officer and the daily rubric ([[../philosophy/05-decision-rubric]]) consume under the usual position/concentration caps.

## Trend registry — Phase A (2026-05-31)

| Page | Trend | Principal's framing |
|---|---|---|
| [[memory-supercycle]] | HBM / DRAM / NAND shortage | 記憶體短缺 MU/Hynix/Samsung 暴漲 |
| [[optical-interconnect-cpo]] | CPO / silicon photonics vs PCB·載板·copper | CPO 若快很多，PCB 載板無法比? |
| [[ai-edge-devices]] | AI PC / NB / iPhone / Vision Pro | 端側 AI、換機潮真假 |
| [[autonomous-driving]] | Waymo vs Tesla vs Benz | 純視覺 vs hybrid、雨天怎麼辦 |
| [[ai-pharma-glp1]] | AI drug discovery + FDA; GLP-1 | AI 新藥需 FDA；減肥藥年輕人火 |
| [[quantum-vs-bitcoin]] | Quantum threat to BTC + PQC | 量子破解比特幣? |
| [[ai-eats-software]] | Does AI collapse SaaS equities? | AI 讓軟體股崩潰? |
| [[model-leadership-and-data]] | 大模型 vs 小模型; mass-data vs leaderboard; Nobel | 領先者是誰、數據是否反映、諾貝爾方向 |
| [[youth-culture-shifts]] | 外送/Uber, social ubiquity, youth health | 文化生活型態質變 → 科技需求 |

See [[scoreboard]] for the scored matrix and [[99_cross_synthesis]] for the cross-trend 綜效 lattice and the culture→demand→supply-chain map.

## See also

- [[../wiki/07_ai_bubble_audit]] — the late-cycle bubble guard these verdicts are stress-tested against
- [[../wiki/16_rally_themes_and_coverage_audit]] — existing rally-theme coverage + the "do not chase" warnings
- [[../watchlist/serenity-supply-chain]] — the CPO / HBM / passives supply-chain ticker map
- [[../philosophy/concepts/supply-chain-bottleneck]] — the alpha-source framework (pick-and-shovel, pricing power)
- [[../philosophy/concepts/evidence-gated-rebalance]] — the 十足的證據 discipline this layer feeds
