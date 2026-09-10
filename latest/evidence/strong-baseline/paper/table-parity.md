# Existing control vs strengthened control (section 43)

## Existing control: B0 `approval_log` vs Full

- agreement: 7 of 8 single-history cases
- divergence: equal-value-substitution, paired-reviewed-candidate

## Strengthened control: B1 `transactional_value_audit` vs Full

- agreement: 7 of 8 single-history cases
- divergence: equal-value-substitution, paired-reviewed-candidate
- in-process Full reproduces the frozen reference on 9 of 9 cases

## Optional robustness controls

- B2 divergence: equal-value-substitution
- B2plus divergence: equal-value-substitution

## Per-case outcomes

| case | reference (Full) | B0/B1 class | B1 | B2 | B2plus | Full |
|---|---|---|---|---|---|---|
| legal-correction | accept `committed` | | accept `committed` | accept `committed` | accept `committed` | accept `committed` |
| equal-value-substitution | reject `candidate_binding` | | accept `committed` | accept `committed` | accept `committed` | reject `candidate_binding` |
| cross-record-candidate | reject `candidate_context` | | reject `candidate_context` | reject `candidate_context` | reject `candidate_context` | reject `candidate_context` |
| stale-version | reject `stale_version` | | reject `stale_version` | reject `stale_version` | reject `stale_version` | reject `stale_version` |
| wrong-value | reject `approved_values` | | reject `approved_values` | reject `approved_values` | reject `approved_values` | reject `approved_values` |
| partial-batch | reject `approved_values` | | reject `approved_values` | reject `approved_values` | reject `approved_values` | reject `approved_values` |
| injected-failure | reject `injected_failure` | | reject `injected_failure` | reject `injected_failure` | reject `injected_failure` | reject `injected_failure` |
| two-step-copy-forward | accept `committed` | | accept `committed` | accept `committed` | accept `committed` | accept `committed` |
| paired-reviewed-candidate | states_equal=False | | states_equal=True | states_equal=False | states_equal=False | states_equal=False |
