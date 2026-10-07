# Cloud manuscript continuation

Prepared 2026-10-07 (Asia/Shanghai). The user requests completion of remaining paper optimization and supplements in the cloud, without depending on their local computer. This handoff supports independent offline work immediately. It does not migrate a running local process.

## Entry point and authoritative manuscript

Repository: https://github.com/lhh666-6/auto-dete

Handoff branch: `codex/phase2-formal-512-handoff`. Always select this branch; the repository default branch is not this handoff.

Download `cloud-handoff/replication-package.zip`, verify SHA-256 `1bc17338d18f198811e0e58eca9b64bded29f9b01cd61558862455e7e0d469d8`, and extract into a NEW workspace. The archive contains 16,074 files, with preserved `research/` and `revisions/` paths. Keep its initial extraction as a reference; work on a copy or a new Git branch.

The current paper is `revisions/2026-10-07-kais-continuity/main.tex` (12-page PDF) and `supplement.tex` (21-page PDF), titled **Review-to-Execution Continuity for Corrected Agent State Changes**. The older root manuscript is not the current editing target. Direct PDF previews are also under `cloud-handoff/previews/`.

The latest reconstruction request targets **Knowledge and Information Systems (KAIS)**; earlier conversation discussed JIIS. Read `reconstruction-requirements.txt` for the full author request. Those requirements have already been implemented once; evaluate the actual current manuscript before making further changes. Historical staged logs are superseded by the current README opening and FINAL-COMPLETION-AUDIT.md.

## Evidence boundaries

1. Original formal experiment: 128 tasks × 2 Agents × 2 policies = 512 planned arms, all terminal. Freeze `phase2-formal-v1.0-9fd97d11ceaed652`, master hash `7773563b40c8db30d6def121915f50fbad032537edde32afd4ba39ec3eea744b`. All failures and unknown outcomes remain in the ledger. Agent A encountered 117 quota-exhausted prefixes and reached 11 review checkpoints; B reached 128. This is the primary evidence in the current paper and archive.
2. Later quota recovery is an ADDITIONAL cohort: 117 selected A pairs, 234 planned arms. It is not a replacement for the primary batch. Freeze `phase2-quota-recovery-v1-c41e052eb585`. GitHub snapshot `research/phase2-results-snapshots/2026-10-07T021002Z/` contains only 45 terminal pairs / 90 arms as of 10:10:02 Shanghai. Its status is PARTIAL, and formal inference from this partial recovery is not allowed. Consult its snapshot-summary.json and checksum files. These data are not in replication-package.zip; retrieve them separately from the handoff branch.
3. Local recovery collection was still running when this handoff was prepared. A static GitHub snapshot is not a live feed. Do not claim that all supplementary collection is finished, silently impute pending outcomes, selectively replace primary failures, or report cloud collection as active without executing and verifying it.
4. Pilot data are excluded from formal analysis. Historical 84-chain evidence represents chains, not 84 independent task successes. Preserve separate completion U, integrity I, recovery and friction outcomes; absence of observed substitution is not proof of its impossibility.

## Work to complete autonomously in the cloud

Proceed with offline work now, rather than stopping at a plan:

- Establish a working copy, verify archive/member checksums, read the current main text, supplement, final audits and full reconstruction requirements.
- Reproduce original formal results without API calls. From the extraction root run `python research/agent-policy-phase2-formal-2026-10-07/analyze_formal.py --output fresh-analysis --figures` using the package requirements. Run `verify_evidence.py` in the manuscript directory. Compare all six exported tables and analysis summary semantically with the supplied exports; record discrepancies before editing prose.
- Audit each quantitative claim and figure against raw outputs, and each cited claim against its actual source. Search official journal guidance and primary literature for any additional positioning claims; do not invent references or claim a literature first without support.
- Improve argument structure, prose, figure readability, captions, supplement navigation, reproducibility instructions and submission readiness as the evidence warrants. Preserve the trustworthy Agent execution identity, correction-aware review-to-execution continuity, formal/system contributions, three central findings and four contributions required by the author. Keep claim strength calibrated to observed coverage.
- Analyze the supplementary snapshot descriptively in a separately labeled report. Identify exactly what requires the final recovery cohort; prepare reproducible analysis and manuscript integration points. Any later completed cohort must retain the primary ledger and be reported as an explicitly separate analysis with its sampling/retry rules.
- Compile both edited documents using an available TeX environment, inspect every rendered page and all references/figures, rerun relevant evidence checks and deliver editable sources, main/supplement PDFs, a concise change log and a verification report. Do not claim verification for checks that could not run.
- Save work in a new `codex/` branch or provide downloadable deliverables if GitHub write access is unavailable. The public repository is readable without authentication; read access does not imply push access. Do not submit to a journal.

Deliver the fullest verifiable revised draft from the available evidence. If final recovery data or credentials are missing, finish all independent work and list the precise remaining dependency; do not label that dependency complete.

## Running remaining online experiments is a separate migration

The cloud does not inherit the local computer's login, proxy, API credentials or active process. Turning off the PC stops any collector still running on that PC. Current archived logs remain preserved.

The recovery design uses Agent A's frozen Codex CLI deployment (recorded version 0.160.1, requested gpt-5.6-terra, low reasoning), not the cloud assistant's own model. Do not substitute Dot's model for the experimental Agent. Obtain credentials only through secure cloud secret configuration; never commit them or copy local account stores into this repository.

Before any cloud online continuation, inspect frozen manifests, verify source/task/schema hashes, establish equivalent deployment identity and resource budgets, document necessary environment changes, verify safe resume behavior and prevent duplicate collection with the local run. Preserve old attempts and classify any restart under the specified recovery rules. If this cannot be verified, continue offline manuscript work and report the migration prerequisite. Do not edit frozen runner/scorer files to bypass checks.

## Expected final handback

Provide revised main and supplement PDFs and sources, regenerated figure sources/exports, a claim-to-evidence verification report, reproducibility instructions, a list of any unresolved dependencies, and the exact commit or artifact identifiers. Distinguish completed editorial work, completed offline verification, incomplete supplementary collection and any unverified cloud runtime.
