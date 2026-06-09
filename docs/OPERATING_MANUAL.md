# PolkaSharks 操作手冊 / 導覽(把專案當 ERP/MES 來用)

一句話:**這是一條「事件 → 篩選 → 品管閘 → 決策 → 執行 → 閉環記憶」的生產線**。
你只負責**進料(提出題材/事件)**和**執行(下單)**;中間的研究、篩選、紀律、記憶由系統跑。
recommend-only,系統永不下單。

---

## 一、事件/議題出現後的標準流程(像 ERP/MES 的工單流)
每當一個**新題材或事件**出現(新聞、IPO、你的點子、一張截圖),走這 7 關:

```
進料 → 研究分類 → 篩選(生產) → 品管閘 → 排程決策 → 執行 → 記錄閉環 → 反饋維護
 0        1            2            3          4          5         6           7
```

| 關 | 名稱(ERP/MES 類比) | 做什麼 | 指令/工具 | 產出 |
|---|---|---|---|---|
| **0** | 進料(收料) | 把事件/題材灌進系統 | `/ingest <文字/網址>`、`#知識注入` | `wiki/inbox/*.md` |
| **1** | 研究分類(BOM/工藝) | 拆價值鏈、找上市代理、定題材池 | `/council <主題>`、`/notebook`、`/ask` | `watchlist/thesis_*.md` (+ 新 scope) |
| **2** | 篩選(MES 生產線) | 三段訊號:吸籌→金叉→起漲 | `/stealth` → `/basecross` → `/rally`(+ Finviz API) | 候選 + 🟢🟡🔵🪨🚫 |
| **3** | 品管閘(QC) | 燃料閘 + regime 閘 + 墓園閘 | 內建於 `/rally`;`/feedback`、health-check | 只放行 🟢(有燃料+連續起漲+regime OK)|
| **4** | 排程決策(MRP/排程) | 分層、定量、定時 | `weekly_plan_q3_2026.md`、`deployment_plan_*.md`、`/ecomrank` | 本週要動的標的+倉位 |
| **5** | 執行(人工) | **你**分批下單、設認賠 | (系統永不下單) | 部位 + 認賠線 |
| **6** | 記錄閉環(稽核軌跡) | 議會結論回寫、連續起漲存檔 | 議會自動回寫 wiki、`rally-state-*.jsonl` | 下一輪的記憶 |
| **7** | 反饋維護(持續改善) | 績效節流、重掃、更新論點 | `/feedback`、`/rescan fom`、更新 watchlist | 校準後的下一輪 |

> 閉環:**第 6 關的記憶 → 餵回第 1 關(議會記憶)+ 第 2 關(rally streak)** → 越跑越準。

---

## 二、模組地圖(系統由哪些「子系統」組成)
| 子系統 | 檔案 | 職責 |
|---|---|---|
| 議會(研究/決策) | `discord/council.py` + `council_memory.py` | 多人格 立場→交叉質詢→投票→結論,結論回寫 wiki 記憶 |
| 篩選引擎 | `discord/basecross.py` | 月線大底金叉 + 資金介入;**所有題材池(scope)在此** |
| 起漲融合 | `scoring/rally_signal.py` | 五~九維融合 + 連續起漲 + **燃料閘(regime)** + 暴漲股 DNA |
| 隱蔽吸籌 | `scoring/stealth_signal.py` | 資金先進、價未動(抓還沒炒上去的) |
| 抄底起漲 | `discord/dipbuy.py` | 日線版(距高+盈利+起漲) |
| 資料源 | `data/finviz_elite.py` | Finviz Elite API(token 只在 .env)→ 9 維精準數據 |
| 換股節流 | `discord/feedback.py` | 績效強不換股+深挖支撐;真反轉才換 |
| 選股核心 | `scoring/fom.py` | FOM 全宇宙 quality 評分(225+ 檔宇宙)|
| 無-bot CLI | `discord/ecom_screens.py` | 一行跑四張表(不靠 Discord)|
| 知識庫 | `wiki_rag.py` + `wiki_ingest.py` | 本地 RAG / 灌知識 |

---

## 三、指令總覽
### Discord(bot 上線後)
**研究/議會**:`/council <主題>` · `/persona <名> <訊息>` · `/ask` · `/notebook` · `/ingest`
**篩選(帶 scope)**:`/stealth <scope>` · `/basecross <scope>` · `/rally <scope>` · `/ecomrank` · `/dipbuy`
**決策/維護**:`/feedback [perf]` · `/rescan [fom|signals|health|all]` · `/picks` · `/meeting`
**導覽**:`/guide`(本流程)· `/playbook`(市場儀表板)· `/cmd`(教學)· `/status`(版本)· `!sync`(同步指令)

### CLI(無 bot,有網路即可)
```
python -m sharks.data.finviz_elite <preset|f=...>     # Finviz 拉精準數據(.env 放 token)
python -m sharks.discord.ecom_screens <scope|tickers> # 四張表:綜合排名/起漲/隱蔽吸籌/月線金叉
python -m sharks.scoring.fom                          # FOM 全宇宙重掃
```

### scope(題材池)— `<scope>` 可填
`space`(太空/SpaceX)· `ipo`(2026 IPO 代理)· `payments`(agentic 支付)· `crypto`(Web3)
· `ecommerce` / `ecommerce_small`(電商)· `ai_software`(AI 錯殺軟體)· `killed2022`
· `broadening`(廣度民生/消費/醫療)· `diversified` / `midrisk`(跨產業轉機)· `all`
(也可 `tickers:AAPL,NVDA` 丟任意代號)

---

## 四、文件索引(知識庫)
**論點(watchlist/)**:`playbook_master.md`(總表)· `weekly_plan_q3_2026.md`(每週)
· `deployment_plan_jun_sep_2026.md`(分批)· `thesis_2026_ipo_wave.md` · `spacex_ipo_2026_event.md`
· `thesis_agentic_payments.md`(含 MCP/A2A/x402/MPP)· `thesis_crypto_cycle_2026.md`
· `thesis_ecommerce_agentic.md` · `thesis_broadening_stealth.md` · `thesis_diversified_turnaround.md`
· `dxyz_premium_special_situation.md`
**底層邏輯(docs/)**:`regime_breadth_principle.md`(燃料閘)· `finviz_screening_recipe.md`
· `ipo_wave_dotcom_analog.md` · 本檔 `OPERATING_MANUAL.md`

---

## 五、維護例程(像系統運維)
| 週期 | 做什麼 |
|---|---|
| **每日** | 看 #雜談/議會;有事件 → 走第 0–1 關(ingest + council) |
| **每週(SOP)** | `finviz_elite` 拉數據 → `ecom_screens <scope>` → 只動 🟢 → regime 健檢 → 記錄認賠線 |
| **每月** | `/rescan fom` 重掃宇宙(更新 quality);檢視/精簡 watchlist;校準燃料閘門檻 |
| **安全** | Finviz/Discord token 只在 `.env`(gitignored);外洩即 Regenerate;每次 commit 掃 token |
| **bot** | 改碼後 `git pull + restart_bot.ps1`;`/status` 看 code 版本、`!sync` 同步指令 |

---

## 六、新增一個題材的最短路徑(範例)
1. `/ingest <該題材的新聞/連結>` → 進 wiki。
2. `/council <題材> 的價值鏈、持續性與盈利分層` → 多人格辯論 + 回寫記憶。
3. 若是會重複用的題材 → 在 `basecross.py` 加一個 scope 群(+ 鏡像到 `fom.py` 宇宙)。
4. `/stealth <scope>` → `/basecross <scope>` → `/rally <scope>` → 只留 🟢。
5. 排進 `weekly_plan` 的當週;分批執行、記錄。
6. 結論回寫 wiki → 下一輪自動有記憶。
