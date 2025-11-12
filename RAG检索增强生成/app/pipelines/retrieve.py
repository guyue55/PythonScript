"""检索管道模块。

将查询嵌入并在向量库中进行检索，返回最相关的文本块内容。
遵循 Google Python Style Guide。
"""

from __future__ import annotations

from typing import List

from ..services.embeddings import EmbeddingsService
from ..services.vector_store import VectorStore


def run_retrieve(
    query: str,
    index_dir: str,
    embed_svc: EmbeddingsService,
    top_k: int = 5,
) -> List[str]:
    """执行查询检索。

    Args:
        query: 用户查询文本。
        index_dir: 索引存储目录路径。
        embed_svc: 嵌入服务实例，用于将查询转换为向量。
        top_k: 返回的最相似项数量。

    Returns:
        List[str]: 检索到的上下文文本内容列表。
    """
    qvec = embed_svc.embed([query])
    store = VectorStore(dim=qvec.shape[1])
    store.load(index_dir)
    results = store.search(qvec, top_k=top_k)
    contexts: List[str] = []
    for _score, meta in results:
        content = meta.get("content")
        if content:
            contexts.append(content)
        else:
            contexts.append(f"来源: {meta.get('source', '')}")
    return contexts