"""Exact search and evidence trace page."""

from dataclasses import asdict

import streamlit as st

from app.application.query_forms import FormFilters, QueryForms


def render(queries: QueryForms) -> None:
    st.header("精确查询与追溯")
    form_id = st.text_input("查询表单 ID")
    employee_id = st.text_input("员工 ID")
    work_order_id = st.text_input("工单 ID")
    if st.button("精确查询"):
        results = queries.search(
            FormFilters(
                form_id=form_id.strip() or None,
                employee_id=employee_id.strip() or None,
                work_order_id=work_order_id.strip() or None,
            )
        )
        st.dataframe(
            [
                {
                    "form_id": result.form.form_id,
                    "version": result.current_record.version,
                    **result.current_record.values,
                }
                for result in results
            ],
            use_container_width=True,
        )
    trace_id = st.text_input("追溯表单 ID")
    if st.button("查看完整证据链", disabled=not trace_id.strip()):
        try:
            trace = queries.trace(trace_id.strip())
            st.json(
                {
                    "form": asdict(trace.form),
                    "versions": [asdict(item) for item in trace.versions],
                    "evidence": [asdict(item) for item in trace.evidence],
                    "audits": [asdict(item) for item in trace.audits],
                    "recognition_attempts": [asdict(item) for item in trace.attempts],
                }
            )
        except KeyError as error:
            st.error(str(error))
