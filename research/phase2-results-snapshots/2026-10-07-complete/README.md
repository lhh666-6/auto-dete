# Completed supplementary paired evaluation of deployment A

The separately frozen deployment-A follow-up finished on **7 October 2026 at 17:46:49 Asia/Shanghai**. All 117 selected pairs / 234 planned arms are terminal. Terminal status includes failures.

`quota-recovery-complete.zip` preserves all 117 attempt directories, raw model inputs and responses, event chains, authoritative state databases/snapshots, collection ledger, launch logs, frozen recovery manifest, runner and supporting scripts. Paths begin with `research/`. `SNAPSHOT-MEMBERS.json` inside the ZIP records every included file's SHA-256. The package contains 16,951 verified files. `archive-receipt.json` records the archive checksum, CRC verification, member verification and credential-pattern scan. No authentication store or API credential was selected.

Archive SHA-256: `536f8b7d784d1af118145affd90c3d613b67ad44d9c5b3607b463bcebeacbec1`.

## Relation to the original study

The original 512-arm ledger remains unchanged. The follow-up selected the 117 deployment-A pairs whose original prefixes terminated with quota exhaustion before receiving a model response. It retained the frozen tasks, prompts, tools, policy order, requested deployment configuration and scorer. It is an additional collection block with its own denominator, not a replacement of original outcomes.

The former `2026-10-07T021002Z` snapshot remains an immutable partial snapshot; this complete archive supersedes it for the follow-up's final input coverage.

## Independent analysis and paper

- Analysis code, tests and separately reported outputs: `research/phase2-followup-analysis-2026-10-07/`.
- Integrated manuscript and supplement: `revisions/2026-10-07-kais-followup/`.
- Original frozen runner and scorer: `research/agent-policy-phase2-formal-2026-10-07/`.
- Complete original evidence: the pinned `cloud-handoff/replication-package.zip` at commit `475e66f549613aaaaa62c2ec81ffdee483636c54`.

Extract into a separate directory and follow the analysis package's README. Offline scoring makes no new provider requests. The archive receipt establishes input preservation; the analysis output and final manuscript validation separately establish reported outcomes.
