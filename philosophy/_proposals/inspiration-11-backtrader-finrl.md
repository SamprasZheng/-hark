---
type: reference
status: proposal
tags: [inspiration, open-source, ai-trading, backtest, rl, reinforcement-learning, backtrader, finrl, proposal]
title: Backtrader + FinRL — backtest substrate + RL sizing critic — proposal
author_role: researcher
proposed_destination: philosophy/references/open-source-inspirations.md (append as entry #11)
proposed_at: 2026-05-29T17:00:00+08:00
source_urls:
  - https://github.com/mementum/backtrader
  - https://github.com/AI4Finance-Foundation/FinRL
  - https://arxiv.org/abs/2011.09607
  - https://github.com/polakowo/vectorbt
---

# Inspiration #11 — `Backtrader` (design-only) + `FinRL` (integrate) (PROPOSAL)

> Draft proposal for the `philosophy/references/open-source-inspirations.md` numbered list. Human approval required before move into the philosophy layer.

**Fit**: ★★★★☆ (FinRL) / ★★★☆☆ (Backtrader — design-inspiration only due to license)

This is a paired inspiration: Backtrader is the cleanest *design* for a Python event-driven backtest engine in OSS, and FinRL is the AI4Finance Foundation's reinforcement-learning library that runs PPO / DDPG / SAC / A2C / TD3 on stock-trading Gym environments. The operator's market scan grouped them under one "RL trading" bucket; this proposal accepts that pairing but with a sharp license-driven split.

## What we borrow

### From Backtrader — design only

Backtrader's strategy / data-feed / broker / analyzer object model is the textbook event-driven backtest design. We borrow the **mental model and class boundaries**, not the code, because:

- **Backtrader is GPLv3.** Per [[../../docs/INSPIRATIONS]] §Licensing & legal, "GPL / AGPL upstream → we treat as design-inspiration only and write our own implementation. No code copying."
- The clean alternative is **vectorbt (Apache 2.0)** for vectorised backtest, or our own thin event-driven engine built on the Backtrader design.

So `src/sharks/backtest/bt_engine.py` is a written-from-scratch event-driven engine whose class boundaries mirror Backtrader's (`Strategy` / `DataFeed` / `Broker` / `Analyzer`) but whose code is `$hark`-licensed proprietary per [[../../README]].

### From FinRL — integrate

FinRL provides:

- **`StockTradingEnv` Gym environment**: state = portfolio + recent OHLCV window + features; action = continuous position vector ∈ \[-1, +1] per ticker; reward = next-step PnL (configurable).
- **PPO / DDPG / SAC / A2C / TD3 wrappers** on top of Stable-Baselines3.
- **Training loop + evaluation harness** on US-equity + crypto datasets.

We borrow FinRL's environment design (Gym-compatible state/action/reward contract) and its SB3 wrappers, adapted to feed from `$hark`'s point-in-time-aware feature store rather than its native CSV loader.

## Where it slots into `$hark`'s architecture

Critical constraint: **the RL agent is a sizing critic, not an entry/exit decider.** Entries and exits stay in the analyst-debate stack ([[../02-signal-taxonomy]] four-dimension matrix → daily 10-signal output per [[../05-decision-rubric]]). The RL agent's job is to map a confirmed-entry candidate to a position size ∈ [0, position-cap], conditional on regime + cycle context.

This split is non-negotiable because:

1. **Andy's constitution** ([[../../sharks]]) embeds opinionated entry rules (TD-9 sequential + supply-chain bottleneck + 52w-high distance + golden cross). An RL agent that overrides these is an unsupervised constitution-rewriter — explicitly forbidden by [[../CLAUDE]] §2.
2. **Sample efficiency**: RL needs hundreds of thousands of episodes to converge. We have ~150 trading days × 60 tickers ≈ 9000 entry decisions per year — five orders of magnitude too few to train an entry policy end-to-end without massive overfitting. Sizing (a continuous output conditioned on already-validated entries) is a much smaller hypothesis class.
3. **Interpretability for the Risk Officer**: a "size 4% of NAV because regime = liquidity-loose AND cycle-phase = mid-bull AND volatility = quartile-2" decision is auditable. An end-to-end entry+size policy is not.

## Phase

**Phase 4 (backtest engine)** + **Phase 5 (RL sizing critic)** per [[../../docs/ROADMAP]]:

- Phase 4 §1 says "choose Backtrader or vectorbt (lean toward vectorbt for speed; decide on first sprint)." This proposal asks the human to expand that decision into a 3-way: vectorbt (Apache, fastest) vs Qlib engine (MIT, most realistic frictions — see companion [[inspiration-10-qlib]]) vs from-scratch Backtrader-design engine.
- Phase 5: `src/sharks/agents/rl_sizing_critic.py` consumes the daily 10-signal candidate output, runs the FinRL-trained PPO policy over a feature vector (regime + cycle + recent return distribution + risk budget remaining), and emits position-size suggestions that the Risk Officer ([[../CLAUDE]] §1.3) can override.

## Proposed module map

| Module | Source | License path |
|---|---|---|
| `src/sharks/backtest/bt_engine.py` | Written from scratch, Backtrader-inspired design | `$hark` proprietary; design attribution in module docstring |
| `src/sharks/backtest/env_gym.py` | FinRL `StockTradingEnv` adapted for `$hark` feature store | FinRL upstream license (expected MIT — **Unconfirmed: verify before commit**); adapted code marked `# Adapted from AI4Finance-Foundation/FinRL` |
| `src/sharks/agents/rl_sizing_critic.py` | FinRL's SB3 PPO wrapper, wrapped for our action contract (size only) | Same as env_gym; SB3 itself is MIT |

## Proposed integration adaptation

- **Action space restricted to sizing**: the FinRL native action is "position vector per ticker in \[-1, +1]." Our action is "size in [0, size-cap] for each pre-validated long candidate, and same for shorts under the [[../03-long-short-taxonomy]] short-side gating." Entries arrive as the *state*, not as a decision the agent makes.
- **Reward includes a risk penalty**: native FinRL reward is next-step PnL. Ours adds a quadratic penalty on portfolio-level [[../08-risk-and-position]] violations (sector cap, single-name cap, max-DD halt proximity). The Risk Officer's invariants are encoded in the reward, not in a post-hoc filter.
- **Walk-forward training**: agent is trained on `2015-2022`, validated on `2023`, deployed on `2024+`. No re-training on rolling windows during a single backtest. This is the canonical RL trading anti-overfit discipline.
- **No live-execution loop**: Phase-5 deployment is `--mode dry-run` only. The agent's size suggestion lands in `outputs/picks-YYYY-MM-DD.json` as an *advisory* field next to the analyst-debate-derived size. The human chooses which to act on. [[../CLAUDE]] §2 "do not place trades" remains intact.

## License

- **Backtrader**: **GPLv3** (per `mementum/backtrader/LICENSE` — **Unconfirmed: verify at adoption time**). Design-inspiration only; no code copy. Mitigated by writing our own engine.
- **FinRL**: expected **MIT** (AI4Finance umbrella convention — **Unconfirmed: verify at adoption time**). Freely integrable with attribution.
- **Stable-Baselines3**: MIT (well-established).
- **vectorbt** (Apache 2.0): the recommended GPLv3-avoiding alternative if the operator decides the from-scratch engine is too much work for Phase 4.

## Integration test sketch

```python
# tests/test_rl_sizing_critic_smoke.py
def test_critic_respects_position_caps():
    state = make_state(candidates=[("NVDA", side="long"), ("TSM", side="long")])
    critic = RLSizingCritic.load("models/rl-sizing-ppo-2024.pt")
    actions = critic.suggest_sizes(state, as_of="2024-06-30")
    # Tier-1 cap per philosophy/08-risk-and-position
    assert all(a.size <= 0.08 for a in actions)
    # Sector cap (NVDA + TSM both semis) — combined ≤ sector cap
    assert sum(a.size for a in actions if a.sector == "semiconductors") <= 0.20

def test_critic_advisory_only_in_dry_run():
    out = sharks.pick.main(["--mode", "auto", "--dry-run"])
    # Critic field is present but NEVER the binding size
    for slot in out["picks"]:
        if slot is not None:
            assert "rl_suggested_size" in slot
            assert "analyst_debate_size" in slot
            # The binding size on the actual recommendation is from the debate
            assert slot["size"] == slot["analyst_debate_size"]
```

## Risks / open questions for the human reviewer

1. **GPLv3 trap**: even *reading* Backtrader's source extensively risks copyright-derivative claims. Mitigation: a sufficiently distinct from-scratch engine, with the design ideas already in the public-domain literature (Tucker, 2013; Chan, 2013) cited in the module docstring instead of Backtrader.
2. **Reward hacking**: an RL agent will find arbitrage in the reward function before it finds alpha. Adversarial-test the reward design in Phase 5 sprint-0 before any training run consumes significant compute.
3. **Continuous re-training cost**: SB3 PPO on ~10 years of daily-bar data is a few hours on a single GPU; not a bottleneck on the operator's RTX 5070.
4. **Drift on regime change**: a policy trained on 2015–2022 regimes may underperform in 2024–2026 AI-bubble regime. Mitigation: Phase 6 introduces regime-gated re-training trigger per [[../concepts/cycle-resonance]].
5. **Sleipnir overlap**: Sleipnir's Dynamic Router (Inspiration #4) is a different "RL-adjacent" component (model-selection routing, not action selection). They do not overlap; this proposal does not displace #4.

## Cross-references

- [[../CLAUDE]] §2 (no execution), §1.3 (Risk Officer veto over critic output)
- [[../02-signal-taxonomy]] — the analyst-debate stack the critic does NOT replace
- [[../03-long-short-taxonomy]] — short-side gating the critic action space must honour
- [[../05-decision-rubric]] — 10-signal contract the critic's output annotates, not replaces
- [[../08-risk-and-position]] — caps the critic must internalise in its reward function
- [[../09-point-in-time]] — feature store the env must read through
- [[../../docs/ROADMAP]] §Phase 4 deliverable 1, §Phase 5 (Lightweight UI — RL field rendered as advisory)
- [[../../docs/INSPIRATIONS]] §Licensing & legal — GPLv3 design-only rule applied
- See also companion proposals [[inspiration-09-fingpt]] (feature pipeline upstream) and [[inspiration-10-qlib]] (engine alternative)

## Notes for the human reviewer on accept

1. Verify Backtrader license at https://github.com/mementum/backtrader/blob/master/LICENSE (expected GPLv3 — confirms design-only rule).
2. Verify FinRL license at https://github.com/AI4Finance-Foundation/FinRL/blob/master/LICENSE (expected MIT).
3. Phase 4 sprint-0 decision: from-scratch Backtrader-design engine vs vectorbt vs Qlib engine. Triangulate with companion proposal [[inspiration-10-qlib]].
4. Phase 5 sizing-critic-vs-fixed-Kelly comparison: before training a PPO critic, benchmark a deterministic [[../concepts/cycle-resonance]]-gated Kelly sizer. If Kelly hits the target Sharpe + MDD, RL is not worth the complexity.
5. After move from `_proposals/` to `philosophy/references/open-source-inspirations.md`, also append the matching row in `docs/INSPIRATIONS.md` integration matrix (see companion proposal [[inspirations-matrix-patch]]).
