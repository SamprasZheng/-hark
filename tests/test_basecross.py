"""Offline tests for the 月線底部金叉 + 資金介入 screener (no network/yfinance)."""

from __future__ import annotations

from sharks.discord import basecross as BC


def _daily(monthly: list[float]) -> list[float]:
    """Expand a monthly series to daily so _to_monthly(bucket=21) recovers it."""
    return [v for v in monthly for _ in range(21)]


def _vol_daily(monthly_vol: list[float]) -> list[float]:
    return [v / 21 for v in monthly_vol for _ in range(21)]


def test_ema_and_monthly_resample():
    assert BC._ema([5, 5, 5, 5], 3) == [5, 5, 5, 5]            # constant → constant
    assert BC._to_monthly([1, 2, 3, 4, 5, 6], bucket=3) == [3, 6]    # last per bucket
    assert BC._to_monthly([1, 2, 3, 4], bucket=2, agg="sum") == [3, 7]


def _fetch(series: dict[str, dict[str, list[float]]]):
    return lambda tickers: {t: series[t] for t in tickers if t in series}


def test_deep_base_with_inflow_is_actionable():
    # 100 → 40 decline (30 mo), then 40 → 62 recovery (10 mo); volume surges at the end.
    monthly = [100 - 2 * i for i in range(30)] + [40 + 2.2 * i for i in range(11)]
    vols = [100.0] * 39 + [320.0, 360.0]              # 近月量能放大 = 資金介入
    rows = BC.screen(["X"], fetch=_fetch({"X": {"close": _daily(monthly),
                                                 "volume": _vol_daily(vols)}}))
    c = rows[0]
    assert 20 <= (c.dist_ath_pct or 0) <= 85          # 大底深度,非近高非落刀
    assert c.inflow and (c.vol_surge or 0) >= 1.3      # 資金介入確認
    assert c.rising
    assert c.verdict[0] in "🟢🟡🔵"                    # 在可操作區間,不是落刀/近高


def test_golden_cross_detected_on_sharp_turn():
    # long decline then a sharp final upturn → 月線 MACD 低檔金叉 at the last bar.
    monthly = [100 - 1.8 * i for i in range(32)] + [46, 58]
    vols = [100.0] * 32 + [300.0, 380.0]
    rows = BC.screen(["G"], fetch=_fetch({"G": {"close": _daily(monthly),
                                                "volume": _vol_daily(vols)}}))
    c = rows[0]
    assert c.golden_cross and c.bottom_zone            # 底部金叉成立
    assert c.inflow
    assert c.verdict.startswith("🟢")                  # 金叉 + 資金 → 綠燈


def test_near_high_is_rejected():
    monthly = [10 + i for i in range(40)]              # 一路新高,貼著高點
    rows = BC.screen(["H"], fetch=_fetch({"H": {"close": _daily(monthly), "volume": []}}))
    assert "近高" in rows[0].verdict


def test_falling_knife_is_flagged():
    monthly = [100 - 2.4 * i for i in range(40)]       # 100 → ~6,跌掉 >90%
    rows = BC.screen(["K"], fetch=_fetch({"K": {"close": _daily(monthly), "volume": []}}))
    assert "跌太深" in rows[0].verdict


def test_insufficient_data():
    rows = BC.screen(["S"], fetch=_fetch({"S": {"close": _daily([10] * 10), "volume": []}}))
    assert rows[0].verdict == "資料不足"


def test_run_basecross_extra_tickers_and_themes():
    series = {t: {"close": _daily([100 - i for i in range(40)]), "volume": []}
              for t in ("ADBE", "INTC", "MELI", "ZZZZ")}
    title, rows = BC.run_basecross("all", fetch=_fetch(series), extra_tickers=["ZZZZ"])
    by = {r.ticker: r for r in rows}
    assert "ZZZZ" in by                                # 自訂 ticker 進得來
    assert by["INTC"].theme and "2022殺" in by["INTC"].theme
    assert "AI錯殺" in by["ADBE"].theme
    assert "電商" in by["MELI"].theme                  # agentic-commerce theme tag


def test_run_basecross_ecommerce_list():
    names = BC.ECOMMERCE_AGENTIC + BC.ECOMMERCE_SMALL
    series = {t: {"close": _daily([100 - i for i in range(40)]), "volume": []} for t in names}
    title, rows = BC.run_basecross("ecommerce", fetch=_fetch(series))
    assert "電商" in title and {r.ticker for r in rows} == set(names)


def test_run_basecross_ecommerce_small_list():
    series = {t: {"close": _daily([100 - i for i in range(40)]), "volume": []}
              for t in BC.ECOMMERCE_SMALL}
    title, rows = BC.run_basecross("ecommerce_small", fetch=_fetch(series))
    assert "小型" in title and {r.ticker for r in rows} == set(BC.ECOMMERCE_SMALL)
    assert "JMIA" in {r.ticker for r in rows}        # 主理人點名的小型電商


def test_run_basecross_space_list():
    series = {t: {"close": _daily([100 - i for i in range(40)]), "volume": []}
              for t in BC.SPACE_PUREPLAYS}
    title, rows = BC.run_basecross("space", fetch=_fetch(series))
    assert "太空" in title and {r.ticker for r in rows} == set(BC.SPACE_PUREPLAYS)
    by = {r.ticker: r for r in rows}
    assert "RKLB" in by and "ASTS" in by and "太空" in by["RKLB"].theme


def test_run_basecross_diversified_list():
    series = {t: {"close": _daily([100 - i for i in range(40)]), "volume": []}
              for t in BC.DIVERSIFIED_TURNAROUND}
    title, rows = BC.run_basecross("diversified", fetch=_fetch(series))
    assert "分散" in title and {r.ticker for r in rows} == set(BC.DIVERSIFIED_TURNAROUND)
    assert len(BC.DIVERSIFIED_TURNAROUND) == 15      # 15 檔跨產業
    assert "分散" in {r.ticker: r for r in rows}["KVUE"].theme


def test_run_basecross_midrisk_list():
    series = {t: {"close": _daily([100 - i for i in range(40)]), "volume": []}
              for t in BC.MID_RISK_TURNAROUND}
    title, rows = BC.run_basecross("midrisk", fetch=_fetch(series))
    assert "中風險" in title and {r.ticker for r in rows} == set(BC.MID_RISK_TURNAROUND)
    assert "C" in {r.ticker for r in rows} and "中風險" in {r.ticker: r for r in rows}["DE"].theme
