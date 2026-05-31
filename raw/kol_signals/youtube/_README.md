# YouTube 來源清單 — KOL / 分析師頻道

> 用途：把各頻道影片網址 dump 成清單，餵給 NotebookLM 或自行轉錄，作為建立
> `$hark/analysts/*` 人格檔的原始素材。
> 產生方式：`yt-dlp --flat-playlist`（2026-05-31 抓取）。
> ⚠️ 數量為當下快照，頻道持續更新。

## 一頁總覽

| 頻道 | 是誰 / 主題 | 語言 | 影片數 | 字幕 | NotebookLM | 對應人格檔 |
|---|---|---|---|---|---|---|
| **a16z** | Andreessen Horowitz 創投，AI/科技/國防/太空/加密 訪談與論壇 | 英 | 1071 | ✅ 自動(en/中) | ✅ 可直接貼 | （新）vc/a16z |
| **bonnieblockchain** | 邦妮區塊鏈，加密 KOL；大量英文大咖訪談(Saylor/Pompliano/Samson Mow/ARK)＋中文解說 | 中英 | 372 | ✅ 自動 | ✅ 可直接貼 | crypto / （新）bonnie |
| **huang** | 黃靖哲分析師．運達投顧，台股「財富指揮官」盤後＋教學，2015–2026 | 繁中 | 3059 | ❌ 無 | ❌ 需轉錄 | [analysts/huang.md] |
| **youtubercrypto** | 比特幣交易，🚨行情/🔥心態/🎖講座/訪談 | 中英 | 1682 | ❌ 無(公開片)；部分會員 | ❌ 需轉錄 | crypto |
| **jiufangwu** | 久方武，總經/哲學/太空/加密 主題投資，巴菲特派；有課程導流 | 中英 | 587 | ❌ 無(公開片)；部分會員 | ❌ 需轉錄 | （新）jiufangwu |
| **andy-sharks** | 鯊魚工作室(Andy)，美股技術面日更，簡中 | 簡中 | 1127 | 未確認 | ⚠️ 多為會員片 | sharks |

## 各頻道檔案

每個頻道都有：
- `<頻道>-urls.txt` — 全部影片網址，一行一個（貼 NotebookLM 用）
- `<頻道>-index.tsv` — `影片ID <tab> 秒數 <tab> 標題`（用來掃標題、挑片）

額外精選（給數量太大的頻道）：
- `huang-curated.md` / `huang-curated-urls.txt` — 從 3059 部中，標題命中其招牌術語/教學關鍵字的 **645 部**（心法、秘技、第一手、缺口、誘多、騙線、底部進場、玻璃基板、量子、13F、巴菲特…）。建人格最該看這批。
- `youtubercrypto-curated.md` / `-curated-urls.txt` — 🎖講座 **6 部**＋訪談 **4 部**（方法論最完整）；另有 702 部 🔥 心態短片在 index 內。

## NotebookLM 使用提醒

1. **來源數上限**：免費版每個 notebook 50 個來源、Plus 版 300 個。`-urls.txt` 動輒上千，**不要整包貼**——用 `-curated` 或自己從 `-index.tsv` 挑。
2. **NotebookLM 吃 YouTube 靠字幕**。無字幕的頻道（huang / youtubercrypto / jiufangwu）匯入大多會失敗或拿不到內容。
   - 這三個頻道要建人格，需先**自行轉錄音訊**（例如本機 Whisper / faster-whisper，你有 RTX 5070）。需要我幫你接這條轉錄 pipeline 再說一聲。
3. ✅ **可直接貼的只有 a16z 與 bonnieblockchain**（有自動字幕、公開）。

## andy-sharks（鯊魚）特別說明

- 抽查發現**相當比例是「會員專屬」**（大鲨鱼会员视频，多為 40–50 分鐘長盤後深析）；公開片多為較短的美股新聞/數據分析。
- 想精準產出「只含公開片」的清單，需逐支探測，但**大量探測會觸發 YouTube 反機器人封鎖**（本次已被暫時鎖 IP）。乾淨做法二選一：
  1. 你登入後提供瀏覽器 cookie（`yt-dlp --cookies-from-browser`）→ 連會員片都能抓；或
  2. 等 IP 冷卻後，我用單執行緒慢速背景探測（約 1 小時）產出 `andy-sharks-public-urls.txt`。
- 目前先交付 `andy-sharks-urls.txt`（全部 1127 部，含會員片；你的下游工具會自動略過抓不到的）。

## 待補 / 已補

- **X.com / Twitter KOL** ✅（2026-05-31 完成）：22 位幣圈/web3 KOL 的「底層邏輯性格」profile 已建檔於
  `../crypto-kol-profiles-2026-05-31.md`＋速查 `../crypto-kol-index.tsv`。
  ⚠️ 刻意放 `raw/kol_signals/`（D 級 sentiment 來源層），**不放 `analysts/`**——`analysts/*` 是會注入 FOM
  加權集成的 persona 檔（`type: analyst-persona`），而這些 KOL 只是情緒源，不該 tilt 股票評分。
  名單已同步進 yxz `kol-tracker`（`D:\DOT\yxz\.claude\skills\kol-tracker\kol-list.yaml`，公開中性版）。
