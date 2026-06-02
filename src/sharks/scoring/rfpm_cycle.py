"""RF / Power-Management / Analog cycle tracker — variable #15 made runnable.

This operationalises the principal's "次級變數 #15":

    "特定射頻(RF)或電源管理 IC 的急單動態 — 終端消費電子復甦的第一個訊號,
     不是看組裝廠,而是看通路商對這些二線、低毛利類比 IC 是否開始下急單。"

The signal is a *leading indicator*: distributor rush-orders / book-to-bill > 1 /
price hikes / lean channel inventory turn up BEFORE the end-market prints. The
2026 twist this tracker is built to surface (see ``tech/rf-connectivity.md`` §0):
the recovery fires through the **industrial / AI / distribution door** while the
**handset door** stays capped by the memory-shortage unit recession. So the
tracker reads TWO doors separately and never collapses them into one number.

It deliberately mirrors ``chip_flow_fsm.py``: a transparent, rule-based state
machine over (a) a price-derived market read and (b) a curated hard-evidence
layer for the signals that have **no free API** (book-to-bill, channel-inventory
days, list-price hikes — these live in earnings calls and distributor reports,
not in yfinance). The hard layer ships seeded with the cross-confirmed 2026 data
and is overridable from ``watchlist/rfpm-cycle-evidence.json`` so the desk edits
numbers as new prints land, without touching code.

Point-in-time: ``as_of`` slices the OHLCV frame to ``<= as_of`` and filters the
evidence layer to entries dated ``<= as_of`` (philosophy/09-point-in-time.md).

RECOMMEND-ONLY. This emits a cycle *reading*, never a trade. It feeds the
tech_dd / FOM observe-first overlay, not ``final_fom``.
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

from sharks.scoring.chip_flow import fetch_daily_ohlcv

# ---------------------------------------------------------------------------
# The basket — grouped by the two doors (tech/rf-connectivity.md §4).
# ---------------------------------------------------------------------------
# LEADING door = power/analog + connectivity + picks-and-shovels + distributors.
# LAGGING door = handset RF front-end (memory-shock capped into 2027).
SEGMENTS: dict[str, list[str]] = {
    # ── leading door ──────────────────────────────────────────────────────
    "power_analog":  ["MPWR", "TXN", "ADI", "ON", "MCHP", "POWI", "VICR", "DIOD", "AOSL"],
    "connectivity":  ["SYNA", "NXPI", "CRUS", "CEVA", "SLAB"],
    "picks_shovels": ["KEYS", "GFS", "TSEM", "MTSI"],
    "distributors":  ["ARW", "AVT"],          # Arrow / Avnet — the book-to-bill tape proxy
    # ── lagging door ──────────────────────────────────────────────────────
    # PURE handset RF only. QCOM/AVGO are deliberately EXCLUDED from the door:
    # their tape is AI/diversified-driven (AVGO ~AI engine, QCOM auto/IoT), so
    # including them flatters the handset read. Kept informational below.
    "handset_rffe":  ["QRVO", "SWKS"],
    # ── informational (not a door) ────────────────────────────────────────
    "diversified_rf": ["QCOM", "AVGO"],        # RF-exposed but AI/diversified tape
}
LEADING_SEGMENTS = ("power_analog", "connectivity", "picks_shovels", "distributors")
LAGGING_SEGMENTS = ("handset_rffe",)
INFORMATIONAL_SEGMENTS = ("diversified_rf",)


def _door_of(seg: str) -> str:
    if seg in LEADING_SEGMENTS:
        return "leading"
    if seg in LAGGING_SEGMENTS:
        return "lagging"
    return "informational"

# Benchmark for relative strength (semis). SPY as the broad anchor.
BENCH_SEMI = "SOXX"
BENCH_BROAD = "SPY"

# Cycle states (also the persisted values). Ordered destock → rollover.
DESTOCK = "DESTOCK"            # 去化中 — inventory still purging, B:B < 1
RUSH_RESTOCK = "RUSH_RESTOCK"  # 急單/復甦 — the variable-#15 trigger: B:B>1, hikes, lean channel
EXPANSION = "EXPANSION"        # 擴張 — broad momentum confirms the restock
OVERHEAT = "OVERHEAT"          # 過熱 — momentum parabolic, double-ordering risk
ROLLOVER = "ROLLOVER"          # 反轉 — momentum + evidence both rolling over
NEUTRAL = "NEUTRAL"            # mixed / insufficient

# ---------------------------------------------------------------------------
# Seeded hard-evidence layer (cross-confirmed 2026 prints; see page Sources).
# Each entry: signal ∈ {-1, 0, +1} (cycle direction), weight, as_of, grade, src.
# Override / extend via watchlist/rfpm-cycle-evidence.json (same shape).
# ---------------------------------------------------------------------------
DEFAULT_EVIDENCE: list[dict] = [
    {"key": "distributor_book_to_bill", "door": "leading", "signal": +1, "weight": 1.0,
     "as_of": "2026-05-31", "grade": "B",
     "note": "Arrow first YoY component growth since 2022 + B:B>1 all 3 regions; Avnet B:B>1; Microchip 4yr-high bookings",
     "source": "Distribution Strategy Group / Digitimes"},
    {"key": "list_price_hikes", "door": "leading", "signal": +1, "weight": 1.0,
     "as_of": "2026-05-31", "grade": "C",
     "note": "TI +15-85% (Apr 1), ADI +15% line-wide (Feb 1); even China (SG Micro/Novosense/3Peak) hiking — destock complete",
     "source": "Digitimes (SKU% paywalled; direction multi-sourced)"},
    {"key": "channel_inventory_days", "door": "leading", "signal": +1, "weight": 0.8,
     "as_of": "2026-05-31", "grade": "A",
     "note": "Microchip distribution inventory 26 days (historic low end), restocking expected; ADI ~6 weeks ordering-to-consumption",
     "source": "MCHP FQ4'26 8-K"},
    {"key": "analog_broad_recovery", "door": "leading", "signal": +1, "weight": 0.8,
     "as_of": "2026-05-31", "grade": "A",
     "note": "ADI +30% broad-based recovery; NXP Ind&IoT +24%; SYNA Core IoT +31%; DIOD 6th straight double-digit qtr",
     "source": "ADI / NXPI / SYNA / DIOD 8-Ks"},
    {"key": "ai_datacenter_power_pull", "door": "leading", "signal": +1, "weight": 0.6,
     "as_of": "2026-05-31", "grade": "A",
     "note": "MPWR Enterprise Data +97.7%; ON AI-DC +30% QoQ; VICR backlog +70%/B:B>2 — the AI overlay on the cyclical turn",
     "source": "MPWR / ON / VICR earnings"},
    {"key": "smartphone_units", "door": "lagging", "signal": -1, "weight": 1.0,
     "as_of": "2026-05-31", "grade": "B",
     "note": "IDC: smartphones -12.9% to 1.12B in 2026 (steepest on record), memory-shortage starves handset BoM; +2% 2027",
     "source": "IDC"},
    {"key": "handset_rf_content", "door": "lagging", "signal": 0, "weight": 0.6,
     "as_of": "2026-05-31", "grade": "B",
     "note": "SWKS: blended RF content 'roughly flat'; RFFE TAM $15.4B(redacted)->$17B(redacted) — content tailwind has flattened",
     "source": "SWKS Q2'26 call / Yole"},
]

# Provisional price-signal thresholds (Phase-4 walk-forward deliverable — these
# are NOT validated numbers, only enough to make the tape read run today).
DEFAULT_THRESHOLDS: dict[str, float] = {
    "min_history": 130,        # ~6 trading months
    "mom_short_days": 63,      # ~3 months
    "mom_long_days": 126,      # ~6 months
    "ma_fast": 50,
    "ma_slow": 200,
    "overheat_mom_pct": 35.0,  # 6m segment return above this + parabolic = overheat risk
}


@dataclass
class SegmentSignal:
    segment: str
    door: str
    n_tickers: int
    n_priced: int
    mom_3m_pct: Optional[float]
    mom_6m_pct: Optional[float]
    pct_above_ma_fast: Optional[float]
    pct_above_ma_slow: Optional[float]
    rs_vs_semi: Optional[float]        # 6m return minus SOXX 6m return (pp)
    score: Optional[float]             # 0-100 composite momentum/breadth score
    per_ticker: dict = field(default_factory=dict)


@dataclass
class CycleReading:
    as_of: str
    state: str                          # the headline (leading-door-driven) state
    leading_door: dict                  # {state, score, evidence_score}
    lagging_door: dict
    evidence_score_leading: float       # -1..+1
    evidence_score_lagging: float
    segments: dict                      # segment -> SegmentSignal asdict
    headline: str
    notes: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Evidence layer
# ---------------------------------------------------------------------------

# Hand-curated layer (grade A/B, committed, the source of truth — edit by hand).
CURATED_EVIDENCE_PATH = Path("watchlist/rfpm-cycle-evidence.json")
# Auto proxy layer (grade C/D, regenerated monthly by rfpm_evidence_fetch; NOT
# committed — lives in outputs/). Merged UNDER curated (curated always wins).
AUTO_EVIDENCE_PATH = Path("outputs/rfpm-cycle-evidence-auto.json")


def _read_evidence_file(path: Path) -> list[dict]:
    if not path or not path.exists():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    except Exception as e:  # pragma: no cover - defensive
        print(f"  warn: bad evidence file {path}: {e}", file=sys.stderr)
        return []


def load_evidence(as_of: Optional[str] = None,
                  evidence_path: Optional[Path] = None,
                  auto_path: Optional[Path] = None,
                  include_auto: bool = True) -> list[dict]:
    """Return evidence dated ``<= as_of``, merged by ``key`` across two layers:
      - **auto** proxy layer (grade C/D, ``outputs/rfpm-cycle-evidence-auto.json``,
        refreshed monthly by ``rfpm_evidence_fetch``) — the base, and
      - **curated** layer (grade A/B, ``watchlist/rfpm-cycle-evidence.json``) —
        which OVERRIDES auto by key (the hand-edited file is always authoritative).
    Falls back to the in-module ``DEFAULT_EVIDENCE`` seed when no curated file
    is present. ``include_auto=False`` reads the curated/seed layer only (used by
    deterministic tests)."""
    path = evidence_path or CURATED_EVIDENCE_PATH
    curated = _read_evidence_file(path) or list(DEFAULT_EVIDENCE)
    auto = _read_evidence_file(auto_path or AUTO_EVIDENCE_PATH) if include_auto else []
    by_key: dict = {}
    for e in auto:        # auto first (lower priority)
        by_key[e.get("key", id(e))] = e
    for e in curated:     # curated overrides auto by key
        by_key[e.get("key", id(e))] = e
    evidence = list(by_key.values())
    if as_of:
        evidence = [e for e in evidence if str(e.get("as_of", "")) <= as_of]
    return evidence


def score_evidence(evidence: list[dict], door: str) -> float:
    """Weighted mean signal for one door, in [-1, +1]. 0 if no evidence."""
    rows = [e for e in evidence if e.get("door") == door]
    if not rows:
        return 0.0
    num = sum(float(e.get("signal", 0)) * float(e.get("weight", 1.0)) for e in rows)
    den = sum(abs(float(e.get("weight", 1.0))) for e in rows) or 1.0
    return round(num / den, 3)


# ---------------------------------------------------------------------------
# Price-derived market read
# ---------------------------------------------------------------------------

def _slice_as_of(df: pd.DataFrame, as_of: Optional[str]) -> pd.DataFrame:
    if as_of is None or df.empty:
        return df
    try:
        return df[df.index <= pd.Timestamp(as_of)]
    except Exception:
        return df


def _bench_return(ticker: str, as_of: Optional[str], days: int, thr: dict) -> Optional[float]:
    df = _slice_as_of(fetch_daily_ohlcv(ticker, 400), as_of)
    return _trailing_return(df, days)


def _trailing_return(df: pd.DataFrame, days: int) -> Optional[float]:
    if df.empty or "Close" not in df.columns:
        return None
    closes = df["Close"].dropna()
    if len(closes) <= days:
        return None
    past = float(closes.iloc[-(days + 1)])
    now = float(closes.iloc[-1])
    if past <= 0:
        return None
    return round((now / past - 1.0) * 100.0, 2)


def _pct_above_ma(df: pd.DataFrame, window: int) -> Optional[bool]:
    if df.empty or "Close" not in df.columns:
        return None
    closes = df["Close"].dropna()
    if len(closes) < window:
        return None
    ma = float(closes.tail(window).mean())
    return bool(float(closes.iloc[-1]) > ma)


def compute_segment_signal(segment: str, tickers: list[str], door: str,
                           as_of: Optional[str], thr: dict,
                           semi_6m: Optional[float],
                           ohlcv: Optional[dict[str, pd.DataFrame]] = None) -> SegmentSignal:
    """Per-segment momentum + breadth + relative-strength, scored 0-100.

    ``ohlcv`` lets tests inject frames; otherwise we fetch via chip_flow.
    """
    per: dict[str, dict] = {}
    mom3, mom6 = [], []
    above_fast = above_slow = priced = 0
    for t in tickers:
        df = (ohlcv or {}).get(t)
        if df is None:
            df = fetch_daily_ohlcv(t, 400)
        df = _slice_as_of(df, as_of)
        r3 = _trailing_return(df, int(thr["mom_short_days"]))
        r6 = _trailing_return(df, int(thr["mom_long_days"]))
        af = _pct_above_ma(df, int(thr["ma_fast"]))
        asl = _pct_above_ma(df, int(thr["ma_slow"]))
        if r6 is not None or af is not None:
            priced += 1
        if r3 is not None:
            mom3.append(r3)
        if r6 is not None:
            mom6.append(r6)
        if af:
            above_fast += 1
        if asl:
            above_slow += 1
        per[t] = {"r3m": r3, "r6m": r6, "above_50d": af, "above_200d": asl}

    n = len(tickers)
    avg3 = round(sum(mom3) / len(mom3), 2) if mom3 else None
    avg6 = round(sum(mom6) / len(mom6), 2) if mom6 else None
    pct_fast = round(above_fast / n * 100, 1) if n else None
    pct_slow = round(above_slow / n * 100, 1) if n else None
    rs = round(avg6 - semi_6m, 2) if (avg6 is not None and semi_6m is not None) else None

    # Composite 0-100: breadth (50%) + 6m momentum mapped (30%) + RS (20%).
    score = None
    if priced:
        breadth = ((pct_fast or 0) + (pct_slow or 0)) / 2.0           # 0-100
        mom_component = max(0.0, min(100.0, 50.0 + (avg6 or 0) * 1.5))  # +33%6m -> 100
        rs_component = max(0.0, min(100.0, 50.0 + (rs or 0) * 2.0))
        score = round(0.5 * breadth + 0.3 * mom_component + 0.2 * rs_component, 1)

    return SegmentSignal(
        segment=segment, door=door, n_tickers=n, n_priced=priced,
        mom_3m_pct=avg3, mom_6m_pct=avg6, pct_above_ma_fast=pct_fast,
        pct_above_ma_slow=pct_slow, rs_vs_semi=rs, score=score, per_ticker=per,
    )


# ---------------------------------------------------------------------------
# Classification — the two-door state machine (pure; unit-tested offline)
# ---------------------------------------------------------------------------

def classify_door(price_score: Optional[float], evidence_score: float, thr: dict,
                  mom_6m: Optional[float]) -> str:
    """Map (price breadth/momentum score 0-100, evidence -1..+1) to a cycle state.

    Evidence is the *leading* hard signal (rush-orders/B:B/hikes); price is the
    market's confirmation. The rush-order trigger (RUSH_RESTOCK) fires on strong
    evidence even before price has fully re-rated — that is the whole point of
    variable #15 (the order book turns before the tape)."""
    ev = evidence_score
    ps = price_score if price_score is not None else 50.0
    parabolic = (mom_6m is not None and mom_6m >= thr["overheat_mom_pct"])

    # Rollover: evidence negative AND price weak.
    if ev <= -0.34 and ps < 45:
        return ROLLOVER
    # Overheat: strong evidence already priced + parabolic momentum + extended breadth.
    if ev >= 0.34 and parabolic and ps >= 75:
        return OVERHEAT
    # Expansion: evidence positive AND price confirms broadly.
    if ev >= 0.34 and ps >= 60:
        return EXPANSION
    # Rush/restock: the leading trigger — strong evidence, price not yet extended.
    if ev >= 0.34:
        return RUSH_RESTOCK
    # Destock: evidence still negative, price weak.
    if ev <= -0.20 and ps < 55:
        return DESTOCK
    return NEUTRAL


def _door_aggregate(segments: dict[str, SegmentSignal], door_segs: tuple) -> tuple[Optional[float], Optional[float]]:
    """Mean price-score and mean 6m-mom across a door's segments (priced only)."""
    scores = [segments[s].score for s in door_segs if s in segments and segments[s].score is not None]
    moms = [segments[s].mom_6m_pct for s in door_segs if s in segments and segments[s].mom_6m_pct is not None]
    avg_score = round(sum(scores) / len(scores), 1) if scores else None
    avg_mom = round(sum(moms) / len(moms), 2) if moms else None
    return avg_score, avg_mom


_STATE_ZH = {
    DESTOCK: "去化中", RUSH_RESTOCK: "急單/復甦(變數#15 觸發)", EXPANSION: "擴張",
    OVERHEAT: "過熱", ROLLOVER: "反轉", NEUTRAL: "中性/混合",
}


def build_reading(segments: dict[str, SegmentSignal], evidence: list[dict],
                  as_of: str, thr: dict) -> CycleReading:
    ev_lead = score_evidence(evidence, "leading")
    ev_lag = score_evidence(evidence, "lagging")
    lead_score, lead_mom = _door_aggregate(segments, LEADING_SEGMENTS)
    lag_score, lag_mom = _door_aggregate(segments, LAGGING_SEGMENTS)

    lead_state = classify_door(lead_score, ev_lead, thr, lead_mom)
    lag_state = classify_door(lag_score, ev_lag, thr, lag_mom)

    notes = [
        "變數#15: rush-order/B:B/price-hike is a LEADING signal — the order book turns before the tape.",
        "Two doors read separately: leading=industrial/AI/distribution, lagging=handset (memory-shock capped).",
    ]
    headline = (
        f"LEADING door = {lead_state} ({_STATE_ZH[lead_state]}); "
        f"LAGGING (handset) door = {lag_state} ({_STATE_ZH[lag_state]}). "
        f"evidence leading={ev_lead:+.2f} lagging={ev_lag:+.2f}."
    )
    return CycleReading(
        as_of=as_of, state=lead_state,
        leading_door={"state": lead_state, "price_score": lead_score,
                      "mom_6m_pct": lead_mom, "evidence_score": ev_lead},
        lagging_door={"state": lag_state, "price_score": lag_score,
                      "mom_6m_pct": lag_mom, "evidence_score": ev_lag},
        evidence_score_leading=ev_lead, evidence_score_lagging=ev_lag,
        segments={s: asdict(sig) for s, sig in segments.items()},
        headline=headline, notes=notes,
    )


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------

def run(as_of: Optional[str] = None, *, network: bool = True,
        evidence_path: Optional[Path] = None,
        ohlcv: Optional[dict[str, pd.DataFrame]] = None,
        include_auto: bool = True,
        auto_path: Optional[Path] = None) -> CycleReading:
    as_of_str = as_of or datetime.now().strftime("%Y-%m-%d")
    thr = DEFAULT_THRESHOLDS
    evidence = load_evidence(as_of_str, evidence_path,
                             auto_path=auto_path, include_auto=include_auto)

    segments: dict[str, SegmentSignal] = {}
    semi_6m = None
    if network or ohlcv is not None:
        semi_6m = (_trailing_return(_slice_as_of((ohlcv or {}).get(BENCH_SEMI)
                   if ohlcv else fetch_daily_ohlcv(BENCH_SEMI, 400), as_of),
                   int(thr["mom_long_days"]))) if (network or ohlcv) else None
        for seg, tickers in SEGMENTS.items():
            door = _door_of(seg)
            segments[seg] = compute_segment_signal(
                seg, tickers, door, as_of_str, thr, semi_6m, ohlcv=ohlcv,
            )
    else:
        # Evidence-only degrade (no network): segments carry no price score.
        for seg, tickers in SEGMENTS.items():
            door = _door_of(seg)
            segments[seg] = SegmentSignal(seg, door, len(tickers), 0, None, None,
                                          None, None, None, None, {})

    return build_reading(segments, evidence, as_of_str, thr)


def write_output(out_dir: Path, reading: CycleReading) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema_version": 1,
        "written_at": datetime.now(timezone.utc).isoformat(),
        "as_of": reading.as_of,
        "variable": "#15 RF / power-management IC rush-order dynamics",
        "recommend_only": True,
        **asdict(reading),
    }
    path = out_dir / f"rfpm-cycle-{reading.as_of}.json"
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False, default=str),
                    encoding="utf-8")
    return path


def main(argv: Optional[list[str]] = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    as_of = next((a for a in argv if not a.startswith("-")), None) \
        or datetime.now().strftime("%Y-%m-%d")
    network = "--no-network" not in argv
    print(f"RF/PM cycle tracker (variable #15) as of {as_of} (network={network})",
          file=sys.stderr)
    reading = run(as_of=as_of, network=network)
    print("  " + reading.headline, file=sys.stderr)
    path = write_output(Path("outputs"), reading)
    print(f"wrote {path}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

