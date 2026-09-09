# r27 shared revision — 2026-09-09

第一作者：梁航豪（Liang Hanghao）。第二作者：宣文涛（xuanwentao）。
本次 r27 修订由梁航豪与宣文涛共同完成。
This r27 revision was jointly revised by Liang Hanghao and xuanwentao.

Author order is confirmed by the first author. Corresponding-author details and CRediT declarations remain subject to final submission approval.

The complete candidate is in [r27-jss/](r27-jss/). Start with [the manuscript](r27-jss/current/paper/main.pdf) and [supplement](r27-jss/current/paper/supplement.pdf). Edit current/ and retain baseline-v8/ unchanged. Preserve initial independent annotation labels before consulting old labels or aggregate results.

The paper, code and evidence are byte-identical to the verified local r27 package. Publication fixes verify_release.py to include two historical cache files already listed in the manifest, and updates its manifest hash. Internal local/unpublished labels record the packaging status before this GitHub publication; this notice records the subsequent publication. The PDF author block is preserved from the verified candidate and must be aligned with the confirmed author order during final submission preparation.

Main: 57 pages; supplement: 12 pages; 54 citations; 19 witness tests passed. Two non-author human annotators independently coded the 360 benign completion runs: inter-human agreement 99.72% (κ=0.974, AC1=0.997, PABAK=0.996); human--rule agreement 96.72% on the 335 behavior-evaluable runs; after author adjudication of 12 items the adjudicated labels match the strict rule (320/335). Full confusion matrices, disagreement lists, and cluster-robust intervals are in `r27-jss/current/evidence/human-annotation-2026-09-10/`. Implementation and tests are unchanged from r26; the 389-test result is inherited from its isolated verification, not a new full-suite run.

Run `python verify_release.py` inside r27-jss/ to verify 20,240 files. Clone with Git LFS and run `git lfs pull` before verifying, because the historical baseline contains large files. GitHub-generated source ZIPs may contain LFS pointers instead of the underlying data.

Original local ZIP SHA-256: `df4437098ec52f56f27f5a18600cdd23896404c97258f4e44ed2caaecc0978ab`. This hash does not apply to GitHub-generated archives.

Pinned tag: `r27-jss-2026-09-09`. Independent annotation results are recorded in this candidate (two non-author annotators; author adjudication disclosed); final submission approvals remain pending. This is a shared submission candidate, not a claim of journal acceptance or completed submission.
