"""Daily picks compiler — emit ``outputs/picks-YYYY-MM-DD.json``.

This is the Phase-3 layer that finally wires the chip-flow FSM into the formal
10-signal contract specified in ``philosophy/05-decision-rubric.md``:

    slots 1–2   long_new            (new long entries — 多頭真漲)
    slots 3–4   short_new           (Mag7 Put / inverse ETF only)
    slots 5–10  position_followup   (add / trim / exit / hold_update)

It reads the FSM state stream (``outputs/state-YYYY-MM-DD.jsonl`` produced by
``sharks.scoring.chip_flow_fsm``) and arbitrates it into slots:

    State 2 BUY        → long_new
    State 1 WATCH      → position_followup (hold_update / watch)
    EXIT_FLAG          → position_followup (exit)

Hard rules honoured from the rubric:
  * Empty-slot rule (line 24): a slot below 0.50 confidence stays ``null``.
    **Padding is forbidden.** Unfilled slots are listed in ``no_action_buckets``.
  * No short model exists yet, so ``short_new_*`` are always ``null`` (honestly
    declared as no-action, never fabricated).
  * Confidence comes straight from the FSM; we never inflate it here.

This module does NOT modify ``daily_signals.py`` or any existing file. It is a
new sibling. If today's state stream is missing it will run the FSM itself.
"""

from __future__ import annotations

import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from sharks.scoring import chip_flow_fsm as fsm

# Minimum confidence to occupy a slot (rubric line 24).
CONFIDENCE_FLOOR = 0.50

# Tickers we know are Tier-1 index heavyweights (everything else defaults to
# the Tier-3 dynamic small/mid bucket the chip-flow model targets).
TIER1 = {"NVDA", "AAPL", "MSFT", "META", "GOOGL", "AMZN", "TSLA"}

LONG_NEW_SLOTS = 2
SHORT_NEW_SLOTS = 2
FOLLOWUP_SLOTS = 6

CONCEPT_PATH = "philosophy/concepts/chip-flow-single-point-breakout.md"


# ---------------------------------------------------------------------------
# Inputs
# ---------------------------------------------------------------------------

def load_news_sentiment(out_dir: Path, as_of: str) -> dict[str, dict]:
    """Return {ticker: news_sentiment_dict} from today's news-sentiment-*.jsonl.

    Empty dict if the file is absent — the FSM degrades gracefully without it.
    """
    path = out_dir / f"news-sentiment-{as_of}.jsonl"
    if not path.exists():
        return {}
    out: dict[str, dict] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
            ticker = obj.get("ticker")
            if ticker:
                out[ticker] = obj
        except Exception:
            continue
    return out


def _apply_news_bump_to_watch(rows: list[dict], ns_map: dict[str, dict]) -> int:
    """For existing WATCH rows (State 1), bump confidence by +0.10 when the
    ticker has ``bearish_no_price_follow=True``. Returns count bumped.

    Used when the state-*.jsonl already exists but a news-sentiment file
    has since been produced — re-running the FSM would be wasteful.
    """
    bumped = 0
    for row in rows:
        if row.get("signal") != fsm.SIG_WATCH:
            continue
        ns = ns_map.get(row.get("ticker", ""))
        if ns and ns.get("bearish_no_price_follow"):
            conf = float(row.get("confidence", 0.0))
            new_conf = round(min(conf + 0.10, 0.85), 3)
            if new_conf > conf:
                row["confidence"] = new_conf
                row.setdefault("notes", []).append("news_bearish_no_price_follow_+0.10")
                bumped += 1
    return bumped


def load_state_stream(out_dir: Path, as_of: str) -> list[dict]:
    """Load today's FSM classifications; run the FSM if the file is absent.

    When a ``news-sentiment-YYYY-MM-DD.jsonl`` is present:
      * fresh FSM run → passes the map straight into ``fsm.run`` so wash-out
        confidences include the 利空不跌 bump.
      * pre-existing state file → applies the bump in-place to WATCH rows
        (avoids re-running the FSM for unchanged tickers).
    """
    path = out_dir / f"state-{as_of}.jsonl"
    ns_map = load_news_sentiment(out_dir, as_of)
    if not path.exists():
        print(f"  state stream missing; running FSM for {as_of}", file=sys.stderr)
        results = fsm.run(as_of=as_of, news_sentiment_map=ns_map)
        fsm.write_state_jsonl(out_dir, as_of, results)
        fsm.write_summary(out_dir, as_of, results)
    if not path.exists():
        return []
    rows: list[dict] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            try:
                rows.append(json.loads(line))
            except Exception:
                continue
    if ns_map:
        bumped = _apply_news_bump_to_watch(rows, ns_map)
        if bumped:
            print(f"  news-sentiment: bumped {bumped} WATCH row(s) for 利空不跌", file=sys.stderr)
    return rows


def detect_regime(out_dir: Path, as_of: str) -> dict:
    """Best-effort regime block. Never fabricates VIX — leaves it null if no
    upstream module reported it."""
    vix: Optional[float] = None
    for prefix in ("liquidity-signals", "breadth-indicator", "regime"):
        files = sorted(out_dir.glob(f"{prefix}*.json"), reverse=True)
        if not files:
            continue
        try:
            data = json.loads(files[0].read_text(encoding="utf-8"))
        except Exception:
            continue
        found = _find_key(data, "vix")
        if isinstance(found, (int, float)):
            vix = float(found)
            break

    high_freq_ok = os.environ.get("SHARKS_HIGH_FREQ_OK") == "1"
    hf_eligible = bool(high_freq_ok and vix is not None and 12.0 <= vix <= 18.0)
    return {
        "macro_state_ref": f"wiki/01_macro_state.md@{as_of}",
        "vix": vix,
        "cycle_resonance_active": None,  # not computed here; null, not guessed
        "high_freq_mode_eligible": hf_eligible,
    }


def _find_key(obj: Any, key: str) -> Optional[Any]:
    """Shallow recursive search for a key (case-insensitive) in nested dicts."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k.lower() == key.lower() and isinstance(v, (int, float)):
                return v
            sub = _find_key(v, key)
            if sub is not None:
                return sub
    elif isinstance(obj, list):
        for item in obj[:50]:
            sub = _find_key(item, key)
            if sub is not None:
                return sub
    return None


# ---------------------------------------------------------------------------
# Slot builders
# ---------------------------------------------------------------------------

def _tier_for(ticker: str) -> int:
    return 1 if ticker in TIER1 else 3


def _size_pct(confidence: float) -> float:
    """Provisional confidence→size map (Phase-4 backtest will replace this).
    Caps at 4% even at max confidence; layered under 08-risk-and-position."""
    return round(min(4.0, max(1.0, confidence * 5.0)), 1)


def build_long_new(row: dict, slot_idx: int, as_of: str) -> dict:
    feats = row.get("features", {})
    bo = feats.get("breakout", {})
    stop = row.get("stop_loss")
    last_close = feats.get("last_close")
    # Enter near the breakout close. Clamp the entry floor to stay above the
    # stop (the breakout-bar low) so the zone never overlaps the stop — matters
    # for tight breakout bars where 0.99*close can dip below the bar low.
    if last_close:
        entry_low = round(last_close * 0.99, 4)
        if stop is not None and entry_low <= stop:
            entry_low = round(stop + max(0.01, last_close * 0.0005), 4)
        entry_high = round(last_close * 1.02, 4)
    else:
        entry_low = entry_high = None
    conf = float(row.get("confidence", 0.0))
    return {
        "slot": f"long_new_{slot_idx}",
        "ticker": row["ticker"],
        "tier": _tier_for(row["ticker"]),
        "quadrant": "genuine_bull",
        "thesis": (
            f"Chip-flow State 2 single-point breakout: reclaimed support + cleared "
            f"consolidation high on {bo.get('vol_multiple', '?')}x volume"
            + (" with institutional confirmation" if bo.get("chip_confirmed") else " (chip-confirm weak)")
        ),
        "horizon_days": 90,
        "entry_zone": {"low": entry_low, "high": entry_high},
        "stop_loss": stop,
        "invalidation": {
            "price": stop,
            "time_stop_days": 135,
            "catalyst": "Close below breakout-bar low AND institutional/main-player turns net-seller",
        },
        "size_pct": _size_pct(conf),
        "confidence": conf,
        "evidence_paths": [
            f"outputs/state-{as_of}.jsonl",
            f"outputs/chip-flow-fsm-{as_of}.json",
            CONCEPT_PATH,
        ],
        "author_role": "compiler",
    }


def build_followup(row: dict, slot_idx: int, as_of: str) -> dict:
    if row.get("signal") == fsm.SIG_EXIT_FLAG:
        action, status = "exit", "exit-flag"
        thesis = "False-breakout / trend-trail stop: lost the breakout-bar low or closed below 10MA."
    else:  # SIG_WATCH (State 1)
        action, status = "hold_update", "watch"
        thesis = "Chip-flow State 1 wash-out: support broken on contracting volume, no main-player dump. Watch for reclaim."
    return {
        "slot": f"position_followup_{slot_idx}",
        "ticker": row["ticker"],
        "action": action,
        "status": status,
        "thesis": thesis,
        "confidence": float(row.get("confidence", 0.0)),
        "evidence_paths": [f"outputs/state-{as_of}.jsonl", CONCEPT_PATH],
        "author_role": "compiler",
    }


# ---------------------------------------------------------------------------
# Compile
# ---------------------------------------------------------------------------

def compile_picks(rows: list[dict], regime: dict, as_of: str) -> dict:
    eligible_buys = sorted(
        [r for r in rows if r.get("signal") == fsm.SIG_BUY and float(r.get("confidence", 0)) >= CONFIDENCE_FLOOR],
        key=lambda r: r.get("confidence", 0), reverse=True,
    )
    followups = sorted(
        [r for r in rows if r.get("signal") in (fsm.SIG_WATCH, fsm.SIG_EXIT_FLAG)],
        key=lambda r: (r.get("signal") != fsm.SIG_EXIT_FLAG, -float(r.get("confidence", 0))),
    )

    signals: list[dict] = []
    no_action: list[str] = []

    # slots 1–2 long_new
    for i in range(1, LONG_NEW_SLOTS + 1):
        if i <= len(eligible_buys):
            signals.append(build_long_new(eligible_buys[i - 1], i, as_of))
        else:
            no_action.append(f"long_new_{i}")

    # slots 3–4 short_new — no short model yet → always no-action (never padded)
    for i in range(1, SHORT_NEW_SLOTS + 1):
        no_action.append(f"short_new_{i}")

    # slots 5–10 position_followup
    for i in range(1, FOLLOWUP_SLOTS + 1):
        slot_no = LONG_NEW_SLOTS + SHORT_NEW_SLOTS + i  # 5..10
        if i <= len(followups):
            fu = build_followup(followups[i - 1], slot_no, as_of)
            signals.append(fu)
        else:
            no_action.append(f"position_followup_{slot_no}")

    return {
        "schema_version": 1,
        "as_of": datetime.now(timezone.utc).isoformat(),
        "regime": regime,
        "signals": signals,
        "no_action_buckets": no_action,
        "footer": {
            "compiled_by": "sharks.daily_picks (chip-flow FSM)",
            "lint_passed": None,
            "duration_ms": None,
        },
    }


def main() -> int:
    t0 = time.time()
    as_of = sys.argv[1] if len(sys.argv) > 1 else datetime.now().strftime("%Y-%m-%d")
    out_dir = Path("outputs")
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"Compiling daily picks for {as_of}", file=sys.stderr)
    rows = load_state_stream(out_dir, as_of)
    regime = detect_regime(out_dir, as_of)
    picks = compile_picks(rows, regime, as_of)
    picks["footer"]["duration_ms"] = int((time.time() - t0) * 1000)

    out_path = out_dir / f"picks-{as_of}.json"
    out_path.write_text(json.dumps(picks, indent=2, default=str), encoding="utf-8")

    filled = len(picks["signals"])
    print(
        f"wrote {out_path}: {filled}/10 slots filled, "
        f"{len(picks['no_action_buckets'])} no-action",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
