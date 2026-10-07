> **KAIS 论文修订（2026-10-07）**：本分支的新版全文、补充材料、可编辑源码和图表见 [KAIS 修订目录](revisions/2026-10-07-kais-continuity/README.md)。[正文 PDF（13 页）](revisions/2026-10-07-kais-continuity/main.pdf) · [补充材料 PDF（23 页）](revisions/2026-10-07-kais-continuity/supplement.pdf) · [源码 ZIP](revisions/2026-10-07-kais-continuity/KAIS-editable-sources.zip)。以下 JIIS 入口及旧版实验档案保留供追溯。

> **Phase 2 当前结果（2026-10-07 10:10 北京时间）**：原正式批次 512 个计划臂已结束；额度恢复补采已纳入 45/117 个配对的中期快照。原始结果、分析表和复算说明见 [PHASE2-RESULTS-LATEST.md](PHASE2-RESULTS-LATEST.md)。

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

