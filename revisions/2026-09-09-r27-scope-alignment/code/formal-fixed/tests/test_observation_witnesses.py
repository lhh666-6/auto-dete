from dataclasses import fields, replace
import json
from pathlib import Path
import sys
import unittest


FORMAL_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(FORMAL_ROOT))

from observation_witnesses import (  # noqa: E402
    CLASSES,
    BatchItem,
    build_report,
    copy_forward_control,
    History,
    normative_outcome,
    observe,
    paired_histories,
    project,
    SourceAnchor,
    SourceTransition,
    CommitStep,
    FieldValue,
    validate_history_domain,
)


class ObservationWitnessTests(unittest.TestCase):
    def test_effect_domain_matches_actual_changes(self) -> None:
        for safe, unsafe in paired_histories().values():
            for history in (safe, unsafe):
                before = {v.field_id: v.value for v in history.predecessor_values}
                after = {v.field_id: v.value for v in history.successor_values}
                self.assertEqual(history.committed_fields,
                                 frozenset(f for f in before if before[f] != after[f]))

    def test_unresolvable_source_is_not_a_complete_trace(self) -> None:
        safe, _ = paired_histories()["D_S"]
        changed = replace(safe, sources=(SourceAnchor("score", "missing-transition"),))
        self.assertEqual(validate_history_domain(changed), ())
        self.assertEqual(normative_outcome(changed)[0], "inadmissible")
        self.assertEqual(normative_outcome(changed)[2], "incomplete-trace")

    def test_batch_fragmentation_has_connected_real_intermediate_state(self) -> None:
        safe, unsafe = paired_histories()["D_B"]
        self.assertEqual(safe.successor_count, 1)
        self.assertEqual(unsafe.successor_count, 2)
        self.assertEqual(unsafe.commits[0].after, unsafe.commits[1].before)
        self.assertEqual(unsafe.commits[0].changed_fields, frozenset({"score"}))
        self.assertEqual(unsafe.commits[1].changed_fields, frozenset({"status"}))
        self.assertEqual(normative_outcome(unsafe),
                         ("inadmissible", "fragmented-successor", "complete-trace"))
        stored = {f.name for f in fields(History)}
        self.assertNotIn("committed_fields", stored)
        self.assertNotIn("successor_count", stored)

    def test_disconnected_commit_sequence_is_rejected(self) -> None:
        _, unsafe = paired_histories()["D_B"]
        broken = replace(unsafe.commits[1], before=unsafe.predecessor_values)
        self.assertIn("disconnected commit sequence",
                      validate_history_domain(replace(unsafe, commits=(unsafe.commits[0], broken))))

    def test_source_wrong_value_wrong_field_and_ambiguity_are_rejected(self) -> None:
        safe, _ = paired_histories()["D_B"]
        original = safe.source_transitions[-1]
        variants = (
            safe.source_transitions[:-1] + (replace(original, value=999),),
            safe.source_transitions[:-1] + (replace(original, field_id="score"),),
            safe.source_transitions + (original,),
        )
        for transitions in variants:
            changed = replace(safe, source_transitions=transitions)
            self.assertEqual(validate_history_domain(changed), ())
            self.assertEqual(normative_outcome(changed)[2], "incomplete-trace")

    def test_unchanged_field_requires_exact_source_copy_forward(self) -> None:
        safe, _ = paired_histories()["D_B"]
        before = (FieldValue("score", 90), FieldValue("status", 50))
        same_source = replace(
            safe, predecessor_values=before,
            commits=(CommitStep("successor-1", before, safe.successor_values),),
            predecessor_sources=(SourceAnchor("score", "prior-score"),
                                 SourceAnchor("status", "transition-status")))
        self.assertEqual(validate_history_domain(same_source), ())
        self.assertEqual(normative_outcome(same_source)[2], "complete-trace")
        changed_source = replace(
            same_source,
            sources=(SourceAnchor("score", "transition-score"),
                     SourceAnchor("status", "replacement-status")),
            source_transitions=same_source.source_transitions +
                              (SourceTransition("replacement-status", "status", 50),))
        self.assertEqual(normative_outcome(changed_source)[2], "incomplete-trace")

    def test_context_observation_includes_actual_target(self) -> None:
        safe, _ = paired_histories()["D_C"]
        wrong_target = replace(safe, target_record_id="record-B")
        self.assertNotEqual(observe(safe, "D_C"), observe(wrong_target, "D_C"))

    def test_observations_and_outcomes_are_derived_not_stored(self) -> None:
        stored_fields = {field.name for field in fields(History)}
        self.assertNotIn("observations", stored_fields)
        self.assertNotIn("outcome", stored_fields)

    def test_each_pair_is_realizable_and_satisfies_irredundancy(self) -> None:
        pairs = paired_histories()
        self.assertEqual(set(pairs), set(CLASSES))

        for omitted, (safe, unsafe) in pairs.items():
            with self.subTest(omitted=omitted):
                self.assertEqual(validate_history_domain(safe), ())
                self.assertEqual(validate_history_domain(unsafe), ())
                self.assertNotEqual(safe, unsafe)

                remaining = tuple(item for item in CLASSES if item != omitted)
                self.assertNotEqual(
                    normative_outcome(safe), normative_outcome(unsafe)
                )
                self.assertEqual(project(safe, remaining), project(unsafe, remaining))
                self.assertNotEqual(project(safe, CLASSES), project(unsafe, CLASSES))

    def test_dual_value_pair_retains_candidate_identity_and_value(self) -> None:
        safe, unsafe = paired_histories()["D_V"]
        safe_candidates = {item.candidate_id: item for item in safe.candidates}
        unsafe_candidates = {item.candidate_id: item for item in unsafe.candidates}

        self.assertEqual(observe(safe, "D_C"), observe(unsafe, "D_C"))
        self.assertEqual(safe_candidates, unsafe_candidates)
        self.assertNotEqual(observe(safe, "D_V"), observe(unsafe, "D_V"))

    def test_batch_and_source_observations_are_separate(self) -> None:
        batch_safe, batch_unsafe = paired_histories()["D_B"]
        source_safe, source_unsafe = paired_histories()["D_S"]

        self.assertEqual(observe(batch_safe, "D_S"), observe(batch_unsafe, "D_S"))
        self.assertEqual(observe(source_safe, "D_B"), observe(source_unsafe, "D_B"))

    def test_domain_validator_rejects_an_unrealizable_reference(self) -> None:
        safe, _ = paired_histories()["D_B"]
        malformed = replace(
            safe,
            batch_items=(
                BatchItem("missing-candidate", safe.batch_items[0].authorization_id),
                safe.batch_items[1],
            ),
        )
        self.assertTrue(validate_history_domain(malformed))

    def test_copy_forward_control_is_a_complete_successor(self) -> None:
        control = copy_forward_control()
        self.assertEqual(validate_history_domain(control), ())
        self.assertEqual(control.declared_item_fields, frozenset({"score"}))
        self.assertEqual(control.schema_field_domain, frozenset({"score", "status"}))
        self.assertEqual(control.committed_fields, frozenset({"score"}))
        self.assertEqual(
            normative_outcome(control),
            ("admissible", "complete-successor", "complete-trace"),
        )

    def test_schema_and_declared_item_domains_are_distinguished(self) -> None:
        control = copy_forward_control()
        self.assertNotEqual(control.declared_item_fields, control.schema_field_domain)
        self.assertNotEqual(normative_outcome(control)[1], "partial-successor")

    def test_canonical_value_equality_drives_commit_effects(self) -> None:
        step = CommitStep("s", (FieldValue("score", 2),), (FieldValue("score", 2.0),))
        self.assertEqual(step.changed_fields, frozenset({"score"}))
        unchanged = CommitStep("s", (FieldValue("score", 2),), (FieldValue("score", 2),))
        self.assertEqual(unchanged.changed_fields, frozenset())

    def test_audit_report_is_json_serializable(self) -> None:
        json.dumps(build_report())


if __name__ == "__main__":
    unittest.main()
