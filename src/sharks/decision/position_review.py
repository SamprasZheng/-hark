"""Position review — the reversal-gated, performance-aware hold/rotate feedback loop.

Sits ON TOP of ``backtest/portfolio_audit``'s base verdicts. It NEVER changes a
position cap or size (``philosophy/08-risk-and-position`` stays sovereign) and it
NEVER emits an order. It only *re-labels* an EXIT / TRIM verdict into HOLD-and-trail
when the name is a strong-trending winner whose support is still intact, and it
attaches (a) the support evidence and (b) the precise condition that would flip it
back to SELL.

Why this exists (owner's ask, 2026-06-01):
    "績效非常好考慮觀察不換股,深入探索支撐數據;一旦行情真反轉再換股."
    -> let winners run; rotate only on a *real* reversal, not on a calendar or a rule.

The four principles it honours:
  1. 多頭真漲 -> hold (``philosophy/03-long-short-taxonomy``). A winner with intact
     support is held, not churned. Rotation requires a real reversal.
  2. Leverage discipline is NOT removed (constitution / 08: no leverage in the alpha
     sleeve). A leveraged WINNER is de-risked via a TRAILING / staged exit instead of
     a dump-at-open — it still must exit, just not in a panic. Toggle with
     ``leveraged_exit_mode`` ("trailing" default | "immediate" = strict dump).
  3. Performance gate: when the sleeve is performing strongly, widen the hold
     hysteresis (deeper deterioration required before rotating) — 績效好就觀察不換股.
  4. Recommend-only: a verdict + evidence, never a trade.

All inputs are plain numbers so the logic unit-tests offline with no network and no
FOM recompute (the audit already produced the FOM breakdown; we reuse it).

FOM-unit conventions (from ``scoring/fom``):
  * momentum  : 0..100   (trend strength; >= strong_mom == still 真漲)
  * bubble    : -100..100 (bubble_guard; very negative == overheated / late-cycle)
  * recent_return : a fraction over a recent window (e.g. 0.12 == +12%), or None.
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Optional


# ─── Tunable knobs (the "parameters" — kept here so they are one obvious place) ──
DEFAULTS: dict = {
    "strong_mom": 60.0,        # momentum at/above this == strong uptrend (still 真漲)
    "weak_mom": 40.0,          # momentum at/below this == fading trend
    "bubble_extreme": -50.0,   # bubble_guard at/below this == overheated late-cycle
    "rollover_drawdown": -0.10,  # recent_return at/below this (with fading mom) == rollover
    "broken_drawdown": -0.20,  # recent_return at/below this == real breakdown
    "strong_return": 0.25,     # recent_return at/above this == a winner-to-hold EVEN IF the
                               # (lagging) FOM momentum score is < strong_mom. Owner choice
                               # 2026-06-01: hold recent rippers, don't churn them.
    "trail_stop_pct": 0.12,    # trailing-stop distance for a held winner (12% off high)
    "trail_stop_pct_leveraged": 0.08,  # tighter trail for a leveraged winner (decay risk)
    "leveraged_trim_now_pct": 0.34,    # de-risk slice taken immediately on a leveraged winner
    # performance-gate widening: when the sleeve is strong, lower the bar to "hold"
    "perf_gate_strong_mom_relief": 10.0,   # strong_mom 60 -> 50 when sleeve is strong
    "perf_gate_weak_mom_tighten": 10.0,    # weak_mom 40 -> 50 when sleeve is weak
    "perf_gate_strong_return_relief": 0.05,  # strong_return 0.25 -> 0.20 when sleeve is strong
    # sleeve-performance classification (median final_fom across cash holdings)
    "sleeve_strong_fom": 55.0,
    "sleeve_weak_fom": 40.0,
}

# Trend states
STRONG = "strong_uptrend"
INTACT = "intact"
ROLLOVER = "rollover"
BROKEN = "broken"

# Reviewed verdicts (base verdicts come from portfolio_audit: SELL* / TRIM* / HOLD* / ADD*)
V_HOLD_TRAIL = "HOLD-TRAIL"        # let the winner run behind a trailing stop
V_TRIM_TRAIL = "TRIM-PARTIAL+TRAIL"  # leveraged winner: de-risk a slice now, trail the rest
V_SELL = "SELL"
V_TRIM = "TRIM"
V_HOLD = "HOLD"


def _is_exit(verdict: str) -> bool:
    return verdict.upper().startswith("SELL")


def _is_trim(verdict: str) -> bool:
    return "TRIM" in verdict.upper()


def classify_trend(
    momentum: Optional[float],
    bubble: Optional[float],
    recent_return: Optional[float] = None,
    *,
    strong_mom: float = DEFAULTS["strong_mom"],
    weak_mom: float = DEFAULTS["weak_mom"],
    strong_return: float = DEFAULTS["strong_return"],
    bubble_extreme: float = DEFAULTS["bubble_extreme"],
    rollover_drawdown: float = DEFAULTS["rollover_drawdown"],
    broken_drawdown: float = DEFAULTS["broken_drawdown"],
) -> str:
    """Reduce the FOM dims (+ optional recent return) to one of four trend states.

    The whole point: separate "still 真漲 (hold the winner)" from "really reversing
    (rotate)". A name keeps its SELL only when it is rolling over or broken. A name
    counts as a winner-to-hold when its momentum score is strong OR it has a clear
    recent up-run (``strong_return``) — so a recent ripper with a lagging momentum
    score is still held, not churned.
    """
    rr = recent_return
    # Real breakdown: a deep recent drawdown OR overheated-and-now-falling.
    if rr is not None and rr <= broken_drawdown:
        return BROKEN
    if bubble is not None and bubble <= bubble_extreme and rr is not None and rr < 0:
        return BROKEN
    # Overheated late-cycle with no confirming up-move yet -> reversal risk (rollover).
    if bubble is not None and bubble <= bubble_extreme and (rr is None or rr <= 0):
        return ROLLOVER
    # Fading trend confirmed by a recent down-move -> rollover.
    if momentum is not None and momentum < strong_mom and rr is not None and rr <= rollover_drawdown:
        return ROLLOVER
    if momentum is not None and momentum <= weak_mom and rr is not None and rr < 0:
        return ROLLOVER
    # Winner-to-hold: strong momentum score (not contradicted by a down-move) ...
    if momentum is not None and momentum >= strong_mom and (rr is None or rr >= 0):
        return STRONG
    # ... OR a clear recent up-run even when the (lagging) momentum score is weak.
    if rr is not None and rr >= strong_return:
        return STRONG
    return INTACT


def sleeve_performance(
    final_foms: list,
    *,
    strong_fom: float = DEFAULTS["sleeve_strong_fom"],
    weak_fom: float = DEFAULTS["sleeve_weak_fom"],
) -> str:
    """Classify the sleeve as strong / normal / weak from the median holding FOM.

    Drives the performance gate: a strong sleeve widens the hold band (don't churn a
    book that is working); a weak sleeve tightens it (cut faster)."""
    vals = sorted(v for v in final_foms if v is not None)
    if not vals:
        return "normal"
    mid = vals[len(vals) // 2] if len(vals) % 2 else (vals[len(vals) // 2 - 1] + vals[len(vals) // 2]) / 2
    if mid >= strong_fom:
        return "strong"
    if mid <= weak_fom:
        return "weak"
    return "normal"


@dataclass
class ReviewedVerdict:
    ticker: str
    base_verdict: str
    reviewed_verdict: str
    changed: bool
    trend: str
    trailing_stop_pct: Optional[float]
    support: dict
    flips_to_sell_when: str
    why: str
    notes: list = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)


def review_position(
    *,
    ticker: str,
    base_verdict: str,
    category: str = "cash_equity",          # cash_equity | leveraged_etf | speculative
    fom_breakdown: Optional[dict] = None,
    trend_momentum: Optional[float] = None,  # for leveraged_etf pass the UNDERLYING momentum
    trend_bubble: Optional[float] = None,
    recent_return: Optional[float] = None,   # recent window return of the name (or underlying)
    leveraged_of: Optional[str] = None,
    perf_gate: str = "normal",               # strong | normal | weak (from sleeve_performance)
    leveraged_exit_mode: str = "trailing",   # trailing (default) | immediate (strict dump)
    cfg: Optional[dict] = None,
) -> ReviewedVerdict:
    """Apply the reversal gate + leverage policy + performance gate to ONE holding.

    Returns the (possibly unchanged) verdict plus the support evidence and the exact
    condition that flips it back to SELL — the "deepen the support data" the owner
    asked for. Never raises; missing inputs degrade to a conservative passthrough.
    """
    cfg = {**DEFAULTS, **(cfg or {})}
    bd = fom_breakdown or {}
    momentum = trend_momentum if trend_momentum is not None else bd.get("momentum")
    bubble = trend_bubble if trend_bubble is not None else bd.get("bubble_guard")

    # ── performance gate: widen/tighten the trend thresholds ────────────────────
    strong_mom = cfg["strong_mom"]
    weak_mom = cfg["weak_mom"]
    strong_return = cfg["strong_return"]
    if perf_gate == "strong":
        strong_mom -= cfg["perf_gate_strong_mom_relief"]   # easier to qualify as a winner-to-hold
        strong_return -= cfg["perf_gate_strong_return_relief"]
    elif perf_gate == "weak":
        weak_mom += cfg["perf_gate_weak_mom_tighten"]       # quicker to call a rollover

    trend = classify_trend(
        momentum, bubble, recent_return,
        strong_mom=strong_mom, weak_mom=weak_mom, strong_return=strong_return,
        bubble_extreme=cfg["bubble_extreme"],
        rollover_drawdown=cfg["rollover_drawdown"],
        broken_drawdown=cfg["broken_drawdown"],
    )

    support = {
        "momentum": momentum, "bubble_guard": bubble,
        "recent_return": recent_return,
        "final_fom": bd.get("final_fom"),
        "contrarian": bd.get("contrarian"), "quality": bd.get("quality"),
        "trend": trend, "perf_gate": perf_gate,
    }
    rr_txt = f"{recent_return:+.0%}" if recent_return is not None else "n/a"
    mom_txt = f"{momentum:.0f}" if momentum is not None else "n/a"

    # ── non-exit base verdicts pass through (but still carry evidence) ──────────
    if not (_is_exit(base_verdict) or _is_trim(base_verdict)):
        return ReviewedVerdict(
            ticker, base_verdict, base_verdict, False, trend, None, support,
            flips_to_sell_when="n/a (not an exit candidate)",
            why=f"base={base_verdict}; trend={trend} (mom {mom_txt}, ret {rr_txt}) — kept",
        )

    flip = (f"momentum<{weak_mom:.0f} OR recent_return<={cfg['rollover_drawdown']:+.0%} "
            f"OR bubble_guard<={cfg['bubble_extreme']:.0f} OR close<trailing-stop")

    # ── leveraged ETF: de-risk ALWAYS, but trail a ripping winner instead of dump ─
    if category == "leveraged_etf":
        if leveraged_exit_mode == "trailing" and trend == STRONG:
            return ReviewedVerdict(
                ticker, base_verdict, V_TRIM_TRAIL, True, trend,
                cfg["trail_stop_pct_leveraged"], support,
                flips_to_sell_when=f"underlying rolls over ({flip})",
                why=(f"槓桿仍要降(constitution: alpha sleeve 不留槓桿),但標的 {leveraged_of or '?'} "
                     f"真漲(mom {mom_txt}, ret {rr_txt}) → 立刻去風險 {cfg['leveraged_trim_now_pct']:.0%}、"
                     f"其餘掛 {cfg['trail_stop_pct_leveraged']:.0%} 移動停利,不開盤倒;rollover 立即清。"),
                notes=["leverage de-risk preserved as trailing, not removed"],
            )
        return ReviewedVerdict(
            ticker, base_verdict, V_SELL, _is_trim(base_verdict), trend, None, support,
            flips_to_sell_when="n/a (selling now)",
            why=(f"槓桿 + 標的 {leveraged_of or '?'} {trend}(mom {mom_txt}, ret {rr_txt}) → "
                 f"decay 會吃掉利潤,照紀律出。"),
            notes=["leveraged_exit_mode=immediate" if leveraged_exit_mode != "trailing" else "no strong uptrend"],
        )

    # ── cash equity: hold the winner, sell only on a real reversal ──────────────
    if trend == STRONG:
        return ReviewedVerdict(
            ticker, base_verdict, V_HOLD_TRAIL, True, trend, cfg["trail_stop_pct"], support,
            flips_to_sell_when=flip,
            why=(f"多頭真漲且支撐完好(mom {mom_txt}, ret {rr_txt}, FOM {bd.get('final_fom')}) → "
                 f"抱住、改掛 {cfg['trail_stop_pct']:.0%} 移動停利,不在強勢中換掉贏家。"),
            notes=["winner held; base exit overridden until real reversal"],
        )
    if trend in (ROLLOVER, BROKEN):
        return ReviewedVerdict(
            ticker, base_verdict, V_SELL, False, trend, None, support,
            flips_to_sell_when="n/a (selling now)",
            why=f"趨勢{('破線' if trend == BROKEN else '轉弱')}(mom {mom_txt}, ret {rr_txt}) → 真反轉,照原訊號出。",
        )
    # intact / neutral: soften a hard SELL to TRIM (don't dump a non-reversing name),
    # keep an existing TRIM as-is.
    if _is_exit(base_verdict):
        return ReviewedVerdict(
            ticker, base_verdict, V_TRIM, True, trend, None, support,
            flips_to_sell_when=flip,
            why=f"中性(mom {mom_txt}, ret {rr_txt})、未見真反轉 → 由 SELL 降為部分減碼,留觀察。",
            notes=["no reversal yet; hard SELL softened to TRIM"],
        )
    return ReviewedVerdict(
        ticker, base_verdict, V_TRIM, False, trend, None, support,
        flips_to_sell_when=flip,
        why=f"維持原減碼(mom {mom_txt}, ret {rr_txt});未達真反轉門檻。",
    )
