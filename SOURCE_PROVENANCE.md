# SOURCE_PROVENANCE.md

This artifact contains three provenance components derived from two source states.
They must not be conflated.

## Source state 1 — commit 68f7b93

### Component A — executable source snapshot

- `source_snapshot_68f7b93/` is the repository tree at commit
  `68f7b93e3ff3a5b99f3053d6567c432cee1c405c` (integrated state).
- File-level identity was verified against git blobs (git hash-object vs
  git rev-parse) for the application, benchmark, test, config, and lock files.
- One internal process document (`docs/eswa-implementation-inventory.md`) was
  excluded from the snapshot for anonymity; it is not needed to run or verify
  the experiments. `docs/eswa-reproducibility.md` is the clean reproducibility
  guide and is included.

### Component B — authority-integration benchmark output

- `artifacts/pipeline_authority_68f7b93e3ff3/` is the output of
  `benchmarks/pipeline_authority_benchmark.py` run from the clean 68f7b93
  snapshot with fixed injected clock and seed:
  `--now 2026-08-17T12:00:00+00:00 --seed 20260817 --cases 12`.
- Two independent runs produced byte-identical outputs.
- `pipeline_authority.json` SHA-256:
  `1677cbb526e786b754e8bdb4d6e983df26f88b59b47ec0dd2733c943ad87c4ed`
- `manifest.json` records `clean_before_run=true`, empty
  `git_status_porcelain`, `source_commit=68f7b93e3ff3a5b99f3053d6567c432cee1c405c`,
  and `config_sha256=a16ac5eefd6e73f06932e917d364fb32dd065fd83b6d54a7d83733a648f9d61d`.

## Source state 2 — commit 195355a (recorded ESWA evaluation run)

### Component C — manuscript-level frozen outputs

- The files under `artifacts/` (recognition, whole-form, workflow, trust
  ablation and stress, resilience, rendered tables/figures, manifest) are the
  27 hashed outputs of the recorded ESWA evaluation run
  (`python -m benchmarks.run_all --config benchmarks/config/eswa-v1.json`),
  executed with a clean tracked source state at commit
  `195355a27f3606bc070d8606ed299549067c5a6e`.
- These are the exact outputs used to generate the reported tables and figures;
  the supplementary material's Artifact inventory (10 files) maps one-to-one
  onto the files under `artifacts/` (same paths and file names).
- `manifest.json` lists all 27 outputs with SHA-256 hashes.

### Reproducibility boundary between the two source states

- The recorded run environment (component C) used, among others, numpy 2.3.5
  and opencv-python-headless 4.13.0.92.
- The 68f7b93 snapshot (component A) constrains numpy `>=1.26,<2` and
  opencv-python-headless `>=4.10,<4.12` in `pyproject.toml`.
- Byte-identical reproduction is therefore claimed only for the
  authority-integration benchmark (component B), which is generated from the
  68f7b93 snapshot itself. The 68f7b93 snapshot is not claimed to reproduce
  the component C files byte-for-byte; component C is supplied frozen.

### Explanatory Figure Provenance

The submitted manuscript contains revised explanatory Figures 1–3 describing the trust architecture, operational pipeline, and reverse-trace lineage.

These diagrams are presentation-layer explanatory materials and are not part of the frozen experimental outputs.

OpenAI ChatGPT (GPT-5.6 Sol) assisted with their design and visual refinement. The final scientific structure, terminology, labels, authority relationships, and workflow logic were reviewed and verified by the author against the manuscript and evaluated implementation.

The frozen benchmark artifacts, source snapshot, manifests, hashes, raw predictions, and quantitative results remain unchanged.

The final explanatory figures are available under
paper/final_explanatory_figures/ as vector PDFs with PNG previews.

## File hashes

### artifacts/manifest.json

- SHA-256 of the manifest file itself:
  `1fde886ce9e75bbc19151a7437e2d7a806530f8da6ecdb681284ea652874758c`
- Recorded benchmark configuration SHA-256 (config_sha256):
  `4c876ca1ca64162b17b18692e2e2dc808f7fe271ffd571897143237bd03777bb`

### Other frozen JSON outputs under artifacts/ (from manifest.json, verified against the files in this package)

| File | SHA-256 |
|---|---|
| recognition_raw.json | 32cdc68b6e9aea48ea187806dc85f60e2f4bb326cc3d067e83d9e567deaa3293 |
| recognition_summary.json | 994e02a919182a2ea0b774a74147f34c39286b5817a41e19db1ce112220bfac8 |
| form_raw.json | 659e1864530655c88a582eebc0d8dfe04e1eac6afe6d62ac387d43ba533ba283 |
| form_summary.json | 0b0fa43bb33db42d81580fac7b379e84db313eaf5ed8ff7d5053857bdcdbe42d |
| form_workflow.json | dbb2f2c49b2d7ff0d8bfbd48891fdee1aad42112fdca4bef670610f22fb2856c |
| trust_faults.json | b82a528f662942f63f0e4ddfade98873410091333eb1c54c0c41b1ce03bde200 |
| trust_ablation.json | e9ffe3807e528f649800af78775dc0778a7fe3bae8825808ba54895f405956e6 |
| trust_stress.json | 2499ade1b018c3016ae1c803f747b873844935dd9b187445701c226938bbe0dd |
| resilience.json | 64b65afa3364c63ecaaf0ca3b7b085a458452d8b8cabf9fdefcb64dbc8e37dc8 |

### paper/ render outputs (18 files)

16 of 18 files are byte-identical to the hashes recorded in manifest.json.
Two files differ from the recorded hashes for a deliberate reason:

| File | Status |
|---|---|
| selective_metrics.tex | Re-rendered table header "Routing rate" → "Abstention rate" during manuscript terminology revision; values unchanged. |
| selective_model_comparison.tex | Re-rendered table header "Review (%)" → "Abstain (%)" during manuscript terminology revision; values unchanged. |

All other paper/ files match the manifest hashes exactly; the two table
headers above were updated without changing any numeric value, and the
updated tables are the ones included in the submitted manuscript and
supplementary material.

## Integrity note

- No experiment was re-run to produce this package; the frozen JSON outputs
  used by the manuscript were copied byte-for-byte and their SHA-256 hashes
  preserved.
- Legacy JSON field names (routing_rate, erroneous_auto_pass_rate) are
  retained unchanged; see the compatibility note in REVIEWER_README.md.
- The package contains no production records and no identity-bearing files
  (author name, email, institution, or local paths were excluded).
