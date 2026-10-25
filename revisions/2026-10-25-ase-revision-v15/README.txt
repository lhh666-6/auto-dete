ASE local revision v15 - 25 October 2026

The Review-Execution Gap in Agentic Software: Approval Scope and Recovery

This is the current local manuscript/source revision. No v15 remote tag or publication
is asserted. Historical v13/v14 sources, frozen hashes and experimental archives remain
unchanged. See V15-CHANGELOG.md for scope and audit/ for current validation reports.

Validated PDFs: manuscript 29 pages, Online Resource 1 32 pages, Online Resource 2
26 pages. The single-entry manuscript source and complete three-document sources
were extracted into clean directories and rebuilt: every page's text and 72-dpi
rendering matched the supplied PDFs. The extracted checker tests passed all 38
new regressions. See audit/packaged-source-validation-v15.json for input identities.

Build all PDFs using Python 3 and pdfLaTeX/BibTeX: python build.py
Build only the manuscript: python build.py --main-only
Auxiliary files go under out/. Supplied figure PDFs, class, style and bibliography
suffice to compile; figure regeneration is optional (requirements-figures.txt).

The v15 auxiliary observation checker uses canonical JSON equality consistently with
its admissibility predicate. Corrected checker, regression tests and upstream fixture
are under qa/; current audit explanations/results are under audit/. This correction
does not alter historical study archives, observations, definitions or statistics.

Run the portable check without modifying its issued receipt:
    python -B qa/test_observation_equality_v15.py --output temporary-result.json
The bundled upstream fixture is hash-checked; no Git checkout or model API is needed.

Scientific readback: REPRODUCE-RECOVERY.md describes two immutable raw archives and
exact INPUT_ROOT placement. The five qa analysis scripts use Python's standard library;
use --output to preserve supplied tables. SDK recollection is separate from saved-record
readback and requires separately pinned environments.

Maintainer packaging from this directory requires the repository layout and v14
ESM_3.zip. An extracted source package can build PDFs and run the checker
independently; it does not need the maintainer packaging tool.

Packaging commands:
    python scripts/package_v15.py --check
After all three current PDFs and scientific QA pass:
    python scripts/package_v15.py --package --validated
Verify without rewriting:
    python scripts/package_v15.py --verify
Page counts are read with pdfinfo or pypdf. SOURCE-MANIFEST.json inventories sources;
upload-package/FILES.json records five scientific payloads, mirrored to
../../submission/ASE-2026-10-25-v15/ready-to-upload/. FINAL-FREEZE-v15.json inventories
the revision, excluding itself. The tool does not commit, push, publish or submit.

Upload roles:
  Manuscript.pdf         main manuscript
  Manuscript-source.zip  one main.tex at archive root and main-document dependencies
  ESM_1.pdf              Online Resource 1
  ESM_2.pdf              Online Resource 2
  ESM_3.zip              full three-document sources and seven original study ZIPs

Inside ESM_3.zip, extract Manuscript-sources.zip for full sources, figures, scripts,
checker/tests and current audit reports. Seven study archives are read directly from
v14 ESM_3.zip and checked byte-for-byte. For SDK studies read START-HERE.md and run
verify_offline.py; historical freezes and mismatches are retained. EXTERNAL-INPUTS.json
preserves original external-evidence references and hashes. Source packages omit
build output, inherited audits, Git metadata and correspondence.

Five scientific payloads do not include author correspondence. Historical v14 files
contain a separately tracked cover letter; its identity, date and withdrawal wording
are not evidence about current portal state. No old cover letter is copied. Local
preparation does not submit a manuscript or confirm a prior withdrawal.
