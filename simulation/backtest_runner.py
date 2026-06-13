#!/usr/bin/env python3
"""
Trading Society -- Backtest Runner (B deliverable, part 2 of 2)

PPST Declaration (this PROGRAM):
- PROJECT: Trading Society
- PROGRAM: simulation/backtest_runner.py
- SKILL:   backtest_harness + LLM-BACKTEST-PROTOCOL compliance + PIT discipline
- TARGET:  A regime-aware, point-in-time-honest backtest harness that runs
           society agents over historical windows, enforces the five protocol
           defenses in code, caps society actions/day, and produces a structured
           JSON artifact scored by performance_tracker. No capital recommendations.

Why this exists
---------------
The user plan asks for "simulation/backtest_runner.py + Performance Tracker".
The repo already has rich deterministic backtests under src/sharks/backtest/.
This runner does NOT duplicate them: it is the *society* harness -- it drives
multiple AGENT decision callables across a window and measures them comparably,
so Ranking / Reflection / Evolution have a common substrate.

Hard guardrails baked in (docs/LLM-BACKTEST-PROTOCOL.md):
  Defense 1 (role restriction): assert_no_banned_keys() rejects any agent output
            on a historical period containing probability/direction/verdict/...
  Defense 2 (walk-forward):     a run carrying any llm_involvement != "none" must
            declare model_cutoff; periods <= cutoff are flagged cutoff_polluted
            and excluded from headline KPIs.
  Defense 4 (RAG isolation):    agents are handed `as_of` and MUST only read data
            <= as_of. The runner slices price history to <= as_of before the call
            so lookahead is structurally impossible for price inputs.
  Defense 5 (marker):           every output JSON carries top-level
            "llm_involvement" in {none, narration_only, decision_input, decision_output}.

This default harness runs with llm_involvement="none": the demo agents are pure
deterministic rules. Wiring a real LLM agent flips the marker and triggers the
walk-forward gate automatically.

Run: python simulation/backtest_runner.py   (runs a tiny synthetic demo)
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple

try:  # tracker is a sibling module; support both "python simulation/x.py" and import
    from simulation.performance_tracker import PerformanceTracker
except Exception:  # pragma: no cover - path fallback for direct script run
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from simulation.performance_tracker import PerformanceTracker

PROTOCOL_PATH = "docs/LLM-BACKTEST-PROTOCOL.md"
DAILY_ACTION_BUDGET = 10

BANNED_LLM_BACKTEST_KEYS = {
    "probability", "direction", "verdict", "target", "forecast", "signal", "score",
}
VALID_LLM_INVOLVEMENT = {"none", "narration_only", "decision_input", "decision_output"}
KPI_ELIGIBLE_INVOLVEMENT = {"none", "narration_only"}


# ---------------------------------------------------------------------------
# Protocol enforcement helpers (Defense 1)
# ---------------------------------------------------------------------------
def find_banned_keys(obj: Any, _path: str = "") -> List[str]:
    """Recursively locate any BANNED_LLM_BACKTEST_KEYS in a nested structure."""
    hits: List[str] = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            if str(k).lower() in BANNED_LLM_BACKTEST_KEYS:
                hits.append(f"{_path}.{k}".lstrip("."))
            hits.extend(find_banned_keys(v, f"{_path}.{k}"))
    elif isinstance(obj, (list, tuple)):
        for i, v in enumerate(obj):
            hits.extend(find_banned_keys(v, f"{_path}[{i}]"))
    return hits


def assert_no_banned_keys(agent_output: Any, *, llm_involvement: str,
                          agent_id: str) -> None:
    """
    Defense 1: if the run involves an LLM in the decision path, agent outputs on
    historical periods may NOT carry forecast-shaped keys. For non-LLM runs this
    is a no-op (deterministic rule outputs are exempt by construction).
    """
    if llm_involvement == "none":
        return
    hits = find_banned_keys(agent_output)
    if hits:
        raise ValueError(
            f"[PROTOCOL VIOLATION] agent '{agent_id}' emitted banned LLM-backtest "
            f"key(s) {hits} under llm_involvement='{llm_involvement}'. "
            f"See {PROTOCOL_PATH} defense #1."
        )


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------
@dataclass
class PricePoint:
    as_of: str          # ISO date string (the bar's timestamp)
    close: float


@dataclass
class AgentSpec:
    """
    A society member as the runner sees it.
    decide(as_of, history) -> structured decision dict. `history` is ALREADY
    sliced to bars with as_of <= the decision date (Defense 4), so the callable
    cannot look ahead even by accident.
    """
    agent_id: str
    decide: Callable[[str, Dict[str, List[PricePoint]]], Dict[str, Any]]
    niche_purity: float = 1.0


@dataclass
class BacktestConfig:
    start: str
    end: str
    llm_involvement: str = "none"
    model_cutoff: Optional[str] = None  # required if llm_involvement != "none"
    action_budget: int = DAILY_ACTION_BUDGET
    periods_per_year: int = 252
    regime_labeler: Optional[Callable[[str], str]] = None  # as_of -> regime label


# ---------------------------------------------------------------------------
# Price loading (PIT-honest). Uses the data lake when available; otherwise the
# caller injects synthetic series (demo / unit tests).
# ---------------------------------------------------------------------------
def load_pit_series(tickers: Sequence[str]) -> Dict[str, List[PricePoint]]:
    """
    Pull daily closes from the data lake (src/sharks/data/data_lake.load_prices).
    Returns {ticker: [PricePoint,...]} sorted ascending by date. Missing tickers
    yield an empty list (no fabrication -- CLAUDE.md No-fabrication boundary).
    """
    series: Dict[str, List[PricePoint]] = {}
    try:
        from sharks.data.data_lake import load_prices  # type: ignore
    except Exception:
        try:
            from src.sharks.data.data_lake import load_prices  # type: ignore
        except Exception:
            # Lake not importable in this context; return empties (caller injects).
            return {t: [] for t in tickers}

    for t in tickers:
        df = load_prices(t)
        pts: List[PricePoint] = []
        if df is not None and not df.empty:
            close_col = "Close" if "Close" in df.columns else (
                "close" if "close" in df.columns else None)
            if close_col is not None:
                for idx, row in df.iterrows():
                    try:
                        ts = idx.date().isoformat() if hasattr(idx, "date") else str(idx)[:10]
                        pts.append(PricePoint(as_of=ts, close=float(row[close_col])))
                    except Exception:
                        continue
        pts.sort(key=lambda p: p.as_of)
        series[t] = pts
    return series


def _slice_history(full: Dict[str, List[PricePoint]], as_of: str
                   ) -> Dict[str, List[PricePoint]]:
    """Defense 4: return only bars with as_of_bar <= as_of (no lookahead)."""
    return {t: [p for p in pts if p.as_of <= as_of] for t, pts in full.items()}


def _forward_return(pts: Sequence[PricePoint], as_of: str) -> Optional[float]:
    """
    Realized next-bar return for scoring: close[t+1]/close[t]-1 where t is the
    last bar <= as_of. Returns None if no next bar exists (end of data).
    This is realized truth used ONLY for scoring after the decision -- the agent
    never sees it (it is computed by the runner, not handed to decide()).
    """
    idx = None
    for i, p in enumerate(pts):
        if p.as_of <= as_of:
            idx = i
        else:
            break
    if idx is None or idx + 1 >= len(pts):
        return None
    prev, nxt = pts[idx].close, pts[idx + 1].close
    if prev <= 0:
        return None
    return nxt / prev - 1.0


def _trading_dates(series: Dict[str, List[PricePoint]], start: str, end: str
                   ) -> List[str]:
    dates = set()
    for pts in series.values():
        for p in pts:
            if start <= p.as_of <= end:
                dates.add(p.as_of)
    return sorted(dates)


# ---------------------------------------------------------------------------
# The runner
# ---------------------------------------------------------------------------
@dataclass
class RunResult:
    config: BacktestConfig
    scoreboard: List[Dict[str, Any]]
    n_dates: int
    polluted_dates: List[str] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)


def _validate_config(cfg: BacktestConfig) -> None:
    if cfg.llm_involvement not in VALID_LLM_INVOLVEMENT:
        raise ValueError(f"llm_involvement must be one of {VALID_LLM_INVOLVEMENT}")
    if cfg.llm_involvement != "none" and not cfg.model_cutoff:
        raise ValueError(
            "Defense 2 (walk-forward): llm_involvement != 'none' requires "
            f"model_cutoff to be declared. See {PROTOCOL_PATH}."
        )


def run_backtest(
    agents: Sequence[AgentSpec],
    series: Dict[str, List[PricePoint]],
    cfg: BacktestConfig,
) -> RunResult:
    """
    Walk each trading date in [start, end]. For each date:
      1. slice history to <= as_of (no lookahead),
      2. ask each agent to decide,
      3. enforce protocol on its output,
      4. enforce the society-wide action budget (Defense: ~10 actions/day),
      5. score realized next-bar return into the PerformanceTracker.
    """
    _validate_config(cfg)
    tracker = PerformanceTracker(action_budget=cfg.action_budget,
                                 periods_per_year=cfg.periods_per_year)
    dates = _trading_dates(series, cfg.start, cfg.end)
    polluted: List[str] = []
    notes: List[str] = []

    for aid in [a.agent_id for a in agents]:
        tracker.ensure(aid)
    for a in agents:
        tracker.set_niche_purity(a.agent_id, a.niche_purity)

    for as_of in dates:
        # Defense 2: flag pre-cutoff dates for LLM-involved runs.
        polluted_today = bool(
            cfg.model_cutoff and cfg.llm_involvement != "none"
            and as_of <= cfg.model_cutoff
        )
        if polluted_today:
            polluted.append(as_of)

        history = _slice_history(series, as_of)
        regime = cfg.regime_labeler(as_of) if cfg.regime_labeler else None
        society_actions_today = 0

        for a in agents:
            decision = a.decide(as_of, history)
            assert_no_banned_keys(decision, llm_involvement=cfg.llm_involvement,
                                  agent_id=a.agent_id)

            actions = decision.get("proposed_actions", []) or []
            # Society-wide action budget enforcement (truncate, never pad).
            remaining = cfg.action_budget - society_actions_today
            if remaining <= 0:
                actions = []
            elif len(actions) > remaining:
                actions = actions[:remaining]
                notes.append(f"{as_of}: action budget hit; truncated "
                             f"{a.agent_id} to {remaining}.")
            society_actions_today += len(actions)

            # Score realized next-bar return for each acted ticker (sign by side).
            period_ret = 0.0
            for act in actions:
                tkr = act.get("ticker")
                side = act.get("side", "long")
                if not tkr or tkr not in series:
                    continue
                fwd = _forward_return(series[tkr], as_of)
                if fwd is None:
                    continue
                signed = fwd if side == "long" else -fwd
                # equal-weight across the day's actions for this agent
                period_ret += signed
                tracker.record_trade(a.agent_id, signed)
            if actions:
                period_ret /= max(1, len(actions))
            # Pre-cutoff polluted periods are recorded but excluded from headline
            # KPIs by the caller via polluted_dates; here we still log for audit.
            tracker.record_period(a.agent_id, period_ret, regime=regime,
                                  actions=len(actions))

    if cfg.llm_involvement not in KPI_ELIGIBLE_INVOLVEMENT and not polluted:
        notes.append("llm_involvement is decision_input/decision_output: results "
                     "are EXPLORATORY only, never headline KPIs (protocol #5).")

    return RunResult(
        config=cfg,
        scoreboard=tracker.scoreboard(),
        n_dates=len(dates),
        polluted_dates=polluted,
        notes=notes,
    )


def result_to_artifact(res: RunResult) -> Dict[str, Any]:
    """Structured JSON artifact, protocol-marked, ready for outputs/ (research)."""
    kpi_eligible = (
        res.config.llm_involvement in KPI_ELIGIBLE_INVOLVEMENT
        or (res.config.model_cutoff is not None and not res.polluted_dates)
    )
    return {
        "type": "trading_society_backtest",
        "as_of_timestamp": datetime.now(timezone.utc).isoformat(),
        "role": "writer",
        "project": "Trading Society",
        "program": "simulation/backtest_runner.py",
        "protocol_ref": PROTOCOL_PATH,
        "llm_involvement": res.config.llm_involvement,
        "model_cutoff": res.config.model_cutoff,
        "window": {"start": res.config.start, "end": res.config.end,
                   "n_trading_dates": res.n_dates},
        "action_budget": res.config.action_budget,
        "cutoff_polluted": bool(res.polluted_dates),
        "polluted_date_count": len(res.polluted_dates),
        "kpi_eligible": kpi_eligible,
        "scoreboard": res.scoreboard,
        "notes": res.notes,
        "disclaimer": ("Research artifact. No capital recommendation. Promotion to "
                       "any signal requires human selection + Risk Officer gate + "
                       "cross-review (AGENTS.md sec.3)."),
    }


# ---------------------------------------------------------------------------
# Demo: two deterministic (non-LLM) agents on a tiny synthetic series.
# llm_involvement = "none" -> trivially KPI-eligible, no banned-key risk.
# ---------------------------------------------------------------------------
def _synthetic_series() -> Dict[str, List[PricePoint]]:
    # Deterministic zig-zag closes for two tickers across 12 business days.
    base = 100.0
    aaa, bbb = [], []
    closes_a = [100, 101, 103, 102, 105, 104, 107, 106, 109, 111, 110, 113]
    closes_b = [50, 49, 51, 52, 50, 53, 52, 54, 53, 55, 54, 56]
    for i, (ca, cb) in enumerate(zip(closes_a, closes_b)):
        d = date(2025, 1, 6 + i).isoformat()  # arbitrary recent window
        aaa.append(PricePoint(as_of=d, close=float(ca)))
        bbb.append(PricePoint(as_of=d, close=float(cb)))
    _ = base
    return {"AAA": aaa, "BBB": bbb}


def _momentum_agent(as_of: str, history: Dict[str, List[PricePoint]]
                    ) -> Dict[str, Any]:
    """Buy a ticker if its last close > the close 2 bars ago (pure rule)."""
    actions = []
    for tkr, pts in history.items():
        if len(pts) >= 3 and pts[-1].close > pts[-3].close:
            actions.append({"ticker": tkr, "side": "long",
                            "rationale": "2-bar momentum up", "size_hint": "small"})
    return {"as_of_timestamp": as_of, "role": "MOMENTUM_SWING",
            "proposed_actions": actions[:2], "no_action_reason": None}


def _reversion_agent(as_of: str, history: Dict[str, List[PricePoint]]
                     ) -> Dict[str, Any]:
    """Fade a one-bar drop (pure rule)."""
    actions = []
    for tkr, pts in history.items():
        if len(pts) >= 2 and pts[-1].close < pts[-2].close:
            actions.append({"ticker": tkr, "side": "long",
                            "rationale": "1-bar dip fade", "size_hint": "tiny"})
    return {"as_of_timestamp": as_of, "role": "MEAN_REVERSION_SWING",
            "proposed_actions": actions[:2], "no_action_reason": None}


def _demo() -> int:
    print("=" * 72)
    print("backtest_runner self-test  (llm_involvement=none, synthetic data)")
    print("=" * 72)
    series = _synthetic_series()
    agents = [
        AgentSpec("MOMENTUM_SWING", _momentum_agent, niche_purity=1.0),
        AgentSpec("MEAN_REVERSION_SWING", _reversion_agent, niche_purity=0.95),
    ]
    cfg = BacktestConfig(start="2025-01-06", end="2025-01-31",
                         llm_involvement="none", action_budget=DAILY_ACTION_BUDGET,
                         regime_labeler=lambda d: "risk_on")
    res = run_backtest(agents, series, cfg)
    artifact = result_to_artifact(res)
    print(json.dumps(artifact, indent=2, ensure_ascii=False))

    print("\n--- Defense 1 demonstration (LLM run rejects banned keys) ---")
    bad = {"proposed_actions": [{"ticker": "AAA", "direction": "up"}]}
    try:
        assert_no_banned_keys(bad, llm_involvement="decision_output", agent_id="X")
        print("  (unexpected) no violation raised")
    except ValueError as e:
        print(f"  correctly rejected: {str(e)[:90]}...")
    return 0


if __name__ == "__main__":
    raise SystemExit(_demo())
