// Auto-Decte TargetSystem_vNext formal model.
// Certificate-Bound Non-Substitutable Admission of AI-Derived Candidate Updates
// into Versioned Authoritative Records.
// Phase B Alloy implementation, after G1 PASS.
// Bounded-model discipline: report "no counterexample within explored scope".

// ---------------------------------------------------------------------------
// Basic domains
// ---------------------------------------------------------------------------
sig Value {}
sig Record {}
sig Field {}
sig Producer {}
sig Principal {}

one sig PrincipalRegistry {
  authorized : set Principal
}

sig EvidenceContent {}
sig EvidenceLocator {}

sig Evidence {
  record  : one Record,
  content : one EvidenceContent,
  locator : one EvidenceLocator
}

pred sameEvidenceIdentity[e1, e2 : Evidence] {
  e1.content = e2.content and e1.locator = e2.locator
}

sig CertId {}

// Ordered Version atoms instead of integer arithmetic.
sig Version {
  record : one Record,
  succ   : lone Version
}

fact versionStructure {
  // No cycles.
  no v : Version | v in v.^succ
  // A version's successor belongs to the same record.
  all v : Version | no v.succ or v.succ.record = v.record
  // Each version has at most one predecessor.
  all v : Version | lone u : Version | u.succ = v
  // Each record has exactly one initial version (no predecessor).
  all r : Record | one v : Version | v.record = r and v not in Version.succ
}

fun initialVersion[r : Record] : one Version {
  { v : Version | v.record = r and v not in Version.succ }
}

fun successor[v : Version] : lone Version {
  v.succ
}

pred olderThan[old, cur : Version] {
  cur in old.^succ
}

// ---------------------------------------------------------------------------
// Candidate, certificate, authorization, transition
// ---------------------------------------------------------------------------
sig Candidate {
  targetRecord    : one Record,
  targetField     : one Field,
  evidence        : one Evidence,
  expectedVersion : one Version,
  value           : one Value,
  producer        : one Producer
}

sig Certificate {
  candidate : one Candidate,
  certId    : one CertId
}

pred certModeledContentEqual[c1, c2 : Certificate] {
  c1.candidate.targetRecord     = c2.candidate.targetRecord
  c1.candidate.targetField      = c2.candidate.targetField
  c1.candidate.value            = c2.candidate.value
  c1.candidate.evidence.content = c2.candidate.evidence.content
  c1.candidate.evidence.locator = c2.candidate.evidence.locator
  c1.candidate.expectedVersion  = c2.candidate.expectedVersion
  c1.candidate.producer         = c2.candidate.producer
}

fact certIdentityFacts {
  // Safe one-way abstraction: modeled difference => different primitive id.
  all c1, c2 : Certificate |
    not certModeledContentEqual[c1, c2] => c1.certId != c2.certId
  // Canonical id is a row key.
  all c1, c2 : Certificate | c1.certId = c2.certId => c1 = c2
}

pred sameCanonicalCertificate[c1, c2 : Certificate] {
  c1.certId = c2.certId
}

sig Authorization {
  certificate    : one Certificate,
  authorizedValue : one Value,
  principal      : one Principal
}

sig Transition {
  targetRecord  : one Record,
  targetField   : one Field,
  evidence      : one Evidence,
  fromVersion   : one Version,
  toVersion     : one Version,
  value         : one Value,
  producer      : one Producer,
  certificate   : one Certificate,
  authorization : one Authorization
}

// ---------------------------------------------------------------------------
// State
// ---------------------------------------------------------------------------
sig State {
  committedValue  : Record -> Field -> lone Value,
  committedSource : Record -> Field -> lone Transition,
  currentVersion  : Record -> one Version,
  transitions     : set Transition,
  candidates      : set Candidate,
  certificates    : set Certificate,
  authorizations  : set Authorization,
  evidence        : set Evidence
}

pred stateInvariant[s : State] {
  all r : Record | s.currentVersion[r].record = r
  all r : Record, f : Field |
    (some s.committedValue[r][f]) iff (some s.committedSource[r][f])
  all r : Record, f : Field, t : Transition |
    t = s.committedSource[r][f] => t.targetRecord = r and t.targetField = f
}

// ---------------------------------------------------------------------------
// Events and trace
// ---------------------------------------------------------------------------
abstract sig Event {
  pre  : one State,
  post : one State
}

sig MachineEvent extends Event {}

sig AdmissionEvent extends Event {
  certificate     : one Certificate,
  authorization   : one Authorization,
  targetRecord    : one Record,
  targetField     : one Field,
  targetEvidence  : one Evidence,
  expectedVersion : one Version,
  value           : one Value
}

sig TamperEvent extends Event {}

sig Trace {
  states : seq State,
  events : seq Event
}

pred wellFormedTrace[tr : Trace] {
  some tr.states
  #tr.states = (#tr.events).plus[1]
  all i : tr.events.inds |
    tr.events[i].pre  = tr.states[i] and
    tr.events[i].post = tr.states[i.plus[1]]
}

pred init[s : State] {
  no s.committedValue
  no s.committedSource
  all r : Record | s.currentVersion[r] = initialVersion[r]
  no s.transitions
  // candidates/certificates/authorizations/evidence are left flexible for
  // trusted initialization and machine artifacts.
}

pred sameState[a, b : State] {
  a.committedValue  = b.committedValue
  a.committedSource = b.committedSource
  a.currentVersion  = b.currentVersion
  a.transitions     = b.transitions
  a.candidates      = b.candidates
  a.certificates    = b.certificates
  a.authorizations  = b.authorizations
  a.evidence        = b.evidence
}

pred orderedTrace[tr : Trace] {
  wellFormedTrace[tr]
  all s : tr.states.elems | stateInvariant[s]
  init[tr.states[0]]
  all i : tr.events.inds | eventStep[tr.events[i]]
}

// ---------------------------------------------------------------------------
// Base effects: illegal successes must remain representable.
// ---------------------------------------------------------------------------
fun setFieldValue[s : State, r : Record, f : Field, v : Value]
    : Record -> Field -> lone Value {
  s.committedValue - (r -> f -> Value) + (r -> f -> v)
}

fun setCommittedSource[s : State, r : Record, f : Field, t : Transition]
    : Record -> Field -> lone Transition {
  s.committedSource - (r -> f -> Transition) + (r -> f -> t)
}

fun setCurrentVersion[s : State, r : Record, v : Version]
    : Record -> one Version {
  s.currentVersion - (r -> Version) + (r -> v)
}

pred admissionEffect[e : AdmissionEvent] {
  some newVersion : Version {
    newVersion = successor[e.pre.currentVersion[e.targetRecord]]
    e.post.committedValue  = setFieldValue[e.pre, e.targetRecord, e.targetField, e.value]
    e.post.currentVersion  = setCurrentVersion[e.pre, e.targetRecord, newVersion]
    e.post.candidates      = e.pre.candidates
    e.post.certificates    = e.pre.certificates + e.certificate
    e.post.authorizations  = e.pre.authorizations + e.authorization
    e.post.evidence        = e.pre.evidence + e.targetEvidence
  }
  some sourceTransition : Transition {
    e.post.committedSource = setCommittedSource[e.pre, e.targetRecord, e.targetField, sourceTransition]
    sourceTransition.targetRecord = e.targetRecord
    sourceTransition.targetField  = e.targetField
  }
  // post.transitions deliberately unconstrained in the base semantics.
}

pred rejectedAdmission[e : AdmissionEvent] {
  sameState[e.pre, e.post]
}

pred baseAdmissionStep[e : AdmissionEvent] {
  rejectedAdmission[e] or admissionEffect[e]
}

pred machineStep[e : MachineEvent] {
  e.post.authorizations  = e.pre.authorizations
  e.post.committedValue  = e.pre.committedValue
  e.post.committedSource = e.pre.committedSource
  e.post.currentVersion  = e.pre.currentVersion
  e.post.transitions     = e.pre.transitions
  e.pre.candidates   in e.post.candidates
  e.pre.certificates in e.post.certificates
  e.pre.evidence     in e.post.evidence
}

pred tamperStep[e : TamperEvent] {
  e.post.committedValue  = e.pre.committedValue
  e.post.committedSource = e.pre.committedSource
  e.post.currentVersion  = e.pre.currentVersion
  e.post.candidates      = e.pre.candidates
  e.post.certificates    = e.pre.certificates
  e.post.authorizations  = e.pre.authorizations
  e.post.evidence        = e.pre.evidence
}

pred eventStep[e : Event] {
  (e in MachineEvent and machineStep[e]) or
  (e in AdmissionEvent and baseAdmissionStep[e]) or
  (e in TamperEvent and tamperStep[e])
}

// ---------------------------------------------------------------------------
// Ablation mode
// ---------------------------------------------------------------------------
abstract sig Ablation {}
one sig Full extends Ablation {}
one sig ABL_1 extends Ablation {}
one sig ABL_2a extends Ablation {}
one sig ABL_2b extends Ablation {}
one sig ABL_3 extends Ablation {}
one sig ABL_4a extends Ablation {}
one sig ABL_4b extends Ablation {}
one sig ABL_5 extends Ablation {}
one sig ABL_6 extends Ablation {}
one sig ABL_7 extends Ablation {}
one sig ABL_8 extends Ablation {}
one sig ABL_9 extends Ablation {}
one sig ABL_10 extends Ablation {}
// ABL_7 is handled separately in traceComplete, not as a contract conjunct.

// ---------------------------------------------------------------------------
// Full admission contract, parameterized by ablation mode
// ---------------------------------------------------------------------------
pred contract[e : AdmissionEvent, m : Ablation] {
  // C-cert-preexists (attempted cert and auth-reference cert both preexist)
  m != ABL_9 => (e.certificate in e.pre.certificates and e.authorization.certificate in e.pre.certificates)
  // C-evidence-preexists
  m != ABL_10 => e.targetEvidence in e.pre.evidence
  // C-record
  m != ABL_3 => e.targetRecord = e.certificate.candidate.targetRecord
  // C-field
  m != ABL_1 => e.targetField = e.certificate.candidate.targetField
  // C-evidence-id
  m != ABL_2a => sameEvidenceIdentity[e.targetEvidence, e.certificate.candidate.evidence]
  // C-evidence-record
  m != ABL_2b => e.targetEvidence.record = e.targetRecord
  // C-version
  m != ABL_4a => e.expectedVersion = e.certificate.candidate.expectedVersion
  // C-fresh
  m != ABL_4b => e.pre.currentVersion[e.targetRecord] = e.expectedVersion
  // C-auth-cert
  m != ABL_5 => sameCanonicalCertificate[e.authorization.certificate, e.certificate]
  // C-principal (always present in the core model)
  e.authorization.principal in PrincipalRegistry.authorized
  // C-auth-value
  m != ABL_8 => e.value = e.authorization.authorizedValue
  // C-transition
  (m != ABL_6) => one t : e.post.transitions - e.pre.transitions {
    e.post.transitions = e.pre.transitions + t
    t = e.post.committedSource[e.targetRecord][e.targetField]
    t.targetRecord  = e.targetRecord
    t.targetField   = e.targetField
    t.evidence      = e.targetEvidence
    t.fromVersion   = e.pre.currentVersion[e.targetRecord]
    t.toVersion     = e.post.currentVersion[e.targetRecord]
    t.toVersion     = successor[t.fromVersion]
    t.value         = e.authorization.authorizedValue
    t.producer      = e.certificate.candidate.producer
    t.certificate   = e.certificate
    t.authorization = e.authorization
  }
}

pred EnforcingTrace[tr : Trace, m : Ablation] {
  orderedTrace[tr]
  all i : tr.events.inds | let e = tr.events[i] |
    (e in AdmissionEvent and admissionEffect[e]) => contract[e, m]
}

// ---------------------------------------------------------------------------
// Context/authorization/trace helper predicates
// ---------------------------------------------------------------------------
pred attemptContextEqualsCertificate[e : AdmissionEvent] {
  e.targetRecord = e.certificate.candidate.targetRecord
  e.targetField  = e.certificate.candidate.targetField
  sameEvidenceIdentity[e.targetEvidence, e.certificate.candidate.evidence]
  e.expectedVersion = e.certificate.candidate.expectedVersion
}

pred fullAdmissionContextOk[e : AdmissionEvent] {
  attemptContextEqualsCertificate[e]
  e.targetEvidence.record = e.targetRecord
}

pred sameCandidateContext[c1, c2 : Candidate] {
  c1.targetRecord = c2.targetRecord
  c1.targetField  = c2.targetField
  sameEvidenceIdentity[c1.evidence, c2.evidence]
  c1.expectedVersion = c2.expectedVersion
}

pred contextDifferent[c1, c2 : Candidate] {
  not sameCandidateContext[c1, c2]
}

pred authReferenceIntegrity[e : AdmissionEvent] {
  e.certificate in e.pre.certificates
  e.authorization.certificate in e.pre.certificates
  e.targetEvidence in e.pre.evidence
  one t : e.post.transitions - e.pre.transitions {
    e.post.transitions = e.pre.transitions + t
    t = e.post.committedSource[e.targetRecord][e.targetField]
    t.authorization = e.authorization
    t.certificate   = e.certificate
    sameCanonicalCertificate[e.authorization.certificate, e.certificate]
    e.authorization.principal in PrincipalRegistry.authorized
    t.value = e.authorization.authorizedValue
    e.value = e.authorization.authorizedValue
  }
}

pred transitionIntegrity[e : AdmissionEvent] {
  one t : e.post.transitions - e.pre.transitions {
    e.post.transitions = e.pre.transitions + t
    t = e.post.committedSource[e.targetRecord][e.targetField]
    t.targetRecord  = e.targetRecord
    t.targetField   = e.targetField
    t.evidence      = e.targetEvidence
    t.fromVersion   = e.pre.currentVersion[e.targetRecord]
    t.toVersion     = e.post.currentVersion[e.targetRecord]
    t.toVersion     = successor[t.fromVersion]
    t.value         = e.authorization.authorizedValue
    t.value         = e.post.committedValue[e.targetRecord][e.targetField]
    t.producer      = e.certificate.candidate.producer
    t.certificate   = e.certificate
    t.authorization = e.authorization
  }
}

// P6: traceComplete over the committed-fact source anchor.
pred traceComplete[s : State, r : Record, f : Field] {
  some s.committedValue[r][f]
  let src = s.committedSource[r][f] {
    some t : Transition {
      t = src
      t in s.transitions
      t.targetRecord = r
      t.targetField  = f
      t.value = s.committedValue[r][f]
      // Correct source-version uniqueness: no trailing "and u = t".
      (one u : s.transitions |
        u.targetRecord = r and u.targetField = f and u.toVersion = src.toVersion)
      some a : Authorization, c : Certificate, ev : Evidence {
        a = t.authorization
        c = t.certificate
        ev = t.evidence
        a in s.authorizations
        c in s.certificates
        ev in s.evidence
        sameCanonicalCertificate[a.certificate, c]
        sameEvidenceIdentity[c.candidate.evidence, ev]
        ev.record = r
        t.targetRecord = c.candidate.targetRecord
        t.targetField  = c.candidate.targetField
        t.value        = a.authorizedValue
        t.producer     = c.candidate.producer
        t.fromVersion  = c.candidate.expectedVersion
        t.toVersion    = successor[t.fromVersion]
        t.fromVersion.record = r
      }
    }
  }
}

// Weakened traceComplete used by ABL_7: omit source membership and
// source-version uniqueness (the trace-validation conjuncts).
pred traceCompleteAbl7[s : State, r : Record, f : Field] {
  some s.committedValue[r][f]
  let src = s.committedSource[r][f] {
    some t : Transition {
      t = src
      // The weakened verifier does NOT require t in s.transitions and does
      // NOT check source-version uniqueness.
      t.targetRecord = r
      t.targetField  = f
      t.value        = s.committedValue[r][f]
    }
  }
}

// ---------------------------------------------------------------------------
// Full-model consistency/regression checks
// ---------------------------------------------------------------------------
check P0_no_machine_write {
  all tr : Trace | EnforcingTrace[tr, Full] implies
    all i : tr.events.inds | let e = tr.events[i] |
      (e in MachineEvent or e in TamperEvent) implies
        e.post.committedValue  = e.pre.committedValue and
        e.post.committedSource = e.pre.committedSource and
        e.post.currentVersion  = e.pre.currentVersion
  all tr : Trace | EnforcingTrace[tr, Full] implies
    all i : tr.events.inds | let e = tr.events[i] |
      e in MachineEvent implies e.post.authorizations = e.pre.authorizations
}
for 2 Record, 2 Field, 4 Version, 2 Certificate, 2 Authorization, 2 Evidence, 3 Value, 2 Producer, 2 Principal, 2 CertId, 5 State, 5 Event, 1 Trace, 2 EvidenceContent, 2 EvidenceLocator, 2 Candidate, 2 Transition

check P1_no_cross_context_admission {
  all tr : Trace | EnforcingTrace[tr, Full] implies
    all i : tr.events.inds | let e = tr.events[i] |
      (e in AdmissionEvent and admissionEffect[e]) => fullAdmissionContextOk[e]
}
for 2 Record, 2 Field, 4 Version, 2 Certificate, 2 Authorization, 2 Evidence, 3 Value, 2 Producer, 2 Principal, 2 CertId, 5 State, 5 Event, 1 Trace, 2 EvidenceContent, 2 EvidenceLocator, 2 Candidate, 2 Transition

check P1_auth_nontransfer {
  all tr : Trace | EnforcingTrace[tr, Full] implies
    all i : tr.events.inds | let e = tr.events[i] |
      (e in AdmissionEvent and admissionEffect[e]) =>
        sameCanonicalCertificate[e.authorization.certificate, e.certificate]
}
for 2 Record, 2 Field, 4 Version, 2 Certificate, 2 Authorization, 2 Evidence, 3 Value, 2 Producer, 2 Principal, 2 CertId, 5 State, 5 Event, 1 Trace, 2 EvidenceContent, 2 EvidenceLocator, 2 Candidate, 2 Transition

check P3_authorization_reference_integrity {
  all tr : Trace | EnforcingTrace[tr, Full] implies
    all i : tr.events.inds | let e = tr.events[i] |
      (e in AdmissionEvent and admissionEffect[e]) => authReferenceIntegrity[e]
}
for 2 Record, 2 Field, 4 Version, 2 Certificate, 2 Authorization, 2 Evidence, 3 Value, 2 Producer, 2 Principal, 2 CertId, 5 State, 5 Event, 1 Trace, 2 EvidenceContent, 2 EvidenceLocator, 2 Candidate, 2 Transition

check P4_stale_reject {
  all tr : Trace | EnforcingTrace[tr, Full] implies
    all i : tr.events.inds | let e = tr.events[i] |
      (e in AdmissionEvent and admissionEffect[e]) =>
        e.pre.currentVersion[e.targetRecord] = e.expectedVersion
}
for 2 Record, 2 Field, 4 Version, 2 Certificate, 2 Authorization, 2 Evidence, 3 Value, 2 Producer, 2 Principal, 2 CertId, 5 State, 5 Event, 1 Trace, 2 EvidenceContent, 2 EvidenceLocator, 2 Candidate, 2 Transition

check P5_transition_integrity {
  all tr : Trace | EnforcingTrace[tr, Full] implies
    all i : tr.events.inds | let e = tr.events[i] |
      (e in AdmissionEvent and admissionEffect[e]) => transitionIntegrity[e]
}
for 2 Record, 2 Field, 4 Version, 2 Certificate, 2 Authorization, 2 Evidence, 3 Value, 2 Producer, 2 Principal, 2 CertId, 5 State, 5 Event, 1 Trace, 2 EvidenceContent, 2 EvidenceLocator, 2 Candidate, 2 Transition

check P6_trace_soundness {
  all tr : Trace | EnforcingTrace[tr, Full] implies
    all s : tr.states.elems, r : Record, f : Field |
      (some s.committedValue[r][f]) =>
        (some src : s.committedSource[r][f] |
          src in s.transitions and
          (one u : s.transitions |
            u.targetRecord = r and u.targetField = f and u.toVersion = src.toVersion)
        ) => traceComplete[s, r, f]
}
for 2 Record, 2 Field, 4 Version, 2 Certificate, 2 Authorization, 2 Evidence, 3 Value, 2 Producer, 2 Principal, 2 CertId, 5 State, 5 Event, 1 Trace, 2 EvidenceContent, 2 EvidenceLocator, 2 Candidate, 2 Transition

// Explicit P6 bad-state families: missing source / duplicate source-version
// are not reported Complete by the full trace predicate.
check P6_missing_source_incomplete {
  all tr : Trace | orderedTrace[tr] implies
    all s : tr.states.elems, r : Record, f : Field |
      (some s.committedValue[r][f]) and
      (some src : s.committedSource[r][f] | src not in s.transitions) =>
        not traceComplete[s, r, f]
}
for 2 Record, 2 Field, 4 Version, 2 Certificate, 2 Authorization, 2 Evidence, 3 Value, 2 Producer, 2 Principal, 2 CertId, 5 State, 5 Event, 1 Trace, 2 EvidenceContent, 2 EvidenceLocator, 2 Candidate, 2 Transition

check P6_duplicate_incomplete {
  all tr : Trace | orderedTrace[tr] implies
    all s : tr.states.elems, r : Record, f : Field |
      (some s.committedValue[r][f]) and
      (some src : s.committedSource[r][f] |
        src in s.transitions and
        some u : s.transitions | u != src and
          u.targetRecord = r and u.targetField = f and u.toVersion = src.toVersion) =>
        not traceComplete[s, r, f]
}
for 2 Record, 2 Field, 4 Version, 2 Certificate, 2 Authorization, 2 Evidence, 3 Value, 2 Producer, 2 Principal, 2 CertId, 5 State, 5 Event, 1 Trace, 2 EvidenceContent, 2 EvidenceLocator, 2 Candidate, 2 Transition


// ---------------------------------------------------------------------------
// SAT-1: legal cases
// ---------------------------------------------------------------------------
run SAT_1_accept {
  some tr : Trace, i : tr.events.inds |
    EnforcingTrace[tr, Full] and
    tr.events[i] in AdmissionEvent and admissionEffect[tr.events[i]] and
    tr.events[i].value = tr.events[i].authorization.authorizedValue and
    tr.events[i].authorization.authorizedValue = tr.events[i].certificate.candidate.value
} for 2 Record, 2 Field, 4 Version, 2 Certificate, 2 Authorization, 2 Evidence, 3 Value, 2 Producer, 2 Principal, 2 CertId, 5 State, 5 Event, 1 Trace, 2 EvidenceContent, 2 EvidenceLocator, 2 Candidate, 2 Transition

run SAT_1_correction {
  some tr : Trace, i : tr.events.inds |
    EnforcingTrace[tr, Full] and
    tr.events[i] in AdmissionEvent and admissionEffect[tr.events[i]] and
    tr.events[i].value = tr.events[i].authorization.authorizedValue and
    tr.events[i].authorization.authorizedValue != tr.events[i].certificate.candidate.value
} for 2 Record, 2 Field, 4 Version, 2 Certificate, 2 Authorization, 2 Evidence, 3 Value, 2 Producer, 2 Principal, 2 CertId, 5 State, 5 Event, 1 Trace, 2 EvidenceContent, 2 EvidenceLocator, 2 Candidate, 2 Transition

run SAT_invariant_admission_tamper {
  some tr : Trace, i : tr.events.inds |
    orderedTrace[tr] and
    tr.events[i] in AdmissionEvent and admissionEffect[tr.events[i]] and
    i.plus[1] in tr.events.inds and tr.events[i.plus[1]] in TamperEvent
} for 2 Record, 2 Field, 4 Version, 2 Certificate, 2 Authorization, 2 Evidence, 3 Value, 2 Producer, 2 Principal, 2 CertId, 5 State, 5 Event, 1 Trace, 2 EvidenceContent, 2 EvidenceLocator, 2 Candidate, 2 Transition

// ---------------------------------------------------------------------------
// SAT-2: attack-state witnesses with contract off (orderedTrace only)
// ---------------------------------------------------------------------------
run SAT2_S1_field_substitution {
  some tr : Trace, i : tr.events.inds |
    orderedTrace[tr] and tr.events[i] in AdmissionEvent and admissionEffect[tr.events[i]] and
    tr.events[i].targetField != tr.events[i].certificate.candidate.targetField
} for 2 Record, 2 Field, 4 Version, 2 Certificate, 2 Authorization, 2 Evidence, 3 Value, 2 Producer, 2 Principal, 2 CertId, 5 State, 5 Event, 1 Trace, 2 EvidenceContent, 2 EvidenceLocator, 2 Candidate, 2 Transition

run SAT2_S2a_evidence_identity_substitution {
  some tr : Trace, i : tr.events.inds |
    orderedTrace[tr] and tr.events[i] in AdmissionEvent and admissionEffect[tr.events[i]] and
    not sameEvidenceIdentity[tr.events[i].targetEvidence, tr.events[i].certificate.candidate.evidence]
} for 2 Record, 2 Field, 4 Version, 2 Certificate, 2 Authorization, 2 Evidence, 3 Value, 2 Producer, 2 Principal, 2 CertId, 5 State, 5 Event, 1 Trace, 2 EvidenceContent, 2 EvidenceLocator, 2 Candidate, 2 Transition

run SAT2_S2b_evidence_owner_substitution {
  some tr : Trace, i : tr.events.inds |
    orderedTrace[tr] and tr.events[i] in AdmissionEvent and admissionEffect[tr.events[i]] and
    sameEvidenceIdentity[tr.events[i].targetEvidence, tr.events[i].certificate.candidate.evidence] and
    tr.events[i].targetEvidence.record != tr.events[i].targetRecord
} for 2 Record, 2 Field, 4 Version, 2 Certificate, 2 Authorization, 2 Evidence, 3 Value, 2 Producer, 2 Principal, 2 CertId, 5 State, 5 Event, 1 Trace, 2 EvidenceContent, 2 EvidenceLocator, 2 Candidate, 2 Transition

run SAT2_S3_record_substitution {
  some tr : Trace, i : tr.events.inds |
    orderedTrace[tr] and tr.events[i] in AdmissionEvent and admissionEffect[tr.events[i]] and
    tr.events[i].targetRecord != tr.events[i].certificate.candidate.targetRecord
} for 2 Record, 2 Field, 4 Version, 2 Certificate, 2 Authorization, 2 Evidence, 3 Value, 2 Producer, 2 Principal, 2 CertId, 5 State, 5 Event, 1 Trace, 2 EvidenceContent, 2 EvidenceLocator, 2 Candidate, 2 Transition

run SAT2_S4a_version_substitution {
  some tr : Trace, i : tr.events.inds |
    orderedTrace[tr] and tr.events[i] in AdmissionEvent and admissionEffect[tr.events[i]] and
    tr.events[i].expectedVersion != tr.events[i].certificate.candidate.expectedVersion and
    tr.events[i].expectedVersion = tr.events[i].pre.currentVersion[tr.events[i].targetRecord]
} for 2 Record, 2 Field, 4 Version, 2 Certificate, 2 Authorization, 2 Evidence, 3 Value, 2 Producer, 2 Principal, 2 CertId, 5 State, 5 Event, 1 Trace, 2 EvidenceContent, 2 EvidenceLocator, 2 Candidate, 2 Transition

run SAT2_S4b_stale_replay {
  some tr : Trace, i : tr.events.inds |
    orderedTrace[tr] and tr.events[i] in AdmissionEvent and admissionEffect[tr.events[i]] and
    tr.events[i].expectedVersion = tr.events[i].certificate.candidate.expectedVersion and
    olderThan[
      tr.events[i].expectedVersion,
      tr.events[i].pre.currentVersion[tr.events[i].targetRecord]
    ]
} for 2 Record, 2 Field, 4 Version, 2 Certificate, 2 Authorization, 2 Evidence, 3 Value, 2 Producer, 2 Principal, 2 CertId, 5 State, 5 Event, 1 Trace, 2 EvidenceContent, 2 EvidenceLocator, 2 Candidate, 2 Transition

run SAT2_S5_auth_certificate_substitution {
  some tr : Trace, i : tr.events.inds |
    orderedTrace[tr] and tr.events[i] in AdmissionEvent and admissionEffect[tr.events[i]] and
    not sameCanonicalCertificate[tr.events[i].authorization.certificate, tr.events[i].certificate] and
    tr.events[i].authorization.certificate.candidate.value = tr.events[i].certificate.candidate.value and
    contextDifferent[
      tr.events[i].authorization.certificate.candidate,
      tr.events[i].certificate.candidate
    ] and
    tr.events[i].authorization.certificate in tr.events[i].pre.certificates and
    tr.events[i].certificate in tr.events[i].pre.certificates
} for 2 Record, 2 Field, 4 Version, 2 Certificate, 2 Authorization, 2 Evidence, 3 Value, 2 Producer, 2 Principal, 2 CertId, 5 State, 5 Event, 1 Trace, 2 EvidenceContent, 2 EvidenceLocator, 2 Candidate, 2 Transition

run SAT2_S8_unrecorded_final_value {
  some tr : Trace, i : tr.events.inds |
    orderedTrace[tr] and tr.events[i] in AdmissionEvent and admissionEffect[tr.events[i]] and
    tr.events[i].value != tr.events[i].authorization.authorizedValue
} for 2 Record, 2 Field, 4 Version, 2 Certificate, 2 Authorization, 2 Evidence, 3 Value, 2 Producer, 2 Principal, 2 CertId, 5 State, 5 Event, 1 Trace, 2 EvidenceContent, 2 EvidenceLocator, 2 Candidate, 2 Transition

run SAT2_S9_conjured_certificate {
  some tr : Trace, i : tr.events.inds |
    orderedTrace[tr] and tr.events[i] in AdmissionEvent and admissionEffect[tr.events[i]] and
    tr.events[i].certificate not in tr.events[i].pre.certificates
} for 2 Record, 2 Field, 4 Version, 2 Certificate, 2 Authorization, 2 Evidence, 3 Value, 2 Producer, 2 Principal, 2 CertId, 5 State, 5 Event, 1 Trace, 2 EvidenceContent, 2 EvidenceLocator, 2 Candidate, 2 Transition

run SAT2_S10_conjured_evidence {
  some tr : Trace, i : tr.events.inds |
    orderedTrace[tr] and tr.events[i] in AdmissionEvent and admissionEffect[tr.events[i]] and
    tr.events[i].targetEvidence not in tr.events[i].pre.evidence
} for 2 Record, 2 Field, 4 Version, 2 Certificate, 2 Authorization, 2 Evidence, 3 Value, 2 Producer, 2 Principal, 2 CertId, 5 State, 5 Event, 1 Trace, 2 EvidenceContent, 2 EvidenceLocator, 2 Candidate, 2 Transition

run SAT2_unauthorized_principal {
  some tr : Trace, i : tr.events.inds |
    orderedTrace[tr] and tr.events[i] in AdmissionEvent and admissionEffect[tr.events[i]] and
    tr.events[i].authorization.principal not in PrincipalRegistry.authorized
} for 2 Record, 2 Field, 4 Version, 2 Certificate, 2 Authorization, 2 Evidence, 3 Value, 2 Producer, 2 Principal, 2 CertId, 5 State, 5 Event, 1 Trace, 2 EvidenceContent, 2 EvidenceLocator, 2 Candidate, 2 Transition

run SAT2_source_transition_deletion {
  some tr : Trace, i : tr.events.inds, j : tr.events.inds |
    orderedTrace[tr] and
    tr.events[i] in AdmissionEvent and admissionEffect[tr.events[i]] and
    j = i.plus[1] and tr.events[j] in TamperEvent and
    some s : State, r : Record, f : Field, src : Transition |
      s = tr.events[j].post and src = s.committedSource[r][f] and src not in s.transitions
} for 2 Record, 2 Field, 4 Version, 2 Certificate, 2 Authorization, 2 Evidence, 3 Value, 2 Producer, 2 Principal, 2 CertId, 5 State, 5 Event, 1 Trace, 2 EvidenceContent, 2 EvidenceLocator, 2 Candidate, 2 Transition

run SAT2_source_replacement {
  some tr : Trace, i : tr.events.inds, j : tr.events.inds |
    orderedTrace[tr] and
    tr.events[i] in AdmissionEvent and admissionEffect[tr.events[i]] and
    j = i.plus[1] and tr.events[j] in TamperEvent and
    some s : State, r : Record, f : Field, src : Transition |
      s = tr.events[j].post and src = s.committedSource[r][f] and
      src not in s.transitions and
      some repl : s.transitions |
        repl != src and
        repl.targetRecord = r and
        repl.targetField = f and
        repl.toVersion = src.toVersion and
        repl.value != src.value
} for 2 Record, 2 Field, 4 Version, 2 Certificate, 2 Authorization, 2 Evidence, 3 Value, 2 Producer, 2 Principal, 2 CertId, 5 State, 5 Event, 1 Trace, 2 EvidenceContent, 2 EvidenceLocator, 2 Candidate, 2 Transition

run SAT2_source_version_duplicate {
  some tr : Trace, i : tr.events.inds, j : tr.events.inds |
    orderedTrace[tr] and
    tr.events[i] in AdmissionEvent and admissionEffect[tr.events[i]] and
    j = i.plus[1] and tr.events[j] in TamperEvent and
    some s : State, r : Record, f : Field, src : Transition |
      s = tr.events[j].post and src = s.committedSource[r][f] and
      src in s.transitions and
      some u : s.transitions | u != src and
        u.targetRecord = r and u.targetField = f and u.toVersion = src.toVersion
} for 2 Record, 2 Field, 4 Version, 2 Certificate, 2 Authorization, 2 Evidence, 3 Value, 2 Producer, 2 Principal, 2 CertId, 5 State, 5 Event, 1 Trace, 2 EvidenceContent, 2 EvidenceLocator, 2 Candidate, 2 Transition

run SAT2_sequential_confirmation {
  some tr : Trace, i : tr.events.inds, j : tr.events.inds |
    orderedTrace[tr] and
    tr.events[i] in AdmissionEvent and admissionEffect[tr.events[i]] and
    tr.events[j] in AdmissionEvent and j = i.plus[1] and
    tr.events[j].expectedVersion = tr.events[i].expectedVersion and
    tr.events[j].pre.currentVersion[tr.events[j].targetRecord] != tr.events[j].expectedVersion
} for 2 Record, 2 Field, 4 Version, 2 Certificate, 2 Authorization, 2 Evidence, 3 Value, 2 Producer, 2 Principal, 2 CertId, 5 State, 5 Event, 1 Trace, 2 EvidenceContent, 2 EvidenceLocator, 2 Candidate, 2 Transition

// ---------------------------------------------------------------------------
// Central rework witnesses: genuine stale replay and context-transfer S5
// ---------------------------------------------------------------------------
run SAT_ABL4b_true_stale_success {
  some tr : Trace, i : tr.events.inds, j : tr.events.inds,
        r : Record, f : Field, v0 : Version, v1 : Version, v2 : Version |
    EnforcingTrace[tr, ABL_4b] and
    j = i.plus[1] and
    tr.events[i] in AdmissionEvent and admissionEffect[tr.events[i]] and
    tr.events[j] in AdmissionEvent and admissionEffect[tr.events[j]] and
    v0 = initialVersion[r] and
    v0.succ = v1 and
    v1.succ = v2 and
    tr.events[i].targetRecord = r and
    tr.events[i].targetField  = f and
    tr.events[i].expectedVersion = v0 and
    tr.events[i].pre.currentVersion[r] = v0 and
    tr.events[i].post.currentVersion[r] = v1 and
    tr.events[j].targetRecord = r and
    tr.events[j].targetField  = f and
    tr.events[j].expectedVersion = v0 and
    tr.events[j].pre.currentVersion[r] = v1 and
    tr.events[j].post.currentVersion[r] = v2 and
    olderThan[v0, tr.events[j].pre.currentVersion[r]]
} for 2 Record, 2 Field, 4 Version, 2 Certificate, 2 Authorization, 2 Evidence, 3 Value, 2 Producer, 2 Principal, 2 CertId, 5 State, 5 Event, 1 Trace, 2 EvidenceContent, 2 EvidenceLocator, 2 Candidate, 2 Transition

run SAT_ABL5_same_value_different_context_transfer {
  some tr : Trace, i : tr.events.inds |
    EnforcingTrace[tr, ABL_5] and
    tr.events[i] in AdmissionEvent and admissionEffect[tr.events[i]] and
    not sameCanonicalCertificate[tr.events[i].authorization.certificate, tr.events[i].certificate] and
    tr.events[i].authorization.certificate.candidate.value = tr.events[i].certificate.candidate.value and
    tr.events[i].authorization.authorizedValue = tr.events[i].certificate.candidate.value and
    contextDifferent[
      tr.events[i].authorization.certificate.candidate,
      tr.events[i].certificate.candidate
    ] and
    tr.events[i].authorization.certificate in tr.events[i].pre.certificates and
    tr.events[i].certificate in tr.events[i].pre.certificates
} for 2 Record, 2 Field, 4 Version, 2 Certificate, 2 Authorization, 2 Evidence, 3 Value, 2 Producer, 2 Principal, 2 CertId, 5 State, 5 Event, 1 Trace, 2 EvidenceContent, 2 EvidenceLocator, 2 Candidate, 2 Transition

run SAT_ABL5_same_value_cross_field_transfer {
  some tr : Trace, i : tr.events.inds |
    EnforcingTrace[tr, ABL_5] and
    tr.events[i] in AdmissionEvent and admissionEffect[tr.events[i]] and
    not sameCanonicalCertificate[tr.events[i].authorization.certificate, tr.events[i].certificate] and
    tr.events[i].authorization.certificate.candidate.value = tr.events[i].certificate.candidate.value and
    tr.events[i].authorization.authorizedValue = tr.events[i].certificate.candidate.value and
    tr.events[i].authorization.certificate.candidate.targetRecord = tr.events[i].certificate.candidate.targetRecord and
    tr.events[i].authorization.certificate.candidate.expectedVersion = tr.events[i].certificate.candidate.expectedVersion and
    tr.events[i].authorization.certificate.candidate.expectedVersion = tr.events[i].pre.currentVersion[tr.events[i].targetRecord] and
    tr.events[i].authorization.certificate.candidate.targetField != tr.events[i].certificate.candidate.targetField and
    tr.events[i].authorization.certificate in tr.events[i].pre.certificates and
    tr.events[i].certificate in tr.events[i].pre.certificates
} for 2 Record, 2 Field, 4 Version, 2 Certificate, 2 Authorization, 2 Evidence, 3 Value, 2 Producer, 2 Principal, 2 CertId, 5 State, 5 Event, 1 Trace, 2 EvidenceContent, 2 EvidenceLocator, 2 Candidate, 2 Transition

// ---------------------------------------------------------------------------
// Ablation checks: each must find a counterexample.
// ---------------------------------------------------------------------------
check ABL_1 {
  all tr : Trace | EnforcingTrace[tr, ABL_1] implies
    all i : tr.events.inds | let e = tr.events[i] |
      (e in AdmissionEvent and admissionEffect[e]) => fullAdmissionContextOk[e]
}
for 2 Record, 2 Field, 4 Version, 2 Certificate, 2 Authorization, 2 Evidence, 3 Value, 2 Producer, 2 Principal, 2 CertId, 5 State, 5 Event, 1 Trace, 2 EvidenceContent, 2 EvidenceLocator, 2 Candidate, 2 Transition

check ABL_2a {
  all tr : Trace | EnforcingTrace[tr, ABL_2a] implies
    all i : tr.events.inds | let e = tr.events[i] |
      (e in AdmissionEvent and admissionEffect[e]) => fullAdmissionContextOk[e]
}
for 2 Record, 2 Field, 4 Version, 2 Certificate, 2 Authorization, 2 Evidence, 3 Value, 2 Producer, 2 Principal, 2 CertId, 5 State, 5 Event, 1 Trace, 2 EvidenceContent, 2 EvidenceLocator, 2 Candidate, 2 Transition

check ABL_2b {
  all tr : Trace | EnforcingTrace[tr, ABL_2b] implies
    all i : tr.events.inds | let e = tr.events[i] |
      (e in AdmissionEvent and admissionEffect[e]) => fullAdmissionContextOk[e]
}
for 2 Record, 2 Field, 4 Version, 2 Certificate, 2 Authorization, 2 Evidence, 3 Value, 2 Producer, 2 Principal, 2 CertId, 5 State, 5 Event, 1 Trace, 2 EvidenceContent, 2 EvidenceLocator, 2 Candidate, 2 Transition

check ABL_3 {
  all tr : Trace | EnforcingTrace[tr, ABL_3] implies
    all i : tr.events.inds | let e = tr.events[i] |
      (e in AdmissionEvent and admissionEffect[e]) => fullAdmissionContextOk[e]
}
for 2 Record, 2 Field, 4 Version, 2 Certificate, 2 Authorization, 2 Evidence, 3 Value, 2 Producer, 2 Principal, 2 CertId, 5 State, 5 Event, 1 Trace, 2 EvidenceContent, 2 EvidenceLocator, 2 Candidate, 2 Transition

check ABL_4a {
  all tr : Trace | EnforcingTrace[tr, ABL_4a] implies
    all i : tr.events.inds | let e = tr.events[i] |
      (e in AdmissionEvent and admissionEffect[e]) => fullAdmissionContextOk[e]
}
for 2 Record, 2 Field, 4 Version, 2 Certificate, 2 Authorization, 2 Evidence, 3 Value, 2 Producer, 2 Principal, 2 CertId, 5 State, 5 Event, 1 Trace, 2 EvidenceContent, 2 EvidenceLocator, 2 Candidate, 2 Transition

check ABL_4b {
  all tr : Trace | EnforcingTrace[tr, ABL_4b] implies
    all i : tr.events.inds | let e = tr.events[i] |
      (e in AdmissionEvent and admissionEffect[e]) =>
        e.pre.currentVersion[e.targetRecord] = e.expectedVersion
}
for 2 Record, 2 Field, 4 Version, 2 Certificate, 2 Authorization, 2 Evidence, 3 Value, 2 Producer, 2 Principal, 2 CertId, 5 State, 5 Event, 1 Trace, 2 EvidenceContent, 2 EvidenceLocator, 2 Candidate, 2 Transition

check ABL_5 {
  all tr : Trace | EnforcingTrace[tr, ABL_5] implies
    all i : tr.events.inds | let e = tr.events[i] |
      (e in AdmissionEvent and admissionEffect[e]) =>
        sameCanonicalCertificate[e.authorization.certificate, e.certificate]
}
for 2 Record, 2 Field, 4 Version, 2 Certificate, 2 Authorization, 2 Evidence, 3 Value, 2 Producer, 2 Principal, 2 CertId, 5 State, 5 Event, 1 Trace, 2 EvidenceContent, 2 EvidenceLocator, 2 Candidate, 2 Transition

check ABL_6 {
  all tr : Trace | EnforcingTrace[tr, ABL_6] implies
    all i : tr.events.inds | let e = tr.events[i] |
      (e in AdmissionEvent and admissionEffect[e]) => transitionIntegrity[e]
}
for 2 Record, 2 Field, 4 Version, 2 Certificate, 2 Authorization, 2 Evidence, 3 Value, 2 Producer, 2 Principal, 2 CertId, 5 State, 5 Event, 1 Trace, 2 EvidenceContent, 2 EvidenceLocator, 2 Candidate, 2 Transition

check ABL_7 {
  // With trace-validation conjuncts removed, a source-deleted/duplicate state
  // is incorrectly accepted by the weakened verifier.
  all tr : Trace | orderedTrace[tr] implies
    all s : tr.states.elems, r : Record, f : Field |
      (some s.committedValue[r][f]) and
      (some src : s.committedSource[r][f] | src not in s.transitions) =>
        not traceCompleteAbl7[s, r, f]
}
for 2 Record, 2 Field, 4 Version, 2 Certificate, 2 Authorization, 2 Evidence, 3 Value, 2 Producer, 2 Principal, 2 CertId, 5 State, 5 Event, 1 Trace, 2 EvidenceContent, 2 EvidenceLocator, 2 Candidate, 2 Transition

run SAT_ABL7_deleted_source_falsely_complete {
  some tr : Trace, i : tr.events.inds, j : tr.events.inds,
        s : State, r : Record, f : Field, src : Transition |
    orderedTrace[tr] and
    tr.events[i] in AdmissionEvent and admissionEffect[tr.events[i]] and
    j = i.plus[1] and tr.events[j] in TamperEvent and
    s = tr.events[j].post and src = s.committedSource[r][f] and
    src not in s.transitions and
    traceCompleteAbl7[s, r, f]
} for 2 Record, 2 Field, 4 Version, 2 Certificate, 2 Authorization, 2 Evidence, 3 Value, 2 Producer, 2 Principal, 2 CertId, 5 State, 5 Event, 1 Trace, 2 EvidenceContent, 2 EvidenceLocator, 2 Candidate, 2 Transition

run SAT_ABL7_duplicate_falsely_complete {
  some tr : Trace, i : tr.events.inds, j : tr.events.inds,
        s : State, r : Record, f : Field, src : Transition |
    orderedTrace[tr] and
    tr.events[i] in AdmissionEvent and admissionEffect[tr.events[i]] and
    j = i.plus[1] and tr.events[j] in TamperEvent and
    s = tr.events[j].post and src = s.committedSource[r][f] and
    src in s.transitions and
    some u : s.transitions | u != src and
      u.targetRecord = r and u.targetField = f and u.toVersion = src.toVersion and
    traceCompleteAbl7[s, r, f]
} for 2 Record, 2 Field, 4 Version, 2 Certificate, 2 Authorization, 2 Evidence, 3 Value, 2 Producer, 2 Principal, 2 CertId, 5 State, 5 Event, 1 Trace, 2 EvidenceContent, 2 EvidenceLocator, 2 Candidate, 2 Transition

check ABL_8 {
  all tr : Trace | EnforcingTrace[tr, ABL_8] implies
    all i : tr.events.inds | let e = tr.events[i] |
      (e in AdmissionEvent and admissionEffect[e]) => transitionIntegrity[e]
}
for 2 Record, 2 Field, 4 Version, 2 Certificate, 2 Authorization, 2 Evidence, 3 Value, 2 Producer, 2 Principal, 2 CertId, 5 State, 5 Event, 1 Trace, 2 EvidenceContent, 2 EvidenceLocator, 2 Candidate, 2 Transition

check ABL_9 {
  all tr : Trace | EnforcingTrace[tr, ABL_9] implies
    all i : tr.events.inds | let e = tr.events[i] |
      (e in AdmissionEvent and admissionEffect[e]) => authReferenceIntegrity[e]
}
for 2 Record, 2 Field, 4 Version, 2 Certificate, 2 Authorization, 2 Evidence, 3 Value, 2 Producer, 2 Principal, 2 CertId, 5 State, 5 Event, 1 Trace, 2 EvidenceContent, 2 EvidenceLocator, 2 Candidate, 2 Transition

check ABL_10 {
  all tr : Trace | EnforcingTrace[tr, ABL_10] implies
    all i : tr.events.inds | let e = tr.events[i] |
      (e in AdmissionEvent and admissionEffect[e]) => authReferenceIntegrity[e]
}
for 2 Record, 2 Field, 4 Version, 2 Certificate, 2 Authorization, 2 Evidence, 3 Value, 2 Producer, 2 Principal, 2 CertId, 5 State, 5 Event, 1 Trace, 2 EvidenceContent, 2 EvidenceLocator, 2 Candidate, 2 Transition

// P6 duplicate witness explicitly placed before any P6 check.
run SAT_P6_duplicate_witness {
  some tr : Trace, i : tr.events.inds, j : tr.events.inds |
    orderedTrace[tr] and
    tr.events[i] in AdmissionEvent and admissionEffect[tr.events[i]] and
    j = i.plus[1] and tr.events[j] in TamperEvent and
    some s : State, r : Record, f : Field, src : Transition |
      s = tr.events[j].post and src = s.committedSource[r][f] and
      src in s.transitions and
      some u : s.transitions | u != src and
        u.targetRecord = r and u.targetField = f and u.toVersion = src.toVersion
} for 2 Record, 2 Field, 4 Version, 2 Certificate, 2 Authorization, 2 Evidence, 3 Value, 2 Producer, 2 Principal, 2 CertId, 5 State, 5 Event, 1 Trace, 2 EvidenceContent, 2 EvidenceLocator, 2 Candidate, 2 Transition

// Dedicated true-duplicate witness: source atom and a distinct duplicate atom
// are both present in State.transitions simultaneously.
run SAT_P6_true_duplicate_witness {
  some tr : Trace, i : tr.events.inds, j : tr.events.inds |
    orderedTrace[tr] and
    tr.events[i] in AdmissionEvent and admissionEffect[tr.events[i]] and
    j = i.plus[1] and tr.events[j] in TamperEvent and
    some s : State, r : Record, f : Field, src : Transition |
      s = tr.events[j].post and src = s.committedSource[r][f] and
      src in s.transitions and
      some u : s.transitions | u != src and
        u.targetRecord = r and u.targetField = f and u.toVersion = src.toVersion
} for 2 Record, 2 Field, 4 Version, 2 Certificate, 2 Authorization, 2 Evidence, 3 Value, 2 Producer, 2 Principal, 2 CertId, 5 State, 5 Event, 1 Trace, 2 EvidenceContent, 2 EvidenceLocator, 2 Candidate, 2 Transition
