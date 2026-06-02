"""Sharks CLI entry point.

Phase 1: argparse skeleton. All subcommands print stub messages and exit 0.
Phase 2+ wires real implementations per docs/ROADMAP.md.

Usage:
    sharks pick --mode {low,high,auto} [--dry-run]
    sharks ingest --source <path>
    sharks wiki lint
"""

from __future__ import annotations

import argparse
import sys
from typing import Sequence


def _cmd_pick(args: argparse.Namespace) -> int:
    print(
        f"[stub] sharks pick called with mode={args.mode}, dry_run={args.dry_run}. "
        f"Phase 3 will implement signal aggregation, the four-dimension scorers, "
        f"the conflict arbitration matrix, and the daily 10-signal output. "
        f"See docs/ROADMAP.md (Phase 3)."
    )
    return 0


def _cmd_ingest(args: argparse.Namespace) -> int:
    print(
        f"[stub] sharks ingest called with source={args.source!r}. "
        f"Phase 2 will implement the Compile-first runtime that reads raw/ and "
        f"updates wiki/ pages with as_of_timestamp discipline. "
        f"See docs/ROADMAP.md (Phase 2)."
    )
    return 0


def _cmd_health_check(args: argparse.Namespace) -> int:
    """Daily portfolio health-check + market-hotspot scan (mature-analyst posture).

    Real implementation (not a stub): composes the regime classifier, funding-chain
    stress, the latest portfolio-audit, leveraged-decay flags, and sector hotspots
    into a recommend-only daily report. RECOMMEND-ONLY — never trades.
    """
    from pathlib import Path

    from sharks.daily_health_check import run_health_check

    report = run_health_check(out_dir=Path(args.out_dir), write=not args.dry_run)
    posture = report["posture"]
    print(f"posture        : {posture['posture']}  (systemic_risk={posture['systemic_risk']})")
    print(f"regime         : {report['regime']['label']}")
    print(f"funding stress : {report['funding_stress']['verdict']} "
          f"(live={report['funding_stress'].get('live_data', False)})")
    print(f"sizing         : {posture['sizing_guidance']}")
    print("recommendations:")
    for rec in report["recommendations"]:
        tk = f" {rec.get('ticker')}" if rec.get("ticker") else ""
        print(f"  - [{rec['type']}] {rec['action']}{tk}")
    ph = report.get("position_health", {})
    if ph.get("available"):
        print(f"sell candidates: {[r['ticker'] for r in ph.get('sell_candidates', [])]}")
        print(f"trim candidates: {[r['ticker'] for r in ph.get('trim_candidates', [])]}")
    if posture["deploy_bear_hedges"]:
        print("bear hedges    : ACTIVATED (也怕大空頭 — systemic trigger live)")
    else:
        print("bear hedges    : on standby (no systemic trigger)")
    return 0


def _cmd_tech_dd(args: argparse.Namespace) -> int:
    """tech/ due-diligence → FOM sleeve overlay (observe-first, recommend-only).

    Annotates the broad tech/ DD registry with verdict × bubble_guard sleeve
    routing + a bounded weight tilt. OBSERVE-ONLY — does not touch final_fom.
    See tech/fom-integration.md.
    """
    from pathlib import Path

    from sharks.scoring.tech_dd import build_report, main as _tech_dd_main

    if args.dry_run:
        rep = build_report(out_dir=Path(args.out_dir))
        counts = {s: len(v) for s, v in rep["buckets"].items()}
        print(f"[dry-run] tech-dd overlay (observe-first). "
              f"coverage={rep['coverage']} fom_used={rep['fom_report_used']} buckets={counts}")
        return 0
    return _tech_dd_main(Path(args.out_dir))


def _cmd_rf_cycle(args: argparse.Namespace) -> int:
    """RF / power-management / analog rush-order cycle tracker (variable #15).

    Reads the two doors separately (leading = industrial/AI/distribution,
    lagging = handset) from a price tape + a curated hard-evidence layer
    (book-to-bill / price hikes / channel-inventory days). RECOMMEND-ONLY —
    emits a cycle reading, never a trade. See tech/rf-connectivity.md.
    """
    from pathlib import Path

    from sharks.scoring.rfpm_cycle import run, write_output

    reading = run(as_of=args.as_of, network=not args.no_network)
    print(reading.headline)
    print(f"  leading evidence={reading.evidence_score_leading:+.2f} "
          f"lagging evidence={reading.evidence_score_lagging:+.2f}")
    if not args.dry_run:
        path = write_output(Path(args.out_dir), reading)
        print(f"wrote {path}")
    return 0


def _cmd_rf_evidence(args: argparse.Namespace) -> int:
    """Monthly: refresh the rf-cycle AUTO evidence proxy layer from financials.

    Derives book-to-bill / pricing-power / recovery proxies from distributor &
    analog revenue-YoY + gross-margin-YoY-Δ (yfinance). Writes
    outputs/rfpm-cycle-evidence-auto.json, merged UNDER the hand-curated layer by
    rf-cycle. RECOMMEND-ONLY.
    """
    from pathlib import Path

    from sharks.scoring.rfpm_evidence_fetch import fetch_and_write

    path = fetch_and_write(as_of=args.as_of, out_dir=Path(args.out_dir),
                           network=not args.no_network)
    print(f"wrote {path}")
    return 0


def _cmd_demand_val(args: argparse.Namespace) -> int:
    """Order/demand-anchored forward valuation for the RF/semi names.

    3 layers: curated order-book (B:B/backlog/contracted/segment-YoY) + yfinance
    earnings-quality + curated intangible scorecard (moat/switching/optionality/
    concentration). The RIGHT lens for earnings-inflecting names; flags order
    deceleration as the kill-switch. RECOMMEND-ONLY.
    """
    from pathlib import Path

    from sharks.scoring.demand_valuation import run, write_output

    rows = run(network=not args.no_network)
    if not args.dry_run:
        path = write_output(Path(args.out_dir), rows, args.as_of or _today())
        print(f"wrote {path}")
    for r in sorted(rows, key=lambda x: (x["premium_to_fair"] is None, x["premium_to_fair"] or 0)):
        prem = r["premium_to_fair"]
        print(f"  {r['ticker']:6} fairPE={r['adjusted_fair_pe']} "
              f"prem={(f'{prem*100:+.0f}%' if prem is not None else 'n/a')} "
              f"traj={r['order_trajectory']} — {r['verdict']}")
    return 0


def _cmd_daily_brief(args: argparse.Namespace) -> int:
    """游庭澔-style daily brief (早報/午報/晚報) → MD + HTML + Discord.

    Macro-first morning-show flow: tape -> 速解讀 (why) -> 類股 -> 台股連結 -> 行事曆;
    午/晚 editions add 個人進出場建議 + 推薦潛力股 (reused from fom-alpha / portfolio-
    audit JSONs, never recomputed). Observe-first / educational — not buy/sell advice.
    """
    from sharks.daily_brief import generate

    r = generate(args.edition, args.out_dir)
    print(f"[{r['edition']}] wrote {r['md']}")
    print(f"          + {r['html']}")
    print(f"          + {r['discord']} ({r['discord_len']} chars)")
    return 0


def _cmd_news_fetch(args: argparse.Namespace) -> int:
    """Free multi-source market-news RSS → outputs/news-headlines-<date>.json.

    Fills the daily-brief news slot (event-driven 隔夜頭條). Public RSS only, graceful
    per-source fallback, zero new deps. Grade C/D — headlines, not verified.
    """
    from sharks.news_fetch import fetch_and_write

    p = fetch_and_write(args.out_dir)
    print(f"news: {len(p['headlines'])} headlines | ok={p['sources_ok']} | failed={p['sources_failed']}")
    return 0


def _cmd_checklist(args: argparse.Namespace) -> int:
    """Standardized decision checklist — one gated scorecard per ticker.

    Composes exclusion (06) + regime + FOM + valuation + order/demand trajectory
    + RF cycle (#15) + 4-dimension arbitration (02) + 4-quadrant route (03) +
    horizon/size (01+08) + invalidation + calibrated confidence (05) into a single
    recommend-only readout. See philosophy/_proposals/standard-decision-checklist.md.
    RECOMMEND-ONLY — emits a scorecard + evidence, never a trade.
    """
    from pathlib import Path

    # The scorecard carries CJK (quadrant labels) + glyphs; force UTF-8 so it never
    # crashes on a cp950 / non-UTF-8 console (the JSON artifact is UTF-8 regardless).
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

    from sharks.decision.checklist import run_checklist, write_output, format_scorecard

    result = run_checklist(args.ticker, as_of=args.as_of, network=not args.no_network)
    print(format_scorecard(result))
    if not args.dry_run:
        path = write_output(Path(args.out_dir), result)
        print(f"wrote {path}")
    return 0


def _today() -> str:
    from datetime import datetime
    return datetime.now().strftime("%Y-%m-%d")


def _cmd_wiki_lint(args: argparse.Namespace) -> int:
    print(
        f"[stub] sharks wiki lint called. "
        f"Phase 2 will implement frontmatter validation, [[link]] resolution, "
        f"as_of_timestamp checks, and log.md format verification. "
        f"See wiki/README.md and philosophy/09-point-in-time.md."
    )
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="sharks",
        description=(
            "Sharks trading system. "
            "Phase 1: scaffold only. See docs/ROADMAP.md."
        ),
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # `sharks pick` — produce the daily 10-signal output
    p_pick = subparsers.add_parser(
        "pick",
        help="produce the daily 10-signal recommendation output (Phase 3 stub)",
    )
    p_pick.add_argument(
        "--mode",
        choices=["low", "high", "auto"],
        default="auto",
        help="frequency mode; see philosophy/07-mode-switch.md",
    )
    p_pick.add_argument(
        "--dry-run",
        action="store_true",
        help="evaluate signals but do not write outputs/ or wiki/05_recommendations/",
    )
    p_pick.set_defaults(func=_cmd_pick)

    # `sharks ingest` — Compile-first runtime entry
    p_ingest = subparsers.add_parser(
        "ingest",
        help="compile a raw/ source into wiki/ pages (Phase 2 stub)",
    )
    p_ingest.add_argument(
        "--source",
        required=True,
        help="path to the raw/ source file to compile",
    )
    p_ingest.set_defaults(func=_cmd_ingest)

    # `sharks health-check` — daily portfolio health-check + hotspot scan (REAL)
    p_health = subparsers.add_parser(
        "health-check",
        help="daily portfolio health-check + market-hotspot scan (mature-analyst, recommend-only)",
    )
    p_health.add_argument(
        "--out-dir", default="outputs",
        help="directory holding portfolio-audit-*.json + where the report is written",
    )
    p_health.add_argument(
        "--dry-run", action="store_true",
        help="print the summary but do not write outputs/daily-health-check-*.json",
    )
    p_health.set_defaults(func=_cmd_health_check)

    # `sharks tech-dd` — tech/ DD → FOM sleeve overlay (REAL, observe-first)
    p_techdd = subparsers.add_parser(
        "tech-dd",
        help="tech/ due-diligence → FOM sleeve overlay (observe-first, recommend-only)",
    )
    p_techdd.add_argument(
        "--out-dir", default="outputs",
        help="dir holding fom-monthly-*.json + where tech-dd-overlay.json is written",
    )
    p_techdd.add_argument(
        "--dry-run", action="store_true",
        help="print the sleeve-bucket summary but do not write outputs/tech-dd-overlay.json",
    )
    p_techdd.set_defaults(func=_cmd_tech_dd)

    # `sharks rf-cycle` — RF/power-mgmt/analog rush-order cycle tracker (REAL)
    p_rf = subparsers.add_parser(
        "rf-cycle",
        help="RF / power-mgmt / analog rush-order cycle tracker (variable #15, recommend-only)",
    )
    p_rf.add_argument(
        "--as-of", default=None,
        help="point-in-time date YYYY-MM-DD (default: today); slices price + evidence to <= as_of",
    )
    p_rf.add_argument(
        "--no-network", action="store_true",
        help="evidence-only read; skip the yfinance price tape",
    )
    p_rf.add_argument(
        "--out-dir", default="outputs",
        help="dir where rfpm-cycle-*.json is written",
    )
    p_rf.add_argument(
        "--dry-run", action="store_true",
        help="print the cycle reading but do not write outputs/rfpm-cycle-*.json",
    )
    p_rf.set_defaults(func=_cmd_rf_cycle)

    # `sharks rf-evidence` — monthly auto-refresh of the rf-cycle proxy layer (REAL)
    p_rfe = subparsers.add_parser(
        "rf-evidence",
        help="monthly: refresh rf-cycle AUTO evidence proxies from financials (recommend-only)",
    )
    p_rfe.add_argument("--as-of", default=None, help="point-in-time date YYYY-MM-DD (default: today)")
    p_rfe.add_argument("--no-network", action="store_true", help="skip fetch (writes an empty proxy set)")
    p_rfe.add_argument("--out-dir", default="outputs", help="dir where rfpm-cycle-evidence-auto.json is written")
    p_rfe.set_defaults(func=_cmd_rf_evidence)

    # `sharks demand-val` — order/demand-anchored forward valuation (REAL)
    p_dv = subparsers.add_parser(
        "demand-val",
        help="order/demand-anchored forward fair value (B:B/backlog/contracted + quality + intangibles)",
    )
    p_dv.add_argument("--as-of", default=None, help="point-in-time date YYYY-MM-DD (default: today)")
    p_dv.add_argument("--no-network", action="store_true", help="skip yfinance; order-book + intangibles only")
    p_dv.add_argument("--out-dir", default="outputs", help="dir where demand-valuation-*.json is written")
    p_dv.add_argument("--dry-run", action="store_true", help="print but do not write outputs/")
    p_dv.set_defaults(func=_cmd_demand_val)

    # `sharks daily-brief` — 游庭澔-style 早/午/晚 brief (REAL)
    p_db = subparsers.add_parser(
        "daily-brief",
        help="游庭澔-style daily brief (早/午/晚) → MD + HTML + Discord (macro + 台股連結 + 進出場/潛力股)",
    )
    p_db.add_argument("--edition", choices=["morning", "midday", "evening"], default="morning",
                      help="morning 早報(盤前總經) / midday 午報(盤中) / evening 晚報(收盤+進出場+潛力股)")
    p_db.add_argument("--out-dir", default="outputs", help="dir where daily-brief-<date>-<edition>.{md,html,txt} is written")
    p_db.set_defaults(func=_cmd_daily_brief)

    # `sharks news-fetch` — free multi-source market-news RSS → news slot (REAL)
    p_news = subparsers.add_parser(
        "news-fetch",
        help="free multi-source market-news RSS → outputs/news-headlines-<date>.json (fills the brief news slot)",
    )
    p_news.add_argument("--out-dir", default="outputs", help="dir where news-headlines-<date>.json is written")
    p_news.set_defaults(func=_cmd_news_fetch)

    # `sharks checklist` — the standardized decision checklist (REAL, recommend-only)
    p_chk = subparsers.add_parser(
        "checklist",
        help="standardized decision checklist for one ticker (gated scorecard, recommend-only)",
    )
    p_chk.add_argument("ticker", help="ticker symbol, e.g. NVDA")
    p_chk.add_argument("--as-of", default=None,
                       help="point-in-time date YYYY-MM-DD (default: today); no lookahead")
    p_chk.add_argument("--no-network", action="store_true",
                       help="offline: FOM + valuation + cycle degrade to 'na' instead of fetching")
    p_chk.add_argument("--out-dir", default="outputs",
                       help="dir where checklist-<ticker>-<date>.json is written")
    p_chk.add_argument("--dry-run", action="store_true",
                       help="print the scorecard but do not write outputs/")
    p_chk.set_defaults(func=_cmd_checklist)

    # `sharks wiki` — wiki maintenance commands
    p_wiki = subparsers.add_parser("wiki", help="wiki maintenance commands")
    wiki_subparsers = p_wiki.add_subparsers(dest="wiki_command", required=True)

    p_wiki_lint = wiki_subparsers.add_parser(
        "lint",
        help="validate wiki frontmatter, links, and point-in-time discipline (Phase 2 stub)",
    )
    p_wiki_lint.set_defaults(func=_cmd_wiki_lint)

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
