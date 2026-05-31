---
type: analysis
as_of: 2026-05-31
data_snapshot: crypto/data/top100-2026-05-30.json
tags: [crypto, btc, halving-cycle, institutional-anchor, four-year-cycle, living-doc]
reconciles: [philosophy/concepts/btc-halving-cycle.md, philosophy/concepts/institutional-btc-anchor.md]
---

# 四年週期 + 大機構介入 — live 對帳（living doc）

> 回答你的三句：**四年週期會不會來 / 大機構介入 / 機會與不確定性**。
> 用的是**真實快照**（`data/top100-2026-05-30.json`，`as_of 2026-05-30T18:47Z`），不是腦補。
> 既有兩頁概念（[[../philosophy/concepts/btc-halving-cycle]]、
> [[../philosophy/concepts/institutional-btc-anchor]]）的舊數字在此對帳；矛盾依 wiki 規則
> 標在較舊的頁上。**姿態：de-risk / observation-first（Phase D，不開新多）。**

## 1. live 數據 vs 概念頁（對帳表）

| 項目 | btc-halving-cycle.md（proposal, 2026-05-29） | **live snapshot 2026-05-30** | 判定 |
|---|---|---|---|
| 週期峰值 | 2025-07 月收 **$115,758** | **ATH $126,080 @ 2025-10-06** | ⚠ 頁面**過時**：真正高點更高、更晚（晚 3 個月） |
| 距峰回撤 | **−37%**（到 2026-05） | **−41.3%** from ATH | 頁面偏淺 |
| 峰值倍數 | +72% / **1.7×** from halving | ~+97% / ~1.9× from halving entry (~$64k) | 頁面低估 |
| 現價 | — | **$73,967** | — |
| BTC dominance | （未記） | **58.8%** | 山寨對 BTC 失血中 |
| 供給 | — | 流通 20.04M / 上限 21M（**95.4% 已挖**） | 供給面已近上限，halving 邊際效果遞減 |

**結論一：頁面的峰值/回撤/倍數三個數字都過時**——真正的 cycle 高點是 **2025-10-06 的 $126,080**，
比頁面寫的 2025-07 $115,758 更高、更晚。已在 [[../philosophy/concepts/btc-halving-cycle]] 上標矛盾旗標。

## 2. Falsification trigger：技術上「已觸發」，但屬措辭瑕疵

頁面的 kill-switch：**「BTC 在 h2024 後 36 個月內（2027-04 前）收上 $115,758，且未先經歷 >50% 回撤」**
→ 則四年週期論作廢、cycle bias 歸 0。

逐項對 live：
- ✅ 收上 $115,758 → BTC 達 **$126,080**（2025-10）。
- ✅ 在 2027-04 前。
- ❓ 「未先經歷 >50% 回撤」→ 從 halving（2024-04 ~$64k）到 2025-10 峰是**上升段**，期間並無 >50% 回撤。

**字面上 → trigger 已觸發。** 但這是**措辭瑕疵**：trigger 的*本意*是抓「**熊市之後**不經深熊就收復前高」，
而 $126,080 本身就是這輪的**製造高點**、不是「收復」。它只是「cycle 峰比某個 7 月月收更高」——這幾乎是廢話，
不等於「四年鋸齒被打破」。**真正該問的是：h2024 會不會印出一個 >50% 的 Phase-D 深熊？** 這題**仍未解**
——現在 −41%，打底窗口 **2026-Q4 → 2027-Q1** 還在前方。

**建議修 trigger 措辭**（給人類核可）：改成「**BTC 自 cycle ATH（$126,080）起，在未發生 >50% 回撤的情況下，
重新收上 $126,080**」——這才是「無深熊即復原」的正確定義，且目前**尚未**成立（我們只 −41%）。

## 3. 兩派現況：純減半 vs 機構錨定

| | 純減半派（[[../philosophy/concepts/btc-halving-cycle]]） | 機構錨定派（[[../philosophy/concepts/institutional-btc-anchor]]） |
|---|---|---|
| 核心 | 4 年鋸齒：減半→FOMO→分發→70-85% 崩 | ETF/MSTR 鎖倉壓振幅、底更淺、像高波宏觀資產 |
| 此輪預測 | Phase D 深熊，底 2026Q4-2027Q1，回撤 −70%+ | 底**顯著淺於** −77%/−84% |
| **live 對帳** | 現 −41%，**尚未**到深熊（但窗口在前方） | **−41% < 上輪 −77%/−84%**：到目前為止**偏向錨定派**（單點、弱證據） |
| 確認要看 | 2026Q4-2027Q1 真的崩到 −70%+ | 底落在 ~ −45~−55% 後回升、ETF 淨流入黏著、振幅續壓 |
| 失效（kill） | trigger 修正版成立（無深熊復原） | **流動性斷裂**→相關性歸 1，sticky 持有者被迫賣（[[../philosophy/concepts/funding-chain-rupture]]）；或新散戶狂熱重啟反身性 |

**結論三（機率框架，誠實版）：**
- **到 2026-05 為止，live 數據微微偏向「機構錨定/被馴化」**——本輪做了新高、且回撤（−41%）明顯比前兩輪淺。
- **但這是單一時點、未到打底窗口**。halving 時鐘說底在 2026Q4-2027Q1；若那時崩到 −70%+，純減半派回來、錨定派被證偽。
- **遞減報酬是兩派共識**（24×→6.7×→~1.9×）：無論哪派，**「翻身級漲幅」大概率已經走掉**。這對「想靠 crypto 翻身」是最該認清的一點。

## 4. 對你的部位含意

- **現在是 Phase D（不開新多）**——你自己的模型 + live 回撤都指向「下行段尚未走完」。
- **BTC**：核心宏觀資產、**≤4% 名目硬頂、機械式 DCA**（在 Alpha 之外，per 你 2026-05-30 決定）。若要 DCA，分批往
  2026Q4-2027Q1 的打底窗口擺，**不是現在一次梭**。預設偏「錨定派（上檔壓縮）」→ 倉更小。
- **山寨**：dominance 58.8% + 山寨對 BTC 重貶 → 此 regime 持山寨對 BTC 是輸家。`narrative_rotation` slot 從嚴、多半 null。
- **退出框架 > 進場選股**：若真有下一輪（~2028-29，下次減半 2028），**預先承諾階梯式減碼**，且要趕在 2030 預售屋負債前收割
  ——前提是你**真的會賣**（這是散戶最難的一關）。

## 5. 待辦 / 監控

- [ ] 修 [[../philosophy/concepts/btc-halving-cycle]] 的 trigger 措辭（人類核可）+ 更新峰值表（$126,080 @ 2025-10-06、−41%、~1.9×）。
- [ ] 監控 **Saylor「可能賣 BTC 付股息」**（[[../raw/kol_signals/crypto-kol-profiles-2026-05-31]]）——最大企業買家若轉賣方，
      是錨定派的反向壓力測試，連動 institutional-anchor 的 liquidity-rupture kill。
- [ ] 每日快照追 BTC dominance + 距 ATH 回撤；接近 2026Q4 打底窗口時加密追蹤。
- [ ] （升級路徑）接 on-chain（MVRV / realized price / ETF 淨流入）以更硬地裁決兩派。

## See also
- [[../philosophy/concepts/btc-halving-cycle]] · [[../philosophy/concepts/institutional-btc-anchor]] · [[../philosophy/concepts/multi-scale-cycles]]（BTC 週期僅佔 combined bias 的 0.15 權重——別讓減半敘事在情緒裡膨脹）
- [[dot-postmortem]] · [[watchlist]] · 數據來源 `data/top100-2026-05-30.json`
