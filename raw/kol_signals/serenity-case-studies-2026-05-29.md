---
type: source
source_class: kol_research_compilation
source_grade: B
source_first_visible_at: 2026-05-29T07:00:00-04:00
ingested_at: 2026-05-29T07:00:00-04:00
source_url: chat://principal-andy
secondary_urls:
  - https://rootdata.com (referenced)
  - https://panewslab.com (referenced)
  - https://kucoin.com (referenced)
topic: serenity-classic-case-studies
tags: [kol, serenity, case-studies, chokepoint, supply-chain, axti, sive, aaoi, rpi, soitec]
---

# Serenity Classic Case Studies(原則性整理 2026-05-29)

User-supplied summary of Serenity's most-discussed high-conviction trades.

## 1. AXTI (AXT Inc.) — 「成名之戰」

**Chokepoint**: 磷化銦 (InP) 基板 — AI 光模組 / 光通訊的關鍵材料瓶頸

- **Position**: AXTI 擁有全球 InP 供應鏈重要份額(後續 CEO 表示約 **40%**)
- **Entry**: 股價 ~$12 / 市值 ~$2 億 USD (early WSB long post)
- **Exit**: 股價 $70+ (約 6×),市值最高 > $70 億 USD
- **Catalyst**: AI 資料中心光互聯爆發 → InP 需求暴漲
- **後續**: 被 WSB 版主 ban,但 thesis 被市場驗證,奠定其從 meme trader → 供應鏈研究者的聲譽
- **意義**: 「紫蘇葉理論」的代表作

## 2. SIVE (Sivers Semiconductors) — 「最高信念,討論最多次」

**Chokepoint**: 連續波 (CW) 雷射光源 — Co-Packaged Optics (CPO) / 矽光子學的關鍵 chokepoint

- **Position**: SIVE 被定位為 **Jabil、Ayar Labs、Wiwynn、Celestial (後被 Marvell 收購)、O-Net** 的重要供應商
- **Entry**: 推薦時市值約 **$130M - $290M USD**
- **Exit (running)**: 市值從低點暴漲近 **19×**,最高 > $23 億 USD
- **Catalysts**: 2026 多次 — Nasdaq 納入 / CHIPS Act 資金 / 客戶訂單 / M&A 訊號
- **Bullish Thesis**: 列出 > 15 個正面 catalysts,看 **2027 CPO 超級週期**
- **持倉態度**: Serenity 多次公開強調此為**最高信念持股**,並計劃增持

## 3. AAOI (Applied Optoelectronics) — 「最快複合成長」

**Chokepoint**: 光收發器全供應鏈 (雷射 → 設計 → 組裝 → 銷售)

- **Position**: AI 光模組需求受益者
- **Entry**: 低點 ~$20-30 區間
- **Exit (running)**: 最高漲幅 **> 5× (部分報導 5.1×)**
- **Thesis**: 預期 **2027 H2 光收發器營收大幅躍進**
- **Position in Serenity's narrative**: 列入「最快複合成長」名單

## 其他高勝率案例

| Ticker | Chokepoint Thesis | Result |
|---|---|---|
| **RPI (Raspberry Pi)** | 需求激增 thesis;財報 +58% YoY revenue growth | 短線大漲 |
| **SOI (Soitec)** | 矽光子基板 (SOI substrate) 壟斷型「最安全長線」持股 | **數百% 漲幅** |
| **VLN** (Valens Semiconductor) | 追蹤組合;AI 光子學 / 化合物半導體 | Multi-bagger |
| **NBIS** (Nebius Group) | AI infra (former Yandex 業務分拆) | Multi-bagger |
| **LPKF** (LPKF Laser & Electronics) | German laser systems for SiPh / advanced packaging | (新提) |
| **SMOL** (?) | (需查驗 ticker;可能 SMCI 的衍生詞,需 Compiler 確認) | TBD |

## 共同模式總結 — 「Serenity Playbook」

1. **早期低估值 + 結構性瓶頸**: 市值多在 **$100M-$300M** 級別,市場尚未關注
2. **Catalyst Verification**: 客戶訂單 / 產能協議 / 政策支持 (CHIPS Act) / 指數納入 / M&A
3. **Timeframe**: **非短期炒作** — 看 **1-2 年甚至更長**的 AI 基礎設施超級週期
4. **Reinforcing trend**: 不可逆趨勢 (光互聯取代銅線)
5. **Overall pattern**: 多倍回報 (5-20×);2 年總體回報極高

## 風格描述

「科學家級供應鏈偵探」:**不追熱門大廠,而是抓「少了它就卡住」的隱形環節**

## 整合進 $hark 系統

### 對應到 FOM 維度

| Serenity 元素 | $hark FOM 對應 |
|---|---|
| 結構性瓶頸 (chokepoint) | [[../../philosophy/concepts/supply-chain-bottleneck]] |
| 早期低估值 | `contrarian` + 加入 `market_cap_filter` (排除 > $5B) |
| Catalyst verification | [[../../philosophy/02-signal-taxonomy]] news 維度 |
| 1-2 年時間框架 | [[../../philosophy/01-time-horizon]] 12m bucket |
| 「不追熱門大廠」 | `fom_alpha.py` 變體 排除 mega cap |

### 整合計畫

- **新建 `src/sharks/scoring/serenity_scout.py`** — 篩選符合 Serenity playbook 的標的:
  - market_cap ∈ [$100M, $3B]
  - sector in {Semiconductors, Photonics, Compound Semis, AI Infra}
  - revenue growth YoY ≥ 30% (proxy: 12m return as proxy where revenue data unavailable)
  - low analyst coverage (Phase 2+: Finnhub coverage data)
  - has named chokepoint thesis (Compiler-tagged in CHOKEPOINT_DB)

- **CHOKEPOINT_DB** 內建已知名單:
  - AXTI: InP substrate
  - SIVE: CW laser / CPO
  - AAOI: optical transceiver supply chain
  - SOI: SiPh substrate
  - NBIS: AI infrastructure
  - LPKF: laser systems for advanced packaging
  - VLN: compound semi
  - RPI: SBC / IoT compute
  - 新候選 (Compiler 待 verify): RPID, AOSL, IIVI/COHR (already large), QUIK, GFS

### 「Find the next AXTI/SIVE」 framework

當前 chokepoint 已被市場發現的標的(AXTI/SIVE/AAOI)現在已經漲完,**不適合再進**。Serenity Scout 的目標是**找下一個**:

**Filter pipeline**:
1. **Universe**: small-cap US-listed semis/photonics (~ 100-300 tickers)
2. **Stage 1 — chokepoint flag**: 屬於某個 AI supply chain 上游 (SiPh / power semi / advanced packaging / specialty materials / compound semi / RF)
3. **Stage 2 — valuation**: P/B ≤ 3 OR P/S ≤ 5 (low valuation)
4. **Stage 3 — momentum yet absent**: 12m return between -20% and +50% (not parabolic, not crashing)
5. **Stage 4 — catalyst pipeline**: any of (CHIPS Act exposure / new customer announcement / capacity expansion / patent filing / management talent moves)
6. **Stage 5 — Compiler qualitative score**: 0-100 「Serenity-fit」 score
7. **Output**: top 10 candidates with full thesis writeup

### 操作風險提醒

- Past performance ≠ future results — Serenity's hit rate on his TOP picks is high but his overall track record may include misses
- 19× / 6× / 5× returns are HEAVILY survivor-biased — for every SIVE that worked, there are 10 similar names that didn't
- 這些 small caps **流動性差 + bid-ask spread 寬** — entry/exit 成本高
- Borrow availability for shorting these names is poor — 不可作 short hedge
- 系統 [[../../philosophy/06-exclusions]] 的 market cap floor 對 tier 3 是 $1B — Serenity-tier 標的可能低於這個 floor,需要 **臨時 floor 例外清單** approved by Risk Officer

## See also

- [[../../raw/kol_signals/serenity-aleabitoreddit-profile-2026-05-29]] — 主 KOL profile
- [[../../philosophy/concepts/supply-chain-bottleneck]] — 框架
- [[../../wiki/03_alpha_library]] §H — Serenity 三階段 rotation framework
- 未來: `src/sharks/scoring/serenity_scout.py` (即將寫)
