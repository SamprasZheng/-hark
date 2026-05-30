# `analysts/` — the persona roster

Each file here is an **analyst persona**: a distinct voice with its own expertise
domain, market focus, personality, signature indicators, and a **bounded FOM
weight tilt** (少許微調). The personas form a council — their tilts are blended by
conviction and applied on top of the regime weights (Fix A), then renormalised.
The regime decides; the personas only nudge.

Loader + ensemble: `src/sharks/analysts/persona.py`. Concept:
`philosophy/concepts/analyst-persona-ensemble.md`.

## Two kinds of file

1. **Structured personas** — carry `type: analyst-persona` frontmatter (below) and
   contribute a quantitative tilt. These are loaded by `load_personas()`.
2. **Free-form voice notes** — pure prose (e.g. a YouTube transcript summary) with
   no such frontmatter. These are skipped by the loader; keep them for research
   colour. Add the frontmatter when you want a voice to start voting.

## Frontmatter schema (copy `_TEMPLATE.md`)

```yaml
---
type: analyst-persona            # REQUIRED — marks the file as a voting persona
name: huang                      # short id used in provenance
expertise: [aipc, advanced-packaging, glass-substrate, first-hand-supply-chain]
market_focus: [taiwan-semis, aipc, robotics]
personality: first-hand-bottom-fisher
fom_weight_tilt:                 # micro-tuning; each delta clamped to +/- 0.08
  momentum: 0.04
  contrarian: 0.02
  cyclic: 0.0
  quality: -0.03
  bubble_guard: -0.03
conviction_weight: 0.6           # how loudly this persona votes [0..1]
signature_indicators:            # this persona's own signals (described in body)
  - first_hand_supply_chain_lead
  - packaging_round_to_square
status: active                   # active | draft | retired
---
```

## Rules

- **Tilts are bounded.** Each `fom_weight_tilt` dimension is clamped to ±0.08 at
  load. You cannot turn a persona into a regime override — by design.
- **The five dimensions** are `momentum / contrarian / cyclic / quality /
  bubble_guard` (must match `src/sharks/scoring/fom.py`).
- **Personas never touch the bubble_guard FLOOR** — that is a regime safety
  mechanic, not a persona lever.
- **Conviction dilutes.** Adding a 10th persona reduces each one's share of the
  blend; the ensemble is a conviction-weighted average, not a sum.
- **`status: draft`** loads but does NOT vote — use it to stage a new persona and
  inspect its tilt before activating.
- **Validate before trusting a tilt.** Back the tilt with the IC study
  (`src/sharks/backtest/fom_validation_backtest.py`): a persona's tilt should
  improve, or at least not degrade, the 3-6m IC on the slice it claims expertise
  over. A tilt with no IC support is just an opinion.

## Worked examples in this folder

- `huang.md` — 黃靖哲: first-hand Taiwan supply-chain / advanced-packaging
  bottom-fisher. Tilts momentum + contrarian up, quality + bubble_guard down
  (buys emerging themes early, before the ATH-extension penalty bites).
- `sam.md` — long-horizon 與時間交朋友 patience. Tilts contrarian + quality up,
  momentum down, bubble_guard up (trims into tops: 高基期不必難捨難分). The
  deliberate opposite of huang — together they demonstrate the blend.
