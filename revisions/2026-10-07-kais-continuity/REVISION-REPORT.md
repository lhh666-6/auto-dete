# Reconstruction and verification report

Revision date: 7 October 2026. Target: Knowledge and Information Systems.

This is a revised, editable manuscript and supplement based on the pinned handoff, not a new experimental collection. The original formal ledger remains the main evidence. The separate quota-recovery cohort is incomplete in the available snapshot and has not been folded into the main estimates. The current two-column article is a submission-oriented review draft; final publisher-template conversion and author sign-off remain separate steps.

## Step 1 — Central thesis

Correction-aware review-to-execution continuity links a machine proposal, an explicitly authorized correction, the reviewed instance and the executed state transition; enforcing that relation makes authorization an observable part of an agent's execution environment.

## Step 2 — Three headline findings

1. **Correction creates a distinct continuity problem.** A correct final value and matching retained context do not identify the candidate instance that was reviewed.
2. **Continuity can be made explicit and enforceable across persistence mechanisms.** The contract combines instance binding with freshness, atomic complete successors and exact field sources; formal checks and two realizations support the evaluated relation.
3. **Online enforcement redirects recovery with measurable friction.** In standardized handoffs, 17 exposed bound continuations preserve continuity through 16 reviewed-instance reuses and one reauthorization. Agent-managed refreshed previews show no observed substitution. The completion interval leaves the utility trade-off open.

## Step 3 — Section outline

1. Introduction: persistent state changes → correction → four-role distinction → executable contract → live continuation.
2. Related Work: approval/tool execution; transactions/provenance; trustworthy execution/recovery.
3. Review-to-Execution Continuity: roles, policy separator, conditional Proposition 1 and successor/source obligations.
4. Formal and Transactional Realization: bounded relations, exact-binding implementations and independent auditing.
5. Controlled and Historical Evidence: compact mechanism evidence and observable hosted correction chains.
6. Prospective Online Agent Experiment: shared review checkpoint, unique policy difference, scenarios, independent endpoints and paired inference.
7. Results: continuity and completion; actual feedback → next action → recovery; friction and complete failure accounting.
8. Discussion and Limitations: learned distinction, authorization as execution environment, accountability/friction trade-off and calibrated scope.
9. Conclusion: explicit, enforceable and empirically observable continuity in state-changing agent workflows.

## Step 4 — Content disposition

| Action | Content | Revision outcome |
|---|---|---|
| Keep | Four roles; context/bound equations; conditional omission proposition; freshness, atomic successors and source preservation | Preserved and made easier to locate; Proposition 1 numbering and opaque-handle condition are explicit |
| Keep | All original planned denominators, utility/integrity cells, unknowns, paired effects and observed recovery categories | No numerical results replaced or inflated |
| Compress | Repeated introductory framing and number-heavy abstract | New 205-word audit-count abstract; one coherent introduction; four contributions |
| Compress | Main-text implementation timing discussion | Complete grids remain in S4; agent-level friction remains a main result |
| Rewrite | Related-work comparison | Acknowledges Cordon, Continuity Kernel and commit-time authorization as close preprints; narrows the evaluated distinction |
| Rewrite | Recovery-cohort status and integration instructions | Main scope paragraph plus dedicated S12; pending outcomes remain unreported |
| Move to supplement | Duplicate joint-outcome chart | Main retains the exact joint-cell table; supplemental chart remains available |
| Restore in supplement | P0–P6 operational contract; no-op/mixed-submission semantics; trust boundary | Recovered from the preserved baseline to repair dangling references, without adding a new experimental guarantee |
| Remove | Bibliographic footnote; duplicated scope/command descriptions; main engineering error code | Journal-aligned ordinary-text preprint mentions and clearer reproduction instructions |
| Rebuild | All four flow diagrams | Unified vector artwork inspired by the supplied reference, with explicit evidence units and observed-only recovery paths |

## Step 5 — Claim–evidence audit

| Proposed claim | Supporting evidence | Main location | Strength | Risk to avoid |
|---|---|---|---|---|
| Equal value/context need not preserve the reviewed instance | Fixed-registry witness and 15 controlled identity substitutions | §§1,3,5; Fig.1 | Constructive separation under the declared responsibility requirement | Claiming context authorization is intrinsically wrong |
| Each declared information class can distinguish an otherwise hidden failure | Executable relational histories and 24 passing witness tests | §3; S2 | Conditional class-wise irredundancy | Universal minimum representation or arbitrary-history proof |
| The contract is executable across the two tested persistence mechanisms | 165 exact-journal/reference cases with matching decisions and query records | §§4–5; Fig.2 | Evaluated cross-representation agreement | General semantic equivalence theorem |
| Bounded formal checks support the encoded relation | 72 archived command matches; 9 intended SAT projections; 20 selected UNSAT mutants | §4; S2 | Receipt-supported finite-scope checks | Saying Alloy was freshly rerun in this revision or that UNSAT proves unrestricted correctness |
| Hosted correction chains expose the four roles | 84 archived chains; 252 evidence associations; 168 versions/traces | §5; S5 | Integration relevance of persisted prefixes | Calling these 84 independent task successes or autonomous attack observations |
| Instance enforcement redirects exposed online continuation | 17 delivered G-bound episodes, all (U,I)=(1,1); B16 reuse/A1 reauthorize | §7; Fig.4 | Direct observed standardized recovery | Natural substitution prevalence or broad cross-provider replication |
| Completion and integrity answer different questions | 15 successful context arms with instance violations; full joint table | §7; main Table2 | Direct original-ledger result | Collapsing U and I into a total score |
| Completion advantage is uncertain and repair has a measured cost | +0.78125 pp, 95% interval [-1.953125,3.515625]; B G median +14.539 s, +1 call | §§7–8 | Paired controlled-task estimate; exposed-cohort friction | No-cost, utility-equivalence or latency-speedup claims |
| N shows no observed substitution | 30 exact transitions per policy in B and 3 in A; two unknown N arms retained | §7; Fig.4 | Observation with explicit coverage | Impossibility or production failure-rate bound |
| Additional quota recovery is incomplete | Separate freeze; fixed 45/117-terminal-pair snapshot | Post-results scope; S12 | Collection status only | Pooling partial selected recovery with the primary ledger |

## Step 6 — Ranked titles and rewritten front matter

1. **Review-to-Execution Continuity for Corrected Agent State Changes** — selected; directly names the concept and execution setting with the least clutter.
2. **Correction-Aware Review-to-Execution Continuity in State-Changing Agents** — emphasizes the contract; slightly more technical.
3. **Trustworthy Agent State Changes through Correction-Aware Review-to-Execution Continuity** — foregrounds scientific identity; longer.
4. **Preserving Review-to-Execution Continuity for Corrected Agent State Updates** — foregrounds preservation of the review relation; somewhat less compact.
5. **Correction-Aware Review-to-Execution Continuity for Trustworthy Agent Execution** — strongest identity alignment; generic execution setting.
6. **Enforcing Review-to-Execution Continuity for Corrected Agent State Changes** — emphasizes the enforceable mechanism.
7. **Review-to-Execution Continuity after Correction in State-Changing Agent Workflows** — makes the temporal sequence explicit; longer.
8. **Review-to-Execution Continuity and Recovery for Corrected Agent State Changes** — highlights the online contribution; slightly crowded.

The selected title is retained because it already meets the author's constraints. The abstract and Introduction are rewritten in the editable main source. The opening now introduces the persistent-action problem, correction and the instance boundary before discussing implementation. Four concise contributions match the four evidence layers. All pending supplementary work remains outside the abstract's original-cohort results.

### Final abstract

State-changing agents may continue acting after a reviewer corrects and authorizes a proposal. During that continuation, an equivalent candidate can replace the reviewed instance even when the final value is correct. We define correction-aware review-to-execution continuity through four distinct roles: machine proposal, authorized correction, reviewed candidate and executed transition. An executable contract links them to predecessor freshness, atomic successors and field-level provenance. Bounded relational checks, two transactional realizations, controlled tests and 84 archived correction chains establish complementary evidence for the contract. A frozen prospective study then compares retained-context and instance-bound authorization over 128 tasks, two deployments and 512 planned trajectories, including terminal failures. In standardized queued handoffs, context authorization admits 17 instance substitutions. The paired bound continuations reject those handoffs and recover with intact continuity through reviewed-candidate reuse in 16 cases and fresh authorization in one. Agent-managed refreshed previews show no observed substitution. Overall completion changes by 0.78 percentage points (task-cluster 95% interval [-1.95, 3.52]); the principal deployment's handoff repairs add one tool call and median 14.54 seconds. Its 128 review checkpoints supply most continuation evidence, compared with 11 in the quota-limited deployment. The results make continuity explicit, enforceable and empirically observable, showing how authorization feedback shapes an agent's execution environment.

## Step 7 — Core sections and results

- Related Work remains three compact blocks. The comparison now acknowledges close commit-time and task-transaction execution work, including its own recovery mechanisms. The contribution is the specific corrected-value/context-fixed identity comparison and its measured continuation consequences.
- Formal/system sections retain the mathematical contract and bounded results. Opaque identifiers are explicitly stated; full operational properties and same-value/no-op differences are restored in S2.
- Controlled and historical evidence supports the main execution story. The 84 chains are not repurposed as task-success prevalence. Long cost grids remain in the supplement.
- The online design explains why shared review history, deterministic review, isolated policy arms and controlled scenarios identify the post-review execution difference.
- Results retain the original 512-arm planned ledger, 128 task-cluster bootstrap, full U/I cells, unknown identification interval, actual delivered feedback and event-order recovery. Missing or zero categories are reported without illustrative fabricated trajectories.

## Step 8 — Discussion, limitations and conclusion

The Discussion connects the four-role contract to what an agent sees and does after a tool result. It distinguishes the standardized G mismatch from voluntary N continuity management, explains the measured extra call/time cost and leaves completion uncertainty unresolved. Main scope calibration appears in the short post-results paragraph and the final scope subsection. The separate quota-recovery cohort is explicitly pending in both appropriate locations, with detailed gates in S12. The Conclusion ends at the agent execution level.

### Editor-facing opening check

- **Problem:** a corrected persistent action can use an equivalent instance that was never reviewed.
- **Distinct contribution:** the corrected-value/context-fixed four-role relation and its execution consequences, with nearby approval/transaction/recovery work acknowledged.
- **Agent/intelligent-systems identity:** actual rejection feedback changes the next sampled action and the eventual recovery path.
- **Mechanism:** explicit policy equations, bounded relational checks, transactional realization and independent persisted-state auditing.
- **Online evidence:** a complete original planned ledger with observed G recovery, separate N behavior and retained failures/unknowns.
- **Payoff:** accountable state changes with observable completion uncertainty and execution cost.

The title, abstract, opening text, four contributions and first two diagrams now answer these questions without requiring the reader to inspect the supplement.

## Step 9 — Figure plan and captions

All four main diagrams are supplied as PDF, SVG and 400-dpi PNG, with executable plotting source. The user's visual reference informs pastel stage grouping, coherent original vector icons, layered cards and designed connectors. Figures 1–3 are explanatory/design schematics; Figure 4 uses only verified observed paths. Ribbons encode the observed 16:1 split, not hypothetical recovery categories. FIGURE-PLAN.md gives full element lists, source mappings and design notes.

1. **Concept diagram.** Distinguish proposal, authorized correction, reviewed instance and executed transition. Horizontal role cards with icons and inset values lead to an explicit non-implication separator.

   Caption: Correction-aware review-to-execution continuity. Review authorizes 101 from $c_1$ while retaining its proposal 100. Equivalent $c_2$ has the same value/context but a different identity. Context permits either instance under the original grant; bound permits only $c_1$. A new authorization can license $c_2$. This is a conceptual construction.

2. **Evidence-chain diagram.** Expose the whole research argument through five pastel stages: problem, contract, realization, controlled/historical validation and prospective online observation. Evidence units remain separate.

   Caption: Evidence chain for trustworthy corrected execution. Distinct layers define continuity, make it executable, validate persistence and integration, then observe live agent continuation. Counts retain separate units: bounded commands, cases per mechanism, archived correction chains and planned paired trajectories.

3. **Online-loop diagram.** Explain shared history, checkpoint copy and isolated policy arms. A host-review icon distinguishes deterministic review from a human-subject study. Actual feedback returns to the next agent action, observed path and independent U/I scoring.

   Caption: Paired online intervention after a shared prospective review. The visible conversation and persisted checkpoint are copied into isolated policy arms. The only execution-rule difference is $I_{eq}$. Actual tool feedback enters the next sampled agent decision, whose actions and terminal state are independently audited. The standardized G handoff supplies an index request; N instead leaves refreshed-preview management to the agent.

4. **Recovery diagram.** Show 17 delivered G-bound episodes branching into 16 reviewed-candidate reuses and 1 reauthorization, ending at 17 intact successful outcomes. N has a separate panel with exact-transition coverage and full utility/integrity accounting.

   Caption: Observed paths after standardized mismatch feedback. All 17 exposed G-bound continuations recover with $(U,I)=(1,1)$: B reuses the reviewed candidate in 16 cases, and A reauthorizes the handoff candidate in one. The separate N panel retains agent-managed preview outcomes and unknown coverage. The figure reports observed paths, not the frequency of naturally occurring substitutions.

## Verification completed

- The handoff ZIP SHA-256 matches `1bc17338d18f198811e0e58eca9b64bded29f9b01cd61558862455e7e0d469d8`. CRC and safe-member extraction checks pass.
- The independent audit confirms no change or missing member in the original reference extraction, all 56 frozen master-manifest file hashes and all 51 baseline/controlled source hashes.
- The original offline analyzer regenerates all six CSV tables and the complete summary with exact semantic agreement. Five CSV files also agree byte-for-byte. Paired-effects JSON key order and summary CRLF/LF account for the two serialization differences.
- All 29 manuscript evidence checks pass after a separator-only Linux portability fix. The frozen scorer, collection code, tasks and raw results are unchanged.
- All 24 executable observation-witness tests pass. The 72 Alloy command receipts and 29 projection receipts are inspected and checked; Alloy was not rerun.
- All 17 formal bibliography entries and their narrow claims were checked against primary/official sources. Nearby preprints are acknowledged in ordinary text. The bibliography footnote was removed; PDF command spacing and ASCII double-hyphen flags were corrected; abstract length and six keywords meet the checked journal guidance.
- Both LaTeX documents are compiled with pdfLaTeX, references resolved and every final page rendered for visual inspection. Final counts are 13 main pages and 23 supplement pages. All 36 pages were rendered and inspected; final figure QA and artifact hashes are recorded in QA-RECEIPT.json.

The analysis runtime used Python 3.12.14, jsonschema 4.26.0 and matplotlib 3.10.8. Available PyYAML 6.0.3 differs from the archived 6.0.2 pin; the inspected offline path does not import YAML. This environment difference is disclosed despite identical semantic outputs. Generated TeX formats and font maps were rebuilt in a writable workspace because the installed TeX distribution lacked them; no system configuration or experimental dependency was changed.

## Remaining dependencies and claim boundaries

1. The complete supplementary quota-recovery ledger, its final terminal status, provenance and recovery-specific analysis remain pending. The 45/117 status is read directly from the pinned snapshot-summary.json; partial outcomes were not independently rescored. No online collector was started or monitored by this revision.
2. E3 medians are verified against supplied archived summaries and hashes. The complete raw E3 timed observations are outside this compact handoff, so the medians were not recomputed from individual timings.
3. Historical chain records were checked; the original 1,260 databases were not freshly rescanned. Controlled experiments, provider runs and Alloy solver calls were not rerun.
4. The retained author list, affiliation, ethics, funding and contribution statements require author confirmation. They were preserved as supplied, not independently certified.
5. Publisher-template conversion, coauthor approval, journal submission and any new experiment are not part of this handback. The compact double-column format is a review draft, not a claim of final portal compliance.

## Source and reproduction map

Pinned handoff: https://github.com/lhh666-6/auto-dete/tree/475e66f549613aaaaa62c2ec81ffdee483636c54/cloud-handoff

Original formal master hash: `7773563b40c8db30d6def121915f50fbad032537edde32afd4ba39ec3eea744b`.

The compact editable package contains the main/supplement sources, referenced figure exports, plotting source, the tables used by that plotting source, manuscript-side verifier and documentation. `build.sh` compiles the two documents on a configured TeX Live installation. Full scientific reproduction additionally needs the original pinned archive and the preserved research-directory structure. Overlay the revised manuscript directory on a working copy of that archive; do not overwrite the preserved reference. Use the offline commands in supplement S9 and README.md.

Detailed independent reports are included as EVIDENCE-AUDIT.md and CITATION-AUDIT.md. Their recorded checks distinguish fresh offline reanalysis from archived receipts. At the time of the manuscript review, no GitHub branch had been pushed and no journal submission had been made. This public package is prepared for publication on the existing handoff branch; the journal-submission status is unchanged.
