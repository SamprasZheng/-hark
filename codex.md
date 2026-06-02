基於你這份 phase 1 規格，我看到的不是「實作漏洞」，而是幾個會直接把交易系統帶歪的**邏輯漏洞**。優先級由高到低如下。

**發現**

1. **[Critical] 沒有 point-in-time 約束，會導致回測與選股嚴重 lookahead**
   你現在的 universe、sector、market cap、`last_earnings_date`、52 週新高、analyst revision、insider buying、新聞與 KOL 摘要，全部都很容易在後續被「用到當下最新資料」而不是「當時可見資料」。  
   這會讓 phase 4 的回測看起來很準，但實盤會崩。
   - 風險來源：`watchlist/universe.yaml`、`entities/*.md`、`03-sentiment-vs-fundamental.md`、`04-sector-and-finviz.md`
   - 必須補：每個訊號都要定義 `as_of_timestamp`，財報與新聞都要按發布時間與可取得時間處理，universe 要有歷史版本。

2. **[Critical] 缺少完整的風險與倉位邏輯**
   你定義了「每天 10 檔推薦」，但沒有定義：
   - 每檔佔比
   - 單一 sector 上限
   - 單一事件風險上限
   - 最大回撤停手機制
   - 進場後的失效條件 / 出場條件
   - earnings 前後是否持有
   - 相關性過高時怎麼降權  
   沒有這些，系統就算方向對，也可能因為集中度或事件風險爆掉。
   - 風險來源：`05-decision-rubric.md`、`01-time-horizon.md`、`07-mode-switch.md`
   - 必須補：明確的 position sizing、max exposure、time stop、thesis invalidation、earnings/event policy。

3. **[High] 「情緒面上漲 = 虛漲」這個規則太硬，會把真正的趨勢股誤殺**
   你把情緒上漲直接視為賣訊號，但很多真正的大趨勢股在 early stage 也會先出現社群熱度、新聞密度、甚至估值壓縮後的情緒修復。  
   若沒有 regime conditioning，這條規則會把 momentum breakout 與泡沫混在一起。
   - 風險來源：`03-sentiment-vs-fundamental.md`
   - 必須補：情緒面只能當「加權因子」，不能單獨當賣出定論；要和營收修正、價格結構、估值區間一起判斷。

4. **[High] Signal taxonomy 缺少衝突解決規則**
   你定義了四維框架：情緒 / 消息 / 技術 / 基本面，但沒有說：
   - 四個維度衝突時誰優先
   - 哪些情況是「直接排除」
   - 哪些情況是「只觀察不交易」
   - 哪些情況是「允許部分加倉」  
   沒有 arbitration，最後很容易變成手工拍腦袋。
   - 風險來源：`02-signal-taxonomy.md`、`05-decision-rubric.md`
   - 必須補：明確的 gating 規則，例如「基本面與消息面反向時，技術面只能做 timing，不可 override thesis」。

5. **[High] Finviz-style filter 很容易變成 data-snooping 工具**
   你想用 Finviz-style screener replay 做分類，方向對，但如果 filter 是在「知道結果後」才挑出來的，就會有極強的資料挖掘偏誤。  
   尤其是像「距離 52 週高點」、「MA crossover」、「Bollinger breakout」這類 price-derived filter，本身就高度相關，容易重複計數。
   - 風險來源：`04-sector-and-finviz.md`、`backtest/README.md`
   - 必須補：訓練 / 驗證 / walk-forward 分離，並限制特徵重疊；同一類 price feature 不能無限制加權。

6. **[High] 新聞與 KOL 每小時摘要有明顯時間洩漏風險**
   「每小時 KOL/macro 摘要」如果沒有嚴格的 release-time normalization，會把市場已反映後的敘事再餵回模型。  
   這種訊號通常看起來很有故事性，但實際上是延遲資訊。
   - 風險來源：`07-mode-switch.md`、未來 Phase 2 的 news pipeline
   - 必須補：把新聞、財報、宏觀事件按「第一次可見時間」入庫，並區分 pre-market / market hours / after-hours。

7. **[Medium] 模式切換用「平日 / 週末 / 在家」做判斷，邏輯太粗**
   高頻/低頻不應該由人的作息決定，而應該由市場狀態決定。  
   例如：  
   - earnings week 不適合高頻
   - 低流動性標的即使週末也不適合高頻
   - Fed day / CPI day / 地緣衝突日要降頻  
   只用日曆切換會讓模式與風險不匹配。
   - 風險來源：`07-mode-switch.md`
   - 必須補：模式切換應依事件風險、流動性、波動率、交易時段來決定。

8. **[Medium] 排除清單不夠數字化，容易留下灰色地帶**
   你說不碰 penny / illiquid / OTC / leveraged ETF，但沒定義門檻。  
   例如：
   - 多少價格以下算 penny
   - 平均成交量多少以下算 illiquid
   - market cap 下限是多少
   - ADR、biotech、post-IPO lockup、halt risk 要不要排  
   沒有數值化，實際執行會不一致。
   - 風險來源：`06-exclusions.md`
   - 必須補：用可機器判斷的條件寫清楚。

9. **[Medium] 「每天 10 檔」是硬約束，可能強迫系統在弱機會日也要出手**
   如果 universe 當天只有 3 檔符合 thesis，你還是硬湊 10 檔，會把低品質標的硬塞進去。  
   這會讓系統從「推薦」退化成「填滿名單」。
   - 風險來源：`05-decision-rubric.md`
   - 必須補：允許 no-trade / fewer-than-10，並把「不出手」視為有效輸出。

10. **[Medium] Mag 7 + 供應鏈池偏重，會把系統鎖死在單一 factor 暴露**
    你現在的核心 universe 很偏大型科技與半導體供應鏈。這適合第一輪哲學，但如果不預留 sector rotation、defensive、rate-sensitive、energy、financial 等輪動類別，系統會過度集中在同一組宏觀因子上。
    - 風險來源：`watchlist/universe.yaml`、`04-sector-and-finviz.md`
    - 必須補：至少為後續階段保留可擴充的 sector bucket，避免把策略等同於「科技 beta」。

**結論**

這份 phase 1 最大的問題不是寫得不夠多，而是有幾個地方如果不先補上，後面 phase 2-4 會「看起來很合理、實際上很假」：

- point-in-time
- 風險與倉位
- signal conflict resolution
- no-trade 機制
- 時間戳與 release-time 處理

如果你要，我下一步可以直接幫你把這份規格整理成一份**「交易邏輯安全清單」**，把上述漏洞轉成可落地的規則條款。