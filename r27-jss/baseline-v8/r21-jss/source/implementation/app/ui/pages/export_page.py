"""Traceable XLSX export page."""

from pathlib import Path

import streamlit as st

from app.application.export_forms import ExportForms
from app.application.query_forms import FormFilters


def render(exports: ExportForms, output_directory: Path) -> None:
    st.header("XLSX 导出")
    export_type = st.selectbox("导出用途", ["PAYROLL", "OUTPUT", "QUALITY", "WORK_ORDER"])
    employee_id = st.text_input("仅导出员工 ID（可空）")
    actor_id = st.text_input("导出人员", value="finance")
    if st.button("生成 XLSX"):
        batch = exports.export(
            export_type,
            FormFilters(employee_id=employee_id.strip() or None),
            output_directory,
            actor_id.strip(),
        )
        st.success(f"导出批次：{batch.export_batch_id}")
        st.download_button(
            "下载 XLSX",
            data=Path(batch.file_path).read_bytes(),
            file_name=Path(batch.file_path).name,
        )
