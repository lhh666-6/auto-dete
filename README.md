# Auto-Decte — frozen JSS submission version

**第一作者：梁航豪（Liang Hanghao）；第二作者：宣文韬（Xuan Wentao）；唯一通讯作者：彭鹏（Peng Peng）。**

Frozen tag: [`r30-jss-2026-09-13`](https://github.com/lhh666-6/auto-dete/tree/r30-jss-2026-09-13). This is the authors' final prepared submission version, not a claim that the journal has received or accepted the paper. Subsequent corrections require a new tag; do not move this tag.

- [Main manuscript](latest/paper/main.pdf) and [supplement](latest/paper/supplement.pdf)
- [Editable manuscript sources and submission files](latest/paper/)
- [CRediT statement](latest/paper/credit-author-statement.txt)
- [Reviewer reproduction guide](REVIEWER_GUIDE.md)
- [Final verification report](latest/docs/FINAL-SUBMISSION-CHECK-2026-09-13.md)
- [Current package](latest/) and [whole-repository freeze manifest](FREEZE-MANIFEST-r30.json)

Clone this tag with Git LFS to obtain the materialized historical raw artifacts. Verify the whole checkout with `python -B verify_freeze.py`, and the current package with `python -B latest/verify_latest.py`. GitHub's automatic source ZIP may contain LFS pointer files; those are not the corresponding data files. The verifier detects them.

## Evidence boundaries

`latest/` contains the final paper, supplement, repaired implementation, formal models, witnesses and derived analyses. `r21-jss/` retains the historical v8 baseline and hosted-run raw records needed for full provenance inspection. The current-only ZIP is not a substitute for the complete repository when checking those raw records. The repository contains both layers.

No original model events, manual labels, or frozen performance measurements were changed in the closeout. The 39 acknowledgment discrepancies have separately archived AI review proposals; they have not become human adjudications.

Re-executing hosted-model calls requires the authors' specified providers and the reviewer's own credentials and will not guarantee identical model outputs. RQ7 requires an external pinned DeepSeek Harness host. Timing results depend on hardware. See the reviewer guide for the exact scope of reproducibility.

## Historical material

- `r27-jss/`: earlier r28 handoff, retained with its own manifests.
- `paper/`, `artifacts/`, `source_snapshot_68f7b93/`, `REVIEWER_README.md`, and `SOURCE_PROVENANCE.md`: historical ESWA-era material, not the current JSS paper.
- [September 11 reproduction report](reproduction/REPRODUCIBILITY-VERIFICATION-2026-09-11.md): historical verification, superseded for current checks by the final report above.

Public availability does not imply an OSI open-source license for all contents. Third-party notices remain with the bundled tools; consult the authors for reuse beyond evaluation. No third-party license is replaced by this README.
