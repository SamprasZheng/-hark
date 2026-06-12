"""Liquidity Fishbowl composite (the ``L`` score).

Implements ``philosophy/concepts/liquidity-fishbowl.md`` — the regime-aware
position-sizing gauge the project's docs have specified since Phase 1 but never
wired. The market is a fishbowl; liquidity is the water level. ``L in [0, 1]``
blends five proxies (doc §"The regime-sizing rule"):

  L = 0.25*reserves_change_30d + 0.15*(1-rrp_change_30d)
    + 0.15*(1-hy_oas) + 0.20*(1-spx_60d_rvol) + 0.25*ad_line_60d_slope

The first three terms come from FRED (WALCL, RRPONTSYD, BAMLH0A0HYM2) via the
keyless :mod:`sharks.data.fred_client`; the last two (SPX 60d realised vol, NYSE
A/D slope) are non-FRED and are accepted as OPTIONAL injected inputs — when
absent the present weights are renormalised so ``L`` stays in ``[0, 1]`` (we
never invent a term).

Linchpin: :func:`regime.classifier.classify_regime` reads liquidity as a colour
BAND (``composite_alert.level`` in GREEN/YELLOW/ORANGE/RED), not a number. So the
orchestrator emits that band via :func:`L_to_alert_level` and the classifier
plugs in unchanged.

Structurally mirrors ``scoring/crypto_top100.py``: pure transforms, injectable
fetch, ``main()`` never raises, and a failed FRED fetch degrades to the last good
snapshot re-stamped under TODAY's date with ``live_data=false`` /
``stale_fallback=true``. RECOMMEND-ONLY context — this gauges sizing, it does not
trade. Zero-dependency (stdlib only).
"""

from __future__ import annotations

import json
import sys
import time
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Optional

from sharks.data.fred_client import FREDError, fetch_series

# ── composite weights (doc §"The regime-sizing rule"; sum to 1.0) ──────────────
WEIGHTS = {
    "reserves": 0.25,
    "rrp": 0.15,
    "hy_oas": 0.15,
    "spx_rvol": 0.20,
    "ad_line": 0.25,
}

# normalise bounds, in each term's native unit (documented):
RESERVES_LO, RESERVES_HI = -200.0, 200.0  # WALCL 30d change, billions USD
RRP_LO, RRP_HI = -200.0, 200.0            # RRPONTSYD 30d change, billions USD
HY_OAS_SOFT, HY_OAS_HARD = 400.0, 700.0   # HY OAS level, basis points
RVOL_SOFT, RVOL_HARD = 15.0, 35.0         # SPX 60d realised vol, annualised %
ADLINE_LO, ADLINE_HI = -1.0, 1.0          # NYSE A/D 60d slope, normalised [-1,1]

GUARDRAILS_NOTE = (
    "RECOMMEND-ONLY sizing gauge (never trades). Liquidity is the water level: "
    "as L falls, total exposure shrinks and the smallest fish (tier3) is cut "
    "first. See philosophy/concepts/liquidity-fishbowl.md + 08-risk-and-position."
)


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


# ── pure transforms ────────────────────────────────────────────────────────────

def normalize(value: Optional[float], lo: float, hi: float, *, invert: bool = False) -> Optional[float]:
    """Clamp ``value`` into ``[0, 1]`` across ``[lo, hi]``; ``invert`` flips it.

    Returns ``None`` for a ``None`` input so missing terms stay missing (never 0).
    """
    if value is None:
        return None
    if hi == lo:
        return 0.0
    t = (value - lo) / (hi - lo)
    t = max(0.0, min(1.0, t))
    return (1.0 - t) if invert else t


def _band(L: Optional[float]) -> str:
    if L is None:
        return "unknown"
    if L > 0.7:
        return "ample"
    if L > 0.4:
        return "normal"
    if L > 0.2:
        return "contracting"
    return "drought"


def L_to_alert_level(L: Optional[float], dragon_eating_dragon: bool = False) -> str:
    """Map the numeric ``L`` to the colour band the classifier matches on."""
    if L is None:
        return "UNKNOWN"
    if dragon_eating_dragon:
        return "RED"
    if L > 0.7:
        return "GREEN"
    if L > 0.4:
        return "YELLOW"
    if L > 0.2:
        return "ORANGE"
    return "RED"


def compute_L(
    *,
    reserves_change_30d: Optional[float] = None,
    rrp_change_30d: Optional[float] = None,
    hy_oas_bps: Optional[float] = None,
    spx_60d_rvol: Optional[float] = None,
    ad_line_60d_slope: Optional[float] = None,
) -> dict:
    """Composite liquidity ``L`` from the five proxy inputs (any may be None).

    Present weights are renormalised to sum 1.0 when terms are missing, so ``L``
    stays in ``[0, 1]``. Flags ``dragon_eating_dragon`` (多殺多) at ``L < 0.15`` and
    ``SPX 60d rvol > 30`` (doc §"The 多殺多 warning condition").
    """
    terms = {
        "reserves": normalize(reserves_change_30d, RESERVES_LO, RESERVES_HI),
        "rrp": normalize(rrp_change_30d, RRP_LO, RRP_HI, invert=True),
        "hy_oas": normalize(hy_oas_bps, HY_OAS_SOFT, HY_OAS_HARD, invert=True),
        "spx_rvol": normalize(spx_60d_rvol, RVOL_SOFT, RVOL_HARD, invert=True),
        "ad_line": normalize(ad_line_60d_slope, ADLINE_LO, ADLINE_HI),
    }
    present = {k: v for k, v in terms.items() if v is not None}
    missing = [k for k, v in terms.items() if v is None]
    if not present:
        return {
            "L": None, "components": {}, "weights_used": {}, "missing": missing,
            "regime_band": "unknown", "dragon_eating_dragon": False,
        }
    wsum = sum(WEIGHTS[k] for k in present)
    weights_used = {k: round(WEIGHTS[k] / wsum, 4) for k in present}
    L = round(sum((WEIGHTS[k] / wsum) * present[k] for k in present), 4)
    dragon = bool(L < 0.15 and spx_60d_rvol is not None and spx_60d_rvol > 30)
    return {
        "L": L,
        "components": {k: round(v, 4) for k, v in present.items()},
        "weights_used": weights_used,
        "missing": missing,
        "regime_band": _band(L),
        "dragon_eating_dragon": dragon,
    }


# ── FRED-series helpers ─────────────────────────────────────────────────────────

def _latest_value(rows: list[dict]) -> Optional[float]:
    for r in reversed(rows):
        if r.get("value") is not None:
            return r["value"]
    return None


def _value_on_or_before(rows: list[dict], target_date: str) -> Optional[dict]:
    best = None
    for r in rows:
        if r.get("value") is None:
            continue
        if r["date"] <= target_date:
            best = r
        else:
            break
    return best


def _change_over_days(rows: list[dict], days: int) -> Optional[float]:
    """Last non-None value minus the value as-of ``days`` calendar days earlier."""
    vals = [r for r in rows if r.get("value") is not None]
    if len(vals) < 2:
        return None
    last = vals[-1]
    try:
        target = (date.fromisoformat(last["date"]) - timedelta(days=days)).isoformat()
    except ValueError:
        return None
    prev = _value_on_or_before(vals, target) or vals[0]
    return last["value"] - prev["value"]


def fetch_fishbowl_series(
    as_of: Optional[str] = None,
    *,
    opener=None,
    vintage_date: Optional[str] = None,
    sleep=time.sleep,
) -> dict:
    """Fetch the FRED-sourced fishbowl inputs and reduce them to scalar terms.

    Units (documented): WALCL is millions USD → converted to billions; RRPONTSYD
    is already billions USD; BAMLH0A0HYM2 is percent → converted to bps. T10Y2Y
    and a weekly TGA proxy (WTREGEN) are fetched for display only (not in ``L``).
    Raises :class:`FREDError` on a fetch failure (the orchestrator catches it).
    """
    end = (as_of or _utc_now_iso())[:10]
    try:
        start = (date.fromisoformat(end) - timedelta(days=120)).isoformat()
    except ValueError:
        start = None

    def series(sid: str) -> list[dict]:
        return fetch_series(
            sid, start=start, end=end, vintage_date=vintage_date, opener=opener, sleep=sleep
        )

    walcl = series("WALCL")
    rrp = series("RRPONTSYD")
    hy = series("BAMLH0A0HYM2")
    t10y2y = series("T10Y2Y")
    tga = series("WTREGEN")

    reserves_m = _change_over_days(walcl, 30)
    reserves_change_30d = reserves_m / 1000.0 if reserves_m is not None else None  # M$ → B$
    rrp_change_30d = _change_over_days(rrp, 30)  # RRPONTSYD already in B$
    hy_pct = _latest_value(hy)
    hy_oas_bps = hy_pct * 100.0 if hy_pct is not None else None  # percent → bps

    return {
        "reserves_change_30d": reserves_change_30d,
        "rrp_change_30d": rrp_change_30d,
        "hy_oas_bps": hy_oas_bps,
        "display": {
            "walcl_latest_million": _latest_value(walcl),
            "rrp_latest_billion": _latest_value(rrp),
            "hy_oas_pct": hy_pct,
            "t10y2y": _latest_value(t10y2y),
            "tga_billion_wtregen": _latest_value(tga),
        },
        "pit": {
            "vintage_date": vintage_date,
            "window_start": start,
            "window_end": end,
        },
    }


# ── snapshot / orchestration ─────────────────────────────────────────────────────

def _latest_fishbowl_snapshot(data_dir) -> Optional[dict]:
    p = Path(data_dir)
    if not p.exists():
        return None
    files = sorted(p.glob("liquidity-fishbowl-*.json"))
    if not files:
        return None
    try:
        return json.loads(files[-1].read_text(encoding="utf-8"))
    except Exception:
        return None


def run_liquidity(
    out_dir=Path("outputs"),
    data_dir=Path("outputs/liquidity_fishbowl"),
    *,
    today: Optional[str] = None,
    write: bool = True,
    opener=None,
    sleep=time.sleep,
    vintage_date: Optional[str] = None,
    spx_60d_rvol: Optional[float] = None,
    ad_line_60d_slope: Optional[float] = None,
) -> dict:
    """Fetch FRED → compute ``L`` → emit a PIT artifact carrying ``composite_alert``.

    On a FRED failure, degrades to the last good snapshot's series re-stamped under
    TODAY's date with ``live_data=false`` / ``stale_fallback=true``. Never raises on
    fetch failure. The handoff is written to ``out_dir/liquidity-fishbowl-<DATE>.json``
    (what :func:`regime.classifier.load_latest_fishbowl` reads) and mirrored into
    ``data_dir`` as the immutable history copy.
    """
    now_iso = today or _utc_now_iso()
    date_str = now_iso[:10]
    prev = _latest_fishbowl_snapshot(data_dir)

    live_data = True
    stale: dict = {}
    try:
        series = fetch_fishbowl_series(
            as_of=now_iso, opener=opener, vintage_date=vintage_date, sleep=sleep
        )
    except FREDError as exc:
        live_data = False
        if prev:
            series = prev.get("series", {})
            stale = {
                "stale_fallback": True,
                "stale_source_as_of": prev.get("as_of"),
                "stale_source_date": prev.get("as_of_date"),
                "error": str(exc),
            }
        else:
            series = {}
            stale = {
                "stale_fallback": True,
                "stale_source_as_of": None,
                "error": str(exc),
                "note": "fetch failed and no prior snapshot — empty composite emitted.",
            }

    comp = compute_L(
        reserves_change_30d=series.get("reserves_change_30d"),
        rrp_change_30d=series.get("rrp_change_30d"),
        hy_oas_bps=series.get("hy_oas_bps"),
        spx_60d_rvol=spx_60d_rvol,
        ad_line_60d_slope=ad_line_60d_slope,
    )
    level = L_to_alert_level(comp["L"], comp["dragon_eating_dragon"])

    envelope = {
        "schema_version": 1,
        "as_of": now_iso,
        "as_of_date": date_str,
        "source": "fred",
        "report_type": "liquidity_fishbowl",
        "live_data": live_data,
        "stale_fallback": bool(stale.get("stale_fallback")) if stale else False,
        "L": comp["L"],
        "regime_band": comp["regime_band"],
        "dragon_eating_dragon": comp["dragon_eating_dragon"],
        "components": comp["components"],
        "weights_used": comp["weights_used"],
        "missing": comp["missing"],
        "series": series,
        # The classifier-compat contract: it matches on composite_alert.level.
        "composite_alert": {
            "level": level,
            "L": comp["L"],
            "headline": f"liquidity {comp['regime_band']} (L={comp['L']})",
        },
        "guardrails": GUARDRAILS_NOTE,
        "note": (
            "L composite per philosophy/concepts/liquidity-fishbowl.md. "
            "SPX 60d rvol + NYSE A/D are optional injected terms; when absent the "
            "present weights are renormalised. For backtests pass vintage_date "
            "(ALFRED) so L uses values as first published, not later revisions."
        ),
    }
    if stale:
        for k, v in stale.items():
            if k != "stale_fallback":
                envelope[k] = v

    if write:
        d = Path(data_dir)
        d.mkdir(parents=True, exist_ok=True)
        blob = json.dumps(envelope, indent=2, default=str)
        (d / f"liquidity-fishbowl-{date_str}.json").write_text(blob, encoding="utf-8")
        od = Path(out_dir)
        od.mkdir(parents=True, exist_ok=True)
        (od / f"liquidity-fishbowl-{date_str}.json").write_text(blob, encoding="utf-8")
        print(
            f"wrote liquidity fishbowl L={comp['L']} band={comp['regime_band']} "
            f"alert={level} for {date_str} (live_data={live_data})",
            file=sys.stderr,
        )
    return envelope


def main() -> int:
    run_liquidity()
    return 0


if __name__ == "__main__":
    sys.exit(main())
