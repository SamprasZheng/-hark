---
type: thesis-watch
tags: [thesis, turnaround, diversified, non-tech, beaten-down, return-vs-risk]
as_of_timestamp: 2026-06-08
author_role: human
source: principal-directive
---

# 跨產業分散轉機股 15 檔(不只科技;兼顧潛在收益與風險)

> 主理人指示(2026-06-08):重新篩選、**不要只挑科技股**,給 15 檔 + 基本介紹。

recommend-only 研究**候選池**(非部位、非個人化建議)。用 `docs/finviz_screening_recipe.md`
的「收益濾鏡 × 風險濾鏡」邏輯,跨產業挑「**錯殺大底 + 有真生意/現金流/股息當地板**」。
本環境無即時價,以下為**結構性候選**(分散在不同產業以分散風險),非已確認訊號——
真正的金叉/距高/連續起漲請用 `/basecross diversified`、`/stealth diversified`、
`/rally diversified` 或 CLI 確認。

## 為什麼挑這些(收益 × 風險)
- **收益**:都從高點被打趴一段(有反彈空間),不是貼著高點。
- **風險**:刻意挑**有真營收/獲利/股息**的大中型,而不是會歸零的微型殭屍股 →
  深跌時有「存活地板」,這正是你 Finviz 篩出一堆 <$5 殭屍股缺的那一塊。
- **分散**:橫跨必需消費/醫療/零售/品牌/媒體/材料/工業/金融/太空/汽車 →
  不押單一產業、不重押科技。

## 第一梯|低風險(防禦、有股息/現金流當地板)
1. **KVUE**（必需消費）— Kenvue,J&J 分拆的消費保健(Tylenol/Listerine/Neutrogena),
   品牌穩、配息,上市後被打趴 → 防禦型轉機。
2. **PFE**（醫療/大藥廠）— Pfizer,COVID 退潮後重摔,高股息、估值低,看新藥/腫瘤管線。
3. **TGT**（零售)— Target,大型量販被打趴,Dividend King(連續多年加息),有真獲利。
4. **NKE**（品牌/消費)— Nike,運動龍頭品牌被殺,資產負債表強,管理層轉型。
5. **KHC**（必需消費)— Kraft Heinz,估值便宜、高股息,Buffett 持股,典型價值。
6. **CVS**（整合醫療)— CVS Health,藥局+保險+PBM 被錯殺,便宜、有股息。

## 第二梯|中風險(週期/轉機,有真生意)
7. **SBUX**（餐飲)— Starbucks,被打趴,新管理層轉型,品牌+現金流仍在。
8. **DIS**（媒體)— Disney,串流+樂園轉機,IP 護城河深,獲利改善中。
9. **EL**（美妝/必需消費)— Estée Lauder,中國拖累重摔,高端品牌,賭中國/庫存修復。
10. **ALB**（材料/鋰)— Albemarle,鋰價崩深跌的週期股,靠規模存活,賭電動車/鋰週期。
11. **MMM**（工業)— 3M,訴訟利空打趴後轉機,多元工業+股息。

## 第三梯|高賠率高風險(轉機未定/槓桿/成長)
12. **PYPL**（金融/Fintech)— PayPal,被殺、估值低但仍獲利,賭支付轉型(屬偏科技)。
13. **RKLB**（太空/工業)— Rocket Lab,太空最純成長股,有發射 backlog,但 pre-profit。
14. **F**（汽車)— Ford,便宜、高股息的週期車廠,賭電動/利率,風險在景氣。
15. **WBD**（媒體)— Warner Bros Discovery,深跌、**高槓桿**媒體,賭拆分/去槓桿,風險最高。

## 更多中風險(週期/公司轉機,有真營收,轉機未證實)— `/basecross midrisk`
跨金融/醫療/工業/材料/通訊/汽車/能源,刻意分散:
16. **C**（金融/大型銀行)— Citigroup,低於淨值的多年重整轉機,有真獲利,賭重整見效。
17. **BIIB**（生技)— Biogen,阿茲海默劇情打趴,有真營收,賭新藥/管線。
18. **MDT**（醫材)— Medtronic,被打趴的醫材龍頭,股息+成長再加速論點。
19. **DE**（農機/工業)— Deere,農業下行週期的週期股,強護城河、撐得過週期。
20. **LYB**（化工/材料)— LyondellBasell,週期化工低谷,高股息,賭景氣回升。
21. **FCX**（銅/材料)— Freeport-McMoRan,銅週期股,槓桿電動化/銅需求。
22. **CMCSA**（通訊/媒體)— Comcast,便宜的有線+NBCU+寬頻,有真 FCF+股息。
23. **APTV**（車用零件)— Aptiv,被打趴的車用電子/ADAS 內容股,週期+內容成長。
24. **GM**（汽車)— General Motors,便宜+回購的週期車廠,EV 選擇權。
25. **SLB**（油服/能源)— Schlumberger,被打趴的油服龍頭,國際/海域上行,真現金流。
26. **DPZ**（餐飲)— Domino's,被殺的特許加盟龍頭,賭同店回升。
27. **GPC**（汽配/零售)— Genuine Parts,汽車/工業零件分銷,Dividend King 被打趴。

## 怎麼跑(系統定生死)
```
/basecross diversified     # 誰真的月線大底金叉 + 資金介入
/stealth diversified       # 誰資金先進、價未動(隱蔽吸籌,最早)
/rally diversified         # 5 維融合 + 連續起漲才可考慮買入(+ 墓園守門)
無 bot:python -m sharks.discord.ecom_screens diversified
```

## 紀律
1. 這是**候選池不是買單**:進場由系統金叉/連續起漲 + regime 健檢確認。
2. **風險分層**:第一梯當底、第三梯只用小倉/投機;別把高賠率當核心。
3. **regime gate**:資金面翻 STRESS → 週期/高槓桿(ALB/F/WBD)先砍。
