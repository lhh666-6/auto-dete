# Reproduce the current JIIS paper

**Correction-Aware Data Admission: Candidate-Bound Authorization and
Field-Level Provenance for AI-Derived Updates**

Use this guide for the [24-page centered manuscript](revisions/2026-10-02-jiis-final-contribution-layout/submission-files/Manuscript.pdf)
and [14-page Online Resource 1](revisions/2026-10-02-jiis-final-contribution-layout/submission-files/ESM_1.pdf).
Start with Steps 1–3. E2, performance measurements and additional formal checks
can be run independently afterwards. Reading author revision notes is unnecessary.

## Choose the claim you want to check

| Paper evidence | Command / route | Expected result and boundary |
|---|---|---|
| E1–E3 reported aggregates | `prepare`, then `verify` | E1: 495 executions / 165 agreement / 15 separators; E2: 60 cases; E3: 22,400 raw timing observations. Recalculates archived data, not fresh system runs. |
| Core supplementary implementation checks | `test` | 10 tests pass. |
| E1 instance-vs-context policy distinction | `e1` | 495 fresh executions; 165 exact/reference agreements; 15 equal-valued substitutions separate policies. |
| Five paired-history constructions | `formal` | 19 Python witness tests; this is not an Alloy solver run. |
| E2 request/display boundary | `e2`, after browser installation | 60 fresh browser cases; nine request substitutions separated; three display-only substitutions accepted by both paths. |
| E3 admission and trace timing | `e3 --section mechanism`, `ablation`, or `trace` | Full frozen grids; compare correctness and distributions, not identical milliseconds. |
| E3 database footprint | `e3 --section storage` | Separate 1,000 / 10,000 / 100,000-transition schemas; not part of the 22,400 timings. |
| Alloy, formal–concrete projection, 35-case catalogue | Separate pinned formal archive, below | These supporting results use their original source/tools; `verify` and `formal` do not rerun them. |

The retained folder name `reproduction/dke` identifies the original deposit.
It is the supported entry point for the current JIIS paper; do not switch to an
older README or pick files from `latest/` to run E1–E3.

## 1. Obtain the entry point and prepare the fixed evidence

Prerequisites: Git and [uv](https://docs.astral.sh/uv/getting-started/installation/).
uv supplies Python 3.11 and the required packages. The following commands work
in PowerShell and in a POSIX shell:

```text
git clone --branch jiis-reviewer-2026-10-03 --filter=blob:none --sparse https://github.com/lhh666-6/auto-dete.git auto-dete-review
cd auto-dete-review
git sparse-checkout set reproduction/dke
git rev-parse HEAD
uv run --no-project --python 3.11 reproduction/dke/reviewer.py prepare
```

If you already have the repository, start in its root and run the last command.
Preparation creates `.reviewer-work/` with the two sibling source trees expected
by the original scripts. It extracts fixed Git objects, verifies source/input
hashes, and obtains the twelve selected archived inputs and raw result records.
No hosted-model calls or archived database downloads are needed. Network access
is used to retrieve Git objects and install dependencies.

| Component | Exact commit |
|---|---|
| E1–E3 deposit | `2645e5e18c900ea91c9c980e44195dc71e410432` |
| Reference source and input archive | `c6d512843c905cab6d8521dd8c914f7fb26d85ae` |

The tool records extracted file hashes in `.reviewer-work/snapshot.json` and
checks them against the deposit's manifests. The historical
`r31-jss-2026-09-13` tag resolves to the reference-source commit above, but it is
not the E1–E3 deposit or the current manuscript. The runner uses explicit commit
IDs so a manuscript revision cannot silently select different experiment code.

All commands below run from the repository root. To use a different location,
append `--workspace PATH` to every invocation. `prepare` requires a new directory
and refuses to overwrite an existing one. Reuse the prepared directory for
later steps; use a new path to start over.

On Windows, a short checkout path such as `C:/review/auto-dete-review` also
keeps filenames manageable for external browser and database tools.

## 2. Verify the published results, without rerunning experiments

```text
uv run --no-project --python 3.11 reproduction/dke/reviewer.py verify
```

This recomputes E1/E2 aggregates from the archived per-case records and all E3
per-cell timing summaries from the raw observations. It also verifies the
selected source and input hashes. Expected output:

| Check | Expected result |
|---|---|
| E1 | 495 executions; 165 exact/reference agreements; 15 equal-valued separators |
| E2 | 60 browser cases; accepted counts 21 for `original_confirm`, 12 for `session_gate` |
| E3 mechanism / ablation / trace | 4,000 / 4,000 / 14,400 observations; all summaries match |
| Rejected E1/E2 cases | Before/after state digests match |

The machine-readable receipt is `.reviewer-work/verification.json`. This step
checks raw-to-summary calculations; it does not execute the admission systems
or inspect every archived database. Continue below for fresh execution.

## 3. Run the core checks and reproduce E1

```text
uv run --no-project --python 3.11 reproduction/dke/reviewer.py test
uv run --no-project --python 3.11 reproduction/dke/reviewer.py e1
```

Expected: ten supplementary tests pass, then all 495 E1 executions complete.
The journal with exact binding and the reference implementation agree on all
165 paired cases. The fifteen equal-valued substitutions distinguish the
context policy from the instance policy. The context arm accepts 60 cases;
the exact and reference arms each accept 45. These are different authorization
policies, rather than a claim that context authorization is always erroneous.

The selected historical proposals are inputs to constructed cases. E1 does not
rerun their original hosted-model workflows. The runner pins SQLAlchemy 2.0.51
and pytest 9.1.1, the packages needed for these core steps. The full original
environment export is retained in
`.reviewer-work/DKE-supplement/requirements-source-lock.txt` for inspection.

Each run prints its new directory under `.reviewer-work/runs/`. E1 writes
`receipts.jsonl`, `summary.json`, databases, selected-input provenance, and
`comparison-to-deposit.json`. Compare decisions and query answers: generated
identifiers and timestamps need not match byte for byte. The comparison exits
with an error if the expected full-case results do not match.

The three E1 arms each execute 165 cases: 165 × 3 = 495. Pairwise agreement has
165 as its denominator, not 495. Context acceptance is 60/165; exact and reference
acceptance are each 45/165. Fifteen substitutions are a policy separator, not a
population error-rate estimate.

## Optional: E2 browser and review-channel experiment

Install Playwright's Chromium once, then run all sixty local browser cases:

```text
uv run --no-project --python 3.11 --with playwright==1.58.0 python -m playwright install chromium
uv run --no-project --python 3.11 reproduction/dke/reviewer.py e2
```

On Linux, Chromium may also require system libraries; Playwright's
`install --with-deps chromium` installs these where permitted. Alternatively,
set `DKE_CHROME` to your existing Chrome executable before running E2. In
PowerShell, use `$env:DKE_CHROME = 'C:/path/to/chrome.exe'`; in a POSIX shell,
use `export DKE_CHROME=/path/to/chrome`.

The original driver used a fixed Windows Chrome path and did not record its
Playwright package version. The runner changes only browser selection in a
disposable driver copy. It records that adapter and both hashes; the archived
driver and all interaction/case logic stay unchanged. Playwright 1.58.0 is the
reviewer driver's version. The browser driver records the actual browser version.

Expected: sixty scored cases, no harness errors, nine request substitutions
accepted by the original path and rejected by the session gate. Both paths
accept the three DOM-only substitutions. Rejected cases preserve state.
The output includes DOM observations, server receipts, screenshots, browser
metadata, `summary.json`, and `comparison-to-deposit.json`.

## Optional: E3 performance and storage

Step 2 already reproduces the published timing summaries from their raw data.
For fresh measurements, choose a full workload section:

```text
uv run --no-project --python 3.11 reproduction/dke/reviewer.py e3 --section mechanism
uv run --no-project --python 3.11 reproduction/dke/reviewer.py e3 --section ablation
uv run --no-project --python 3.11 reproduction/dke/reviewer.py e3 --section trace
uv run --no-project --python 3.11 reproduction/dke/reviewer.py e3 --section storage
```

Each command creates a separate output directory. Omitting `--section` runs all
four sections together. These commands use the full frozen grids: five warmups
and 200 timed trials per arm/cell, with seed 20260923. Mechanism and ablation
each produce 4,000 timed observations; trace produces 14,400. Storage constructs
1,000, 10,000 and 100,000 transitions and is separate from timing evidence.

Trace and storage can take substantially longer and use more disk space than
E1. The output contains configuration, environment, source hashes, raw records,
summaries and section receipts. Compare workload sizes, outputs, SQL counts
and timing distributions; fresh milliseconds depend on hardware and system
load. The runner uses Python 3.11 and records the actual Python/SQLite runtime,
which may differ from the original environment recorded in the deposit.

For original database inspection, use the [fixed experimental deposit](https://github.com/lhh666-6/auto-dete/tree/2645e5e18c900ea91c9c980e44195dc71e410432/DKE-supplement).
Its `restore_large_database.py` reconstructs the compressed 100,000-transition
database and checks its SHA-256. Full database inspection is separate from the
small evidence workspace prepared here.

## Optional: paired-history witnesses and additional formal evidence

```text
uv run --no-project --python 3.11 reproduction/dke/reviewer.py formal
```

Expected: nineteen Python witness tests. This checks the paired-history
constructions; it does not rerun the Alloy solver. The existing bounded Alloy
batch, formal–concrete projection and 35-case catalogue are additional evidence
used by the paper. Use the [frozen JSS reproduction guide](https://github.com/lhh666-6/auto-dete/blob/r31-jss-2026-09-13/REVIEWER_GUIDE.md)
in a **separate clone of that tag** for their packaged tools and commands.
Those checks have their own source version and output directories.

For those checks only, make a separate checkout:

```text
git clone --branch r31-jss-2026-09-13 --filter=blob:none --sparse https://github.com/lhh666-6/auto-dete.git auto-dete-formal
cd auto-dete-formal
git sparse-checkout set latest reproduction/tools
```

Then follow that tag's root `REVIEWER_GUIDE.md` for its Java/Alloy environment,
`latest/formal/alloy/batch/run_batch_alloy.ps1`, and the implementation
`conformance` commands. The archive expects 72 Alloy command outcomes, 29
projection checks (9 SAT / 20 UNSAT), and 35 catalogue cases. These older
environments and tools are separate from the minimal E1–E3 setup; the old
manuscript's RQ numbering is not the current JIIS numbering.

## If a step stops

| Message / symptom | Next action |
|---|---|
| `Workspace exists` from `prepare` | Reuse it with `verify`, or choose a new `--workspace PATH` for **every** command. Preparation intentionally never overwrites a workspace. |
| Git object retrieval or dependency download fails | Check network access; use an ordinary Git clone rather than GitHub's source ZIP. The runner reads pinned historical Git objects. |
| `Prepared file changed` or a source-hash mismatch | Stop; use a new workspace and rerun `prepare`. Do not edit the frozen scripts to make checks pass. |
| Browser executable missing | Install Chromium as described above, or set `DKE_CHROME` to a working Chrome executable. |
| Fresh performance differs from the table | Compare workload size, decisions/query outputs, SQL counts, and timing distributions. Hardware-dependent milliseconds are not an equality check. |

When reporting a failure, include `git rev-parse HEAD`, the exact command,
Python/OS information, and the generated receipt/error message. No model API
key is needed for these steps.

## Manuscript and historical records

- [Current JIIS submission source package and build instructions](revisions/2026-10-02-jiis-final-contribution-layout/README.md):
  compile the manuscript independently of the experimental runner.
- [Pinned experiment protocol](https://github.com/lhh666-6/auto-dete/blob/2645e5e18c900ea91c9c980e44195dc71e410432/DKE-supplement/PROTOCOL.md):
  detailed experimental definitions, controls and selection rules.
- [September 27 entry-point verification](docs/reproduction/DKE-ENTRY-VERIFICATION-2026-09-27.md):
  retains the earlier browser/performance verification record.
- [October 3 entry-point verification](docs/reproduction/JIIS-ENTRY-VERIFICATION-2026-10-03.json):
  records the fresh-workspace commands actually checked for this reviewer entry.
- [Supplied-package identity check](docs/reproduction/JIIS-PACKAGE-VERIFICATION-2026-10-03.json):
  confirms that the supplied centered package matches the current PDFs and sources.

`latest/`, older reviewer readmes and editorial revision records document prior
research stages. They are not additional steps for E1–E3. Hosted-model reanalysis
and fresh provider calls belong to the historical study; no credentials are
needed for the steps in this guide.
