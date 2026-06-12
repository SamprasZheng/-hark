"""DefiLlama stablecoins client — stdlib, dependency-free on-chain liquidity proxy.

Pulls the aggregate stablecoin circulating supply from DefiLlama's KEYLESS JSON
endpoint ``https://stablecoins.llama.fi/stablecoins?includePrices=true``. This is
the on-chain analog of the macro "water level" (cf. the FRED liquidity fishbowl):
stablecoin supply expanding = fresh USD entering crypto; contracting = USD
leaving. It is the genuinely keyless, stdlib-fetchable on-chain signal — unlike
Polkadot Coretime (Subscan needs a key; public RPC needs SCALE decoding), which
is deferred to a v2.

``urllib`` only (no ``requests``), same retry/backoff discipline as
``data/coingecko_client.py``: 429 honours ``Retry-After``; 5xx + transport back
off; a non-429 4xx is fatal; exhaustion raises :class:`DefiLlamaError` so the
caller can fall back and flag the column stale — never invents a number.

Context: this feeds a PROTOTYPE observation column on the crypto Top-100 snapshot.
Crypto is ring-fenced (BTC ≤4% outside the ≤5% Alpha sleeve; alts ≤5% spot-only;
observation-first) — it is not a trading driver.
"""

from __future__ import annotations

import json
import time
import urllib.error
import urllib.request
from typing import Optional

DEFILLAMA_STABLES = "https://stablecoins.llama.fi/stablecoins?includePrices=true"
DEFAULT_USER_AGENT = "sharks-crypto-tracker/0.1 (+https://github.com/SamprasZheng)"

# Cap the per-asset breakdown so the immutable snapshot does not bloat.
_BY_ASSET_TOP_N = 10


class DefiLlamaError(RuntimeError):
    """Raised when stablecoin data cannot be fetched after exhausting retries."""


def _retry_after_seconds(exc) -> Optional[float]:
    hdrs = getattr(exc, "headers", None) or getattr(exc, "hdrs", None)
    if hdrs is None:
        return None
    try:
        val = hdrs.get("Retry-After")
    except Exception:
        return None
    if val is None:
        return None
    try:
        return float(val)
    except (TypeError, ValueError):
        return None


def _request_json(
    url: str,
    *,
    opener=None,
    max_retries: int = 4,
    timeout: float = 30.0,
    base_backoff: float = 1.5,
    sleep=time.sleep,
):
    """GET ``url`` → parsed JSON, retrying on 429 / 5xx / transport / non-JSON.

    ``opener`` is injectable (defaults to ``urllib.request.urlopen``). Raises
    :class:`DefiLlamaError` when retries are exhausted.
    """
    opener = opener or urllib.request.urlopen
    last_err = None
    for attempt in range(max_retries):
        req = urllib.request.Request(
            url, headers={"User-Agent": DEFAULT_USER_AGENT, "Accept": "application/json"}
        )
        try:
            with opener(req, timeout=timeout) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            if exc.code == 429:
                last_err = "http 429 (rate limited)"
                delay = _retry_after_seconds(exc)
                if delay is None:
                    delay = base_backoff * (2 ** attempt)
            elif 500 <= exc.code < 600:
                last_err = f"http {exc.code}"
                delay = base_backoff * (2 ** attempt)
            else:
                raise DefiLlamaError(f"DefiLlama HTTP {exc.code} for {url}") from exc
        except (urllib.error.URLError, TimeoutError) as exc:
            last_err = f"transport ({getattr(exc, 'reason', exc)})"
            delay = base_backoff * (2 ** attempt)
        except json.JSONDecodeError as exc:
            last_err = f"non-json response ({exc})"
            delay = base_backoff * (2 ** attempt)
        if attempt < max_retries - 1:
            sleep(delay)
    raise DefiLlamaError(
        f"DefiLlama fetch failed after {max_retries} attempts ({last_err}): {url}"
    )


def normalize_stablecoins(payload: dict, *, as_of: Optional[str] = None) -> dict:
    """Reduce a DefiLlama ``/stablecoins`` payload to the USD-pegged aggregate. Pure.

    Sums each asset's ``circulating.peggedUSD`` (USD-pegged supply only — the
    crypto-native USD water level). Missing / non-numeric values are skipped, never
    invented. Returns ``total_circulating_usd = None`` if nothing parseable.
    """
    assets = payload.get("peggedAssets") if isinstance(payload, dict) else None
    if not isinstance(assets, list):
        raise DefiLlamaError("unexpected DefiLlama payload (no peggedAssets list)")
    total = 0.0
    count = 0
    by_asset: dict[str, float] = {}
    for a in assets:
        if not isinstance(a, dict):
            continue
        circ = a.get("circulating")
        usd = circ.get("peggedUSD") if isinstance(circ, dict) else None
        if isinstance(usd, (int, float)) and not isinstance(usd, bool):
            total += usd
            count += 1
            sym = (a.get("symbol") or "").upper()
            if sym:
                by_asset[sym] = by_asset.get(sym, 0.0) + usd
    top = dict(sorted(by_asset.items(), key=lambda kv: kv[1], reverse=True)[:_BY_ASSET_TOP_N])
    return {
        "total_circulating_usd": round(total, 2) if count else None,
        "by_asset": top,
        "asset_count": count,
        "source": "defillama",
        "as_of_timestamp": as_of,
        "source_first_visible_at": as_of,
    }


def fetch_stablecoin_supply(
    *,
    as_of: Optional[str] = None,
    base_url: str = DEFILLAMA_STABLES,
    opener=None,
    sleep=time.sleep,
    max_retries: int = 4,
    timeout: float = 30.0,
) -> dict:
    """Fetch the aggregate USD-pegged stablecoin supply. Raises
    :class:`DefiLlamaError` only when retries are exhausted (caller decides
    fallback). ``as_of`` is stamped onto the result for point-in-time provenance.
    """
    payload = _request_json(
        base_url, opener=opener, sleep=sleep, max_retries=max_retries, timeout=timeout
    )
    return normalize_stablecoins(payload, as_of=as_of)
