"""Supply_Chain_Graph_Hook — Perception for 7 Dragons + tier-2/3 suppliers.

When NVDA/TSM etc. have catalyst, auto-map to sub-suppliers (e.g. 3037, 2233) and compute momentum.
Uses existing data (finviz, polygon, warehouse for prices, known graph in code or data lake).
Part of perception -> SupplyChain_Hunter_Agent.
"""

from __future__ import annotations

from typing import Dict, Any, List

# Known simple graph (extend with real DB or from philosophy/entities/supply)
SUPPLY_GRAPH = {
    "NVDA": ["TSM", "ASML", "AVGO", "3037.TW", "2233.TW"],  # example tier2
    "AAPL": ["TSM", "GLW"],
    # ... add more from existing abm_supply_chain or raw
}

def query_sub_suppliers(ticker: str) -> List[str]:
    """Return tier-2/3 suppliers for a Dragon ticker."""
    return SUPPLY_GRAPH.get(ticker.upper(), [])


def get_supply_chain_momentum(ticker: str, capex_up: float = 0.0) -> Dict[str, Any]:
    """Compute Revenue_Turnaround_Factor for subs based on Dragon CAPEX up-revision."""
    subs = query_sub_suppliers(ticker)
    factor = 1.0 + (capex_up * 0.5) if capex_up > 0 else 1.0  # simple multiplier
    return {
        "dragon": ticker,
        "sub_suppliers": subs,
        "revenue_turnaround_factor": round(factor, 2),
        "recommend": "For low-base subs like 3037 if factor >1.2 and price <50% ATH.",
        "as_of": "use point-in-time from warehouse or polygon",
    }


SUPPLY_HOOKS = {
    "query_sub_suppliers": query_sub_suppliers,
    "get_supply_chain_momentum": get_supply_chain_momentum,
}
