# Introduction and related-work revision notes

Prepared 26 September 2026. These notes are editorial support and are not part of the submitted manuscript.

## Positioning decisions

- The central contribution is an application-level, correction-aware admission relation and its conditional distinguishability analysis. The article does not claim a new transaction protocol, universal schema minimality, or architectural exclusivity.
- C1 combines the contract and conditional paired-history analysis; C2 concerns relational and transactional enforcement; C3 covers comparative, review-boundary, and cost evidence.
- Exact event-journal/reference parity (165/165 corresponding constructed cases) is stated in the introduction. The stricter policy's 15 additional rejections under the value-level policy are part of the policy choice, not an unqualified security advantage.
- The browser negative control is introduced early: database binding cannot establish what was displayed to or perceived by a human reviewer.
- The figure reference and established labels were preserved. No RQ numbering is introduced in these sections.
- The old generated nearest-neighbor matrix is no longer included by Section 2. It should not remain in the compiled main manuscript through another input path unless independently checked and deliberately reintroduced.

## Primary-source verification

The following sources were inspected online while writing these sections. Claims were paraphrased and kept narrow; none is treated as an experimental comparison conducted by this study.

| Citation key | Primary source checked | Scope supported |
| --- | --- | --- |
| `gray1981transaction` (new) | [Original paper PDF hosted by Stanford](https://web.stanford.edu/class/archive/cs/cs240/cs240.1236/old/sp2014/readings/Gray81.pdf) | Transaction as atomic, durable, consistency-preserving state transformation; author/title/year and pages corroborated by proceedings metadata. The official VLDB PDF URL was unavailable through the browser, so the original-paper mirror is used. |
| `kung1981occ` (new) | [Author-hosted original paper](https://www.eecs.harvard.edu/~htk/publication/1981-tods-kung-robinson.pdf), [CMU database-group bibliography](https://db.cs.cmu.edu/publications/) | Optimistic validation/concurrency control; TODS 6(2), 213–226, 1981; DOI 10.1145/319566.319567. |
| `fowler2005eventsourcing` (new) | [Author's original pattern article](https://martinfowler.com/eaaDev/EventSourcing.html) | Sequence of state-changing events and reconstruction; publication date 12 December 2005. This is a practitioner pattern article, not a peer-reviewed experimental system. |
| `buneman2001whywhere` | [Author-institution original paper repository](https://www.research.ed.ac.uk/files/16509989/Why_and_Where_A_Characterization_of_Data_Provenance.pdf) | Why/where provenance; ICDT 2001, 316–330, DOI 10.1007/3-540-44503-X_20. |
| `cheney2009provenance` | [Author-hosted paper](https://homepages.inf.ed.ac.uk/jcheney/publications/provdbsurvey.pdf), [author-institution publication record](https://www.research.ed.ac.uk/en/publications/provenance-in-databases-why-how-and-where/) | Why/how/where survey and applications. The volume front matter says 2007, while copyright and the university's publication record say 2009; the existing 2009 citation is retained consistent with the latter. |
| `moreau2013provdm` | [W3C Recommendation](https://www.w3.org/TR/2013/REC-prov-dm-20130430/) | Entities, activities, agents, derivation/responsibility, application extensions. The text acknowledges the provenance specification family has constraints; it does not imply PROV is merely unconstrained vocabulary. |
| `arab2018reenactment` | [Authors' research-group publication record](https://www.cs.iit.edu/~dbgroup/bibliography/AG17c.html), [original paper in NSF repository](https://par.nsf.gov/servlets/purl/10048274) | Multi-version transactional provenance and reenactment; TKDE 30(3), 599–612, 2018, DOI 10.1109/TKDE.2017.2769056. |
| `fett2023dpop` | [RFC 9449](https://www.rfc-editor.org/rfc/rfc9449.html) | Proof-of-possession token binding and request method/target URI checks. No claim that DPoP binds an arbitrary payload or establishes human review. |
| `debenedetti2024agentdojo` | [Official NeurIPS 2024 paper](https://proceedings.neurips.cc/paper_files/paper/2024/file/97091a5177d8dc64b1da8bf3e1f6fb54-Paper-Datasets_and_Benchmarks_Track.pdf) | Dynamic tool-agent evaluation over untrusted data, separate utility/security outcomes. No claim our fixtures reproduce AgentDojo. |
| `jackson2002alloy` | [Author-group original paper](https://groups.csail.mit.edu/sdg/pubs/2002/alloy-journal.pdf) | Alloy relational modeling and bounded analysis; TOSEM 11(2), 256–290. |
| `torlak2007kodkod` | [Author-group original paper](https://groups.csail.mit.edu/sdg/pubs/2007/tacas07-torlak-jackson.pdf), [MIT project description](https://publications.csail.mit.edu/abstracts/abstracts07/emina/emina.html) | SAT-based relational model finding and bounded problem domains. |
| `marinov2001testera` | [Author's project/publication page](https://mir.cs.illinois.edu/marinov/mulsaw/), [author-hosted TestEra paper describing abstraction and concretization](https://mir.cs.illinois.edu/marinov/publications/KhurshidMarinov01TestEraINS.pdf) | Established TestEra technique and original ASE 2001 paper identity/pages; no suggestion our selected projections have TestEra's exhaustive input coverage. |

## Closest modern work: follow-up verification

A targeted follow-up checked the five nearest modern references on the original arXiv abstract pages and full HTML version 1. All five URLs resolve to matching titles, authors, and subject matter. Their close relationship is now explicitly acknowledged in the new subsection “Recent governed-memory and activation contracts.” This is a bounded check of the five specified papers, not a comprehensive survey.

| Citation key | Verified full primary source | Finding and implication |
| --- | --- | --- |
| `he2026continuity` | [arXiv:2608.11632v1](https://arxiv.org/html/2608.11632v1) | Sections 2–3 already bind proposal identity, exact predecessor, pre-state authority, evidence, complete accepted state, and lineage across multiple possible storage substrates. This is the closest general activation contract. The revision explicitly relinquishes novelty claims for proposal/authority separation and complete successors in general; its contribution is the narrower correction-aware field relation and its analysis/evidence. |
| `cui2026memtxn` | [arXiv:2607.27834v1](https://arxiv.org/html/2607.27834v1) | Method separates source-support admission, temporal visibility, and saved-active-map recovery. Ordered PatchTest checks value/source token support; this is different from, and potentially complementary to, human authorization of a changed value. No experimental superiority comparison is made. |
| `saidi2026mutmem` | [arXiv:2608.02843v1](https://arxiv.org/html/2608.02843v1) | Sections 4–5 bind authorized retrieval-weight changes to old/new quantized weights, provenance, signing epoch, and predecessor continuity. We distinguish its mutation object and cryptographic assurance, not imply it lacks authorization or provenance. |
| `zhou2026latticemind` | [arXiv:2608.08236v1](https://arxiv.org/html/2608.08236v1) | Method retains explicit claim status, conflict, supersession, and provenance. Its selection/reconciliation function is distinct from the paper's correction admission relation. |
| `he2026stored` | [arXiv:2609.02127v1](https://arxiv.org/html/2609.02127v1) | Introduction “Accepted-state boundary” expressly takes an authenticated accepted head as input; later sections govern projection and assertion release. Cited as complementary downstream work. |

All are identified as **preprints**. The existing bibliography titles/authors/arXiv identifiers match the checked primary records. The former generated matrix is not restored because a compact comparison of stated scopes is more defensible than treating an unreported relation as an absent capability.

## References removed from Sections 1–2

The following 2026 citations from the prior introduction/related-work text were not independently reverified in this rewrite and are not used to support the revised novelty argument: `zhan2026authoritycollapse`, `salas2026governed`, `li2026memtx`, `bhardwaj2026superlocalmemory`, `nakayashiki2026staleconstraints`, `tulshibagwale2026txtokens`, `coetzee2026spttxn`, `xu2026caplease`, `liu2026pce`, `he2026dtf`, `zhu2026ebte`, `chitan2026cappcl`, `delattre2026cage`, `liu2026toolgate`, `choong2026capchain`, `dai2026harnesses`, and `deepseek2026architecture`.

Removal is **not a finding that these references are nonexistent or incorrect**. The revised account makes narrower claims grounded in verified database foundations; it does not claim an exhaustive survey of agent-memory systems. If any of these items remain cited elsewhere, those uses require their own source check. `filtered.bib` was deliberately not modified by this subtask.

Several established testing, software-engineering, and artifact-evaluation citations were also removed from these two sections to shorten the background and avoid venue-driven citation padding. This was a relevance decision, not an adverse finding about those papers. Any citations retained in other sections should be assessed in their own context.

## Integration requirement

Include `editorial/verified-literature.bib` in the main bibliography input, or merge its three entries into the final bibliography. Do not include the same keys twice. The three additions are `gray1981transaction`, `kung1981occ`, and `fowler2005eventsourcing`. Existing citation keys were kept for the verified sources already in `filtered.bib`.
