"""Performance-feedback rotation throttle — the principal's discipline rule.

> 績效強 + 沒真反轉 → 不換股,深挖支撐數據(贏家為什麼還在贏)。
> 真反轉確認(regime 翻 / 資金面 STRESS / systemic)→ 才放行換股。

This is a recommend-only LENS on top of the existing portfolio audit. It does NOT
change the core scorer; it RE-FRAMES the rotation signals through a
performance-and-reversal gate so the system "lets winners run" and only churns on
a confirmed reversal — straight from the constitution (default-HOLD; offense needs
十足的證據; defense moves fast on a systemic trigger).

Inputs (point-in-time, from outputs/):
  * portfolio-audit-*.json : per-holding verdict + fom_breakdown + pct + category
  * daily-health-check-*.json : regime, funding_stress, posture(systemic/hedges)

"績效" honesty: realized P&L is NOT in the data (the audit is the ~10% active
sleeve; the NVDA RSU that dominates is excluded by design). So performance is
either STATED by the principal (ground truth) or estimated from a book-strength
proxy (HOLD-share × FOM, net of leveraged decay). The report always says which.

Pure + testable: composes a FeedbackReport from dicts; no network, no LLM.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

# Verdicts that mean "a winner we hold" vs "rotate/trim out".
_HOLD = ("HOLD",)
_OUT = ("SELL", "TRIM")

# Reversal triggers (any one ⇒ 真反轉; mirrors daily_health_check posture logic).
_REVERSAL_REGIMES = {"risk_off", "capitulation"}
_REVERSAL_FUNDING = {"STRESS", "RUPTURE"}


@dataclass
class Holding:
    ticker: str
    pct: float
    verdict: str
    category: str
    final_fom: Optional[float]
    momentum: Optional[float] = None
    quality: Optional[float] = None
    bubble_guard: Optional[float] = None
    decay_pct: Optional[float] = None

    def is_hold(self) -> bool:
        return self.verdict.upper().startswith(_HOLD)

    def is_out(self) -> bool:
        return any(self.verdict.upper().startswith(x) for x in _OUT)


@dataclass
class FeedbackReport:
    verdict: str = "WATCH"           # HOLD_AND_DEEPEN | WATCH | ROTATE
    reversal: bool = False
    reversal_reasons: list[str] = field(default_factory=list)
    perf_basis: str = "proxy"        # "stated" | "proxy"
    perf_label: str = ""             # 非常好/普通/差 or proxy summary
    book_strength: float = 0.0       # 0..1 HOLD-share of the active book
    support: list[Holding] = field(default_factory=list)      # winners to deepen
    rotation: list[Holding] = field(default_factory=list)     # SELL/TRIM candidates
    invalidation: list[str] = field(default_factory=list)     # what flips to ROTATE
    note: str = ""
    as_of: str = ""


def _load(path: Optional[Path]) -> Optional[dict]:
    if not path or not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def _latest(outputs_dir: Path, prefix: str) -> Optional[Path]:
    files = sorted(outputs_dir.glob(f"{prefix}*.json"))
    return files[-1] if files else None


def _holdings(audit: dict) -> list[Holding]:
    out: list[Holding] = []
    for key in ("portfolio_1_audit", "portfolio_2_audit"):
        for r in audit.get(key, []) or []:
            fb = r.get("fom_breakdown") or {}
            lev = r.get("leveraged_scorer") or {}
            out.append(Holding(
                ticker=r.get("ticker", "?"),
                pct=float(r.get("pct") or 0.0),
                verdict=str(r.get("verdict") or ""),
                category=str(r.get("category") or ""),
                final_fom=fb.get("final_fom"),
                momentum=fb.get("momentum"),
                quality=fb.get("quality"),
                bubble_guard=fb.get("bubble_guard"),
                decay_pct=lev.get("annual_decay_pct"),
            ))
    return out


def detect_reversal(hc: Optional[dict]) -> tuple[bool, list[str]]:
    """True 真反轉 if regime/funding/posture signal a systemic turn."""
    if not hc:
        return False, ["health-check 缺失,反轉訊號不可用(預設不反轉)"]
    reasons: list[str] = []
    regime = (hc.get("regime", {}) or {}).get("label", "")
    fund = (hc.get("funding_stress", {}) or {}).get("verdict", "")
    pos = hc.get("posture", {}) or {}
    if regime in _REVERSAL_REGIMES:
        reasons.append(f"regime={regime}")
    if str(fund).upper() in _REVERSAL_FUNDING:
        reasons.append(f"資金面={fund}")
    if pos.get("systemic_risk"):
        reasons.append("posture.systemic_risk=True")
    if pos.get("deploy_bear_hedges"):
        reasons.append("空頭避險已啟動")
    return bool(reasons), reasons


def compose_feedback(outputs_dir: Path, stated_perf: Optional[str] = None,
                     *, hold_share_strong: float = 0.45,
                     fom_min: float = 45.0, top_n: int = 6) -> FeedbackReport:
    """Build the throttle verdict. ``stated_perf`` ∈ {great, ok, bad, None}."""
    audit = _load(_latest(outputs_dir, "portfolio-audit-"))
    hc = _load(_latest(outputs_dir, "daily-health-check-"))
    rep = FeedbackReport(as_of=(audit or {}).get("as_of", (hc or {}).get("as_of", "")))

    reversal, reasons = detect_reversal(hc)
    rep.reversal, rep.reversal_reasons = reversal, reasons

    holds_all = _holdings(audit) if audit else []
    cash = [h for h in holds_all if h.category != "leveraged_etf"]
    # book strength = pct-share of the cash-equity book sitting in HOLD verdicts
    cash_pct = sum(h.pct for h in cash) or 1.0
    hold_pct = sum(h.pct for h in cash if h.is_hold())
    rep.book_strength = round(hold_pct / cash_pct, 2)

    # performance: stated by principal wins; else the proxy.
    if stated_perf in ("great", "非常好", "good", "ok", "普通", "bad", "差"):
        rep.perf_basis = "stated"
        rep.perf_label = {"great": "非常好", "good": "好", "ok": "普通", "bad": "差"}.get(
            stated_perf, stated_perf)
        strong = stated_perf in ("great", "非常好", "good")
    else:
        rep.perf_basis = "proxy"
        rep.perf_label = f"持倉強度推估 HOLD占比={rep.book_strength:.0%}"
        strong = rep.book_strength >= hold_share_strong

    # winners to deepen: top HOLD cash-equities by pct, thesis-intact (FOM ok)
    winners = sorted([h for h in cash if h.is_hold()], key=lambda h: h.pct, reverse=True)
    rep.support = winners[:top_n]
    # rotation candidates: SELL/TRIM (decay-first leverage stands regardless)
    rep.rotation = sorted([h for h in holds_all if h.is_out()],
                          key=lambda h: (h.category != "leveraged_etf", -h.pct))[:top_n]

    if reversal:
        rep.verdict = "ROTATE"
        rep.note = ("真反轉確認 — 放行換股紀律:先處理系統性風險與下列 SELL/TRIM。"
                    "防守可以快(系統性觸發即動)。")
    elif strong:
        rep.verdict = "HOLD_AND_DEEPEN"
        rep.note = ("績效強 + 無真反轉 → 不主動換掉強勢現股,改深挖支撐數據(下方)。"
                    "槓桿 ETF 的 decay 減碼屬衛生、不算換股,仍可執行。換股需十足證據。")
    else:
        rep.verdict = "WATCH"
        rep.note = ("績效未達『非常好』且無反轉 → 正常健檢,不急著動作;"
                    "等績效轉強(續抱)或反轉確認(換股)。")

    rep.invalidation = [
        "regime 轉 risk_off / capitulation",
        "資金面轉 STRESS / RUPTURE(接 FRED/ALFRED 後即時)",
        "posture.systemic_risk=True 或空頭避險觸發",
        "強勢持股跌破關鍵結構 / 動能與 FOM 同步走弱",
    ]
    if not audit:
        rep.note = "找不到 portfolio-audit;先跑 `python -m sharks.backtest.portfolio_audit`。"
    return rep
