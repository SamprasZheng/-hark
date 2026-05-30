---
type: synthesis
tags: [personal-finance, rsu, espp, monetization, sell-schedule, concentration]
title: 股權變現排程 — RSU/ESPP「預設變現機器」+ 到 $hark 的橋
as_of_timestamp: 2026-05-30T00:00:00-04:00
author_role: compiler
status: live
schema_version: 1
---

# 股權變現排程(預設變現機器)

> **不看盤決定賣不賣。** 每筆 vest/ESPP 先賣掉「強制變現額」餵飽房/債/稅,剩下的才談進攻。
> 消除「等反彈」的心理偏誤——這正是把房/債/稅變成**固定排程**的執行層。

## §1. 🔒 硬規則:強制變現公式

每筆 vest / ESPP,**先賣這些(以台幣計、再換算股數)**:

```
強制變現 = 預留稅款
         + 未來 6 個月現金流缺口
         + 下一筆到期房款(攤提)
         + 當季還債目標
```

賣完強制額後的**剩餘股票**,才有三條出路(優先序見 §4):
1. 續抱 NVDA(推進降集中度進度)
2. 換股進 $hark(P1/P2,依 rubric)
3. 進 Alpha sleeve(**受 [[06_cashflow_offense_and_guardrails]] 的 ≤5% 上限約束**)

> 現階段債務高 → 強制額幾乎吃掉整筆 vest,Alpha 分到的很少。**這是刻意的**:進攻只動用真正多餘的錢。債務下降後,剩餘自然變多。

## §2. 變現日曆(@31.38;股數/金額待你確認「已 vested 可動用」數)

RSU 截圖(2026-05-30,gross vest market value;US 預扣後淨額較低):

| 窗口 | 類型 | 股數(gross) | Gross 市值(USD) | ≈ TWD | 你的套現上限(你說) |
|---|---|---|---|---|---|
| 2026-06(6/17) | RSU | 76 | $16,148 | NT$507K | — |
| 2026-08 | ESPP | TBD | ~$16,000 | ~NT$502K | **~50萬** |
| 2026-09 | RSU | 59 | $12,536 | NT$393K | ~45–50萬 |
| 2026-12 | RSU | 59 | $12,536 | NT$393K | ~45–50萬 |
| 2027-02 | ESPP(成本 $97) | TBD | ~$16,000 | ~NT$502K | **~50萬** |
| 2027-03 | RSU | 59 | $12,536 | NT$393K | ~45–50萬 |
| 2027-06 | RSU | 59 | $12,536 | NT$393K | ~45–50萬 |
| 2027-09 | RSU | 43 | $9,137 | NT$287K | |
| 2027-12 | RSU | 42 | $8,924 | NT$280K | |

> **稅性提醒**(見 [[04_long_range_tax_plan]]):RSU **vest 當天賣** → capital gain≈0;ESPP(成本 $97)賣出 → 海外所得增加最多,緊盯 750萬線。

## §3. 強制變現 worked example(下一筆:2026-06 / 2026-08)

各項待 [[01_financial_profile]] 數字補齊;先放結構與佔位:

| 項目 | 估算 | 來源 |
|---|---|---|
| 預留稅款 | TBD(同日賣 capital gain≈0;主要為綜所稅缺口攤提) | [[04_long_range_tax_plan]] |
| 6 個月現金流缺口 | ~25K × 6 ≈ **NT$150K**(待確認缺口) | [[01_financial_profile]] §3 |
| 下一筆房款攤提 | 2027Q4 的 55萬 ÷ ~6 季 ≈ **NT$92K/季** | [[03_house_funding_plan]] |
| 當季還債目標 | **TBD**(建議鎖定一個季度砍本金額) | [[02_debt_and_consolidation]] |
| **強制變現合計** | **≈ NT$342K + 還債目標 + 稅** | |

→ 以 2026-08 ESPP ~50萬 為例:強制額吃掉大部分,**剩餘極少 → Alpha 這季幾乎不分**。完全符合「先房/債/稅」。

## §4. 賣出後分配瀑布(嚴格優先序)

1. **預留稅款** → 獨立放著,不花。
2. **6 個月現金流缺口** → 生活戶(止血)。
3. **下一筆房款攤提** → **SGOV 房屋頭期戶**(鎖定,永不交易,見 [[03_house_funding_plan]] §5)。
4. **當季還債目標** → 砍**最高利率**那筆本金([[02_debt_and_consolidation]] §6)。
5. **剩餘(若有)** → 續抱 / 換股進 $hark / Alpha sleeve(≤5%)。

## §5. 降集中度路徑(沿用 [[../12_employee_concentration]] §3)

| 時間 | NVDA 占可動用曝險目標 |
|---|---|
| 現在 | ~80%(可動用口徑) |
| 2026 H2 連續 vest 後 | 65–70% |
| 2027 Q1 | **50%** |
| 2027 Q4(房款前) | **40%** |

> 注意兩種口徑:含未來未 vested 的「總曝險」 vs 只算已 vested 的「可動用」。報告時標清楚,避免數字漂移。

## §6. 與 $hark 的分工(重要界線)

- **本頁只排程「賣多少、何時、為何(房/債/稅)」**,以及降集中度節奏。
- **不建議買哪支、不代下單、不搬錢。** 賣出後若要「換股」,買進標的交給 $hark 的 audit / decision rubric / exclusions(見 [[../../philosophy/05-decision-rubric]]、[[../12_employee_concentration]] §6)。
- Alpha sleeve 的紀律(上限、停損、禁用工具)在 [[06_cashflow_offense_and_guardrails]]。

## See also

- [[06_cashflow_offense_and_guardrails]] — Alpha sleeve 上限 + 停損
- [[04_long_range_tax_plan]] — 每筆賣出登錄 ledger
- [[03_house_funding_plan]] — SGOV 房屋戶撥款
- [[02_debt_and_consolidation]] — 當季還債目標
- [[../12_employee_concentration]] — 集中度母頁
