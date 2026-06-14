"""Social_KOL_Validator_Agent — Brain layer for de-risking KOL small-cap ideas.

Validates with chips, TD-9 volume guard, exclusions (SI>20%, small mktcap).
Outputs for short_new or long_new (or reject as trap).
Integrates with kol_logic_scraper, conflict_resolver, 03-long-short-taxonomy.

Pydantic for structured handoff to Risk_Officer.
"""

from __future__ import annotations

from pydantic import BaseModel
from typing import Optional

from sharks.data.kol_logic_scraper import validate_kol_chips


class KOLValidation(BaseModel):
    agent: str = "Social_KOL_Validator_Agent"
    kol_stock: str
    action_type: str  # "LONG_SETUP" | "SHORT_ATTACK" | "REJECT_TRAP"
    is_meme_trap: bool
    chips_verification: str
    confidence: float = 0.0


def run_social_kol_validator(kol_stock: str, kol_thesis: Optional[dict] = None) -> KOLValidation:
    """Validate KOL rec; enforce guards."""
    val = validate_kol_chips(kol_stock, kol_thesis or {})
    action = "LONG_SETUP" if not val.get("is_meme_trap") else "REJECT_TRAP"
    if "SHORT" in (kol_thesis or {}).get("thesis", "") and not val.get("is_meme_trap"):
        action = "SHORT_ATTACK"
    return KOLValidation(
        kol_stock=kol_stock,
        action_type=action,
        is_meme_trap=val.get("is_meme_trap", True),
        chips_verification=val.get("chips_verification", "Failed validation"),
        confidence=0.75 if not val.get("is_meme_trap") else 0.1,
    )


if __name__ == "__main__":
    print(run_social_kol_validator("SYNA").model_dump_json(indent=2))
