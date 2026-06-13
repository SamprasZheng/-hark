"""Macro_News_Ingest_Hook — Perception layer for Fed, geopolitics, macro regime.

Part of $harks three-layer architecture. Outputs structured data for Brain Agents (Macro_Regime_Shield_Agent).
Never places trades; outputs recommendations/signals only. Use with point-in-time discipline.

Integrates with existing: fred_client, polygon, news_fetch, data_lake.
"""

from __future__ import annotations

from datetime import datetime
from typing import Dict, Any, Optional

from sharks.data import fred_client, polygon_client
# from sharks.news_fetch import ... (extend as needed)


def fetch_fed_dot_plot(as_of: Optional[str] = None) -> Dict[str, Any]:
    """Fetch and parse latest FOMC dot plot / Powell speech.

    Returns Fed_Hawk_Dove_Score (-1.0 hawkish to +1.0 dovish) + regime flag.
    Stub: extend with real parsing of FRED series or PDF text (use existing fred_client).
    """
    # Example: use FRED for effective fed funds or sentiment proxy
    try:
        # Placeholder: real impl would parse dot plot releases or use LLM on transcript
        score = 0.2  # example: mildly hawkish from recent
        regime = "HAWKISH" if score > 0 else "DOVISH"
        return {
            "fed_hawk_dove_score": score,
            "macro_regime": regime,
            "as_of": as_of or datetime.utcnow().isoformat(),
            "source": "FRED + transcript parse (extend with raw/macro/ or news)",
            "notes": "P0 for Macro_Regime_Shield_Agent. Trigger defensive if >0.5 hawkish."
        }
    except Exception as e:
        return {"error": str(e), "fed_hawk_dove_score": 0.0}


def monitor_geopolitical_risk(keywords: list[str] = None, lookback_hours: int = 24) -> Dict[str, Any]:
    """Monitor X/news for geopolitical risk (tariffs, sanctions, military).

    Returns Macro_Risk_Regime (LOW/MED/HIGH) + score.
    Use existing news/X clients or extend KOL scraper.
    """
    keywords = keywords or ["tariff", "sanction", "war", "geopolitical", "fed hike"]
    # Stub: integrate with existing kol_signals or news_fetch; compute burst freq
    risk_score = 0.3  # example
    regime = "HIGH" if risk_score > 0.7 else "MED" if risk_score > 0.3 else "LOW"
    return {
        "macro_risk_regime": regime,
        "risk_score": risk_score,
        "keywords_burst": keywords,
        "as_of": datetime.utcnow().isoformat(),
        "action": "If HIGH, Macro_Regime_Shield_Agent should force short_side_allowed=True and vol target down."
    }


# Hook registration for perception layer / daily routine
MACRO_HOOKS = {
    "fetch_fed_dot_plot": fetch_fed_dot_plot,
    "monitor_geopolitical_risk": monitor_geopolitical_risk,
}
