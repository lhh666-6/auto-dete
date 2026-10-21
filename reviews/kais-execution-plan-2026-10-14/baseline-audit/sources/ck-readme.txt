# Continuity Kernel bounded model

`bounded_model.py` is a standard-library-only bounded explorer for owner-first
proposal admission, exact requirement coverage, the four dispositions,
stage-aware canonicalization/target failures, expiry-before-Defer, the normative
first-failing activation order, stage-prefix receipt fields, candidate/effect
binding, distinct initial and final activation freshness, complete
kind-specific accepted-unit schemas and prospective-unit construction,
proposal/effect reclamation, authority evolution, handoff/retargeting, acyclic
head/lineage/receipt/handoff construction, creation-context BranchCreate
admission, genesis-parent validation, append-only Prepared, SourceFenced,
Aborted, and TargetActive revisions, explicit pointer clearing, typed outcome
and handoff-result keys, lifecycle receipts, total C-tag abstract target
activation, restoration, and deterministic context-counter charging. It is not a storage
implementation, conformance suite, or performance benchmark.

The finite model has one branch, one shared admission row, one proposal scope
owned by principal 0, one adversarial principal, proposal identifiers 0--12,
effect identifiers 0--3, source writer 0, target writers 1--2, integer head and
authority versions reached within seven transitions, and fixed finite request,
coverage, receipt, lifecycle, and decision variants. Archive inclusion roots,
cryptography, canonicalization, and persistence are abstracted.

Run it with:

```sh
python src/transactional_continuity_kernel/bounded_model.py
```

Expected output with the checked-in model is:

```text
bounded_model_ok states=2808230 transitions=5526474 max_depth=7 pids=13 eids=4 principals=2 branches=1 shared_rows=1
```

This output was reproduced with CPython 3.13.9. The exact executed working-tree
artifact is identified by its digest. It imports only Python's `__future__`,
`collections`, `dataclasses`, and `typing` modules. The model source SHA-256 is
`af28a28f195493009a53cce1aeca43c7fc4937871688ad1e9160ed3412b4fece`.
The script fails on an invariant violation or an unreached coverage goal.
