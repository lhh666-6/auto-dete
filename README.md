# Auto-Decte — manuscript handoff

**第一作者：梁航豪；第二作者：宣文韬（xuanwentao）。本次修订由两位作者共同完成。**

## Current submission candidate — `latest/`

Target venue: Journal of Systems and Software. The integrated current manuscript, supplement, repaired source, and evidence are under [`latest/`](latest/).

- [Main manuscript (62 pages)](latest/paper/main.pdf)
- [Supplement (19 pages)](latest/paper/supplement.pdf)
- [Package notes, reproduction commands, and verification summary](latest/README.md)
- [Complete integrated package](latest/)

Verify the package against its manifest with `cd latest && python verify_latest.py`.

## Earlier r28 handoff — `r27-jss/`

- [Main manuscript (58 pages)](r27-jss/current/paper/main.pdf)
- [Supplement (15 pages)](r27-jss/current/paper/supplement.pdf)
- [Second-author handoff and remaining decisions](r27-jss/SECOND-AUTHOR-HANDOFF-zh.md)
- [Joint revision statement](R27-COLLABORATION.md)
- [Complete package](r27-jss/)

`r27-jss/` is the earlier r28 handoff, with `r27-jss/baseline-v8/` as the unchanged v8 export; `r27-jss/verify_release.py` checks that sealed tree. Earlier tagged versions remain historical. Use Git LFS for the complete baseline. This public package supports continued author review; it is not a claim of submission or acceptance.
