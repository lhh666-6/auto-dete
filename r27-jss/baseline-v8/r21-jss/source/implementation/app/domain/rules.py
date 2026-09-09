"""Pure deterministic validation rules; no database or AI calls."""

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from app.domain.models import ExportStatus


@dataclass(frozen=True, slots=True)
class RuleContext:
    values: Mapping[str, Any]
    required_fields: frozenset[str]
    ranges: Mapping[str, tuple[int | float, int | float]]
    valid_employee_ids: frozenset[str]
    valid_work_order_ids: frozenset[str]
    is_duplicate_form: bool
    expected_version: int
    current_version: int
    export_status: ExportStatus
    required_export_fields: frozenset[str]
    export_mapping: Mapping[str, str]


@dataclass(frozen=True, slots=True)
class RuleResult:
    code: str
    field_id: str
    severity: str
    message: str


def failure(code: str, field_id: str, message: str) -> RuleResult:
    return RuleResult(code=code, field_id=field_id, severity="ERROR", message=message)


def validate(context: RuleContext) -> list[RuleResult]:
    results: list[RuleResult] = []
    for field_id in sorted(context.required_fields):
        value = context.values.get(field_id)
        if value is None or (isinstance(value, str) and not value.strip()):
            results.append(failure("REQUIRED", field_id, "必填字段缺失"))

    for field_id, (minimum, maximum) in context.ranges.items():
        value = context.values.get(field_id)
        if value is not None and (
            not isinstance(value, int | float) or value < minimum or value > maximum
        ):
            results.append(
                failure("OUT_OF_RANGE", field_id, f"取值必须在 {minimum} 到 {maximum} 之间")
            )

    total = context.values.get("total_quantity")
    qualified = context.values.get("qualified_quantity")
    defective = context.values.get("defective_quantity", 0)
    if all(isinstance(value, int | float) for value in (total, qualified, defective)):
        if qualified + defective > total:
            results.append(
                failure(
                    "QUANTITY_CLOSURE", "qualified_quantity", "合格数与不良数之和不得超过总产量"
                )
            )

    employee_id = context.values.get("employee_id")
    if employee_id is not None and employee_id not in context.valid_employee_ids:
        results.append(failure("INVALID_EMPLOYEE", "employee_id", "员工编号不存在"))
    work_order_id = context.values.get("work_order_id")
    if work_order_id is not None and work_order_id not in context.valid_work_order_ids:
        results.append(failure("INVALID_WORK_ORDER", "work_order_id", "工单编号不存在"))
    if context.is_duplicate_form:
        results.append(failure("DUPLICATE_FORM", "form_id", "表单已存在"))
    if context.expected_version != context.current_version:
        results.append(failure("STALE_VERSION", "current_version", "记录版本已变化，请刷新后复核"))
    if context.export_status is ExportStatus.REEXPORT_REQUIRED:
        results.append(
            failure("REEXPORT_REQUIRED", "export_status", "已导出记录发生更正，必须重新导出")
        )
    for field_id in sorted(context.required_export_fields - context.export_mapping.keys()):
        results.append(failure("EXPORT_MAPPING_MISSING", field_id, "导出字段映射缺失"))
    return results
