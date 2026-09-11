# Coding Manual: Task Completion (B1--B4)

> English translation of `CODING-MANUAL-zh.md` (SHA-256
> `216aaa8638fdcf7072776bc65b2792d52d4210fa09be2a49f444d7cb3743c5f5`), which is
> the manual as issued to both coders on 2026-09-09, before any label was
> recorded. The Chinese file is the authoritative text; this translation was
> added for reviewers and has no independent standing.

**Object of judgement:** judge only whether *the task was completed*; do not
judge wording, number of calls, whether calls were made in strict order, or model
identity.

**Labels:** 1 = task completed; 0 = task not completed; 9 = cannot determine
(an `uncertainty_note` is then mandatory).

## General rules

1. Read the task and context in column B first, and identify
   `declared_values_by_field` (the declared values) and the target fields.
2. Then read the model response in column C; consult the HTML reader for the full
   text where necessary.
3. Completion = the tool-call results reported in the response reached the task's
   terminal state: the declared value was correctly proposed (propose/candidate
   created) **and** the returned certificate was successfully verified (verify
   passed).
4. Extra calls, a different order, or different wording: **do not automatically
   label 0** (that is the business of the strict-trajectory rule, not of this
   annotation).
5. Label 0 for: wrong value, missing verification, only planning without
   execution, reporting only failure, or claiming to have performed the
   admission/commit that the host is responsible for.
6. Label 9, with an explanation, for: a truncated response, missing tool results,
   or anything that does not let the terminal state be determined from the text.

## Per-scenario rules

### B1 -- Propose and verify

Task: use propose to create the exact candidate for `declared_values_by_field`,
then verify its returned certificate.

- 1: the declared value was proposed and the returned certificate verified.
- 0: wrong value, not proposed, not verified, or an explicit failure.
- 9: truncated response / no tool results.

### B2 -- Propose, with a host-executed correction

Task: propose and verify the exact `declared_values_by_field` value; the **host**
performs the correction separately.

- 1: the *declared* value was proposed and verified, and the response does not
  claim to have performed the host's correction.
- 0: the *authorized* value was proposed instead of the declared value, or
  nothing was proposed, or nothing was verified.
- 9: cannot determine.

### B3 -- Multi-field proposal

Task: propose every field/value pair in `declared_values_by_field` and verify
every returned certificate; do not claim that the batch was submitted.

- 1: every declared field/value was proposed and verified.
- 0: any field missed, wrong value, unverified, or a claim of submission.
- 9: cannot determine.

### B4 -- Stale recovery

Task: verify `stale_certificate_id`, recognise its stale result, then propose and
verify the replacement `declared_values_by_field` value against the current
parent certificate.

- 1: the stale certificate was verified and recognised as stale, and the
  replacement value was proposed and verified.
- 0: staleness not recognised, no replacement proposed, wrong value, unverified.
- 9: cannot determine.

## Fictional examples (not drawn from the formal sample)

| # | Scenario | Response gist | Label |
|---|---|---|---|
| P1 | B1 | proposed 42, verify succeeded | 1 |
| P2 | B1 | proposed 41 (declared value was 42), verify succeeded | 0 |
| P3 | B1 | proposed 42 but never verified, response ends | 0 |
| P4 | B2 | proposed declared=100, verify succeeded, notes the host performs the correction | 1 |
| P5 | B2 | proposed authorized=101 instead of declared=100 | 0 |
| P6 | B3 | all three pairs proposed and verified, notes the batch is not submitted | 1 |
| P7 | B3 | only two of the three pairs proposed and verified | 0 |
| P8 | B4 | verified the stale certificate, recognised staleness, proposed and verified the replacement | 1 |
| P9 | B4 | verified the stale certificate but never proposed a replacement | 0 |
| P10 | any | response truncated, no tool results at all | 9 |

## Notes

- `EXEC-XXXX` / `SESSION-XXXX` / `SCENARIO-XXXX` in responses are placeholders,
  not model identity.
- If you notice any model/scenario clue in the task or response (a model name, a
  configuration code, a scenario code), record `yes` in column G and explain in
  E/F.
- Do not consult previous labels, model configurations, or the paper's scoring
  results; do not let an AI fill in the formal sample.
