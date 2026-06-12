"""本地千股均線掃描器 — 越線 / 連線 / 騎線 / 大底 + 板塊廣度(完全離線).

主理人指令(2026-06-10):數據存 local 後要做推演預測。本模組**只讀 data/lake/prices/
*.parquet**(yfinance 湖,由 sharks.data.data_lake 維護),不打任何 API —— 沒有 Finviz
訂閱、甚至沒網路都能跑。純 pandas 向量化,千股 × 多均線秒級完成,零新依賴。

四種訊號(外部 review 採納項,定義對齊 docs/finviz_screening_recipe.md 的紀律):
  越線 cross    — close 近 K 日內上穿 MA20 / MA60(初步表態)
  連線 aligned  — 多頭排列 MA5>MA20>MA60 且三條斜率向上(趨勢確認)
  騎線 riding   — 連續 N 日 low 貼 MA20 不破(沿線推進,最強持續型)
  大底 bottom   — 距 52w 低 <15% + 量縮 + RSI 底背離(吸籌期,僅供 stealth 交叉驗證)

板塊廣度:每板塊「站上 MA50 的比例」(% above MA50)→ 餵 regime/breadth 的細粒度層;
比例從 <30% 跳上 >50% 的板塊 = 早期輪動訊號(熱點偵測,不是預測)。

recommend-only:輸出是研究排序,**不是買訊**。進場仍走 燃料閘 + 連續起漲 + regime
(/rally、/stealth);本掃描器只負責「找出值得看的」與「板塊溫度」。

Point-in-time:as_of = 數據最後一根 bar 的日期(NYSE close),不是執行時間;輸出存
outputs/ma-scan-<as_of>.json 供回測讀取(philosophy/09-point-in-time.md)。

CLI:
    python -m sharks.scoring.ma_scanner            # 掃整個 lake
    python -m sharks.scoring.ma_scanner NVDA VST   # 只掃指定 tickers
"""

from __future__ import annotations

import json
import sys
import warnings
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)

import numpy as np
import pandas as pd

LAKE = Path("data/lake")

# ── tunables(紀律參數,集中可調)──
CROSS_LOOKBACK = 3        # 越線:上穿發生在近 K 根內
RIDE_DAYS = 10            # 騎線:連續 N 日貼線
RIDE_TOL = 0.02           # 騎線:low 容許跌破 MA20 的緩衝(2%)
BOTTOM_DIST_52W = 0.15    # 大底:距 52 週低 < 15%
VOL_CONTRACT = 0.75       # 大底:近 20d 均量 < 0.75 × 120d 均量(量縮)
REJECT_TOL = 0.03         # 拒絕棒:收盤低於當日 high 超過此比例(長上影)
RSI_N = 14
MIN_BARS = 130            # 不足 130 根日 K(~半年)不評(均線/52w 不可靠)


# ── indicator helpers(向量化,單一 ticker 的 Series)──

def rsi(close: pd.Series, n: int = RSI_N) -> pd.Series:
    """Wilder RSI(EWM 近似)。"""
    delta = close.diff()
    up = delta.clip(lower=0).ewm(alpha=1 / n, min_periods=n).mean()
    dn = (-delta.clip(upper=0)).ewm(alpha=1 / n, min_periods=n).mean()
    rs = up / dn.replace(0, np.nan)
    return 100 - 100 / (1 + rs)


def _slope_up(ma: pd.Series, k: int = 5) -> bool:
    """均線近 k 根斜率向上(末值 > k 根前)。"""
    if len(ma.dropna()) < k + 1:
        return False
    return bool(ma.iloc[-1] > ma.iloc[-1 - k])


def scan_one(df: pd.DataFrame) -> Optional[dict]:
    """單一 ticker 的 OHLCV DataFrame(欄位 Open/High/Low/Close/Volume)→ 訊號 dict。
    純函式(不碰磁碟),供測試直接餵合成數據。"""
    if df is None or len(df) < MIN_BARS or "Close" not in df:
        return None
    close, low, vol = df["Close"], df["Low"], df.get("Volume")
    high = df["High"] if "High" in df else close
    ma5, ma20 = close.rolling(5).mean(), close.rolling(20).mean()
    ma50, ma60 = close.rolling(50).mean(), close.rolling(60).mean()
    ma200 = close.rolling(200).mean() if len(close) >= 200 else pd.Series(np.nan, index=close.index)
    r = rsi(close)

    above20, above60 = close > ma20, close > ma60
    cross20 = bool((above20 & ~above20.shift(1).fillna(False)).tail(CROSS_LOOKBACK).any())
    cross60 = bool((above60 & ~above60.shift(1).fillna(False)).tail(CROSS_LOOKBACK).any())

    aligned = bool(
        ma5.iloc[-1] > ma20.iloc[-1] > ma60.iloc[-1]
        and _slope_up(ma5) and _slope_up(ma20) and _slope_up(ma60)
    ) if not (np.isnan(ma60.iloc[-1]) or np.isnan(ma5.iloc[-1])) else False

    tail_low, tail_ma = low.tail(RIDE_DAYS), ma20.tail(RIDE_DAYS)
    riding = bool(
        len(tail_ma.dropna()) == RIDE_DAYS
        and (tail_low >= tail_ma * (1 - RIDE_TOL)).all()
        and close.iloc[-1] >= ma20.iloc[-1]
        and _slope_up(ma20)
    )

    # 大底:距 52w 低 + 量縮 + RSI 底背離(後段價創更低、RSI 反而墊高)
    win = close.tail(252)
    lo52 = float(win.min())
    # 52w 高取 High 欄(盤中極值):用 close 算會把長上影拒絕棒誤報成「距高 0%」
    hi52 = float(high.tail(252).max())
    dist_lo = (close.iloc[-1] - lo52) / lo52 if lo52 > 0 else np.nan
    vol_contract = bool(
        vol is not None and len(vol.dropna()) >= 120
        and vol.tail(20).mean() < VOL_CONTRACT * vol.tail(120).mean()
    )
    divergence = False
    if len(close) >= 120 and not r.tail(120).isna().all():
        c120, r120 = close.tail(120), r.tail(120)
        a_c, b_c = c120.iloc[:60], c120.iloc[60:]
        ia, ib = a_c.idxmin(), b_c.idxmin()
        divergence = bool(b_c.min() < a_c.min() and r120.loc[ib] > r120.loc[ia])
    bottom = bool(dist_lo is not np.nan and dist_lo < BOTTOM_DIST_52W and vol_contract and divergence)

    # 拒絕棒:最後一根收盤距當日 high 回落 > REJECT_TOL(blow-off 遭賣壓拒絕的警示)
    last_high = float(high.iloc[-1])
    rejection = bool(last_high > 0 and (last_high - float(close.iloc[-1])) / last_high > REJECT_TOL)

    return {
        "close": round(float(close.iloc[-1]), 2),
        "as_of_bar": str(close.index[-1].date()) if hasattr(close.index[-1], "date") else str(close.index[-1]),
        "cross_ma20": cross20, "cross_ma60": cross60,
        "aligned": aligned, "riding": riding, "bottom": bottom,
        "above_ma50": bool(close.iloc[-1] > ma50.iloc[-1]) if not np.isnan(ma50.iloc[-1]) else None,
        "above_ma200": bool(close.iloc[-1] > ma200.iloc[-1]) if not np.isnan(ma200.iloc[-1]) else None,
        "dist_52w_low_pct": round(float(dist_lo) * 100, 1) if dist_lo == dist_lo else None,
        "dist_52w_high_pct": round((float(close.iloc[-1]) - hi52) / hi52 * 100, 1) if hi52 > 0 else None,
        "rejection_bar": rejection,
        "rsi": round(float(r.iloc[-1]), 1) if not np.isnan(r.iloc[-1]) else None,
        "vol_contract": vol_contract, "rsi_divergence": divergence,
    }


# ── lake I/O ──

def lake_tickers(lake: Path = LAKE) -> list[str]:
    return sorted({p.stem.rsplit("_", 1)[0] for p in (lake / "prices").glob("*_1d.parquet")})


def load_lake_prices(ticker: str, lake: Path = LAKE) -> Optional[pd.DataFrame]:
    p = lake / "prices" / f"{ticker}_1d.parquet"
    if not p.exists():
        return None
    try:
        return pd.read_parquet(p)
    except Exception:
        return None


def load_sector(ticker: str, lake: Path = LAKE) -> str:
    p = lake / "info" / f"{ticker}.json"
    try:
        return json.loads(p.read_text(encoding="utf-8")).get("sector") or "Unknown"
    except Exception:
        return "Unknown"


# ── full scan + sector breadth ──

def scan_lake(tickers: Optional[list[str]] = None, lake: Path = LAKE) -> dict:
    """掃描 lake →(每檔訊號, 板塊廣度)。完全離線。"""
    tks = tickers or lake_tickers(lake)
    rows: dict[str, dict] = {}
    for t in tks:
        sig = scan_one(load_lake_prices(t, lake))
        if sig:
            sig["sector"] = load_sector(t, lake)
            rows[t] = sig

    sectors: dict[str, dict] = {}
    for t, s in rows.items():
        b = sectors.setdefault(s["sector"], {"n": 0, "above_ma50": 0, "aligned": 0, "bottom": 0})
        b["n"] += 1
        b["above_ma50"] += 1 if s.get("above_ma50") else 0
        b["aligned"] += 1 if s.get("aligned") else 0
        b["bottom"] += 1 if s.get("bottom") else 0
    breadth = {
        k: {"n": v["n"],
            "pct_above_ma50": round(v["above_ma50"] / v["n"] * 100, 1),
            "pct_aligned": round(v["aligned"] / v["n"] * 100, 1),
            "pct_bottom": round(v["bottom"] / v["n"] * 100, 1)}
        for k, v in sorted(sectors.items(), key=lambda kv: -kv[1]["above_ma50"] / max(kv[1]["n"], 1))
        if v["n"] >= 3  # 太小的板塊樣本不報
    }

    as_of = max((s["as_of_bar"] for s in rows.values()), default=None)
    return {
        "as_of": as_of,                       # point-in-time = 最後一根 bar,非執行時間
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "engine": "ma-scanner-offline-lake",
        "n_scanned": len(rows),
        "signals": {
            "cross_ma60": sorted(t for t, s in rows.items() if s["cross_ma60"]),
            "cross_ma20": sorted(t for t, s in rows.items() if s["cross_ma20"]),
            "aligned": sorted(t for t, s in rows.items() if s["aligned"]),
            "riding": sorted(t for t, s in rows.items() if s["riding"]),
            "bottom": sorted(t for t, s in rows.items() if s["bottom"]),
        },
        "sector_breadth": breadth,
        "rows": rows,
        "disclaimer": "recommend-only 研究排序;進場仍走 燃料閘+連續起漲+regime,永不下單。",
    }


def write_scan(report: dict, out_dir: Path = Path("outputs")) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"ma-scan-{report.get('as_of') or datetime.now().strftime('%Y-%m-%d')}.json"
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def main(argv: Optional[list[str]] = None) -> int:
    args = [a.upper() for a in (sys.argv[1:] if argv is None else argv)]
    tks = args or None
    n_lake = len(lake_tickers())
    if n_lake == 0:
        print("lake 是空的 — 先跑 python -m sharks.data.data_lake 建湖(需網路一次)", file=sys.stderr)
        return 1
    print(f"離線 MA 掃描:lake {n_lake} 檔(無 API 呼叫)…", file=sys.stderr)
    rep = scan_lake(tks)
    path = write_scan(rep)
    sig = rep["signals"]
    print(f"✅ ma-scan as_of={rep['as_of']} — 掃 {rep['n_scanned']} 檔 → {path}")
    for k, label in (("aligned", "連線(多頭排列)"), ("riding", "騎線(沿 MA20)"),
                     ("cross_ma60", "越線(上穿 MA60)"), ("bottom", "大底(量縮+背離)")):
        names = sig[k]
        print(f"  {label}: {len(names)} 檔 — {' '.join(names[:15])}{' …' if len(names) > 15 else ''}")
    print("  板塊廣度 %>MA50:")
    for sec, b in list(rep["sector_breadth"].items())[:11]:
        bar = "█" * int(b["pct_above_ma50"] // 5)
        print(f"    {sec:24} {b['pct_above_ma50']:5.1f}%  ({b['n']}檔) {bar}")
    print("recommend-only — 進場仍走 燃料閘+連續起漲+regime。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
