# 開盤前艙位調整 — 2026-06-12(美股開盤前)

> recommend-only;系統只建議、永不下單。執行與否是人的決定。

## 1. 市場狀態:**mania**(QQQ 月線四態)
- 曝險規則:不加總曝險;移動停利收緊;新倉只准 DNA 可入候補(現=0 即不開)
- MC 至 2027 末:中位 26.1% · P(正) 83.2%(iid 低估尾巴,曝險跟狀態不跟點估計)

## 2. 持倉動作(健檢自動裁決)
- **清倉**:OPITQ
- **換股**:SMR→EXPD/CSX、MSFU→MSFT/CRDO、PTIR→PLTR/CRDO、CRMG→CRM/CRDO、LULG→LULU/ROST、INTU→CRDO/KLAC、SAFX→ROST/CRDO
- **減碼**:AMAT、APPS、PD、CRWG、AOSL
- **待驗證**:NXPX、APA
- **續抱⚠**:ADBE、VST、ZM、ORCL、UEC、RIVN、NTLA、ARRY、LPL

## 3. 持倉 × 反身性斷裂交集(最高優先警示)
- (無 — 持倉沒有踩在斷裂名單上)

## 4. 新倉紀律(DNA 雙濾鏡分桶)
- 可入候補(≥85):**0 檔 → 今日不開新倉**
- watch(≥75):SMCI(⚠近鄰失敗×1)、ESTC(🚩⚠近鄰失敗×2)、DXCM(🚩⚠近鄰失敗×3)、BLMN(⚠近鄰失敗×1)
- 剔除(斷裂):HUM
- sizing:deep-kill 袖上限 **11.0%**(資料驅動)· 單筆風險 ≤1-2% 總資本 · 樂透型=衛星倉,主倉走淺基型

## 5. 系統健康(audit/observability)
- deep-kill 存活率:**74.1%**(bootstrap 90% CI 71.2–77.0%) · 事件 n=664(下市票 0)
- 案例庫:60 成功 + 172 失敗類比
- 規則觸發統計(本批):{'deep-kill-sizing-cap': 19, 'axti-similar-failures': 12, 'break-hard-exclude': 1, 'pit-overrule-human-review': 1}
- 數據新鮮度:scan 2026-06-11 · rally-dna 2026-05-01 · reflexivity 2026-06-10

_generated 2026-06-12T06:53:20.620546+00:00_