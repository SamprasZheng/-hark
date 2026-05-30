"""Analyst-persona loader + FOM weight-tilt ensemble.

The principal maintains a roster of analyst personas under `analysts/` — each a
distinct voice with its own expertise domain, market focus, personality, and
signature indicators (e.g. 黃靖哲 = first-hand supply-chain / advanced-packaging
bottom-fishing; sam = long-horizon 與時間交朋友 patience). This module turns those
voices into a small, BOUNDED quantitative contribution: each persona supplies a
`fom_weight_tilt` — a micro-adjustment (少許微調) to the five FOM dimension weights
— and a `conviction_weight` saying how loudly it votes in the ensemble.

Design guardrails (so a roster of personas can never blow up the scorer):
  - Each per-dimension tilt is clamped to ±MAX_TILT (default 0.08).
  - Tilts are applied ON TOP OF the regime base weights (Fix A), then clamped
    non-negative and renormalised to sum 1.0 — so the regime stays the primary
    driver and personas only nudge.
  - The ensemble is a conviction-weighted average of active personas' tilts, so
    adding a 20th persona dilutes rather than dominates.
  - Personas do NOT touch the bubble_guard FLOOR (a regime safety mechanic) —
    only the dimension weights.

No network, no LLM. Pure, testable. Frontmatter is parsed without pyyaml (not a
dependency) via a minimal reader that handles exactly this schema.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Optional

DIMENSIONS = ("momentum", "contrarian", "cyclic", "quality", "bubble_guard")
MAX_TILT = 0.08          # per-dimension micro-tuning ceiling (|delta| <= 0.08)
DEFAULT_ANALYSTS_DIR = Path("analysts")

_FM_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*\n", re.DOTALL)


def _parse_frontmatter(text: str) -> dict:
    """Minimal YAML-subset reader for the analyst-persona schema. Handles
    top-level scalars, inline `[a, b]` lists, indented `- item` lists, and one
    level of indented `key: value` maps (for fom_weight_tilt)."""
    m = _FM_RE.match(text)
    if not m:
        return {}
    out: dict = {}
    cur_key: Optional[str] = None
    cur_kind: Optional[str] = None  # "map" | "list"
    for raw in m.group(1).splitlines():
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        indented = raw[0] in (" ", "\t")
        line = raw.strip()
        if indented and cur_key is not None:
            if line.startswith("- "):
                if not isinstance(out.get(cur_key), list):
                    out[cur_key] = []
                out[cur_key].append(line[2:].strip().strip("\"'"))
                cur_kind = "list"
            elif ":" in line:
                k, _, v = line.partition(":")
                if not isinstance(out.get(cur_key), dict):
                    out[cur_key] = {}
                out[cur_key][k.strip()] = _coerce(v.strip())
                cur_kind = "map"
            continue
        # top-level line
        if ":" not in line:
            continue
        key, _, val = line.partition(":")
        key = key.strip()
        val = val.strip()
        if val == "":
            cur_key, cur_kind = key, None
            # leave undefined until we see indented children
            out.setdefault(key, None)
        else:
            cur_key, cur_kind = None, None
            out[key] = _coerce(val)
    # clean up any keys left as None with no children
    return out


def _coerce(v: str):
    v = v.strip()
    if v.startswith("[") and v.endswith("]"):
        inner = v[1:-1].strip()
        return [x.strip().strip("\"'") for x in inner.split(",") if x.strip()] if inner else []
    if v.lower() in ("true", "false"):
        return v.lower() == "true"
    try:
        if re.fullmatch(r"-?\d+", v):
            return int(v)
        return float(v)
    except ValueError:
        return v.strip("\"'")


def _clamp_tilt(tilt: dict) -> dict:
    """Clamp every dimension delta into [-MAX_TILT, +MAX_TILT]; ignore unknown keys."""
    out = {}
    for dim in DIMENSIONS:
        d = float(tilt.get(dim, 0.0) or 0.0)
        out[dim] = max(-MAX_TILT, min(MAX_TILT, d))
    return out


def load_personas(analysts_dir: Path = DEFAULT_ANALYSTS_DIR) -> list[dict]:
    """Load every persona file carrying `type: analyst-persona` frontmatter.
    Files without that frontmatter (pure-prose voice notes) are skipped, so the
    roster can mix structured personas with free-form research notes."""
    if not analysts_dir.exists():
        return []
    personas = []
    for path in sorted(analysts_dir.glob("*.md")):
        fm = _parse_frontmatter(path.read_text(encoding="utf-8"))
        if fm.get("type") != "analyst-persona":
            continue
        fm["_file"] = path.name
        fm["fom_weight_tilt"] = _clamp_tilt(fm.get("fom_weight_tilt") or {})
        cw = fm.get("conviction_weight", 0.5)
        try:
            fm["conviction_weight"] = max(0.0, min(1.0, float(cw)))
        except (TypeError, ValueError):
            fm["conviction_weight"] = 0.5
        personas.append(fm)
    return personas


def apply_persona_tilt(base_weights: dict, tilt: dict) -> dict:
    """Apply one tilt to base regime weights: add, clamp non-negative, renormalise
    to sum 1.0. The regime stays primary; the tilt only nudges."""
    tilt = _clamp_tilt(tilt)
    raw = {d: max(0.0, float(base_weights.get(d, 0.0)) + tilt.get(d, 0.0)) for d in DIMENSIONS}
    total = sum(raw.values())
    if total <= 0:
        return dict(base_weights)
    return {d: raw[d] / total for d in DIMENSIONS}


def ensemble_weights(
    base_weights: dict,
    personas: Optional[list[dict]] = None,
    analysts_dir: Path = DEFAULT_ANALYSTS_DIR,
) -> dict:
    """Blend all active personas into a single conviction-weighted tilt, apply it
    to the regime base weights, and renormalise. Returns the final weights plus
    provenance (which personas contributed and the effective tilt)."""
    if personas is None:
        personas = load_personas(analysts_dir)
    active = [p for p in personas if p.get("status", "active") == "active"]

    if not active:
        return {
            "weights": {d: float(base_weights.get(d, 0.0)) for d in DIMENSIONS},
            "contributors": [],
            "effective_tilt": {d: 0.0 for d in DIMENSIONS},
            "note": "no active personas — regime base weights unchanged.",
        }

    conv_total = sum(p["conviction_weight"] for p in active) or 1.0
    eff_tilt = {d: 0.0 for d in DIMENSIONS}
    for p in active:
        w = p["conviction_weight"] / conv_total
        for d in DIMENSIONS:
            eff_tilt[d] += w * p["fom_weight_tilt"].get(d, 0.0)
    eff_tilt = _clamp_tilt(eff_tilt)  # the blend can never exceed the per-dim ceiling

    final = apply_persona_tilt(base_weights, eff_tilt)
    return {
        "weights": final,
        "contributors": [
            {"name": p.get("name", p.get("_file")),
             "conviction_weight": p["conviction_weight"],
             "tilt": p["fom_weight_tilt"]}
            for p in active
        ],
        "effective_tilt": eff_tilt,
        "note": (
            "Regime base weights nudged by the conviction-weighted ensemble of "
            f"{len(active)} active persona(s); renormalised to sum 1.0. Personas "
            "tilt, the regime decides."
        ),
    }
