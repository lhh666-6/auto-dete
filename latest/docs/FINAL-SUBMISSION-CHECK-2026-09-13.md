# Final submission check — 13 September 2026

## Decision and scope

The technical package is prepared for a versioned submission freeze after prose compression. This is not a claim of acceptance, independent replication, universal scientific validity, or completed journal submission. The current main manuscript is 60 single-column preprint pages including references; the separate supplement is 20 pages. The September 12 candidate and earlier dated reports are historical; this report supersedes their page counts and verification status.

## Completed checks

| Check | Observed result |
|---|---|
| Lock-pinned Python environment | Fresh environment from unchanged uv.lock; Python 3.11.9, SQLAlchemy 2.0.51, NumPy 1.26.4 |
| Implementation suite | 389 passed; approximately 403 seconds in this run |
| Alloy re-execution | 72 commands matched; not only archived-output verification |
| Formal/concrete regeneration | 29 cases: 9 SAT, 20 UNSAT |
| Fault catalogue | 35/35 passed, zero failures |
| Witness tests | 19 passed |
| Checklist control / strengthened control | 27 / 9 passed |
| Annotation/manifest integration tests | 7 passed |
| Frozen RQ8 claims | 23/23 recomputed exactly |
| Endpoint sensitivity rerun | Strict 320; endpoint 331; zero strict-success/endpoint-failure cases; strict verdicts match frozen records |
| Main / supplement compilation | 60 / 20 pages; no Warning, undefined reference, overfull or underfull diagnostic |
| References | 54 cited keys, no missing or unused key; all 54 work identities/locators supported after title/subtitle follow-up |
| Highlights | Five bullets, each within 85 characters |
| Git LFS local integrity | fsck passed; materialized objects available |
| Full-manifest validator | Correct content, altered content, missing file, LFS pointer and path-escape cases checked |

Evidence logs and machine-readable metrics are in `../evidence/r30-final-verification/`. Re-execution outputs remain in the local final-check workspace; the deposited summaries identify those runs. Fresh timing and hosted-output reproduction were not attempted. The final prose-only pass preserves protected implementation, model, figure, table, bibliography and original evidence hashes. [Compression details](COMPRESSION-2026-09-13.md) record the 62-to-60-page reduction.

Bibliography verification checked work identity and locator metadata, not every cited claim against full text. Crossref split three main titles from subtitles; follow-up confirmed them. The pinned DeepSeek architecture and IETF draft were checked at their primary pages. Paperpile library synchronization was unavailable and is not certified. Current official JSS Guide for Authors retrieval was blocked, so this report does not certify every current formatting requirement.

## Authorship and measurement integrity

Liang Hanghao is first author; Xuan Wentao is second author; Peng Peng is the sole corresponding author (hnu16pp@hnu.edu.cn). The byline, CRediT and contact materials agree. Peng's roles are Supervision and Writing–review & editing. The public Hunan University profile and linked personal page support his affiliation and contact details. No ORCID or additional email has been invented.

The original 325 acknowledgment labels remain unchanged: human–rule agreement is 286/325 and kappa 0.644171. All 39 disagreements remain without human adjudication. The separate unblinded AI review proposes 5 rule errors, 33 human errors and 1 ambiguous case under its stated interpretation; these are review proposals, not validated replacement labels. A3 ambiguity and author involvement remain explicit. The eleven-case strict-trajectory review is no longer phrased as verification of all 335 cases. The ethics statement attributes the no-approval assessment to the authors, without claiming a verified institutional exemption. AI assistance remains disclosed.

## Journal and repository readiness

The JSS scope includes software engineering for AI systems, but scope fit does not resolve editorial novelty or length judgments. A project audit of the official guide on 25 August recorded single-anonymized review and encouraged fewer than 36 single-column pages; an older guide mirror also requires a reason for longer papers. The final 60-page paper remains a material editorial risk. Its cover letter explains the length; it does not assert permission for it. The submission portal's current guide must be checked before submission.

The root README identifies `latest/` as the current manuscript; legacy roots and v8 results are explicitly historical. The complete repository contains the original records; `latest/` alone is not the full raw-data package. The root reviewer guide documents clone/LFS retrieval, lock-pinned installation, deterministic checks, external harness requirements, and paid-provider boundaries. Two manifests cover the current package and the full materialized tracked tree. The full reviewer ZIP includes materialized LFS files; GitHub-generated source ZIPs may contain pointers. No unconfirmed open-source license or JSS Open Science certification is claimed.

## Remaining submission actions

The authors must confirm approval of this final manuscript, originality/concurrent-submission status, article type, current journal instructions, funding/conflicts/ethics accuracy, and the corresponding author's mailing details. These are personal/institutional facts, not facts established by a freeze. Cover letter, highlights, CRediT and a Chinese portal checklist are supplied. The paper is ready for those submission steps, subject to the current journal's requirements and editorial assessment. No model attacks, new dataset, additional annotator or unrequested experiment was added during closeout.

## Sources consulted

- JSS official scope: https://shop.elsevier.com/journals/journal-of-systems-and-software/0164-1212
- Official guide endpoint (access blocked during this check): https://www.sciencedirect.com/journal/journal-of-systems-and-software/publish/guide-for-authors
- Older guide mirror, used only as historical context: https://www.readkong.com/page/journal-of-systems-and-software-elsevier-8555648
- Hunan University profile: https://csee.hnu.edu.cn/people/pengpeng
- Linked personal page: https://bnu05pp.github.io/
- CRediT role definitions: https://credit.niso.org/contributor-roles-defined/
