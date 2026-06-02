"""Attention radar — abnormal social/search attention as an EARLY-theme radar.

Per tech/social-attention-alpha.md: retail/search attention is a short-horizon,
mostly CONTRARIAN, retail-herding signal — its ONE durable positive use is EARLY
THEME DETECTION (a name's attention ACCELERATING before it is broadly held). This
module computes that signal (trailing-only, lookahead-safe) and optionally pulls a
free ApeWisdom snapshot, surfacing accelerating names as 🆕 candidates for human DD.

OBSERVE-FIRST + WATCHLIST-ONLY: it SURFACES, never buys. Attention at the extreme
IS the crowd → default contrarian. Pure core (no dependency) + a best-effort
stdlib-urllib ApeWisdom fetch that degrades gracefully when offline.
"""

from __future__ import annotations

import json
import urllib.request
from typing import Optional

import numpy as np
import pandas as pd


def abnormal_attention(series: pd.Series, baseline: int = 30) -> Optional[float]:
    """Trailing z-score of the latest attention vs the prior `baseline` window,
    EXCLUDING the latest point (no lookahead). z > 2 = an abnormal spike."""
    s = series.dropna()
    if len(s) < baseline + 2:
        return None
    hist = s.iloc[-(baseline + 1):-1]      # prior window, excludes the latest point
    mu, sd = float(hist.mean()), float(hist.std(ddof=1))
    if sd <= 1e-9:
        return None
    return float((s.iloc[-1] - mu) / sd)


def acceleration(series: pd.Series, short: int = 3, long: int = 10) -> Optional[float]:
    """Short-MA vs long-MA of attention (normalised). Positive = accelerating —
    the theme-trigger the principal wants BEFORE the crowd arrives."""
    s = series.dropna()
    if len(s) < long + 1:
        return None
    sm = float(s.iloc[-short:].mean())
    lm = float(s.iloc[-long:].mean())
    if lm <= 1e-9:
        return None
    return float((sm - lm) / lm)


def attention_score(series: pd.Series, baseline: int = 30) -> dict:
    """Combine abnormal-z + acceleration into an early-theme score + a crowding
    flag. early_theme_score rewards ACCELERATING-but-not-yet-extreme; `crowded`
    (z > 3) means peak attention ≈ peak crowding ≈ reversal risk (contrarian)."""
    z = abnormal_attention(series, baseline)
    acc = acceleration(series)
    if z is None or acc is None:
        return {"z": z, "acceleration": acc, "early_theme_score": None, "crowded": None}
    not_extreme = 1.0 if 0.0 < z < 3.0 else 0.5
    early = max(0.0, acc) * not_extreme
    return {"z": round(z, 3), "acceleration": round(acc, 4),
            "early_theme_score": round(early, 4), "crowded": bool(z > 3.0)}


def fetch_apewisdom(filter_: str = "all-stocks", page: int = 1, timeout: int = 10) -> Optional[list[dict]]:
    """Best-effort free ApeWisdom mention ranks (no API key). Returns None on ANY
    failure (offline / rate-limit / schema change) — never raises. Snapshot only,
    NO point-in-time history (sourcing caveat per social-attention-alpha.md)."""
    url = f"https://apewisdom.io/api/v1.0/filter/{filter_}/page/{page}"
    try:
        with urllib.request.urlopen(url, timeout=timeout) as r:  # nosec - read-only public API
            data = json.loads(r.read().decode("utf-8"))
        return data.get("results", [])
    except Exception:
        return None


def radar_from_apewisdom(top: int = 15) -> dict:
    """Snapshot radar ranked by mention VELOCITY (24h change). WATCHLIST candidates
    for human DD; observe-first. Degrades gracefully when ApeWisdom is unreachable
    (the pure core above still works on any supplied attention series)."""
    rows = fetch_apewisdom()
    if rows is None:
        return {"available": False, "candidates": [],
                "note": ("ApeWisdom unreachable (offline/rate-limit). The pure-core "
                         "attention_score() still works on a supplied mention/SVI series.")}
    cands = []
    for r in rows:
        try:
            m = float(r.get("mentions", 0))
            mp = float(r.get("mentions_24h_ago") or 0)
        except (TypeError, ValueError):
            continue
        vel = (m - mp) / mp if mp > 0 else None
        if vel is None:
            continue
        cands.append({"ticker": r.get("ticker"), "name": r.get("name"),
                      "mentions": r.get("mentions"), "velocity": round(vel, 3),
                      "rank": r.get("rank")})
    cands.sort(key=lambda c: c["velocity"], reverse=True)
    return {"available": True, "candidates": cands[:top],
            "note": ("Snapshot only (no PIT history); attention is contrarian at the "
                     "extreme; WATCHLIST → human DD, never auto-buy.")}


def main() -> int:
    import sys
    from datetime import datetime, timezone
    from pathlib import Path

    radar = radar_from_apewisdom()
    report = {
        "as_of": datetime.now(timezone.utc).isoformat(),
        "report_type": "attention_radar",
        "observe_first": True,
        "note": ("Early-theme radar (accelerating, not-yet-crowded). Feeds tech/_weekly-watch "
                 "as 🆕 human-DD candidates. Contrarian at extreme; never a buy signal."),
        **radar,
    }
    out = Path("outputs") / "attention-radar.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    print(f"wrote {out}  (apewisdom available={radar['available']})", file=sys.stderr)
    if radar["available"]:
        print("top velocity:", [c["ticker"] for c in radar["candidates"][:8]], file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
