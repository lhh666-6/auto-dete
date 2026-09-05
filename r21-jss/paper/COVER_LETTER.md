# Cover letter — Journal of Systems and Software

[AUTHOR INPUT NEEDED: submission date]

Dear Editors of the *Journal of Systems and Software*,

Please consider our manuscript, “Authoritative-State Admission for AI-Derived Updates: Failure
Distinguishability, Transactional Realization, and Evaluation,” as a Research Paper in the
*Journal of Systems and Software*.

The manuscript addresses a software-engineering problem that arises when AI-generated proposals
can enter persistent operational records. Once committed, these values become authoritative state
used by downstream software. We therefore study the architecture, verification, and validation of
the admission boundary itself: which persisted candidate was authorized, for which record context
and version, which value became durable, and how that decision can be traced later.

The paper identifies correction-aware authoritative-state admission as distinct from authorized
mutation. It characterizes five observable information classes needed to distinguish candidate
substitution, correction erasure, stale replay, partial successors, and source ambiguity. The
transactional Python/SQLite realization binds a human authorization to the exact persisted
candidate and an explicit authorized value, commits one complete multi-field successor atomically,
and preserves both the machine proposal and exact per-field source history when the reviewer
authorizes a different value.

The validation connects several evidence layers to this same authoritative-state relation. Bounded
Alloy analysis exercises legal, ablated, and attack states; a separate projection checks selected
persisted executions; an independent catalogue covers declared implementation faults; and
stateful, concurrency, lifecycle, harness, and repeated live-agent experiments test the implemented
capability boundary. The Final live-agent matrix covers three qualified model configurations,
three prompt variants, fourteen scenarios, and 1,260 planned executions. Benign task completion
was 320/335, while no unauthorized authoritative mutation occurred in 899 evaluable challenges
(one-sided 95% upper bound 0.33%); 93 runtime failures remain separately reported. A
persistence-equivalent comparator confirms matching relational post-states, while form-scoped
trace loading reduces the measured database-query shape without changing the tested trace results.

This contribution aligns directly with JSS topics in Software Engineering for AI systems and in
methods and tools for software architecture, verification and validation, and testing. Its focus is
software architecture and evidence for admission integrity in AI-assisted record systems—not a
claim of general AI safety, model accuracy, or prompt-injection security. The manuscript also
provides a documented artifact structure linking source, formal models, experiment configuration,
raw receipts, normalized paper inputs, and deterministic tables and figures.

[AUTHOR INPUT NEEDED: confirm that the manuscript is original, is not under review elsewhere, and
has been approved by all authors.]

The complete reproducibility package is publicly available at
https://github.com/lhh666-6/auto-dete/tree/r21-jss-2026-09-05/r21-jss. It includes
the manuscript source and PDF, clean implementation and experiment code, formal
models, all final run records, normalized inputs, and SHA-256 manifests.

The author declares no competing interests and no external funding. The manuscript
contains the final factual disclosure of generative-AI assistance.

Thank you for considering this manuscript. We believe it will interest JSS readers working on
software architecture, formal and empirical validation, AI-enabled systems, transactional
software, and reproducible software-engineering evidence.

Sincerely,

Liang Hanghao  
College of Computer Science and Electronic Engineering, Hunan University  
Changsha, China  
Email: zwu691403@gmail.com  
[AUTHOR INPUT NEEDED: postal address and postcode, if required by the submission system]
