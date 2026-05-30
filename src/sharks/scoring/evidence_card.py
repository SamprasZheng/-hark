"""Evidence Card renderer — turns deep_research output into wiki/21 §6 cards.

Per FOM-Alpha pick, prints:
  - Verdict + evidence/risk score
  - Moat (Buffett 3M score / type / thesis)
  - Fundamentals (Fwd PE / ROE / FCF / dividend / revenue growth / op margin)
  - Technicals (price / 52w range / golden cross / TD-9 / Bollinger)
  - Chip flow (institutions / insiders / short interest)
  - Evidence list (✅)
  - Risk list (🔴/⚠️)
  - FOMO check (synthesised: too close to 52w high + upper band + far from low)
  - Optional local-LLM thesis (rendered when Ollama is running, silent otherwise)

The card is plain markdown so it composes into daily_signals.py output.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

# Emoji-prefixed keys that deep_research.py writes
K_MOAT = "\U0001f3f0 moat_analysis"
K_FUND = "\U0001f4b0 fundamental"
K_TECH = "\U0001f4ca technical_signals"
K_CHIP = "\U0001f4c9 chip_flow"
K_EV = "\U0001f3af evidence_check"
K_RISK = "⚠️ risk_check"
K_VERDICT = "\U0001f4cb verdict"
K_SCORE = "\U0001f4cb evidence_score"
K_EVCT = "\U0001f4cb evidence_count"
K_RKCT = "\U0001f4cb risk_count"


def _is_num(v) -> bool:
    if v is None:
        return False
    try:
        float(v)
        return True
    except (TypeError, ValueError):
        return False


def _fmt_pct(v, prec: int = 1) -> str:
    if not _is_num(v):
        return "—"
    return f"{float(v):.{prec}f}%"


def _fmt_money_b(v) -> str:
    if not _is_num(v):
        return "—"
    x = float(v)
    if abs(x) >= 0.1:
        return f"${x:.1f}B"
    return f"${x * 1000:.0f}M"


def _fmt_num(v, prec: int = 1) -> str:
    if not _is_num(v):
        return "—"
    return f"{float(v):.{prec}f}"


def render_card(
    report: dict,
    fom_pick: Optional[dict] = None,
    llm_thesis: Optional[str] = None,
) -> list[str]:
    """Render one evidence card as a list of markdown lines (indented under a bullet)."""
    if not report:
        return []

    name = report.get("company_name", report.get("ticker", "?"))
    verdict = report.get(K_VERDICT, "?")
    ev_count = report.get(K_EVCT, 0)
    risk_count = report.get(K_RKCT, 0)
    score = report.get(K_SCORE, 0)

    moat = report.get(K_MOAT, {}) or {}
    fund = report.get(K_FUND, {}) or {}
    tech = report.get(K_TECH, {}) or {}
    chip = report.get(K_CHIP, {}) or {}

    lines: list[str] = []

    # Company line
    sector = report.get("sector") or "?"
    industry = report.get("industry") or "?"
    lines.append(f"  - 🏢 _{name}_ · {sector} / {industry}")

    # Verdict
    lines.append(
        f"  - 📋 **Verdict**: {verdict} — evidence {ev_count} / risk {risk_count} / score {score}"
    )

    # Moat
    moat_score = moat.get("moat_score_buffett", "NOT_RATED")
    moat_type = moat.get("moat_type", "?")
    moat_thesis = moat.get("thesis", "?")
    if moat_score != "NOT_RATED":
        lines.append(
            f"  - 🏰 **護城河 {moat_score}/100** · {moat_type} · _{moat_thesis}_"
        )
    else:
        lines.append(f"  - 🏰 **護城河**: NOT_RATED — _{moat_thesis}_")

    # Fundamentals — what the user explicitly asked for: cash flow, earnings, valuation
    fund_line = (
        f"  - 💰 **基本面**: Fwd PE {_fmt_num(fund.get('forward_pe'))} · "
        f"ROE {_fmt_pct(fund.get('return_on_equity_pct'))} · "
        f"FCF {_fmt_money_b(fund.get('free_cashflow_billion'))} · "
        f"營收 YoY {_fmt_pct(fund.get('revenue_growth_yoy_pct'))} · "
        f"OpMargin {_fmt_pct(fund.get('operating_margin_pct'))} · "
        f"股息 {_fmt_pct(fund.get('dividend_yield_pct'))}"
    )
    lines.append(fund_line)

    # Technicals — flag 底部黃金交叉 explicitly (user asked for this signal)
    price = tech.get("current_price")
    dist_high = tech.get("dist_from_52w_high_pct")
    dist_low = tech.get("dist_from_52w_low_pct")
    gx = bool(tech.get("golden_cross_5_vs_12"))
    td9 = tech.get("td9_setup", "NONE")
    bb = tech.get("bollinger_position", "?")

    if gx and _is_num(dist_low) and float(dist_low) < 30:
        gx_str = "🌟 **底部黃金交叉**"
    elif gx:
        gx_str = "✓"
    else:
        gx_str = "✗"

    tech_line = (
        f"  - 📊 **技術面**: 價 ${_fmt_num(price, 2)} · "
        f"距高 -{_fmt_num(dist_high)}% · "
        f"距低 +{_fmt_num(dist_low)}% · "
        f"黃金交叉 {gx_str} · "
        f"TD-9 {td9} · "
        f"Bollinger {bb}"
    )
    lines.append(tech_line)

    # Chip flow
    inst = chip.get("heldPercentInstitutions_pct")
    insider = chip.get("heldPercentInsiders_pct")
    short = chip.get("shortPercentOfFloat_pct")
    lines.append(
        f"  - 📉 **籌碼面**: 機構 {_fmt_pct(inst, 0)} · "
        f"Insider {_fmt_pct(insider, 1)} · "
        f"短興趣 {_fmt_pct(short, 1)}"
    )

    # Evidence list
    ev_list = report.get(K_EV, []) or []
    if ev_list:
        lines.append(
            f"  - ✅ **Evidence ({len(ev_list)})**: " + " · ".join(ev_list[:8])
        )

    # Risk list
    risk_list = report.get(K_RISK, []) or []
    if risk_list:
        lines.append(
            f"  - ⚠️ **Risk ({len(risk_list)})**: " + " · ".join(risk_list[:5])
        )

    # FOMO check — the user's explicit "FOMO Evidence Check" requirement
    fomo_signals: list[str] = []
    if _is_num(dist_high) and float(dist_high) < 5:
        fomo_signals.append(f"距 52w 高僅 -{_fmt_num(dist_high)}%")
    if bb == "UPPER_BAND":
        fomo_signals.append("Bollinger 上軌（超買）")
    if _is_num(dist_low) and float(dist_low) > 80:
        fomo_signals.append(f"距 52w 低 +{_fmt_num(dist_low)}%（漲幅已大）")
    if td9 == "SELL_SETUP":
        fomo_signals.append("TD-9 SELL setup")
    if fomo_signals:
        lines.append(
            "  - 🚨 **FOMO check**: "
            + " / ".join(fomo_signals)
            + " — **可能在追高，不是進場點**"
        )
    else:
        lines.append("  - 🚨 **FOMO check**: 無明顯追高訊號")

    # LLM thesis — graceful fallback when Ollama is down
    if llm_thesis and not llm_thesis.startswith("[ERROR"):
        lines.append("  - 🧠 **本地 LLM thesis**:")
        for tl in llm_thesis.strip().split("\n")[:6]:
            if tl.strip():
                lines.append(f"    > {tl}")
    else:
        lines.append(
            "  - 🧠 _LLM thesis_: Ollama 未啟動 — `ollama pull llama3.2:3b` 後此處自動生成"
        )

    return lines


def load_deep_research(out_dir: Path) -> dict:
    """Return {ticker: report} from the most recent deep-research-*.json."""
    files = sorted(out_dir.glob("deep-research-*.json"), reverse=True)
    if not files:
        return {}
    try:
        data = json.loads(files[0].read_text(encoding="utf-8"))
    except Exception:
        return {}
    return data.get("reports", {}) or {}


def maybe_generate_thesis(ticker: str, report: dict) -> Optional[str]:
    """Try local LLM thesis. Returns None silently when Ollama isn't available."""
    try:
        from sharks.ai import local_llm
    except Exception:
        return None
    try:
        if not local_llm.check_ollama_running():
            return None
        return local_llm.generate_thesis(ticker, report)
    except Exception:
        return None


def render_pick_with_card(
    pick: dict,
    deep_reports: dict,
    *,
    use_llm: bool = True,
) -> list[str]:
    """Render one FOM-Alpha pick as a bullet followed by an evidence card.

    If no deep_research data exists for the ticker, prints a graceful placeholder
    pointing at how to fix it.
    """
    ticker = pick.get("ticker", "?")
    head = (
        f"- **{ticker}** (FOM {pick.get('final_fom_alpha', '?')}) — "
        f"mom {pick.get('momentum', '?')} / "
        f"contr {pick.get('contrarian', '?')} / "
        f"bubble {pick.get('bubble_guard', '?')}"
    )
    report = deep_reports.get(ticker)
    if not report:
        return [
            head,
            f"  - 📋 _尚無 deep_research_ — 跑 `uv run python -m sharks.scoring.deep_research {ticker}` 補上",
        ]
    thesis = maybe_generate_thesis(ticker, report) if use_llm else None
    return [head] + render_card(report, fom_pick=pick, llm_thesis=thesis)
