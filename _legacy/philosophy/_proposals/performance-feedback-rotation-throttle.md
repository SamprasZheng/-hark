---
type: concept
tags: [discipline, rotation, performance-feedback, position-management, proposal]
as_of_timestamp: 2026-06-01T00:00:00+08:00
author_role: researcher
status: proposal
---

# 績效反饋換股節流(Performance-Feedback Rotation Throttle)

**原則(principal directive, 2026-06-01):** 投資組合績效**非常好**時,**不要急著換股** —
改去**深入探索支撐數據**(贏家為什麼還在贏);**一旦行情真的沒了、真反轉**,再換股。

這是把憲法的「預設 HOLD、不過多操作、進攻需十足證據、防守可在系統性觸發時快速行動」
具體化成一個**作用在換股訊號上的節流閥**。它**不改核心 scorer**,只在建議層重新框定:

## 判定

- **真反轉(reversal)** = 任一成立:`regime ∈ {risk_off, capitulation}` /
  `資金面 ∈ {STRESS, RUPTURE}` / `posture.systemic_risk` / 空頭避險觸發 /
  強勢持股跌破關鍵結構且動能與 FOM 同步走弱。
- **績效強(strong)** = 本人回報「非常好」(ground truth;實現損益不在 audit 內,
  主動 sleeve 僅約 10%,RSU 主導且刻意排除),或持倉強度代理高(現股 HOLD 占比 ×
  FOM,扣槓桿 decay)。

## 動作

| 狀態 | 動作 |
|---|---|
| 績效強 **且** 無真反轉 | **不換股**;深挖支撐數據(每檔強勢現股的 FOM 五維、動能、題材是否完好);列出「會翻成換股」的失效觸發。槓桿 ETF 的 decay 減碼屬**衛生**(不算換股),仍執行。 |
| 真反轉確認 | **放行換股**;先處理系統性風險與 SELL/TRIM。防守可快。 |
| 其餘 | 正常健檢,不急著動作。 |

## 為什麼

- 贏家換掉贏家是最貴的錯誤之一;強勢且論點完好時,**續抱 + 加深理解**優於輪動。
- 但「續抱」不能變成「鴕鳥」——所以明確定義**真反轉**的客觀觸發,反轉一到就換,不戀棧。
- 對齊 [[philosophy/05-decision-rubric]] 的不補位、[[philosophy/08-risk-and-position]] 的防守快/進攻慢。

## 實作

`src/sharks/discord/feedback.py`(`compose_feedback`),純函式讀 `outputs/` 的
portfolio-audit + daily-health-check;Discord 以 `/feedback [perf]` 與每場會議的
「📊 換股節流」段落呈現。recommend-only,永不下單。
