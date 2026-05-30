---
type: source
source_class: principal_directive
source_grade: A
source_first_visible_at: 2026-05-29T07:00:00-04:00
ingested_at: 2026-05-29T07:00:00-04:00
source_url: chat://principal-andy
topic: principal-watchlist-and-thesis-requests
tags: [watchlist, principal, consumer-electronics, recovery]
---

# Principal Watchlist + Thesis Requests 2026-05-29

## §1. Portfolio image — current tracked names (28 tickers)

User-supplied via screenshot, requesting FOM scoring + sector rotation analysis:

| Ticker | Company |
|---|---|
| ZM | Zoom Communications Inc |
| PEP | PepsiCo Inc |
| DIS | Walt Disney Co |
| LUNR | Intuitive Machines Inc |
| UPS | United Parcel Service Inc |
| DOCN | DigitalOcean Holdings Inc |
| SHAK | Shake Shack Inc |
| ARRY | Array Technologies Inc |
| RRX | Regal Rexnord Corp |
| IP | International Paper Co |
| DELL | Dell Technologies Inc |
| ORCL | Oracle Corp |
| UEC | Uranium Energy Corp |
| TAC | Transalta Corp |
| GFS | GlobalFoundries Inc |
| AAPL | Apple Inc |
| BIRK | Birkenstock Holding Plc |
| PG | Procter & Gamble Co |
| ALGM | Allegro Microsystems Inc |
| SKYT | SkyWater Technology Inc |
| RELY | Remitly Global Inc |
| PATH | UiPath Inc |
| APPN | Appian Corp |
| AESI | Atlas Energy Solutions Inc |
| GRPN | Groupon Inc |
| EXTR | Extreme Networks Inc |

(AAPL chart shown May 22 close — recent uptrend Feb → May)

**Compiler observation on this list**:

- **Mix of large & small**: ranges from PEP/DIS/AAPL/PG (mega cap) to SHAK/LUNR/SKYT/GRPN (small-mid)
- **Sector spread**: tech (ZM/DOCN/PATH/APPN/ORCL/EXTR) / consumer (DIS/SHAK/BIRK/GRPN/PG/PEP) / industrials (UPS/RRX/IP) / specialty semis (GFS/ALGM/SKYT) / energy (UEC/AESI/TAC) / space (LUNR) / payments (RELY)
- **Notable inclusions**: 
  - **GFS (GlobalFoundries)** — Serenity's "non-leading-edge foundry" play, similar thesis to XFAB
  - **SKYT (SkyWater Technology)** — US specialty foundry (Defense/aerospace)
  - **LUNR (Intuitive Machines)** — Space / Moon mission
  - **AESI (Atlas Energy Solutions)** — frac sand for shale (energy plays)
- **Bubble watchlist already in $hark universe**: ORCL (principal-flagged), AAPL, DELL
- **Consumer recovery candidates** (per principal §3): AAPL, DELL — already here

**Action**: Run FOM v2 on this 28-ticker list with persistence-week boost; identify under-positioned candidates relative to sector rotation.

## §2. Consumer electronics recovery thesis (principal-named)

Principal believes consumer electronics may be recovering. Watch:

| Ticker | Thesis | Buffett-tier? |
|---|---|---|
| **LULU** | Lululemon — premium athleisure; post-pandemic correction recovery | Mid moat |
| **NKE** | Nike — global brand, China recovery + AI marketing | High moat |
| **VFC** | VF Corp — Vans/North Face/Timberland — turnaround play | Low moat |
| **VSCO** | Victoria's Secret — brand-rebuild + activewear pivot | Low moat |
| **TSLA** | Tesla — EV cycle + robotics + SpaceX IPO catalyst | Volatile |
| **AAPL** | Apple — iPhone refresh cycle + Apple Intelligence + India growth | High moat (Buffett owned) |
| **DELL** | Dell — AI server demand (already up); PC refresh cycle (laggard) | Modest moat |
| **HPQ** | HP — PC refresh laggard; printer recurring revenue | Modest moat |

**Compiler thesis**: AAPL + DELL + HPQ are positioned at intersection of consumer recovery + AI hardware tailwind. NKE has best Buffett-moat. LULU/VFC/VSCO are pure-cyclical recovery plays — higher beta.

## §3. Sector laggards search ("同板塊都上漲了只剩它沒漲")

Principal explicitly asks: find names where same-sector peers have rallied but specific name has lagged. This is a **mean-reversion candidate signal**.

Method:
- For each sector ETF, find the 3 best-performing members (12m return)
- For each, find members in same sector with 12m return < 25% of the top 3 average
- Stage as "catch-up" candidates

This will feed into [[../../wiki/05_recommendations/2026-05-29-overnight-batch]].

## §4. Trump black-swan defense ask

Principal asks: do we buy UVXY / UVIX for defense? Or what?

**Compiler immediate response** (full analysis in [[../../wiki/10_defensive_hedging]]):

- ⚠️ **UVXY / UVIX 不適合長期持有** — they decay 50-80% / year due to VIX futures contango
- **Better options**:
  1. **VIX call options** (60-90 DTE) — defined risk
  2. **TLT calls** — flight-to-quality
  3. **GLD long position** — macro uncertainty hedge
  4. **Mag 7 puts** with policy exposure (NVDA, TSM)
  5. **SH** (-1× SPY) — sustainable inverse without 2-3× decay
  6. **Cash buffer** — Buffett's preferred hedge
- **Sizing**: tail hedge ≤ 5% of portfolio, with explicit "decay budget" annually

## §5. "From SP500 + R2K 每日 3+3 推薦" 系統

Principal wants:
- 3 SP500 picks + 3 R2K picks daily
- 100 candidate watchlist
- **NOT mega caps** (NVDA hard to keep exploding)
- Highest-explosive-potential sectors
- Golden cross + Trump policy + data-backed
- Alpha + upside (not stability)

**Compiler will build**: `src/sharks/scoring/fom_alpha.py` — variant with:
- Market cap filter: exclude > $500B
- Universe: SP500 (top 500 by market cap, excluding mega) + Russell 2000 sample (high-coverage names)
- Weight reshuffle: momentum 30% / bubble_guard 25% / cyclic 20% / contrarian 15% / buffett 10%
- Golden cross 20/60MA crossover boost +0.10 to FOM
- Daily output: top 3 from SP500 + top 3 from R2K
- 100-name watchlist

## §6. Principal sleeping — overnight batch authority

Principal explicitly authorised overnight work: "ABCDE 都做" + "把計畫書沒做的都做一做".

**Compiler interprets this as authorisation for**:
- ✅ Save narratives to raw/
- ✅ Build new code modules in src/sharks/
- ✅ Run backtests
- ✅ Write wiki pages
- ✅ Move accepted proposals
- ⚠️ NOT authorised: trading actions, philosophy/sharks.md edits, breaking CLAUDE.md SAFETY boundaries

All overnight work consolidated into [[../../wiki/05_recommendations/2026-05-29-overnight-batch]] (final summary page for morning review).
