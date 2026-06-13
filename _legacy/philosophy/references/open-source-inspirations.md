---
type: reference
tags: [inspiration, open-source, architecture, borrow-list]
title: Open-Source Inspirations
author_role: human
---

# Open-Source Inspirations

The 8 open-source projects whose architecture or implementation patterns this system explicitly borrows. Cross-referenced with `docs/INSPIRATIONS.md` (the implementation-side notes — when to integrate, which module ports).

Source: Gemini-side discussion (see `D:\DOT\$hark\gemini.md`).

---

## 1. `Ss1024sS/LLM-wiki` (GitHub)

**Fit**: ★★★★★

A Python implementation of the Karpathy LLM Wiki pattern. Enforces "Compile-first" and "Writeback" as architectural constraints.

**What we borrow**: the Compile-first runtime that reads `raw/` and writes to `wiki/` with structural awareness (entity merge, contradiction flagging). Phase 2 ports this into `src/sharks/compile/`.

**Phase**: 2.

---

## 2. `OpenClaw` + `Awesome Finance Skills`

**Fit**: ★★★★☆

OpenClaw provides a multi-agent SubAgent / Agent Teams architecture. The Finance Skills package adds source aggregators (華爾街見聞, 財聯社, Polymarket, Twitter / KOL feed).

**What we borrow**: the SubAgent-as-intel-collector pattern. Phase 3 deploys a Macro SubAgent (Fed / Trump / antitrust) and a KOL SubAgent (filtered Twitter / Telegram feeds), each writing to `raw/` only.

**Phase**: 2 (intel collectors) + 3 (SubAgent orchestration).

---

## 3. `AI4Finance-Foundation/FinRobot`

**Fit**: ★★★★☆

A multi-agent AI finance platform with automatic Equity Research Report generation.

**What we borrow**: the report-generation templating that consolidates fundamental analysis into a structured deliverable. Phase 3 adapts this for `wiki/02_mag7_bottleneck.md` quarterly re-generation per [[../concepts/supply-chain-bottleneck]].

**Phase**: 3.

---

## 4. `sdchen53/Sleipnir`

**Fit**: ★★★★★

Debate-driven heterogeneous multi-agent stock operations framework. Features:
- Time-Aware RAG (chronologically-bound retrieval)
- Dual-frequency operation (low-freq for US equities + high-freq for crypto)
- Dynamic Router that allocates different LLMs to different reasoning tasks (cost optimisation)

**What we borrow**: the Time-Aware RAG enforces the [[../09-point-in-time]] discipline at the retrieval layer. The Dynamic Router pattern maps directly to our [[../07-mode-switch]] mode logic. Phase 3 ports both.

**Phase**: 3.

---

## 5. `TauricResearch/TradingAgents`

**Fit**: ★★★★★

Multi-agent framework simulating a top-tier Wall Street research operation. Implements distinct agent roles:
- Fundamental Analyst Agent
- Technical Analyst Agent
- Sentiment Analyst Agent
- Risk Management Team

The Trader Agent triggers a structured Debate among the analysts before any position decision.

**What we borrow**: the role decomposition maps almost 1:1 onto our four-dimension taxonomy ([[../02-signal-taxonomy]]). The Debate pattern resolves dimension conflicts in a way that complements our matrix-based arbitration. Phase 3 implements the Risk Management Team as our Risk Officer ([[../CLAUDE]]).

**Phase**: 3.

---

## 6. `FinStep-AI/ContestTrade`

**Fit**: ★★★★★

Multi-agent trading system explicitly designed to resist LLM noise sensitivity (KOL pump dynamics, short-term sentiment swings). Architecture:
- **Data Team**: compresses incoming news / K-lines / indicators into structured Text Factors (avoids LLM context blow-up)
- **Research Team**: parallel decision-making with internal Authentic Market Feedback scoring; only top-historical-accuracy agent outputs reach the final decision

**What we borrow**: the Data Team / Research Team split is the cleanest answer to our [[../09-point-in-time]] release-time-normalisation problem. Phase 3 imports the compression layer; Phase 4 adapts the Authentic Market Feedback scoring for our walk-forward backtest.

**Phase**: 3 (Data Team) + 4 (Research Team scoring).

---

## 7. `mariostoev/finviz` (Python finviz library)

**Fit**: ★★★☆☆

Unofficial Finviz screener / parser. Allows direct programmatic invocation of Finviz screeners (e.g., `Screeners(filters={'20MA': 'Cross over 60MA', '52W High': '0-10% below'})`).

**What we borrow**: drop-in screener client. Phase 2 wraps this into our `src/sharks/data/finviz_client.py` with point-in-time discipline added on top (Finviz returns "current" — the client must caveat and timestamp).

**Phase**: 2.

---

## 8. `awoo424/algotrading`

**Fit**: ★★★★☆

Algorithmic trading repo combining technical analysis + macro indicators + news sentiment.

**What we borrow**:
- VADER sentiment scoring on news headlines + KOL feeds (Phase 4)
- Multi-source feature fusion (technical + sentiment) into the backtest engine (Phase 4)

**Phase**: 4.

---

## Integration map (the borrow stack)

```
Your $hark module                ←──── Borrowed from
1. Compile-first runtime         ←──── Ss1024sS/LLM-wiki
2. Intel SubAgents (macro/KOL)   ←──── OpenClaw + Awesome Finance Skills
3. Equity research generator     ←──── FinRobot
4. Time-Aware RAG + Dynamic      ←──── Sleipnir
   Router (mode switching)
5. Four-dimension analyst        ←──── TradingAgents
   debate
6. Noise-resistance compression  ←──── ContestTrade
7. Finviz screener client        ←──── mariostoev/finviz
8. Sentiment + technical fusion  ←──── awoo424/algotrading
```

## Borrowing discipline

- **License compatibility**: every borrow must check the upstream license. If GPL, the borrowed code stays in a clearly-separated module; if MIT / Apache, freely integrated.
- **Attribution**: each module that ports upstream code carries a `# Adapted from <upstream-url>` line at the top.
- **No silent copy-paste**: every borrow is read, understood, adapted to Sharks' point-in-time and source-grading discipline before integration. Phase 2-4 work is integration, not copy.
- **Upstream tracking**: when an upstream project ships a relevant update (e.g. Sleipnir adds a new mode), the Phase 5+ review checks whether to backport.

## See also

- `docs/INSPIRATIONS.md` — implementation-side mirror of this page, with phase-specific module names and integration tests
