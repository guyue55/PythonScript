"""入库管道模块。

负责加载原始文档、切分、向量化并写入向量索引。
遵循 Google Python Style Guide。
"""

from __future__ import annotations

import os
from typing import List

from ..config import AppConfig
from ..services.embeddings import EmbeddingsService
from ..services.vector_store import VectorStore
from ..utils.doc_loader import load_documents
from ..utils.logging import get_logger
from ..utils.text_splitter import split_texts

LOGGER = get_logger(__name__)


def run_ingest(source_dir: str, index_dir: str, cfg: AppConfig) -> None:
    """执行入库流程。

    Args:
        source_dir: 原始文档目录路径。
        index_dir: 索引存储目录路径。
        cfg: 应用配置对象。
    """
    os.makedirs(index_dir, exist_ok=True)

    # 1) 加载文档
    docs = load_documents(source_dir)
    if not docs:
        LOGGER.warning("未在目录中发现可用文档: %s", source_dir)
        return

    # 2) 切分文本
    chunks = split_texts(docs, chunk_size=cfg.chunk_size, chunk_overlap=cfg.chunk_overlap)
    contents: List[str] = [c["content"] for c in chunks]
    metas: List[dict] = [{"source": c["source"], "content": c["content"]} for c in chunks]
    LOGGER.info("切分得到文本块数量: %d", len(chunks))

    # 3) 生成嵌入
    embed_svc = EmbeddingsService(cfg.embedding_model)
    vectors = embed_svc.embed(contents)

    # 4) 写入索引
    store = VectorStore(dim=vectors.shape[1])
    store.add(vectors, metas)
    store.save(index_dir)
    LOGGER.info("入库完成，索引目录: %s", index_dir)