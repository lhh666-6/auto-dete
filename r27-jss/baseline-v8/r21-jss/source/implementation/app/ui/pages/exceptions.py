"""Deterministic rule inspection page."""

import json

import streamlit as st

from app.domain.models import ExportStatus
from app.domain.rules import RuleContext, validate


def render() -> None:
    st.header("规则校验与异常")
    raw = st.text_area(
        "待校验字段（JSON 对象）",
        value=(
            '{"employee_id":"E001","work_order_id":"WO-1",'
            '"total_quantity":10,"qualified_quantity":8,"defective_quantity":2}'
        ),
    )
    if st.button("运行确定性规则"):
        try:
            values = json.loads(raw)
            if not isinstance(values, dict):
                raise ValueError("字段必须是 JSON 对象")
            context = RuleContext(
                values=values,
                required_fields=frozenset({"employee_id", "work_order_id", "total_quantity"}),
                ranges={"total_quantity": (0, 99999)},
                valid_employee_ids=frozenset({str(values.get("employee_id", ""))}),
                valid_work_order_ids=frozenset({str(values.get("work_order_id", ""))}),
                is_duplicate_form=False,
                expected_version=1,
                current_version=1,
                export_status=ExportStatus.NOT_EXPORTED,
                required_export_fields=frozenset({"employee_id", "total_quantity"}),
                export_mapping={"employee_id": "员工", "total_quantity": "总产量"},
            )
            results = validate(context)
            if results:
                st.dataframe(
                    [
                        {
                            "错误码": result.code,
                            "字段": result.field_id,
                            "级别": result.severity,
                            "说明": result.message,
                        }
                        for result in results
                    ]
                )
            else:
                st.success("确定性规则校验通过")
        except (json.JSONDecodeError, ValueError) as error:
            st.error(str(error))
