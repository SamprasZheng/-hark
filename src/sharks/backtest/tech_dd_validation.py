"""DD-tilt predictive-validity backtest — does the `tech_dd` weight tilt add IC?

The OBSERVE-FIRST gate from `tech/fom-integration.md` §3: the DD verdict tilt
stays OUT of `final_fom` until a walk-forward shows it improves the
cross-sectional Information Coefficient. This module IS that gate — it mirrors the
method of `fom_validation_backtest.py`: at each month-end, over the DD-COVERED
subset of the universe, compare the IC (FOM vs realised forward return) of the
BASELINE FOM against the DD-TILTED FOM.

*** CRITICAL HONESTY — LOOKAHEAD ***
The `TECH_DD` verdicts are static and dated 2026-05-31 (today). Applying today's
verdicts to historical month-ends uses information that did not exist then, so
this is a MECHANISM / SENSITIVITY test, NOT a validated forward edge. It answers
"IF these verdicts had been held constant, would the tilt have helped the rank?"
— useful for sizing the tilt's effect, but NOT headline-eligible, and the tilt
stays observe-first regardless of the result. A true validation needs forward
data accruing from 2026-05-31 onward (or a point-in-time verdict history we do
not have). This is stamped in the report.
"""

from __future__ import annotations

import json
import sys
import warnings
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)

import numpy as np
import pandas as pd

from sharks.analysts.persona import apply_persona_tilt
from sharks.backtest.fom_validation_backtest import (
    BACKTEST_START,
    DATA_END,
    DATA_START,
    _aggregate,
    _forward_returns,
    spearman_ic,
)
from sharks.scoring.fom import DEFAULT_UNIVERSE, fetch_monthly, rank_universe
from sharks.scoring.tech_dd import TECH_DD, dd_verdict_tilt

DEFAULT_HORIZONS = (1, 3, 6, 12)


def tilted_fom(score) -> float:
    """Recompute a FOMScore's FOM under its DD verdict tilt (observe-only).
    Uncovered tickers return their baseline final_fom unchanged."""
    dd = TECH_DD.get(score.ticker)
    if dd is None:
        return score.final_fom
    tilt = dd_verdict_tilt(dd.verdict, dd.flags)
    w = apply_persona_tilt(score.weights, tilt)
    base = score._weighted_base(w, score.bubble_guard_floor)
    return float(base * (1.0 + score.persistence_boost))


def run_validation_dd(
    closes: pd.DataFrame,
    universe: Optional[list[str]] = None,
    horizons: tuple[int, ...] = DEFAULT_HORIZONS,
    backtest_start: str = BACKTEST_START,
) -> dict:
    """Walk-forward IC of baseline vs DD-tilted FOM over the DD-covered subset."""
    universe = universe or sorted(set(DEFAULT_UNIVERSE) | set(TECH_DD.keys()))
    month_ends = closes.index[closes.index >= pd.Timestamp(backtest_start)]

    per_h = {h: {"base_ic": [], "tilt_ic": []} for h in horizons}
    periods = 0
    persistence: dict[str, int] = {}

    for as_of in month_ends:
        pos = closes.index.searchsorted(as_of)
        if pos + max(horizons) >= len(closes):
            break
        scored = rank_universe(closes, universe, as_of, persistence)
        if len(scored) < 10:
            continue
        persistence = {s.ticker: persistence.get(s.ticker, 0) + 1 for s in scored[:50]}
        covered = [s for s in scored if s.ticker in TECH_DD]
        if len(covered) < 5:
            continue
        base = {s.ticker: s.final_fom for s in covered}
        tilt = {s.ticker: tilted_fom(s) for s in covered}
        periods += 1
        for h in horizons:
            fwd = _forward_returns(closes, pos, h)
            fwd_cov = {t: fwd[t] for t in base if t in fwd}
            if len(fwd_cov) < 5:
                continue
            b = spearman_ic(base, fwd_cov)
            t = spearman_ic(tilt, fwd_cov)
            if b is not None:
                per_h[h]["base_ic"].append(b)
            if t is not None:
                per_h[h]["tilt_ic"].append(t)

    by_h = {}
    for h in horizons:
        b = _aggregate(per_h[h]["base_ic"])
        t = _aggregate(per_h[h]["tilt_ic"])
        delta = (round(t["ic_ir"] - b["ic_ir"], 2)
                 if (t["ic_ir"] is not None and b["ic_ir"] is not None) else None)
        by_h[f"{h}m"] = {
            "n_periods": b["n_periods"],
            "base_ic_ir": b["ic_ir"],
            "tilt_ic_ir": t["ic_ir"],
            "base_mean_ic": b["mean_ic"],
            "tilt_mean_ic": t["mean_ic"],
            "delta_ic_ir": delta,
        }
    return {
        "periods_scored": periods,
        "dd_covered_count": len(TECH_DD),
        "by_horizon": by_h,
        "interpretation": _interpret_dd(by_h),
    }


def _interpret_dd(by_h: dict) -> dict:
    deltas = [v["delta_ic_ir"] for v in by_h.values() if v["delta_ic_ir"] is not None]
    if not deltas:
        return {"verdict": "INCONCLUSIVE", "note": "no periods scored."}
    mean_delta = float(np.mean(deltas))
    pos = sum(1 for d in deltas if d > 0)
    if mean_delta >= 0.5 and pos >= len(deltas) - 1:
        verdict = "DD-TILT-ADDS-IC (mechanism only; lookahead-tainted → STILL observe-first)"
    elif mean_delta <= -0.5:
        verdict = "DD-TILT-HURTS-IC → do NOT apply; keep verdicts as router/annotation only"
    else:
        verdict = "DD-TILT-NEUTRAL → no measurable rank edge; keep out of final_fom (observe-first holds)"
    return {
        "mean_delta_ic_ir": round(mean_delta, 2),
        "horizons_tilt_beats_base": f"{pos}/{len(deltas)}",
        "verdict": verdict,
        "note": ("delta = tilted IC_IR − baseline IC_IR over the DD-covered subset. "
                 "A small |delta| is expected — the tilt is bounded ±0.06 by design. "
                 "Lookahead-tainted (static verdicts on history); observe-first regardless."),
    }


def main() -> int:
    out_dir = Path("outputs")
    out_dir.mkdir(parents=True, exist_ok=True)
    pull = sorted(set(DEFAULT_UNIVERSE) | set(TECH_DD.keys()) | {"SPY"})
    print(f"Pulling {len(pull)} tickers {DATA_START}..{DATA_END}", file=sys.stderr)
    closes = fetch_monthly(pull, DATA_START, DATA_END)
    print(f"  data: {len(closes.columns)} tickers, {len(closes)} months", file=sys.stderr)
    result = run_validation_dd(closes)
    report = {
        "as_of": datetime.now(timezone.utc).isoformat(),
        "report_type": "tech_dd_tilt_validity",
        "llm_involvement": "none",
        "headline_eligible": False,
        "lookahead_caveat": (
            "TECH_DD verdicts are static as-of 2026-05-31 applied to history → "
            "MECHANISM/SENSITIVITY test, not a validated forward edge. The tilt "
            "remains observe-first regardless; a true test needs forward data from "
            "2026-05-31 onward."),
        "method": (
            "Walk-forward cross-sectional Spearman IC over the DD-covered subset: "
            "baseline FOM vs DD-tilted FOM (apply_persona_tilt of dd_verdict_tilt) vs "
            "realised forward returns. PIT prices; STATIC verdicts (lookahead — see caveat)."),
        "data_window": {"start": BACKTEST_START, "end": DATA_END},
        **result,
    }
    out_path = out_dir / "tech-dd-validation.json"
    out_path.write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")
    print(f"wrote {out_path}", file=sys.stderr)
    print(json.dumps(report["by_horizon"], indent=2), file=sys.stderr)
    print("VERDICT:", report["interpretation"]["verdict"], file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
