---
type: synthesis
domain: method
tags: [attention, retail-sentiment, google-trends, reddit, stocktwits, contrarian, squeeze-risk, early-theme-radar, alt-data, lookahead]
as_of_timestamp: 2026-05-31T06:00:00+08:00
author_role: researcher
status: live
schema_version: 1
---

# 社群/搜尋躍活數據 = 訊號層? / Social & Search Attention as a Signal Layer

The principal wants **Reddit / Google Trends / X 躍活數據** as an EARLY RADAR — 趨勢追蹤 + 尚未被定價的 alpha. This page is the skeptical practitioner guide: what the academic record actually says, the 2026 data-access reality, how to build an attention factor with look-ahead hygiene, and where it adds value vs noise inside `$hark`. **Research/educational only — not buy/sell advice. Point-in-time = 2026-05-31.** Complements (does not duplicate) the existing news-NLP seam (`scoring/news_sentiment.py` + `ai/dispatcher.py`) and the planned Phase-5 sentiment dim.

## §0. 一句話 + 訊號性質 / Bottom line + signal nature

> **Retail/search attention is a SHORT-HORIZON, mostly CONTRARIAN, retail-herding signal — a thermometer of who-is-crowding, NOT a long-term alpha engine.** The replicated finding (across 15 years of literature) is: a spike in attention predicts a *small* price pop over ~1–2 weeks that **reverses within the year**, and *intense* retail buying predicts *negative* forward returns. As a positive momentum factor it is weak and decaying; as a **(a) contrarian/blow-off flag, (b) squeeze-risk gauge, and (c) early-THEME radar** it has real, defensible use. Treat it like the `bubble_guard` cousin for the crowd, not like an earnings surprise.

訊號性質 in one row: **horizon = days-to-2-weeks** (decays fast); **sign = mostly contrarian at the extreme** (high attention → reversal); **what it measures = retail/household attention & crowding**, which is exactly the population that buys late ([[../wiki/07_ai_bubble_audit|late-cycle]] read). Anyone selling it as "find the next 10× before Wall Street" is selling the rare tail, not the base rate.

## §1. 證據 / Evidence — does attention predict returns?

The literature is unusually consistent, and it does **not** say "buy what's trending."

- **Da, Engelberg & Gao (2011), "In Search of Attention," J. Finance.** The seminal paper. Builds the **Google Search Volume Index (SVI)** as a *direct, timely* proxy for **retail** attention (vs indirect proxies like volume/news). Russell 3000, 2004–2008: an SVI spike predicts **higher prices over the next ~2 weeks (order of ~30 bps) and an eventual price reversal within the year**; also explains the large IPO first-day pop and long-run IPO underperformance. The shape — *pop then reversal* — is the whole story. [In Search of Attention — https://onlinelibrary.wiley.com/doi/10.1111/j.1540-6261.2011.01679.x — retrieved 2026-05-31 — grade A — cross-confirmed (Wiley + author PDF + 2,000+ cites)]
- **Barber & Odean (2008), "All That Glitters," Rev. Financial Studies.** Individual investors are **net buyers of attention-grabbing stocks** (in the news, abnormal volume, extreme one-day returns) because of the *search problem* on the buy side. Critically, these attention-driven buys **predict significantly negative future returns** — retail buys after the move, at the wrong time. This is the foundational *contrarian* result. [All That Glitters — https://faculty.haas.berkeley.edu/odean/papers%20current%20versions/allthatglitters_rfs_2008.pdf — retrieved 2026-05-31 — grade A — primary-fetched]
- **Barber, Huang, Odean & Schwarz (2022), "Attention-Induced Trading and Returns: Evidence from Robinhood Users," J. Finance.** The modern, sharpest contrarian estimate: intense herding into the top-bought names forecasts **average 20-day abnormal returns of −4.7%** for the most-bought stocks each day, and the negative return *grows* as you isolate the most intense herding episodes. Robinhood's "Top Movers" UI manufactured the herd. [Attention-Induced Trading and Returns — https://onlinelibrary.wiley.com/doi/abs/10.1111/jofi.13183 — retrieved 2026-05-31 — grade A — cross-confirmed (Wiley + SSRN 3715077 + IIMB PDF)]
- **Da, Engelberg & Gao (2015), "The Sum of All FEARS," Rev. Financial Studies.** Aggregates household search ("recession," "unemployment," "bankruptcy") into the **FEARS** index. 2004–2011: FEARS predicts **short-term return reversals, temporary volatility increases, and fund flows out of equity into bonds** — a *market-level* sentiment thermometer, again reversal-flavoured. [The Sum of All FEARS — https://academic.oup.com/rfs/article-abstract/28/1/1/1682440 — retrieved 2026-05-31 — grade A — cross-confirmed (Oxford + UCSD-Rady PDF)]
- **Bollen, Mao & Zeng (2011), "Twitter Mood Predicts the Stock Market," J. Comp. Science.** The famous (and famously fragile) claim that an aggregate Twitter "calm" mood Granger-causes DJIA with 86.7% directional accuracy. Heavily cited but **its out-of-sample robustness is contested** (see Econ Journal Watch "Shy of the Character Limit" rebuttal). Cite it as *the origin of social-sentiment trading*, and as a **cautionary tale of in-sample overfit**, not as a working signal. [Twitter Mood — https://www.sciencedirect.com/science/article/abs/pii/S187775031100007X — retrieved 2026-05-31 — grade A — single-source-pending; rebuttal: https://econjwatch.org/articles/shy-of-the-character-limit-twitter-mood-predicts-the-stock-market-revisited — grade C]
- **WSB / meme-stock studies (2021–2025).** GameStop work finds **rank correlation ~0.93 between WSB GME mentions and retail trading volume intraday** (mentions track flow tightly), and that WSB "opinion leaders" can trigger consensus — but the community's predictive coherence **decayed** after Jan-2021 as it shifted from finance to memes. Recent stock-level work ("What's Trending?", MDPI 2025) and news-vs-social comparisons confirm **social sentiment now dominates news sentiment** for retail-driven names and that retail order imbalance persists for weeks. [How online discussion affects trading: GameStop — https://pmc.ncbi.nlm.nih.gov/articles/PMC8965552/ — grade B — cross-confirmed; What's Trending? Stock-Level Investor Sentiment — https://www.mdpi.com/2227-7072/13/3/158 — retrieved 2026-05-31 — grade B; Sentimental showdown news vs social — https://pmc.ncbi.nlm.nih.gov/articles/PMC11076966/ — grade B]

**Evidence verdict:** attention → returns is **real but short-horizon and largely contrarian/reversal**, strongest precisely where crowding is most retail (meme names, IPOs, low-float). It is **not** a standalone long-term alpha. The one durable *positive* edge is **theme detection** (attention rising on a ticker/sector *before* it is broadly held), which is a routing signal, not a buy signal.

## §2. 資料源 + 取得現實 (2026) / Data sources + access reality

The folklore stack ("just scrape Reddit + Google Trends") collided with the 2023 API monetisation wave. Realistic free/cheap options as of 2026-05-31:

| Source | Cost (2026) | API / access | Gotcha (the real trap) |
|---|---|---|---|
| **Google Trends** | Free | `pytrends` (unofficial), or paid scrapers (ScrapingBee etc.) | **Relative-not-absolute + renormalization = silent lookahead.** Index is rescaled 0–100 *per request*; re-pulling a window can change historical values, and the max-point is only known *after* the window ends → trivially leaks future info. Rate-limited (~60s sleep after a few hundred calls); unofficial = can break anytime. [pytrends — https://github.com/GeneralMills/pytrends — grade B; rate/rescale issue #523 — grade C] |
| **Reddit (official)** | Free **≤100 QPM**; commercial **~$0.24 / 1k calls** (≈$12k/mo for 50M); enterprise $50k–$500k+/yr | **PRAW** (Python) on OAuth; free tier ~60 req/min in practice | Free tier fine for tracking a fixed watchlist; **no cheap historical bulk** since the 2023 change. [Reddit API pricing — https://data365.co/blog/reddit-api-pricing — retrieved 2026-05-31 — grade B — cross-confirmed] |
| **Reddit history (Pushshift)** | **Effectively dead** to the public | — | Reddit revoked Pushshift mid-2023; now **approved-moderators only**. Successor **PullPush** (`pullpush.io`) mirrors the API for 3rd parties but coverage/longevity is not guaranteed → no reliable point-in-time backfill. [Pushshift shutdown / PullPush — https://pullpush-io.github.io/ — retrieved 2026-05-31 — grade B] |
| **X / Twitter API** | **Basic $200/mo · Pro $5,000/mo · Enterprise tens of $k/mo**; **pay-per-use** broadly announced **Feb 2026**; free tier gutted (≤500 posts/mo, read) | v2 endpoints | Basic's monthly read cap is too small for real-time firehose; **Pro is the practical floor for systematic use** and is expensive. Pay-per-use (2026) may finally make light usage affordable — watch it. [X API pricing — https://www.xpoz.ai/blog/guides/understanding-twitter-api-pricing-tiers-and-alternatives/ — retrieved 2026-05-31 — grade B — cross-confirmed; pay-per-use launch — https://devcommunity.x.com/t/announcing-the-launch-of-x-api-pay-per-use-pricing/256476 — grade A] |
| **StockTwits** | Free public API (no key for read) | Public message + **sentiment-v2** endpoints | Sentiment is **user-self-labelled** Bullish/Bearish; only **~30–50% of messages are labelled** → noisy, skews bullish, gameable by spam. [StockTwits sentiment API — https://sentiment-v2-api.stocktwits.com/ — grade B] |
| **ApeWisdom** | **Free, no key** | Simple JSON: ticker mention ranks across r/wallstreetbets, r/stocks, r/options, crypto | **The cheapest viable WSB-mention aggregator.** Pre-computes mention counts + rank deltas every few minutes → skips Reddit-API cost entirely. Black-box methodology; no point-in-time history → log it yourself daily. [ApeWisdom API — https://apewisdom.io/api/ — retrieved 2026-05-31 — grade C] |
| **swaggystocks / Quiver / similar** | Free tier + paid | Web + some APIs | WSB sentiment dashboards; convenient but **opaque + survivorship-prone**; treat as grade-C confirmation, not primary. |
| **Sensor Tower / data.ai (app DAU)** | Enterprise (expensive) | Vendor API | App-download/DAU as a fundamental proxy (e.g. a viral app → its parent). **Overlaps youth-culture-shifts** ([[youth-culture-shifts]]); useful but pricey, and DAU ≠ revenue. |
| **Alt-data vendors (RavenPack/Bitvore, etc.)** | Enterprise $$$ | Curated NLP feeds | Clean + point-in-time, but priced for funds; out of scope for the free/cheap stack. |

**Realistic free/cheap `$hark` stack:** **Google Trends (`pytrends`, with strict anti-rescale hygiene) + ApeWisdom (free WSB mentions) + StockTwits public sentiment + Reddit free tier (PRAW, fixed watchlist).** X is *deferred* until pay-per-use proves cheap. This stack costs ~$0 and covers the three things that matter: search attention, WSB mention velocity, and self-reported retail tone.

## §3. 建因子 / How to build an attention factor

Build a small panel of point-in-time daily features per ticker, then combine into a **single bounded z-score**, mirroring the existing bounded-tilt discipline ([[fom-integration]] §2b).

1. **Abnormal-attention z-score (core).** For each stream (SVI, mention count, message count): `z = (x_t − μ_trailing) / σ_trailing` over a **trailing-only** window (e.g. 30–90d) — never a window that includes future points. This is the abnormal-attention analogue of abnormal-volume; it is the single most defensible feature.
2. **Velocity / acceleration.** Δz and Δ²z (is attention *accelerating*?). Acceleration is the **theme-detection** signal — a ticker going from rank-200 to rank-20 on ApeWisdom in 3 days is the early-radar trigger.
3. **Sentiment NLP (reuse, don't rebuild).** Route raw text (StockTwits/Reddit titles) through the **existing `ai/dispatcher.py` `news_nlp` task** → local Nemotron bullish/bearish/neutral + confidence (same envelope `scoring/news_sentiment.py` already consumes). No new model. Aggregate to a confidence-weighted tone score. **Self-labelled StockTwits tags are a weak prior only**, given the 30–50% label rate.
4. **Dispersion / breadth of mentions.** How many *distinct* users/subreddits, not raw count → guards against a single spammer or one mega-thread. Breadth-confirmed spikes are far more reliable than count spikes.
5. **Squeeze-risk read (the highest-value composite).** `squeeze_flag = high attention-z × high short-interest × low float`. Short interest (FINRA bi-monthly / borrow-fee data) × an attention spike is the classic GME setup — useful as a **risk flag** (binary blow-off hazard), explicitly *not* a buy.

**Point-in-time + look-ahead hygiene (non-negotiable, ties to [[_sourcing-protocol]]):**
- **Google Trends rescaling = silent lookahead — the #1 trap.** Pull each historical day *as it would have been known then* (expanding/rolling pulls anchored to `as_of`), persist the raw daily series to disk **once**, and **never** re-pull a window and overwrite history. A single re-pull that renormalises to a later peak silently injects future information into every prior bar.
- **Stamp every datapoint with its retrieval date** and store immutably; backfilled social history (PullPush, ApeWisdom-with-no-history) is **not** point-in-time and must be excluded from any backtest claiming a forward edge.
- **Lag everything by ≥1 bar** to the tradable open; intraday mention→volume correlation (the 0.93 GME number) is *contemporaneous*, not predictive.
- **Account-age / bot filter** before counting — post-2021 WSB is heavily astroturfed; weight by account age + karma or the breadth feature absorbs spam.

## §4. 加值 vs 噪音 / Where it adds value vs noise

| Use case | Verdict | Why |
|---|---|---|
| **Early THEME detection** (a new sector/ticker's attention *accelerating* before institutional flows / before it's in the index) | ✅ **Real, defensible** | The one durable *positive* use. Feeds [[_weekly-watch]] as a 🆕-candidate radar — "what is the crowd waking up to that our DD hasn't covered?" Routing signal, not a buy. |
| **Squeeze / blow-off RISK flag** (attention-z × short-interest × low float) | ✅ **Real (as a risk gauge)** | Flags binary squeeze hazard on names we might otherwise size normally; protects the book, doesn't generate offense. |
| **Sentiment-extreme CONTRARIAN** (fade the most-bought / max-euphoria names) | ✅ **Real but hard to harvest** | Barber-Odean / Robinhood −4.7%/20d is robust *on average*, but the left tail (the name that keeps squeezing) can bankrupt a naive short → use as a **don't-chase / trim** signal, not a systematic short. |
| **Positive momentum** ("buy what's trending up") | ⚠️ **Weak + decaying** | The ~30bps/2-week SVI pop is small, crowded, and reverses; net of costs it's marginal. Not a core factor. |
| **Stale / lagging confirmation** (ticker already +200%, now top of WSB) | ❌ **Pure noise / late** | Peak attention ≈ peak crowding ≈ the reversal point. This is where retail buys and the literature says forward returns are *negative*. |
| **Twitter-mood market timing** (Bollen-style aggregate) | ❌ **Overfit folklore** | Origin story, not a live signal; out-of-sample contested. |

## §5. 整合到 $hark / Integration hooks

Wire as an **observe-first, bounded, NON-headline dimension** — same governance as the DD tilt ([[fom-integration]] §5): *the quant decides; attention nudges; never overrides Risk Officer, caps, exclusions, or the 十足的證據 gate.* Two concrete hooks:

- **Hook A — early-theme radar into `tech/`.** A daily `attention-radar.json` (top movers by attention-acceleration + breadth, from the free stack) feeds **[[_weekly-watch]]** as 🆕-candidates and a "crowd is waking to X" column. This is the principal's *尚未被定價的 alpha* request, kept honest: it surfaces themes for **human DD**, it does not buy them. Cheap, low-risk, high-optionality.
- **Hook B — an attention z-score as a bounded FOM dim (Phase-5).** This is explicitly the planned **Phase-5 sentiment dim**. Add an `attention_z` feature consumed exactly like a persona / the DD tilt: **bounded (≤±0.06/dim), renormalised, sign mostly CONTRARIAN at the extreme** (high attention-z → small *negative* momentum tilt; rising-but-low → small positive theme tilt), and **`squeeze_flag` exposed as an annotation column** (like `dd_sleeve`), never folded into headline FOM. **Observe-first is mandatory**: per the DD precedent, the bounded tilt only enters `final_fom` *after* a walk-forward shows it adds IC ([[../philosophy/concepts/fom-predictive-validity]]) — and given the contrarian/decay evidence, the prior is that it stays an **annotation + sleeve-router input**, not a score component. Reuse `news_sentiment.py` + `dispatcher.py` for the NLP leg; do not build a second model.

> Net: attention is best wired as **(1) a free early-theme radar feeding the weekly tracker, and (2) a contrarian/squeeze annotation on the FOM panel** — not as a new alpha source folded into the headline score.

## §6. 同溫層風險陷阱 / Echo-chamber & method pitfalls

The anti-同溫層 mandate applies to *this very signal* — it is **literally a measurement of the echo chamber**, so its failure modes are acute:

- **It IS the crowd.** By construction this signal measures retail consensus; trading *with* it at the extreme = joining the herd the literature says loses. Default posture must be **contrarian/risk, not trend-following**.
- **Lookahead via rescaling** — the Google Trends renormalization trap (§3) is the single easiest way to manufacture a fake backtest edge. Most published "Google Trends alpha" blogs are contaminated by it.
- **Crowding / capacity decay** — once a social signal is known, it is arbitraged and front-run (alpha-decay literature); the WSB-coherence decay after 2021 is a live example. Assume the published edge is smaller now.
- **Reflexivity & manipulation** — pump-and-dump, paid promotion, and bots inflate mentions on purpose; the breadth/account-age filters (§3) are not optional.
- **Survivorship & black-box vendors** — ApeWisdom/swaggystocks show *current* trending names with no clean history; treating their live snapshots as backtestable history is survivorship bias.
- **Confirmation bias on our own themes** — the most dangerous use is grepping social data to *confirm* a `tech/` thesis we already hold ([[_sourcing-protocol]] §4 "the most dangerous claim is the one that confirms the thesis"). Use attention to find what we're **missing**, and to flag where we might be **late**, not to cheer our book.

## Sources

1. Da, Engelberg & Gao (2011), *In Search of Attention*, J. Finance 66(5):1461–99 — SVI, ~2-week pop + within-year reversal — https://onlinelibrary.wiley.com/doi/10.1111/j.1540-6261.2011.01679.x — grade A — cross-confirmed
2. Barber & Odean (2008), *All That Glitters*, RFS 21(2):785–818 — attention-buying → negative forward returns — https://faculty.haas.berkeley.edu/odean/papers%20current%20versions/allthatglitters_rfs_2008.pdf — grade A — primary-fetched
3. Barber, Huang, Odean & Schwarz (2022), *Attention-Induced Trading and Returns: Evidence from Robinhood Users*, J. Finance 77(6):3141–90 — −4.7%/20d on top-bought — https://onlinelibrary.wiley.com/doi/abs/10.1111/jofi.13183 — grade A — cross-confirmed
4. Da, Engelberg & Gao (2015), *The Sum of All FEARS*, RFS 28(1):1–32 — FEARS → reversals, vol, fund flows — https://academic.oup.com/rfs/article-abstract/28/1/1/1682440 — grade A — cross-confirmed
5. Bollen, Mao & Zeng (2011), *Twitter Mood Predicts the Stock Market*, J. Comp. Sci. 2(1):1–8 — origin of social-sentiment trading (overfit caution) — https://www.sciencedirect.com/science/article/abs/pii/S187775031100007X — grade A — single-source-pending
6. Econ Journal Watch, *Shy of the Character Limit: "Twitter Mood…" Revisited* — robustness rebuttal — https://econjwatch.org/articles/shy-of-the-character-limit-twitter-mood-predicts-the-stock-market-revisited — grade C
7. *How online discussion board activity affects stock trading: GameStop* (PMC) — ~0.93 mention↔volume rank corr — https://pmc.ncbi.nlm.nih.gov/articles/PMC8965552/ — grade B — cross-confirmed
8. *What's Trending? Stock-Level Investor Sentiment and Returns* (MDPI, 2025) — recent stock-level sentiment evidence — https://www.mdpi.com/2227-7072/13/3/158 — retrieved 2026-05-31 — grade B
9. *Sentimental showdown: News vs social media* (PMC) — social sentiment now dominates news for retail names — https://pmc.ncbi.nlm.nih.gov/articles/PMC11076966/ — grade B
10. pytrends (unofficial Google Trends) + rate/rescale issue — https://github.com/GeneralMills/pytrends — retrieved 2026-05-31 — grade B/C
11. Reddit API pricing (post-2023; ~$0.24/1k, free ≤100 QPM) — https://data365.co/blog/reddit-api-pricing — retrieved 2026-05-31 — grade B — cross-confirmed
12. Pushshift shutdown → PullPush successor — https://pullpush-io.github.io/ — retrieved 2026-05-31 — grade B
13. X/Twitter API pricing tiers + pay-per-use (Feb 2026) — https://www.xpoz.ai/blog/guides/understanding-twitter-api-pricing-tiers-and-alternatives/ + https://devcommunity.x.com/t/announcing-the-launch-of-x-api-pay-per-use-pricing/256476 — retrieved 2026-05-31 — grade B/A
14. StockTwits public sentiment-v2 API (user-labelled, ~30–50% tagged) — https://sentiment-v2-api.stocktwits.com/ — grade B
15. ApeWisdom free WSB-mention API — https://apewisdom.io/api/ — retrieved 2026-05-31 — grade C
16. Crowding/short-squeeze & alpha-decay (S3 Partners; Di Mascio-Lines-Naik) — capacity decay context — http://www.efmaefm.org/0EFMAMEETINGS/EFMA%20ANNUAL%20MEETINGS/2025-Greece/papers/Manuscript-with-author-details223.pdf — grade C

## See also

- [[fom-integration]] — the bounded ±0.06, observe-first, sleeve-router pattern this dim copies · [[_weekly-watch]] (Hook A radar) · [[_sourcing-protocol]] (考證 + anti-own-confirmation)
- [[youth-culture-shifts]] — app-DAU / culture overlap with Sensor Tower data · [[../wiki/07_ai_bubble_audit]] — the late-cycle crowd-attention read
- `src/sharks/scoring/news_sentiment.py` · `src/sharks/ai/dispatcher.py` — the existing news-NLP seam this reuses (no second model)
- [[../philosophy/concepts/fom-predictive-validity]] — why the tilt stays observe-first until IC-validated
