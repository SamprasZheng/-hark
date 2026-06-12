"""上漲 DNA — 大波段基因萃取 + 20 年月線回測 + 九轉/瘋狂延續研究 + regime 推演.

主理人指令(2026-06-12):用本地月線湖(decades, data/lake/prices/*_1mo.parquet)
找「上漲 DNA」(TSLA 2020 / NVDA·META·GOOGL 2022 / MU 2025 / SIVEF·LITE·COHR 2026),
回答:月線神奇九轉有沒有用?月線瘋狂(blow-off)之後買盤是否延續(最後一隻老鼠基率)?
大底怎麼抄?2026-27 還能不能看多(馬可夫 + 蒙地卡羅 + run-length 存活率)?
「如果每天都買 rally 推薦」的歷史績效近似?

llm_involvement: none — 全部 rule-based(符合 docs/LLM-BACKTEST-PROTOCOL.md 的
headline-KPI 資格;LLM 只設計了規則,不在回測迴圈內做任何分類/回憶)。

誠實揭露(寫進輸出 JSON,報告必須引用):
  1. 倖存者偏差 — 宇宙 = 今日 FOM universe(倖存者),絕對報酬高估;
     以「超額 vs QQQ」與勝率為主要讀數,絕對值僅供量級參考。
  2. Finviz 9 維的新聞/籌碼/基本面維度沒有歷史快照 — 20 年回測只能用
     價量近似「技術 + 資金」兩維;這是 rally 訊號的下界近似,不是全系統重演。
  3. 月線最後一根 bar 為當月 partial → 一律丟棄(point-in-time)。
  4. 出場用訊號當月收盤(略樂觀半根 bar);進場用次月開盤(無前視)。

CLI:
    python -m sharks.backtest.rally_dna            # 全研究 → outputs/rally-dna-<as_of>.json
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

# ── tunables(紀律參數;2026-06-12 網格校準,見 outputs/rally-dna-*.json tuning_note)──
# 網格 (kill_dd × vol_x) 全組合 win 44-46%、median ≈ -4% → 穩健非刀鋒。兩個 preset:
#   broad(預設): 抓到 7/8 點名大波段(TSLA20/NVDA22/.../LITE26)— 上漲 DNA 本體
#   deep:        深殺+量能閘,單筆期望最高(超額 +49.8%/筆)但案例捕捉 1/8
KILL_DD = -0.35           # broad:距 36 個月高 ≥35% 跌幅(點名案例中位數 -44%)
KILL_WINDOW = 18          # 「曾被殺」回看月數
MA_M = 10                 # 月線生命線(10 個月 ≈ 200 日)
VOL_X = 1.0               # broad:不設量能閘(月量數據噪音大,會 miss 2022 級底)
DEEP_KILL_DD = -0.55      # deep preset
DEEP_VOL_X = 1.3
COST_RT_PCT = 0.4         # 來回交易成本+滑價(0.2%/邊,美股流動股保守估)
MAX_HOLD_M = 36           # 最長持有月數
BLOWOFF_R6 = 0.80         # 瘋狂:6 個月 +80%
BLOWOFF_EXT = 1.40        # 且收盤 ≥ 1.4 × MA12
ERAS = [(2005, 2009), (2010, 2014), (2015, 2019), (2020, 2022), (2023, 2026)]

CASES = {                  # 主理人點名的大波段(研究視窗,起點~趨勢前,終點~波段尾/今)
    "TSLA": ("2019-01-01", "2021-02-01"),
    "NVDA": ("2022-01-01", "2024-07-01"),
    "META": ("2022-01-01", "2024-07-01"),
    "GOOGL": ("2022-01-01", "2024-07-01"),
    "MU": ("2024-06-01", "2026-06-01"),
    "SIVEF": ("2025-01-01", "2026-06-01"),
    "LITE": ("2025-01-01", "2026-06-01"),
    "COHR": ("2025-01-01", "2026-06-01"),
}


# ── data ──

def load_monthly(ticker: str, lake: Path = LAKE) -> Optional[pd.DataFrame]:
    p = lake / "prices" / f"{ticker}_1mo.parquet"
    if not p.exists():
        return None
    try:
        df = pd.read_parquet(p)
    except Exception:
        return None
    if df is None or df.empty or "Close" not in df:
        return None
    return df.iloc[:-1] if len(df) > 1 else None   # 丟當月 partial bar(PIT)


def monthly_universe(lake: Path = LAKE) -> list[str]:
    return sorted({p.stem.rsplit("_", 1)[0] for p in (lake / "prices").glob("*_1mo.parquet")})


# ── 月線神奇九轉(DeMark setup count)──

def td_setup_counts(close: pd.Series, direction: str = "sell") -> pd.Series:
    """連續 N 根月收 vs 4 根前比較的計數(sell: close>close[-4];buy: <)。9 = setup 完成。"""
    cmp = close > close.shift(4) if direction == "sell" else close < close.shift(4)
    cnt = pd.Series(0, index=close.index, dtype=int)
    run = 0
    for i, ok in enumerate(cmp.fillna(False).tolist()):
        run = run + 1 if ok else 0
        cnt.iloc[i] = run
    return cnt


def _fwd_stats(close: pd.Series, idx: list[int], horizons=(3, 6, 12)) -> dict:
    """事件月 → 前向報酬 / 12 個月內最大回撤 / 最大漲幅(以事件月收盤為基準)。"""
    rows = []
    for i in idx:
        if i + 12 >= len(close):
            continue
        c0 = float(close.iloc[i])
        if not c0 > 0:
            continue
        fwd = close.iloc[i + 1:i + 13]
        r = {f"r{h}m": float(close.iloc[i + h] / c0 - 1) for h in horizons}
        r["max_dd_12m"] = float(fwd.min() / c0 - 1)
        r["max_gain_12m"] = float(fwd.max() / c0 - 1)
        rows.append(r)
    if not rows:
        return {"n": 0}
    d = pd.DataFrame(rows)
    out = {"n": len(d)}
    for k in d.columns:
        out[f"median_{k}"] = round(float(d[k].median()) * 100, 1)
        out[f"mean_{k}"] = round(float(d[k].mean()) * 100, 1)
    out["pct_r6m_pos"] = round(float((d["r6m"] > 0).mean()) * 100, 1)
    out["pct_r12m_pos"] = round(float((d["r12m"] > 0).mean()) * 100, 1)
    return out


def study_td9(universe: list[str]) -> dict:
    """月線九轉 sell/buy setup 完成後的前向統計 vs 全樣本基線。"""
    ev = {"sell9": [], "buy9": [], "baseline": []}
    per_close: list[tuple[pd.Series, dict]] = []
    for t in universe:
        df = load_monthly(t)
        if df is None or len(df) < 30:
            continue
        close = df["Close"]
        s9 = td_setup_counts(close, "sell")
        b9 = td_setup_counts(close, "buy")
        per_close.append((close, {"sell9": [i for i in range(len(close)) if s9.iloc[i] == 9],
                                  "buy9": [i for i in range(len(close)) if b9.iloc[i] == 9],
                                  "baseline": list(range(20, len(close) - 13, 6))}))
    out = {}
    for key in ("sell9", "buy9", "baseline"):
        rows = []
        for close, idxs in per_close:
            st = _fwd_stats(close, idxs[key])
            if st["n"]:
                rows.append(st)
        if not rows:
            out[key] = {"n": 0}
            continue
        d = pd.DataFrame(rows)
        n = int(d["n"].sum())
        w = d["n"] / n
        out[key] = {"n_events": n,
                    **{c: round(float((d[c] * w).sum()), 1)
                       for c in d.columns if c != "n"}}
    return out


# ── 月線瘋狂(blow-off)延續研究 — 最後一隻老鼠的基率 ──

def blowoff_flags(df: pd.DataFrame) -> pd.Series:
    close = df["Close"]
    r6 = close / close.shift(6) - 1
    ma12 = close.rolling(12).mean()
    return (r6 >= BLOWOFF_R6) & (close >= BLOWOFF_EXT * ma12)


def study_blowoff(universe: list[str]) -> dict:
    rows = []
    for t in universe:
        df = load_monthly(t)
        if df is None or len(df) < 30:
            continue
        f = blowoff_flags(df)
        # 只取「進入瘋狂」的第一個月(連續旗標去重)
        idx = [i for i in range(1, len(f)) if bool(f.iloc[i]) and not bool(f.iloc[i - 1])]
        st = _fwd_stats(df["Close"], idx)
        if st["n"]:
            rows.append(st)
    if not rows:
        return {"n_events": 0}
    d = pd.DataFrame(rows)
    n = int(d["n"].sum())
    w = d["n"] / n
    return {"n_events": n,
            **{c: round(float((d[c] * w).sum()), 1) for c in d.columns if c != "n"}}


# ── 上漲 DNA 觸發 + 20 年月線回測 ──

def dna_trigger(df: pd.DataFrame, kill_dd: Optional[float] = None,
                vol_x: Optional[float] = None) -> pd.Series:
    """大底修復觸發(PIT):曾被殺 + 站回 MA10(近 2 個月內上穿)+ 連 2 月收高
    + 月量閘(vol_x>1 時)。全部只用 ≤t 的資料。"""
    kill_dd = KILL_DD if kill_dd is None else kill_dd
    vol_x = VOL_X if vol_x is None else vol_x
    close, vol = df["Close"], df.get("Volume")
    ma = close.rolling(MA_M).mean()
    dd36 = close / close.rolling(36, min_periods=12).max() - 1
    killed = dd36.rolling(KILL_WINDOW, min_periods=1).min() <= kill_dd
    above = close > ma
    crossed_recently = (~above.shift(1).fillna(False)) | (~above.shift(2).fillna(False))
    two_up = (close > close.shift(1)) & (close.shift(1) > close.shift(2))
    if vol_x > 1.0 and vol is not None and vol.notna().sum() > 24:
        vol_ok = vol >= vol_x * vol.rolling(12).median()
    else:
        vol_ok = pd.Series(True, index=close.index)
    return (killed & above & crossed_recently & two_up & vol_ok).fillna(False)


def entry_evidence(df: pd.DataFrame, i: int) -> dict:
    """進場月的「底層證據」(全 PIT):深殺 / 月線 buy-9 枯竭 / 量縮吸籌。
    這些就是貝葉斯引擎的條件 — 回測會輸出 P(win | 證據數) 的經驗似然表。"""
    close, vol = df["Close"], df.get("Volume")
    dd36 = close / close.rolling(36, min_periods=12).max() - 1
    deep = bool(dd36.iloc[max(0, i - KILL_WINDOW):i + 1].min() <= DEEP_KILL_DD)
    b9 = td_setup_counts(close.iloc[:i + 1], "buy")
    buy9 = bool(b9.iloc[max(0, i - 9):].max() >= 7)        # 近 9 個月內出現 ≥7 連弱(枯竭)
    vc = False
    if vol is not None and vol.notna().sum() > 27:
        v3 = vol.iloc[max(0, i - 2):i + 1].mean()
        v24 = vol.iloc[max(0, i - 23):i + 1].mean()
        vc = bool(v24 > 0 and v3 < 0.75 * v24)             # 觸發前量縮(吸籌期特徵)
    return {"deep_kill": deep, "buy9_exhaust": buy9, "vol_contract": vc,
            "n_evidence": int(deep) + int(buy9) + int(vc)}


def backtest_dna(universe: list[str], qqq_close: Optional[pd.Series] = None,
                 kill_dd: Optional[float] = None, vol_x: Optional[float] = None) -> dict:
    """逐檔:觸發 → 次月開盤進場 → 跌破 MA10 當月收盤出場(或滿 36 個月)。"""
    trades = []
    for t in universe:
        df = load_monthly(t)
        if df is None or len(df) < 48 or "Open" not in df:
            continue
        trig = dna_trigger(df, kill_dd=kill_dd, vol_x=vol_x)
        close, opn = df["Close"], df["Open"]
        ma = close.rolling(MA_M).mean()
        i, n = 0, len(df)
        while i < n - 2:
            if not bool(trig.iloc[i]):
                i += 1
                continue
            e = i + 1                                   # 次月
            entry = float(opn.iloc[e])
            if not entry > 0:
                i += 1
                continue
            j_exit = None
            for j in range(e, min(e + MAX_HOLD_M, n)):
                if float(close.iloc[j]) < float(ma.iloc[j]):
                    j_exit = j
                    break
            j_exit = j_exit if j_exit is not None else min(e + MAX_HOLD_M, n) - 1
            px = close.iloc[e:j_exit + 1]
            ret = float(close.iloc[j_exit] / entry - 1)
            ev = entry_evidence(df, i)
            tr = {"ticker": t,
                  "entry": str(df.index[e].date()), "exit": str(df.index[j_exit].date()),
                  "months": j_exit - e + 1, "ret_pct": round(ret * 100, 1),
                  "max_gain_pct": round(float(px.max() / entry - 1) * 100, 1),
                  "max_dd_pct": round(float(px.min() / entry - 1) * 100, 1),
                  "n_evidence": ev["n_evidence"], **{k: ev[k] for k in
                  ("deep_kill", "buy9_exhaust", "vol_contract")}}
            if qqq_close is not None:
                q = qqq_close.reindex(df.index[[e, j_exit]], method="nearest")
                if q.notna().all() and float(q.iloc[0]) > 0:
                    tr["excess_vs_qqq_pct"] = round((ret - (float(q.iloc[1] / q.iloc[0]) - 1)) * 100, 1)
            trades.append(tr)
            i = j_exit + 1                               # 出場後才可再進
    if not trades:
        return {"n_trades": 0}
    d = pd.DataFrame(trades)

    def agg(sub: pd.DataFrame) -> dict:
        if sub.empty:
            return {"n": 0}
        net = sub["ret_pct"] - COST_RT_PCT
        out = {"n": len(sub),
               "win_rate_pct": round(float((sub["ret_pct"] > 0).mean()) * 100, 1),
               "mean_ret_pct": round(float(sub["ret_pct"].mean()), 1),
               "median_ret_pct": round(float(sub["ret_pct"].median()), 1),
               "mean_net_ret_pct": round(float(net.mean()), 1),       # 扣 0.4% 來回成本
               "median_net_ret_pct": round(float(net.median()), 1),
               "p10_ret_pct": round(float(sub["ret_pct"].quantile(.1)), 1),
               "p90_ret_pct": round(float(sub["ret_pct"].quantile(.9)), 1),
               "mean_months": round(float(sub["months"].mean()), 1),
               "median_max_dd_pct": round(float(sub["max_dd_pct"].median()), 1)}
        if "excess_vs_qqq_pct" in sub and sub["excess_vs_qqq_pct"].notna().any():
            out["mean_excess_vs_qqq_pct"] = round(float(sub["excess_vs_qqq_pct"].mean()), 1)
            out["pct_beat_qqq"] = round(float((sub["excess_vs_qqq_pct"] > 0).mean()) * 100, 1)
        return out

    yr = d["entry"].str.slice(0, 4).astype(int)
    by_era = {f"{a}-{b}": agg(d[(yr >= a) & (yr <= b)]) for a, b in ERAS}
    # walk-forward 框架:參數用 2019+ 點名案例校準 → 2005-2018 進場 = 真 out-of-sample
    walk_forward = {"oos_2005_2018": agg(d[yr <= 2018]), "is_2019_2026": agg(d[yr >= 2019]),
                    "note": "broad 參數以 2019-2026 案例捕捉率選定;2005-2018 為未見資料"}
    # 經驗貝葉斯似然表:P(win / 期望報酬 | 底層證據數) — 證據越多,後驗越高?讓數據說話
    by_evidence = {f"evidence_{k}": agg(d[d["n_evidence"] == k]) for k in sorted(d["n_evidence"].unique())}
    by_single = {k: agg(d[d[k]]) for k in ("deep_kill", "buy9_exhaust", "vol_contract")}
    top = d.sort_values("ret_pct", ascending=False).head(8).to_dict("records")
    worst = d.sort_values("ret_pct").head(5).to_dict("records")
    return {"n_trades": len(d), "overall": agg(d), "by_era": by_era,
            "walk_forward": walk_forward,
            "bayes_by_evidence_count": by_evidence, "bayes_by_single_evidence": by_single,
            "top_trades": top, "worst_trades": worst}


# ── 點名大波段的 DNA 指紋 ──

def case_fingerprint(t: str, win: tuple[str, str]) -> Optional[dict]:
    df = load_monthly(t)
    if df is None or len(df) < 24:
        return None
    close = df["Close"]
    seg = close.loc[win[0]:win[1]]
    if seg.empty:
        return None
    trough_dt = seg.idxmin()
    i_tr = int(close.index.get_loc(trough_dt))
    ath_before = float(close.iloc[:i_tr + 1].max())
    ma = close.rolling(MA_M).mean()
    below = (close < ma).iloc[:i_tr + 1][::-1]
    base_months = int(below.cummin().sum()) if len(below) else 0   # 谷底前連續低於 MA10 的月數
    trig = dna_trigger(df)
    after = [k for k in range(i_tr, len(df)) if bool(trig.iloc[k])]
    peak_after = float(close.iloc[i_tr:].loc[:win[1]].max()) if i_tr < len(close) else None
    out = {"ticker": t, "trough": str(trough_dt.date()),
           "dd_from_ath_pct": round((float(close.iloc[i_tr]) / ath_before - 1) * 100, 1) if ath_before > 0 else None,
           "base_months_below_ma10": base_months,
           "trough_to_window_peak_pct": round((peak_after / float(close.iloc[i_tr]) - 1) * 100, 1) if peak_after else None}
    if after:
        k = after[0]
        out["dna_trigger"] = str(df.index[k].date())
        out["months_trough_to_trigger"] = k - i_tr
        out["trough_to_trigger_pct"] = round((float(close.iloc[k]) / float(close.iloc[i_tr]) - 1) * 100, 1)
        peak_seg = close.iloc[k:]
        out["trigger_to_peak_pct"] = round((float(peak_seg.max()) / float(close.iloc[k]) - 1) * 100, 1)
    else:
        out["dna_trigger"] = None
    return out


# ── 系統性案例發掘(阿卡西記憶 v2:25 年 × 各板塊 × 大小型 自動挖牛票)──
# 主理人指令(2026-06-12):點名 7 案只是舉例 — 要從歷史自動找 top 牛票建案例庫。
# 板塊標籤用今日 GICS(⚠ 僅作多樣性抽樣,不進訊號 — 09-point-in-time 揭露);
# 規模用谷底時的月成交額(價×量,PIT)分桶,不用今日市值。

CASE_MIN_KILL = -0.30     # 案例資格:谷底前曾被殺 ≥30%
CASE_MIN_GAIN = 1.0       # 案例資格:谷底後 24 個月內 ≥+100%
CASE_SECTOR_CAP = 3       # 每時代每板塊最多 3 檔(避免單一板塊壟斷記憶)


def discover_bull_cases(universe: list[str], top_per_era: int = 10,
                        loader=None, sector_of=None) -> dict:
    """全湖掃描:被殺 ≥30% 的局部谷底 + 24 個月 ≥+100% → 依時代取 top(板塊上限 3)
    → 在谷底後找 DNA 式觸發月 → 抽特徵。回傳案例庫 + 質心(全體/深殺/淺基兩型)。"""
    loader = loader or load_monthly
    if sector_of is None:
        from sharks.scoring.ma_scanner import load_sector
        sector_of = load_sector
    events = []
    for t in universe:
        df = loader(t)
        if df is None or len(df) < 60:
            continue
        close, vol = df["Close"], df.get("Volume")
        dd = close / close.rolling(36, min_periods=12).max() - 1
        ma = close.rolling(MA_M).mean()
        is_trough = (dd <= CASE_MIN_KILL) & (close == close.rolling(13, center=True, min_periods=7).min())
        n = len(close)
        for i in [k for k in range(12, n - 13) if bool(is_trough.iloc[k])]:
            c0 = float(close.iloc[i])
            if not c0 > 0:
                continue
            fwd = close.iloc[i + 1:min(i + 25, n)]
            gain = float(fwd.max() / c0 - 1)
            if gain < CASE_MIN_GAIN:
                continue
            trig = None
            for k in range(i + 1, min(i + 13, n)):
                if (float(close.iloc[k]) > float(ma.iloc[k])
                        and float(close.iloc[k]) > float(close.iloc[k - 1]) > float(close.iloc[k - 2])):
                    trig = k
                    break
            if trig is None:
                continue
            f = dna_features(df, trig)
            if f is None:
                continue
            dv = float((close.iloc[i] * vol.iloc[i])) if vol is not None and pd.notna(vol.iloc[i]) else None
            events.append({"ticker": t, "trough": str(df.index[i].date()),
                           "trigger": str(df.index[trig].date()),
                           "year": int(str(df.index[i])[:4]), "gain_24m_pct": round(gain * 100, 1),
                           "dollar_vol_at_trough": dv, **f})
    if not events:
        return {"n_cases": 0}
    d = pd.DataFrame(events)
    # 每 ticker 每時代留最大漲幅那次
    d["era"] = d["year"].map(lambda y: next((f"{a}-{b}" for a, b in ERAS if a <= y <= b), "pre-2005"))
    d = d.sort_values("gain_24m_pct", ascending=False).drop_duplicates(["ticker", "era"])
    # 規模分桶(谷底月成交額三分位,PIT)
    dv = d["dollar_vol_at_trough"]
    q1, q2 = dv.quantile(.33), dv.quantile(.67)
    d["size_bucket"] = np.where(dv <= q1, "small", np.where(dv <= q2, "mid", "large"))
    picks = []
    for era, sub in d.groupby("era"):
        sub = sub.sort_values("gain_24m_pct", ascending=False)
        used: dict[str, int] = {}
        for _, r in sub.iterrows():
            sec = sector_of(r["ticker"]) or "Unknown"
            if used.get(sec, 0) >= CASE_SECTOR_CAP:
                continue
            used[sec] = used.get(sec, 0) + 1
            picks.append({**r.to_dict(), "sector": sec})
            if sum(used.values()) >= top_per_era:
                break
    lib = pd.DataFrame(picks)

    def centroid(sub: pd.DataFrame) -> dict:
        return {k: round(float(sub[k].median()), 3) for k in MATCH_FEATS
                if k in sub and sub[k].notna().any()}

    deep = lib[lib["dd_min18"] <= DEEP_KILL_DD]
    shallow = lib[lib["dd_min18"] > DEEP_KILL_DD]
    return {"n_cases": len(lib),
            "by_era": lib["era"].value_counts().to_dict(),
            "by_size": lib["size_bucket"].value_counts().to_dict(),
            "by_sector": lib["sector"].value_counts().head(8).to_dict(),
            "median_gain_24m_pct": round(float(lib["gain_24m_pct"].median()), 1),
            "centroid_all": centroid(lib),
            "centroid_deep_kill": centroid(deep) if len(deep) >= 5 else None,
            "centroid_shallow_base": centroid(shallow) if len(shallow) >= 5 else None,
            "n_deep": len(deep), "n_shallow": len(shallow),
            "cases": lib.sort_values("gain_24m_pct", ascending=False).head(60).to_dict("records"),
            "disclosure": "板塊=今日標籤僅作抽樣多樣性(09-PIT 揭露);規模=谷底月成交額(PIT)"}


# ── DNA 匹配器(質心 → 今天全宇宙最近鄰;v2 可注入案例庫質心 + Finviz 三面)──

MATCH_FEATS = ("dd36", "dist_ma10", "buy9_max", "r3m", "vol_ratio")


def dna_features(df: pd.DataFrame, i: int) -> Optional[dict]:
    """月 i 的 DNA 特徵向量(全 PIT):距 36 月高、距 MA10、buy-9 枯竭度、3 月修復動能、
    量能比。供案例質心與今日匹配共用 — 同一把尺。"""
    if i < 36:
        return None
    close, vol = df["Close"], df.get("Volume")
    c = float(close.iloc[i])
    ma = close.rolling(MA_M).mean()
    if pd.isna(ma.iloc[i]) or not c > 0:
        return None
    dd36 = c / float(close.iloc[max(0, i - 35):i + 1].max()) - 1
    dd_min18 = float((close / close.rolling(36, min_periods=12).max() - 1)
                     .iloc[max(0, i - KILL_WINDOW + 1):i + 1].min())
    b9 = td_setup_counts(close.iloc[:i + 1], "buy")
    vc = None
    if vol is not None and vol.notna().sum() > 27:
        v24 = float(vol.iloc[max(0, i - 23):i + 1].mean())
        vc = float(vol.iloc[i - 2:i + 1].mean()) / v24 if v24 > 0 else None
    return {"dd36": round(dd36, 3), "dd_min18": round(dd_min18, 3),
            "dist_ma10": round(c / float(ma.iloc[i]) - 1, 3),
            "buy9_max": int(b9.iloc[max(0, i - 9):].max()),
            "r3m": round(c / float(close.iloc[i - 3]) - 1, 3),
            "vol_ratio": round(vc, 3) if vc is not None else None}


def named_case_centroid() -> Optional[dict]:
    """主理人點名 7 案例的觸發月質心(保留作對照;主質心改用 discover 案例庫)。"""
    targets = []
    for t, w in CASES.items():
        fp = case_fingerprint(t, w)
        if not fp or not fp.get("dna_trigger"):
            continue
        df = load_monthly(t)
        dates = [str(x.date()) for x in df.index]
        if fp["dna_trigger"] not in dates:
            continue
        f = dna_features(df, dates.index(fp["dna_trigger"]))
        if f:
            targets.append(f)
    if not targets:
        return None
    tgt = pd.DataFrame(targets)
    return {k: float(tgt[k].median()) for k in MATCH_FEATS if k in tgt}


def enrich_with_finviz(tickers: list[str]) -> dict[str, dict]:
    """Finviz Elite 現況快照:三面 dims + 原始機構/內部人流向(反身性懲罰用)。"""
    try:
        from sharks.data.finviz_elite import (DIMENSION_COLUMNS, DIMENSION_VIEW, _num,
                                              fetch_universe, finviz_row_to_dims)
        try:
            from sharks.discord.config import PROJECT_ROOT, _read_dotenv
            _read_dotenv(PROJECT_ROOT / ".env")
        except Exception:
            pass
        out = {}
        for fr in fetch_universe(tickers, view=DIMENSION_VIEW, columns=DIMENSION_COLUMNS):
            tk = (fr.get("Ticker") or "").upper()
            if tk:
                out[tk] = {**finviz_row_to_dims(fr),
                           "inst_trans": _num(fr, "Inst Trans", "Institutional Transactions"),
                           "insider_trans": _num(fr, "Insider Trans", "Insider Transactions")}
        return out
    except Exception:
        return {}


# v2.1 權重(2026-06-12 review):消息(noisy 且 Finviz 常 None)→ 換成反身性懲罰。
# ⚠ 權重 = 顯式先驗,非擬合 — Finviz 維度無歷史快照,無法誠實回測;
# 每次評分落盤 outputs/dna-scores-log.jsonl,累積後用實際前向報酬做前瞻校準。
WEIGHTS_V21 = {"tech": 0.40, "fundamental": 0.30, "capital": 0.20, "reflexivity": 0.10}
REFLEX_FACTOR = {"回饋健康": 1.0, "n/a(未近高)": 0.75, "數據缺": 0.5,
                 "背離觀察": 0.25, "斷裂警告": 0.0}
ENTER_SCORE, WATCH_SCORE = 85.0, 75.0    # >85 可入候補(仍走燃料閘);>75 watch
RULES_PATH = Path("config/dna_rules.json")


def load_rules() -> list[dict]:
    try:
        return json.loads(RULES_PATH.read_text(encoding="utf-8")).get("rules", [])
    except Exception:
        return []


def apply_rules(row: dict, ctx: dict, rules: list[dict]) -> dict:
    """宣告式規則:when 全等值匹配(row ∪ ctx)→ 套用 then。純函式,順序執行。"""
    scope = {**ctx, **row}
    for r in rules:
        if all(scope.get(k) == v for k, v in (r.get("when") or {}).items()):
            for k, v in (r.get("then") or {}).items():
                row[k] = v
            row.setdefault("rules_fired", []).append(r.get("id"))
            scope = {**ctx, **row}
    return row


def latest_pit_contested() -> dict[str, bool]:
    """最新 pit-merged/pit-fundamentals 輸出的「PIT 翻案爭議」標記(有拉過 PIT 的票才有)。"""
    out: dict[str, bool] = {}
    for prefix in ("pit-merged", "pit-fundamentals"):
        files = sorted(Path("outputs").glob(f"{prefix}-*.json"))
        if not files:
            continue
        try:
            d = json.loads(files[-1].read_text(encoding="utf-8"))
            for t, v in (d.get("tickers") or {}).items():
                if isinstance(v, dict) and v.get("pit_fundamental_contested") is not None:
                    out[t] = bool(v["pit_fundamental_contested"])
        except Exception:
            continue
    return out


def dna_match_today(universe: list[str], top_n: int = 25,
                    centroid: Optional[dict] = None, enrich: bool = True,
                    library_cases: Optional[list[dict]] = None,
                    failed_cases: Optional[list[dict]] = None,
                    market_state: Optional[str] = None) -> dict:
    """今天誰最像歷史贏家的起漲點:案例庫質心 z-score 最近鄰(技術/量能歷史相似度)
    + Finviz 三面(基本面/資金買盤/消息,現況)→ dna_plus 綜合分。
    門檻:近 18 個月內曾被殺 ≥30%。recommend-only。"""
    if centroid is None:
        centroid = named_case_centroid()
    if not centroid:
        return {"n_candidates": 0, "error": "no case targets"}

    rows = []
    for t in universe:
        df = load_monthly(t)
        if df is None or len(df) < 40:
            continue
        f = dna_features(df, len(df) - 1)
        if f is None or f["dd_min18"] > -0.30:
            continue
        f["triggered_recent"] = bool(dna_trigger(df).iloc[-2:].any())
        rows.append({"ticker": t, **f})
    if not rows:
        return {"n_candidates": 0}
    d = pd.DataFrame(rows)
    z = pd.DataFrame(index=d.index)
    tz, stats = {}, {}
    for k in MATCH_FEATS:
        col = d[k].astype(float)
        col = col.fillna(col.median())
        mu, sd = float(col.mean()), float(col.std()) or 1.0
        stats[k] = (mu, sd)
        z[k] = (col - mu) / sd
        tz[k] = (centroid[k] - mu) / sd
    d["dna_distance"] = np.sqrt(sum((z[k] - tz[k]) ** 2 for k in MATCH_FEATS))
    d = d.sort_values("dna_distance").head(max(top_n * 2, 50))
    dims = enrich_with_finviz(d["ticker"].tolist()) if enrich else {}
    for col in ("fundamental", "capital", "inst_trans", "insider_trans"):
        d[col] = d["ticker"].map(lambda t: (dims.get(t) or {}).get(col))

    # 反身性懲罰:near-high 用 52 週高距離(最新 ma-scan;HUM 級衝突在 52w 不在 36m),
    # 缺 ma-scan 時退回 dd36 近似;資金腿斷者抓 FCF 第二腿(限額)
    from sharks.scoring.reflexivity import _fcf_yoy, reflexivity_state
    d52: dict[str, float] = {}
    try:
        scan_files = sorted(p for p in Path("outputs").glob("ma-scan-*.json")
                            if "intraday" not in p.name)
        rows52 = json.loads(scan_files[-1].read_text(encoding="utf-8")).get("rows", {})
        d52 = {t: r.get("dist_52w_high_pct") for t, r in rows52.items()
               if r.get("dist_52w_high_pct") is not None}
    except Exception:
        pass
    fcf_budget = 10
    verdicts, fcfs = [], []
    for _, r in d.iterrows():
        dist_hi = d52.get(r["ticker"], float(r["dd36"]) * 100)
        fcf = None
        flow_bad = ((r["inst_trans"] is not None and not pd.isna(r["inst_trans"]) and r["inst_trans"] < 0)
                    or (r["insider_trans"] is not None and not pd.isna(r["insider_trans"]) and r["insider_trans"] <= -10))
        if flow_bad and dist_hi > -5 and fcf_budget > 0:
            fcf = _fcf_yoy(r["ticker"])
            fcf_budget -= 1
        st = reflexivity_state(dist_52w_high_pct=dist_hi,
                               inst_trans=None if pd.isna(r["inst_trans"]) else r["inst_trans"],
                               insider_trans=None if pd.isna(r["insider_trans"]) else r["insider_trans"],
                               fcf_yoy_pct=fcf)
        verdicts.append(st["verdict"])
        fcfs.append(fcf)
    d["reflexivity"] = verdicts
    d["fcf_yoy_pct"] = fcfs

    tech_pct = 1 - d["dna_distance"].rank(pct=True)               # 越像越高
    def pct(col):
        s = d[col].astype(float)
        return s.rank(pct=True).fillna(0.5) if s.notna().any() else pd.Series(0.5, index=d.index)
    reflex_f = d["reflexivity"].map(lambda v: REFLEX_FACTOR.get(v, 0.5))
    w = dict(WEIGHTS_V21)
    if market_state == "mania":            # 狀態感知:mania 提高反身性權重(v3 藍圖 §3)
        w["reflexivity"], w["capital"] = 0.15, 0.15
    fund_pct, cap_pct = pct("fundamental"), pct("capital")
    # SHAP 式貢獻分解(可解釋性 = 信賴核心):每維 = 權重 × 百分位 × 100
    d["c_tech"] = (w["tech"] * tech_pct * 100).round(1)
    d["c_fund"] = (w["fundamental"] * fund_pct * 100).round(1)
    d["c_capital"] = (w["capital"] * cap_pct * 100).round(1)
    d["c_reflex"] = (w["reflexivity"] * reflex_f * 100).round(1)
    d["dna_plus"] = (d["c_tech"] + d["c_fund"] + d["c_capital"] + d["c_reflex"]).round(1)
    d["archetype"] = np.where(d["dd_min18"] <= DEEP_KILL_DD, "deep_kill", "shallow_base")
    # 權重敏感度(索引對齊處計算):排名對權重穩健 → 分數只作分桶
    alt1 = 0.25 * tech_pct + 0.25 * fund_pct + 0.25 * cap_pct + 0.25 * reflex_f
    alt2 = 0.60 * tech_pct + 0.20 * fund_pct + 0.10 * cap_pct + 0.10 * reflex_f
    base_rank = d["dna_plus"].rank()
    sens = {"spearman_vs_equal_w": round(float(base_rank.corr(alt1.rank(), method="spearman")), 3),
            "spearman_vs_tech60": round(float(base_rank.corr(alt2.rank(), method="spearman")), 3),
            "top10_overlap_equal_w": len(set(d.nlargest(10, "dna_plus")["ticker"])
                                         & set(d.assign(s=alt1).nlargest(10, "s")["ticker"])),
            "note": "權重=顯式先驗非擬合;評分落盤累積後做前瞻校準"}
    # 最相似 Top3 歷史案例(成功 ∪ 失敗同池 — AXTI 型風險偵測)+ 實際後續報酬
    pool = ([{**c, "kind": "win", "ret_pct": c.get("gain_24m_pct")} for c in (library_cases or [])
             if all(c.get(k) is not None for k in MATCH_FEATS)]
            + [{**c, "kind": "fail", "ret_pct": c.get("end_ret_pct"),
                "trough": c.get("trigger")} for c in (failed_cases or [])
               if all(c.get(k) is not None for k in MATCH_FEATS)])
    sim_col, axti_col = [], []
    for _, r in d.iterrows():
        if not pool:
            sim_col.append([])
            axti_col.append(None)
            continue
        ds = []
        for c in pool:
            dist = sum(((float(c[k]) - stats[k][0]) / stats[k][1]
                        - float(z.loc[r.name, k])) ** 2 for k in MATCH_FEATS) ** 0.5
            ds.append((round(dist, 2), c))
        ds.sort(key=lambda x: x[0])
        top3 = [{"ticker": c["ticker"], "kind": c["kind"], "trough": c.get("trough"),
                 "ret_24m_pct": c.get("ret_pct"), "distance": dist} for dist, c in ds[:3]]
        sim_col.append(top3)
        axti_col.append(sum(1 for s in top3 if s["kind"] == "fail") >= 2)
    d["similar_cases"] = sim_col
    d["axti_risk"] = axti_col            # 近鄰 Top3 含 ≥2 失敗案例 → 規則升 human_review
    # 三欄分流 → 宣告式規則引擎(config/dna_rules.json;含 human_review)
    def base_bucket(row):
        if row["reflexivity"] == "斷裂警告":
            return "剔除"
        if row["dna_plus"] >= ENTER_SCORE:
            return "可入候補"
        if row["dna_plus"] >= WATCH_SCORE:
            return "watch"
        return "觀察"
    d["bucket"] = d.apply(base_bucket, axis=1)
    d = d.sort_values("dna_plus", ascending=False)
    rules, contested = load_rules(), latest_pit_contested()
    ctx = {"market_state": market_state}
    records = []
    for r in d.to_dict("records"):
        r["pit_fundamental_contested"] = contested.get(r["ticker"])
        records.append(apply_rules(r, ctx, rules))
    d = pd.DataFrame(records)
    return {"n_candidates": len(d), "finviz_enriched": bool(dims),
            "market_state": market_state,
            "case_centroid": {k: round(v, 3) for k, v in centroid.items()},
            "weights_effective": w, "thresholds": {"enter": ENTER_SCORE, "watch": WATCH_SCORE},
            "weight_sensitivity": sens,
            "bucket_counts": d["bucket"].value_counts().to_dict(),
            "top": [{**{k: (None if (isinstance(v, float) and pd.isna(v)) else v) for k, v in r.items()},
                     "dna_distance": round(float(r["dna_distance"]), 2)}
                    for r in d.head(top_n).to_dict("records")],
            "note": "v2.1:技術40+基本面30+買盤20+反身性懲罰10;斷裂警告無條件剔除;權重為先驗,評分落盤待前瞻校準。"}


# ── regime 推演:馬可夫 + 蒙地卡羅 + run-length 存活(QQQ 月線)──

def regime_monte_carlo(qqq: pd.DataFrame, months_ahead: int = 19, n_paths: int = 5000,
                       seed: int = 42) -> dict:
    close = qqq["Close"].tail(240)                      # 近 20 年
    ma = close.rolling(MA_M).mean()
    state = (close > ma).astype(int)                    # 1=bull(>MA10mo), 0=bear
    r_next = close.pct_change().shift(-1)
    pools = {s: r_next[(state == s) & r_next.notna()].values for s in (0, 1)}
    # 轉移矩陣
    tm = np.zeros((2, 2))
    sv = state.dropna().astype(int).values
    for a, b in zip(sv[:-1], sv[1:]):
        tm[a, b] += 1
    tm = tm / np.clip(tm.sum(axis=1, keepdims=True), 1, None)
    # run-length 存活:目前多頭已走 L 月 → P(再活 ≥12 月)
    runs, cur = [], 1
    for a, b in zip(sv[:-1], sv[1:]):
        if a == b == 1:
            cur += 1
        elif a == 1:
            runs.append(cur)
            cur = 1
    cur_run = 0
    for s in sv[::-1]:
        if s == 1:
            cur_run += 1
        else:
            break
    if cur_run and sv[-1] == 1:
        runs_arr = np.array(runs + [cur_run]) if runs else np.array([cur_run])
        ge_l = (runs_arr >= cur_run).sum()
        ge_l12 = (runs_arr >= cur_run + 12).sum()
        survival_12m = round(float(ge_l12 / ge_l) * 100, 1) if ge_l else None
    else:
        survival_12m = None
    # Monte Carlo
    rng = np.random.default_rng(seed)
    ends, mins, news = [], [], 0
    s0 = int(sv[-1])
    for _ in range(n_paths):
        s, lvl, mn, hi = s0, 1.0, 1.0, 1.0
        for _ in range(months_ahead):
            lvl *= 1.0 + float(rng.choice(pools[s]))
            mn, hi = min(mn, lvl), max(hi, lvl)
            s = int(rng.random() < tm[s, 1])
        ends.append(lvl)
        mins.append(mn)
        news += hi > 1.0001
    ends, mins = np.array(ends), np.array(mins)
    return {
        "asset": "QQQ", "months_ahead": months_ahead, "n_paths": n_paths,
        "current_state": "bull" if s0 else "bear", "bull_run_months": int(cur_run),
        "bull_run_survival_12m_pct": survival_12m,
        "transition": {"bull_stay": round(float(tm[1, 1]) * 100, 1),
                       "bear_stay": round(float(tm[0, 0]) * 100, 1)},
        "mc_end_return_pct": {"median": round(float(np.median(ends) - 1) * 100, 1),
                              "p10_worst": round(float(np.quantile(ends, .1) - 1) * 100, 1),
                              "p90_best": round(float(np.quantile(ends, .9) - 1) * 100, 1)},
        "mc_p_end_positive": round(float((ends > 1).mean()) * 100, 1),
        "mc_p_drawdown_ge_30": round(float((mins <= 0.70).mean()) * 100, 1),
        "mc_p_make_new_high": round(float(news / n_paths) * 100, 1),
    }


# ── 四態馬可夫(寬鬆牛 / 狂熱泡沫 / 緊縮熊 / 流動性枯竭)──

def classify_states4(close: pd.Series) -> pd.Series:
    """月線四態(全 PIT:波動分位用 expanding,不偷看未來):
    mania  狂熱泡沫  = 站上 MA10 且 12 個月 ≥ +35%
    bull   寬鬆牛市  = 站上 MA10(非狂熱)
    crisis 流動性枯竭 = 跌破 MA10 且 6 個月年化波動 ≥ 自身歷史 80 分位
    bear   緊縮熊市  = 跌破 MA10(非枯竭)"""
    ma = close.rolling(MA_M).mean()
    r12 = close / close.shift(12) - 1
    vol6 = close.pct_change().rolling(6).std() * np.sqrt(12)
    vhi = vol6.expanding(60).quantile(0.8)
    out = []
    for i in range(len(close)):
        if pd.isna(ma.iloc[i]):
            out.append(None)
            continue
        if close.iloc[i] > ma.iloc[i]:
            out.append("mania" if (not pd.isna(r12.iloc[i]) and r12.iloc[i] >= 0.35) else "bull")
        else:
            hi = vhi.iloc[i]
            out.append("crisis" if (not pd.isna(hi) and not pd.isna(vol6.iloc[i])
                                    and vol6.iloc[i] >= hi) else "bear")
    return pd.Series(out, index=close.index)


def regime_markov4(qqq: pd.DataFrame, months_ahead: int = 19, n_paths: int = 5000,
                   seed: int = 42) -> dict:
    """四態轉移矩陣 + 各態次月報酬池 + 蒙地卡羅(池空時退回 bull/bear 池)。"""
    close = qqq["Close"].tail(300)
    states = classify_states4(close).dropna()
    close = close.loc[states.index]
    r_next = close.pct_change().shift(-1)
    names = ["bull", "mania", "bear", "crisis"]
    pools = {s: r_next[(states == s) & r_next.notna()].values for s in names}
    fallback = {"mania": "bull", "crisis": "bear"}
    for s in names:
        if len(pools[s]) < 6 and s in fallback:
            pools[s] = pools[fallback[s]]
    tm = pd.DataFrame(0.0, index=names, columns=names)
    sv = states.tolist()
    for a, b in zip(sv[:-1], sv[1:]):
        tm.loc[a, b] += 1
    tm = tm.div(tm.sum(axis=1).replace(0, 1), axis=0)
    rng = np.random.default_rng(seed)
    cum = np.cumsum([tm.loc[s].values for s in names], axis=1)  # per-state cdf
    idx = {s: k for k, s in enumerate(names)}
    ends, mins = [], []
    s0 = sv[-1]
    for _ in range(n_paths):
        s, lvl, mn = s0, 1.0, 1.0
        for _ in range(months_ahead):
            lvl *= 1.0 + float(rng.choice(pools[s]))
            mn = min(mn, lvl)
            s = names[int(np.searchsorted(cum[idx[s]], rng.random()))]
        ends.append(lvl)
        mins.append(mn)
    ends, mins = np.array(ends), np.array(mins)
    dist = states.value_counts(normalize=True).round(3).to_dict()
    return {
        "asset": "QQQ", "states": names, "current_state": s0,
        "state_distribution_20y": dist,
        "transition_matrix": {a: {b: round(float(tm.loc[a, b]), 3) for b in names} for a in names},
        "state_mean_next_month_ret_pct": {s: round(float(np.mean(pools[s])) * 100, 2) for s in names},
        "mc_end_return_pct": {"median": round(float(np.median(ends) - 1) * 100, 1),
                              "p10_worst": round(float(np.quantile(ends, .1) - 1) * 100, 1),
                              "p90_best": round(float(np.quantile(ends, .9) - 1) * 100, 1)},
        "mc_p_end_positive": round(float((ends > 1).mean()) * 100, 1),
        "mc_p_drawdown_ge_30": round(float((mins <= 0.70).mean()) * 100, 1),
        "caveat": "iid-within-state 抽樣低估連環崩跌尾巴;曝險水位用狀態判讀,不用點估計",
    }


# ── 觸發點基本面指紋(深挖底層:錯殺=價殺、基本面/CapEx 未壞)──

def case_fundamentals(ticker: str, trigger_date: str) -> dict:
    """觸發當下「已公布」的年度財報(period_end ≤ trigger,PIT):營收 YoY、CapEx YoY、
    FCF 正負。驗證主理人假說:估值被壓但成長/資本支出路線圖未延遲 = 完美錯殺。
    yfinance 年報僅回溯 ~5 年 → 較舊案例會回 out_of_window。"""
    out = {"ticker": ticker, "trigger": trigger_date}
    try:
        import yfinance as yf
        tk = yf.Ticker(ticker)
        trig = pd.Timestamp(trigger_date)

        def yoy(df, labels):
            if df is None or getattr(df, "empty", True):
                return None, None
            row = None
            for lb in labels:
                if lb in df.index:
                    row = df.loc[lb]
                    break
            if row is None:
                return None, None
            pts = sorted(((pd.Timestamp(c), v) for c, v in row.items()
                          if pd.notna(v) and pd.Timestamp(c) <= trig), key=lambda x: x[0])
            if len(pts) < 2:
                return None, None
            (d0, v0), (d1, v1) = pts[-2], pts[-1]
            g = (v1 / v0 - 1) * 100 if v0 else None
            return (round(float(g), 1) if g is not None else None), str(d1.date())

        inc, cf = tk.income_stmt, tk.cashflow
        out["rev_yoy_pct"], out["fy_end_used"] = yoy(inc, ["Total Revenue", "Operating Revenue"])
        out["capex_yoy_pct"], _ = yoy(cf, ["Capital Expenditure", "Capital Expenditures"])
        fcf, _ = yoy(cf, ["Free Cash Flow"])
        out["fcf_yoy_pct"] = fcf
        if out["rev_yoy_pct"] is None:
            out["note"] = "out_of_window(yfinance 年報回溯不足)"
    except Exception as e:
        out["error"] = str(e)[:80]
    return out


# ── 5 年日線 rally 近似回測(「如果我每天都買推薦」)──

def daily_rally_backtest(universe: list[str], lake: Path = LAKE) -> dict:
    """技術閘近似 rally buy_consider:上穿 MA60 + 連 2 日收高 + 量 ≥1.5×20d 均量。
    次日開盤進,收盤跌破 MA20 出。僅近 5 年(日線湖深度)。"""
    trades = []
    sig_months: dict[str, int] = {}
    for t in universe:
        p = lake / "prices" / f"{t}_1d.parquet"
        if not p.exists():
            continue
        try:
            df = pd.read_parquet(p)
        except Exception:
            continue
        if df is None or len(df) < 130 or "Close" not in df or "Open" not in df:
            continue
        c, o, v = df["Close"], df["Open"], df.get("Volume")
        ma60, ma20 = c.rolling(60).mean(), c.rolling(20).mean()
        above = c > ma60
        cross = above & ~above.shift(1).fillna(False)
        two_up = (c > c.shift(1)) & (c.shift(1) > c.shift(2))
        vol_ok = (v >= 1.5 * v.rolling(20).mean()) if v is not None else pd.Series(True, index=c.index)
        trig = (cross & two_up & vol_ok).fillna(False)
        i, n = 0, len(df)
        while i < n - 2:
            if not bool(trig.iloc[i]):
                i += 1
                continue
            e = i + 1
            entry = float(o.iloc[e])
            if not entry > 0:
                i += 1
                continue
            j_exit = None
            for j in range(e, min(e + 120, n)):
                if float(c.iloc[j]) < float(ma20.iloc[j]):
                    j_exit = j
                    break
            j_exit = j_exit if j_exit is not None else min(e + 120, n) - 1
            ret = float(c.iloc[j_exit] / entry - 1)
            dt = df.index[e]
            sig_months[str(dt)[:7]] = sig_months.get(str(dt)[:7], 0) + 1
            trades.append({"ticker": t, "entry": str(dt.date()), "year": int(str(dt)[:4]),
                           "ret_pct": round(ret * 100, 2), "days": j_exit - e + 1})
            i = j_exit + 1
    if not trades:
        return {"n_trades": 0}
    d = pd.DataFrame(trades)

    def agg(sub):
        return {"n": len(sub),
                "win_rate_pct": round(float((sub["ret_pct"] > 0).mean()) * 100, 1),
                "mean_ret_pct": round(float(sub["ret_pct"].mean()), 2),
                "median_ret_pct": round(float(sub["ret_pct"].median()), 2),
                "mean_days": round(float(sub["days"].mean()), 1)} if len(sub) else {"n": 0}

    by_year = {int(y): agg(d[d["year"] == y]) for y in sorted(d["year"].unique())}
    sm = pd.Series(sig_months)
    return {"n_trades": len(d), "overall": agg(d), "by_year": by_year,
            "signals_per_month": {"mean": round(float(sm.mean()), 1), "max": int(sm.max()),
                                  "note": "每月訊號數 — 『每天都買』的實際下單頻率量級"}}


# ── main ──

def main(argv: Optional[list[str]] = None) -> int:
    uni = monthly_universe()
    if not uni:
        print("月線湖是空的 — 先跑 data_lake(period=max, 1mo)", file=sys.stderr)
        return 1
    print(f"rally-DNA 研究:月線湖 {len(uni)} 檔(全離線,rule-based)…", file=sys.stderr)
    qqq = load_monthly("QQQ")
    qqq_close = qqq["Close"] if qqq is not None else None

    cases = [c for c in (case_fingerprint(t, w) for t, w in CASES.items()) if c]
    dna = backtest_dna(uni, qqq_close)                                   # broad preset
    dna_deep = backtest_dna(uni, qqq_close, kill_dd=DEEP_KILL_DD, vol_x=DEEP_VOL_X)
    td9 = study_td9(uni)
    blow = study_blowoff(uni)
    mc = regime_monte_carlo(qqq) if qqq is not None else {}
    mc4 = regime_markov4(qqq) if qqq is not None else {}
    daily = daily_rally_backtest(uni)
    cases_fund = [case_fundamentals(c["ticker"], c["dna_trigger"])
                  for c in cases if c.get("dna_trigger")]          # 7 檔,網路
    library = discover_bull_cases(uni)                             # 系統性案例庫(25 年)
    failed_events = []
    fa_files = sorted(Path("outputs").glob("failed-analogs-*.json"))
    if fa_files:
        try:
            failed_events = json.loads(fa_files[-1].read_text(encoding="utf-8")).get("failed_events") or []
        except Exception:
            pass
    match = dna_match_today(uni, centroid=library.get("centroid_all") or None,
                            library_cases=library.get("cases"),
                            failed_cases=failed_events,
                            market_state=mc4.get("current_state"))

    as_of = None
    if qqq is not None:
        as_of = str(qqq.index[-1].date())
    report = {
        "as_of": as_of, "generated_at": datetime.now(timezone.utc).isoformat(),
        "engine": "rally-dna-offline-monthly", "llm_involvement": "none",
        "universe_n": len(uni),
        "params": {"kill_dd": KILL_DD, "ma_months": MA_M, "vol_x": VOL_X,
                   "blowoff": {"r6": BLOWOFF_R6, "ext_vs_ma12": BLOWOFF_EXT}},
        "dna_case_studies": cases,
        "dna_case_fundamentals": cases_fund,
        "case_library": library,
        "named_case_centroid": named_case_centroid(),
        "dna_match_today": match,
        "regime_markov4": mc4,
        "dna_backtest_20y": dna,
        "dna_backtest_20y_deep": dna_deep,
        "tuning_note": ("2026-06-12 網格 (kill_dd∈{-35,-45,-55}% × vol_x∈{1.0,1.3}):全組合 "
                        "win 44-46%、median≈-4% → 穩健。broad(-35%/1.0) 抓 7/8 點名案例;"
                        "deep(-55%/1.3) 單筆期望最高(超額+49.8%)但案例 1/8。兩 preset 並列。"),
        "td9_monthly": td9,
        "blowoff_continuation": blow,
        "regime_monte_carlo": mc,
        "daily_rally_5y": daily,
        "disclosures": [
            "倖存者偏差:宇宙=今日 FOM universe;絕對報酬高估,以超額 vs QQQ 與勝率為主讀數",
            "9 維中的新聞/籌碼/基本面無歷史快照 — 此為價量兩維的下界近似,非全系統重演",
            "月線當月 partial bar 一律丟棄;進場次月開盤、出場訊號當月收盤(略樂觀半根)",
            "llm_involvement: none(LLM-BACKTEST-PROTOCOL 合規)",
        ],
        "disclaimer": "recommend-only 研究;歷史基率非預測保證;永不下單。",
    }
    out = Path("outputs") / f"rally-dna-{as_of or datetime.now().strftime('%Y-%m-%d')}.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    # 評分落盤(前瞻校準資料集:累積 N 個月後用實際前向報酬擬合權重 — 唯一誠實的證據路徑)
    with (Path("outputs") / "dna-scores-log.jsonl").open("a", encoding="utf-8") as fh:
        fh.write(json.dumps({"as_of": as_of, "generated_at": report["generated_at"],
                             "weights": WEIGHTS_V21,
                             "rows": [{k: r.get(k) for k in ("ticker", "dna_plus", "dna_distance",
                                       "fundamental", "capital", "reflexivity", "bucket",
                                       "triggered_recent")} for r in match.get("top") or []]},
                            ensure_ascii=False) + "\n")
    print(f"wrote {out}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
