module concrete_projection
open auto_decte_batch
one sig ConcreteRecord extends Record {}
one sig FieldAtom0 extends Field {}
one sig ValueAtom0, ValueAtom1 extends Value {}
one sig ProducerAtom0 extends Producer {}
one sig PrincipalAtom0 extends Principal {}
one sig ContentAtom0 extends EvidenceContent {}
one sig LocatorAtom0 extends EvidenceLocator {}
one sig EvidenceAtom0 extends Evidence {}
one sig VersionAtom0, VersionAtom1 extends Version {}
one sig CandidateAtom0 extends Candidate {}
one sig CertIdAtom0 extends CertId {}
one sig CertificateAtom0 extends Certificate {}
one sig AuthorizationAtom0 extends Authorization {}
one sig TransitionAtom0 extends Transition {}
one sig ConcretePre, ConcretePost extends State {}
one sig AdmissionItemAtom0 extends AdmissionItem {}
one sig ConcreteAdmission extends BatchAdmissionEvent {}
fact ConcreteRelations {
  ConcreteRecord.authoritativeFields = FieldAtom0
  PrincipalRegistry.authorized = PrincipalAtom0
  VersionAtom0.record = ConcreteRecord
  VersionAtom0.succ = VersionAtom1
  VersionAtom1.record = ConcreteRecord
  no VersionAtom1.succ
  EvidenceAtom0.record = ConcreteRecord
  EvidenceAtom0.content = ContentAtom0
  EvidenceAtom0.locator = LocatorAtom0
  CandidateAtom0.targetRecord = ConcreteRecord
  CandidateAtom0.targetField = FieldAtom0
  CandidateAtom0.evidence = EvidenceAtom0
  CandidateAtom0.expectedVersion = VersionAtom0
  CandidateAtom0.value = ValueAtom0
  CandidateAtom0.producer = ProducerAtom0
  CertificateAtom0.candidate = CandidateAtom0
  CertificateAtom0.certId = CertIdAtom0
  AuthorizationAtom0.certificate = CertificateAtom0
  AuthorizationAtom0.authorizedValue = ValueAtom1
  AuthorizationAtom0.principal = PrincipalAtom0
  TransitionAtom0.targetRecord = ConcreteRecord
  TransitionAtom0.targetField = FieldAtom0
  TransitionAtom0.evidence = EvidenceAtom0
  TransitionAtom0.fromVersion = VersionAtom0
  TransitionAtom0.toVersion = VersionAtom1
  TransitionAtom0.value = ValueAtom1
  TransitionAtom0.producer = ProducerAtom0
  TransitionAtom0.certificate = CertificateAtom0
  TransitionAtom0.authorization = AuthorizationAtom0
  no ConcretePre.committedValue
  no ConcretePre.committedSource
  ConcretePre.currentVersion = ConcreteRecord -> VersionAtom0
  no ConcretePre.transitions
  no ConcretePre.candidates
  ConcretePre.certificates = CertificateAtom0
  no ConcretePre.authorizations
  ConcretePre.evidence = EvidenceAtom0
  ConcretePost.committedValue = ConcreteRecord -> FieldAtom0 -> ValueAtom1
  ConcretePost.committedSource = ConcreteRecord -> FieldAtom0 -> TransitionAtom0
  ConcretePost.currentVersion = ConcreteRecord -> VersionAtom1
  ConcretePost.transitions = TransitionAtom0
  no ConcretePost.candidates
  ConcretePost.certificates = CertificateAtom0
  ConcretePost.authorizations = AuthorizationAtom0
  ConcretePost.evidence = EvidenceAtom0
  AdmissionItemAtom0.certificate = CertificateAtom0
  AdmissionItemAtom0.authorization = AuthorizationAtom0
  AdmissionItemAtom0.targetRecord = ConcreteRecord
  AdmissionItemAtom0.targetField = FieldAtom0
  AdmissionItemAtom0.targetEvidence = EvidenceAtom0
  AdmissionItemAtom0.expectedVersion = VersionAtom0
  AdmissionItemAtom0.value = ValueAtom1
  AdmissionItemAtom0.transition = TransitionAtom0
  ConcreteAdmission.pre = ConcretePre
  ConcreteAdmission.post = ConcretePost
  ConcreteAdmission.items = AdmissionItemAtom0
  ConcreteAdmission.targetRecord = ConcreteRecord
  ConcreteAdmission.principal = PrincipalAtom0
}
pred ConcreteRefinement {
  legalAdmission[ConcreteAdmission, Full]
}
run ConcreteRefinement for exactly 1 Record, exactly 1 Field, exactly 2 Value, exactly 1 Producer, exactly 1 Principal, exactly 1 EvidenceContent, exactly 1 EvidenceLocator, exactly 1 Evidence, exactly 2 Version, exactly 1 Candidate, exactly 1 CertId, exactly 1 Certificate, exactly 1 Authorization, exactly 1 Transition, exactly 2 State, exactly 1 AdmissionItem, exactly 1 BatchAdmissionEvent, exactly 0 MachineEvent, exactly 0 TamperEvent
