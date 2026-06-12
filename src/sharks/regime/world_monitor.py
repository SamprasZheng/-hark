"""World Monitor — GSCPI/GPR 感測 → 世界事件求值 → DNA 鏈消費(world model 核心).

每晨(SharksDNA-Morning,rally_dna 之前)跑一次:
  1. 拉 GSCPI / GPR 月度 / GPR 每日(data/world_indicators,grade A 免 key)
  2. 算 metrics(最新值、單月差、60 月滾動 z、1985+ 分位數)
  3. 用 config/world_events.json 把數值條件求值成布林事件(規則引擎只吃等值旗標)
  4. 聚合 impacts(ctx_flags / weight_shifts / deepkill_cap_multiplier / exposure_penalty)
  5. 落盤 outputs/world-monitor-<date>.json + data/lake/world/ 前向 vintage 史

失敗紀律(仿 regime/liquidity.run_liquidity):never raise — 單源失敗退回該源
最近一次 lake 快照並標 stale;全失敗則輸出 degraded 信封,DNA 鏈照常跑
(事件全 False = 與世界模型上線前行為相同)。

PIT:兩來源每次發布就地修訂全史、無官方 vintage 庫 — 每日把解析後序列存成
data/lake/world/<series>-<date>.json(不可變,首寫為準),自 2026-06-12 起
前向累積本地 vintage;在此之前的歷史回測不得使用本模組輸出(無第一可見時點)。

CLI:
    python -m sharks.regime.world_monitor [--dry-run]
"""

from __future__ import annotations

import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Optional

EVENTS_CONFIG = Path("config/world_events.json")
LAKE_WORLD = Path("data/lake/world")

_OPS: dict[str, Callable] = {
    ">=": lambda a, b: a >= b,
    ">": lambda a, b: a > b,
    "<=": lambda a, b: a <= b,
    "<": lambda a, b: a < b,
    "==": lambda a, b: a == b,
}


# ── 純統計助手 ──

def _values(rows: list[dict], since: Optional[str] = None) -> list[float]:
    return [r["value"] for r in rows or []
            if r.get("value") is not None and (since is None or r.get("date", "") >= since)]


def percentile_of(history: list[float], x: float) -> Optional[float]:
    """x 在 history 內的百分位(% of values <= x)。純函式。"""
    if not history:
        return None
    return round(100.0 * sum(1 for v in history if v <= x) / len(history), 1)


def trailing_z(values: list[float], window: int = 60) -> Optional[float]:
    """最後一點對含自身的近 window 點之 z-score(同 probe 校準口徑)。"""
    tail = values[-window:]
    if len(tail) < max(12, window // 5):
        return None
    mu = sum(tail) / len(tail)
    var = sum((v - mu) ** 2 for v in tail) / max(len(tail) - 1, 1)
    sd = var ** 0.5
    if sd == 0:
        return None
    return round((tail[-1] - mu) / sd, 2)


# ── metrics(純函式:client 列 → 扁平指標)──

def compute_metrics(gscpi_rows: Optional[list[dict]],
                    gpr_monthly: Optional[dict[str, list[dict]]],
                    gpr_daily: Optional[dict[str, list[dict]]],
                    manual_flags: Optional[dict] = None) -> dict:
    """缺源 → 對應 metric 缺席(事件求值記 degraded,不發明值)。"""
    m: dict = {}
    if gscpi_rows:
        vals = _values(gscpi_rows)
        if vals:
            m["gscpi"] = round(vals[-1], 3)
            m["gscpi_date"] = gscpi_rows[-1]["date"]
            if len(vals) >= 2:
                m["gscpi_delta_1m"] = round(vals[-1] - vals[-2], 3)
    gm = gpr_monthly or {}
    gpr_rows = gm.get("GPR") or []
    if gpr_rows:
        hist = _values(gpr_rows, since="1985-01-01")
        m["gpr"] = round(hist[-1], 1) if hist else None
        m["gpr_date"] = gpr_rows[-1]["date"]
        if hist:
            m["gpr_pctile"] = percentile_of(hist, hist[-1])
    gprt = _values(gm.get("GPRT") or [], since="1985-01-01")
    if gprt:
        m["gprt"] = round(gprt[-1], 1)
    for col, key in (("GPRC_TWN", "gprc_twn"), ("GPRC_CHN", "gprc_chn")):
        vals = _values(gm.get(col) or [], since="1985-01-01")
        if vals:
            m[key] = round(vals[-1], 3)
            z = trailing_z(vals, 60)
            if z is not None:
                m[f"{key}_z60"] = z
            m[f"{key}_pctile"] = percentile_of(vals, vals[-1])
    gd = gpr_daily or {}
    ma30 = gd.get("GPRD_MA30") or []
    if ma30:
        vals = _values(ma30)
        if vals:
            m["gprd_ma30"] = round(vals[-1], 1)
            m["gprd_date"] = ma30[-1]["date"]
    for k, v in (manual_flags or {}).items():
        if not k.startswith("_"):
            m[f"manual.{k}"] = bool(v)
    return m


# ── 事件求值(純函式)──

def eval_condition(cond: dict, metrics: dict, missing: list[str]) -> bool:
    """遞迴 any/all + 葉節點 {metric, op, value}。缺 metric → False 並記名。"""
    if "any" in cond:
        return any(eval_condition(c, metrics, missing) for c in cond["any"])
    if "all" in cond:
        return all(eval_condition(c, metrics, missing) for c in cond["all"])
    metric = cond.get("metric")
    x = metrics.get(metric)
    if x is None:
        missing.append(metric)
        return False
    op = _OPS.get(cond.get("op", ""))
    if op is None:
        return False
    try:
        return bool(op(x, cond.get("value")))
    except TypeError:
        return False


def evaluate_events(config: dict, metrics: dict) -> tuple[list[dict], list[str]]:
    """→ (觸發事件列表, degraded metric 名單)。"""
    fired, missing = [], []
    for ev in config.get("events") or []:
        if eval_condition(ev.get("condition") or {}, metrics, missing):
            fired.append({"id": ev.get("id"), "name": ev.get("name"),
                          "category": ev.get("category"),
                          "severity": ev.get("severity"),
                          "impact": ev.get("impact") or {}})
    return fired, sorted(set(m for m in missing if m))


def aggregate_impacts(fired: list[dict]) -> dict:
    """多事件疊加:cap 乘數取 min(最保守)、exposure_penalty 取 max、
    weight_shifts 同向合併且總量封頂 0.10(權重=顯式先驗,事件只准微調)。"""
    out: dict = {"ctx_flags": {}, "weight_shifts": [],
                 "deepkill_cap_multiplier": None, "exposure_penalty": 0.0,
                 "review_groups": []}
    shifts: dict[tuple, float] = {}
    for e in fired:
        imp = e.get("impact") or {}
        if imp.get("ctx_flag"):
            out["ctx_flags"][imp["ctx_flag"]] = True
        ws = imp.get("weight_shift")
        if ws and ws.get("amount"):
            key = (ws.get("give_to"), ws.get("take_from"))
            shifts[key] = shifts.get(key, 0.0) + float(ws["amount"])
        mult = imp.get("deepkill_cap_multiplier")
        if isinstance(mult, (int, float)):
            cur = out["deepkill_cap_multiplier"]
            out["deepkill_cap_multiplier"] = mult if cur is None else min(cur, mult)
        pen = imp.get("exposure_penalty")
        if isinstance(pen, (int, float)):
            out["exposure_penalty"] = max(out["exposure_penalty"], float(pen))
        for g in imp.get("review_groups") or []:
            if g not in out["review_groups"]:
                out["review_groups"].append(g)
    total = sum(shifts.values())
    scale = (0.10 / total) if total > 0.10 else 1.0
    out["weight_shifts"] = [{"give_to": g, "take_from": t,
                             "amount": round(a * scale, 3)}
                            for (g, t), a in shifts.items()]
    return out


# ── lake 前向 vintage 史(不可變,首寫為準 — 同 state/snapshot 精神)──

def _lake_snapshot(name: str, payload, today: str, lake_dir: Path) -> None:
    lake_dir.mkdir(parents=True, exist_ok=True)
    p = lake_dir / f"{name}-{today}.json"
    if p.exists():
        return
    p.write_text(json.dumps({"retrieved_at": datetime.now(timezone.utc).isoformat(),
                             "series": payload}, ensure_ascii=False),
                 encoding="utf-8")


def _lake_latest(name: str, lake_dir: Path):
    files = sorted(lake_dir.glob(f"{name}-*.json"))
    if not files:
        return None, None
    try:
        d = json.loads(files[-1].read_text(encoding="utf-8"))
        return d.get("series"), files[-1].stem.replace(f"{name}-", "")
    except Exception:
        return None, None


# ── orchestration(never raise)──

def run_world_monitor(out_dir: Path = Path("outputs"), *, today: Optional[str] = None,
                      write: bool = True, opener=None, sleep=time.sleep,
                      fetchers: Optional[dict] = None,
                      config_path: Path = EVENTS_CONFIG,
                      lake_dir: Path = LAKE_WORLD) -> dict:
    """感測 → 事件 → impacts → 落盤。單源失敗退 lake 快照標 stale,絕不 raise。"""
    today = today or datetime.now().strftime("%Y-%m-%d")
    try:
        config = json.loads(Path(config_path).read_text(encoding="utf-8"))
    except Exception:
        config = {}

    if fetchers is None:
        from sharks.data.world_indicators import (fetch_gpr_daily, fetch_gpr_monthly,
                                                  fetch_gscpi)
        fetchers = {
            "gscpi": lambda: fetch_gscpi(opener=opener, sleep=sleep),
            "gpr_monthly": lambda: fetch_gpr_monthly(opener=opener, sleep=sleep),
            "gpr_daily": lambda: fetch_gpr_daily(opener=opener, sleep=sleep),
        }

    series: dict = {}
    stale_sources: list[str] = []
    failed_sources: list[str] = []
    for name in ("gscpi", "gpr_monthly", "gpr_daily"):
        try:
            series[name] = fetchers[name]()
            if write:
                _lake_snapshot(name, series[name], today, lake_dir)
        except Exception:
            fallback, snap_date = _lake_latest(name, lake_dir)
            if fallback is not None:
                series[name] = fallback
                stale_sources.append(f"{name}(snapshot {snap_date})")
            else:
                series[name] = None
                failed_sources.append(name)

    metrics = compute_metrics(series.get("gscpi"), series.get("gpr_monthly"),
                              series.get("gpr_daily"),
                              manual_flags=config.get("manual_flags"))
    fired, degraded = evaluate_events(config, metrics)
    impacts = aggregate_impacts(fired)

    report = {
        "as_of": {"gscpi": metrics.get("gscpi_date"),
                  "gpr_monthly": metrics.get("gpr_date"),
                  "gpr_daily": metrics.get("gprd_date")},
        "retrieved_at": datetime.now(timezone.utc).isoformat(),
        "engine": "world-monitor", "llm_involvement": "none",
        "live_data": not stale_sources and not failed_sources,
        "stale_sources": stale_sources,
        "failed_sources": failed_sources,
        "metrics": metrics,
        "events_triggered": fired,
        "impacts": impacts,
        "degraded_metrics": degraded,
        "config_version": config.get("version"),
        "source_grades": {"gscpi": "A(NY Fed)", "gpr": "A(Caldara-Iacoviello 官方)"},
        "pit_note": ("兩來源就地修訂、無官方 vintage;本地 vintage 自 2026-06-12 起"
                     "前向累積於 data/lake/world/ — 之前的歷史回測不得用本輸出"),
        "disclaimer": "recommend-only;事件=篩選/微調輸入,非倉位指令。",
    }
    if write:
        out_dir.mkdir(exist_ok=True)
        p = out_dir / f"world-monitor-{today}.json"
        p.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"wrote {p}", file=sys.stderr)
    return report


def main(argv: Optional[list[str]] = None) -> int:
    import argparse
    ap = argparse.ArgumentParser(description="world monitor — GSCPI/GPR → 世界事件")
    ap.add_argument("--out-dir", default="outputs")
    ap.add_argument("--dry-run", action="store_true", help="印結果不落盤")
    args = ap.parse_args(argv)
    rep = run_world_monitor(Path(args.out_dir), write=not args.dry_run)
    try:
        sys.stdout.reconfigure(encoding="utf-8")    # cp950 console 防護
    except Exception:
        pass
    ev = "、".join(e["id"] for e in rep["events_triggered"]) or "無"
    print(f"world-monitor:events={ev} live={rep['live_data']} "
          f"GSCPI={rep['metrics'].get('gscpi')} GPR={rep['metrics'].get('gpr')} "
          f"TWN={rep['metrics'].get('gprc_twn')}(z60 {rep['metrics'].get('gprc_twn_z60')})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
