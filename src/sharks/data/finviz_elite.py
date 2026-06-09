"""Finviz Elite export-API client — the modern ``/export?...&auth=TOKEN`` endpoint.

SECURITY (read me):
- The API token comes **only** from env ``FINVIZ_ELITE_API_KEY`` (``.env`` is
  gitignored). It is **never** hardcoded, never committed, never printed/logged —
  ``redact()`` strips the ``auth=`` param from any URL we surface in errors.
- If a token ever appears in a screenshot/chat, regenerate it on Finviz.

WHAT it does: configure a screen in the Finviz UI, copy the ``f=...`` filter string
from the URL, and this fetches the CSV export → rows / tickers you can pipe into the
``basecross`` / ``rally`` / ``stealth`` screens.

Pure helpers (``build_export_url`` / ``redact`` / ``parse_csv`` / ``tickers_from_rows``)
are unit-tested offline; only ``fetch_screen`` touches the network (urllib follows
the 301 redirect automatically, so no ``curl -L`` needed). recommend-only.

Validate on a networked machine:
    FINVIZ_ELITE_API_KEY=... python -m sharks.data.finviz_elite "ta_alltime_b30h,sh_price_o5"
(or a preset name; prints ticker count + first rows, never the token).
"""

from __future__ import annotations

import csv
import io
import os
import re
import urllib.request
from typing import Optional

EXPORT_BASE = "https://elite.finviz.com/export"

# Convenience presets = the ``f=`` filter string copied from a Finviz screener URL.
# ⚠️ Finviz filter CODES change/vary — treat these as a STARTING POINT and verify by
# copying the f=... from your own configured screener (docs/finviz_screening_recipe.md
# explains the return×risk filter logic). Override freely by passing a raw filter str.
PRESETS: dict[str, str] = {
    # beaten (≥30% below ATH) + liquid + not a penny stock + above the 50d MA
    "dipbuy": "ta_alltime_b30h,sh_avgvol_o500,sh_price_o5,ta_sma50_pa",
    # add survival/quality layer: + current ratio>1.5 + positive sales growth
    "dipbuy_quality": "ta_alltime_b30h,sh_avgvol_o500,sh_price_o5,ta_sma50_pa,fa_curratio_o1.5,fa_sales5years_pos",
}

_TOKEN_ENV = "FINVIZ_ELITE_API_KEY"


def _token(explicit: Optional[str] = None) -> str:
    tok = (explicit or os.environ.get(_TOKEN_ENV, "")).strip()
    if not tok:
        raise RuntimeError(
            f"{_TOKEN_ENV} not set — put your Finviz Elite token in .env "
            f"(gitignored). Never commit it.")
    return tok


def redact(url: str) -> str:
    """Hide the auth token in any URL we print/log/raise."""
    return re.sub(r"(auth=)[^&]+", r"\1***", url)


def build_export_url(filters: str, *, token: str, view: str = "111",
                     columns: Optional[str] = None) -> str:
    """Build the export URL. ``filters`` = the Finviz ``f=`` string;
    ``columns`` = optional ``c=`` column ids."""
    query = f"v={view}&f={filters}"
    if columns:
        query += f"&c={columns}"
    return f"{EXPORT_BASE}?{query}&auth={token}"


def parse_csv(text: str) -> list[dict]:
    """Parse the export CSV text into a list of row dicts."""
    return list(csv.DictReader(io.StringIO(text)))


def tickers_from_rows(rows: list[dict]) -> list[str]:
    """Pull the ticker column (Finviz labels it 'Ticker')."""
    out = []
    for r in rows:
        t = (r.get("Ticker") or r.get("ticker") or "").strip()
        if t:
            out.append(t.upper())
    return out


def resolve_filters(filters_or_preset: str) -> str:
    """A preset name → its filter string; otherwise treat the input as a raw f= str."""
    return PRESETS.get(filters_or_preset, filters_or_preset)


def fetch_screen(filters_or_preset: str, *, token: Optional[str] = None,
                 view: str = "111", columns: Optional[str] = None,
                 timeout: int = 30) -> list[dict]:
    """Fetch a screen's CSV export → row dicts. Network; token from env. Errors are
    redacted so the token never leaks into a traceback/log."""
    filters = resolve_filters(filters_or_preset)
    url = build_export_url(filters, token=_token(token), view=view, columns=columns)
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 PolkaSharks"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:   # follows 301
            text = resp.read().decode("utf-8", "replace")
    except Exception as exc:
        raise RuntimeError(f"finviz export failed [{redact(url)}]: {exc}") from None
    if "<html" in text[:200].lower():
        raise RuntimeError("finviz returned HTML, not CSV — token invalid/expired or "
                           "bad filter string (URL redacted).")
    return parse_csv(text)


def fetch_tickers(filters_or_preset: str, **kw) -> list[str]:
    """Convenience: screen → ticker list (to feed basecross/rally/stealth)."""
    return tickers_from_rows(fetch_screen(filters_or_preset, **kw))


def main(argv: Optional[list[str]] = None) -> int:
    import sys
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv:
        print("用法: python -m sharks.data.finviz_elite '<f=過濾字串或preset>'\n"
              f"presets: {', '.join(PRESETS)}", file=sys.stderr)
        return 2
    arg = argv[0]
    try:
        rows = fetch_screen(arg)
    except Exception as exc:
        print(f"驗證失敗:{exc}", file=sys.stderr)   # token already redacted
        return 1
    tickers = tickers_from_rows(rows)
    print(f"✅ Finviz API OK — {len(tickers)} 檔(filters={resolve_filters(arg)})")
    print("前 30 檔:", ", ".join(tickers[:30]))
    print("→ 餵進系統:python -m sharks.discord.ecom_screens " + " ".join(tickers[:20]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
