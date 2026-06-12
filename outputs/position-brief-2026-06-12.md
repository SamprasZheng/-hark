# 開盤前艙位調整 — 2026-06-12(美股開盤前)

> recommend-only;系統只建議、永不下單。執行與否是人的決定。

## 1. 市場狀態:**mania**(QQQ 月線四態)
- 曝險規則:不加總曝險;移動停利收緊;新倉只准 DNA 可入候補(現=0 即不開)
- MC 至 2027 末:中位 26.1% · P(正) 83.2%(iid 低估尾巴,曝險跟狀態不跟點估計)

## 2. 全球風險(World Monitor)
- 觸發事件:**TS_HIGH**(high)、**GSCPI_SPIKE**(med-high)、**GPR_ELEVATED**(info)
- GSCPI 1.769(z 單位;≥1.5=尖峰)· GPR 184.2(基準~100;p95≈169/p99≈330)· 台灣分項 0.489(60月z 2.24;p95≈0.25)
- ABM 情境(週更):TS_HIGH 先驗 0.22 · 預期斷供 2.09 季 · deep-kill 折減 -0.21pp(TS_HIGH 條件式 -4.73pp;與 cap 乘數不疊乘)

## 3. 持倉動作(健檢自動裁決)
- **清倉**:OPITQ
- **換股**:SMR→CSX/EXPD、MSFU→MSFT/ASML、PTIR→PLTR/ASML、CRMG→CRM/ASML、LULG→LULU/LEVI、INTU→ASML/KLAC、SAFX→C/ASML
- **減碼**:AMAT、APPS、PD、CRWG、AOSL
- **待驗證**:NXPX、APA
- **續抱⚠**:ADBE、VST、ZM、ORCL、POET、UEC、NTLA、ARRY、LPL

## 4. 持倉 × 反身性斷裂交集(最高優先警示)
- AMAT

## 5. 新倉紀律(DNA 雙濾鏡分桶)
- 可入候補(≥85):**0 檔 → 今日不開新倉**
- watch(≥75):ESTC(🚩⚠近鄰失敗×2)、DXCM(🚩⚠近鄰失敗×3)
- 剔除(斷裂):HUM
- sizing:deep-kill 袖上限 11.0% × 0.75(世界事件 TS_HIGH、GSCPI_SPIKE、GPR_ELEVATED)= **8.2%**(資料驅動)· 單筆風險 ≤1-2% 總資本 · 樂透型=衛星倉,主倉走淺基型

## 6. 系統健康(audit/observability)
- deep-kill 存活率:**74.1%**(bootstrap 90% CI 71.2–77.0%) · 事件 n=664(下市票 0)
- 案例庫:60 成功 + 172 失敗類比
- 規則觸發統計(本批):{'axti-similar-failures': 12, 'deep-kill-sizing-cap': 17, 'world-gscpi-deepkill-caution': 17, 'world-ts-high-taiwan-review': 1, 'break-hard-exclude': 1, 'pit-overrule-human-review': 1}
- 數據新鮮度:scan 2026-06-11 · rally-dna 2026-05-01 · reflexivity 2026-06-11 · world 2026-06-12

_generated 2026-06-12T12:33:21.849249+00:00_