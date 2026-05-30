---
type: recommendation
tags: [portfolio-audit, employee-concentration, liquidity-signals, comprehensive]
as_of_timestamp: 2026-05-30T00:00:00-04:00
trading_date: 2026-06-02
regime_ref: 01_macro_state.md@2026-05-30
schema_version: 1
author_role: compiler
risk_officer_review: pending
data_sources:
  - outputs/portfolio-audit-2026-05-30.json
  - outputs/liquidity-signals-2026-05-30.json
  - outputs/fom-alpha-2026-05-29.json
---

# Portfolio Audit + Employee Plan + Liquidity Alert — 2026-05-30

## 🔔 §1. Liquidity Alert: YELLOW(1/3 訊號示警)

| 訊號 | 狀態 | 數據 |
|---|---|---|
| **M2 Money Stock** | 🟢 **支持性** | $22.2T,YoY +2.78%(Warsh 不干預驗證) |
| **BTC** | 🔴 **結構性熊** | $73K(-37% 從 $116K 高),低於 20m MA |
| **黃金(GLD)** | 🟡 **臨界** | +36% YoY,但 6m 只 +6.4%(門檻 10%)— 邊緣 |
| **複合警示** | **YELLOW** | 1 訊號發出;若黃金繼續 → ORANGE |

**意義**:不是即將崩盤,**但 BTC 已先行破絕證實 6-12 月領先警告**。歷史對標:2018 Q3 BTC 先破,Q4 SPX -20%。
**動作**:維持系統「May-Oct 防禦 + Nov buy-the-dip」戰術不變;**增加追蹤黃金 6m return**(若 > 10% → 升 ORANGE)

---

## 🔴 §2. Portfolio 1 處置清單(32 持倉)

### 必須立即賣出 — 13 支(占 P1 約 38%)

| Ticker | 名稱 | % | 理由 |
|---|---|---|---|
| **TARK** | 2× ARKK | 13.0% | 槓桿 ETF decay + ARKK 集合 bubble |
| **LABU** | 3× XBI Bull | 5.1% | 3× 槓桿 + 進入 6-10 月 XBI 最弱季 |
| **ORCX** | 2× ORCL | 4.5% | 🚨 你親自旗的破絕股 2× 版 |
| **AAPB** | 2× AAPL | 3.5% | AAPL 9 月弱 + decay |
| **NOWL** | 2× NOW | 3.2% | NOW 本身好但 decay 吃光 |
| **SMCL** | 2× SMCI | 3.0% | 🚨 你親自旗的破絕股 2× 版 |
| **LULG** | 2× LULU | 3.0% | LULU 中性 + decay |
| **QBTX** | 2× Quantum | 2.2% | 量子敘事 + 槓桿 |
| **QSU** | 量子 | 1.9% | 同上 |
| **RBLU** | 2× RBLX | 1.9% | 遊戲 + 槓桿 |
| **QUBX** | 量子 | 1.7% | 同上 |
| **OKLL** | 2× OKLO | 1.6% | 🚨 你親自旗的破絕股 2× 版 |
| **RGTX** | Rigetti(量子)| 3.6% | 純敘事零營收 + 火紅買入 = farmer mindset |

**賣出釋出現金 ≈ 48% × portfolio 1 ≈ $5,400**

### Trim 30-50% — 5 支

| Ticker | % | 動作 | 理由 |
|---|---|---|---|
| **CRSR** | 4.5% | 砍 50% → 2.2% | 電競周邊弱品質 + 消費復甦邊緣 |
| **DDD** | 3.1% | 砍 70% → 0.9% | 3D 列印業績差;接近 SELL |
| **ENPH** | 3.1% | 砍 30% → 2.1% | TAN 6-10 月最弱,11 月再加 |
| **AMPX** | 1.9% | 砍 50% → 0.9% | 電池投機 |
| **CRCT** | 1.8% | 砍 50% → 0.9% | 消費電子弱品質 |

### Hold(暫不動)— 14 支

| Ticker | 為何 hold |
|---|---|
| **SBIT** | 反向 BTC -1×;系統說 BTC Q4 才見底 → SBIT 還有空間 |
| **VSCO, ARRY, NKE, LULU, TSLA, STZ, APA, SWKS, PG, PEP, CRM, VFC** | FOM 中性;觀察 |
| **NOW** | Buffett tier!(現股版,**不是 NOWL 槓桿版**)|

### ✅ P1 處置完釋出現金

- 賣出 13 支:~$5,400
- Trim 5 支:~$700
- **總釋出: ~$6,100** → 進 SGOV 房屋頭期戶 + 機會時加 Buffett tier 持倉

---

## 🟡 §3. Portfolio 2 處置清單(26 持倉)

### 必須賣出 — 1 支

| Ticker | 理由 |
|---|---|
| **SHAK** | 消費 mid-cap;品質弱;FOM < 30 |

### Trim 30% — 4 支

| Ticker | 動作 | 理由 |
|---|---|---|
| **LUNR** | 砍 50% | 太空敘事;高 vol 低 IP |
| **DOCN** | 砍 50% | SaaS 沒抓到 AI;tepid |
| **DELL** | 砍 30%(你說想加,但系統說 momentum 已過熱) | 你「買太少」感覺實際是好事;系統說等回測 |
| **SKYT** | 砍 30% | 特殊代工投機 |

### ⚠️ ADD(系統建議,但需要 override 判讀)

| Ticker | 系統判讀 | 你的判讀 | 結論 |
|---|---|---|---|
| **ORCL** | FOM 78(contrarian 81)— ADD | 你親口說「已開始下跌」破絕中 | **Compiler override:DEFER**(已寫進 09_postmortem ENTRY-001) |
| **UEC** | FOM 59(Trump 核能 + golden cross)— ADD | 你已持有 | **同意 ADD**:$300-500 加碼 |

### Hold — 19 支

包括 AAPL(Buffett tier;但已在 NVDA RSU 80% 不需加)、PG、PEP、AESI、GFS、ALGM(中性)、其他

---

## 🎯 §4. 必須補洞:你沒有 MSFT 也沒有 META!

**這是最重要的缺口**。

### 為什麼必須補

| 維度 | MSFT | META |
|---|---|---|
| Buffett 3M | 73 | 75 |
| FOM v1 排名 | #4 | **#1** |
| 與 NVDA correlation | 中等(2022 同跌 50%;2025-2026 decouple)| 低(獨立業務週期)|
| 6 月買進的合理性 | $430-450 區間進場 | $560-590 區間進場 |

### 配置建議(從 6/17 NVDA RSU 釋出資金)

- **MSFT 起始 $5,000-7,000**(若 RSU vest 賣 50% 釋出 $7,500)
- **META 起始 $5,000-7,000**

---

## 📅 §5. 員工 NVDA RSU/ESPP 處置 schedule

(詳見 [12_employee_concentration](../12_employee_concentration))

### 6/17 vest($15K)— 12 天後

| 動作 | 金額 |
|---|---|
| 賣 50% vest | $7,500 |
| → SGOV(房屋頭期準備) | $3,000 |
| → MSFT 起始 | $1,500 |
| → META 起始 | $1,500 |
| → LMT 加倉 | $750 |
| → UEC 加倉 | $750 |

### 8 月 ESPP($16K)
類似分配,但 SGOV 加大 → 50%

### 9 月 RSU($15K)— 進入秋季最弱期
**SGOV 75%**;暫停股票加倉(等 11 月 buy-the-dip)

### 12 月 RSU($15K)
分配回正常 — 進入 11月強季

---

## 📝 §6. 整體 plan 一頁化

```
NVDA 集中度 schedule:
  現在: 80% → 6/17後: 70% → 8月: 65% → 9月: 60% → 12月: 55% → 2027 Q1: 50%

Portfolio 1 立即動作(本週):
  ✘ 賣 13 支槓桿 ETF + 量子($5,400)
  ✘ Trim 5 支($700)
  → 釋出 $6,100 → SGOV + MSFT/META 起始

Portfolio 2 立即動作:
  ✘ 賣 SHAK
  ⚠ DEFER ORCL(你 override)
  ✓ Add UEC $300-500

6/17 後 RSU 處置:
  賣 50% = $7,500 分配給:
    SGOV 40% / MSFT 20% / META 20% / LMT 10% / UEC 10%

每月跑系統:
  • portfolio_audit.py — 持倉檢視
  • fom_alpha.py — 機會掃描
  • liquidity_signals.py — 黑天鵝預警
  • cycle_validator.py — 規則性催化劑
```

---

## 🎓 §7. 給你的核心智慧

1. **集中是力量,過度集中是脆弱** — Buffett 沒有單股 80%
2. **稅務優化 = 額外 alpha** — vest 立即賣 0 新增稅
3. **流動性訊號(M2/BTC/Gold)是 3-12 月先行警告** — 不是進場訊號,是部位調整節奏
4. **跟你判斷一致時放大,違背你判斷時警示** — ORCL 你說破,系統說 ADD → Compiler 尊重 principal
5. **房屋頭期 ≠ 投資** — 鎖定 SGOV,不能再賭

---

## See also

- [[12_employee_concentration]] — RSU/ESPP/稅務完整 framework
- [[10_defensive_hedging]] — 防禦組合(現金為王)
- [[06_cycle_framework]] — 多尺度週期
- [[09_postmortem_log]] — 不重蹈覆轍 + farmer mindset 案例
- [[../philosophy/concepts/farmer-mindset]] — 「火紅買入」反案例
- [[../philosophy/08-risk-and-position]] — 集中度規則
