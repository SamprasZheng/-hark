"""Regime-conditioned valuation — dynamic target prices by environment.

The principal wants a valuation system that gives DIFFERENT target prices under
different market environments (積極樂觀 / 寬鬆 / 中性 / 保守 / 悲觀恐慌), an estimated
return, a backtest of accuracy, and week/month/quarter horizons — to make
"arbitrage" (price vs fair-value gap) intuitive.

Method (v1):
  target_price(regime) = interpolate within the analyst [low, mean, high] band by
  the regime's band-position (積極樂觀 → near high, 悲觀恐慌 → near low). Fallback
  when no analyst band: forward EPS × trailing P/E × regime factor (P/E reversion).
  upside = target/price − 1; horizon return = upside × convergence(horizon).

Environment is read from regime/classifier.classify_regime (real breadth/liquidity
/SPX data) mapped to the 5 labels; variables/20260531.md is the qualitative micro
overlay; a manual override is supported.

HONESTY (考證): full per-stock fundamental-multiple calibration needs a fundamentals
data vendor (yfinance gives only CURRENT multiples + analyst targets, not history).
So v1 (a) uses live analyst bands for the per-stock target, and (b) calibrates the
REGIME dimension — do forward returns actually differ by environment — with a
price-based backtest. Observe-first / watchlist-only; not buy/sell advice.
"""

from __future__ import annotations

from typing import Optional

import numpy as np
import pandas as pd

# ─── The 5 environments (ordered risk-on → risk-off) ───────────────────────────
# band_position: where the target sits in the analyst [low→high] band (1.0=high).
# pe_factor: multiplier on trailing P/E for the no-analyst-band fallback.
ENVIRONMENT_REGIMES: dict[str, dict] = {
    # tilt: position relative to the analyst MEAN (consensus fair value). +1 → toward
    # the high target, −1 → toward the low. 中性 = the consensus mean itself.
    "積極樂觀": {"tilt": 0.80, "pe_factor": 1.20, "desc": "aggressive/optimistic — toward analyst highs"},
    "寬鬆":     {"tilt": 0.40, "pe_factor": 1.08, "desc": "easing/liquidity-supported — above mean"},
    "中性":     {"tilt": 0.00, "pe_factor": 1.00, "desc": "neutral — analyst consensus mean"},
    "保守":     {"tilt": -0.40, "pe_factor": 0.88, "desc": "conservative — below mean"},
    "悲觀恐慌": {"tilt": -0.80, "pe_factor": 0.72, "desc": "panic — toward analyst lows / trough"},
}
ENV_ORDER = ["積極樂觀", "寬鬆", "中性", "保守", "悲觀恐慌"]

# regime/classifier label → environment
CLASSIFIER_TO_ENV = {
    "bull_trend": "積極樂觀", "late_bull": "寬鬆", "neutral": "中性",
    "risk_off": "保守", "capitulation": "悲觀恐慌",
}

# fraction of the price→target gap that historically closes per holding horizon
# (v1 ASSUMPTION — to be re-calibrated from the backtest; intentionally modest).
HORIZON_CONVERGENCE = {"week": 0.05, "month": 0.15, "quarter": 0.35}


def current_environment(override: Optional[str] = None) -> dict:
    """The current environment (one of the 5). Uses regime/classifier (real data)
    mapped to the 5 labels; `override` forces an environment (manual read off the
    variables/20260531.md micro-dashboard)."""
    if override in ENVIRONMENT_REGIMES:
        return {"environment": override, "source": "manual override", "classifier_label": None}
    try:
        from sharks.regime.classifier import classify_regime
        r = classify_regime()
        env = CLASSIFIER_TO_ENV.get(r["label"], "中性")
        return {"environment": env, "source": "regime/classifier", "classifier_label": r["label"],
                "reasons": r.get("reasons", [])}
    except Exception as e:  # pragma: no cover
        return {"environment": "中性", "source": f"fallback ({e})", "classifier_label": None}


def target_for_regime(f: dict, env: str) -> Optional[float]:
    """Target price for one ticker under one environment. Analyst-band interpolation
    when low/high present; else forward-EPS × trailing-P/E × regime factor."""
    reg = ENVIRONMENT_REGIMES.get(env)
    if reg is None:
        return None
    lo, mean, hi = f.get("target_low"), f.get("target_mean"), f.get("target_high")
    tilt = reg["tilt"]
    if mean and lo and hi and hi > lo:
        # centre on the analyst consensus mean; tilt toward high (>0) or low (<0)
        if tilt >= 0:
            return round(float(mean) + tilt * (float(hi) - float(mean)), 2)
        return round(float(mean) + tilt * (float(mean) - float(lo)), 2)
    # fallback: P/E-reversion
    feps, tpe = f.get("forward_eps"), f.get("trailing_pe")
    if feps and tpe and feps > 0 and tpe > 0:
        return round(float(feps) * float(tpe) * reg["pe_factor"], 2)
    if mean:  # last resort: scale the consensus mean by the regime tilt (±20%)
        return round(float(mean) * (1.0 + 0.25 * tilt), 2)
    return None


def all_regime_targets(f: dict) -> dict:
    """Target price under every environment (so the user sees the full range)."""
    return {env: target_for_regime(f, env) for env in ENV_ORDER}


def valuation(f: dict, env: str, env_base_return: Optional[dict] = None) -> dict:
    """Full valuation for a ticker under the current environment.

    Returns two DISTINCT numbers (do not conflate):
      - upside_to_target: the valuation gap (target/price − 1), analyst-implied.
      - est_return: the expected return per horizon. CALIBRATED to the regime
        backtest base rate when `env_base_return` is supplied (honest — what this
        environment historically delivers at the market level); otherwise the v1
        uncalibrated upside×convergence assumption (flagged as such).
    """
    price = f.get("price")
    target = target_for_regime(f, env)
    out = {"ticker": f.get("ticker"), "environment": env, "price": price,
           "target": target, "all_regime_targets": all_regime_targets(f)}
    if target and price and price > 0:
        upside = target / float(price) - 1.0
        out["upside_to_target"] = round(upside, 4)
        if env_base_return:
            out["est_return"] = {h: v for h, v in env_base_return.items() if v is not None}
            out["est_return_basis"] = "regime-backtest base rate (calibrated to past data)"
        else:
            out["est_return"] = {h: round(upside * c, 4) for h, c in HORIZON_CONVERGENCE.items()}
            out["est_return_basis"] = "upside × convergence (uncalibrated v1 assumption)"
        out["method"] = "analyst-band" if (f.get("target_low") and f.get("target_high")) else "pe-reversion"
    else:
        out["upside_to_target"] = None
        out["est_return"] = None
        out["method"] = "no-data"
    return out


# ─── Price-based environment proxy + regime backtest (calibration) ─────────────
def price_environment(closes: pd.Series, as_of: pd.Timestamp) -> Optional[str]:
    """Map an index price series to one of the 5 environments from trend + momentum
    (a computable historical proxy for the backtest). Not the live classifier."""
    s = closes.loc[:as_of].dropna()
    if len(s) < 210:
        return None
    price = float(s.iloc[-1])
    ma200 = float(s.iloc[-200:].mean())
    dist = price / ma200 - 1.0
    mom6 = float(price / s.iloc[-126] - 1.0) if len(s) > 126 else 0.0
    if dist > 0.10 and mom6 > 0.10:
        return "積極樂觀"
    if dist > 0.02 and mom6 > 0.0:
        return "寬鬆"
    if dist < -0.10 and mom6 < -0.15:
        return "悲觀恐慌"
    if dist < -0.02:
        return "保守"
    return "中性"


def regime_forward_return_backtest(closes: pd.Series, horizons=(21, 63)) -> dict:
    """Walk-forward: classify each day's environment (price proxy) and measure the
    forward return by environment. Calibrates whether the 5 environments actually
    sort forward returns (the justification for regime-scaled targets)."""
    s = closes.dropna()
    by_env = {env: {h: [] for h in horizons} for env in ENV_ORDER}
    idx = s.index
    for i in range(210, len(s) - max(horizons), 5):   # step 5 trading days
        as_of = idx[i]
        env = price_environment(s, as_of)
        if env is None:
            continue
        for h in horizons:
            fwd = float(s.iloc[i + h] / s.iloc[i] - 1.0)
            by_env[env][h].append(fwd)
    out = {}
    for env in ENV_ORDER:
        out[env] = {f"{h}d_mean_fwd_ret": (round(float(np.mean(by_env[env][h])), 4) if by_env[env][h] else None)
                    for h in horizons}
        out[env]["n"] = len(by_env[env][horizons[0]])
    return out


# ─── v2: P/E-anchored valuation with REALISTIC downside ────────────────────────
# Fixes the v1 flaw where "panic" = analyst-low (a constructive 12-mo target, NOT a
# crash). v2 anchors fair value on the INDUSTRY P/E and models downside as genuine
# multiple compression + a beta-implied drawdown — so a high-multiple high-beta name
# (NVDA) shows a deep, honest downside, not −4%.
MARKET_CRASH_REF = 0.35          # a "real" market drawdown, for the beta-implied floor (grade-C)
SECTOR_TROUGH_FACTOR = 0.60      # bears compress sector multiples ~40%
SECTOR_PEAK_FACTOR = 1.35
# Forward-P/E anchors by sector, as_of 2026-05-31 — grade-C CONTEXT, not gospel.
INDUSTRY_PE = {
    "Technology": 30.0, "Communication Services": 22.0, "Consumer Cyclical": 24.0,
    "Healthcare": 18.0, "Financial Services": 15.0, "Industrials": 21.0,
    "Energy": 12.0, "Consumer Defensive": 21.0, "Utilities": 18.0,
    "Basic Materials": 16.0, "Real Estate": 18.0,
}


def peg_fair_pe(growth: Optional[float], industry_pe: float) -> float:
    """PEG≈1 growth-justified P/E, clamped to [0.7×, 2.5×] the industry P/E. A
    40%-grower earns ~40×; a no-grower falls back to the industry P/E."""
    if growth is None or growth <= 0:
        return industry_pe
    return float(min(max(growth * 100.0, industry_pe * 0.7), industry_pe * 2.5))


def industry_pe_valuation(f: dict, industry_pe: Optional[float] = None) -> Optional[dict]:
    """P/E-anchored valuation. Two fair-value anchors (do not conflate):
      - fair_value_industry: forward EPS × INDUSTRY P/E (conservative mean-reversion).
      - fair_value_growth:   forward EPS × PEG≈1 P/E (rewards real growth).
    Downside is REAL: panic_floor = min(multiple compression to a sector trough,
    beta-implied drawdown in a −35% market). premium_to_*_fair shows how stretched
    the current price is. yfinance grade-C; watchlist only."""
    feps, price, beta = f.get("forward_eps"), f.get("price"), f.get("beta")
    ipe = industry_pe if industry_pe is not None else INDUSTRY_PE.get(f.get("sector"))
    if not (feps and feps > 0 and price and ipe):
        return None
    growth = f.get("earnings_growth_yoy") or f.get("revenue_growth_yoy")
    gpe = peg_fair_pe(growth, ipe)
    fair_ind = round(feps * ipe, 2)
    fair_growth = round(feps * gpe, 2)
    bear_pe = round(feps * ipe * SECTOR_TROUGH_FACTOR, 2)
    bear_beta = round(price * (1.0 - (beta or 1.0) * MARKET_CRASH_REF), 2)
    panic = min(bear_pe, bear_beta)
    cur = f.get("fwd_pe")
    return {
        "current_fwd_pe": round(float(cur), 1) if cur else None,
        "industry_pe": ipe,
        "growth_justified_pe": round(gpe, 1),
        "fair_value_industry": fair_ind,
        "fair_value_growth": fair_growth,
        "panic_floor": panic,
        "bear_multiple_compression": bear_pe,
        "bear_beta_implied": bear_beta,
        "realistic_downside": round(panic / price - 1, 3),
        "premium_to_industry_fair": round(price / fair_ind - 1, 3),
        "premium_to_growth_fair": round(price / fair_growth - 1, 3),
        "beta": beta,
        "growth": round(float(growth), 3) if growth else None,
    }


def main() -> int:
    import json
    import sys
    import warnings
    from datetime import datetime, timezone
    from pathlib import Path
    warnings.filterwarnings("ignore")
    import yfinance as yf
    from sharks.scoring.fundamentals import fetch_fundamentals

    env = current_environment()
    cur = env["environment"]

    spx = yf.download("^GSPC", start="2008-01-01", end="2026-05-29", interval="1d",
                      auto_adjust=True, progress=False)["Close"]
    if isinstance(spx, pd.DataFrame):
        spx = spx.iloc[:, 0]
    bt = regime_forward_return_backtest(spx)
    env_base = {"month": bt[cur].get("21d_mean_fwd_ret"), "quarter": bt[cur].get("63d_mean_fwd_ret")}

    watch = ["NKE", "AMZN", "NVDA", "MSFT", "META", "AAPL", "GOOGL", "TSLA", "LLY", "CRM"]
    vals = [valuation(fetch_fundamentals(t), cur, env_base) for t in watch]

    report = {"as_of": datetime.now(timezone.utc).isoformat(), "report_type": "valuation",
              "environment": env, "valuations": vals, "regime_backtest_spx": bt,
              "note": "v1: analyst-band × regime target; regime backtest = price proxy on SPX 2008-2026. Observe-first."}
    out = Path("outputs") / "valuation.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    print(f"wrote {out}  | environment={env['environment']} ({env.get('classifier_label')})", file=sys.stderr)
    for v in vals:
        if v["upside_to_target"] is not None:
            print(f"  {v['ticker']:5} px={v['price']} tgt={v['target']} valuation-gap={v['upside_to_target']:+.1%} "
                  f"({v['method']})", file=sys.stderr)
    print(f"  est_return for current env ({cur}) = {env_base}  [calibrated base rate]", file=sys.stderr)
    print("  regime backtest (SPX fwd return by environment):", file=sys.stderr)
    for env_name in ENV_ORDER:
        print(f"    {env_name:5} 21d={bt[env_name].get('21d_mean_fwd_ret')} 63d={bt[env_name].get('63d_mean_fwd_ret')} n={bt[env_name]['n']}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
