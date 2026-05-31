"""Crypto Marketcap Top-100 tracker — daily breadth snapshot + structure analysis.

Compile-first, mirroring ``daily_health_check.py``: pure transforms where possible,
data-fetching injectable, ``main()`` never raises and returns 0, graceful
degrade (note, never fake). One run produces three point-in-time artifacts, each
``as_of``-stamped:

  1. ``crypto/data/top100-<DATE>.json``   — immutable raw snapshot (the facts)
  2. ``crypto/analysis/top100-<DATE>.md``  — human-readable structure analysis
  3. ``outputs/crypto-top100-<DATE>.json`` — machine handoff for downstream work

Data flow: CoinGecko ``/coins/markets`` → normalise → snapshot → categorise via
``crypto/watchlist.yaml`` → analysis + handoff. On fetch failure we re-emit the
last good snapshot under TODAY's date with ``live_data=false`` /
``stale_fallback=true`` (degrade, note, never silently reuse an old date).

GUARDRAILS (baked into every artifact): RECOMMEND-ONLY — this never trades. Crypto
is a small speculative satellite on an already risk-on-heavy book. BTC ≤4% notional
is a CORE macro holding (mechanical DCA, hard ceiling, OUTSIDE the Alpha sleeve);
alts live in the ≤5% Alpha sleeve — SPOT ONLY, no leverage / futures / margin /
crypto-leveraged products. Empty slots stay null; no padding. Posture is
de-risk / observation-first. The personal Alpha-sleeve policy lives in the private
finance/ system; BTC ≤4% is per philosophy/06-exclusions.md.

YAML is read WITHOUT pyyaml by reusing ``analysts/persona.py`` ``_parse_frontmatter``
(the watchlist is authored as a ``---``-fenced doc) — $hark stays dependency-free.
"""

from __future__ import annotations

import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from sharks.analysts.persona import _parse_frontmatter
from sharks.data.coingecko_client import (
    COINGECKO_BASE,
    MARKETS_PATH,
    CoinGeckoError,
    fetch_markets,
)

GUARDRAILS_NOTE = (
    "RECOMMEND-ONLY (never trades). Crypto = speculative satellite on an already "
    "risk-on-heavy book. BTC ≤4% notional is a CORE macro holding — mechanical DCA, "
    "hard ceiling, OUTSIDE the ≤5% Alpha sleeve. Alts live in the ≤5% Alpha sleeve: "
    "SPOT ONLY, NO leverage / futures / margin / crypto-leveraged products. Empty slots "
    "stay null (no padding). Posture: de-risk / observation-first."
)

# Movers are filtered to the top-N by market cap to cut microcap noise (the raw
# top-100 gainers are otherwise dominated by rank 80-100 microcaps).
MAJORS_RANK_CUTOFF = 50

# Tags that are not "narrative" buckets in the category breakdown render.
_NON_NARRATIVE_TAGS = ("uncategorized", "stablecoin")


# ── IO helpers ────────────────────────────────────────────────────────────────

def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_watchlist(path) -> dict:
    """Parse ``crypto/watchlist.yaml`` (a ``---``-fenced doc) without pyyaml, reusing
    the persona frontmatter reader. Returns {} if the file is absent."""
    p = Path(path)
    if not p.exists():
        return {}
    return _parse_frontmatter(p.read_text(encoding="utf-8"))


def latest_snapshot(data_dir) -> Optional[dict]:
    """Most recent ``top100-*.json`` snapshot, or None. Mirrors ``_latest_audit``."""
    p = Path(data_dir)
    if not p.exists():
        return None
    files = sorted(p.glob("top100-*.json"))
    if not files:
        return None
    try:
        return json.loads(files[-1].read_text(encoding="utf-8"))
    except Exception:
        return None


# ── pure transforms (no network) ──────────────────────────────────────────────

def _sym(coin: dict) -> str:
    return (coin.get("symbol") or "").upper()


def categorize(coins: list[dict], category_tags: Optional[dict], stablecoins) -> dict:
    """Bucket each coin into its watchlist narrative tag(s). A coin may carry several
    tags (e.g. BNB = l1 + exchange_token). Coins in no tag and not a stablecoin fall
    into ``uncategorized`` — the report names them so new narratives aren't missed."""
    stable = {s.upper() for s in (stablecoins or [])}
    tag_map = {tag: {s.upper() for s in (syms or [])} for tag, syms in (category_tags or {}).items()}
    out: dict[str, list[str]] = {tag: [] for tag in tag_map}
    out["stablecoin"] = []
    out["uncategorized"] = []
    for coin in coins:
        s = _sym(coin)
        if not s:
            continue
        if s in stable:
            out["stablecoin"].append(s)
        tagged = False
        for tag, members in tag_map.items():
            if s in members:
                out[tag].append(s)
                tagged = True
        if not tagged and s not in stable:
            out["uncategorized"].append(s)
    return out


def market_structure(coins: list[dict], stablecoins) -> dict:
    """Total tracked market cap, BTC dominance, ETH share, stablecoin share, and
    top-10 concentration — the cross-sectional gauges. Percentages are of the
    tracked set (top-N), not the whole market; the report says so."""
    stable = {s.upper() for s in (stablecoins or [])}
    total = sum(c.get("market_cap") or 0 for c in coins)
    by_sym: dict[str, float] = {}
    for c in coins:
        s = _sym(c)
        if s and s not in by_sym:
            by_sym[s] = c.get("market_cap") or 0
    btc = by_sym.get("BTC", 0)
    eth = by_sym.get("ETH", 0)
    stable_mcap = sum(mc for s, mc in by_sym.items() if s in stable)
    ranked = sorted((c.get("market_cap") or 0 for c in coins), reverse=True)
    top10 = sum(ranked[:10])

    def pct(x):
        return round(100.0 * x / total, 2) if total else None

    return {
        "total_market_cap": total,
        "coin_count": len(coins),
        "btc_dominance_pct": pct(btc),
        "eth_share_pct": pct(eth),
        "stablecoin_share_pct": pct(stable_mcap),
        "top10_concentration_pct": pct(top10),
    }


def compute_movers(coins: list[dict], key: str = "price_change_pct_24h", n: int = 10,
                   max_rank: Optional[int] = None) -> dict:
    """Top-``n`` gainers and losers by ``key`` (a price-change window). Coins missing
    the field are excluded rather than treated as 0. When ``max_rank`` is set, only coins
    ranked <= max_rank are considered — cuts the microcap noise that otherwise dominates
    the raw top-100 gainers."""
    pool = coins
    if max_rank is not None:
        pool = [c for c in coins
                if isinstance(c.get("market_cap_rank"), int)
                and not isinstance(c.get("market_cap_rank"), bool)
                and c["market_cap_rank"] <= max_rank]
    vals = [c for c in pool if isinstance(c.get(key), (int, float)) and not isinstance(c.get(key), bool)]
    ordered = sorted(vals, key=lambda c: c[key])

    def row(c):
        return {"symbol": _sym(c), key: round(c[key], 2), "rank": c.get("market_cap_rank")}

    losers = [row(c) for c in ordered[:n]]
    gainers = [row(c) for c in reversed(ordered[-n:])]
    return {"window": key, "max_rank": max_rank, "gainers": gainers, "losers": losers}


def _rank_map(snap) -> dict:
    coins = snap.get("coins", []) if isinstance(snap, dict) else (snap or [])
    out = {}
    for c in coins:
        s = (c.get("symbol") or "").upper()
        if s:
            out[s] = c.get("market_cap_rank")
    return out


def rank_churn(today, prev, n: int = 10) -> dict:
    """New entrants / drop-outs / biggest rank moves vs the prior snapshot."""
    if not prev:
        return {"available": False, "note": "no prior snapshot — churn unavailable on first run."}
    t, p = _rank_map(today), _rank_map(prev)
    new_entrants = sorted(s for s in t if s not in p)
    dropped_out = sorted(s for s in p if s not in t)
    moves = [
        {"symbol": s, "prev_rank": p[s], "rank": t[s], "delta": p[s] - t[s]}
        for s in t
        if s in p and t[s] is not None and p[s] is not None
    ]
    moves.sort(key=lambda x: abs(x["delta"]), reverse=True)
    return {
        "available": True,
        "new_entrants": new_entrants,
        "dropped_out": dropped_out,
        "biggest_rank_moves": moves[:n],
    }


# ── snapshot envelope + handoff ───────────────────────────────────────────────

def build_snapshot_envelope(coins, *, as_of, as_of_date, vs_currency, live_data, stale, source_per_page):
    env = {
        "schema_version": 1,
        "as_of": as_of,
        "as_of_date": as_of_date,
        "source": "coingecko",
        "source_url": f"{COINGECKO_BASE}{MARKETS_PATH}",
        "vs_currency": vs_currency,
        "per_page": source_per_page,
        "count": len(coins),
        "live_data": live_data,
        "stale_fallback": bool(stale.get("stale_fallback")) if stale else False,
        "coins": coins,
    }
    if stale:
        for k, v in stale.items():
            if k != "stale_fallback":
                env[k] = v
    return env


def write_snapshot(snapshot: dict, data_dir) -> Path:
    d = Path(data_dir)
    d.mkdir(parents=True, exist_ok=True)
    path = d / f"top100-{snapshot['as_of_date']}.json"
    path.write_text(json.dumps(snapshot, indent=2, default=str), encoding="utf-8")
    return path


def build_handoff(snapshot, structure, movers_24h, movers_7d, categories, churn, watchlist) -> dict:
    return {
        "schema_version": 1,
        "as_of": snapshot["as_of"],
        "as_of_date": snapshot["as_of_date"],
        "report_type": "crypto_top100",
        "live_data": snapshot["live_data"],
        "stale_fallback": snapshot["stale_fallback"],
        "guardrails": GUARDRAILS_NOTE,
        "market_structure": structure,
        "movers_24h": movers_24h,
        "movers_7d": movers_7d,
        "categories": categories,
        "category_counts": {k: len(v) for k, v in categories.items()},
        "uncategorized": categories.get("uncategorized", []),
        "rank_churn": churn,
        "watchlist_overrides": watchlist.get("human_overrides", {}),
    }


# ── markdown render ───────────────────────────────────────────────────────────

def _human(n) -> str:
    if not n:
        return "0"
    for unit, div in (("T", 1e12), ("B", 1e9), ("M", 1e6)):
        if abs(n) >= div:
            return f"{n / div:.2f}{unit}"
    return f"{n:.0f}"


def _mover_table(append, movers: dict) -> None:
    key = movers["window"]
    scope = f" · top-{movers['max_rank']}" if movers.get("max_rank") else ""
    append(f"| dir | symbol | {key}{scope} | rank |")
    append("|---|---|---|---|")
    for i, g in enumerate(movers["gainers"], 1):
        append(f"| ▲{i} | {g['symbol']} | {g.get(key)} | {g.get('rank')} |")
    for i, l in enumerate(movers["losers"], 1):
        append(f"| ▼{i} | {l['symbol']} | {l.get(key)} | {l.get('rank')} |")


def _ordered_overrides(overrides: dict) -> list[str]:
    """DOT and BTC always spotlighted first (mandatory), then the rest."""
    priority = [k for k in ("DOT", "BTC") if k in overrides]
    rest = [k for k in overrides if k not in priority]
    return priority + rest


def render_markdown(snapshot, structure, movers_24h, movers_7d, categories, churn, watchlist) -> str:
    lines: list[str] = []
    A = lines.append
    flag = "LIVE" if snapshot["live_data"] else "STALE-FALLBACK ⚠"
    A(f"# Crypto Top-{snapshot['count']} — {snapshot['as_of_date']} ({flag})")
    A("")
    A(f"> as_of: `{snapshot['as_of']}` · source: {snapshot['source']} · vs: {snapshot['vs_currency']}")
    if snapshot.get("stale_fallback"):
        A(">")
        A(f"> ⚠ **STALE FALLBACK** — live fetch failed; re-emitting the last good snapshot "
          f"(`{snapshot.get('stale_source_as_of')}`) under today's date. Numbers are NOT current. "
          f"Error: `{snapshot.get('error')}`")
    A("")
    A(f"> **Guardrails** — {GUARDRAILS_NOTE}")
    A("")
    A("---")
    A("")

    A("## Market structure")
    A("")
    ms = structure
    A(f"- Total tracked market cap (top-{ms['coin_count']}): **${_human(ms['total_market_cap'])}**")
    A(f"- BTC dominance: **{ms['btc_dominance_pct']}%** · ETH share: {ms['eth_share_pct']}% "
      f"· Stablecoin share: {ms['stablecoin_share_pct']}% · Top-10 concentration: "
      f"{ms['top10_concentration_pct']}%")
    A("")
    A("> BTC dominance is the discriminating gauge for the cycle theses "
      "([[philosophy/concepts/btc-halving-cycle]] vs [[philosophy/concepts/institutional-btc-anchor]]). "
      "Rising dominance in a drawdown = alts bleeding to BTC. The Compiler reconciles this LIVE number "
      "against the model pages; a contradiction is flagged on the older page (wiki rule).")
    A("")

    A("## Movers — 24h")
    A("")
    _mover_table(A, movers_24h)
    A("")
    A("## Movers — 7d")
    A("")
    _mover_table(A, movers_7d)
    A("")

    A("## Narrative categories")
    A("")
    for tag, syms in categories.items():
        if tag in _NON_NARRATIVE_TAGS:
            continue
        if syms:
            A(f"- **{tag}** ({len(syms)}): {', '.join(syms)}")
    if categories.get("stablecoin"):
        A(f"- _stablecoin_ ({len(categories['stablecoin'])}): {', '.join(categories['stablecoin'])}")
    A("")
    uncat = categories.get("uncategorized", [])
    if uncat:
        A(f"> ⚠ **Uncategorized ({len(uncat)})** — not in any watchlist tag; possible NEW narrative "
          f"to map into `crypto/watchlist.yaml`: {', '.join(uncat)}")
        A("")

    A("## Rank churn vs prior snapshot")
    A("")
    if churn.get("available"):
        if churn.get("new_entrants"):
            A(f"- New entrants: {', '.join(churn['new_entrants'])}")
        if churn.get("dropped_out"):
            A(f"- Dropped out: {', '.join(churn['dropped_out'])}")
        if churn.get("biggest_rank_moves"):
            A("- Biggest rank moves:")
            for m in churn["biggest_rank_moves"]:
                arrow = "▲" if m["delta"] > 0 else ("▼" if m["delta"] < 0 else "—")
                A(f"    - {m['symbol']}: {m['prev_rank']} → {m['rank']} ({arrow}{abs(m['delta'])})")
    else:
        A(f"- {churn.get('note', 'unavailable')}")
    A("")

    A("## Watchlist spotlight (human overrides)")
    A("")
    overrides = watchlist.get("human_overrides") or {}
    coins = snapshot.get("coins", [])
    for sym in _ordered_overrides(overrides):
        rank = next((c.get("market_cap_rank") for c in coins if (c.get("symbol") or "").upper() == sym), None)
        loc = f"rank #{rank}" if rank else "not in current top set"
        A(f"### {sym} — {loc}")
        A(f"> {overrides.get(sym)}")
        A("")

    A("---")
    A("")
    A("> **Data, not narrative.** The tables above are facts from the snapshot (`as_of`-stamped). "
      "Narrative attribution — *why* something moved — is added separately by the Compiler with sourced "
      "URLs + A–E source grades (`crypto/analysis`, Part B1), never inferred from price alone. "
      "Recommendations live in `crypto/recommendations/` and are analytical arguments with an invalidation "
      "price + time-stop + position size, not orders. Posture: de-risk / observation-first.")
    return "\n".join(lines) + "\n"


# ── orchestration ─────────────────────────────────────────────────────────────

def run_crypto_top100(
    out_dir=Path("outputs"),
    data_dir=Path("crypto/data"),
    watchlist_path=Path("crypto/watchlist.yaml"),
    analysis_dir=Path("crypto/analysis"),
    *,
    today: Optional[str] = None,
    write: bool = True,
    opener=None,
    sleep=time.sleep,
    vs_currency: str = "usd",
    per_page: int = 100,
) -> dict:
    """Fetch → snapshot (or stale-fallback) → categorise → write analysis + handoff.

    All data inputs are injectable; a failed fetch degrades to the last good snapshot
    re-stamped with TODAY's ``as_of`` and flagged stale. Never raises on fetch failure.
    """
    now_iso = today or _utc_now_iso()
    date_str = now_iso[:10]
    watchlist = load_watchlist(watchlist_path)
    prev = latest_snapshot(data_dir)

    live_data = True
    stale: dict = {}
    try:
        coins = fetch_markets(vs_currency=vs_currency, per_page=per_page, opener=opener, sleep=sleep)
    except CoinGeckoError as exc:
        live_data = False
        if prev:
            coins = prev.get("coins", [])
            stale = {
                "stale_fallback": True,
                "stale_source_as_of": prev.get("as_of"),
                "stale_source_date": prev.get("as_of_date"),
                "error": str(exc),
            }
        else:
            coins = []
            stale = {
                "stale_fallback": True,
                "stale_source_as_of": None,
                "error": str(exc),
                "note": "fetch failed and no prior snapshot — empty snapshot emitted.",
            }

    snapshot = build_snapshot_envelope(
        coins, as_of=now_iso, as_of_date=date_str, vs_currency=vs_currency,
        live_data=live_data, stale=stale, source_per_page=per_page,
    )
    if write:
        write_snapshot(snapshot, data_dir)

    structure = market_structure(coins, watchlist.get("stablecoins"))
    categories = categorize(coins, watchlist.get("category_tags"), watchlist.get("stablecoins"))
    movers_24h = compute_movers(coins, "price_change_pct_24h", 10, max_rank=MAJORS_RANK_CUTOFF)
    movers_7d = compute_movers(coins, "price_change_pct_7d", 10, max_rank=MAJORS_RANK_CUTOFF)
    churn = rank_churn(snapshot, prev)
    handoff = build_handoff(snapshot, structure, movers_24h, movers_7d, categories, churn, watchlist)
    markdown = render_markdown(snapshot, structure, movers_24h, movers_7d, categories, churn, watchlist)

    if write:
        ad = Path(analysis_dir)
        ad.mkdir(parents=True, exist_ok=True)
        (ad / f"top100-{date_str}.md").write_text(markdown, encoding="utf-8")
        od = Path(out_dir)
        od.mkdir(parents=True, exist_ok=True)
        (od / f"crypto-top100-{date_str}.json").write_text(
            json.dumps(handoff, indent=2, default=str), encoding="utf-8"
        )
        print(
            f"wrote crypto top-{snapshot['count']} snapshot + analysis for {date_str} "
            f"(live_data={live_data})",
            file=sys.stderr,
        )
    return handoff


def main() -> int:
    run_crypto_top100()
    return 0


if __name__ == "__main__":
    sys.exit(main())
