# R20 limitation-centralization design

## Objective

Increase authorial confidence without expanding any claim. The current R19 manuscript repeats
negative boundary clauses across the abstract, introduction, methods, results, appendix, and
conclusion. R20 will preserve the evidence semantics while moving the full limitation inventory to
Section 9.

## Approved editorial rule

The user's instruction supplies the approved design: each experimental block keeps at most one
interpretive boundary that is necessary to read that result correctly; Section 9 becomes the single
detailed limitation register.

## Changes

1. Preserve R19 unchanged and create an isolated R20 paper candidate.
2. Abstract: replace the multi-item negative list with one positive scope sentence.
3. Introduction: keep one finite-evidence scope sentence and point to Section 9; remove the repeated
   catalogue of things not established.
4. Methods/evaluation: retain operational exclusions only when they define the actual trust boundary
   or denominator. Move general caveats to Section 9.
5. Results: lead with findings. Each RQ may keep one short statement of permitted inference, but not
   a repeated multi-item disclaimer.
6. Appendix: report artifact identity and verification behavior; move interpretive disclaimers to
   Section 9 except where needed to distinguish baseline/additional inputs.
7. Conclusion: use one compact scope sentence and one forward-looking sentence.
8. Section 9: organize the complete limitations once under formal scope, construct validity,
   external validity, trust/security, AI-origin/harness validity, performance/portability, artifact
   validity, and novelty-search scope.

## Invariants

- No numerical result, citation, evidence path, denominator, or claim-ledger mapping changes.
- No limitation disappears; every removed disclaimer is represented in Section 9.
- Trust-boundary facts that define the mechanism remain in the method section.
- “Bounded” remains where it is a technical term (e.g., bounded relational analysis), not as a
  recurring rhetorical hedge.

## Verification

- Compare pre/post inventories of limitation concepts.
- Compile with the verified MiKTeX fallback.
- Require zero undefined references/citations and zero overfull boxes.
- Run a focused proofread for defensive repetition, negative-sentence density, and Section 9
  completeness.
