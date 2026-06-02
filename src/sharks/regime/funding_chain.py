"""Funding-chain rupture detector — "資金鏈斷裂監控" leading indicators.

Implements philosophy/concepts/funding-chain-rupture.md (proposed) §4 of the
AI-Quant-US merge. The credit/liquidity rupture that PRECEDES equity
capitulation, stratified by latency:

  Tier-1 (daily, market-priced, leading)  — weight 1.0
  Tier-2 (weekly, baseline composite)     — weight 0.5
  Tier-3 (quarterly, confirmatory only)   — weight 0.0 (never triggers alone)

**Split of concern (the honest Phase boundary):**

  - The SCORING logic here is complete and unit-tested — it takes a dict of
    pre-fetched indicator readings and produces a composite stress score +
    verdict. No network.
  - The DATA FETCH (`fetch_funding_indicators`) is a Phase 2 stub: it raises
    NotImplementedError until the FRED ALFRED + market-data clients exist, exactly
    like the other Phase 1 data-client stubs. This keeps the module honest — the
    logic is real, the live wiring is explicitly deferred.

Thresholds below are documented INITIAL values (conservative, literature-based),
explicitly flagged as Phase 4 calibration targets — not fitted.
"""

from __future__ import annotations

from typing import Optional

# ─── Indicator taxonomy (per the funding-chain-rupture concept) ───
# Each indicator: tier, direction ("higher_worse"), and three threshold bands
# (normal / elevated / stress). Values are in the indicator's native unit.
# Thresholds are INITIAL conservative values — Phase 4 calibration targets.
INDICATORS: dict[str, dict] = {
    # Tier-1 — daily, market-priced, leading
    "sofr_ois_bp": {
        "tier": 1, "direction": "higher_worse",
        "elevated": 15, "stress": 30,
        "desc": "term-SOFR vs OIS basis (bp) — replaces obsolete FRA-OIS",
    },
    "sofr_iorb_bp": {
        "tier": 1, "direction": "higher_worse",
        "elevated": 5, "stress": 15,
        "desc": "SOFR vs IORB (bp), persistent — repo/collateral scarcity (de-seasonalised)",
    },
    "ccy_basis_bp": {
        "tier": 1, "direction": "lower_worse",
        "elevated": -25, "stress": -50,
        "desc": "EUR/JPY-USD 3m cross-currency basis (bp) — USD funding stress (more negative = worse)",
    },
    "cdx_ig_fin_bp": {
        "tier": 1, "direction": "higher_worse",
        "elevated": 90, "stress": 140,
        "desc": "CDX IG financials sub-index (bp) — systemic-node default pricing proxy",
    },
    "hy_oas_bp": {
        "tier": 1, "direction": "higher_worse",
        "elevated": 450, "stress": 600,
        "desc": "HY OAS (FRED BAMLH0A0HYM2, bp) — market-priced, ~1d lag",
    },
    # Tier-2 — weekly composite baseline
    "nfci": {
        "tier": 2, "direction": "higher_worse",
        "elevated": 0.0, "stress": 0.5,
        "desc": "Chicago Fed NFCI — >0 = tighter than average",
    },
    "stlfsi": {
        "tier": 2, "direction": "higher_worse",
        "elevated": 0.0, "stress": 1.0,
        "desc": "St. Louis Fed Financial Stress Index — >0 = above-average stress",
    },
    # Tier-3 — quarterly, confirmatory only (weight 0 — never triggers alone)
    "sloos_tightening_pct": {
        "tier": 3, "direction": "higher_worse",
        "elevated": 20, "stress": 40,
        "desc": "SLOOS net % banks tightening C&I standards — quarterly, confirmatory",
    },
}

TIER_WEIGHT = {1: 1.0, 2: 0.5, 3: 0.0}

# Per-band severity contribution (0 normal, 1 elevated, 2 stress).
_BAND_SEVERITY = {"normal": 0, "elevated": 1, "stress": 2}


def classify_indicator(name: str, value: float) -> str:
    """Return 'normal' | 'elevated' | 'stress' for one indicator reading."""
    spec = INDICATORS.get(name)
    if spec is None:
        raise KeyError(f"unknown funding indicator {name!r}")
    elev, stress = spec["elevated"], spec["stress"]
    if spec["direction"] == "higher_worse":
        if value >= stress:
            return "stress"
        if value >= elev:
            return "elevated"
        return "normal"
    else:  # lower_worse (e.g. ccy basis going more negative)
        if value <= stress:
            return "stress"
        if value <= elev:
            return "elevated"
        return "normal"


def funding_stress_score(readings: dict[str, float]) -> dict:
    """Composite funding-stress score from a dict of indicator readings.

    Tier-1 indicators carry full weight, Tier-2 half, Tier-3 zero (confirmatory
    only — they appear in the breakdown but never move the score, enforcing the
    'never trigger off Tier-3 alone' rule). Score is 0-100 (0 = calm).

    Verdict bands: CALM < 25 <= WATCH < 50 <= STRESS < 75 <= RUPTURE.
    """
    per_indicator: list[dict] = []
    weighted_sev = 0.0
    weighted_max = 0.0
    tier1_stress_hits = 0

    for name, value in readings.items():
        spec = INDICATORS.get(name)
        if spec is None:
            continue
        band = classify_indicator(name, value)
        sev = _BAND_SEVERITY[band]
        w = TIER_WEIGHT[spec["tier"]]
        weighted_sev += w * sev
        weighted_max += w * 2  # max severity per indicator is 2
        if spec["tier"] == 1 and band == "stress":
            tier1_stress_hits += 1
        per_indicator.append({
            "indicator": name, "tier": spec["tier"], "value": value,
            "band": band, "weight": w,
        })

    score = round(weighted_sev / weighted_max * 100, 1) if weighted_max > 0 else 0.0

    if score >= 75 or tier1_stress_hits >= 3:
        verdict = "RUPTURE"
    elif score >= 50 or tier1_stress_hits >= 2:
        verdict = "STRESS"
    elif score >= 25 or tier1_stress_hits >= 1:
        verdict = "WATCH"
    else:
        verdict = "CALM"

    return {
        "score": score,
        "verdict": verdict,
        "tier1_stress_hits": tier1_stress_hits,
        "indicators_scored": len(per_indicator),
        "breakdown": per_indicator,
        "note": (
            "Tier-3 (SLOOS) carries weight 0 and never moves the score on its own. "
            "A RUPTURE verdict requires either score>=75 or >=3 Tier-1 stress hits. "
            "Thresholds are INITIAL values — Phase 4 calibration targets, not fitted."
        ),
    }


def fetch_funding_indicators(as_of: Optional[str] = None) -> dict[str, float]:
    """Phase 2 stub. Will pull Tier-1/2/3 indicators from FRED ALFRED (vintage-
    honest) + market-data feeds. Raises until those clients exist — matching the
    Phase 1 data-client stub convention so the gap is explicit, not silently faked.
    """
    raise NotImplementedError(
        "fetch_funding_indicators requires the Phase 2 FRED ALFRED + market-data "
        "clients (SOFR-OIS, SOFR-IORB, ccy basis, CDX IG financials, HY OAS, NFCI, "
        "FSI, SLOOS). Pass pre-fetched readings to funding_stress_score() directly "
        "until then. See docs/ROADMAP.md Phase 2 + the funding-chain-rupture concept."
    )
