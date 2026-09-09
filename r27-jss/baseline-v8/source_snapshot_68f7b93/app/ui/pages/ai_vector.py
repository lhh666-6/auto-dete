"""Safe AI review and optional similarity search page."""

import json
from typing import Any
from uuid import uuid4

import streamlit as st

from app.adapters.vector.local import LocalVectorIndex, VectorDocument
from app.application.ai_review_forms import AIReviewForms


class ContextError(ValueError):
    pass


def parse_context(raw: str) -> dict[str, Any]:
    try:
        context = json.loads(raw)
    except json.JSONDecodeError as error:
        raise ContextError("上下文必须是有效 JSON") from error
    if not isinstance(context, dict):
        raise ContextError("上下文必须是 JSON 对象")
    return context


def render(ai_reviews: AIReviewForms, vector_index: LocalVectorIndex) -> None:
    st.header("AI 辅助与相似检索")
    st.caption("AI 默认关闭；建议独立保存且必须人工确认。相似结果不修改业务事实。")
    form_id = st.text_input("AI 审查表单 ID")
    context_text = st.text_area("脱敏审查上下文（JSON）", value="{}")
    actor_id = st.text_input("审查人员", value="reviewer", key="ai-reviewer")
    if st.button("运行 AI 审查", disabled=not form_id.strip()):
        try:
            review = ai_reviews.run(form_id.strip(), parse_context(context_text), actor_id.strip())
            st.json(review.model_dump(mode="json"))
        except (ContextError, KeyError, ValueError) as error:
            st.error(str(error))

    st.subheader("本地相似异常检索")
    document_form_id = st.text_input("索引表单 ID")
    document_content = st.text_area("异常摘要")
    if st.button(
        "加入本地索引", disabled=not document_form_id.strip() or not document_content.strip()
    ):
        vector_index.add(
            VectorDocument(
                vector_id=f"VECTOR-{uuid4().hex}",
                form_id=document_form_id.strip(),
                content_type="EXCEPTION",
                content=document_content.strip(),
            )
        )
        st.success("已加入本地相似检索索引")
    query = st.text_input("相似异常查询")
    if st.button("检索相似记录", disabled=not query.strip()):
        st.dataframe(
            [
                {
                    "form_id": match.document.form_id,
                    "content": match.document.content,
                    "score": match.score,
                }
                for match in vector_index.search(query.strip())
            ]
        )
