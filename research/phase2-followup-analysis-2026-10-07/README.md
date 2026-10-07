# Supplementary paired evaluation of deployment A

This independent analysis covers the separately frozen later collection of 117 deployment-A task pairs (234 arms). Selection used the original **pre-response quota failure**, before any model response or policy exposure. The original 512-arm primary collection is unchanged and is not pooled with these 234 arms here. The contribution is the observed agent recovery behavior; the quota selection and collection period delimit its scope.

## Verified findings

All 117 pairs reached the shared review checkpoint. The cohort comprises N=29, G=15, V=16, E=14, L=29, and R=14 pairs. Context completed 114/117 tasks; bound completed 116/117. Context integrity was I=1 in 102 and I=0 in 15; bound integrity was I=1 in all 117. Neither policy had unknown integrity. All 15 context integrity failures were completed G tasks with candidate substitution. These are retained in the failure archaeology alongside four incomplete tasks (19 distinct arms total).

In G, all 15 bound arms received delivered, recoverable `INSTANCE_MISMATCH` feedback and finished with U=1/I=1. Eight reused the reviewed candidate; seven reauthorized. Relative to each matched context arm, bound used a mean 1.6 additional suffix tool calls (median 1) and 17.967 seconds additional suffix time (median 14.532 seconds). N has 58 transitions, 29 per policy, all same-instance, policy-admissible and A-instance-compatible. The 83 delivered recovery episodes are descriptive and include non-commit capability feedback in R.

The supplementary paired completion difference (bound minus context) is +1.7094 percentage points, with a scenario-stratified task bootstrap percentile interval [0, 4.2735] points. This is an explicitly exploratory application of the original bootstrap method to the selected A-only cohort, **not the preregistered A+B primary estimator**. Its uncertainty is conditional on the selected tasks and observed collection; it does not correct selection or identify an effect across deployments or collection periods.

Three runtime failure arms remain: L-010/context (`ACCOUNT_QUOTA_EXHAUSTED`), E-015/context (`DEPLOYMENT_CHANGED`) and E-015/bound (`prefix_failure`, also `DEPLOYMENT_CHANGED`). E-009/context ended with an abandon trajectory. E-015/bound's terminal label does not erase its successfully reached shared checkpoint. `DEPLOYMENT_CHANGED` records a runtime identity-check failure; returned model and revision are null, so the logs do not establish that a model revision changed.

## Reproduce

Run from the repository root with Python 3.11 and `jsonschema` available. The verified environment was Python 3.11.9 / jsonschema 4.26.0. No API, model invocation, network access, or credentials are used by these analysis commands.

```powershell
python -B -m unittest discover -s research/phase2-followup-analysis-2026-10-07 -p test_analysis.py -v
python -B research/phase2-followup-analysis-2026-10-07/analyze.py
python -B research/phase2-followup-analysis-2026-10-07/audit_usage.py
python -B research/phase2-followup-analysis-2026-10-07/verify_outputs.py
```

Default output is `research/phase2-followup-analysis-2026-10-07/outputs`. A second deterministic reproduction can be written without replacing the review outputs by supplying `--output research/phase2-followup-analysis-2026-10-07/reproduction` to each of the last three commands. The output must be a descendant of this package; paths elsewhere are refused. Compare each deterministic table/JSON against `outputs`; `verification.json` records output hashes and source hashes. Source and raw collection sibling directories must retain their existing layout.

The initial 13 guardrail tests were written and observed failing before implementation; additional nested-error, native-error classification and attempt-inventory tests were also observed failing before their helpers were added. All 18 tests now pass. Cross-file checks reconcile independent scores, every scheduled row, failures, transitions, episodes, provider request IDs, native usage and native file hashes.

## Traceability and methods

The input is `../agent-policy-phase2-quota-recovery-2026-10-07/recovery-manifest.json` and its immutable `results` tree. The parent experiment is `../agent-policy-phase2-formal-2026-10-07`. The script verifies the recovery manifest's sidecar digest and derived freeze identity; verifies every original frozen source/design hash; checks the original 15,832 result files against the pre-recollection hash ledger; reproduces eligibility from original raw quota errors; and checks task, configuration, assignment, policy order and event identities against their frozen records. Recovery raw-file hashes are written to `source-file-hashes.json` and compared before and after analysis.

The selection rule takes the final completed attempt of each terminal pair, preserving every earlier attempt in the ledger and native accounting. Duplicate/missing pairs or attempts, unfinished attempts, assignment drift and untracked behavioral retries are rejected. This completed collection has exactly 117 pair attempts, one per pair. Transport retries within attempts remain in their original provider directories and are never collapsed into new task observations. No failure-based selection or rerun occurs.

Each of the 234 arms is rescored with the unchanged frozen `score_run`; `validate_run` separately validates each arm and shared prefix. All 7,989 events passed schema, chain, artifact, task/configuration/freeze identity and state-history checks. Checkpoint clone consistency is covered by the frozen validator. Independent scores matched all 234 cached score files and 234 pair-result score entries exactly (468 comparisons); all 117 pair-result objects matched their status ledger. Zero validation errors and zero validation violations were found. The invariant violations reported as scientific outcomes by the scorer (15 G context A-instance failures) remain outcomes and must not be confused with audit-validation errors.

Table extraction adapts the frozen exporter logic. It calls that module only for general CSV/event/usage helpers; it never calls the frozen A+B/128-task export entry point or its paired estimator on an A-only cohort. For every task, a bound-minus-context contrast is computed. Bootstrap replicates sample tasks with replacement **within each scenario**, retaining both policies and the observed number of tasks in each scenario. There are 10,000 draws using seed 20261007; sorted percentile endpoints use indices `int(.025*(B-1))` and `int(.975*(B-1))`, matching the original method. Missing binary continuity outcomes would be retained with lower/upper identification contrasts; none occurred. The flat continuity interval is a consequence of fixed scenario weights and identical within-scenario contrasts, not population certainty.

All planned arms remain in completion denominators. The failure CSV includes incomplete utility, I=0 and I=unknown according to the original export convention. Suffix elapsed time includes observed runtime delays; time-to-success uses the original 720,000 ms cap and assigns it to unsuccessful arms. Paired friction is computed at task level, without restricting to successful tasks. Logical per-arm elapsed time includes the common prefix; unique accounting counts that prefix once per actual attempt.

Native usage is verified against the original stdout `turn.completed` records and provider thread IDs. There are 1,477 native provider stdout attempts and 1,474 model responses, each with matching native usage and request identity. Three retained failed invocations have no completed usage. One failed timeout stream contains a diagnostic `error` item; no unexpected native tool action was found. Observed completed usage totals are 34,418,220 input tokens and 122,723 output tokens, including 26,312,704 cached input tokens and 44,775 reasoning output tokens as separately reported native fields. These fields overlap; do not add cached inputs to inputs or reasoning outputs to outputs. Missing failed-attempt usage is unknown, not zero, so observed totals are not complete billable usage. Currency cost is unavailable. Every response records requested alias `gpt-5.6-terra`, with null returned-model and returned-revision fields.

Collection ran from 2026-10-07 00:15:55 UTC to 09:46:49 UTC (08:15:55–17:46:49 Asia/Shanghai). Source hashes:

- Parent freeze master: `7773563b40c8db30d6def121915f50fbad032537edde32afd4ba39ec3eea744b`
- Recovery manifest: `3f11ebba8fb43b7ce2582e229678366a2338751505e61a667f02aea4c9b82e8f`
- Frozen runner/scorer: `b977501a058b1f061f5feecbc9fcab465da04af8ea93e1ea49b255cf113f6ebc`
- Event schema: `5905017ebc95740700f084e2fdfc8f40fa40786fab69d0f8d1335d002d2bcd12`

## Output map

| File in outputs | Contents |
|---|---|
| analysis-summary.json | Cohort, outcome, recovery, paired estimates, audit and method scope |
| table1-outcomes.csv | Original-compatible 12 scenario/policy aggregate rows |
| table2-continuity.csv | Original-compatible 231 accepted non-idempotent transitions |
| table3-recovery.csv | Original-compatible 83 delivered recovery episodes |
| table4-utility-friction.csv | Original-compatible 234 arm-level cost/completion rows |
| paired-effects.csv | 117 matched differences; bound minus context |
| failure-archaeology-all-arms.csv | All 19 failure or integrity-failure arms |
| scored-arms.json | Independent full frozen scores with attempt and policy provenance |
| arm-rows.json | Full selected arm extraction, including termination payloads |
| attempt-ledger.json | Every retained task-pair attempt and the selection flag |
| validation-ledger.json | Prefix and arm validation findings |
| prefix-accounting.json | Prefix elapsed time and usage, charged once per attempt |
| source-file-hashes.json | Immutable raw result file inventory |
| native-attempt-usage-ledger.json | Every native stdout attempt, hash, response mapping and usage |
| native-usage-summary.json | Full native-attempt counts and observed usage with missingness |
| verification.json | Cross-file checks, dependency versions, source and output hashes |

The separately prepared completed-A sensitivity view, if used, belongs in its own explicitly post hoc package. No such recombination is produced or silently substituted for primary results here.
