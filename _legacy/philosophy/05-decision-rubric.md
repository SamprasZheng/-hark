---
type: synthesis
tags: [decision-rubric, daily-10-signal, output-schema, philosophy]
title: Daily 10-Signal Decision Rubric
author_role: human
---

# 05 · Daily 10-Signal Decision Rubric

Resolves Gemini review point #2 (each day producing 10 new picks against a 1-12m horizon is a flow-vs-stock contradiction) and codex review point #9 (forced quota produces low-quality fill).

## The 10-signal contract

Every daily `wiki/05_recommendations/YYYY-MM-DD.md` and the companion `outputs/picks-YYYY-MM-DD.json` carry exactly 10 slots, allocated as:

| Slot range | Bucket | Description |
|---|---|---|
| 1–2 | `long_new` | New long entries that just earned a quadrant placement in 多頭真漲 |
| 3–4 | `short_new` | New short entries (Mag 7 Put / inverse ETF only — see [[03-long-short-taxonomy]]) |
| 5–10 | `position_followup` | Adjustments to existing positions: add / trim / exit / hold-update |

## The empty-slot rule

If no qualifying candidate exists for a slot, the slot value is `null`. **Padding is forbidden.** The Risk Officer rejects any submission that fills a slot with a candidate whose confidence < 0.50 just to hit 10.

Aggregate "no-action" days are normal. The system's edge depends on selectivity. A typical month should contain:

- 2–5 full days with all 10 slots filled
- ~10 days with 6–9 slots filled
- ~5 days with 3–5 slots filled
- 0–2 full no-action days

If the no-action frequency exceeds 8 / month, the screener is too strict (revisit [[04-sector-and-finviz]] thresholds). If full-fill days exceed 50% of the month, the screener is too loose.

## The JSON schema

`outputs/picks-YYYY-MM-DD.json` validates against:

```json
{
  "schema_version": 1,
  "as_of": "2026-05-28T20:00:00-04:00",
  "regime": {
    "macro_state_ref": "wiki/01_macro_state.md@2026-05-28",
    "vix": 14.2,
    "cycle_resonance_active": false,
    "high_freq_mode_eligible": false
  },
  "signals": [
    {
      "slot": "long_new_1",
      "ticker": "NVDA",
      "tier": 1,
      "quadrant": "genuine_bull",
      "thesis": "Brief one-line thesis. Detail in evidence_paths.",
      "horizon_days": 90,
      "entry_zone": {"low": 458.0, "high": 472.0},
      "stop_loss": 432.0,
      "invalidation": {
        "price": 432.0,
        "time_stop_days": 135,
        "catalyst": "Blackwell launch delay > 1 quarter OR CoWoS capacity downgrade"
      },
      "size_pct": 4.0,
      "confidence": 0.72,
      "evidence_paths": [
        "raw/earnings/nvda-2026Q1.md",
        "wiki/02_mag7_bottleneck.md#cowos",
        "philosophy/entities/nvidia.md"
      ],
      "author_role": "compiler"
    }
  ],
  "no_action_buckets": ["short_new_2"],
  "footer": {
    "compiled_by": "Claude Opus 4.7 + Risk Officer review",
    "lint_passed": true,
    "duration_ms": 18400
  }
}
```

## The Markdown companion

`wiki/05_recommendations/YYYY-MM-DD.md` is the human-readable view. It MUST:

- Carry frontmatter with `as_of_timestamp` matching the JSON's `as_of`
- Reference `regime.macro_state_ref` via `[[link]]`
- Include one paragraph per slot rendering the thesis + key evidence
- End with a `## Discarded candidates` section listing tickers that screened in but were rejected, with the reason (which iron rule, which sentiment z-score, etc.). Discarded candidates are valuable training data and must never be lost.

## Confidence calibration

Confidence in `[0, 1]` and means:
- `0.50` — minimum threshold for slotting. Below this, slot stays `null`.
- `0.65` — typical good signal. Eligible for full bucket size cap.
- `0.80+` — confluence: all four signal dimensions aligned without contradiction. Rare.

The Risk Officer reviews confidence scores against the conflict-arbitration outputs in [[02-signal-taxonomy]]. Scores claimed without conflict-matrix support are corrected downward.

## Position followup taxonomy (slots 5–10)

Each followup must declare its action type:

- `add` — increase size; requires fresh A-grade source supporting thesis strengthening
- `trim` — reduce size by a defined percentage; reasons include partial profit, sector cap breach, correlation drift
- `exit` — close position; triggered by invalidation hit, time stop, or thesis falsification
- `hold_update` — no size change but thesis evidence updated; logged for next ratification window

Followups that are simply "still holding, no change" do not earn a slot — they remain in `wiki/positions.md` with the last-update timestamp.

## Anti-pattern: spread-by-slot

A common implementation bug is to spread weak candidates across slots to maximise published-pick count. The matrix above prevents this by binding each slot to a quadrant condition. A single high-confidence multi-day position followup MAY occupy multiple followup slots (e.g. an exit + a same-ticker re-entry on a different bucket), but each occurrence must declare its own confidence and evidence.
