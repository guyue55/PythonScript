"""文件加载器模块。

提供从目录中读取 `.txt`、`.md`、`.pdf` 文档并转换为
LangChain `Document` 的功能，统一后续切分与入库处理。
"""

from __future__ import annotations

import os
from typing import List

from langchain_core.documents import Document

try:
    from pypdf import PdfReader
except Exception:  # pragma: no cover - 在没有 PDF 依赖时允许运行
    PdfReader = None


def load_documents_from_dir(source_dir: str) -> List[Document]:
    """从指定目录加载文档。

    Args:
        source_dir: 目录路径，函数会遍历并读取受支持的文件类型。

    Returns:
        List[Document]: 转换后的文档对象列表，包含 `page_content` 与 `metadata`。

    Raises:
        FileNotFoundError: 当目录不存在时抛出。
    """

    if not os.path.isdir(source_dir):
        raise FileNotFoundError(f"目录不存在: {source_dir}")

    docs: List[Document] = []
    for root, _, files in os.walk(source_dir):
        for fname in files:
            fpath = os.path.join(root, fname)
            lower = fname.lower()
            if lower.endswith(".txt") or lower.endswith(".md"):
                try:
                    with open(fpath, "r", encoding="utf-8") as f:
                        content = f.read()
                    docs.append(
                        Document(page_content=content, metadata={"source": fpath})
                    )
                except UnicodeDecodeError:
                    # 回退为二进制读取并忽略错误字符
                    with open(fpath, "rb") as f:
                        raw = f.read().decode("utf-8", errors="ignore")
                    docs.append(
                        Document(page_content=raw, metadata={"source": fpath})
                    )
            elif lower.endswith(".pdf") and PdfReader:
                try:
                    reader = PdfReader(fpath)
                    text = "\n".join(page.extract_text() or "" for page in reader.pages)
                    docs.append(Document(page_content=text, metadata={"source": fpath}))
                except Exception:
                    # 避免 PDF 解析失败阻断流程
                    continue
            else:
                # 跳过不支持的类型
                continue

    return docs