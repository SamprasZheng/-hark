---
type: concept
tags: [moonshot, 飆股, volume, insider, hype, evidence-gate, sleeve, high-variance]
title: Moonshot Hunter — 飆股獵手 (evidence-gated, the opposite of FOM)
author_role: human
source: "Principal directive 2026-05-31: 我也要買飆股 — 著重交易量/insider/炒作/巨頭合作/打入供應鏈. Implemented in src/sharks/scoring/moonshot_hunter.py."
---

# Moonshot Hunter — 飆股獵手

The scorer for the ring-fenced high-variance sleeve. FOM is built to *avoid* the
parabola (bubble_guard penalises extension); the moonshot hunter is built to
*ride* it — because the NASDAQ-100 答案 showed FOM structurally cannot pick the
BKNG +343% / TSLA +743% winners (overlap 0.36/3). Catching those is a **different
job with a different risk profile**, so it is a separate sleeve, capped, never
mixed into the core. Per [[../../sharks]], it is also where discipline matters
most — this sleeve is exactly how the 複委託 graveyard (−90/−100% husks) was built.

## The deliberate inversion of FOM

| | FOM (core) | Moonshot hunter |
|---|---|---|
| Stance on a parabola | penalise (bubble_guard) | **reward** (hype_score) |
| Horizon | 3-6 months | days-to-weeks, opportunistic |
| What it wants | quality + durable momentum | ignition: volume + acceleration + catalyst |
| Sizing | core | **ring-fenced ≤ sleeve cap, small per name** |

`hype_score()` is literally the inverse of `bubble_guard`: it rewards the raw
recent run + leg-over-leg acceleration + realised-vol expansion. That is *not* a
mistake — the high-variance sleeve exists to capture the vertical move, accepting
the risk.

## The five signals (the principal's criteria)

`src/sharks/scoring/moonshot_hunter.py`:

1. **交易量 — `volume_surge_score`** (price-computable): recent vs trailing volume
   ratio through a log curve (1×→0, ~3×→50, ~10×→100). The ignition tell.
2. **炒作 — `hype_score`** (price-computable): parabola + acceleration + vol
   expansion (the bubble_guard inversion above).
3. **Insider buying — `insider_buying`** (evidence): qualitative, A/B-grade only.
4. **巨頭合作 — `bigtech_partnership`** (evidence): qualitative, A/B-grade only.
5. **打入供應鏈 design-win — `supply_chain_design_win`** (evidence): qualitative.

`moonshot_score` blends volume + hype + evidence into 0-100. Leveraged-long single
-stock ETFs (TSLL/MSTX/CONL/LULG/CRWG/AAPB/FBL/MSFU…) are tagged
`instrument=leveraged_etf` and are *eligible* moonshot vehicles (their decay is
scored separately by `src/sharks/scoring/leveraged_etf.py`).

## The line between a disciplined moonshot and a lottery ticket

The evidence gate is the whole discipline. Only A/B-grade confirmed catalysts
count (mirrors `daily_health_check.CONFIRMING_GRADES`). The critical rule:

- **price-heat HIGH + ZERO confirmed evidence → `PURE-HYPE-NO-EVIDENCE`** — a
  *warning*, never a buy. This is exactly the 複委託-graveyard pattern (chasing a
  hot chart with no catalyst). The same parabola scores ~53 / flagged with no
  evidence vs ~87 / `EVIDENCE-BACKED-MOONSHOT` once two A-grade catalysts confirm.
- **price-heat HIGH + ≥1 confirmed catalyst → `EVIDENCE-BACKED-MOONSHOT`** — the
  only tier that is actionable, and still only at sleeve-cap size.

So price tells you *when* it is moving; the evidence gate alone decides *whether*
you are allowed to act. Hype without a catalyst is a refusal, by construction.

## What this assumes — and where it breaks

- **Evidence quality is the system.** A falsely-confirmed partnership/insider flag
  defeats the gate. Source-grade honestly; default to unconfirmed.
- **Insider + partnership data are not price feeds.** They are researcher inputs
  (SEC Form-4, 8-K, press releases) fed in with a source grade — the module scores
  what it is given, it does not invent catalysts.
- **Sleeve discipline is external.** The scorer ranks; the ≤-cap sizing and the
  ring-fence live in [[../08-risk-and-position]] + the sleeve classifier. A great
  moonshot score is never a reason to exceed the cap.

## See also

- [[return-horizon-structure]] — why the moonshot sleeve is separate from FOM/value
- [[evidence-gated-rebalance]] — the A/B-grade evidence discipline this enforces
- [[nasdaq100-calibration]] — the proof FOM cannot pick moonshots (0.36/3 overlap)
- [[farmer-mindset]] — the chase-without-evidence trap this guards against
- [[../08-risk-and-position]] — the sleeve cap that bounds it
- [[../02-signal-taxonomy]] — where volume/news signals sit
- [[../../sharks]] — constitution
