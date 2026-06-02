---
type: synthesis
domain: tech-trend
tags: [ai-coding, agentic-coding, claude-code, codex, cursor, copilot, swe-bench, value-capture, wrapper-risk, winners-losers]
as_of_timestamp: 2026-05-31T02:30:00+08:00
author_role: researcher
phase: B
confidence: 0.78
verdict: 結構
verdict_by_horizon: {T0: 質變, T1: 結構, T2: 結構/質變, T3: open}
rubric: {A1: 2, A2: 2, A3: 2, A4: 1, A5: 2}
sources_grade_summary: "A: 4  B: 9  C: 4  D: 0  E: 0"
---
# AI 編碼代理戰爭 — Claude Code vs Codex vs Cursor / The Agentic-Coding War

## 0. 一句話判決 + 桌面觀點 / Verdict + desk view
**結構 (conf 0.78).** Agentic coding is the single most *monetized, capability-validated* AI agent use-case on the board — it is a real 質變, but the equity edge sits with the **model labs + the platform-distribution layer**, NOT the pure IDE wrapper. Two facts anchor everything: (a) coding is the highest-revenue agent category — Claude Code alone hit **>$2.5B run-rate by Feb 2026** and is ~4% of *all* public GitHub commits worldwide [1]; OpenAI's ~$6B Q1'26 revenue was explicitly "boosted by Codex" [9]. (b) The capability frontier is a *tight cluster at the top* (GPT-5.5 88.7% vs Claude Opus 4.8 88.6% SWE-bench Verified [2]) — no durable model moat, which is exactly why value will not stay trapped in any one model.
**Desk view (caveated, not advice):** the labs win the war; coding is their cash cow and their best agent-RL flywheel. The **wrapper (Cursor) is a real business but a structurally fragile one** — it grew 0→$2B ARR in 3 years [3] yet must pay its own suppliers (Anthropic/OpenAI) who *also ship competing CLIs at flat-rate subsidized prices*. Cursor's survival bet is vertical integration (its own Composer model [12]). Sharpest falsifier of the bull-wrapper case: Cursor was **negative gross margin on individual devs** and only reached *slight* GM profitability via cheaper models (Composer + China's Kimi) [4][12] — the classic thin-margin reseller signature. Microsoft is quietly conceding the same by moving Copilot to **token-based billing in June 2026** because flat-seat economics broke [11]. Investable conclusion: own the **labs (private) / the platform (MSFT)**; the listed-equity 抄底 is the *picks-and-shovels under all of them* (compute/memory), not the editor.

## 1. 技術底蘊 / Technical moat (A1 = 2 — agentic capability + harness design)
The 質變 is **long-horizon agentic coding**: an agent that plans, edits across a repo, runs the terminal, reads test output, and iterates autonomously — not autocomplete. Capability is now benchmark-validated and *saturating near the top*:
- **SWE-bench Verified (real GitHub-issue resolution):** GPT-5.5 **88.7%** (Apr 23 '26) ≈ Claude Opus 4.8 **88.6%** ≈ Opus 4.7 **87.6%** — a <2pt spread among leaders [2][2b]. A "Claude Mythos Preview" reportedly hit 93.9% but is preview-grade [2b].
- **Terminal-Bench 2.0 (agentic tasks in a real shell — the harness-level test):** top cluster GPT-5.5 ~82–84.7% across harnesses; **Codex CLI + GPT-5.5 = 82.2%**; top harness "vix"+Opus 4.7 = 90.2% [5]. The leaderboard explicitly separates *harness* (Claude Code, Codex CLI) from *raw model* — and **harness design adds real points**: Claude Code reportedly lifts Opus to ~80.9% SWE-bench vs lower raw-model scores in weaker frameworks [5b].
**The paradigm split that matters for value capture:** the **CLI-agent** (Claude Code, Codex CLI, Gemini CLI) is lab-owned and model-native; the **IDE-plugin** (Cursor, Copilot, Windsurf) owns the developer surface. Claude Code vs Codex head-to-head: Claude Code led on autonomy/agentic coding for ~18 months (Anthropic's coding dominance dates to Sonnet 3.5, Jun '24 — see [[model-leadership-and-data]]); Codex closed the gap hard with GPT-5.5 (now #1 on raw SWE-bench [2]) and broader OS reach (Computer Use on Windows [Codex docs]). **A1=2:** the capability is real, hard, and validated — but it is *replicable across labs within a quarter*, so the moat is the RL-data/distribution flywheel, not a static algorithm.

## 2. 需求數據 / Demand reality (A2 = 2 — label Q vs FY, ARR vs revenue)
| 指標 Metric | 數值 Value | 期間 Period | 來源 Source (grade) |
|---|---|---|---|
| Claude Code **run-rate revenue** | **>$2.5B** (doubled since Jan'26) | as of Feb 2026 | [1] (A, Anthropic official) |
| Claude Code share of all public GitHub commits | ~4% | Feb 2026 | [1] (A) |
| Claude Code enterprise share of its own revenue | >50%; biz subs 4× since Jan'26 | Feb 2026 | [1] (A) |
| Cursor (Anysphere) **ARR** | **~$2B** (0→$2B in ~3yr, fastest B2B ever) | Feb 2026 | [3] (B) |
| Cursor ARR forecast | >$6B | end-2026 (proj.) | [3] (B) |
| Cursor gross margin | *slight* GM-positive; **negative on individual devs**, positive on large enterprise | Apr 2026 | [4] (B) |
| GitHub Copilot **paid subscribers** | **~4.7M** (+~75% YoY) | Jan 2026 | [6] (B) |
| MSFT 365 Copilot paid **seats** (all Copilot, not just code) | ~15M (+160% YoY) | Q2 FY26 | [7] (B) |
| Codex weekly developers | ~4M | Apr 2026 | [8] (B, OpenAI help) |
| OpenAI Q1'26 revenue ("boosted by Codex") | ~$6B (quarter) | Q1 2026 | [9] (B, The Information) |
| Windsurf ARR at Cognition acquisition | $82M (ent. ARR doubling QoQ) | Jul 2025 | [10] (B) |
| Devin (Cognition) ARR | $1M (Sep'24) → $73M (Jun'25) | 2024–25 | [10] (B) |
**Read:** demand is *realized P&L*, not survey intent — this is the strongest A2 in the Phase-B set. Coding burns the most tokens of any agent use (an intensive Claude Code dev = $1,000+/mo API [9b]; Uber exhausted its 2026 AI budget in 4 months as Claude Code adoption went 32%→84% of 5,000 engineers [9b]). That token-intensity is *why* coding is the labs' top revenue line — and why it's a margin trap for flat-rate wrappers.

## 3. 資金與權威背書 / Capital & authority (A3 = 2)
Capital is voting at unprecedented scale, and it is voting for the **labs over the wrappers**: Anthropic closed a **$65B Series H at a $965B valuation (May 28 '26)** — explicitly "revenue exploded thanks to Claude Code," $47B run-rate, eclipsing OpenAI ($852B, $122B raise, Mar'26) to become the most valuable AI startup [13][13b]. That is a ~2.5× re-rate from the $380B Series G (Feb'26) [14] — *coding is the named accelerant on the most valuable AI company on earth*. Wrapper-tier capital is also massive but explicitly *defensive*: Cursor raising ~$2B at **$50B** (a16z + Thrive, Nvidia strategic; Apr'26) [3]; Cognition (Devin+Windsurf) in talks at **$25B** [10b]. Authority/primary backing: Anthropic's own funding release is the A-grade source for Claude Code metrics [1]; OpenAI Codex rate-card/pricing is primary [8]. **A3=2:** heaviest capital + primary-filing backing in the cluster.

## 4. 誰捕獲價值 / Who captures value (A4 = 1) — 受益 / 受損 / 抄底
**受益 (CAPTURERS — own the model or the distribution):**
- **Model labs (Anthropic / OpenAI — private).** Coding is their single highest-revenue agent category and their best agent-RL data flywheel. Anthropic's coding lead is the clearest durable moat in [[model-leadership-and-data]]. *They capture first.*
- **Microsoft / GitHub (MSFT — listed).** Distribution moat: Copilot bundled into the M365 + GitHub install base (~90% of Fortune 100); 4.7M paid code seats + 15M total Copilot seats [6][7]. The platform layer survives even as model leadership rotates — it just swaps the model underneath.
- **Nvidia (NVDA — listed, indirect).** The token-burn of agentic coding ($1k+/dev/mo [9b]) is the most inference-intensive agent workload → flows to compute + HBM ([[memory-supercycle]]). *The pick-and-shovel under every player above.*

**受損 / on-notice (LOSERS):**
- **Stack Overflow** — the canonical casualty: posts −90% vs 2020 peak; 84% of devs now use AI tools but *trust* in AI accuracy fell to 29% (from 40%) [15][16]. Q&A-as-product is structurally eaten (detail in [[ai-eats-software]]).
- **The pure IDE wrapper (Cursor) — contested, not dead.** Bear case: it pays suppliers who undercut it with subsidized flat-rate CLIs; negative GM on individuals [4][11]. Bull case: 0→$2B ARR, real enterprise switching costs, agent-orchestration UX, and a vertical-integration hedge (Composer model on Kimi K2.5 [12]). **A4=1** *because* the value-capture verdict is genuinely split: distribution+model are clear winners, but whether the wrapper is durable or disintermediated is the open question — and Cursor's own-model pivot is a tacit admission the reseller model alone doesn't hold.
- **Junior/outsourced dev labor & low-code** — agentic coding compresses the junior-task and boilerplate tier (ties [[ai-eats-software]] §6).

**抄底 candidates (research-only, not advice):** the listed proxies are the *infrastructure under all coding agents* — **MSFT** (distribution that survives model rotation) and the **compute/memory chain (NVDA + HBM names in [[memory-supercycle]])**. The "wrapper" itself (Cursor/Cognition) is private and, on current margins, the *least* investable layer of the stack.

## 5. 多時程 / Multi-horizon
- **T0 (now):** 質變 — realized. Claude Code leads enterprise/autonomy; **Codex (GPT-5.5) leads raw SWE-bench** [2]; Cursor leads IDE distribution; Copilot leads enterprise seats. Capability clustered <2pt apart.
- **T1 (1–3y):** 結構. Value concentrates to labs + MSFT distribution. Wrappers either vertically integrate (own model) or get squeezed on margin. Pricing migrates flat-seat → token/usage (Copilot June'26 [11]) — the same seat→outcome migration seen sector-wide ([[ai-eats-software]] §6).
- **T2 (3–5y):** 結構/質變. Autonomous multi-file agents handle a majority of routine PRs; the dev role shifts to spec/review (consistent with the 84%-use / 29%-trust gap [16] — humans stay in the loop as reviewers).
- **T3 (5–10y):** open. If a lab achieves a *durable* coding-capability gap (not the current <2pt cluster), it could vertically integrate the whole stack and disintermediate every wrapper. If capability stays commoditized, distribution (MSFT) wins the rent.

## 6. 爆發條件 + 里程碑階梯 / Milestone ladder (falsifiable, weekly-trackable)
1. **SWE-bench Verified progression** — verify: swebench.com / tbench.ai monthly. Status: leaders 88–[redacted]%, preview ~94% [2][5]. Next check: does any model break a *durable >5pt* lead (would re-open A1 moat)? **Falsifier:** sustained gap → labs disintermediate wrappers.
2. **Cursor ARR vs gross margin** — verify: TechCrunch/Bloomberg/The Information funding coverage. Status: $2B ARR Feb'26, *slight* GM, $6B ARR guided end-26 [3][4]. **Falsifier of bull-wrapper:** if ARR grows but GM stays negative on the core dev tier → reseller trap confirmed.
3. **Claude Code as % of Anthropic revenue** — verify: Anthropic releases / The Information. Status: >$2.5B run-rate, ~8% of $30B+ run-rate, >50% enterprise [1][13]. Next check: does the % rise (coding = durable cash cow) or plateau?
4. **Copilot token-billing transition (June'26)** — verify: GitHub pricing pages, Microsoft FY26 earnings. Status: announced June'26 [11]. **Falsifier of flat-seat economics:** confirms even the platform can't subsidize flat seats → usage pricing is the end-state.
5. **Enterprise coding-agent penetration** — verify: Menlo State-of-GenAI, earnings call mentions. Status: coding the single largest enterprise app category (~$4.0B FY25, Menlo [[ai-eats-software]]); Uber 32%→84% [9b].
6. **Model-vs-wrapper value-capture verdict** — verify: does Cursor's Composer reach cost-parity & wean off Anthropic/OpenAI, OR do labs' CLIs (Claude Code/Codex) take IDE share? Status: Composer 2 shipped on Kimi K2.5 [12]; Claude Code is "Cursor's main rival" per its own investors [4].

## 7. 時代影響與交互 / Era impact & interactions
Agentic coding is the *spearhead* of [[ai-eats-software]] — both the **supply-side cost collapse** (building software is now agent-assisted) and the **demand-side substitution** (Stack Overflow [15]). It is the **highest-monetized expression of [[model-leadership-and-data]]** — Anthropic's coding dominance is the single durable moat in an otherwise converged model field, and the RL-data from coding agents feeds back into model quality. Token-intensity links directly to [[memory-supercycle]] (inference demand) and the [[../wiki/07_ai_bubble_audit]] (is the $965B/$50B capital ahead of realized margin?).

## 8. 同溫層 + 自我打臉 / Echo-chamber + self-rebuttal
**Echo-chamber gap (precise):** the dev-Twitter consensus is *"Cursor is the inevitable winner, it's the new IDE."* The financials say the opposite about *durability*: Cursor is **GM-negative on its core individual-dev product** [4] and its biggest rival is its own supplier's CLI [4]. The narrative prices Cursor as a platform; the P&L reads like a thin-margin reseller racing to build a model before its suppliers undercut it. **Conversely**, the bear-Twitter *"wrappers are dead, just use Claude Code"* over-extrapolates: Cursor still printed $2B ARR with real enterprise GM and switching costs — distribution UX is a moat too.
**Self-rebuttal of my own desk view (labs win):** (1) capability is a <2pt cluster [2] — if it *stays* commoditized, the model is the commodity and the **distribution layer (MSFT/Cursor) captures the rent**, not the labs — my "labs win" call inverts. (2) The labs' coding revenue is partly *subsidized land-grab* (flat-rate plans burning compute) — the same flat-seat economics that broke for Copilot [11] could compress lab coding margins too; ARR ≠ profit. (3) Anthropic's $965B / Cursor's $50B embed years of capture that MIT-NANDA-style ROI data ([[ai-eats-software]] §7) hasn't fully validated — front-loaded on spend, lagging on returns. **Flag:** the capability verdict is solid; the *value-capture* verdict (A4=1) is the genuinely contested call.

## Sources
1. Anthropic Series G release — Claude Code >$2.5B run-rate, 4% of GitHub commits, >50% enterprise — https://www.anthropic.com/news/anthropic-raises-30-billion-series-g-funding-380-billion-post-money-valuation — retrieved 2026-05-31 — grade A — primary-fetched
2. SWE-bench Verified May 2026 leaderboard (GPT-5.5 88.7%, Opus 4.7 87.6%) — https://www.marc0.dev/en/leaderboard — retrieved 2026-05-31 — grade B — cross-confirmed
2b. SWE-bench Verified 48-model board (Opus 4.8 88.6%, Mythos preview 93.9%) — https://benchlm.ai/benchmarks/sweVerified — retrieved 2026-05-31 — grade C — cross-confirmed
3. Cursor/Anysphere $2B ARR Feb'26, raising $2B at $50B (TechCrunch) — https://techcrunch.com/2026/04/17/sources-cursor-in-talks-to-raise-2b-at-50b-valuation-as-enterprise-growth-surges/ — retrieved 2026-05-31 — grade B — primary-fetched
4. Cursor crossroads — negative GM on individuals, Claude Code as main rival, Composer plan (Fortune) — https://fortune.com/2026/03/21/cursor-ceo-michael-truell-ai-coding-claude-anthropic-venture-capital/ — retrieved 2026-05-31 — grade B — cross-confirmed
5. Terminal-Bench 2.0 leaderboard (Codex CLI+GPT-5.5 82.2%, harness vs model) — https://www.tbench.ai/leaderboard/terminal-bench/2.0 — retrieved 2026-05-31 — grade A — primary-fetched
5b. Coding-agent harness comparison (Claude Code lifts Opus to ~80.9%) — https://artificialanalysis.ai/agents/coding-agents — retrieved 2026-05-31 — grade C — single-source-pending
6. GitHub Copilot ~4.7M paid (+75% YoY) — https://windowsforum.com/threads/microsoft-copilot-hits-15-million-paid-seats-and-4-7-million-github-subscribers.400630/ — retrieved 2026-05-31 — grade B — cross-confirmed
7. Microsoft 15M paid Copilot seats +160% YoY (Q2 FY26) — https://creati.ai/ai-news/2026-02-10/microsoft-copilot-15-million-paid-seats-160-percent-growth/ — retrieved 2026-05-31 — grade B — cross-confirmed
8. OpenAI Codex rate-card / ~4M weekly devs / token billing (primary) — https://help.openai.com/en/articles/20001106-codex-rate-card — retrieved 2026-05-31 — grade B — primary-fetched
9. OpenAI ~$6B Q1'26 revenue "boosted by Codex" (The Information) — https://www.theinformation.com/articles/openai-held-1-billion-revenue-lead-anthropic-first-quarter — retrieved 2026-05-31 — grade B — single-source-pending(paywall)
9b. Coding = highest token-burn agent use; Uber 32%→84% Claude Code (SaaStr/analysis) — https://www.saastr.com/anthropic-just-passed-openai-in-revenue-while-spending-4x-less-to-train-their-models/ — retrieved 2026-05-31 — grade C — cross-confirmed
10. Cognition acquires Windsurf; Windsurf $82M ARR, Devin $1M→$73M (TechCrunch) — https://techcrunch.com/2025/07/14/cognition-maker-of-the-ai-coding-agent-devin-acquires-windsurf/ — retrieved 2026-05-31 — grade B — cross-confirmed
10b. Cognition (Devin+Windsurf) in talks at $25B valuation — https://pulse2.com/cognition-ai-coding-startup-in-funding-talks-at-25-billion-valuation/ — retrieved 2026-05-31 — grade C — single-source-pending
11. Microsoft moving Copilot to token-based billing June'26 (Where's Your Ed At) — https://www.wheresyoured.at/exclusive-microsoft-moving-all-github-copilot-subscribers-to-token-based-billing-in-june/ — retrieved 2026-05-31 — grade B — primary-fetched
12. Cursor Composer 2 built on Kimi K2.5, code-only, lower cost (the-decoder) — https://the-decoder.com/cursor-takes-on-openai-and-anthropic-with-composer-2-a-code-only-model-built-to-match-rivals-at-a-fraction-of-the-cost/ — retrieved 2026-05-31 — grade B — cross-confirmed
13. Anthropic $65B Series H at $965B, eclipses OpenAI, "Claude Code" named (CNBC/Bloomberg) — https://www.cnbc.com/2026/05/28/anthropic-open-ai-startup-value.html — retrieved 2026-05-31 — grade B — primary-fetched
13b. Anthropic $965B / OpenAI $852B valuation crossover (Bloomberg) — https://www.bloomberg.com/news/articles/2026-05-28/anthropic-raises-at-965-billion-valuation-eclipsing-openai — retrieved 2026-05-31 — grade B — cross-confirmed
14. Anthropic $380B Series G (Feb'26) re-rate baseline — https://venturebeat.com/technology/anthropic-says-it-hit-a-30-billion-revenue-run-rate-after-crazy-80x-growth — retrieved 2026-05-31 — grade B — cross-confirmed
15. Stack Overflow posts −90% vs 2020 peak (Similarweb/SO) — https://www.similarweb.com/blog/insights/ai-news/stack-overflow-chatgpt/ — retrieved 2026-05-31 — grade B — cross-confirmed
16. Stack Overflow 2025 Dev Survey — 84% use AI, trust in accuracy 29% (primary) — https://survey.stackoverflow.co/2025/ai/ — retrieved 2026-05-31 — grade A — primary-fetched

