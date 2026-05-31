"""One-off driver: Bayesian posterior + regime-conditioned valuation/target prices
for the RF / connectivity / power-analog / foundry / test semiconductor names.

Composes the EXISTING engines (no new model):
  - scoring.bayesian_update.posterior_for_ticker  (prior from tech_dd rubric+verdict
    → posterior from milestone ladder → edge vs market-implied bubble_guard)
  - scoring.valuation.valuation / industry_pe_valuation  (regime-conditioned analyst-
    band target + P/E-anchored fair value + REALISTIC downside)
  - scoring.valuation.regime_forward_return_backtest (SPX) for the calibrated est_return

Writes outputs/rf-bayes-valuation-<as_of>.json. Observe-first / watchlist-only;
NOT buy/sell advice. yfinance grade-C (current multiples + analyst targets).
"""

from __future__ import annotations

import json
import sys
import warnings
from datetime import datetime, timezone
from pathlib import Path

warnings.filterwarnings("ignore")
import pandas as pd
import yfinance as yf

from sharks.scoring.bayesian_update import posterior_for_ticker
from sharks.scoring.fundamentals import fetch_fundamentals
from sharks.scoring.tech_dd import TECH_DD, load_fom_bubble_guard
from sharks.scoring.valuation import (
    current_environment, valuation, industry_pe_valuation,
    regime_forward_return_backtest, ENV_ORDER,
)

# RF / connectivity / power-analog / foundry / test semis (the shortlist semis).
SEMIS = ["KEYS", "GFS", "TSEM", "ADI", "NXPI", "QRVO", "SWKS", "QCOM", "AVGO",
         "MPWR", "TXN", "ON", "MCHP", "POWI", "VICR", "NVTS", "DIOD", "AOSL",
         "CRUS", "SYNA", "CEVA", "MTSI"]


def main() -> int:
    as_of = sys.argv[1] if len(sys.argv) > 1 else "2026-05-31"
    env = current_environment()
    cur = env["environment"]
    print(f"environment = {cur} ({env.get('classifier_label')})", file=sys.stderr)

    # Calibrated env base-rate return (SPX regime backtest)
    spx = yf.download("^GSPC", start="2008-01-01", end="2026-05-29", interval="1d",
                      auto_adjust=True, progress=False)["Close"]
    if isinstance(spx, pd.DataFrame):
        spx = spx.iloc[:, 0]
    bt = regime_forward_return_backtest(spx)
    env_base = {"month": bt[cur].get("21d_mean_fwd_ret"), "quarter": bt[cur].get("63d_mean_fwd_ret")}

    bg_map = load_fom_bubble_guard(Path("outputs"))

    rows = []
    for t in SEMIS:
        f = fetch_fundamentals(t)
        bg = (bg_map.get(t) or {}).get("bubble_guard")
        bayes = posterior_for_ticker(t, bubble_guard=bg)
        val = valuation(f, cur, env_base)
        v2 = industry_pe_valuation(f)
        dd = TECH_DD.get(t)
        rows.append({
            "ticker": t,
            "verdict": dd.verdict if dd else None,
            "trend": dd.trend if dd else None,
            "flags": list(dd.flags) if dd else [],
            "bayes": bayes,
            "bubble_guard": bg,
            "price": f.get("price"),
            "fwd_pe": f.get("fwd_pe"),
            "target_regime": val.get("target"),
            "upside_to_target": val.get("upside_to_target"),
            "all_regime_targets": val.get("all_regime_targets"),
            "valuation_v2": v2,
            "analyst_reco": f.get("recommendation"),
        })

    report = {
        "as_of": datetime.now(timezone.utc).isoformat(), "quote_date": as_of,
        "report_type": "rf_bayes_valuation", "observe_first": True,
        "environment": env, "env_base_return": env_base,
        "regime_backtest_spx": bt,
        "note": ("prior(tech_dd rubric+verdict) → posterior(milestone) → edge(bubble_guard); "
                 "regime-conditioned analyst-band target + P/E-anchored fair value + realistic "
                 "downside. WATCHLIST only, not buy/sell advice; yfinance grade-C."),
        "rows": rows,
    }
    out = Path("outputs") / f"rf-bayes-valuation-{as_of}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    print(f"wrote {out}", file=sys.stderr)

    # compact table
    print(f"\n{'TKR':6}{'verdict':8}{'prior':>7}{'post':>7}{'edge':>7}{'price':>9}"
          f"{'tgt(寬)':>9}{'up%':>7}{'fairG':>8}{'down%':>7}{'fwdPE':>7}", file=sys.stderr)
    for r in rows:
        b = r["bayes"] or {}
        v2 = r["valuation_v2"] or {}
        edge = b.get("edge")
        up = r["upside_to_target"]
        dn = v2.get("realistic_downside")
        print(f"{r['ticker']:6}{(r['verdict'] or '-'):8}"
              f"{(b.get('prior') or 0):>7.2f}{(b.get('posterior') or 0):>7.2f}"
              f"{(f'{edge:+.2f}' if edge is not None else '  n/a'):>7}"
              f"{(r['price'] or 0):>9.2f}{(r['target_regime'] or 0):>9.2f}"
              f"{(f'{up*100:+.0f}' if up is not None else 'n/a'):>7}"
              f"{(v2.get('fair_value_growth') or 0):>8.2f}"
              f"{(f'{dn*100:+.0f}' if dn is not None else 'n/a'):>7}"
              f"{(r['fwd_pe'] or 0):>7.1f}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
