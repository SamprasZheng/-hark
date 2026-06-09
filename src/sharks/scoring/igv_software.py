"""IGV software-sector screen — the 「IGV 錯殺抄底 + NVIDIA 合作」 feature.

Universe: the FULL IGV (iShares Expanded Tech-Software Sector ETF) constituent list
(112 US-listed equities, from the fund's SEC NPORT-P period-end 2026-03-31, top-25
weights cross-checked vs stockanalysis.com 2026-05-28). Refresh: re-pull the NPORT-P
or stockanalysis holdings and replace IGV_UNIVERSE; bump IGV_AS_OF.

For each name the screen composes THREE layers:

  1. FOM dimensions (price-derived) via the owner's EXISTING engine
     `scoring.fom_alpha.score_ticker_alpha` — momentum / contrarian (逆勢) / quality /
     bubble_guard / moat. The contrarian dimension is the 錯殺 (oversold) signal.

  2. Fundamentals (only for the screened SHORTLIST, to keep runtime sane) via
     `scoring.fundamentals.fetch_fundamentals` + `scoring.valuation.industry_pe_valuation`:
     forward P/E, revenue growth, analyst upside, premium-to-fair, realistic downside,
     turnaround_score — so a 錯殺 call is checked against real numbers, not just price.

  3. NVIDIA-partnership tag (curated `NVIDIA_PARTNERS`) — which names have an announced
     NVIDIA collaboration and of what KIND. This is the current volatility catalyst:
     these move on NVDA / GTC / Computex newsflow. Tier ranks correlation strength:
     equity (NVDA owns a stake) > headline (GTC-grade co-dev/co-market) > medium >
     integration (product-level only).

Output: `outputs/igv-software-<date>.json` with 錯殺型 / 趨勢型 / nvidia_partners buckets.
Recommend-only / research-and-education. Data yfinance grade-C. No trades, no caps touched.

Run: PYTHONPATH=src .venv/Scripts/python.exe -m sharks.scoring.igv_software [YYYY-MM-DD]
"""
from __future__ import annotations

import json
import sys
import warnings
from datetime import datetime, timezone
from pathlib import Path

warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)

import pandas as pd

from sharks.scoring.fom import fetch_monthly, INDICES, SECTOR_ETFS
from sharks.scoring.fom_alpha import score_ticker_alpha

# ─── Full IGV universe (SEC NPORT-P 2026-03-31; equities only, cash/derivatives dropped) ──
IGV_AS_OF = "2026-03-31"
IGV_SOURCE = "iShares Expanded Tech-Software Sector ETF — SEC NPORT-P; xref stockanalysis.com/etf/igv"
IGV_UNIVERSE = [
    "PLTR", "MSFT", "ORCL", "CRM", "PANW", "INTU", "APP", "NOW", "ADBE", "CRWD",
    "SNPS", "CDNS", "FTNT", "ADSK", "EA", "MSTR", "DDOG", "ROP", "TTWO", "WDAY",
    "FICO", "ZM", "PTC", "TRMB", "TYL", "ZS", "HUBS", "GWRE", "TEAM", "IOT",
    "DT", "GEN", "NTNX", "DOCU", "BMNR", "MANH", "IDCC", "U", "RBRK", "PCOR",
    "CWAN", "DSGX", "OTEX", "QBTS", "BSY", "CRCL", "AUR", "SNAP", "WULF", "PATH",
    "CORZ", "ESTC", "HUT", "YOU", "S", "ACIW", "RIOT", "DBX", "PEGA", "APPF",
    "CIFR", "DLB", "TTAN", "CCCS", "BOX", "BILL", "ZETA", "LIF", "QLYS", "WK",
    "MARA", "GTLB", "QTWO", "KVYO", "RNG", "SOUN", "ADEA", "VRNS", "TDC", "BRZE",
    "CLSK", "ALRM", "SPSC", "OS", "TENB", "BL", "AGYS", "BB", "RAMP", "FRSH",
    "ATEN", "NCNO", "INTA", "NN", "BLKB", "AVPT", "ALKT", "FIVN", "LSPD", "PRGS",
    "AI", "APPN", "VYX", "VERX", "CXM", "ASAN", "PD", "SEMR", "PAR", "NABL", "RPD",
]

# Names in IGV that are NOT pure software (crypto miners / BTC-treasury / quantum) —
# surfaced so a 錯殺 reading isn't mistaken for a software-fundamentals call.
IGV_NON_SOFTWARE = {
    "MSTR", "BMNR", "CRCL", "WULF", "HUT", "CORZ", "CIFR", "RIOT", "MARA", "CLSK",  # crypto/BTC
    "QBTS",  # quantum
    "AUR",   # autonomous trucking
    "SNAP",  # social/ads
}

# ─── Curated NVIDIA-partnership intel (2026-06-02; verified w/ sources) ──────────
# tier: equity > headline > medium > integration (descending NVDA-correlation strength)
NVIDIA_PARTNERS: dict[str, dict] = {
    "SNPS": {"tier": "equity", "type": "cuLitho / EDA on Grace-Blackwell + NVDA equity stake (~$2B)",
             "note": "GPU-accelerated EDA up to 15x + cuLitho in production at TSMC; NVDA equity = tightest correlation to NVDA newsflow",
             "url": "https://nvidianews.nvidia.com/news/nvidia-and-synopsys-announce-strategic-partnership-to-revolutionize-engineering-and-design"},
    "NOW":  {"tier": "headline", "type": "NIM / Llama-Nemotron / agentic AI co-dev",
             "note": "Native AI Agents on NVIDIA NIM + blueprints; AI Enterprise + DGX Cloud; GTC 2025 expansion",
             "url": "https://www.servicenow.com/company/media/press-room/nvidia-agentic-ai-partnership.html"},
    "CRWD": {"tier": "headline", "type": "NIM / Nemotron security agents",
             "note": "Falcon + NIM for genAI threat hunting; Oct 2025 Charlotte AI AgentWorks on Nemotron+NIM",
             "url": "https://www.crowdstrike.com/en-us/press-releases/crowdstrike-nvidia-redefine-cybersecurity-always-on-ai-agents-protect-nations-digital-infrastructure/"},
    "PLTR": {"tier": "headline", "type": "GPU-accelerated Ontology / cuOpt",
             "note": "AIP + Ontology on NVIDIA GPU data processing + cuOpt; GTC DC Oct 2025; launch customer Lowe's",
             "url": "https://nvidianews.nvidia.com/news/nvidia-palantir-ai-enterprise-data-intelligence"},
    "CDNS": {"tier": "headline", "type": "Blackwell EDA / digital twin",
             "note": "Millennium M2000 on Blackwell (GB200 NVL72); GPU-accelerated EDA up to 80x; expanded Apr 2026",
             "url": "https://blogs.nvidia.com/blog/cadence-millennium-nvidia-blackwell/"},
    "ADBE": {"tier": "headline", "type": "NeMo / Omniverse / Firefly Foundry",
             "note": "GTC Mar 2026: Firefly on CUDA-X/NeMo/Cosmos + Agent Toolkit; 3D digital-twin on Omniverse",
             "url": "https://www.businesswire.com/news/home/20260316532073/en/"},
    "CRM":  {"tier": "headline", "type": "Agentforce + Nemotron",
             "note": "Agentforce autonomous agents on NVIDIA AI; Nemotron Nano 3 inside the NVIDIA Agent Toolkit",
             "url": "https://www.salesforce.com/news/press-releases/2024/09/17/nvidia-ai-agent-partnership/"},
    "DT":   {"tier": "medium", "type": "AI/LLM observability for NVIDIA AI Factory",
             "note": "May 2025: full-stack + LLM observability in NVIDIA Enterprise AI Factory design (Blackwell/NIM)",
             "url": "https://www.dynatrace.com/news/press-release/dynatrace-nvidia-ai-llm-observability/"},
    "DDOG": {"tier": "integration", "type": "GPU monitoring (product-level, not a headline partnership)",
             "note": "DCGM/NVML exporters + GPU Monitoring; in NVIDIA Enterprise AI Factory ecosystem; NOT co-marketed",
             "url": "https://www.datadoghq.com/blog/monitor-nvidia-gpus-with-datadog/"},
    # SNOW (Snowflake) has a real NVIDIA partnership but is NOT an IGV constituent — kept for reference.
    "SNOW": {"tier": "headline", "type": "NeMo Retriever / NIM in Cortex (NOT in IGV)",
             "note": "NVIDIA AI Enterprise + NeMo Retriever in Snowflake Cortex; Arctic served as a NIM",
             "url": "https://www.snowflake.com/en/news/press-releases/snowflake-and-nvidia-power-customized-ai-applications-for-customers-and-partners/"},
}
_TIER_RANK = {"equity": 0, "headline": 1, "medium": 2, "integration": 3}


# ─── Pure helpers (offline, unit-tested) ────────────────────────────────────────
def nvidia_tag(ticker: str) -> dict | None:
    """The NVIDIA-partnership tag for an IGV name, or None. Pure."""
    p = NVIDIA_PARTNERS.get(ticker)
    if not p:
        return None
    return {"tier": p["tier"], "type": p["type"], "note": p["note"], "url": p["url"]}


def is_oversold(row: dict, *, min_contrarian: float = 55.0, min_moat: int = 50,
                bubble_floor: float = -50.0) -> bool:
    """錯殺型: contrarian (逆勢) high, moat intact, not an extreme-bubble name. Pure."""
    return (row.get("contrarian", 0) >= min_contrarian
            and row.get("ip_defensibility", 0) >= min_moat
            and row.get("bubble_guard", -100) > bubble_floor)


def is_momentum(row: dict, *, min_momentum: float = 55.0, bubble_floor: float = -50.0) -> bool:
    """趨勢型: momentum high, not an extreme-bubble name. Pure."""
    return row.get("momentum", 0) >= min_momentum and row.get("bubble_guard", -100) > bubble_floor


def partner_sort_key(row: dict) -> tuple:
    """Sort NVIDIA partners by tier (equity first) then FOM-alpha desc. Pure."""
    nv = row.get("nvidia") or {}
    return (_TIER_RANK.get(nv.get("tier"), 9), -row.get("final_fom_alpha", 0))


def _recent_return(closes, ticker, bars: int = 3):
    try:
        s = closes[ticker].dropna()
    except Exception:
        return None
    if len(s) < bars + 1:
        return None
    try:
        return round(float(s.iloc[-1] / s.iloc[-1 - bars] - 1.0), 3)
    except Exception:
        return None


# ─── Screen ─────────────────────────────────────────────────────────────────────
def fom_rows(closes, as_of: pd.Timestamp) -> list[dict]:
    """FOM-score every IGV name we have price data for (price-derived; no network
    beyond the closes already fetched). Adds ret_3m + the NVIDIA tag + non-software flag."""
    rows: list[dict] = []
    for t in IGV_UNIVERSE:
        if t not in closes.columns or closes[t].dropna().empty:
            continue
        try:
            r = score_ticker_alpha(closes, t, as_of)
        except Exception:
            continue
        r["ret_3m"] = _recent_return(closes, t)
        r["nvidia"] = nvidia_tag(t)
        r["non_software"] = t in IGV_NON_SOFTWARE
        rows.append(r)
    return rows


def attach_fundamentals(rows: list[dict], tickers: set[str]) -> None:
    """Pull fundamentals + P/E-anchored valuation for `tickers` (network) and merge
    the key numbers in-place. Best-effort; a failed name just carries no fundamentals."""
    from sharks.scoring.fundamentals import fetch_fundamentals
    from sharks.scoring.valuation import industry_pe_valuation
    by_ticker = {r["ticker"]: r for r in rows}
    for t in tickers:
        r = by_ticker.get(t)
        if r is None:
            continue
        try:
            f = fetch_fundamentals(t)
        except Exception:
            continue
        val = None
        try:
            val = industry_pe_valuation(f)
        except Exception:
            val = None
        r["fundamentals"] = {
            "fwd_pe": f.get("fwd_pe"), "trailing_pe": f.get("trailing_pe"),
            "ps_ttm": f.get("ps_ttm"), "revenue_growth_yoy": f.get("revenue_growth_yoy"),
            "operating_margin": f.get("operating_margin"), "fcf": f.get("fcf"),
            "analyst_upside": f.get("analyst_upside"), "market_cap": f.get("market_cap"),
            "recommendation": f.get("recommendation"),
            "turnaround_score": (f.get("flags") or {}).get("turnaround_score"),
            "premium_to_industry_fair": (val or {}).get("premium_to_industry_fair"),
            "realistic_downside": (val or {}).get("realistic_downside"),
        }


def screen(as_of: pd.Timestamp, *, with_fundamentals: bool = True,
           shortlist_n: int = 12) -> dict:
    """Run the full IGV screen. Returns the report dict (also what main() writes)."""
    start = (as_of - pd.Timedelta(days=6 * 365)).strftime("%Y-%m-%d")
    uni = sorted(set(IGV_UNIVERSE) | set(INDICES) | set(SECTOR_ETFS))
    closes = fetch_monthly(uni, start, as_of.strftime("%Y-%m-%d"))
    rows = fom_rows(closes, as_of)

    oversold = sorted([r for r in rows if is_oversold(r)],
                      key=lambda x: x["contrarian"], reverse=True)
    momentum = sorted([r for r in rows if is_momentum(r)],
                      key=lambda x: x["momentum"], reverse=True)
    partners = sorted([r for r in rows if r.get("nvidia")], key=partner_sort_key)

    # Deepen only the shortlist with fundamentals (network): top oversold + top
    # momentum + every NVIDIA partner. Keeps the run tractable on ~112 names.
    if with_fundamentals:
        shortlist = ({r["ticker"] for r in oversold[:shortlist_n]}
                     | {r["ticker"] for r in momentum[:shortlist_n]}
                     | {r["ticker"] for r in partners})
        attach_fundamentals(rows, shortlist)

    def slim(r: dict) -> dict:
        keep = ("ticker", "final_fom_alpha", "momentum", "contrarian", "bubble_guard",
                "quality", "ip_defensibility", "ret_3m", "nvidia", "non_software", "fundamentals")
        return {k: r.get(k) for k in keep if k in r}

    return {
        "as_of": datetime.now(timezone.utc).isoformat(),
        "screen_date": as_of.strftime("%Y-%m-%d"),
        "report_type": "igv_software_screen",
        "igv_as_of": IGV_AS_OF, "igv_source": IGV_SOURCE,
        "universe_size": len(IGV_UNIVERSE), "scored": len(rows),
        "note": ("FOM (price) + fundamentals (shortlist) + NVIDIA-partner catalyst tag. "
                 "錯殺=逆勢高+護城河完好; NVIDIA partner tier equity>headline>medium>integration "
                 "= NVDA-newsflow correlation. yfinance grade-C; research/observe-only, not advice."),
        "oversold": [slim(r) for r in oversold],
        "momentum": [slim(r) for r in momentum],
        "nvidia_partners": [slim(r) for r in partners],
        "all_scored": [slim(r) for r in sorted(rows, key=lambda x: x["final_fom_alpha"], reverse=True)],
    }


def main() -> int:
    as_of = pd.Timestamp(sys.argv[1]) if len(sys.argv) > 1 else pd.Timestamp.today().normalize()
    print(f"IGV software screen as of {as_of.date()} — {len(IGV_UNIVERSE)} names", file=sys.stderr)
    report = screen(as_of)
    out_dir = Path("outputs")
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"igv-software-{as_of.strftime('%Y-%m-%d')}.json"
    path.write_text(json.dumps(report, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    print(f"wrote {path} (scored {report['scored']}/{report['universe_size']})", file=sys.stderr)

    def line(r):
        nv = r.get("nvidia")
        fu = r.get("fundamentals") or {}
        au = fu.get("analyst_upside")
        return (f"  {r['ticker']:5} FOMa={r.get('final_fom_alpha',0):5.1f} "
                f"逆勢={r.get('contrarian',0):4.0f} 動能={r.get('momentum',0):4.0f} "
                f"泡沫={r.get('bubble_guard',0):5.0f} 護城河={r.get('ip_defensibility',0):3} "
                f"3m={r.get('ret_3m')} fPE={fu.get('fwd_pe')} 分析師={au} "
                f"{'NV:'+nv['tier'] if nv else ''}")

    print("\n=== 錯殺型 oversold (top 8) ===", file=sys.stderr)
    for r in report["oversold"][:8]:
        print(line(r), file=sys.stderr)
    print("\n=== NVIDIA 合作夥伴 (by tier) ===", file=sys.stderr)
    for r in report["nvidia_partners"]:
        print(line(r), file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
