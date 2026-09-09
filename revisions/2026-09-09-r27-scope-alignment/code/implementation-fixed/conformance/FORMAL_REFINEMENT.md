# Executable Formal–Concrete Refinement (R2)

`tests/conformance/alloy_projection.py` is an independent test-side adapter
from persisted SQLite authority rows to the conservative batch Alloy model.
It does not invoke the production admission validator. For each committed
case it serializes raw record, certificate, evidence, decision/binding,
transition, value, version, and source-pointer relations into canonical JSON;
the generated Alloy wrapper fixes an exact instance and asks whether
`legalAdmission[event, Full]` is satisfiable.

Rejected cases are captured before and after the attempted call. Projection
fails if any record version, decision, binding, transition, certificate,
evidence identity, form version, or review status changes. Their Alloy wrapper
requires a `rejectedAdmission` stutter and a failing Full contract for the
attempted item relation.

The active freeze is named by `ACTIVE_REFINEMENT_FREEZE.txt`. It contains nine
SAT lifecycle/rejection projections and twenty UNSAT single-dimension mapping
mutants. Every case retains `projection.json`, `concrete_projection.als`, Alloy
stdout/stderr, and `alloy-result/receipt.json`; `manifest.json` hashes the three
semantic artifacts. Verify it with:

```powershell
uv run python conformance/verify_formal_refinement_records.py
```

The concrete implementation deliberately admits only the value-changing
subset after its first certificate-era snapshot. The formal relation permits
legal same-value admissions to preserve conservative equivalence with the
historical singleton model. R2 therefore establishes bounded refinement for
the selected concrete traces; it does not claim completeness, unbounded proof,
or equivalence of the concrete and formal behavior sets.
