#!/usr/bin/env python3
"""
Trading Society -- Real-universe competition over the FOM stock universe (+ SpaceX)

PPST Declaration (this PROGRAM):
- PROJECT: Trading Society
- PROGRAM: simulation/universe_competition.py
- SKILL:   society traders pick from the FOM universe on REAL lake prices ->
           ranked by REAL backtested performance (competition / leaderboard)
- TARGET:  Run the society's deterministic trader genomes over the real FOM
           universe (finviz-screened + FOM universe-of-record) using point-in-time
           lake prices, rank them by realized performance, surface each trader's
           "today" signals, and include a SpaceX sleeve. llm_involvement="none"
           (rule strategies over historical prices) => protocol KPI-eligible.

Governance:
- SpaceX is PRIVATE: no ticker, no price. It is MONITOR-ONLY here (honoring
  watchlist/spacex_ipo_2026_event.md). The society "trades the SpaceX theme" via
  PUBLIC proxies that exist in the lake: DXYZ (Destiny Tech100 NAV proxy), RKLB,
  ASTS, PL, LUNR, STRL, IRDM, GSAT, LMT, NOC, BA. No SpaceX price is fabricated.
- This ranks TRADERS on history. It is research / recommend-only. It does NOT
  emit a capital order and does NOT replace the canonical 10-signal pipeline
  (src/sharks/daily_picks.py) or the Risk-Officer gate (CLAUDE.md sec.5, sec.10).
- PIT: the backtest_runner slices price history to <= as_of before every decision,
  so lookahead is structurally impossible.

Run: python simulation/universe_competition.py
"""

from __future__ import annotations

import glob
import json
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

try:
    from simulation.backtest_runner import (
        BacktestConfig, run_backtest, load_pit_series, PricePoint, AgentSpec)
    from simulation.strategy_agent import make_agent_spec, make_decider
    from simulation.evolution.mutator import AgentConfig
except Exception:  # pragma: no cover
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from simulation.backtest_runner import (
        BacktestConfig, run_backtest, load_pit_series, PricePoint, AgentSpec)
    from simulation.strategy_agent import make_agent_spec, make_decider
    from simulation.evolution.mutator import AgentConfig

REPO = Path(__file__).resolve().parents[1]
LAKE_PRICES = REPO / "data" / "lake" / "prices"
PROTOCOL_PATH = "docs/LLM-BACKTEST-PROTOCOL.md"

# SpaceX is private; these PUBLIC names are its tradeable proxies / value chain.
SPACE_SLEEVE = ["DXYZ", "RKLB", "ASTS", "PL", "LUNR", "STRL", "IRDM", "GSAT",
                "LMT", "NOC", "BA"]
SPACEX_MONITOR_ONLY = {
    "name": "SpaceX (private)",
    "status": "monitor_only",
    "reason": "Private company -- no public ticker / price. Not tradeable; "
              "tracked as an IPO event (watchlist/spacex_ipo_2026_event.md).",
    "tradeable_proxies": {
        "DXYZ": "Destiny Tech100 -- direct SpaceX NAV exposure (closest proxy)",
        "RKLB": "Rocket Lab -- purest public launch comparable",
        "ASTS/PL/LUNR/IRDM/GSAT": "satcom / earth-obs / launch value chain",
        "LMT/NOC/BA": "aerospace & defense primes",
    },
}

# The society's trader genomes (the core tactical roles, parameterized).
def society_traders() -> List[AgentConfig]:
    return [
        AgentConfig("MOMENTUM_SWING", "daily_momentum",
                    params={"momentum_tilt": 1.0, "lookback": 5, "entry_threshold": 0.02, "max_actions": 3}),
        AgentConfig("MOMENTUM_FAST", "intraday_momentum",
                    params={"momentum_tilt": 1.0, "lookback": 2, "entry_threshold": 0.015, "max_actions": 3}),
        AgentConfig("TREND_RIDER", "strategic_trend",
                    params={"momentum_tilt": 1.0, "lookback": 10, "entry_threshold": 0.04, "max_actions": 3}),
        AgentConfig("MEAN_REVERSION", "counter_trend",
                    params={"momentum_tilt": -1.0, "lookback": 3, "entry_threshold": 0.03, "max_actions": 3}),
        AgentConfig("REVERSION_FAST", "fast_fade",
                    params={"momentum_tilt": -1.0, "lookback": 1, "entry_threshold": 0.02, "max_actions": 3}),
        AgentConfig("BREAKOUT_HUNTER", "breakout",
                    params={"momentum_tilt": 1.0, "lookback": 3, "entry_threshold": 0.03, "max_actions": 3}),
    ]


def lake_has(ticker: str) -> bool:
    return (LAKE_PRICES / f"{ticker}_1d.parquet").exists()


def _latest_finviz_scan() -> Tuple[Optional[str], List[str]]:
    files = sorted(glob.glob(str(REPO / "outputs" / "finviz-scan-*.json")))
    if not files:
        return None, []
    path = files[-1]
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except Exception:
        return path, []
    names: List[str] = []
    for key in ("buy_consider", "overshoot_200d", "squeeze_watch"):
        v = data.get(key) or []
        names.extend([t for t in v if isinstance(t, str)])
    return path, names


def _fom_universe() -> List[str]:
    try:
        import sys
        if str(REPO / "src") not in sys.path:
            sys.path.insert(0, str(REPO / "src"))
        from sharks.scoring.fom import DEFAULT_UNIVERSE  # type: ignore
        return list(DEFAULT_UNIVERSE)
    except Exception:
        return []


def build_universe(max_names: int = 130) -> Dict[str, Any]:
    """
    FOM-screened universe = latest finviz scan candidates UNION the SpaceX sleeve
    UNION a slice of the FOM universe-of-record, intersected with lake availability.
    Capped at max_names (the drop is reported, never silent).
    """
    scan_path, scan_names = _latest_finviz_scan()
    fom = _fom_universe()

    ordered: List[str] = []
    seen = set()
    # Priority: SpaceX sleeve first (user directive), then finviz screen, then FOM.
    for group in (SPACE_SLEEVE, scan_names, fom):
        for t in group:
            if t not in seen and lake_has(t):
                ordered.append(t)
                seen.add(t)

    dropped = max(0, len(ordered) - max_names)
    universe = ordered[:max_names]
    return {
        "tickers": universe,
        "n": len(universe),
        "dropped_for_cap": dropped,
        "sources": {
            "finviz_scan": os.path.basename(scan_path) if scan_path else None,
            "finviz_candidates_in_lake": len([t for t in scan_names if lake_has(t)]),
            "fom_universe_in_lake": len([t for t in fom if lake_has(t)]),
            "space_sleeve_in_lake": [t for t in SPACE_SLEEVE if lake_has(t)],
        },
    }


def _recent_window(series: Dict[str, List[PricePoint]], n_days: int = 90
                   ) -> Tuple[str, str, int]:
    """Pick the last n_days of common trading dates from the loaded series."""
    all_dates = set()
    for pts in series.values():
        for p in pts:
            all_dates.add(p.as_of)
    dates = sorted(all_dates)
    if not dates:
        return "", "", 0
    window = dates[-n_days:]
    return window[0], window[-1], len(window)


def run_competition(max_names: int = 130, window_days: int = 90,
                    action_budget: int = 10) -> Dict[str, Any]:
    uni = build_universe(max_names)
    tickers = uni["tickers"]
    series = load_pit_series(tickers)
    series = {t: pts for t, pts in series.items() if pts}  # drop empties
    start, end, n_dates = _recent_window(series, window_days)

    traders = society_traders()
    leaderboard: List[Dict[str, Any]] = []
    for cfg in traders:
        spec = make_agent_spec(cfg)
        bcfg = BacktestConfig(start=start, end=end, llm_involvement="none",
                              action_budget=action_budget,
                              regime_labeler=lambda d: "live")
        res = run_backtest([spec], series, bcfg)
        if not res.scoreboard:
            continue
        row = res.scoreboard[0]
        m = row["metrics"]
        leaderboard.append({
            "trader": cfg.agent_id, "niche": cfg.niche,
            "fitness": row["fitness"],
            "total_return": round(m["total_return"], 4),
            "sharpe": round(m["sharpe"], 3),
            "sortino": round(m["sortino"], 3),
            "max_drawdown": round(m["max_drawdown"], 4),
            "win_rate": round(m["win_rate"], 3),
            "n_trades": m["n_trades"],
        })
    leaderboard.sort(key=lambda r: (r["fitness"], r["total_return"]), reverse=True)

    champion = leaderboard[0]["trader"] if leaderboard else None

    # Today's signals from each trader (recommend-only), and SpaceX-sleeve signals.
    latest_as_of = end
    full_hist = {t: [p for p in pts if p.as_of <= latest_as_of]
                 for t, pts in series.items()}
    signals_today: Dict[str, List[Dict[str, Any]]] = {}
    for cfg in traders:
        decide = make_decider(cfg)
        out = decide(latest_as_of, full_hist)
        signals_today[cfg.agent_id] = out.get("proposed_actions", [])

    space_present = [t for t in SPACE_SLEEVE if t in series]
    space_hist = {t: full_hist[t] for t in space_present if t in full_hist}
    space_signals: Dict[str, List[Dict[str, Any]]] = {}
    if champion:
        champ_cfg = next(c for c in traders if c.agent_id == champion)
        champ_decide = make_decider(champ_cfg)
        space_signals[champion] = champ_decide(latest_as_of, space_hist).get(
            "proposed_actions", [])

    return {
        "type": "trading_society_universe_competition",
        "as_of_timestamp": datetime.now(timezone.utc).isoformat(),
        "role": "writer",
        "project": "Trading Society",
        "program": "simulation/universe_competition.py",
        "protocol_ref": PROTOCOL_PATH,
        "llm_involvement": "none",
        "kpi_eligible": True,
        "universe": {**uni, "window": {"start": start, "end": end,
                                       "n_trading_dates": n_dates,
                                       "n_priced": len(series)}},
        "spacex": SPACEX_MONITOR_ONLY,
        "spacex_sleeve_priced": space_present,
        "leaderboard": leaderboard,
        "champion": champion,
        "champion_signals_today": signals_today.get(champion, []) if champion else [],
        "all_traders_signals_today": signals_today,
        "spacex_sleeve_champion_signals_today": space_signals.get(champion, []),
        "disclaimer": (
            "Research / recommend-only. Trader ranking on historical lake prices "
            "(llm_involvement=none, PIT). NOT a capital order; does not replace "
            "the canonical 10-signal pipeline or the Risk-Officer gate. SpaceX is "
            "private and monitor-only; only public proxies are traded."),
    }


def _print_summary(result: Dict[str, Any]) -> None:
    u = result["universe"]
    print("=" * 72)
    print("TRADING SOCIETY -- real-universe competition (FOM + SpaceX sleeve)")
    print("=" * 72)
    print(f"Universe: {u['n']} names ({u['window']['n_priced']} priced), "
          f"window {u['window']['start']}..{u['window']['end']} "
          f"({u['window']['n_trading_dates']} dates)")
    print(f"SpaceX sleeve priced: {', '.join(result['spacex_sleeve_priced'])}")
    print(f"SpaceX itself: {result['spacex']['status']} "
          f"({result['spacex']['reason'][:60]}...)")
    print("\nLEADERBOARD (ranked by realized fitness, then return):")
    print(f"  {'#':<2} {'trader':<16} {'fit':>6} {'return':>8} {'sharpe':>7} "
          f"{'maxDD':>7} {'win':>5} {'trades':>6}")
    for i, r in enumerate(result["leaderboard"], 1):
        print(f"  {i:<2} {r['trader']:<16} {r['fitness']:>6.3f} "
              f"{r['total_return']:>+8.3f} {r['sharpe']:>7.2f} "
              f"{r['max_drawdown']:>7.3f} {r['win_rate']:>5.2f} {r['n_trades']:>6}")
    print(f"\nChampion: {result['champion']}")
    sig = result["champion_signals_today"]
    print(f"Champion signals today (recommend-only, {len(sig)}): "
          f"{[(a['ticker'], a['side']) for a in sig]}")
    ss = result["spacex_sleeve_champion_signals_today"]
    print(f"SpaceX-sleeve signals from champion: "
          f"{[(a['ticker'], a['side']) for a in ss]}")
    print("\n" + result["disclaimer"])


def main() -> int:
    result = run_competition()
    out_dir = REPO / "outputs"
    out_dir.mkdir(exist_ok=True)
    stamp = result["as_of_timestamp"][:10]
    out_path = out_dir / f"trading-society-competition-{stamp}.json"
    out_path.write_text(json.dumps(result, indent=2, ensure_ascii=False),
                        encoding="utf-8")
    _print_summary(result)
    print(f"\nArtifact: {out_path.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
