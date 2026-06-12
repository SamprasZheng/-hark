# $hark DNA 引擎架構(v3,2026-06-12)

> 設計原則:**演進不翻修** — v3 五層藍圖映射到既有 `sharks.*` 模組,不做 big-bang
> 改名(983+ 測試與既有管線不付翻修稅);新模組按層歸位。可審計性 > 聰明。

## 五層映射(藍圖 → 現有模組)

| 層 | 職責 | 模組 |
|---|---|---|
| **1. Data(Raw + PIT)** | 不可變輸入、PIT 對齊 | `data/data_lake`(離線湖 + info lint)、`data/polygon_financials`(filing_date 錨點)、`data/pit_merger`(Polygon×yfinance FCF 合併)、`data/finviz_elite`(現況快照,**非歷史真相源**)、`raw/`(immutable) |
| **2. Feature & Memory** | 案例庫、特徵、質心 | `backtest/rally_dna.discover_bull_cases`(60+ 案例自動發掘)、`dna_features`(統一特徵尺)、`case_fingerprint`;Chroma 進入條件見 `QLIB-VECTORDB-PLAN.md` |
| **3. Model & Scoring** | 匹配、九維、反身性 | `rally_dna.dna_match_today`(雙型質心 + SHAP 式分解 + 最相似案例)、`scoring/reflexivity`、`scoring/rally_signal`(9 維)、`scoring/fom` |
| **4. Decision & Risk** | 規則、分桶、sizing、狀態機 | `config/dna_rules.json` + `apply_rules`(宣告式,human_review)、`regime_markov4`(四態)、健檢 `ui/server.holdings_health`、`backtest/portfolio_audit` |
| **5. Execution & Audit** | 呈現、排程、留痕 | `ui/server`(dashboard)、`daily_dna_routine`(早晚排程 + 艙位 brief)、`outputs/dna-scores-log.jsonl`(前瞻校準)、`wiki/log.md`(裁決留痕) |

## 關鍵設計決策(與理由)

1. **權重 = 顯式先驗,非擬合**:Finviz 維度無歷史快照 → 任何「歷史擬合權重」皆假。
   敏感度監測(Spearman ≥0.86)+ 評分落盤前瞻校準是唯一誠實路徑。
2. **PIT 錨點 = filing_date**:回測與案例對齊用申報日,杜絕財報前視(philosophy/09)。
3. **規則引擎宣告式**:`config/dna_rules.json` 改規則不改程式;每筆輸出帶 `rules_fired`
   (可審計);邊緣案例(HUM 型 PIT 翻案)→ `human_review=True` 而非機器硬裁。
4. **狀態感知權重**:mania 態自動提高 reflexivity 權重(0.10→0.15)。
5. **LLM-BACKTEST-PROTOCOL**:headline KPI 全 rule-based;LLM 只設計規則不進迴圈。

## 依賴採用準則(先讓需求長到工具的尺寸)

| 工具 | 進入條件 | 現狀 |
|---|---|---|
| pydantic | 對外 API/多人協作時 | dict schema + 測試夠用 |
| Chroma | 案例 >150 或文本檢索 | 60 案例,質心夠用 |
| Qlib | 組合層回測需求 | **Windows 可裝可 import(實測 0.9.7)**;先 vectorbt 評估 |
| structlog | 多進程除錯痛點出現 | `dna-routine-log.txt` + wiki/log 夠用 |

## 風險登記簿(Risk Register)

- **倖存者偏差**:宇宙=今日 FOM universe;deep-kill 型缺 failed-analogs 子庫
  (同形態死掉的案例)→ 真實存活率未知,**靠分倉上限(≤10-15%)防禦,非靠估計**。TODO。
- **HUM 型季節性污染**:年度 FCF 讀數被單季(保險 Q4)扭曲 → PIT 季度翻案規則已上線。
- **MC iid 尾巴低估**:P(DD≥30%) 偏樂觀;曝險跟狀態不跟點估計。
- **Finviz 維度 None**:消息欄未接通(權重已移除);Polygon news 為候選源。
- **yfinance FCF 回填僅 ~6 季**:更深歷史的 FCF 需 Polygon 明細科目(標準化表無 CapEx)。

## 審計工件(每筆裁決可回溯)

`outputs/dna-scores-log.jsonl`(評分史)· `outputs/dna-routine-log.txt`(排程史)·
`wiki/log.md`(變更與裁決)· `rules_fired` per row(規則觸發鏈)· raw/(immutable 輸入)
