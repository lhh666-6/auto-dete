# E1 identity-isolation control

SAFE = review A, admit A. UNSAFE = review A, admit the equal-valued B.

| policy | evidence variant | clock | SAFE | UNSAFE | indistinguishable under declared projection | review-origin diagnostic | records exact candidate relation |
|---|---|---|---|---|---|---|---|
| transactional_value_audit | a | deterministic | accept | accept `committed` | True | AMBIGUOUS | False |
| transactional_value_audit | a | wallclock | accept | accept `committed` | True | AMBIGUOUS | False |
| transactional_value_audit | b | deterministic | accept | accept `committed` | True | AMBIGUOUS | False |
| transactional_value_audit | b | wallclock | accept | accept `committed` | True | AMBIGUOUS | False |
| B2 | a | deterministic | accept | accept `committed` | True | AMBIGUOUS | False |
| B2 | a | wallclock | accept | accept `committed` | True | AMBIGUOUS | False |
| B2 | b | deterministic | accept | reject `reviewed_context` | False | AMBIGUOUS | False |
| B2 | b | wallclock | accept | reject `reviewed_context` | False | AMBIGUOUS | False |
| B2plus | a | deterministic | accept | accept `committed` | False | AMBIGUOUS | False |
| B2plus | a | wallclock | accept | accept `committed` | False | AMBIGUOUS | False |
| B2plus | b | deterministic | accept | reject `reviewed_context` | False | AMBIGUOUS | False |
| B2plus | b | wallclock | accept | reject `reviewed_context` | False | AMBIGUOUS | False |
| candidate_bound | a | deterministic | accept | reject `candidate_binding` | False | EXPLICITLY_BOUND | True |
| candidate_bound | a | wallclock | accept | reject `candidate_binding` | False | EXPLICITLY_BOUND | True |
| candidate_bound | b | deterministic | accept | reject `candidate_binding` | False | EXPLICITLY_BOUND | True |
| candidate_bound | b | wallclock | accept | reject `candidate_binding` | False | EXPLICITLY_BOUND | True |
