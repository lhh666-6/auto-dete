# Current shared manuscript: r27

**第一作者：梁航豪；第二作者：宣文涛（xuanwentao）。本次修订由两位作者共同完成。**

This revision was jointly revised by Liang Hanghao and xuanwentao.

- [Main manuscript — 58 pages](r27-jss/current/paper/main.pdf)
- [Supplement — 14 pages](r27-jss/current/paper/supplement.pdf)
- [Complete r27 candidate, source and frozen baseline](r27-jss/)
- [Joint revision credit, verification and publication status](R27-COLLABORATION.md)

Pinned version: `r27-jss-2026-09-10-b`. The r27 candidate adds a conditional positive Alloy trace-completeness assertion and mutation control under `r27-jss/current/evidence/r27-trace-mutation/`, a minimal ordinary approval/audit-log baseline under `r27-jss/current/evidence/r27-standard-practice-baseline/`, per-model missingness and cluster-robust interval tables, and published per-run annotation labels with a standard-library recomputation script under `r27-jss/current/evidence/human-annotation-2026-09-10/`. Use Git LFS when cloning the complete package. Earlier descriptions below are historical.

---

# Auto-Decte reproducibility artifacts

## Current JSS R21 package

The current reproducibility package for *Authoritative-State Admission for
AI-Derived Updates: Failure Distinguishability, Transactional Realization, and
Evaluation* is available in [`r21-jss/`](r21-jss/README.md).

It contains the manuscript source and PDF, complete clean source code, Alloy
models, transactional and conformance tests, frozen correctness/performance
evidence, all 1,260 planned final live-agent run records, normalized paper
inputs, and SHA-256 integrity manifests.

Author: Liang Hanghao, College of Computer Science and Electronic Engineering,
Hunan University. Correspondence: zwu691403@gmail.com.

## Earlier ESWA reviewer artifact

Anonymous public release of the executable artifacts for the manuscript
"Auto-Decte: Trust-Constrained Document Intelligence through Candidate--Fact
Separation and Certificate-Bound Human Authorization" (under review).

This repository contains the source snapshot, frozen experiment outputs, and
reproduction commands. It is released anonymously for review; author and
repository provenance will be restored after acceptance.

### ESWA reviewer artifact

The repository contains the frozen evaluation artifacts used in the ESWA submission, together with the final explanatory workflow diagrams.

Figures 1–3 are explanatory diagrams whose visual design was assisted by OpenAI ChatGPT (GPT-5.6 Sol) and subsequently reviewed and verified by the author.

Experimental data, quantitative plots, manifests, hashes, and benchmark outputs remain frozen and unchanged.

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
