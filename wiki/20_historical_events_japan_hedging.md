---
type: synthesis
tags: [historical-events, japan-rate-hike, hedging, yen-carry, model-calibration, skills]
title: 100 年大事件 + 日本升息 + 對沖 playbook + skills/agents + 模型校準
as_of_timestamp: 2026-05-30T09:00:00-04:00
author_role: compiler
status: live
schema_version: 1
sources:
  - outputs/twse-complete-2026-05-30.json
---

# 100 年大事件 + 日本升息 + 對沖 + 模型校準 + skills

---

## §1. 🌍 過去 100 年股市大事件 + 跌幅 + 復合疊加

### 主要崩盤事件對照表

| 年 | 事件 | SPX 跌幅 | 時程 | 主因 | 加重因素 | 復合疊加 |
|---|---|---|---|---|---|---|
| 1929 | 大蕭條 | **-89%** | 3 年 | margin loans 過度 + 銀行擠兌 | Smoot-Hawley 關稅 + 金本位緊縮 | ✅ 政策錯誤連鎖 |
| 1973-74 | 石油危機 | -48% | 21 月 | 阿拉伯石油禁運 + Bretton Woods 崩 | 越戰 + 通膨 + 尼克森辭職 | ✅ 地緣 + 通膨 + 政治 |
| 1987 | 黑色星期一 | **-23%(單日!)** | 1 天 | Portfolio insurance 演算法死循環 + 高利率 | 中東緊張 + 美元贬值 | ⚠️ 結構錯誤主因 |
| 1990 | 海灣戰爭 / S&L | -20% | 3 月 | 第一次伊拉克戰 + 儲蓄機構危機 | 房價泡沫 + 高利率 | ⚠️ 中度 |
| 1997-98 | 亞洲金融危機 | -19% | 6 月 | 泰銖貶值 → 韓國 / 印尼 / 俄羅斯 | LTCM 破產 + 高槓桿 | ✅ 連環崩 |
| 2000-02 | dot-com | **-49% (-78% NDX)** | 2.5 年 | 無營收科技過度估值 | 9/11 + 安隆案 | ✅ 估值 + 信任 + 黑天鵝 |
| 2008 | GFC | **-57%** | 17 月 | 次貸 + Lehman 倒 | AIG / Bear Stearns / 信用凍結 | ✅✅✅ 連環倒 |
| 2010 | Flash Crash | -9%(分鐘)| 36 min | HFT algo 鯰魚效應 | 希臘債務 | ⚠️ 結構主因 |
| 2011 | 美債降評 + 歐債 | -19% | 5 月 | S&P 降美國 AAA + 希臘違約風險 | 福島核災 | ⚠️ 三疊加 |
| 2015-16 | 中國股災 + 油崩 | -14% | 7 月 | 上證崩 + 人民幣貶值 + 油 $30 | Fed 升息預期 | ⚠️ 雙重 |
| 2018 Q4 | Trump 1 貿易戰 | -20% | 3 月 | 中美貿易戰升級 + Fed 升息預期 | Powell put 沒出 | ⚠️ 政策衝擊 |
| 2020 | Covid | **-34%** | 33 天 | 公衛突發 + 經濟停擺 | 油價戰 + BTC 同跌 | ✅ 流動性 + 信心 |
| 2022 | Fed 鷹派 | -25%(-33% NDX)| 12 月 | Powell 暴力升息 + Cathie ARK 崩 | 烏俄戰 + 通膨高 | ✅ 利率 + 估值 |
| 2024 Aug | Yen 套利平倉 | **-10%(週)** | 1 週 | 🇯🇵 BOJ 升息 → 日圓套利強平 | NVDA 開始疑慮 | ⚠️ **這就是日本因素** |
| 2025-26 | Trump 2 關稅 | -8% | 4 月 | 全球互惠關稅震盪 | BTC 已破 / 黃金漲 | 🟡 進行中 |

### 復合疊加規律(系統校準用)

**跌幅 -10% 級**:1 個觸發點(政策 / 黑天鵝)
**跌幅 -20% 級**:2 個觸發點疊加(政策 + 結構 OR 地緣 + 估值)
**跌幅 -30% 級**:3 個觸發點(政策 + 信用 + 流動性)
**跌幅 -50% 級**:**結構性崩潰**(銀行倒 / 信用凍結 / 連環崩)
**跌幅 -80% 級**:**錯誤政策連鎖**(1929 / 2002 dot-com)

### 對你系統的校準意義

當系統檢測 `N 個獨立訊號` 同向時:
- 1 訊號 → 警報 YELLOW(預期 -5~-10% 修正)
- 2 訊號 → ORANGE(預期 -10~-20% 回調)
- 3 訊號 → RED(預期 -20~-30% 中度熊)
- 4+ 訊號 → CRITICAL(預期 -30%+ 重度危機)

**目前 YELLOW(1.5 訊號)** = 對應歷史 -5~-10% 跌幅機率

---

## §2. 🇯🇵 日本升息 — 真實大魔王分析

### 2024 Aug 預演的恐怖

2024 年 8 月 BOJ 升 25 基點 → 觸發:
- **USD/JPY 從 161 → 142(-12% 一週)**
- **日經 -25%(週內)**
- **NVDA / SOXX -15%(週內)**
- **VIX 飆 +200% 至 65**(短暫)
- **NDX -10%(週內)**

### 為什麼日本升息這麼危險(機制)

#### 日圓套利(Yen Carry Trade)

```
Step 1: 機構借日圓(零利率)→ 賣 → 換美元
Step 2: 用美元買 NVDA / TSLA / 高貝塔資產
Step 3: 賺利差 + 資產上漲

問題:當日圓升值(BOJ 升息或避險)
Step 4: 美元資產被強平(覆蓋日圓借款)
Step 5: 高貝塔資產急跌
Step 6: VIX 飆,所有風險資產同跌
```

**估計全球日圓套利規模:$5-20 兆美元**(IMF 估)

### 2026 日本升息風險

| 情境 | 機率 | 觸發 |
|---|---|---|
| BOJ 不升息(零) | 30% | 通膨溫和 + 經濟疲弱 |
| 小升 0.25% | 40% | 通膨持續 + 日圓壓力 |
| 中升 0.5% | 20% | 通膨突破 + 美元強勢 |
| 大升 1% | 8% | 通膨失控 |
| 緊急行動 | 2% | 日圓崩 |

**對你 portfolio 衝擊**(若中升 0.5%):
- NVDA:**-15~-25%** in week
- VIX:+150%
- TSM(日本相關):-10~-20%
- 你 80% NVDA → **portfolio -12~-20% in week**

### 日本升息 vs Fed 升息 vs Trump 政策

| 衝擊 | 影響 | 時程 |
|---|---|---|
| Fed 升息 | 漸進、可預期 | 月 |
| Trump 政策 | 突發、可逆 | 日 - 週 |
| **BOJ 升息** | **突發、不可逆、連環觸發** | **日 - 1 週(最快)** |
| 地緣戰爭 | 突發、長期 | 月 - 年 |

**日本升息是 2024-2026 最被低估的「快速衝擊」風險**

---

## §3. 🛡️ 對沖 Playbook(分情境)

### 情境 A:慢漲 — VIX 低、市況穩

```
Cash:          15%
GLD 黃金:       3-5%
LMT 國防:      4-5%
VIX call:      不需(decay 太大)
SH inverse:    不需
```

### 情境 B:YELLOW(目前狀況)

```
Cash:          20% (SGOV)
GLD 黃金:       4-5%
LMT/NOC:       8-10%
VIX 60d call:  0.5%($8K notional 對沖 $80K portfolio)
SH inverse:    可選 1-2%
妖股部位:       <5%
```

### 情境 C:ORANGE — 寬度過熱 + 黃金 +10% + BTC < $60K

```
Cash:          30%
GLD 黃金:       6-8%
TLT 長債:       5%
LMT/NOC:       8%
VIX 60d call:  1-1.5%
SH inverse:    3-5%
NVDA Put:      1-2%(if RSU 仍 > 50%)
妖股:           1-2%(緊縮)
```

### 情境 D:RED — 3+ 訊號示警

```
Cash:          40%
GLD:           8-10%
TLT:           10%
SH/SDS:        5-8%
NVDA / SOXX Put:  2-3%
妖股:           0
進攻 alpha:     最低額度
```

### 情境 E:**日本升息突發**(最重要)

**24 小時內動作**:
```
1. 立即賣 SOXX 50%(NVDA/AMD/AVGO)
2. 買 VIX call(已不便宜但仍要)
3. 換 GLD 6-8%
4. 暫停所有妖股
5. 妖股小型股全清(流動性差,連環跌)
6. 觀察 USD/JPY 為主要訊號
```

**3-5 天內**:
```
1. 評估恐慌底部(VIX 觸頂 + Put / Call > 1.5)
2. 用現金分批進 Buffett tier(MSFT/META/AAPL)
3. 黃金繼續持有等 +20%
```

### 對沖工具(美股可立刻交易)

| Ticker | 用途 | 適用場景 |
|---|---|---|
| **GLD** | 黃金 | 通膨 + 黑天鵝 + 流動性 |
| **TLT** | 長債(20+ 年) | Fed 急降 + 經濟硬著陸 |
| **VXX** | VIX 期貨 | 短期波動爆發(decay 大) |
| **SH** | -1× SPY | 結構性熊 |
| **SDS** | -2× SPY | 強烈熊 |
| **SQQQ** | -3× QQQ | NDX 急跌(decay 極大) |
| **YCS** | -2× 日圓 | 日圓貶值賺(對沖 BOJ 不升)|
| **FXY** | 1× 日圓 | 日圓升值賺(對沖 BOJ 升息)|
| **EWJ** | 日股 ETF | 觀察日股反應 |

---

## §4. 🤖 系統 Skills / Agents 完整清單

### 已部署 Modules(14 個)

| 編號 | 模組 | 用途 |
|---|---|---|
| 1 | `fom.py` | 主要 5 維 FOM 評分 |
| 2 | `fom_alpha.py` | 小中型 alpha 變體 |
| 3 | `cycle_bias.py` | 多尺度週期 |
| 4 | `liquidity_signals.py` | M2/BTC/GLD 三訊號 |
| 5 | `breadth_indicator.py` | NDX/RUT 寬度過熱 |
| 6 | `chip_flow.py` | 籌碼面(機構 + 短興趣 + 量爆) |
| 7 | `meme_squeeze_hunter.py` | 妖股 PUMP 偵測 |
| 8 | `serenity_scout.py` | 供應鏈 chokepoint |
| 9 | `correlation_matrix.py` | NVDA 相關性 |
| 10 | `github_data_universe.py` | SP500 502 + R2K 200 |
| 11 | `taiwan_universe.py` | 台股 72 |
| 12 | `twse_complete.py` | **台股 490(NEW)** |
| 13 | `oversold_recovery_2022.py` | 2022 錯殺回升 |
| 14 | `global_hunter.py` | 多市場 92 ticker |
| 15 | `finnhub_integration.py` | 8 端點 stub(等 API)|
| 16 | `fama_french_validation.py` | 99% 顯著驗證 |
| 17 | `streamlit_app.py` | 10 頁 GUI |

### Agents(角色)

| Agent | 職責 |
|---|---|
| **Compiler** | 把 raw/ 編譯進 wiki/ |
| **Researcher** | 寫深度 entity / concept 頁 |
| **Risk Officer** | 風控 + 否決違規推薦 |
| **(未來)Devil's Advocate** | 每推薦自動產反方論點 |
| **(未來)Market Historian** | 每事件比對歷史對照 |

### Wiki 知識庫(20 頁)

`philosophy/`:17 個 concepts + 13 entities + 11 編號哲學 + Karpathy ref
`wiki/`:01-20 編號 + 推薦頁 + log + positions + alpha_library

### Backtest 驗證

- **總報酬 +975%** vs SPY +129%(2016-2026)
- **Fama-French alpha t=3.859**(99% 顯著)
- **NVDA 抓中 55 次 top 3**
- **MDD -53%**(集中度,單股 cap 後可降至 -30%)

---

## §5. 🎲 沒有常勝模型 — 校準方法

### 真實(每個模型都有失敗時刻)

| 模型 | 強項 | 弱項 |
|---|---|---|
| Aggressive | 牛市末段 | 熊市重傷 |
| Conservative | 熊市 / 升息 | 牛市落後 |
| Trend | 強勢 trending | 整理 / 反轉誤殺 |
| Smart Money | 主力多空轉折 | 散戶妖股錯失 |
| Technical | 短線 swing | 基本面強股漏接 |
| Fundamental | 長線 + 估值 | 速度太慢錯過 |
| Ensemble | 平均較佳 | 平庸 |

### 校準方法(避免日調參過擬合)

#### 方法 1:Walk-Forward Validation
```
2016-2020 (60%) — Train(設定權重)
2020-2023 (20%) — Validate(微調)
2023-2026 (20%) — Test(只看不調)
```

#### 方法 2:每月校準(非每日)
```
每月底:
  1. 計算上月所有模型表現
  2. 計算 IC(Information Coefficient)
  3. 若某模型 3 月 IC < 0.05 → 休眠
  4. 若某模型 3 月 IC > 0.15 → 加權
  5. 權重調整 < 5%(避免反應過度)
```

#### 方法 3:Ensemble 投票(最保險)
```
N 模型對 ticker X 投票:
  6+ 模型同意 → STRONG_BUY
  4-5 同意   → BUY
  2-3 同意   → WATCH
  0-1        → SKIP
```

#### 方法 4:Regime-Conditional 模型切換
```
Regime 偵測:
  if VIX < 16 & 牛市 → Aggressive 主
  if VIX > 25 & 熊市 → Conservative 主
  if 寬度 OVERHEATED → Smart Money 主(找出貨股)
  if BTC h2024 phase D → Cycle Aware
```

#### 方法 5:Postmortem 強制學習
```
每次失敗:
  1. 寫進 09_postmortem_log.md
  2. 識別「哪個模型誤判」
  3. 該模型該維度 IC 自動下調
  4. 不重新訓練,純 Bayesian update
```

---

## §6. 🇹🇼 台股 490 隻 Top 5 (TWSE 完整 scan)

| Rank | Ticker | 名稱 |
|---|---|---|
| 1 | **8046.TW** | 南亞電(PCB)|
| 2 | **3017.TW** | 奇鋐(伺服器散熱)|
| 3 | **1519.TW** | (待驗證)|
| 4 | **2413.TW** | (待驗證)|
| 5 | **2368.TW** | (待驗證)|

涵蓋從 72 → **490** 隻台股(7× 擴展)

---

## §7. 立即動作清單

### 系統(本週)
- [x] Local Streamlit 啟動 ✅ http://localhost:8501
- [x] TWSE 完整 490 ✅
- [ ] Streamlit Cloud 部署(免費 24/7 公開)
- [ ] YCS / FXY 加入 universe(日圓對沖工具)
- [ ] BOJ 政策日曆加入 catalyst calendar
- [ ] 多模型 ensemble 完整實作

### 內容(本週)
- [ ] 錄第一集 Streamlit demo(5-10 分鐘)
- [ ] 寫 Blog:「為何日本升息是 2026 最大風險」
- [ ] PolkaSharks Twitter / X 自我介紹文

### 對沖(立即)
- [ ] 確認你 portfolio GLD 倉位 3-5%
- [ ] 考慮 FXY 1-2%(日圓升值對沖)
- [ ] BOJ 會議日記入日曆(下次 7 月)

---

## §8. 一句話

> **「100 年大事件告訴我們:**
> - **單一觸發 → -10% 級**
> - **2 觸發疊加 → -20% 級**
> - **3 觸發 → -30%+ 級**
>
> **日本升息是 2026 最被低估的快速衝擊;
> 對沖工具 GLD + FXY + VIX call + 現金 = 不會輸太多。**
>
> **沒有常勝模型,但 ensemble 投票 + 月度校準 = 穩定高勝率。」**

---

## See also

- [[06_cycle_framework]] — 多尺度週期
- [[07_ai_bubble_audit]] — 泡沫檢核
- [[10_defensive_hedging]] — UVXY 不能用
- [[11_adaptive_loop]] — 自我改進
- [[18_ultimate_integration]] — Fama-French 解釋

## Sources

- [TWSE Open API](https://openapi.twse.com.tw/)
- [TPEx Open API](https://www.tpex.org.tw/openapi/)
- IMF Working Papers on Yen carry trade
- BIS 90+ Years of Market History
