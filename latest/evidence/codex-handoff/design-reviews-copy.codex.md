# Executable checklist design and implementation plan

Authorization: the user selected the proposed small executable comparison. This document makes that approved scope concrete; no hosted-model calls or changes to prior frozen experiments are required.

## Question and arms

Can a value-approval transaction with a complete value audit identify the exact candidate selected during review, and separate correction of candidate 100 from acceptance of candidate 101 when both commit 101?

One standard-library Python/SQLite demonstrator has two explicitly declared policies, not two claimed industry systems. Both arms preserve immutable candidates, complete version snapshots, principal/value/domain-bound approvals, atomic CAS, and complete before/after value audits. Both reject wrong context, wrong authorized values, stale version, and partial batch submission, and roll back an injected failure. The common baseline is intentionally stronger than the former paper's informal approval-flag example.

- Value-audit arm: approvals identify record, expected version, field domain, and authorized values, but omit which candidate was inspected. Immutable candidates are still retained. Full audit history allows last-change source reconstruction; the comparison must credit this capability.
- Candidate-bound arm: additionally persists the inspected candidate identity with each approval, checks it on submission, and stores exact per-field source references with copy-forward. Proposed values are reconstructed by immutable candidate joins rather than duplicated.

The added arm is an illustrative specialization, not a second production implementation of the complete Auto-Decte contract: no cryptographic evidence verification, enterprise authentication, distributed revocation, race stress, or performance measurement is claimed.

## Cases fixed before execution

1. Legal 100-to-101 correction with unchanged batch.
2. Candidate replacement by a distinct same-record/same-field, equal-valued candidate after approval.
3. Cross-record candidate: common rejection control.
4. Stale expected version after a valid intervening commit: common rejection control.
5. Submitted value differs from approved value: common rejection control.
6. Submitted field set omits one approved field: common rejection control.
7. Injected exception after CAS/persistence but before commit: common rollback control.
8. Two-step evolution with exact source inheritance for the unchanged quantity field: both arms should support reconstruction; the added arm also stores it.
9. Paired histories: review candidate 100 versus candidate 101, both approve/commit 101, with identical candidate pools, values, actor, and version. Compare complete persisted database observations within each arm. Only the reviewed candidate differs in external inputs. Baseline equality demonstrates omitted review linkage, not absence of the candidate values themselves.

Rejections compare pre/post database snapshots taken after approval persistence. Every run writes raw SQL state plus external requested action, database file, and a measured outcome. The external review intent must not be misrepresented as information retained by the baseline.

## Implementation plan

- [ ] Add behavior tests, execute failing tests before implementation.
- [ ] Implement `code/checklist-example/value_audit_demo.py` with shared transaction logic and narrow policy additions.
- [ ] Implement `run_example.py` to execute fixed cases, inspect raw SQLite independently, save records and derive a LaTeX table.
- [ ] Execute tests and controls; inspect paired persisted states and exact-source reconstruction.
- [ ] Document supports and non-claims, replace the hypothetical Supplement S3 example, add a short main-text result without expanding beyond 54 pages if possible.
- [ ] Compile both PDFs, compare protected code/data/formal sources against the 54-page baseline, build and verify a new manifest/ZIP.

No new statistical or novelty-superiority claim will be inferred from deterministic construction counts. Baseline passes, limitations, and supplementary page growth must be reported.
