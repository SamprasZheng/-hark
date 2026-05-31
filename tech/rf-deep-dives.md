---
type: synthesis
domain: tech-trend
tags: [rf, merger-arb, qorvo, skyworks, globalfoundries, tower, rf-soi, silicon-photonics, foundry, deep-dive]
as_of_timestamp: 2026-05-31T23:55:00+08:00
author_role: researcher
confidence: 0.72
parent: "[[rf-connectivity]]"
sources_grade_summary: "A: 8 B: 9 C: 6 D: 1 E: 0"
phase: D
---
# RF 深掘:QRVO+SWKS 合併套利 × GFS vs TSEM Foundry 旋轉 / RF Deep-Dives

> [[rf-connectivity]] 的兩個二階深掘。Principal 點名要的。Research/educational,**非買賣建議**;價格為 2026-05-29 收盤。

## A. QRVO + SWKS 合併套利 — 「監管賠率賭注」,不是乾淨套利

**條款(primary: Qorvo DEFM14A / 8-K / 425):** SWKS 為存續方,每股 QRVO 換 **$32.50 現金 + 0.960 SWKS 股**(固定比例,**無 collar**——QRVO 持有人承擔 SWKS 全部價格風險);合併後 SWKS ~63% / QRVO ~37%。雙方股東已於 **2026-02-11 通過**。公司終止費 **$298.7M**;反壟斷反向費 **$100M**;outside date **2027-04-27**(可延至 2027-10-27)。QRVO **已暫停財測與法說**;季內 SWKS 支持 QRVO $400M 回購。

**套利數學(2026-05-29 收盤):**
| 項 | 數 |
|---|---|
| QRVO / SWKS 收盤 | **$103.56 / $77.85** |
| 成交價值/QRVO股 = 32.50 + 0.960×77.85 | **$107.24** |
| Gross spread = (107.24−103.56)/103.56 | **+3.55%**(~$3.68/股) |
| 年化(假設 2027-03-31 完成,306 天) | **≈4.2%**(滑到 outside date ≈3.9%;若「2026 末」≈6.0%) |
| Break 下檔(QRVO standalone $66–92) | **−11%(回 $92)~ −36%(Mizuho $66)**;中值 $80 = **−22.8%** |
| 風險/報酬比(上行 vs break 下檔) | **0.10 ~ 0.32 → 約 3:1 至 10:1 對你不利** |
| 市場隱含完成機率 | **~87%**(中值下檔反推) |

**判讀:** 這是**高完成機率才划算的賭注** —— 你冒 11–36% 的 break 下檔,只賺 ~3.6%。**真正的搖擺不是 FTC(Second Request 2026-02-05,通常可滿足),是中國 SAMR Phase II** —— 兩家都重度依賴 Apple-China RF 供應鏈,SAMR 近年有 slow-walk/否決美系半導體併購的前科(Intel 併 Tower 即死於此)。**這不是「便宜買 QRVO」的理由,是一個 ring-fenced、押「SAMR 會放行」的事件部位**;且 QRVO 暫停財測 → break 當天 air-pocket 會更猛。一筆 grade-D 來源稱 FTC 已提告,**primary filing 無法佐證,勿信**。

## B. GlobalFoundries (GFS) vs Tower (TSEM) — 誰是更乾淨的「AI + RF 雙押」

問題拆成兩個市場定價極不同的賭注:**GFS = 多元規模 foundry + 光子選擇權**;**TSEM = 已變成矽光子的槓桿型買權**。

| 指標 (cal Q1'26) | **GFS** | **TSEM** |
|---|---|---|
| 營收 / YoY | $1.634B / **+3.1%** | $413.6M / **+15%** |
| 毛利(非IFRS/GAAP) | 29.0% / 27.6% | ~26.8%(2028 模型目標 39%) |
| SiPho / AI | ~$400M 2026(~5–6% 營收),**>$1B run-rate 出 2028**;設計進前四大 pluggable 的 3 家;客戶 NVDA/AVGO/Cisco/MRVL/Lightmatter | **$1.3B 已簽約 2027 SiPho + $290M 預付**;SiPho +3× YoY、產能 end-2026 ×5;光收發器 SiGe+SiPho #1 |
| RF-SOI | 300mm RF-SOI 先行(9SW/45nm);手機段一部分,Smart Mobile **−4.8%** | **#1 merchant RF-SOI 手機 FEM**;但 FY26 **指引向下**(200→300mm 轉換),2027–28 才回 |
| 2028 模型 | AI 為主成長;SiPho >$1B run-rate | **$2.8B 營收 / $750M 淨利 / 39% GM** |
| 淨現金 / 補貼 | ~$2.1–2.6B;CHIPS $1.5B + 量子 $375M | ~$1.4B;Intel(NM 300mm)+ ST(Agrate)租戶 |
| 估值 | fwd P/E ~40–46×、EV/S **~6.1×**、EV/EBITDA ~18–20× | fwd P/E ~67–94×、EV/S **~16.9×**、EV/EBITDA ~51× |

**判決:**
- **嚴格技術/槓桿讀:TSEM 是更純的「AI + RF 雙押」** —— RF-SOI(手機 FEM)#1 + SiPho/SiGe(光收發)#1,且有**全業界唯一現金預付的 AI 光子 backlog**($1.3B/2027)。要「業務本身最純粹同時是 RF 護城河 + AI 光子」就是 TSEM。
- **但作為投資、按估值與時機:GFS 是更乾淨的風險調整後雙押** —— 同樣兩個終端(RF-SOI 300mm 領先 + 進前三大的 SiPho),只付 **~1/3 的營收倍數**,且有 **10× 的 EBITDA 基數、淨現金+CHIPS 補貼、真實的資料中心段(14%、+32%)** → AI 光子上行近乎「免費選擇權」掛在獲利、多元的 foundry 上。TSEM 的 SiPho 成功**已被股價預付**(+20% 單日跳到歷史高),且其 RF 腿在 2026 是 down-year(雙押是「SiPho 現在、RF 2027」的序貫,非並進)。
- **TSEM 完勝的條件**:若 AI 光子如預付所示複利 **且** RF-SOI 手機 2027–28 設計案回來,則 2028 模型偏保守、SiPho 主導再 re-rate,**對這條 RF→SiPho 旋轉的百分比槓桿無人能及**——此時 GFS 的多元化反而**稀釋**了你想押的旋轉。
- **一句話**:要**有安全邊際的雙押 → GFS**;要**最大、合約背書的 SiPho 曝險且能忍 RF 腿是 2027 故事、估值是 2028 故事 → TSEM**。兩者 2026-05 都已 re-rate,倍數含動能溢價,冷靜盤再進。

## See also
- [[rf-connectivity]] — 母頁(RF=anti-bubble,成長已遷徙)· [[semiconductor-industry-map]] — foundry 在第 5 關
- [[optical-interconnect-cpo]] / [[optical-supply-chain-deep]] — SiPho 下游(GFS/TSEM 賣給誰)
