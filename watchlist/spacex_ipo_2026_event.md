---
type: event-watch
tags: [event, ipo, spacex, space, catalyst, this-week]
as_of_timestamp: 2026-06-08
author_role: human
source: principal-directive
---

# 事件觀察:SpaceX 上市(本週重點事件)

> 主理人標記(2026-06-08):**SpaceX 上市是這週的重點事件**。

recommend-only 事件追蹤,**不是部位**。以下只記錄「該追蹤什麼」與紀律,不捏造
SpaceX 的 ticker / 定價 / 確切日期(這些以官方公告為準;無確認前一律標 TBD)。

## 為什麼重要(底層邏輯)
- SpaceX 體量極大,IPO 會是**整個太空板塊的情緒與資金催化劑**:不論本身定價如何,
  通常會帶動「太空 / 衛星 / 發射 / 國防航太」這條供應鏈的**題材輪動與成交量放大**。
- 對齊現有論點:這是「**有題材**」那一格——可餵進 `/rally` 的「消息 / 供應鏈」維度。

## 太空價值鏈分層(底層邏輯)— FOM 宇宙 `SPACE` 群,`/basecross space` 可篩
SpaceX = 發射(Falcon/Starship)+ Starlink(衛星寬頻,真正的金礦)。IPO 把整個太空
經濟重新定價,催化**注意力與資金**。按價值鏈分,受惠/競爭關係不同:

| 子板塊 | 標的 | 與 SpaceX 的關係 |
|---|---|---|
| **發射** | `RKLB`(Rocket Lab) | **最純對標**,Neutron 出來直接受惠注意力;真有發射 backlog |
| **衛星通訊 / direct-to-cell** | `ASTS`、`IRDM`、`GSAT`、`VSAT` | **雙面刃**:題材受惠,但 **Starlink 直接競爭**;`IRDM`/`GSAT` 有真營收/合約 |
| **對地觀測 / 數據** | `PL`、`BKSY`、`SPIR` | 受惠注意力;政府/國防數據合約是持續性關鍵 |
| **製造 / 月球 / 政府** | `RDW`、`LUNR` | `LUNR` 有 NASA CLPS 合約營收;`RDW` 靠併購成長 |

> 這些是**相鄰受惠/連動**,不是 SpaceX 本身。多為 **2021-SPAC 在 2022 被殺的倖存者
> = 錯殺大底**——正好吃我們的 `/stealth`(隱蔽吸籌)+ `/basecross`(月線金叉)。
> SpaceX 散戶能不能買、何時、用什麼管道,以官方為準,確認前不做進場假設。

## 持續性 vs 純題材(別把催化劑當買訊)
- **有持續性**:`RKLB`(發射 backlog)、`IRDM`(獲利 satcom)、`GSAT`(Apple 金援)、
  `LUNR`(NASA 合約)、`ASTS`(電信商協議,但仍燒錢、pre-revenue ramp)。
- **純題材/高風險**:多數太空股**燒錢、pre-profit**,IPO 噴完容易回落 →
  `/rally`/`/stealth` 會把無合約、純消息的打成 **🚫 墓園型**。
- **雙面刃**:satcom(IRDM/VSAT/ASTS)被 Starlink 競爭,持續性看**差異化合約**,不是炒題材。

## 怎麼追蹤(用系統現有工具)
```
/stealth space        # 隱蔽吸籌:誰在 IPO 前資金先進、價未動(抓還沒炒上去的)
/basecross space      # 月線大底金叉 + 資金介入(誰真的已表態)
/rally space          # 5 維融合 + 連續起漲才可考慮
/council SpaceX 上市對太空板塊的資金輪動與持續性   # 多人格辯論 + 回寫 wiki 記憶
無 bot:python -m sharks.discord.ecom_screens space   # 一行出四張表
```

## 紀律(別把催化劑當買訊)
1. **事件 ≠ 買點**。IPO 催化的是情緒;進場仍要 `連續起漲 + 有題材撐 + regime/資金面健檢`。
2. **墓園守門**:若相鄰股只是消息面噴出、技術/資金過熱但無實質卡位(供應鏈 design-win /
   訂單 / 盈利),`/rally` 會打成「純炒作·無實證」——不追。
3. IPO 當天波動極大;首日不接刀,等**止穩 + 連續起漲**(對齊 basecross/rally 的判準)。
