---
type: concept
tags: [analyst-persona, ensemble, fom, weight-tilt, council, regime]
title: Analyst-Persona Ensemble (分析師議會微調)
author_role: human
source: "Principal directive 2026-05-31: analysts/ 新增角色，各有專長領域 / 量化指標 / 性格 / 市場著重點，測試加入少許 FOM 微調權重. Implemented in src/sharks/analysts/persona.py + analysts/."
---

# Analyst-Persona Ensemble

A roster of analyst personas under `analysts/`, each a distinct voice with its own
expertise domain, market focus, personality, and signature indicators — converted
into a small, **bounded** quantitative contribution: a micro-tilt (少許微調) to the
five FOM dimension weights. The personas form a *council*; their tilts are blended
by conviction and applied on top of the regime weights (see
[[regime-gated-scoring]]), then renormalised. Per [[../../sharks]], **the regime
decides; the personas only nudge.**

## Why a council, not a single brain

Different analysts have genuinely different, defensible edges: 黃靖哲 reads
first-hand Taiwan supply-chain and buys emerging themes *early* (momentum-up,
bubble_guard-down); `sam` is a long-horizon contrarian who buys weakness and trims
euphoria (contrarian-up, momentum-down). Neither is "right" — they are right in
*different regimes and on different names*. An ensemble lets the book hold both
biases and only tilt where the council actually agrees; where they disagree
(momentum), the conviction-weighted blend partially cancels — which is the correct
behaviour, not a bug.

## The mechanism (bounded by construction)

`src/sharks/analysts/persona.py`:

- **`load_personas()`** reads every `analysts/*.md` carrying `type:
  analyst-persona` frontmatter. Pure-prose voice notes (no such frontmatter) are
  skipped, so research colour and voting personas can coexist in one folder.
- **Each `fom_weight_tilt` is clamped to ±0.08 per dimension** at load. A persona
  can never become a regime override — by design.
- **`apply_persona_tilt(base, tilt)`** adds the tilt to the regime base weights,
  clamps non-negative, and renormalises to sum 1.0.
- **`ensemble_weights(base, personas)`** blends all *active* personas into one
  conviction-weighted tilt (`conviction_weight ∈ [0,1]`), then applies it. Adding
  a 10th persona *dilutes* the others — the blend is an average, not a sum.
- **`status: draft`** loads but does not vote (stage and inspect a tilt before
  activating); **`retired`** is ignored.
- Personas never touch the **bubble_guard floor** — that is a regime safety
  mechanic, not a persona lever.

Worked example (huang conviction 0.6 + sam conviction 0.4 on neutral weights):
the blend nets to a *mild-contrarian* tilt (contrarian +0.038, momentum +0.014,
bubble_guard −0.014) — they cancel on momentum, agree on contrarian. Final weights
still sum to 1.0.

## The validation contract (no opinion without evidence)

A tilt is a hypothesis, not a fact. Every persona tilt must be checked against the
IC study ([[fom-predictive-validity]]): the tilt should **improve, or at least not
degrade, the 3-6m Information Coefficient** on the slice the persona claims
expertise over. A tilt with no IC support is an opinion and stays at low
`conviction_weight` or `status: draft`. This keeps the council honest — voices earn
weight by measured edge, not by eloquence.

## What this assumes — and where it breaks

- **Frontmatter quality.** A mis-specified tilt silently nudges the scorer; the
  ±0.08 clamp bounds the damage but cannot fix a wrong sign. Review tilts like
  code.
- **Correlated personas.** Five momentum bulls are not a diverse council — they
  are one loud vote. Diversity of *bias*, not count, is what makes the ensemble
  robust. (A future check: warn when active tilts are highly correlated.)
- **Tilts are not stock picks.** A persona expresses *weighting* bias, not
  individual buy calls; the evidence gate ([[evidence-gated-rebalance]]) still
  governs any actual switch.

## See also

- [[regime-gated-scoring]] — the base weights personas tilt on top of
- [[fom-predictive-validity]] — where every tilt must be re-validated
- [[evidence-gated-rebalance]] — the gate that still governs actual rebalances
- [[separation-mind]] — guards the council against 分別心 / single-voice capture
- [[../02-signal-taxonomy]] — the dimensions the tilts re-weight
- [[../05-decision-rubric]] — where the ensemble weights enter the decision
- [[../../sharks]] — constitution
