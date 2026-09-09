"""Pure admission-shape rules shared by service and trusted adapter."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from app.domain.authority import canonical_values_equal


class AdmissionShapeError(ValueError):
    def __init__(self, code: str, message: str) -> None:
        self.code = code
        super().__init__(message)


@dataclass(frozen=True, slots=True)
class AdmissionPlan:
    complete_values: dict[str, Any]
    admission_fields: frozenset[str]
    initial_certificate_snapshot: bool


def derive_admission_plan(
    *,
    declared_fields: frozenset[str],
    previous_values: Mapping[str, Any],
    previous_fact_sources: Mapping[str, str],
    proposed_values: Mapping[str, Any],
) -> AdmissionPlan:
    """Derive the exact initial domain or later changed-field set."""

    if not declared_fields:
        raise AdmissionShapeError(
            "EMPTY_DECLARED_FIELD_SET", "declared authoritative field set is empty"
        )
    proposed_domain = frozenset(proposed_values)
    if not proposed_domain <= declared_fields:
        raise AdmissionShapeError(
            "DECLARED_FIELD_DOMAIN_MISMATCH",
            "proposed snapshot contains a field outside the declared field domain",
        )

    initial = not previous_fact_sources
    if initial:
        if proposed_domain != declared_fields:
            raise AdmissionShapeError(
                "INITIAL_FIELD_SET_MISMATCH",
                "initial certificate-era snapshot must cover every declared field",
            )
        return AdmissionPlan(
            complete_values=dict(proposed_values),
            admission_fields=declared_fields,
            initial_certificate_snapshot=True,
        )

    if frozenset(previous_values) != declared_fields:
        raise AdmissionShapeError(
            "PERSISTED_FIELD_DOMAIN_MISMATCH",
            "previous snapshot does not equal the declared field domain",
        )
    if frozenset(previous_fact_sources) != declared_fields:
        raise AdmissionShapeError(
            "PERSISTED_SOURCE_DOMAIN_MISMATCH",
            "previous source map does not equal the declared field domain",
        )
    complete_values = dict(previous_values)
    complete_values.update(proposed_values)
    changed = frozenset(
        field
        for field in declared_fields
        if not canonical_values_equal(complete_values[field], previous_values[field])
    )
    if not changed:
        raise AdmissionShapeError(
            "NO_CHANGED_FIELDS", "post-initial admission must change at least one field"
        )
    return AdmissionPlan(
        complete_values=complete_values,
        admission_fields=changed,
        initial_certificate_snapshot=False,
    )
