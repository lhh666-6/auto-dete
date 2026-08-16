# Authority-Aware Novelty Design for Auto-Decte

**Date:** 2026-08-16
**Status:** Approved design for DSH prototype work
**Target manuscript:** Auto-Decte ESWA journal extension
**Stable experiment baseline:** `195355a`

## 1. Objective

Strengthen Auto-Decte's novelty without expanding it into a new web platform or claiming a general access-control theory. The work combines:

- **Track B — Executable Authority Contract:** turn the existing candidate--fact boundary into a set of named properties, mechanisms, negative tests, and results;
- **Track C — Evidence-Bound Authority Transition:** require every fact-transition request to carry a verifiable candidate certificate, then route review according to evidence integrity, provenance, freshness, and predictive uncertainty.

The intended contribution is narrower than safe AI, formal information-flow security, or a new selective-classification algorithm. It is an expert-system architecture for document intelligence in which machine-derived values remain non-authoritative, and eligibility for human authorization is explicitly evidence-bound and executable.

## 2. Non-goals

This prototype must not:

- restore or build FastAPI, React, PWA, authentication, RBAC, or a new UI;
- add more OCR or LLM features merely to increase system size;
- modify the ESWA manuscript before the prototype passes its novelty gate;
- claim a security proof, penetration-test result, or protection against privileged database/host compromise;
- claim control of human dangerous-confirmation risk before a controlled human study exists;
- silently optimize automatic completion at the expense of reliable failure detection;
- use production records or identifiable form photographs.

## 3. Closest prior-work threats

A targeted neighbor scan identified four areas that constrain the novelty claim:

1. **Selective prediction and learning to defer** already study rejection and delegation to human experts. See Mozannar and Sontag, [Consistent Estimators for Learning to Defer to an Expert](https://proceedings.mlr.press/v119/mozannar20b.html).
2. **Human--AI selective prediction** already shows that human behavior affects the value of algorithmic selection. See [Role of Human-AI Interaction in Selective Prediction](https://doi.org/10.1609/aaai.v36i5.20465).
3. **Automation bias and selective adherence** already study whether people accept algorithmic advice. See [Human–AI Interactions in Public Sector Decision Making](https://doi.org/10.1093/jopart/muac007).
4. **Information-flow labels and declassification** already separate data labels from component identity. See [Protecting Privacy Using the Decentralized Label Model](https://doi.org/10.1145/363516.363526).

Therefore, Auto-Decte cannot claim novelty merely because it rejects uncertain predictions, sends work to a human, attaches provenance, or labels machine output as non-authoritative. Its defensible novelty must come from the following combination:

> An evidence-bound candidate certificate is an enforced precondition for a version-checked human fact transition, while review routing remains authority-preserving and is evaluated through matched architecture baselines and executable fault properties.

This is a targeted positioning check, not an exhaustive systematic review. A full novelty claim still requires a broader literature search before submission.

## 4. Track B: Executable Authority Contract

### 4.1 Contract properties

The prototype must expose four properties with stable names.

#### P1 — Machine noninterference

No exposed machine service has a transition that creates or revises an authoritative fact:

\[
\forall m\in M,\quad m\not\rightarrow F.
\]

Negative tests must attempt fact-like operations through recognition, retrieval, and AI-adapter paths.

#### P2 — Stale-review safety

A decision bound to an older fact version cannot authorize a transition:

\[
version(H_t)\neq version(F_t)\Rightarrow reject.
\]

The test must create a valid candidate, advance the fact version independently, and demonstrate that the original decision is rejected without modifying the current fact.

#### P3 — Provenance completeness

Every created fact version must support reverse trace:

\[
F_t\rightarrow H\rightarrow C\rightarrow E.
\]

The trace must identify the decision, candidate, evidence hash, producer/version, and relevant field locator. Missing lineage must prevent the transition rather than merely create an incomplete audit record.

#### P4 — Model substitutability

Changing the recognizer may change candidate content and uncertainty, but not the authority contract:

\[
M_1\rightarrow C,\quad M_2\rightarrow C,
\]

while both preserve:

\[
C\rightarrow H\rightarrow F.
\]

At least two candidate producers must pass the same certificate validation and transition tests.

### 4.2 Required paper-facing matrix

The eventual output should support one compact table with these columns:

| Property | Enforcement mechanism | Positive test | Negative test | Metric/result |
|---|---|---|---|---|
| P1 | candidate-only machine port | candidate persists | direct fact write attempted | fact unchanged |
| P2 | expected-version check | current review accepted | stale review submitted | stale transition rejected |
| P3 | mandatory certificate lineage | reverse trace complete | evidence/producer omitted | transition rejected |
| P4 | producer-neutral contract | two producers accepted | producer-specific bypass attempted | same boundary preserved |

No property may appear in the manuscript without an executable test and a stored result artifact.

## 5. Track C: Evidence-Bound Authority Transition

### 5.1 Candidate certificate

Introduce an immutable `CandidateCertificate` value object. The phase-one prototype should include:

- `candidate_id`;
- `evidence_hash`;
- `evidence_locator` describing page/region/field;
- `template_id` and `template_version`;
- `source_kind`: recognition, retrieval, AI suggestion, or manual entry;
- `producer_id` and `producer_version`;
- `calibration_id` where predictive selection is used;
- `confidence` or decision-margin value;
- `selected`/abstained state;
- `lineage_parent_ids` for derived candidates;
- `target_record_id`;
- `expected_fact_version`;
- `created_at`;
- integrity results for evidence, identity, provenance, and freshness.

The certificate is not a cryptographic identity system. In phase one, it is a content-addressed, immutable application object with explicit validation rules.

### 5.2 Transition rule

A fact transition is eligible only when all three terms are present:

\[
FactTransition
=
HumanDecision
+
ValidCertificate
+
CurrentVersion.
\]

The transition validator must reject:

- a missing or mismatched evidence hash;
- an absent field locator;
- an unknown source or producer version;
- a missing calibration identifier when selection is claimed;
- an expired/stale expected fact version;
- incomplete lineage for a derived candidate;
- an attempt to convert an abstained candidate without explicit manual resolution;
- an action lacking an attributable human decision and reason.

Rejection must be explicit and leave the authoritative fact unchanged.

### 5.3 Authority-preserving routing

The policy returns one of three routes:

1. `STANDARD_REVIEW` — certificate valid and no enhanced-risk condition;
2. `ENHANCED_REVIEW` — certificate valid but uncertainty, disagreement, or weak evidence requires additional attention;
3. `REJECT_REACQUIRE` — certificate invalid or evidence/identity/freshness preconditions fail.

No route creates a fact automatically. Routing only changes the level of human review or requests new evidence.

Hard validity checks run before any numerical score. A high model confidence must never compensate for broken evidence integrity, incomplete provenance, or a stale record version.

## 6. Optional Track C extension: risk-budgeted routing

Only after the certificate prototype passes should DSH explore a routing score:

\[
r(c)=f(u,1-i,1-p,1-v,d),
\]

where:

- `u` is predictive uncertainty;
- `i` is evidence-integrity validity;
- `p` is provenance completeness;
- `v` is state freshness;
- `d` is model or source disagreement.

The long-term optimization target is:

\[
\min_{\pi}\ \mathbb{E}[C_{review}]
\quad\text{subject to}\quad
R_{danger}(\pi)\leq\epsilon.
\]

Before a human study, `R_danger` is unavailable. The prototype must use the narrower label **fault-escape surrogate** and compare policies at matched review/reacquisition budgets. It must not describe surrogate control as control of human confirmation risk.

Weights must not be selected to make the evaluation set look favorable. They must be fixed by configuration, calibrated on a disjoint split, or learned using an explicitly separated training/calibration protocol.

## 7. Architecture baselines

The benchmark must compare three isolated architectures using identical candidate values and injected faults:

### A. Direct editable/write path

Machine output can modify the operational record. This unsafe architecture exists only inside the benchmark and must never connect to production or real records.

### B. Ordinary human confirmation

A reviewer can confirm or edit machine output, but the benchmark omits the complete certificate, stale-version protection, or reverse-trace precondition. Exact omissions must be documented; this baseline must not be intentionally crippled beyond that definition.

### C. Auto-Decte authority contract

Machine output remains a candidate. Fact creation requires a valid certificate, current expected version, and attributable human decision.

The comparison must distinguish architecture properties from UI appearance. All three conditions should use the same recognition outputs and equivalent review information whenever the architecture permits it.

## 8. Failure handling and evaluation metrics

Automatic complete-form success is a throughput measure, not the primary safety criterion. The prototype must report separately:

- automatic pipeline completion rate;
- detected-failure/manual-routing rate;
- silent fault-escape rate;
- invalid-transition rejection rate;
- valid-certificate coverage;
- reverse-trace completeness;
- stale-transition containment;
- review or reacquisition burden.

A result such as 75% automatic completion, 25% reliably detected manual routing, and zero observed silent wrong facts is scientifically meaningful. It may be preferable to a higher completion rate obtained through an unreliable fallback.

For a later human crossover study, the primary endpoints are:

- final factual accuracy;
- dangerous confirmation rate:

\[
R_{danger}
=
\frac{\text{wrong machine values accepted as facts}}
{\text{wrong machine values presented}}.
\]

Secondary endpoints are review time, missed errors, unnecessary corrections, manual-routing rate, and inappropriate AI-suggestion acceptance.

## 9. Novelty gates

The prototype enters the manuscript only if all applicable gates pass.

### Gate N1 — Enforced rather than descriptive

Certificate fields must be transition preconditions. If they are merely extra audit metadata written after confirmation, Track C adds no meaningful novelty.

### Gate N2 — Distinguishable from ordinary confirmation

The architecture baseline must demonstrate at least one stale, incomplete-provenance, or evidence-mismatch case that ordinary confirmation permits but the authority contract rejects.

### Gate N3 — Matched-budget routing value

If risk-budgeted routing is claimed, it must reduce fault escape at a matched review/reacquisition budget, or reduce review burden at a matched fault-escape level, on a held-out evaluation split.

### Gate N4 — No circular evaluation

The same rule used to inject a fault cannot be the sole rule used to detect it. At least some faults must be generated independently of the tested validation condition.

### Gate N5 — Claim discipline

The evidence must support the exact intended claim. A property-test result supports an application-contract claim, not a general security theorem. A simulated reviewer supports workflow execution, not a human-factors claim.

If N1 or N2 fails, retain Track B only. If N3 fails, retain the certificate architecture but do not claim a new routing method.

## 10. Work isolation and ownership

### Codex documentation area

Codex owns only this design document during the DSH prototype phase:

```text
D:\Claude_Design\auto-decte-paper\docs\superpowers\specs\
  2026-08-16-authority-aware-novelty-design.md
```

Codex will not modify experiment or manuscript files until the DSH commit is reviewed and the user approves integration.

### DSH worktree

Create an isolated worktree from the verified experiment baseline:

```powershell
git -C D:\Claude_Design\auto-decte-paper\experiments\auto-decte worktree add `
  D:\Claude_Design\auto-decte-paper\.worktrees\dsh-authority-novelty `
  -b dsh/authority-novelty 195355a
```

DSH owns only these phase-one files:

```text
app/domain/authority.py
app/application/transition_policy.py
benchmarks/authority_routing.py
tests/unit/test_authority.py
tests/benchmarks/test_authority_routing.py
docs/dsh/authority-prototype-notes.md
```

DSH must not edit during phase one:

```text
eswa/
app/adapters/database/
app/application/review_forms.py
app/ui/
config/
existing benchmark artifacts
```

The phase-one implementation should be a pure-domain prototype with deterministic inputs. Integration into persistence and the existing review service is a separate, user-approved phase.

## 11. DSH implementation brief

The following block can be supplied directly to DSH:

> Work in `D:\Claude_Design\auto-decte-paper\.worktrees\dsh-authority-novelty` on branch `dsh/authority-novelty`, based on commit `195355a`. You are not alone in the codebase: do not revert or overwrite changes outside your owned files. Implement a pure-domain prototype of `CandidateCertificate`, certificate validation, and authority-preserving routing with `STANDARD_REVIEW`, `ENHANCED_REVIEW`, and `REJECT_REACQUIRE`. Hard integrity/provenance/freshness failures must run before uncertainty scoring, and no route may create or modify a fact. Add deterministic architecture-baseline and fault-routing benchmarks plus unit tests. Use only the six owned phase-one files listed in the design. Do not modify the ESWA manuscript, database adapters, existing review service, UI, configuration, or existing artifacts. Do not claim human-risk control or a security proof. Run the existing test suite, Ruff, and mypy. Commit the work and report the commit hash, test outputs, benchmark output, changed-file list, assumptions, and any failed novelty gates.

## 12. Required DSH deliverables

DSH must return:

1. a single reviewable Git commit;
2. the commit hash and `git diff --stat 195355a..HEAD`;
3. complete pytest, Ruff, and mypy outputs;
4. benchmark JSON or console output for the three routing policies/baselines;
5. examples of each certificate-rejection family;
6. matched-budget comparison if the optional risk policy is attempted;
7. a written statement of which novelty gates N1--N5 pass or fail;
8. all assumptions and any required integration changes, without implementing those integration changes.

## 13. Review decision after DSH handoff

Codex will classify the prototype into one of four outcomes:

- **B only:** executable contract is useful, but the certificate does not create a distinct enforced mechanism;
- **B + C certificate:** evidence-bound transition is defensible, but routing remains a simple engineering policy;
- **B + C method:** certificate and matched-budget authority-aware routing both demonstrate distinct value;
- **Reject prototype:** complexity grows without producing a testable novelty advantage.

Only after this classification should the user decide whether to integrate the prototype, rerun formal experiments, or revise the manuscript.

## 14. Intended manuscript language if successful

If only Track B passes:

> We formulate candidate--fact separation as an executable authority contract linking four application properties to enforcement mechanisms, negative tests, and reproducible outcomes.

If the certificate also passes N1 and N2:

> We introduce an evidence-bound authority transition in which an attributable human decision is necessary but not sufficient for fact creation: the reviewed candidate must also carry a valid, current, and provenance-complete certificate.

If risk-budgeted routing passes N3 on held-out data:

> We further evaluate authority-aware routing, which allocates review and reacquisition using predictive uncertainty together with evidence integrity, provenance completeness, and state freshness, and improves fault containment at a matched intervention budget.

The paper must not use the stronger sentence unless the corresponding gate passes.
