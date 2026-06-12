"""世界條件化 regime 轉移表 — 純計數基線(非 ML).

把 rally_dna.classify_states4 的 QQQ 月線四態(mania/bull/bear/crisis)按
世界指標分箱(GPR 地緣風險 / GSCPI 供應鏈壓力)做經驗轉移計數:
P(次月狀態 | 當月狀態) 全期 + 各 gpr_band / gscpi_band / 聯合箱。

定位:這是未來任何 ML(LightGBM 等)必須打敗的誠實基線 — 工具只在需求
長過它時才升級。n<8 的薄格標 low_n,不從薄格下結論。

PIT 誠實揭露(philosophy/09):
  1. 條件化用「月 t 世界值 → 轉移 t→t+1」,隱含月底可見假設;GPR 每日版
     近即時可近似成立,GSCPI 為次月初發布 → gscpi 條件化含輕微後見。
  2. GPR/GSCPI 兩來源每次發布就地修訂全史、無官方 vintage —— 本表是
     「以今日修訂史回看」的描述統計,非可交易回測。
  3. 故 observe-first:輸出僅供 brief 決策支援文字,不進 KPI、不改 sizing。

世界月度列由呼叫端注入(list of {as_of, gpr, gscpi, ...});main() 嘗試載入
最新 outputs/world-backfill-*.json 的 monthly_rows,缺檔則退化為無條件表。

llm_involvement: none — 全 rule-based 計數;LLM 只設計規則,不在迴圈內。

CLI:
    python -m sharks.backtest.regime_transitions    # → outputs/regime-transitions-<date>.json
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

# ── 分箱閾值(模組常數;改校準改 config/world_events.json 後同步這裡)──
GPR_ELEVATED_MIN = 146.0
GPR_EXTREME_MIN = 330.0
GSCPI_PRESSURE_MIN = 1.0
GSCPI_SPIKE_MIN = 1.5
LOW_N = 8

THRESHOLDS_DOC = {
    "_doc": ("分箱錨定 config/world_events.json calibration(as_of 2026-06-12,"
             "GPR 月度 1985-01 起 n=497):gpr p90=146(GPR_ELEVATED 事件同源)、"
             "p99=330(GPR_EXTREME 事件閾值);GSCPI 本身即 NY Fed 全史 z-score"
             "(1998+,mean≈0/sd≈1)→ 1.0=壓力、1.5=尖峰(GSCPI_SPIKE 事件閾值)。"
             "LOW_N=8:二項比例 n<8 時標準誤 >17pp,薄格只計數不下結論。"),
    "gpr_band": {"calm": f"< {GPR_ELEVATED_MIN}", "elevated": f">= {GPR_ELEVATED_MIN}",
                 "extreme": f">= {GPR_EXTREME_MIN}"},
    "gscpi_band": {"normal": f"< {GSCPI_PRESSURE_MIN}", "pressure": f">= {GSCPI_PRESSURE_MIN}",
                   "spike": f">= {GSCPI_SPIKE_MIN}"},
    "low_n_threshold": LOW_N,
}

STATES = ("bull", "mania", "bear", "crisis")        # 同 rally_dna.regime_markov4 順序


# ── 純函式:分箱 ──

def _metric(row: dict, key: str):
    """平鋪鍵優先,退到 world_backfill 的巢狀 metrics 形狀;缺 → None。"""
    v = row.get(key)
    if v is not None:
        return v
    m = row.get("metrics")
    return m.get(key) if isinstance(m, dict) else None


def band_of(metrics_row: Optional[dict]) -> dict:
    """世界月度列 → {gpr_band, gscpi_band}。缺值 → None(不發明)。

    接受平鋪列({as_of, gpr, gscpi, ...})或 world_backfill 實際輸出的
    巢狀形狀({as_of, metrics: {gpr, gscpi, ...}})。
    """
    row = metrics_row or {}
    gpr, gscpi = _metric(row, "gpr"), _metric(row, "gscpi")
    if gpr is None:
        gpr_band = None
    elif gpr >= GPR_EXTREME_MIN:
        gpr_band = "extreme"
    elif gpr >= GPR_ELEVATED_MIN:
        gpr_band = "elevated"
    else:
        gpr_band = "calm"
    if gscpi is None:
        gscpi_band = None
    elif gscpi >= GSCPI_SPIKE_MIN:
        gscpi_band = "spike"
    elif gscpi >= GSCPI_PRESSURE_MIN:
        gscpi_band = "pressure"
    else:
        gscpi_band = "normal"
    return {"gpr_band": gpr_band, "gscpi_band": gscpi_band}


# ── 月份助手 ──

def _month_key(d) -> str:
    return str(d)[:7]


def _next_month(ym: str) -> str:
    y, m = int(ym[:4]), int(ym[5:7])
    return f"{y + m // 12}-{m % 12 + 1:02d}"


# ── 轉移表(純計數)──

def _new_cell() -> dict:
    return {"n": 0, "counts": {s: 0 for s in STATES}}


def _bump(cell: dict, nxt: str) -> None:
    cell["n"] += 1
    cell["counts"][nxt] = cell["counts"].get(nxt, 0) + 1


def _finalize(cell: dict) -> dict:
    n = cell["n"]
    probs = ({s: round(c / n, 4) for s, c in cell["counts"].items()} if n else None)
    return {"n": n, "counts": cell["counts"], "probs": probs, "low_n": n < LOW_N}


def transition_table(states: list, world_rows: Optional[list] = None) -> dict:
    """月度狀態序列 → 經驗轉移表(無條件 + 各世界箱)。

    states: [(date, state)],月份須連續 — 月份斷層的配對跳過(skipped_gaps)。
    world_rows: [{as_of, gpr, gscpi, ...}] 月度世界列;月 t 的箱條件化
    轉移 t→t+1。None → 只出無條件表(退化路徑)。
    """
    norm = [(_month_key(d), s) for d, s in states if s is not None]
    pairs, skipped = [], 0
    for (ym_a, cur), (ym_b, nxt) in zip(norm[:-1], norm[1:]):
        if _next_month(ym_a) != ym_b:
            skipped += 1
            continue
        pairs.append((ym_a, cur, nxt))

    world_map: dict[str, dict] = {}
    if world_rows is not None:
        for r in world_rows:
            ym = _month_key((r or {}).get("as_of") or "")
            if len(ym) == 7:
                world_map[ym] = band_of(r)

    uncond = {s: _new_cell() for s in STATES}
    by_gpr: dict[str, dict] = {}
    by_gscpi: dict[str, dict] = {}
    by_joint: dict[str, dict] = {}
    n_with_world = 0
    for ym, cur, nxt in pairs:
        _bump(uncond.setdefault(cur, _new_cell()), nxt)
        if world_rows is None:
            continue
        bands = world_map.get(ym)
        gb = bands.get("gpr_band") if bands else None
        cb = bands.get("gscpi_band") if bands else None
        if gb is None and cb is None:
            continue                                    # 該月無世界值 → 只進無條件表
        n_with_world += 1
        if gb is not None:
            _bump(by_gpr.setdefault(gb, {s: _new_cell() for s in STATES})
                  .setdefault(cur, _new_cell()), nxt)
        if cb is not None:
            _bump(by_gscpi.setdefault(cb, {s: _new_cell() for s in STATES})
                  .setdefault(cur, _new_cell()), nxt)
        if gb is not None and cb is not None:
            _bump(by_joint.setdefault(f"{gb}|{cb}", {s: _new_cell() for s in STATES})
                  .setdefault(cur, _new_cell()), nxt)

    def _fin_table(tbl: dict) -> dict:
        return {band: {s: _finalize(c) for s, c in cells.items()}
                for band, cells in tbl.items()}

    out = {
        "states": list(STATES),
        "low_n_threshold": LOW_N,
        "n_transitions": len(pairs),
        "skipped_gaps": skipped,
        "unconditioned": {s: _finalize(c) for s, c in uncond.items()},
        "by_gpr_band": None,
        "by_gscpi_band": None,
        "by_joint": None,
        "world_alignment": None,
    }
    if world_rows is not None:
        out["by_gpr_band"] = _fin_table(by_gpr)
        out["by_gscpi_band"] = _fin_table(by_gscpi)
        out["by_joint"] = _fin_table(by_joint)
        out["world_alignment"] = {"n_with_world": n_with_world,
                                  "n_without_world": len(pairs) - n_with_world,
                                  "n_world_rows": len(world_map)}
    return out


# ── 展望(observe-first;不改 sizing)──

def regime_outlook(current_state: Optional[str], current_bands: Optional[dict],
                   table: dict) -> dict:
    """目前狀態+世界箱 → 次月分布(回退鏈:joint → gpr_band → 無條件)。

    薄格(low_n)或缺格觸發回退;無條件格即使 low_n 也用(已是最底層,
    讀數自帶 low_n 旗)。輸出 = 決策支援文字素材,NO sizing 變更。
    """
    note = "observe-first:次月分布僅供 brief 決策支援,不進 KPI、不改 sizing。"
    bands = current_bands or {}
    gb, cb = bands.get("gpr_band"), bands.get("gscpi_band")
    base = {"current_state": current_state,
            "current_bands": {"gpr_band": gb, "gscpi_band": cb}, "note": note}
    if current_state is None:
        return {**base, "used_level": None, "n": 0, "next_month_probs": None,
                "low_n": None, "fallback_path": [{"level": None, "reason": "no_current_state"}]}

    def _cell(level: str) -> Optional[dict]:
        if level == "joint" and gb and cb:
            return ((table.get("by_joint") or {}).get(f"{gb}|{cb}") or {}).get(current_state)
        if level == "gpr_band" and gb:
            return ((table.get("by_gpr_band") or {}).get(gb) or {}).get(current_state)
        if level == "unconditioned":
            return (table.get("unconditioned") or {}).get(current_state)
        return None

    tried = []
    for level in ("joint", "gpr_band", "unconditioned"):
        cell = _cell(level)
        if cell is None:
            tried.append({"level": level, "reason": "no_cell"})
            continue
        if cell["n"] == 0:
            tried.append({"level": level, "reason": "n=0"})
            continue
        if level != "unconditioned" and cell["low_n"]:
            tried.append({"level": level,
                          "reason": f"low_n(n={cell['n']}<{LOW_N})"})
            continue
        return {**base, "used_level": level, "n": cell["n"],
                "next_month_probs": cell["probs"], "low_n": cell["low_n"],
                "fallback_path": tried}
    return {**base, "used_level": None, "n": 0, "next_month_probs": None,
            "low_n": None, "fallback_path": tried}


# ── 報告組裝 + 落盤 ──

def _load_backfill_rows(out_dir: Path) -> tuple[Optional[list], Optional[str]]:
    """最新 outputs/world-backfill-*.json → (monthly_rows, 檔名);缺/壞 → (None, None)。"""
    files = sorted(Path(out_dir).glob("world-backfill-*.json"))
    if not files:
        return None, None
    try:
        payload = json.loads(files[-1].read_text(encoding="utf-8"))
    except Exception:
        return None, None
    rows = payload.get("monthly_rows") if isinstance(payload, dict) else None
    if not isinstance(rows, list) or not rows:
        return None, None
    if not all(isinstance(r, dict) and r.get("as_of") for r in rows):
        return None, None
    return rows, files[-1].name


def build_report(states: list, world_rows: Optional[list], *, today: str,
                 source_name: Optional[str] = None) -> dict:
    table = transition_table(states, world_rows)
    current_state = states[-1][1] if states else None
    if world_rows:
        latest = max(world_rows, key=lambda r: str(r.get("as_of") or ""))
        current_bands = band_of(latest)
    else:
        current_bands = {"gpr_band": None, "gscpi_band": None}
    outlook = regime_outlook(current_state, current_bands, table)
    return {
        "as_of": today,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "engine": "regime-transitions",
        "llm_involvement": "none",
        "n_months": len(states),
        "n_transitions": table["n_transitions"],
        "world_conditioned": world_rows is not None,
        "world_rows_source": source_name,
        "thresholds": THRESHOLDS_DOC,
        "table": table,
        "current_outlook": outlook,
        "note": ("observe-first:純計數基線(非 ML)— 未來任何模型須先打敗本表。"
                 "輸出不進 KPI、不改 sizing。"),
        "disclaimer": ("recommend-only;以今日修訂史回看的描述統計,非可交易回測"
                       "(GPR/GSCPI 無官方 vintage;GSCPI 次月初發布 → "
                       "gscpi 條件化含輕微後見)。"),
    }


def write_report(report: dict, out_dir: Path, today: str) -> Path:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    p = out_dir / f"regime-transitions-{today}.json"
    p.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    return p


def main(argv: Optional[list[str]] = None) -> int:
    import argparse
    ap = argparse.ArgumentParser(
        description="世界條件化 regime 轉移表(計數基線,observe-first)")
    ap.add_argument("--out-dir", default="outputs")
    ap.add_argument("--dry-run", action="store_true", help="印結果不落盤")
    args = ap.parse_args(argv)

    from sharks.backtest.rally_dna import classify_states4, load_monthly
    qqq = load_monthly("QQQ")
    if qqq is None:
        print("regime-transitions: missing QQQ lake (data/lake/prices/QQQ_1mo.parquet)",
              file=sys.stderr)
        return 1
    series = classify_states4(qqq["Close"]).dropna()
    states = [(_month_key(idx), st) for idx, st in series.items()]
    print(f"regime-transitions: states n={len(states)} "
          f"({states[0][0]} -> {states[-1][0]})", file=sys.stderr)

    world_rows, source_name = _load_backfill_rows(Path(args.out_dir))
    if world_rows is None:
        print("regime-transitions: no world-backfill output -> "
              "degrade to unconditioned table", file=sys.stderr)
    else:
        print(f"regime-transitions: world rows n={len(world_rows)} ({source_name})",
              file=sys.stderr)

    today = datetime.now().strftime("%Y-%m-%d")
    report = build_report(states, world_rows, today=today, source_name=source_name)
    if not args.dry_run:
        p = write_report(report, Path(args.out_dir), today)
        print(f"wrote {p}", file=sys.stderr)

    try:
        sys.stdout.reconfigure(encoding="utf-8")        # cp950 console 防護
    except Exception:
        pass
    ol = report["current_outlook"]
    probs = ol.get("next_month_probs") or {}
    top = max(probs, key=probs.get) if probs else None
    print(f"regime-transitions: state={ol.get('current_state')} "
          f"level={ol.get('used_level')} n={ol.get('n')} "
          f"top_next={top}({probs.get(top)}) "
          f"conditioned={report['world_conditioned']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
