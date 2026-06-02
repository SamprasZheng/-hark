"""Macro-analog matching — mechanism-set overlap over human-curated episodes.

Per `philosophy/_proposals/ai-quant-us-roadmap-merge-2026-05-30.md` §4 and
`philosophy/concepts/macro-analog-matching.md` (proposed). This module is a
**decision-support / hypothesis-generation** tool, NOT a predictive quant signal.

Design constraints enforced here (from the reviewer audit):

  1. **No high-dim clustering.** Episodes are described by a 4-axis regime cube
     (Growth / Inflation / Liquidity / Credit) and a set of named *mechanisms*.
     Matching is set-overlap over the mechanisms — explainable, sanity-checkable,
     immune to the curse of dimensionality that kills cosine/k-means at N<10.
  2. **Mechanism set, not single-year nearest neighbour.** Output is a ranked
     *distribution* of episodes sharing mechanisms with the present, not a single
     "you are 87% like 1973" label.
  3. **Decision support, not prediction.** The output schema deliberately EXCLUDES
     `probability`, `direction`, `verdict`, `forecast`, `score`, `target` — the
     same banned-key set as `docs/LLM-BACKTEST-PROTOCOL.md` defense #1. Anything
     consuming this module (human or LLM) is forbidden from converting overlap
     into a probability.
  4. **Open-ended human curation.** Episodes are immutable JSON files under
     `data/macro_analog_events/`. ML over them is gated until >=50 events with
     >=5 per archetype exist (not implemented; intentionally absent).

Zero external dependencies (stdlib json only) — matches the JSON-on-disk pattern.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

# Keys that must never appear in this module's output — converting an analog
# overlap into one of these is the misuse the concept page forbids.
BANNED_OUTPUT_KEYS = frozenset(
    {"probability", "direction", "verdict", "forecast", "score", "target", "signal"}
)

REGIME_CUBE_AXES = ("growth", "inflation", "liquidity", "credit")

DEFAULT_EVENTS_DIR = Path("data/macro_analog_events")


def load_events(events_dir: Path = DEFAULT_EVENTS_DIR) -> list[dict[str, Any]]:
    """Load every curated episode JSON. Skips malformed files rather than
    crashing the caller. Each event keeps its source path under ``_path``."""
    events_dir = Path(events_dir)
    if not events_dir.is_dir():
        return []
    out: list[dict[str, Any]] = []
    for path in sorted(events_dir.glob("*.json")):
        try:
            event = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if "mechanisms" not in event or "event_id" not in event:
            continue
        event["_path"] = str(path)
        out.append(event)
    return out


def mechanism_overlap(
    current_mechanisms: list[str] | set[str],
    event: dict[str, Any],
) -> dict[str, Any]:
    """Set-overlap between the present mechanisms and one episode's mechanisms."""
    current = {m.strip().lower() for m in current_mechanisms}
    event_mechs = {m.strip().lower() for m in event.get("mechanisms", [])}
    shared = sorted(current & event_mechs)
    union = current | event_mechs
    return {
        "overlap_count": len(shared),
        "overlapping_mechanisms": shared,
        "jaccard": round(len(shared) / len(union), 3) if union else 0.0,
    }


def cube_distance(cube_a: dict[str, str], cube_b: dict[str, str]) -> int:
    """Number of the 4 regime-cube axes whose labels DIFFER. 0 = identical
    qualitative regime; 4 = opposite on every axis. A coarse, human-readable
    sanity companion to the mechanism overlap — NOT a similarity score to rank on."""
    diff = 0
    for axis in REGIME_CUBE_AXES:
        if cube_a.get(axis) != cube_b.get(axis):
            diff += 1
    return diff


def match(
    current_mechanisms: list[str] | set[str],
    current_cube: dict[str, str] | None = None,
    events_dir: Path = DEFAULT_EVENTS_DIR,
    k: int = 5,
) -> dict[str, Any]:
    """Rank curated episodes by mechanism-set overlap with the present.

    Returns a decision-support object (NO probability / direction). Episodes with
    zero mechanism overlap are dropped. Ties on overlap_count are broken by
    Jaccard, then (if a current_cube is supplied) by smaller cube_distance.
    """
    events = load_events(events_dir)
    scored: list[dict[str, Any]] = []
    for event in events:
        ov = mechanism_overlap(current_mechanisms, event)
        if ov["overlap_count"] == 0:
            continue
        entry = {
            "event_id": event["event_id"],
            "label": event.get("label", ""),
            "period": event.get("period", ""),
            "overlap_count": ov["overlap_count"],
            "overlapping_mechanisms": ov["overlapping_mechanisms"],
            "jaccard": ov["jaccard"],
            "regime_cube": event.get("regime_cube", {}),
            "trigger": event.get("trigger", ""),
            "outcomes": event.get("outcomes", {}),
            "pit_note": event.get("pit_note", ""),
        }
        if current_cube is not None:
            entry["cube_axes_differing"] = cube_distance(current_cube, entry["regime_cube"])
        scored.append(entry)

    def _sort_key(e: dict[str, Any]):
        return (
            -e["overlap_count"],
            -e["jaccard"],
            e.get("cube_axes_differing", 0),
        )

    scored.sort(key=_sort_key)

    result = {
        "method": "mechanism-set-overlap-v1",
        "disclaimer": (
            "DECISION SUPPORT, NOT PREDICTION. This is a ranked distribution of "
            "historical episodes sharing mechanisms with the present. It does not "
            "imply a probability or a direction. Use it to generate hypotheses and "
            "checklists ('episode X was triggered by Y — is Y present now?'), never "
            "as a forecast. See docs/LLM-BACKTEST-PROTOCOL.md."
        ),
        "current_mechanisms": sorted({m.strip().lower() for m in current_mechanisms}),
        "current_cube": current_cube or {},
        "events_considered": len(events),
        "matches": scored[:k],
    }
    _assert_no_banned_keys(result)
    return result


def _assert_no_banned_keys(obj: Any) -> None:
    """Defensive: guarantee the output never carries a prediction-flavoured key.
    Recurses dicts/lists. Raises if a banned key is found (a programming error)."""
    if isinstance(obj, dict):
        for key, value in obj.items():
            if key in BANNED_OUTPUT_KEYS:
                raise AssertionError(
                    f"macro_analog output must not contain banned key {key!r} "
                    f"(decision-support, not prediction)"
                )
            _assert_no_banned_keys(value)
    elif isinstance(obj, list):
        for item in obj:
            _assert_no_banned_keys(item)
