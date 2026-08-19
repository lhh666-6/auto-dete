from app.adapters.vector.local import LocalVectorIndex, VectorDocument


def test_local_similarity_search_returns_references_without_mutating_documents() -> None:
    index = LocalVectorIndex()
    first = VectorDocument("V1", "FORM-1", "EXCEPTION", "数量闭合失败 不良数异常")
    second = VectorDocument("V2", "FORM-2", "EXCEPTION", "二维码损坏 需要人工分类")
    index.add(first)
    index.add(second)

    matches = index.search("数量 不良 异常", limit=1)

    assert matches[0].document.vector_id == "V1"
    assert matches[0].score > 0
    assert first.content == "数量闭合失败 不良数异常"
