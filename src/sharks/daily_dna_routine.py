"""每日 DNA 例行 — 早上累積數據,美股開盤前產出艙位調整 brief.

主理人指令(2026-06-12):「每天早晚排程累積數據,一開盤告訴我要做什麼艙位調整」。

兩個模式(台北時間;美股 EDT 開盤 = 21:30 TPE):
  morning  07:40 二~六(美股已收盤數小時,EOD bar 完整):
           刷新 lake 1d → EOD ma-scan 落盤 → reflexivity 掃描 → rally_dna(評分落盤累積)
  preopen  21:10 一~五(開盤前 ~20 分):
           彙整最新 outputs(健檢/DNA 分桶/反身性/markov 態)→ outputs/position-brief-<date>.md

排程:Windows 工作排程器(SharksDNA-Morning / SharksDNA-PreOpen);**機器需在該時段開機**。
recommend-only:brief 是研究建議,執行永遠是人的動作(CLAUDE.md §2)。

CLI:
    python -m sharks.daily_dna_routine morning
    python -m sharks.daily_dna_routine preopen
"""

from __future__ import annotations

import json
import os
import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
LOG = PROJECT_ROOT / "outputs" / "dna-routine-log.txt"


def _log(msg: str) -> None:
    LOG.parent.mkdir(exist_ok=True)
    with LOG.open("a", encoding="utf-8") as fh:
        fh.write(f"{datetime.now(timezone.utc).isoformat()} {msg}\n")


def _latest(prefix: str) -> dict:
    files = sorted(p for p in (PROJECT_ROOT / "outputs").glob(f"{prefix}-*.json")
                   if "intraday" not in p.name and not p.name.endswith(".bak"))
    if not files:
        return {}
    try:
        return json.loads(files[-1].read_text(encoding="utf-8"))
    except Exception:
        return {}


def run_morning() -> int:
    """數據累積:lake 刷新 → EOD 掃描 → 反身性 → rally_dna。各步獨立 try,一步炸不拖全局。"""
    os.chdir(PROJECT_ROOT)
    _log("morning: start")
    from concurrent.futures import ThreadPoolExecutor
    try:
        from sharks.data.data_lake import store_prices
        from sharks.scoring import ma_scanner
        tks = ma_scanner.lake_tickers()
        with ThreadPoolExecutor(max_workers=8) as ex:
            errs = sum(1 for r in ex.map(lambda t: store_prices(t, "5y", "1d"), tks)
                       if "error" in r or r.get("status") == "no_data")
        rep = ma_scanner.scan_lake()
        path = ma_scanner.write_scan(rep)
        _log(f"morning: lake {len(tks)} refreshed (err {errs}); scan -> {path}")
    except Exception:
        _log("morning: SCAN FAILED\n" + traceback.format_exc())
    try:
        from sharks.scoring import reflexivity
        reflexivity.main([])
        _log("morning: reflexivity ok")
    except Exception:
        _log("morning: reflexivity FAILED\n" + traceback.format_exc())
    try:
        from sharks.regime import world_monitor          # 須在 rally_dna 前(它讀本步輸出)
        res = world_monitor.run_world_monitor()
        _log(f"morning: world-monitor ok (events {len(res.get('events_triggered') or [])}, "
             f"live={res.get('live_data')})")
    except Exception:
        _log("morning: world-monitor FAILED\n" + traceback.format_exc())
    try:
        from sharks.backtest import rally_dna
        rally_dna.main([])
        _log("morning: rally_dna ok (scores logged)")
    except Exception:
        _log("morning: rally_dna FAILED\n" + traceback.format_exc())
    try:
        from sharks.backtest import failed_analogs
        res = failed_analogs.collect(10)        # Phase 2:每晨收 10 檔下市票(~50/週)
        _log(f"morning: failed-analogs collected {res['collected']} "
             f"(dir {res['total_in_dir']})")
    except Exception:
        _log("morning: failed-analogs collect FAILED\n" + traceback.format_exc())
    try:
        from sharks.memory import case_store    # 每日:案例庫向量 sync(rally_dna 之後)
        res = case_store.sync_from_outputs()
        _log(f"morning: case-store sync ok ({res})")
    except Exception:
        _log("morning: case-store sync FAILED\n" + traceback.format_exc())
    now = datetime.now()
    if now.weekday() == 1:                      # 週二 TPE = 美股週一收盤後:ABM 情境模擬
        try:
            from sharks.regime import abm_supply_chain
            abm_supply_chain.main([])
            _log("morning: abm ok")
        except Exception:
            _log("morning: abm FAILED\n" + traceback.format_exc())
    if now.weekday() == 5:                      # 週六 TPE = 美股週五收盤後:存活率全量重算
        try:                                    # (collect 每日累積分母;cap 隨之動態更新)
            from sharks.backtest import failed_analogs
            failed_analogs.main([])             # analyze → outputs/failed-analogs-<date>.json
            _log("morning: failed-analogs survival recompute ok")
        except Exception:
            _log("morning: failed-analogs recompute FAILED\n" + traceback.format_exc())
        try:                                    # 世界史回填 + regime 轉移表(週更,皆可再生)
            from sharks.regime import world_backfill
            world_backfill.main([])
            from sharks.backtest import regime_transitions
            regime_transitions.main([])
            _log("morning: world-backfill + regime-transitions ok")
        except Exception:
            _log("morning: backfill/transitions FAILED\n" + traceback.format_exc())
    if now.day == 1:                            # 每月 1 日:世界閾值重校建議(人工套用)
        try:
            from sharks.regime import world_monitor
            rep = world_monitor.recalibrate()
            flagged = sum(1 for s in rep.get("suggestions") or [] if s.get("review"))
            _log(f"morning: world recalibrate ok ({len(rep.get('suggestions') or [])} "
                 f"suggestions, {flagged} review-flagged)")
        except Exception:
            _log("morning: world recalibrate FAILED\n" + traceback.format_exc())
    _log("morning: done")
    return 0


def _api_usage_line() -> str:
    """當日 per-source API 計數(call_log;觀測用,DataRouter 提案的採納內核)。"""
    try:
        from sharks.data.call_log import summary
        s = summary()
        if not s:
            return "(無記錄)"
        return " · ".join(f"{src} {v['calls']}" + (f"(err {v['errors']})" if v["errors"] else "")
                          for src, v in sorted(s.items()))
    except Exception:
        return "(無記錄)"


def _world_insight_lines(world: dict) -> list[str]:
    """全球風險區塊的觀察層三行(行為偏差/歷史鏡頭/regime 展望)— 缺料即省略,
    全部 observe-first:文字參考,不 gate 任何 KPI/sizing。"""
    L: list[str] = []
    bv = world.get("behavioral") or {}
    if bv.get("score") is not None:
        L.append(f"- 行為偏差分數:**{bv['score']}/10**(顯式先驗;"
                 f"組件 {'+'.join(sorted((bv.get('components') or {}).keys())) or '—'})"
                 + (f" — {bv['mania_note']}" if bv.get("mania_note") else ""))
    bf = _latest("world-backfill")
    study = (bf.get("event_forward_study") or {})
    spike = (study.get("events") or {}).get("GSCPI_SPIKE") or {}
    base = study.get("base_rate") or {}
    if spike.get("fwd") and base.get("fwd"):
        def med(d, h):
            v = ((d.get("fwd") or {}).get(h) or {}).get("median_pct")
            return v if v is not None else "—"
        L.append(f"- 歷史鏡頭(1999+,synthetic-revised vintage):GSCPI_SPIKE 月份 QQQ 前向 "
                 f"3m {med(spike, '3m')}% / 6m {med(spike, '6m')}% vs 基準 "
                 f"{med(base, '3m')}% / {med(base, '6m')}% — 唯一明確跑輸基準的事件;"
                 f"TS_HIGH 月份歷史上不低於基準(恐懼≠賣訊,實質供應鏈壓力才是)")
    rt = _latest("regime-transitions")
    ol = rt.get("current_outlook") or {}
    dist = ol.get("next_month_probs") or {}
    if dist:
        top = sorted(dist.items(), key=lambda kv: -kv[1])[:3]
        L.append(f"- 下月態展望(經驗計數,observe-first):"
                 + " / ".join(f"{k} {v:.0%}" for k, v in top)
                 + f"(條件層級 {ol.get('used_level', '?')},n={ol.get('n', '?')}"
                 + (";低樣本" if ol.get("low_n") else "") + ")")
    return L


def compose_position_brief() -> str:
    """艙位調整 brief(純彙整,不重算):markov 態 → 曝險水位;健檢 → 持倉動作;
    DNA 分桶 → 新倉紀律;反身性 → 剔除警示。"""
    today = datetime.now().strftime("%Y-%m-%d")
    dna = _latest("rally-dna")
    reflex = _latest("reflexivity")
    world = _latest("world-monitor")
    abm = _latest("abm-supply-chain")
    try:
        from sharks.ui.server import holdings_health
        health = holdings_health("all")
    except Exception:
        health = {"rows": [], "error": traceback.format_exc()[-200:]}

    m4 = dna.get("regime_markov4") or {}
    state = m4.get("current_state", "?")
    exposure_rule = {
        "mania": "不加總曝險;移動停利收緊;新倉只准 DNA 可入候補(現=0 即不開)",
        "bull": "正常水位;依燃料閘+streak 進場",
        "bear": "DNA 抄底熱區 — 小注分批,僅限觸發確認",
        "crisis": "強制降風險:槓桿歸零、總曝險減半、只留核心",
    }.get(state, "狀態未知 — 保守")

    match = dna.get("dna_match_today") or {}
    buckets: dict[str, list] = {}
    for r in match.get("top") or []:
        buckets.setdefault(r.get("bucket", "?"), []).append(r["ticker"])
    breaks = [r["ticker"] for r in (reflex.get("rows") or []) if r.get("verdict") == "斷裂警告"]
    held = {r["ticker"]: r for r in health.get("rows") or []}
    held_breaks = sorted(set(held) & set(breaks))

    act: dict[str, list[str]] = {}
    for r in health.get("rows") or []:
        a = r.get("action", "?")
        sw = "/".join(s["ticker"] for s in (r.get("swaps") or [])[:2])
        act.setdefault(a, []).append(f"{r['ticker']}" + (f"→{sw}" if sw and a == "換股" else ""))

    wm = world.get("metrics") or {}
    wm_events = world.get("events_triggered") or []
    wm_line = ("、".join(f"**{e.get('id')}**({e.get('severity')})" for e in wm_events)
               if wm_events else "(無觸發事件)")

    L = [f"# 開盤前艙位調整 — {today}(美股開盤前)",
         "",
         "> recommend-only;系統只建議、永不下單。執行與否是人的決定。",
         "",
         f"## 1. 市場狀態:**{state}**(QQQ 月線四態)",
         f"- 曝險規則:{exposure_rule}",
         f"- MC 至 2027 末:中位 {((m4.get('mc_end_return_pct') or {}).get('median'))}% · "
         f"P(正) {m4.get('mc_p_end_positive')}%(iid 低估尾巴,曝險跟狀態不跟點估計)",
         "",
         "## 2. 全球風險(World Monitor)",
         f"- 觸發事件:{wm_line}",
         f"- GSCPI {wm.get('gscpi', '—')}(z 單位;≥1.5=尖峰)· "
         f"GPR {wm.get('gpr', '—')}(基準~100;p95≈169/p99≈330)· "
         f"台灣分項 {wm.get('gprc_twn', '—')}(60月z {wm.get('gprc_twn_z60', '—')};p95≈0.25)",
         *([f"- ABM 情境(週更):TS_HIGH 先驗 {(abm.get('scenario_priors') or {}).get('TS_HIGH', '—')} · "
            f"預期斷供 {abm.get('expected_disruption_quarters', '—')} 季 · deep-kill 折減 "
            f"{abm.get('deepkill_survival_delta_pct', '—')}pp"
            f"(TS_HIGH 條件式 {((abm.get('per_scenario_loss') or {}).get('TS_HIGH') or {}).get('survival_delta_pct_conditional', '—')}pp;"
            f"與 cap 乘數不疊乘)"] if abm else []),
         *_world_insight_lines(world),
         "",
         "## 3. 持倉動作(健檢自動裁決)"]
    for a in ("清倉", "換股", "減碼", "待驗證", "續抱⚠"):
        if act.get(a):
            L.append(f"- **{a}**:{'、'.join(act[a])}")
    # watch 名單帶近鄰失敗警示(AXTI 型)與 human_review 旗
    def tag(r):
        t = r["ticker"]
        nf = sum(1 for s in (r.get("similar_cases") or []) if s.get("kind") == "fail")
        flags = ("🚩" if r.get("human_review") else "") + (f"⚠近鄰失敗×{nf}" if nf else "")
        return f"{t}{('(' + flags + ')') if flags else ''}"
    watch_tagged = [tag(r) for r in (match.get("top") or []) if r.get("bucket") == "watch"]

    fa = _latest("failed-analogs")
    boot = (fa.get("survival_bootstrap") or {}).get("survival_pct") or {}
    cap = fa.get("cap_recommendation") or {}
    rules_count: dict[str, int] = {}
    for r in match.get("top") or []:
        for rid in r.get("rules_fired") or []:
            rules_count[rid] = rules_count.get(rid, 0) + 1

    # 世界事件 cap 乘數:套在消費端(failed-analogs 保持純存活統計;出處全寫進 brief)
    base_cap = cap.get("recommended", 11)
    wm_cap_mult = (world.get("impacts") or {}).get("deepkill_cap_multiplier")
    if isinstance(wm_cap_mult, (int, float)) and wm_cap_mult < 1 and isinstance(base_cap, (int, float)):
        cap_txt = (f"{base_cap}% × {wm_cap_mult}(世界事件 "
                   f"{'、'.join(e.get('id', '?') for e in wm_events)})= "
                   f"**{round(base_cap * wm_cap_mult, 1)}%**")
    else:
        cap_txt = f"**{base_cap}%**"
    L += ["",
          "## 4. 持倉 × 反身性斷裂交集(最高優先警示)",
          f"- {'、'.join(held_breaks) if held_breaks else '(無 — 持倉沒有踩在斷裂名單上)'}",
          "",
          "## 5. 新倉紀律(DNA 雙濾鏡分桶)",
          f"- 可入候補(≥85):{'、'.join(buckets.get('可入候補', [])) or '**0 檔 → 今日不開新倉**'}",
          f"- watch(≥75):{'、'.join(watch_tagged) or '—'}",
          f"- 剔除(斷裂):{'、'.join(buckets.get('剔除', [])) or '—'}",
          f"- sizing:deep-kill 袖上限 {cap_txt}(資料驅動)· "
          f"單筆風險 ≤1-2% 總資本 · 樂透型=衛星倉,主倉走淺基型",
          "",
          "## 6. 系統健康(audit/observability)",
          f"- deep-kill 存活率:**{fa.get('survival_rate_pct', '—')}%**"
          + (f"(bootstrap 90% CI {boot.get('ci90', ['—', '—'])[0]}–{boot.get('ci90', ['—', '—'])[1]}%)"
             if boot.get("ci90") else "")
          + f" · 事件 n={fa.get('n_events', '—')}(下市票 {fa.get('n_from_delisted', 0)})",
          f"- 案例庫:{(dna.get('case_library') or {}).get('n_cases', '—')} 成功 + "
          f"{len(fa.get('failed_events') or [])} 失敗類比",
          f"- 規則觸發統計(本批):{rules_count or '無'}",
          f"- 數據新鮮度:scan {health.get('as_of_scan')} · rally-dna {dna.get('as_of')} · "
          f"reflexivity {reflex.get('as_of_scan')} · "
          f"world {str(world.get('retrieved_at') or '—')[:10]}"
          + ("(stale)" if world.get("stale_sources") else ""),
          f"- API 用量(今日 UTC):{_api_usage_line()}",
          "",
          f"_generated {datetime.now(timezone.utc).isoformat()}_"]
    return "\n".join(L)


def risk_queue_entries(today: str, held_breaks: list[str],
                       match_rows: list[dict], world_events: list[str]) -> list[dict]:
    """Risk Officer 待審佇列(純函式):持倉×斷裂交集(最高優先)+ human_review 票。
    每筆帶 reason 與來源欄位,append-only JSONL 留審計鏈。"""
    entries = []
    for t in held_breaks:
        entries.append({"date": today, "ticker": t, "priority": "high",
                        "reason": "持倉 × 反身性斷裂交集",
                        "source": "reflexivity ∩ holdings"})
    for r in match_rows or []:
        if r.get("human_review"):
            entries.append({"date": today, "ticker": r.get("ticker"),
                            "priority": "medium",
                            "reason": "、".join(r.get("rules_fired") or []) or "human_review",
                            "source": "dna_match_today",
                            "world_events": world_events or None})
    return entries


def _append_risk_queue(entries: list[dict]) -> int:
    """冪等 append:同 (date,ticker,reason) 不重複寫。回傳新增筆數。"""
    q = PROJECT_ROOT / "outputs" / "risk-review-queue.jsonl"
    seen = set()
    if q.exists():
        for line in q.read_text(encoding="utf-8").splitlines():
            try:
                d = json.loads(line)
                seen.add((d.get("date"), d.get("ticker"), d.get("reason")))
            except Exception:
                continue
    new = [e for e in entries if (e["date"], e["ticker"], e["reason"]) not in seen]
    if new:
        with q.open("a", encoding="utf-8") as fh:
            for e in new:
                fh.write(json.dumps(e, ensure_ascii=False) + "\n")
    return len(new)


def _local_llm_commentary(md: str) -> str:
    """可選:本地 nemotron 評論區(grade-E,永不 gate 任何裁決)。失敗回空字串。"""
    try:
        from sharks.ai.nemotron_client import NemotronClient
        client = NemotronClient()
        call = client.chat("executor", [
            {"role": "system",
             "content": ("你是 $hark 的本地 Risk Officer 助理。讀完艙位 brief,"
                         "用繁體中文輸出最多 4 條一行評論:優先指出(1)brief 內互相"
                         "矛盾之處(2)被低估的風險交集(3)執行紀律提醒。"
                         "禁止建議買賣;不知道就不寫;不重複 brief 已明說的內容。")},
            {"role": "user", "content": md[:6000]},
        ], reasoning="off", temperature=0.2, max_tokens=350)
        if getattr(call, "error", None) or not getattr(call, "content", ""):
            return ""
        return ("\n\n## 7. 本地模型評論(nemotron · grade-E — 僅供參考,"
                "不 gate 任何裁決)\n" + call.content.strip() + "\n")
    except Exception:
        return ""


def run_preopen() -> int:
    os.chdir(PROJECT_ROOT)
    _log("preopen: start")
    md = compose_position_brief()
    md += _local_llm_commentary(md)             # Ollama 沒開 = 空字串,brief 照常
    p = PROJECT_ROOT / "outputs" / f"position-brief-{datetime.now().strftime('%Y-%m-%d')}.md"
    p.write_text(md, encoding="utf-8")
    _log(f"preopen: wrote {p}")
    try:                                        # Risk Officer 待審佇列(append-only)
        today = datetime.now().strftime("%Y-%m-%d")
        dna = _latest("rally-dna")
        reflex = _latest("reflexivity")
        world = _latest("world-monitor")
        breaks = [r["ticker"] for r in (reflex.get("rows") or [])
                  if r.get("verdict") == "斷裂警告"]
        from sharks.ui.server import holdings_health
        held = {r["ticker"] for r in (holdings_health("all").get("rows") or [])}
        match_rows = (dna.get("dna_match_today") or {}).get("top") or []
        ev = [e.get("id") for e in (world.get("events_triggered") or [])]
        n = _append_risk_queue(risk_queue_entries(
            today, sorted(held & set(breaks)), match_rows, ev))
        _log(f"preopen: risk-queue +{n}")
    except Exception:
        _log("preopen: risk-queue FAILED\n" + traceback.format_exc())
    try:
        sys.stdout.reconfigure(encoding="utf-8")    # cp950 console 防護
    except Exception:
        pass
    print(md)
    return 0


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    mode = (args[0] if args else "preopen").lower()
    return run_morning() if mode == "morning" else run_preopen()


if __name__ == "__main__":
    sys.exit(main())
