module concrete_projection
open auto_decte_batch
one sig ConcreteRecord extends Record {}
one sig FieldAtom0, FieldAtom1 extends Field {}
one sig ValueAtom0, ValueAtom1, ValueAtom2 extends Value {}
one sig ProducerAtom0 extends Producer {}
one sig PrincipalAtom0 extends Principal {}
one sig ContentAtom0 extends EvidenceContent {}
one sig LocatorAtom0, LocatorAtom1, LocatorAtom2 extends EvidenceLocator {}
one sig EvidenceAtom0, EvidenceAtom1, EvidenceAtom2 extends Evidence {}
one sig VersionAtom0, VersionAtom1, VersionAtom2 extends Version {}
one sig CandidateAtom0, CandidateAtom1, CandidateAtom2 extends Candidate {}
one sig CertIdAtom0, CertIdAtom1, CertIdAtom2 extends CertId {}
one sig CertificateAtom0, CertificateAtom1, CertificateAtom2 extends Certificate {}
one sig AuthorizationAtom0, AuthorizationAtom1, AuthorizationAtom2 extends Authorization {}
one sig TransitionAtom0, TransitionAtom1, TransitionAtom2 extends Transition {}
one sig ConcretePre, ConcretePost extends State {}
one sig AdmissionItemAtom0 extends AdmissionItem {}
one sig ConcreteAdmission extends BatchAdmissionEvent {}
fact ConcreteRelations {
  ConcreteRecord.authoritativeFields = FieldAtom0 + FieldAtom1
  PrincipalRegistry.authorized = PrincipalAtom0
  VersionAtom0.record = ConcreteRecord
  VersionAtom0.succ = VersionAtom1
  VersionAtom1.record = ConcreteRecord
  VersionAtom1.succ = VersionAtom2
  VersionAtom2.record = ConcreteRecord
  no VersionAtom2.succ
  EvidenceAtom0.record = ConcreteRecord
  EvidenceAtom0.content = ContentAtom0
  EvidenceAtom0.locator = LocatorAtom2
  EvidenceAtom1.record = ConcreteRecord
  EvidenceAtom1.content = ContentAtom0
  EvidenceAtom1.locator = LocatorAtom0
  EvidenceAtom2.record = ConcreteRecord
  EvidenceAtom2.content = ContentAtom0
  EvidenceAtom2.locator = LocatorAtom1
  CandidateAtom0.targetRecord = ConcreteRecord
  CandidateAtom0.targetField = FieldAtom0
  CandidateAtom0.evidence = EvidenceAtom1
  CandidateAtom0.expectedVersion = VersionAtom1
  CandidateAtom0.value = ValueAtom2
  CandidateAtom0.producer = ProducerAtom0
  CertificateAtom0.candidate = CandidateAtom0
  CertificateAtom0.certId = CertIdAtom0
  CandidateAtom1.targetRecord = ConcreteRecord
  CandidateAtom1.targetField = FieldAtom1
  CandidateAtom1.evidence = EvidenceAtom0
  CandidateAtom1.expectedVersion = VersionAtom0
  CandidateAtom1.value = ValueAtom1
  CandidateAtom1.producer = ProducerAtom0
  CertificateAtom1.candidate = CandidateAtom1
  CertificateAtom1.certId = CertIdAtom1
  CandidateAtom2.targetRecord = ConcreteRecord
  CandidateAtom2.targetField = FieldAtom0
  CandidateAtom2.evidence = EvidenceAtom2
  CandidateAtom2.expectedVersion = VersionAtom0
  CandidateAtom2.value = ValueAtom0
  CandidateAtom2.producer = ProducerAtom0
  CertificateAtom2.candidate = CandidateAtom2
  CertificateAtom2.certId = CertIdAtom2
  AuthorizationAtom0.certificate = CertificateAtom2
  AuthorizationAtom0.authorizedValue = ValueAtom0
  AuthorizationAtom0.principal = PrincipalAtom0
  AuthorizationAtom1.certificate = CertificateAtom1
  AuthorizationAtom1.authorizedValue = ValueAtom1
  AuthorizationAtom1.principal = PrincipalAtom0
  AuthorizationAtom2.certificate = CertificateAtom0
  AuthorizationAtom2.authorizedValue = ValueAtom2
  AuthorizationAtom2.principal = PrincipalAtom0
  TransitionAtom0.targetRecord = ConcreteRecord
  TransitionAtom0.targetField = FieldAtom0
  TransitionAtom0.evidence = EvidenceAtom2
  TransitionAtom0.fromVersion = VersionAtom0
  TransitionAtom0.toVersion = VersionAtom1
  TransitionAtom0.value = ValueAtom0
  TransitionAtom0.producer = ProducerAtom0
  TransitionAtom0.certificate = CertificateAtom2
  TransitionAtom0.authorization = AuthorizationAtom0
  TransitionAtom1.targetRecord = ConcreteRecord
  TransitionAtom1.targetField = FieldAtom1
  TransitionAtom1.evidence = EvidenceAtom0
  TransitionAtom1.fromVersion = VersionAtom0
  TransitionAtom1.toVersion = VersionAtom1
  TransitionAtom1.value = ValueAtom1
  TransitionAtom1.producer = ProducerAtom0
  TransitionAtom1.certificate = CertificateAtom1
  TransitionAtom1.authorization = AuthorizationAtom1
  TransitionAtom2.targetRecord = ConcreteRecord
  TransitionAtom2.targetField = FieldAtom0
  TransitionAtom2.evidence = EvidenceAtom1
  TransitionAtom2.fromVersion = VersionAtom1
  TransitionAtom2.toVersion = VersionAtom2
  TransitionAtom2.value = ValueAtom2
  TransitionAtom2.producer = ProducerAtom0
  TransitionAtom2.certificate = CertificateAtom0
  TransitionAtom2.authorization = AuthorizationAtom2
  ConcretePre.committedValue = ConcreteRecord -> FieldAtom0 -> ValueAtom0 + ConcreteRecord -> FieldAtom1 -> ValueAtom1
  ConcretePre.committedSource = ConcreteRecord -> FieldAtom0 -> TransitionAtom0 + ConcreteRecord -> FieldAtom1 -> TransitionAtom1
  ConcretePre.currentVersion = ConcreteRecord -> VersionAtom1
  ConcretePre.transitions = TransitionAtom0 + TransitionAtom1
  no ConcretePre.candidates
  ConcretePre.certificates = CertificateAtom0 + CertificateAtom1 + CertificateAtom2
  ConcretePre.authorizations = AuthorizationAtom0 + AuthorizationAtom1
  ConcretePre.evidence = EvidenceAtom0 + EvidenceAtom1 + EvidenceAtom2
  ConcretePost.committedValue = ConcreteRecord -> FieldAtom0 -> ValueAtom2 + ConcreteRecord -> FieldAtom1 -> ValueAtom1
  ConcretePost.committedSource = ConcreteRecord -> FieldAtom0 -> TransitionAtom2 + ConcreteRecord -> FieldAtom1 -> TransitionAtom1
  ConcretePost.currentVersion = ConcreteRecord -> VersionAtom2
  ConcretePost.transitions = TransitionAtom0 + TransitionAtom1 + TransitionAtom2
  no ConcretePost.candidates
  ConcretePost.certificates = CertificateAtom0 + CertificateAtom1 + CertificateAtom2
  ConcretePost.authorizations = AuthorizationAtom0 + AuthorizationAtom1 + AuthorizationAtom2
  ConcretePost.evidence = EvidenceAtom0 + EvidenceAtom1 + EvidenceAtom2
  AdmissionItemAtom0.certificate = CertificateAtom0
  AdmissionItemAtom0.authorization = AuthorizationAtom2
  AdmissionItemAtom0.targetRecord = ConcreteRecord
  AdmissionItemAtom0.targetField = FieldAtom0
  AdmissionItemAtom0.targetEvidence = EvidenceAtom1
  AdmissionItemAtom0.expectedVersion = VersionAtom1
  AdmissionItemAtom0.value = ValueAtom2
  AdmissionItemAtom0.transition = TransitionAtom2
  ConcreteAdmission.pre = ConcretePre
  ConcreteAdmission.post = ConcretePost
  ConcreteAdmission.items = AdmissionItemAtom0
  ConcreteAdmission.targetRecord = ConcreteRecord
  ConcreteAdmission.principal = PrincipalAtom0
}
pred ConcreteRefinement {
  legalAdmission[ConcreteAdmission, Full]
}
run ConcreteRefinement for exactly 1 Record, exactly 2 Field, exactly 3 Value, exactly 1 Producer, exactly 1 Principal, exactly 1 EvidenceContent, exactly 3 EvidenceLocator, exactly 3 Evidence, exactly 3 Version, exactly 3 Candidate, exactly 3 CertId, exactly 3 Certificate, exactly 3 Authorization, exactly 3 Transition, exactly 2 State, exactly 1 AdmissionItem, exactly 1 BatchAdmissionEvent, exactly 0 MachineEvent, exactly 0 TamperEvent
