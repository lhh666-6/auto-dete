# Reference status check — 24 October 2026 (v10)

Scope: `revisions/2026-10-24-ase-intro-v10/references.bib` (41 entries, 40 cited) against the v10
manuscript. Read-only check; no further bibliography change was made for this revision.

Method: arXiv API (`export.arxiv.org`) for version/journal-ref metadata; OpenAlex for work type and
published-record lookup; Crossref for the LogicHunter DOI. DBLP was not reachable (bot-protection
challenge), so DBLP is a stated gap, not a negative result.

## Counts after v10

| Quantity | v9 | v10 |
|---|---|---|
| Bibliography entries | 43 | 41 |
| Cited keys | 42 | 40 |
| arXiv `@misc` preprints | 10 | 8 |
| Preprint share of cited keys | 23.8% | 20.0% |

v10 removes two entries together with their in-text citations: *REVISE* (Qi et al., arXiv
2609.00643) and *Resume Means Resume* (Khan, arXiv 2608.03836). Neither is cited anywhere else in
the manuscript, and neither has a peer-reviewed version (arXiv metadata has no journal-ref;
OpenAlex returns type `preprint`; Crossref title search finds no matching published item). The
removal is therefore editorial: REVISE is an online-revision recovery planner, and resume
semantics are already covered by the framework documentation and the published framework-testing
study cited. It is not a version-driven substitution.

## Remaining preprints

| Key | Role in the paper | arXiv | Latest | Peer-reviewed version found |
|---|---|---|---|---|
| `zhu2026resa` (ReSA) | reconstruction-aware authorization (closest work) | 2609.26529 | v1 | none found |
| `bindschaedler2026guarded` (Guarded Commits) | commit-time approval/policy (closest work) | 2610.00037 | v1 | none found |
| `kumar2026loopjacking` (Loopjacking) | post-approval substitution (closest work) | 2609.21081 | v1 | none found |
| `wang2026approval` (Approval Laundering) | approval-execution binding failures (closest work) | 2609.38983 | v1 | none found |
| `wang2026acg` (ACG) | versioned authorization repair | 2609.32428 | v1 | none found |
| `cordon` (Cordon) | semantic transactions for tool-using agents | 2606.17573 | v1 | none found |
| `continuity-kernel` (CK) | transactional continuity kernel | 2608.11632 | v1 | none found |
| `commit-time-auth` | commit-time authorization | 2607.10487 | v1 | none found |
| `logicunter` | agent-framework fuzzing | 2607.06195 | v1 | **Proc. ACM Softw. Eng. 3(ISSTA), 1171-1193, 2026; DOI 10.1145/3832142 verified** |

## Assessment

1. The four closest works remain preprints and are cited as such; the paper states "We use their
   archived version-1 preprints, as for ReSA." All four currently have only version 1.
2. The manuscript no longer front-loads six works in the introduction: the research-gap paragraph
   names the four closest (ReSA, Guarded Commits, Loopjacking, Approval Laundering); ACG and the
   transactional mechanisms are discussed in Related Work as comparison points.
3. Preprints still do not carry the argumentative load: the contract and validation rest on
   peer-reviewed foundations plus the paper's own 165-case, 72-route and 504/54/16-cell evidence.
4. LogicHunter's formal version is verified; the entry already cites the proceedings and DOI.

## Recommendation

No further bibliography change for submission. Re-run if submission is delayed by several weeks,
since the four closest preprints are actively under review. DBLP remains unchecked in this
environment.
