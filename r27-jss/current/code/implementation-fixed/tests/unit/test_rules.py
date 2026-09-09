import pytest

from app.domain.models import ExportStatus
from app.domain.rules import RuleContext, validate


def valid_context(**overrides: object) -> RuleContext:
    arguments: dict[str, object] = {
        "values": {
            "employee_id": "E001",
            "work_order_id": "WO-1",
            "total_quantity": 10,
            "qualified_quantity": 8,
            "defective_quantity": 2,
        },
        "required_fields": frozenset({"employee_id", "work_order_id", "total_quantity"}),
        "ranges": {"total_quantity": (0, 99999)},
        "valid_employee_ids": frozenset({"E001"}),
        "valid_work_order_ids": frozenset({"WO-1"}),
        "is_duplicate_form": False,
        "expected_version": 1,
        "current_version": 1,
        "export_status": ExportStatus.NOT_EXPORTED,
        "required_export_fields": frozenset({"employee_id", "total_quantity"}),
        "export_mapping": {"employee_id": "员工", "total_quantity": "总产量"},
    }
    arguments.update(overrides)
    return RuleContext(**arguments)  # type: ignore[arg-type]


def test_valid_record_has_no_rule_failures() -> None:
    assert validate(valid_context()) == []


@pytest.mark.parametrize(
    ("context", "code", "field_id"),
    [
        (valid_context(values={}), "REQUIRED", "employee_id"),
        (
            valid_context(
                values={
                    "employee_id": "E001",
                    "work_order_id": "WO-1",
                    "total_quantity": 100000,
                }
            ),
            "OUT_OF_RANGE",
            "total_quantity",
        ),
        (
            valid_context(
                values={
                    "employee_id": "E001",
                    "work_order_id": "WO-1",
                    "total_quantity": 10,
                    "qualified_quantity": 9,
                    "defective_quantity": 2,
                }
            ),
            "QUANTITY_CLOSURE",
            "qualified_quantity",
        ),
        (valid_context(valid_employee_ids=frozenset({"E999"})), "INVALID_EMPLOYEE", "employee_id"),
        (
            valid_context(valid_work_order_ids=frozenset({"WO-9"})),
            "INVALID_WORK_ORDER",
            "work_order_id",
        ),
        (valid_context(is_duplicate_form=True), "DUPLICATE_FORM", "form_id"),
        (valid_context(expected_version=0), "STALE_VERSION", "current_version"),
        (
            valid_context(export_status=ExportStatus.REEXPORT_REQUIRED),
            "REEXPORT_REQUIRED",
            "export_status",
        ),
        (
            valid_context(export_mapping={"employee_id": "员工"}),
            "EXPORT_MAPPING_MISSING",
            "total_quantity",
        ),
    ],
)
def test_rule_failures_are_field_specific_and_machine_readable(
    context: RuleContext, code: str, field_id: str
) -> None:
    failures = validate(context)
    assert any(result.code == code and result.field_id == field_id for result in failures)
    assert all(result.severity and result.message for result in failures)
