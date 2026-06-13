#!/usr/bin/env python3
"""
Trading Society -- Layer 1: short-term allocation recommendation

PPST Declaration (this PROGRAM):
- PROJECT: Trading Society
- PROGRAM: simulation/layer1_allocation.py
- SKILL:   present the society vote as a next-quarter allocation (new/hold/trim,
           core/satellite split, position caps)
- TARGET:  Turn the 14-trader portfolio vote into a readable, recommend-only
           "next-quarter allocation" -- core growth (large-cap, 80% of growth) +
           satellite (small-cap high-beta, 20%) + dynamic defensive leg -- with
           NEW / HOLD / TRIM lists vs the prior run, under the regime guardrail +
           valuation floor + concentration caps. No LLM. Not a capital order.

Layer 1 of the 3-layer framework (short-term decision support, top priority).
Layer 2 = the 2018-2026 evolving competition; Layer 3 = the 10-year potential
scorecard (layer3_potential.py).

Caps (principal spec): core single-name <= 12%, satellite single-name <= 6%,
single-sector <= 35%. Defensive floor from regime/valuation (>= 35% when high-val).

Run: python simulation/layer1_allocation.py
"""

from __future__ import annotations

import glob
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

CORE_NAME_CAP = 0.12
SAT_NAME_CAP = 0.06
CORE_SHARE = 0.80   # core gets 80% of the growth leg, satellite 20%
SAT_SHARE = 0.20


def _next_quarter_label(as_of: str) -> str:
    y, m = int(as_of[:4]), int(as_of[5:7])
    q = (m - 1) // 3 + 1
    nq, ny = (q + 1, y) if q < 4 else (1, y + 1)
    return f"{ny} Q{nq}"


def _prior_holdings() -> Set[str]:
    files = sorted(glob.glob(str(_ROOT / "outputs" / "layer1-allocation-*.json")))
    if not files:
        return set()
    try:
        prior = json.loads(Path(files[-1]).read_text(encoding="utf-8"))
        held = set()
        for k in ("core", "satellite"):
            held |= {x["ticker"] for x in prior.get("allocation", {}).get(k, [])}
        held |= {x["ticker"] for x in
                 prior.get("allocation", {}).get("defensive", {}).get("holdings", [])}
        return held
    except Exception:
        return set()


def run() -> Dict[str, Any]:
    from simulation.universe_competition import build_universe
    from simulation.backtest_runner import load_pit_series
    from simulation.portfolio_generator import generate_portfolio

    uni = build_universe(max_names=170)
    series = {t: p for t, p in load_pit_series(uni["tickers"]).items() if p}
    pf = generate_portfolio("next_quarter", 126, series, uni)

    regime = pf.get("regime_guardrail") or {}
    dd = pf["defensive_decision"]
    growth = dd["core_growth_ratio"]
    core_leg = pf["core_growth_leg"]
    defensive = pf["defensive_leg"]
    specialists = pf.get("specialists") or {}
    macro = pf["macro_risk_environment"]

    # satellite = Small Cap Catalyst Hunter picks (small-cap high-beta)
    sat_src = (specialists.get("top_picks", {}) or {}).get("SMALL_CAP_CATALYST_HUNTER", [])
    sat_names = {p["ticker"] for p in sat_src}

    # core = the leg's large-cap names (exclude satellite small-caps)
    core_src = [c for c in core_leg if c["ticker"] not in sat_names]
    core_total = sum(c["weight"] for c in core_src) or 1.0
    core = [{"ticker": c["ticker"],
             "weight": round(min(CORE_NAME_CAP, CORE_SHARE * growth * c["weight"] / core_total), 4),
             "sector": c.get("sector"), "backers": c.get("backers", [])}
            for c in core_src]

    sat_top = sat_src[:4]
    per_sat = (SAT_SHARE * growth) / max(1, len(sat_top))
    satellite = [{"ticker": p["ticker"], "weight": round(min(SAT_NAME_CAP, per_sat), 4),
                  "score": p.get("score"), "suggested_size": p.get("suggested_size")}
                 for p in sat_top]

    # NEW / HOLD / TRIM vs the prior Layer-1 run
    prior = _prior_holdings()
    current = ({a["ticker"] for a in core} | {a["ticker"] for a in satellite}
               | {h["ticker"] for h in defensive["holdings"]})
    new = sorted(current - prior)
    hold = sorted(current & prior)
    trim = sorted(prior - current)
    baseline = not prior

    as_of = pf["as_of"]
    result = {
        "type": "trading_society_layer1_allocation",
        "as_of_timestamp": datetime.now(timezone.utc).isoformat(),
        "role": "writer", "project": "Trading Society",
        "program": "simulation/layer1_allocation.py",
        "llm_involvement": "none", "layer": 1,
        "quarter": _next_quarter_label(as_of), "as_of": as_of,
        "regime": {"label": regime.get("regime"),
                   "macro_score": macro.get("score_0_100"),
                   "buffett_indicator": macro.get("buffett_indicator"),
                   "defensive_floor": dd.get("defensive_ratio"),
                   "growth_ratio": growth},
        "allocation": {"core": core, "satellite": satellite, "defensive": defensive},
        "decision_lists": {"new": new, "hold": hold, "trim": trim,
                           "is_baseline": baseline},
        "caps": {"core_name": CORE_NAME_CAP, "satellite_name": SAT_NAME_CAP,
                 "sector": 0.35},
        "disclaimer": ("Layer-1 short-term allocation. Recommend-only RESEARCH; not a "
                       "capital order and does not replace the canonical 10-signal "
                       "pipeline or the Risk-Officer gate. Weights are relative "
                       "(cost-aware) backtest votes; macro real-FRED, sectors real-"
                       "Finviz. Promotion needs human + Risk-Officer gate + review."),
    }
    return result


def format_readout(r: Dict[str, Any]) -> str:
    reg = r["regime"]
    lines = []
    lines.append(f"=== {r['quarter']} 配置建議 (as of {r['as_of']}) ===")
    lines.append(f"總體 Regime: {reg['label']} | Macro risk {reg['macro_score']}/100 | "
                 f"Buffett Indicator {reg['buffett_indicator']}%")
    floor = reg["defensive_floor"]
    lines.append(f"防禦強度: {floor*100:.0f}%"
                 + (" (高估值 floor 強制)" if reg['buffett_indicator'] and reg['buffett_indicator'] > 200 else ""))
    dl = r["decision_lists"]
    if dl["is_baseline"]:
        lines.append("(首次基準配置 -- 全部列為新增;下次跑會給 新增/繼續持有/減持 diff)")

    core = r["allocation"]["core"]
    lines.append(f"\n核心成長腿 (大型股, {sum(c['weight'] for c in core)*100:.0f}%):")
    for c in core:
        tag = "[新增]" if c["ticker"] in dl["new"] else ("[繼續持有]" if c["ticker"] in dl["hold"] else "")
        lines.append(f"   {c['ticker']:<6} {c['weight']*100:>5.1f}%  {tag}  ({c.get('sector')})")
    if dl["trim"]:
        lines.append(f"   減持/觀望(已退出本季): {', '.join(dl['trim'])}")

    sat = r["allocation"]["satellite"]
    lines.append(f"\n衛星層 (小盤高 Beta, {sum(s['weight'] for s in sat)*100:.0f}%) "
                 f"-- Small Cap Catalyst Hunter:")
    for s in sat:
        lines.append(f"   {s['ticker']:<6} {s['weight']*100:>5.1f}%  (score {s['score']})")

    d = r["allocation"]["defensive"]
    held = ", ".join(h["ticker"] for h in d["holdings"][:8])
    lines.append(f"\n防禦腿 ({reg['defensive_floor']*100:.0f}%): "
                 f"現金 {d['cash_pct']*100:.1f}% + {held}")
    lines.append("\n" + r["disclaimer"])
    return "\n".join(lines)


def _ascii_summary(r: Dict[str, Any]) -> str:
    """ASCII-only console summary (the cp950 console mangles CJK; the full
    Chinese readout is written to a UTF-8 .md file instead)."""
    reg, dl = r["regime"], r["decision_lists"]
    out = [f"Layer 1 -- {r['quarter']} allocation (as of {r['as_of']})",
           f"  regime={reg['label']} macro={reg['macro_score']} BI={reg['buffett_indicator']}% "
           f"defensive={reg['defensive_floor']*100:.0f}% growth={reg['growth_ratio']*100:.0f}%"]
    core = r["allocation"]["core"]
    out.append(f"  CORE (large, {sum(c['weight'] for c in core)*100:.0f}%): "
               + ", ".join(f"{c['ticker']} {c['weight']*100:.1f}%" for c in core[:10]))
    sat = r["allocation"]["satellite"]
    out.append(f"  SATELLITE (small, {sum(s['weight'] for s in sat)*100:.0f}%): "
               + ", ".join(f"{s['ticker']} {s['weight']*100:.1f}%" for s in sat))
    d = r["allocation"]["defensive"]
    out.append(f"  DEFENSIVE ({reg['defensive_floor']*100:.0f}%): cash {d['cash_pct']*100:.1f}% + "
               + ", ".join(h["ticker"] for h in d["holdings"][:6]))
    out.append(f"  new={len(dl['new'])} hold={len(dl['hold'])} trim={len(dl['trim'])}"
               + (" (baseline)" if dl["is_baseline"] else ""))
    return "\n".join(out)


def main() -> int:
    r = run()
    stamp = r["as_of_timestamp"][:10]
    out = _ROOT / "outputs" / f"layer1-allocation-{stamp}.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(r, indent=2, ensure_ascii=False), encoding="utf-8")
    # full Chinese readout -> UTF-8 .md (renders correctly; console is cp950)
    md = _ROOT / "outputs" / f"layer1-allocation-{stamp}.md"
    md.write_text(format_readout(r), encoding="utf-8")
    print(_ascii_summary(r))
    print(f"\nReadout (UTF-8, Chinese): {md.relative_to(_ROOT)}")
    print(f"Artifact (JSON):          {out.relative_to(_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
