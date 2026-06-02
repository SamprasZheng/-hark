"""Eval-function calibration loop (評估函數校正).

The checklist's confidence is shaped by weights.yaml. This module closes the loop:
it reads the most recent FOM walk-forward validation artifact from outputs/ (the
IC / IC-IR / hit-rate study), records the OBSERVED metrics into weights.yaml's
``observed:`` block, and reports what a future re-weighting would key off.

PHASE-1 HONESTY: this records measured metrics and flips ``calibration_status`` to
``calibrated-<date>``; it does NOT fabricate new adjustment magnitudes. Refining the
``adjustments`` from per-horizon win-rate is the iterative next step (the mechanism
is wired; the numbers stay the existing seeds until there is enough validation data
to move them honestly). Run ``python -m sharks.decision.calibrate`` (read-only report)
or ``--write`` to fold the observed metrics into weights.yaml.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

from sharks.decision import _yamlite
from sharks.decision.checklist import WEIGHTS_PATH

REPO_ROOT = Path(__file__).resolve().parents[3]
OUTPUTS_DIR = REPO_ROOT / "outputs"

# Artifact name patterns we know how to read, most-specific first.
VALIDATION_GLOBS = ("fom-validation-*.json", "fom_validation-*.json",
                    "fom-ic-*.json", "fom-validation.json")


def _latest(glob: str) -> Optional[Path]:
    hits = sorted(OUTPUTS_DIR.glob(glob))
    return hits[-1] if hits else None


def _find_validation_artifact() -> Optional[Path]:
    for g in VALIDATION_GLOBS:
        p = _latest(g)
        if p is not None:
            return p
    return None


def _pick(d: dict, *keys, default=None):
    """First present key (tolerant to the artifact's exact field names)."""
    for k in keys:
        if isinstance(d, dict) and d.get(k) is not None:
            return d[k]
    return default


def extract_metrics(artifact: dict) -> dict:
    """Pull IC / IC-IR / hit-rate / best-horizon from a validation artifact.

    Primary schema is the fom_validation_backtest output:
      {"interpretation": {"best_horizon", "best_horizon_mean_ic", "best_ic_ir",
                          "best_horizon_hit_rate", "verdict"},
       "by_horizon": {"6m": {"mean_ic", "ic_ir", "mean_hit_rate"}, ...}}
    Falls back to a few flat field names for other artifact shapes.
    """
    interp = artifact.get("interpretation") or {}
    by_h = artifact.get("by_horizon") or {}
    best = interp.get("best_horizon") or _pick(artifact, "best_horizon", "horizon", "optimal_horizon")

    ic = interp.get("best_horizon_mean_ic")
    ir = interp.get("best_ic_ir")
    hit = interp.get("best_horizon_hit_rate")
    if best and best in by_h:                      # fall back to the by-horizon row
        bh = by_h[best]
        ic = ic if ic is not None else bh.get("mean_ic")
        ir = ir if ir is not None else bh.get("ic_ir")
        hit = hit if hit is not None else bh.get("mean_hit_rate")

    return {
        "ic_mean": ic if ic is not None else _pick(artifact, "ic_mean", "mean_ic", "IC", "ic"),
        "ic_ir": ir if ir is not None else _pick(artifact, "ic_ir", "IC_IR", "icir"),
        "hit_rate": hit if hit is not None else _pick(artifact, "hit_rate", "hitrate", "hit"),
        "best_horizon": best,
        "verdict": interp.get("verdict"),
        "by_horizon": {h: {k: v.get(k) for k in ("mean_ic", "ic_ir", "mean_hit_rate")}
                       for h, v in by_h.items()} or None,
    }


def _yaml_scalar(v) -> str:
    if v is None:
        return "null"
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, (int, float)):
        return str(v)
    return f'"{v}"'


def apply_to_weights_text(text: str, observed: dict, status: str) -> str:
    """Update ``calibration_status`` and the ``observed:`` block in weights.yaml
    text, preserving all comments and the adjustment knobs (targeted line edit,
    not a full re-dump — our zero-dep reader has no dumper)."""
    out: list[str] = []
    in_observed = False
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("calibration_status:"):
            out.append(f'calibration_status: "{status}"')
            continue
        if stripped == "observed:":
            in_observed = True
            out.append(line)
            continue
        if in_observed:
            if line and not line.startswith("  "):  # dedent ends the block
                in_observed = False
            else:
                key = stripped.split(":", 1)[0].strip() if ":" in stripped else None
                if key in observed:
                    out.append(f"  {key}: {_yaml_scalar(observed[key])}")
                    continue
        out.append(line)
    return "\n".join(out) + "\n"


def calibrate(*, write: bool = False, weights_path: Optional[Path] = None) -> dict:
    """Read the latest validation artifact and return a calibration report. With
    ``write=True`` fold the observed metrics into weights.yaml."""
    weights_path = weights_path or WEIGHTS_PATH
    today = datetime.now().strftime("%Y-%m-%d")
    artifact_path = _find_validation_artifact()

    report: dict = {"as_of": today, "artifact": None, "observed": None,
                    "status": "phase1-seed-uncalibrated", "wrote": False, "notes": []}

    if artifact_path is None:
        report["notes"].append(
            "no FOM validation artifact found in outputs/ (looked for "
            f"{', '.join(VALIDATION_GLOBS)}). Run `python -m sharks.backtest."
            "fom_validation_backtest` first, then re-run calibrate. weights.yaml "
            "left at its seed.")
        return report

    try:
        artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        report["notes"].append(f"could not read {artifact_path.name}: {e}")
        return report

    observed = extract_metrics(artifact)
    observed["source_artifact"] = artifact_path.name
    report["artifact"] = artifact_path.name
    report["observed"] = observed
    have = any(observed.get(k) is not None for k in ("ic_mean", "ic_ir", "hit_rate"))
    report["status"] = f"calibrated-{today}" if have else "phase1-seed-uncalibrated"
    report["notes"].append(
        "Phase-1: observed metrics recorded; adjustment knobs unchanged "
        "(re-weighting from per-horizon win-rate is the iterative next step).")

    if write:
        text = weights_path.read_text(encoding="utf-8")
        weights_path.write_text(apply_to_weights_text(text, observed, report["status"]),
                                encoding="utf-8")
        report["wrote"] = True

    return report


def main(argv: Optional[list[str]] = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    write = "--write" in argv
    rep = calibrate(write=write)
    print(f"calibration ({rep['status']}):", file=sys.stderr)
    if rep["observed"]:
        o = rep["observed"]
        print(f"  artifact={rep['artifact']}  IC={o.get('ic_mean')} IC_IR={o.get('ic_ir')} "
              f"hit={o.get('hit_rate')} best_horizon={o.get('best_horizon')}", file=sys.stderr)
    for n in rep["notes"]:
        print(f"  - {n}", file=sys.stderr)
    if write:
        print(f"  wrote observed metrics into {WEIGHTS_PATH.name}", file=sys.stderr)
    # also drop a JSON report for provenance
    try:
        OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
        p = OUTPUTS_DIR / f"calibration-report-{rep['as_of']}.json"
        p.write_text(json.dumps(rep, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"  wrote {p}", file=sys.stderr)
    except OSError:
        pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
