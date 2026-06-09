---
type: synthesis
tags: [portfolio, liquidity, tiers, flex-buffer, holdings, tax-loss-harvest, private]
title: 倉位重整 — 實際持倉(11 張截圖消化)+ 流動性分層
as_of_timestamp: 2026-05-31T00:00:00+08:00
status: live
schema_version: 1
---

# 倉位重整(實際持倉)

> 來源:`finance/portfolio/` 11 張截圖(2026-05-30,參考市值,點時間)。**財務/流動性角度**消化;**交易決策仍以 `$hark` 為準**(FOM/rubric/exclusions),本頁不重複。
> 現金:台幣 **NT$86,000**;其餘幾乎全是股票。匯率 @31.38。

## §1. 容器總覽(比記憶多!揭露 5 個容器)

| 容器 | 約略市值 | 角色 | 觀察 |
|---|---|---|---|
| **NVDA RSU/ESPP**(員工портal,未截圖) | ~$130K ≈ **NT$4,079K** | 鎖定核心 | 占總曝險 ~87%(見 [[../05_equity_monetization_schedule]]) |
| **US 直券 P1(Individual)** | ~$11.4K ≈ **NT$357K** | 主動槓桿+現股 | ~37 檔,槓桿單股 ETF 為主 |
| **複委託 8840(Fubon,teal app)** | TBD(小) | 主題現股籃子 | 11 檔,僅見股數無市值 |
| **證券 app — 台股 9A92** | **NT$42,325** | **高股息存股** | 0056/00878/00929 等,+35~50% |
| **證券 app — 複委託(美股)** | ~$1,880 ≈ **NT$59K**(活的部分) | 投機殘骸 | 多檔 −90~−100%(見 §5)|
| **證券 app — 海外定時定額** | **NT$19,314** | 藍籌 DCA(=「其他小存股」)| GOOG/TSLA/NFLX |
| **台幣現金** | **NT$86,000** | Tier 0 | 7 天日常扣款 |
| **合計(ex-RSU)** | ~**NT$563K** + 8840 | | NVDA RSU 仍壓倒性 |

## §2. US 直券 P1(Individual,~$11.4K)

槓桿單股 ETF(多列 `$hark` SELL):TARK $1,515、LABU $585、AAPB $399、NOWL $469、LULG $336、RBLU $214、QSU $209、TSLL $158、OKLL $178、ONDU $147。
現股/品質:HPQ $551、CRSR $484、ALGM $476、SBIT $476、ENPH $340、STZ $203、AMPX $202、SWKS $197、PG $197、PEP $196、UAA $179、VFC $174、CRM $215、LULU $209、CRCT $208、APA $207、NKE $205、TSLA $205、VSCO $276、ARRY $273、RUN $101、WOLF $59、MRNA $54、NOK $149。
**塵粉(<$10,可清):** CRWD $8.8、DDOG $8.6、WDAY $8.5、XYZ $7.8、WDC $7.7、NXPI $7.7、MSFT $7.7。

## §3. 複委託 8840(Fubon)— 僅股數(市值待補)

AOSL 3、BLDP 100、HPQ 40、LG Display ADR 30、Intellia(NTLA)20、**Office Properties(OPI)1,000**、Oracle 2、Rivian 20、**XCF Global 500**、Turtle Beach 30、Uranium Energy(UEC)30。
> ⚠ 待補市值(此 app 只顯示股數)→ [[../context/assumptions-and-inputs]] §4。

## §4. 台股 9A92(NT$42,325)— 你的「存股 dividend sleeve」

| ETF | 股 | 市值 | 獲利 |
|---|---|---|---|
| 0056 元大高股息 | 270 | 13,503 | +34.98% |
| 00929 復華台灣科技優息 | 502 | 15,151 | +50.07% |
| 00878 國泰永續高股息 | 197 | 6,044 | +40.20% |
| 00965 元大航太防衛科技 | 177 | 4,484 | +0.45% |
| 00983A 主動中信ARK創新 | 261 | 3,143 | +3.56% |

> 這就是 [[../04_long_range_tax_plan]] §8 講的國內高股息現金流;**已在做、且都正報酬**。

## §5. 🩹 稅務虧損收割清單(高價值)

證券-app 複委託有一堆 −90~−100% 的死部位。**這些是已可實現的「海外財產交易損失」,在你有大筆 NVDA 賣出利得的年度,同年實現可抵減海外所得(AMT 計算)**——見 [[../04_long_range_tax_plan]]:

| 標的 | 股 | 市值 | 跌幅 |
|---|---|---|---|
| 中國恒大 | 40,000 | HKD 0 | −100% |
| Fisker(FSRNQ) | 2,000 | $0 | −100% |
| Farfetch(FTCHQ) | 270 | $0 | −100% |
| Green Giant(GGEI) | 2,000 | $0.2 | −99.94% |
| MMTE | 5 | $2.6 | −99.62% |
| NU Ride(NRDE) | 13 | $29.25 | −92.92% |
| LCDL(2x LCID) | 40 | $37.86 | −91.74% |
| Beyond Meat(BYND) | 50 | $39.43 | −88.69% |
| PYPG(2x PYPL) | 20 | $111.71 | −64.92% |

死部位(恒大/Fisker/Farfetch/GGEI/MMTE)幾乎 $0 → **賣掉清乾淨無損失、且無 wash-sale 顧慮**(不會買回)。**行動**:在大額賣 NVDA 的年度,同年一起實現這些損失抵稅。
（活的部分:AAPB $803.54、WOLF $592.8、MARA $143.8、ICLN $117.85、SPY $2.43。）

## §6. 海外定時定額(NT$19,314)=「其他小存股」

GOOG NT$6,495(+8.25%)、TSLA NT$11,846(+7.69%)、NFLX NT$973(−2.7%);另 BRK.B/DIS/HD/JPM/META/WMT 已設定但目前 TWD 0。→ 這就是你說「尚未列入」的小存股,**已列入**。

## §7. 流動性分層 + 缺錢規則

| Tier | 內容 | 動用規則 |
|---|---|---|
| **0 現金** | 台幣 86,000 | 未來 7 天扣款 |
| **1 鎖定** | NVDA RSU/ESPP ~$130K | **禁日常變現**;僅窗口期強制變現(稅/房/大額債)→ [[../05_equity_monetization_schedule]] |
| **2 主力** | US P1 現股品質股 + 台股 9A92 高股息 | 高股息續抱(現金流);P1 槓桿 ETF 依 `$hark` 重整 |
| **3 彈性緩衝** | 海外定時定額藍籌(GOOG/TSLA/NFLX)+ P1 部分變現性高的小倉 | **缺錢調節閥** ↓ |

> **缺錢規則**:Tier0 現金 < **NT$30,000** 且未來 7 天有大額扣款 → 先減 **Tier 3**(藍籌 DCA / 流動性高小倉),**不動 NVDA、不破房/債/稅排程**。死部位($0)不能當緩衝(賣了拿不到錢),只能拿來抵稅(§5)。

## §8. 顧問觀察(誠實)

1. **碎片化嚴重**:5 個容器、~60+ 檔,大量 −90% 槓桿單股 ETF 與死部位。**注意力與資金被稀釋**——和你「精力稀缺」的現實衝突。
2. **建議方向(交給 `$hark` 執行)**:① 清死部位(順便抵稅);② 縮槓桿單股 ETF(TARK/LABU/AAPB/NOWL/… `$hark` 多列 SELL);③ 保留台股高股息(現金流);④ 整併到少數高信念部位。
3. **這些加總 ex-RSU 僅 ~NT$56萬**,相對 RSU 4,079K + 債 400萬是小數 → **真正的槓桿仍是 RSU 排程 + 還債,不是這裡的再平衡**。

## 待補
- [ ] 複委託 8840 各檔市值(只見股數)。
- [ ] 設定 Tier0 安全下限(預設 30,000)。
- [ ] 與 `$hark` 對齊清死部位 + 縮槓桿 ETF 的賣出清單。

## See also
- [[../05_equity_monetization_schedule]] · [[../04_long_range_tax_plan]](§5 抵稅)· [[../daily-log/README]] · [[../context/assumptions-and-inputs]]
- `$hark`(交易決策 source of truth)
