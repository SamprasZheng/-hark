---
type: thesis-watch
tags: [thesis, agentic-payments, fintech, stripe, visa, mastercard, paypal, coinbase, mcp, a2a, x402, crypto]
as_of_timestamp: 2026-06-08
author_role: human
source: principal-directive
---

# Agentic 支付 / 代理人支付 — 金融科技下一個變革?(含 MCP/A2A/x402 之爭)

> 主理人(2026-06):Stripe + AI 代理電商 = 機器人支付/代理人支付,還帶點 crypto。若這是
> 潮流、下一個熱點,PayPal/Block/Coinbase/傳統信用卡銀行該怎麼佈局?他們有機會嗎?
> 而 MCP / A2A / x402 到底誰佔最後大餅?

recommend-only 研究。已建 `/basecross payments`、`/rally payments`、`/stealth payments`。
(協議/產品細節變化快,以官方為準;不確定處已標。)

## 底層邏輯:AI 代理會自己買東西 → 需要「機器付款」層
電商是第一個引爆點(代理幫你逛/比價/下單)→ 緊接著就是**付款**:代理要能**自主授權、付款、
對帳**。這催生「agentic commerce + agentic payments」整套基建。重點變革:
- **從「人點按結帳」→「代理代為付款」**:需要新的**授權/憑證/額度/可稽核**機制。
- **微支付 / 按次付費**(代理呼叫 API、買資料)→ 傳統刷卡手續費不划算 → **穩定幣**有空間。

## 三層協議(常被當成對手,其實是不同層,互補)
| 協議 | 誰 | 解決什麼 | 類比 |
|---|---|---|---|
| **MCP** | Anthropic | 代理↔工具/資料 連接(已被 OpenAI/Google/MS 採用) | AI 工具的 USB-C |
| **A2A** | Google(捐 Linux 基金會) | 代理↔代理 溝通協作 | 代理間的網路協定 |
| **x402** | Coinbase | 代理付款(HTTP 402 + USDC 穩定幣按次付) | 機器的「付費閘門」 |
| **AP2** | Google + 60 夥伴(MC/Amex/PayPal/Coinbase) | 代理支付授權框架,**同時支援卡 + 穩定幣/x402** | 代理付款的「規則書」 |
| **MPP** | **Stripe + Tempo** | Machine Payments Protocol:Stripe 自己的**機器/代理支付協定**,走 **Tempo(穩定幣 L1)** 結算 | Stripe 想**自己掌軌**,不只串卡 |

> **MPP(Stripe+Tempo)的戰略意義(主理人 2026-06 補)**:Stripe 從「整合卡」走向「**自己擁有
> 結算軌**」——Tempo 是 Stripe/Paradigm 系的穩定幣鏈,MPP 讓代理用穩定幣按次付。這**直接
> 挑戰** x402(Coinbase/USDC)與卡組織的「資金層」,把代理支付變成**多軌競爭**:
> 卡組織(信任/高額)vs Stripe-Tempo-MPP(穩定幣原生)vs Coinbase-x402-USDC(crypto 原生)。
> 含義:① 機器/微支付這塊**穩定幣軌勝面升高** → 利好穩定幣基建(CRCL/COIN)與「自有軌」的
> Stripe(等 IPO);② 卡組織仍守「高價值 + 信任 + 爭議」場景,不會被一夕取代,但**成長敘事
> 被分食**;③ 多協定並存(按場景分),**贏家仍是坐在結算+分發節點的人**,不是協定本身。
> (細節變化快,以官方為準;本系統無法上網查證。)

**誰吃大餅?我的判斷:不是單一協議贏者全拿,而是「協議商品化管線、價值歸於結算+信任+
分發」**:
- MCP/A2A/x402/AP2 是**互補的開放標準**(工具/協作/付款/授權),會像 TCP/HTTP 一樣**變成
  免費水管**;贏家不是水管本身。
- **真正吃大餅的是坐在「結算 + 信任 + 分發」節點的人**:
  - **卡組織(V/MA)**:提供**信任/憑證/爭議/額度**——代理付款仍需資金來源 + 可信身分。
    他們正主動推 **Visa Intelligent Commerce / MC Agent Pay(+AP2)**,把自己**嵌入**代理流程,
    **不是被取代,是適應**。→ 最穩的贏家。
  - **Stripe(私有,IPO H1'26)**:商戶/代理整合層的領頭,買了 **Bridge(穩定幣)**,
    與 Nvidia 等 AI 端銜接(代理算力 ↔ 付款軌互補)。→ 整合層霸主,但要等 IPO。
  - **Coinbase + USDC(x402)**:**crypto 原生機器支付**的軌(微支付、跨境、免卡費)。
    若機器經濟起來,這是新利基;高 beta、看 crypto 週期。
  - **PayPal**:有代理工具 + Venmo + Honey(購物),但**市佔流失中**,是**落後/轉機**——
    機會在於它能否在代理電商保持相關性,**要證明**。

## 佈局與評估(他們有機會嗎?)
| 標的 | 角色 | 機會評估 | 風險分層 |
|---|---|---|---|
| **V / MA** | 信任/憑證/結算 | **最穩**:主動推 agent-pay、護城河在信任與分發,適應而非被顛覆;高品質獲利 | 低(核心) |
| **AXP** | 卡+客群 | 受惠卡仍是資金層;封閉迴路 | 低 |
| **Stripe**(私有) | 整合層霸主 | 最純 agentic-commerce,但只能等 IPO / 用同業代理 | — (IPO) |
| **COIN / CRCL** | x402 / USDC 穩定幣軌 | **最高賠率**:機器支付+穩定幣若成主流的新軌;但 crypto 週期+監管 | 高(投機) |
| **XYZ(Block)** | 消費/SMB | Cash App+Square,agentic 不是最前排;轉機 | 中 |
| **PYPL** | 落後轉機 | 便宜、有工具,但要證明在代理電商保持相關;**證實前是 value trap 風險** | 中(turnaround) |
| **FI/GPN/FOUR** | 收單/處理 | 賣鏟子,受惠交易量;agentic 是順風 | 中 |

## 結論(佈局原則)
1. **核心壓「信任+結算」= V/MA**(適應者,有燃料=真賺錢),不是賭被顛覆。
2. **投機壓「新軌」= COIN/CRCL**(x402/穩定幣機器支付的選擇權,小倉)。
3. **Stripe 用 IPO 代理 + 同業(V/MA/XYZ)**先佈局,等 IPO。
4. **PYPL 是轉機賭注**:要看到「代理電商相關性」的證據才加碼,否則 🪨 缺燃料。
5. 用系統:`/rally payments` 只取**有燃料 + 連續起漲**的;純敘事的會被打 🚫/🪨。

## 一句話
**協議(MCP/A2A/x402/AP2)會變免費水管;錢流經的「信任+結算+分發」節點(卡組織、Stripe、
穩定幣軌)才吃大餅。** 卡組織最穩、穩定幣軌最高賠率、PayPal 要證明自己。
