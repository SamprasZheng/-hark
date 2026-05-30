"""Universe management — extended scan list + OTC handling + buy-warnings.

The FOM `DEFAULT_UNIVERSE` (~116) is the curated core. For broad moonshot /
value hunting the principal wants a much wider net (500-1000) and OTC names in
*consideration* — with an explicit warning before any OTC buy. This module
assembles the wider universe and carries the risk flags.

Honest scope note: a clean 500-1000 US-listed universe really wants a data-vendor
constituent file (this env lacks lxml for Wikipedia and the iShares endpoint is
anti-bot). So:
  - `EXTENDED_TICKERS` is a large hand-curated liquid-name batch (sectors broadly
    covered) that, with DEFAULT_UNIVERSE + the value QUALITY_COMPOUNDERS, reaches
    several hundred names.
  - `data/universe_extra.txt` (one ticker per line, '#'=comment) is a DROP-IN: put
    any vendor list there and `full_universe(include_extra=True)` folds it in — the
    clean path to 1000 without code changes.
  - OTC names live in `OTC_WATCH`, are OFF by default, and every OTC (or leveraged)
    ticker returns a `buy_warning()` so the system reminds the operator before a buy.
"""

from __future__ import annotations

from pathlib import Path

from sharks.scoring.fom import DEFAULT_UNIVERSE
from sharks.scoring.leveraged_etf import is_leveraged_etf, LEVERAGED_ETF_REGISTRY

# Large liquid US-listed batch across sectors (curated; deduped against
# DEFAULT_UNIVERSE at assembly). Intentionally broad so the scanner casts a wide
# net for both moonshots and beaten-down value.
EXTENDED_TICKERS = [
    # mega/large tech + comms
    "GOOG", "GOOGL", "AMZN", "AAPL", "ORCL", "IBM", "CSCO", "ADBE", "INTU", "CRM",
    "NOW", "SNPS", "CDNS", "ANSS", "ADSK", "WDAY", "TEAM", "DDOG", "SNOW", "NET",
    "PANW", "FTNT", "CRWD", "ZS", "OKTA", "MDB", "HUBS", "TTD", "APP", "SHOP",
    "UBER", "ABNB", "DASH", "SPOT", "RBLX", "PINS", "SNAP", "RDDT", "COIN", "HOOD",
    "PYPL", "SQ", "AFRM", "SOFI", "TOST", "NU", "MELI", "SE", "GLBE",
    # semis broad
    "INTC", "MU", "TXN", "ADI", "MCHP", "ON", "NXPI", "MPWR", "SWKS", "QRVO",
    "TER", "ENTG", "KLAC", "LRCX", "AMAT", "ASML", "TSM", "WOLF", "AMKR", "UMC",
    "ALAB", "CRDO", "ARM", "SMCI", "ANET", "CIEN", "COHR", "LITE", "INDI", "AMBA",
    # healthcare broad
    "JNJ", "LLY", "MRK", "ABBV", "PFE", "TMO", "DHR", "ABT", "MDT", "ISRG", "SYK",
    "BSX", "EW", "BDX", "ZBH", "BIIB", "VRTX", "REGN", "GILD", "AMGN", "BMY",
    "MRNA", "BNTX", "NVAX", "RXRX", "SDGR", "DNA", "CRSP", "NTLA", "BEAM", "VKTX",
    "HIMS", "DXCM", "PODD", "TNDM", "ELV", "CI", "HUM", "CVS", "UNH", "MCK", "CNC",
    # financials broad
    "JPM", "BAC", "WFC", "C", "GS", "MS", "SCHW", "BLK", "BX", "KKR", "APO", "ARES",
    "V", "MA", "AXP", "COF", "DFS", "SYF", "ALLY", "SPGI", "MCO", "ICE", "CME",
    "MSCI", "FDS", "NDAQ", "TROW", "BRK-B", "PGR", "TRV", "ALL", "CB", "AIG", "MET",
    # consumer broad
    "WMT", "COST", "TGT", "HD", "LOW", "DG", "DLTR", "KR", "BJ", "TJX", "ROST",
    "ORLY", "AZO", "ULTA", "BBY", "DKS", "FND", "RH", "W", "CHWY", "ETSY", "CVNA",
    "NKE", "LULU", "DECK", "ONON", "CROX", "SKX", "VFC", "RL", "TPR", "CPRI",
    "SBUX", "MCD", "CMG", "YUM", "DPZ", "WING", "TXRH", "DRI", "SHAK", "CAVA",
    "KO", "PEP", "MDLZ", "KHC", "GIS", "K", "HSY", "CL", "KMB", "CLX", "CHD",
    "PG", "EL", "MO", "PM", "STZ", "TAP", "DEO", "BUD",
    "DIS", "NFLX", "WBD", "PARA", "CMCSA", "T", "VZ", "TMUS", "EA", "TTWO", "RBLX",
    # industrials / energy / materials broad
    "GE", "HON", "MMM", "CAT", "DE", "BA", "RTX", "LMT", "NOC", "GD", "LHX", "HWM",
    "ETN", "EMR", "PH", "ROK", "ITW", "DOV", "AME", "FTV", "XYL", "IR", "CMI", "PCAR",
    "UNP", "CSX", "NSC", "UPS", "FDX", "ODFL", "JBHT", "CHRW", "EXPD", "SAIA",
    "URI", "PWR", "FAST", "GWW", "WM", "RSG", "WCN", "VRT", "GEV", "PWR", "ETN",
    "XOM", "CVX", "COP", "EOG", "SLB", "HAL", "OXY", "PSX", "MPC", "VLO", "WMB",
    "KMI", "OKE", "LNG", "FANG", "DVN", "HES", "TRGP", "APA", "CTRA", "EQT", "AR",
    "LIN", "SHW", "ECL", "APD", "FCX", "NEM", "NUE", "STLD", "VMC", "MLM", "DOW",
    "ALB", "MOS", "CF", "CTVA", "DD", "PPG", "RPM", "AVTR", "IFF",
    # utilities / real estate broad
    "NEE", "DUK", "SO", "D", "AEP", "EXC", "XEL", "PEG", "SRE", "ED", "WEC", "ES",
    "VST", "CEG", "NRG", "TLN", "AMT", "PLD", "EQIX", "DLR", "O", "CCI", "PSA",
    "SPG", "WELL", "VICI", "EXR", "AVB", "EQR", "INVH", "IRM", "SBAC",
    # autos / mobility
    "TSLA", "RIVN", "LCID", "GM", "F", "MBLY", "HSAI", "LAZR", "APTV", "BWA",
    # space / defense / new-industrial
    "RKLB", "LUNR", "ASTS", "PL", "RDW", "ACHR", "JOBY", "OKLO", "SMR", "BWXT",
]

# OTC / pink-sheet watch — OFF by default; high risk (thin liquidity, light
# disclosure, foreign ADR pinks). In consideration only; buy_warning() fires.
# NOTE: only GENUINE OTC pink-sheet ADRs here — NYSE/NASDAQ ADRs (e.g. NVO, TSM,
# ASML, BABA) live in EXTENDED_TICKERS, not here.
OTC_WATCH = [
    "TCEHY",   # Tencent
    "NSRGY",   # Nestle
    "RHHBY",   # Roche
    "ASMLF",   # ASML ordinary (OTC; NASDAQ primary is ASML)
    "TOELY",   # Tokyo Electron
    "SSNLF",   # Samsung Electronics
    "BYDDY",   # BYD
    "SFTBY",   # SoftBank
    "PCRFY",   # Panasonic
    "LVMUY",   # LVMH
]

_EXTRA_FILE = Path("data/universe_extra.txt")


def is_otc(ticker: str) -> bool:
    """Heuristic OTC flag: explicit OTC_WATCH membership, or a 5-letter ADR-pink
    suffix pattern (…F / …Y) not on a primary exchange."""
    t = ticker.upper()
    if t in OTC_WATCH:
        return True
    return len(t) == 5 and t[-1] in {"F", "Y"} and t not in DEFAULT_UNIVERSE


def buy_warning(ticker: str) -> str | None:
    """A pre-buy reminder string, or None if the name carries no special risk
    flag. The system surfaces this before any OTC / leveraged buy (per the
    principal's '如果真的要買就提醒我')."""
    t = ticker.upper()
    if is_otc(t):
        return ("⚠ OTC/pink-sheet: 流動性差、買賣價差大、資訊揭露少。買前確認真實成交量 "
                "+ 一手財報，且只用飆股 sleeve 的小額。")
    if is_leveraged_etf(t):
        spec = LEVERAGED_ETF_REGISTRY[t]
        if spec.get("vix_futures"):
            return "⚠ VIX-futures: contango 每月吃 5-10%，只能戰術對沖、不可長抱。"
        if spec["factor"] < 0:
            return "⚠ 反向 ETF: 對沖工具、每日 reset，趨勢一反就燒錢。"
        return f"⚠ {spec['factor']}x 槓桿 ETF: 每日 decay、波動放大；飆股 sleeve 小額戰術用。"
    return None


def _load_extra() -> list[str]:
    if not _EXTRA_FILE.exists():
        return []
    out = []
    for line in _EXTRA_FILE.read_text(encoding="utf-8").splitlines():
        s = line.split("#", 1)[0].strip().upper()
        if s:
            out.append(s)
    return out


def full_universe(include_extended: bool = True, include_otc: bool = False,
                  include_extra: bool = True) -> list[str]:
    """Assemble the scan universe. DEFAULT_UNIVERSE always included; EXTENDED on by
    default; OTC OFF by default (risk); the drop-in data/universe_extra.txt folded
    in when present (the path to a vendor 1000-name list)."""
    names = set(DEFAULT_UNIVERSE)
    if include_extended:
        names |= set(EXTENDED_TICKERS)
    if include_extra:
        names |= set(_load_extra())
    if include_otc:
        names |= set(OTC_WATCH)
    return sorted(names)
