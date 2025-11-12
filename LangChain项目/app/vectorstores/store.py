"""向量库封装模块。

提供构建与加载向量索引的统一接口，支持 FAISS 与 Chroma。
"""

from __future__ import annotations

import os
from typing import List

from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings

try:
    from langchain_community.vectorstores import FAISS
except Exception:  # pragma: no cover - 允许无 FAISS 环境运行
    FAISS = None

try:
    from langchain_community.vectorstores import Chroma
except Exception:  # pragma: no cover - 允许无 Chroma 环境运行
    Chroma = None


class VectorStoreManager:
    """向量库管理器。

    统一创建与加载语义检索器，隐藏具体后端差异。
    """

    @staticmethod
    def build_index(
        documents: List[Document], embeddings: Embeddings, backend: str, index_dir: str
    ) -> None:
        """构建并保存向量索引。

        Args:
            documents: 文档列表。
            embeddings: 嵌入模型实例，实现 `Embeddings` 接口。
            backend: 向量库后端标识（"faiss" 或 "chroma"）。
            index_dir: 索引目录路径。
        """

        os.makedirs(index_dir, exist_ok=True)
        if backend.lower() == "faiss":
            if FAISS is None:
                raise RuntimeError("FAISS 不可用，请安装 faiss-cpu 或使用 chroma")
            vs = FAISS.from_documents(documents, embeddings)
            vs.save_local(index_dir)
        elif backend.lower() == "chroma":
            if Chroma is None:
                raise RuntimeError("Chroma 不可用，请安装 chromadb 或使用 faiss")
            # Chroma 使用持久化目录创建索引
            Chroma.from_documents(documents, embeddings, persist_directory=index_dir)
        else:
            raise ValueError("不支持的向量库后端：" + backend)

    @staticmethod
    def load_retriever(embeddings: Embeddings, backend: str, index_dir: str):
        """加载检索器接口。

        Args:
            embeddings: 嵌入模型实例。
            backend: 向量库后端标识（"faiss" 或 "chroma"）。
            index_dir: 索引目录路径。

        Returns:
            BaseRetriever: LangChain 检索器对象，具有 `get_relevant_documents` 等方法。
        """

        if backend.lower() == "faiss":
            if FAISS is None:
                raise RuntimeError("FAISS 不可用，请安装 faiss-cpu 或使用 chroma")
            vs = FAISS.load_local(
                index_dir,
                embeddings,
                allow_dangerous_deserialization=True,
            )
            return vs.as_retriever()
        elif backend.lower() == "chroma":
            if Chroma is None:
                raise RuntimeError("Chroma 不可用，请安装 chromadb 或使用 faiss")
            vs = Chroma(embedding_function=embeddings, persist_directory=index_dir)
            return vs.as_retriever()
        else:
            raise ValueError("不支持的向量库后端：" + backend)