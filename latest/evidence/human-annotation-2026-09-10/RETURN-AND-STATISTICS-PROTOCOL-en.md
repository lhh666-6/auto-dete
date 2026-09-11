# Return and Statistics Convention (Task Completion, B1--B4)

> English translation of `RETURN-AND-STATISTICS-PROTOCOL-zh.md` (SHA-256
> `bfaa5001ba1cd81017d117fcf5ccfeb5a9be7216600cfb40e322463cd9517568`), the
> convention issued with the blind package on 2026-09-09, before any label was
> recorded. The Chinese file is the authoritative text.

1. After completing the exercises in guide 01, fill columns D/E/F/G row by row on
   the 正式标注 sheet of workbook 02; save and return it.
2. On receipt the organiser: first saves the original submission and its SHA-256,
   then checks row IDs, coverage (360/360), missing values, and illegal values.
3. Statistics are computed in two steps and must never be conflated:
   - **Pre-adjudication**: on the 335 runs the original rule judged
     behaviour-evaluable, build a 2x2 table (human 1/0 x strict rule 1/0) and
     report percent agreement, Cohen's kappa with a 95% CI, class frequencies,
     and the confusion matrix; report the 25 runs the original rule could not
     score separately (whether the human could score them, and the result).
   - **Post-adjudication**: disagreements are adjudicated by a non-author third
     party (or by consensus) and saved in a separate table; the two original
     columns must not be overwritten. Report pre- and post-adjudication
     separately.
4. Compare with the existing 320/360 (strict) and 331/360 (post-hoc endpoint):
   - if the human completion count is near 320/335, that supports the strict
     criterion;
   - if it is closer to 331/335, the strict criterion is too severe;
   - if it is markedly below both, the rule criterion overestimates.
   All three outcomes must be reported honestly; it is not acceptable to report
   only the "agreement" conclusion.
5. State the distinction explicitly: this is **human--rule agreement, not
   two-human inter-rater agreement**; a single human label does not by itself
   establish measurement validity.
6. If the main-text counts change as a result, synchronise the main text,
   behavioural result tables, related figures, derived files, and the manifest by
   LaTeX label, then recompile, verify, and publish a new immutable version.
