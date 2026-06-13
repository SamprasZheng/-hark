"""SupplyChain_Hunter_Agent — Brain layer specialist for Dragon sub-suppliers.

Receives catalyst from perception (Supply_Chain_Graph_Hook), outputs structured recs for Risk_Officer.
Fits 2 long_new slots in daily 10-signal (genuine bull quadrant only).
Integrates with conflict_resolver (momentum lock), exclusions.

Pydantic output for cross-agent JSON.
"""

from __future__ import annotations

from pydantic import BaseModel
from typing import List, Optional

from sharks.data.supply_chain_graph import get_supply_chain_momentum


class SupplyChainRec(BaseModel):
    agent: str = "SupplyChain_Hunter_Agent"
    catalyst_source: str
    recommended_sub_ticker: str
    reasoning: str
    confidence_score: float
    quadrant: str = "genuine_bull"  # only genuine for long_new
    horizon_days: int = 90


def run_supply_chain_hunter(catalyst_ticker: str = "NVDA", capex_up: float = 0.2) -> SupplyChainRec:
    """Core logic: map catalyst to subs, compute momentum, output Pydantic."""
    mom = get_supply_chain_momentum(catalyst_ticker, capex_up)
    sub = mom["sub_suppliers"][0] if mom["sub_suppliers"] else "TBD"
    rec = SupplyChainRec(
        catalyst_source=f"{catalyst_ticker}_Catalyst",
        recommended_sub_ticker=sub,
        reasoning=f"Sub momentum factor {mom['revenue_turnaround_factor']} from Dragon CAPEX. Low base + technical cross.",
        confidence_score=0.82,
    )
    return rec


# For daily workflow integration (called from daily_picks or decision)
if __name__ == "__main__":
    print(run_supply_chain_hunter().model_dump_json(indent=2))
