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
    # Inverse index (bear hedges — leverage decay applies)
    "SBIT": {"underlying": "BTC-USD", "factor": -1, "name": "ProShares Short BTC -1x"},
    "SQQQ": {"underlying": "QQQ", "factor": -3, "name": "ProShares 3x Short QQQ"},
    "SOXS": {"underlying": "SOXX", "factor": -3, "name": "Direxion 3x Semis Bear"},
    "SPXU": {"underlying": "SPY", "factor": -3, "name": "ProShares 3x Short SP500"},
    "SDOW": {"underlying": "DIA", "factor": -3, "name": "ProShares 3x Short Dow30"},
    # VIX-futures vol products — decay is dominated by CONTANGO ROLL, not leverage
    # variance; the f·(f-1)·σ² model UNDERSTATES their bleed by a wide margin.
    # Long-vol (UVXY/UVIX) = crash insurance with brutal carry; short-vol (SVIX)
    # = carry trade that blows up in a crash (cf. XIV, Feb 2018, -96% in a day).
    "UVXY": {"underlying": "VIX", "factor": 1.5, "name": "ProShares Ultra VIX Short-Term Futures (1.5x)", "vix_futures": True},
    "UVIX": {"underlying": "VIX", "factor": 2, "name": "Volatility Shares 2x VIX Futures", "vix_futures": True},
    "VXX": {"underlying": "VIX", "factor": 1, "name": "iPath B S&P500 VIX Short-Term Futures (1x)", "vix_futures": True},
    "SVIX": {"underlying": "VIX", "factor": -1, "name": "Volatility Shares -1x VIX Futures", "vix_futures": True},
    "SVXY": {"underlying": "VIX", "factor": -0.5, "name": "ProShares Short VIX Short-Term Futures (-0.5x)", "vix_futures": True},
}

# The bear-hedge menu — products a defensive book ("也怕大空頭") can use to hedge a
# systemic drawdown. Long-vol + inverse index. These are TACTICAL crash insurance,
# never buy-and-hold: index inverse bleeds via leverage decay, VIX bleeds via
# contango roll (~5-10%/month in calm markets). Size tiny; expect to bleed in calm.
BEAR_HEDGE_TICKERS = ["SBIT", "SQQQ", "SOXS", "SPXU", "SDOW", "UVXY", "UVIX", "VXX"]
# Short-vol products are NOT hedges — they are risk-ON carry trades with tail risk.
SHORT_VOL_TICKERS = ["SVIX", "SVXY"]

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
    is_vix = spec.get("vix_futures", False)
    decay = volatility_drag(factor, annual_vol)
    abs_f = abs(factor)
    weak_underlying = underlying_fom is not None and underlying_fom < 50

    if is_vix:
        # VIX-futures products: the f·(f-1)·σ² leverage-decay model does NOT
        # capture their dominant bleed (contango roll). Branch first.
        if factor > 0:
            # long-vol: a crash hedge that bleeds carry every calm day
            verdict = "VOL-HEDGE-DECAY"
        else:
            # short-vol: a carry trade with crash tail risk — NOT a hedge
            verdict = "SHORT-VOL-TAIL-RISK"
    elif factor < 0:
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

    if is_vix:
        note = (
            "VIX-futures product: dominant bleed is CONTANGO ROLL (~5-10%/mo in "
            "calm markets), NOT the leverage-decay figure above (which understates "
            "it). Long-vol = crash insurance, size tiny, expect to bleed daily. "
            "Short-vol = carry trade with crash tail risk (cf. XIV Feb-2018 -96%)."
        )
    else:
        note = (
            "Leveraged ETFs are tactical, not buy-hold; decay compounds daily. "
            "Verdict is decay-first. Inverse funds are hedge instruments."
        )

    return {
        "ticker": ticker,
        "known": True,
        "name": spec["name"],
        "underlying": spec["underlying"],
        "factor": factor,
        "vix_futures": is_vix,
        "annual_vol_assumed": annual_vol,
        "annual_decay_pct": round(decay * 100, 1),
        "underlying_fom": underlying_fom,
        "decay_adjusted_score": adjusted,
        "verdict": verdict,
        "note": note,
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


def bear_hedge_menu(annual_vol: float = DEFAULT_ANNUAL_VOL) -> dict:
    """Defensive-hedge reference card for a book that 'also fears a big bear'
    (也怕大空頭). Lists the inverse-index + long-vol instruments available as
    *tactical* crash insurance, with their decay/carry character. NOT a
    recommendation to hold — these all bleed in calm markets; they are sized
    small and deployed only when a systemic-risk signal fires (see
    src/sharks/regime/funding_chain.py + wiki/10_defensive_hedging.md).
    """
    hedges = [score_leveraged_etf(t, annual_vol=annual_vol) for t in BEAR_HEDGE_TICKERS]
    short_vol = [score_leveraged_etf(t, annual_vol=annual_vol) for t in SHORT_VOL_TICKERS]
    return {
        "note": (
            "Bear-market hedge menu. Inverse-index funds (SQQQ/SOXS/SPXU/SDOW, "
            "-3x) bleed via leverage decay; VIX-futures (UVXY/UVIX/VXX) bleed via "
            "contango roll. Both are TACTICAL crash insurance — deploy only on a "
            "systemic-risk trigger, size ≤ a few % of NAV, expect carry bleed. "
            "SBIT (-1x BTC) is the BTC-specific hedge."
        ),
        "inverse_and_long_vol_hedges": hedges,
        "short_vol_DANGER": short_vol,
        "deploy_when": (
            "funding_chain stress = STRESS/RUPTURE, or regime = risk_off/"
            "capitulation, or a confirmed systemic catalyst — never as buy-and-hold."
        ),
        "see": ["wiki/10_defensive_hedging.md", "src/sharks/regime/funding_chain.py"],
    }
