# Correction-Aware Data Admission

**Candidate-Bound Authorization and Field-Level Provenance for AI-Derived Updates**

This repository contains the current Journal of Intelligent Information Systems
(JIIS) submission manuscript, its fixed experimental evidence, and earlier
DKE/JSS research versions. The October 2 contribution-focused revision and
pagination fixes are in the [current JIIS submission package](revisions/2026-10-02-jiis-final-contribution-layout/).

## Start here

| I want to… | Open this |
|---|---|
| Read the current paper | [Main manuscript — 24 pages](revisions/2026-10-02-jiis-final-contribution-layout/submission-files/Manuscript.pdf) |
| Read the full definitions and experimental details | [Online Resource 1 — 14 pages](revisions/2026-10-02-jiis-final-contribution-layout/submission-files/ESM_1.pdf) |
| Reproduce the results | **[Reviewer guide](REVIEWER_GUIDE.md)** |
| Obtain editable manuscript sources or submission files | [JIIS submission package](revisions/2026-10-02-jiis-final-contribution-layout/README.md) |

The reviewer guide provides one route: verify the deposited results, run the
core checks, then reproduce E1. Browser and performance experiments are separate
optional steps. It prepares the fixed source versions automatically, writes
fresh outputs to a separate workspace, and needs no model API credentials.
The first steps do not download the archived database collection.

## Versions used by the current paper

| Component | Fixed version |
|---|---|
| Manuscript and submission package | [October 2 JIIS contribution and layout revision](revisions/2026-10-02-jiis-final-contribution-layout/) |
| E1–E3 scripts and original results | [`2645e5e`](https://github.com/lhh666-6/auto-dete/tree/2645e5e18c900ea91c9c980e44195dc71e410432/DKE-supplement) |
| Reference implementation and historical input records | [`c6d5128`](https://github.com/lhh666-6/auto-dete/tree/c6d512843c905cab6d8521dd8c914f7fb26d85ae/latest/code/implementation-fixed) |

The reproduction entry point uses these exact commits. Later documentation
changes do not change the deposited experiments. The manuscript folder's
manifest identifies its files; its submission guide explains the packaged
sources and build process.

## Earlier versions and author revision records

These are retained for provenance; begin with the reviewer guide above for the
deposited experimental evidence used by the JIIS paper.

- [JIIS preparation package, October 2](revisions/2026-10-02-jiis-preparation/): original author-supplied source, retained unchanged.
- [DKE manuscript, September 26](revisions/2026-09-26-dke-manuscript/).
- [Frozen JSS version, September 13](https://github.com/lhh666-6/auto-dete/tree/r31-jss-2026-09-13),
  with its [original reviewer guide](https://github.com/lhh666-6/auto-dete/blob/r31-jss-2026-09-13/REVIEWER_GUIDE.md).
  The root `latest/` directory belongs to that research line, not the current JIIS manuscript.
- [Earlier DKE draft, September 24](revisions/2026-09-24-dke-draft/).
- [Author revision notes](revisions/2026-09-26-dke-manuscript/修改说明.md) and
  [editorial checks](revisions/2026-09-26-dke-manuscript/editorial/).
- `r21-jss/` holds historical source and hosted-run records; `r27-jss/` holds an
  earlier handoff. `paper/`, `artifacts/`, `source_snapshot_68f7b93/`,
  `REVIEWER_README.md` and `SOURCE_PROVENANCE.md` contain earlier ESWA-era material.

Public availability does not imply an OSI open-source license for all contents.
Third-party notices remain with the bundled tools; consult the authors for
reuse beyond evaluation. Repository files do not state journal acceptance.
