# Superseded material in this directory

This directory mixes current method documents with earlier per-unit analysis
reports. Read this before using the latter.

## Current method

| Question | Read |
|---|---|
| How the labels were produced, and what was issued to the coders | `PROVENANCE.md`, `CODING-MANUAL-zh.md`, `CODING-MANUAL-en.md` |
| How to recompute the coefficients and intervals | `README-REPRODUCE.md`, `recompute_irr.py` |
| The coefficients as reported in the paper | `recomputed-irr.json` |
| The package as issued (blinding transformation, freeze) | `BLIND-PACKAGE-MANIFEST.json` |

## Superseded

`2026-09-10-case/`, `2026-09-10-model/`, and `2026-09-10-cell/` are the earlier
per-unit reports, retained unchanged. Two points in them no longer describe the
published analysis:

1. **Adjudication expectation.** Their section 6 states that disagreements
   *should* be adjudicated by a non-author third party or by consensus. That was
   the convention issued with the blind package, and it was **not** obtained: one
   coder is the second author and the adjudicator was the first author. The
   deviation, and what the published text now says about it, are recorded in
   `PROVENANCE.md` and in Supplement S2.8. The per-unit reports are not corrected,
   because they are the record of what was run at the time.

2. **Wording strength.** Where those reports describe cluster resampling, the
   published text is weaker on purpose: the case-, model-, and cell-level
   intervals are *clustering-sensitivity summaries*, not population-calibrated
   intervals from a large sample of models. Note also that each of the 360 benign
   runs has its own `case_id`, so case-level resampling resamples the same units
   as an ordinary row bootstrap; only the model (three) and cell (twelve) levels
   change the resampling unit.

## Unchanged

The label columns, the pre-adjudication disagreements in `disagreements-*.csv`,
and the adjudication files are inputs to the published analysis and are not
rewritten by this notice.
