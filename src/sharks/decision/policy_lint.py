"""Risk-Officer pre-screen — load risk_config.yaml and lint a candidate pick.

`risk_config.yaml` (repo root) is the single source of truth mirroring
philosophy/06-exclusions.md + 08-risk-and-position.md. `lint_pick` checks a
candidate against it and returns a list of violations (empty == clean). PURE
(no network) so it is the deterministic gate the checklist and any future
`sharks pick` generator run before emitting a recommendation.

RECOMMEND-ONLY: a violation means "do not slot this", never an order.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from sharks.decision import _yamlite

# src/sharks/decision/policy_lint.py -> parents[3] == repo root ($hark)
REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_RISK_CONFIG = REPO_ROOT / "risk_config.yaml"

_REQUIRED_SECTIONS = (
    "exclusions", "position_caps_pct", "concentration_caps_pct",
    "max_drawdown_halt", "horizon_size_caps_pct", "confidence",
)


def load_risk_config(path: Optional[Path] = None) -> dict:
    """Load + validate risk_config.yaml. Raises if a required section is missing
    (a missing section means the mirror drifted from the philosophy pages)."""
    cfg = _yamlite.load(path or DEFAULT_RISK_CONFIG)
    missing = [s for s in _REQUIRED_SECTIONS if s not in cfg]
    if missing:
        raise ValueError(f"risk_config.yaml missing required sections: {missing}")
    return cfg


def size_cap_for(tier: Optional[int], horizon: Optional[str], cfg: dict) -> Optional[float]:
    """The applicable single-position size cap (%). Horizon cap (01-time-horizon)
    overrides the flat per-tier cap (08) when a horizon is supplied."""
    if tier is None:
        return None
    hcaps = cfg.get("horizon_size_caps_pct", {})
    if horizon and horizon in hcaps:
        c = hcaps[horizon].get(f"tier{tier}")
        if c is not None:
            return float(c)
    return cfg["position_caps_pct"].get(f"tier{tier}")


def lint_pick(pick: dict, cfg: Optional[dict] = None) -> list[dict]:
    """Return a list of ``{"rule", "detail"}`` violations (empty == clean). PURE.

    Only keys present in ``pick`` are checked, so a partial candidate degrades
    gracefully (absence of a field is "unknown", never an auto-fail). Recognised
    keys: price, dollar_vol_60d, share_vol_30d, market_cap, tier, size_pct,
    horizon, side ('long'|'short'), short_interest_pct, borrow_fee_apr,
    days_to_cover, vix, options_ok.
    """
    cfg = cfg or load_risk_config()
    ex = cfg["exclusions"]
    violations: list[dict] = []

    def add(rule: str, detail: str) -> None:
        violations.append({"rule": rule, "detail": detail})

    price = pick.get("price")
    if price is not None and price < ex["price_floor_usd"]:
        add("price_floor", f"price ${price} < ${ex['price_floor_usd']} floor (06-exclusions)")

    dv = pick.get("dollar_vol_60d")
    if dv is not None and dv < ex["liquidity_60d_avg_dollar_vol_usd"]:
        add("liquidity_floor", f"60d $vol {dv:,.0f} < {ex['liquidity_60d_avg_dollar_vol_usd']:,.0f}")
    sv = pick.get("share_vol_30d")
    if sv is not None and sv < ex["liquidity_30d_avg_share_vol"]:
        add("liquidity_floor", f"30d share vol {sv:,.0f} < {ex['liquidity_30d_avg_share_vol']:,.0f}")

    mc, tier = pick.get("market_cap"), pick.get("tier")
    if mc is not None and tier == 2 and mc < ex["market_cap_floor_tier2_usd"]:
        add("market_cap_floor", f"tier2 mcap {mc:,.0f} < {ex['market_cap_floor_tier2_usd']:,.0f}")
    if mc is not None and tier == 3 and mc < ex["market_cap_floor_tier3_usd"]:
        add("market_cap_floor", f"tier3 mcap {mc:,.0f} < {ex['market_cap_floor_tier3_usd']:,.0f}")

    size = pick.get("size_pct")
    cap = size_cap_for(tier, pick.get("horizon"), cfg)
    if size is not None and cap is not None and size > cap:
        hz = f"/{pick.get('horizon')}" if pick.get("horizon") else ""
        add("position_cap", f"size {size}% > tier{tier}{hz} cap {cap}% (08-risk-and-position)")

    if pick.get("side") == "short":
        si = pick.get("short_interest_pct")
        if si is not None and si > ex["short_interest_pct_max"]:
            add("short_iron", f"short interest {si:.0%} > {ex['short_interest_pct_max']:.0%} -> Put-only (03)")
        bf = pick.get("borrow_fee_apr")
        if bf is not None and bf > ex["borrow_fee_apr_max"]:
            add("short_iron", f"borrow fee {bf:.0%} > {ex['borrow_fee_apr_max']:.0%} -> Put-only (03)")
        dtc = pick.get("days_to_cover")
        if dtc is not None and dtc > ex["days_to_cover_max"]:
            add("short_iron", f"days-to-cover {dtc} > {ex['days_to_cover_max']} -> Put-only (03)")

    vix = pick.get("vix")
    if vix is not None and vix > ex["vix_defensive_threshold"] and pick.get("side") == "long":
        add("vix_defensive", f"VIX {vix} > {ex['vix_defensive_threshold']} -> defensive-only, no new long (06)")

    return violations
