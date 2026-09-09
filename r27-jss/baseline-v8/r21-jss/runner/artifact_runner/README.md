# Auto-Decte artifact runner

This is the sole supported source-to-evidence interface. It uses only Python's
standard library and is path-independent.

Modes:

- `verify`: verify a staged source manifest and any frozen evidence manifest.
- `rerun-correctness`: run configured correctness commands into a new output.
- `rerun-performance`: run configured performance commands into a new output.
- `reproduce-paper`: normalize retained correctness/performance receipts and declared
  JSON artifacts into paper inputs, including deterministic quality counts, with a
  raw-to-paper SHA-256 lineage ledger.
- `full`: run correctness and performance, then normalize results.

Every mutating mode refuses an existing output directory. Each command retains
stdout, stderr, exit status, duration, hashes, and timeout status even when it
fails. Manifests deliberately exclude their own file. A failed run is never
resumed in place; use a new run ID and retain the failed directory.

The declared install policy is online resolution from the indexes encoded by
`uv.lock`; no offline/wheelhouse claim is made. Expected peak disk is dominated
by the 100k-transition storage cell and should be budgeted at 5 GB. Correctness
may take tens of minutes including Alloy; the full performance grid may take
several hours on the characterized machine.

Build a staging freeze:

```powershell
$env:PYTHONPATH = (Get-Location).Path
python -B -m artifact_runner.freeze `
  --parent-root . `
  --implementation-root experiments/auto-decte `
  --config artifact_runner/config/source_freeze.json `
  --output release-staging/<freeze-id>
```

The runner never reads legacy ESWA aggregate artifacts or historical G3b result
directories.

For an immutable staging smoke test, synchronize dependencies into an external
environment with `uv sync --no-install-project --frozen --all-extras`, invoke
Python with `-B`, set `PYTHONDONTWRITEBYTECODE=1`, and disable pytest's cache
provider. Editable installation into the staged source is intentionally
forbidden because it writes `*.egg-info` into the source tree.
