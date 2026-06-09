"""跑真的:電商/廣度 four-screen 一次出(/basecross + /rally + /ecomrank + /stealth 的 CLI 版)。

WHY: 這支讓你**不必依賴 Discord bot**,在任何有網路的機器上一行就能跑出真數字:

    python -m sharks.discord.ecom_screens                 # 大+小電商
    python -m sharks.discord.ecom_screens small           # 只小型電商
    python -m sharks.discord.ecom_screens broadening      # 民生/消費/醫療(隱蔽吸籌池)
    python -m sharks.discord.ecom_screens all             # 全部錯殺池
    python -m sharks.discord.ecom_screens 8454.TW 8044.TW # 額外加台股代號

它複用 basecross(月線距高/金叉/量能)、rally_signal(5維+連續起漲+綜合排名)、
stealth_signal(隱蔽吸籌:資金先進價未動)。需要 `yfinance`(pip install yfinance)。
純列印,recommend-only,永不下單。

``render(candidates, ...)`` 是純函式(吃已抓好的 candidates),離線可單元測試;
``main`` 才用 yfinance 真抓。
"""

from __future__ import annotations

import sys

from sharks.discord import basecross as BC
from sharks.discord.config import Settings
from sharks.scoring import rally_signal as RS
from sharks.scoring import stealth_signal as ST


def _ecom_universe(scope: str) -> tuple[str, list[str]]:
    if scope in ("small", "ecommerce_small"):
        return "小型電商", list(BC.ECOMMERCE_SMALL)
    if scope in ("broadening", "stealth"):
        return "廣度錯殺(民生/消費/醫療)", list(BC.BROADENING_LAGGARDS)
    if scope == "space":
        return "太空板塊(SpaceX IPO)", list(BC.SPACE_PUREPLAYS)
    if scope == "diversified":
        return "跨產業分散轉機股", list(BC.DIVERSIFIED_TURNAROUND)
    if scope == "midrisk":
        return "中風險轉機股", list(BC.MID_RISK_TURNAROUND)
    if scope == "ipo":
        return "2026 IPO 代理", list(BC.IPO_PROXIES)
    if scope == "killed2022":
        return "2022 殺下來", list(BC.KILLED_2022)
    if scope in ("all", "everything"):
        return "全部錯殺池", sorted(set(BC.KILLED_2022) | set(BC.AI_OVERSOLD_SOFTWARE)
                                     | set(BC.ECOMMERCE_AGENTIC) | set(BC.ECOMMERCE_SMALL)
                                     | set(BC.BROADENING_LAGGARDS))
    return "大+小電商", BC.ECOMMERCE_AGENTIC + BC.ECOMMERCE_SMALL


def render(candidates: list, *, quality_by_ticker=None, prior_streaks=None) -> str:
    """Format the three screens from already-fetched basecross candidates (pure)."""
    quality_by_ticker = quality_by_ticker or {}
    small = set(BC.ECOMMERCE_SMALL)
    out: list[str] = []

    # 1) 綜合排名 (獲利空間 × 基本面 × 炒作動能, 動能即時 fold-in)
    ranked = RS.ecommerce_rank(candidates, quality_by_ticker=quality_by_ticker)
    out.append("═══ 綜合排名 (基本面35% + 獲利空間35% + 炒作動能30%) ═══")
    out.append(f"{'#':>2} {'代號':<7}{'綜合':>5}{'基本':>5}{'空間':>5}{'動能':>5}  大/小")
    for i, r in enumerate(ranked, 1):
        f = lambda v: f"{v:.0f}" if isinstance(v, (int, float)) else "–"
        mom = "待" if r.get("momentum_pending") else f(r.get("momentum"))
        sz = "小" if r["ticker"] in small else "大"
        out.append(f"{i:>2} {r['ticker']:<7}{r['composite']:>5.0f}"
                   f"{f(r.get('fundamental')):>5}{f(r.get('upside')):>5}{mom:>5}   [{sz}]")

    # 2) 起漲訊號 (5維 + 連續起漲才可考慮買入)
    sigs = RS.build_signals(candidates, quality_by_ticker=quality_by_ticker,
                            prior_streaks=prior_streaks)
    out.append("\n═══ 起漲訊號 (連續起漲才『可考慮買入』) ═══")
    for s in sigs:
        out.append(f"  {s.ticker:<7} C{s.composite:>4.0f} 連{s.streak} · {s.conviction}")

    # 3) 隱蔽吸籌 (資金先進、價未動 = 收貨指紋,抓還沒炒上去的)
    stealth = ST.stealth_rank(candidates)
    out.append("\n═══ 隱蔽吸籌 (資金先進、價未動;🕵️=最值得盯) ═══")
    for r in stealth:
        if r.stealth or r.verdict.startswith(("🟡", "🔵")):
            cap = f"{r.capital:.0f}" if r.capital is not None else "–"
            out.append(f"  {r.ticker:<7} 吸籌{r.score:>4.0f} 資金{cap:>4} · {r.verdict}")

    # 4) 月線大底金叉 + 資金介入
    out.append("\n═══ 月線大底金叉 + 資金介入 (basecross) ═══")
    for c in candidates:
        if c.last is None:
            out.append(f"  {c.ticker:<7} {c.verdict} — {c.note}")
        else:
            vs = f" 量×{c.vol_surge:.1f}" if c.vol_surge else ""
            out.append(f"  {c.ticker:<7} {c.verdict} · 距高 {c.dist_ath_pct:.0f}%{vs}")
    return "\n".join(out)


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    _scopes = {"small", "ecommerce_small", "broadening", "stealth", "space",
               "killed2022", "all", "everything", "ecommerce", "diversified", "midrisk", "ipo"}
    scope = "ecommerce"
    extra: list[str] = []
    for a in argv:
        if a.lower() in _scopes:
            scope = a.lower()
        else:
            extra.append(a.upper())
    label, base = _ecom_universe(scope)
    tickers = sorted(set(base) | set(extra))
    print(f"抓取 {label} {len(tickers)} 檔(yfinance ~5y)… 請稍候。", file=sys.stderr)
    try:
        candidates = BC.screen(tickers, fetch=BC.default_fetch,
                               quality_by_ticker=BC.quality_from_fom(Settings.load().outputs_dir))
    except Exception as exc:  # network / yfinance not installed
        print(f"抓取失敗:{exc}\n→ 確認有網路且已 pip install yfinance。", file=sys.stderr)
        return 2
    quality = BC.quality_from_fom(Settings.load().outputs_dir)
    streaks = RS.load_prior_streaks(Settings.load().outputs_dir)
    print(render(candidates, quality_by_ticker=quality, prior_streaks=streaks))
    print("\nrecommend-only · 先驗被 FOM/即時數據覆蓋 · 連續起漲+題材才考慮 · 永不下單")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
