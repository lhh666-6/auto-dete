# AUTO-DECTE R21 reviewer-package candidate

## Repeated benchmark extension status (2026-08-31)

The earlier six-case R21 package described below remains technically complete. A later approved
extension adds a repeated, cross-provider live-agent authority benchmark. Its provider-neutral
implementation, deterministic 112-run dry-run, reporting renderer, resource gate, and Final
configuration/freeze builders are complete locally. Pilot-1 subsequently completed all 112
coordinates but failed the frozen qualification gate: only DeepSeek D1 qualified, so Final is
blocked by the missing OpenAI family. Pilot-1 and its verified manifest remain unchanged.

No repeated-benchmark result is citable yet, and the manuscript has not been updated with Pilot or
diagnostic observations. Pilot-2 stopped after one invocation because a relative MCP data path
opened an unintended empty database; that root is externally manifested, classified as an aborted
harness run, and prohibited from resuming. The repaired Pilot-3 uses a complete locked 112-run plan,
zero automatic transport retries, hard launch-lock enforcement, and at most one provider invocation
per quota-aware checkpoint command. Its preflight passes and its output root remains absent.

This directory is the standalone R21 reviewer-package candidate for
*Certificate-Bound Admission of AI-Derived Updates into Versioned Authoritative
Records*. It contains the current implementation and tests, the R17 runner and
frozen raw evidence, the R18 hosted-AI fixture, the R19 DeepSeek Harness (DSH)
plugin experiment, and the R21 live-agent/performance extension. R21 adds exactly
three separately manifested paper inputs for six real-agent scenarios, a
relationally equivalent admission comparator, and an optimized reverse-trace
rerun. This is a locally assembled package; no public R21 URL or DOI is claimed.

## Layout

- `source/implementation/`: immutable Python/SQLite implementation, tests,
  conformance runners, benchmark code, `pyproject.toml`, and `uv.lock`.
- `source/formal/` and `source/tools/`: the bundled Alloy models, Alloy 6.2.0,
  and JRE required by the conformance tests.
- `source/paper-repo/`: the preserved R17 paper-repository source snapshot.
- `source/dsh-plugin-auto-decte/`: canonical two-tool DSH plugin, experiment
  driver, source pin, normalizer, and offline verifier.
- `source/live-agent-experiment/`: two-tool MCP server, locked scenarios,
  independent database probe, and non-overwriting Codex runner.
- `source/performance-experiment/`: feature-equivalent admission and optimized
  trace benchmark sources plus locked configs.
- `source/external/downloads/`: official version-pinned DSH release archive.
- `runner/`: the preserved R17 artifact runner and release-verification tools.
- `evidence/frozen/`: the read-only R17 raw evidence; its own manifest verifies
  independently from later overlays.
- `evidence/final-rerun-paper/paper_inputs/`: the ten normalized R17 baseline
  inputs copied byte-for-byte from the preserved R19/R17 lineage.
- `evidence/reproduced/`: the only permitted destination for new executions.
- `evidence/reproduced/r19-dsh-2026-08-27-final/`: ten-case R19 receipt and
  non-self-referential 30-file manifest; failed run-1/run-2 directories remain
  retained as provenance and are not citable alternatives.
- `evidence/r19-revision-manifest.json`: non-self-referential R19 overlay
  manifest covering implementation, plugin, evidence, literature, and paper.
- `evidence/reproduced/r21/live-agent-run-4/`: canonical amended six-scenario live-agent run;
  run-2 is the earlier verification-only protocol and incomplete run-3 is retained as failure
  provenance after a Windows locale decoding stop.
- `evidence/reproduced/r21/feature-baseline-run-1/`: 2,000-pair equivalent baseline.
- `evidence/reproduced/r21/trace-optimization-comparison-3/`: adopted-baseline
  comparison over the clean run-2 optimized measurements.
- `evidence/r21-paper-input-manifest.json`: three R21 inputs, two generated tables,
  and their hashed source evidence.
- `paper/`: JSS LaTeX source, compiled PDF, editable vectors, generated tables,
  bibliography, and paper-specific audit ledgers.
- `research_audit/08_FINAL_RESEARCH_LOCK.md`: exact claim/evidence boundary.

Historical failed packages, the legacy ESWA manuscript, and the non-submitted
AI ideation raster remain outside the citable evidence set. The preserved R17
source/release manifests describe their historical pre-R21 tree and are not
expected to validate the modified R21 root; the frozen evidence's own manifest
does validate in place, and the final R21 revision manifest binds this package.

## R21 verification

From this directory:

```powershell
python scripts/build_r21_inputs.py verify
python scripts/build_r21_manifest.py verify
python source/dsh-plugin-auto-decte/experiment/verify_receipt.py verify `
  evidence/reproduced/r19-dsh-2026-08-27-final
```

The retained R19 revision manifest describes the pre-R21 overlay and is verified
at the R19 package root; it is intentionally not regenerated against this later
paper revision. The R21 revision manifest supersedes it for the complete current
directory.

The preserved R17 raw evidence verifies independently with:

```powershell
$env:PYTHONPATH = (Resolve-Path 'runner').Path
python -B runner/release_tools/r17_release.py verify-declared `
  --root evidence/frozen --manifest evidence/frozen/manifest.json
```

From `source/implementation/`, the frozen Python checks are:

```powershell
uv sync --frozen --extra dev --extra research
uv run pytest -q
uv run ruff check app tests
uv run mypy app
```

The current implementation regression passes 364 tests; the amended live-agent
adapter passes 15 additional tests and the three focused R21 benchmark modules pass five.
The complete command record is reported in `FINAL_CODEX_HANDOFF.md`.
DSH source identity and canonical plugin hashes are in
`source/dsh-plugin-auto-decte/SOURCE_PIN.json`. The keyless experiment uses the
real pinned Cordis plugin lifecycle and DSH `ToolRuntime`. R21's separate live
agent uses the authenticated Codex CLI and exposes no confirmation tool.

The live-agent adapter has its own frozen environment. From
`source/live-agent-experiment/`, run `uv sync --frozen` and `uv run pytest -q`.
Bridge tests use `source/implementation/.venv/Scripts/python.exe`, created by
the implementation `uv sync` command; alternatively set
`AUTO_DECTE_IMPLEMENTATION_PYTHON` to an explicit interpreter. Hosted reruns
also require an authenticated `codex-cli 0.150.0-alpha.8`; the exact executable,
requested model alias, and versions are recorded in each run metadata file.

## Integrity boundary

`evidence/r21-paper-input-manifest.json` binds every R21 normalized input and
generated table to the raw R21 receipts, configurations, benchmark sources, and
direct execution dependencies used to produce it. The final
`evidence/r21-revision-manifest.json` binds this complete package. The preserved
`evidence/frozen/manifest.json` remains authoritative for the frozen raw R17
baseline. Full performance reruns require several hours and fresh output paths;
the retained R17 and R21 receipts are the citable completed executions.

## Paper

`paper/main.pdf` is the compiled R21 reviewer copy. It integrates the live-agent
experiment, necessity scenarios, feature-equivalent performance baseline, and
indexed reverse-trace evaluation. Author names, affiliations, funding,
conflicts, acknowledgments, institutional declarations, and a stable R21
artifact URL/DOI remain explicitly marked author inputs; see
`paper/AUTHOR_INPUT_NEEDED.md`. The public GitHub repository currently contains
an older ESWA artifact and must not be cited as the R21 deposit until the R21
package is uploaded and pinned by commit, release, or DOI.
