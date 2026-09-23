# September 23 DKE supplementary experiment deposit

The `DKE-supplement/` directory preserves the executed experiment package,
including pilot outputs, scripts, reports, raw timings, browser observations,
and databases. It adds evidence alongside the frozen JSS package; no frozen
submission files or historical tags are replaced.

- [Chinese results report](../DKE-supplement/REPORT.md)
- [English manuscript insertion](../DKE-supplement/MANUSCRIPT_INSERT.md)
- [Execution protocol and amendments](../DKE-supplement/PROTOCOL.md)
- [Reproduction instructions](../DKE-supplement/README.md)
- [File hashes, including databases](../DKE-supplement/artifact-manifest.json)
- [Source integrity record](../DKE-supplement/source-integrity.json)

## Preserve the executed layout when reproducing

The scripts were run with the following sibling directories. Their original
bytes are retained to preserve the pre-run hashes; repository publication does
not silently rewrite those scripts or the original machine paths in receipts.

```text
workspace/
  dke-experiments/    # source checkout at c6d512843c905cab6d8521dd8c914f7fb26d85ae
  DKE-supplement/     # copy of this deposited directory
  .venv-study/       # Python 3.11 environment with the locked dependencies
```

Copy the deposited directory outside the source checkout into that layout before
running the scripts. Obtain the pinned source using a separate checkout or Git
worktree. Use fresh result directories as explained in the package README.
The summary and integrity scripts intentionally refer to the original `e1`,
`e2`, and `e3` paths; do not mix new measurements into those sealed results.
The browser experiment uses Windows Chrome and a configurable driver-Python
path. No API keys or hosted model requests are required.

The 141,062,144-byte full storage database is deposited as `full.db.gz` to
avoid a slow large-object transfer. Compression is lossless; restore it before
checking the original artifact manifest:

```sh
python -B DKE-supplement/restore_large_database.py
```

The restoration script verifies the decompressed SHA-256 against the original
manifest and refuses to overwrite differing existing data. The publication
packaging receipt records both sizes and hashes. Other original experiment
files retain their executed bytes. Historical source artifacts elsewhere in
the repository still require Git LFS.

Paths in the original JSON manifests use Windows separators. Hashes identify
this specific execution; regenerated databases may have different timestamps and IDs.

## Scientific scope

The new comparator is study code, not an independently deployed third-party
system. Archived proposal values are mapped to constructed cases, and browser
interaction is automated. The experiments are not human-subject research or new
provider evaluations. Exact-binding equivalence and the DOM-only substitution
limitation are retained in the report. Performance measurements describe one
machine and explicitly stated timing boundaries; materialization and storage
ablations are not functionally complete security baselines.
