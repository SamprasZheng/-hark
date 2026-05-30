---
type: source
source_class: principal_account_snapshot
source_grade: A
source_first_visible_at: 2026-05-29T21:56:00-04:00
ingested_at: 2026-05-29T23:15:00-04:00
author_role: human
account: taiwan_domestic_9A92-0316376
---

# Taiwan domestic broker (9A92-0316376) — snapshot 2026-05-29

Newly observed account, not previously captured in [[../../src/sharks/backtest/portfolio_audit]] PORTFOLIO_1 / PORTFOLIO_2. Taiwan-listed ETFs only (台股 tab), not 複委託.

Source: 證券 → 台股 screen, account 9A92-0316376, taken 2026-05-29 21:56 local.

## Holdings

| 代號 | 名稱 | 股數 | 參考市值 (TWD) | 獲利率 |
|---|---|---|---|---|
| 0056 | 元大高股息 | 270 | NT$13,390 | +33.85% |
| 00878 | 國泰永續高股息 | 197 | NT$6,007 | +39.34% |
| 00929 | 復華台灣科技優息 | 502 | NT$15,015 | +48.72% |
| 00965 | 元大航太防衛科技 | 174 | NT$4,377 | -0.21% |
| 00983A | 主動中信ARK創新 | 220 | NT$2,628 | +3.38% |

**Total**: NT$41,417 ≈ **$1,320 USD** (at 31.38 TWD/USD).

## Profile

- All five are Taiwan-listed ETFs (台股), not US ADRs and not 複委託-routed.
- Three high-dividend trackers (0056, 00878, 00929), one defence/aerospace thematic (00965), one ARK-Innovation-style active (00983A).
- Position size is small (~$1.3K USD) — call it a satellite / dividend yield experiment rather than a primary book.
- All five up significantly except 00965 — consistent with 2025-2026 Taiwan high-yield ETF run.

## Notes for audit refresh

- Add a third account container alongside PORTFOLIO_1 and PORTFOLIO_2 if you want this captured in the audit. Suggested name: `PORTFOLIO_TW` (or repurpose PORTFOLIO_2 if 複委託 / 台股 should be unified — but they're different brokerage accounts so keep separate).
- These tickers don't currently have entity coverage under `philosophy/entities/`. Taiwan-listed high-yield ETFs may not warrant per-entity pages — could be covered by a single `philosophy/concepts/taiwan-high-yield-etf-basket.md` synthesis.
