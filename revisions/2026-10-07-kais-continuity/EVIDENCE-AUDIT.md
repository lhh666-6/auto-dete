# Independent evidence audit

## Conclusion

The offline prospective analysis reproduces all six supplied CSV tables and the analysis summary semantically, with no numerical discrepancy in the principal manuscript claims. The original 512-arm planned denominator, 256 paired units and 128 task clusters remain intact. Two interrupted N arms remain unknown; they are not replaced or scored as intact. The 17 G-context violations and 17 delivered G-bound recoveries are supported by the archived scorer, raw-event checks and independently recomputed table counts.

One reproducibility defect requires correction: the supplied manuscript verifier uses Windows separators from its source manifest as literal Linux filename characters. It fails before completing its checks. A separator-only repair in an isolated audit copy passes all 29 checks, including when the online inputs are replaced by the newly regenerated exports. Frozen sources and raw records were not modified.

This audit verifies the submitted records and repeats the archived independent scoring procedure. It does not constitute new online model collection, fresh controlled-system experiments, a new Alloy solve, or reconstruction of the original 1,260 historical databases.

## Inputs and preservation

- Authoritative manuscript examined: `reference/revisions/2026-10-07-kais-continuity/main.tex` and `supplement.tex`, plus their audit, reconstruction, protocol and verification documents.
- Archive SHA-256: `1bc17338d18f198811e0e58eca9b64bded29f9b01cd61558862455e7e0d469d8`.
- A post-audit comparison of all 16,075 archive members against the extracted reference found zero missing files and zero changed files. See `reference-integrity.json`.
- All 56 master-manifest file hashes pass. Master SHA-256 is `7773563b40c8db30d6def121915f50fbad032537edde32afd4ba39ec3eea744b`.
- All 51 normalized-path source-manifest hashes for baseline/controlled evidence pass.
- All audit outputs, the portable verifier copy and the verification-tree copy are below this audit directory. The original reference and frozen collection files remain byte-identical to the archive.

## Execution and semantic comparison

The analyzer, exporter, scoring/audit functions, oracle, episode classifier, bootstrap implementation and transitive imports were inspected before execution. Provider functions are defined on import but are never invoked by the offline analyzer. The scoring path opens SQLite inputs read-only. Python bytecode output was disabled. The analyzer was invoked with its original source and an absolute fresh output path:

`analyze_formal.py --output fresh-analysis --figures`

It completed successfully and reported `planned_arms=512, formal_inference_allowed=True`. Both figure families were generated as PDF, SVG and PNG, and their PNGs were inspected. Fontconfig emitted non-fatal cache-directory warnings; figure files were nevertheless generated and readable.

Runtime: Python 3.12.14, jsonschema 4.26.0, matplotlib 3.10.8 and available PyYAML 6.0.3. The archived requirements pin PyYAML 6.0.2. No installation was performed. The inspected offline analysis path does not import YAML, so this version difference did not participate in the analysis. Python differs from the collection environment; the semantic outputs still match exactly.

CSV comparison parses header/row dictionaries, parses nested JSON-valued cells, canonicalizes object-key order and compares full row multisets. This preserves duplicate-row multiplicity while avoiding dependence on row or dictionary serialization order. JSON summaries are compared as parsed complete objects, including all effect estimates, bootstrap intervals, usage records and prefix accounting. This is stronger than comparing selected totals or hashes alone.

| Export | Rows | Semantic result | Byte result |
|---|---:|---|---|
| table1-outcomes.csv | 24 | Exact match | Exact match |
| table2-continuity.csv | 261 | Exact match | Exact match |
| table3-recovery.csv | 99 | Exact match | Exact match |
| table4-utility-friction.csv | 512 | Exact match | Exact match |
| paired-effects.csv | 256 | Exact match | JSON object-key order differs |
| failure-archaeology-all-arms.csv | 273 | Exact match | Exact match |
| analysis-summary.json | Complete object | Exact match | CRLF versus LF differs |

The manuscript aggregation script was then executed in the independent verification tree using the fresh exports. All aggregate fields match the supplied aggregation, excluding only `input_hashes`, where the byte hash of the semantically identical paired-effects file properly changes.

## Verified prospective claims

### Denominators and coverage

- Collection status is COMPLETE and all 256 pair records are terminal. This is a terminal accounting status, not a claim that every arm contains a complete model trajectory.
- The 512 unique planned arms belong to 128 task instances and two configurations. The bootstrap resamples scenario-stratified task clusters, retains both configurations and both policy arms, uses 10,000 draws and seed 20261007, and averages configuration-specific paired differences within each task.
- A reaches 11/128 shared review checkpoints; B reaches 128/128.
- A has 234 prefix-failure arm records from 117 shared-prefix failures, four further runtime-error suffixes and 18 final-report suffixes. B has 236 final-report suffixes, 18 invalid-output suffixes, one missing-termination partial arm and one unstarted arm.
- The two unknowns are the context and bound arms of `FORMAL-N-020-B`. Context has `termination_missing` and `final_state_missing`; bound has `arm_not_started`. Neither enters an observed recovery numerator.
- The raw-provider aggregation reconfirms 357 A usage-limit error events. These are provider attempt/error events, not 357 separate tasks.

### Utility and integrity

Joint cells use the order (U=1,I=1), (U=1,I=0), (U=0,I=1), (U=0,I=0), unknown:

- A-context: 8, 1, 119, 0, 0
- A-bound: 9, 0, 119, 0, 0
- B-context: 103, 14, 8, 2, 1
- B-bound: 119, 0, 8, 0, 1

Thus context completes 126/256 and bound 128/256. The aggregate effect is 0.0078125, interval [-0.01953125, 0.03515625], or +0.78125 percentage points with interval [-1.953125, 3.515625]. B completes 117/128 versus 119/128; its effect is 0.015625, interval [-0.0390625, 0.0703125]. B has five context-only and seven bound-only completions; exact two-sided McNemar p=0.7744140625. A has no completion-discordant pair.

The continuity failure-incidence identification endpoints are -0.0703125 and -0.0625. Their separate bootstrap intervals are [-0.08203125,-0.0625] and [-0.07421875,-0.05078125]. An aggregate identified point estimate is intentionally absent because continuity is unknown for two arms. Neither provider failure nor a rejected admission is automatically an integrity violation.

### Transitions and recovery

- There are 261 observed authoritative transitions. All 17 executed substitutions occur in G-context, one in A and sixteen in B. All are same-value/same-context, policy-admissible under context, instance-incompatible, and pass the reported source-provenance/copy-forward checks.
- Fifteen violating context arms nevertheless complete the task. The two remaining violations coexist with unsuccessful task completion.
- N has three same-instance transitions per policy in A and thirty per policy in B, with no observed substitution or delivered rejection episode. Absence of an observed N substitution does not prove substitution is unreachable or rare in production.
- The 99 delivered episodes come from 99 distinct feedback-bearing arms: six in A and 93 in B. Every episode has a legal path at its recorded rejection-time state. The raw audit validates a received subsequent provider response and feedback-containing input, rather than accepting queued feedback as delivery.
- G-bound contributes 17 delivered episodes, all ending U=1,I=1: sixteen B continuations reuse the reviewed candidate, while the one A continuation requests fresh authorization.
- In B, E has 16 delivered episodes and 15 recovered per policy. V has 13 delivered and 12 recovered per policy. R has nine delivered/context and ten delivered/bound, but nine episode recovery endpoints per policy. The extra B-bound R continuation has successful run-level completion without a recorded episode endpoint.
- Observed labels include reuse, reproposal, reauthorization, evidence refresh, state refresh, successful state confirmation and two runtime-failure episodes. The stated zero categories are absent in the complete table. These are conditional descriptive results, not unconditional causal recovery-rate estimates.

### Friction

For B's 127 pairs with two suffix records, mean bound-minus-context differences are 0.070866 calls, 0.039370 model turns, zero authorizations and 1.285598 seconds elapsed; median elapsed difference is 0.687 seconds. All 128 pairs remain in the capped-success-time endpoint.

For B's sixteen G pairs, every pair has exactly one extra Agent tool call, mean model-turn increase 0.9375, no extra authorization request, mean elapsed increase 8.8445625 seconds and median 14.539 seconds. The manuscript's 8.84 and 14.54 rounding is correct. A's single exposed G pair adds two calls, one of them an authorization request.

B's capped time-to-success mean difference is -9.744703125 seconds overall and -76.5275 seconds in G. This improvement is not a latency speedup: unsuccessful context reports receive the 720-second cap. Prefix usage is counted once for each of 256 pairs; unavailable currency cost and token components remain unobserved.

### Complete failure ledger

The 273 distinct U=0/I=0/unknown arms partition into 238 A runtime failures, fifteen successful context violations, two unsuccessful context violations, sixteen further unsuccessful B arms with I=1, and two unknown N arms. B's eighteen invalid-output terminations include the two unsuccessful G violations and sixteen intact-integrity failures. No pilot or deterministic fixture is included in the formal assignment ledger.

## Controlled and historical evidence

The archived E1 receipts independently aggregate to 165 executions per mechanism: context accepts 60 and rejects 105; exact journal and reference each accept 45 and reject 120. Context accepts all fifteen same-value/same-context substitutions; exact journal/reference reject all fifteen. The 165 matched exact/reference receipt pairs have identical acceptance and query records. All rejected E1 receipts retain equal before/after authoritative digests.

E2 has 66 raw server receipts because six successful replay setup calls are additional to the sixty scored cases. The sixty-case table confirms nine request substitutions accepted by the original path and rejected by the session gate; three display-only cases are accepted per path. There are 27 rejected E2 receipts, all with stutter, which combine with 345 E1 rejections to give the reported 372 rejected attempts.

The included E3 summary CSVs confirm the reported representative medians: reference 712.00365 ms versus exact journal 22.0879 ms; bulk trace 170.2419 ms versus point trace 509.0902 ms. They also preserve 200 observations per arm/cell, 20 mechanism rows, 20 materialization rows and 72 trace rows. The manuscript's rounded values agree. This audit checks the supplied summaries and their hashes; the current package does not contain the complete raw E3 timed observations needed to recompute these medians independently.

The 84 historical correction-chain records have zero recorded failures, 252 evidence associations, 252 candidate-certificate checks, 168 version checks and 168 P6 trace checks. Their endpoints comprise 80 PASS_UTILITY_SAFE, one PASS_SAFE_BUT_UTILITY_FAILED, two MODEL_API_FAILURE and one TIMEOUT. Configuration counts are G1=29, G2=26 and D1=29. Every chain is single-field; none supplies nonvacuous unchanged-field coverage. Preserved proposal payloads differ from the authorized payloads, which equal the committed payloads. The complete original historical databases are outside this local handoff, so the audit verifies the chain records and original receipts, not a fresh scan of all 1,260 databases.

All 24 executable observation-witness tests pass. Archived command receipts retain 72 expected matches (44 SAT, 28 UNSAT), nine intended SAT projections and twenty selected UNSAT mutants. This is receipt verification plus fresh witness testing, not a new Alloy execution or arbitrary-history proof.

## D1 interpretation

The D1 two-direction proof is valid under its stated fixed environment/authorized value, independently declared responsibility relation, decision-independent operational reachability and biconditional implementation assumption: Admit iff G and policy-match. If only the forward implication is justified, the empty-intersection condition is sufficient but not necessary. G must not hide exact identity or the responsibility outcome. With policy-dependent histories, use the corresponding policy-dependent reachable set rather than implying a universal granularity ordering.

The paper should retain the source's scientific calibration: this is a characterization of safe permitted substitutions, not by itself a new general authorization theory or proof of arbitrary-length history preservation. Controlled E1 supplies an identity-only separator under declared instance responsibility. Historical A4 changes evidence/context and cannot stand in for that separator; the 84 correction chains provide legal-integration evidence. The current kernel's only bound-specific commit check is the INSTANCE_MISMATCH branch; the other checks are common.

## Actionable corrections and final verification cautions

1. **Portable verifier.** In `verify_evidence.py`, original line 37, replace `(ROOT/path).read_bytes()` with `(ROOT/path.replace('\\','/')).read_bytes()`. Preserve hash values and source manifests. The unmodified failure is in `verify-evidence-original.log`; portable and fresh-export passes are in `verify-evidence-portable.log` and `verify-evidence-fresh.log`.
2. **Stale supplement targets.** Original supplement lines 90 and 119 say the main text retains a numbered Proposition 1 and five-witness proof; line 129 says P0–P6 remain in a main contract table; line 468 points to a main conformance section. The current main has an unnumbered proposition/construction and no P0–P6 table or separately named conformance section. Replace these references with accurate current section descriptions, or restore the promised detailed target. Suggested wording at line 129: “The implementation uses operational checks P0–P6; their bounded-check and persisted-state mappings are detailed below.” At line 468: replace the absent main-section reference with explicit local domain distinctions, supported by the archived formal model.
3. **Completed-document tense.** Original supplement line 557 says the final audit “will map” the numbers. Replace with “The completion audit maps each main-text numerical claim to its controlled, historical or prospective evidence source.”
4. **Avoid overclaiming audit breadth.** Describe this revision as fresh offline rescoring of all planned formal arms plus verification of archived controlled/historical records. Do not state that the present audit recollected online trajectories, reran E1–E3, rescanned historical databases or reran Alloy.
5. **Verifier scope is narrower than manuscript validity.** Its citation gate hardcodes exactly 17 entries and its structural gates count nine sections/six keywords. If the revision legitimately adds citations, adjust the non-frozen manuscript verification gate rather than deleting a necessary citation or treating the old fixed count as a scientific invariant. It does not verify literature accuracy, every supplement cross-reference, every rendered page, or the D1 proof.
6. **Preserve interpretation gates.** Retain planned-arm versus received-trajectory wording; the 128 task-cluster resampling unit; U/I separation; G harness origin; N/G separation; explicit unknowns; A's limited checkpoint coverage; delivered-episode recovery denominators; and actual versus capped time distinctions. No principal numerical replacement is needed.

## Audit deliverables

- `independent_audit.py`: repeatable semantic comparison and independent counting script
- `independent-results.json`: complete machine-readable counts, effects, semantic comparisons and source-hash results
- `reference-integrity.json`: post-audit archive/reference preservation check
- `fresh-analysis/`: six fresh CSVs, complete summary and six generated figure files
- `analysis-run.log`: original offline analyzer output
- `witness-tests.log`: 24-test fresh pass
- `verify-evidence-original.log`: original portability failure
- `verify-evidence-portable.log`: all 29 checks after the isolated separator fix
- `verify-evidence-fresh.log`: all 29 checks using fresh online exports and fresh manuscript aggregates
- `verification-tree/`: independent writable verifier workspace, retaining the portable and original verifier files
