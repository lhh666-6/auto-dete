# Unified r27 candidate (public, 2026-09-10 revision 2)

Read current/paper/main.pdf with current/paper/supplement.pdf.
The current revision includes repaired sources, formal dependencies, derived
analyses, versioned witness v5, the r27 positive trace-completeness assertion
and its mutation control under `current/evidence/r27-trace-mutation/`, the
annotation analysis under `current/evidence/human-annotation-2026-09-10/`
(one author coder and one non-author volunteer; author adjudication disclosed;
normalized per-run labels, a standard-library recomputation script, and the
unused third-party adjudication protocol and blank template), and the minimal
ordinary approval/audit-log baseline under
`current/evidence/r27-standard-practice-baseline/`.

`baseline-v8/` is the exact historical Git export already verified for r26,
retained byte for byte; it is not modified and its historical logs may contain
author-local paths.

`SOURCE-CROSSWALK.json` covers the current paper, implementation, formal
sources, tools and derived evidence by declared path correspondence. Files
without a same-path baseline counterpart are explicit; historical manifests
retain lineage.

Verify every delivered file with `python verify_release.py` after extraction;
this revision passes with 20,417 files. The packaged
`current/formal/alloy/batch/verify_batch_package.ps1 -RequireRawResults` gate
also passes against the delivered package. Local absolute paths in the current
package logs were normalized to `<PROJECT_ROOT>`.

No paid calls are needed for record inspection. Dependencies remain necessary
for actual code execution. The second author's email and a DOI remain pending.
