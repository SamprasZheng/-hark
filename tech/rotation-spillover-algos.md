---
type: synthesis
domain: method
tags: [trading-algorithms, sector-rotation, lead-lag, spillover, momentum, statarb, factor-timing, regime-switching, flow, network-propagation, semiconductor, granger]
as_of_timestamp: 2026-05-31T06:00:00+08:00
author_role: researcher
status: live
schema_version: 1
---

# Rotation / Spillover 交易演算法地圖 / Algorithm Families for Trend, Rotation & Liquidity-Spillover Alpha

**Research/educational only — not buy/sell advice. Point-in-time 2026-05-31.** The principal asks 「有什麼交易演算法可以參考」for趨勢追蹤 / 板塊輪動 / **流動性外溢**, with a specific thesis: *流動性集中在半導體，是否外溢、從哪個產業開始傳導*. This surveys eight algorithm families, separates **measured/replicated edge from decayed folklore**, and ends with a concrete semis-spillover detector mapped to existing `$hark` modules.

## §0. 一句話 + algo map

**One line:** The replicated edges that fit the principal's question are (a) **economic-link / lead-lag cross-predictability** (supplier follows customer with a lag — Cohen-Frazzini ~150bp/mo, Lee tech-links ~117bp/mo) and (b) **directional spillover networks** (Diebold-Yilmaz: who is net *transmitter*); cross-sectional sector-momentum *chasing* is largely noise at the quarter horizon (our own [[../philosophy/concepts/hotspot-sector-rotation]] measured IC_IR 0.52) and TS-momentum has decayed under crowding.

| # | Family | Core edge | Real or decayed (2026) | OSS / paper |
|---|---|---|---|---|
| 1 | XS + TS momentum / rotation | trend persistence 1–12m | **decaying** (crowded; sector-XS ≈ noise) | `vectorbt`, Jegadeesh-Titman 1993, Moskowitz-Ooi-Pedersen 2012 |
| 2 | **Lead-lag / spillover** | gradual diffusion across linked firms | **real, partly persistent** | `statsmodels` Granger, `PyIF`/`pyinform` TE, Cohen-Frazzini 2008 |
| 3 | StatArb / pairs / cointegration | residual mean-reversion | **decayed** (pairs); residual-OU survives | `arbitragelab`, Avellaneda-Lee 2010 |
| 4 | Factor momentum / timing | factor autocorrelation | **real**, subsumes stock momentum | Ehsani-Linnainmaa 2022 |
| 5 | Regime-switching / change-point | rotate models by state | **real as a gate**, not alpha | `hmmlearn`, `ruptures`, Bai-Perron 1998 |
| 6 | Flow-based (ETF / dealer-gamma) | non-fundamental demand pressure | **real but short-lived + reverses** | SqueezeMetrics GEX/DIX, Ben-David-Franzoni 2018 |
| 7 | Attention / sentiment | retail attention → pressure | **real, ~2wk then reverses** | Google Trends, Da-Engelberg-Gao 2011 |
| 8 | Graph / network propagation | spillover on supply-chain graph | **emerging, promising** | `networkx`, Li-Ferreira 2025 (network momentum) |

## §1. Cross-sectional + time-series momentum

**Core:** XS momentum buys past winners / sells losers (Jegadeesh-Titman 1993); TS momentum trades each asset on its own trailing sign (Moskowitz-Ooi-Pedersen 2012 — past 12m predicts next month, then partially reverses); dual-momentum (Antonacci) layers an absolute filter on a relative pick. **Edge:** under-reaction to slow-diffusing news. **Data:** monthly closes — trivial. **Decay/pitfalls:** TSMOM risk-adjusted returns fell ~87% from 1995-2000 to 2018-2023 (crowding); GEM is specification-fragile (hundreds-of-bp gaps between implementations). Crucially, our own walk-forward ([[../philosophy/concepts/hotspot-sector-rotation]]) found **sector-momentum persistence ≈ noise (IC_IR 0.52)** while seasonality carries the edge (2.78). **OSS:** `vectorbt`, `zipline-reloaded`, QuantConnect.

## §2. LEAD-LAG / SPILLOVER (the principal's core)

This is the family that *directly* answers「外溢、從哪個產業傳導」. The unifying theory is **Hong-Stein 1999 gradual information diffusion**: news reaches "newswatchers" in one segment before it is priced into economically-linked names, so the laggard is predictable.

- **Customer-supplier momentum** — Cohen-Frazzini 2008: buy the *supplier* after a positive shock to its *customer*; long-short ~**150bp/mo alpha**, Smith-Breeden prize. Effect strongest where investor attention is low.
- **Supply-chain cross-predictability** — Menzly-Ozbas 2010: supplier and customer *industries* cross-predict; magnitude **declines with analyst coverage / institutional ownership** (i.e. the edge lives in under-covered names).
- **Technological links** — Lee-Sun-Wang-Zhang 2019: firms sharing a patent/tech space cross-predict, ~**117bp/mo**, distinct from industry momentum, strongest for low-attention, hard-to-arbitrage focal firms.
- **Industry momentum** — Moskowitz-Grinblatt 1999: much of single-stock momentum is *industry* momentum.
- **Granger causality / transfer entropy / lead-lag networks** — directional tests of who-moves-first; transfer entropy (TE) is the model-free, non-linear generalisation of Granger (captures non-linear + asymmetric flow). Diebold-Yilmaz 2012/2014 turns a VAR's forecast-error-variance decomposition into a **directed, weighted spillover network** identifying net *transmitters* vs *receivers* — the formal version of "which sector starts the transmission."

**Real or decayed?** The link-momentum effects are among the *more durable* anomalies (grounded in attention frictions, not a risk premium), but the original magnitudes shrink in liquid, high-coverage mega-caps — so apply them to the *second-tier* names around the leader, not NVDA itself. **Data:** a customer-supplier or tech-link map (10-K Item 1 customers, FactSet Revere, patent classes) + daily returns. **OSS:** `statsmodels.tsa.stattools.grangercausalitytests`, `PyIF` / `pyinform` (transfer entropy), `networkx` for the directed graph; Diebold-Yilmaz via the `frequencyConnectedness` R package or a VAR in `statsmodels`.

## §3. Statistical arbitrage / pairs / cointegration

**Core:** trade the residual of a mean-reverting spread. Gatev-Goetzmann-Rouwenhorst 2006 (distance pairs) reported ~11%/yr 1962-2002, but **the simple distance rule has largely decayed post-publication** (crowding + faster arbitrage). Avellaneda-Lee 2010 generalised to **PCA/ETF factor residuals modelled as Ornstein-Uhlenbeck** (contrarian s-scores) — residual-mean-reversion survives better than naïve pairs. **Data:** clean daily prices, 60d window, ~10bp round-trip. **Pitfalls:** regime breaks snap cointegration; this is mean-reversion, *opposite* to the trend/spillover families — use it for a relative-value leg, not to catch a rotation's start. **OSS:** `hudson-and-thames/arbitragelab` (distance/cointegration/PCA/OU), `statsmodels` (Engle-Granger / Johansen).

## §4. Factor momentum & factor timing

**Core:** Ehsani-Linnainmaa 2022 — most factors are *positively autocorrelated* (avg factor earns 6bp after a losing year vs 51bp after a winning year); **factor momentum subsumes individual-stock momentum** ("momentum is not a distinct factor — it times other factors"). **Edge:** persistence in factor returns, concentrated in high-eigenvalue PCs. **Real?** Yes — one of the better-replicated recent results. **Data:** a factor-return panel (value/quality/low-vol/sector). **Pitfall:** crashes exactly when factor autocorrelations break (regime turns) — pair with §5. **OSS:** build on Fama-French/AQR factor data; `qlib` for the ML pipeline.

## §5. Regime-switching / change-point

**Core:** detect the market *state* (bull/bear/turbulent) and rotate models. **HMM** (`hmmlearn`) infers latent regimes from returns+vol; **Bai-Perron 1998** tests for multiple structural breaks in mean/variance; online change-point via `ruptures`. Regime-switching factor investing (e.g. switch a leveraged value model → market-neutral in downturns) improves risk-adjusted metrics. **Real?** As a **gate/timer** yes; as standalone alpha, weak and prone to lag. **Data:** index returns, realised vol, macro-uncertainty. **Pitfall:** regimes are labelled *after* the break; avoid lookahead. This is the natural home for the [[../philosophy/concepts/liquidity-fishbowl]] `L`-score and [[../philosophy/concepts/hotspot-sector-rotation]]'s seasonality-vs-momentum switch. **OSS:** `hmmlearn`, `statsmodels` Markov-switching, `ruptures`.

## §6. Flow-based (ETF flows, dealer/gamma positioning)

**Core:** trade the price impact of *non-fundamental* demand. Ben-David-Franzoni-Moussawi 2018: ETF flows forecast returns that **reverse within ~5 days** (38% of the move is transient pressure), strongest in leveraged/high-activity ETFs. Dealer **gamma exposure (GEX)**: positive-gamma dealers suppress vol (buy dips/sell rips), negative-gamma amplify moves — SqueezeMetrics/SpotGamma publish daily SPX GEX + DIX (dark-pool). **Real?** Yes but **short-horizon and mean-reverting** — a timing/risk overlay, not a rotation-discovery tool. **Data:** ETF creation/redemption, options open-interest by strike. **Pitfall:** flow-chasing into the reversal is the classic retail blowup. **OSS:** SqueezeMetrics DIX/GEX, `optionsdx`.

## §7. Attention / sentiment

**Core:** Da-Engelberg-Gao 2011 — Google Search Volume Index proxies *retail attention*; a spike predicts higher prices over ~2 weeks **then reverses within the year** (temporary price pressure). **Edge:** attention-driven demand. **Real?** Replicated, but the signal is *pressure-then-reversal*, not durable trend — and attention is precisely the variable that *kills* the lead-lag edge (§2 effects vanish in high-attention names). So attention is best used **inversely**: hunt un-crowded alpha where attention is *low* but link-momentum says a move is coming. Cross-refs `src/sharks/scoring/news_sentiment.py` and [[../philosophy/concepts/price-volume-divergence]]. **Data:** Google Trends, news/social counts. **OSS:** `pytrends`, the `$hark` news-sentiment scorer.

## §8. Graph / network propagation on a supply-chain graph

**Core:** put names on a directed graph (edges = supplier/customer/tech links or estimated lead-lag) and **propagate** a shock outward — §2 generalised to the whole network. Li-Ferreira 2025 ("network momentum"): learn a sparse adjacency matrix from lead-lag (signature Lévy-area + DTW), then trade momentum *spillover* across the graph — net Sharpe ~0.35 vs 0.28 MACD on 28 futures, **with lower turnover**. Diebold-Yilmaz variance-decomposition networks (§2) give the directed transmitter/receiver edges directly. **Real?** Emerging but promising — *exactly* the right abstraction for the principal's question. **Data:** an adjacency matrix (supply-chain map or estimated lead-lag) + returns. **OSS:** `networkx` (graph + centrality), `statsmodels` VAR for edges; optional `torch-geometric` for GNN variants.

## §9. 直接回答：半導體外溢偵測 (semis → which sector next + detect the start)

The principal's thesis has empirical support: **SOX leads** — its turns precede the broader IT sector / Nasdaq-100 by ~1–2 quarters and lead global chip revenue by ~3 quarters (~0.86 corr); the transmission map is **hyperscaler capex → semis (SOX moves first) → memory/storage → optical/networking → power/industrial equipment → broad tech breadth**. A detection stack, all PIT:

1. **Confirm semis as the source node** — `sector_flow.detect_rotation`: is SOXX in `leaders` *and* `rotating_in` (short-RS > long-RS)? That establishes liquidity concentration.
2. **Lead-lag edges out of semis** — run **Granger / transfer-entropy** (§2) from `SOXX` returns onto candidate sector ETFs (XLI, XLU/power, XLB, optical & networking proxies, downstream XLK names). The sectors where `SOXX → X` is significant *and X has not yet moved* are the **next-transmission candidates**. Build the directed graph with `networkx`; rank by Diebold-Yilmaz net *from-SOXX* directional spillover.
3. **Supplier-link confirmation** — for individual transmission (not just sector ETFs), apply Cohen-Frazzini/Lee tech-link logic inside [[../philosophy/concepts/chip-flow-single-point-breakout]]: a positive shock at the chip leader predicts the *under-covered* supplier/adjacent name with a lag.
4. **Detect the *start*, not the *middle*** — the start shows up as (a) **breadth** turning up in the candidate sector (`regime/breadth_indicator.py` — A/D widening from semis outward), (b) **chip-flow accumulation** (`scoring/chip_flow.py`: block-accumulation + volume-burst *before* the price gap), and (c) attention still *low* (§7) — the un-crowded window. When attention spikes (Google Trends), the easy edge is gone.
5. **Gate it** — none of this is a buy; it produces a *watchlist* that must still clear [[../philosophy/concepts/evidence-gated-rebalance]] (5-dim 十足的證據) and the [[../philosophy/concepts/liquidity-fishbowl]] `L`-score.

## §10. 整合到 $hark / Integration

- **`regime/sector_flow.py`** → add a `lead_lag_network()` that runs pairwise Granger/TE on the `SECTOR_ETFS` matrix and returns directed edges + a `transmits_from(etf)` accessor. This is the cleanest home for the Diebold-Yilmaz net-transmitter score; complements the existing relative-strength `detect_rotation`.
- **`scoring/chip_flow.py`** (single-point breakout) → extend to **supplier-link momentum**: given a `links` map (customer→supplier / tech-link), propagate a leader's chip-flow shock to linked names (Cohen-Frazzini transmission), turning the single-point detector into a small propagation step (§8).
- **`regime/funding_chain.py` + `liquidity-fishbowl`** → already the regime/§5 layer; the spillover detector should *only* fire offense when `L` is healthy.
- **New seam** — a thin `regime/spillover_graph.py` (`networkx`) consuming both modules' edges, exposing centrality / net-transmitter ranks; feed top candidates to the FOM watchlist, never auto-trade.

## §11. 同溫層風險 / crowded & decayed factors

- **TS/XS price-momentum & distance-pairs are crowded** — measured decay (TSMOM −87% risk-adj; pairs post-2002). Treat as confirmation, not edge.
- **Sector-momentum *chasing* is ~noise** at the quarter horizon (our own IC_IR 0.52) — the principal's instinct to find *un-crowded* transmission is correct; chasing the already-hot sector is the trap.
- **The link/attention edges live in low-coverage names** — they shrink precisely where everyone is looking (Menzly-Ozbas, Lee). So semis-spillover alpha is in the **second-tier suppliers/adjacent sectors**, not the mega-cap leader.
- **Flow & attention signals reverse** — using them as trend confirmation (vs short-term pressure) inverts the edge.
- **Backtest hygiene** — every estimator above is lookahead-prone (regime labels, cointegration windows, flow vintages); mirror the strict `.loc[:as_of]` discipline already in `sector_flow.py` and the [[_sourcing-protocol]].

## Sources

1. Cohen & Frazzini, "Economic Links and Predictable Returns," *J. Finance* 63(4):1977-2011, 2008 — https://onlinelibrary.wiley.com/doi/10.1111/j.1540-6261.2008.01379.x (PDF http://www.econ.yale.edu/~shiller/behfin/2006-04/cohen-frazzini.pdf) — retrieved 2026-05-31 — grade A — cross-confirmed (AQR, HBS, SSRN).
2. Menzly & Ozbas, "Market Segmentation and Cross-Predictability of Returns," *J. Finance* 65(4):1555-1580, 2010 — https://onlinelibrary.wiley.com/doi/abs/10.1111/j.1540-6261.2010.01578.x — retrieved 2026-05-31 — grade A — primary-fetched (Wiley + AFA internet appendix).
3. Lee, Sun, Wang & Zhang, "Technological Links and Predictable Returns," *J. Financial Economics* 132(3):76-96, 2019 — https://www.sciencedirect.com/science/article/abs/pii/S0304405X18303167 (SSRN 3036241) — retrieved 2026-05-31 — grade A — cross-confirmed.
4. Hong & Stein, "A Unified Theory of Underreaction, Momentum Trading and Overreaction," *J. Finance* 54(6):2143-2184, 1999 — http://www.columbia.edu/~hh2679/jf-mom.pdf — retrieved 2026-05-31 — grade A — primary-fetched.
5. Moskowitz, Ooi & Pedersen, "Time Series Momentum," *J. Financial Economics* 104(2):228-250, 2012 — https://w4.stern.nyu.edu/facdir/lpederse/papers/TimeSeriesMomentum.pdf — retrieved 2026-05-31 — grade A — primary-fetched.
6. Jegadeesh & Titman, "Returns to Buying Winners and Selling Losers," *J. Finance* 48(1), 1993 — referenced via Moskowitz-Pedersen — retrieved 2026-05-31 — grade A — single-source-pending (seminal, not re-fetched).
7. Moskowitz & Grinblatt, "Do Industries Explain Momentum?," *J. Finance* 54(4):1249-1290, 1999 — https://onlinelibrary.wiley.com/doi/abs/10.1111/0022-1082.00146 — retrieved 2026-05-31 — grade A — cross-confirmed.
8. Gatev, Goetzmann & Rouwenhorst, "Pairs Trading: Performance of a Relative-Value Arbitrage Rule," *Rev. Financial Studies* 19(3):797-827, 2006 — https://academic.oup.com/rfs/article-abstract/19/3/797/1646694 — retrieved 2026-05-31 — grade A — cross-confirmed; post-2002 decay = analysis (grade C).
9. Avellaneda & Lee, "Statistical Arbitrage in the U.S. Equities Market," *Quantitative Finance* 10(7):761-782, 2010 — https://papers.ssrn.com/sol3/papers.cfm?abstract_id=1153505 — retrieved 2026-05-31 — grade A — cross-confirmed.
10. Ehsani & Linnainmaa, "Factor Momentum and the Momentum Factor," *J. Finance* 77(3):1877-1919, 2022 — https://onlinelibrary.wiley.com/doi/abs/10.1111/jofi.13131 (NBER w25551) — retrieved 2026-05-31 — grade A — cross-confirmed.
11. Diebold & Yilmaz, "Better to Give than to Receive: ... Directional Measurement of Volatility Spillovers," *Int. J. Forecasting* 28(1) 2012; & "On the network topology of variance decompositions," *J. Econometrics* 182(1) 2014 — https://arxiv.org/pdf/2211.04184 (retrospective); https://financialconnectedness.org — retrieved 2026-05-31 — grade A — cross-confirmed.
12. Ben-David, Franzoni & Moussawi, "Do ETFs Increase Volatility?," *J. Finance* 73(6), 2018; ETF-flow reversal — https://www.nber.org/system/files/working_papers/w20071/revisions/w20071.rev0.pdf — retrieved 2026-05-31 — grade A — cross-confirmed.
13. Da, Engelberg & Gao, "In Search of Attention," *J. Finance* 66(5):1461-1499, 2011 — https://www3.nd.edu/~zda/google.pdf — retrieved 2026-05-31 — grade A — primary-fetched.
14. Bai & Perron, "Estimating and Testing Linear Models with Multiple Structural Changes," *Econometrica* 66(1), 1998; + Wang et al., "Adaptive Hierarchical HMM for Structural Market Change," *JRFM* 19(1):15, 2026 — https://www.mdpi.com/1911-8074/19/1/15 — retrieved 2026-05-31 — grade A/B — cross-confirmed.
15. Li & Ferreira, "Follow the Leader: Enhancing Systematic Trend-Following Using Network Momentum," arXiv:2501.07135, 2025 — https://arxiv.org/html/2501.07135v1 — retrieved 2026-05-31 — grade B — primary-fetched (preprint).
16. SqueezeMetrics, "The Implied Order Book / GEX & DIX"; SpotGamma "Gamma Exposure (GEX)" — https://spotgamma.com/gamma-exposure-gex/ — retrieved 2026-05-31 — grade C — practitioner (single-source-pending).
17. AlphaArchitect / arXiv 2602.11708, TSMOM decay ~87% 1995-2000→2018-2023 (factor crowding) — https://alphaarchitect.com/are-trend-following-and-time-series-momentum-research-results-robust/ — retrieved 2026-05-31 — grade C — analysis.
18. PD Macro / Regions / MacroMicro, SOX as leading indicator (~1-2 quarters ahead of IT; ~3 quarters / 0.86 corr to chip revenue; capex→memory→optical transmission) — https://pdmacro.com/the-sox-spx-yoy-a-semiconductor-cycle-leading-indicator/ ; https://www.regions.com/-/media/pdfs/AssetManagement-The-Semiconductor-Cycle.pdf — retrieved 2026-05-31 — grade C/B — cross-confirmed (multiple practitioner).
19. `hudson-and-thames/arbitragelab` (PCA/OU/cointegration statarb) — https://github.com/hudson-and-thames/arbitragelab — retrieved 2026-05-31 — grade B — OSS.
20. `microsoft/qlib`, `vectorbt`, `statsmodels` (grangercausalitytests / VAR / Markov-switching), `hmmlearn`, `ruptures`, `networkx`, `PyIF`/`pyinform` (transfer entropy), `pytrends` — https://github.com/microsoft/qlib ; https://vectorbt.dev — retrieved 2026-05-31 — grade B — OSS.

## See also

- [[../philosophy/concepts/hotspot-sector-rotation]] — measured: seasonality (IC_IR 2.78) >> sector-momentum (0.52); the empirical anchor for §1/§11
- [[../philosophy/concepts/chip-flow-single-point-breakout]] · `scoring/chip_flow.py` — the §2/§8 supplier-link extension target
- `regime/sector_flow.py` — the §10 lead-lag-network extension target
- [[../philosophy/concepts/liquidity-fishbowl]] · `regime/funding_chain.py` — the §5 regime gate
- [[../philosophy/concepts/return-horizon-structure]] — daily-reversal / monthly-momentum / annual-value term structure (which family fits which horizon)
- [[../philosophy/concepts/price-volume-divergence]] · `scoring/news_sentiment.py` — the §7 attention cross-ref
- [[_sourcing-protocol]] — 考證 discipline applied to every claim above
