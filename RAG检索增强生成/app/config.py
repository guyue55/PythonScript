"""应用配置模块。

提供统一的配置加载，支持从环境变量与 .env 文件读取。
遵循 Google Python Style Guide，所有配置字段提供类型注释。
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional

from dotenv import load_dotenv


@dataclass
class AppConfig:
    """应用配置对象。

    该配置对象汇总 RAG 管道所需的参数，包括数据路径、文本切分、模型与检索配置。

    Attributes:
        index_dir: 向量索引存储目录路径。
        raw_dir: 原始文档目录路径。
        processed_dir: 处理后的文档目录路径。
        chunk_size: 文本切分的块大小（字符数）。
        chunk_overlap: 文本块之间的重叠大小（字符数）。
        embedding_model: Sentence-Transformers 模型名称。
        llm_provider: LLM 提供方标识（如 "openai" 或 "none"）。
        llm_model: 具体的 LLM 模型名称（可选）。
        openai_api_key: OpenAI API 密钥（可选）。
    """

    index_dir: str = "data/index"
    raw_dir: str = "data/raw"
    processed_dir: str = "data/processed"

    chunk_size: int = 800
    chunk_overlap: int = 120

    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    llm_provider: str = "none"
    llm_model: Optional[str] = None
    openai_api_key: Optional[str] = None


def load_config() -> AppConfig:
    """加载应用配置。

    Returns:
        AppConfig: 解析自环境变量的配置对象，包含默认值回退。
    """
    load_dotenv()

    cfg = AppConfig(
        index_dir=os.getenv("INDEX_DIR", AppConfig.index_dir),
        raw_dir=os.getenv("RAW_DIR", AppConfig.raw_dir),
        processed_dir=os.getenv("PROCESSED_DIR", AppConfig.processed_dir),
        chunk_size=int(os.getenv("CHUNK_SIZE", AppConfig.chunk_size)),
        chunk_overlap=int(os.getenv("CHUNK_OVERLAP", AppConfig.chunk_overlap)),
        embedding_model=os.getenv("EMBEDDING_MODEL", AppConfig.embedding_model),
        llm_provider=os.getenv("LLM_PROVIDER", AppConfig.llm_provider),
        llm_model=os.getenv("LLM_MODEL", "gpt-4o-mini"),
        openai_api_key=os.getenv("OPENAI_API_KEY"),
    )
    return cfg