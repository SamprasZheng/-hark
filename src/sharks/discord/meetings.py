"""Compose 晨會 / 晚會 / 週會 digests from the existing ``outputs/`` artefacts.

This module is deliberately Discord-free and pure: it reads the JSON the daily
routine already produces (health-check, portfolio-audit, fom-monthly, picks,
crypto-top100) and returns a structured ``MeetingDigest``. ``bot.py`` turns that
into embeds. Keeping it pure means the smoke test can build a real digest with
no token and no network.

It invents nothing. Every number comes from a point-in-time ``outputs/`` file;
when a file is missing the section says so rather than guessing — consistent with
the constitution's "do not invent tickers, prices, or dates" rule.

The optional narrative (今日國際局勢 / 台美股行情 discussion) is NOT generated
here — meetings stay free + instant. ``bot.py`` may append a Claude research
blurb using the prompt builders at the bottom of this file.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from sharks.discord.config import Settings

DISCLAIMER = "僅供研究與教育,非個人化投資建議;系統只建議、永不下單。"


@dataclass
class Section:
    heading: str
    body: str


@dataclass
class MeetingDigest:
    kind: str                      # "morning" | "evening" | "weekly"
    title: str
    subtitle: str
    as_of: str
    sections: list[Section] = field(default_factory=list)
    footer: str = DISCLAIMER

    def add(self, heading: str, body: str) -> None:
        self.sections.append(Section(heading, (body or "—").strip()))

    def to_markdown(self) -> str:
        lines = [f"# {self.title}", f"_{self.subtitle}_", ""]
        for s in self.sections:
            lines.append(f"## {s.heading}")
            lines.append(s.body)
            lines.append("")
        lines.append(f"> {self.footer}")
        return "\n".join(lines)


# ── file helpers ──────────────────────────────────────────────────────────────

def _latest(outputs_dir: Path, prefix: str) -> Optional[Path]:
    files = sorted(outputs_dir.glob(f"{prefix}*.json"))
    return files[-1] if files else None


def _load(path: Optional[Path]) -> Optional[dict]:
    if not path or not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def _cap(s: str, n: int = 900) -> str:
    s = s.strip()
    return s if len(s) <= n else s[: n - 1] + "…"


def _tickers(rows: Any, key: str = "ticker", limit: int = 12) -> str:
    if not isinstance(rows, list) or not rows:
        return "—"
    out = []
    for r in rows[:limit]:
        if isinstance(r, dict):
            out.append(str(r.get(key, "?")))
        else:
            out.append(str(r))
    more = "" if len(rows) <= limit else f" (+{len(rows) - limit})"
    return ", ".join(out) + more


# ── section builders (shared) ─────────────────────────────────────────────────

def _posture_section(d: MeetingDigest, hc: Optional[dict]) -> None:
    if not hc:
        d.add("盤勢與姿態", "找不到 daily-health-check;先跑 `python -m sharks.cli health-check`。")
        return
    regime = hc.get("regime", {}) or {}
    fund = hc.get("funding_stress", {}) or {}
    pos = hc.get("posture", {}) or {}
    reasons = "、".join(regime.get("reasons", []) or [])
    body = (
        f"**regime**: `{regime.get('label', '?')}` ({reasons or 'n/a'})\n"
        f"**資金面**: `{fund.get('verdict', '?')}`"
        f"{' · live' if fund.get('live_data') else ' · stub'}\n"
        f"**姿態**: `{pos.get('posture', '?')}` · systemic_risk="
        f"{pos.get('systemic_risk')}\n"
        f"**部位指引**: {_cap(str(pos.get('sizing_guidance', '—')), 320)}\n"
        f"**空頭避險**: {'已啟動 ⚠️' if pos.get('deploy_bear_hedges') else '待命'}"
    )
    d.add("盤勢與姿態", body)


def _recommendations_section(d: MeetingDigest, hc: Optional[dict]) -> None:
    recs = (hc or {}).get("recommendations") or []
    if not recs:
        return
    lines = []
    for r in recs[:6]:
        tk = f" `{r.get('ticker')}`" if r.get("ticker") else ""
        detail = _cap(str(r.get("detail", "")), 160)
        lines.append(f"- **[{r.get('type', '?')}]** {r.get('action', '')}{tk} — {detail}")
    d.add("建議動作（recommend-only）", "\n".join(lines))


def _position_health_section(d: MeetingDigest, hc: Optional[dict], audit: Optional[dict]) -> None:
    ph = (hc or {}).get("position_health") or {}
    parts = []
    if ph.get("available"):
        parts.append(f"**賣出候選**: {_tickers(ph.get('sell_candidates'))}")
        parts.append(f"**減碼候選**: {_tickers(ph.get('trim_candidates'))}")
    if audit:
        p1 = audit.get("p1_summary", {}) or {}
        p2 = audit.get("p2_summary", {}) or {}
        if p1:
            parts.append(
                f"**P1**: SELL {_tickers(p1.get('SELL'))} · TRIM {_tickers(p1.get('TRIM'))}"
            )
        if p2:
            parts.append(
                f"**P2**: SELL {_tickers(p2.get('SELL'))} · TRIM {_tickers(p2.get('TRIM'))}"
            )
    if parts:
        d.add("持倉健檢", "\n".join(parts))


def _fom_picks_section(d: MeetingDigest, fom: Optional[dict], heading: str = "FOM 選股（3–6個月 tilt）") -> None:
    if not fom:
        return
    picks = fom.get("top_3_picks") or []
    if not picks:
        return
    lines = []
    for p in picks[:5]:
        lines.append(
            f"- #{p.get('rank', '?')} **{p.get('ticker', '?')}** "
            f"FOM={p.get('final_fom', '?')} · {p.get('sector', '')} "
            f"(mom {p.get('momentum', '?')}/qual {p.get('quality', '?')}/"
            f"guard {p.get('bubble_guard', '?')})"
        )
    note = "FOM 是 3–6 個月傾向,不是隔日計時器(IC 在 6m 最強,1m 近雜訊)。"
    d.add(heading, "\n".join(lines) + f"\n_{note}_")


def _daily_signals_section(d: MeetingDigest, picks: Optional[dict]) -> None:
    sigs = (picks or {}).get("signals") or []
    sigs = [s for s in sigs if isinstance(s, dict) and s.get("ticker")]
    if not sigs:
        return
    lines = []
    for s in sigs[:6]:
        thesis = _cap(str(s.get("thesis", "")), 140)
        lines.append(
            f"- **{s.get('slot', '?')}** `{s.get('ticker')}` "
            f"[{s.get('quadrant', '')}] {thesis}"
        )
    d.add("每日 10-訊號（最近一次）", "\n".join(lines))


def _crypto_section(d: MeetingDigest, cr: Optional[dict]) -> None:
    if not cr:
        return
    ms = cr.get("market_structure", {}) or {}
    movers = (cr.get("movers_24h", {}) or {}).get("gainers", []) or []
    g = ", ".join(
        f"{m.get('symbol', '?')} +{m.get('price_change_pct_24h', '?')}%" for m in movers[:5]
    )
    mcap = ms.get("total_market_cap")
    mcap_t = f"{mcap/1e12:.2f}T" if isinstance(mcap, (int, float)) else "?"
    body = (
        f"**總市值** ${mcap_t} · **BTC dominance** {ms.get('btc_dominance_pct', '?')}% · "
        f"**Top10 集中度** {ms.get('top10_concentration_pct', '?')}%\n"
        f"**24h 強勢**: {g or '—'}\n"
        f"_週末加密為觀察/去風險優先;BTC≤4% 在 ≤5% Alpha 籃外。_"
    )
    d.add("加密 Top-100（週末窗口）", body)


# ── public composers ──────────────────────────────────────────────────────────

def compose_morning(settings: Settings, now_tpe: datetime) -> MeetingDigest:
    o = settings.outputs_dir
    hc = _load(_latest(o, "daily-health-check-"))
    audit = _load(_latest(o, "portfolio-audit-"))
    fom = _load(_latest(o, "fom-monthly-"))
    is_weekly = now_tpe.strftime("%A") == settings.weekly_day

    d = MeetingDigest(
        kind="morning",
        title=f"🌅 晨會 — {now_tpe:%Y-%m-%d}（{_zh_dow(now_tpe)}）",
        subtitle="回顧隔夜美股 + 今日台/亞洲開盤姿態。先看數據,國際局勢/行情敘事見下。",
        as_of=(hc or {}).get("as_of", now_tpe.isoformat()),
    )
    _posture_section(d, hc)
    _recommendations_section(d, hc)
    _position_health_section(d, hc, audit)
    _fom_picks_section(d, fom, "本週重點 FOM 選股" if is_weekly else "FOM 選股（最近一次）")
    if is_weekly:
        d.add("📅 週會（週一）", "今天加跑 FOM 全宇宙掃描 + IC 校準 + 熱點預測;結果進 #每日選股。")
    return d


def compose_noon(settings: Settings, now_tpe: datetime) -> MeetingDigest:
    o = settings.outputs_dir
    hc = _load(_latest(o, "daily-health-check-"))
    audit = _load(_latest(o, "portfolio-audit-"))
    fom = _load(_latest(o, "fom-monthly-"))
    d = MeetingDigest(
        kind="noon",
        title=f"🕛 午會 — {now_tpe:%Y-%m-%d}（{_zh_dow(now_tpe)}）",
        subtitle="台股午盤 + 昨夜美股收盤回顧 + 今晚美股前哨。盤中只健檢,不過度操作。",
        as_of=(hc or {}).get("as_of", now_tpe.isoformat()),
    )
    _posture_section(d, hc)
    _position_health_section(d, hc, audit)
    _fom_picks_section(d, fom, "FOM 選股（最近一次）")
    return d


def compose_evening(settings: Settings, now_tpe: datetime) -> MeetingDigest:
    o = settings.outputs_dir
    hc = _load(_latest(o, "daily-health-check-"))
    audit = _load(_latest(o, "portfolio-audit-"))
    picks = _load(_latest(o, "picks-"))
    fom = _load(_latest(o, "fom-monthly-"))
    is_weekend = now_tpe.strftime("%A") in ("Saturday", "Sunday")
    cr = _load(_latest(o, "crypto-top100-")) if is_weekend else None

    d = MeetingDigest(
        kind="evening",
        title=f"🌆 晚會 — {now_tpe:%Y-%m-%d}（{_zh_dow(now_tpe)}）",
        subtitle="美股開盤（夏令約 21:30）前的 preview + 台股收盤檢討。",
        as_of=(hc or {}).get("as_of", now_tpe.isoformat()),
    )
    _posture_section(d, hc)
    _daily_signals_section(d, picks)
    _fom_picks_section(d, fom, "FOM 選股（最近一次）")
    _position_health_section(d, hc, audit)
    if is_weekend:
        _crypto_section(d, cr)
    return d


def compose_weekly(settings: Settings, now_tpe: datetime) -> MeetingDigest:
    o = settings.outputs_dir
    fom = _load(_latest(o, "fom-monthly-"))
    d = MeetingDigest(
        kind="weekly",
        title=f"📅 週會 — {now_tpe:%Y-%m-%d}",
        subtitle="每週的真正再平衡思考:FOM 掃描 + IC 校準 + 熱點。日常只健檢,不過多操作。",
        as_of=(fom or {}).get("as_of", now_tpe.isoformat()),
    )
    _fom_picks_section(d, fom, "本週 FOM Top 選股")
    if fom and fom.get("top_50_watchlist"):
        d.add("Top-50 觀察清單", _tickers(fom.get("top_50_watchlist"), limit=20))
    if fom and fom.get("bubble_alerts_negative_guard"):
        d.add("⚠️ 泡沫警示（負 guard）", _tickers(fom.get("bubble_alerts_negative_guard"), limit=12))
    return d


def _zh_dow(dt: datetime) -> str:
    return "週" + "一二三四五六日"[dt.weekday()]


def digest_to_brief(d: MeetingDigest) -> str:
    """Flatten a digest into a compact text brief to feed the council debate."""
    parts = [d.subtitle]
    for s in d.sections:
        parts.append(f"{s.heading}: {s.body}")
    return "\n".join(parts)


# ── narrative prompts (bot.py decides whether to spend Claude tokens) ──────────

def research_prompt(kind: str) -> str:
    """Prompt for the optional Claude research blurb appended to a meeting."""
    base = (
        "用繁體中文,200 字內,做一段簡短的盤前/盤後敘事。"
        "讀 wiki/01_macro_state.md、wiki/02_mag7_bottleneck.md 與 raw/macro/ 最新內容,"
        "需要時補上你知道的近況。涵蓋:(1) 今日國際局勢/總經重點(Fed、Trump 政策、地緣),"
        "(2) 台股與美股行情概況,(3) 一句話風險提醒。"
        "只做研究敘事,非個人化投資建議。若資料不足就說明,不要捏造數字。"
    )
    if kind == "morning":
        return "【晨會敘事】回顧隔夜美股、預判今日台/亞洲盤。" + base
    if kind == "evening":
        return "【晚會敘事】檢討今日台股、預判即將開盤的美股。" + base
    return "【週會敘事】本週總經與板塊輪動主軸。" + base
