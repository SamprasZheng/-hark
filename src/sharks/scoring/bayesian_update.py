"""Bayesian bottleneck posterior — an observe-first lens over the tech/ DD layer.

Formalises `tech/bayesian-bottleneck-engine.md`: turns the qualitative DD output
(verdict + confidence + milestone ladder + bubble_guard) into an explicit
posterior P(H_i = "node i is the active bottleneck") and an EDGE vs the market.

A LENS, not a new model — no new data, no dependency. OBSERVE-FIRST: the posterior
is an ANNOTATION; it must NOT enter final_fom until the priors/likelihood-ratios
are calibrated against realised milestone→outcome hit-rates (reliability/Brier,
mirroring fom-predictive-validity). Until then it is a thinking tool, watchlist-only.
"""

from __future__ import annotations

import math
from typing import Optional

# verdict → log-odds band added to the structural prior
VERDICT_BAND = {"質變": 1.0, "結構": 0.2, "過熱": -0.5, "太早": -1.0, "受損": -1.5}

_BETA0, _BETA1 = -0.5, 2.0      # prior-on-prior coefficients (calibrate later — §4)
_CLAMP = (0.05, 0.95)          # never 0/1 — the map is not the territory
_DEFAULT_LR = 3.0              # default milestone likelihood ratio
_SHRINK_K = 3.0               # correlation shrinkage λ = k/(k+n_eff)
_TAU = 40.0                   # bubble_guard → market-implied probability scale
_EDGE_MIN = 0.10             # actionable edge threshold


def _safe_sigmoid(x: float) -> float:
    x = max(-30.0, min(30.0, x))
    return 1.0 / (1.0 + math.exp(-x))


def logit(p: float) -> float:
    p = min(max(p, 1e-6), 1 - 1e-6)
    return math.log(p / (1 - p))


def _clamp(p: float) -> float:
    return min(max(p, _CLAMP[0]), _CLAMP[1])


def prior_from_rubric(rubric: dict, verdict: str, confidence: Optional[float] = None) -> float:
    """Structural prior P0(H) from the 5-axis rubric + verdict band, optionally
    blended 50/50 with the page's stated confidence. Clamped to [0.05, 0.95]."""
    rubric_sum = sum(float(rubric.get(k, 0) or 0) for k in ("A1", "A2", "A3", "A4", "A5"))
    lo = _BETA0 + _BETA1 * (rubric_sum / 10.0) + VERDICT_BAND.get(verdict, 0.0)
    p = _safe_sigmoid(lo)
    if confidence is not None:
        p = 0.5 * p + 0.5 * float(confidence)
    return _clamp(p)


def prior_from_verdict(verdict: str, confidence: Optional[float] = None) -> float:
    """Prior when only the verdict (no per-ticker rubric) is known — assumes a
    neutral rubric sum of 6/10 and applies the verdict band."""
    return prior_from_rubric({k: 1.2 for k in ("A1", "A2", "A3", "A4", "A5")}, verdict, confidence)


def milestone_logodds_update(prior: float, milestones: list[dict]) -> dict:
    """Sequential Naive-Bayes log-odds update with correlation shrinkage.

    milestones: [{status: '✅'|'⏳'|'❌', lr: float}]. ✅ adds +log(LR), ❌ adds
    −log(LR), ⏳ no change. Shrinkage λ = k/(k+n_eff) damps correlated evidence so
    a long ladder can't manufacture false certainty."""
    raw = 0.0
    n_eff = 0
    for m in milestones:
        s = {"✅": 1, "❌": -1}.get(m.get("status"), 0)
        if s == 0:
            continue
        lr = max(1.0001, float(m.get("lr", _DEFAULT_LR)))
        raw += s * math.log(lr)
        n_eff += 1
    lam = _SHRINK_K / (_SHRINK_K + n_eff) if n_eff else 1.0
    delta = lam * raw
    post = _clamp(_safe_sigmoid(logit(prior) + delta))
    return {"prior": round(prior, 4), "posterior": round(post, 4),
            "n_evidence": n_eff, "log_odds_delta": round(delta, 4)}


def edge_vs_market(posterior: float, bubble_guard: Optional[float]) -> dict:
    """edge = P_post − P_market, where P_market ≈ σ(−bubble_guard/τ): froth
    (bubble_guard ≈ −95) ⇒ market already believes ⇒ edge ≈ 0 even at high
    posterior. The formal statement of 「受益者 ≠ 該價位的股票」."""
    if bubble_guard is None:
        return {"posterior": round(posterior, 4), "market_implied": None,
                "edge": None, "actionable": None}
    p_mkt = _clamp(_safe_sigmoid(-float(bubble_guard) / _TAU))
    edge = posterior - p_mkt
    return {"posterior": round(posterior, 4), "market_implied": round(p_mkt, 4),
            "edge": round(edge, 4), "actionable": bool(edge > _EDGE_MIN)}


def _synthesize_milestones(milestone_score: float, n: int = 3) -> list[dict]:
    """Turn a 0-1 milestone_score (fraction of ladder ✅) into n pseudo-milestones."""
    n_pos = int(round(max(0.0, min(1.0, milestone_score)) * n))
    return [{"status": "✅", "lr": _DEFAULT_LR} for _ in range(n_pos)] + \
           [{"status": "⏳"} for _ in range(n - n_pos)]


def posterior_for_ticker(ticker: str, bubble_guard: Optional[float] = None,
                         milestones: Optional[list[dict]] = None) -> Optional[dict]:
    """Full observe-first read for a DD-covered ticker: prior (from verdict) →
    posterior (milestones or milestone_score) → edge (vs bubble_guard).
    Returns None if the ticker is not in the DD registry."""
    from sharks.scoring.tech_dd import TECH_DD
    dd = TECH_DD.get(ticker.upper())
    if dd is None:
        return None
    prior = prior_from_verdict(dd.verdict)
    ms = milestones if milestones is not None else _synthesize_milestones(dd.milestone_score)
    upd = milestone_logodds_update(prior, ms)
    edge = edge_vs_market(upd["posterior"], bubble_guard)
    return {"ticker": dd.ticker, "verdict": dd.verdict, "trend": dd.trend,
            "prior": upd["prior"], "posterior": upd["posterior"],
            "n_evidence": upd["n_evidence"], **{k: edge[k] for k in ("market_implied", "edge", "actionable")},
            "observe_first": True}
