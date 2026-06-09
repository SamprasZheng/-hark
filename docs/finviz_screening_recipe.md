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
