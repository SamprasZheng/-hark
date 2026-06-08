"""Offline test for the ecom_screens CLI render (no network/yfinance)."""

from __future__ import annotations

from sharks.discord import basecross as BC
from sharks.discord import ecom_screens as ES


def _fetch(ts):
    out = {}
    for t in ts:
        monthly = [100 - 1.5 * i for i in range(34)] + [49, 53]
        out[t] = {"close": [v for v in monthly for _ in range(21)],
                  "volume": [300 / 21] * (21 * 34) + [900 / 21] * (21 * 2)}
    return out


def test_render_has_three_sections_and_ranks():
    cands = BC.screen(["JMIA", "VIPS", "SHOP"], fetch=_fetch)
    txt = ES.render(cands, quality_by_ticker={"VIPS": 75.0})
    assert "綜合排名" in txt and "起漲訊號" in txt and "月線大底金叉" in txt
    assert "JMIA" in txt and "墓園" in txt          # weak-fundamental name flagged
    # VIPS (FOM 75 overrides prior) should outrank weak-fundamental JMIA overall
    assert txt.index("VIPS") < txt.index("JMIA")


def test_universe_scopes():
    assert ES._ecom_universe("small")[1] == list(BC.ECOMMERCE_SMALL)
    assert set(ES._ecom_universe("all")[1]) == set(BC.ECOMMERCE_AGENTIC) | set(BC.ECOMMERCE_SMALL)
