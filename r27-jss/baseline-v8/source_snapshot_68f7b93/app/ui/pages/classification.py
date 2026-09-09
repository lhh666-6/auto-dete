"""Image quality, QR classification, and manual reclassification page."""

from typing import cast

import cv2
import numpy as np
import streamlit as st
from numpy.typing import NDArray

from app.application.recognize_forms import RecognizeForms


class InvalidImageError(ValueError):
    pass


def decode_image(content: bytes) -> NDArray[np.uint8]:
    image = cv2.imdecode(np.frombuffer(content, dtype=np.uint8), cv2.IMREAD_COLOR)
    if image is None:
        raise InvalidImageError("文件不是可读取的图片")
    return cast(NDArray[np.uint8], image)


def render(recognition: RecognizeForms) -> None:
    st.header("图像质量与模板分类")
    form_id = st.text_input("分类表单 ID")
    uploaded = st.file_uploader(
        "选择已导入表单的图片副本",
        type=["png", "jpg", "jpeg", "tif", "tiff"],
        key="classification-image",
    )
    actor_id = st.text_input("分类人员", value="classifier")
    if st.button("检测质量并读取二维码", disabled=uploaded is None or not form_id.strip()):
        assert uploaded is not None
        try:
            image = decode_image(uploaded.getvalue())
            st.image(image, channels="BGR", caption="待分类图片")
            quality = recognition.assess_quality(image)
            if quality.acceptable:
                st.success("图像质量检查通过")
            else:
                st.error(f"需要重新采集：{', '.join(quality.reason_codes)}")
            result = recognition.classify_image(form_id.strip(), image)
            if result.template_reference:
                st.success(f"二维码模板：{result.template_reference}")
            else:
                st.warning("未读取到二维码，已进入人工分类队列")
        except (InvalidImageError, KeyError, ValueError) as error:
            st.error(str(error))

    st.subheader("人工重新分类")
    manual_form_id = st.text_input("人工分类表单 ID")
    template_id = st.text_input("目标模板 ID")
    template_version = st.text_input("目标模板版本", value="1")
    reason = st.text_input("重新分类原因", value="二维码损坏")
    if st.button(
        "保存人工分类",
        disabled=not manual_form_id.strip() or not template_id.strip(),
    ):
        try:
            recognition.manual_reclassify(
                manual_form_id.strip(),
                template_id.strip(),
                template_version.strip(),
                actor_id.strip(),
                reason.strip(),
            )
            st.success("已保存人工分类并生成审计事件")
        except (KeyError, ValueError) as error:
            st.error(str(error))
