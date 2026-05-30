---
type: source
source_class: principal_account_snapshot
source_grade: A
source_first_visible_at: 2026-05-30T11:42:00-04:00
ingested_at: 2026-05-30T23:55:00-04:00
author_role: human
accounts:
  - us_direct_broker_p1          # "Individual" Stock-Slices account, ~$11.4K
  - taiwan_fubon_8840_p2         # 複委託 — speculative graveyard + survivors
  - taiwan_domestic_9a92         # 台股 dividend / thematic ETFs
  - taiwan_dca_overseas          # 海外定時定額 (GOOG/NFLX/TSLA)
  - nvda_equity_comp_overlay     # RSU vesting schedule (overlay, NOT in audit)
---

# Full multi-account snapshot — 2026-05-30

Consolidated from 14 broker screenshots in `raw/portfolio/` (timestamps 09:56–11:42
local on 2026-05-30; 複委託 graveyard + 台股 captured same session). This is the
**master position-consume artefact** the principal requested ("消化目前倉位").

Five distinct pools. Only **P1** is mirrored into the FOM/leveraged audit; the others
are overlay/context (graveyard is dead money, RSU is equity-comp, 台股 is a separate
NTD dividend sleeve).

---

## Pool 1 — US direct broker "Individual" (P1) ≈ $11,357 USD

33 positions, sorted by Mkt Val desc. Total inferred from TARK 13.34% = $1,515 → NAV ≈ **$11,357**.
Snapshot taken 11:42 ET. Color = day P/L tint (🟢 green / 🔴 red / ⚪ flat) where legible.

| # | Ticker | % Acct | Mkt Val | Lev? | Tint | Note |
|---|---|---|---|---|---|---|
| 1 | TARK | 13.34% | $1,515.00 | 2x ARKK | 🟢 | **single largest position; 2x leveraged, decay-exposed** |
| 2 | LABU | 5.20% | $585.00 | 3x XBI | 🟢 | 3x biotech bull — high decay |
| 3 | HPQ | 4.88% | $551.19 | — | 🟢 | NEW vs 5/29 head; PC/print, Computex-adjacent |
| 4 | CRWG | 4.65% | $514.67 | 2x CRWV | 🟢 | 2x CoreWeave — AI-infra high-beta |
| 5 | CRSR | 4.31% | $484.00 | — | 🟢 | Corsair — gaming peripherals |
| 6 | ALGM | 4.25% | $476.30 | — | 🔴 | Allegro Micro — auto/industrial analog |
| 7 | SBIT | 4.17% | $475.61 | -1x BTC | 🟢 | **inverse BTC hedge** (green = BTC down today) |
| 8 | NOWL | 3.89% | $469.21 | 2x NOW | 🟢 | 2x ServiceNow |
| 9 | AAPB | 3.57% | $398.80 | 2x AAPL | 🔴 | 2x Apple |
| 10 | DDD | 3.17% | $354.68 | — | 🟢 | 3D Systems — 3D-print spec |
| 11 | ENPH | 3.04% | $340.30 | — | 🔴 | Enphase — solar |
| 12 | LULG | 2.97% | $336.00 | 2x LULU | ⚪ | 2x Lululemon |
| 13 | VSCO | 2.44% | $275.75 | — | 🔴 | Victoria's Secret |
| 14 | ARRY | 2.42% | $272.70 | — | 🔴 | Array Tech — solar tracker |
| 15 | CRM | 1.89% | $214.53 | — | 🟢 | Salesforce |
| 16 | RBLU | 1.90% | $213.90 | 2x RBLX | 🟢 | 2x Roblox |
| 17 | LULU | 1.86% | $209.26 | — | 🔴 | Lululemon (also held 2x via LULG) |
| 18 | QSU | 1.86% | $208.50 | — | 🟢 | (QuantumScape-related / verify ticker) |
| 19 | CRCT | 1.84% | $207.50 | — | 🟢 | Cricut |
| 20 | APA | 1.84% | $206.52 | — | 🔴 | APA Corp — E&P oil/gas |
| 21 | NKE | 1.81% | $205.35 | — | 🔴 | Nike |
| 22 | TSLA | 1.82% | $204.75 | — | 🔴 | Tesla (also held 2x via TSLL) |
| 23 | STZ | 1.80% | $202.58 | — | 🔴 | Constellation Brands |
| 24 | AMPX | 1.80% | $202.30 | — | 🔴 | Amprius — battery |
| 25 | SWKS | 1.75% | $196.96 | — | 🟢 | Skyworks — RF |
| 26 | PG | 1.75% | $196.69 | — | 🟢 | Procter & Gamble — defensive |
| 27 | PEP | 1.74% | $195.82 | — | 🔴 | PepsiCo — defensive |
| 28 | UAA | 1.56% | $178.50 | — | 🔴 | Under Armour |
| 29 | OKLL | 1.56% | $178.39 | 2x OKLO | 🔴 | 2x Oklo — nuclear SMR spec |
| 30 | VFC | 1.53% | $173.80 | — | 🟢 | VF Corp |
| 31 | TSLL | 1.41% | $158.20 | 2x TSLA | 🔴 | 2x Tesla |
| 32 | NOK | 1.32% | $149.20 | — | 🟢 | Nokia |
| 33 | ONDU | 1.34% | $147.00 | — | 🔴 | (Ondas / verify ticker) |

**Leveraged sleeve in P1 (10 of 33 = ~$5.0K, ~44% of NAV by value):**
TARK (2x), LABU (3x), CRWG (2x), SBIT (-1x), NOWL (2x), AAPB (2x), LULG (2x),
RBLU (2x), OKLL (2x), TSLL (2x). This is the audit's primary leveraged-decay exposure.

### Rotation vs 2026-05-29 snapshot (de-leveraging in progress)

SOLD/exited since 5/29 (confirmed by Order Status screen, see below):
**ORCX, QBTX, QUBX, RGTX, SMCL** — all 2x single-stock names. Plus NOW (parent) trimmed.
ENTERED/grew: **HPQ, CRWG, ALGM, NOK, ONDU, UAA, TSLL**.
Net read: principal is **rotating OUT of decayed 2x single-stock ETFs into a mix of
cash-flow names (HPQ/PG/PEP/NKE) and AI-infra (CRWG)** — directionally consistent with
the leveraged-ETF decay thesis.

### Order Status screen (recent SELL fills, screenshot 09:56)

| Ticker | Name | Action | Fill |
|---|---|---|---|
| ORCX | Defiance Daily 2x Long ORCL | Sell 10 @ Mkt | $52.97 |
| QBTX | Tradr 2x Long QBTS | Sell 10 @ Mkt | $22.02 |
| QUBX | Tradr 2x Long QUBT | Sell 10 @ Mkt | $17.54 |
| RGTX | Defiance Daily 2x Long RGTI | Sell 10 @ Mkt | $34.905 |
| SMCL | GraniteShares 2x Long SMCI | Sell 3 @ Mkt | $115.4601 |

All five are 2x single-stock leveraged ETFs being **closed out** — the de-leverage move.

---

## Pool 2 — 複委託 (Taiwan Fubon 8840 / P2) — speculative graveyard + survivors

Largely **dead money**: a cluster of -90% to -100% speculative wipeouts (consistent with
the ~400萬 2025 crypto/spec drawdown in memory). A few survivors carry the account.

**Catastrophic (write-offs / near-zero):**

| Ticker | Sh | P/L% | Value | Note |
|---|---|---|---|---|
| 中國恒大 (Evergrande 03333) | 40,000 | -100% | HKD ~0 | delisted/defunct |
| FSRNQ (Fisker) | 2,000 | -100% | ~0 | bankrupt |
| FTCHQ (Farfetch) | 270 | -100% | ~0 | delisted |
| GGEI (Green Giant) | 2,000 | -99.94% | ~0 | shell |
| IMTE | 5 | -99.62% | ~0 | spec |
| NRDE (NU Ride) | 13 | -92.92% | ~0 | ex-Lordstown |
| LCDL (2x LCID) | 40 | -91.74% | low | 2x Lucid — decayed |
| BYND | 50 | -88.69% | low | Beyond Meat |
| PYPG (2x PYPL) | 20 | -64.92% | $111.71 | 2x PayPal — decayed |
| MARA | 10 | -31.47% | $143.8 | BTC miner |

**Survivors / green:**

| Ticker | Sh | P/L% | Value | Note |
|---|---|---|---|---|
| WOLF (Wolfspeed) | 10 | +88.04% | $592.8 | SiC — the big P2 winner |
| AAPB (2x AAPL) | 20 | +22.26% | $803.54 | 2x Apple (also in P1) |
| ICLN | 5 | +13.57% | $117.85 | clean-energy ETF |

**Other 複委託 cash holdings (from 庫存 list, share counts only):**
AOSL 3, BLDP 100, HPQ 40, LPL 30, NTLA 20, ORCL 2, RIVN 20, TBCH 30, UEC 30,
OPI 1,000, XCF Global 500.

> Mature-analyst read: P2 is a **lesson archive, not a working book**. The dead names
> are sunk; only WOLF/AAPB/ICLN are live. No FOM action on the zeros — they are tax-loss
> / housekeeping items, not rebalance candidates. The pattern (2x single-stock + meme +
> China property + EV-SPAC) is the exact failure mode the leveraged-ETF scorer and
> bubble_guard are designed to flag going forward.

---

## Pool 3 — 台股 domestic (9A92-0316376) — dividend / thematic ETF sleeve ≈ NT$42.3K

The **healthiest sleeve** — disciplined Taiwan high-dividend + thematic ETFs, all green.

| Ticker | Name | Sh | P/L% | Value (TWD) |
|---|---|---|---|---|
| 0056 | 元大高股息 | 270 | +34.98% | 13,503 |
| 00878 | 國泰永續高股息 | 197 | +40.20% | 6,044 |
| 00929 | 復華台灣科技優息 | 502 | +50.07% | 15,151 |
| 00965 | 元大航太防衛科技 | 177 | +0.45% | 4,484 |
| 00983A | 主動中信ARK創新 | 261 | +3.56% | 3,143 |

Total ≈ **NT$42,325 ≈ ~$1,320 USD**. High-dividend core (0056/00878/00929) compounding
nicely; aerospace-defense (00965) and active-ARK (00983A) are newer thematic adds near flat.

---

## Pool 4 — 海外定時定額 DCA (複委託 recurring buy)

| Ticker | P/L% | Value (TWD) | Note |
|---|---|---|---|
| GOOG | +8.25% | 6,495 | active DCA |
| TSLA | +7.69% | 11,846 | active DCA (also held in P1) |
| NFLX | -2.70% | 973 | active DCA |
| BRK.B / DIS / HD / JPM / META / WMT | — | 0 | configured, not funded |

---

## Pool 5 — NVDA RSU vesting schedule (overlay — NOT in audit, per principal instruction)

Equity-comp portal, not a brokerage. Listed for **concentration overlay only**
(`portfolio_audit.py` CONCENTRATION_CONTEXT_USD ≈ $130K). Vesting cadence:

| Vest date | Shares | Value (USD) |
|---|---|---|
| 2026-06 | 76 | $16,148 |
| 2026-09 | 59 | $12,536 |
| 2026-12 | 59 | $12,536 |
| 2027-03 | 59 | $12,536 |
| 2027-06 | 59 | $12,536 |
| 2027-09 | 43 | $9,136 |
| 2027-12 | 42 | $8,924 |

---

## Consolidated exposure & concentration

| Pool | Approx USD | Share of liquid-ish |
|---|---|---|
| NVDA RSU overlay | ~$130,000 | ~88% |
| P1 "Individual" | ~$11,357 | ~7.7% |
| P2 複委託 (live names only ~$1.8K; zeros ≈0) | ~$1,800 | ~1.2% |
| 台股 9A92 | ~$1,320 | ~0.9% |
| DCA overseas | ~$640 | ~0.4% |
| **Total ex-RSU** | **~$15,100** | — |
| **Total incl RSU** | **~$147,100** | — |

**Dominant risk = NVDA RSU (~88%).** Every P1 rebalance moves <8% of net worth; the
real concentration lever is RSU sale cadence, not P1 churn (per `wiki/12_employee_concentration`).

## Mature-analyst flags (for the daily health-check)

1. **TARK 13.3% of P1 + 44% of P1 in leveraged ETFs** — the single biggest *manageable*
   risk. 2x/3x decay compounds daily; this is a tactical sleeve sized like a core sleeve.
2. **Good instinct already in motion**: the 5/30 sells (ORCX/QBTX/QUBX/RGTX/SMCL) show the
   principal trimming the worst-decay 2x single-stock names without prompting. Reinforce, don't fight.
3. **SBIT (-1x BTC) 4.2%** is a deliberate inverse hedge ("也怕大空頭"); keep but size-check
   vs the leveraged longs — net beta matters more than gross.
4. **台股 dividend sleeve is the model** the rest of the book should aspire to: disciplined,
   green, low-drama. Not a rebalance candidate.
5. **P2 zeros are not positions** — exclude from any FOM rotation math; treat as tax-loss/closeout.

## Provenance

14 screenshots in `raw/portfolio/` (5 were >2000px, downscaled to `_resized/` for OCR).
P1 reconstructed from 3 scroll captures (head/mid/tail of the "Individual" Positions tab).
複委託 graveyard from 庫存損益 + Order Status captures. This file supersedes
`2026-05-29-snapshot-p1.md` as the current P1 state; the 5/29 file is retained for the
rotation diff above.
