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
