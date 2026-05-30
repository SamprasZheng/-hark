"""Chip-Flow & Single-Point Breakout — three-state FSM orchestration layer.

This is the **state-machine** the analyst model specifies in
``philosophy/concepts/chip-flow-single-point-breakout.md``. It is deliberately
SEPARATE from ``chip_flow.py`` (which produces a continuous 0–100 chip-flow
*score*). This module reuses ``chip_flow.py``'s sub-signal primitives and
assembles them into the State 0 → State 1 → State 2 machine:

    State 0  ACCUMULATION  (籌碼沉澱)  — watchlist, do NOT open
    State 1  WASH_OUT      (洗盤騙線)  — observation, do NOT catch the knife
    State 2  BREAKOUT      (單點突破)  — BUY signal fires

The BUY only fires on a *transition* into State 2 (per the concept page:
"the model deliberately refuses to anticipate the breakout from the
accumulation phase; it waits for the trigger bar"). Transition is detected two
ways, belt-and-suspenders:
  1. self-contained — did price dip below support then reclaim + break the
     consolidation high on volume, all inside the recent window?
  2. cross-day — compare against the previous ``outputs/state-*.jsonl`` so we
     never re-emit a BUY for a ticker that was already in BREAKOUT yesterday.

Point-in-time: every public hook honours ``as_of`` per
``philosophy/09-point-in-time.md`` — the OHLCV frame is sliced to ``<= as_of``
before any feature is computed.

THRESHOLDS: the concept page (line 142) intentionally leaves N / volume-dry-up
ratio / breakout multiple undefined, to be tuned by Phase-4 walk-forward
backtest. They live in ``DEFAULT_THRESHOLDS`` below as **provisional
placeholders** so the FSM can run today. They are NOT analyst-provided numbers;
do not treat them as validated. The backtest harness overrides them.
"""

from __future__ import annotations

import json
import sys
import warnings
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)

import pandas as pd

from sharks.scoring.chip_flow import (
    DEFAULT_TICKERS,
    block_trade_proxy,
    fetch_daily_ohlcv,
    fetch_yf_quote_info,
    price_volume_divergence,
    volume_burst_detection,
)

# ---------------------------------------------------------------------------
# Provisional thresholds — Phase-4 backtest deliverable, NOT analyst numbers.
# ---------------------------------------------------------------------------
DEFAULT_THRESHOLDS: dict[str, float] = {
    "consolidation_lookback": 20,        # N sessions to measure the range
    "consolidation_max_range_pct": 18.0, # (hi-lo)/mean below this = "in range"
    "vol_dryup_ratio": 0.75,             # recent 5d vol / 20d avg below this = dried up
    "support_ma": 20,                    # 20-day MA = the key support line
    "support_break_margin": 0.01,        # close must be >1% below support to count as a *break* (filters noise)
    "trail_ma": 10,                      # 10-day MA = trend-trail exit reference
    "breakout_vol_multiple": 2.0,        # State 2 day volume >= 2x 20d avg
    "wash_out_lookback": 12,             # how recently support was broken (bars)
    "min_history": 40,                   # bars required before we classify
}

# State labels (also the jsonl persisted values).
ACCUMULATION = "ACCUMULATION"
WASH_OUT = "WASH_OUT"
BREAKOUT = "BREAKOUT"
NONE = "NONE"

# Signal emitted to the picks layer (Phase 3 reads these).
SIG_BUY = "BUY"                  # fresh transition into State 2
SIG_HOLD = "HOLD"               # already in State 2 yesterday
SIG_WATCH = "WATCH"            # State 1 — watch for reclaim
SIG_WATCHLIST = "WATCHLIST"   # State 0 — accumulation, not yet actionable
SIG_EXIT_FLAG = "EXIT_FLAG"   # broke below the breakout-bar low → false-breakout stop
SIG_NONE = None


@dataclass
class BreakoutSignal:
    """State-2 payload. ``breakout_bar_low`` is the pre-committed stop
    (the [[objective-watershed]] from the concept page §Module 4)."""

    confidence: float
    breakout_bar_low: float
    consolidation_high: float
    vol_multiple: float
    chip_confirmed: bool


@dataclass
class StateClassification:
    ticker: str
    as_of: str
    state: str
    confidence: float
    signal: Optional[str]
    stop_loss: Optional[float]
    transition: Optional[str] = None
    features: dict = field(default_factory=dict)
    notes: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Feature computation
# ---------------------------------------------------------------------------

def _slice_as_of(df: pd.DataFrame, as_of: Optional[str]) -> pd.DataFrame:
    """Point-in-time slice: keep only bars on/before ``as_of`` (YYYY-MM-DD)."""
    if as_of is None or df.empty:
        return df
    try:
        cutoff = pd.Timestamp(as_of)
        return df[df.index <= cutoff]
    except Exception:
        return df


def compute_features(df: pd.DataFrame, thr: dict) -> Optional[dict]:
    """Derive the geometric + volume features the three states share."""
    if df.empty or len(df) < int(thr["min_history"]):
        return None
    closes = df["Close"].dropna()
    highs = df["High"].dropna()
    lows = df["Low"].dropna()
    vols = df["Volume"].dropna()
    if len(closes) < int(thr["min_history"]):
        return None

    lookback = int(thr["consolidation_lookback"])
    # The consolidation band is the PRIOR N bars, EXCLUDING today — otherwise a
    # breakout bar inflates its own resistance and can never clear it.
    prior_highs = highs.iloc[-(lookback + 1):-1] if len(highs) > lookback else highs.iloc[:-1]
    prior_lows = lows.iloc[-(lookback + 1):-1] if len(lows) > lookback else lows.iloc[:-1]
    prior_closes = closes.iloc[-(lookback + 1):-1] if len(closes) > lookback else closes.iloc[:-1]
    window_hi = float(prior_highs.max())
    window_lo = float(prior_lows.min())
    window_mean = float(prior_closes.mean())
    range_pct = (window_hi - window_lo) / window_mean * 100 if window_mean > 0 else 999.0

    ma_support = float(closes.tail(int(thr["support_ma"])).mean())
    ma_trail = float(closes.tail(int(thr["trail_ma"])).mean())

    avg_20d_vol = float(vols.tail(20).mean())
    recent_5d_vol = float(vols.tail(5).mean())
    vol_dryup_ratio = recent_5d_vol / avg_20d_vol if avg_20d_vol > 0 else 1.0

    last_close = float(closes.iloc[-1])
    last_high = float(highs.iloc[-1])
    last_low = float(lows.iloc[-1])
    last_vol = float(vols.iloc[-1])
    today_vol_multiple = last_vol / avg_20d_vol if avg_20d_vol > 0 else 0.0

    # Did price dip below support within the recent window, then come back?
    wb = int(thr["wash_out_lookback"])
    recent_closes = closes.tail(wb)
    dipped_below_support = bool((recent_closes < ma_support).any())
    min_recent_close = float(recent_closes.min())

    return {
        "last_close": round(last_close, 4),
        "last_high": round(last_high, 4),
        "last_low": round(last_low, 4),
        "last_vol": int(last_vol),
        "consolidation_high": round(window_hi, 4),
        "consolidation_low": round(window_lo, 4),
        "range_pct": round(range_pct, 2),
        "ma_support": round(ma_support, 4),
        "ma_trail": round(ma_trail, 4),
        "avg_20d_vol": int(avg_20d_vol),
        "vol_dryup_ratio": round(vol_dryup_ratio, 3),
        "today_vol_multiple": round(today_vol_multiple, 3),
        "dipped_below_support_recent": dipped_below_support,
        "min_recent_close": round(min_recent_close, 4),
    }


def _chip_confirms_buying(df: pd.DataFrame, info: dict) -> tuple[bool, list[str]]:
    """Institutional / main-player confirmation proxy (free-data approximation).

    True chip confirmation needs 三大法人 / 主力分點 (Phase 4 twse_chip_client).
    Until then we proxy with: bullish P/V divergence, block accumulation, a
    volume burst, or a high institutional-held %.
    """
    reasons: list[str] = []
    div = price_volume_divergence(df)
    if "bullish" in div.get("divergence_class", ""):
        reasons.append("bullish_divergence")
    block = block_trade_proxy(df)
    if block.get("count", 0) >= 1:
        reasons.append(f"block_accum_x{block['count']}")
    vb = volume_burst_detection(df)
    if vb.get("burst_count_5d", 0) >= 1:
        reasons.append("volume_burst")
    inst = info.get("heldPercentInstitutions")
    if inst is not None and inst > 0.60:
        reasons.append(f"inst_{inst*100:.0f}pct")
    return (len(reasons) > 0, reasons)


def _chip_shows_dump(df: pd.DataFrame) -> bool:
    """True if the tape shows active institutional distribution (a real dump)."""
    div = price_volume_divergence(df)
    cls = div.get("divergence_class", "")
    return "active selling" in cls or "distribution" in cls


# ---------------------------------------------------------------------------
# Public state hooks (signatures match the concept page Implementation hooks)
# ---------------------------------------------------------------------------

def is_accumulation(feats: dict, df: pd.DataFrame, info: dict) -> Optional[float]:
    """State 0 confidence in [0, 1], or None if not in accumulation.

    Conditions (concept page §State 0): in-range consolidation + volume dry-up
    + chip-flow divergence (institutional net-buy proxy) despite the dry tape.
    """
    thr = DEFAULT_THRESHOLDS
    in_range = feats["range_pct"] <= thr["consolidation_max_range_pct"]
    dried_up = feats["vol_dryup_ratio"] <= thr["vol_dryup_ratio"]
    chip_ok, _ = _chip_confirms_buying(df, info)
    if not (in_range and dried_up):
        return None
    conf = 0.40
    if dried_up:
        conf += 0.10
    if chip_ok:
        conf += 0.20
    if in_range:
        conf += 0.05
    return round(min(conf, 0.90), 3)


def is_wash_out(
    feats: dict, df: pd.DataFrame, info: dict,
    *, news_sentiment: Optional[dict] = None,
) -> Optional[float]:
    """State 1 confidence, or None.

    Conditions (concept page §State 1): support break on contracting (not
    panicked) volume + no main-player dump + 利空不跌 (bearish-news-no-follow).

    The 利空不跌 leg is optional. When ``news_sentiment`` for this ticker
    reports ``bearish_no_price_follow: True``, we add a +0.10 confidence
    bump. When absent (Ollama down, no Finnhub key, etc.) the FSM degrades
    to the pre-news three-condition form — that's the documented fallback.
    """
    thr = DEFAULT_THRESHOLDS
    # A real support break: >margin below the 20MA, OR below the consolidation
    # low. A sub-margin dip is noise, not a wash-out.
    broke_ma = feats["last_close"] < feats["ma_support"] * (1 - thr["support_break_margin"])
    broke_low = feats["last_close"] < feats["consolidation_low"]
    below_support = broke_ma or broke_low
    contracting = feats["today_vol_multiple"] < 1.5   # not a climactic panic spike
    no_dump = not _chip_shows_dump(df)
    if not (below_support and contracting):
        return None
    conf = 0.40
    if contracting:
        conf += 0.10
    if no_dump:
        conf += 0.15
    # closer the break is to the support line (shallow flush), higher conviction
    if feats["last_close"] > feats["consolidation_low"]:
        conf += 0.05
    # 利空不跌 confluence — News × Technical conflict resolved Technical-side
    # per 02-signal-taxonomy. Only counts when the news layer actually fired.
    if news_sentiment and news_sentiment.get("bearish_no_price_follow"):
        conf += 0.10
    return round(min(conf, 0.85), 3)


def is_breakout(feats: dict, df: pd.DataFrame, info: dict) -> Optional[BreakoutSignal]:
    """State 2 BreakoutSignal, or None.

    Conditions (concept page §State 2): reclaim support AND break the
    consolidation high + volume >= breakout multiple + chip confirmation.
    Returns the breakout-bar low as the pre-committed stop.
    """
    thr = DEFAULT_THRESHOLDS
    reclaimed = feats["last_close"] > feats["ma_support"]
    broke_high = feats["last_close"] >= feats["consolidation_high"]
    vol_ok = feats["today_vol_multiple"] >= thr["breakout_vol_multiple"]
    chip_ok, _ = _chip_confirms_buying(df, info)
    if not (reclaimed and broke_high and vol_ok):
        return None
    conf = 0.45
    if vol_ok:
        conf += 0.15
    if chip_ok:
        conf += 0.20   # chip confirmation is the non-negotiable confluence leg
    else:
        conf -= 0.10   # breakout w/o chip confirm is a Strategy-B momentum trade, not State 2
    # bonus if this breakout followed a recent wash-out (the textbook path)
    if feats["dipped_below_support_recent"]:
        conf += 0.10
    return BreakoutSignal(
        confidence=round(min(max(conf, 0.0), 0.95), 3),
        breakout_bar_low=feats["last_low"],
        consolidation_high=feats["consolidation_high"],
        vol_multiple=feats["today_vol_multiple"],
        chip_confirmed=chip_ok,
    )


# ---------------------------------------------------------------------------
# Classification + transition
# ---------------------------------------------------------------------------

def classify(
    ticker: str,
    as_of: Optional[str] = None,
    prev_state: Optional[str] = None,
    df: Optional[pd.DataFrame] = None,
    info: Optional[dict] = None,
    *,
    news_sentiment: Optional[dict] = None,
) -> StateClassification:
    """Classify one ticker into the FSM state and derive its signal.

    ``prev_state`` is yesterday's persisted state (from the prior
    ``state-*.jsonl``) used to detect fresh transitions / EXIT_FLAG.
    ``news_sentiment`` is the per-ticker output of
    ``sharks.scoring.news_sentiment.analyse`` (optional; closes the 利空不跌 leg).
    """
    as_of_str = as_of or datetime.now().strftime("%Y-%m-%d")
    if df is None:
        df = fetch_daily_ohlcv(ticker, 120)
    df = _slice_as_of(df, as_of)
    if info is None:
        info = fetch_yf_quote_info(ticker)

    feats = compute_features(df, DEFAULT_THRESHOLDS)
    if feats is None:
        return StateClassification(
            ticker=ticker, as_of=as_of_str, state=NONE, confidence=0.0,
            signal=SIG_NONE, stop_loss=None, notes=["insufficient_history"],
        )

    notes: list[str] = []
    # Priority: BREAKOUT (most specific) → WASH_OUT → ACCUMULATION → NONE.
    bo = is_breakout(feats, df, info)
    if bo is not None:
        _, chip_reasons = _chip_confirms_buying(df, info)
        notes.append(f"chip_confirm: {chip_reasons or 'none'}")
        fresh = prev_state in (WASH_OUT, ACCUMULATION, None, NONE)
        signal = SIG_BUY if fresh else SIG_HOLD
        transition = f"{prev_state or 'NEW'}->{BREAKOUT}" if fresh else None
        return StateClassification(
            ticker=ticker, as_of=as_of_str, state=BREAKOUT,
            confidence=bo.confidence, signal=signal,
            stop_loss=bo.breakout_bar_low, transition=transition,
            features={**feats, "breakout": asdict(bo)}, notes=notes,
        )

    # EXIT_FLAG: were we in BREAKOUT and have now lost the breakout-bar low?
    if prev_state == BREAKOUT and feats["last_close"] < feats["ma_trail"]:
        notes.append("closed_below_trail_ma_after_breakout")
        return StateClassification(
            ticker=ticker, as_of=as_of_str, state=NONE, confidence=0.55,
            signal=SIG_EXIT_FLAG, stop_loss=None,
            transition=f"{BREAKOUT}->exit", features=feats, notes=notes,
        )

    wo_conf = is_wash_out(feats, df, info, news_sentiment=news_sentiment)
    if wo_conf is not None:
        return StateClassification(
            ticker=ticker, as_of=as_of_str, state=WASH_OUT,
            confidence=wo_conf, signal=SIG_WATCH, stop_loss=None,
            transition=(f"{prev_state}->{WASH_OUT}" if prev_state not in (WASH_OUT, None) else None),
            features=feats, notes=notes,
        )

    acc_conf = is_accumulation(feats, df, info)
    if acc_conf is not None:
        return StateClassification(
            ticker=ticker, as_of=as_of_str, state=ACCUMULATION,
            confidence=acc_conf, signal=SIG_WATCHLIST, stop_loss=None,
            transition=(f"{prev_state}->{ACCUMULATION}" if prev_state not in (ACCUMULATION, None) else None),
            features=feats, notes=notes,
        )

    return StateClassification(
        ticker=ticker, as_of=as_of_str, state=NONE, confidence=0.0,
        signal=SIG_NONE, stop_loss=None, features=feats, notes=notes,
    )


# ---------------------------------------------------------------------------
# Persistence (Phase 2.6)
# ---------------------------------------------------------------------------

def load_prev_states(out_dir: Path, before: str) -> dict[str, str]:
    """Return {ticker: state} from the most recent state-*.jsonl strictly
    before ``before`` (YYYY-MM-DD). Empty dict if none — FSM still works on
    day 1 via the self-contained recent-path heuristic."""
    files = sorted(out_dir.glob("state-*.jsonl"))
    prior = [f for f in files if f.stem.replace("state-", "") < before]
    if not prior:
        return {}
    out: dict[str, str] = {}
    for line in prior[-1].read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
            out[obj["ticker"]] = obj["state"]
        except Exception:
            continue
    return out


def write_state_jsonl(out_dir: Path, as_of: str, results: list[StateClassification]) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"state-{as_of}.jsonl"
    with path.open("w", encoding="utf-8") as fh:
        for r in results:
            fh.write(json.dumps(asdict(r), default=str) + "\n")
    return path


def write_summary(out_dir: Path, as_of: str, results: list[StateClassification]) -> Path:
    """Compact per-day rollup: state counts + the BUY list. Referenced by the
    picks compiler's evidence_paths, so both the CLI and the daily_picks
    fallback must produce it."""
    out_dir.mkdir(parents=True, exist_ok=True)
    counts: dict[str, int] = {}
    for r in results:
        counts[r.state] = counts.get(r.state, 0) + 1
    summary = {
        "as_of": datetime.now(timezone.utc).isoformat(),
        "schema_version": 1,
        "state_counts": counts,
        "buy_signals": [
            {"ticker": r.ticker, "confidence": r.confidence, "stop_loss": r.stop_loss}
            for r in results if r.signal == SIG_BUY
        ],
    }
    path = out_dir / f"chip-flow-fsm-{as_of}.json"
    path.write_text(json.dumps(summary, indent=2, default=str), encoding="utf-8")
    return path


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def run(
    tickers: Optional[list[str]] = None, as_of: Optional[str] = None,
    *, news_sentiment_map: Optional[dict[str, dict]] = None,
) -> list[StateClassification]:
    tickers = tickers or DEFAULT_TICKERS
    as_of_str = as_of or datetime.now().strftime("%Y-%m-%d")
    out_dir = Path("outputs")
    prev = load_prev_states(out_dir, as_of_str)
    ns_map = news_sentiment_map or {}

    results: list[StateClassification] = []
    for t in tickers:
        try:
            r = classify(
                t, as_of=as_of, prev_state=prev.get(t),
                news_sentiment=ns_map.get(t),
            )
            results.append(r)
            if r.signal in (SIG_BUY, SIG_EXIT_FLAG):
                print(f"  {t}: {r.state} conf={r.confidence} *** {r.signal} ***", file=sys.stderr)
            else:
                print(f"  {t}: {r.state} conf={r.confidence} ({r.signal})", file=sys.stderr)
        except Exception as e:
            print(f"  {t}: error {e}", file=sys.stderr)
    return results


def main() -> int:
    as_of = sys.argv[1] if len(sys.argv) > 1 else datetime.now().strftime("%Y-%m-%d")
    print(f"Chip-flow FSM as of {as_of}", file=sys.stderr)
    results = run(as_of=as_of)
    out_dir = Path("outputs")
    path = write_state_jsonl(out_dir, as_of, results)
    write_summary(out_dir, as_of, results)

    buys = [r for r in results if r.signal == SIG_BUY]
    print(f"wrote {path} ({len(results)} tickers, {len(buys)} BUY)", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
