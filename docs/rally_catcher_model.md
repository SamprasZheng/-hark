# 起漲捕捉模型(Rally-Ignition)— 什麼條件最能抓到起漲股(Finviz 數據驅動)

> 主理人(2026-06):重點是**先抓到起漲的股票**。2022 錯殺機會很多,但資金不如 2021 順,
> 所以**嚴格篩選**。有 Finviz API 後,FOM/Rescan/DeepBuy 都要真數據支持。

recommend-only。本檔定義「起漲」的可操作模型 + Finviz screener 條件 + 參數,全程用 Finviz
(不用 yfinance)。Finviz filter 碼參考 mariostoev/finviz;**碼會變,務必在 Finviz UI 對一次**。

## 一、什麼是「起漲」(操作定義)
起漲 = **從底部結構剛轉為上升、有買盤進場、但還沒被追高**。四個必要條件:
1. **趨勢剛翻**:站上 20 日 + 50 日線(早期),最好 SMA20 剛上穿 SMA50。
2. **買盤偵測(資金)**:相對量能放大(Rel Volume > 1.5)、內部人/法人轉買。
3. **有空間**:距 52 週/ATH 還有一段(10–40%),不是貼著高點、也不是落刀(>70%)。
4. **有燃料(tight regime 必要)**:真盈利(毛利+、EPS 成長+)或真題材;否則只是反彈,撐不起大浪。

> **2021 vs 2026 的差別**:2021 雞犬升天,條件 1+2 就夠;2026 廣度小,**條件 4(燃料)是硬門檻**
> —— 這就是「嚴格篩選」的數學:沒盈利/沒題材的,`/rally` 一律打 🪨 缺燃料 / 🚫 墓園。

## 二、Finviz screener 條件(已編成 presets)
| preset | 條件(f=) | 抓什麼 |
|---|---|---|
| `rally_ignition` | 站上 20/50 線 + 月漲 + RelVol>1.5 + 量>500K + 價>$5 + 毛利+ + EPS YoY+ | **早期起漲、有盈利底** |
| `mis_killed_2022` | 距 52w 高 ≥30% + 站上 50 線 + RelVol>1.5 + 營收5y+ + 毛利+ | **錯殺反轉、開始翻** |
| `dipbuy` / `dipbuy_quality` | 距 ATH≥30% + 流動性 + 站上 50 線(+ 流動比/營收) | 抄底基本盤 |

跑法(全 Finviz,無 yfinance):
```
python -m sharks.data.finviz_elite rally rally_ignition
python -m sharks.data.finviz_elite rally mis_killed_2022
/finviz rally_ignition        # Discord(重啟後)
```

## 三、9 維模型 + 參數(rally_signal,Finviz 餵入)
`finviz_row_to_dims` 把 Finviz 欄位 → 9 維;`assess` 融合 + 燃料閘:
- **技術**:Perf Month/Quart + 相對 SMA50/200 + RSI(50–72 健康)
- **資金(買盤)**:Rel Volume + Insider/Inst Transactions
- **基本面**:ROE/毛利/營收成長/淨利率 · **估值**:P/E、P/S、PEG · **成長**:EPS/Sales
- **風險**:Beta/Short Float/波動 · **分析師**:Recom · **距高**:52W High
- **參數(tight regime)**:`RALLY_MIN=55`(起漲門檻)、`BUY_MIN=62`、`WAVE_FUEL_MIN=55`
  (真盈利/真題材門檻,比 catalyst 50 嚴)、`MIN_STREAK_BUY=3`(連續起漲≥3 期才考慮)。
- **判定**:🟢 連續起漲+有燃料=可考慮 / 🟡 起漲中 / 🔵 蓄勢 / 🪨 缺燃料(不追)/ 🚫 墓園。

## 四、重點板塊(主理人指定,已是 scope,直接 Finviz 篩)
- **支付(龍蝦 AI 代理帶動)** `payments`:`V MA AXP PYPL XYZ FI GPN FOUR COIN CRCL HOOD SOFI NU`
  - 卡組織(V/MA)= 最穩;穩定幣軌(COIN/CRCL)= 高賠率;PYPL/XYZ = 轉機。Stripe 私有(等 IPO)。
  - 跑:`python -m sharks.data.finviz_elite rally payments`
- **電商** `ecommerce`:`AMZN SHOP SE …`(+ 富邦媒 `8454.TW` 已先行啟動 → 用 `tickers:8454.TW`)
  - 跑:`finviz_elite rally ecommerce` 或 `... rally ecommerce tickers... `(台股加 .TW)
- 其他 scope:`crypto`(MSTR/COIN/CRCL/礦工)、`ipo`、`broadening`、`space`…

## 五、把 FOM / DeepBuy 接上 Finviz 真數據(下一步,需主機驗證)
現況:FOM 用 yfinance 價格 + **手寫 IP_DEFENSIBILITY**,**無真基本面**;dipbuy quality 缺則 TBD。
升級:用一次 Finviz 全欄位 export(整個宇宙)→ 取得**真 P/E、ROE、毛利、成長、Rel Volume、
內部人/法人** → 餵 FOM 的 quality/valuation 維度 + dipbuy 的 quality + rally 的基本面,
**取代手寫先驗**。(實作需在有 Finviz API 的主機跑+驗證。)

## 六、嚴格篩選紀律(2026 非 2021)
1. **燃料閘第一**:沒真盈利/真題材 → 不追(這是「嚴格」的核心)。
2. **連續起漲**:單根不算,≥3 期 + composite≥62 才考慮。
3. **regime 閘**:資金面 STRESS → 收手,小型/高 beta 先砍。
4. **分批 + 留彈藥**:對齊 weekly_plan / deployment_plan。
