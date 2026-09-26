# Evaluation rewrite and numerical audit

Files owned in this revision: sections/07-evaluation-protocol.tex, sections/08-results.tex, and tables/dke/{comparator,review,admission,trace,storage}.tex. Original data, experimental scripts, and historical manuscript files were not edited. No new experiment or model request was performed.

## Sources and checks

- Read DKE-supplement/REPORT.md, PROTOCOL.md, and MANUSCRIPT_INSERT.md, plus the original sections 07/08.
- Checked E1 raw summary.json: all 165 exact-journal/reference paired acceptance decisions and query-answer sets agree.
- Checked E2 CSV: thirty cases/path; original accepts 21 and rejects 9, session gate accepts 12 and rejects 18; all rejected cases have zero writes. Case-family totals form the manuscript table.
- Programmatically matched every displayed row in the ten-cell admission table against both source CSV files at two decimal places.
- Programmatically matched all three displayed trace rows against the source CSV, including SQL counts.
- Summed n over both admission CSVs and trace CSV: 22,400 timed observations.
- Storage uses original exact bytes, MiB = bytes / 1,048,576, and full-minus-reduced bytes divided by transition count.
- Combined section source length is approximately 2,700 whitespace-delimited words before table captions. Parent performs whole-manuscript compilation and visual QA.

## Interpretation preserved

E1 has fifteen inputs but only seven distinct proposed values. Archived values are inputs to newly constructed histories, not end-to-end workflow replay. The comparator is independently written for the same study, not third-party or external-team evidence. Value/context policy remains richer than bare value equality. Exact mechanisms reject fifteen cases permitted by that weaker policy, as well as removing its fifteen instance-policy violations. Query counts are eighteen field-level answers per accepted case. Rejection starts after authorization preparation.

E2 consists of sixty cases plus six initial confirmations for replay setup. The original path trusts the caller when constructing the binding; its nine request substitutions expose that premise rather than contradict its transaction contract. Both paths accept three DOM-only substitutions. The extension uses simulated principals and a separate session database, without display attestation or cross-database crash-atomicity claims.

E3 source is the equality-repaired implementation. Current measurements replace old v8 cost claims in the main text. The complete-mechanism comparison includes schema/ORM/validation differences and eager versus lazy connection establishment. The independent manual-source ablation is not cross-subtracted from recognition-source timings. Trace uses the same current verifier and changes repository access only. Storage is synthetic direct population with external evidence bytes excluded.

## Structural changes for integration

Three RQs replace the original eight. Historical formal/concrete results are retained explicitly as retained evidence rather than all newly rerun. Historical hosted-agent outcomes are compressed and separate task completion from fixed host challenges. Supplemental locations S4 (full costs) and S5 (historical integration) match the new parent-authored supplement.

Retained labels: sec:evaluation, sec:results, sec:executable-relation-result, tab:storage-cost. New labels: tab:dke-comparator, tab:dke-review, tab:dke-admission, tab:dke-trace, sec:historical-integration. Old generated evaluation tables and historical cost/behavior/evidence-map figures are not included in these sections. Parent should update any leftover references to their removed labels.
