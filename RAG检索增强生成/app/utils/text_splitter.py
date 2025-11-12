"""文本切分工具模块。

提供简单的按字符长度切分，支持重叠以提高召回有效性。
遵循 Google Python Style Guide。
"""

from __future__ import annotations

from typing import Dict, List


def split_texts(
    docs: List[Dict[str, str]],
    chunk_size: int = 800,
    chunk_overlap: int = 120,
) -> List[Dict[str, str]]:
    """将文档文本切分为块。

    Args:
        docs: 文档列表，每项包含 `path` 和 `text`。
        chunk_size: 每个文本块的最大字符长度。
        chunk_overlap: 相邻文本块之间的重叠字符数。

    Returns:
        List[Dict[str, str]]: 切分后的文本块列表，包含 `source` 与 `content`。

    Raises:
        ValueError: 当 `chunk_size` 或 `chunk_overlap` 非法时抛出。
    """
    if chunk_size <= 0 or chunk_overlap < 0:
        raise ValueError("chunk_size 必须 > 0，且 chunk_overlap >= 0")
    if chunk_overlap >= chunk_size:
        raise ValueError("chunk_overlap 必须小于 chunk_size")

    chunks: List[Dict[str, str]] = []
    for doc in docs:
        text = doc.get("text", "")
        source = doc.get("path", "")
        start = 0
        end = chunk_size
        while start < len(text):
            chunk = text[start:end]
            if chunk.strip():
                chunks.append({"source": source, "content": chunk})
            start = end - chunk_overlap
            end = start + chunk_size
    return chunks