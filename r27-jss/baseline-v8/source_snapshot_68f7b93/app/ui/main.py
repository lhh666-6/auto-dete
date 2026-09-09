"""Streamlit entry point."""

import streamlit as st

from app.services.container import Services, build_services
from app.ui.pages import (
    ai_vector,
    classification,
    exceptions,
    export_page,
    import_page,
    review,
    search,
)
from config.settings import Settings

st.set_page_config(page_title="工业级产量数据采集 Demo", layout="wide")
st.title("工业级产量数据采集 Demo")


@st.cache_resource
def services() -> Services:
    return build_services(Settings())


import_tab, classification_tab, review_tab, rules_tab, search_tab, ai_tab, export_tab = st.tabs(
    [
        "批量导入",
        "图像分类",
        "人工复核",
        "规则异常",
        "查询追溯",
        "AI 与相似检索",
        "XLSX 导出",
    ]
)
with import_tab:
    import_page.render(services().imports)
with classification_tab:
    classification.render(services().recognition)
with review_tab:
    review.render(services().reviews)
with rules_tab:
    exceptions.render()
with search_tab:
    search.render(services().queries)
with ai_tab:
    ai_vector.render(services().ai_reviews, services().vector_index)
with export_tab:
    export_page.render(services().exports, services().settings.exports_root)
