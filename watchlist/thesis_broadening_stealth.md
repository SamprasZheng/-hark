---
type: thesis-watch
tags: [thesis, broadening, stealth-accumulation, rotation, rally-pattern, regime-conditional]
as_of_timestamp: 2026-06-08
author_role: human
source: principal-directive
---

# 起漲型態:廣度輪動 × 隱蔽吸籌(抓華爾街還沒炒上去的錯殺股)

> 主理人思路(2026-06-08):週五暴跌但行情可能未完,因為**太多小股票還沒站起來**。
> 現在明顯是 AI 在帶全市場;若擴散到民生消費等其他產業,華爾街會把**錯殺的股票悄悄
> 炒起來**(像今年的 INTC/MU),挑大家沒看到的。**我要抓他們想炒、但還沒炒上去的票。**

recommend-only 研究論點。已建進系統:`/stealth`、basecross `broadening` 群、
`stealth_signal.py`、FOM 宇宙 `BROADENING_LAGGARDS`。

## 兩面判讀(不盲目附和)
- ✅ **多方(廣度輪動)**:領頭(AI/半導體)鈍化時,資金常輪動到**落後的民生/消費/醫療**;
  「小股票還沒動」確實代表還有未走完的廣度。
- ⚠️ **空方(2022 重演的尾部風險,你自己點到)**:若 regime 翻 risk_off、**資金面翻 STRESS**,
  **小型/低流動股會最先死**。所以這套是 **regime-conditional**——不是無腦做多。
- **裁判**:系統的 `regime classifier` + `funding_stress`。資金面沒 STRESS 才放行廣度做多;
  翻了就 default-hold / 減小型曝險(對齊憲法:防守快、進攻需十足證據)。

## 怎麼「抓還沒炒上去的」= 隱蔽吸籌指紋
追高是抓**已經噴**的;你要的是**上游一步**——`/stealth` 找的指紋:
1. **資金先進**:成交量相對放大(有人在收貨)。
2. **價還沒動**:月線**還沒**金叉突破(量進價未動 = 還在吸,不是已表態)。
3. **距高深**:被錯殺、還沒回去(有空間、非近高、非落刀)。
4. **低關注(可選)**:大家還沒看到(越隱蔽分數越高)。
> 刻意 reward「低動能」:已經垂直 = 大家都看到了 = 不隱蔽,分數反而降。

## 候選池(broadening,非-AI 錯殺)
- 民生必需:`KHC CAG CL HSY GIS K KVUE CLX SJM BG`
- 消費非必需落後:`NKE SBUX LULU EL TGT DG DLTR FIVE MCD`
- 醫療錯殺:`PFE MRNA BMY CVS HUM GILD DXCM`
> 加任意代號:`/stealth broadening tickers:XYZ` 或 CLI `python -m sharks.discord.ecom_screens broadening`

## 怎麼跑(bot 上線 → Discord;或無 bot → CLI)
```
/stealth broadening                 # 隱蔽吸籌偵測(預設民生/消費/醫療)
/stealth all                        # 全錯殺池(2022殺+AI錯殺+電商+廣度)
/basecross broadening               # 看誰真的月線金叉了(已表態)
/rally broadening                   # 5維+連續起漲(已啟動的)
無 bot:python -m sharks.discord.ecom_screens broadening   # 一行出四張表
```

## 紀律
1. **隱蔽吸籌是機率、不是內線**:量增可能是換手、避險、被動資金;`/stealth` 只給「疑似收貨」
   的優先序,不是確認。要配 `/basecross`(是否真金叉)+ regime 健檢。
2. **regime gate 第一**:資金面翻 STRESS → 小股票先砍,別逆勢接。這正是你說的「2022 重演」防線。
3. **分批、小倉**:吸籌期波動大、確認度低;對齊憲法「進攻需十足證據」。
