module trace_mutation_check

// Mutation control for the r27 positive trace-completeness assertion.
// The only change relative to formal/alloy/batch/auto_decte_batch.als is that
// transitionItemOk omits the post-state certificate-binding conjunct
// `i.transition.certificate = i.certificate`. The production model keeps it.
// With the conjunct removed, LegalAdmissionTraceCompleteUnderWellFormedPre
// finds a counterexample (SAT); with the conjunct present it is UNSAT.
open auto_decte_batch_trace_mutation

check LegalAdmissionTraceCompleteUnderWellFormedPre for 2 Record, 3 Field, 6 Version, 5 Candidate, 5 Certificate, 5 Authorization, 5 Evidence, 5 Value, 3 Producer, 3 Principal, 5 CertId, 4 State, 4 Event, 6 AdmissionItem, 6 Transition, 2 EvidenceContent, 3 EvidenceLocator
