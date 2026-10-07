# DKE supplementary experiment protocol

Protocol drafted before new outcome collection on 2026-09-23. This is a local,
prospective execution plan, not an externally registered study.

## Source and scope

- Reference source: https://github.com/lhh666-6/auto-dete,
  tag `r31-jss-2026-09-13`, commit `c6d512843c905cab6d8521dd8c914f7fb26d85ae`.
- Use `latest/code/implementation-fixed` without changing the sealed source.
- No hosted-model requests, API keys, human subjects, or externally sent messages.
- Replayed archived model output and explicitly synthetic extensions are inputs,
  not new model runs or evidence of real-world fault prevalence.
- New event-journal comparator is independently written in sqlite3 for this study;
  it is not an independently developed commercial system or field deployment.

## E1: provenance and admission comparison

Compare a versioned immutable event journal with rich review context, the same
journal with exact reviewed-candidate binding, and the actual reference service's
transactional admission implementation. Keep candidates, authorization values,
field set, freshness, and source-copy policy equal. Where available, add the
paper's existing strengthened baseline as a continuity check.

Cases include legal Accept, Correction, multiple-field updates and unchanged
sources; equal-valued candidate substitution, different-context substitution,
stale authorization, replay, invalid item, and injected transaction interruption.
Use full candidate identity as defined in the source, never invent two different
hashes for identical certificate content.

Score value-level and instance-level authorization policies separately. For
successful histories independently query proposal value, authorized value,
reviewer, reviewed candidate, and current field-source version. Distinguish wrong,
ambiguous, unavailable, and correct answers. Read the resulting database using a
separate query oracle, not the production trace's answer. Reject checks compare
logical database digests before/after the attempted admission.

Bound-baseline equivalence is a valid outcome. Deterministic constructed cases are
reported as cases, not independent population samples. Workflow variations and
archived inputs are explicitly identified in raw receipts.

## E2: displayed-review to confirmation

Exercise a local instrumented review interface backed by the actual reference
service, comparing unmodified confirmation with a new server-held review-session
binding. Independently record the DOM-displayed certificate and proposed value.
Inject candidate substitution after display, target substitution in the confirm
request, a concurrent state update, and replay. Include legitimate reselection,
Accept and Correction controls. Also check authorized-value and principal binding.

Measure displayed/authorized/committed identity agreement, false rejection,
unsafe acceptance, and zero-write rejection. Scripted interaction does not prove
human attention, authentication security, or resistance to a compromised host.
New session binding is a study extension, not a guarantee attributed to old code.

## E3: current-version costs

Rerun the original 10-cell admission and 36-cell trace grids against the current
equality-repaired implementation. Defaults: 5 warmups and 200 observations per
cell. Admission comparisons separate the historical prevalidated-materialization
ablation from complete end-to-end mechanisms. Interleave compared arms in a
seeded random order and keep durability settings explicit.

Compare current optimized tracing with the same current trace logic using an
uncached repository-access wrapper where possible; require full result equality.
Report SQL counts, p50/p95, failures, source code hashes, timing boundary, and
environment. Retain raw timings. Replay representative JSON equality cases and
measure storage at 1,000 / 10,000 / 100,000 transitions where feasible. Do not
interpret old-machine/new-machine timing ratios as causal speedups.

## Execution integrity

Pilot runs use separate output directories. Preserve failed runs and reasons.
Freeze final scripts/configuration before final collection. Retain versioned
changes to this protocol with the reason; never silently change labels to make
the implementation win. The final report separates new measurements, reproduced
checks, and remaining external-validity limitations.

## Execution amendments recorded before the E3 final run

- E1 pilot 1 exposed a harness-only input mismatch: ReviewForms requires the
  values and candidate-map key sets to agree. The adapter now projects values
  onto submitted candidate fields. Pilot 2 passed; both pilot directories are
  retained. E1 final uses 12 archived input cells plus 3 synthetic type controls.
- E2 includes a DOM-only substitution negative control. The pilot demonstrates
  that neither server path can attest a compromised display. The session gate
  is an experimental local wrapper with a separate session database and fixed
  trusted principal labels, not production authentication or a crash-atomic
  cross-database protocol. Final browser inputs are 100, 2.5 and true; 2.5 avoids
  JavaScript JSON serialization silently normalizing an integral float to int.
- E3 uses the 10-cell grid for both end-to-end mechanisms and materialization
  ablation. Mechanism equivalence refers to this shared tested contract and
  workload; the independently written journal does not implement every feature
  of the reference application's schema, certificate validation, or trace UI.
- The controlled trace ablation changes three bulk repository operations into
  ID enumeration and real point lookups, leaving the current verifier unchanged.
  It is not a reconstruction of the historical preoptimization implementation.
- Valid unrelated forms are seeded once and copied as SQLite snapshots before
  each trace cell. Selected-form field/history and total-record counts remain
  the original 36-cell grid; all setup is outside timing. Full trace objects are
  compared on every timed invocation after the timer stops.
- E3 pilots passed all four sections at reduced sizes. Final sections run
  sequentially, after E1/E2 and regression tests have finished. OS/background
  activity is not controlled; timing CIs describe this single-machine run only.
