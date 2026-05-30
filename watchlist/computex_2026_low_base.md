---
type: watchlist
tags: [computex-2026, low-base, long-short, architecture-proposal, tax-defense, external-spec]
title: COMPUTEX 2026 低基期多空伏兵 + 跨界整合規格（外部提案，待對帳）
as_of_timestamp: 2026-05-31T10:00:00+08:00
author_role: researcher
status: watchlist
source: "External integration spec pasted by principal 2026-05-31 (likely another LLM). Captured per principal request; NOT adopted wholesale — see §0 reconciliation."
schema_version: 1
---

# COMPUTEX 2026 低基期多空伏兵 + 跨界整合規格

> 依 principal 指示「創新檔儲存、不動現有 code/working tree」存入此外部規格。
> **這不是已採納的決策**——本檔是「待對帳的外部提案」。交易決策仍以 `$hark`
> 憲法 ([[../sharks]]) + [[../philosophy/concepts/evidence-gated-rebalance]] 為準。

---

## §0. 對帳 / Reconciliation（誠實標註：本規格與已 commit 決策的衝突）

這份外部規格與本 session 已 commit、且經 Reviewer-2 嚴格論證的決策**有數處直接衝突**。
原封照搬會違反 [[../CLAUDE]] §3「矛盾不可靜默覆蓋」。逐項標記，**採納前必須重訪**：

| 外部規格主張 | $hark 既定決策 | 裁決 |
|---|---|---|
| **TimescaleDB / ClickHouse** 存時序 | **DuckDB over Parquet**（Reviewer-2 明確否決 TimescaleDB；見 ai-quant proposal） | ❌ 衝突 — 不採 TimescaleDB；單機單人用 DuckDB |
| **Pinecone / Milvus** 向量庫 | **本地 file-based RAG**（BoW/BGE，無外部向量庫）；`src/sharks/ai/rag_library.py` | ❌ 衝突 — 單人不需雲端向量庫 |
| **Kafka / Redis Pub/Sub** 事件總線 | 低頻單機刻意保持簡單；無訊息總線 | ⚠ 過度工程 — 低頻不需要;Phase 6+ 再議 |
| **高頻 LightGBM / DeepLOB** 預測 | principal 反覆指示**低頻、以週為單位、不過多操作** | ❌ 衝突 — 違反低頻指令 |
| 情緒分數直接餵 **LightGBM/XGBoost** 訓練 | **LLM-pollution protocol**（docs/LLM-BACKTEST-PROTOCOL.md）警告 closed-loop 污染 | ⚠ 危險 — 須走 §11 防污染閘 |
| **670 萬**海外所得免稅線 | **已更正為 750 萬**（AMT 基本所得額；見 memory + wiki personal） | 🔴 **事實錯誤** — 是 750 萬不是 670 萬 |
| CPCV 取代 Walk-Forward | 我們的 IC 研究用 walk-forward + train/test split（已驗證有效） | ✅ 可並存 — CPCV 是好補強，非取代 |
| 波動率目標 wᵢ=σ_target/σᵢ | 與 `philosophy/08-risk-and-position` 相容 | ✅ 採納 — 純 Python 數學，不讓 LLM 算 |
| LLM 降為「特徵工程師」、嚴格 JSON 輸出 | 與 evidence-gate + macro_analog BANNED_OUTPUT_KEYS 一致 | ✅ 採納 — 本就是這個方向 |
| 做空排除 mktcap<$10B 或 SI>20% 迷因股 | `philosophy/06-exclusions` 可加此條 | ✅ 採納 — 防軋空，好規則 |

**結論**：架構層（Kafka/TimescaleDB/Pinecone/DeepLOB）對單機低頻系統**過度工程且與已定決策衝突**，不採；演算法護欄層（結構化 JSON、情緒連續化、波動率目標、做空排除、CPCV）**多數採納**；**670→750 萬是必須修正的事實錯誤**。

---

## §1. COMPUTEX 2026 多空伏兵（6/2–6/5）— 時效性交易觀察

> 篩選邏輯：尚未創歷史新高、基期低、剛啟動的台美股。**這是 watchlist / 觀察，非買單**；
> 每檔仍須過 [[../philosophy/concepts/evidence-gated-rebalance]] 十足的證據閘 + 倉位上限。

### 🟢 多頭佈局桶（價量起漲 + 基本面）

| 標的 | 量化面 | 基本面催化 | 可掃? |
|---|---|---|---|
| **宇隆 2233**（台股） | 週線長期橫盤、剛放量突破平台、20/60MA 黃金交叉初升 | 傳統車件 → AI 機器人伺服馬達/減速機；首設「AI 機器人專區」 | Phase-2 suffix |
| **欣興 3037 / 南電 8046**（台股） | 一年縮量築底、距高點極遠、剛站上年線、主力吸籌 | AMD Helios + 新世代 GPU 晶片面積/層數↑ → ABF 載板幾何級數消耗；落後補漲 | Phase-2 suffix |
| **Synaptics SYNA**（美股） | 日線 W 底、距 52 週新高仍遠、動能臨界黃金交叉 | COMPUTEX 實體參展 Astra™ AI-native 嵌入式晶片；雲端→邊緣 (Edge AI) 受惠 | ✅ US-listed |
| **Astera Labs ALAB**（美股，補列） | （待補 20/60MA） | AI 連接/retimer 供應鏈 | ✅ US-listed |
| **上銀 2049**（台股，補列） | （待補 20/60MA） | 機器人減速機/線性傳動 | Phase-2 suffix |

### 🔴 空頭/警戒桶（情緒過熱 + 九轉竭盡）

| 標的類型 | 量化面 | 情緒面 | 操盤 |
|---|---|---|---|
| 一線水冷/散熱**妖股** | 日/週線 TD-9 連續見 9、近 3 日漲但量縮（價量背離）、距 52 週高 <1%、乖離過高 | KOL/媒體集體喊單、情緒分數逼近 1.0 極端超買 | 展中利多見報但不漲反跌＝「利多兌現」→ 多單分批止盈、破 5MA 建標準 Put |

> 做空紀律（[[../philosophy/06-exclusions]] 待加）：嚴禁融券放空 mktcap<$10B 或 SI>20% 迷因股（防軋空）；空頭優先大型權值股 Put 或產業反向 ETF。

---

## §2. 架構升級提案（外部，§0 已標衝突 — 採納前重訪）

**事件驅動拓撲**（外部建議；本系統低頻暫不採 Kafka/Redis 總線）：
數據感知層 → 時序庫(外部建 TimescaleDB / **本系統用 DuckDB**) + 向量庫(外部 Pinecone / **本系統用本地 RAG**) → 訊息總線 → 大腦層(LLM 情緒連續化 −1..1 文本因子) + 量化/執行層(模型 + NemoClaw 熔斷)。

**採納的演算法護欄**：
- LLM 降為特徵工程師、`Pydantic/Instructor` 嚴格 JSON、情緒 −1.0..1.0 連續化 → 當 Alpha 文本因子。**但須過 LLM-pollution 閘**（docs/LLM-BACKTEST-PROTOCOL.md）。
- TD-9 雙重驗證（[[../philosophy/concepts/td-9-sequential]] 待加）：TD-9 ∧ 量縮 ∧ 情緒過熱 → Short/Put；TD-9 ∧ 爆量 ∧ 基本面上修 → Hold/續抱。
- 波動率目標 wᵢ = σ_target/σᵢ（σ_target 例 15%，σᵢ 由 GARCH/歷史算）— 純 Python，不讓 LLM 算浮點。
- CPCV（組合對稱淨化交叉驗證）補強現有 walk-forward + train/test。

---

## §3. 個人長線財務/稅務「防空洞」(2026–2030) — 指標摘要 + 私密指標

> ⚠ **隱私邊界**：詳細債務/薪資/RSU 數字屬**私密**，存於 `D:/DOT/finance/`（永不入 git）。
> 本檔（$hark git-tracked，雖 local-only）只記**交易/排程相關的可公開原則** + 修正項，
> 不複製敏感數字。詳見 `D:/DOT/finance/01_financial_profile`。

**可記錄的原則（與交易排程相關）**：
- **借新還舊**：400 萬信貸 5 年→7 年(84 期)，月付 ~$75K→~$53K，釋放 ~$22K/月現金流。2026 年做完最安全（聯徵查詢到 2030 房貸時已沖淡）。
- **RSU vest 當天賣**：vest 日資本利得=0，稅務單純化；變現現金流砸最高利率最長期信貸本金（= 無風險保證報酬）。
- **ESPP $97 成本 loss-harvest**：2026 同年實現非-NVDA 套牢虧損 ⟺ 賣 $97 ESPP，海外盈虧同年互抵。
- 🔴 **修正**：免稅線是 **750 萬基本所得額**（AMT），**不是規格寫的 670 萬**。所有 12 月熔斷門檻請依 750 萬重算（規格的「逼近 600 萬就停」需上修）。
- **三戶分離**：房屋頭期戶(SGOV/美元定存，神聖不可動) / 還債戶(股權變現挹注) / Alpha-交易 sleeve(高壓期上限暫設極低)。
- **12 月控流熔斷**：11 月底核算今年已實現海外 Capital Gain，逼近免稅線(750 萬)即停 12 月變現窗口、剩餘 ESPP 移隔年 2 月窗口攤平。

> 此節與 [[../philosophy/concepts/return-horizon-structure]] 的「Alpha sleeve ≤5%、不上槓桿」一致；
> 高壓期 Alpha 上限暫設極低 = 與 sleeve_classifier 的飆股 20% 上限**在現階段更保守**。

---

## See also
- [[../philosophy/concepts/evidence-gated-rebalance]] — 每檔伏兵進場前的證據閘
- [[../philosophy/concepts/return-horizon-structure]] — 三/四 sleeve 架構
- [[../philosophy/concepts/moonshot-hunter]] — 散熱妖股 = 純炒作無證據的反面教材
- [[../tech/index]] — SYNA(Edge AI) / ABF 載板 / CPO 的 DD 層
- [[../philosophy/06-exclusions]] — 做空排除(待加 mktcap/SI 條款)
- `D:/DOT/finance/` — 個人財務防空洞詳細數字（私密、不入 git）
- [[../CLAUDE]] — §3 矛盾標註規則（本檔 §0 即依此而作）
