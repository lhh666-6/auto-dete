# Review-to-Execution Continuity for Corrected Agent State Changes

Research manuscript and replication artifacts for correction-aware authorization of state-changing agents. The current package contains a **12-page article**, **29-page supplement**, frozen inputs, archived trajectories, scoring code and figure sources.

中文入口：以下链接对应当前论文与复现材料。复算使用已保存的轨迹，无需模型账户；原始实验、补充采集和事后敏感性分析分别保留。

## Start here

| I want to… | Open this |
|---|---|
| Read the current paper | [Article PDF](revisions/2026-10-07-kais-followup/main.pdf) · [Supplement PDF](revisions/2026-10-07-kais-followup/supplement.pdf) |
| Reproduce the results from raw trajectories | **[Step-by-step offline reproduction](REPRODUCIBILITY.md)** |
| Find the source of a table, figure or claim | [Paper-to-artifact map](docs/reproduction/ARTIFACT-MAP.md) |
| Check what was actually rerun | [Fresh reproduction verification](docs/reproduction/REPRODUCTION-VERIFICATION-2026-10-07.md) |
| Obtain editable paper/figure sources | [Manuscript source ZIP](revisions/2026-10-07-kais-followup/KAIS-editable-sources.zip) · [Build instructions](revisions/2026-10-07-kais-followup/README.md) |
| Inspect data provenance and expected outcomes | [Results and archive index](PHASE2-RESULTS-LATEST.md) · [File checksums](docs/reproduction/ARTIFACT-MANIFEST.json) |
| Prepare the submission files | [Submission checklist](docs/submission/SUBMISSION-CHECKLIST.md) · [Cover-letter draft](docs/submission/COVER-LETTER.md) |
| Rerun earlier controlled mechanisms | [Supporting-evidence reviewer guide](REVIEWER_GUIDE.md) |

## Fixed reproducibility version

Use tag **`kais-reproducibility-2026-10-07`** for this documented release. The working manuscript continues on `codex/phase2-formal-512-handoff`. Keep the resolved commit with any reproduced outputs.

```text
git clone --branch kais-reproducibility-2026-10-07 --filter=blob:none --sparse https://github.com/lhh666-6/auto-dete.git auto-dete-review
cd auto-dete-review
git rev-parse HEAD
```

Continue with the sparse-checkout, archive extraction and isolated-environment commands in [REPRODUCIBILITY.md](REPRODUCIBILITY.md). The compact route downloads the original and complete supplementary ZIPs plus the analysis and manuscript directories; a full checkout also includes much larger historical dependencies. New outputs go into a separate working copy.

Python 3.11 and the [tested dependency set](docs/reproduction/requirements-offline-2026-10-07.txt) support the online-trajectory analyses. Download/install steps require network access; scoring and reanalysis use local evidence. TeX, browser workloads and Java/Alloy are separate optional workflows. Fresh provider calls would constitute a new collection and are not needed to reproduce these reported outputs.

## Evidence collections

| Collection | Size | Interpretation |
|---|---:|---|
| Original frozen collection | 128 tasks × 2 deployments × 2 policies = 512 planned arms | Original primary estimator; quota failures, other failures and unknowns remain. |
| Separately frozen supplementary A | 117 selected task pairs / 234 arms | Later collection selected by pre-response quota failure; separately labeled exploratory evidence. |
| Completed-A sensitivity (S13) | 256 routed pairs / 512 arms, assembled from the two sources | Explicitly post hoc; one source per pair, no additional independent tasks and no replacement of the original estimator. |

The complete supplementary archive finished on 7 October 2026. Earlier partial snapshots and pilot runs remain historical records. The [artifact map](docs/reproduction/ARTIFACT-MAP.md) distinguishes these collections from the formal checks, controlled mechanisms and historical correction-chain audit.

## Preservation and reuse

Frozen experiment directories and raw archives retain their original bytes and paths. [Artifact checksums](docs/reproduction/ARTIFACT-MANIFEST.json) identify the release inputs; verification receipts distinguish fresh execution from inspection of archived outputs. Figures and PDFs may differ in renderer metadata across environments; numeric results are compared semantically.

This repository contains an unpublished research manuscript and does not assert journal acceptance. No blanket open-source license is assigned to all materials; existing third-party notices remain applicable. Cite the manuscript title, authors, repository URL and resolved release commit when identifying this artifact version.

## Earlier versions and supporting deposits

The earlier reviewer commands remain useful for the controlled E1–E3 layer. Their historical manuscript names, dates and test counts refer to that layer, not the current article.

<details>
<summary>Archived JIIS entry and earlier research versions — labels below refer to the October 3 version</summary>

# Correction-Aware Data Admission

**Candidate-Bound Authorization and Field-Level Provenance for AI-Derived Updates**

This repository contains the current Journal of Intelligent Information Systems
(JIIS) submission manuscript, its fixed experimental evidence, and earlier
DKE/JSS research versions. **The current manuscript is the 24-page centered
JIIS version supplied by the authors on October 3, 2026**, with a 14-page Online
Resource. Its PDFs, source ZIPs, and editable files match the supplied package.
Use the [current submission package](revisions/2026-10-02-jiis-final-contribution-layout/)
and the reviewer route below; earlier revision folders are not additional setup steps.

## Start here

| I want to… | Open this |
|---|---|
| Read the current paper | [Main manuscript — 24 pages](revisions/2026-10-02-jiis-final-contribution-layout/submission-files/Manuscript.pdf) |
| Read the full definitions and experimental details | [Online Resource 1 — 14 pages](revisions/2026-10-02-jiis-final-contribution-layout/submission-files/ESM_1.pdf) |
| Reproduce the results | **[Reviewer guide](REVIEWER_GUIDE.md)** |
| Obtain editable manuscript sources or submission files | [JIIS submission package](revisions/2026-10-02-jiis-final-contribution-layout/README.md) |

## Reviewer quick start

Install Git and [uv](https://docs.astral.sh/uv/getting-started/installation/),
then run from PowerShell or a POSIX shell:

```text
git clone --branch jiis-reviewer-2026-10-03 --filter=blob:none --sparse https://github.com/lhh666-6/auto-dete.git auto-dete-review
cd auto-dete-review
git sparse-checkout set reproduction/dke
uv run --no-project --python 3.11 reproduction/dke/reviewer.py prepare
uv run --no-project --python 3.11 reproduction/dke/reviewer.py verify
uv run --no-project --python 3.11 reproduction/dke/reviewer.py test
uv run --no-project --python 3.11 reproduction/dke/reviewer.py e1
```

Expected: archived E1/E2 summaries and all **22,400** E3 timing observations
match; **10 tests pass**; fresh E1 produces **495 executions**, **165
exact/reference agreements**, and **15 equal-valued policy separators**.
Outputs go to `.reviewer-work/`, never into the deposited evidence.

`verify` recomputes archived records; `e1` runs the systems again. For fresh
browser runs, performance workloads, witness tests, and the separate Alloy /
projection / fault-catalogue evidence, follow the [reviewer guide](REVIEWER_GUIDE.md).
The [October 3 verification receipt](docs/reproduction/JIIS-ENTRY-VERIFICATION-2026-10-03.json)
records exactly which checks were rerun. The named tag freezes this entry point;
the experiment commits below remain unchanged.

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

<details>
<summary>Historical manuscripts and author revision records</summary>

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

</details>

Public availability does not imply an OSI open-source license for all contents.
Third-party notices remain with the bundled tools; consult the authors for
reuse beyond evaluation. Repository files do not state journal acceptance.

</details>
