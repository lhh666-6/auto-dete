Auto-Decte — Reviewer artifact (FINAL)
======================================

Source code snapshot, frozen experiment outputs, and reproduction commands for
the submitted manuscript (Expert Systems with Applications).

Provenance
----------
The executable source snapshot is pinned to commit `68f7b93`.

The authority-integration benchmark under `artifacts/pipeline_authority_68f7b93e3ff3/`
was reproduced from that clean snapshot and is byte-identical across repeated runs.

The manuscript-level recognition, whole-form, workflow, ablation, stress, and
resilience artifacts under `artifacts/` are the frozen outputs used to generate
the reported tables and figures and originate from the recorded ESWA evaluation
run associated with commit `195355a`.

Contents
  source_snapshot_68f7b93/   executable source snapshot at 68f7b93
                             (application, benchmarks, tests, config, docs)
  artifacts/
    pipeline_authority_68f7b93e3ff3/
                             authority-integration benchmark output
                             (manifest.json + pipeline_authority.json)
    *.json                   frozen manuscript-level outputs (recognition,
                             whole-form, workflow, trust ablation and stress,
                             resilience, manifest with SHA-256 hashes)
    paper/                   rendered tables and figures for the manuscript
  paper/final_explanatory_figures/
                             final explanatory workflow diagrams
                             (manuscript Figures 1-3; AI-assisted design,
                             author-verified; not benchmark outputs)
  reproduction/commands.txt  exact reproduction commands
  SOURCE_PROVENANCE.md       detailed provenance and file hashes

Verify the included 68f7b93 source snapshot
--------------------------------------------
uv sync --extra dev --extra research
uv run pytest -q            (239 tests in the verified integrated state)
uv run ruff check .
uv run mypy

Re-run the authority-integration benchmark
------------------------------------------
uv run python -m benchmarks.pipeline_authority_benchmark --output <dir> \
    --now 2026-08-17T12:00:00+00:00 --seed 20260817 --cases 12
    (byte-identical reruns; payload sha256
     1677cbb526e786b754e8bdb4d6e983df26f88b59b47ec0dd2733c943ad87c4ed)

Manuscript-level frozen outputs
-------------------------------
The exact frozen outputs used by the manuscript are supplied under artifacts/.
They originate from the recorded ESWA run at 195355a.
The included 68f7b93 snapshot is not claimed to reproduce those files byte-for-byte.

## Explanatory Figures

Figures 1–3 in the submitted manuscript are explanatory architecture and workflow diagrams rather than experimental outputs.

OpenAI ChatGPT (GPT-5.6 Sol) was used to assist with the design and visual refinement of these diagrams. All scientific content, terminology, labels, process relationships, and final figure selections were reviewed and verified by the author.

These explanatory figures are not claimed to be generated from the frozen benchmark code.

Quantitative plots and tables remain programmatically generated from the frozen experimental artifacts.

Final explanatory figures are provided under:

paper/final_explanatory_figures/

Legacy artifact field names
---------------------------
- routing_rate corresponds to the manuscript's abstention rate.
- erroneous_auto_pass_rate corresponds to the manuscript's erroneous acceptance rate.
The frozen JSON keys were retained unchanged to preserve artifact hashes.

Notes
-----
- Test counts are software verification information, not scientific sample sizes.
- All data are deterministic synthetic; no production records are included.
- Internal design and process documents are intentionally excluded.
