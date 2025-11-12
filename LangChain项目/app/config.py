"""应用配置模块。

提供 `AppConfig` 数据类与 `load_config` 函数用于统一管理项目配置，
包括数据路径、文本切分参数、模型选择与向量库后端。

遵循 Google Python Style Guide，包含详细文档字符串与类型注释。
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional

from dotenv import load_dotenv


@dataclass
class AppConfig:
    """应用配置数据类。

    Attributes:
        raw_data_dir: 原始文档目录路径。
        index_data_dir: 索引目录路径，用于保存向量库索引。
        chunk_size: 文本切分块大小（字符数）。
        chunk_overlap: 文本切分重叠大小（字符数）。
        llm_provider: LLM 提供商标识，例如 "openai" 或 "none"。
        llm_model: LLM 模型名称。
        openai_api_key: OpenAI API Key（若使用 OpenAI）。
        embeddings_provider: 嵌入模型提供商（如 "huggingface"、"openai"）。
        embeddings_model: 嵌入模型标识或名称。
        vectorstore: 向量库后端选择（"faiss" 或 "chroma"）。
    """

    raw_data_dir: str
    index_data_dir: str
    chunk_size: int
    chunk_overlap: int
    llm_provider: str
    llm_model: str
    openai_api_key: Optional[str]
    embeddings_provider: str
    embeddings_model: str
    vectorstore: str


def load_config(env_path: Optional[str] = None) -> AppConfig:
    """从环境变量或 .env 文件加载应用配置。

    Args:
        env_path: 可选的 `.env` 文件路径；若为 None 则使用默认搜索路径。

    Returns:
        AppConfig: 已填充默认值并从环境覆盖的配置对象。

    Raises:
        ValueError: 当切分参数非法或关键路径为空时抛出。
    """

    if env_path:
        load_dotenv(dotenv_path=env_path, override=True)
    else:
        load_dotenv(override=True)

    raw_data_dir = os.getenv("RAW_DATA_DIR", "LangChain项目/data/raw")
    index_data_dir = os.getenv("INDEX_DATA_DIR", "LangChain项目/data/index")
    chunk_size = int(os.getenv("CHUNK_SIZE", "800"))
    chunk_overlap = int(os.getenv("CHUNK_OVERLAP", "120"))
    llm_provider = os.getenv("LLM_PROVIDER", "openai")
    llm_model = os.getenv("LLM_MODEL", "gpt-4o-mini")
    openai_api_key = os.getenv("OPENAI_API_KEY")
    embeddings_provider = os.getenv("EMBEDDINGS_PROVIDER", "huggingface")
    embeddings_model = os.getenv("EMBEDDINGS_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
    vectorstore = os.getenv("VECTORSTORE", "faiss")

    if chunk_size <= 0:
        raise ValueError("CHUNK_SIZE 必须为正整数。")
    if chunk_overlap < 0:
        raise ValueError("CHUNK_OVERLAP 不能为负数。")
    if not raw_data_dir or not index_data_dir:
        raise ValueError("RAW_DATA_DIR 与 INDEX_DATA_DIR 不能为空。")

    return AppConfig(
        raw_data_dir=raw_data_dir,
        index_data_dir=index_data_dir,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        llm_provider=llm_provider,
        llm_model=llm_model,
        openai_api_key=openai_api_key,
        embeddings_provider=embeddings_provider,
        embeddings_model=embeddings_model,
        vectorstore=vectorstore,
    )