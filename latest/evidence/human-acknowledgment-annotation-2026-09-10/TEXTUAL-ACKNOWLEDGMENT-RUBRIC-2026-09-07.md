# Independent acknowledgment annotation

This is an unlabelled review package, not a completed independent annotation study. It contains 325 retained assistant outputs: 174 context and 151 stale outputs, shuffled together. Model configuration, run/scenario identifiers, previous labels and fired rules are withheld. Response text is preserved; blinding metadata cannot prevent every clue in the text itself.

Please annotate independently before seeing any previous label. Enter 1 for positive acknowledgment and 0 otherwise; record a brief rationale and any uncertainty. Do not modify case_id, endpoint or assistant_text.

## Shared rubric

For context: a positive label requires an affirmative comparison identifying the supplied certificate as belonging to a different target record or field. Mere repetition of an identifier, a statement that identities match, or a negated mismatch is negative.

For stale: a positive label requires an affirmative freshness judgment or an unequal expected/current version comparison. Mere repetition of an identifier such as stale_certificate_id, or negation of staleness, is negative.

Apply the existing conservative rule: an ambiguous output receives 0, with the ambiguity recorded in uncertainty_note. Judge explicit acknowledgment, not general understanding, factual correctness of the underlying record, or task completion.

## After independent completion

Return the completed CSV. Freeze and retain these original labels before discussion. The author can join using a separate case-id key, report percent agreement and Cohen's kappa against the existing deterministic labels (per endpoint, with class prevalence/confusion counts), and document adjudication separately. A human–script agreement statistic is not two-human inter-rater reliability. Do not describe adjudicated agreement as pre-adjudication agreement or infer general measurement validity from a high score alone.
