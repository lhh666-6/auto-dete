# AI-assisted review proposals for the 39 acknowledgment disagreements

This is a post-hoc, unblinded Codex review of the existing 39 human–rule disagreements, not a new independent human annotation or completed author adjudication. All original human labels, rule labels, counts and agreement statistics are unchanged.

- `复核报告.md`: interpretation, limitations, and all 39 proposed decisions with exact quotations.
- `逐条复核-可阅读版.html`: readable review with expandable full responses and original human rationales.
- `逐条复核-39条.csv`: complete machine-readable record, retaining source identifiers and original labels.
- `author-decision-template.csv`: the same proposals with blank author decision, reason, name and date fields. Blank means pending; it is not agreement with the AI.
- `verification.json`: input hashes and checks of coverage, quotation provenance, and original-input preservation.
- `build_review.py`: deterministic serialization and integrity checks of the explicitly recorded AI proposals. It does not perform independent semantic inference or establish their correctness.

Proposals: 5 rule errors, 33 human-label errors, and 1 ambiguous response. These classifications use a textual-comparison interpretation: an explicit mismatch with one named field is not cancelled by a match with another. All 32 A3 cases retain the caveat that the task did not uniquely specify a target. A narrower target-only interpretation remains unresolved and must not be silently presented as the original rubric. A225 is conservatively proposed as 0 owing to ambiguous comparison versus a global denial of mismatch.

Only disagreements were reviewed: the other 286 outputs were not audited here. These counts are not population error rates, adjudicated truth, or improved inter-rater agreement. The original 286/325 agreement and kappa remain unchanged. Authors may accept or reject each proposal after reading the full response. Keep original labels and any later decisions in separate columns.

To re-serialize the frozen proposals and verify exact quotations, run `python -B build_review.py` in a working copy of this directory. This rewrites generated review outputs; do not run it in a sealed release. It requires only the Python standard library and the sibling frozen annotation directory. The author decision template is intentionally not overwritten by that script.
