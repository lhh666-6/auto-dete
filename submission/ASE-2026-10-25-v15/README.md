# ASE v15 local scientific upload layout

Current source revision: [v15](../../revisions/2026-10-25-ase-revision-v15/README.txt), dated 25 October 2026. These files are prepared locally; this directory does not establish journal submission, prior withdrawal or a published v15 release.

| File under ready-to-upload/ | Upload role |
|---|---|
| Manuscript.pdf | Main manuscript |
| Manuscript-source.zip | Editable main manuscript; one main.tex at archive root |
| ESM_1.pdf | Online Resource 1 |
| ESM_2.pdf | Online Resource 2 |
| ESM_3.zip | Online Resource 3: complete three-document sources and seven unchanged study archives |

The [packaging tool](../../revisions/2026-10-25-ase-revision-v15/scripts/package_v15.py) generates these five payloads after current PDF/scientific validation is acknowledged. Generated `FILES.json` records actual page counts, sizes and SHA-256 hashes. It mirrors the revision's `upload-package/` payloads here and verifies CRCs, dependency completeness, source manifests and byte-identical inheritance of seven study ZIPs from v14. Build outputs and old audits are excluded from source archives.

Upload the files using corresponding manuscript/source/supplementary portal roles. The full `Manuscript-sources.zip` is nested in `ESM_3.zip`; it contains all three document sources, current v15 checker/tests and audits. The separate singular `Manuscript-source.zip` is the manuscript-only source upload.

Author correspondence is a separate role outside the five scientific payloads and their manifest. Historical v14 directories contain a tracked cover letter beyond that scientific manifest; v15 does not copy it, its earlier submission identity or withdrawal wording. Any new letter must follow current author instructions and actual portal state. Preparing this directory neither submits a manuscript nor confirms any prior withdrawal.
