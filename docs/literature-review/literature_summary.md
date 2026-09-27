# Stage 2 - Related-work literature audit

Date: 27 September 2026. A targeted adverse audit across the eight requested families; not an exhaustive systematic review. Existing bibliography/library notes preceded primary-source searching. Local scholarly/Paperpile tools were unavailable, so official PDFs/HTML plus Crossref/DataCite metadata were used.

## Findings that change the framing

The broad components and several combinations have strong precedents. In particular, version-bound approval, user correction, unchanged-source provenance, and exact-proposal atomic activation cannot be presented as new inventions. Section 2 should compare the specified joint field relation and its analyzed policy distinction.

The main bibliography adds selected established sources rather than every candidate. Older peer-reviewed systems carry the approval/curation argument; the five existing 2026 memory references remain explicitly preprints. Method references are concise. The eleven-dimension analysis remains outside the manuscript.

## Reading and selection rules

Every selected mechanism comparison includes abstract, introduction/contributions and relevant methods. Partial candidates remain separately flagged. Silence is never coded as inability. Published versions take precedence over preprints; standards and practice documents are identified accurately. No personal-library membership is claimed.

## Mershad2015 - Approving Updates in Collaborative Databases

- Citation: ['Khaleel Mershad', 'Qutaibah M. Malluhi', 'Mourad Ouzzani', 'Mingjie Tang', 'Walid G. Aref']; 2015 IEEE International Conference on Cloud Engineering (IC2E); 2015.
- Status: Published conference paper.
- Source: [Approving Updates in Collaborative Databases](https://www.cs.purdue.edu/homes/aref/papers/ic2e2015.pdf); DOI [10.1109/IC2E.2015.31](https://doi.org/10.1109/IC2E.2015.31).
- Read: {"status": "relevant-method-full", "read": "Abstract, introduction/contributions, Section III architecture and requirements, Section IV implementation and approval process; Section V evaluation checked for system scope.", "source_file": "sources/mershad2015.pdf", "locator": "Sections III-A/B and IV-A/B; PDF pp. 3–4, published pp. 44–45."}
- Actual contribution: Update-Pending-Approval (UPA) in HBase: collaborator updates are visible while pending; privileged principal investigators approve or reject persisted cell-history records. Retains versions and operator/operation/status/comments metadata; optimizes access to last inserted and last approved values with three modes.
- Overlap: Direct prior art for persisted field/cell proposals, human content approval and review of particular stored versions. In IV-B, the PI gives a cell ID and timestamps of the records selected from the History table to ScHistory. This is stronger than approval merely bound to a user, field, or surrounding context.
- Distinction/unestablished: The sections read do not establish a human correction record retaining both original machine value xc and a separately authorized xa for the same proposal, or the joint invariant tying that review to a fresh document predecessor, an atomic complete document successor, and explicit sources for every successor field. Bulk approval is described as one operation, while timestamp selections are sequentially approved; neither wording establishes the manuscript's document-wide atomic snapshot obligation. This is an evidence limit, not a proof that extensions could not supply it.
- Internal novelty risk: high - Anticipates the broad exact persisted version → human approval relation; must be cited and compared. The manuscript can claim a narrower joint authorization-and-commit discipline only with a precise difference.

## Mershad2018AUDIT - AUDIT: approving and tracking updates with dependencies in collaborative databases

- Citation: ['Khaleel Mershad', 'Qutaibah M. Malluhi', 'Mourad Ouzzani', 'Mingjie Tang', 'Michael Gribskov', 'Walid G. Aref']; Distributed and Parallel Databases; 2018.
- Status: Published journal article; online 21 September 2017, March 2018 issue.
- Source: [AUDIT: approving and tracking updates with dependencies in collaborative databases](https://doi.org/10.1007/s10619-017-7208-y); DOI [10.1007/s10619-017-7208-y](https://doi.org/10.1007/s10619-017-7208-y).
- Read: {"status": "partial", "read": "Official author-institution metadata and abstract; first-page material accessible. Publisher full text/PDF was not available in this run. No method-level conclusion is drawn, and no 2015 implementation details are attributed to this article.", "metadata_url": "https://researchportal.hbku.edu.qa/en/publications/audit-approving-and-tracking-updates-with-dependencies-in-collabo", "locator": "Abstract and bibliographic record only."}
- Actual contribution: The abstract describes update approval and tracking of dependencies in collaborative databases, preserving updated data for discussion and approval while supporting dependency management.
- Overlap: High-priority journal follow-up in the same approval family. Abstract-level overlap includes collaborator updates, approval, histories, and dependencies.
- Distinction/unestablished: Method unavailable: exact review binding, dependency granularity, concurrency enforcement, and all manuscript-specific witness obligations require full-text reading. No negative novelty conclusion about these mechanisms is justified from the abstract.
- Internal novelty risk: high - Closest named journal follow-up to the 2015 challenger, but the risk assessment is a reading priority rather than a verified full-method anticipation claim. Use 2015 for grounded implementation comparison.

## Eltabakh2007bdbms - bdbms—A Database Management System for Biological Data

- Citation: ['Mohamed Y. Eltabakh', 'Mourad Ouzzani', 'Walid G. Aref']; Third Biennial Conference on Innovative Data Systems Research (CIDR 2007); 2007.
- Status: Published conference system/design paper.
- Source: [bdbms—A Database Management System for Biological Data](https://www.cs.purdue.edu/bdbms/publications/bdbms-system.pdf); no DOI claimed.
- Read: {"status": "relevant-method-full", "read": "Official PDF: abstract, introduction and full Section 6 Content-based Approval. Other parts were used only for orientation.", "locator": "Section 6, PDF p. 9 (zero-based web page index 8); no proceedings-page range independently verified."}
- Actual contribution: Database support for biological data curation, including annotations, provenance/dependency tracking and content-based approval. SQL configures approval for a table or selected columns by a user/group. An operation log and inverse statements allow custodians to inspect updates and disapprove them, including dependent-data invalidation.
- Overlap: Human approval of database content, selected-column granularity, update logs, old values and reviewer authority substantially predate AI-specific acceptance models.
- Distinction/unestablished: The read approval section describes log inspection and inverse operations after changes, rather than proving the manuscript's full pre-commit acceptance relation. Exact immutable proposal review targets, xc/xa correction records, a freshly validated document predecessor, and complete successor-field source obligations are not established by the section. This does not show such extensions are impossible.
- Internal novelty risk: high - Challenges broad claims that database updates lack human content approval or that database permissions alone govern acceptance. The 2015 UPA paper is a more direct grounded exact-version challenger.

## ClarkWilson1987 - A Comparison of Commercial and Military Computer Security Policies

- Citation: ['David D. Clark', 'David R. Wilson']; 1987 IEEE Symposium on Security and Privacy; 1987.
- Status: Published conference paper.
- Source: [A Comparison of Commercial and Military Computer Security Policies](https://groups.csail.mit.edu/ana/Publications/PubPDFs/A%20Comparison%20of%20Commercial%20and%20Military%20Computer%20Security%20Policies.pdf); DOI [10.1109/SP.1987.10001](https://doi.org/10.1109/SP.1987.10001).
- Read: {"status": "relevant-method-full", "read": "Abstract/introduction, commercial integrity discussion, and formal certification/enforcement rules C1–C5 and E1–E4; task sequencing discussion.", "source_file": "sources/clarkwilson1987.pdf", "locator": "Published pp. 184–191, particularly formal model pp. 189–191.", "metadata_note": "Crossref page field was truncated to 184–184; 184–194 was checked against the official scan/author publication information."}
- Actual contribution: Formal commercial integrity policy based on well-formed transactions, constrained data items (CDIs), transformation procedures (TPs), authenticated user/TP/CDI authorization relations, separation of duty, certification, and append-only audit logs.
- Overlap: Established integrity transitions, authenticated human authority, legal execution relationships, separation between certification and execution, and reconstructible audit evidence. UDI-to-CDI validation is a useful conceptual comparison for externally supplied proposals.
- Distinction/unestablished: UDI/CDI validation is performed by certified procedures; it is not itself a human review bound to one persisted AI candidate. The model could encode richer policies through TPs/CDIs, but the read specification does not establish the manuscript's particular xc/xa, current document predecessor, and total successor-field witness relation.
- Internal novelty risk: medium - Foundational challenge to general authorization-plus-integrity rhetoric; does not alone anticipate the complete field-level relation. Present the manuscript as an application policy built from established integrity principles.

## KungRobinson1981 - On Optimistic Methods for Concurrency Control

- Citation: ['H. T. Kung', 'John T. Robinson']; ACM Transactions on Database Systems; 1981.
- Status: Published journal article.
- Source: [On Optimistic Methods for Concurrency Control](https://www.eecs.harvard.edu/~htk/publication/1981-tods-kung-robinson.pdf); DOI [10.1145/319566.319567](https://doi.org/10.1145/319566.319567).
- Read: {"status": "relevant-method-full", "read": "Abstract/introduction, Section 2 read/validation/write phases, Section 3 validation conditions and serial validation; concurrency-control discussion used for scope.", "source_file": "sources/occ1981.pdf", "locator": "Published pp. 213–220, especially pp. 216–220."}
- Actual contribution: Optimistic concurrency control: transactions work on local copies, validate read/write conflicts and serialization order, and write shared state only on successful validation. Serial validation coordinates validation and writing.
- Overlap: Revalidation before exposing writes, abort/restart on conflicting work, and atomic coordination of validation with writes are established foundations for a fresh predecessor acceptance check.
- Distinction/unestablished: OCC is conflict/serialization control, not a persisted AI candidate and human-review policy. Read/write-set validation is not automatically identical to a deliberately stricter document-wide expected-head comparison; the latter may reject even changes that would serialize.
- Internal novelty risk: medium - Freshness/commit validation cannot be claimed as a new transaction technique; combining it with proposal-authority provenance is a narrower application contract.

## BunemanChapmanCheney2006 - Provenance Management in Curated Databases

- Citation: ['Peter Buneman', 'Adriane P. Chapman', 'James Cheney']; Proceedings of the 2006 ACM SIGMOD International Conference on Management of Data; 2006.
- Status: Published conference paper.
- Source: [Provenance Management in Curated Databases](https://www.pure.ed.ac.uk/ws/files/16509719/Provenance_Management_in_Curated_Databases.pdf); DOI [10.1145/1142473.1142534](https://doi.org/10.1145/1142473.1142534).
- Read: {"status": "relevant-method-full", "read": "Abstract/introduction, Sections 2.1–2.2 including naive, transactional and hierarchical provenance and complete From/Unch/Trace rules; Section 3 provenance queries through source/history/modification functions.", "source_file": "sources/curated2006.pdf", "locator": "Paper pp. 1–6 / published pp. 539–544; official repository PDF has a one-page cover before paper p. 1."}
- Actual contribution: Provenance for curated databases with insert/copy/delete operations, versioned paths and transactions; multiple storage granularity choices with formal reconstruction rules. Source, history and modification queries reconstruct data origins and copying paths.
- Overlap: Exact field/data locations, transaction/version identity, retained origins, and explicit carryforward of unchanged data are already established. Section 2.2's From(t,p,p) rule for Unch(t,p) traces unchanged location p back to the same location in predecessor version t−1. Copying a value and replacing it with an equal value can have different sources.
- Distinction/unestablished: Human curation motivates the system but per-proposal reviewer authorization and an original-machine-versus-authorized-value correction record are not established. Transactional provenance intentionally retains net committed copy effects rather than every temporary intermediate copy. This is a material contrast with independently persisted proposal/review evidence, without denying that richer annotations could be added.
- Internal novelty risk: high - Challenges novelty of exact unchanged-field predecessor sources, source-preserving copy, and update-history trace queries. The manuscript's contribution must be the joint acceptance policy and evidence discipline, not these provenance concepts individually.

## Arab2018 - Using Reenactment to Retroactively Capture Provenance for Transactions

- Citation: ['Bahareh Sadat Arab', 'Dieter Gawlick', 'Vasudha Krishnaswamy', 'Venkatesh Radhakrishnan', 'Boris Glavic']; IEEE Transactions on Knowledge and Data Engineering; 2018.
- Status: Published journal article; online November 2017, March 2018 issue.
- Source: [Using Reenactment to Retroactively Capture Provenance for Transactions](https://www.cs.uic.edu/~bglavic/dbgroup/assets/pdfpubls/AG17c.pdf); DOI [10.1109/TKDE.2017.2769056](https://doi.org/10.1109/TKDE.2017.2769056).
- Read: {"status": "relevant-method-full", "read": "Abstract/introduction/contributions, Sections 3–4 multiversion provenance and SI/RC-SI histories, complete Sections 5.1–5.3 reenactment, and Sections 6.1–6.2 implementation/optimizations. Section 7 setup checked; no evaluation-number claims used.", "source_file": "sources/arab2018-uic.pdf", "locator": "Published pp. 599–609; principal evidence pp. 600–601, 603–608."}
- Actual contribution: MV-semirings distinguish tuple versions and transaction operations, including commit, under SI and read-committed SI. Reenactment queries reconstruct a transaction's provenance from audit logs and time travel; GProM translates the result into ordinary SQL without changing live transaction processing.
- Overlap: Exact tuple-version identities, update/commit history, reconstructing the version actually read by an operation, and querying affected tuples are established. Versions are not reduced to their current values.
- Distinction/unestablished: The paper positively scopes out application-side dependencies, including client-side query results reused in later updates, and procedural provenance. SQL provenance representation/reconstruction is not enforcement of human approval of a persisted candidate. Unchanged attributes use identity expressions, but total exact successor-field authority sources are not the paper's stated granularity or enforcement policy.
- Internal novelty risk: medium - Substantial component overlap in version-sensitive transaction histories; the documented application-side scope limitation supports a fair boundary around human proposal/review evidence. Do not imply transaction provenance cannot represent additional review annotations.

## PROVDM2013 - PROV-DM: The PROV Data Model

- Citation: ['Luc Moreau (editor)', 'Paolo Missier (editor)']; W3C Recommendation, 30 April 2013; 2013.
- Status: Normative W3C Recommendation; data model, not peer-reviewed research paper.
- Source: [PROV-DM: The PROV Data Model](https://www.w3.org/TR/2013/REC-prov-dm-20130430/); no DOI claimed.
- Read: {"status": "relevant-method-full", "read": "Overview/abstract and introduction; entity/activity/agent core; relevant generation/usage, derivation/revision/quotation, association/delegation, specialization/alternate, collections, identifier/equality subsections.", "locator": "Sections 2.1, 5.1–5.3, 5.5–5.6, and 5.7.1."}
- Actual contribution: Interoperable provenance vocabulary for entities, activities and agents and qualified relations for use, generation, derivation, revision, responsibility, delegation and identity. Can describe distinct versions and copies without identifying them by value.
- Overlap: Representation of candidate, review activity, correction, agent, version, generation/use and exact entity identity is readily expressible in PROV. Equal values do not force identical provenance entities.
- Distinction/unestablished: PROV-DM is a representation model rather than the manuscript's enforced application acceptance policy. Describing a review as an activity using a candidate does not alone ensure a server authorizes only that candidate, refreshes its document predecessor, commits atomically, or supplies a source for all fields. These are additional constraints/implementation obligations, not representational impossibilities.
- Internal novelty risk: medium - Challenges claims of a newly expressible provenance relationship or identity/value distinction. Supports presenting the manuscript as a constrained domain model and enforcement contract.

## Fowler2005 - Event Sourcing

- Citation: ['Martin Fowler']; Author's web essay, 12 December 2005; 2005.
- Status: Authoritative software-practice draft/essay; not peer-reviewed.
- Source: [Event Sourcing](https://www.martinfowler.com/eaaDev/EventSourcing.html); no DOI claimed.
- Read: {"status": "relevant-method-full", "read": "Opening definition, How it Works, application state/event storage discussion, separating processing/logic, reversing events and external queries.", "locator": "Opening definition and sections How it Works, Reversing Events, External Queries."}
- Actual contribution: Store domain changes as a sequence of events that drives state; supports complete rebuild, temporal queries and replay. Reverse operations need prior values when events store only differences; replay of external queries requires historical responses.
- Overlap: Durable history, state reconstruction, before/after information and reproducible replay are established patterns. An approval or correction can be an application event, so do not suggest event sourcing cannot encode it.
- Distinction/unestablished: Event sourcing supplies a general event/state pattern, not an enforced exact candidate-bound human approval and total field-source acceptance contract. Replay reconstructs state but does not automatically prove who authorized each accepted field or whether the document predecessor was fresh when approval was applied.
- Internal novelty risk: low - Low risk for the full joint relation, strong prior art for generic audit/replay rhetoric. Retain as architectural background rather than research novelty proof.

## gdr2011 - Guided Data Repair

- Citation: ['Mohamed Yakout', 'Ahmed K. Elmagarmid', 'Jennifer Neville', 'Mourad Ouzzani', 'Ihab F. Ilyas']; Proceedings of the VLDB Endowment 4(5):279–289; 2011.
- Status: Published peer-reviewed research article.
- Source: [Guided Data Repair](https://cs.uwaterloo.ca/~ilyas/papers/YakoutVLDB2011.pdf); DOI [10.14778/1952376.1952378](https://doi.org/10.14778/1952376.1952378).
- Read: Abstract; introduction/problem/contributions pp279–280; solution/update generation and consistency manager p281; feedback and replacement semantics Sec.4.2 p283.
- Actual contribution: Ranks suggested cell repairs using value of information and active learning; user labels improve repairs and train a model that can make further decisions.
- Overlap: PossibleUpdates stores r=<t,A,v,s>. User confirms, rejects, retains, or supplies v'. Confirmed updates change the database; the consistency manager refreshes inconsistent suggestions.
- Distinction/unestablished: Replacement v' is treated as confirmation of r'=<t,A,v',1>; the text does not establish preserving the original r and machine v alongside r' in a durable review/commit witness. It also does not establish immutable proposal occurrence identity, commit-time predecessor checking, atomic complete successor evidence, or exact sources for every unchanged field.
- Internal novelty risk: high - Direct predecessor for machine-suggested, human-reviewed repair and freshness-aware candidate maintenance; the stronger identity-and-complete-provenance relation remains unestablished.

## falcon2016 - Interactive and Deterministic Data Cleaning

- Citation: ['Jian He', 'Enzo Veltri', 'Donatello Santoro', 'Guoliang Li', 'Giansalvatore Mecca', 'Paolo Papotti', 'Nan Tang']; SIGMOD 2016:893–907; 2016.
- Status: Published peer-reviewed research conference paper.
- Source: [Interactive and Deterministic Data Cleaning](https://dbgroup.cs.tsinghua.edu.cn/ligl/papers/sigmod2016-clean.pdf); DOI [10.1145/2882903.2915242](https://doi.org/10.1145/2882903.2915242).
- Read: Abstract/introduction pp893–894; workflow and SQL language Sec.Sec.1–2 p894; lattice maintenance Sec.5.1 p899; closed rule sets Sec.5.2 p900.
- Actual contribution: Generalizes a user cell correction into candidate SQL UPDATE rules and finds useful rules through efficient lattice search and human validation.
- Overlap: Human True/False validation of Q determines whether it repairs more data. Candidate effects are maintained as data changes. Closed rule sets affect identical tuples but can contain both semantically valid and invalid rules.
- Distinction/unestablished: The candidate under review is a SQL rule generalized from a user edit, not a separately retained original machine xc plus authorized xa. Immutable proposal-instance binding, fresh commit pre-state, complete atomic field-source evidence, and same-value candidate substitution experiments are not established.
- Internal novelty risk: high - Already recognizes identical instance effects need not imply semantic validity. This is a strong challenge to broad novelty claims about equivalence versus approval, but not evidence of the manuscript's exact stored-candidate contract.

## wrangler2011 - Wrangler: Interactive Visual Specification of Data Transformation Scripts

- Citation: ['Sean Kandel', 'Andreas Paepcke', 'Joseph Hellerstein', 'Jeffrey Heer']; CHI 2011:3363–3372; 2011.
- Status: Published peer-reviewed research conference paper.
- Source: [Wrangler: Interactive Visual Specification of Data Transformation Scripts](https://idl.cs.washington.edu/files/2011-Wrangler-CHI.pdf); DOI [10.1145/1978942.1979444](https://doi.org/10.1145/1978942.1979444).
- Read: Abstract/introduction pp3363–3364; walkthrough/previews pp3365–3367; interactive descriptions/previews/history and export pp3368–3369.
- Actual contribution: Mixed-initiative transformation specification using direct manipulation, inferred suggestions, editable previews, and exportable auditable transformation scripts.
- Overlap: Users inspect/edit suggested transforms before executing them. Applied transforms enter editable, annotated histories and scripts can be replayed on new sources.
- Distinction/unestablished: History records applied transformations; retention of each original unedited machine proposal together with the authorized edited version is not established. Exact proposal occurrence binding, commit freshness, atomic complete successor provenance, and unchanged-field exact source assignments are not established.
- Internal novelty risk: medium - Strong precedent for human-refined machine transformations and auditable histories; different focus from exact proposal authorization and total successor evidence.

## katara2015 - KATARA: A Data Cleaning System Powered by Knowledge Bases and Crowdsourcing

- Citation: ['Xu Chu', 'John Morcos', 'Ihab F. Ilyas', 'Mourad Ouzzani', 'Paolo Papotti', 'Nan Tang', 'Yin Ye']; SIGMOD 2015:1247–1261; 2015.
- Status: Published peer-reviewed research conference paper; distinct from 2015 PVLDB demo 'KATARA: Reliable Data Cleaning...' (10.14778/2824032.2824096).
- Source: [KATARA: A Data Cleaning System Powered by Knowledge Bases and Crowdsourcing](https://cs.uwaterloo.ca/~ilyas/papers/ChuSIGMOD2015.pdf); DOI [10.1145/2723372.2749431](https://doi.org/10.1145/2723372.2749431).
- Read: Abstract/introduction/contributions pp1247–1248; pattern definition Sec.3; question validation Sec.5; data annotation and top-k repair generation Sec.Sec.6.1–6.2 p1254.
- Actual contribution: Aligns dirty tables to knowledge bases, validates table patterns through crowd questions, annotates correctness, and generates ranked repairs.
- Overlap: Crowd verifies missing facts and users/crowd select appropriate top-k repair. KB/crowd validation categories expose evidence origin.
- Distinction/unestablished: Correctness annotations and repair choices do not establish a retained machine xc versus authorized xa, immutable review-candidate identities, predecessor freshness, atomic successor evidence, or total exact sources for fields outside the discovered pattern.
- Internal novelty risk: medium - Crowd-guided relation validation and repair selection overlap substantially; complete review/commit identity semantics are unestablished.

## nadeef2013 - NADEEF: A Commodity Data Cleaning System

- Citation: ['Michele Dallachiesa', 'Amr Ebaid', 'Ahmed Eldawy', 'Ahmed Elmagarmid', 'Ihab F. Ilyas', 'Mourad Ouzzani', 'Nan Tang']; SIGMOD 2013:541–552; 2013.
- Status: Published peer-reviewed research conference paper; dashboard feedback details explicitly deferred to future work in this paper.
- Source: [NADEEF: A Commodity Data Cleaning System](https://www.hbku.edu.qa/sites/default/files/nadeefsigmod2013.pdf); DOI [10.1145/2463676.2465327](https://doi.org/10.1145/2463676.2465327).
- Read: Abstract/introduction/contributions pp541–542; architecture/updater/lineage Sec.2.2 p544; violation/candidate-fix definitions Sec.3 pp544–545; repair overview Sec.5.
- Actual contribution: Extensible rule interface with black-box detection/fix methods and holistic repair cores across heterogeneous constraints.
- Overlap: Candidate fixes specify conjunctive cell assignments that must be taken together. Updater selects committed changes; metadata management is intended to retain full lineage and change order.
- Distinction/unestablished: The paper defers dashboard-feedback details, so exact human review binding is unestablished. Conjunctive repair semantics do not establish atomic complete successor-plus-evidence writes or exact immediate sources of unchanged fields.
- Internal novelty risk: medium - A clear predecessor for candidate fixes, commit selection, and lineage; insufficient documented human authorization protocol for full anticipation.

## holoclean2017 - HoloClean: Holistic Data Repairs with Probabilistic Inference

- Citation: ['Theodoros Rekatsinas', 'Xu Chu', 'Ihab F. Ilyas', 'Christopher Ré']; Proceedings of the VLDB Endowment 10(11):1190–1201; 2017.
- Status: Published peer-reviewed research article; cite published version, not arXiv 1702.00820.
- Source: [HoloClean: Holistic Data Repairs with Probabilistic Inference](https://www.vldb.org/pvldb/vol10/p1190-rekatsinas.pdf); DOI [10.14778/3137628.3137631](https://doi.org/10.14778/3137628.3137631).
- Read: Abstract/introduction pp1190–1191; contribution and problem/solution Sec.2 p1192; factor graphs Sec.3 p1193.
- Actual contribution: Compiles heterogeneous constraint, reference-data, and statistical evidence into a scalable probabilistic repair model.
- Overlap: Distinguishes original observed cell value vc, latent true value vc*, and inferred value vhatc; models each cell and produces a proposed cleaned dataset.
- Distinction/unestablished: True/inferred values are statistical repair variables, not human authorized xa. The audited methods do not establish exact proposal-bound approval, retained original proposal after correction, fresh commit predecessor, or complete exact field-source evidence.
- Internal novelty risk: low - Strong repair-generation baseline but farther from the authorization/commit relation; value quality and exact evidence identity are different evaluation targets.

## dbwiki2011 - The Database Wiki Project: A General-Purpose Platform for Data Curation and Collaboration

- Citation: ['Peter Buneman', 'James Cheney', 'Sam Lindley', 'Heiko Mueller']; ACM SIGMOD Record 40(3):15–20; 2011.
- Status: Published technical prototype article; university research metadata explicitly labels peer-reviewed. Companion SIGMOD 2011 demo read as corroboration, not a separate selected work..
- Source: [The Database Wiki Project: A General-Purpose Platform for Data Curation and Collaboration](https://sigmodrecord.org/publications/sigmodRecord/1109/pdfs/04.prototypes.buneman.pdf); DOI [10.1145/2070736.2070740](https://doi.org/10.1145/2070736.2070740).
- Read: Abstract/introduction/contributions pp15–16; storage Sec.2.1 pp16–17; query Sec.2.3 p18; node IDs, atomic updates, and provenance Sec.Sec.3.1–3.3 pp18–20.
- Actual contribution: Combines structured wiki editing with persistent item identities, archived versions, fine-grained provenance, annotation, and history/provenance querying.
- Overlap: Each item has provenance; atomic subtree/attribute edits retain past values and unchanged tree structure; node URLs provide persistent IDs and source references.
- Distinction/unestablished: Machine proposal and exact human review target are not established. Atomic tree edit does not prove the manuscript's complete relation successor-plus-total-evidence transaction. Exact review occurrences cannot be inferred from node/value identity: repeated values reuse text nodes and no-value-change edits are deliberately not recorded.
- Internal novelty risk: high - Strong challenge to broad claims of new atomic, versioned, fine-grained curation provenance. The specific candidate-review-commit contract remains unestablished.

## 2608.11632 - Beyond Memory: A Transactional Continuity Kernel for Long-Lived AI Agents

- Citation: ['Jun He', 'Deying Yu']; arXiv preprint; 2026.
- Status: Official abs has no journal reference/peer-reviewed venue. Exact-title publication-update searches found no verified published counterpart; this is a bounded search result, not proof of nonpublication..
- Source: [Beyond Memory: A Transactional Continuity Kernel for Long-Lived AI Agents](https://arxiv.org/abs/2608.11632); DOI [10.48550/arXiv.2608.11632](https://doi.org/10.48550/arXiv.2608.11632).
- Read: Abstract; Sec. 1; Sec. 2.1-2.3; Sec. 3.1-3.5; Sec. 4.3; Sec. 5.1-5.3; Appendix A.2; Appendix B.1-B.2; Appendix C.2-C.3
- Actual contribution: Governed authoritative branch activation with sealed candidates, signed evidence, fresh exact predecessors, pre-state authorization, receipts, and a complete atomic accepted unit.
- Overlap: A direct predecessor for the broad core contract, including signed approver evidence and human preparation. Calling it only memory continuity would obscure substantial overlap.
- Distinction/unestablished: DKE's mandatory human per-field decisions, separate xc/xa correction objects, total exact per-field source preservation, and five-class conditional irredundancy are not established by the inspected CK specification. A configurable CK could implement them; that does not establish they are novel.
- Internal novelty risk: high - Already specifies the exact-proposal/exact-head/pre-state-authority/atomic-complete-unit admission boundary; DKE must show more than an application-level instantiation.

## 2607.27834 - MemTxn: A Transaction Boundary for Source-Supported Updates and Complete-State Recovery in Agent Memory

- Citation: ['Hanshuai Cui', 'Zhiqing Tang', 'Zhi Yao', 'Fanshuai Meng', 'Qianli Ma', 'Weijia Jia']; arXiv preprint; 2026.
- Status: Official abs has no journal reference/peer-reviewed venue. Exact-title publication-update searches found no verified published counterpart; this is a bounded search result, not proof of nonpublication..
- Source: [MemTxn: A Transaction Boundary for Source-Supported Updates and Complete-State Recovery in Agent Memory](https://arxiv.org/abs/2607.27834); DOI [10.48550/arXiv.2607.27834](https://doi.org/10.48550/arXiv.2607.27834).
- Read: Abstract; Introduction; Method: Overview; System model and trust boundary; Source-supported update admission; Conflict-conditioned version resolution; Durable audit and complete-state recovery; Contract implications and complexity
- Actual contribution: Ordered lexical source-support admission, chronology-based version visibility, and durable recovery of the full application-visible active map.
- Overlap: An answer-model-external commit boundary, append-only versions, source-bearing proposals, and unchanged state on rejected writes.
- Distinction/unestablished: No inspected human candidate-bound authorization, separate corrected xa, or total unchanged-field source object contract; concurrency is explicitly outside its guarantee.
- Internal novelty risk: medium - Source-governed activation, version lineage, atomic pointers, and complete active-map recovery already exist; exact human/candidate/field relation remains unestablished.

## 2608.02843 - MutMem: Cryptographically Authorized Mutation in Persistent Agent Memory

- Citation: ['Walid Saidi']; arXiv preprint; 2026.
- Status: Official abs has no journal reference/peer-reviewed venue. Exact-title publication-update searches found no verified published counterpart; this is a bounded search result, not proof of nonpublication..
- Source: [MutMem: Cryptographically Authorized Mutation in Persistent Agent Memory](https://arxiv.org/abs/2608.02843); DOI [10.48550/arXiv.2608.02843](https://doi.org/10.48550/arXiv.2608.02843).
- Read: Abstract; Sec. 1-1.1; Sec. 2.1-2.4; Sec. 3; Sec. 4; Sec. 5.1-5.7; Sec. 6.1-6.4; Sec. 7; Sec. 11.1-11.3
- Actual contribution: Retention-preserving housekeeper-authorized memory reweighting and signed epistemic label changes, with portable provenance/recall verification.
- Overlap: Explicit version-preserving corrections; signatures bind tenant, memory, old/new weights and provenance; writer checks current predecessor/live state.
- Distinction/unestablished: A human decision for each AI field candidate, preserved xc plus corrected xa, complete record successor and total field source equality are not established. Autonomous housekeeper mutation is explicitly its owner.
- Internal novelty risk: medium - Retained correction versions, exact signed old/new transitions, signer epochs, predecessor checks, and atomic mutation already cover key ingredients.

## 2608.08236 - LatticeMind: A Conflict-Aware Memory Primitive for Multi-Agent Systems

- Citation: ['Heng Zhou', 'Lian Zhang', 'Yutao Fan', 'Tiancheng He', 'Siki Chen', 'Hejia Geng', 'Philip Torr', 'Zhenfei Yin']; arXiv preprint; 2026.
- Status: Official abs has no journal reference/peer-reviewed venue. Exact-title publication-update searches found no verified published counterpart; this is a bounded search result, not proof of nonpublication..
- Source: [LatticeMind: A Conflict-Aware Memory Primitive for Multi-Agent Systems](https://arxiv.org/abs/2608.08236); DOI [10.48550/arXiv.2608.08236](https://doi.org/10.48550/arXiv.2608.08236).
- Read: Abstract; Sec. 1; Sec. 2.1-2.3; Sec. 3.1-3.3; Algorithm 1; Sec. 4.3; Appendix A.10-A.11
- Actual contribution: Structured conflict-aware persistent memory with symbolic checking, selective LLM reconciliation, supersession/contestation, and scope-local software state slots.
- Overlap: Separate proposed/confirmed states, typed slots, source/evidence metadata, retained losing candidates and rendered provenance transitions.
- Distinction/unestablished: Human exact-instance approval and complete atomic successor contract are not established. Equal normalized values explicitly merge sources instead of preserving one prior source object.
- Internal novelty risk: medium - Explicit persisted statuses, per-slot update decisions and provenance preserve disagreement; its equal-value source-merge policy is a concrete different contract.

## 2609.02127 - Stored Is Not Supported: Typed Provenance and Assertion Guardrails for Persistent AI Agents

- Citation: ['Jun He', 'Deying Yu']; arXiv preprint; 2026.
- Status: Official abs has no journal reference/peer-reviewed venue. Exact-title publication-update searches found no verified published counterpart; this is a bounded search result, not proof of nonpublication..
- Source: [Stored Is Not Supported: Typed Provenance and Assertion Guardrails for Persistent AI Agents](https://arxiv.org/abs/2609.02127); DOI [10.48550/arXiv.2609.02127](https://doi.org/10.48550/arXiv.2609.02127).
- Read: Abstract; Sec. 1; Sec. 2.1-2.7; Sec. 3.1-3.5; Sec. 4.1-4.4; Sec. 5 scope; Appendix A.1
- Actual contribution: Typed provenance DAG and role promotion, source-root independence, head-bound resolver witnesses and outward assertion mediation.
- Overlap: Preserved immutable source vertices, fresh target claims and exact dependency traces; support/authority differs from storage presence.
- Distinction/unestablished: A mandatory human field acceptance/correction pipeline or total per-field source-preservation recurrence is not established. It explicitly takes atomic accepted-state ordering as an assumption.
- Internal novelty risk: medium - Exact immutable dependencies and fresh role-promoted targets already separate retained AI priors from accountable claims; atomicity is inherited from CK rather than its contribution.

## 2609.01235 - MutMem-V2: Cryptographically Authorized Mutation in Persistent Agent Memory Portable Verification and Reproducible Evidence

- Citation: ['Walid Saidi']; arXiv preprint; 2026.
- Status: Official abs has no journal reference/peer-reviewed venue. Exact-title publication-update searches found no verified published counterpart; this is a bounded search result, not proof of nonpublication..
- Source: [MutMem-V2: Cryptographically Authorized Mutation in Persistent Agent Memory Portable Verification and Reproducible Evidence](https://arxiv.org/abs/2609.01235); DOI [10.48550/arXiv.2609.01235](https://doi.org/10.48550/arXiv.2609.01235).
- Read: Abstract; Sec. 1-3; Sec. 4.1-4.4; Sec. 5; Sec. 6.1-6.3; Sec. 7.1; Sec. 11-12
- Actual contribution: Portable exact-byte recall/mutation evidence envelopes, external trust anchors, complete per-result membership, independent verifier parity and signed-noop terminal.
- Overlap: Object/identity/provenance substitution detection and exact terminal closure strengthen MutMem beyond the original citation.
- Distinction/unestablished: No mandatory human candidate-bound field authorization or total per-field successor source function; historical V1 benchmarks are expressly not current V2 reruns.
- Internal novelty risk: medium - Direct update to existing MutMem citation adds exact cross-object identity, closed failure classes and conformance; does not add a human field-candidate transaction.

## 2607.23929 - MemTX: Transactional Belief Commit for Stateful Agent Memory

- Citation: ['Xiaoyang Li', 'Yiqi Wang', 'Haohui Lu', 'Zhi Chen', 'Mo Li', 'Pingan Song', 'Mingkai Zheng', 'Taotao Cai']; arXiv preprint; 2026.
- Status: Official abs has no journal reference/peer-reviewed venue. Exact-title publication-update searches found no verified published counterpart; this is a bounded search result, not proof of nonpublication..
- Source: [MemTX: Transactional Belief Commit for Stateful Agent Memory](https://arxiv.org/abs/2607.23929); DOI [10.48550/arXiv.2607.23929](https://doi.org/10.48550/arXiv.2607.23929).
- Read: Latest v2 Abstract; Sec. 1; Sec. 3.1-3.6; Sec. 4 conformance scope; Sec. 5 ablations; Appendix H.3
- Actual contribution: Staged belief lifecycle, snapshot/risk-based reads, ordered commit validation, irreversible-action gating and typed cascading repair.
- Overlap: Persisted candidate records with source/permissions/DAG, stale late-write rejection, equal-authority cross-source quarantine for user review.
- Distinction/unestablished: Exact instance-bound human review for all fields and preserved xc/corrected xa are not established. Transactions explicitly may partially commit. Evaluation sometimes identifies records by value strings, not record IDs.
- Internal novelty risk: medium - A close staged-belief/admission/stale-write/review/derivation system; its partial commits and conditional user review differ from complete human field admission.

## fett2023dpop - OAuth 2.0 Demonstrating Proof of Possession (DPoP)

- Citation: Daniel Fett; Brian Campbell; John Bradley; Torsten Lodderstedt; Michael Jones; David Waite; IETF RFC 9449; 2023.
- Status: standard.
- Source: [OAuth 2.0 Demonstrating Proof of Possession (DPoP)](https://www.rfc-editor.org/rfc/rfc9449.html); DOI [10.17487/RFC9449](https://doi.org/10.17487/RFC9449).
- Read: Abstract, introduction, 4.2–4.3, 11.7
- Actual contribution: Sender-constrained OAuth tokens and request method/URI proof checks, with replay controls.
- Overlap: Binding scope and replay prevention at request layer.
- Distinction/unestablished: Original machine value, corrected human value, complete field-source successor are not the protocol's semantic objects. DPoP expressly permits additional signed claims; extension capability is acknowledged.
- Internal novelty risk: low - Method analogy, not a correction-admission competitor.

## backman2024httpsignatures - HTTP Message Signatures

- Citation: Annabelle Backman; Justin Richer; Manu Sporny; IETF RFC 9421; 2024.
- Status: standard.
- Source: [HTTP Message Signatures](https://www.rfc-editor.org/rfc/rfc9421.html); DOI [10.17487/RFC9421](https://doi.org/10.17487/RFC9421).
- Read: Abstract, introduction, 1.4, 2.3, 3, 7.2.1 and 7.2.8
- Actual contribution: Detached signatures/MACs over declared HTTP components; application profiles choose required coverage and verification rules.
- Overlap: Application-specific binding and protection of selected message components, including a content digest when required.
- Distinction/unestablished: Human review target and post-commit field provenance require an application relation, not an implication of a message signature.
- Internal novelty risk: low - Established binding foundation; prevents claiming request binding as a new security primitive.

## owasp2026transactionauthorization - Transaction Authorization Cheat Sheet

- Citation: OWASP Foundation; OWASP Cheat Sheet Series; accessed 27 September 2026; 2026.
- Status: authoritative practitioner guidance, undated living document.
- Source: [Transaction Authorization Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Transaction_Authorization_Cheat_Sheet.html); no DOI claimed.
- Read: Purpose, introduction, functional 1.1/1.5, non-functional 2.1–2.3/2.5–2.10
- Actual contribution: Significant transaction-data acknowledgement, server-side authorization, controlled operation states, invalidation on modification, execution-time final gate and operation-unique credentials.
- Overlap: Direct precedent for server-held review/operation consistency, TOCTOU protection, replay prevention and protected approval data.
- Distinction/unestablished: The inspected guidance does not specify the manuscript's dual-value Correction and total copied-forward field-source relation. Unique credentials do not alone establish handling of value-identical proposal instances.
- Internal novelty risk: medium - E2 binding principle is established guidance; describe E2 as applying/testing an admission-boundary design.

## jackson2002alloy - Alloy: A Lightweight Object Modelling Notation

- Citation: Daniel Jackson; ACM TOSEM 11(2):256–290; 2002.
- Status: peer-reviewed journal.
- Source: [Alloy: A Lightweight Object Modelling Notation](https://groups.csail.mit.edu/sdg/pubs/2002/alloy-journal.pdf); DOI [10.1145/505145.505149](https://doi.org/10.1145/505145.505149).
- Read: Abstract, introduction, 2.1–2.2, kernel semantics
- Actual contribution: Relational structural specification with simulation and counterexample search within finite scopes.
- Overlap: Specification/analysis method.
- Distinction/unestablished: Correction admission relation is an application specification, not an Alloy language contribution.
- Internal novelty risk: low - Method precedent.

## torlak2007kodkod - Kodkod: A Relational Model Finder

- Citation: Emina Torlak; Daniel Jackson; TACAS, LNCS 4424:632–647; 2007.
- Status: peer-reviewed conference.
- Source: [Kodkod: A Relational Model Finder](https://groups.csail.mit.edu/sdg/pubs/2007/tacas07-torlak-jackson.pdf); DOI [10.1007/978-3-540-71209-1_49](https://doi.org/10.1007/978-3-540-71209-1_49).
- Read: Abstract, introduction, 3 model finding, 4 translation
- Actual contribution: SAT-based finite relational model finding with partial instances and compact encodings.
- Overlap: Solver foundation.
- Distinction/unestablished: No application-specific correction/authorization claim is attributed to this work.
- Internal novelty risk: low - Method precedent.

## marinov2001testera - TestEra: A Novel Framework for Automated Testing of Java Programs

- Citation: Darko Marinov; Sarfraz Khurshid; ASE:22–31; 2001.
- Status: peer-reviewed conference.
- Source: [TestEra: A Novel Framework for Automated Testing of Java Programs](https://mir.cs.illinois.edu/marinov/publications/MarinovKhurshid01TestEra.pdf); DOI [10.1109/ASE.2001.989787](https://doi.org/10.1109/ASE.2001.989787).
- Read: Abstract and introduction p22, example p23, framework 3.1 p24 and translation 3.2
- Actual contribution: Bounded relational test generation, concretization into program inputs and abstraction of outputs for specification checking.
- Overlap: Formal–concrete testing method.
- Distinction/unestablished: The manuscript tests selected persisted-state projections, not TestEra-style exhaustive bounded input enumeration.
- Internal novelty risk: low - Method precedent; cannot claim abstraction/concretization as novelty.

## buneman2001whywhere - Why and Where: A Characterization of Data Provenance

- Citation: See verified manuscript bibliography.; See verified manuscript bibliography.; 2001.
- Status: Published peer-reviewed work; survey identified as synthesis..
- Source: [Why and Where: A Characterization of Data Provenance](https://www.pure.ed.ac.uk/ws/files/16509989/Why_and_Where_A_Characterization_of_Data_Provenance.pdf); DOI [10.1007/3-540-44503-X_20](https://doi.org/10.1007/3-540-44503-X_20).
- Read: Abstract; introduction; Sections 2, 4, 5.1 and 6.
- Actual contribution: Defines why witness bases and where source locations for query-derived data.
- Overlap: Enforcement or provenance foundation.
- Distinction/unestablished: The application-specific Correction and human review relation was not assessed as a claim of this source.
- Internal novelty risk: low - Foundation; no novelty attributed to its underlying mechanism.

## cheney2009provenance - Provenance in Databases: Why, How, and Where

- Citation: See verified manuscript bibliography.; See verified manuscript bibliography.; 2009.
- Status: Published peer-reviewed work; survey identified as synthesis..
- Source: [Provenance in Databases: Why, How, and Where](https://homepages.inf.ed.ac.uk/jcheney/publications/provdbsurvey.pdf); DOI [10.1561/1900000006](https://doi.org/10.1561/1900000006).
- Read: Abstract; introduction pp380-382; 1.1.1-1.1.3; Sections 3 and 4.1.
- Actual contribution: Synthesizes why/how/where provenance, applications and relationships.
- Overlap: Enforcement or provenance foundation.
- Distinction/unestablished: The application-specific Correction and human review relation was not assessed as a claim of this source.
- Internal novelty risk: low - Foundation; no novelty attributed to its underlying mechanism.

## gray1981transaction - The Transaction Concept: Virtues and Limitations

- Citation: See verified manuscript bibliography.; See verified manuscript bibliography.; 1981.
- Status: Published peer-reviewed work; survey identified as synthesis..
- Source: [The Transaction Concept: Virtues and Limitations](https://web.stanford.edu/class/archive/cs/cs240/cs240.1236/old/sp2014/readings/Gray81.pdf); no DOI claimed.
- Read: Abstract; introduction p144; general transaction model p145; implementation overview p146.
- Actual contribution: Defines atomic, durable, consistency-preserving state transformations.
- Overlap: Enforcement or provenance foundation.
- Distinction/unestablished: The application-specific Correction and human review relation was not assessed as a claim of this source.
- Internal novelty risk: low - Foundation; no novelty attributed to its underlying mechanism.

## US20200117643A1 - Data curation system with version control for workflow states and provenance

- Citation: Gluzman Peregrine et al. (Tamr); US patent application publication; 2020.
- Status: Patent disclosure, not peer-reviewed research; no legal novelty verdict..
- Source: [Data curation system with version control for workflow states and provenance](https://patents.google.com/patent/US20200117643A1/en); no DOI claimed.
- Read: Abstract/overview; action phases; provenance; state history; linkage approvals; claims 1, 7, 8, 11.
- Actual contribution: Machine proposals, operator-approved changes, versioned curation states and element provenance form a broad neighboring design.
- Overlap: Approval precedes new state creation; unchanged presented data govern continuing approval validity.
- Distinction/unestablished: Exact value-identical instance rejection and the xc/xa field authorization tuple were not established. This is a serious further-comparison lead.
- Internal novelty risk: high - Broad joint design overlap; retained in the internal audit.

## Coverage gaps and stopping decision

AUDIT 2018 is highly relevant but only abstract/publisher preview was available, including a failed author-shared read-online link. No method-level absence is inferred. Workflow-role constraints and some maker-checker practice sources were discovered without adequate method access; they are not promoted into mechanism comparisons. The read 2015 UPA and commercial-integrity work supply affirmative approval precedents. Patent disclosures and frontier reconstruction papers are retained as challengers, not as peer-reviewed confirmations.

The sources read justify a narrower relation-level framing and the existing experimental separator. They do not justify "first", universal necessity, minimality, uniqueness, or superiority over all alternatives.
