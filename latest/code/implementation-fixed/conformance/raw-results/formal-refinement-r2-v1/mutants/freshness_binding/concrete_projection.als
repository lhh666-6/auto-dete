module concrete_projection
open auto_decte_batch
one sig ConcreteRecord extends Record {}
one sig FieldAtom0, FieldAtom1 extends Field {}
one sig ValueAtom0, ValueAtom1, ValueAtom2 extends Value {}
one sig ProducerAtom0 extends Producer {}
one sig PrincipalAtom0 extends Principal {}
one sig ContentAtom0 extends EvidenceContent {}
one sig LocatorAtom0, LocatorAtom1 extends EvidenceLocator {}
one sig EvidenceAtom0, EvidenceAtom1 extends Evidence {}
one sig VersionAtom0, VersionAtom1 extends Version {}
one sig CandidateAtom0, CandidateAtom1 extends Candidate {}
one sig CertIdAtom0, CertIdAtom1 extends CertId {}
one sig CertificateAtom0, CertificateAtom1 extends Certificate {}
one sig AuthorizationAtom0, AuthorizationAtom1 extends Authorization {}
one sig TransitionAtom0, TransitionAtom1 extends Transition {}
one sig ConcretePre, ConcretePost extends State {}
one sig AdmissionItemAtom0, AdmissionItemAtom1 extends AdmissionItem {}
one sig ConcreteAdmission extends BatchAdmissionEvent {}
fact ConcreteRelations {
  ConcreteRecord.authoritativeFields = FieldAtom0 + FieldAtom1
  PrincipalRegistry.authorized = PrincipalAtom0
  VersionAtom0.record = ConcreteRecord
  VersionAtom0.succ = VersionAtom1
  VersionAtom1.record = ConcreteRecord
  no VersionAtom1.succ
  EvidenceAtom0.record = ConcreteRecord
  EvidenceAtom0.content = ContentAtom0
  EvidenceAtom0.locator = LocatorAtom0
  EvidenceAtom1.record = ConcreteRecord
  EvidenceAtom1.content = ContentAtom0
  EvidenceAtom1.locator = LocatorAtom1
  CandidateAtom0.targetRecord = ConcreteRecord
  CandidateAtom0.targetField = FieldAtom0
  CandidateAtom0.evidence = EvidenceAtom0
  CandidateAtom0.expectedVersion = VersionAtom1
  CandidateAtom0.value = ValueAtom0
  CandidateAtom0.producer = ProducerAtom0
  CertificateAtom0.candidate = CandidateAtom0
  CertificateAtom0.certId = CertIdAtom0
  CandidateAtom1.targetRecord = ConcreteRecord
  CandidateAtom1.targetField = FieldAtom1
  CandidateAtom1.evidence = EvidenceAtom1
  CandidateAtom1.expectedVersion = VersionAtom0
  CandidateAtom1.value = ValueAtom1
  CandidateAtom1.producer = ProducerAtom0
  CertificateAtom1.candidate = CandidateAtom1
  CertificateAtom1.certId = CertIdAtom1
  AuthorizationAtom0.certificate = CertificateAtom0
  AuthorizationAtom0.authorizedValue = ValueAtom0
  AuthorizationAtom0.principal = PrincipalAtom0
  AuthorizationAtom1.certificate = CertificateAtom1
  AuthorizationAtom1.authorizedValue = ValueAtom2
  AuthorizationAtom1.principal = PrincipalAtom0
  TransitionAtom0.targetRecord = ConcreteRecord
  TransitionAtom0.targetField = FieldAtom0
  TransitionAtom0.evidence = EvidenceAtom0
  TransitionAtom0.fromVersion = VersionAtom0
  TransitionAtom0.toVersion = VersionAtom1
  TransitionAtom0.value = ValueAtom0
  TransitionAtom0.producer = ProducerAtom0
  TransitionAtom0.certificate = CertificateAtom0
  TransitionAtom0.authorization = AuthorizationAtom0
  TransitionAtom1.targetRecord = ConcreteRecord
  TransitionAtom1.targetField = FieldAtom1
  TransitionAtom1.evidence = EvidenceAtom1
  TransitionAtom1.fromVersion = VersionAtom0
  TransitionAtom1.toVersion = VersionAtom1
  TransitionAtom1.value = ValueAtom2
  TransitionAtom1.producer = ProducerAtom0
  TransitionAtom1.certificate = CertificateAtom1
  TransitionAtom1.authorization = AuthorizationAtom1
  no ConcretePre.committedValue
  no ConcretePre.committedSource
  ConcretePre.currentVersion = ConcreteRecord -> VersionAtom0
  no ConcretePre.transitions
  no ConcretePre.candidates
  ConcretePre.certificates = CertificateAtom0 + CertificateAtom1
  no ConcretePre.authorizations
  ConcretePre.evidence = EvidenceAtom0 + EvidenceAtom1
  ConcretePost.committedValue = ConcreteRecord -> FieldAtom0 -> ValueAtom0 + ConcreteRecord -> FieldAtom1 -> ValueAtom2
  ConcretePost.committedSource = ConcreteRecord -> FieldAtom0 -> TransitionAtom0 + ConcreteRecord -> FieldAtom1 -> TransitionAtom1
  ConcretePost.currentVersion = ConcreteRecord -> VersionAtom1
  ConcretePost.transitions = TransitionAtom0 + TransitionAtom1
  no ConcretePost.candidates
  ConcretePost.certificates = CertificateAtom0 + CertificateAtom1
  ConcretePost.authorizations = AuthorizationAtom0 + AuthorizationAtom1
  ConcretePost.evidence = EvidenceAtom0 + EvidenceAtom1
  AdmissionItemAtom0.certificate = CertificateAtom0
  AdmissionItemAtom0.authorization = AuthorizationAtom0
  AdmissionItemAtom0.targetRecord = ConcreteRecord
  AdmissionItemAtom0.targetField = FieldAtom0
  AdmissionItemAtom0.targetEvidence = EvidenceAtom0
  AdmissionItemAtom0.expectedVersion = VersionAtom1
  AdmissionItemAtom0.value = ValueAtom0
  AdmissionItemAtom0.transition = TransitionAtom0
  AdmissionItemAtom1.certificate = CertificateAtom1
  AdmissionItemAtom1.authorization = AuthorizationAtom1
  AdmissionItemAtom1.targetRecord = ConcreteRecord
  AdmissionItemAtom1.targetField = FieldAtom1
  AdmissionItemAtom1.targetEvidence = EvidenceAtom1
  AdmissionItemAtom1.expectedVersion = VersionAtom0
  AdmissionItemAtom1.value = ValueAtom2
  AdmissionItemAtom1.transition = TransitionAtom1
  ConcreteAdmission.pre = ConcretePre
  ConcreteAdmission.post = ConcretePost
  ConcreteAdmission.items = AdmissionItemAtom0 + AdmissionItemAtom1
  ConcreteAdmission.targetRecord = ConcreteRecord
  ConcreteAdmission.principal = PrincipalAtom0
}
pred ConcreteRefinement {
  legalAdmission[ConcreteAdmission, Full]
}
run ConcreteRefinement for exactly 1 Record, exactly 2 Field, exactly 3 Value, exactly 1 Producer, exactly 1 Principal, exactly 1 EvidenceContent, exactly 2 EvidenceLocator, exactly 2 Evidence, exactly 2 Version, exactly 2 Candidate, exactly 2 CertId, exactly 2 Certificate, exactly 2 Authorization, exactly 2 Transition, exactly 2 State, exactly 2 AdmissionItem, exactly 1 BatchAdmissionEvent, exactly 0 MachineEvent, exactly 0 TamperEvent
