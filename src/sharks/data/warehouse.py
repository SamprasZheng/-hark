"""yfinance(EOD) + Parquet 本地倉儲 — 增量更新 + 精確月線型態(三連陽/50-200金叉/距ATH/醞釀).

WHY: Finviz 快照給不了月線 K 序列。本檔用 yfinance 抓 EOD 存 Parquet(增量更新、防 IP 鎖),
在本地算 Finviz 做不到的精確型態:
  * 距 ATH %        — price < 50% ATH(深跌有空間)
  * 50/200 日線金叉  — 剛黃金交叉(50SMA 上穿 200SMA)= 結構翻多
  * 月線連續三陽     — 連續 3 根月 K 收高(月線級別上漲)
  * 🌱 醞釀/即將起漲 — 深跌(距ATH≥50%)+ 剛金叉 + 月線剛轉 → 預測「即將三連陽」(OKLO/SMCI型)

分工:**Finviz 管基本面/買盤/篩選/快照;本檔管價格歷史/波型**,兩者互補。
型態函式是純 stdlib(離線可單元測試);yfinance / pandas / duckdb 只在 IO 函式內延遲載入,
所以這個模組在沒有那些套件(或 numpy 壞掉)時仍可 import + 測純邏輯。recommend-only。

CLI(主機,需 yfinance + 修好 numpy):
    python -m sharks.data.warehouse sync supercycle      # 增量更新該池的 EOD → Parquet
    python -m sharks.data.warehouse scan pre_ignition     # 本地算型態 → 列出即將起漲候選
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

DATA_DIR = "raw/market_data/daily"      # 每檔一個 <ticker>.parquet(增量、point-in-time)


# ── 純型態函式(stdlib,離線可測)─────────────────────────────────────────────

def _sma(xs: list[float], n: int, i: int) -> Optional[float]:
    """xs[i] 的 n 日簡單移動平均(資料不足回 None)。"""
    if i + 1 < n:
        return None
    window = xs[i - n + 1:i + 1]
    return sum(window) / n


def monthly_closes(dates: list[str], closes: list[float]) -> list[float]:
    """日線(YYYY-MM-DD, close)→ 月線收盤(每個年月的最後一根)。"""
    out: list[float] = []
    last_key = None
    for d, c in zip(dates, closes):
        key = d[:7]                     # YYYY-MM
        if key != last_key:
            out.append(c)
            last_key = key
        else:
            out[-1] = c                 # 同月 → 更新為較晚的收盤
    return out


def consecutive_green_months(m_closes: list[float]) -> int:
    """月線尾端連續上漲的根數(close > 前一月 close)。3 = 月線三連陽。"""
    n = 0
    for i in range(len(m_closes) - 1, 0, -1):
        if m_closes[i] > m_closes[i - 1]:
            n += 1
        else:
            break
    return n


def dist_ath_pct(closes: list[float]) -> float:
    """距歷史高 %(正 = 低於高點多少)。"""
    if not closes:
        return 0.0
    ath = max(closes)
    return round((ath - closes[-1]) / ath * 100, 1) if ath else 0.0


def golden_cross(closes: list[float], *, fast: int = 50, slow: int = 200,
                 lookback: int = 63) -> bool:
    """日線 fastSMA 上穿 slowSMA 且**近期才交叉**(lookback 內曾 fast<=slow)= 剛翻多。"""
    if len(closes) < slow + 1:
        return False
    f_now, s_now = _sma(closes, fast, len(closes) - 1), _sma(closes, slow, len(closes) - 1)
    if f_now is None or s_now is None or not (f_now > s_now):
        return False
    for t in range(max(slow, len(closes) - lookback), len(closes)):
        f, s = _sma(closes, fast, t), _sma(closes, slow, t)
        if f is not None and s is not None and f <= s:
            return True                 # 近期內曾在下方 → 剛交叉
    return False


def classify(dates: list[str], closes: list[float]) -> dict:
    """精確月線型態判定 → {dist_ath_pct, golden_cross, green_months, stage, deep}.

    stage:
      🌊 大浪(第三浪) = 金叉 + 月線三連陽 + 不算太深(距高<35%,已走一段)
      📈 月線三連陽    = 月線連續≥3 陽
      🌱 醞釀/即將起漲 = 深跌(距高≥50%,price<50%ATH)+ 剛金叉 + 月線剛轉(預測)
      🚀 起漲          = 剛金叉,月線剛轉
      〰️ 整理
    """
    if len(closes) < 60:
        return {"dist_ath_pct": dist_ath_pct(closes), "golden_cross": False,
                "green_months": 0, "stage": "資料不足", "deep": False}
    mc = monthly_closes(dates, closes)
    green = consecutive_green_months(mc)
    d = dist_ath_pct(closes)
    gc = golden_cross(closes)
    deep = d >= 50.0                                  # price < 50% ATH
    m_turning = len(mc) >= 2 and mc[-1] > mc[-2]
    if gc and green >= 3 and d < 35:
        stage = "🌊 大浪/第三浪"
    elif green >= 3:
        stage = "📈 月線三連陽"
    elif deep and gc and m_turning:
        stage = "🌱 醞釀(深跌剛金叉·即將起漲)"
    elif gc and m_turning:
        stage = "🚀 起漲(剛金叉)"
    else:
        stage = "〰️ 整理"
    return {"dist_ath_pct": d, "golden_cross": gc, "green_months": green,
            "stage": stage, "deep": deep}


# ── IO(主機:yfinance + Parquet 增量更新;延遲載入)──────────────────────────

def update_cache(ticker: str, *, data_dir: str = DATA_DIR, start: str = "2018-01-01"):
    """增量抓 EOD → <ticker>.parquet。已最新則跳過(防 IP 鎖)。回傳 (ok, rows_added)。"""
    import datetime as _dt
    import pandas as pd
    import yfinance as yf
    Path(data_dir).mkdir(parents=True, exist_ok=True)
    fp = Path(data_dir) / f"{ticker}.parquet"
    start_date, existing = start, None
    if fp.exists():
        existing = pd.read_parquet(fp)
        if len(existing):
            last = pd.to_datetime(existing["Date"]).max()
            start_date = (last + pd.Timedelta(days=1)).strftime("%Y-%m-%d")
    today = _dt.date.today().strftime("%Y-%m-%d")
    if start_date >= today:
        return True, 0
    try:
        df = yf.download(ticker, start=start_date, end=today, progress=False, auto_adjust=True)
    except Exception:
        return False, 0
    if df is None or df.empty:
        return True, 0
    df = df.reset_index()[["Date", "Close"]]
    df["Date"] = df["Date"].astype(str).str[:10]
    if existing is not None:
        df = pd.concat([existing, df]).drop_duplicates("Date").sort_values("Date")
    df.to_parquet(fp, index=False)
    return True, len(df)


def load_daily(ticker: str, *, data_dir: str = DATA_DIR):
    """讀本地 Parquet → (dates, closes)。無檔回 ([],[])。"""
    import pandas as pd
    fp = Path(data_dir) / f"{ticker}.parquet"
    if not fp.exists():
        return [], []
    df = pd.read_parquet(fp).sort_values("Date")
    return df["Date"].astype(str).tolist(), [float(x) for x in df["Close"].tolist()]


def _resolve_tickers(arg: str) -> list[str]:
    """scope 名 → ticker 清單(複用 Finviz 的 fom_universe/scope);否則當逗號清單。"""
    try:
        from sharks.data import finviz_elite as FE
        kind, _, tks = FE.resolve_target(arg)
        if kind == "universe":
            return FE.fom_universe()
        if kind == "scope" and tks:
            return tks.split(",")
    except Exception:
        pass
    return [t.strip().upper() for t in arg.replace(" ", ",").split(",") if t.strip()]


def scan(tickers: list[str], *, data_dir: str = DATA_DIR) -> list[dict]:
    """對已快取的 ticker 跑型態判定 → 排序(醞釀/三連陽優先,再按距高深淺)。"""
    rank = {"🌊 大浪/第三浪": 0, "📈 月線三連陽": 1, "🌱 醞釀(深跌剛金叉·即將起漲)": 2,
            "🚀 起漲(剛金叉)": 3, "〰️ 整理": 4, "資料不足": 5}
    out = []
    for t in tickers:
        dates, closes = load_daily(t, data_dir=data_dir)
        if not closes:
            continue
        r = classify(dates, closes)
        r["ticker"] = t
        out.append(r)
    out.sort(key=lambda r: (rank.get(r["stage"], 9), -r["green_months"], -r["dist_ath_pct"]))
    return out


def main(argv: Optional[list[str]] = None) -> int:
    import sys
    argv = list(sys.argv[1:] if argv is None else argv)
    if len(argv) < 2:
        print("用法:\n"
              "  python -m sharks.data.warehouse sync <scope|tickers>   # 增量更新 EOD→Parquet\n"
              "  python -m sharks.data.warehouse scan <scope|tickers>   # 本地算月線型態\n"
              "  (需 yfinance + pandas;scope 如 supercycle/space/universe 或 NVDA,MU,...)",
              file=sys.stderr)
        return 2
    cmd, target = argv[0], argv[1]
    tickers = _resolve_tickers(target)
    if cmd == "sync":
        ok_n = added = 0
        for i, t in enumerate(tickers, 1):
            ok, n = update_cache(t)
            ok_n += int(ok); added += n
            if i % 25 == 0:
                print(f"  …{i}/{len(tickers)}", file=sys.stderr)
        print(f"✅ 同步 {ok_n}/{len(tickers)} 檔,新增 {added} 列 → {DATA_DIR}")
        return 0
    if cmd == "scan":
        rows = scan(tickers)
        hot = [r for r in rows if r["stage"].startswith(("🌊", "📈", "🌱"))]
        print(f"📊 月線型態掃描 {len(rows)} 檔(已快取);大浪/三連陽/醞釀候選 {len(hot)}:")
        for r in rows[:40]:
            print(f"  {r['ticker']:<6} 距高{r['dist_ath_pct']:>4.0f}% 月陽{r['green_months']} "
                  f"金叉{'Y' if r['golden_cross'] else '-'} · {r['stage']}")
        print("recommend-only · 月線歷史本地算 · 永不下單")
        return 0
    print(f"未知指令:{cmd}(用 sync 或 scan)", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
