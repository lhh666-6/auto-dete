module auto_decte_batch

// Conservative batch extension of the historical singleton Auto-Decte model.
// The historical models in ../auto_decte*.als are immutable evidence inputs.
// Full keeps one atomic record/version envelope while lifting P1-P5 pointwise.

// ---------------------------------------------------------------------------
// Basic domains and record/version structure
// ---------------------------------------------------------------------------

sig Value {}
sig Field {}
sig Producer {}
sig Principal {}

one sig PrincipalRegistry {
  authorized : set Principal
}

sig Record {
  authoritativeFields : some Field
}

sig EvidenceContent {}
sig EvidenceLocator {}

sig Evidence {
  record  : one Record,
  content : one EvidenceContent,
  locator : one EvidenceLocator
}

pred sameEvidenceIdentity[e1, e2 : Evidence] {
  e1.content = e2.content
  e1.locator = e2.locator
}

sig CertId {}

sig Version {
  record : one Record,
  succ   : lone Version
}

fact versionStructure {
  no v : Version | v in v.^succ
  all v : Version | no v.succ or v.succ.record = v.record
  all v : Version | lone u : Version | u.succ = v
  all r : Record | one v : Version | v.record = r and v not in Version.succ
}

fun initialVersion[r : Record] : one Version {
  {v : Version | v.record = r and v not in Version.succ}
}

fun successor[v : Version] : lone Version {
  v.succ
}

pred olderThan[old, cur : Version] {
  cur in old.^succ
}

// ---------------------------------------------------------------------------
// Candidate, certificate, authorization, transition, and state
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
  all c1, c2 : Certificate |
    not certModeledContentEqual[c1, c2] => c1.certId != c2.certId
  all c1, c2 : Certificate | c1.certId = c2.certId => c1 = c2
}

pred sameCanonicalCertificate[c1, c2 : Certificate] {
  c1.certId = c2.certId
}

sig Authorization {
  certificate     : one Certificate,
  authorizedValue : one Value,
  principal       : one Principal
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
  all r : Record |
    (no s.committedValue[r] and no s.committedSource[r]) or
    (all f : Field |
      (some s.committedValue[r][f]) iff f in r.authoritativeFields) and
    (all f : Field |
      (some s.committedSource[r][f]) iff f in r.authoritativeFields)
  all r : Record, f : Field, t : Transition |
    t = s.committedSource[r][f] =>
      t.targetRecord = r and t.targetField = f
}

pred init[s : State] {
  no s.committedValue
  no s.committedSource
  all r : Record | s.currentVersion[r] = initialVersion[r]
  no s.transitions
  stateInvariant[s]
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

// ---------------------------------------------------------------------------
// Events and deliberately permissive base effects
// ---------------------------------------------------------------------------

abstract sig Event {
  pre  : one State,
  post : one State
}

sig MachineEvent extends Event {}

sig AdmissionItem {
  certificate     : one Certificate,
  authorization   : one Authorization,
  targetRecord    : one Record,
  targetField     : one Field,
  targetEvidence  : one Evidence,
  expectedVersion : one Version,
  value           : one Value,
  transition      : one Transition
}

sig BatchAdmissionEvent extends Event {
  items        : some AdmissionItem,
  targetRecord : one Record,
  principal    : one Principal
}

sig TamperEvent extends Event {}

fun batchValueUpdates[e : BatchAdmissionEvent]
    : Record -> Field -> Value {
  {r : Record, f : Field, v : Value |
    r = e.targetRecord and
    some i : e.items | i.targetField = f and i.value = v}
}

fun batchSourceUpdates[e : BatchAdmissionEvent]
    : Record -> Field -> Transition {
  {r : Record, f : Field, t : Transition |
    r = e.targetRecord and
    some i : e.items | i.targetField = f and i.transition = t}
}

fun setBatchValues[s : State, e : BatchAdmissionEvent]
    : Record -> Field -> lone Value {
  s.committedValue - (e.targetRecord -> e.items.targetField -> Value) +
    batchValueUpdates[e]
}

fun setBatchSources[s : State, e : BatchAdmissionEvent]
    : Record -> Field -> lone Transition {
  s.committedSource - (e.targetRecord -> e.items.targetField -> Transition) +
    batchSourceUpdates[e]
}

fun setCurrentVersion[s : State, r : Record, v : Version]
    : Record -> one Version {
  s.currentVersion - (r -> Version) + (r -> v)
}

pred baseAdmissionEffect[e : BatchAdmissionEvent] {
  some newVersion : Version {
    newVersion = successor[e.pre.currentVersion[e.targetRecord]]
    e.post.committedValue = setBatchValues[e.pre, e]
    e.post.committedSource = setBatchSources[e.pre, e]
    e.post.currentVersion =
      setCurrentVersion[e.pre, e.targetRecord, newVersion]
  }
  e.post.candidates = e.pre.candidates
  e.post.certificates = e.pre.certificates + e.items.certificate
  e.post.authorizations = e.pre.authorizations + e.items.authorization
  e.post.evidence = e.pre.evidence + e.items.targetEvidence
  // post.transitions is deliberately unconstrained here. Full or an
  // ablation contract decides how item transitions relate to the state.
}

pred rejectedAdmission[e : BatchAdmissionEvent] {
  sameState[e.pre, e.post]
}

pred baseAdmissionStep[e : BatchAdmissionEvent] {
  rejectedAdmission[e] or baseAdmissionEffect[e]
}

pred machineStep[e : MachineEvent] {
  e.post.authorizations = e.pre.authorizations
  e.post.committedValue = e.pre.committedValue
  e.post.committedSource = e.pre.committedSource
  e.post.currentVersion = e.pre.currentVersion
  e.post.transitions = e.pre.transitions
  e.pre.candidates in e.post.candidates
  e.pre.certificates in e.post.certificates
  e.pre.evidence in e.post.evidence
}

pred tamperStep[e : TamperEvent] {
  e.post.committedValue = e.pre.committedValue
  e.post.committedSource = e.pre.committedSource
  e.post.currentVersion = e.pre.currentVersion
  e.post.candidates = e.pre.candidates
  e.post.certificates = e.pre.certificates
  e.post.authorizations = e.pre.authorizations
  e.post.evidence = e.pre.evidence
  // Only the transition set may change. Witnesses below require a
  // non-stuttering loss, replacement, or duplicate delta.
}

// ---------------------------------------------------------------------------
// Full contract and one-mechanism ablations
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

pred uniqueItemFields[e : BatchAdmissionEvent] {
  all disj i, j : e.items | i.targetField != j.targetField
}

pred snapshotShape[e : BatchAdmissionEvent] {
  e.items.targetField in e.targetRecord.authoritativeFields
  no e.pre.committedValue[e.targetRecord] =>
    e.items.targetField = e.targetRecord.authoritativeFields
  some e.pre.committedValue[e.targetRecord] =>
    all f : e.targetRecord.authoritativeFields |
      some e.pre.committedValue[e.targetRecord][f] and
      some e.pre.committedSource[e.targetRecord][f]
}

pred certificatePreexists[e : BatchAdmissionEvent, i : AdmissionItem] {
  i.certificate in e.pre.certificates
  i.authorization.certificate in e.pre.certificates
}

pred evidencePreexists[e : BatchAdmissionEvent, i : AdmissionItem] {
  i.targetEvidence in e.pre.evidence
}

pred recordBinding[e : BatchAdmissionEvent, i : AdmissionItem] {
  i.targetRecord = e.targetRecord
  i.targetRecord = i.certificate.candidate.targetRecord
}

pred fieldBinding[i : AdmissionItem] {
  i.targetField = i.certificate.candidate.targetField
}

pred evidenceIdentityBinding[i : AdmissionItem] {
  sameEvidenceIdentity[
    i.targetEvidence,
    i.certificate.candidate.evidence
  ]
}

pred evidenceRecordBinding[e : BatchAdmissionEvent, i : AdmissionItem] {
  i.targetEvidence.record = e.targetRecord
  i.certificate.candidate.evidence.record = e.targetRecord
}

pred versionBinding[i : AdmissionItem] {
  i.expectedVersion = i.certificate.candidate.expectedVersion
}

pred freshBinding[e : BatchAdmissionEvent, i : AdmissionItem] {
  i.expectedVersion = e.pre.currentVersion[e.targetRecord]
}

pred authorizationCertificateBinding[i : AdmissionItem] {
  sameCanonicalCertificate[
    i.authorization.certificate,
    i.certificate
  ]
}

pred principalBinding[e : BatchAdmissionEvent, i : AdmissionItem] {
  i.authorization.principal = e.principal
  e.principal in PrincipalRegistry.authorized
}

pred authorizationValueBinding[i : AdmissionItem] {
  i.value = i.authorization.authorizedValue
}

pred transitionItemOk[e : BatchAdmissionEvent, i : AdmissionItem] {
  i.transition in e.post.transitions - e.pre.transitions
  i.transition = e.post.committedSource[e.targetRecord][i.targetField]
  i.transition.targetRecord = e.targetRecord
  i.transition.targetField = i.targetField
  i.transition.evidence = i.targetEvidence
  i.transition.fromVersion = e.pre.currentVersion[e.targetRecord]
  i.transition.toVersion = e.post.currentVersion[e.targetRecord]
  i.transition.toVersion = successor[i.transition.fromVersion]
  // Transition integrity follows the attempted/committed value. The
  // independent C-auth-value conjunct relates that value to authorization.
  i.transition.value = i.value
  i.transition.value = e.post.committedValue[e.targetRecord][i.targetField]
  i.transition.producer = i.certificate.candidate.producer
  i.transition.authorization = i.authorization
}

pred transitionBijection[e : BatchAdmissionEvent] {
  e.post.transitions = e.pre.transitions + e.items.transition
  all disj i, j : e.items | i.transition != j.transition
  all i : e.items | transitionItemOk[e, i]
  all t : e.post.transitions - e.pre.transitions |
    one i : e.items | i.transition = t
}

pred fullItemOk[e : BatchAdmissionEvent, i : AdmissionItem] {
  certificatePreexists[e, i]
  evidencePreexists[e, i]
  recordBinding[e, i]
  fieldBinding[i]
  evidenceIdentityBinding[i]
  evidenceRecordBinding[e, i]
  versionBinding[i]
  freshBinding[e, i]
  authorizationCertificateBinding[i]
  principalBinding[e, i]
  authorizationValueBinding[i]
  transitionItemOk[e, i]
}

pred batchContract[e : BatchAdmissionEvent, m : Ablation] {
  uniqueItemFields[e]
  snapshotShape[e]
  all i : e.items {
    m != ABL_9 => certificatePreexists[e, i]
    m != ABL_10 => evidencePreexists[e, i]
    m != ABL_3 => recordBinding[e, i]
    m != ABL_1 => fieldBinding[i]
    m != ABL_2a => evidenceIdentityBinding[i]
    m != ABL_2b => evidenceRecordBinding[e, i]
    m != ABL_4a => versionBinding[i]
    m != ABL_4b => freshBinding[e, i]
    m != ABL_5 => authorizationCertificateBinding[i]
    principalBinding[e, i]
    m != ABL_8 => authorizationValueBinding[i]
  }
  m != ABL_6 => transitionBijection[e]
}

pred legalAdmission[e : BatchAdmissionEvent, m : Ablation] {
  stateInvariant[e.pre]
  baseAdmissionEffect[e]
  batchContract[e, m]
}

pred fullAdmissionStep[e : BatchAdmissionEvent] {
  stateInvariant[e.pre]
  rejectedAdmission[e] or legalAdmission[e, Full]
}

// ---------------------------------------------------------------------------
// Property helpers and singleton correspondence
// ---------------------------------------------------------------------------

pred itemContextOk[e : BatchAdmissionEvent, i : AdmissionItem] {
  recordBinding[e, i]
  fieldBinding[i]
  evidenceIdentityBinding[i]
  evidenceRecordBinding[e, i]
  versionBinding[i]
}

pred itemAuthorizationOk[e : BatchAdmissionEvent, i : AdmissionItem] {
  certificatePreexists[e, i]
  evidencePreexists[e, i]
  authorizationCertificateBinding[i]
  principalBinding[e, i]
  authorizationValueBinding[i]
}

pred allItemEffectsVisible[e : BatchAdmissionEvent] {
  all i : e.items {
    e.post.committedValue[e.targetRecord][i.targetField] = i.value
    e.post.committedSource[e.targetRecord][i.targetField] = i.transition
    transitionItemOk[e, i]
  }
  all r : Record - e.targetRecord {
    e.post.committedValue[r] = e.pre.committedValue[r]
    e.post.committedSource[r] = e.pre.committedSource[r]
    e.post.currentVersion[r] = e.pre.currentVersion[r]
  }
}

// The historical singleton contract mapped into a one-item batch. Candidate
// state is auxiliary, exactly as in the historical model; only the attempted
// certificate(s) and target evidence must preexist.
pred historicalSingletonContract[e : BatchAdmissionEvent] {
  #e.items = 1
  all i : e.items {
    certificatePreexists[e, i]
    evidencePreexists[e, i]
    recordBinding[e, i]
    fieldBinding[i]
    evidenceIdentityBinding[i]
    evidenceRecordBinding[e, i]
    versionBinding[i]
    freshBinding[e, i]
    authorizationCertificateBinding[i]
    principalBinding[e, i]
    authorizationValueBinding[i]
    transitionItemOk[e, i]
  }
  transitionBijection[e]
}

pred singletonMappingDomain[e : BatchAdmissionEvent] {
  #e.items = 1
  stateInvariant[e.pre]
  e.targetRecord.authoritativeFields = e.items.targetField
}

pred singletonObservableEffect[e : BatchAdmissionEvent] {
  #e.items = 1
  baseAdmissionEffect[e]
  allItemEffectsVisible[e]
}

// ---------------------------------------------------------------------------
// P6 trace predicate and legal-prefix corruption witnesses
// ---------------------------------------------------------------------------

pred traceComplete[s : State, r : Record, f : Field] {
  some s.committedValue[r][f]
  let src = s.committedSource[r][f] {
    src in s.transitions
    src.targetRecord = r
    src.targetField = f
    src.value = s.committedValue[r][f]
    one u : s.transitions |
      u.targetRecord = r and
      u.targetField = f and
      u.toVersion = src.toVersion
    src.authorization in s.authorizations
    src.certificate in s.certificates
    src.evidence in s.evidence
    sameCanonicalCertificate[
      src.authorization.certificate,
      src.certificate
    ]
    sameEvidenceIdentity[
      src.certificate.candidate.evidence,
      src.evidence
    ]
    src.evidence.record = r
    src.certificate.candidate.targetRecord = r
    src.certificate.candidate.targetField = f
    src.value = src.authorization.authorizedValue
    src.producer = src.certificate.candidate.producer
    src.fromVersion = src.certificate.candidate.expectedVersion
    src.toVersion = successor[src.fromVersion]
  }
}

pred legalPrefix[a : BatchAdmissionEvent, t : TamperEvent] {
  init[a.pre]
  legalAdmission[a, Full]
  stateInvariant[a.post]
  t.pre = a.post
  tamperStep[t]
}

pred anchorLossWitness[a : BatchAdmissionEvent, t : TamperEvent] {
  legalPrefix[a, t]
  some i : a.items {
    let src = i.transition |
      t.post.transitions = t.pre.transitions - src and
      src not in t.post.transitions and
      not traceComplete[t.post, a.targetRecord, i.targetField]
  }
  t.post.transitions != t.pre.transitions
}

pred anchorReplacementWitness[a : BatchAdmissionEvent, t : TamperEvent] {
  legalPrefix[a, t]
  some i : a.items, replacement : Transition - t.pre.transitions {
    let src = i.transition |
      replacement != src and
      replacement.targetRecord = src.targetRecord and
      replacement.targetField = src.targetField and
      replacement.toVersion = src.toVersion and
      t.post.transitions = t.pre.transitions - src + replacement and
      src not in t.post.transitions and
      replacement in t.post.transitions and
      not traceComplete[t.post, a.targetRecord, i.targetField]
  }
  t.post.transitions != t.pre.transitions
}

pred sourceDuplicateWitness[a : BatchAdmissionEvent, t : TamperEvent] {
  legalPrefix[a, t]
  some i : a.items, duplicate : Transition - t.pre.transitions {
    let src = i.transition |
      duplicate != src and
      duplicate.targetRecord = src.targetRecord and
      duplicate.targetField = src.targetField and
      duplicate.toVersion = src.toVersion and
      t.post.transitions = t.pre.transitions + duplicate and
      src in t.post.transitions and
      duplicate in t.post.transitions and
      not traceComplete[t.post, a.targetRecord, i.targetField]
  }
  t.post.transitions != t.pre.transitions
}

// ---------------------------------------------------------------------------
// Effective paired ablation witnesses
// ---------------------------------------------------------------------------

pred corruptFor[e : BatchAdmissionEvent, m : Ablation, bad : AdmissionItem] {
  (m = ABL_1 and not fieldBinding[bad]) or
  (m = ABL_2a and not evidenceIdentityBinding[bad]) or
  (m = ABL_2b and not evidenceRecordBinding[e, bad]) or
  (m = ABL_3 and not recordBinding[e, bad]) or
  (m = ABL_4a and not versionBinding[bad]) or
  (m = ABL_4b and not freshBinding[e, bad]) or
  (m = ABL_5 and not authorizationCertificateBinding[bad]) or
  (m = ABL_6 and not transitionItemOk[e, bad]) or
  (m = ABL_8 and not authorizationValueBinding[bad]) or
  (m = ABL_9 and not certificatePreexists[e, bad]) or
  (m = ABL_10 and not evidencePreexists[e, bad])
}

pred oneCorruptOneValid[e : BatchAdmissionEvent, m : Ablation] {
  m != Full
  m != ABL_7
  #e.items >= 2
  some disj bad, good : e.items |
    corruptFor[e, m, bad] and fullItemOk[e, good]
}

pred effectiveAblationWitness[e : BatchAdmissionEvent, m : Ablation] {
  legalAdmission[e, m]
  oneCorruptOneValid[e, m]
  not sameState[e.pre, e.post]
}

pred sameAttempt[a, b : BatchAdmissionEvent] {
  a.pre = b.pre
  a.items = b.items
  a.targetRecord = b.targetRecord
  a.principal = b.principal
}

pred pairedAblationWitness[m : Ablation] {
  some effective, rejected : BatchAdmissionEvent {
    effective != rejected
    effectiveAblationWitness[effective, m]
    sameAttempt[effective, rejected]
    rejectedAdmission[rejected]
    not batchContract[rejected, Full]
  }
}

// ---------------------------------------------------------------------------
// Non-circular preservation and regression assertions
// ---------------------------------------------------------------------------

assert StateInvariantPreserved {
  all e : BatchAdmissionEvent |
    stateInvariant[e.pre] and
    baseAdmissionEffect[e] and
    batchContract[e, Full] =>
      stateInvariant[e.post]
}

assert P0NoMachineAuthoritativeWrite {
  all e : MachineEvent | machineStep[e] =>
    e.post.committedValue = e.pre.committedValue and
    e.post.committedSource = e.pre.committedSource and
    e.post.currentVersion = e.pre.currentVersion and
    e.post.transitions = e.pre.transitions and
    e.post.authorizations = e.pre.authorizations
}

assert P1ExactContext {
  all e : BatchAdmissionEvent |
    legalAdmission[e, Full] =>
      all i : e.items | itemContextOk[e, i]
}

assert P3AuthorizationIntegrity {
  all e : BatchAdmissionEvent |
    legalAdmission[e, Full] =>
      all i : e.items | itemAuthorizationOk[e, i]
}

assert P4Freshness {
  all e : BatchAdmissionEvent |
    legalAdmission[e, Full] =>
      all i : e.items | freshBinding[e, i]
}

assert P5TransitionBijection {
  all e : BatchAdmissionEvent |
    legalAdmission[e, Full] => transitionBijection[e]
}

assert FullNoPartialItemEffects {
  all e : BatchAdmissionEvent |
    legalAdmission[e, Full] => allItemEffectsVisible[e]
}

assert RejectionHasNoEffect {
  all e : BatchAdmissionEvent |
    rejectedAdmission[e] => sameState[e.pre, e.post]
}

assert SingletonContractEquivalence {
  all e : BatchAdmissionEvent |
    singletonMappingDomain[e] and baseAdmissionEffect[e] =>
      (batchContract[e, Full] iff historicalSingletonContract[e])
}

assert SingletonEffectEquivalence {
  all e : BatchAdmissionEvent |
    #e.items = 1 and legalAdmission[e, Full] =>
      singletonObservableEffect[e]
}

assert FullRejectsAblatedAttempt {
  all e : BatchAdmissionEvent, m : Ablation |
    oneCorruptOneValid[e, m] => not batchContract[e, Full]
}

assert P6MissingAnchorIncomplete {
  all s : State, r : Record, f : Field |
    some s.committedValue[r][f] and
    s.committedSource[r][f] not in s.transitions =>
      not traceComplete[s, r, f]
}

assert P6DuplicateSourceVersionIncomplete {
  all s : State, r : Record, f : Field |
    (some src : s.committedSource[r][f] |
      src in s.transitions and
      some u : s.transitions - src |
        u.targetRecord = r and
        u.targetField = f and
        u.toVersion = src.toVersion) =>
      not traceComplete[s, r, f]
}

// The positive trace-completeness direction is conditional on a well-formed
// pre-state. Without the two preconditions below, the deliberately permissive
// base effect admits a legal Full admission from a state that already carries
// a stray transition to the successor version, and traceComplete then fails
// because the source version is no longer unique. The concrete service
// enforces both preconditions through reverse-trace validation and CAS; this
// assertion makes the dependency explicit rather than assuming it. A mutation
// that deletes the post-state certificate binding flips this assertion to SAT
// (evidence/r27-trace-mutation).
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

// ---------------------------------------------------------------------------
// Reusable legal-witness predicates
// ---------------------------------------------------------------------------

pred batchAcceptMulti[e : BatchAdmissionEvent] {
  legalAdmission[e, Full]
  #e.items >= 2
  all i : e.items |
    i.authorization.authorizedValue = i.certificate.candidate.value
}

pred batchCorrectionMulti[e : BatchAdmissionEvent] {
  legalAdmission[e, Full]
  #e.items >= 2
  all i : e.items |
    i.authorization.authorizedValue != i.certificate.candidate.value
}

pred batchMixed[e : BatchAdmissionEvent] {
  legalAdmission[e, Full]
  #e.items >= 2
  some accept, correction : e.items |
    accept != correction and
    accept.authorization.authorizedValue =
      accept.certificate.candidate.value and
    correction.authorization.authorizedValue !=
      correction.certificate.candidate.value
}

pred batchSameValueMulti[e : BatchAdmissionEvent] {
  legalAdmission[e, Full]
  #e.items >= 2
  some e.pre.committedValue[e.targetRecord]
  some i : e.items |
    e.pre.committedValue[e.targetRecord][i.targetField] = i.value
}

pred batchInitialSnapshot[e : BatchAdmissionEvent] {
  init[e.pre]
  legalAdmission[e, Full]
  #e.items >= 2
  e.items.targetField = e.targetRecord.authoritativeFields
}

pred singletonLegal[e : BatchAdmissionEvent] {
  legalAdmission[e, Full]
  #e.items = 1
}

// ---------------------------------------------------------------------------
// S1 command catalog
// ---------------------------------------------------------------------------

check StateInvariantPreserved for 2 Record, 3 Field, 6 Version, 5 Candidate, 5 Certificate, 5 Authorization, 5 Evidence, 5 Value, 3 Producer, 3 Principal, 5 CertId, 4 State, 4 Event, 6 AdmissionItem, 6 Transition, 2 EvidenceContent, 3 EvidenceLocator
check P0NoMachineAuthoritativeWrite for 2 Record, 3 Field, 6 Version, 5 Candidate, 5 Certificate, 5 Authorization, 5 Evidence, 5 Value, 3 Producer, 3 Principal, 5 CertId, 4 State, 4 Event, 6 AdmissionItem, 6 Transition, 2 EvidenceContent, 3 EvidenceLocator
check P1ExactContext for 2 Record, 3 Field, 6 Version, 5 Candidate, 5 Certificate, 5 Authorization, 5 Evidence, 5 Value, 3 Producer, 3 Principal, 5 CertId, 4 State, 4 Event, 6 AdmissionItem, 6 Transition, 2 EvidenceContent, 3 EvidenceLocator
check P3AuthorizationIntegrity for 2 Record, 3 Field, 6 Version, 5 Candidate, 5 Certificate, 5 Authorization, 5 Evidence, 5 Value, 3 Producer, 3 Principal, 5 CertId, 4 State, 4 Event, 6 AdmissionItem, 6 Transition, 2 EvidenceContent, 3 EvidenceLocator
check P4Freshness for 2 Record, 3 Field, 6 Version, 5 Candidate, 5 Certificate, 5 Authorization, 5 Evidence, 5 Value, 3 Producer, 3 Principal, 5 CertId, 4 State, 4 Event, 6 AdmissionItem, 6 Transition, 2 EvidenceContent, 3 EvidenceLocator
check P5TransitionBijection for 2 Record, 3 Field, 6 Version, 5 Candidate, 5 Certificate, 5 Authorization, 5 Evidence, 5 Value, 3 Producer, 3 Principal, 5 CertId, 4 State, 4 Event, 6 AdmissionItem, 6 Transition, 2 EvidenceContent, 3 EvidenceLocator
check FullNoPartialItemEffects for 2 Record, 3 Field, 6 Version, 5 Candidate, 5 Certificate, 5 Authorization, 5 Evidence, 5 Value, 3 Producer, 3 Principal, 5 CertId, 4 State, 4 Event, 6 AdmissionItem, 6 Transition, 2 EvidenceContent, 3 EvidenceLocator
check RejectionHasNoEffect for 2 Record, 3 Field, 6 Version, 5 Candidate, 5 Certificate, 5 Authorization, 5 Evidence, 5 Value, 3 Producer, 3 Principal, 5 CertId, 4 State, 4 Event, 6 AdmissionItem, 6 Transition, 2 EvidenceContent, 3 EvidenceLocator
check SingletonContractEquivalence for 2 Record, 3 Field, 6 Version, 5 Candidate, 5 Certificate, 5 Authorization, 5 Evidence, 5 Value, 3 Producer, 3 Principal, 5 CertId, 4 State, 4 Event, 6 AdmissionItem, 6 Transition, 2 EvidenceContent, 3 EvidenceLocator
check SingletonEffectEquivalence for 2 Record, 3 Field, 6 Version, 5 Candidate, 5 Certificate, 5 Authorization, 5 Evidence, 5 Value, 3 Producer, 3 Principal, 5 CertId, 4 State, 4 Event, 6 AdmissionItem, 6 Transition, 2 EvidenceContent, 3 EvidenceLocator
check FullRejectsAblatedAttempt for 2 Record, 3 Field, 6 Version, 5 Candidate, 5 Certificate, 5 Authorization, 5 Evidence, 5 Value, 3 Producer, 3 Principal, 5 CertId, 4 State, 4 Event, 6 AdmissionItem, 6 Transition, 2 EvidenceContent, 3 EvidenceLocator
check P6MissingAnchorIncomplete for 2 Record, 3 Field, 6 Version, 5 Candidate, 5 Certificate, 5 Authorization, 5 Evidence, 5 Value, 3 Producer, 3 Principal, 5 CertId, 4 State, 4 Event, 6 AdmissionItem, 6 Transition, 2 EvidenceContent, 3 EvidenceLocator
check P6DuplicateSourceVersionIncomplete for 2 Record, 3 Field, 6 Version, 5 Candidate, 5 Certificate, 5 Authorization, 5 Evidence, 5 Value, 3 Producer, 3 Principal, 5 CertId, 4 State, 4 Event, 6 AdmissionItem, 6 Transition, 2 EvidenceContent, 3 EvidenceLocator
check LegalAdmissionTraceCompleteUnderWellFormedPre for 2 Record, 3 Field, 6 Version, 5 Candidate, 5 Certificate, 5 Authorization, 5 Evidence, 5 Value, 3 Producer, 3 Principal, 5 CertId, 4 State, 4 Event, 6 AdmissionItem, 6 Transition, 2 EvidenceContent, 3 EvidenceLocator

run SAT_BATCH_accept_multi { some e : BatchAdmissionEvent | batchAcceptMulti[e] } for 2 Record, 3 Field, 6 Version, 5 Candidate, 5 Certificate, 5 Authorization, 5 Evidence, 5 Value, 3 Producer, 3 Principal, 5 CertId, 4 State, 4 Event, 6 AdmissionItem, 6 Transition, 2 EvidenceContent, 3 EvidenceLocator
run SAT_BATCH_correction_multi { some e : BatchAdmissionEvent | batchCorrectionMulti[e] } for 2 Record, 3 Field, 6 Version, 5 Candidate, 5 Certificate, 5 Authorization, 5 Evidence, 6 Value, 3 Producer, 3 Principal, 5 CertId, 4 State, 4 Event, 6 AdmissionItem, 6 Transition, 2 EvidenceContent, 3 EvidenceLocator
run SAT_BATCH_mixed_accept_correction { some e : BatchAdmissionEvent | batchMixed[e] } for 2 Record, 3 Field, 6 Version, 5 Candidate, 5 Certificate, 5 Authorization, 5 Evidence, 6 Value, 3 Producer, 3 Principal, 5 CertId, 4 State, 4 Event, 6 AdmissionItem, 6 Transition, 2 EvidenceContent, 3 EvidenceLocator
run SAT_BATCH_same_value_multi { some e : BatchAdmissionEvent | batchSameValueMulti[e] } for 2 Record, 3 Field, 6 Version, 5 Candidate, 5 Certificate, 5 Authorization, 5 Evidence, 5 Value, 3 Producer, 3 Principal, 5 CertId, 4 State, 4 Event, 6 AdmissionItem, 6 Transition, 2 EvidenceContent, 3 EvidenceLocator
run SAT_BATCH_initial_snapshot { some e : BatchAdmissionEvent | batchInitialSnapshot[e] } for 2 Record, 3 Field, 6 Version, 5 Candidate, 5 Certificate, 5 Authorization, 5 Evidence, 5 Value, 3 Producer, 3 Principal, 5 CertId, 4 State, 4 Event, 6 AdmissionItem, 6 Transition, 2 EvidenceContent, 3 EvidenceLocator
run SAT_BATCH_singleton { some e : BatchAdmissionEvent | singletonLegal[e] } for 2 Record, 3 Field, 6 Version, 5 Candidate, 5 Certificate, 5 Authorization, 5 Evidence, 5 Value, 3 Producer, 3 Principal, 5 CertId, 4 State, 4 Event, 6 AdmissionItem, 6 Transition, 2 EvidenceContent, 3 EvidenceLocator

run SAT_ABL_1_effective_pair { pairedAblationWitness[ABL_1] } for 2 Record, 3 Field, 6 Version, 6 Candidate, 6 Certificate, 6 Authorization, 6 Evidence, 6 Value, 3 Producer, 3 Principal, 6 CertId, 4 State, 4 Event, 6 AdmissionItem, 6 Transition, 3 EvidenceContent, 3 EvidenceLocator
run SAT_ABL_2a_effective_pair { pairedAblationWitness[ABL_2a] } for 2 Record, 3 Field, 6 Version, 6 Candidate, 6 Certificate, 6 Authorization, 6 Evidence, 6 Value, 3 Producer, 3 Principal, 6 CertId, 4 State, 4 Event, 6 AdmissionItem, 6 Transition, 3 EvidenceContent, 3 EvidenceLocator
run SAT_ABL_2b_effective_pair { pairedAblationWitness[ABL_2b] } for 2 Record, 3 Field, 6 Version, 6 Candidate, 6 Certificate, 6 Authorization, 6 Evidence, 6 Value, 3 Producer, 3 Principal, 6 CertId, 4 State, 4 Event, 6 AdmissionItem, 6 Transition, 3 EvidenceContent, 3 EvidenceLocator
run SAT_ABL_3_effective_pair { pairedAblationWitness[ABL_3] } for 2 Record, 3 Field, 6 Version, 6 Candidate, 6 Certificate, 6 Authorization, 6 Evidence, 6 Value, 3 Producer, 3 Principal, 6 CertId, 4 State, 4 Event, 6 AdmissionItem, 6 Transition, 3 EvidenceContent, 3 EvidenceLocator
run SAT_ABL_4a_effective_pair { pairedAblationWitness[ABL_4a] } for 2 Record, 3 Field, 6 Version, 6 Candidate, 6 Certificate, 6 Authorization, 6 Evidence, 6 Value, 3 Producer, 3 Principal, 6 CertId, 4 State, 4 Event, 6 AdmissionItem, 6 Transition, 3 EvidenceContent, 3 EvidenceLocator
run SAT_ABL_4b_effective_pair { pairedAblationWitness[ABL_4b] } for 2 Record, 3 Field, 6 Version, 6 Candidate, 6 Certificate, 6 Authorization, 6 Evidence, 6 Value, 3 Producer, 3 Principal, 6 CertId, 4 State, 4 Event, 6 AdmissionItem, 6 Transition, 3 EvidenceContent, 3 EvidenceLocator
run SAT_ABL_5_effective_pair { pairedAblationWitness[ABL_5] } for 2 Record, 3 Field, 6 Version, 6 Candidate, 6 Certificate, 6 Authorization, 6 Evidence, 6 Value, 3 Producer, 3 Principal, 6 CertId, 4 State, 4 Event, 6 AdmissionItem, 6 Transition, 3 EvidenceContent, 3 EvidenceLocator
run SAT_ABL_6_effective_pair { pairedAblationWitness[ABL_6] } for 2 Record, 3 Field, 6 Version, 6 Candidate, 6 Certificate, 6 Authorization, 6 Evidence, 6 Value, 3 Producer, 3 Principal, 6 CertId, 4 State, 4 Event, 6 AdmissionItem, 7 Transition, 3 EvidenceContent, 3 EvidenceLocator
run SAT_ABL_8_effective_pair { pairedAblationWitness[ABL_8] } for 2 Record, 3 Field, 6 Version, 6 Candidate, 6 Certificate, 6 Authorization, 6 Evidence, 6 Value, 3 Producer, 3 Principal, 6 CertId, 4 State, 4 Event, 6 AdmissionItem, 6 Transition, 3 EvidenceContent, 3 EvidenceLocator
run SAT_ABL_9_effective_pair { pairedAblationWitness[ABL_9] } for 2 Record, 3 Field, 6 Version, 6 Candidate, 6 Certificate, 6 Authorization, 6 Evidence, 6 Value, 3 Producer, 3 Principal, 6 CertId, 4 State, 4 Event, 6 AdmissionItem, 6 Transition, 3 EvidenceContent, 3 EvidenceLocator
run SAT_ABL_10_effective_pair { pairedAblationWitness[ABL_10] } for 2 Record, 3 Field, 6 Version, 6 Candidate, 6 Certificate, 6 Authorization, 6 Evidence, 6 Value, 3 Producer, 3 Principal, 6 CertId, 4 State, 4 Event, 6 AdmissionItem, 6 Transition, 3 EvidenceContent, 3 EvidenceLocator

run SAT_P6_legal_anchor_loss { some a : BatchAdmissionEvent, t : TamperEvent | anchorLossWitness[a, t] } for 2 Record, 3 Field, 6 Version, 5 Candidate, 5 Certificate, 5 Authorization, 5 Evidence, 5 Value, 3 Producer, 3 Principal, 5 CertId, 4 State, 4 Event, 5 AdmissionItem, 7 Transition, 2 EvidenceContent, 3 EvidenceLocator
run SAT_P6_legal_anchor_replacement { some a : BatchAdmissionEvent, t : TamperEvent | anchorReplacementWitness[a, t] } for 2 Record, 3 Field, 6 Version, 5 Candidate, 5 Certificate, 5 Authorization, 5 Evidence, 6 Value, 3 Producer, 3 Principal, 5 CertId, 4 State, 4 Event, 5 AdmissionItem, 8 Transition, 2 EvidenceContent, 3 EvidenceLocator
run SAT_P6_legal_source_version_duplicate { some a : BatchAdmissionEvent, t : TamperEvent | sourceDuplicateWitness[a, t] } for 2 Record, 3 Field, 6 Version, 5 Candidate, 5 Certificate, 5 Authorization, 5 Evidence, 6 Value, 3 Producer, 3 Principal, 5 CertId, 4 State, 4 Event, 5 AdmissionItem, 8 Transition, 2 EvidenceContent, 3 EvidenceLocator
