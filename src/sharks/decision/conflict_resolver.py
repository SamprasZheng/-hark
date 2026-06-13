"""Conflict Resolver — P0/P1 guard for momentum vs counter-trend signals + real balance clipping.

Pure recommendation logic. Accepts explicit balance_data (populated by human from broker export or paper log).
Never calls live APIs, never holds keys, never emits orders.

Integrates:
- Momentum Decoupling Lock: Institutional breakout (投信連續買超 + 量能突破) → hard block SHORT until TD-9 exhaustion.
- Hard Clipping: actual_size = min(theoretical, available_buying_power * cap)

Used before quadrant routing (03-long-short-taxonomy) and position sizing.
"""

from __future__ import annotations

from typing import Dict, Any


def validate_strategy_bounds(
    target_ticker: str,
    signals: Dict[str, Any],
    balance_data: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Validate and adjust a proposed signal against hard conflicts and real financial power.

    Args:
        target_ticker: e.g. "NVDA"
        signals: dict with at least:
            - "proposed_action": "LONG" | "SHORT" | "TRIM" | ...
            - "institutional_buying_streak": int (投信連續買超期數)
            - "volume_breakthrough": bool
            - "theoretical_position_size": float (or notional)
            - optional: "td9_status", etc.
        balance_data: explicit dict from human (e.g. from daily export or data/balance_metrics.json):
            {
                "available_buying_power": float,   # real remaining cash / buying power
                "tail_winsorization_cap": float,   # e.g. 0.15 (15% of available)
                "as_of": "2026-06-13",
                "source": "human_export_from_broker_or_paper"
            }

    Returns:
        {
            "status": "PASSED" | "REJECTED" | "ADJUSTED",
            "reason": str or None,
            "signals": adjusted_signals_dict (with "actual_position_size" if clipped)
        }
    """
    result = {"status": "PASSED", "reason": None, "signals": dict(signals)}

    # --- P0: Momentum Decoupling Lock (黃靖哲 institutional breakout vs TD-9 counter-trend short) ---
    inst_streak = signals.get("institutional_buying_streak", 0) or 0
    vol_break = bool(signals.get("volume_breakthrough", False))
    proposed = signals.get("proposed_action", "").upper()

    if inst_streak >= 3 and vol_break and proposed == "SHORT":
        result["status"] = "REJECTED"
        result["reason"] = (
            "CRITICAL CONFLICT (Momentum Decoupling Lock): "
            "Institutional buying streak + volume breakthrough detected. "
            "TD-9 / counter-trend SHORTING is STRICTLY FORBIDDEN during structural institutional breakthroughs per 03-long-short-taxonomy and disclosures. "
            "Route to LONG or HOLD only until TD exhaustion confirmed."
        )
        return result

    # --- P1: Hard Clipping against real available buying power (Winsorization + financial reality) ---
    theoretical = float(signals.get("theoretical_position_size", 0) or 0)
    available = float(balance_data.get("available_buying_power", 0) or 0)
    cap = float(balance_data.get("tail_winsorization_cap", 0.15))  # default 15% of available

    if theoretical > 0 and available > 0:
        max_allowed = available * cap
        if theoretical > max_allowed:
            adjusted = dict(signals)
            adjusted["actual_position_size"] = max_allowed
            adjusted["notes"] = (
                f"Winsorized / hard-clipped from theoretical {theoretical:.2f} "
                f"to {max_allowed:.2f} based on available_buying_power={available:.2f} "
                f"and cap={cap} (from human-provided balance_data)."
            )
            result["status"] = "ADJUSTED"
            result["reason"] = "Hard clipping applied per financial defense rules (P1)."
            result["signals"] = adjusted

    # Always require explicit human balance_data provenance for audit
    if not balance_data.get("source"):
        if result["status"] == "PASSED":
            result["status"] = "ADJUSTED"
        result["signals"].setdefault("notes", "")
        result["signals"]["notes"] += " WARNING: balance_data missing 'source' (human export / paper log). Size recommendation should be manually confirmed."

    return result


def get_momentum_decoupling_note() -> str:
    """For RAG / prompt injection."""
    return (
        "Momentum Decoupling Lock active: When institutional_buying_streak >=3 AND volume_breakthrough, "
        "SHORT proposals on that ticker are rejected. This prevents Huang-style momentum chasing from colliding with TD-9 counter-trend shorting."
    )
