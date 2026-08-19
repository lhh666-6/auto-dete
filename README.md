# Auto-Decte — Trust-Constrained Document Intelligence

Anonymous public release of the executable artifacts for the manuscript
"Auto-Decte: Trust-Constrained Document Intelligence through Candidate--Fact
Separation and Certificate-Bound Human Authorization" (under review).

This repository contains the source snapshot, frozen experiment outputs, and
reproduction commands. It is released anonymously for review; author and
repository provenance will be restored after acceptance.

## Contents

- `source_snapshot_68f7b93/` — executable source snapshot (application,
  benchmarks, tests, config, docs) pinned to commit `68f7b93`.
- `artifacts/` — frozen experiment outputs:
  - `pipeline_authority_68f7b93e3ff3/` — authority-integration benchmark
    output, byte-identical across repeated runs (payload SHA-256
    `1677cbb526e786b754e8bdb4d6e983df26f88b59b47ec0dd2733c943ad87c4ed`);
  - `recognition_*\form_*\trust_*\resilience.json` and `paper/` — the
    27 frozen outputs of the recorded ESWA evaluation run (commit `195355a`)
    used to generate the reported tables and figures.
- `paper/final_explanatory_figures/` — final explanatory workflow diagrams
  (manuscript Figures 1–3); AI-assisted design, author-verified; distinct
  from the quantitative renders under `artifacts/paper/`.
- `reproduction/commands.txt` — exact reproduction commands.
- `REVIEWER_README.md` — provenance and reproduction guide.
- `SOURCE_PROVENANCE.md` — detailed provenance and file hashes.

## Data boundary

All data are deterministic synthetic. No production records, employee
identities, or real deployment data are included. The integrated software
verification suite passes 239 automated tests; test counts are software
verification information, not scientific sample sizes.

## License

Released for review purposes; all rights retained by the authors.
