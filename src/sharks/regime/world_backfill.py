"""世界指標歷史回填 + 合成 vintage 事件重播(world model 研究層).

關鍵事實:GSCPI / GPR 每次下載都含**全史**(就地修訂),因此可以把序列截斷到
任一過去時點,重建 world_monitor 當時「會」算出的 metrics 與事件。誠實前提
(輸出一律標 ``vintage: "synthetic-revised"`` + 來源快照日期):

  1. 重建用的是今日修訂值,非真實首印(first print)— 無官方 vintage 庫可對照。
  2. 假設月度值於該觀測月月末即可見;實際發布滯後數日 → 月度事件的 1m 前瞻
     統計帶有約一個發布滯後的 lookahead,僅供研究,不得當成可交易歷史訊號。

deliverable:``event_forward_study`` — 各事件(TS_HIGH / GSCPI_SPIKE /
GPR_EXTREME / GPR_ELEVATED)歷史命中月份 vs QQQ 前瞻 1/3/6 個月報酬
(中位數/平均、各格 n),對照全月份 base rate。表格之外不做任何因果宣稱。

recommend-only / observe-first:本模組只產生研究輸出,不產生任何交易指令。
llm_involvement: none(純規則/統計引擎)。

CLI:
    python -m sharks.regime.world_backfill [--days 90] [--start 1998-01]
"""

from __future__ import annotations

import calendar
import json
import statistics
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional

from sharks.regime.world_monitor import (EVENTS_CONFIG, LAKE_WORLD,
                                         compute_metrics, evaluate_events)

VINTAGE = "synthetic-revised"
STUDY_EVENTS = ("TS_HIGH", "GSCPI_SPIKE", "GPR_EXTREME", "GPR_ELEVATED")
HORIZONS_M = (1, 3, 6)
METRIC_SUBSET = ("gscpi", "gpr", "gprc_twn", "gprc_twn_z60", "gprd_ma30")
SOURCES = ("gscpi", "gpr_monthly", "gpr_daily")

VINTAGE_NOTE = (
    "synthetic-revised:以最新 lake 快照的「今日全史(已修訂)」截斷重建各 as-of "
    "時點的指標與事件;非真實首印 vintage(兩來源就地修訂、無官方 vintage 庫)。"
    "並假設月度值於觀測月月末即可見(實際發布滯後數日 → 1m 前瞻略帶發布滯後的 "
    "lookahead)。僅供研究,不得當成可交易的歷史訊號;表格之外不做因果宣稱。"
)


# ── lake 讀取 ──

def load_world_lake(lake_dir: Path = LAKE_WORLD) -> dict:
    """讀各源最新快照(sorted-glob 由新到舊;空 series 的壞快照跳過退上一份,
    不發明)。→ {gscpi, gpr_monthly, gpr_daily, snapshot_dates, retrieved_at}。"""
    out: dict = {"snapshot_dates": {}, "retrieved_at": {}}
    for name in SOURCES:
        series, snap, retrieved = None, None, None
        for p in sorted(lake_dir.glob(f"{name}-*.json"), reverse=True):
            try:
                d = json.loads(p.read_text(encoding="utf-8"))
            except Exception:
                continue
            s = d.get("series")
            if not s or (isinstance(s, dict) and not any(s.values())):
                continue                      # 空快照(壞 parse)→ 退上一份
            series = s
            snap = p.stem.replace(f"{name}-", "")
            retrieved = d.get("retrieved_at")
            break
        out[name] = series
        out["snapshot_dates"][name] = snap
        out["retrieved_at"][name] = retrieved
    return out


# ── as-of 截斷 + 指標重建(純函式)──

def _truncate_rows(rows: Optional[list[dict]], asof_date: str) -> list[dict]:
    return [r for r in rows or [] if r.get("date", "") <= asof_date]


def truncate_series(series: dict, asof_date: str) -> dict:
    """全部序列截到 date <= asof_date(PIT 形狀:之後的列一律不可見)。"""
    return {
        "gscpi": _truncate_rows(series.get("gscpi"), asof_date),
        "gpr_monthly": {c: _truncate_rows(rows, asof_date)
                        for c, rows in (series.get("gpr_monthly") or {}).items()},
        "gpr_daily": {c: _truncate_rows(rows, asof_date)
                      for c, rows in (series.get("gpr_daily") or {}).items()},
    }


def reconstruct_metrics_asof(series: dict, asof_date: str) -> dict:
    """截斷後重算 world_monitor.compute_metrics(同一套公式,manual_flags={})。
    純函式:給定輸入必得同輸出。"""
    t = truncate_series(series, asof_date)
    return compute_metrics(t["gscpi"] or None, t["gpr_monthly"] or None,
                           t["gpr_daily"] or None, manual_flags={})


def backfill_events(series: dict, dates: list[str], config: dict) -> list[dict]:
    """各 as-of 時點重建 metrics → 事件求值 → 帶 vintage 標籤的列。"""
    rows = []
    for asof in dates:
        m = reconstruct_metrics_asof(series, asof)
        fired, missing = evaluate_events(config, m)
        rows.append({
            "as_of": asof,
            "metrics": {k: m.get(k) for k in METRIC_SUBSET},
            "events": [e["id"] for e in fired],
            "degraded_metrics": missing,
            "vintage": VINTAGE,
        })
    return rows


# ── as-of 日期產生(純函式)──

def month_end_dates(start_ym: str = "1998-01", end_ym: Optional[str] = None) -> list[str]:
    """月末日期序列 'YYYY-MM-DD',含 start_ym 與 end_ym 兩端(end 預設=本月)。"""
    if end_ym is None:
        end_ym = datetime.now().strftime("%Y-%m")
    y, m = int(start_ym[:4]), int(start_ym[5:7])
    ey, em = int(end_ym[:4]), int(end_ym[5:7])
    out = []
    while (y, m) <= (ey, em):
        out.append(f"{y:04d}-{m:02d}-{calendar.monthrange(y, m)[1]:02d}")
        y, m = (y + 1, 1) if m == 12 else (y, m + 1)
    return out


def recent_daily_dates(days: int, end_date: Optional[str] = None) -> list[str]:
    """最近 days 個日曆日(含 end_date,預設=今天),由舊到新。"""
    end = (datetime.strptime(end_date, "%Y-%m-%d").date() if end_date
           else datetime.now().date())
    return [(end - timedelta(days=i)).isoformat() for i in range(max(days, 0) - 1, -1, -1)]


# ── 前瞻研究(deliverable)──

def _cell(rets: list[float]) -> dict:
    if not rets:
        return {"n": 0, "median_pct": None, "mean_pct": None}
    return {"n": len(rets),
            "median_pct": round(statistics.median(rets) * 100, 2),
            "mean_pct": round(statistics.mean(rets) * 100, 2)}


def event_forward_study(event_rows: list[dict], qqq_monthly,
                        horizons: tuple[int, ...] = HORIZONS_M,
                        event_ids: tuple[str, ...] = STUDY_EVENTS) -> dict:
    """各事件命中月 vs QQQ 前瞻 1/3/6 月報酬(條件式 vs base rate,各格 n)。

    event_rows 為月度回填列(as_of=月末);qqq_monthly 為月線 DataFrame
    (index=月初 timestamp,Close 欄;rally_dna.load_monthly 已丟當月 partial)。
    回答「事件歷史上跟著什麼」— 只給表格,不做表格之外的宣稱。
    """
    if qqq_monthly is None or getattr(qqq_monthly, "empty", True) \
            or "Close" not in qqq_monthly:
        return {"underlying": "QQQ", "horizons_m": list(horizons),
                "base_rate": None, "events": None,
                "note": "QQQ 月線缺席 — 不發明,前瞻研究略過"}
    close = qqq_monthly["Close"]
    pos = {f"{ts.year:04d}-{ts.month:02d}": i for i, ts in enumerate(close.index)}

    def fwd(i: int, h: int) -> Optional[float]:
        if i + h >= len(close):
            return None
        a, b = float(close.iloc[i]), float(close.iloc[i + h])
        return (b / a - 1.0) if a > 0 else None

    mapped = [(r, pos[r["as_of"][:7]]) for r in event_rows if r["as_of"][:7] in pos]
    base_idx = [i for _, i in mapped]

    def fwd_table(indices: list[int]) -> dict:
        return {f"{h}m": _cell([x for x in (fwd(i, h) for i in indices)
                                if x is not None]) for h in horizons}

    events: dict = {}
    for eid in event_ids:
        fired = [(r["as_of"], i) for r, i in mapped if eid in r["events"]]
        idx = [i for _, i in fired]
        events[eid] = {
            "months_fired": len(idx),
            "fired_share_pct": (round(100.0 * len(idx) / len(base_idx), 1)
                                if base_idx else None),
            "first_fired": fired[0][0] if fired else None,
            "last_fired": fired[-1][0] if fired else None,
            "fwd": fwd_table(idx),
        }
    return {
        "underlying": "QQQ",
        "horizons_m": list(horizons),
        "n_months_mapped": len(mapped),
        "base_rate": {"n_months": len(base_idx), "fwd": fwd_table(base_idx)},
        "events": events,
        "note": "條件式前瞻報酬表(synthetic-revised vintage);"
                "表格之外不做因果宣稱。",
    }


# ── CLI ──

def main(argv: Optional[list[str]] = None) -> int:
    import argparse
    ap = argparse.ArgumentParser(
        description="world 歷史回填 + 合成 vintage 事件重播(研究輸出,非交易指令)")
    ap.add_argument("--days", type=int, default=90, help="每日回填的最近日曆日數")
    ap.add_argument("--start", default="1998-01", help="月度回填起點 YYYY-MM(GSCPI 起點)")
    ap.add_argument("--out-dir", default="outputs")
    ap.add_argument("--lake-dir", default=str(LAKE_WORLD))
    ap.add_argument("--dry-run", action="store_true", help="算結果不落盤")
    args = ap.parse_args(argv)

    today = datetime.now().strftime("%Y-%m-%d")
    lake_dir = Path(args.lake_dir)
    try:
        config = json.loads(Path(EVENTS_CONFIG).read_text(encoding="utf-8"))
    except Exception:
        config = {}

    print("loading world lake snapshots ...", file=sys.stderr)
    series = load_world_lake(lake_dir)
    print(f"  snapshots: {series['snapshot_dates']}", file=sys.stderr)

    # 月度終點 = 月度數據最後觀測月(避免尾端重覆 carry 最新值灌水命中數)
    last_dates = []
    if series.get("gscpi"):
        last_dates.append(series["gscpi"][-1]["date"])
    gpr_rows = (series.get("gpr_monthly") or {}).get("GPR") or []
    if gpr_rows:
        last_dates.append(gpr_rows[-1]["date"])
    end_ym = max(last_dates)[:7] if last_dates else today[:7]

    monthly_dates = month_end_dates(args.start, end_ym)
    print(f"monthly backfill {monthly_dates[0]} .. {monthly_dates[-1]} "
          f"({len(monthly_dates)} months) ...", file=sys.stderr)
    monthly_rows = backfill_events(series, monthly_dates, config)

    daily_dates = recent_daily_dates(args.days, today)
    print(f"daily backfill last {args.days} days ...", file=sys.stderr)
    daily_rows = backfill_events(series, daily_dates, config)

    print("forward study vs QQQ ...", file=sys.stderr)
    from sharks.backtest.rally_dna import load_monthly
    qqq = load_monthly("QQQ")
    study = event_forward_study(monthly_rows, qqq)

    report = {
        "as_of": today,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "engine": "world-backfill",
        "llm_involvement": "none",
        "vintage": VINTAGE,
        "vintage_note": VINTAGE_NOTE,
        "snapshot_dates": series["snapshot_dates"],
        "snapshot_retrieved_at": series["retrieved_at"],
        "config_version": config.get("version"),
        "n_monthly_rows": len(monthly_rows),
        "n_daily_rows": len(daily_rows),
        "event_forward_study": study,
        "monthly_rows": monthly_rows,
        "daily_rows_recent": daily_rows,
        "disclaimer": "recommend-only / observe-first;研究輸出,非倉位指令。",
    }
    if not args.dry_run:
        out_dir = Path(args.out_dir)
        out_dir.mkdir(exist_ok=True)
        p = out_dir / f"world-backfill-{today}.json"
        p.write_text(json.dumps(report, ensure_ascii=False, indent=2),
                     encoding="utf-8")
        print(f"wrote {p}", file=sys.stderr)
        # 緊湊 lake 檔(可覆寫 — 由快照可再生,非首寫為準的 vintage 快照)
        lake_dir.mkdir(parents=True, exist_ok=True)
        archive = {"generated_at": report["generated_at"], "vintage": VINTAGE,
                   "snapshot_dates": series["snapshot_dates"],
                   "rows": monthly_rows}
        pa = lake_dir / "backfill-monthly.json"
        pa.write_text(json.dumps(archive, ensure_ascii=False), encoding="utf-8")
        print(f"wrote {pa}", file=sys.stderr)

    try:
        sys.stdout.reconfigure(encoding="utf-8")    # cp950 console 防護
    except Exception:
        pass
    ev = study.get("events") or {}
    print(f"world-backfill: months={len(monthly_rows)} days={len(daily_rows)} "
          f"vintage={VINTAGE}")
    base = (study.get("base_rate") or {}).get("fwd") or {}
    if base:
        b = " ".join(f"{h}m {c['median_pct']}%/n{c['n']}" for h, c in
                     ((k[:-1], v) for k, v in base.items()))
        print(f"  base rate (all months): {b}")
    for eid, e in ev.items():
        f1, f3, f6 = (e["fwd"].get("1m") or {}), (e["fwd"].get("3m") or {}), \
                     (e["fwd"].get("6m") or {})
        print(f"  {eid}: fired {e['months_fired']}m "
              f"({e['fired_share_pct']}%) | fwd median "
              f"1m {f1.get('median_pct')}% 3m {f3.get('median_pct')}% "
              f"6m {f6.get('median_pct')}% (n {f1.get('n')}/{f3.get('n')}/{f6.get('n')})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
