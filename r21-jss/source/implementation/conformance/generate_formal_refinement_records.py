"""Generate the immutable R2 concrete-to-Alloy refinement evidence bundle."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import tempfile
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.application.review_forms import AuthorityRejectionError, ConcurrentReviewError
from tests.conformance.alloy_projection import (
    AlloyOutcome,
    capture_authority_snapshot,
    project_committed_admission,
    project_rejected_admission,
    run_projection,
)
from tests.conformance.test_g3b_conformance import _env, _record_machine

FREEZE_ID = "formal-refinement-r2-v1"
MUTATIONS = (
    "item_field_binding",
    "evidence_identity_binding",
    "version_binding",
    "freshness_binding",
    "authorization_certificate_binding",
    "principal_binding",
    "authorization_value_binding",
    "transition_bijection",
    "certificate_preexists",
    "evidence_preexists",
    "committed_value_effect",
    "committed_source_effect",
    "transition_field_binding",
    "transition_evidence_binding",
    "transition_version_binding",
    "transition_value_binding",
    "transition_producer_binding",
    "transition_certificate_binding",
    "transition_authorization_binding",
    "initial_snapshot_domain",
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _initial_projection(
    workspace: Path,
    *,
    candidate_values: dict[str, Any],
    committed_values: dict[str, Any],
):
    engine, repository, reviews, recognition, field_ids = _env(workspace, list(candidate_values))
    certificates = {
        field: _record_machine(repository, recognition, field_ids[field], value)
        for field, value in candidate_values.items()
    }
    reviews.confirm(
        "FORM-1",
        0,
        committed_values,
        "reviewer-1",
        "R2 frozen projection",
        certificate_ids_by_field={
            field: certificates[field].certificate_id for field in committed_values
        },
        manual_evidence_ids_by_field={},
    )
    projection = project_committed_admission(
        repository,
        form_id="FORM-1",
        version=1,
        declared_fields=tuple(candidate_values),
    )
    return projection, engine, repository, reviews, recognition, field_ids


def main(output: Path | None = None) -> None:
    repo_root = Path(__file__).resolve().parents[1]
    freeze_root = output or repo_root / "conformance" / "raw-results" / FREEZE_ID
    if freeze_root.exists():
        raise FileExistsError(f"refusing to overwrite evidence freeze {freeze_root}")
    freeze_root.mkdir(parents=True)
    rows: list[dict[str, Any]] = []

    def execute(case: str, projection, expected: AlloyOutcome) -> None:
        outcome = run_projection(projection, freeze_root / case)
        if outcome is not expected:
            raise RuntimeError(f"{case}: expected {expected}, got {outcome}")
        case_root = freeze_root / case
        rows.append(
            {
                "case": case,
                "projection_outcome": projection.payload["outcome"],
                "alloy_outcome": str(outcome),
                "projection_sha256": _sha256(case_root / "projection.json"),
                "wrapper_sha256": _sha256(case_root / "concrete_projection.als"),
                "receipt_sha256": _sha256(case_root / "alloy-result" / "receipt.json"),
            }
        )

    with tempfile.TemporaryDirectory(prefix="auto-decte-r2-") as temp:
        work_root = Path(temp)
        cases = {
            "singleton-accept": ({"a": 1}, {"a": 1}),
            "singleton-correction": ({"a": 1}, {"a": 10}),
            "multi-all-accept": ({"a": 1, "b": 2}, {"a": 1, "b": 2}),
            "multi-all-correction": (
                {"a": 1, "b": 2},
                {"a": 10, "b": 20},
            ),
            "multi-mixed": ({"a": 1, "b": 2}, {"a": 1, "b": 20}),
            "initial-batch": (
                {"a": 1, "b": 2, "c": 3},
                {"a": 1, "b": 2, "c": 3},
            ),
        }
        mixed_projection = None
        for case, (candidate_values, committed_values) in cases.items():
            workspace = work_root / case
            workspace.mkdir()
            projection, engine, _, _, _, _ = _initial_projection(
                workspace,
                candidate_values=candidate_values,
                committed_values=committed_values,
            )
            execute(case, projection, AlloyOutcome.SAT)
            engine.dispose()
            if case == "multi-mixed":
                mixed_projection = projection

        delta_workspace = work_root / "unchanged-source-copy-forward"
        delta_workspace.mkdir()
        _, engine, repository, reviews, recognition, field_ids = _initial_projection(
            delta_workspace,
            candidate_values={"a": 1, "b": 2},
            committed_values={"a": 1, "b": 2},
        )
        certificate = _record_machine(repository, recognition, field_ids["a"], 3)
        reviews.confirm(
            "FORM-1",
            1,
            {"a": 3},
            "reviewer-1",
            "delta",
            certificate_ids_by_field={"a": certificate.certificate_id},
            manual_evidence_ids_by_field={},
        )
        execute(
            "unchanged-source-copy-forward",
            project_committed_admission(
                repository,
                form_id="FORM-1",
                version=2,
                declared_fields=("a", "b"),
            ),
            AlloyOutcome.SAT,
        )
        engine.dispose()

        stale_workspace = work_root / "stale-rejection"
        stale_workspace.mkdir()
        _, engine, repository, reviews, _, _ = _initial_projection(
            stale_workspace,
            candidate_values={"a": 1},
            committed_values={"a": 1},
        )
        stale_certificate = repository.list_certificates_for_form("FORM-1")[0]
        before = capture_authority_snapshot(repository, form_id="FORM-1")
        try:
            reviews.confirm(
                "FORM-1",
                0,
                {"a": 2},
                "reviewer-2",
                "stale",
                certificate_ids_by_field={"a": stale_certificate.certificate_id},
                manual_evidence_ids_by_field={},
            )
        except ConcurrentReviewError:
            pass
        else:
            raise RuntimeError("stale fixture unexpectedly committed")
        after = capture_authority_snapshot(repository, form_id="FORM-1")
        execute(
            "stale-rejection",
            project_rejected_admission(
                repository,
                form_id="FORM-1",
                declared_fields=("a",),
                expected_version=0,
                attempted_values={"a": 2},
                certificate_ids_by_field={"a": stale_certificate.certificate_id},
                principal="reviewer-2",
                before=before,
                after=after,
            ),
            AlloyOutcome.SAT,
        )
        engine.dispose()

        invalid_workspace = work_root / "invalid-item-rejection"
        invalid_workspace.mkdir()
        engine, repository, reviews, recognition, field_ids = _env(invalid_workspace, ["a", "b"])
        cert_a = _record_machine(repository, recognition, field_ids["a"], 1)
        _record_machine(repository, recognition, field_ids["b"], 2)
        before = capture_authority_snapshot(repository, form_id="FORM-1")
        try:
            reviews.confirm(
                "FORM-1",
                0,
                {"a": 1, "b": 2},
                "reviewer-1",
                "invalid item",
                certificate_ids_by_field={
                    "a": cert_a.certificate_id,
                    "b": cert_a.certificate_id,
                },
                manual_evidence_ids_by_field={},
            )
        except AuthorityRejectionError:
            pass
        else:
            raise RuntimeError("invalid-item fixture unexpectedly committed")
        after = capture_authority_snapshot(repository, form_id="FORM-1")
        execute(
            "invalid-item-rejection",
            project_rejected_admission(
                repository,
                form_id="FORM-1",
                declared_fields=("a", "b"),
                expected_version=0,
                attempted_values={"a": 1, "b": 2},
                certificate_ids_by_field={
                    "a": cert_a.certificate_id,
                    "b": cert_a.certificate_id,
                },
                principal="reviewer-1",
                before=before,
                after=after,
            ),
            AlloyOutcome.SAT,
        )
        engine.dispose()

        if mixed_projection is None:
            raise RuntimeError("mixed projection was not generated")
        for mutation in MUTATIONS:
            execute(
                f"mutants/{mutation}",
                mixed_projection.with_mutation(mutation),
                AlloyOutcome.UNSAT,
            )

    manifest = {
        "freeze_id": FREEZE_ID,
        "schema": "auto-decte-formal-refinement-manifest-v1",
        "case_count": len(rows),
        "sat_count": sum(row["alloy_outcome"] == "SAT" for row in rows),
        "unsat_count": sum(row["alloy_outcome"] == "UNSAT" for row in rows),
        "cases": rows,
    }
    (freeze_root / "manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(
        f"FORMAL_REFINEMENT_FREEZE_PASS {FREEZE_ID} "
        f"CASES={manifest['case_count']} SAT={manifest['sat_count']} "
        f"UNSAT={manifest['unsat_count']}"
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    arguments = parser.parse_args()
    main(arguments.output.resolve() if arguments.output else None)
