"""Macro_Regime_Shield_Agent — Brain layer for regime-aware global switch.

Aggregates Macro_News_Ingest_Hook; outputs regime for all downstream (short allowed? vol target?).
Fits into 05-decision-rubric and Risk_Officer (defensive overrides long_new if HIGH risk).

Pydantic output.
"""

from __future__ import annotations

from pydantic import BaseModel

from sharks.data.macro_news_ingest import fetch_fed_dot_plot, monitor_geopolitical_risk


class MacroRegime(BaseModel):
    agent: str = "Macro_Regime_Shield_Agent"
    current_regime: str  # "OFFENSIVE" | "DEFENSIVE_VOL_TARGETING" | ...
    global_risk_level: str  # "LOW" | "MED" | "HIGH"
    short_side_allowed: bool
    reason: str


def run_macro_regime_shield() -> MacroRegime:
    fed = fetch_fed_dot_plot()
    geo = monitor_geopolitical_risk()
    risk = "HIGH" if fed.get("fed_hawk_dove_score", 0) > 0.5 or geo.get("macro_risk_regime") == "HIGH" else "MED"
    regime = "DEFENSIVE_VOL_TARGETING" if risk == "HIGH" else "OFFENSIVE"
    return MacroRegime(
        current_regime=regime,
        global_risk_level=risk,
        short_side_allowed=(risk == "HIGH"),
        reason=f"Fed: {fed.get('macro_regime')}; Geo: {geo.get('macro_risk_regime')}. Force short/vol down if HIGH.",
    )


if __name__ == "__main__":
    print(run_macro_regime_shield().model_dump_json(indent=2))
