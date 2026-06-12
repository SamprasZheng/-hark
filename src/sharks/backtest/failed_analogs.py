"""Failed-analogs 子庫 — DeepKill 形態的「死掉的同類」與真實存活率.

風險登記簿最高優先(2026-06-12):案例庫只收了活下來的怪物 → deep-kill 分倉上限
(8% vs 15%)需要真實存活率才能數據驅動。本模組:

Phase 1(analyze,離線):湖內所有 deep-kill 觸發事件,**固定 24 個月視窗**分類結局:
    monster  ≥+100%(案例庫等級)     ok   +30%~+100%
    dud      -40%~+30%(死水)        disaster ≤-40% 或途中 max_dd ≤-50%
  survival = (monster+ok) 占比;sizing 上限用透明公式從分布導出(見 cap_recommendation)。

Phase 2(collect,網路):Polygon delisted 票(下市=湖外的真亡者)逐批收月線到
  data/lake/failed/,跑同樣觸發偵測 → 補進分母。免費層 5 req/min → 每次 --budget N,
  掛排程慢慢收;分母隨之變誠實。

⚠ **免費層結構性阻斷(2026-06-12 夜實證)**:Polygon 免費層對 2 年窗外的下市票
  aggs 回 **0 根**(ABMD/Abiomed 實測,status OK resultsCount 0);yfinance 對下市票
  已清空;Stooq 有 JS 反爬牆。→ 免費層下 48 根月線門檻**永遠**達不到,分母回填
  需付費數據(Polygon Starter $29/mo = 5 年史;Sharadar 等 survivorship-free 源)。
  **manifest 毒化警告**:目前 too_short 條目多為免費層假象(真公司如 ABMD/AAWW 也
  被標 too_short)— 升級付費層後必須先清掉 manifest 的 too_short 條目重掃,
  否則永久跳過可用票。survival 74.1% 維持「倖存者宇宙上界」標注。

⚠ 揭露:Phase 1 仍是倖存者宇宙(下市者缺席)→ **真實存活率只會更低**,
sizing 取下緣。llm_involvement: none。

CLI:
    python -m sharks.backtest.failed_analogs                 # analyze(離線)
    python -m sharks.backtest.failed_analogs collect 20      # Phase 2 收 20 檔下市票
"""

from __future__ import annotations

import json
import sys
import time
import warnings
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)

import numpy as np
import pandas as pd

from sharks.backtest.rally_dna import (DEEP_KILL_DD, DEEP_VOL_X, dna_features, dna_trigger,
                                       load_monthly, monthly_universe)

FAILED_DIR = Path("data/lake/failed")
HORIZON_M = 24
SLEEVE_DRAG_BUDGET = 0.02     # 可接受的 deep-kill 袖子對總資本的期望拖累(2%)
CAP_BOUNDS = (0.05, 0.15)     # 分倉上限的夾範圍


def classify_outcome(entry: float, fwd_close: pd.Series) -> dict:
    """固定 24 個月視窗的結局分類(純函式)。fwd_close = 進場後的月收盤序列。"""
    if not entry > 0 or fwd_close.empty:
        return {"outcome": "no_data"}
    end_ret = float(fwd_close.iloc[-1] / entry - 1)
    max_gain = float(fwd_close.max() / entry - 1)
    max_dd = float(fwd_close.min() / entry - 1)
    if max_gain >= 1.0:
        oc = "monster"
    elif max_gain >= 0.30:
        oc = "ok"
    elif end_ret <= -0.40 or max_dd <= -0.50:
        oc = "disaster"
    else:
        oc = "dud"
    return {"outcome": oc, "end_ret_pct": round(end_ret * 100, 1),
            "max_gain_pct": round(max_gain * 100, 1), "max_dd_pct": round(max_dd * 100, 1)}


def deepkill_ledger(universe: list[str], loader=None) -> list[dict]:
    """全宇宙 deep-kill 觸發事件 → 24 個月固定視窗結局(成功與失敗同一把尺)。"""
    loader = loader or load_monthly
    out = []
    for t in universe:
        df = loader(t)
        if df is None or len(df) < 60 or "Open" not in df:
            continue
        trig = dna_trigger(df, kill_dd=DEEP_KILL_DD, vol_x=DEEP_VOL_X)
        close, opn = df["Close"], df["Open"]
        n = len(df)
        i = 0
        while i < n - HORIZON_M - 1:
            if not bool(trig.iloc[i]):
                i += 1
                continue
            e = i + 1
            entry = float(opn.iloc[e])
            res = classify_outcome(entry, close.iloc[e:e + HORIZON_M])
            if res.get("outcome") != "no_data":
                f = dna_features(df, i) or {}
                out.append({"ticker": t, "trigger": str(df.index[i].date()),
                            "year": int(str(df.index[i])[:4]), **res, **f})
            i = e + HORIZON_M           # 不重疊視窗,事件獨立
    return out


def bootstrap_survival(ledger: list[dict], n_boot: int = 10000, seed: int = 42) -> dict:
    """非參數 bootstrap(重抽 n_boot 次):存活率 90% CI + P(損)/損幅的 95 百分位
    (悲觀端,餵 cap)。向量化,seed 固定可重現。"""
    rets = np.array([r["end_ret_pct"] for r in ledger]) / 100
    succ = np.array([r.get("outcome") in ("monster", "ok") for r in ledger])
    n = len(ledger)
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, n, size=(n_boot, n))
    surv = succ[idx].mean(axis=1)
    r = rets[idx]
    neg = r < 0
    ploss = neg.mean(axis=1)
    lgl = np.where(neg, -r, 0).sum(axis=1) / np.clip(neg.sum(axis=1), 1, None)
    q = lambda a, p: float(np.percentile(a, p))
    return {"n_boot": n_boot,
            "survival_pct": {"point": round(float(succ.mean()) * 100, 1),
                             "ci90": [round(q(surv, 5) * 100, 1), round(q(surv, 95) * 100, 1)]},
            "p_loss_pct_ci95_high": round(q(ploss, 95) * 100, 1),
            "lgl_pct_ci95_high": round(q(lgl, 95) * 100, 1)}


def cap_recommendation(ledger: list[dict], boot: Optional[dict] = None) -> dict:
    """透明 sizing 公式:cap = 拖累預算 / (P(損) × |平均損|),夾在 [5%,15%]。
    再以「倖存者壓力版」(P損+10pp、損幅×1.2)取下緣 — 下市者缺席的補償。"""
    d = pd.DataFrame(ledger)
    rets = d["end_ret_pct"] / 100
    p_loss = float((rets < 0).mean())
    lgl = float(-rets[rets < 0].mean()) if (rets < 0).any() else 0.25
    cap_raw = SLEEVE_DRAG_BUDGET / max(p_loss * lgl, 1e-6)
    p_s, l_s = min(p_loss + 0.10, 0.95), lgl * 1.2
    cap_stress = SLEEVE_DRAG_BUDGET / max(p_s * l_s, 1e-6)
    clip = lambda c: round(min(max(c, CAP_BOUNDS[0]), CAP_BOUNDS[1]) * 100, 1)
    out = {"formula": "cap = 拖累預算2% / (P(損)×|平均損|),夾 [5%,15%]",
           "p_loss": round(p_loss * 100, 1), "loss_given_loss_pct": round(lgl * 100, 1),
           "cap_pct": clip(cap_raw),
           "cap_stress_pct": clip(cap_stress),
           "single_position_risk_note": "單筆 deep-kill 風險 ≤1-2% 總資本(進場額×停損幅);袖上限管總曝險",
           "note": "壓力版+CI 悲觀端取低者(下市者缺席 → 真實 P(損) 更高);Phase 2 回填後重算"}
    if boot:
        cap_ci = SLEEVE_DRAG_BUDGET / max((boot["p_loss_pct_ci95_high"] / 100)
                                          * (boot["lgl_pct_ci95_high"] / 100), 1e-6)
        out["cap_ci_pct"] = clip(cap_ci)
        out["recommended"] = min(clip(cap_stress), clip(cap_ci))
    else:
        out["recommended"] = clip(cap_stress)
    return out


def analyze() -> dict:
    uni = monthly_universe()
    # Phase 2 已收的下市票也納入(若有)
    failed_uni = sorted({p.stem.rsplit("_", 1)[0] for p in FAILED_DIR.glob("*_1mo.parquet")})

    def failed_loader(t):
        p = FAILED_DIR / f"{t}_1mo.parquet"
        try:
            df = pd.read_parquet(p)
            return df.iloc[:-1] if len(df) > 1 else None
        except Exception:
            return None

    ledger = deepkill_ledger(uni) + deepkill_ledger(failed_uni, loader=failed_loader)
    if not ledger:
        return {"n_events": 0}
    d = pd.DataFrame(ledger)
    dist = d["outcome"].value_counts(normalize=True).round(3).mul(100).to_dict()
    survival = round(float(d["outcome"].isin(["monster", "ok"]).mean()) * 100, 1)
    by_era = {str(y): round(float(sub["outcome"].isin(["monster", "ok"]).mean()) * 100, 1)
              for y, sub in d.groupby((d["year"] // 5) * 5) if len(sub) >= 20}
    failed = d[d["outcome"].isin(["dud", "disaster"])]
    boot = bootstrap_survival(ledger)
    from sharks.backtest.rally_dna import MATCH_FEATS
    failed_events = [{k: r.get(k) for k in
                      ("ticker", "trigger", "outcome", "end_ret_pct", *MATCH_FEATS)}
                     for r in failed.to_dict("records")
                     if all(r.get(k) is not None for k in MATCH_FEATS)][:300]
    return {"as_of": datetime.now(timezone.utc).isoformat(),
            "engine": "failed-analogs(deep-kill 24m 固定視窗)", "llm_involvement": "none",
            "n_events": len(d), "n_from_delisted": int((~d["ticker"].isin(uni)).sum()),
            "outcome_dist_pct": dist, "survival_rate_pct": survival,
            "survival_bootstrap": boot,
            "survival_by_era_pct": by_era,
            "median_ret_by_outcome": {k: round(float(sub["end_ret_pct"].median()), 1)
                                      for k, sub in d.groupby("outcome")},
            "cap_recommendation": cap_recommendation(ledger, boot),
            "failed_events": failed_events,
            "failed_analogs_sample": failed.nsmallest(20, "end_ret_pct").to_dict("records"),
            "disclosures": ["Phase 1 宇宙=今日倖存者(下市者缺席)→ 真實存活率更低,sizing 取壓力下緣",
                            "成功與失敗用同一觸發與同一 24m 視窗 — 同一把尺",
                            f"Phase 2 已回填下市票 {len(failed_uni)} 檔(data/lake/failed/)"]}


# ── Phase 2:Polygon 下市票收集(掛排程慢慢收)──

def fetch_delisted_tickers(max_pages: int = 3) -> list[dict]:
    """Polygon reference/tickers?active=false(分頁;1 call/頁,1000 檔/頁)。"""
    import requests
    from sharks.data.polygon_financials import _token
    tok = _token()
    url = "https://api.polygon.io/v3/reference/tickers"
    params = {"market": "stocks", "active": "false", "type": "CS", "limit": 1000, "apiKey": tok}
    out, pages = [], 0
    while pages < max_pages:
        r = requests.get(url, params=params, timeout=30)
        r.raise_for_status()
        j = r.json()
        out += [{"ticker": x.get("ticker"), "name": x.get("name"),
                 "delisted_utc": x.get("delisted_utc")} for x in j.get("results") or []]
        pages += 1
        nxt = j.get("next_url")
        if not nxt:
            break
        url, params = nxt, {"apiKey": tok}
        time.sleep(13)
    return out


# ── Phase 2 候選排序先驗(顯式啟發式;不丟棄只重排 — 掃描終究全覆蓋,只是先掃高機率區)──

PRIORITIZE_PRIORS: dict = {
    "_doc": ("collect 候選重排先驗。2026-06-12 生產實跑:570 檔掃描 100% too_short — "
             "2010+ 下市清單按字母序前段被 SPAC/殼公司/權證灌爆(<48 根月線必跳票),"
             "真營運公司死亡(分母要的樣本)被排到後面。重排只改掃描順序、集合不變;"
             "分數為顯式猜測非擬合,誤判成本僅是「晚一點掃到」。"),
    "SHELL_NAME": {
        "score": -2.0,
        "patterns": ("acquisition", "acq corp", "spac", "blank check",
                     "capital corp", "holdings corp", "merger"),
        "_doc": ("名稱含殼公司字樣(不分大小寫子字串)→ 墊後。SPAC/空白支票公司"
                 "上市到下市常 <4 年,幾乎必 too_short。子字串有誤傷可能"
                 "(如 'Space…' 含 'spac'),但只重排不丟棄,成本可接受。"),
    },
    "WARRANT_SUFFIX": {
        "score": -3.0, "suffixes": ("W", "R", "U"), "min_len": 5,
        "_doc": ("ticker 長度 ≥5 且結尾 W/R/U(不分大小寫;Polygon 慣用小寫 w 標"
                 "權證,如 AINCw、AXG.U)= 權證/權利/單位 — 從來不是營運公司,"
                 "罰最重。2026-06-12 manifest 驗證:570 檔中 9 檔命中,全 too_short。"
                 "min_len=5 避免誤殺真公司短碼(如 AAU=Almaden Minerals)。"),
    },
    "PRIORITY_YEARS": {
        "score": 1.0, "lo": "2012", "hi": "2023",
        "_doc": ("delisted_utc 落在 2012..2023(含)→ 提前:真公司死亡年代,含 "
                 "2015-16 油價崩盤與 2022 成長股屠殺;2024+ 以 SPAC 清算潮為主,"
                 "2010-11 與 2024+ 同樣不加分。年份缺值(None)不發明、不加分。"),
    },
}


def prioritize_candidates(cands: list[dict]) -> list[dict]:
    """重排(永不丟棄)Phase 2 下市票候選 — 先掃「真營運公司死亡」高機率區。

    純函式、穩定排序(同分保留原始相對順序);缺欄位(name / delisted_utc /
    ticker = None)一律視為無訊號 = 0 分,不發明值。先驗見 PRIORITIZE_PRIORS。"""
    shell = PRIORITIZE_PRIORS["SHELL_NAME"]
    warr = PRIORITIZE_PRIORS["WARRANT_SUFFIX"]
    yrs = PRIORITIZE_PRIORS["PRIORITY_YEARS"]

    def score(c: dict) -> float:
        s = 0.0
        name = (c.get("name") or "").lower()
        if name and any(p in name for p in shell["patterns"]):
            s += shell["score"]
        t = c.get("ticker") or ""
        if len(t) >= warr["min_len"] and t.upper().endswith(warr["suffixes"]):
            s += warr["score"]
        y = (c.get("delisted_utc") or "")[:4]
        if y and yrs["lo"] <= y <= yrs["hi"]:
            s += yrs["score"]
        return s

    return sorted(cands, key=lambda c: -score(c))      # sorted 穩定:同分保原序


CURATED_PATH = Path("watchlist/delisted_candidates.yaml")


def _load_curated(path: Optional[Path] = None) -> list[dict]:
    """讀 curated 下市票清單(目標式解析:只認 '- ticker:' 與其 delisted: 行;
    _yamlite 不支援列表故不用)。缺檔/壞檔 → []。"""
    import re
    p = path or CURATED_PATH
    out: list[dict] = []
    try:
        cur = None
        for ln in p.read_text(encoding="utf-8").splitlines():
            m = re.match(r"^\s*-\s*ticker:\s*([A-Z][A-Z0-9.]*)\s*$", ln)
            if m:
                cur = {"ticker": m.group(1), "name": None, "delisted_utc": None,
                       "curated": True}
                out.append(cur)
                continue
            if cur is not None:
                d = re.match(r"^\s+delisted:\s*(\d{4})\s*$", ln)
                if d:
                    cur["delisted_utc"] = f"{d.group(1)}-01-01"
    except Exception:
        return []
    return out


def _candidate_queue(done: set, fetch_fn=None, prioritize: bool = True,
                     curated_path: Optional[Path] = None) -> list[dict]:
    """curated 清單(高價值真亡者)永遠排最前 → fetch → 過濾(已收 / 缺 ticker /
    2010 前下市)→(預設)重排。fetch_fn 可注入;prioritize=False 保留來源順序。"""
    curated = [c for c in _load_curated(curated_path) if c["ticker"] not in done]
    seen = {c["ticker"] for c in curated}
    cands = [x for x in (fetch_fn or fetch_delisted_tickers)()
             if x.get("ticker") and x["ticker"] not in done and x["ticker"] not in seen
             and (x.get("delisted_utc") or "")[:4] >= "2010"]
    tail = prioritize_candidates(cands) if prioritize else cands
    return curated + tail


def collect(budget: int = 20, max_seconds: float = 1200.0,
            prioritize: bool = True, fetch_fn=None) -> dict:
    """收 budget 檔下市票月線 → data/lake/failed/(免費層限速 13s/call)。
    進度存 failed-manifest.jsonl,跨次執行續收。

    max_seconds = 牆鐘預算(預設 20 分):budget 只數「可收」票,掃過長段
    too_short 跳票時嘗試數無上限;另外 requests 的 scalar timeout 只管位元組
    間隔,擋不住涓流回應(2026-06-12 生產實跑吊死 2.5h 的根因)— 每筆抓取
    再包硬性 60s(thread + future timeout),雙保險讓晨間管線永遠走得完。

    prioritize = 候選重排(預設開;見 prioritize_candidates / PRIORITIZE_PRIORS):
    殼公司/權證墊後、2012..2023 真公司死亡年代提前,提高每晚 budget 的命中率;
    fetch_fn 可注入(測試用)。"""
    import requests
    from concurrent.futures import ThreadPoolExecutor
    from concurrent.futures import TimeoutError as FutTimeout
    from sharks.data.polygon_financials import _token
    tok = _token()
    FAILED_DIR.mkdir(parents=True, exist_ok=True)
    manifest = FAILED_DIR / "failed-manifest.jsonl"
    done = set()
    if manifest.exists():
        for ln in manifest.read_text(encoding="utf-8").splitlines():
            try:
                done.add(json.loads(ln)["ticker"])
            except Exception:
                pass
    cands = _candidate_queue(done, fetch_fn, prioritize)
    got = 0
    t0 = time.monotonic()
    pool = ThreadPoolExecutor(max_workers=1)
    with manifest.open("a", encoding="utf-8") as fh:
        for x in cands:
            if got >= budget or time.monotonic() - t0 > max_seconds:
                break
            t = x["ticker"]
            time.sleep(13)
            try:
                u = (f"https://api.polygon.io/v2/aggs/ticker/{t}/range/1/month/"
                     f"2005-01-01/2026-06-01")
                from sharks.data.call_log import record
                t_req = time.monotonic()
                fut = pool.submit(requests.get, u,
                                  params={"adjusted": "true", "limit": 500, "apiKey": tok},
                                  timeout=30)
                try:
                    r = fut.result(timeout=60)      # 硬上限:涓流回應也走得掉
                    record("polygon", "aggs-delisted",
                           latency_ms=int((time.monotonic() - t_req) * 1000))
                except FutTimeout:
                    record("polygon", "aggs-delisted", ok=False, note="hard-timeout-60s")
                    fh.write(json.dumps({"ticker": t, "status": "err:hard-timeout-60s"}) + "\n")
                    pool.shutdown(wait=False)        # 棄置卡住的 worker,換新池
                    pool = ThreadPoolExecutor(max_workers=1)
                    continue
                r.raise_for_status()
                rows = r.json().get("results") or []
                if len(rows) < 48:                  # 至少 4 年月線才夠形態偵測
                    fh.write(json.dumps({"ticker": t, "status": "too_short"}) + "\n")
                    continue
                df = pd.DataFrame({
                    "Open": [b.get("o") for b in rows], "High": [b.get("h") for b in rows],
                    "Low": [b.get("l") for b in rows], "Close": [b.get("c") for b in rows],
                    "Volume": [b.get("v") for b in rows]},
                    index=pd.to_datetime([b["t"] for b in rows], unit="ms"))
                df.to_parquet(FAILED_DIR / f"{t}_1mo.parquet")
                fh.write(json.dumps({"ticker": t, "status": "ok", "bars": len(df),
                                     "delisted": x.get("delisted_utc")}) + "\n")
                got += 1
            except Exception as e:
                fh.write(json.dumps({"ticker": t, "status": f"err:{str(e)[:60]}"}) + "\n")
    pool.shutdown(wait=False)
    return {"collected": got, "total_in_dir": len(list(FAILED_DIR.glob('*_1mo.parquet'))),
            "elapsed_s": round(time.monotonic() - t0, 1)}


def reset_thin_manifest(manifest: Optional[Path] = None) -> dict:
    """付費層升級日專用:清掉 manifest 的免費層假象條目(too_short/err)讓其重掃,
    只保留 ok(已有 parquet 的真收穫)。被清條目封存到 failed-manifest.archive-<date>.jsonl
    (審計鏈)。免費層下執行=明天起重燒同一批 API,所以不排程、只手動。"""
    manifest = manifest or (FAILED_DIR / "failed-manifest.jsonl")
    if not manifest.exists():
        return {"kept": 0, "archived": 0, "note": "no manifest"}
    keep, drop = [], []
    for ln in manifest.read_text(encoding="utf-8").splitlines():
        try:
            (keep if json.loads(ln).get("status") == "ok" else drop).append(ln)
        except Exception:
            drop.append(ln)
    if drop:
        arch = manifest.parent / f"failed-manifest.archive-{datetime.now().strftime('%Y-%m-%d')}.jsonl"
        with arch.open("a", encoding="utf-8") as fh:
            fh.write("\n".join(drop) + "\n")
    manifest.write_text(("\n".join(keep) + "\n") if keep else "", encoding="utf-8")
    return {"kept": len(keep), "archived": len(drop)}


def main(argv: Optional[list[str]] = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    if args and args[0] == "collect":
        budget = int(args[1]) if len(args) > 1 else 20
        res = collect(budget)
        print(f"collected {res['collected']} delisted tickers "
              f"(dir total {res['total_in_dir']})", file=sys.stderr)
        return 0
    if args and args[0] == "reset-thin":
        res = reset_thin_manifest()
        print(f"reset-thin: kept {res['kept']} ok, archived {res['archived']} "
              f"(paid-tier rescan enabled)", file=sys.stderr)
        return 0
    rep = analyze()
    p = Path("outputs") / f"failed-analogs-{datetime.now().strftime('%Y-%m-%d')}.json"
    p.write_text(json.dumps(rep, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"wrote {p}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
