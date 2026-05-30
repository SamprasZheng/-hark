"""Fama-French 因子驗證 — 證明 FOM 真實 alpha.

Uses Ken French Data Library (free).

Method:
  1. Pull Fama-French 3 factor monthly returns
  2. Build hypothetical FOM portfolio monthly returns (from backtest)
  3. Regress portfolio excess returns on factors
  4. Check alpha (intercept) + t-stat for significance
"""

from __future__ import annotations

import io
import json
import sys
import warnings
import zipfile
from datetime import datetime, timezone
from pathlib import Path

warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)

import urllib.request

import numpy as np
import pandas as pd

try:
    import statsmodels.api as sm
    HAVE_SM = True
except ImportError:
    HAVE_SM = False


FF3_URL = "https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/F-F_Research_Data_Factors_CSV.zip"
FF5_URL = "https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/F-F_Research_Data_5_Factors_2x3_CSV.zip"


def fetch_ff_factors(url: str = FF3_URL) -> pd.DataFrame:
    """Pull and parse Ken French monthly factor data."""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=30) as r:
            zip_bytes = r.read()
        z = zipfile.ZipFile(io.BytesIO(zip_bytes))
        csv_name = next(n for n in z.namelist() if n.endswith(".CSV") or n.endswith(".csv"))
        raw_text = z.read(csv_name).decode("latin-1")
        # Parse — skip header + footer
        lines = raw_text.splitlines()
        data_start = next(i for i, line in enumerate(lines)
                          if line.strip().startswith("19") or line.strip().startswith("20"))
        # Find end of monthly data (where annual data starts or footer)
        data_end = None
        for i in range(data_start, len(lines)):
            line = lines[i].strip()
            if not line or "Annual" in line or "Copyright" in line:
                data_end = i
                break
        if data_end is None:
            data_end = len(lines)
        # Parse
        rows = []
        for line in lines[data_start:data_end]:
            line = line.strip()
            if not line:
                continue
            parts = [p.strip() for p in line.split(",")]
            if not parts[0].isdigit() or len(parts[0]) != 6:
                continue
            rows.append(parts)
        # 3-factor: Mkt-RF, SMB, HML, RF
        cols = ["YYYYMM", "Mkt_RF", "SMB", "HML", "RF"]
        df = pd.DataFrame(rows, columns=cols[:len(rows[0])])
        df["date"] = pd.to_datetime(df["YYYYMM"], format="%Y%m")
        for c in ["Mkt_RF", "SMB", "HML", "RF"]:
            if c in df.columns:
                df[c] = pd.to_numeric(df[c], errors="coerce") / 100  # convert to decimal
        df = df.set_index("date").drop(columns=["YYYYMM"])
        return df.dropna()
    except Exception as e:
        print(f"  WARN: FF fetch failed: {e}", file=sys.stderr)
        return pd.DataFrame()


def simulate_fom_returns_from_backtest() -> pd.Series:
    """Build hypothetical monthly returns from existing backtest output.

    Reads outputs/fom-backtest-2016-to-2026.json and constructs implied returns.
    """
    try:
        path = Path("outputs/fom-backtest-2016-to-2026.json")
        if not path.exists():
            return pd.Series(dtype=float)
        data = json.loads(path.read_text())
        history = data.get("portfolio_history_summary", [])
        if not history:
            return pd.Series(dtype=float)
        # Each entry has portfolio_mv + invested_total
        records = []
        prev_mv = None
        prev_inv = None
        for h in history:
            m = pd.to_datetime(h["month"])
            mv = h["portfolio_mv"]
            inv = h["invested_total"]
            if prev_mv is not None and prev_inv is not None:
                # Add new investment doesn't count as return
                if prev_mv > 0:
                    # Return excluding new contribution
                    new_invest = inv - prev_inv
                    if mv - new_invest > 0:
                        ret = (mv - new_invest - prev_mv) / prev_mv
                        records.append((m, ret))
            prev_mv = mv
            prev_inv = inv
        if not records:
            return pd.Series(dtype=float)
        df = pd.DataFrame(records, columns=["date", "return"]).set_index("date")
        return df["return"]
    except Exception as e:
        print(f"  WARN: backtest read failed: {e}", file=sys.stderr)
        return pd.Series(dtype=float)


def run_ff_regression(portfolio_returns: pd.Series, ff: pd.DataFrame) -> dict:
    """Run Fama-French regression: r_p - r_f = alpha + b*MKT + s*SMB + h*HML + e."""
    if not HAVE_SM:
        return {"error": "statsmodels not installed"}
    # Align
    pr = portfolio_returns.copy()
    pr.index = pr.index.to_period("M").to_timestamp()
    ff.index = ff.index.to_period("M").to_timestamp()
    merged = pd.concat([pr.rename("port"), ff], axis=1).dropna()
    if len(merged) < 12:
        return {"error": f"insufficient overlap ({len(merged)} months)"}
    # Excess return
    merged["excess"] = merged["port"] - merged["RF"]
    # Regress
    X = merged[["Mkt_RF", "SMB", "HML"]]
    X = sm.add_constant(X)
    y = merged["excess"]
    model = sm.OLS(y, X).fit()
    return {
        "n_months": len(merged),
        "alpha_monthly_pct": round(float(model.params["const"]) * 100, 3),
        "alpha_annualized_pct": round(float(model.params["const"]) * 12 * 100, 2),
        "alpha_tstat": round(float(model.tvalues["const"]), 3),
        "alpha_significant_95": bool(abs(float(model.tvalues["const"])) > 1.96),
        "alpha_significant_99": bool(abs(float(model.tvalues["const"])) > 2.58),
        "mkt_beta": round(float(model.params["Mkt_RF"]), 3),
        "smb_loading": round(float(model.params["SMB"]), 3),
        "hml_loading": round(float(model.params["HML"]), 3),
        "r_squared": round(float(model.rsquared), 3),
        "interpretation": _interpret(model),
    }


def _interpret(model) -> str:
    alpha_t = abs(float(model.tvalues["const"]))
    smb = float(model.params["SMB"])
    hml = float(model.params["HML"])
    parts = []
    if alpha_t > 2.58:
        parts.append("🟢 **真實 alpha** — 統計顯著 (99%);系統訊號超越 3 因子模型")
    elif alpha_t > 1.96:
        parts.append("🟡 顯著 alpha (95%) — 真實但需更多資料")
    else:
        parts.append("🔴 Alpha 不顯著 — 報酬可能解釋於因子曝險")
    if smb > 0.2:
        parts.append(f"📐 SMB +{smb:.2f}: 賺小型股 premium")
    elif smb < -0.2:
        parts.append(f"📐 SMB {smb:.2f}: 偏大型股")
    if hml > 0.2:
        parts.append(f"📐 HML +{hml:.2f}: 賺價值 premium")
    elif hml < -0.2:
        parts.append(f"📐 HML {hml:.2f}: 偏成長股")
    return " | ".join(parts)


def main():
    out_dir = Path("outputs")
    out_dir.mkdir(parents=True, exist_ok=True)
    today = datetime.now().strftime("%Y-%m-%d")

    print("Fetching Fama-French 3 factor data...", file=sys.stderr)
    ff = fetch_ff_factors()
    if ff.empty:
        print("⚠️  FF fetch failed", file=sys.stderr)
        report = {"status": "FF_FETCH_FAILED",
                   "next_steps": "Download manually from Ken French website"}
    else:
        print(f"  FF data: {len(ff)} months", file=sys.stderr)
        print("Simulating FOM portfolio returns from backtest...", file=sys.stderr)
        pr = simulate_fom_returns_from_backtest()
        if pr.empty:
            print("  no backtest data", file=sys.stderr)
            report = {"status": "NO_PORTFOLIO_RETURNS",
                       "next_steps": "Run fom_backtest first"}
        else:
            print(f"  portfolio: {len(pr)} months", file=sys.stderr)
            result = run_ff_regression(pr, ff)
            report = {
                "as_of": datetime.now(timezone.utc).isoformat(),
                "fama_french_3_factor_regression": result,
                "interpretation": result.get("interpretation"),
                "ff_data_period": f"{ff.index[0].date()} to {ff.index[-1].date()}",
                "portfolio_period": f"{pr.index[0].date()} to {pr.index[-1].date()}",
            }
            print(f"  alpha: {result.get('alpha_annualized_pct')}% pa (t={result.get('alpha_tstat')})",
                  file=sys.stderr)

    out_path = out_dir / f"fama-french-validation-{today}.json"
    out_path.write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")
    print(f"wrote {out_path}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
