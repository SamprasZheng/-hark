"""Daily portfolio health-check + market-hotspot scan — mature-analyst discipline.

The daily decision-support loop the principal asked for (每天倉位健檢 + 每天掃描市場
熱點 + 增減倉位建議). Its governing philosophy is a seasoned trader's, not a
day-trader's:

  1. DEFAULT TO INACTION. A held position stays held unless there is a *reason* to
     act. Churn is the enemy; the audit's HOLD is the modal outcome.
  2. OFFENSE NEEDS FULL EVIDENCE (十足的證據). A "rotate in / switch / add" call is
     authorised only when a quorum of independent confirmations is present:
     confirmed positive catalyst (消息) + capital-flow data (資金) + volume (交易量)
     + import-export / shipment data (進出口) + earnings / profitability (營利).
     **Absence of evidence is NOT evidence** — every dimension defaults to
     UNCONFIRMED, and only A/B-grade sources clear it (a rumour does not).
  3. DEFENSE IS ALLOWED TO BE FAST (asymmetry). Cutting risk on a systemic signal
     needs a far lower bar than adding risk. 老手 sells quickly, buys slowly.
  4. SYSTEMIC RISK OVERRIDES EVERYTHING. When regime is risk_off/capitulation OR
     funding stress is STRESS/RUPTURE, posture goes DEFENSIVE and the bear-hedge
     menu (也怕大空頭) activates regardless of any offense signal.

Pure logic where possible; data-fetching is injectable so the gate + posture are
unit-testable without network. Composes: regime classifier, funding_chain,
sector_flow, portfolio_audit, leveraged_etf.

This module RECOMMENDS; it never trades (CLAUDE.md §2 / sharks.md). Output is a
structured report written to outputs/daily-health-check-<date>.json.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

# ─── Evidence taxonomy — the 十足的證據 the principal listed ───
EVIDENCE_DIMENSIONS: dict[str, str] = {
    "catalyst_news": "確實利多消息 — confirmed, sourced catalyst (A/B grade, not rumour)",
    "capital_flow":  "資金流向數據 — ETF / institutional / dark-pool flow into the name/theme",
    "volume":        "交易量支持 — volume confirmation / accumulation footprint",
    "trade_data":    "進出口 / 出貨數據 — import-export / shipment / channel-check data",
    "earnings":      "營利支持 — earnings, margin, or forward-guidance support",
}

# Only A/B-grade sources count as 'confirmed' (CLAUDE.md §5 source grading).
# A rumour / social post (C-E) does NOT clear the evidence gate.
CONFIRMING_GRADES = frozenset({"A", "B"})

OFFENSE_ACTIONS = frozenset({"rotate_in", "switch_into", "add", "initiate"})
DEFENSE_ACTIONS = frozenset({"trim", "rotate_out", "switch_out", "exit", "hedge"})


def evidence_gate(
    evidence: Optional[dict] = None,
    action: str = "rotate_in",
    systemic_risk: bool = False,
) -> dict:
    """The 十足的證據 discipline. Decide whether an action is *authorised*.

    Args:
        evidence: {dimension: {"confirmed": bool, "grade": "A".."E", "note": str}}
                  for each of EVIDENCE_DIMENSIONS. Missing/partial dims default to
                  UNCONFIRMED — absence of evidence is not evidence.
        action: one of OFFENSE_ACTIONS (add risk) or DEFENSE_ACTIONS (cut risk).
        systemic_risk: when True, defensive actions are authorised on the systemic
                       trigger alone (the asymmetry — defense may move fast).

    Returns dict with `authorised` (bool), `verdict`, `confirmed`, `missing`,
    `n_confirmed`, and a `rationale`.
    """
    evidence = evidence or {}
    confirmed: list[str] = []
    for dim in EVIDENCE_DIMENSIONS:
        e = evidence.get(dim) or {}
        if bool(e.get("confirmed")) and e.get("grade", "E") in CONFIRMING_GRADES:
            confirmed.append(dim)
    n = len(confirmed)
    missing = [d for d in EVIDENCE_DIMENSIONS if d not in confirmed]

    if action in OFFENSE_ACTIONS:
        earnings_ok = "earnings" in confirmed
        primary_ok = ("catalyst_news" in confirmed) or ("capital_flow" in confirmed)
        authorised = n >= 4 and earnings_ok and primary_ok
        if authorised:
            verdict = "AUTHORISED"
            rationale = (
                f"{n}/5 evidence dims confirmed incl. earnings + a primary "
                f"(news/flow). Conviction switch cleared — 十足的證據."
            )
        else:
            verdict = "INSUFFICIENT-EVIDENCE → HOLD"
            gaps = []
            if n < 4:
                gaps.append(f"only {n}/5 confirmed (need ≥4)")
            if not earnings_ok:
                gaps.append("earnings/營利 not confirmed (mandatory)")
            if not primary_ok:
                gaps.append("no confirmed primary catalyst (news) or capital-flow")
            rationale = (
                "Offense bar NOT met: " + "; ".join(gaps) +
                ". Default to HOLD — do not chase without full evidence."
            )
    elif action in DEFENSE_ACTIONS:
        # Asymmetry: defense clears on a systemic trigger OR ≥2 deterioration dims.
        authorised = systemic_risk or n >= 2
        if systemic_risk:
            verdict = "AUTHORISED (systemic)"
            rationale = "Systemic-risk trigger active — defensive action cleared on the fast path."
        elif authorised:
            verdict = "AUTHORISED"
            rationale = f"{n}/5 deterioration signals confirmed (≥2) — defensive trim cleared."
        else:
            verdict = "WATCH"
            rationale = (
                f"Only {n}/5 deterioration signals — not yet actionable; keep on watch. "
                "Defense may move fast, but still needs a reason."
            )
    else:
        raise ValueError(
            f"unknown action {action!r}; expected one of "
            f"{sorted(OFFENSE_ACTIONS | DEFENSE_ACTIONS)}"
        )

    return {
        "action": action,
        "authorised": authorised,
        "verdict": verdict,
        "n_confirmed": n,
        "confirmed": confirmed,
        "missing": missing,
        "rationale": rationale,
    }


def mature_analyst_posture(regime_label: str, funding_verdict: str = "CALM") -> dict:
    """Combine regime + funding-stress into a book-level posture + sizing guidance.

    Encodes rule #4 (systemic risk overrides) and the 老手 asymmetry. The posture
    drives whether the bear-hedge menu (也怕大空頭) is activated.
    """
    systemic = (regime_label in {"risk_off", "capitulation"}
                or funding_verdict in {"STRESS", "RUPTURE"})

    if funding_verdict == "RUPTURE" or regime_label == "capitulation":
        posture = "MAX_DEFENSIVE"
        sizing = "Cash-heavy. No new longs. Deploy inverse/vol hedges. Preserve capital."
    elif systemic:
        posture = "DEFENSIVE"
        sizing = "Cut leveraged + lowest-conviction first. Tighten caps. Hedge tactically."
    elif regime_label == "late_bull":
        posture = "NEUTRAL-CAUTIOUS"
        sizing = ("Ride the trend but raise the new-entry bar; trim worst-decay leverage; "
                  "let winners run, add only on full evidence.")
    elif regime_label == "bull_trend":
        posture = "RISK_ON"
        sizing = "Full tier-2/3 caps permitted; still gate adds on evidence."
    else:  # neutral / unknown
        posture = "NEUTRAL"
        sizing = "Balanced. No forced action. Hold quality, prune obvious decay."

    deploy_hedges = posture in {"DEFENSIVE", "MAX_DEFENSIVE"}
    return {
        "posture": posture,
        "systemic_risk": systemic,
        "deploy_bear_hedges": deploy_hedges,
        "sizing_guidance": sizing,
        "inputs": {"regime": regime_label, "funding_verdict": funding_verdict},
    }


def scan_hotspots(
    closes=None,
    as_of=None,
    rotation: Optional[dict] = None,
) -> dict:
    """Daily market-hotspot scan (每天掃描市場熱點) via sector rotation.

    A 'hotspot' is a sector rotating IN on relative strength — a WATCH candidate,
    explicitly NOT an auto-buy. Any rotate-in into a hotspot name must still clear
    evidence_gate(). Accepts a precomputed `rotation` dict (for tests) or computes
    it from `closes` via sector_flow.detect_rotation.
    """
    if rotation is None:
        if closes is None:
            return {
                "available": False,
                "note": "no price data supplied — hotspot scan skipped (provide closes or rotation).",
            }
        from sharks.regime.sector_flow import detect_rotation  # local import: pandas
        rotation = detect_rotation(closes, as_of)

    rotating_in = rotation.get("rotating_in", [])
    leaders = rotation.get("leaders", [])
    return {
        "available": True,
        "rotating_in": rotating_in,
        "leaders": leaders,
        "rotating_out": rotation.get("rotating_out", []),
        "laggards": rotation.get("laggards", []),
        "note": (
            "A hotspot (rotating_in / leader sector) is a WATCH candidate, not a "
            "buy. Any rotate-in must still clear evidence_gate (十足的證據): confirmed "
            "catalyst + flow + volume + trade-data + earnings. Sector heat alone is "
            "necessary, never sufficient."
        ),
    }


def _latest_audit(out_dir: Path) -> Optional[dict]:
    files = sorted(out_dir.glob("portfolio-audit-*.json"))
    if not files:
        return None
    try:
        return json.loads(files[-1].read_text(encoding="utf-8"))
    except Exception:
        return None


def _position_health(audit: Optional[dict]) -> dict:
    """Summarise the latest portfolio-audit into actionable buckets, surfacing
    leveraged-decay flags. Pure transform over the audit JSON."""
    if not audit:
        return {"available": False, "note": "no portfolio-audit-*.json found — run portfolio_audit first."}

    p1 = audit.get("portfolio_1_audit", [])
    lev = {r["ticker"]: r for r in audit.get("p1_leveraged_audit", [])}

    sells, trims, holds = [], [], []
    for r in p1:
        v = (r.get("verdict") or "").upper()
        entry = {"ticker": r["ticker"], "verdict": r.get("verdict")}
        lr = lev.get(r["ticker"])
        if lr:
            entry["decay_pct"] = lr.get("annual_decay_pct")
            entry["decay_verdict"] = lr.get("verdict")
        if v.startswith("SELL"):
            sells.append(entry)
        elif "TRIM" in v:
            trims.append(entry)
        else:
            holds.append(entry)

    # Worst-decay leveraged names — the structural-bleed priority list.
    worst_decay = sorted(
        audit.get("p1_leveraged_audit", []),
        key=lambda x: x.get("annual_decay_pct", 0), reverse=True,
    )[:5]

    return {
        "available": True,
        "sell_candidates": sells,
        "trim_candidates": trims,
        "hold": holds,
        "worst_decay_leveraged": [
            {"ticker": x["ticker"], "factor": x.get("factor"),
             "annual_decay_pct": x.get("annual_decay_pct"), "verdict": x.get("verdict")}
            for x in worst_decay
        ],
        "concentration_context": audit.get("concentration_context", {}).get("note"),
    }


def run_health_check(
    out_dir: Path = Path("outputs"),
    funding_readings: Optional[dict] = None,
    closes=None,
    as_of=None,
    today: Optional[str] = None,
    write: bool = True,
) -> dict:
    """Assemble the daily health-check report. All data inputs are optional and
    injectable; missing inputs degrade gracefully (noted, never faked)."""
    from sharks.regime.classifier import classify_regime
    from sharks.regime.funding_chain import funding_stress_score
    from sharks.scoring.leveraged_etf import bear_hedge_menu

    regime = classify_regime()
    regime_label = regime.get("label", "neutral")

    if funding_readings:
        funding = funding_stress_score(funding_readings)
    else:
        funding = {
            "verdict": "CALM", "score": None,
            "note": ("no live funding indicators (fetch_funding_indicators is a "
                     "Phase-2 stub) — assuming CALM. A real STRESS/RUPTURE would "
                     "flip posture DEFENSIVE; wire FRED ALFRED to make this live."),
            "live_data": False,
        }
    funding_verdict = funding.get("verdict", "CALM")

    posture = mature_analyst_posture(regime_label, funding_verdict)
    audit = _latest_audit(out_dir)
    health = _position_health(audit)
    hotspots = scan_hotspots(closes=closes, as_of=as_of)

    # Default recommendation posture: act on defense (systemic), hold on offense.
    recommendations: list[dict] = []
    if posture["systemic_risk"]:
        recommendations.append({
            "type": "DEFENSIVE-OVERRIDE",
            "action": "de-risk",
            "detail": (
                "Systemic risk active (regime/funding). Cut leveraged + lowest-"
                "conviction first; consider deploying the bear-hedge menu. Defensive "
                "actions clear on the fast path (evidence_gate systemic=True)."
            ),
        })
    else:
        recommendations.append({
            "type": "DEFAULT-HOLD",
            "action": "hold",
            "detail": (
                "No systemic trigger. Default posture is HOLD — do not churn. Any "
                "rotate-in / switch requires FULL evidence (十足的證據) via "
                "evidence_gate; sector heat alone is not sufficient."
            ),
        })

    # If the audit already flags structural-decay leverage, surface a standing
    # (regime-independent) defensive recommendation — leverage decay is not a
    # 'systemic' event but it IS a confirmed structural drag (defense-side evidence).
    if health.get("available") and health.get("worst_decay_leveraged"):
        top = health["worst_decay_leveraged"][0]
        if (top.get("annual_decay_pct") or 0) >= 30:
            recommendations.append({
                "type": "STRUCTURAL-DECAY",
                "action": "trim",
                "ticker": top["ticker"],
                "detail": (
                    f"{top['ticker']} ({top.get('factor')}x) carries "
                    f"~{top.get('annual_decay_pct')}%/yr structural decay → "
                    f"{top.get('verdict')}. Leveraged ETFs are tactical, not core; "
                    "trimming worst-decay is a confirmed-evidence defensive trim, "
                    "not market-timing."
                ),
            })

    report = {
        "as_of": today or datetime.now(timezone.utc).isoformat(),
        "schema_version": 1,
        "report_type": "daily_health_check",
        "philosophy": (
            "Default to inaction. Offense needs 十足的證據; defense may move fast; "
            "systemic risk overrides everything toward defensive. RECOMMEND-ONLY."
        ),
        "regime": {"label": regime_label, "reasons": regime.get("reasons"),
                   "bubble_guard_floor": regime.get("bubble_guard_floor")},
        "funding_stress": funding,
        "posture": posture,
        "position_health": health,
        "hotspots": hotspots,
        "recommendations": recommendations,
        "bear_hedge_menu": bear_hedge_menu() if posture["deploy_bear_hedges"] else
                           {"activated": False, "note": "no systemic trigger — hedges on standby."},
        "evidence_gate_reference": {
            "dimensions": EVIDENCE_DIMENSIONS,
            "offense_rule": "≥4/5 confirmed (A/B grade) AND earnings AND a primary (news|flow).",
            "defense_rule": "systemic trigger OR ≥2/5 deterioration signals.",
            "note": "Use evidence_gate(evidence, action, systemic_risk) per candidate before any switch.",
        },
    }

    if write:
        out_dir.mkdir(parents=True, exist_ok=True)
        date_str = (today or datetime.now(timezone.utc).isoformat())[:10]
        out_path = out_dir / f"daily-health-check-{date_str}.json"
        out_path.write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")
        print(f"wrote {out_path}", file=sys.stderr)

    return report


def main() -> int:
    run_health_check()
    return 0


if __name__ == "__main__":
    sys.exit(main())
