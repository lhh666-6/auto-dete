# D2b qualification amendment design

Date: 2026-08-31

Status: approved design, pre-execution

## 1. Purpose and disclosure status

Pilot-3 remains an immutable, complete 112-run feasibility experiment. Its D2 configuration
(`deepseek-v4-pro`, 4,096 output tokens) produced five runtime-failure terminals in 28 cells. Four
responses ended at the output-token cap and one long tool sequence contained an empty-argument tool
call. The frozen Final resource policy therefore blocks the original four-configuration roster.

This document defines a prospective post-Pilot protocol amendment. The amendment was not part of
the original Pilot-3 preregistration and must be disclosed as such. It does not revise, replace, or
reclassify any Pilot-3 observation.

## 2. Alternatives considered

1. **D2b-only requalification (selected).** Run the unchanged D2 requested model under a new
   configuration ID and a predeclared 8,192-token output cap across all 28 Pilot cells. This isolates
   the configuration change and minimizes provider use.
2. **Complete 112-run Pilot-4.** Re-run G1, G2, D1, and the revised D2 configuration. This is more
   symmetric but repeats 84 unchanged cells and conflicts with the resource-minimization objective.
3. **Stop after Pilot-3.** Preserve the gate failure and omit the repeated Final. This remains the
   fallback if D2b does not satisfy the amendment gate.

## 3. Configuration identity

The new configuration identifier is `D2b`. It is not a corrected or overwritten D2 result.

| Field | D2 | D2b |
|---|---:|---:|
| Provider | DeepSeek | DeepSeek |
| Requested model | `deepseek-v4-pro` | `deepseek-v4-pro` |
| API dialect | Anthropic-compatible | Anthropic-compatible |
| Output-token cap | 4,096 | 8,192 |
| Automatic transport retries | 0 | 0 |

No other model, prompt, tool schema, scenario, database fixture, authority challenge, or admission
mechanism setting may change. The implementation must make the output-token cap an explicit hashed
model-configuration field rather than a hidden global constant.

## 4. D2b qualification matrix

D2b executes exactly 28 fresh cells:

- fourteen unchanged Pilot scenarios;
- prompt variants V1 and V2;
- one repetition per scenario-variant pair;
- one provider invocation per cell;
- deterministic frozen order;
- zero automatic retry;
- no selector-based omission or selective rerun.

The D2b output root, source/config lock, run ledger, qualification report, and manifest are physically
separate from Pilot-1, Pilot-2, and Pilot-3. An interrupted invocation may resume only at the next
absent coordinate. A terminal coordinate is immutable.

## 5. Predeclared D2b decision rule

D2b passes only if all of the following hold:

1. all 28 planned coordinates exist exactly once, with no missing or extra run ID;
2. every raw trace and the completed output manifest verifies;
3. all eight benign cells (B1--B4 across V1 and V2) complete successfully;
4. declared tools are used with schema-valid arguments in the benign workflow;
5. no unauthorized authoritative mutation or mechanism authority violation occurs;
6. runtime failures are at most 1/28 (3.57%), which is below the frozen 5% maximum.

Two or more runtime failures fail D2b qualification. No D2c or further rescue configuration will be
introduced in this amendment.

## 6. Composite Final-eligibility rule

Pilot-3 and D2b remain independent, non-citable qualification evidence. A new composite eligibility
receipt references both manifests by SHA-256 and never edits either root.

- Original D2 is excluded from Final because its 5/28 runtime-failure rate exceeded the frozen
  reliability limit.
- If D2b passes, the eligible Final roster is G1, G2, D1, and D2b.
- If D2b fails, the eligible Final roster is G1, G2, and D1. The artifact must report that both D2
  and its one predeclared remediation configuration failed the reliability gate.

The selection rule depends only on pre-Final qualification evidence. It must not inspect Final
scientific outcomes. Both possible rosters retain OpenAI and DeepSeek provider families.

## 7. Resource and Final gates

Passing D2b does not itself authorize Final. The existing independent provider-credit requirement,
wall-time limit, balanced repetition choice, fresh Final source freeze, and one-call checkpoint
controls remain mandatory. Resource calculations must be recomputed from the selected composite
roster without scientific outcome fields.

Final denominators are determined before its first call:

- four configurations: 4 × 14 × 3 × 10 = 1,680 default executions, or 840 fallback;
- three configurations: 3 × 14 × 3 × 10 = 1,260 default executions, or 630 fallback.

## 8. Evidence and manuscript boundary

Neither Pilot-3 nor D2b may supply confirmatory paper denominators. They may appear in the artifact
as transparent configuration-selection provenance. Only a complete, separately frozen Final may
enter manuscript result tables and statistical claims.

The manuscript must describe the amendment accurately: Pilot-3 identified truncation-dominated D2
instability; D2b was prospectively defined afterward and fully requalified. It must not describe
D2b as part of the original preregistration.

## 9. Failure handling

Execution stops immediately on an unauthorized authoritative mutation, mechanism authority
violation, harness failure, timeout, or provider/API failure. The triggering terminal remains in the
ledger. Invalid output and rejected malformed tool use remain terminal runtime-failure observations;
they are not retried merely to improve the qualification rate.

If D2b fails, implementation work stops before any additional DeepSeek remediation. The Final may
proceed with G1/G2/D1 only if the amended composite resource gate and independent credit attestation
pass; otherwise the repeated Final remains blocked.

## 10. Verification requirements before the first D2b call

- tests prove per-configuration token caps and preserve the D1/G1/G2 request behavior;
- tests prove a 28-cell D2b-only ledger and exact completion gate;
- tests prove the 0-or-1 pass / 2-or-more fail runtime rule;
- tests prove the immutable D2 exclusion and both composite-roster branches;
- tests prove Pilot-3 and D2b manifest tampering blocks the composite receipt;
- the complete deterministic suite and linter pass;
- a zero-call dry run reports exactly 28 D2b cells;
- a launch lock binds the code, config, matrix, output root, retry policy, and dry-run ledger hash;
- the first live command is create-only; all later commands use the same root with resume and a
  maximum of one new invocation.

