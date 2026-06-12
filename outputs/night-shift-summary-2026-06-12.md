# 夜班總結 + 晨間決策清單 — 2026-06-12 夜(給主理人醒來讀)

> recommend-only;以下全部已 commit、已測試(全套 1155 預期綠);決策項只有兩個。

## 一、今晚 11 個 commit 的一句話帳

| Commit | 內容 |
|---|---|
| a149040 | World Model v1(GSCPI/GPR 事件引擎 + 曝險 + DNA 整合) |
| 4b288d1 / 4406eaf / 9b63eb7 | ABM 模擬 / 向量案例庫(212 筆)/ UI 世界面板 |
| 896488b / a3b7416 | 排程全自動化 + 曝險地圖 v2→v3(網證:SIVEF 出台鏈、ANET 入、AVGO 升 A 級) |
| dd08bdd / b29f1a0 / 6a43957 | 本地模型線 + Risk 佇列 / collect 懸掛修復 / 審計工件 |
| ba84b4a / 1e8fca3 | **夜班 wave1**:時間旅行回放 + regime 轉移表 + 行為偏差層 + 整合 |
| 2a390ca / 009e195 / e85821b | wiki index 補齊 / **wave2** UI+collect 優先級 / 免費層阻斷記錄 |
| (本檔同 commit) | GSCPI_SPIKE 規則升級 + reset-thin + 本決策文件 |

## 二、頭條發現(27 年回放,synthetic-revised vintage)

**GSCPI_SPIKE 是 1999 年以來唯一明確跑輸基準的世界事件**(QQQ 前向 6m 中位
−0.18% vs 基準 +8.37%,n=27)。TS_HIGH(46 個月)從不低於基準。
→ 世界觀修正:**恐懼是噪音,供應鏈實質壓力才是訊號** — 而 GSCPI_SPIKE 現在正觸發。

已動作(標注晨間覆核):`config/world_events.json` GSCPI_SPIKE 升 **cap ×0.85 +
曝險罰則 0.15**(_basis 引回放數據)。**TS_HIGH 未下調** — 理由:歷史均值不低於
基準 ≠ 尾部安全(27 年樣本內沒發生過封鎖;TS_HIGH 的衝擊錨定 ABM 尾部情境
TS_BLOCKADE −10pp,不是均值)。今日疊加後 cap 乘數仍 = min(0.75, 0.85) = 0.75,
**實際 sizing 無變化**;變化在 TS_HIGH 解除後 GSCPI 單獨觸發的日子。

其他:行為偏差 **8.5/10**(mania 過度自信警語首次實彈開火);下月態展望
mania 64%/bull 27%/bear 9%(無條件層 n=44 — mania×高地緣的歷史先例近乎不存在)。

## 三、晨間決策 #1:下市票分母(失敗類比的誠實化)

**問題實證**(三連 probe):Polygon 免費層對 2 年窗外下市票回 **0 根**(ABMD 實測);
yfinance 已清空下市票;Stooq 有 JS 反爬牆。→ **免費層下分母回填不可能**,
今晚掃的 570 個 too_short 全是假象。

| 方案 | 成本 | 得到什麼 | 風險/備註 |
|---|---|---|---|
| **A. Polygon Starter** | **$29/mo**(可單月) | 5 年歷史窗 → 2021 後下市票可收;一個月衝刺即可回填一批真亡者,然後降回免費 | 5 年窗仍收不到 2015-16 油氣熊的死者(那要 Developer $79);**升級日先跑 `python -m sharks.backtest.failed_analogs reset-thin`** 清假條目(已備好,2 tests) |
| B. yfinance+Stooq 混合 | $0 | — | **已否證**(0 根/JS 牆),不建議再花時間 |
| C. 維持現狀 | $0 | 74.1% 維持「倖存者上界」標注,cap 取悲觀端 11% | 誠實但分母永遠不長 |

**建議**:A 的單月衝刺($29 一次性)— 正是 plan.md「偶爾付費驗證」的標準場景;
收完一批 2021+ 死者就能第一次算出含真亡者的存活率。

## 四、晨間決策 #2:GSCPI_SPIKE 規則升級覆核

上面第二節的 config 變更(cap ×0.85 / 罰則 0.15)依 [[../philosophy/08-risk-and-position]]
屬 Risk Officer 轄區 — 同意則不用動,否決則 revert `config/world_events.json` 一個 hunk。

## 五、今早自動發生的事(不用你動手)

07:40 SharksDNA-Morning(週六):完整鏈 + **存活率全量重算** + **回放/轉移表週更首跑**
+ 案例庫 sync;brief 會帶今晚全部新區塊。儀表板 `python -m sharks.ui.server` 看 🌍 面板。

## 六、已知開口(不急)

ANET 站點級組裝對映、china_revenue 兩層拆分(Risk Officer 裁決)、ARM/設備商月度復查、
Ollama 開機後本地研究線即可用(`python -m sharks.ai.research_agent --ticker COHR`)。
