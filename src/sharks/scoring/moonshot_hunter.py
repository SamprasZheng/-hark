"""飆股獵手 — Moonshot Hunter, the DELIBERATE OPPOSITE of FOM.

FOM (`fom.py`) scores the **core sleeve**: quality + momentum names you hold for
3–6 months. Its `bubble_guard` dimension PENALISES parabolas — a name up +200% in
six months gets −50, because for a core position that is late-cycle bubble stress.

This module scores the **ring-fenced high-variance sleeve** — the tiny, sized-to-
zero-out book whose entire job is to catch a 飆股: the BKNG +343% / TSLA +743% type
multi-bagger. To do that it must take the EXACT INVERSE stance of FOM:

    FOM bubble_guard:   parabola → PUNISH (it is risk to a core holding)
    moonshot hype:      parabola → REWARD (it is the whole point of the sleeve)

Hunting moonshots without discipline is just gambling — and gambling is precisely
how the principal's 複委託 graveyard (the dead account of chased hype) happened. So
the discipline here is NOT a quality filter (that would defeat the purpose); it is
an **evidence gate**. The five criteria the principal listed split cleanly:

  PRICE-COMPUTABLE (necessary, never sufficient):
    1. 交易量  volume surge / unusual volume   → volume_surge_score
    2. 炒作層面 hype / momentum-acceleration    → hype_score
  QUALITATIVE EVIDENCE (the catalyst that separates a moonshot from a pump):
    3. INSIDER TRADING   內部人買進        → evidence "insider_buying"
    4. 巨頭合作  big-tech partnership      → evidence "bigtech_partnership"
    5. 打入巨頭供應鏈 supply-chain design-win → evidence "supply_chain_design_win"

A name that lights up on price/hype alone with ZERO confirmed catalyst is flagged
PURE-HYPE-NO-EVIDENCE — the warning that says "this is the graveyard pattern, do
NOT size into it". A name with the same hype PLUS ≥1 confirmed A/B-grade catalyst
is an EVIDENCE-BACKED-MOONSHOT. The price score tells you WHEN; the evidence gate
tells you WHETHER you are allowed to act. That gate is the entire difference
between a disciplined moonshot and a lottery ticket.

Evidence grading mirrors `daily_health_check.CONFIRMING_GRADES = {"A","B"}`: only
A/B-grade sourcing counts as confirmed; a rumour (C–E) does not clear the gate.

Pure logic, no network in the scoring functions — price series and evidence are
passed in, so every function is unit-testable. Leveraged long ETFs (TSLL/SOXL/…)
are a legitimate moonshot-sleeve instrument; we reuse `leveraged_etf.is_leveraged_etf`
to TAG them, and do NOT re-implement decay (that lives in `leveraged_etf.py`).

This module RECOMMENDS; it never trades.
"""

from __future__ import annotations

import math
from typing import Optional

import numpy as np
import pandas as pd

from sharks.scoring.leveraged_etf import LEVERAGED_ETF_REGISTRY, is_leveraged_etf

# The qualitative catalysts the principal listed (criteria 3–5). These are the
# evidence kinds that separate a disciplined moonshot from chasing a pump.
EVIDENCE_KINDS = {"insider_buying", "bigtech_partnership", "supply_chain_design_win"}

# Only A/B-grade sourcing clears the gate — same convention as
# daily_health_check.CONFIRMING_GRADES. A rumour / social post (C–E) is NOT
# confirmation; absence of grade defaults to UNCONFIRMED.
CONFIRMING_GRADES = frozenset({"A", "B"})

# A price/hype reading at or above this is "hot enough to be dangerous" — hot
# enough that holding it without a confirmed catalyst is the graveyard pattern.
HOT_THRESHOLD = 60.0


def volume_surge_score(volumes: pd.Series, as_of) -> float:
    """0..100 — how UNUSUAL recent volume is vs its own trailing baseline (交易量).

    Ratio of recent average volume (last ~5 bars / 1 month) to a trailing
    baseline (~60 bars / 12 months). A 飆股 ignites on a volume expansion — money
    showing up — so higher ratio → higher score. Mapped log-style so a 1x ratio
    is ~0, ~3x is ~50, and ~10x+ saturates near 100.
    """
    if volumes is None:
        return 0.0
    v = volumes.dropna()
    v = v.loc[:as_of]
    if len(v) < 6:
        return 0.0
    recent_n = min(5, max(1, len(v) // 6))
    recent = float(v.iloc[-recent_n:].mean())
    baseline = float(v.iloc[:-recent_n].tail(60).mean()) if len(v) > recent_n else 0.0
    if baseline <= 0 or recent <= 0:
        return 0.0
    ratio = recent / baseline
    # log2 mapping: ratio 1x→0, 2x→~30, ~3.2x→~50, ~10x→~100. Capped at [0,100].
    score = 30.0 * math.log2(max(ratio, 1e-9))
    return float(max(0.0, min(100.0, score)))


def hype_score(closes: pd.Series, as_of) -> float:
    """0..100 — short-horizon momentum ACCELERATION + range/vol EXPANSION (炒作層面).

    INTENTIONALLY THE INVERSE STANCE of FOM's `bubble_guard`. Where bubble_guard
    sees a parabola and subtracts up to −50 (late-cycle stress for a core hold),
    this REWARDS the parabola: a moonshot is a name going vertical, and the high-
    variance sleeve exists precisely to ride that, accepting the crash risk that
    comes with it. We are not trying to avoid the bubble — we are trying to be
    early IN it, with an evidence catalyst and a tiny position as the only brakes.

    Components (all bullish-vertical):
      - recent return acceleration: short return (≈1m) running hot vs medium (≈3m)
      - raw short-horizon return magnitude (the parabola itself)
      - range / realised-vol EXPANSION vs a calmer trailing window (energy)
    """
    if closes is None:
        return 0.0
    s = closes.dropna()
    s = s.loc[:as_of]
    if len(s) < 8:
        return 0.0
    last = float(s.iloc[-1])
    r6 = last / float(s.iloc[-7]) - 1.0 if len(s) > 6 else 0.0
    # Two consecutive 3-bar legs, to measure ACCELERATION (the 2nd derivative):
    # the recent leg's return vs the immediately-prior leg's return.
    recent_leg = last / float(s.iloc[-4]) - 1.0 if len(s) > 3 else 0.0
    prior_leg = float(s.iloc[-4]) / float(s.iloc[-7]) - 1.0 if len(s) > 6 else 0.0

    score = 0.0
    # 1) Raw parabola — the bigger the recent run, the better (opposite of bubble_guard).
    if r6 > 2.0:        # +200% in ~6 bars → going vertical
        score += 45
    elif r6 > 1.0:
        score += 32
    elif r6 > 0.5:
        score += 20
    elif r6 > 0.2:
        score += 10
    # 2) Acceleration — the recent leg running hotter than the prior leg (curve
    #    bending UP). This is what makes a parabola, vs a steady linear trend.
    accel = recent_leg - prior_leg
    if accel > 0.30:
        score += 25
    elif accel > 0.10:
        score += 15
    elif accel > 0.0:
        score += 7
    # 3) Range / realised-vol EXPANSION — moonshots widen their daily range. Compare
    #    the recent window's realised vol to the CALM trailing baseline (the quiet
    #    accumulation before ignition), not the transition bars.
    rets = s.pct_change().dropna()
    if len(rets) >= 12:
        recent_vol = float(rets.iloc[-5:].std())
        base_vol = float(rets.iloc[:-5].std())
        if base_vol > 0:
            expansion = recent_vol / base_vol
            if expansion > 2.0:
                score += 30
            elif expansion > 1.3:
                score += 18
            elif expansion > 1.0:
                score += 8
    return float(max(0.0, min(100.0, score)))


def evidence_score(evidence: Optional[dict]) -> dict:
    """Score the qualitative catalysts (criteria 3–5: insider / partnership / supply-chain).

    Args:
        evidence: {kind: {"confirmed": bool, "grade": "A".."E", "note": str}} for
                  kinds in EVIDENCE_KINDS. Unknown kinds are ignored; missing kinds
                  default to UNCONFIRMED (absence of evidence is not evidence).

    A kind counts as confirmed ONLY when confirmed=True AND grade in {"A","B"} —
    the same A/B bar as daily_health_check. A rumour (grade C–E) does NOT count,
    even if someone flagged confirmed=True; the grade is the backstop.

    Returns {n_confirmed, confirmed_kinds, evidence_points} where evidence_points
    (0..100) rewards each confirmed catalyst — the disciplined-vs-gamble signal.
    """
    evidence = evidence or {}
    confirmed: list[str] = []
    for kind in EVIDENCE_KINDS:
        e = evidence.get(kind) or {}
        if bool(e.get("confirmed")) and e.get("grade", "E") in CONFIRMING_GRADES:
            confirmed.append(kind)
    n = len(confirmed)
    # First confirmed catalyst is worth the most (it is what flips the warning);
    # additional independent catalysts stack but with diminishing weight.
    points_ladder = {0: 0.0, 1: 60.0, 2: 85.0, 3: 100.0}
    evidence_points = points_ladder.get(n, 100.0)
    return {
        "n_confirmed": n,
        "confirmed_kinds": sorted(confirmed),
        "evidence_points": evidence_points,
    }


def _instrument_tag(ticker: str) -> str:
    """Tag leveraged LONG ETFs (factor > 0) — a legit moonshot-sleeve instrument.
    Inverse/short funds are hedges, not moonshots, so they keep the equity tag."""
    if is_leveraged_etf(ticker):
        spec = LEVERAGED_ETF_REGISTRY.get(ticker, {})
        if spec.get("factor", 0) > 0:
            return "leveraged_etf"
    return "equity"


def moonshot_score(
    closes: pd.Series,
    volumes: pd.Series,
    as_of,
    evidence: Optional[dict] = None,
    ticker: str = "",
) -> dict:
    """Blend volume-surge + hype + evidence into a 0..100 moonshot score + conviction.

    Price weight 60% (volume 25% + hype 35%) sets the "is it moving" floor;
    evidence weight 40% is what earns the right to ACT on the move.

    CRITICAL DISCIPLINE — the pure-hype warning:
      A HOT price/hype reading (≥ HOT_THRESHOLD) with ZERO confirmed A/B evidence
      is flagged "PURE-HYPE-NO-EVIDENCE". This is the 複委託-graveyard pattern:
      chasing a parabola with no catalyst. The flag is a WARNING, not a buy — the
      sleeve's discipline is to either find the catalyst or stand aside.
      The same hot reading WITH ≥1 confirmed catalyst is "EVIDENCE-BACKED-MOONSHOT".
    Other tiers: "WATCH" (moderate heat / partial signal), "AVOID" (low everything).
    """
    vol = volume_surge_score(volumes, as_of)
    hype = hype_score(closes, as_of)
    ev = evidence_score(evidence)

    price_heat = 0.25 / 0.60 * vol + 0.35 / 0.60 * hype  # weighted avg of the two
    score = 0.25 * vol + 0.35 * hype + 0.40 * ev["evidence_points"]
    score = float(max(0.0, min(100.0, score)))

    hot = price_heat >= HOT_THRESHOLD
    has_evidence = ev["n_confirmed"] >= 1

    if hot and has_evidence:
        conviction = "EVIDENCE-BACKED-MOONSHOT"
    elif hot and not has_evidence:
        # The graveyard pattern: vertical price, no catalyst. WARN, do not chase.
        conviction = "PURE-HYPE-NO-EVIDENCE"
    elif price_heat >= 35.0 or has_evidence:
        conviction = "WATCH"
    else:
        conviction = "AVOID"

    pure_hype_warning = conviction == "PURE-HYPE-NO-EVIDENCE"
    return {
        "ticker": ticker,
        "instrument": _instrument_tag(ticker) if ticker else "equity",
        "moonshot_score": round(score, 1),
        "volume_surge": round(vol, 1),
        "hype": round(hype, 1),
        "price_heat": round(price_heat, 1),
        "evidence_points": ev["evidence_points"],
        "n_confirmed_evidence": ev["n_confirmed"],
        "confirmed_kinds": ev["confirmed_kinds"],
        "conviction": conviction,
        "pure_hype_warning": pure_hype_warning,
        "note": (
            "PURE-HYPE-NO-EVIDENCE: hot price with no confirmed catalyst — this is "
            "the 複委託-graveyard pattern. Find the insider/partnership/supply-chain "
            "evidence or stand aside; do NOT chase."
            if pure_hype_warning else
            "Moonshot sleeve is ring-fenced & tiny. Price tells you WHEN; the "
            "evidence gate tells you WHETHER you may act. RECOMMEND-ONLY."
        ),
    }


def rank_moonshots(
    closes_df: pd.DataFrame,
    volumes_df: pd.DataFrame,
    as_of,
    evidence_by_ticker: Optional[dict] = None,
) -> list[dict]:
    """Score a universe and rank by moonshot_score (descending).

    Args:
        closes_df / volumes_df: columns are tickers, index is time.
        evidence_by_ticker: {ticker: evidence_dict} (see evidence_score). Missing
                            tickers default to no evidence → eligible for the
                            pure-hype warning if their price runs hot.
    """
    evidence_by_ticker = evidence_by_ticker or {}
    out: list[dict] = []
    for ticker in closes_df.columns:
        vols = volumes_df.get(ticker) if volumes_df is not None else None
        res = moonshot_score(
            closes_df[ticker], vols, as_of,
            evidence=evidence_by_ticker.get(ticker), ticker=ticker,
        )
        out.append(res)
    out.sort(key=lambda r: r["moonshot_score"], reverse=True)
    return out
