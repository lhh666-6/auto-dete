"""Evidence image import page."""

import tempfile
from pathlib import Path

import streamlit as st

from app.application.import_forms import DuplicateEvidenceError, ImportForms


def render(imports: ImportForms) -> None:
    st.header("批量导入")
    st.caption("原始文件按 SHA-256 保存，重复文件和重复表单会被拒绝。")
    uploaded = st.file_uploader("选择表单图片", type=["png", "jpg", "jpeg", "tif", "tiff"])
    form_id = st.text_input("表单 ID")
    template_id = st.text_input("模板 ID", value="MANUAL")
    template_version = st.text_input("模板版本", value="1")
    actor_id = st.text_input("导入人员", value="operator")
    if st.button("导入图片", disabled=uploaded is None or not form_id.strip()):
        assert uploaded is not None
        temporary_path: Path | None = None
        try:
            with tempfile.NamedTemporaryFile(
                delete=False, suffix=Path(uploaded.name).suffix
            ) as temporary:
                temporary.write(uploaded.getbuffer())
                temporary_path = Path(temporary.name)
            evidence = imports.import_image(
                temporary_path,
                form_id.strip(),
                template_id.strip(),
                template_version.strip(),
                actor_id.strip(),
            )
            st.success(f"导入成功：{evidence.file_id}")
        except DuplicateEvidenceError as error:
            st.error(str(error))
        finally:
            if temporary_path is not None:
                temporary_path.unlink(missing_ok=True)
