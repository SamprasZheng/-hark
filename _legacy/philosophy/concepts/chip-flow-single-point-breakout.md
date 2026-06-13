---
type: concept
tags: [chip-flow, breakout, state-machine, wash-out, accumulation, technical, structural, analyst-model, advisor-source]
title: Chip-Flow & Single-Point Breakout (籌碼水流與單點突破)
author_role: human
source: "External investment advisor — formalised by user 2026-05-29"
---

# Chip-Flow & Single-Point Breakout (籌碼水流 + 單點突破)

A structured **three-state state machine** for catching the precise inflection where a heavily-washed-out small-cap turns into a high-conviction long. Originated by an external investment advisor; formalised here as the second analyst model internalised into Sharks (the first being Andy's constitution itself). The model overlaps strongly with [[../../sharks]] principles 1 (動態模型與概率), 5 (魚缸生態與資金博弈), 6 (客觀分水嶺), and bottoming-pattern recognition #2 (縮量也不下跌) — see explicit mapping in §Integration below.

> **Why this lives in `concepts/` (not in `sharks.md`)**: The constitution is Andy's. This model is another analyst's. They are compatible but distinct sources. Per [[../../sharks]] line 10, constitution is human-only and never modified by ingest — new analyst voices land as concept pages, not as edits to the constitution.

---

## Module 1 — Data Ingestion (數據採集層)

The model assumes both quant signals and narrative signals on a daily cadence.

- **Low-frequency (EOD)**: daily close, daily volume, institutional net-buy/sell (法人三大), key broker-branch net flow (主力分點進出).
- **News & sentiment (hourly)**: financial-news headlines + body, NLP-classified as bullish/bearish; the key derivative is **"news vs price reaction divergence"** — e.g. a bearish headline that the tape refuses to discount.

**Mapping to current $hark data layer**:
- US tickers — `src/sharks/data/yfinance_client.py` (EOD OHLCV) + `finnhub_client.py` (news) cover most of the inputs.
- TW tickers — **no client exists** for 三大法人 / 主力分點. Phase 2 must add `src/sharks/data/twse_client.py` or a paid wrapper (FinMind / 富邦 / 永豐). Without it, the model degrades to OHLCV-only on Taiwan names — which **breaks State 0 detection** (no institutional confirmation).
- US degradation path: when institutional data is sparse, substitute with 13F drift + dark-pool prints aggregated via Finnhub or a future broker feed.

---

## Module 2 — Universe Selection (靜態篩選)

A pre-filter applied before any state-machine evaluation. The model is explicitly designed for **small-to-mid cap with light float**, because the chip-flow thesis depends on a tractable orderbook a single main player can dominate.

- **Cap filter**: exclude large-cap index heavyweights.
- **Thematic tag filter**: ticker must carry a current dominant-narrative tag (AI infra / policy beneficiary / earnings turnaround / supply-chain reshuffle).
- **Liquidity floor**: minimum average daily turnover that allows clean entry/exit at the user's intended size.

**Mapping to $hark**: extend `watchlist/universe.yaml` with a dynamic **Tier 3** bucket populated by this filter. Distinguish from [[supply-chain-bottleneck]] which targets the upstream chokepoint at the top of the food chain — this model targets the **follow-on small names below the chokepoint** that ride the same narrative.

---

## Module 3 — Core Logic State Machine (核心邏輯狀態機)

Every ticker in the filtered universe is classified each EOD into exactly one of three states.

### State 0 — Accumulation (籌碼沉澱)

**Triggers**:
- Price in a range / consolidation (no fresh swing high or low for N sessions — N tuned in Phase 4 backtest).
- Daily volume **dries up well below the monthly average**.
- **Chip-flow divergence**: despite the dry volume, institutional / key-broker net flow shows a **continuous net-buy streak** over the lookback window.

**System reading**: water is pooling. Retail has left; the main player is feeding. Add to the **long-watchlist** bucket; do **NOT** open a position. State 0 alone is necessary-but-not-sufficient.

**$hark cross-reference**: this is the bullish-divergence branch of [[price-volume-divergence]] enriched with explicit institutional confirmation, occurring inside a [[cycle-resonance]] half-year-correction window.

### State 1 — Wash-out (洗盤騙線)

**Triggers**:
- Price breaks the key support (20MA, or the lower edge of the consolidation range).
- The break happens on **contracting, not panicked, volume** — no climactic sell.
- Institutional / branch data shows **no large-scale main-player dump**.
- A bearish news headline drops but the tape **refuses to follow through** (利空不跌).

**System reading**: a deliberate flush to stop out weak hands. Still observation phase. **Do not catch the knife** — wait for price to reclaim the broken support before re-engaging the State 0 → State 2 path.

**$hark cross-reference**: this is the operational form of [[last-snow]] (peak bearishness + structural bottom) combined with the trigger condition for [[separation-mind]] (this is exactly when retail capitulates because of comparative pain).

### State 2 — Single-Point Breakout (單點突破) — BUY SIGNAL

**Triggers**:
- Price reclaims the broken support and **breaks the consolidation high**.
- **Volume expansion**: that day's volume is ≥ 2× the trailing monthly average.
- EOD chip data confirms institutional AND main-player are **simultaneously large net buyers** on the breakout bar.

**System reading**: wash-out is over; real money is lighting the fuse. **Entry signal fires.**

**$hark cross-reference**: this is the precise sub-instance of [[../10-strategies]] Strategy A (consolidation breakout). Strategy A's general trigger ("close clears the consolidation band on volume") is the same shape; this model adds the **chip-flow confirmation** as a non-negotiable gating clause, which Strategy A treats as optional.

---

## Module 4 — Execution & Risk (雙軌執行 + 風控)

### Long-horizon low-frequency mode (primary, ~80%)

- EOD-only evaluation. State machine runs after market close.
- Execution: open the next session at the open or near-close, never intraday-chased.
- Filters intraday noise — this is the model's default home.
- **$hark cross-reference**: mirrors the **Low** branch of [[../07-mode-switch]]. Default for both US (after-hours) and TW (afternoon) routines.

### High-frequency short mode (dynamic switch, ~20%)

- Minute-bar price+volume + hourly news sentiment.
- Activated for: weekend crypto, or supervised hours in front of the screen on a high-volatility name.
- **Inherits the same market-state gating** as $hark High mode: requires `SHARKS_HIGH_FREQ_OK=1`, VIX inside [12, 18], no earnings within ±3 sessions, no Fed/CPI/NFP in window.

### Iron-clad risk module

- **False-breakout stop**: if price closes below the low of the breakout day's bar AND EOD chip data shows institutional / main-player turning net-seller → **hard stop**, no discretion. (The bar low is the model's pre-committed [[objective-watershed]].)
- **Trend-trail exit**: ride the 10MA. Close below 10MA **plus** chip-flow dispersion (broker concentration falling) → scale out.
- **$hark cross-reference**: layers cleanly under the existing [[../08-risk-and-position]] sizing and DD-halt rules; does not override them.

---

## Integration into the Sharks framework

### 4-dimension signal-taxonomy mapping (per [[../02-signal-taxonomy]])

| Trigger from this model | $hark dimension | Notes |
|---|---|---|
| EOD institutional / main-player net-buy | **Fundamental** (treats fund flow as fundamental capital allocation) | Earns slot-eligibility, not slot-fill alone |
| News-bearish but price holds (利空不跌) | News × Technical conflict, Technical wins | Per matrix row "News ↔ Technical (same direction)" inverted, treated as Technical priority |
| Volume-expansion breakout | **Technical** | Subject to 30% bucket-size cap if standing alone |
| Dominant-narrative tag carry | **News / Sentiment** | Modifier, never primary |

State 2 firing **combines Fundamental (institutional confirm) + Technical (volume breakout) + News (narrative tag)** simultaneously — this earns the "confluence" tag under the four-aligned row of the arbitration matrix and is eligible for an upper bucket-size cap.

### Conflict arbitration with Strategy B (momentum)

- **Same direction**: confluence. Up-tier the size cap.
- **Opposite direction**: this model wins. Chip-flow + breakout is anchored in Fundamental+News, which the matrix prioritises over sentiment-only momentum.
- **Same direction, different time horizon**: this model's trade is long-horizon (1–6 month bucket per [[../01-time-horizon]]); Strategy B is short-horizon (≤ 6 weeks). They can coexist as two independent slots on the same ticker.

### Signal contract (per [[../05-decision-rubric]])

- **State 2 firing** → emit to `outputs/picks-YYYY-MM-DD.json` as a `long_new` row.
- **State 1 persisting** → emit as a `position_followup` row with status `watch`.
- **False-breakout stop firing** → emit as a `position_followup` row with status `exit-flag`.

---

## Implementation hooks (Phase 2+)

- **New scorer**: `src/sharks/scoring/chip_flow.py`
  - `is_accumulation(ticker, as_of) -> Optional[float]` — State 0 confidence in [0, 1]
  - `is_wash_out(ticker, as_of) -> Optional[float]` — State 1 confidence
  - `is_breakout(ticker, as_of) -> Optional[BreakoutSignal]` — State 2 + the breakout-bar low (the pre-committed stop)
  - All three honour `as_of` for point-in-time discipline per [[../09-point-in-time]]
- **New data client**: `src/sharks/data/twse_client.py` for TW 三大法人 / 主力分點 — Phase 2 deliverable.
- **State persistence**: append daily classification to `outputs/state-YYYY-MM-DD.jsonl` per ticker, so future ML / backtest has clean ground truth.
- **Thresholds left undefined here on purpose**: the consolidation length N, the volume-dry-up ratio, the breakout volume-multiple, the wash-out severity — all tuned by walk-forward backtest per [[../04-sector-and-finviz]] Rule 1 (train/val/test split). Hard-coding magic numbers in this concept page would shortcut the discipline.

---

## What this model assumes — and where it breaks

- **Assumes TW institutional data is reachable EOD** — in practice there is T+1 latency on some 主力分點 sources, which delays State 0 confirmation by one session.
- **Assumes 主力分點 feeds are stable** — broker-branch APIs are not officially public; production use requires paid (FinMind / Tej / 富邦) or self-scraped pipelines with their own SLA risk.
- **US degradation**: in US markets without 三大法人 data, replace with 13F quarterly drift + dark-pool aggregate prints. This **lowers signal frequency** (quarterly not daily) but preserves the institutional-confirmation logic.
- **Crypto adaptation**: replace institutional flow with on-chain whale-wallet aggregate net-flow + exchange reserve changes. Volume-expansion breakout still applies. News sentiment shifts to crypto-Twitter NLP.

---

## Analyst-Model Interface (schema for the next analyst to internalise)

Every future analyst model added to `philosophy/concepts/` under the `analyst-model` tag should specify these five contracts. This concept page acts as the reference implementation.

| # | Contract | What this model provides | Where to look in $hark |
|---|---|---|---|
| 1 | **States + transitions** | State 0 (Accumulation) → State 1 (Wash-out) → State 2 (Breakout); transitions per §Module 3 | this file |
| 2 | **Signal dimensions** | Fundamental (institutional) + Technical (volume+price) + News (narrative + 利空不跌) | [[../02-signal-taxonomy]] |
| 3 | **Entry contract** | State 2 → `long_new` slot; State 1 → `position_followup:watch`; stop → `position_followup:exit-flag` | [[../05-decision-rubric]] |
| 4 | **Risk module** | False-breakout stop @ breakout-bar low; 10MA trend-trail exit | [[../08-risk-and-position]] |
| 5 | **Mode routing** | Low mode primary; High mode gated on `SHARKS_HIGH_FREQ_OK=1` + VIX/earnings/Fed window | [[../07-mode-switch]] |

Future drop-ins (e.g. "Analyst X's event-arbitrage", "Analyst Y's sector-rotation") clone this file, replace §Module 3 with their own state machine, and re-map §Integration tables.

---

## Anti-patterns (what not to call a State 2)

- **Volume expansion without chip-flow confirmation** — a retail-driven gap-and-go without institutional net-buy is **not** State 2 in this model. It might be a Strategy B momentum trade, but it does not earn the chip-flow confluence tag.
- **Chip-flow confirmation without price breakout** — institutional accumulation alone is State 0, not State 2. The model deliberately refuses to anticipate the breakout from the accumulation phase; it waits for the trigger bar.
- **"Looks like it's washing out"** — State 1 requires the four explicit conditions (support break + volume contraction + no institutional dump + bearish-news-no-follow-through). Eyeballing the chart and calling it wash-out is the same cognitive trap [[separation-mind]] warns about.

---

## See also

- [[../../sharks]] — Andy's constitution; this model is compatible with principles 1, 5, 6 and bottoming-pattern #2
- [[../02-signal-taxonomy]] — four-dimension framework and conflict-arbitration matrix
- [[../05-decision-rubric]] — daily 10-signal contract this model emits into
- [[../07-mode-switch]] — Low / High frequency routing inherited verbatim
- [[../08-risk-and-position]] — sizing, DD-halt, and exit rules layered under this model
- [[../09-point-in-time]] — `as_of` discipline required by every scorer in §Implementation hooks
- [[../10-strategies]] — Strategy A, of which this model is the precise sub-case
- [[price-volume-divergence]] — bullish-divergence dry-up pattern at State 0
- [[cycle-resonance]] — half-year-correction window inside which State 0 lives
- [[last-snow]] — the macro counterpart to State 1 (peak bearishness)
- [[separation-mind]] — the cognitive trap State 1 inflicts on retail
- [[supply-chain-bottleneck]] — structural alpha at the top of the food chain (this model targets the bottom)
- [[objective-watershed]] — the breakout-bar low used as the pre-committed stop
