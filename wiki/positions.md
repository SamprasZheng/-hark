---
type: synthesis
tags: [positions, open, invalidation, live]
title: Open Positions and Thesis State
status: live
as_of_timestamp: 2026-06-11T16:00:00-04:00
author_role: compiler
source_paths:
  - raw/principal/2026-06-11-snapshot-p1.md
  - raw/principal/2026-06-11-snapshot-8840.md
confidence: 0.85
---

# Open Positions — P1(US 直券 "Individual")

> as_of **2026-06-11 美股收盤**(截圖 2026-06-12 10:21 TPE)。可見部位小計 ≈ **$6,696**;
> 清單在 ~$202 截斷、現金不可見 → 視為**下限快照**。機器可讀版:
> `src/sharks/backtest/portfolio_audit.py::PORTFOLIO_1`。P2(複委託)未重新截圖,
> 仍為 2026-05-30 基準。

| Ticker | Mkt Val | Day % | 槓桿 | 註 |
|---|---|---|---|---|
| IGV | $1,278.56 | −0.40% | — | 軟體 ETF — 最大持倉(19.1% 可見) |
| SIVEF | $891.00 | +12.08% | — | Sivers Semiconductors(STO:SIVE 的 OTC F 股)— [[../philosophy/entities/sivers-semiconductors]];6/11 +12% = GlobalFoundries 合作催化 |
| HPQ | $503.03 | +0.16% | — | |
| ALGM | $482.00 | +8.22% | — | 也在 P2 |
| CRWG | $396.88 | +3.04% | 2x CRWV | |
| ZM | $370.60 | −1.39% | — | 也在 P2 |
| MSFU | $360.19 | −2.38% | 2x MSFT | |
| PTIR | $324.55 | +1.67% | 2x PLTR | |
| CRMG | $315.09 | −4.07% | 2x CRM | |
| DDD | $302.37 | +4.63% | — | |
| ENPH | $280.00 | +10.74% | — | |
| LULG | $278.00 | +1.46% | 2x LULU | |
| INTU | $277.75 | −2.28% | — | |
| ARRY | $223.51 | +9.00% | — | |
| NXPX | $210.00 | +13.42% | ?(疑 2x NXPI) | **TBD 待驗證** |
| APA | ~$202.5 | 紅 | — | 截斷列推定,待確認 |

## 結構讀數(Compiler 觀察,非裁決)

- **槓桿單股 2x 佔可見部位 ≈28%**(CRWG/MSFU/PTIR/CRMG/LULG,+NXPX 若證實則 31%+)。
  舊槓桿(TARK/LABU/SBIT/NOWL/AAPB/RBLU)已出 — 與 06-07 指令一致 — **但換了一批新標的
  重新上槓桿**。[[../philosophy/08-risk-and-position]] 的 alpha-sleeve 不留槓桿紀律
  與這個結構衝突,須 Risk Officer 重審(audit 引擎會出 per-holding verdict)。
- IGV+SIVEF 兩檔 = 32% 可見部位。SIVEF 已解碼(principal 2026-06-12):Sivers Semi,
  論點 = CPO 外部光源(ELS)咽喉點([[../philosophy/entities/sivers-semiconductors]])。
  注意:~$130M 微型股 + OTC F 股流動性 — 13% 可見部位的集中度本身是風險點。
- 每檔的 invalidation triggers 尚未按本頁 schema 補齊(entry/catalyst/triggers TBD —
  這批是 06-07 之後重建的倉,principal 尚未提供進場價與論點)。

---

# Open Positions — P2(複委託 8840,Fubon)

> as_of **2026-06-11 美股收盤**(3 截圖,字母序完整帳本)。**24 檔,合計 ≈ $9,482**
> (OPITQ 計 0)。市值 = 現價 × 股數;成本欄截斷,僅近似。機器可讀版:
> `portfolio_audit.py::PORTFOLIO_2`。完整表:[[../raw/principal/2026-06-11-snapshot-8840]]。

前五大:ADBE $1,094、CPNG $863、VST $732、AMAT $553、RDW $513。
主題分布:AI 半導體(AMAT/ARM/AOSL)、電力/核能/鈾(VST/SMR/UEC)、太空(RDW)、
光子(POET)、超跌軟體(ADBE/PD/ZETA/APPS/NOW)、EV/鋰(RIVN/LAC)。

P2 結構讀數:
- **OPITQ $0(1,000 股,破產殼)→ 稅損收割候選**(portfolio/04_long_range_tax_plan)。
- 無槓桿 ETF(P2 乾淨);最大單檔 ADBE 11.5%,集中度可。
- VST 同時在 daily-reco Tier A 埋伏名單(已持 5 股 = 論點已有部位,加碼仍走啟動信號)。
- ⚠ audit 舊 P2 清單(ZM/PEP/DIS…26 檔)與本帳本幾乎無交集 — 已被取代;
  舊清單出處(疑另一容器)待 principal 釐清。

## Expected entry format per position(schema,未變)

```
## NVDA — long_new — 2026-05-28T20:00:00-04:00

**Strategy**: A (consolidation-breakout)
**Tier / Bucket**: tier1_mag7 / 3m
**Size**: 4.0% of portfolio
**Entry zone**: $458 – $472
**Thesis / Catalyst / Invalidation triggers / Evidence paths / Followup log**: …
```

## Discipline reminders

- A position MUST declare all three invalidation triggers
- A position with `catalyst` field empty is **invalid** and rejected by Risk Officer
- "Hold through earnings without action" is not allowed — every earnings event forces a re-rate per [[../philosophy/08-risk-and-position]]
- Comparison-driven trims trigger a [[../philosophy/concepts/separation-mind]] flag and require Risk Officer review

## See also

- [[../philosophy/05-decision-rubric]] — daily followup slots
- [[../philosophy/08-risk-and-position]] — invalidation contract
- [[../portfolio/index]] — 全容器(RSU/台股/複委託)總覽
