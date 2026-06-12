"""nemoclaw 本地研究 agent — 結構化證據 → grade-E 研究草稿(recommend-only).

定位(CLAUDE.md §5 源分級紀律):本地小模型(RTX 5070 12GB,nemotron-3-nano:4b)
輸出 = **grade E(未驗證)** — 只能產「草稿 + 待驗證問題 + 建議檢索詞」,
**永不**直接寫 wiki/、永不觸發部位。升級路徑:草稿 → web/一手源逐項驗證
(researcher,URL+檢索日)→ 才可進 wiki/24 類驗證頁。高精度需求走
``SHARKS_NEMOTRON_BACKEND=nim``(雲端 49B,同一介面)。

它做的事:把本地已有的結構化證據(lake info、最新 reflexivity/rally-dna/
world-monitor 列、案例庫近鄰)拼成 context → 本地模型生成研究假設草稿 →
落 ``outputs/research-draft-<ticker>-<date>.md``。Ollama 沒開 = 優雅降級
(NemotronClient never-raise),不擋任何管線。

CLI:
    python -m sharks.ai.research_agent --ticker COHR [--dry-run]
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Optional

GRADE_NOTE = ("grade-E(本地小模型,未驗證)— 僅供研究起點;進 wiki 前每項主張須"
              "補 URL+檢索日;依 CLAUDE.md §5 不得觸發任何部位動作")


def _latest_json(prefix: str, out_dir: Path = Path("outputs")) -> dict:
    files = sorted(p for p in out_dir.glob(f"{prefix}-*.json")
                   if "intraday" not in p.name and not p.name.endswith(".bak"))
    if not files:
        return {}
    try:
        return json.loads(files[-1].read_text(encoding="utf-8"))
    except Exception:
        return {}


def gather_context(ticker: str, *, out_dir: Path = Path("outputs"),
                   lake_info_dir: Path = Path("data/lake/info")) -> dict:
    """拼本地結構化證據(全部可離線取得;缺哪塊就標 None,不發明)。"""
    t = ticker.upper()
    ctx: dict = {"ticker": t}
    try:
        info = json.loads((lake_info_dir / f"{t}.json").read_text(encoding="utf-8"))
        ctx["sector"] = info.get("sector")
        ctx["industry"] = info.get("industry")
        ctx["summary"] = (info.get("longBusinessSummary") or "")[:600]
    except Exception:
        ctx["sector"] = ctx["industry"] = ctx["summary"] = None
    reflex = _latest_json("reflexivity", out_dir)
    ctx["reflexivity"] = next((r for r in (reflex.get("rows") or [])
                               if r.get("ticker") == t), None)
    dna = _latest_json("rally-dna", out_dir)
    match = (dna.get("dna_match_today") or {}).get("top") or []
    ctx["dna_row"] = next((r for r in match if r.get("ticker") == t), None)
    world = _latest_json("world-monitor", out_dir)
    ctx["world_events"] = [e.get("id") for e in (world.get("events_triggered") or [])]
    ctx["world_metrics"] = {k: (world.get("metrics") or {}).get(k)
                            for k in ("gscpi", "gpr", "gprc_twn", "gprc_twn_z60")}
    try:
        from sharks.scoring.global_exposure import exposure_for
        ctx["exposure"] = exposure_for(t, ctx.get("sector"))
    except Exception:
        ctx["exposure"] = None
    try:
        from sharks.memory.case_store import CaseStore
        feats = {k: ctx["dna_row"].get(k) for k in
                 ("dd36", "dist_ma10", "buy9_max", "r3m", "vol_ratio")} \
            if ctx.get("dna_row") else None
        if feats and all(v is not None for v in feats.values()):
            ctx["similar_cases"] = CaseStore().query_similar(feats, n=3)
        else:
            ctx["similar_cases"] = None
    except Exception:
        ctx["similar_cases"] = None
    return ctx


def build_prompt(ctx: dict) -> list[dict]:
    """純函式:context → chat messages。要求模型輸出固定四節草稿。"""
    system = ("你是 $hark 鯊魚系統的本地研究助理。你只能根據提供的結構化證據推理,"
              "不知道的就寫「待查」。輸出繁體中文 markdown,固定四節:"
              "## 假設(每條一行,標注依據哪個欄位)/ ## 反方論點 / "
              "## 待驗證問題(每條附建議檢索詞)/ ## 風險備註。"
              "禁止給出買賣建議;禁止編造數字或來源。")
    user = ("研究標的證據包(JSON):\n" +
            json.dumps(ctx, ensure_ascii=False, indent=1, default=str) +
            "\n\n請產出研究草稿(此輸出為 grade-E,將由人類/網證流程驗證)。")
    return [{"role": "system", "content": system},
            {"role": "user", "content": user}]


def run(ticker: str, *, client=None, write: bool = True,
        out_dir: Path = Path("outputs"),
        gather: Callable[..., dict] = gather_context) -> dict:
    """產草稿信封。client 可注入(測試);預設 NemotronClient(never-raise)。"""
    if client is None:
        from sharks.ai.nemotron_client import NemotronClient
        client = NemotronClient()
    ctx = gather(ticker, out_dir=out_dir) if gather is gather_context else gather(ticker)
    call = client.chat("executor", build_prompt(ctx),
                       reasoning="off", temperature=0.3, max_tokens=900)
    today = datetime.now().strftime("%Y-%m-%d")
    env = {
        "ticker": ticker.upper(), "as_of": today,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "engine": "research-agent-local", "grade": "E",
        "llm_involvement": "draft-only(grade-E;不進 KPI、不觸發部位)",
        "model": getattr(call, "model", None),
        "backend": getattr(call, "backend", None),
        "ok": not getattr(call, "error", None),
        "error": getattr(call, "error", None),
        "context_keys_present": sorted(k for k, v in ctx.items() if v),
        "draft_md": getattr(call, "content", "") or "",
        "note": GRADE_NOTE,
    }
    if write and env["ok"] and env["draft_md"]:
        out_dir.mkdir(exist_ok=True)
        p = out_dir / f"research-draft-{ticker.upper()}-{today}.md"
        p.write_text(
            f"# 研究草稿 — {ticker.upper()}({today})\n\n"
            f"> {GRADE_NOTE}。model: {env['model']}({env['backend']})\n\n"
            f"{env['draft_md']}\n", encoding="utf-8")
        env["path"] = str(p)
        print(f"wrote {p}", file=sys.stderr)
    return env


def main(argv: Optional[list[str]] = None) -> int:
    import argparse
    ap = argparse.ArgumentParser(description="nemoclaw 本地研究草稿(grade-E)")
    ap.add_argument("--ticker", required=True)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args(argv)
    env = run(args.ticker, write=not args.dry_run)
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    if not env["ok"]:
        print(f"research-agent: degraded ({env['error']}) — Ollama 未開或 backend disabled")
        return 0
    print(env.get("path") or env["draft_md"][:400])
    return 0


if __name__ == "__main__":
    sys.exit(main())
