"""Daily Signals — integrate all modules into one push-format markdown.

Reads latest outputs from:
  - fom-monthly / fom-alpha
  - serenity-scout
  - meme-squeeze-hunter
  - liquidity-signals
  - correlation-matrix
  - portfolio-audit

Outputs: outputs/daily_push_YYYY-MM-DD.md (human-readable summary)
"""

from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path

from sharks.scoring.evidence_card import (
    load_deep_research,
    render_pick_with_card,
)


def load_latest(out_dir: Path, prefix: str):
    files = sorted(out_dir.glob(f"{prefix}*.json"), reverse=True)
    if not files:
        return None
    try:
        return json.loads(files[0].read_text(encoding="utf-8"))
    except Exception as e:
        print(f"  warn: cannot load {files[0]}: {e}", file=sys.stderr)
        return None


def main():
    out_dir = Path("outputs")
    today = datetime.now().strftime("%Y-%m-%d")

    liquidity = load_latest(out_dir, "liquidity-signals")
    fom = load_latest(out_dir, "fom-alpha")
    serenity = load_latest(out_dir, "serenity-scout")
    meme = load_latest(out_dir, "meme-squeeze-hunter")
    corr = load_latest(out_dir, "correlation-matrix")
    audit = load_latest(out_dir, "portfolio-audit")
    deep_reports = load_deep_research(out_dir)

    lines = [f"# 📅 Daily Signals — {today}", ""]

    # Liquidity alert
    if liquidity:
        comp = liquidity.get("composite_alert", {})
        lines += [f"## 🔔 警報等級: **{comp.get('level', '?')}** — {comp.get('headline', '')}", ""]
        m2 = liquidity.get("m2_signal", {})
        btc = liquidity.get("btc_signal", {})
        gld = liquidity.get("gold_signal", {})
        lines += [
            f"- **M2**: YoY {m2.get('yoy_growth_pct', '?')}% → {m2.get('interpretation', '?')}",
            f"- **BTC**: ${btc.get('last_price', '?')} (距高 -{btc.get('dist_from_high_pct', '?')}%) → {btc.get('interpretation', '?')}",
            f"- **GLD**: ${gld.get('last_price', '?')} (6m +{gld.get('r6_pct', '?')}%, 12m +{gld.get('r12_pct', '?')}%) → {gld.get('interpretation', '?')}",
            "",
        ]

    # FOM-Alpha top picks — each pick gets a wiki/21 §6 evidence card under it.
    # Card includes moat / cash flow / earnings / golden-cross / FOMO check;
    # local LLM thesis is appended when Ollama is up, silent placeholder otherwise.
    if fom:
        lines += ["## 🎯 今日 FOM-Alpha 推薦", ""]
        lines += ["### SP500 Top 3", ""]
        for p in fom.get("top_3_sp500_eligible", []):
            lines.extend(render_pick_with_card(p, deep_reports))
            lines.append("")
        lines += ["### R2K Top 3", ""]
        for p in fom.get("top_3_r2k_eligible", []):
            lines.extend(render_pick_with_card(p, deep_reports))
            lines.append("")

    # Meme/squeeze top picks (anti-Buffett)
    if meme:
        lines += ["## 🔥 妖股 / Squeeze Top 10(高刺激)", ""]
        for p in (meme.get("top_25_by_score", [])[:10]):
            flags = ", ".join(p.get("flags", []))
            lines.append(f"- **{p['ticker']}** ({p['name']}): score {p['squeeze_score']}, 1m {p['r1m_pct']}%, 1y {p['r12m_pct']}%, 距高 -{p['dist_from_12m_high_pct']}% → {flags}")
        lines.append("")

    # Serenity Scout
    if serenity:
        lines += ["## 🕵️ Serenity Scout — Chokepoint 候選", ""]
        for p in (serenity.get("top_15_with_staging_bonus", [])[:5]):
            lines.append(f"- **{p['ticker']}**: {p['chokepoint_thesis']} — Stage: {p['stage_per_serenity_db']}")
        lines.append("")

    # Correlation insights
    if corr:
        lines += ["## 📉 NVDA 相關性(分散工具)", ""]
        divs = corr.get("highest_diversifiers_vs_nvda", {})
        lines.append("**最強分散**:")
        for t, v in list(divs.items())[:8]:
            lines.append(f"- {t}: {v}")
        lines.append("")

    # Portfolio actions
    if audit:
        lines += ["## 📋 你 Portfolio 處置摘要", ""]
        p1 = audit.get("p1_summary", {})
        p2 = audit.get("p2_summary", {})
        lines.append(f"- **P1 SELL**: {', '.join(p1.get('SELL', []))}")
        lines.append(f"- **P1 TRIM**: {', '.join(p1.get('TRIM', []))}")
        lines.append(f"- **P2 SELL**: {', '.join(p2.get('SELL', []))}")
        lines.append(f"- **P2 ADD**: {', '.join(p2.get('ADD', []))}")
        lines.append("")

    lines += [
        "## 🎯 今日重點動作",
        "1. 警報等級監測黃金 6m 變化",
        "2. 槓桿 ETF 持倉(P1)減持優先",
        "3. NVDA RSU 集中度持續降低",
        "4. 加 GLD 對沖(若還沒)",
        "",
        "## See also",
        "- wiki/14_2026_outlook_and_meme_year.md — 妖股年判定 + 預測",
        "- wiki/13_global_hunting_grounds.md — 全球狩獵地圖",
        "- wiki/12_employee_concentration.md — RSU 集中度框架",
        "- wiki/10_defensive_hedging.md — 防禦組合",
    ]

    out_path = out_dir / f"daily_push_{today}.md"
    out_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {out_path}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
