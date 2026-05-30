---
type: analyst-persona
name: CHANGE_ME
expertise: [domain-1, domain-2]
market_focus: [sector-or-theme-1, sector-or-theme-2]
personality: one-line-character
fom_weight_tilt:
  momentum: 0.0
  contrarian: 0.0
  cyclic: 0.0
  quality: 0.0
  bubble_guard: 0.0
conviction_weight: 0.5
signature_indicators:
  - signature_indicator_1
  - signature_indicator_2
status: draft
---

# <Persona display name>

> One-paragraph character sketch: who this analyst is, how they see the market,
> what edge they claim.

## Expertise & market focus

What sectors / themes / regions this persona covers, and why their read there is
worth weighting.

## Signature indicators

For each `signature_indicators` entry, describe the signal in words: what it
measures, what confirms it, what invalidates it. (These are documentation today;
promote the high-value ones to real `src/sharks/` scorers as they prove out.)

## FOM weight tilt — rationale

Justify each non-zero `fom_weight_tilt` delta. Example: "momentum +0.04 because I
enter emerging themes on the first leg, before mass recognition." Keep |delta| <=
0.08; back it with the IC study before raising conviction.

## Relationship to the constitution & other personas

How this persona's bias composes with (or deliberately opposes) others, and where
it must still defer to [[../sharks]] (the constitution) and the regime classifier.
