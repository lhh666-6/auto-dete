# v15 local revision — 25 October 2026

This revision follows the [25 October v14 review](../../reviews/2026-10-25-ase-v14-multiagent/summary.md). It is a local manuscript/source revision, not a pushed release, published tag or journal submission. Historical v13/v14 sources, manifests and archives are preserved.

The revision addresses the observation checker's canonical JSON equality mismatch with a separate corrected checker and regression tests under `qa/`; current `audit/` records the scope and executed results. The correction concerns the auxiliary projection used in the executable observation claim. It does not establish that the production gate admitted a wrong value or invalidate the typed mathematical proposition. Historical experimental archives remain intact.

The manuscript work addresses the AI preparation disclosure and distinguishes prior recovery evidence from this paper's scope, route-choice observations and cost accounting. Source changes and validation results are inspectable in this revision and its current audits. No new hosted/model observations are introduced, and experimental statistics retain their original scope.

Root navigation identifies v15 as the current local manuscript and distinguishes it from the unchanged v13/v14 experimental freeze. Submission guidance distinguishes five scientific payloads from author correspondence and does not interpret historical cover-letter withdrawal wording as a current portal fact. No old cover letter is automatically copied.

`scripts/package_v15.py` provides read-only preflight, deliberate post-validation packaging and verification. It generates source/payload inventories and `FINAL-FREEZE-v15.json`; reads page counts from actual current PDFs; verifies ZIP CRCs, hashes, local source dependencies and inherited study ZIP identities; and records exact results at runtime. The freeze does not hash itself. Final hashes, page counts and completion evidence belong in generated manifests and audit reports, rather than provisional values in this change log.

The package comprises `Manuscript.pdf`, `Manuscript-source.zip`, `ESM_1.pdf`, `ESM_2.pdf` and `ESM_3.zip`. The singular source ZIP contains one root `main.tex` and its dependencies. Online Resource 3 contains complete three-document sources, current QA/checker tests and audit explanation, plus seven byte-identical study ZIP members from v14 Online Resource 3. Build output, inherited audits, Git metadata and private correspondence are excluded from source packages.

No commit, push or remote tag is created by this workflow. Regenerate the package whenever included sources or PDFs change; `--verify` detects stale payloads.

## Completed validation

- Main manuscript: 29 pages. Online Resources 1 and 2: 32 and 26 pages.
- The repaired checker passes 38 new offline equality regressions, while retaining the five omission pairs, the instance-identity pair and the copy-forward control. New regression counts remain separate from historical experimental totals.
- Independent review confirmed that all 35 inherited table/figure files, including supplement assets, are byte-identical to v14. The seven study archives are likewise inherited byte-for-byte.
- Clean-extracted single-entry and full-source packages rebuild successfully. All pages have identical extracted text and 72-dpi renderings to the corresponding issued PDFs; the extracted regression harness also passes without a Git dependency. The required `sn-basic.bst` is explicitly shipped because the class selects it implicitly.
- Final logs have no undefined references/citations, unresolved labels or overfull boxes. Underfull spacing warnings remain recorded and the reviewed changed pages are visually readable; no blanket zero-warning claim is made.
- The exact PDF and compilation-input identities are in the current audit JSON files. Historical v14 files and experimental archives remain unchanged.
