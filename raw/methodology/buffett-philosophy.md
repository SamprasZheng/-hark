---
type: source
source_class: methodology_reference
source_grade: A
source_first_visible_at: 2026-05-29T06:00:00-04:00
ingested_at: 2026-05-29T06:00:00-04:00
source_url: chat://principal-andy
topic: warren-buffett-investment-philosophy
tags: [buffett, value-investing, moat, margin-of-safety, 3m, methodology]
---

# Warren Buffett Investment Philosophy (源自 D:\DOT\$hark\buffet.md)

## 6 核心面向

### 1. Graham 「價值投資」三大基石
- **內在價值 (Intrinsic Value)**: 買股票 = 買企業所有權的一部分
- **市場先生 (Mr. Market)**: 情緒化擬人;用價格波動而非被它左右
- **安全邊際 (Margin of Safety)**: 以低於內在價值的折扣買入

早期 Graham 派「**撿煙屁股**」(cigarette butt) — 在市場極度恐慌時以低於清算價格買入。

### 2. Munger 啟發 — 從「便宜貨」轉向「偉大企業」
**「以合理的價格買入優秀的公司,而不是以便宜的價格買入普通公司」**

- 尋找具備「**經濟護城河 (Economic Moat)**」的企業
- 強大品牌、壟斷地位、定價能力 — 例:Coca-Cola, American Express, See's Candies

**3M 法則**:
- **Management** (企業管治)
- **Moat** (護城河)
- **Margin of Safety** (安全邊際)

### 3. 能力圈 (Circle of Competence) + 棒球理論
- 不投資看不懂的技術/行業
- 棒球理論:股市是沒人逼你揮棒的比賽,**耐心等球進甜蜜區**才重手出擊
- **少數但高質量的集中投資**

### 4. 複利思維 (長期持有)
- 「人生就像滾雪球。最重要之事是發現足夠濕的雪和**長長的坡**」
- 重倉股平均持有 > 20 年
- 對好企業的持有期限是「**永遠**」

### 5. 逆反人性
- **「別人恐懼時貪婪,別人貪婪時要恐懼」**
- 1987 股災、2000 dot-com、2008 金融海嘯都手握巨額現金抄底

### 6. 極簡專注
- **80% 時間花在閱讀和思考上**
- 80/20 法則 — 對大多數事情說「不」

---

## 5 個經典案例

### Case 1: American Express (1963 沙拉油危機)
- **危機**: 子公司被騙 $150M,股價腰斬 $60 → $35
- **巴菲特觀察**: 親自去牛排館/銀行/超市,發現消費者照常使用 AMEX
- **品牌特許權 (護城河) 絲毫未損** — 80% 旅行支票市佔
- **操作**: 合夥公司 40% 資金 (~$13M) 重倉
- **結果**: 5 年漲 5 倍

→ **啟示**: 好公司遇到暫時性危機 → 安全邊際 + 大膽入市

### Case 2: Berkshire Hathaway (撿煙屁股錯誤)
- **危機**: 紡織廠瀕臨破產
- **撿煙屁股**: 以 $7/股 (低於營運資本) 買入
- **情緒化錯誤**: CEO 苛扣 $0.125 → 巴菲特大怒重倉收購並開除 CEO
- **後續**: 巴菲特坦承這是**最愚蠢的情緒化決策**
- **轉型**: Munger 建議 — 停止收購劣質公司,改用保險浮存金 (零成本現金流) 收購優質企業

→ **啟示**: 徹底放棄純看資產報表的低價策略;轉向「合理價格買偉大企業」

### Case 3: Washington Post (1973 經濟危機)
- **危機**: 市值僅剩 $88M
- **內在價值估算**: $400-500M
- **「合法壟斷」**: 華盛頓地區報紙獨家地位
- **操作**: $10.6M 買 10% 股份
- **結果**: 持有到 1995 增值至 $400M+,每年股息 $7M

→ **啟示**: 忽略「市場先生」悲觀情緒,運用「內在價值」選股

### Case 4: Coca-Cola (1987 Black Monday)
- **危機**: 股災;1985 「新口味可樂」公關失敗
- **巴菲特觀察**: 失敗的「新可樂」反而證明了消費者對「**原味配方**」極度忠誠
- **操作**: 1988 起重倉,$1.02B (Berkshire 淨資產 30%)
- **結果**: 1991 增值至 $3.74B,每年股息 $6-7B

→ **啟示**: 時間是優秀企業的朋友;定價能力 + 全球品牌忠誠度 = 驚人複利

### Case 5: Apple + BYD + 日本五大商社 (晚年進化)
- **Apple (2016)**: 看穿其本質是「消費品公司」具極強客戶黏性 — 2024 上漲 10×
- **BYD (2008)**: Munger 推薦,HK$8 買入 → HK$350+ (40 倍)
- **日本五大商社 (近年)**: 低本益比 + 高股息 + 多元業務 + 穩定現金流 — 預計持有 ≥ 10 年

→ **啟示**: 即使年邁,能力圈內持續尋找全球被低估的優質資產

---

## 與 $hark FOM 系統的整合

### 對應 FOM 維度

| Buffett 概念 | FOM 維度對應 |
|---|---|
| 護城河 (Moat) | `ip_defensibility` (已有) + `quality` dim (已有) |
| 安全邊際 (Margin of Safety) | `contrarian` dim (已有) — 距 52w 高 + IP |
| 內在價值 | **新增 `buffett_value` dim** — forward P/E vs sector + FCF yield + dividend stability |
| 市場先生 | `bubble_guard` (已有) + 新增 `mr_market_signal` — 情緒極端時觸發 |
| 能力圈 | Hard exclude from universe.yaml (排除自己不懂的) |
| 棒球理論 | persistence boost — 等股票連續多週進 top 50 才入場 |
| 逆反人性 | 已有 contrarian dim;Y2 midterm 期已建框架 |
| 複利長期持有 | 12m bucket (已有,需開啟 enable trigger) |

### Buffett 補充修正

1. **不在能力圈的硬排除**: 加密貨幣以外的衍生品、外幣、商品期貨、複雜結構債 — `philosophy/06-exclusions.md` 已有但要強化能力圈邏輯
2. **「永遠」持有時間**: 對於 Buffett-tier 護城河 + 安全邊際 (IP 90+ AND contrarian 80+) 的標的,12m bucket 之後可標記 `permanent_hold = true` — 跳過 14 月強制 thesis 更新
3. **集中投資**: 當前 [[../../philosophy/05-decision-rubric]] 是 10 訊號分散,但 Buffett 哲學主張集中。Compiler 提案 — **Buffett-tier 標的允許單檔 tier 1 cap 上修到 12%** (從 8%)
4. **市場恐懼時貪婪**: VIX > 35 是當前的「force observation」,但 Buffett 派會在這時 **強制執行 +50% 加倉現有 Buffett-tier 持倉**(只在 VIX 極端時)

→ 待建提案: `philosophy/_proposals/buffett-3m-integration.md`
