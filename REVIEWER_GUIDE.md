# Reviewer guide — r31-jss-2026-09-13

## Obtain the complete evidence

The reference environment is Windows, Python 3.11.9 and PowerShell. Java 21 and Alloy 6.2.0 are bundled. TeX compilation requires a TeX distribution with elsarticle, BibTeX and the listed packages; latexmk additionally needs Perl. Installing Python/TeX dependencies requires network access; the deterministic verification steps make no paid model calls.

```powershell
git lfs install
git clone --branch r31-jss-2026-09-13 https://github.com/lhh666-6/auto-dete.git auto-dete-review
Set-Location auto-dete-review
git lfs pull
python -B verify_freeze.py
python -B latest/verify_latest.py
```

Use the complete clone for raw hosted-run records. `latest/` alone contains the current paper and derived evidence but not every historical raw record. The full local reviewer ZIP provided with the freeze materializes LFS contents and contains the same root manifest. GitHub-generated source ZIPs may have pointers instead: `verify_freeze.py` reports that explicitly.

Preserve an untouched copy. Run the following in a disposable working copy, placing outputs outside the repository. Set `$reviewOutput` to a new directory and record the path. Do not run experimental generators over archived evidence.

## Install the lock-pinned environment

From the repository root, using an installed uv:

```powershell
$reviewOutput = Join-Path $env:TEMP ('auto-dete-review-' + [guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path $reviewOutput | Out-Null
$env:UV_PROJECT_ENVIRONMENT = Join-Path $reviewOutput 'venv'
uv sync --project latest/code/implementation-fixed --locked --extra dev --extra research --no-install-project --python 3.11
$reviewPython = Join-Path $env:UV_PROJECT_ENVIRONMENT 'Scripts/python.exe'
& $reviewPython -B reproduction/tools/verify_rq8_claims.py latest/code/figure-work/evidence/agent-authority-benchmark-v2/manuscript-input/2026-09-03-three-config-10x/normalized/agent_authority_benchmark_runs.json
```

The final check used the unchanged lock, including SQLAlchemy 2.0.51 and NumPy 1.26.4. Do not replace the lock with the older verifier's environment versions.

## Formal and implementation checks

From the repository root:

```powershell
./latest/formal/alloy/batch/verify_batch_package.ps1 -RequireRawResults
./latest/formal/alloy/batch/run_batch_alloy.ps1 -FreezeId reviewer-run -OutputRoot (Join-Path $reviewOutput 'alloy')
Push-Location latest/code/implementation-fixed
& $reviewPython -B -m pytest -q -p no:cacheprovider --basetemp (Join-Path $reviewOutput 'pytest')
& $reviewPython -B conformance/run_catalogue.py --output (Join-Path $reviewOutput 'catalogue')
& $reviewPython -B conformance/verify_catalogue_results.py (Join-Path $reviewOutput 'catalogue')
& $reviewPython -B conformance/verify_formal_refinement_records.py
& $reviewPython -B conformance/generate_formal_refinement_records.py --output (Join-Path $reviewOutput 'refinement')
Pop-Location
Push-Location latest/code/formal-fixed
& $reviewPython -B -m unittest discover -s tests -v
Pop-Location
Push-Location latest/code/checklist-example
& $reviewPython -B -m pytest -q -p no:cacheprovider
Pop-Location
Push-Location latest/code/strong-baseline
& $reviewPython -B -m pytest -q -p no:cacheprovider
Pop-Location
```

Expected: 72 Alloy commands; 389 implementation tests; 35/35 catalogue cases; 29 projections (9 SAT, 20 UNSAT); 19 witness tests; 27 checklist-control tests; 9 strengthened-control tests. One local final run took about seven minutes for the implementation suite; timings depend on the machine.

## Annotation and endpoint reanalysis

- [Acknowledgment analysis commands](latest/evidence/human-acknowledgment-annotation-2026-09-10/README-REPRODUCE.md): 325 exact joins, agreement 286/325, kappa 0.644171. Write the output and generated TeX table outside the package.
- Benign annotation: from `latest/evidence/human-annotation-2026-09-10/`, run `recompute_irr.py --labels labels-A1-A2-normalized.csv --out <new-output.json> --replicates 5000 --seed 20260910` with the configured interpreter.
- Endpoint reanalysis: `latest/code/scripts/endpoint_sensitivity.py` takes `--runs-root r21-jss/evidence/agent-authority-benchmark-v2/final/2026-09-01-three-config-10x/runs`, the normalized JSON path used above, and a new `--output-dir`. Paths are interpreted relative to the current working directory; invoke from the repository root.
- [AI review proposals](latest/evidence/acknowledgment-ai-review-2026-09-12/README.md) are separate post-hoc judgments. Original human labels, rubric and rule-hit results remain the reported data.

## Manuscript build

In a disposable copy of `latest/paper/`, run `latexmk -pdf main.tex` then `latexmk -pdf supplement.tex`. If latexmk/Perl is unavailable, use `pdflatex -output-directory=out` for each stem, copy `filtered.bib` to `out/`, run `bibtex main` from `out/`, then repeat pdflatex until references stabilize. The shipped `.latexmkrc` handles the copy and output paths for latexmk. Build PDFs may differ bytewise owing to timestamps/toolchain metadata; compare text, references, tables and declared counts.

## What is and is not reproduced

| Evidence | Reproduction boundary |
|---|---|
| RQ1–RQ5 | Bundled formal/implementation/control source and frozen records; final checks rerun the formal batch, projection generation, catalogue and test suites. |
| RQ6 | Source and frozen cost inputs supplied. Values can be traced to deposited JSON; fresh wall-clock timings need not match. This freeze does not replace the v8 timing experiment. |
| RQ7 | Driver/plugin source and source pin are supplied under `r21-jss/source/dsh-plugin-auto-decte/`. The pinned DeepSeek Harness host is external, not redistributed here. Consult its SOURCE_PIN.json and setup documentation. |
| RQ8 | All original hosted-run records remain available for inspection and deterministic reanalysis. Generating fresh hosted outputs requires provider credentials and can yield different outputs. |

The project is publicly inspectable, not certified independently replicated. Open Science evaluation by JSS is a separate journal process. This freeze does not claim that every legacy exploratory script is a supported entry point; use the commands above and the current package guide.
