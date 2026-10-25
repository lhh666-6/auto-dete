ASE manuscript revision v17 - 25 October 2026

Derived from local v16, based on GitHub v15 commit
ae686c95f5e7a04e3ea16880239e0a6b85b3de14.

Main-text edits connect the comparison model, execution validation and recovery
observations. The abstract's closing sentence is aligned with that account.
Methods, results, mathematical definitions, citations, figures, data, QA programs
and both Online Resources retain their v16 content.
The current source availability pointer is version-neutral. No new experiment.

Build using Python 3 and pdfLaTeX/BibTeX: python build.py
Build main only: python build.py --main-only
Build auxiliaries go under out/; supplied figures suffice for compilation.

The unchanged v15 checker can be replayed without overwriting its issued receipt:
    python -B qa/test_observation_equality_v15.py --output temporary-result.json
Scientific readback and external inputs: REPRODUCE-RECOVERY.md and
EXTERNAL-INPUTS.json. Use separate --output directories for derived results.

Current wording and preservation checks are in audit/framing-v17.json;
audit/packaged-source-validation-v17.json records clean-extraction build checks.
The issued observation-equality-v15.* receipts refer to the inherited checker.
SOURCE-MANIFEST.json inventories the full sources and FINAL-FREEZE-v17.json
pins this local delivery. upload-package/ contains five synchronized payloads:
Manuscript.pdf, Manuscript-source.zip, ESM_1.pdf, ESM_2.pdf and ESM_3.zip.
The singular source ZIP builds the main manuscript; ESM_3.zip contains complete
three-document sources and seven unchanged study archives. Read START-HERE.md
inside each SDK study archive before choosing offline readback or recollection.

The publication payloads are mirrored to submission/ASE-2026-10-25-v17/ready-to-upload
in the parent repository. No GitHub push, tag, journal submission or author
correspondence is performed by local preparation.
