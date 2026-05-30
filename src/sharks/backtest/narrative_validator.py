"""Pull monthly OHLCV from 2020 and validate the principal's 2020-2026 narrative.

Reads no API keys; yfinance is free + key-less.

Outputs:
  outputs/narrative-validation-YYYY-MM-DD.json — structured returns per phase
  outputs/narrative-validation-YYYY-MM-DD.md  — human-readable summary

Phase 2 / early. Phase 4 backtest framework replaces this with walk-forward.
"""

from __future__ import annotations

import json
import math
import sys
import warnings
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)

import numpy as np
import pandas as pd
import yfinance as yf

# ------------------------------------------------------------------- universe

INDICES = ["^GSPC", "^NDX", "^SOX", "^VIX"]
MAG7 = ["NVDA", "AAPL", "TSLA", "AMZN", "GOOGL", "MSFT", "META"]
SUPPLY_TIER2 = ["TSM", "ASML", "AVGO", "AMD", "ARM", "MU", "AMAT", "LRCX", "INTC"]

# Serenity-framework rotation buckets (per WebSearch 2026-05-29):
MEMORY_PHASE1 = ["MU", "WDC", "STX", "SIMO"]  # HBM / DRAM / NAND adjacents
OPTICAL_PHASE2 = ["LITE", "COHR", "CIEN", "ANET", "AAOI", "FN", "INFN"]  # transceivers
SIPH_PHASE3 = ["AXTI", "ALAB", "CRDO", "AEHR", "POET"]  # silicon photonics, light sources

# Macro / crypto co-asset
CRYPTO = ["BTC-USD", "ETH-USD"]

ALL_TICKERS = sorted(
    set(INDICES + MAG7 + SUPPLY_TIER2 + MEMORY_PHASE1 + OPTICAL_PHASE2 + SIPH_PHASE3 + CRYPTO)
)

START = "2019-12-01"  # buffer month for first-bar lookback
END = "2026-05-29"
TODAY = "2026-05-29"

# ------------------------------------------------------------------- phases (per wiki/03_alpha_library §A)

@dataclass
class Phase:
    code: str
    name: str
    start: str  # inclusive month-start
    end: str    # inclusive month-end (uses month-end close)
    leader_claim: Optional[str] = None  # principal's named leader (for verification)


PHASES: list[Phase] = [
    Phase("P1", "Covid emergency rally", "2020-03-01", "2021-12-31", leader_claim="TSLA"),
    Phase("P2", "Tightening drawdown", "2022-01-01", "2022-12-31", leader_claim=None),
    Phase("P3", "AI revolution emergence", "2023-01-01", "2024-11-30", leader_claim="NVDA"),
    Phase("P4_btc", "Trump-election BTC extension (sub-period)", "2024-09-01", "2024-12-31", leader_claim="BTC-USD"),
    Phase("P5", "Trump-tariff drawdown", "2024-12-01", "2025-04-30", leader_claim=None),
    Phase("P6", "AI rally resumption + breadth", "2025-05-01", "2026-05-31", leader_claim="NVDA"),
]

# ------------------------------------------------------------------- data ingest

def pull_monthly(tickers: list[str], start: str, end: str) -> pd.DataFrame:
    """Bulk-pull monthly bars; returns multi-index Close prices DataFrame."""
    print(f"yfinance: pulling {len(tickers)} tickers, monthly bars, {start}..{end}", file=sys.stderr)
    raw = yf.download(
        tickers=tickers,
        start=start,
        end=end,
        interval="1mo",
        auto_adjust=True,
        progress=False,
        group_by="ticker",
        threads=True,
    )

    # Normalise: build a clean Close-only DataFrame indexed by month.
    closes = pd.DataFrame()
    for t in tickers:
        try:
            if isinstance(raw.columns, pd.MultiIndex):
                s = raw[t]["Close"]
            else:
                s = raw["Close"]  # single-ticker case (defensive)
            closes[t] = s
        except (KeyError, ValueError):
            print(f"  - WARN: no data for {t}", file=sys.stderr)
    closes = closes.sort_index()
    # Drop tz to make slicing trivial
    if closes.index.tz is not None:
        closes.index = closes.index.tz_localize(None)
    return closes


# ------------------------------------------------------------------- analysis

def phase_return(closes: pd.DataFrame, ticker: str, phase: Phase) -> Optional[float]:
    """Return for ticker over [phase.start .. phase.end], using month-end closes.

    Logic: take the last close BEFORE phase.start as the entry, and the last
    close ON OR BEFORE phase.end as the exit. None if ticker has no data in window.
    """
    s = closes.get(ticker)
    if s is None or s.dropna().empty:
        return None
    s = s.dropna()
    start_ts = pd.Timestamp(phase.start)
    end_ts = pd.Timestamp(phase.end)
    pre_start = s.loc[:start_ts]
    in_window = s.loc[start_ts:end_ts]
    if in_window.empty:
        return None
    entry = pre_start.iloc[-1] if not pre_start.empty else in_window.iloc[0]
    exit_ = in_window.iloc[-1]
    if entry == 0 or math.isnan(entry) or math.isnan(exit_):
        return None
    return float(exit_ / entry - 1.0)


def phase_drawdown(closes: pd.DataFrame, ticker: str, phase: Phase) -> Optional[float]:
    """Max drawdown (negative number) during phase, from running max to subsequent min."""
    s = closes.get(ticker)
    if s is None:
        return None
    in_window = s.loc[pd.Timestamp(phase.start):pd.Timestamp(phase.end)].dropna()
    if len(in_window) < 2:
        return None
    cumax = in_window.cummax()
    dd = (in_window / cumax - 1.0).min()
    return float(dd)


def rank_leaders(closes: pd.DataFrame, phase: Phase, universe: list[str], top_n: int = 5) -> list[tuple[str, float]]:
    """Top N tickers by phase return."""
    ranks = []
    for t in universe:
        r = phase_return(closes, t, phase)
        if r is not None:
            ranks.append((t, r))
    ranks.sort(key=lambda x: x[1], reverse=True)
    return ranks[:top_n]


def realised_vol_annual(closes: pd.DataFrame, ticker: str, start: str, end: str) -> Optional[float]:
    """Annualised realised vol of monthly log returns."""
    s = closes.get(ticker)
    if s is None:
        return None
    s = s.loc[pd.Timestamp(start):pd.Timestamp(end)].dropna()
    if len(s) < 4:
        return None
    lr = np.log(s / s.shift(1)).dropna()
    return float(lr.std() * math.sqrt(12))


def distance_from_52w_high(closes: pd.DataFrame, ticker: str, as_of: str) -> Optional[float]:
    """Distance from 52w-high (positive number = below the high)."""
    s = closes.get(ticker)
    if s is None:
        return None
    s = s.dropna()
    as_of_ts = pd.Timestamp(as_of)
    window = s.loc[as_of_ts - pd.Timedelta(days=365):as_of_ts]
    if window.empty:
        return None
    high = window.max()
    last = s.loc[:as_of_ts].iloc[-1] if not s.loc[:as_of_ts].empty else None
    if last is None or high == 0:
        return None
    return float((high - last) / high)


# ------------------------------------------------------------------- main

def main(out_dir: Path) -> int:
    out_dir.mkdir(parents=True, exist_ok=True)

    closes = pull_monthly(ALL_TICKERS, START, END)
    # Persist the close matrix for repro
    closes.to_csv(out_dir / f"monthly-closes-{TODAY}.csv")

    universe_for_ranking = MAG7 + SUPPLY_TIER2 + MEMORY_PHASE1 + OPTICAL_PHASE2 + SIPH_PHASE3 + ["BTC-USD"]

    report = {
        "as_of": datetime.now(timezone.utc).isoformat(),
        "schema_version": 1,
        "data_window": {"start": START, "end": END},
        "tickers_with_data": [t for t in ALL_TICKERS if t in closes.columns and not closes[t].dropna().empty],
        "tickers_missing_data": [t for t in ALL_TICKERS if t not in closes.columns or closes[t].dropna().empty],
        "phases": [],
    }

    # Per-phase analysis
    for phase in PHASES:
        leaders = rank_leaders(closes, phase, universe_for_ranking, top_n=10)
        idx_returns = {idx: phase_return(closes, idx, phase) for idx in INDICES}
        leader_verification = None
        if phase.leader_claim:
            actual_rank = next(
                (i + 1 for i, (t, _) in enumerate(rank_leaders(closes, phase, universe_for_ranking, top_n=999))
                 if t == phase.leader_claim),
                None,
            )
            claim_return = phase_return(closes, phase.leader_claim, phase)
            leader_verification = {
                "claimed_leader": phase.leader_claim,
                "claimed_leader_return": claim_return,
                "claimed_leader_actual_rank": actual_rank,
            }
        report["phases"].append({
            "code": phase.code,
            "name": phase.name,
            "start": phase.start,
            "end": phase.end,
            "index_returns": idx_returns,
            "top_10_leaders": [{"ticker": t, "return": r} for t, r in leaders],
            "leader_verification": leader_verification,
        })

    # Memory cycle close-up (Phase 1 of Serenity rotation)
    memory_2024_2025 = {
        t: {
            "ytd_2024": phase_return(closes, t, Phase("MEM_2024", "Memory 2024", "2024-01-01", "2024-12-31")),
            "ytd_2025": phase_return(closes, t, Phase("MEM_2025", "Memory 2025", "2025-01-01", "2025-12-31")),
            "1y_to_today": phase_return(closes, t, Phase("MEM_TRAIL", "Memory trailing", "2025-05-29", TODAY)),
        }
        for t in MEMORY_PHASE1
    }
    report["serenity_phase1_memory"] = memory_2024_2025

    # Optical (Phase 2 of Serenity rotation)
    optical_2024_2026 = {
        t: {
            "ytd_2024": phase_return(closes, t, Phase("OPT_2024", "Optical 2024", "2024-01-01", "2024-12-31")),
            "ytd_2025": phase_return(closes, t, Phase("OPT_2025", "Optical 2025", "2025-01-01", "2025-12-31")),
            "1y_to_today": phase_return(closes, t, Phase("OPT_TRAIL", "Optical trailing", "2025-05-29", TODAY)),
            "distance_from_52w_high_pct": distance_from_52w_high(closes, t, TODAY),
        }
        for t in OPTICAL_PHASE2
    }
    report["serenity_phase2_optical"] = optical_2024_2026

    # SiPh / external light source (Phase 3 — just starting)
    siph_2024_2026 = {
        t: {
            "ytd_2024": phase_return(closes, t, Phase("SIPH_2024", "SiPh 2024", "2024-01-01", "2024-12-31")),
            "ytd_2025": phase_return(closes, t, Phase("SIPH_2025", "SiPh 2025", "2025-01-01", "2025-12-31")),
            "1y_to_today": phase_return(closes, t, Phase("SIPH_TRAIL", "SiPh trailing", "2025-05-29", TODAY)),
            "distance_from_52w_high_pct": distance_from_52w_high(closes, t, TODAY),
        }
        for t in SIPH_PHASE3
    }
    report["serenity_phase3_siph"] = siph_2024_2026

    # Realised volatility per ticker (for sizing reference)
    rvol_window = {"start": "2024-01-01", "end": TODAY}
    rvol = {t: realised_vol_annual(closes, t, rvol_window["start"], rvol_window["end"]) for t in universe_for_ranking}
    report["realised_vol_24m"] = {"window": rvol_window, "annualised": rvol}

    # SPX cycle-resonance candidate check: drawdowns in P2 and P5
    report["cycle_resonance_calibration"] = {
        "p2_2022_drawdown": phase_drawdown(closes, "^GSPC", PHASES[1]),
        "p5_2025_drawdown": phase_drawdown(closes, "^GSPC", PHASES[4]),
        "p2_ndx_drawdown": phase_drawdown(closes, "^NDX", PHASES[1]),
        "p5_ndx_drawdown": phase_drawdown(closes, "^NDX", PHASES[4]),
    }

    # NVDA range check (principal: 180-220 currently)
    nvda_recent = closes.get("NVDA")
    if nvda_recent is not None:
        last3 = nvda_recent.dropna().tail(3).to_dict()
        report["nvda_recent_3_months"] = {str(k.date()): float(v) for k, v in last3.items()}

    # Persist
    out_json = out_dir / f"narrative-validation-{TODAY}.json"
    out_json.write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")
    print(f"wrote {out_json}", file=sys.stderr)
    print(f"wrote {out_dir / f'monthly-closes-{TODAY}.csv'}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main(Path("outputs")))
