# crypto/ — Marketcap Top-100 tracker (state + content)

Daily cross-sectional crypto market tracking, compiled the $hark way:
**raw snapshot → human analysis → machine handoff**, every artifact `as_of`-stamped.
The *code* lives in `src/sharks/` (importable + tested); this folder holds *state and
content*.

## What runs

```powershell
# from the repo root, with the venv active (or via scripts/crypto_top100.ps1)
python -m sharks.scoring.crypto_top100
```

One run produces three point-in-time artifacts:

| Artifact | Path | Tracked? |
|---|---|---|
| Immutable raw snapshot (100 coins, normalised) | `crypto/data/top100-<DATE>.json` | gitignored (regenerated) |
| Human-readable structure analysis | `crypto/analysis/top100-<DATE>.md` | tracked |
| Machine handoff (structure / movers / churn) | `outputs/crypto-top100-<DATE>.json` | gitignored (like all `outputs/`) |

Data source: CoinGecko `/coins/markets` (free, no API key, stdlib `urllib` only — $hark
stays dependency-free). On a fetch failure the run **degrades**: it re-emits the last good
snapshot under TODAY's date with `live_data:false` / `stale_fallback:true` — it never
invents prices and never silently reuses an old date.

## Files

- `watchlist.yaml` — narrative map (`category_tags`), tiers, stablecoins, and the
  mandatory DOT / BTC `human_overrides`. A `---`-fenced doc so the persona frontmatter
  reader parses it without pyyaml. **Before editing, snapshot it to
  `watchlist_history/crypto-watchlist-<DATE>.yaml`** (tracked — point-in-time integrity).
- `data/` — daily raw snapshots (gitignored).
- `analysis/` — daily human analysis (tracked). Part B1 narrative attribution (the *why*,
  with sourced URLs + A–E grades) is added here by the Compiler, never inferred from price.
- `recommendations/` — disciplined argument files (Part B2): each pick carries an entry
  zone, single invalidation price, time-stop, position size, confidence, evidence — plus a
  mandatory **AVOID** bucket. Empty slots stay `null` (no padding).
- `dot-postmortem.md`, `cycle-and-institutional.md` — Part B living docs (written after the
  first live pull, data-driven).

## Guardrails (non-negotiable)

- **RECOMMEND-ONLY.** This system never trades. Order execution is a human action.
- **BTC ≤4% notional** — a *core macro* holding: mechanical DCA, hard ceiling, **OUTSIDE**
  the ≤5% Alpha sleeve (per `philosophy/06-exclusions.md`).
- **Alts ≤5% Alpha sleeve** — **SPOT ONLY**. No leverage / futures / margin / crypto-
  leveraged products. The personal Alpha-sleeve policy lives in the private `finance/`
  system; this repo cites it, never copies its numbers.
- **Posture: de-risk / observation-first.** Per `philosophy/concepts/btc-halving-cycle.md`
  the cycle model reads as a bear/Phase-D regime — "no new longs." The tracker's job is cold
  observation + de-risking discipline, not chasing.

See `docs/ROADMAP.md` for the deferred upgrades (CLI subcommand, ccxt weekend OHLCV,
on-chain metrics, `/coins/categories` auto-tagging, crypto-audit contract).
