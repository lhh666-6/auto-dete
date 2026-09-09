"""Manual review page components."""

import json
from collections.abc import Mapping
from typing import Any

import streamlit as st

from app.application.review_forms import ConcurrentReviewError, ReviewForms


class ReviewValuesError(ValueError):
    pass


def parse_review_values(raw: str) -> dict[str, Any]:
    try:
        values = json.loads(raw)
    except json.JSONDecodeError as error:
        raise ReviewValuesError("字段值必须是有效 JSON") from error
    if not isinstance(values, dict):
        raise ReviewValuesError("字段值必须是 JSON 对象")
    return values


def build_selection(
    reviews: ReviewForms,
    form_id: str,
    expected_version: int,
    values: Mapping[str, Any],
    chosen_by_field: Mapping[str, str | None],
    manual_evidence_id: str | None,
) -> tuple[dict[str, str | None], dict[str, str]]:
    """Resolve reviewer choices to contract mappings; ids only.

    chosen_by_field maps each field to a persisted certificate id (machine
    path, loaded from the database) or None (manual-entry path). Manual
    fields share one evidence id entered by the reviewer; machine fields
    need no evidence input. Callers never construct certificate payloads —
    only ids are passed to confirm().
    """
    certificate_ids_by_field: dict[str, str | None] = {}
    manual_evidence_ids_by_field: dict[str, str] = {}
    for field_key in values:
        choice = chosen_by_field.get(field_key)
        if choice:
            certificate_ids_by_field[field_key] = choice
        else:
            if not manual_evidence_id:
                raise ReviewValuesError("人工录入字段需要至少一个证据 ID")
            certificate_ids_by_field[field_key] = None
            manual_evidence_ids_by_field[field_key] = manual_evidence_id
    return certificate_ids_by_field, manual_evidence_ids_by_field


def _certificate_label(certificate: Any) -> str:
    return (
        f"{certificate.producer_id}/{certificate.producer_version} "
        f"#{certificate.certificate_id[:8]} 值={certificate.value} "
        f"状态={certificate.selection_state.value}"
    )


def render(reviews: ReviewForms) -> None:
    st.header("人工复核")
    st.caption("OCR/AI 可关闭；页面提交会生成不可变版本和审计事件。")
    form_id = st.text_input("待复核表单 ID")
    expected_version = st.number_input("当前版本", min_value=0, step=1)
    raw_values = st.text_area(
        "确认字段（JSON 对象）",
        value='{"employee_id": "", "total_quantity": 0, "qualified_quantity": 0}',
    )
    values: dict[str, Any] = {}
    try:
        values = parse_review_values(raw_values)
    except ReviewValuesError as error:
        st.warning(str(error))

    # One source choice per field: a persisted machine certificate (loaded
    # from the database by form, field, and expected version) or the manual
    # entry path. Only ids are passed to confirm().
    chosen_by_field: dict[str, str | None] = {}
    if form_id.strip():
        for field_key in values:
            eligible = reviews.eligible_certificates(
                form_id.strip(), int(expected_version), field_key
            )
            options: dict[str, str | None] = {"人工录入（无机器证书）": None}
            for certificate in eligible:
                options[_certificate_label(certificate)] = certificate.certificate_id
            labels = list(options)
            default_label = labels[0]
            if eligible:
                default_label = _certificate_label(eligible[0])
            choice = st.selectbox(
                f"字段 {field_key} 来源",
                labels,
                index=labels.index(default_label),
            )
            chosen_by_field[field_key] = options[choice]
    actor_id = st.text_input("复核人员", value="reviewer")
    reason = st.text_input("确认/更正原因", value="manual confirmation")
    evidence_ids = st.text_input("人工录入证据 ID（逗号分隔，首个用于所有人工字段）")
    if st.button("确认并生成新版本", disabled=not form_id.strip()):
        try:
            resolved = tuple(
                value.strip() for value in evidence_ids.split(",") if value.strip()
            )
            certificate_ids_by_field, manual_evidence_ids_by_field = build_selection(
                reviews,
                form_id.strip(),
                int(expected_version),
                values,
                chosen_by_field,
                resolved[0] if resolved else None,
            )
            record = reviews.confirm(
                form_id.strip(),
                int(expected_version),
                values,
                actor_id.strip(),
                reason.strip(),
                certificate_ids_by_field=certificate_ids_by_field,
                manual_evidence_ids_by_field=manual_evidence_ids_by_field,
            )
            st.success(f"已生成版本 {record.version}：{record.record_id}")
        except (ReviewValuesError, ConcurrentReviewError, KeyError, ValueError) as error:
            st.error(str(error))
