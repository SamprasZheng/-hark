"""Attribution telemetry — closed-loop post-mortem for a failed/closed pick.

When a swing pick hits its stop / time-stop / underperforms, classify *why* by
diffing the realized outcome against the entry thesis, into one of:

  * ``regime_flip``          — the market regime turned (systemic, not stock-specific)
  * ``quant_signal_failure`` — price fell while the FOM signal stayed high, OR the
                               entry signal decayed with the regime intact
  * ``narrative_shift``      — the supply-chain / macro thesis behind the pick moved
  * ``execution_timing``     — regime + signal + narrative intact → entered / exited
                               at the wrong point (residual catch-all)

RECOMMEND-ONLY: this reads outcomes and emits an attribution; it never trades and
never asserts a position. It composes with — does NOT extend — ``discord/feedback.py``
(that is a *today* rotation throttle; this is a retrospective two-timestamp diff).
It fills the empty §G "mistake library" of ``wiki/03_alpha_library.md`` and realizes
the OPERATING_MANUAL 關7 反饋維護 closed loop.

Structure clones ``decision/checklist.py``: pure helpers + a dataclass result + a
recommend-only orchestrator, every external input injectable so the classifier is
unit-tested offline. Network (FOM re-score, price outcome) is lazy + best-effort:
when a baseline is unavailable the corresponding cause rule simply does not fire,
never fabricates. Zero new dependencies.

Narrative-delta dependency: the interim heuristic is page-level (did wiki/02 & 03
get re-ingested after entry?). ``run_postmortem`` accepts an injectable
``narrative_snapshot`` so the parallel PIT-snapshot feature
(:mod:`sharks.state`) slots in as ``method="pit_snapshot"`` with no rewrite.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Optional

from sharks.state._frontmatter import parse_frontmatter

# Regime ordering (best → worst) for "downgrade" detection.
_REGIME_RANK = {"bull_trend": 4, "late_bull": 3, "neutral": 2, "risk_off": 1, "capitulation": 0}
_REVERSAL_REGIMES = {"risk_off", "capitulation"}

FOM_HIGH = 45.0          # mirrors portfolio_audit.fom_verdict "healthy" floor
UNDERPERF_FLOOR = -0.10  # forward return at/under this counts as a failed pick
NARRATIVE_PAGES = ("02_mag7_bottleneck", "03_alpha_library")

CAUSES = ("regime_flip", "quant_signal_failure", "narrative_shift", "execution_timing", "none")


# ─── data model ──────────────────────────────────────────────────────────────────
@dataclass
class PostmortemResult:
    ticker: str
    entry_date: str
    exit_date: str
    exited_reason: str       # stop | time_stop | underperform | exit_flag | open
    cause: str               # one of CAUSES
    cause_confidence: float
    entry_thesis: str
    outcome: dict
    deltas: dict
    why: str
    evidence_paths: list = field(default_factory=list)

    def to_dict(self) -> dict:
        d = asdict(self)
        d["schema_version"] = 1
        d["recommend_only"] = True
        d["report_type"] = "attribution_postmortem"
        return d


# ─── entry extraction ────────────────────────────────────────────────────────────
def _entry_from_signal(sig: dict, entry_date: str) -> dict:
    """Project a picks-*.json ``long_new`` signal into a post-mortem entry record."""
    ez = sig.get("entry_zone") or {}
    inv = sig.get("invalidation") or {}
    mid = None
    if ez.get("low") is not None and ez.get("high") is not None:
        mid = (ez["low"] + ez["high"]) / 2.0
    return {
        "ticker": (sig.get("ticker") or "").upper() or None,
        "entry_date": str(entry_date)[:10],
        "thesis": sig.get("thesis", ""),
        "confidence": sig.get("confidence"),
        "entry_zone": ez,
        "entry_mid": mid,
        "stop_loss": sig.get("stop_loss"),
        "invalidation": inv,
        "time_stop_days": inv.get("time_stop_days"),
        "quadrant": sig.get("quadrant"),
        "evidence_paths": sig.get("evidence_paths", []),
        # Optional baselines (present only if a future picks build records them):
        "final_fom_entry": sig.get("final_fom_entry"),
        "momentum_entry": sig.get("momentum_entry"),
        "regime_label_entry": sig.get("regime_label_entry"),
    }


def scan_closed_positions(out_dir=Path("outputs")) -> list[dict]:
    """All ``long_new`` entries across ``outputs/picks-*.json`` (oldest first).

    The trigger feed: the caller runs :func:`run_postmortem` on each and keeps the
    ones whose ``exited_reason != "open"``. Pure file read; never raises.
    """
    out = Path(out_dir)
    entries: list[dict] = []
    if not out.exists():
        return entries
    for f in sorted(out.glob("picks-*.json")):
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
        except Exception:
            continue
        entry_date = str(data.get("as_of") or "")
        for sig in data.get("signals", []) or []:
            if isinstance(sig, dict) and str(sig.get("slot", "")).startswith("long_new") and sig.get("ticker"):
                entries.append(_entry_from_signal(sig, entry_date))
    return entries


# ─── detection ───────────────────────────────────────────────────────────────────
def detect_exit(entry: dict, outcome: dict, as_of_exit: str) -> str:
    """Classify how the pick closed (recommend-only — never asserts a trade)."""
    stop = entry.get("stop_loss")
    exit_close = outcome.get("exit_close")
    exit_low = outcome.get("exit_low", exit_close)
    if stop is not None and exit_low is not None and exit_low <= stop:
        return "stop"
    tsd, ed = entry.get("time_stop_days"), entry.get("entry_date")
    if tsd and ed and as_of_exit:
        try:
            days = (date.fromisoformat(as_of_exit[:10]) - date.fromisoformat(ed[:10])).days
            if days >= tsd:
                return "time_stop"
        except ValueError:
            pass
    if outcome.get("exit_flag"):
        return "exit_flag"
    fr = outcome.get("forward_return")
    if fr is not None and fr <= UNDERPERF_FLOOR:
        return "underperform"
    return "open"


# ─── the cause classifier (pure, first-match, degrades on missing dims) ───────────
def classify_cause(
    entry: dict,
    outcome: dict,
    *,
    fom_delta: Optional[dict] = None,
    regime_delta: Optional[dict] = None,
    narrative_delta: Optional[dict] = None,
) -> dict:
    """Map (entry thesis, outcome, FOM/regime/narrative deltas) → one cause tag.

    Deterministic and order-sensitive: regime_flip > quant_signal_failure >
    narrative_shift > execution_timing. Each branch is guarded by the presence of
    its inputs, so a missing dimension is skipped rather than guessed.
    """
    fr = outcome.get("forward_return")
    reason = outcome.get("exited_reason", "open")
    adverse = reason in ("stop", "time_stop", "underperform", "exit_flag") or (fr is not None and fr <= 0)
    if not adverse:
        return {"cause": "none", "confidence": 0.0,
                "why": "pick did not stop out or underperform", "evidence": {}}

    # 1. regime flip — systemic, not stock-specific
    if regime_delta:
        e, n = regime_delta.get("entry"), regime_delta.get("now")
        if e and n and e != n:
            if n in _REVERSAL_REGIMES and e not in _REVERSAL_REGIMES:
                return {"cause": "regime_flip", "confidence": 0.9,
                        "why": f"market regime flipped {e}->{n} — systemic, not the stock",
                        "evidence": {"regime": regime_delta}}
            re_, rn_ = _REGIME_RANK.get(e), _REGIME_RANK.get(n)
            if re_ is not None and rn_ is not None and rn_ < re_:
                return {"cause": "regime_flip", "confidence": 0.7,
                        "why": f"regime downgraded {e}->{n}",
                        "evidence": {"regime": regime_delta}}

    # 2/3. quant signal failure
    if fom_delta:
        fnow, fd, md = (
            fom_delta.get("final_fom_now"),
            fom_delta.get("fom_delta"),
            fom_delta.get("momentum_delta"),
        )
        if fnow is not None and fd is not None and fnow >= FOM_HIGH and fd >= -10:
            return {"cause": "quant_signal_failure", "confidence": 0.75,
                    "why": f"FOM stayed high ({fnow}) while price fell — the signal was wrong, not the regime",
                    "evidence": {"fom": fom_delta}}
        if (md is not None and md <= -25) or (fd is not None and fd <= -15):
            return {"cause": "quant_signal_failure", "confidence": 0.7,
                    "why": "the entry signal decayed (FOM/momentum rolled over) with regime intact",
                    "evidence": {"fom": fom_delta}}

    # 4. narrative shift
    if narrative_delta and narrative_delta.get("changed"):
        conf = 0.5 if narrative_delta.get("method") == "wiki_mtime_heuristic" else 0.7
        return {"cause": "narrative_shift", "confidence": conf,
                "why": "the supply-chain / macro thesis behind the pick moved after entry",
                "evidence": {"narrative": narrative_delta}}

    # 5. execution timing (residual)
    return {"cause": "execution_timing", "confidence": 0.4,
            "why": ("regime + signal + narrative intact — likely entered/exited at the "
                    "wrong point (stop too tight, or chased the breakout bar)"),
            "evidence": {}}


# ─── best-effort delta computation (lazy / wrapped; tests inject instead) ──────────
def compute_outcome(entry: dict, *, as_of_exit: str, closes=None, network: bool = True) -> dict:
    """Realized outcome for ``entry`` by ``as_of_exit``. Reuses fom.fetch_monthly for
    the close series when ``network``; best-effort (degrades to no return)."""
    out = {"entry_mid": entry.get("entry_mid"), "exit_close": None,
           "exit_low": None, "forward_return": None}
    ticker = entry.get("ticker")
    if closes is None and network and ticker:
        try:
            from sharks.scoring.fom import fetch_monthly
            start = entry.get("entry_date") or "2020-01-01"
            closes = fetch_monthly([ticker], start=start, end=as_of_exit)
        except Exception:
            closes = None
    if closes is not None and ticker:
        try:
            s = closes[ticker].dropna()
            exit_close = float(s.iloc[-1])
            out["exit_close"] = out["exit_low"] = exit_close
            mid = entry.get("entry_mid")
            if mid:
                out["forward_return"] = round(exit_close / mid - 1.0, 4)
        except Exception:
            pass
    return out


def compute_fom_delta(entry: dict, *, fom_now: Optional[dict] = None) -> Optional[dict]:
    """FOM delta vs the entry baseline. Returns None when the entry FOM baseline is
    absent (today's picks don't record it) — so the quant rule simply won't fire
    rather than fabricate a delta."""
    fom_entry = entry.get("final_fom_entry")
    if fom_entry is None or fom_now is None:
        return None
    fnow = fom_now.get("final_fom")
    mnow = fom_now.get("momentum")
    return {
        "final_fom_now": fnow,
        "fom_delta": round(fnow - fom_entry, 2) if fnow is not None else None,
        "momentum_delta": (round(mnow - entry["momentum_entry"], 2)
                           if mnow is not None and entry.get("momentum_entry") is not None else None),
    }


def compute_regime_delta(
    entry: dict,
    *,
    regime_now: Optional[str] = None,
    regime_label_entry: Optional[str] = None,
    out_dir=Path("outputs"),
    network: bool = True,
) -> dict:
    """Entry vs exit regime labels. Entry label comes from the injected value, the
    entry record, or a same-dated ``regime-classification-*.json`` artifact; exit
    label from the injected value or a live classify_regime() (best-effort)."""
    e = regime_label_entry or entry.get("regime_label_entry")
    if e is None:
        ed = (entry.get("entry_date") or "")[:10]
        p = Path(out_dir) / f"regime-classification-{ed}.json"
        if p.exists():
            try:
                e = json.loads(p.read_text(encoding="utf-8")).get("label")
            except Exception:
                e = None
    n = regime_now
    if n is None and network:
        try:
            from sharks.regime.classifier import classify_regime
            n = classify_regime().get("label")
        except Exception:
            n = None
    return {"entry": e, "now": n, "flipped": bool(e and n and e != n)}


def compute_narrative_delta(
    entry_date: str,
    *,
    narrative_snapshot: Optional[dict] = None,
    wiki_root=Path("wiki"),
    pages: tuple[str, ...] = NARRATIVE_PAGES,
) -> dict:
    """Did the thesis pages move after entry?

    Injected ``narrative_snapshot`` (a PIT snapshot, ``{"changed": bool, "pages":
    [...]}``) upgrades the method to ``pit_snapshot``. Otherwise the interim
    heuristic compares the live ``as_of_timestamp`` of wiki/02 & wiki/03 to the
    entry date — page-level only (it cannot tell *which* claim changed).
    """
    if narrative_snapshot is not None:
        return {
            "changed": bool(narrative_snapshot.get("changed")),
            "pages": narrative_snapshot.get("pages", []),
            "method": "pit_snapshot",
        }
    ed = str(entry_date)[:10]
    changed_pages: list[dict] = []
    for stem in pages:
        p = Path(wiki_root) / f"{stem}.md"
        if not p.exists():
            continue
        try:
            fm, _ = parse_frontmatter(p.read_text(encoding="utf-8"))
        except Exception:
            continue
        ts = str(fm.get("as_of_timestamp") or "")[:10]
        if ts and ed and ts > ed:
            changed_pages.append({"page": stem, "as_of": ts})
    return {"changed": bool(changed_pages), "pages": changed_pages, "method": "wiki_mtime_heuristic"}


# ─── orchestration ─────────────────────────────────────────────────────────────
def run_postmortem(
    entry: dict,
    *,
    as_of_exit: Optional[str] = None,
    outcome: Optional[dict] = None,
    fom_delta: Optional[dict] = None,
    fom_now: Optional[dict] = None,
    regime_now: Optional[str] = None,
    regime_label_entry: Optional[str] = None,
    narrative_snapshot: Optional[dict] = None,
    closes=None,
    network: bool = True,
    wiki_root=Path("wiki"),
    out_dir=Path("outputs"),
) -> PostmortemResult:
    """Attribute one closed/failed pick. Every external input is injectable; with
    ``network=False`` and injected ``outcome``/deltas it is fully offline. Never
    raises on missing data (the corresponding cause rule just doesn't fire)."""
    as_of_exit = (as_of_exit or datetime.now().strftime("%Y-%m-%d"))[:10]

    if outcome is None:
        outcome = compute_outcome(entry, as_of_exit=as_of_exit, closes=closes, network=network)
    if "exited_reason" not in outcome:
        outcome["exited_reason"] = detect_exit(entry, outcome, as_of_exit)

    if fom_delta is None:
        fom_delta = compute_fom_delta(entry, fom_now=fom_now)
    regime_delta = compute_regime_delta(
        entry, regime_now=regime_now, regime_label_entry=regime_label_entry,
        out_dir=out_dir, network=network,
    )
    narrative_delta = compute_narrative_delta(
        entry.get("entry_date", ""), narrative_snapshot=narrative_snapshot, wiki_root=wiki_root,
    )

    cause = classify_cause(
        entry, outcome, fom_delta=fom_delta, regime_delta=regime_delta, narrative_delta=narrative_delta,
    )
    return PostmortemResult(
        ticker=entry.get("ticker"),
        entry_date=entry.get("entry_date", ""),
        exit_date=as_of_exit,
        exited_reason=outcome["exited_reason"],
        cause=cause["cause"],
        cause_confidence=cause["confidence"],
        entry_thesis=entry.get("thesis", ""),
        outcome=outcome,
        deltas={"fom": fom_delta or {}, "regime": regime_delta or {}, "narrative": narrative_delta or {}},
        why=cause["why"],
        evidence_paths=list(entry.get("evidence_paths", []))
        + ["wiki/02_mag7_bottleneck.md", "wiki/03_alpha_library.md"],
    )


# ─── output ──────────────────────────────────────────────────────────────────────
def write_output(out_dir, result: PostmortemResult) -> Path:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    payload = {"written_at": datetime.now(timezone.utc).isoformat(), **result.to_dict()}
    path = out_dir / f"postmortem-{result.ticker}-{result.exit_date}.json"
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    return path


def write_aggregate(out_dir, results: list[PostmortemResult], exit_date: str) -> Path:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        "written_at": datetime.now(timezone.utc).isoformat(),
        "report_type": "attribution_postmortem_aggregate",
        "schema_version": 1,
        "recommend_only": True,
        "exit_date": exit_date,
        "count": len(results),
        "postmortems": [r.to_dict() for r in results],
    }
    path = out_dir / f"postmortem-{exit_date}.json"
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    return path


def format_summary(result: PostmortemResult) -> str:
    """Plain-language readout + a paste-ready stanza for wiki/03_alpha_library.md §G."""
    o = result.outcome
    fr = o.get("forward_return")
    fr_s = f"{fr * 100:+.1f}%" if isinstance(fr, (int, float)) else "n/a"
    lines = [
        f"  {result.ticker}  entry {result.entry_date} -> exit {result.exit_date}",
        f"  exited: {result.exited_reason}   return: {fr_s}",
        f"  CAUSE: {result.cause}  (confidence {result.cause_confidence})",
        f"  why: {result.why}",
        f"  narrative-method: {result.deltas.get('narrative', {}).get('method', 'n/a')}",
    ]
    return "\n".join(lines)


def main() -> int:
    import sys

    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    results = []
    for e in scan_closed_positions():
        r = run_postmortem(e)
        if r.exited_reason != "open":
            results.append(r)
    print(f"postmortem: {len(results)} closed/failed pick(s)")
    for r in results:
        print(format_summary(r))
        print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
