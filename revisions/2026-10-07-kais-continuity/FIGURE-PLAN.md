# Revised main-paper figures

## Deliverables and design

The four figures use a consistent pastel stage palette, dark colored outlines, original geometric vector icons, rounded layered panels, inset detail cards, and designed connectors. The supplied visual reference informed the style only; none of its pixels or icons are incorporated. Figure 4 uses exactly two observed recovery ribbons, with widths proportional to the 16:1 episode counts.

All four final artboards are **172 × 80 mm**. Body and header text use base sizes of at least **7.5 pt** at that width; mathematical subscripts use conventional smaller sizes. Render at the paper's full text width, without subsequent reduction below 172 mm if the 7.5 pt floor must be preserved. Colors supplement explicit labels; interpretation does not require distinguishing colors alone.

Editable source: `make_revision_figures.py`.

Exports, each available as PDF, editable-text SVG, and 400 dpi PNG:

1. `figures/revised-figure1-concept`
2. `figures/revised-figure2-evidence-chain`
3. `figures/revised-figure3-online-loop`
4. `figures/revised-figure4-recovery-paths`

The previous joint-outcomes plot is retained for the supplement. This figure work does not edit `main.tex` or `supplement.tex`.

## Figure 1: concept and four roles

### Description

Four pastel panels distinguish the machine proposal, authorized correction, reviewed instance, and executed transition. Original agent, reviewer, reviewed-document, execution-gear and database icons make these roles immediately legible. The example preserves the original proposal 100, records authorization of 101 for candidate c1, and shows two alternative execution requests that would persist 101. The footer states logical non-implication: matching proposal value and retained context do not establish instance identity. The admission contrast assumes that the common guards hold and applies to alternatives under the original grant; it does not show a grant being consumed twice.

### Compact caption

Four roles in a corrected change. Review authorizes 101 for proposal 100 on c1. Equivalent c2 can produce 101 yet break instance continuity. With common guards satisfied, context admits either alternative; bound requires c1 under the original grant. Schematic alternatives, not successive uses of one grant.

### Source and scope

`main.tex`, the correction relation and definitions of G, K_eq and I_eq in the review-to-execution continuity section. Values 100 and 101 and identities c1/c2 are a motivating construction, not observations from an experimental run. The figure's two execution rows share the persisted value but deliberately differ in the supplied candidate instance.

## Figure 2: evidence chain

### Description

Five differentiated pastel stages progress from the instance-continuity problem to a contract, formal/transactional realization, controlled/historical validation and prospective online observation. Chevron headers, document/contract/network/chart/agent icons and white evidence-unit insets provide a layered visual hierarchy. The footer states the progression from specification to executable realization, testing and observation. Counts retain their interpretation units: 72 bounded commands, 165 cases per mechanism, 84 historical correction chains and 512 planned online policy arms.

### Compact caption

Evidence chain from the continuity problem to live agent continuation. Bounded formal commands, controlled cases per mechanism, historical correction chains and planned policy arms retain their distinct units. Specification, implementation, validation and observation answer different questions.

### Source and scope

- `evidence/formal/command_results.json`: 72 expected/actual command outcomes agree, in finite encoded scopes.
- `evidence/controlled/results/e1/summary.json`: each of the three mechanisms has 165 planned and scored controlled cases.
- `evidence/final-number-verification.json`: the historical 84-chain audit passes. The manuscript explains that these are persisted correction chains, not whole-task successes.
- `evidence/online/manuscript-aggregates.json`: the frozen export is COMPLETE and includes 512 planned policy arms.

The stages do not pool denominators, imply an unbounded formal proof, or generalize the controlled tasks into natural substitution prevalence.

## Figure 3: online loop

### Description

The left group shows an actual agent proposal and a deterministic host review/checkpoint. A gear with a review certificate represents the host, avoiding a misleading human-reviewer depiction in this experiment. The checkpoint copies conversation and persisted state into isolated policy arms. Explicit gate formulas differ only by I_eq. Both feed actual tool results to a subsequent model response; the next meaningful agent action may produce further tool feedback, shown by the return edge. The recorded continuation yields an observed path and independent (U,I) scoring. All planned arms remain in the ledger, including failures and unknown coverage.

### Caption

Prospective paired design. An actual agent prefix obtains deterministic host review; the checkpoint copies visible history and persisted state into isolated context and bound arms. Only I_eq differs in the execution rule. Actual tool results reach subsequent model responses, and the agent's meaningful actions form observed paths scored independently for utility U and integrity I. The return arrow denotes further feedback/action cycles. All planned arms remain, including prefix failures and unknown integrity.

### Source and scope

`main.tex`, prospective experiment sections on shared review history, the unique policy difference, actual feedback delivery, independent scoring and retention of planned arms. The diagram describes the design; it does not assert that every planned arm reached the checkpoint or received feedback. The observed path box is intentionally open rather than presenting hypothetical repairs as observed frequencies.

## Figure 4: observed recovery paths

### Description

The standardized G panel connects 17 delivered bound instance-mismatch rejections to exactly two recorded paths. Sixteen B continuations next commit the original reviewed candidate; one A continuation first authorizes the handoff candidate, then commits. Both paths end at (U,I)=(1,1). Ribbon widths encode 16:1. The paired-context note reports all 17 accepted substitutions as integrity violations, without falsely assigning all of them utility success. The planned denominator note preserves 15 A shared-prefix failures.

N has a separate agent-managed refreshed-preview panel and no incoming rejection ribbon. It reports zero observed substitutions, 30 B and 3 A exact transitions per policy, and B's 32-arm outcome partition per policy: 28 (U=1,I=1), 3 (U=0,I=1), and 1 (U=0,I unknown). Unknown integrity therefore does not imply unknown utility. The transition and planned-arm denominators are distinct.

### Caption

Observed standardized-handoff recovery is distinct from agent-managed preview continuation. G-bound delivers 17 mismatch rejections: B's 16 continuations next commit the reviewed candidate; A's single continuation authorizes the handoff candidate, then commits. All 17 reach (U,I)=(1,1); paired context admits 17 instance violations. Ribbon widths encode the 16:1 observed episodes. Only 17 of 32 planned G pairs reach this exposure. N produces no observed substitution or mismatch feedback; transition counts and planned-run outcomes retain separate denominators.

### Source and scope

- `evidence/online/table3-recovery.csv`: G-bound Delivered=True, RecoverableReject=True, trigger INSTANCE_MISMATCH, 16 B commit/reuse-reviewed paths and one A request_authorization/reauthorization path; all 17 recovered with U=True and I=1.
- `evidence/online/table2-continuity.csv`: 17 policy-admissible G-context executed substitutions; no N executed substitutions; exact N transition counts A=3 and B=30 under each policy.
- `evidence/online/table1-outcomes.csv`: each G configuration/policy plans 16 arms; the checkpoint is reached in one A pair and sixteen B pairs. N-B has 32 planned arms per policy, 28 task completions, 31 integrity-covered arms and one integrity-unknown arm.
- `evidence/online/failure-archaeology-all-arms.csv`: both N integrity-unknown arms have known unsuccessful utility.

The figure does not invent reverify, reproposal, abandonment, invalid-loop or other branches in G. E/V/R descriptive recovery belongs in its evidence table. No partial-collection recovery rate is used.

## Reproduction and QA

Run `python3 make_revision_figures.py` from this directory. The script validates the source counts before authoring, then writes all 12 figure exports and `figures/revised-figure-source-audit.json` with source SHA-256 hashes, interpretation units and figure dimensions.

PDF render-review copies are in `reviews/figure-review/`. The final audit checks exact page dimensions, embedded fonts, vector-only drawing content, searchable text, SVG editable text and image dimensions, in addition to inspecting every complete PNG. The final inspection report is `reviews/FIGURE-VISUAL-QA.md`.
