# r27 positive trace-completeness assertion and mutation control

This directory records the r27 response to the Alloy review finding that the
bounded model had no positive assertion from a legal Full admission to a
trace-complete post-state, and no mutation test for the post-state certificate
binding.

## Positive assertion

`formal/alloy/batch/auto_decte_batch.als` now defines

```
assert LegalAdmissionTraceCompleteUnderWellFormedPre {
  all e : BatchAdmissionEvent |
    legalAdmission[e, Full] and
    (all r : Record, f : Field |
      some e.pre.committedSource[r][f] => traceComplete[e.pre, r, f]) and
    (all i : e.items |
      no t : e.pre.transitions |
        t.targetRecord = i.targetRecord and
        t.targetField = i.targetField and
        t.toVersion = successor[e.pre.currentVersion[e.targetRecord]])
    => all i : e.items |
         traceComplete[e.post, i.targetRecord, i.targetField]
}
```

and the S1/S2 catalogues add a `check` for it. The assertion is deliberately
conditional. An unconditional `legalAdmission[Full] => traceComplete` is false
in the current bounded model: the permissive base effect admits a legal
admission from a pre-state that already contains a stray transition to the
successor version, after which the committed source is not unique and
`traceComplete` fails. The two explicit preconditions are exactly the
well-formedness properties that the concrete service enforces through
predecessor trace validation, the unique (form_id, created_version, field_key) database constraint, and transactional compare-and-swap. The r27 bounded catalogue
therefore records the assertion in a batch catalogue that now holds 36 commands per profile (72 total), with expected UNSAT for
the new assertion.

## Mutation control

The mutation is the single removal of the post-state certificate-binding
conjunct

```
i.transition.certificate = i.certificate
```

from `transitionItemOk`. `auto_decte_batch_trace_mutation.als` is the S1 model
with that conjunct removed; `trace_mutation_check.als` opens it and checks
`LegalAdmissionTraceCompleteUnderWellFormedPre`. The check is SAT:
`LegalAdmissionTraceCompleteUnderWellFormedPre-solution-0.txt` contains the
counterexample and `receipt.json` is the Alloy receipt. With the conjunct
present (the production model), the same check is UNSAT. This demonstrates that
the positive assertion is sensitive to the post-state certificate binding whose
absence the previous suite could not detect.

## Reproduction

From `r27-jss/current/`, with the bundled JRE and Alloy jar:

```powershell
& 'formal/alloy/batch/run_batch_alloy.ps1' -FreezeId '<new-freeze-id>'
```

The main catalogue is in `formal/alloy/batch/raw-results/<id>/`, where `<id>` is named by `formal/alloy/batch/ACTIVE_FREEZE.txt` (currently `2026-09-11-trace-witness`).
To reproduce the mutation counterexample directly:

```powershell
& 'tools/jre21/jdk-21.0.12.1+1-jre/bin/java.exe' -jar tools/alloy-6.2.0.jar exec -q `
  -c LegalAdmissionTraceCompleteUnderWellFormedPre `
  -t text -o <out-dir> evidence/r27-trace-mutation/trace_mutation_check.als
```

The counterexample file is a diagnostic artifact, not a claim that the
production model contains the mutation.
