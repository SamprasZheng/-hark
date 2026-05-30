"""Leveraged / inverse ETF scorer — decay-aware (2x / 3x / 5x / -1x).

The plain FOM momentum scorer (`fom.py`) deliberately skips daily-rebalanced
leveraged single-stock and index ETFs because their price path is dominated by
**volatility drag**, not by the underlying's trend. This module scores them on
their own terms so the principal's P1 book (≈ 28 of 32 positions are leveraged
ETFs) is no longer an audit blind spot.

Core physics — for a daily-rebalanced fund tracking factor `f` of an underlying
with annualised volatility `σ`, the expected geometric return is roughly:

    f · μ_underlying  −  0.5 · f · (f − 1) · σ²          (annualised)

The second term is the **decay / drag**: it is positive (a drag) for any
|f| > 1, grows with f², and grows with variance. At f=2, σ=40% → ~16%/yr; at
f=3, σ=40% → ~48%/yr; at f=5, σ=40% → ~160%/yr (mathematically — such products
usually reset or get wiped first). This is why leveraged ETFs are tactical
instruments, never buy-and-hold.

Pure logic, no network: callers pass the underlying's FOM (optional) and an
annualised volatility estimate. Verdicts are decay-first, underlying-FOM-second.
"""

from __future__ import annotations

from typing import Optional

# ticker -> {underlying, factor, name}. factor negative = inverse.
# Seeded from the principal's P1 holdings + common index leverage ladder.
# Extend freely; unknown tickers fall through to a generic message.
LEVERAGED_ETF_REGISTRY: dict[str, dict] = {
    # Principal P1 single-stock 2x
    "TARK": {"underlying": "ARKK", "factor": 2, "name": "Tradr 2x ARKK"},
    "ORCX": {"underlying": "ORCL", "factor": 2, "name": "2x ORCL Daily"},
    "AAPB": {"underlying": "AAPL", "factor": 2, "name": "GraniteShares 2x AAPL"},
    "NOWL": {"underlying": "NOW", "factor": 2, "name": "2x NOW Daily"},
    "SMCL": {"underlying": "SMCI", "factor": 2, "name": "2x SMCI Daily"},
    "LULG": {"underlying": "LULU", "factor": 2, "name": "2x LULU Daily"},
    "QBTX": {"underlying": "QTUM", "factor": 2, "name": "2x Quantum Daily"},
    "QUBX": {"underlying": "QUBT", "factor": 2, "name": "2x QUBT Daily"},
    "RGTX": {"underlying": "RGTI", "factor": 2, "name": "2x RGTI Daily"},
    "RBLU": {"underlying": "RBLX", "factor": 2, "name": "2x RBLX Daily"},
    "OKLL": {"underlying": "OKLO", "factor": 2, "name": "2x OKLO Daily"},
    "CRWG": {"underlying": "CRWV", "factor": 2, "name": "Leverage Shares 2x CRWV"},
    # 3x index
    "LABU": {"underlying": "XBI", "factor": 3, "name": "Direxion 3x Biotech Bull"},
    "TQQQ": {"underlying": "QQQ", "factor": 3, "name": "ProShares 3x QQQ"},
    "SOXL": {"underlying": "SOXX", "factor": 3, "name": "Direxion 3x Semis Bull"},
    "SPXL": {"underlying": "SPY", "factor": 3, "name": "Direxion 3x SP500 Bull"},
    "FNGU": {"underlying": "NYFANG", "factor": 3, "name": "MicroSectors 3x FANG+"},
    # 5x (rare; Leverage Shares / European-style)
    "5QQQ": {"underlying": "QQQ", "factor": 5, "name": "Leverage Shares 5x QQQ"},
    # Inverse
    "SBIT": {"underlying": "BTC-USD", "factor": -1, "name": "ProShares Short BTC -1x"},
    "SQQQ": {"underlying": "QQQ", "factor": -3, "name": "ProShares 3x Short QQQ"},
}

# Default annualised vol when the caller has no estimate (single-stock leverage
# underlyings are high-vol; 0.45 is a conservative single-stock placeholder).
DEFAULT_ANNUAL_VOL = 0.45


def volatility_drag(factor: int, annual_vol: float) -> float:
    """Annualised decay fraction from daily rebalancing: 0.5·f·(f−1)·σ².
    Works for inverse factors too (f=-1 → σ²). Returns a positive drag."""
    return 0.5 * factor * (factor - 1) * (annual_vol ** 2)


def is_leveraged_etf(ticker: str) -> bool:
    return ticker in LEVERAGED_ETF_REGISTRY


def score_leveraged_etf(
    ticker: str,
    underlying_fom: Optional[float] = None,
    annual_vol: float = DEFAULT_ANNUAL_VOL,
) -> dict:
    """Decay-first verdict for a leveraged/inverse ETF.

    Verdict ladder (decay-first, underlying-FOM-second):
      - |factor| >= 5  → "AVOID" (decay regime makes buy-hold irrational)
      - decay >= 0.30  → "TACTICAL-ONLY-or-SELL" (SELL if underlying weak)
      - |factor| == 3  → "TACTICAL-ONLY" (short-hold only)
      - else (2x)      → "TRIM-or-TACTICAL" (TRIM if underlying weak)
    Inverse funds get an "INVERSE-HEDGE" tag (held as a hedge, different logic).
    """
    spec = LEVERAGED_ETF_REGISTRY.get(ticker)
    if spec is None:
        return {"ticker": ticker, "known": False,
                "note": "not in LEVERAGED_ETF_REGISTRY — add mapping to score"}

    factor = spec["factor"]
    decay = volatility_drag(factor, annual_vol)
    abs_f = abs(factor)
    weak_underlying = underlying_fom is not None and underlying_fom < 50

    if factor < 0:
        verdict = "INVERSE-HEDGE"
    elif abs_f >= 5:
        verdict = "AVOID"
    elif decay >= 0.30:
        verdict = "SELL" if weak_underlying else "TACTICAL-ONLY"
    elif abs_f == 3:
        verdict = "TACTICAL-ONLY"
    else:  # 2x
        verdict = "TRIM" if weak_underlying else "TACTICAL-OK"

    # A rough "decay-adjusted" attractiveness: start from the underlying FOM and
    # subtract a penalty scaled by annual decay (capped) — for ranking only.
    if underlying_fom is not None:
        penalty = min(decay, 0.5) * 60  # up to -30 pts at 50%+ annual decay
        adjusted = round(max(0.0, underlying_fom - penalty), 1)
    else:
        adjusted = None

    return {
        "ticker": ticker,
        "known": True,
        "name": spec["name"],
        "underlying": spec["underlying"],
        "factor": factor,
        "annual_vol_assumed": annual_vol,
        "annual_decay_pct": round(decay * 100, 1),
        "underlying_fom": underlying_fom,
        "decay_adjusted_score": adjusted,
        "verdict": verdict,
        "note": (
            "Leveraged ETFs are tactical, not buy-hold; decay compounds daily. "
            "Verdict is decay-first. Inverse funds are hedge instruments."
        ),
    }


def audit_leveraged_holdings(
    holdings: dict[str, float],
    underlying_foms: Optional[dict[str, float]] = None,
    vols: Optional[dict[str, float]] = None,
) -> list[dict]:
    """Score a dict of {ticker: weight_or_value}. Only known leveraged ETFs are
    scored; the rest are skipped. Returns the per-ETF verdicts, sorted by annual
    decay descending (worst-decay first)."""
    underlying_foms = underlying_foms or {}
    vols = vols or {}
    out: list[dict] = []
    for ticker in holdings:
        if not is_leveraged_etf(ticker):
            continue
        spec = LEVERAGED_ETF_REGISTRY[ticker]
        fom = underlying_foms.get(spec["underlying"])
        vol = vols.get(ticker, DEFAULT_ANNUAL_VOL)
        out.append(score_leveraged_etf(ticker, underlying_fom=fom, annual_vol=vol))
    out.sort(key=lambda r: r["annual_decay_pct"], reverse=True)
    return out
