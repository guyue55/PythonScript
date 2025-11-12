"""入库（索引构建）管道。

实现文档加载、文本切分、嵌入生成与向量库索引的持久化保存。
"""

from __future__ import annotations

from typing import List

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_openai import OpenAIEmbeddings
from langchain_community.embeddings import HuggingFaceEmbeddings

from app.config import AppConfig
from app.loaders.file_loader import load_documents_from_dir
from app.utils.logging import get_logger
from app.vectorstores.store import VectorStoreManager


logger = get_logger(__name__)


def _get_embeddings(cfg: AppConfig) -> Embeddings:
    """根据配置创建嵌入模型。

    Args:
        cfg: 应用配置对象。

    Returns:
        Embeddings: 嵌入模型实例。
    """

    if cfg.embeddings_provider.lower() == "openai":
        if not cfg.openai_api_key:
            raise ValueError("使用 OpenAI 嵌入需要 OPENAI_API_KEY。")
        return OpenAIEmbeddings(model=cfg.embeddings_model, api_key=cfg.openai_api_key)
    # 默认使用 HuggingFace 本地模型
    return HuggingFaceEmbeddings(model_name=cfg.embeddings_model)


def run_ingest(cfg: AppConfig, source_dir: str | None = None, index_dir: str | None = None) -> None:
    """执行入库流程：加载、切分、嵌入并保存索引。

    Args:
        cfg: 应用配置对象。
        source_dir: 可选的源目录，未提供时使用配置中的 `raw_data_dir`。
        index_dir: 可选的索引目录，未提供时使用配置中的 `index_data_dir`。
    """

    src = source_dir or cfg.raw_data_dir
    dst = index_dir or cfg.index_data_dir
    docs = load_documents_from_dir(src)
    logger.info("加载文档数: %d", len(docs))

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=cfg.chunk_size, chunk_overlap=cfg.chunk_overlap
    )
    chunks: List[Document] = splitter.split_documents(docs)
    logger.info("切分后的文档块数: %d", len(chunks))

    embeddings = _get_embeddings(cfg)
    VectorStoreManager.build_index(chunks, embeddings, cfg.vectorstore, dst)
    logger.info("索引已保存到: %s", dst)