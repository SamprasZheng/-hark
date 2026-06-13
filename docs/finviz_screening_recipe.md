# Finviz 潛力股篩選配方(兼顧潛在收益與風險)→ 灌進 $hark 系統排序

recommend-only 研究方法。Finviz 負責**撒網找宇宙**,$hark 系統(`/basecross` `/stealth`
`/rally`)負責**加紀律 + 排序 + 墓園守門**。兩段式:Finviz 找候選 → 貼進系統定生死。

## 核心觀念:收益濾鏡 × 風險濾鏡(缺一不可)
深跌小型股「反彈空間大」(收益)和「可能要倒/落刀」(風險)是同一件事的兩面。
**只用收益濾鏡 = 一堆殭屍股**(像「Aerospace + SMA50 cross + 距高30%」會撈到 API/DDD/
QMCO 這種多年下跌的)。要兩組濾鏡疊起來。

### A. 收益 / 起漲濾鏡(找「會動的」)
- **All-Time High / Low**:`30%~70% below`(被打趴、有空間;>70% 多半是落刀)
- **50-Day MA**:`Price above SMA50` 或 `SMA50 crossed SMA200 above`(月線翻揚/金叉)
- **20-Day MA**:`Price above SMA20`(短線剛站上)
- **Performance**:`Month Up` 或 `Quarter Up`(起漲動能)
- **Relative Volume**:`Over 1.5`(量能放大 = 資金介入)

### B. 風險 / 存活濾鏡(濾掉落刀與殭屍 — 你現在缺的就是這段)
- **Average Volume**:`Over 500K`(最好 >1M)— 流動性,避免出不掉的微型股
- **Price**:`Over $5`(最好 >$10)— 避開雞蛋水餃/下市風險(你截圖很多 <$5)
- **Market Cap**:`+Small (over $300M)` — 避開歸零的 nano-cap
- **Current Ratio**:`Over 1.5` — 付得出帳、撐得過寒冬(**最關鍵的存活濾鏡**)
- **Debt/Equity**:`Under 1`(最好 <0.5)— 沒被債壓垮
- **Gross Margin**:`Positive (>0%)`(最好 >20%)— 是真生意不是燒錢殼
- **Sales growth past 5 years**:`Positive` — 不是結構性衰退(避免價值陷阱)
- **Insider / Institutional Transactions**:`Positive` — 內部人/法人在買(資金佐證)

### C. 兩個現成配方
**穩健潛力股(低風險)**:距高 30–50% + Price>SMA50 + Avg Vol>1M + Price>$10 +
Debt/Eq<0.5 + Current Ratio>1.5 + Sales growth positive + Insider buying。
→ 數量少、品質高的轉機股。

**積極潛力股(高賠率、控風險)**:距高 50%+ + Price>SMA20 + Rel Vol>1.5 +
Avg Vol>500K + Price>$2 + Current Ratio>1 + Gross Margin>20%。
→ 被打趴但量能進場、且有存活地板的小型股。

## 兩段式工作流(Finviz → 系統)
1. **Finviz**:套上面 A+B 濾鏡 → 匯出/抄下 ticker 清單(這是「宇宙」)。
2. **系統定生死**(貼 ticker 進去):
   ```
   /stealth all tickers:API,AUDC,DUOT,IPWR,…   # 隱蔽吸籌:資金先進、價未動(最早)
   /basecross all tickers:…                      # 月線大底金叉 + 資金介入(已表態)
   /rally all tickers:…                          # 5維 + 連續起漲 + 墓園守門
   無 bot:python -m sharks.discord.ecom_screens API AUDC DUOT IPWR …
   ```
   系統會補上 Finviz **沒有**的東西:月線金叉強度、連續起漲、基本面 quality、
   **墓園守門**(純炒作無實證一律打 🚫)。

## 常見陷阱(你截圖正好踩到)
- **「SMA50 cross」在還在下跌的月線上 = 假訊號**:價格仍創新低時的均線交叉是雜訊。
  → 要疊「距高甜蜜區 + 量能放大 + Current Ratio」才濾掉 API/DDD/QMCO 這種。
- **只看 Charts 不看 Financial**:Finviz 的 `Financial` / `Ownership` 分頁看
  Debt/Eq、Current Ratio、Insider/Inst Transactions——**落刀 vs 轉機就差在這**。
- **多時間軸**:月線看大底結構、週線看金叉、日線看進場;別只用單一時間軸。
- **產業濾鏡會混入雜訊**:Aerospace 篩出 MSOS(大麻)/DDD(3D列印)是標籤鬆,要再人工剔。

## 紀律
1. Finviz 是**找宇宙**,不是買訊;真正的進場由系統的金叉/連續起漲 + regime 健檢確認。
2. **風險濾鏡優先於收益濾鏡**:寧可少幾檔,也不要撈到落刀。
3. 小型股 regime-conditional:資金面翻 STRESS → 先砍,別逆勢接。

---

## Finviz Elite Custom View 設定檢查清單(export-API 路徑)

> 自動化路徑用的是 Finviz Elite 的 `/export` API(`src/sharks/data/finviz_elite.py`,view=152
> Custom)。欄名比對走集中式 `HEADER_ALIASES`(大小寫不敏感 + 多措辭別名),所以**任何
> 帳號的欄名變體都對得上**——唯一需要你手動做的,是在 Custom view 把欄位**勾出來**。
> 缺欄一律優雅降級為 `None`(不報錯、不下單),但對應的閘門會「暗」掉。

### 目前已覆蓋(view=152 預設已帶)
technical / capital / fundamental / valuation / growth / risk / analyst / **dist_ath_pct**
(`52-Week High`、`50/200-Day SMA`、`EPS/Sales Growth`、ROE/毛利/淨利、P/E·P/S·PEG、
Beta·Short Float·Volatility、Analyst Recom、Insider/Inst Transactions、Rel/Avg Volume、Price)。

### 仍需手動勾選的 5 欄(勾完才會亮的閘門)

| Finviz 欄位(Custom view 勾選名) | 點亮的閘門 / 用途 | 缺少時的行為(graceful) |
|---|---|---|
| **Forward P/E** | valuation 改用前瞻 PE(成長股 trailing 失真) | 退回 trailing `P/E` |
| **Earnings** | `earnings_blackout`(財報 ≤3 日不開新倉 — **風險閘**) | gate 永遠 `False`(等於 bypass,**風險**) |
| **ATR** | ATR 部位 sizing(stop = entry − k·ATR) | `atr/atr_pct=None`,無 ATR 停損;改用固定 risk% sizing |
| **Inst Own** | 機構持股**水位**(IPO-drain 防禦傾斜) | `inst_own=None` |
| **Insider Own** | `squeeze_watch`(Short Float≥10% ＋ 高內部人持股) | squeeze 預警永不觸發 |

### 設定步驟(約 5 分鐘,一次性)
1. Finviz → Screener → 切到 **Custom** 表格視圖(URL 帶 `v=152`)。
2. 點欄位齒輪,勾選上表 5 欄(名稱以你帳號顯示為準;`HEADER_ALIASES` 會吸收措辭差異)。
3. 存檔。之後 `python -m sharks.data.finviz_elite rally universe`(或每日排程)即自動帶到。
4. 驗證(自動自報):跑完 stderr 會印「**閘門欄位覆蓋**」行 + `outputs/finviz-scan-<date>.json`
   會帶 `gate_coverage` 區塊。5 欄到位 → 印 **✅ 三閘可運作**、`gate_coverage.dark==[]`;
   仍缺 → 印 `⚠️ 缺欄(對應閘暗):…`。無需人工比對 `null`。

### 注意
- 排程每日跑,但 finviz pull 有 **Tue–Sat TPE 閘**(`scripts/daily_routine.ps1`):TPE 週日/週一
  會重抓上週五收盤,故跳過,避免污染 `連續起漲` streak 與 `overshoot_200d`。
- 趁訂閱在線,每跑一次就把原始 export 存進 `raw/market_data/finviz-export-*.csv`(point-in-time,
  gitignored,本地保存)——訂閱失效後 CLI 自動 fallback 讀最近存檔做離線回測。
