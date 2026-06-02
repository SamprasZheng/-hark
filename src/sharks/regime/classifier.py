"""Regime classifier — gates FOM weights based on market state.

Consumes the latest breadth-indicator + liquidity-signals JSON artefacts
(produced by sharks.regime.breadth_indicator and sharks.regime.liquidity_signals)
and emits a regime label + a weights table that downstream scoring (fom.py)
applies in place of the default mean-reversion-biased weights.

Five regimes:
  - bull_trend     : breadth NORMAL + liquidity GREEN + SPX > 200dma
                     → momentum-heavy, bubble_guard partially muted
  - late_bull      : breadth OVERHEATED + liquidity YELLOW (current default
                     state in mid-2026 per breadth/liquidity outputs)
                     → momentum-tilted but bubble_guard kept; floor at -50
                       so single-name parabolic doesn't fully drown the signal
  - neutral        : nothing definitive triggered → current canonical FOM
                     weights (25/25/15/15/20)
  - risk_off       : breadth OVERHEATED + liquidity ORANGE/RED, OR
                     SPX < 200dma → defensive, contrarian-heavy
  - capitulation   : breadth CAPITULATION → aggressive contrarian, quality up

Each regime returns:
  {
    "label": str,
    "reasons": [str, ...],
    "weights": {momentum, contrarian, cyclic, quality, bubble_guard},  # sums to 1
    "bubble_guard_floor": int  # clamp bubble_guard reading below this
  }

Per philosophy/06-cycle_framework.md and the principal directive 2026-05-29
that FOM was systematically underweighting high-momentum ATH winners
(MU/AMD/INTC) in the current AI-cycle bull regime.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import pandas as pd


# ─── Weight tables ─────────────────────────────────────────────────────────────
#
# Each entry must sum to exactly 1.0 across the five base dimensions
# (momentum, contrarian, cyclic, quality, bubble_guard).
#
# bubble_guard_floor: clamp value applied BEFORE the
# (bub + 100) / 2 → 0..100 normalisation in FOMScore.base_score, so a -95
# bubble_guard reading with floor -50 becomes (-50 + 100) / 2 = 25 instead of
# the raw 2.5. This is the lever that prevents a single late-cycle penalty
# from drowning a strong-momentum AI-cycle name.

REGIME_PROFILES: dict[str, dict] = {
    "bull_trend": {
        "weights": {
            "momentum": 0.40,
            "contrarian": 0.15,
            "cyclic": 0.15,
            "quality": 0.15,
            "bubble_guard": 0.15,
        },
        "bubble_guard_floor": -40,
        "description": (
            "Healthy breadth + green liquidity + index above 200dma. "
            "Reward momentum heavily; trim bubble_guard penalty to -40 floor."
        ),
    },
    "late_bull": {
        "weights": {
            "momentum": 0.35,
            "contrarian": 0.18,
            "cyclic": 0.15,
            "quality": 0.15,
            "bubble_guard": 0.17,
        },
        "bubble_guard_floor": -50,
        "description": (
            "Breadth overheated but liquidity only yellow and index still "
            "above 200dma. Continue rewarding momentum but keep bubble_guard "
            "active with a -50 floor so AI-cycle supply-chain leaders are not "
            "drowned by a -95 single-name penalty."
        ),
    },
    "neutral": {
        "weights": {
            "momentum": 0.25,
            "contrarian": 0.25,
            "cyclic": 0.15,
            "quality": 0.15,
            "bubble_guard": 0.20,
        },
        "bubble_guard_floor": -100,
        "description": "Canonical FOM weights — used when no regime signal triggers.",
    },
    "risk_off": {
        "weights": {
            "momentum": 0.15,
            "contrarian": 0.30,
            "cyclic": 0.10,
            "quality": 0.20,
            "bubble_guard": 0.25,
        },
        "bubble_guard_floor": -100,
        "description": (
            "Breadth overheated and liquidity orange/red, or index below 200dma. "
            "Lean into quality + contrarian; raise bubble_guard weight."
        ),
    },
    "capitulation": {
        "weights": {
            "momentum": 0.15,
            "contrarian": 0.40,
            "cyclic": 0.10,
            "quality": 0.20,
            "bubble_guard": 0.15,
        },
        "bubble_guard_floor": -100,
        "description": (
            "Breadth in capitulation per breadth_indicator. Aggressive contrarian "
            "+ quality posture to fish wash-out bottoms; bubble_guard de-emphasised "
            "because the universe is no longer in a bubble zone."
        ),
    },
}


# ─── File-system helpers ────────────────────────────────────────────────────────
def _latest_json(out_dir: Path, prefix: str) -> Optional[Path]:
    candidates = sorted(out_dir.glob(f"{prefix}-*.json"))
    return candidates[-1] if candidates else None


def load_latest_breadth(out_dir: Path = Path("outputs")) -> Optional[dict]:
    p = _latest_json(out_dir, "breadth-indicator")
    if p is None:
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def load_latest_liquidity(out_dir: Path = Path("outputs")) -> Optional[dict]:
    p = _latest_json(out_dir, "liquidity-signals")
    if p is None:
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


# ─── Classifier ────────────────────────────────────────────────────────────────
def classify_regime(
    breadth: Optional[dict] = None,
    liquidity: Optional[dict] = None,
    spx_above_200dma: Optional[bool] = None,
) -> dict:
    """Return regime label + applied weights + reasons.

    Inputs default to latest outputs/{breadth,liquidity}-*.json when omitted.

    Args:
        breadth: parsed breadth-indicator JSON (verdict in {OVERHEATED, NORMAL,
                 CAPITULATION_BOTTOM, ...})
        liquidity: parsed liquidity-signals JSON
                   (composite_alert.level in {GREEN, YELLOW, ORANGE, RED})
        spx_above_200dma: optional override; otherwise inferred from
                          breadth['indices_vs_ma']['SPX']['vs_200ma']['above_ma']

    Returns:
        {
          'label': str,
          'reasons': list[str],
          'weights': dict,                 # sums to 1.0
          'bubble_guard_floor': int,
          'description': str,
          'inputs': {                      # what we observed
              'breadth_verdict': str,
              'liquidity_level': str,
              'spx_above_200dma': bool,
          },
        }
    """
    breadth = breadth or load_latest_breadth() or {}
    liquidity = liquidity or load_latest_liquidity() or {}

    breadth_verdict = breadth.get("verdict", "UNKNOWN")
    liq_level = (liquidity.get("composite_alert") or {}).get("level", "UNKNOWN")

    if spx_above_200dma is None:
        spx_block = (breadth.get("indices_vs_ma") or {}).get("SPX") or {}
        vs_200 = spx_block.get("vs_200ma") or {}
        spx_above_200dma = bool(vs_200.get("above_ma")) if vs_200 else None

    reasons: list[str] = []

    # ── Pick a regime ───────────────────────────────────────────────────────
    label = "neutral"

    if breadth_verdict == "CAPITULATION_BOTTOM":
        label = "capitulation"
        reasons.append(f"breadth verdict = {breadth_verdict}")
    elif spx_above_200dma is False:
        label = "risk_off"
        reasons.append("SPX below 200dma")
        if liq_level in {"ORANGE", "RED"}:
            reasons.append(f"liquidity composite = {liq_level}")
    elif breadth_verdict == "OVERHEATED" and liq_level in {"ORANGE", "RED"}:
        label = "risk_off"
        reasons.append(f"breadth {breadth_verdict} + liquidity {liq_level}")
    elif breadth_verdict == "OVERHEATED":
        # Overheated but liquidity not yet bearish → late-cycle bull.
        # Keep bubble_guard but raise its floor so a single -95 reading does
        # not drown momentum signal of true supply-chain leaders.
        label = "late_bull"
        reasons.append(f"breadth {breadth_verdict} + liquidity {liq_level or 'unknown'}")
        if spx_above_200dma:
            reasons.append("SPX above 200dma")
    elif breadth_verdict == "NORMAL" and liq_level in {"GREEN", "YELLOW", "UNKNOWN"}:
        if spx_above_200dma:
            label = "bull_trend"
            reasons.append(f"breadth NORMAL + liquidity {liq_level} + SPX above 200dma")
        else:
            label = "neutral"
            reasons.append("breadth NORMAL but SPX not above 200dma — neutral")
    else:
        reasons.append(
            f"no rule matched (breadth={breadth_verdict}, liquidity={liq_level}, "
            f"spx_above_200dma={spx_above_200dma}) — fallback neutral"
        )

    profile = REGIME_PROFILES[label]
    # Defensive: profile weights MUST sum to 1.0 (rounded to 6 dp).
    total = round(sum(profile["weights"].values()), 6)
    if total != 1.0:
        raise ValueError(
            f"Regime profile {label!r} weights sum to {total}, not 1.0. "
            f"Fix REGIME_PROFILES in regime/classifier.py."
        )

    return {
        "label": label,
        "reasons": reasons,
        "weights": dict(profile["weights"]),
        "bubble_guard_floor": profile["bubble_guard_floor"],
        "description": profile["description"],
        "inputs": {
            "breadth_verdict": breadth_verdict,
            "liquidity_level": liq_level,
            "spx_above_200dma": spx_above_200dma,
        },
    }


# ─── CLI entry (for ad-hoc check) ──────────────────────────────────────────────
def main() -> int:
    import sys

    out_dir = Path("outputs")
    regime = classify_regime()
    print(f"Regime: {regime['label']}", file=sys.stderr)
    print(f"  inputs: {regime['inputs']}", file=sys.stderr)
    print(f"  reasons: {regime['reasons']}", file=sys.stderr)
    print(f"  weights: {regime['weights']}", file=sys.stderr)
    print(f"  bubble_guard_floor: {regime['bubble_guard_floor']}", file=sys.stderr)

    # Persist a snapshot
    today = pd.Timestamp.now().strftime("%Y-%m-%d")
    out_path = out_dir / f"regime-classification-{today}.json"
    out_path.write_text(
        json.dumps(regime, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"wrote {out_path}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
