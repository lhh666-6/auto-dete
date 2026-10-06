# Independent Phase 2 pilot code review

Date: 2026-10-06. Scope: `src/phase2`, tests and the approved frozen v0.2 pilot protocol. Read-only review; implementation and tests were being edited concurrently by the main agent. No online pilot was run by this reviewer. Deterministic fixtures are engineering evidence only.

## Assessment

The basic scientific contrast is implemented correctly: same-context sibling candidates share retained evidence and lineage while their instance IDs differ; context permits their execution and bound rejects it. The host uses the same commit path except for the instance check. Database and visible conversation copies are independent after a common checkpoint. Real tool results are appended before the next provider decision, and the G action is clearly labeled as harness-origin. These are valuable tested foundations.

The initial implementation is **not ready for an online pilot without the important fixes below**. Several issues concern independent measurement and audit coverage rather than the intended policy contrast. The main agent has begun implementing fixes; this report records the independently observed defects and does not claim that concurrent fixes have all passed final verification.

## Important findings

### 1. Rejected mutations can pass the independent integrity audit

Location: `runner.py:validate_run`, `runner.py:score_run`; `oracle.py:integrity`.

The validator initially verifies artifact hashes and event structure, but does not reconcile each tool's before/after authoritative head with the mutation journal or independently enforce rejected-action stutter. The oracle then checks the final state's self-contained journal. A transient authoritative mutation visible in raw snapshots can consequently disappear from the final journal and be scored I=1.

**Reproduction:** in a temporary G fixture, wrap `Host.call` so an INSTANCE_MISMATCH rejection changes `reference_note`, then restore it immediately before the agent later commits c1. The admission log records `state_unchanged=false`, and raw snapshots show the mutation. The scorer returned **U=true, I=1, audit_errors=[]**. No source file was modified for this reproduction.

**Required fix:** independently compare initialization, every authoritative before/after snapshot, recorded transitions, and final state. A proven head mutation on a rejected decision must produce I=0, even if later restored. Incomplete coverage should be unknown. Validate shared-prefix chains and artifacts as well as the arm, since a hash of an unchecked prefix is not an audit of its contents. Add the transient rejection-mutation regression.

### 2. A proven violation is lost when another field is missing

Location: `oracle.py:integrity`, originally lines 42–70.

All transition checks are constructed inside one `try` block. A missing evidence field raises before the checks dictionary is returned, discarding already available evidence of instance mismatch and all other violations.

**Reproduction:** on a successful transition, change `grant.reviewed_candidate_id` to another ID and delete `transition.evidence`. The oracle returned **I=unknown, continuity_failures=0**, despite an explicitly identifiable A_instance violation. This contradicts the frozen addendum's violation-over-missing precedence.

**Required fix:** evaluate continuity and each available check independently; retain proven violations while separately recording unavailable checks. The main agent has added a regression for this reproduction.

### 3. Reviewed certificates are not independently authenticated

Location: `oracle.py:integrity`, original certificate check near line 53.

The executed candidate's certificate and context hash are checked, but the stored reviewed candidate's certificate and context hash are not. Equal context and readable evidence do not validate the reviewed envelope.

**Reproduction:** change only `transition.grant.reviewed_candidate.certificate_id` to `bad`. The oracle returned **I=1**.

**Required fix:** authenticate both the reviewed and executed candidates against their content addresses and context hashes, and retain review/source binding checks. The main agent has added the corresponding mutant regression.

### 4. Continuity incidence incorrectly inherits all Integrity unknowns

Location: `runner.py:score_run`, original `continuity_failure_incidence` expression.

The primary continuity outcome is null whenever I is unknown. Missing evidence bytes can make full Integrity unknown while transition coverage and every reviewed/executed instance ID still fully establish continuity. Conversely, an identified mismatch remains a proven incidence=1 even with unrelated missing audit data.

**Required fix:** score continuity with its own coverage requirements: 1 for any proven executed mismatch, 0 only when all successful transitions are enumerated with classifiable matching IDs, unknown otherwise. Do not exclude classifiable runs merely because a different integrity check is unknown. Report planned-denominator bounds. The main agent has added a regression for the independent classification.

### 5. Behavioral recovery paths count failed operations as completed recovery actions

Location: `runner.py:score_run`, path classification from tool-call names.

Any call to `request_authorization` labels the path reauthorization, even if the tool rejects it. Thus a request for a nonexistent candidate followed by a successful reuse of c1 is mislabeled reauthorization. A failed `propose` similarly contributes to reproposal classification. The protocol's recovery taxonomy requires valid receipts and correct effective review targets, not just attempted tool names.

**Required fix:** join calls to results, classify successful operations and effective target bindings, and separately retain failed attempts and invalid loops. Preserve reverify where supported rather than losing it in a single coarse label. Add a failed-reauthorization-then-reuse regression.

### 6. Malformed successful provider responses can abort collection outside the failure handler

Location: `providers.py:deepseek`, JSON decoding/body traversal; `runner.py:loop` transport exception handler.

HTTP 200 followed by malformed JSON raises `JSONDecodeError`; a non-object body or malformed content entries can raise attribute/type errors. These escape the `TransportError` handler. A provider protocol failure can therefore prevent arm finalization and subsequent planned-arm execution, rather than become a recorded terminal/format-repair outcome.

**Required fix:** normalize provider-body failures into a documented error class or action-format failure, retain raw response bytes, and finish the affected run. Verify malformed JSON and incorrect response-body shape with mocked HTTP responses; do not call live services for these tests.

### 7. Exact feedback delivery is checked only by error code

Location: `runner.py:validate_run`, feedback comparison.

The delivery validator initially checks that a matching decision reference and some response exist, then compares only `error_code`. Dropping or changing the remaining feedback can still be classified as delivered. The scorer also builds confirmed denominators from delivery claims even when validation reports feedback failure.

**Required fix:** compare the complete actual tool result/notice payload with the corresponding authoritative result artifact and bind it to the exact request/response attempt. Only independently proven delivery should enter the confirmed denominator; distinguish attempted-but-unknown delivery. Keep later model failures in the denominator after proven delivery.

## Issues already being repaired during review

- **Invalid commit arguments:** `record_tool` initially unconditionally indexed commit arguments after the host returned INVALID_ARGUMENTS. A model-selected `commit {}` aborted the pair. The main agent added a regression and an explicit path that logs the error without constructing an admission decision. That regression passed in the observed concurrent test snapshot.
- **Host exception after mutation:** tool exceptions initially escaped without a final state audit. The main agent added uncertain-outcome feedback and before/after persistence. Its mutation-after-exception regression passed in the observed snapshot.
- **Recovery numerator:** `recovered` initially meant any later accepted commit, including runs lacking a completed accurate final report. The main agent changed it to require completed U and I=1 and added G eligibility/success fields. The missing-report regression passed in the observed snapshot. G must retain all legal-checkpoint bound arms, including failures before confirmed feedback; conditional delivered recovery remains a separate denominator.

## Resource and reproducibility checks

- HTTP retries are restricted to 429/5xx/transport failures, at most two retries, with 2s/8s waits and Retry-After respected within the overall timer. Responses and attempts are retained. No model-selection-by-pilot-result or semantic task restart is present in the reviewed loop.
- The CLI starts ephemeral requests with the full visible conversation and requests disabled native capabilities. This provides explicit message-state continuation, not cloning hidden provider state. Native actions are rejected if observed in completed events.
- The frozen output limit is 4096 tokens, but the CLI config declares `max_output_tokens=null` and `output_cap_limitation=CLI upstream output cap unavailable`. This is a disclosed implementation limitation, but it conflicts with a claim that all frozen output/token caps are enforced. Before pilot, either implement an actual supported upstream cap or explicitly version the execution freeze and budget claims. Post-hoc response truncation would not establish an upstream token/currency hard cap. Monetary cost is correctly unknown for account-backed CLI.
- Ensure the final execution freeze hashes the actual implementation, rendered fixture bytes, prompts, feedback interface, assignments, dependencies, and selected configurations after fixes. The currently reviewed design freeze does not itself establish an immutable implementation freeze.
- Tests cover valid controls, type-sensitive canonical values, checkpoint isolation, same-context substitution, rejection head stutter in the normal host, grant supersession, replay, evidence/candidate tampering, copy-forward, and G feedback. Missing mutation coverage and provider-body failures need the additional adversarial checks above.

## Scope and online status

L/N/G-only implementation is the intended **four-case pilot** (L1/N2/G1, two configurations, two policies), not an omission of the formally planned E/V/R arms. Formal acquisition remains unauthorized and unimplemented. Tests for shared guards may use deterministic mutants without being counted as online scientific trajectories.

The availability artifact reports **A: CODEX_TIMEOUT; B: HTTP_402**. The parent identified the DeepSeek response as insufficient balance. No selected two-provider configuration or actual online pilot has been established. These are external availability blockers, not evidence of scientific policy failure, and deterministic provider fixtures must never be substituted for the requested online pilot.

## Verification snapshot

An independently run concurrent-edit suite finished **28 tests**, with **two failures and one error** in the newly added oracle regressions: violation precedence, reviewed certificate authentication, and the not-yet-added continuity classification field. All other observed tests passed. This is a transient development snapshot, not a final failing verdict after the main agent's subsequent fixes. The three direct oracle/stutter reproductions above were also run separately. A final review should rerun the completed suite and record which findings remain open before any online pilot starts.

## FINAL RETEST — PASS for the bounded engineering pilot

Final independent retest, 2026-10-06: **34 tests passed, no failures or errors**, in 4.937 seconds. This addendum supersedes the initial readiness assessment and the transient 28-test development snapshot above. The reviewer changed only this report and used temporary local fixtures; no implementation edits or online arms were executed.

The important findings have been addressed in the reviewed final code:

- Cross-snapshot reconciliation checks initialization, every tool before/after head, mutation journal, accepted receipts, final state, and the shared-prefix checkpoint. The transient mutation on a rejected request now scores I=0 even after later restoration. Prefix corruption is detected rather than treated as a valid clone.
- Per-check lazy evaluation preserves an independently proven instance mismatch when evidence is missing. Both reviewed and executed certificates are authenticated. Continuity classification has separate mutation/identity coverage, rather than inheriting every full-Integrity unknown.
- Invalid argument responses and post-mutation tool exceptions are retained without silently assuming stutter. Recovery requires completed accurate task delivery and I=1; G checkpoint eligibility is reported separately from conditional delivered-rejection recovery. Failed authorization attempts no longer become successful reauthorization paths.
- Malformed HTTP 200 envelopes are normalized into a finalizable recorded provider error. Missing feedback-input and final-state snapshots return audit uncertainty instead of crashing. The state-unavailable fallback also preserves I=0 when raw snapshots have already proven a violation.
- The validator compares the **complete actual feedback object**, not just its error code, and binds it to the exact model input/request/response. Scoring uses the validator's proven-feedback ID set. An additional independent temporary mutant retained INSTANCE_MISMATCH but changed the feedback's commit request ID, updated the input references and event hashes, and was correctly rejected as `feedback_content_mismatch`; its confirmed delivered-recoverable denominator was zero. Removing the relevant feedback message likewise produced zero confirmed delivery after the event-specific fix.

The latest availability artifacts supersede the earlier external blocker status: configuration A is **AVAILABLE**, requested `gpt-5.6-terra`, using the existing system proxy; configuration B is **AVAILABLE**, requested and returned `deepseek-v4-flash`, using the user-authorized DSH credential stored encrypted outside the repository. These remain interface availability checks, not recovery performance or online pilot results. No online arms had started at final review.

No remaining important issue was identified for the authorized four-case, two-configuration, two-policy engineering pilot. This verdict does not establish readiness for formal 128-arm acquisition or production deployment. `run_pilot.py` prepares the actual execution package with source/test/input/configuration/assignment hashes before starting the predefined 16 arms.

The CLI upstream 4096-token output cap remains unavailable. The execution freeze explicitly records that deviation: the upstream output cap applies only to DeepSeek, while both providers retain request/response/tool/time limits. The pilot report must preserve that limitation and must not claim an upstream CLI token cap or currency hard cap. This is a disclosed budget limitation, not a verified cap. Availability aliases also remain mutable provider deployments, and the local hash/timestamp freeze is not an immutable public preregistration.
