---
type: synthesis
domain: method
tags: [bayesian, bottleneck, posterior, likelihood, serenity, formalization, expected-value]
as_of_timestamp: 2026-05-31T07:30:00+08:00
author_role: researcher
status: live
schema_version: 1
---

# 貝葉斯瓶頸引擎 / The Bayesian Bottleneck Engine

The principal asked: **can `$hark` integrate Bayesian inference, and can it be mathematically formalised?** After digesting Serenity's (@aleabitoreddit) Bayesian-bottleneck logic — **the answer is yes to both, and the deeper truth is that `$hark` is *already* an implicit Bayesian engine.** The `tech/` DD layer builds priors, the `_weekly-watch` milestone ladder is the update step, and `lead_lag.py` + rotation is the sequential total-probability rotation. Formalising = making the implicit math explicit + numerically honest. **Research/educational only.**

> **考證 caveat up front:** Serenity's *method* is sound and is essentially what this layer already does. His *return claims* (4502% YTD, 225× over 2y, 35-picks/4-down) are **anonymous, unaudited, self-reported → grade D/E** under [[_sourcing-protocol]], with unmeasurable survivorship + selection bias. **Adopt the process; never anchor on the numbers.** He is already a grade-D KOL-model here ([[../watchlist/serenity-supply-chain]], `serenity_scout.py`, [[../philosophy/concepts/serenity-supply-chain-bottleneck]]) — "treat codes as leads to verify," per the watchlist's own disclaimer.

## §1. Serenity 四步 ↔ `$hark` 模組 (the mapping)

| Serenity step | Bayesian object | Existing `$hark` module |
|---|---|---|
| ① 研讀論文 + 拆 BOM → 供應鏈地圖 | **先驗 P(H)** from *structure* (物理現實), not price-extrapolation | `tech/` 21 trend pages (技術底蘊+需求數據+供應鏈 → 5-axis rubric + `confidence` + verdict); [[../watchlist/serenity-supply-chain]] |
| ② 識別瓶頸後果斷下注 | act on **EV** under uncertainty, position-capped | `FOM` + [[fom-integration]] sleeve router + [[../philosophy/concepts/evidence-gated-rebalance]] |
| ③ 持有中尽调驗證邏輯 | **後驗 P(H\|E)** — posterior from evidence | **[[_weekly-watch]] milestone ladder** (每個里程碑 = 證據 E; ✅/❌ = likelihood); the "self-refutation" section on every page = the falsifier |
| ④ 輪動到最活躍瓶頸 | **全概率 + 序貫更新** (posterior→next prior) | [[alpha-transmission-framework]] + `lead_lag.py` `transmission_candidates` + `sector_flow` + [[../philosophy/concepts/hotspot-sector-rotation]] |

The philosophy you quoted — *相信基於概率不是信念；概率錨定結構不是歷史；決策依據期望值不是確定性* — is **already the constitution** ([[../sharks]]): probabilistic not predictive, structure-anchored ([[../philosophy/concepts/supply-chain-bottleneck]]), EV-gated ([[../philosophy/05-decision-rubric]]).

## §2. 數學形式化 / The formalisation

**Hypothesis.** For node *i* and horizon *h*: `H_i^h = {node i is the active capacity-constrained, pricing-power bottleneck over h}` (the "霍爾木茲海峽" event).

**Prior** `P(H_i)` — from the DD rubric, NOT price. Map the 5-axis rubric + verdict + page `confidence` to a calibrated prior via log-odds:
```
logit(P0_i) = β0 + β1·(rubric_sum_i/10) + verdict_band(v_i)
P0_i = σ(logit)                          # σ = logistic, clamp to [0.05, 0.95]
```
where `verdict_band`: 質變 +1.0, 結構 +0.2, 過熱 −0.5, 太早 −1.0, 受損 −1.5. (Initial β's are priors-on-priors; calibrate later — §4.)

**Likelihood update — the core.** Each milestone *m* (from [[_weekly-watch]]) carries a likelihood ratio `LR_m = P(E_m=✅ | H)/P(E_m=✅ | ¬H)`. A *well-designed falsifiable* milestone has `LR_m ≫ 1`. Sequential (Naive-Bayes) update in **log-odds** — the numerically clean form:
```
logit(P_post) = logit(P0) + Σ_m s_m · log(LR_m)
   s_m = +1 if ✅ (evidence for H), −1 if ❌ (falsifier → ×1/LR), 0 if ⏳
```
This is exactly Serenity's step ③: *正面證據 → 後驗飆升 → 加倉; 反面證據 → 後驗驟降 → 止損.* `❌` is a falsifier, not a price move — *"我們驗證的不是股價漲沒漲，而是當初下注的邏輯是否還被事實強化."*

**Correlation shrinkage (anti-overconfidence).** Milestones are NOT independent, so raw Naive-Bayes overstates confidence. Damp the evidence by an effective-count factor:
```
logit(P_post) = logit(P0) + λ · Σ_m s_m·log(LR_m),   λ = k/(k + n_eff)  (k≈3)
```
This is the numerical twin of the [[../philosophy/concepts/evidence-gated-rebalance]] 十足的證據 quorum (≥4/5 dims) — the gate *is* a likelihood-ratio quorum, now explicit.

**Edge = 認知差.** The tradeable quantity is the gap between your posterior and the market's implied probability:
```
edge_i = P_post(H_i) − P_mkt(H_i),   P_mkt ≈ σ(−bubble_guard_i / τ)
```
`bubble_guard` is the market-belief proxy: froth (bg ≈ −95) ⇒ `P_mkt ≈ 0.92` (market already believes ⇒ **edge ≈ 0 even if your posterior is high**). This is the mathematical statement of the layer's rule **「受益者 ≠ 該價位的股票」** and of "un-crowded alpha": you want high `P_post` AND low `P_mkt`.

**Sizing — EV / fractional Kelly, capped.** Act only when `edge > edge_min`; size:
```
f*_i = clip( frac · edge_i / (1 − P_post) , 0, cap_i )   # cap from Risk Officer / sleeve
```
太早/過熱 verdicts ⇒ `cap` = Moonshot ring-fence ≤5% regardless of edge (the Alpha-sleeve rule). Nothing bypasses [[../philosophy/08-risk-and-position]].

**Sequential rotation = total probability (step ④).** Maintain `{P_post(H_i)}` for all nodes; capital flows to `argmax_i [ edge_i · payoff_i ]`. Last round's posterior becomes next round's prior; the [[_weekly-watch]] weekly pass IS the sequential update. The bottleneck "moves" along the transmission chain ([[alpha-transmission-framework]]: capex→semis→memory→optical→**power**→industrials), and `lead_lag.transmission_candidates` ranks where `P(bottleneck_{next})` is rising but not yet priced.

## §3. 可以整合嗎? — YES: the minimal implementation

`src/sharks/scoring/bayesian_update.py` (pure, observe-first): `prior_from_rubric()` → `milestone_logodds_update()` (with shrinkage) → `edge_vs_market()`. It is a **LENS over data you already produce** (verdict, confidence, milestone_score, bubble_guard) — no new data, no new model. It turns the qualitative DD into an explicit posterior + edge, runnable as `posterior_for_ticker(ticker)`.

## §4. 為什麼這跟你既有紀律一致 / Why it fits (not a new religion)

- **It is the same observe-first discipline.** The Bayesian posterior is an *annotation*, not a `final_fom` input — exactly like the DD tilt (which a walk-forward showed was IC-neutral). The priors/LRs must be **calibrated** before they size anything: reliability diagrams + Brier score on the [[_weekly-watch]] milestone hit-rate, mirroring [[../philosophy/concepts/fom-predictive-validity]]. Until calibrated, it is a thinking tool.
- **It makes the gate numerical.** 十足的證據 (5-dim quorum) = a likelihood-ratio quorum; "default-hold, offense needs full evidence" = "don't move off the prior without enough LR." 
- **It enforces 認知差.** edge = posterior − market-implied formalises why we avoid the front-run darling (high `P_mkt`) and hunt the un-crowded downstream node (low `P_mkt`, rising `P_post`).

## §5. 限制 / Where the math breaks (honest)

- **Independence is false** → shrinkage λ is a band-aid, not a cure; correlated milestones still over-count. Prefer few, orthogonal, high-LR milestones.
- **LRs are subjective** until back-measured against realised milestone→outcome hit-rates (the calibration loop). An un-calibrated LR is just a confident guess.
- **Priors can be overconfident** (the BOM-prior feels precise but the map ≠ territory). Clamp to [0.05, 0.95]; never 0/1.
- **Regime breaks invalidate likelihoods** — in a funding-chain rupture ([[../philosophy/concepts/funding-chain-rupture]]) correlations → 1 and node-level posteriors all move together; gate with the regime classifier.
- **`P_mkt` from bubble_guard is a rough proxy** — a real market-implied probability needs options/valuation; treat as ordinal, not exact.

## See also
- [[alpha-transmission-framework]] (the rotation engine this scores) · [[fom-integration]] (observe-first sibling) · [[_weekly-watch]] (the evidence stream) · [[scoreboard]] (the priors)
- [[../philosophy/concepts/evidence-gated-rebalance]] · [[../philosophy/concepts/fom-predictive-validity]] · [[../philosophy/concepts/supply-chain-bottleneck]] · [[../philosophy/concepts/serenity-supply-chain-bottleneck]]
- `src/sharks/scoring/bayesian_update.py` (the runnable core)
