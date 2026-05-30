# wiki/

The LLM-compiled state layer. Per [[../philosophy/references/karpathy-llm-wiki]], this is where the Compiler agent integrates `raw/` source material into a structured, interlinked, persistent knowledge base.

## Reading order for agents (every session)

1. [[index]] — MOC, navigate from here
2. [[log]] — last 10 entries for recent activity awareness
3. [[01_macro_state]] — current Fed / liquidity / regime read
4. [[02_mag7_bottleneck]] — current Mag 7 + supply-chain map
5. [[positions]] — current open positions, theses, invalidation triggers

## Pages in this layer

- `index.md` — MOC (Map of Content) for the wiki
- `log.md` — append-only chronological log
- `01_macro_state.md` — current macro/policy/liquidity regime
- `02_mag7_bottleneck.md` — Mag 7 supply-chain bottleneck map (the alpha source)
- `03_alpha_library.md` — historical case library (cycle-resonance instances, true-top + true-bottom examples, etc.)
- `04_backtest_log.md` — backtest run records (Phase 4+)
- `positions.md` — open positions and their thesis state
- `05_recommendations/` — daily 10-signal outputs (`YYYY-MM-DD.md` + archive)

## Phase 1 state

Every page in this layer is a **stub**. The Compiler populates them in Phase 2+ as `raw/` sources arrive. Stub pages carry `status: stub` in their frontmatter so backtests can verify they were not accidentally referenced as data.

## Writeback discipline

Per [[../CLAUDE]] Section 3:

- When a `raw/` source arrives, the Compiler reads it, integrates relevant claims into existing wiki pages (NOT just creating new ones), and only then writes a new page if warranted
- Chat-derived analytical answers that are durable should be filed back into the wiki, not lost to conversation history
- Every new page or page update carries `as_of_timestamp` matching the latest source `source_first_visible_at` it draws from. See [[../philosophy/09-point-in-time]].
- Contradictions are flagged on the older page (NOT silently overwritten) and the human resolves them

## Wiki health invariants

Phase 2 implements a lint job (`uv run sharks wiki lint`) that verifies:

1. Every `[[link]]` resolves to an existing file
2. Every page carries the mandatory frontmatter
3. Every page outside stubs carries `as_of_timestamp`
4. Every `source_paths` reference exists in `raw/`
5. No orphan pages (every page is reachable from `index.md`)
6. `log.md` is parseable: every line starting with `## ` matches the `## [YYYY-MM-DD HH:MM TZ] <action> | <title>` format

Lint failures are P1 bugs. The Risk Officer rejects writebacks that introduce lint failures.

## What does NOT live here

- Raw external content → `raw/`
- Static philosophy and concept definitions → `philosophy/`
- Daily JSON decision outputs → `outputs/`
- Code → `src/`
