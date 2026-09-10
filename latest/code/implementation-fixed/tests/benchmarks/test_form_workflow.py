from pathlib import Path

from benchmarks.form_workflow import run_synthetic_form_workflow
from benchmarks.synthetic import render_form


def test_synthetic_form_workflow_reaches_versioned_fact_and_export_trace(
    tmp_path: Path,
) -> None:
    form = render_form(
        [str(value) for value in range(10)],
        [value % 2 == 0 for value in range(10)],
        seed=31,
        template_id="TEMPLATE-A",
        template_version="1",
    )

    outcome = run_synthetic_form_workflow(form, tmp_path, form_id="FORM-31")

    assert outcome.candidate_count == 20
    assert outcome.record_version == 1
    assert outcome.export_trace_success is True
    assert set(outcome.audit_events) >= {
        "IMPORT",
        "CLASSIFY",
        "RECOGNIZE",
        "CONFIRM",
        "EXPORT",
    }
