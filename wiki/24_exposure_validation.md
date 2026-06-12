---
type: synthesis
tags: [world-model, exposure, validation, research]
title: World Exposure Map 驗證 — 台鏈/光通訊/中國營收名單覆核
as_of_timestamp: 2026-06-12T19:00:00+08:00
author_role: researcher
source_paths: [config/world_exposure.json]
confidence: 0.7
---

# World Exposure Map 驗證(2026-06-12)

對 [[23_world_model]] §6.5 認列的技術債(「曝險地圖是專家先驗,未經驗證」)做第一輪
網路證據覆核。方法:taiwan_chain 20 檔逐檔查證(每檔 1 輪檢索,證據以公司自述/
SEC 文件/一線媒體為準);optics_cpo 與 china_revenue 低深度抽查。**本頁只提建議,
不改 `config/world_exposure.json`** — 變更由人類 + Risk Officer 裁決。

分類定義:**CONFIRMED-HIGH** = TSMC 投片或台灣組裝為核心產品命脈;**PARTIAL** =
有實質台灣曝險但分散(多為需求端營收);**WRONG** = 查無重大台灣依賴。

## 1. taiwan_chain 逐檔驗證(權重 0.9)

| Ticker | 分類 | 證據一行 | 來源 · 2026-06-12 |
|---|---|---|---|
| TSM | CONFIRMED-HIGH | 全部 GIGAFAB 與 >90% 產能在台灣本島 | [tsmc.com fab capacity](https://www.tsmc.com/english/dedicatedFoundry/manufacturing/fab_capacity) |
| NVDA | CONFIRMED-HIGH | 先進 GPU 幾乎全數 TSMC 代工,無同規模替代(Intel/SMIC 均不可行) | [trefis.com](https://www.trefis.com/stock/nvda/articles/583581/the-5-trillion-ai-risk-sitting-in-the-taiwan-strait/2025-11-21) |
| AMD | CONFIRMED-HIGH | fabless;CPU/GPU/客製 SoC 主力 TSMC,Lisa Su 自承正尋求分散 | [theregister.com](https://www.theregister.com/2023/07/24/amd_looks_beyond_tsmc/) |
| AVGO | CONFIRMED-HIGH | top-10 AI ASIC 晶圓代工 ~99% 在 TSMC;XPU 用 N3(台南 Fab 18B) | [indexbox.io](https://www.indexbox.io/blog/broadcom-tsmc-lead-2027-custom-ai-chip-market-says-counterpoint/) |
| ARM | **PARTIAL(建議降級)** | 純 IP 授權、不製造任何晶片;台灣曝險僅為下游權利金的二階效應 | [strategyzer.com](https://www.strategyzer.com/library/arm-business-model) |
| MU | CONFIRMED-HIGH | >65% DRAM 在台生產(台中/桃園,Inotera/Rexchip 廠);DRAM 僅台/日兩地 | [taipeitimes.com](https://www.taipeitimes.com/News/biz/archives/2023/09/11/2003806037) |
| AMAT | PARTIAL | FY2025 台灣營收 24%($6.86B)— 需求端;設備產地在美/新加坡 | [SEC 10-K](https://www.sec.gov/Archives/edgar/data/0000006951/000162828025056742/amat-20251026.htm) |
| LRCX | PARTIAL | FY2025 台灣營收 19% — 需求端,次於中/韓 | [SEC 10-K](https://www.sec.gov/Archives/edgar/data/707549/000070754925000085/lrcx-20250928.htm) |
| ASML | PARTIAL | 2025 各季台灣出貨佔 30–35%;製造在荷蘭 Veldhoven | [SEC 6-K](https://www.sec.gov/Archives/edgar/data/0000937966/000162828026003701/a2026_01x28xpresentation.htm) |
| KLAC | PARTIAL | FY2025 台灣營收 $3.21B(約 26%)— 需求端,次於中國 39% | [KLA 10-K](https://ir.kla.com/sec-filings/all-sec-filings/content/0000319201-25-000024/0000319201-25-000024.pdf) |
| ONTO | PARTIAL(偏高) | 台灣為最大單一市場:2024 全年 31%、2025Q1 38%(CoWoS 先進封裝檢測) | [nasdaq.com](https://www.nasdaq.com/articles/innovation-international-revenue-performance-explored) |
| SMCI | CONFIRMED-HIGH | 桃園園區 5 棟 28 萬 m²、目標年組裝 200 萬系統;製造僅美/台/荷三地 | [taipeitimes.com](https://www.taipeitimes.com/News/biz/archives/2021/06/03/2003758490) |
| COHR | **PARTIAL(建議移出)** | 收發器主力產地馬來西亞怡保(累計出貨 3 億顆)+越南;查無台灣直接產線 | [coherent.com](https://www.coherent.com/news/press-releases/manufacturing-milestone-300-million-transceiveres-shipped) |
| LITE | **PARTIAL(建議移出)** | 製造重心泰國(自有曼谷線 + Fabrinet 代工);查無台灣產線 | [yolegroup.com](https://www.yolegroup.com/industry-news/lumentum-to-ramp-transceiver-production-in-bangkok/) |
| SIVEF | **WRONG(建議移出)** | 自有 fab 在蘇格蘭 Glasgow(InP 100mm、5,000 wafer/年);無台灣製造依賴 | [sivers-semiconductors.com](https://www.sivers-semiconductors.com/company-history/) |
| AAOI | CONFIRMED-HIGH | 新北市 26.8 萬呎主力廠(產能 +110%);中國寧波廠 2022 年已議售;另有德州 | [ao-inc.com](https://investors.ao-inc.com/news-releases/news-release-details/applied-optoelectronics-moving-larger-manufacturing-facility) |
| MRVL | CONFIRMED-HIGH | fabless;先進製程主力 TSMC,以長約鎖定產能(AI/資料中心晶片) | [Marvell 10-K](https://investor.marvell.com/sec-filings/all-sec-filings/content/0001835632-25-000057/mrvl-20250201.htm) |
| ALAB | CONFIRMED-HIGH | 全產品線於 TSMC 製造;TSMC 為早期投資人 | [wikipedia](https://en.wikipedia.org/wiki/Astera_Labs)、[S-1](https://www.sec.gov/Archives/edgar/data/1736297/000119312524040419/d285484ds1.htm) |
| CRDO | CONFIRMED-HIGH | SerDes/IC 於 TSMC 12nm→N7/N5/N3 開發並量產 | [businesswire.com](https://www.businesswire.com/news/home/20250924583473/en/Credo-Launches-224G-PAM4-SerDes-IP-on-TSMC-N3-Process-Technology) |
| QCOM | CONFIRMED-HIGH(分散中) | 旗艦 Snapdragon 現於 TSMC;CES 2026 宣布重啟 Samsung 2nm 雙代工(2026 末量產) | [domain-b.com](https://www.domain-b.com/amp/technology/electronics/qualcomm-explores-2nm-chip-production-with-samsung-rekindles-dual-foundry-strategy) |

統計:CONFIRMED-HIGH 12 / PARTIAL 7 / WRONG 1。先驗名單方向大致正確,但把
**「TSMC 投片」與「賣設備給台灣」兩種曝險混在同一個 0.9 群組**是最大結構問題
(設備五檔台灣營收 19–38%,是需求端二階曝險,非產線斷供的一階曝險)。

## 2. 抽查結果

**optics_cpo(0.7)**:FN 製造全在泰國(Chonburi 等園區;NVIDIA 1.6T 收發器獨家組裝
夥伴)([beyondspx.com](https://www.beyondspx.com/quote/FN/fabrinet-the-precision-engine-powering-ai-s-optical-backbone-nyse-fn) · 2026-06-12)。
群組 `_doc` 寫「關稅+台海雙重暴露」— 對 FN/LITE/SIVEF 而言台海軸不成立(產地
泰/泰/蘇格蘭),關稅軸成立。權重 0.7 可留,`_doc` 建議改寫為「關稅+AI 光通訊
需求鏈;台海僅間接(DSP 晶片多為 TSMC 代工)」。無須除名。

**china_revenue(0.6)**:抽 2 檔皆成立 — TXN 出貨入中國約佔營收 50%(終端客戶
HQ 口徑約 20%,FY2025 10-K)([sec.gov](https://www.sec.gov/Archives/edgar/data/0000097476/000009747626000059/txn-20251231.htm) · 2026-06-12);
INTC 中國(含港)FY2024 營收 29.3%、為最大單一市場([bullfincher.io](https://bullfincher.io/companies/intel-corporation/revenue-by-geography) · 2026-06-12)。
其餘 10 檔未逐檔驗證(WYNN/LVS 的澳門依賴屬常識級,仍標 TBD)。無 clear error。

## 3. 遺漏候選(均已查證)

| Ticker | 理由一行 | 來源 · 2026-06-12 |
|---|---|---|
| AAPL | TSMC 為 Apple silicon 唯一代工(A10 起);最先進製程依台灣法規不得外移 | [macrumors.com](https://www.macrumors.com/2025/03/27/made-in-america-apple-chips-to-lag-behind-taiwan/) |
| ASX | 全球最大 OSAT(市占 ~19%),總部+主要產能在高雄 | [wikipedia](https://en.wikipedia.org/wiki/ASE_Group) |
| UMC | 台灣晶圓代工,總部新竹、12 吋主力 Fab 12A 在台南 | [umc.com](https://www.umc.com/en/About/about_overview) |
| ANET | 核心交換器矽片(Broadcom Jericho/Tomahawk)為 TSMC 5nm;CM 為 Foxconn/Celestica(組裝地未證實在台) | [nextplatform.com](https://www.nextplatform.com/2023/10/17/micas-takes-on-arista-and-the-whiteboxes-in-datacenter-switching/)、[10-K](https://www.sec.gov/Archives/edgar/data/0001596532/000159653224000043/anet-20231231.htm) |
| TER(次優先) | TSMC 為前五大客戶之一;中+台佔出貨約 30–40% — 屬需求端,與設備組同級 | [digitimes.com](https://www.digitimes.com/news/a20191216PD201.html)、[nanalyze.com](https://www.nanalyze.com/2024/11/can-teradyne-return-to-strong-growth/) |

前提:加入前先與 `watchlist/universe.yaml` 對帳(ASX/UMC 若不在可交易池,僅列
觀察)。AAPL 已在 china_revenue 0.6;因曝險取 max,加入 taiwan_chain 即升 0.9。

## 4. 建議 config 變更(不在本頁執行)

1. **移出 taiwan_chain**:SIVEF(WRONG)、COHR、LITE(製造在馬/越/泰)。三檔仍留
   optics_cpo → 有效曝險 0.9→0.7,非歸零。
2. **移出或降權 ARM**:純 IP,無產線;退 sector_base Technology 0.45,或留群組但
   個別降 0.5(需新增 per-ticker override 機制,成本較高 — 建議直接移出)。
3. **加入 taiwan_chain**:AAPL、ASX、UMC(CONFIRMED-HIGH 證據);ANET 以
   「矽片端依賴成立、組裝地 TBD」註記加入或交人裁。
4. **結構選項(交 Risk Officer)**:把 AMAT/LRCX/KLAC/ASML/ONTO(+TER)拆出成
   `taiwan_demand_equipment` 權重 0.6 — 它們的台灣營收 19–38% 是訂單遞延風險,
   與 NVDA「產品做不出來」不同階;現行 0.9×penalty 0.25 對設備組過罰。
5. **optics_cpo `_doc` 改寫**(見 §2);QCOM 留原位但每季覆核 Samsung 2nm 分流進度。

## 5. 同溫層缺口(誠實申報)

- **投片占比不可得**:各 fabless 在 TSMC 的實際 wafer 配比是非公開商業資訊;本頁
  以公司自述+一線媒體近似,無法量化「TSMC 佔該公司 COGS 幾 %」。
- **單一來源數字**:AVGO 的「~99%」出自 Counterpoint 一家(媒體互相轉引,AI 敘事
  高熱期同溫層風險);LRCX/ONTO/INTC 的地理營收比例經彙整站轉述,未逐字核對
  10-K 原文。
- **每檔僅 1 輪檢索**:反向證據(如 COHR 在台隱性產線、SIVEF 的台灣代工夥伴)
  若存在但不在首頁結果,會漏。
- **china_revenue 12 檔只抽 2 檔**;NKE/SBUX/TSLA/CAT/WYNN/LVS/MCHP/ADI/AAPL/QCOM
  維持先驗,標 TBD。
- 後續:以 `polygon_financials`(filing_date 錨)做 10-K 地理營收的機器化抽驗
  ([[23_world_model]] §6.5 原計畫),取代本頁的人工檢索口徑。

## See also

- [[23_world_model]] — 被驗證的曝險地圖所屬感測層
- [[../philosophy/09-point-in-time]] — config 為 git 版控,改名單即留 vintage
- [[../philosophy/08-risk-and-position]] — 群組權重變更需 Risk Officer 覆核
