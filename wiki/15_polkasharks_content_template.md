---
type: synthesis
tags: [polkasharks, youtube, content, blog, video, brand]
title: PolkaSharks 波卡鯊 內容生產 SOP
as_of_timestamp: 2026-05-30T04:00:00-04:00
author_role: human + compiler
status: live
schema_version: 1
---

# PolkaSharks 波卡鯊 內容生產 SOP

> 從系統分析 → YouTube / Blog → 鯊魚式內容
> 風格:銳利、直接、數據驅動、自嘲幽默、強烈意見有依據

---

## §1. 鯊魚式品牌定位

**You're the data-driven shark, not the cheerleader.**

| | 一般 KOL | PolkaSharks |
|---|---|---|
| 風格 | 「這支股很棒,大家可以參考」| 「這支 FOM 64.5,但 bubble guard -55,跟風進場一週後再來找我哭」 |
| 證據 | 朋友推薦、新聞、直覺 | 系統 backtest 8.5× SPY,5 維度交叉驗證 |
| 自嘲 | 不承認錯誤 | 「上次我推薦 ORCL,結果就是我自己旗的破絕股,蠢」|
| 教育 | 跟風 | 教你 5 維分析框架 |
| 警告 | 弱 / 沒有 | 「2× 槓桿 ETF decay 每年 50-80%,跟 UVXY 一樣笨」|

---

## §2. 每支推薦股的 5 維分析框架(每集都用)

### 維度 1:基本面(Fundamentals)— 5 分鐘

**必講內容**:
- 公司在做什麼(1 句話)
- 護城河類型(品牌 / 網路效應 / 規模 / 切換成本 / 監管)
- 最近一季營收成長 YoY
- 毛利率走向
- Buffett 3M 分數(我系統有)

**信賴度標籤**:
- 🟢 Buffett tier(3M ≥ 75)
- 🟡 中等 moat(3M 50-74)
- 🔴 投機(3M < 50)

### 維度 2:技術面(Technical)— 3 分鐘

**必講內容**:
- 距 52w 高 / 低
- 5MA / 20MA / 60MA 排列
- 黃金交叉 / 死亡交叉
- TD-9 神奇九轉(用 [[concepts/td-9-sequential]] 計算)
- Bollinger 帶位置
- 是否 OVERHEATED(用 wiki/breadth)

**訊號標籤**:
- 🟢 Strategy A 整理突破
- 🟡 Strategy B 動能但近 52w 高
- 🔴 TD-9 sell setup + 量縮

### 維度 3:籌碼面(Chip Flow)— 3 分鐘

**必講內容**:
- 機構持股 %(yfinance heldPercentInstitutions)
- 短興趣 %(yfinance shortPercentOfFloat)
- 最近量爆次數(我系統 volume_burst_detection)
- 量價背離方向(bullish / bearish)
- Block trade 累積跡象

**訊號標籤**:
- 🟢 機構大量累積(80%+ 持股 + 量爆 + 多筆累積)
- 🟡 中性(無明顯訊號)
- 🔴 distribution(量爆 + 價跌)

### 維度 4:題材(Theme / Catalyst)— 2 分鐘

**必講內容**:
- 屬於哪個 narrative(AI / 國防 / 能源 / 消費復甦 / 妖股)
- 6 個月內可預期 catalyst(財報日、產品發表、政策)
- Trump policy 加分 / 減分
- 季節性順 / 逆風

### 維度 5:資金流入(Capital Flow)— 2 分鐘

**必講內容**:
- Sector ETF 30 天 momentum
- ETF flow(IWM / QQQ / SPY 之比)
- 同 sector 同行表現比較
- ARK / Renaissance / 機構持倉資料

---

## §3. 標準 10 分鐘影片腳本模板

```
[0:00-0:30] 開場 + 鉤子
「今天聊三支股,一支 Buffett tier 我親自抱,
 一支妖股我絕不碰 — 你猜得到嗎?」

[0:30-1:30] 自我提醒 + 系統介紹
「我有套自研系統,backtest 從 2016 跑出 8.5× SPY 報酬」
「5 維交叉驗證 — 基本面、技術面、籌碼面、題材、資金流」
「不是財務建議,但訊號全公開」

[1:30-4:30] 第一支股
「LMT 洛克希德馬丁」
基本面:Buffett 3M = 79,國防寡占,毛利率穩定
技術面:距 52w 高 8%,健康整理
籌碼面:84% 機構持股,2% short
題材:Y2 midterm 國防 bipartisan + Iran 風險
資金流:ITA Nov 季節性 75% 勝率
*** 推薦:中度高信心,5% 倉位 ***

[4:30-7:30] 第二支股
「NTLA Intellia 基因編輯」
籌碼面爆點:47% short float 軋空炸彈
技術面:距高 21%(深修彈起)
基本面:生技投機等級
*** 推薦:小注 1-2%,風險自擔 ***

[7:30-9:00] 第三支股(警示)
「OKLO / SMCI / ORCL — 不要碰!」
我自己以前推薦 ORCL,**自己打臉**
籌碼面:OKLO short 23% + 機構出貨
*** 警示:歸零風險 ***

[9:00-10:00] 結尾
「下集教大家解讀『市場寬度過熱』
 訂閱 / 留言點題」
免責聲明
```

---

## §4. 標準 1500 字 Blog 模板

```
# 標題:[妖股年第 X 集] 系統挑出的「機構暗中累積」3 支股 vs 散戶火紅 3 大陷阱

## 引言(150字)
今天我系統跑出來一個有趣訊號 —
你以為散戶在追的 QBTS / OKLO 是機會,
但我系統的籌碼面分析告訴你:
**機構在出貨**,他們在低調買 NTLA / ARM / RGTI...

## 系統介紹(200字)
PolkaSharks 自研模型:5 維度 + backtest 8.5× SPY
- 基本面(Buffett 3M)
- 技術面(週期+趨勢+破底翻)
- 籌碼面(機構+空單+量爆)
- 題材(Narrative + Trump)
- 資金流(ETF + Sector momentum)

## 推薦 #1:LMT(500字)
[基本面 / 技術面 / 籌碼面 / 題材 / 資金流]

## 推薦 #2:NTLA(400字)
[同樣框架]

## 警示 #3:OKLO / SMCI(250字)
[同樣框架但反向]

## 結語 + 免責聲明
```

---

## §5. 每週內容主題輪換

| 週 | 主題 | 範例 |
|---|---|---|
| W1 | 大盤+宏觀 | YELLOW 警報、流動性訊號、Y2 midterm |
| W2 | 防禦 + Buffett tier | LMT、NOC、PG、PEP、MSFT/META |
| W3 | 妖股獵手 | NTLA、RGTI、BLNK 等抄底 |
| W4 | 警示專題 | UVXY 不能買、槓桿 ETF 陷阱、跟風買的 ORCL |

每月一支:**台股 / 商品 / 國際特殊**

---

## §6. 標題模板(高 CTR)

### YouTube 標題

```
✅ 好範例:
「機構偷偷在買的 3 支股(系統 8.5× SPY 跑出)」
「我打臉 ORCL 推薦 — 自己搞砸後學到的教訓」
「散戶在追量子股,我看到的真相 + 系統警報」
「妖股年的 5 個明確訊號 — 你的部位該怎麼調」

❌ 不要用:
「明日股市必漲標的」(誇大)
「保證賺錢」(犯法)
「跟著我買 100%」(過度承諾)
```

### Blog 標題

```
✅ 範例:
「[數據] 為何我系統說 5 月不該追 NVDA — 並推薦 3 支「真分散」標的」
「[實戰] 我自己 80% NVDA 集中,我如何 6 個月降到 50%」
「[警示] 槓桿 ETF 為何是長期持有的死亡陷阱 — UVXY / TARK / LABU 案例」
```

---

## §7. 系統推薦自動產出影片大綱

我會每週自動產出:

```
[週日晚上] 自動產出當週影片大綱:

📺 PolkaSharks W22 大綱(2026-05-31)

🎯 主題:「OVERHEATED 警報 — 系統的 5 維說減倉」

📊 數據點:
- M2 +2.78% / BTC -37% / GLD +36% / 市場寬度 OVERHEATED
- 4/5 訊號示警

🎬 三支推薦:
1. LMT(Buffett tier 防禦)— FOM 64.2
2. NTLA(基因編輯 + 47% short 軋空)— chip flow 65
3. UEC(Trump 核能 + 你已持有)— FOM 59.4

⚠️ 三支警示:
1. ORCL / ORCX(自我打臉)
2. 量子 QBTS / OKLL / SMCL(火紅買入)
3. TARK / LABU(槓桿 ETF decay)

📌 教育點:
「市場寬度過大」概念 + NDX/RUT 比

🎙️ 風格指示:
- 開場自嘲 ORCL 案例
- 中段用 NVDA RSU 集中度當例子
- 結尾警告 SpaceX IPO trap
```

---

## §8. 法律免責標準聲明(每集必念)

```
「本影片 / 文章內容純粹分享個人研究與系統訊號,
 不是投資建議。
 
 過去績效不代表未來。
 任何投資都有歸零風險。
 投資前請自己做功課,並諮詢合格理財顧問。
 
 我自己持倉會在資訊欄揭露,
 不過揭露 ≠ 推薦你跟單。」
```

---

## §9. 系統升級配套(我每週做)

| 週 | 升級項目 | 給 PolkaSharks 用的訊號 |
|---|---|---|
| W22 | 整合籌碼面進每日 push | 機構動向直接可講 |
| W23 | Sentiment dim(reddit) | 社群熱度可講 |
| W24 | Options flow proxy | 期權 IV 可講 |
| W25 | 完整 2010+ backtest | 信心數字升級 |
| W26 | Devil's Advocate 反方論點 | 每支股自帶反方分析 |

---

## §10. 起步建議(本週可做)

### 立即(今晚)
- [ ] 註冊 / 確認 YouTube 頻道狀態
- [ ] 選 1 個影片主題(建議:「YELLOW 警報 + 我的 3 支真分散標的」)
- [ ] 用今晚數據寫好腳本(我可以幫你產)

### 本週
- [ ] 錄第一集
- [ ] 寫第一篇 blog(可放 Substack / Medium / 自架)
- [ ] 設立社群媒體 cross-post(X / Threads / IG)

### 30 天目標
- [ ] 4 集影片 + 4 篇 blog
- [ ] 100-500 訂閱數
- [ ] 建立 weekly schedule(週日影片、週三 blog)

---

## §11. 跟其他 KOL 差異化

| KOL 類型 | 內容特徵 | PolkaSharks 的差異 |
|---|---|---|
| Cathie Wood 派 | 純樂觀大方向 | 我有空頭警示 + 籌碼面 |
| 技術派 | 圖表為主 | 我有基本面 + 籌碼面整合 |
| 內線 KOL | 跟單為主 | 我提供系統,教釣魚不給魚 |
| 基本面派 | Buffett-only | 我有妖股獵手平衡 |
| 加密 KOL | BTC only | 我有股票+加密+商品+台股 |

**獨家賣點**:
1. 系統可重現(backtest 數字明確)
2. 跨市場(美股+台股+商品+加密)
3. 5 維交叉驗證(任何單一維度都不夠)
4. 自我打臉(ORCL 案例真實)
5. 預測 vs 實際追蹤(postmortem ledger 公開)

---

## See also

- [[14_2026_outlook_and_meme_year]] — 完整內容素材庫
- [[13_global_hunting_grounds]] — 多市場狩獵地圖
- [[09_postmortem_log]] — 自我打臉素材
- [[../raw/methodology/buffett-philosophy]] — 基本面框架
- [[../philosophy/concepts/buffett-3m]] — Buffett tier 評分
- [[../philosophy/concepts/td-9-sequential]] — 技術面神奇九轉
- 未來: `src/sharks/content/youtube_outline_generator.py` — 自動產影片大綱(Phase 3)
