"""True total-exposure gauge — RSU + active book + income/career on ONE cycle.

Standard portfolio tools score only the brokerage book. They miss that, for an
employee whose RSU dominates net worth and whose salary IS the cycle, a downturn
craters assets AND income TOGETHER — on top of any debt. This module aggregates all
containers, stress-tests the CORRELATED hit (beta-scaled asset drop + an income
shock for the cycle you work in), and flags concentration.

PURE logic; NO private numbers live in the repo — the caller supplies them. Advisory
context only; RSU is a tax/employment decision, never a trade.
"""

from __future__ import annotations

from typing import Optional


def true_exposure(containers: dict, debt_usd: float = 0.0) -> dict:
    """containers: {name: usd_value}. Returns gross assets, net worth (assets − debt),
    and each container's share."""
    assets = float(sum(containers.values()))
    return {
        "gross_assets_usd": round(assets, 0),
        "debt_usd": round(debt_usd, 0),
        "net_liquid_worth_usd": round(assets - debt_usd, 0),
        "shares_pct": {k: round(100.0 * v / assets, 1) for k, v in containers.items()} if assets else {},
    }


def crash_scenario(containers: dict, betas: dict, market_drop: float = 0.35,
                   debt_usd: float = 0.0, annual_income_usd: float = 0.0,
                   income_hit_frac: float = 0.45) -> dict:
    """Stress test: a `market_drop` selloff hits each container via its beta (capped
    −95%), plus an income shock (grant cut + bonus cut + layoff risk) on the cycle the
    person works in. Surfaces the simultaneous asset + income + debt blow."""
    after, loss = {}, {}
    for k, v in containers.items():
        drop = min(betas.get(k, 1.0) * market_drop, 0.95)
        after[k] = round(v * (1 - drop), 0)
        loss[k] = round(v * drop, 0)
    a_before = float(sum(containers.values()))
    a_after = float(sum(after.values()))
    income_loss = round(annual_income_usd * income_hit_frac, 0)
    return {
        "market_drop": market_drop,
        "assets_before": round(a_before, 0), "assets_after": round(a_after, 0),
        "asset_loss": round(a_before - a_after, 0),
        "per_container_after": after, "per_container_loss": loss,
        "net_worth_before": round(a_before - debt_usd, 0),
        "net_worth_after": round(a_after - debt_usd, 0),
        "income_loss_est": income_loss,
        "total_hit_assets_plus_income": round((a_before - a_after) + income_loss, 0),
    }


def concentration_verdict(exposure: dict, single_name_pct: float, risk_on_pct: float) -> dict:
    """Flag dangerous concentration. single_name_pct = the biggest one-stock share;
    risk_on_pct = everything that craters together in a selloff."""
    flags = []
    if single_name_pct >= 60:
        flags.append(f"single-name {single_name_pct:.0f}% >= 60% (extreme)")
    elif single_name_pct >= 35:
        flags.append(f"single-name {single_name_pct:.0f}% >= 35%")
    if risk_on_pct >= 85:
        flags.append(f"risk-on {risk_on_pct:.0f}% >= 85% (no ballast)")
    gross = exposure.get("gross_assets_usd", 0) or 1
    if exposure.get("net_liquid_worth_usd", 0) < 0.2 * gross:
        flags.append("net worth < 20% of gross assets (debt-levered)")
    level = "EXTREME" if len(flags) >= 2 else ("ELEVATED" if flags else "OK")
    return {"level": level, "flags": flags}


def main() -> int:  # pragma: no cover - illustrative (NON-private placeholder numbers)
    import sys
    ex_containers = {"EMPLOYER_RSU": 100.0, "ACTIVE_BOOK": 10.0, "ETF": 5.0}
    ex_betas = {"EMPLOYER_RSU": 2.0, "ACTIVE_BOOK": 2.5, "ETF": 0.8}
    exp = true_exposure(ex_containers, debt_usd=80.0)
    cs = crash_scenario(ex_containers, ex_betas, market_drop=0.35, debt_usd=80.0,
                        annual_income_usd=100.0, income_hit_frac=0.45)
    print("exposure:", exp, file=sys.stderr)
    print("crash:", cs, file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
