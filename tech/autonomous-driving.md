---
type: synthesis
domain: tech-trend
tags: [autonomous-driving, robotaxi, lidar, pure-vision, sae-levels, adas]
as_of_timestamp: 2026-05-31T01:15:00+08:00
author_role: researcher
confidence: 0.74
verdict: 結構
rubric: {A1: 2, A2: 2, A3: 2, A4: 1, A5: 1}
sources_grade_summary: "A: 7 B: 4 C: 3 D: 0 E: 0"
---
# 自駕成熟度 — 純視覺 vs Hybrid 的真實裁決 / Autonomous Driving Maturity: Vision vs Hybrid, Adjudicated

## 0. 一句話判決 / Verdict
**結構 (structural, conf 0.74).** The principal's framing — "pure-vision is winning" — conflates *scalable/cheap* with *capable*. By every datable safety metric, the hybrid L4 stack (Waymo) is the only system delivering driverless rides at scale with a peer-reviewed >90% serious-crash reduction; pure-vision (Tesla) only crossed into unsupervised commercial service in Jan-2026, still geofenced and remote-monitored — it is *catching up cheaply*, not "ahead." The "雨天怎麼辦" question is real: cameras are passive and degrade in fog/rain where LiDAR's active ranging does not. The decisive 2025-26 fact: **cheap LiDAR ($200, heading to $100) is collapsing the "vision is cheaper" cost argument** — yet that same collapse bankrupted Luminar, so the sensor is winning while its Western makers are not investable [Sub-$200 Lidar — IEEE Spectrum — retrieved 2026-05-31 — grade C][Luminar buys/Chapter 11 — WardsAuto — retrieved 2026-05-31 — grade B].

## 1. 技術底蘊 / Technical moat (A1) — the core debate
Two architectures, two philosophies. **Pure-vision (Tesla):** 8 cameras + end-to-end neural net, no radar/LiDAR since the 2021 radar deletion; bet is that human-level driving needs only human-equivalent sensing plus superhuman compute/data [Why Tesla walked away from radar/LiDAR — Not a Tesla App — retrieved 2026-05-31 — grade C]. **Hybrid (Waymo, Mercedes):** LiDAR + radar + camera fusion — redundant, geometry-grounded perception that does not depend on inferring 3D from 2D pixels. The physics asymmetry is the crux of "雨天怎麼辦": cameras are *passive* and lose signal in fog/rain/glare/night, whereas LiDAR/radar are *active* and range through conditions cameras cannot [LiDAR vs Tesla — Sustainable Business Mag — retrieved 2026-05-31 — grade C]. Tesla's 2026 mitigation is a software "visibility grid" that labels occluded scenes to suppress phantom braking — and FSD 14.3 *restricts itself to low-aggression modes in rain*, an implicit admission of the weather ceiling [How Tesla Vision sees through weather — Not a Tesla App — retrieved 2026-05-31 — grade C]. **Moat verdict: A1=2.** Both stacks have deep, defensible moats (data+compute vs sensor-fusion+HD-map), but they are *different* moats — not one beating the other.

## 2. 需求真實性 — 數據 / Demand reality (A2)

| 指標 metric | 數值 value | 日期 date | 來源 source (grade) |
|---|---|---|---|
| Waymo paid rides/week | ~500,000 | Q1 2026 | TechCrunch ridership chart (B) |
| Waymo cities (US) | 10–11 operating | 2026 | Waymo Year-in-Review (A) |
| Waymo cumulative autonomous miles | >200M (170M analyzed for safety) | Feb / Mar 2026 | Waymo Safety Impact (A) |
| Waymo annual trips 2025 | >14M (3x vs 2024) | Dec 2025 | Waymo Year-in-Review (A) |
| Tesla Austin robotaxi fleet | ~37–44 cars, ~10 fully unsupervised | Mar 2026 | Basenor / CNBC (B/C) |
| Tesla Austin geofence | 20 → ~245 sq mi | Jun-2025 → Mar-2026 | Basenor (C) |
| Mercedes Drive Pilot (L3 certified) | CA + NV (US); whole Autobahn (DE) | 2023 US / Dec-2024 DE | Mercedes-Benz Group (A) |

The asymmetry is stark: Waymo is doing **half a million paid driverless rides every week across 10+ cities**, having tripled volume in 2025 and targeting 1M/week by end-2026 [TechCrunch — retrieved 2026-05-31 — grade B][Waymo Year-in-Review — retrieved 2026-05-31 — grade A]. Tesla, eleven months after its Jun-2025 Austin launch, runs a *dozens-of-cars* invite-only pilot, ~20% of which finally have no in-car monitor [Musk removes safety supervisors — CNBC — retrieved 2026-05-31 — grade B]. **A2=2** — demand for L4 robotaxi is proven and scaling; vision-only commercial driverless demand is real but two orders of magnitude smaller today.

## 3. 資金與權威背書 / Capital & authority (A3)
**Capital:** Waymo raised a **$16B round in Feb-2026** [Waymo $16B round — Waymo blog — retrieved 2026-05-31 — grade A]. **Authority — the decisive evidence:** Over **170M fully autonomous miles**, the Waymo Driver shows **91–92% fewer serious-injury/fatal crashes**, 82–83% fewer airbag-deployment crashes, and a **Swiss Re reinsurance study** of 25M miles found 92% fewer bodily-injury and 88% fewer property-damage claims vs human drivers — plus a peer-reviewed *Traffic Injury Prevention* paper showing statistically significant pedestrian (92%), cyclist (82%) and motorcyclist (82%) injury reductions [Waymo Safety Impact — retrieved 2026-05-31 — grade A][Swiss Re / 56.7M-mile study — Taylor & Francis — retrieved 2026-05-31 — grade A]. **Regulatory:** Mercedes holds the only consumer **SAE L3** certification — CA + NV in the US, and the *entire 13,191 km German Autobahn at up to 95 km/h* since Dec-2024 [Mercedes 95 km/h — Mercedes-Benz Group — retrieved 2026-05-31 — grade A]. Tesla FSD remains **SAE L2 (supervised)** in private hands; only the Austin robotaxi is operating driverless, with remote operators on standby. **A3=2** — capital and authority overwhelmingly validate the hybrid camp; this is the single biggest crack in the "vision is ahead" echo chamber.

## 4. 供應鏈與可投資節點 / Supply chain & investable nodes (A4)
The investable paradox of 2025-26: **the LiDAR product is winning but the Western LiDAR equities are dying.** Automotive LiDAR market crossed $1B (+60% YoY); Hesai (HSAI) shipped 200k+ units/month, passed 2M cumulative, holds ~43% of long-range ADAS share, and is pushing ASP to **sub-$200** (flagship ATX ~$200) [Hesai No.1 ADAS LiDAR — Hesai — retrieved 2026-05-31 — grade A][Hesai Q1 ASP — AInvest — retrieved 2026-05-31 — grade C]. MicroVision launched a sub-$200 solid-state unit targeting $100 [Sub-$200 Lidar — IEEE Spectrum — retrieved 2026-05-31 — grade C]. **But Luminar (LAZR) was dropped by Volvo (Nov-2025) and filed Chapter 11 (Dec-2025); MicroVision bought its assets for $33M** — a brutal signal that Western LiDAR is being commoditized by Chinese scale [Luminar Chapter 11 / MicroVision $33M — WardsAuto — retrieved 2026-05-31 — grade B]. **Compute SoC** is the cleaner node: NVIDIA DRIVE Thor (2,000 TOPS) powers Mercedes city-driving (late-2026), Lucid, Volvo trucks, and an Uber robotaxi tie-up; Tesla keeps compute in-house (AI5) [NVIDIA Uber robotaxi / Thor — NVIDIA — retrieved 2026-05-31 — grade A]. **A4=1** — chokepoints exist but the marquee LiDAR pure-plays are value traps; compute (NVDA) and Chinese verticals are the durable nodes.

## 5. 大模型 vs 小模型 / Model angle
Both camps are converging on **end-to-end neural nets and world models**. Tesla's FSD is the canonical end-to-end vision policy. NVIDIA's 2026 DRIVE stack ships "Alpamayo" reasoning/world models for L4 [NVIDIA DRIVE AV / Alpamayo — TechEBlog — retrieved 2026-05-31 — grade C]. The model layer is where vision and hybrid *re-converge*: a world model can fuse LiDAR+camera+radar tokens identically. This ties directly to [[model-leadership-and-data]] — whoever owns the largest fleet data + best world-model training wins the *policy*, regardless of sensor suite. The sensor debate is increasingly a cost/redundancy question layered under a shared model architecture.

## 6. 顛覆 / 取代向量 / Disruption vector (A5)
Robotaxi unit economics, not tech, gate the disruption. Waymo's path to profit hinges on cost/mile (vehicle hardware ~$100k+ historically, falling) vs a human-driver TNC. Cheap LiDAR ($200 vs prior $1k+) plus cheaper compute materially improves the hybrid economics — undercutting the historical "vision is the only scalable path" claim. Tesla's disruption thesis (millions of consumer cars flipping to a robotaxi network overnight) remains a **dated projection**: as of 2026-05 it is dozens of geofenced, remote-monitored Model Ys in one city, not a fleet flip. **A5=1** — disruption is real and datable for Waymo's *city-by-city* expansion, but the mass-market "vision flips the installed base" vector is still announced, not delivered.

## 7. 同溫層風險 + 空方論點 / Echo-chamber flags + bear case
**Echo-chamber gap:** Retail/X consensus equates "Tesla pure-vision is winning" with technical superiority. The DATA says otherwise — Waymo logs 170M driverless miles with peer-reviewed/insurer-validated safety; Tesla logged **zero** autonomous miles in California's 2025 disengagement report (it tests under L2, exempt) and runs a dozens-of-cars pilot [CA DMV 2025 disengagement — DMV / TechCrunch — retrieved 2026-05-31 — grade A]. Vision is *cheaper and more scalable in principle*, not *more capable today*. **Bear cases:** (1) Robotaxi unit economics may never beat low-cost human TNC at city scale — Waymo still unprofitable. (2) Western LiDAR is a value trap (Luminar BK; Innoviz fragile) even as the part wins — Chinese (Hesai/Huawei) capture the margin. (3) Tesla robotaxi timeline is a serial slip; "unsupervised" still means remote operators on standby. (4) L3 liability (Mercedes assumes liability hands-off) is a legal moat *and* a scaling brake — strict ODD (clear weather, daylight, ≤40 mph US) keeps it niche. (5) Disengagement reports are non-comparable across firms — beware over-reading any single metric.

## 8. 跨主題綜效 / Cross-synergies
- [[ai-edge-devices]] — robotaxi/L3 is the highest-value automotive *edge compute* socket; NVIDIA Thor / Qualcomm Ride / Tesla AI5 are edge inference at 1,000+ TOPS in-vehicle.
- [[model-leadership-and-data]] — end-to-end driving policies and world models make fleet data the real moat; sensor choice is increasingly subordinate to the model + data flywheel.
- [[optical-interconnect-cpo]] — indirect: robotaxi/AV training compute drives the same datacenter buildout.

## Sources
1. Waymo 2025 Year in Review — https://waymo.com/blog/2025/12/2025-year-in-review/ — retrieved 2026-05-31 — grade A
2. Waymo Safety Impact (170M miles, 91-92% crash reduction, Swiss Re) — https://waymo.com/safety/impact/ — retrieved 2026-05-31 — grade A
3. Waymo raises $16B investment round — https://waymo.com/blog/2026/02/waymo-raises-usd16-billion-investment-round/ — retrieved 2026-05-31 — grade A
4. Comparison of Waymo Rider-Only crash rates (peer-reviewed, Traffic Injury Prevention) — https://www.tandfonline.com/doi/full/10.1080/15389588.2025.2499887 — retrieved 2026-05-31 — grade A
5. Waymo skyrocketing ridership (500k rides/week) — https://techcrunch.com/2026/03/27/waymo-skyrocketing-ridership-in-one-chart/ — retrieved 2026-05-31 — grade B
6. Mercedes-Benz increases L3 top speed to 95 km/h (Autobahn) — https://group.mercedes-benz.com/innovations/product-innovation/autonomous-driving/drive-pilot-95-kmh.html — retrieved 2026-05-31 — grade A
7. Mercedes-Benz DRIVE PILOT California certification — https://group.mercedes-benz.com/innovation/product-innovation/autonomous-driving/drive-pilot-california.html — retrieved 2026-05-31 — grade A
8. Musk removes safety supervisors from some Austin robotaxis — https://www.cnbc.com/2026/01/22/musk-says-tesla-takes-safety-supervisors-out-of-some-austin-robotaxis.html — retrieved 2026-05-31 — grade B
9. Tesla Robotaxi Austin: 20% without safety monitor / geofence 245 sq mi — https://www.basenor.com/blogs/news/tesla-robotaxi-austin-20-now-running-without-safety-monitor — retrieved 2026-05-31 — grade C
10. CA DMV 9M test miles / Waymo 68% VMT, Tesla zero autonomous miles — https://www.dmv.ca.gov/portal/news-and-media/autonomous-vehicle-permit-holders-in-california-logged-more-than-9-million-test-miles-between-december-1-2024-and-november-30-2025/ — retrieved 2026-05-31 — grade A
11. AV testing dropped 50% / Tesla not reporting — https://techcrunch.com/2025/01/31/autonomous-vehicle-testing-in-california-dropped-50-heres-why/ — retrieved 2026-05-31 — grade B
12. Hesai No.1 long-range ADAS LiDAR 2025 (43% share, 2M units) — https://www.hesaitech.com/hesai-secures-no-1-in-long-range-adas-lidar-shipments-in-2025-by-yole-group/ — retrieved 2026-05-31 — grade A
13. Hesai Q1 ASP / ATX ~$200 sub-$200 push — https://www.ainvest.com/news/hesai-q1-2025-unpacking-key-contradictions-adas-lidar-asp-margins-capacity-expansion-2505/ — retrieved 2026-05-31 — grade C
14. Sub-$200 LiDAR / MicroVision $100 target — https://spectrum.ieee.org/solid-state-lidar-microvision-adas — retrieved 2026-05-31 — grade C
15. MicroVision buys Luminar assets $33M (Luminar Chapter 11, Volvo drop) — https://www.wardsauto.com/news/microvision-buys-assets-of-troubled-lidar-maker-luminar-for-33m/811377/ — retrieved 2026-05-31 — grade B
16. NVIDIA makes world robotaxi-ready (Uber, Thor) — https://nvidianews.nvidia.com/news/nvidia-uber-robotaxi — retrieved 2026-05-31 — grade A
17. NVIDIA DRIVE AV stack + Alpamayo world models — https://www.techeblog.com/nvidia-self-driving-car-drive-av-stack-alpamayo/ — retrieved 2026-05-31 — grade C
18. Why Tesla walked away from radar/LiDAR (vision-only) — https://www.notateslaapp.com/news/3077/why-tesla-walked-away-from-radar-and-lidar-to-go-all-in-on-vision — retrieved 2026-05-31 — grade C
19. How Tesla Vision sees through weather (FSD 14.3 rain restriction) — https://www.notateslaapp.com/news/4162/how-tesla-vision-sees-through-inclement-weather — retrieved 2026-05-31 — grade C
20. China ADAS supplier rankings (BYD 13.2%, Huawei LiDAR 41.5%) — https://autonews.gasgoo.com/articles/market-industry/rankings-of-adas-component-suppliers-in-china-jan-dec-2025-lidar-market-su[redacted-acct]525657333761 — retrieved 2026-05-31 — grade C

