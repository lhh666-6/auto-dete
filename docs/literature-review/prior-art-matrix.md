# Stage 3 - Prior-art comparison matrix

This is an internal analytical matrix, not a manuscript novelty scoreboard. E = explicit; P = partial; N = not assessed. N never means a system cannot implement the relation. Explicit cells apply in the cited system's own domain and granularity.

Reverse authorization means tracing a committed field back to proposal, reviewer, authorized value and source. The synthesis corrects earlier forward-impact wording in the provenance audit.

| Work | Proposal | Exact ID | Review | xc/xa | Human | Fresh | Atomic | Unchanged source | Total sources | Reverse query | Same-value |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Mershad2015 | E | E | E | P | E | N | N | N | P | P | P |
| Mershad2018AUDIT | P | N | N | N | P | N | N | N | P | N | N |
| Eltabakh2007bdbms | P | P | P | P | E | N | N | P | P | P | N |
| ClarkWilson1987 | N | P | P | P | E | P | P | N | N | P | N |
| KungRobinson1981 | P | P | N | N | N | E | P | N | N | N | N |
| BunemanChapmanCheney2006 | N | E | N | N | P | N | P | E | E | P | P |
| Arab2018 | N | E | N | N | P | P | P | P | P | P | P |
| PROVDM2013 | P | E | P | P | P | N | N | P | P | P | P |
| Fowler2005 | P | P | N | P | N | N | N | P | P | P | N |
| gdr2011 | P | P | P | P | E | P | N | N | N | N | N |
| falcon2016 | P | P | P | N | E | P | N | N | N | N | P |
| wrangler2011 | P | P | P | P | E | N | N | N | P | P | N |
| katara2015 | P | P | P | N | E | N | N | N | P | N | N |
| nadeef2013 | P | P | N | N | P | P | P | N | P | P | N |
| holoclean2017 | P | P | N | N | N | N | N | P | P | N | N |
| dbwiki2011 | N | P | N | N | E | P | P | P | P | P | P |
| 2608.11632 | E | E | P | P | P | E | E | P | P | P | P |
| 2607.27834 | P | P | N | P | N | P | P | P | P | P | N |
| 2608.02843 | P | E | P | P | P | E | P | P | P | P | P |
| 2608.08236 | E | P | P | P | N | N | N | P | P | P | P |
| 2609.02127 | P | E | P | P | P | P | P | P | P | P | P |
| 2609.01235 | P | E | P | P | P | P | P | P | P | P | P |
| 2607.23929 | E | P | P | P | P | P | P | N | P | P | N |
| fett2023dpop | N | N | N | N | N | N | N | N | N | N | N |
| backman2024httpsignatures | N | N | N | N | N | N | N | N | N | N | N |
| owasp2026transactionauthorization | N | N | N | N | N | N | N | N | N | N | N |
| jackson2002alloy | N | N | N | N | N | N | N | N | N | N | N |
| torlak2007kodkod | N | N | N | N | N | N | N | N | N | N | N |
| marinov2001testera | N | N | N | N | N | N | N | N | N | N | N |
| buneman2001whywhere | N | N | N | N | N | N | N | N | N | P | N |
| cheney2009provenance | N | N | N | N | N | N | N | N | N | P | N |
| gray1981transaction | N | N | N | N | N | N | P | N | N | N | N |
| US20200117643A1 | P | P | P | P | P | P | P | P | P | P | N |

## Closest-work interpretation

- UPA 2015 explicitly approves selected persisted cell versions. Exact-version human approval is prior art.
- Guided Data Repair allows a user-supplied replacement value; Falcon explicitly distinguishes identical current effects from valid rule semantics. Correction and equal-result semantic distinctions are prior art.
- Curated-database provenance already preserves unchanged predecessor sources. DBWiki already provides fine-grained identities, version history, provenance and atomic edit operations.
- Continuity Kernel already combines exact proposal identity, pre-state authority, freshness and an atomic complete accepted unit. Its signed approver evidence and human preparation must be acknowledged. Read it together with Stored Is Not Supported rather than claiming gaps artificially from either paper alone.
- The defensible contribution is this specified field-level Correction admission relation, its conditional failure-distinguishability characterization, and controlled executable comparisons. The audit does not prove that no earlier design can encode or instantiate it.
- AUDIT 2018 methods and some workflow constraint leads remain unread. Their cells do not support negative capability claims; the manuscript uses the fully read 2015 implementation for its grounded comparison.

## Mershad2015

[Approving Updates in Collaborative Databases](https://www.cs.purdue.edu/homes/aref/papers/ic2e2015.pdf)

| Dimension | Assessment | Evidence boundary |
|---|---|---|
| persisted_proposal | explicit | Pending cell values and metadata persist in the History table before PI approval. |
| exact_identity | explicit | Cell ID plus timestamp selects a stored historical record (III-A; IV-A/B). |
| candidate_bound_review | explicit | PI queries history and supplies selected record timestamps to ScHistory (IV-B). Explicit logical version selection; an immutable security grant or comprehensive TOCTOU defense is not inferred. |
| proposal_authorized_separation | partial | Pending versus approved values/statuses and last-inserted versus last-approved views are explicit. Retaining xc and corrected xa as two values bound to one AI candidate is not established. |
| human_authority | explicit | A privileged principal investigator approves/rejects on data content (III-B; IV-B). |
| fresh_predecessor | not-assessed | The read approval implementation does not establish a document-head comparison at acceptance. No assertion of absence elsewhere. |
| atomic_complete_successor | not-assessed | Individual/bulk approval and HBase modes are described; atomic construction of a complete document successor with all its witnesses is not established. |
| unchanged_exact_source | not-assessed | Cell-history retention does not itself establish a mandatory exact carryforward source for each unchanged document field. |
| total_field_provenance | partial | Per-cell histories track each operation and metadata within the system; a total successor-field source relation is not stated. |
| reverse_query | partial | History queries return persisted cell versions, operator and approval metadata; the full field-to-original-proposal/reviewer/xa/source tuple was not established. (Sections III-A/B and IV-A/B; PDF pp. 3–4, published pp. 44–45.) |
| equal_value_substitution | partial | Different timestamps identify different history records even if values coincide (inference from the identifier scheme). A dedicated equal-valued substitution adversary or rejection rule is not evaluated. |

## Mershad2018AUDIT

[AUDIT: approving and tracking updates with dependencies in collaborative databases](https://doi.org/10.1007/s10619-017-7208-y)

| Dimension | Assessment | Evidence boundary |
|---|---|---|
| persisted_proposal | partial | Abstract concerns updated data pending approval; persistence implementation not assessed. |
| exact_identity | not-assessed | Full method unavailable; cannot infer version identity from the title or predecessor article. |
| candidate_bound_review | not-assessed | Full method unavailable; cannot infer candidate-level review binding. |
| proposal_authorized_separation | not-assessed | Full method unavailable; no xc/xa correction comparison. |
| human_authority | partial | Content approval is abstract-level scope; exact authorization mechanism not assessed. |
| fresh_predecessor | not-assessed | Full method unavailable; no concurrency comparison. |
| atomic_complete_successor | not-assessed | Full method unavailable; no atomic successor comparison. |
| unchanged_exact_source | not-assessed | Full method unavailable; no carryforward-source comparison. |
| total_field_provenance | partial | Dependency tracking is abstract-level scope; total field coverage not assessed. |
| reverse_query | not-assessed | Relevant query method unavailable; no reverse authorization capability inferred. (Abstract and bibliographic record only.) |
| equal_value_substitution | not-assessed | Full method unavailable; no equal-value threat comparison. |

## Eltabakh2007bdbms

[bdbms—A Database Management System for Biological Data](https://www.cs.purdue.edu/bdbms/publications/bdbms-system.pdf)

| Dimension | Assessment | Evidence boundary |
|---|---|---|
| persisted_proposal | partial | Logs preserve updates while custodians decide; independent pre-application machine proposals are not the described abstraction. |
| exact_identity | partial | Log entries identify update operations and metadata; a unique persisted candidate-instance binding contract is not established in Section 6. |
| candidate_bound_review | partial | Custodians inspect logged operations and approve/disapprove their content. Version-specific immutable approval semantics require further evidence. |
| proposal_authorized_separation | partial | Pending/permanent approval and old values via inverses distinguish states, but xc/xa for one corrected candidate is not established. |
| human_authority | explicit | APPROVED BY specifies user/group; custodians make approval decisions, alongside GRANT/REVOKE. |
| fresh_predecessor | not-assessed | No document-head freshness obligation was established in the read method. |
| atomic_complete_successor | not-assessed | No complete document snapshot and evidence co-commit contract was established in the read method. |
| unchanged_exact_source | partial | Inverse statements retain old values for reversal; this is not yet an exact carryforward witness for each unchanged successor field. |
| total_field_provenance | partial | Annotations/dependencies are database capabilities; the read approval method does not impose a total per-successor-field authority/source relation. |
| reverse_query | partial | Logged updates and inverse operations support backward inspection; the complete reverse authorization tuple was not established. (Section 6, PDF p. 9 (zero-based web page index 8); no proceedings-page range independently verified.) |
| equal_value_substitution | not-assessed | The read method does not assess equal-valued candidate substitution; no absence claim is made. |

## ClarkWilson1987

[A Comparison of Commercial and Military Computer Security Policies](https://groups.csail.mit.edu/ana/Publications/PubPDFs/A%20Comparison%20of%20Commercial%20and%20Military%20Computer%20Security%20Policies.pdf)

| Dimension | Assessment | Evidence boundary |
|---|---|---|
| persisted_proposal | not-assessed | UDI inputs are modeled, but durable AI proposal artifacts awaiting human review are not established. |
| exact_identity | partial | Named CDIs, TPs and user authorization relations identify protected objects/actions; exact candidate-instance identity is not specified. |
| candidate_bound_review | partial | Certification/authorization govern permitted transformations. Human review of an individual persisted value requires an additional policy instantiation. |
| proposal_authorized_separation | partial | Unconstrained versus constrained data is explicit; a corrected AI proposal retaining xc and xa is not implied by that classification. |
| human_authority | explicit | E2 legal user/TP/CDI relations, E3 authentication and E4 certifier/executor separation constrain authority. |
| fresh_predecessor | partial | C2 valid-state preservation and serial equivalence are explicit foundations; a reviewed document's expected-head check at acceptance is not the same specified obligation. |
| atomic_complete_successor | partial | Well-formed transactions preserve integrity; a complete successor snapshot with every field source is not a model requirement shown here. |
| unchanged_exact_source | not-assessed | No explicit unchanged-field source obligation is established in the read model. |
| total_field_provenance | not-assessed | C4 operation reconstruction is explicit, but total field-origin witnesses are not established. |
| reverse_query | partial | C4 reconstructs transaction operations from audit data; a field-to-proposal/reviewer/xa/source query is not specified. (Published pp. 184–191, particularly formal model pp. 189–191.) |
| equal_value_substitution | not-assessed | The formal model does not assess the manuscript's equal-valued proposal substitution example. |

## KungRobinson1981

[On Optimistic Methods for Concurrency Control](https://www.eecs.harvard.edu/~htk/publication/1981-tods-kung-robinson.pdf)

| Dimension | Assessment | Evidence boundary |
|---|---|---|
| persisted_proposal | partial | Private tentative transaction copies are explicit; they are not necessarily durable reviewable AI proposal objects. |
| exact_identity | partial | Named database objects and transaction order numbers support concurrency bookkeeping; candidate-instance identity is a different layer. |
| candidate_bound_review | not-assessed | Human candidate review is outside the studied concurrency mechanism. |
| proposal_authorized_separation | not-assessed | Tentative writes versus validated writes are not an explicit human xc/xa correction relation. |
| human_authority | not-assessed | The studied authorization target is transaction scheduling, not human reviewer authority. |
| fresh_predecessor | explicit | Conflict validation against intervening transactions is explicit. This is a foundation/component overlap, not an exact claim of document-wide head equality. |
| atomic_complete_successor | partial | Validated transaction writes are coordinated; publishing a complete document and all provenance rows is application-specific. |
| unchanged_exact_source | not-assessed | Exact provenance sources for unchanged fields are outside the studied mechanism. |
| total_field_provenance | not-assessed | The paper does not assess total per-field provenance obligations. |
| reverse_query | not-assessed | Concurrency-control method does not assess reverse authorization queries. (Published pp. 213–220, especially pp. 216–220.) |
| equal_value_substitution | not-assessed | Equal-valued review-target substitution is outside the studied mechanism. |

## BunemanChapmanCheney2006

[Provenance Management in Curated Databases](https://www.pure.ed.ac.uk/ws/files/16509719/Provenance_Management_in_Curated_Databases.pdf)

| Dimension | Assessment | Evidence boundary |
|---|---|---|
| persisted_proposal | not-assessed | The update model records curator operations; independent pending AI proposals are not the studied object. |
| exact_identity | explicit | Database/relation/tuple/field paths plus transaction/version identifiers distinguish data locations and states. |
| candidate_bound_review | not-assessed | Per-proposal human approval is not assessed by the read provenance mechanism. |
| proposal_authorized_separation | not-assessed | Transactional net-effect provenance is not an explicit retained xc/xa correction record. |
| human_authority | partial | User/transaction metadata and human curator operations are modeled; reviewer authority is an additional policy. |
| fresh_predecessor | not-assessed | The provenance semantics use transaction versions; a human review followed by a current-head acceptance guard is not established. |
| atomic_complete_successor | partial | Transaction boundaries support committed net-effect provenance; an implementation-level atomic complete-document-plus-witness contract is not established. |
| unchanged_exact_source | explicit | From(t,p,p) follows Unch(t,p), and Trace links to predecessor version t−1 (2.2). |
| total_field_provenance | explicit | Within the closed modeled update history, Copy and Unch rules reconstruct provenance across surviving paths, including compressed subtrees. External unarchived source history is not guaranteed. |
| reverse_query | partial | Section 3 provides backward source/history/modification queries; exact original-proposal/human-reviewer/xa roles require additional policy. (Paper pp. 1–6 / published pp. 539–544; official repository PDF has a one-page cover before paper p. 1.) |
| equal_value_substitution | partial | Copy provenance depends on location/history rather than only value, so equal values may have different sources. A review-target substitution security rule is not assessed. |

## Arab2018

[Using Reenactment to Retroactively Capture Provenance for Transactions](https://www.cs.uic.edu/~bglavic/dbgroup/assets/pdfpubls/AG17c.pdf)

| Dimension | Assessment | Evidence boundary |
|---|---|---|
| persisted_proposal | not-assessed | Durable pre-review AI proposals are not the studied SQL transaction object. |
| exact_identity | explicit | MV annotations carry tuple identity, transaction, operation and version; implementation expects unique immutable tuple IDs (3; 6.2). |
| candidate_bound_review | not-assessed | Human candidate approval is outside the method; application-side dependencies are expressly outside scope. |
| proposal_authorized_separation | not-assessed | Tuple update versions distinguish database states, not a human xc/xa authorization correction record. |
| human_authority | partial | Audited users/transactions can be annotated; human reviewer authority is not an acceptance obligation supplied by the method. |
| fresh_predecessor | partial | Reenactment reconstructs historically correct operation inputs under SI/RC-SI. That is not a fresh document-head approval guard at a later commit. |
| atomic_complete_successor | partial | Commit annotations and database transaction semantics are represented; complete document-plus-approval-witness atomicity is a separate policy. |
| unchanged_exact_source | partial | Attributes outside UPDATE use identity expressions and unchanged tuples retain annotations; an exact separate source record for each unchanged field is not an enforced obligation. |
| total_field_provenance | partial | Tuple-level provenance and attribute values are encoded; total field-level authorized-source witnesses are not established. |
| reverse_query | partial | Reenactment recovers backward update/transaction provenance; the original-proposal/reviewer/authorized-value tuple is not its demonstrated query. (Published pp. 599–609; principal evidence pp. 600–601, 603–608.) |
| equal_value_substitution | partial | Distinct tuple versions/provenance summands may produce equal-valued tuples. Rejecting an equal-valued candidate substituted after review is an application rule, not assessed here. |

## PROVDM2013

[PROV-DM: The PROV Data Model](https://www.w3.org/TR/2013/REC-prov-dm-20130430/)

| Dimension | Assessment | Evidence boundary |
|---|---|---|
| persisted_proposal | partial | An entity can describe a proposal with fixed aspects; mandatory database persistence is not part of this representation standard. |
| exact_identity | explicit | Identifiers and entity equality explicitly distinguish entities; specialized versions and value attributes are available. |
| candidate_bound_review | partial | Usage can identify the exact entity used by a review activity; mandatory authorization binding is an additional policy. |
| proposal_authorized_separation | partial | Separate original/revised entities and values can represent correction; normative xc/xa authorization semantics are additional constraints. |
| human_authority | partial | Agents, association, attribution and delegation represent responsibility/authority relationships; a required human approval gate is not imposed. |
| fresh_predecessor | not-assessed | The data model is not a current document-head concurrency-control policy. |
| atomic_complete_successor | not-assessed | The data model does not assess database co-commit/atomic successor implementation. |
| unchanged_exact_source | partial | Derivation/quotation can represent copies from exact entities; every unchanged field need not have a mandatory source relation in the standard. |
| total_field_provenance | partial | Collections and membership can represent fields, including incompletely described collections; closed total field coverage requires an additional constraint. |
| reverse_query | partial | Entities, agents and activities can encode backward authorization provenance; a mandatory application query requires a profile. (Sections 2.1, 5.1–5.3, 5.5–5.6, and 5.7.1.) |
| equal_value_substitution | partial | Different identifiers can distinguish equal-valued entities. A server-side substitution rejection policy requires additional constraints. |

## Fowler2005

[Event Sourcing](https://www.martinfowler.com/eaaDev/EventSourcing.html)

| Dimension | Assessment | Evidence boundary |
|---|---|---|
| persisted_proposal | partial | Stored events can preserve proposals if the application defines them; independently persisted proposals before review are not mandated. |
| exact_identity | partial | Event objects and ordered history distinguish occurrences conceptually; exact candidate identity is an application schema choice. |
| candidate_bound_review | not-assessed | No particular human review-to-candidate authorization protocol is assessed. |
| proposal_authorized_separation | partial | Separate proposal/correction/approval events are representable; xc/xa retention semantics require application logic. |
| human_authority | not-assessed | Required reviewer authority is not a constraint supplied by the general pattern. |
| fresh_predecessor | not-assessed | A fresh expected document-head check at acceptance is not assessed in this essay. |
| atomic_complete_successor | not-assessed | Complete document/evidence co-commit atomicity is not established by the read event-sourcing pattern. |
| unchanged_exact_source | partial | Replay implicitly preserves state not changed by events; explicit predecessor source witnesses for every field are not required by the pattern. |
| total_field_provenance | partial | All state changes should be event driven for reconstruction; that is not equivalent to a total accepted-field authority/origin relation. |
| reverse_query | partial | History can reconstruct prior operations; the required authorization tuple depends on recorded event contents. (Opening definition and sections How it Works, Reversing Events, External Queries.) |
| equal_value_substitution | not-assessed | Equal-valued candidate substitution after review is not assessed in the essay. |

## gdr2011

[Guided Data Repair](https://cs.uwaterloo.ca/~ilyas/papers/YakoutVLDB2011.pdf)

| Dimension | Assessment | Evidence boundary |
|---|---|---|
| persisted_proposal | partial | Stored list explicit, durable persistence/retention not established. |
| exact_identity | partial | Target tuple/attribute/value given; occurrence identifier not established. |
| candidate_bound_review | partial | Feedback on individual r; enforcement against equivalent replacement r not established. |
| proposal_authorized_separation | partial | v' creates r', with no established retained r->r' correction witness. |
| human_authority | explicit | User labels control consulted updates, with delegated learner decisions also allowed. |
| fresh_predecessor | partial | Inter-update consistency maintenance; no atomic commit freshness proof. |
| atomic_complete_successor | not-assessed | Method/foundation reference: this application obligation was not assessed. |
| unchanged_exact_source | not-assessed | Method/foundation reference: this application obligation was not assessed. |
| total_field_provenance | not-assessed | Method/foundation reference: this application obligation was not assessed. |
| reverse_query | not-assessed | Method/foundation reference: this application obligation was not assessed. |
| equal_value_substitution | not-assessed | Method/foundation reference: this application obligation was not assessed. |

## falcon2016

[Interactive and Deterministic Data Cleaning](https://dbgroup.cs.tsinghua.edu.cn/ligl/papers/sigmod2016-clean.pdf)

| Dimension | Assessment | Evidence boundary |
|---|---|---|
| persisted_proposal | partial | Candidate rule lattice materialized partially; durable exact proposal record not established. |
| exact_identity | partial | Rule/query structures identified, without immutable machine proposal occurrence. |
| candidate_bound_review | partial | Q receives direct feedback; representative Q stands for a closed rule set. |
| proposal_authorized_separation | not-assessed | Method/foundation reference: this application obligation was not assessed. |
| human_authority | explicit | True Q triggers additional repairs. |
| fresh_predecessor | partial | Dynamic lattice maintenance, not commit freshness validation. |
| atomic_complete_successor | not-assessed | Method/foundation reference: this application obligation was not assessed. |
| unchanged_exact_source | not-assessed | Method/foundation reference: this application obligation was not assessed. |
| total_field_provenance | not-assessed | Method/foundation reference: this application obligation was not assessed. |
| reverse_query | not-assessed | Method/foundation reference: this application obligation was not assessed. |
| equal_value_substitution | partial | Explicit effect-versus-validity distinction; no candidate-ID substitution attack or complete evidence contract. |

## wrangler2011

[Wrangler: Interactive Visual Specification of Data Transformation Scripts](https://idl.cs.washington.edu/files/2011-Wrangler-CHI.pdf)

| Dimension | Assessment | Evidence boundary |
|---|---|---|
| persisted_proposal | partial | Saved/applied transform scripts, not established retained pre-edit suggestion. |
| exact_identity | partial | Transform descriptors distinguish operations; no proposal occurrence identifier. |
| candidate_bound_review | partial | Transform inspection and execution; immutable review-target enforcement not established. |
| proposal_authorized_separation | partial | Suggested transform parameters can be edited; original suggestion retention not established. |
| human_authority | explicit | User executes selected/refined transforms. |
| fresh_predecessor | not-assessed | Method/foundation reference: this application obligation was not assessed. |
| atomic_complete_successor | not-assessed | Method/foundation reference: this application obligation was not assessed. |
| unchanged_exact_source | not-assessed | Method/foundation reference: this application obligation was not assessed. |
| total_field_provenance | partial | Script-level documentation, not exhaustive successor-field exact sources. |
| reverse_query | partial | History review/replay supplies traceability, not manuscript reverse field-source query. |
| equal_value_substitution | not-assessed | Method/foundation reference: this application obligation was not assessed. |

## katara2015

[KATARA: A Data Cleaning System Powered by Knowledge Bases and Crowdsourcing](https://cs.uwaterloo.ca/~ilyas/papers/ChuSIGMOD2015.pdf)

| Dimension | Assessment | Evidence boundary |
|---|---|---|
| persisted_proposal | partial | Generated ranked top-k possibilities; durable reviewed proposal occurrence not established. |
| exact_identity | partial | Instance graphs use KB resource/attribute mappings; not exact proposal identity. |
| candidate_bound_review | partial | Selection among top-k repairs, no identity-bound audit/commit proof. |
| proposal_authorized_separation | not-assessed | Method/foundation reference: this application obligation was not assessed. |
| human_authority | explicit | User/crowd picks repair; crowd validates facts. |
| fresh_predecessor | not-assessed | Method/foundation reference: this application obligation was not assessed. |
| atomic_complete_successor | not-assessed | Method/foundation reference: this application obligation was not assessed. |
| unchanged_exact_source | not-assessed | Method/foundation reference: this application obligation was not assessed. |
| total_field_provenance | partial | KB/crowd correctness categories cover discovered semantics, not every successor field's immediate exact source. |
| reverse_query | not-assessed | Method/foundation reference: this application obligation was not assessed. |
| equal_value_substitution | not-assessed | Method/foundation reference: this application obligation was not assessed. |

## nadeef2013

[NADEEF: A Commodity Data Cleaning System](https://www.hbku.edu.qa/sites/default/files/nadeefsigmod2013.pdf)

| Dimension | Assessment | Evidence boundary |
|---|---|---|
| persisted_proposal | partial | Candidate fix sets exist, no durable review record established. |
| exact_identity | partial | Cell target and donor-cell expressions; not proposal occurrence. |
| candidate_bound_review | not-assessed | Method/foundation reference: this application obligation was not assessed. |
| proposal_authorized_separation | not-assessed | Method/foundation reference: this application obligation was not assessed. |
| human_authority | partial | Feedback interface proposed, detailed implementation deferred. |
| fresh_predecessor | partial | Iterative repair/updater handles new violations and termination; not commit pre-state validation. |
| atomic_complete_successor | partial | Conjunctive modifications together is a semantic condition, not a transaction proof. |
| unchanged_exact_source | not-assessed | Method/foundation reference: this application obligation was not assessed. |
| total_field_provenance | partial | Full change lineage stated without total successor-field exact sourcing. |
| reverse_query | partial | Metadata queried for errors/fixes; exact source reverse-query contract unestablished. |
| equal_value_substitution | not-assessed | Method/foundation reference: this application obligation was not assessed. |

## holoclean2017

[HoloClean: Holistic Data Repairs with Probabilistic Inference](https://www.vldb.org/pvldb/vol10/p1190-rekatsinas.pdf)

| Dimension | Assessment | Evidence boundary |
|---|---|---|
| persisted_proposal | partial | Proposed cleaned dataset/model output; no persisted reviewed candidate instance established. |
| exact_identity | partial | Tuple cells identified, not review-target occurrence. |
| candidate_bound_review | not-assessed | Method/foundation reference: this application obligation was not assessed. |
| proposal_authorized_separation | not-assessed | Method/foundation reference: this application obligation was not assessed. |
| human_authority | not-assessed | Method/foundation reference: this application obligation was not assessed. |
| fresh_predecessor | not-assessed | Method/foundation reference: this application obligation was not assessed. |
| atomic_complete_successor | not-assessed | Method/foundation reference: this application obligation was not assessed. |
| unchanged_exact_source | partial | Clean cells fixed as evidence; exact predecessor source link unestablished. |
| total_field_provenance | partial | Per-cell factors/external evidence, not exact source assignment for every committed successor field. |
| reverse_query | not-assessed | Method/foundation reference: this application obligation was not assessed. |
| equal_value_substitution | not-assessed | Method/foundation reference: this application obligation was not assessed. |

## dbwiki2011

[The Database Wiki Project: A General-Purpose Platform for Data Curation and Collaboration](https://sigmodrecord.org/publications/sigmodRecord/1109/pdfs/04.prototypes.buneman.pdf)

| Dimension | Assessment | Evidence boundary |
|---|---|---|
| persisted_proposal | not-assessed | Method/foundation reference: this application obligation was not assessed. |
| exact_identity | partial | Persistent node/value identities, not proposal occurrence identity. |
| candidate_bound_review | not-assessed | Method/foundation reference: this application obligation was not assessed. |
| proposal_authorized_separation | not-assessed | Method/foundation reference: this application obligation was not assessed. |
| human_authority | explicit | Curators directly edit data. |
| fresh_predecessor | partial | Current entry loaded and parent alive check; no documented review-to-commit concurrency guard. |
| atomic_complete_successor | partial | Explicit atomic tree edits and new DB version, not full relation plus evidence transaction. |
| unchanged_exact_source | partial | Untouched nodes/timestamp inheritance preserve structure; exact immediate predecessor-field source witness unestablished. |
| total_field_provenance | partial | Every piece has provenance, but required successor-field source relation not established. |
| reverse_query | partial | History/provenance queries explicit; manuscript reverse field-source relation not established. |
| equal_value_substitution | partial | Skips unchanged-value edits/reuses past value nodes; not an exact review-target substitution experiment. |

## 2608.11632

[Beyond Memory: A Transactional Continuity Kernel for Long-Lived AI Agents](https://arxiv.org/abs/2608.11632)

| Dimension | Assessment | Evidence boundary |
|---|---|---|
| persisted_proposal | explicit | Candidate namespace and signed proposal are separate from accepted head. (Sec. 2.1 Table 1; Sec. 2.2 Eq.3) |
| exact_identity | explicit | Owner-bound pid plus typed canonical proposal/evidence/candidate-root seals. (Sec. 2.2; Sec. 3.1; Appendix B.2) |
| candidate_bound_review | partial | Signed approver evidence is acquired and exactly sealed with proposal/candidate; a mandatory human field verdict is not specified. (Sec. 2.2; Sec. 3.1 Table 2; Appendix A.2) |
| proposal_authorized_separation | partial | Off-commit sealed candidate versus accepted unit; no inspected xc/xa human-correction rule. (Sec. 2.1; Sec. 3.2) |
| human_authority | partial | Approvers sign evidence and human interaction occurs in preparation; humans are not declared mandatory for every write. (Sec. 2.2; Sec. 3.5) |
| fresh_predecessor | explicit | Complete canonical head comparison and two freshness checks against serialized context. (Sec. 2.1 Eq.1; Sec. 3.1) |
| atomic_complete_successor | explicit | All-or-nothing state, authority, head, branch row, outcome, receipt, lineage/effects. (Sec. 3.2 Eq.9; Appendix B.1) |
| unchanged_exact_source | partial | Restoration keeps current unmasked paths and byte-copies branch genesis provenance; not a total per-field source-object rule. (Sec. 4.3; Appendix C.2-C.3) |
| total_field_provenance | partial | Typed component roots and complete lineage/evidence binding; not an exact source function over every data field. (Sec. 2.1; Appendix B.1) |
| reverse_query | partial | Commit receipt/outcome binds proposal, evidence, predecessor and successor, providing partial reverse trace; exact field proposal-human reviewer-xa-source tuple is not specified. (Sec. 3.2-3.3; Appendix B.1) |
| equal_value_substitution | partial | Seals include proposal identity beyond candidate-root value; same-valued candidate replacement should fail binding, but this is an inference, not a reported same-value review experiment. (Sec. 3.1; Appendix B.2) |

## 2607.27834

[MemTxn: A Transaction Boundary for Source-Supported Updates and Complete-State Recovery in Agent Memory](https://arxiv.org/abs/2607.27834)

| Dimension | Assessment | Evidence boundary |
|---|---|---|
| persisted_proposal | partial | Proposed transaction and durable intent are specified; persistence of every rejected raw AI candidate is not established. (Method: System model) |
| exact_identity | partial | q.id, opaque source ID, accepted vid, and parent pointers; no exact-instance review binding. (Method: System model) |
| candidate_bound_review | not-assessed | Admission is Ordered PatchTest, not an inspected exact-candidate human review protocol. (Method: Source-supported admission) |
| proposal_authorized_separation | partial | Accepted z contains q and version metadata; proposal/active lifecycle is separate, but human corrected xa is not defined. (Method: System model) |
| human_authority | not-assessed | No mandatory human authority established by inspected method. |
| fresh_predecessor | partial | Store assigns parent from current active pointer; concurrent fresh exact-head acceptance is explicitly not guaranteed. (Method: System model; Source-supported admission) |
| atomic_complete_successor | partial | Atomic pointer activation and complete-map compensating recovery; not DKE complete accepted record + total field sources. (Method: Source-supported admission; Recovery) |
| unchanged_exact_source | partial | Append-only historical versions and whole saved map recovery; no per-unchanged-field source equality rule. (Method: System model; Recovery) |
| total_field_provenance | partial | Each q includes source span and source ID, but source-support is lexical and semantic role binding is out of scope. (Method: Eq.1; System model) |
| reverse_query | partial | Accepted z contains original q/source/evidence and parent version; reviewer and explicit human authorized-value chain are not established. (Method: System model; Source-supported admission) |
| equal_value_substitution | not-assessed | Audit substitutions change source-supported values, not distinct equal-valued approved candidate identities. (Experiments: Source-Support Admission) |

## 2608.02843

[MutMem: Cryptographically Authorized Mutation in Persistent Agent Memory](https://arxiv.org/abs/2608.02843)

| Dimension | Assessment | Evidence boundary |
|---|---|---|
| persisted_proposal | partial | Retained signed outcome/mutation evidence; not an AI field-candidate staging store. (Sec. 3-5) |
| exact_identity | explicit | Memory UUID, tenant, exact signer epoch, provenance node and old/new weights signed. (Sec. 5.4-5.6) |
| candidate_bound_review | partial | Exact transition authorization is bound cryptographically; human candidate review is not established. (Sec. 5.5-5.6) |
| proposal_authorized_separation | partial | Historical content and signed transition/evidence retained; no explicit human xc/xa correction pair. (Sec. 3-4) |
| human_authority | partial | Enrolled master and actor authority exist, but native housekeeper owns autonomous mutation. (Sec. 2.1) |
| fresh_predecessor | explicit | Terminal no-fork predecessor and live old weight must agree, within the per-memory mutation scope. (Sec. 5.4-5.6) |
| atomic_complete_successor | partial | Outcome/provenance/projection/live-weight update share restricted transaction; not a complete multi-field successor contract. (Sec. 4; Sec. 5.6) |
| unchanged_exact_source | partial | Original memory content and history retained; classification changes leave value/type/scope/content hash unchanged. (Abstract; Sec. 3; Sec. 5.7) |
| total_field_provenance | partial | Signed memory/provenance and recall evidence; every output field's unique exact source is not specified. (Sec. 5-7) |
| reverse_query | partial | From live memory, signed provenance identifies signer, old/new values and preceding mutations; not a complete per-field human review/proposal/xa trace. (Sec. 5.5-5.6; Sec. 6.1) |
| equal_value_substitution | partial | Signatures distinguish memory/provenance even for matching weights; equal target gives no transition. No equal-valued reviewed-candidate attack is reported. (Sec. 4; Sec. 5.5; Sec. 6.3-6.4) |

## 2608.08236

[LatticeMind: A Conflict-Aware Memory Primitive for Multi-Agent Systems](https://arxiv.org/abs/2608.08236)

| Dimension | Assessment | Evidence boundary |
|---|---|---|
| persisted_proposal | explicit | Proposed/Confirmed/Contested/Superseded item status and structured writes. (Sec. 3.1-3.2) |
| exact_identity | partial | Canonical entity/slot/branch/env key and metadata; not immutable candidate-instance approval identity. (Sec. 3.2 Eq.1) |
| candidate_bound_review | partial | Checker/reconciler compares explicit claims, but human review tied to a persisted instance is not established. (Sec. 3.2) |
| proposal_authorized_separation | partial | Status transition and retained losing claims; distinct human corrected xc/xa not specified. (Sec. 3.1-3.2) |
| human_authority | not-assessed | Human notes have evidence weight; that is not a human write authorization protocol. (Sec. 3.2) |
| fresh_predecessor | not-assessed | Current-slot comparison is described; commit-time exact full predecessor serialization is not established. (Algorithm 1) |
| atomic_complete_successor | not-assessed | Sequential append/compare/check/render loop; atomic complete accepted successor is not specified. (Algorithm 1) |
| unchanged_exact_source | partial | Explicitly uses a different rule: equal normalized slot values merge sources/evidence into existing entry. (Sec. 3.2) |
| total_field_provenance | partial | Slot claims carry evidence metadata and losing claims keep provenance; total exact source mapping not established. (Sec. 3.1-3.2) |
| reverse_query | partial | Rendered state/transition provenance exposes supporting claims and sources; no exact proposal-human reviewer-authorized value-source authorization query is specified. (Sec. 3.2) |
| equal_value_substitution | partial | Equal-value identity is intentionally consolidated via evidence accumulation; no exact-instance approval-substitution test. (Sec. 3.2) |

## 2609.02127

[Stored Is Not Supported: Typed Provenance and Assertion Guardrails for Persistent AI Agents](https://arxiv.org/abs/2609.02127)

| Dimension | Assessment | Evidence boundary |
|---|---|---|
| persisted_proposal | partial | Distinct persisted epistemic roles including model priors/hypotheses; not every AI output stored as a review candidate. (Sec. 1; Sec. 2.6) |
| exact_identity | explicit | Every dependency resolves to immutable exact version or authenticated unavailable marker. (Sec. 2 E2; Sec. 2.6 Proposition 1) |
| candidate_bound_review | partial | Fresh role target depends on exact source set and evaluator/policy; human review binding not established. (Sec. 2.6) |
| proposal_authorized_separation | partial | Promotion adds fresh target and never mutates predecessor vertices; human correction xc/xa is not specified. (Sec. 2.6) |
| human_authority | partial | Authenticated user messages ground attributed reports, but this is source standing, not mandatory write approval. (Sec. 2.6 Eq.14) |
| fresh_predecessor | partial | Head-use verification at emission and E1 ordering assumption; not an implemented exact-head admission transaction. (Sec. 2 E1; Sec. 4.2) |
| atomic_complete_successor | partial | Taken as accepted-head assumption, explicitly outside contribution/evaluation. (Sec. 1 Accepted-state boundary; Sec. 2 E1) |
| unchanged_exact_source | partial | Immutable predecessor vertices and historical traces survive promotion/supersession; no per-field source equality recurrence. (Sec. 2.6; Sec. 3.5) |
| total_field_provenance | partial | Conditional traceability for every reachable claim, not a source function over every successor field. (Sec. 2.6 Proposition 1) |
| reverse_query | partial | Claim-to-exact-version dependency trace and release-unit binding provide provenance traceback; no full candidate-human reviewer-xa field authorization query. (Sec. 2.6 Proposition 1; Sec. 4.4) |
| equal_value_substitution | partial | Exact-version references and witnesses distinguish immutable claim objects; no equal-valued approved AI-candidate substitution experiment. (Sec. 2 E2; Sec. 3.2) |

## 2609.01235

[MutMem-V2: Cryptographically Authorized Mutation in Persistent Agent Memory Portable Verification and Reproducible Evidence](https://arxiv.org/abs/2609.01235)

| Dimension | Assessment | Evidence boundary |
|---|---|---|
| persisted_proposal | partial | Portable retained requests/outcomes/evidence, rather than durable raw AI review proposals. (Sec. 3-5) |
| exact_identity | explicit | Exact canonical bytes and subject/epoch/certificate/provenance/request bindings across objects. (Sec. 4) |
| candidate_bound_review | partial | Exact signed request/transition bindings; no human review relation. (Sec. 4.4; Sec. 5) |
| proposal_authorized_separation | partial | Outcome evidence and authorized_transition/signed_noop/occurrence_observation are separate. (Sec. 5) |
| human_authority | partial | External master trust anchor and effective grants; autonomous housekeeper profile is distinct. (Sec. 3.1) |
| fresh_predecessor | partial | Verifier reconstructs V1 exact predecessor; read-only portable verifier does not execute current-state admission. (Sec. 5; Sec. 6.1) |
| atomic_complete_successor | partial | V1 native mutation profile inherited; V2 specifies portable complete evidence, not complete successor storage activation. (Sec. 1; Sec. 5) |
| unchanged_exact_source | partial | Recall decisions forbid canonical-memory/retention mutation; signed_noop fabricates no weight projection. (Sec. 4.4; Sec. 5) |
| total_field_provenance | partial | Complete five-object evidence per disclosed result, not a total per-output-field source assignment. (Sec. 4.2) |
| reverse_query | partial | Returned result evidence binds memory/source provenance, actor and authority commitments; not a full original AI proposal-human reviewer-xa field authorization query. (Sec. 4.2-4.4) |
| equal_value_substitution | partial | Exact object/identity/provenance substitution checks and signed_noop distinguish content from authority; no equal-valued human-reviewed proposal test. (Sec. 3.2; Sec. 4.4; Sec. 5) |

## 2607.23929

[MemTX: Transactional Belief Commit for Stateful Agent Memory](https://arxiv.org/abs/2607.23929)

| Dimension | Assessment | Evidence boundary |
|---|---|---|
| persisted_proposal | explicit | Staging records tentative observations and provenance edges before commit. (Sec. 3.2) |
| exact_identity | partial | Governed source-bearing records and DAG; exact immutable candidate identity binding is not established. (Sec. 3.1-3.2) |
| candidate_bound_review | partial | Equal-authority different-source conflicts quarantine for user review; exact review-token identity protocol not specified. (Sec. 3.2) |
| proposal_authorized_separation | partial | Tentative/validated/committed lifecycle separates authority states; no xc/xa correction object pair. (Sec. 3.1-3.2) |
| human_authority | partial | User review only for declared ties, plus trusted harness tiers; not mandatory human approval for every candidate. (Sec. 3.1-3.2) |
| fresh_predecessor | partial | Rejects rival committed after snapshot before authority comparison; not exact complete-head equality for entire successor. (Sec. 3.2) |
| atomic_complete_successor | partial | Ordered per-record checks explicitly permit partial transaction commit. (Sec. 3.2) |
| unchanged_exact_source | not-assessed | No total unchanged-field exact source rule established. |
| total_field_provenance | partial | Records carry source and derivation DAG; cascade covers only recorded provenance. (Sec. 3.1; Sec. 3.4) |
| reverse_query | partial | Committed record source/permissions/derivation and audit entries provide partial provenance traceback; no exact original proposal-human reviewer-xa-source tuple. (Sec. 3.1-3.4) |
| equal_value_substitution | not-assessed | Appendix H.3 disallows identical value in expected-abort and expected-commit lists because grader is value-based; no same-value identity test. (Appendix H.3) |

## fett2023dpop

[OAuth 2.0 Demonstrating Proof of Possession (DPoP)](https://www.rfc-editor.org/rfc/rfc9449.html)

| Dimension | Assessment | Evidence boundary |
|---|---|---|
| persisted_proposal | not-assessed | Method/foundation reference: this application obligation was not assessed. |
| exact_identity | not-assessed | Method/foundation reference: this application obligation was not assessed. |
| candidate_bound_review | not-assessed | Method/foundation reference: this application obligation was not assessed. |
| proposal_authorized_separation | not-assessed | Method/foundation reference: this application obligation was not assessed. |
| human_authority | not-assessed | Method/foundation reference: this application obligation was not assessed. |
| fresh_predecessor | not-assessed | Method/foundation reference: this application obligation was not assessed. |
| atomic_complete_successor | not-assessed | Method/foundation reference: this application obligation was not assessed. |
| unchanged_exact_source | not-assessed | Method/foundation reference: this application obligation was not assessed. |
| total_field_provenance | not-assessed | Method/foundation reference: this application obligation was not assessed. |
| reverse_query | not-assessed | Method/foundation reference: this application obligation was not assessed. |
| equal_value_substitution | not-assessed | Method/foundation reference: this application obligation was not assessed. |

## backman2024httpsignatures

[HTTP Message Signatures](https://www.rfc-editor.org/rfc/rfc9421.html)

| Dimension | Assessment | Evidence boundary |
|---|---|---|
| persisted_proposal | not-assessed | Method/foundation reference: this application obligation was not assessed. |
| exact_identity | not-assessed | Method/foundation reference: this application obligation was not assessed. |
| candidate_bound_review | not-assessed | Method/foundation reference: this application obligation was not assessed. |
| proposal_authorized_separation | not-assessed | Method/foundation reference: this application obligation was not assessed. |
| human_authority | not-assessed | Method/foundation reference: this application obligation was not assessed. |
| fresh_predecessor | not-assessed | Method/foundation reference: this application obligation was not assessed. |
| atomic_complete_successor | not-assessed | Method/foundation reference: this application obligation was not assessed. |
| unchanged_exact_source | not-assessed | Method/foundation reference: this application obligation was not assessed. |
| total_field_provenance | not-assessed | Method/foundation reference: this application obligation was not assessed. |
| reverse_query | not-assessed | Method/foundation reference: this application obligation was not assessed. |
| equal_value_substitution | not-assessed | Method/foundation reference: this application obligation was not assessed. |

## owasp2026transactionauthorization

[Transaction Authorization Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Transaction_Authorization_Cheat_Sheet.html)

| Dimension | Assessment | Evidence boundary |
|---|---|---|
| persisted_proposal | not-assessed | Method/foundation reference: this application obligation was not assessed. |
| exact_identity | not-assessed | Method/foundation reference: this application obligation was not assessed. |
| candidate_bound_review | not-assessed | Method/foundation reference: this application obligation was not assessed. |
| proposal_authorized_separation | not-assessed | Method/foundation reference: this application obligation was not assessed. |
| human_authority | not-assessed | Method/foundation reference: this application obligation was not assessed. |
| fresh_predecessor | not-assessed | Method/foundation reference: this application obligation was not assessed. |
| atomic_complete_successor | not-assessed | Method/foundation reference: this application obligation was not assessed. |
| unchanged_exact_source | not-assessed | Method/foundation reference: this application obligation was not assessed. |
| total_field_provenance | not-assessed | Method/foundation reference: this application obligation was not assessed. |
| reverse_query | not-assessed | Method/foundation reference: this application obligation was not assessed. |
| equal_value_substitution | not-assessed | Method/foundation reference: this application obligation was not assessed. |

## jackson2002alloy

[Alloy: A Lightweight Object Modelling Notation](https://groups.csail.mit.edu/sdg/pubs/2002/alloy-journal.pdf)

| Dimension | Assessment | Evidence boundary |
|---|---|---|
| persisted_proposal | not-assessed | Method/foundation reference: this application obligation was not assessed. |
| exact_identity | not-assessed | Method/foundation reference: this application obligation was not assessed. |
| candidate_bound_review | not-assessed | Method/foundation reference: this application obligation was not assessed. |
| proposal_authorized_separation | not-assessed | Method/foundation reference: this application obligation was not assessed. |
| human_authority | not-assessed | Method/foundation reference: this application obligation was not assessed. |
| fresh_predecessor | not-assessed | Method/foundation reference: this application obligation was not assessed. |
| atomic_complete_successor | not-assessed | Method/foundation reference: this application obligation was not assessed. |
| unchanged_exact_source | not-assessed | Method/foundation reference: this application obligation was not assessed. |
| total_field_provenance | not-assessed | Method/foundation reference: this application obligation was not assessed. |
| reverse_query | not-assessed | Method/foundation reference: this application obligation was not assessed. |
| equal_value_substitution | not-assessed | Method/foundation reference: this application obligation was not assessed. |

## torlak2007kodkod

[Kodkod: A Relational Model Finder](https://groups.csail.mit.edu/sdg/pubs/2007/tacas07-torlak-jackson.pdf)

| Dimension | Assessment | Evidence boundary |
|---|---|---|
| persisted_proposal | not-assessed | Method/foundation reference: this application obligation was not assessed. |
| exact_identity | not-assessed | Method/foundation reference: this application obligation was not assessed. |
| candidate_bound_review | not-assessed | Method/foundation reference: this application obligation was not assessed. |
| proposal_authorized_separation | not-assessed | Method/foundation reference: this application obligation was not assessed. |
| human_authority | not-assessed | Method/foundation reference: this application obligation was not assessed. |
| fresh_predecessor | not-assessed | Method/foundation reference: this application obligation was not assessed. |
| atomic_complete_successor | not-assessed | Method/foundation reference: this application obligation was not assessed. |
| unchanged_exact_source | not-assessed | Method/foundation reference: this application obligation was not assessed. |
| total_field_provenance | not-assessed | Method/foundation reference: this application obligation was not assessed. |
| reverse_query | not-assessed | Method/foundation reference: this application obligation was not assessed. |
| equal_value_substitution | not-assessed | Method/foundation reference: this application obligation was not assessed. |

## marinov2001testera

[TestEra: A Novel Framework for Automated Testing of Java Programs](https://mir.cs.illinois.edu/marinov/publications/MarinovKhurshid01TestEra.pdf)

| Dimension | Assessment | Evidence boundary |
|---|---|---|
| persisted_proposal | not-assessed | Method/foundation reference: this application obligation was not assessed. |
| exact_identity | not-assessed | Method/foundation reference: this application obligation was not assessed. |
| candidate_bound_review | not-assessed | Method/foundation reference: this application obligation was not assessed. |
| proposal_authorized_separation | not-assessed | Method/foundation reference: this application obligation was not assessed. |
| human_authority | not-assessed | Method/foundation reference: this application obligation was not assessed. |
| fresh_predecessor | not-assessed | Method/foundation reference: this application obligation was not assessed. |
| atomic_complete_successor | not-assessed | Method/foundation reference: this application obligation was not assessed. |
| unchanged_exact_source | not-assessed | Method/foundation reference: this application obligation was not assessed. |
| total_field_provenance | not-assessed | Method/foundation reference: this application obligation was not assessed. |
| reverse_query | not-assessed | Method/foundation reference: this application obligation was not assessed. |
| equal_value_substitution | not-assessed | Method/foundation reference: this application obligation was not assessed. |

## buneman2001whywhere

[Why and Where: A Characterization of Data Provenance](https://www.pure.ed.ac.uk/ws/files/16509989/Why_and_Where_A_Characterization_of_Data_Provenance.pdf)

| Dimension | Assessment | Evidence boundary |
|---|---|---|
| persisted_proposal | not-assessed | Foundation rather than application-specific authorization contract. (Abstract; introduction; Sections 2, 4, 5.1 and 6.) |
| exact_identity | not-assessed | Foundation rather than application-specific authorization contract. (Abstract; introduction; Sections 2, 4, 5.1 and 6.) |
| candidate_bound_review | not-assessed | Foundation rather than application-specific authorization contract. (Abstract; introduction; Sections 2, 4, 5.1 and 6.) |
| proposal_authorized_separation | not-assessed | Foundation rather than application-specific authorization contract. (Abstract; introduction; Sections 2, 4, 5.1 and 6.) |
| human_authority | not-assessed | Foundation rather than application-specific authorization contract. (Abstract; introduction; Sections 2, 4, 5.1 and 6.) |
| fresh_predecessor | not-assessed | Foundation rather than application-specific authorization contract. (Abstract; introduction; Sections 2, 4, 5.1 and 6.) |
| atomic_complete_successor | not-assessed | Foundation rather than application-specific authorization contract. (Abstract; introduction; Sections 2, 4, 5.1 and 6.) |
| unchanged_exact_source | not-assessed | Foundation rather than application-specific authorization contract. (Abstract; introduction; Sections 2, 4, 5.1 and 6.) |
| total_field_provenance | not-assessed | Foundation rather than application-specific authorization contract. (Abstract; introduction; Sections 2, 4, 5.1 and 6.) |
| reverse_query | partial | Backward derivation/source explanations overlap; the human authorization tuple requires additional semantics. (Abstract; introduction; Sections 2, 4, 5.1 and 6.) |
| equal_value_substitution | not-assessed | Foundation rather than application-specific authorization contract. (Abstract; introduction; Sections 2, 4, 5.1 and 6.) |

## cheney2009provenance

[Provenance in Databases: Why, How, and Where](https://homepages.inf.ed.ac.uk/jcheney/publications/provdbsurvey.pdf)

| Dimension | Assessment | Evidence boundary |
|---|---|---|
| persisted_proposal | not-assessed | Foundation rather than application-specific authorization contract. (Abstract; introduction pp380-382; 1.1.1-1.1.3; Sections 3 and 4.1.) |
| exact_identity | not-assessed | Foundation rather than application-specific authorization contract. (Abstract; introduction pp380-382; 1.1.1-1.1.3; Sections 3 and 4.1.) |
| candidate_bound_review | not-assessed | Foundation rather than application-specific authorization contract. (Abstract; introduction pp380-382; 1.1.1-1.1.3; Sections 3 and 4.1.) |
| proposal_authorized_separation | not-assessed | Foundation rather than application-specific authorization contract. (Abstract; introduction pp380-382; 1.1.1-1.1.3; Sections 3 and 4.1.) |
| human_authority | not-assessed | Foundation rather than application-specific authorization contract. (Abstract; introduction pp380-382; 1.1.1-1.1.3; Sections 3 and 4.1.) |
| fresh_predecessor | not-assessed | Foundation rather than application-specific authorization contract. (Abstract; introduction pp380-382; 1.1.1-1.1.3; Sections 3 and 4.1.) |
| atomic_complete_successor | not-assessed | Foundation rather than application-specific authorization contract. (Abstract; introduction pp380-382; 1.1.1-1.1.3; Sections 3 and 4.1.) |
| unchanged_exact_source | not-assessed | Foundation rather than application-specific authorization contract. (Abstract; introduction pp380-382; 1.1.1-1.1.3; Sections 3 and 4.1.) |
| total_field_provenance | not-assessed | Foundation rather than application-specific authorization contract. (Abstract; introduction pp380-382; 1.1.1-1.1.3; Sections 3 and 4.1.) |
| reverse_query | partial | Backward derivation/source explanations overlap; the human authorization tuple requires additional semantics. (Abstract; introduction pp380-382; 1.1.1-1.1.3; Sections 3 and 4.1.) |
| equal_value_substitution | not-assessed | Foundation rather than application-specific authorization contract. (Abstract; introduction pp380-382; 1.1.1-1.1.3; Sections 3 and 4.1.) |

## gray1981transaction

[The Transaction Concept: Virtues and Limitations](https://web.stanford.edu/class/archive/cs/cs240/cs240.1236/old/sp2014/readings/Gray81.pdf)

| Dimension | Assessment | Evidence boundary |
|---|---|---|
| persisted_proposal | not-assessed | Foundation rather than application-specific authorization contract. (Abstract; introduction p144; general transaction model p145; implementation overview p146.) |
| exact_identity | not-assessed | Foundation rather than application-specific authorization contract. (Abstract; introduction p144; general transaction model p145; implementation overview p146.) |
| candidate_bound_review | not-assessed | Foundation rather than application-specific authorization contract. (Abstract; introduction p144; general transaction model p145; implementation overview p146.) |
| proposal_authorized_separation | not-assessed | Foundation rather than application-specific authorization contract. (Abstract; introduction p144; general transaction model p145; implementation overview p146.) |
| human_authority | not-assessed | Foundation rather than application-specific authorization contract. (Abstract; introduction p144; general transaction model p145; implementation overview p146.) |
| fresh_predecessor | not-assessed | Foundation rather than application-specific authorization contract. (Abstract; introduction p144; general transaction model p145; implementation overview p146.) |
| atomic_complete_successor | partial | Atomic state transformations are established; total field sources and review witnesses are application obligations. (General model p145) |
| unchanged_exact_source | not-assessed | Foundation rather than application-specific authorization contract. (Abstract; introduction p144; general transaction model p145; implementation overview p146.) |
| total_field_provenance | not-assessed | Foundation rather than application-specific authorization contract. (Abstract; introduction p144; general transaction model p145; implementation overview p146.) |
| reverse_query | not-assessed | Foundation rather than application-specific authorization contract. (Abstract; introduction p144; general transaction model p145; implementation overview p146.) |
| equal_value_substitution | not-assessed | Foundation rather than application-specific authorization contract. (Abstract; introduction p144; general transaction model p145; implementation overview p146.) |

## US20200117643A1

[Data curation system with version control for workflow states and provenance](https://patents.google.com/patent/US20200117643A1/en)

| Dimension | Assessment | Evidence boundary |
|---|---|---|
| persisted_proposal | partial | Versioned curation, approval and provenance overlap; exact manuscript obligation requires further comparison. (Description: Curation Actions, Provenance, State History; claims 1, 7, 8, 11) |
| exact_identity | partial | Versioned curation, approval and provenance overlap; exact manuscript obligation requires further comparison. (Description: Curation Actions, Provenance, State History; claims 1, 7, 8, 11) |
| candidate_bound_review | partial | Versioned curation, approval and provenance overlap; exact manuscript obligation requires further comparison. (Description: Curation Actions, Provenance, State History; claims 1, 7, 8, 11) |
| proposal_authorized_separation | partial | Versioned curation, approval and provenance overlap; exact manuscript obligation requires further comparison. (Description: Curation Actions, Provenance, State History; claims 1, 7, 8, 11) |
| human_authority | partial | Versioned curation, approval and provenance overlap; exact manuscript obligation requires further comparison. (Description: Curation Actions, Provenance, State History; claims 1, 7, 8, 11) |
| fresh_predecessor | partial | Versioned curation, approval and provenance overlap; exact manuscript obligation requires further comparison. (Description: Curation Actions, Provenance, State History; claims 1, 7, 8, 11) |
| atomic_complete_successor | partial | Versioned curation, approval and provenance overlap; exact manuscript obligation requires further comparison. (Description: Curation Actions, Provenance, State History; claims 1, 7, 8, 11) |
| unchanged_exact_source | partial | Versioned curation, approval and provenance overlap; exact manuscript obligation requires further comparison. (Description: Curation Actions, Provenance, State History; claims 1, 7, 8, 11) |
| total_field_provenance | partial | Versioned curation, approval and provenance overlap; exact manuscript obligation requires further comparison. (Description: Curation Actions, Provenance, State History; claims 1, 7, 8, 11) |
| reverse_query | partial | Versioned curation, approval and provenance overlap; exact manuscript obligation requires further comparison. (Description: Curation Actions, Provenance, State History; claims 1, 7, 8, 11) |
| equal_value_substitution | not-assessed | Not established in the inspected description/claims. (Description and claims 1, 7, 8, 11) |
