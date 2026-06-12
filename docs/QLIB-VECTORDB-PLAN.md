# Qlib + 向量 DB 引入計畫(阿卡西記憶 v3)

> 主理人指令 2026-06-12:「請安排引入 Qlib 還有向量 DB」。本文件 = 分階段引入計畫
> 與進入條件;`pyproject.toml [akashic]` extras 已預留。原則:**先讓需求長到工具的
> 尺寸,再裝工具** — 60 案例的質心匹配還不需要向量 DB,但成長路徑要先鋪好。

## A. Chroma(向量 DB)— 案例記憶體

**進入條件(任一)**:案例庫 >150 筆;或特徵維度 >15(加入基本面/消息序列後);
或需要「以案例敘事文本檢索」(嵌入 narrative,不只數值特徵)。

分階段:
1. **現狀(已做)**:`rally_dna.discover_bull_cases` 產出結構化案例(JSON in
   outputs/rally-dna-*.json)— 數值特徵質心 + 兩型架構(深殺/淺基)。
2. **v3a — Chroma 本地持久化**:`pip install -e ".[akashic]"`;新模組
   `sharks/memory/case_store.py`:每案例一筆 document(數值特徵 + 觸發當時的
   敘事摘要文本),metadata = {era, sector, size, gain, archetype}。檢索 =
   數值 KNN(現有)∪ 文本相似(新增)。
3. **v3b — 事件/文化層**:把 raw/macro、wiki 事件頁嵌入同庫,案例關聯總經狀態
   (馬可夫四態標籤已可直接當 metadata)。

## B. Qlib(Microsoft 量化平台)— 因子工廠

**進入條件**:要做(a)多因子橫斷面回測(IC/IR 工業級)、(b)walk-forward 自動化、
(c)組合層模擬(倉位上限/換手約束)— 即超出 per-trade 統計的需求時。

風險與前置:
- ~~Windows 原生安裝常炸~~ → **2026-06-12 實測:pyqlib 0.9.7 在 Windows + py3.12
  乾淨 venv 裝好且 import 成功**(wheel 已齊)。剩餘風險降為「workflow 級」:
  數據初始化(qlib bin 格式)與 qrun 全流程未煙測 — 下一步寫 lake→qlib 轉換器
  + 最小 workflow 驗證,通過即解開 pyproject `[akashic]` 的註解。
- 數據餵入:Qlib 自有格式 → 寫 `lake → qlib bin` 轉換器(monthly/daily parquet
  已齊,轉換是純 IO)。
- **LLM-BACKTEST-PROTOCOL 適用**:Qlib 內跑的策略同樣要 rule-based 才有
  headline-KPI 資格。

## C. Danelfin / I Know First(外部 AI 推薦)— 參考訊號層

定位:**D 級來源**(黑箱、不可審計)→ 依 CLAUDE.md §5 只能 inform watchlist,
不能單獨觸發開倉。引入方式:若取得其每日 top list(API/訂閱),作為
`dna_match_today` 的旁證欄位(`external_ai_flags`),交集 = 加分、分歧 = 記錄
不裁決。先不訂閱;等系統自身 alpha 驗證穩定後再評估是否值得花錢買旁證。

## 優先順序(2026-06-12)

1. 案例庫成長(自動發掘已上線,持續累積)→ 觸發 Chroma 進入條件再裝
2. vectorbt 評估(輕量先行)→ Qlib 等組合層需求成熟
3. 外部 AI 旁證最後(花錢買的是 confirmation,不是 alpha)
