"""Exchange ticker-suffix recognition — Phase-2 後綴支援.

yfinance accepts Yahoo exchange-suffixed symbols natively (e.g. `2330.TW`,
`000660.KS`, `8053.T`, `0700.HK`, `MC.PA`) — `taiwan_universe.fetch_monthly`
already proves the data path works. What was missing is the METADATA layer this
module provides: parse a symbol's suffix into {exchange, country, currency,
region}, so the FOM universe, `tech_dd`'s non-US registry, and the regional
scanners can tag / route / FX-caveat non-US names uniformly instead of each
hard-coding its own list.

Pure, no network, no dependency.

Scoring caveat (documented, NOT hidden): FOM momentum/quality run on
LOCAL-CURRENCY price series, so cross-currency comparison carries an unhedged FX
component. Treat a non-US FOM as a WITHIN-REGION rank until a Phase-3
USD-normalisation lands. `fx_caveat()` returns the reminder string for any
non-US symbol.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Exchange:
    suffix: str
    exchange: str
    country: str
    currency: str
    region: str          # "NA" | "EU" | "APAC"


# Yahoo-Finance exchange suffixes → metadata. Extend as coverage grows.
SUFFIX_MAP: dict[str, Exchange] = {
    "TW":  Exchange("TW", "TWSE", "Taiwan", "TWD", "APAC"),
    "TWO": Exchange("TWO", "TPEx", "Taiwan", "TWD", "APAC"),
    "KS":  Exchange("KS", "KRX (KOSPI)", "South Korea", "KRW", "APAC"),
    "KQ":  Exchange("KQ", "KOSDAQ", "South Korea", "KRW", "APAC"),
    "T":   Exchange("T", "Tokyo SE", "Japan", "JPY", "APAC"),
    "HK":  Exchange("HK", "HKEX", "Hong Kong", "HKD", "APAC"),
    "SS":  Exchange("SS", "Shanghai SE", "China", "CNY", "APAC"),
    "SZ":  Exchange("SZ", "Shenzhen SE", "China", "CNY", "APAC"),
    "SW":  Exchange("SW", "SIX Swiss", "Switzerland", "CHF", "EU"),
    "PA":  Exchange("PA", "Euronext Paris", "France", "EUR", "EU"),
    "AS":  Exchange("AS", "Euronext Amsterdam", "Netherlands", "EUR", "EU"),
    "DE":  Exchange("DE", "XETRA", "Germany", "EUR", "EU"),
    "F":   Exchange("F", "Frankfurt SE", "Germany", "EUR", "EU"),
    "MI":  Exchange("MI", "Borsa Italiana", "Italy", "EUR", "EU"),
    "ST":  Exchange("ST", "Nasdaq Stockholm", "Sweden", "SEK", "EU"),
    "L":   Exchange("L", "London SE", "UK", "GBP", "EU"),
    "MC":  Exchange("MC", "BME Madrid", "Spain", "EUR", "EU"),
    "TO":  Exchange("TO", "Toronto SE", "Canada", "CAD", "NA"),
    "V":   Exchange("V", "TSX Venture", "Canada", "CAD", "NA"),
}


@dataclass(frozen=True)
class ParsedTicker:
    symbol: str          # as given (upper-cased)
    base: str            # symbol without the exchange suffix
    suffix: Optional[str]
    exchange: Optional[Exchange]
    is_non_us: bool
    is_adr_pink: bool    # OTC ADR pink (no dot, 5 letters ending F/Y)


def parse_ticker(symbol: str) -> ParsedTicker:
    """Parse a Yahoo symbol into its base + exchange metadata.

    A US primary listing (no recognised dot-suffix) → is_non_us=False, exchange=None.
    An OTC ADR pink (e.g. BYDDY, TCEHY, LVMUY — no dot, 5 letters ending F/Y) is
    flagged separately (these trade in USD but track a foreign primary)."""
    t = symbol.strip().upper()
    if "." in t:
        base, _, suf = t.rpartition(".")
        ex = SUFFIX_MAP.get(suf)
        return ParsedTicker(
            symbol=t, base=base, suffix=suf, exchange=ex,
            is_non_us=ex is not None, is_adr_pink=False,
        )
    is_pink = len(t) == 5 and t[-1] in {"F", "Y"}
    return ParsedTicker(symbol=t, base=t, suffix=None, exchange=None,
                        is_non_us=False, is_adr_pink=is_pink)


def is_non_us(symbol: str) -> bool:
    """True for a recognised non-US exchange-suffixed symbol."""
    return parse_ticker(symbol).is_non_us


def region_of(symbol: str) -> str:
    """'NA' | 'EU' | 'APAC'. Unsuffixed (US primary) and ADR pinks → 'NA'."""
    p = parse_ticker(symbol)
    return p.exchange.region if p.exchange else "NA"


def currency_of(symbol: str) -> str:
    """ISO currency of the listing. US primary / ADR pink → 'USD'."""
    p = parse_ticker(symbol)
    return p.exchange.currency if p.exchange else "USD"


def fx_caveat(symbol: str) -> Optional[str]:
    """Reminder for any non-US symbol that its FOM is computed in local currency
    (unhedged FX) — a within-region rank, not USD-comparable, pending Phase-3
    USD-normalisation. None for US listings."""
    p = parse_ticker(symbol)
    if not p.is_non_us:
        return None
    return (f"⚠ {p.exchange.country} listing ({p.exchange.currency}): FOM 以當地幣別計算，"
            "跨幣別比較含未對沖匯率成分 — 視為區域內排名，待 Phase-3 USD 正規化。")


def split_by_region(symbols) -> dict[str, list[str]]:
    """Bucket a list of symbols into US / APAC / EU / ADR_PINK for region-aware
    scanning (each region pulled + ranked within itself avoids the FX-mix bias)."""
    out: dict[str, list[str]] = {"US": [], "APAC": [], "EU": [], "ADR_PINK": []}
    for s in symbols:
        p = parse_ticker(s)
        if p.is_adr_pink:
            out["ADR_PINK"].append(p.symbol)
        elif p.exchange is None:
            out["US"].append(p.symbol)
        else:
            out[p.exchange.region].append(p.symbol)
    return out
