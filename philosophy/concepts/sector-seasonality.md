---
type: concept
status: proposal
tags: [sector-rotation, seasonality, monthly, sector-etf, proposal]
title: Sector Seasonality — proposal
author_role: compiler
proposed_destination: philosophy/concepts/sector-seasonality.md
proposed_at: 2026-05-29T03:30:00-04:00
---

# Sector Seasonality (PROPOSAL)

> Draft proposal. Human approval required.

## Best-month / worst-month per sector (verified 2005-2026)

| Sector | ETF | Best month (mean, hit rate) | Worst month (mean, hit rate) |
|---|---|---|---|
| Technology | XLK | **Jul +3.6% / 81%** | Sep -0.5% / 57% |
| Consumer Discretionary | XLY | Jul +3.3% / 76% | Jun -0.1% / 52% |
| Consumer Staples | XLP | Jul +2.9% / 76% | Sep -0.8% / 43% |
| Energy | XLE | Apr +3.8% / 64% | Aug -1.2% / 48% |
| Financials | XLF | **Jul +3.1% / 81%** | Jun -1.6% / 33% |
| Industrials | XLI | **Nov +3.6% / 81%** | Jun -1.0% / 38% |
| Healthcare | XLV | Jul +2.7% / 81% | Sep -0.7% / 48% |
| Utilities | XLU | **Jul +3.2% / 86%** | Sep -1.2% / 52% |
| Materials | XLB | Nov +3.2% / 86% | Sep -1.9% / 48% |
| Real Estate | XLRE | **Jul +4.2% / 100%** | Sep -3.6% / 20% |
| Communications | XLC | Nov +3.5% / 75% (since 2018) | Sep -2.3% / 25% |
| Semiconductors | SOXX | May +4.7% / 77% | Sep -0.4% / 48% |
| Biotech | XBI | Nov +4.7% / 70% | Mar -1.0% / 52% |
| Aerospace/Defense | ITA | Nov +3.2% / 75% | Mar -0.7% / 55% |
| **Solar** | **TAN** | **Jan +3.9% / 72%** | Oct -2.7% / 39% |
| Gaming/Esports | HERO | Nov +4.6% / 71% (since 2019) | Sep -2.6% / 33% |
| Homebuilders | XHB | **Nov +3.3% / 90%** | Jun -2.2% / 45% |

## Universal patterns

### July is broadly strong
Best month for XLK, XLY, XLP, XLF, XLV, XLU, XLRE. Strong reasons:
- Q2 earnings positive surprise tendency
- Summer travel/leisure flow
- Pre-back-to-school consumer pickup
- Defensive sectors benefit from summer cooling demand (XLU)

### November is broadly strong
Best month for XLI, XLB, XLC, XBI, ITA, HERO, XHB. Strong reasons:
- Pre-Santa-rally positioning
- Q4 capex acceleration (XLI, XLB)
- Year-end fund flows (XBI especially)
- Holiday consumer (XLY, XHB, HERO)

### September is broadly weak
Worst month for XLK, XLP, XLV, XLU, XLB, XLRE, XLC, XBI, HERO. Three theses:
- Tax-loss selling preparation
- End-of-fiscal-Q3 portfolio cleanup
- Volatility-premium seasonality (option market expects September weakness, sometimes self-fulfilling)

## Sector-specific quirks

### XLE (Energy) — April peak
Strong: April +3.8% (spring driving demand)
Other strong: November +2.3%
**Diverges from broader market** in October-November (less Santa rally exposure)

### TAN (Solar) — January peak (corrects principal misintuition)
- Principal claimed solar strong in **December**
- Empirical: TAN best month is **January** (+3.85%, 72% positive)
- December is mediocre (+0.76%, 56% positive)
- **Thesis for January effect**: year-start policy announcements (renewable subsidies, tax credit extensions), portfolio reallocation into ESG
- Worst months for TAN: Sept (-2.6%), Oct (-2.7%)

### HERO (Gaming) — November peak (corrects principal misintuition)
- Principal claimed gaming up in **summer (Jul-Aug)**
- Empirical: HERO best month is **November** (+4.6%, 71% positive)
- Second-strongest: May (+3.6%), June (+3.7%)
- July (+1.7%, 67%) and August (+0.6%, 50%) are mediocre
- **Caveat**: only 6-year data (since Oct 2019); summer effect may not be visible in short sample

### XHB (Homebuilders) — November is the cleanest signal
- Nov +3.3% with **90% positive rate** (the highest hit rate of any sector-month combo)
- Best month for tactical entries; strongly anchors Q4-Q1 housing-related positioning

### SOXX (Semiconductors) — May peak (unusual!)
- May +4.7% (77% positive) — best month
- Most other sectors peak Jul or Nov; SOXX peaks earlier
- **Thesis**: semiconductor inventory restocking cycle leads broader tech by 1-2 months

## Operational use

### Sector bias inputs to `multi-scale-cycles-concept` framework

When a candidate is in a sector entering its seasonally favourable month:
- `sector_bias = +0.7` (when sector best-month hit rate > 75%)
- `sector_bias = +0.4` (when best-month hit rate 65-75%)
- `sector_bias = +0.2` (when best-month hit rate 55-65%)

When entering seasonally weak month:
- `sector_bias = -0.4 to -0.6` (Sep for most sectors)

### Sector rotation enabling rules (additions to `watchlist/universe.yaml`)

- **TAN enable in December**: stage entries for January effect
- **HERO enable in October**: stage entries for November rally
- **XHB enable in October**: stage entries for Nov-Apr best-6m
- **XLU / XLP enable in May**: defensive heading into September weakness

## Caveats

- Data spans 2005-2026 for most ETFs (15-20 years, 15-22 observations per month)
- XLC, XLRE, HERO data is shorter (8-10 years); patterns less robust
- Sample-size confidence: monthly mean estimates have wide confidence intervals; treat differences < 0.5% as noise
- The 2020-2026 sample is unusual (Covid + Fed-zero + AI cycle); may not generalise to non-cycle regimes

## See also

- [[../../wiki/06_cycle_framework]] §4 — full sector data
- [[sell-in-may-and-september-weak]] — broad-index monthly seasonality
- [[multi-scale-cycles-concept]] — broader framework
- [[../04-sector-and-finviz]] — existing sector framework (this proposes adding seasonal triggers)
