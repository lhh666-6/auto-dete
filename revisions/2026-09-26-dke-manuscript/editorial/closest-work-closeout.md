# Five closest works: source fidelity check

Checked 27 September 2026 against the cited primary papers. This is a check of the manuscript's descriptions, not a claim that the literature search proves universal novelty. No references were added or removed.

| Work | Primary-source location | Description checked in Section 2 | Finding |
|---|---|---|---|
| [Mershad et al. (2015)](https://www.cs.purdue.edu/homes/aref/papers/ic2e2015.pdf) | IV-B, Approving Updates, PDF p. 4 | Pending cell history, approval by cell identity plus record timestamps or a timestamp range | Accurate. The text acknowledges version-specific content approval. |
| [Guided Data Repair](https://www.vldb.org/pvldb/vol4/p279-yakout.pdf) | 4.2, Learning User Feedback | Confirm, reject, retain, and a user-supplied replacement represented as another repair | Accurate. Human correction is acknowledged as an existing capability. |
| [Falcon](https://dbgroup.cs.tsinghua.edu.cn/ligl/papers/sigmod2016-clean.pdf) | 5.2, Closed Rule Sets, printed p. 900 | Rules affecting the same tuples on a dataset can differ in semantic validity | Accurate. The text acknowledges this precedent without equating rule validity with candidate-instance authorization. |
| [DBWiki](https://sigmodrecord.org/publications/sigmodRecord/1109/pdfs/04.prototypes.buneman.pdf) | 2, querying; 3.1, URLs; 3.2, update operations | Fine-grained node identifiers, version/provenance queries, and atomic edits | Accurate. Stable node URLs are distinguished from path-based URLs, which the source says can change. |
| [Continuity Kernel v1](https://arxiv.org/html/2608.11632v1) | 2.2; 3.1–3.2; 3.5 | Proposal identity, predecessor, pre-state authority, signed approval/evaluation evidence, lineage, atomic accepted unit, and human interaction during preparation | Accurate. Section 2 acknowledges this close activation contract and does not claim that it cannot encode the application's correction relation. |

The manuscript's contribution remains the specified field-level correction relation and its failure-distinguishing characterization, supported by the policy comparison. Existing approval, provenance, transaction, and activation components are acknowledged. No assertion of being the universally necessary, minimal, unique, or complete design was added.

Primary PDFs/text used during checking are retained in the ignored local audit cache. Tool access to the GDR/Falcon PDFs was intermittent; the locally cached primary-source text was also inspected. Continuity Kernel remains cited as a preprint, with its version pinned.
