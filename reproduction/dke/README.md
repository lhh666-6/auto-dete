# Reviewer tools for the current JIIS paper

Start with the repository's [reviewer guide](../../REVIEWER_GUIDE.md). It lists
prerequisites, commands, expected results and the optional experiments.

The directory name `dke` is retained for compatibility with the original frozen
deposit. The current manuscript is the 24-page centered JIIS version linked
from the root README. The `jiis-reviewer-2026-10-03` tag freezes the reviewer
entry point; the scientific deposit and reference-source commits are unchanged.

`reviewer.py` prepares only the pinned sources and small evidence files needed
for E1–E3 and the paired-history witness tests. It checks the deposited source
hashes, supplies the sibling directory layout expected by the original scripts,
and puts new outputs in `.reviewer-work/runs/`. The original deposit, manuscript
and historical directories remain unchanged.

| Action | What it does |
|---|---|
| `prepare` | Extract fixed Git objects into a new workspace; verify source/input hashes. |
| `verify` | Recompute archived E1/E2 aggregates and E3 timing summaries from raw records. |
| `test` | Run the ten supplementary implementation/control tests. |
| `formal` | Run the paired-history Python witness tests; this is separate from Alloy analysis. |
| `e1` | Execute all 495 constructed cases and compare results with the deposit. |
| `e2` | Execute all 60 local browser cases and compare results with the deposit. |
| `e3` | Rerun full performance workloads; select a section with `--section`. |

All actions accept `--workspace PATH`. Preparation requires a new directory;
later actions reuse it. New executions receive timestamped output directories.
Dependency installation and Git object retrieval may use the network. The
experiments themselves make no hosted-model calls.

E2 has one recorded launch-path adapter: a disposable copy of the browser
driver selects `DKE_CHROME`, or the Chromium installed by Playwright. No case,
page, request, assertion or admission logic changes. Both driver hashes and
the chosen driver package are saved in `browser-adapter.json`. The original
Playwright package version was not recorded; the reviewer driver uses 1.58.0.

`verify` checks the selected evidence and raw-to-summary calculations. Full
database inspection, storage restoration, hosted-run reanalysis and the Alloy
batch have their own instructions in the reviewer guide and linked archives.
