"""Offline tests for the cuFOLIO Mean-CVaR bridge ($hark side).

optimize() itself needs WSL + GPU + network, so it is NOT exercised here; we test
the pure marshalling (Windows→WSL path mapping) and — when discord.py is present —
the /optimize universe resolver and the embed renderer.
"""

from __future__ import annotations

import importlib.util

import pytest

from sharks.scoring.cufolio_optimize import _wsl_path


def test_wsl_path_maps_windows_drive():
    assert _wsl_path(r"C:\Users\x\f.json") == "/mnt/c/Users/x/f.json"
    assert _wsl_path(r"D:\DOT\$hark\t.json") == "/mnt/d/DOT/$hark/t.json"


_HAS_DISCORD = importlib.util.find_spec("discord") is not None
discord_only = pytest.mark.skipif(not _HAS_DISCORD, reason="discord.py not installed")


@discord_only
def test_resolve_universe_presets_and_custom():
    from sharks.discord.bot import _resolve_universe

    soft, lbl = _resolve_universe("software", None)
    assert "MSFT" in soft and lbl
    crypto, _ = _resolve_universe("crypto", None)
    assert "BTC-USD" in crypto                       # bare BTC mapped to a yfinance symbol
    custom, _ = _resolve_universe("software", "aapl, msft  nvda")
    assert custom == ["AAPL", "MSFT", "NVDA"]         # comma/space split + upper


@discord_only
def test_optimize_embed_ok_and_error():
    from sharks.discord.bot import optimize_to_embed

    ok = optimize_to_embed(
        {"ok": True, "expected_return": 0.0018, "CVaR": 0.041, "solve_time": 0.35,
         "used": 8, "requested": 8,
         "top": [["AVGO", 0.25], ["AMD", 0.24], ["MSFT", 0.0]]},
        "megacap", "cuopt")
    assert "Mean-CVaR" in ok.title
    assert any("權重" in f.name for f in ok.fields)   # weights field rendered
    assert any("RTX 5070" in (ok.footer.text or "") for _ in [0])  # GPU device noted

    err = optimize_to_embed({"ok": False, "error": "boom"}, "x", "cuopt")
    assert "boom" in err.description
