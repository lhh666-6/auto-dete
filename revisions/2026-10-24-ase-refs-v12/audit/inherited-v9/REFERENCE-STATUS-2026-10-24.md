# Reference status check — 24 October 2026

Scope: `revisions/2026-10-24-ase-polish-v9/references.bib` (43 entries, 42 cited) against the
v9 manuscript. Read-only check; no bibliography or manuscript change was made.

Method: arXiv API (`export.arxiv.org`) for version/journal-ref metadata; OpenAlex for work type
and published-record lookup; Crossref for the one conference DOI. DBLP was not reachable
(bot-protection challenge), so DBLP is a stated gap, not a negative result.

## Counts

| Quantity | Value |
|---|---|
| Bibliography entries | 43 |
| Cited keys | 42 |
| arXiv `@misc` preprints | 10 |
| Preprint share of cited keys | 23.8% |

The manuscript's own wording is precise: "We use their archived version-1 preprints, as for
ReSA." The four entries whose URL has no `v1` suffix (ReSA, Guarded Commits, Loopjacking,
Approval Laundering) currently have only a version 1 on arXiv, so the claim holds. *Resume Means
Resume* is explicitly labelled version 3 in the entry and is not covered by the version-1 claim.

## Item-by-item status

| Key | What it is used for | arXiv | Latest | Peer-reviewed version found |
|---|---|---|---|---|
| `zhu2026resa` (ReSA) | reconstruction-aware authorization analysis | 2609.26529 | v1 | none found |
| `bindschaedler2026guarded` (Guarded Commits) | commit-time approval/policy validation | 2610.00037 | v1 | none found |
| `kumar2026loopjacking` (Loopjacking) | post-approval state substitution in released products | 2609.21081 | v1 | none found |
| `wang2026approval` (Approval Laundering) | approved-action vs dispatched-action divergence | 2609.38983 | v1 | none found |
| `wang2026acg` (ACG) | versioned authorization repair | 2609.32428 | v1 | none found |
| `qi2026revise` (REVISE) | validity-guided recovery in workflows | 2609.00643 | v1 | none found |
| `cordon` (Cordon) | semantic transactions for tool-using agents | 2606.17573 | v1 | none found |
| `continuity-kernel` (CK) | transactional continuity kernel | 2608.11632 | v1 | none found |
| `commit-time-auth` | commit-time authorization | 2607.10487 | v1 | none found |
| `resume-means-resume` | checkpoint/interrupt/resume contract | 2608.03836 | v3 | none found (Zenodo artifact only) |
| `logicunter` | agent-framework fuzzing | 2607.06195 | v1 | **Proc. ACM Softw. Eng. 3(ISSTA), 1171–1193, 2026; DOI 10.1145/3832142 verified** |

arXiv metadata for all ten preprints contains no `journal_ref`; OpenAlex returns type
`preprint` for each and no separate published record; Crossref title search produced no matching
published item. All ten therefore remain preprints as of 24 October 2026.

## Assessment against the three concerns

1. **Directly competing work is mostly preprint.** Five preprints are in the direct comparison
   set (ReSA, Guarded Commits, Loopjacking, Approval Laundering, ACG). This is unavoidable for a
   mid-2026 topic. The paper already states that these are cited as archived preprints and
   derives differences from their *content*, not from an assumed peer-reviewed consensus.
2. **Do preprints carry the argumentative load?** No. The contract and validation rest on
   peer-reviewed foundations (transactions, provenance, access control, runtime verification,
   formal modelling) plus the paper's own 165-case, 72-route, 504/54/16-cell evidence. Preprints
   support positioning and the closest-work comparison only.
3. **Version accuracy.** Verified: no newer or formally published version exists for the ten
   preprints; the version-1 wording is accurate; Resume's version 3 is labelled.

## Recommendation

- Do not reduce or rewrite the bibliography. Removing the closest preprint comparisons would
  create a larger novelty risk than citing them.
- No bib edit is required for submission. Optional cosmetic improvement (only if another
  revision is made): add `volume = {3}`, `number = {ISSTA}`, `pages = {1171--1193}` to
  `logicunter`, whose DOI and venue are already correct.
- Re-run this check if submission is delayed by more than a few weeks, since several of these
  preprints are actively under review.
- Limitation: DBLP could not be queried in this environment; if DBLP coverage matters, check the
  five direct competitors there before submission.
