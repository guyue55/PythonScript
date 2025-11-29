"""应用配置模块。

提供 `AppConfig` 与 `load_config`，统一管理智能体所需的环境参数。
遵循 Google Python Style Guide，包含详尽文档字符串与类型注释。
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
        llm_provider: LLM 提供商标识，例如 "openai" 或 "moonshot"。
        llm_model: LLM 模型名称字符串（如 "gpt-4o-mini" 或 "kimi-latest"）。
        llm_api_key: 通用 LLM API Key（优先使用）。
        llm_base_url: 可选 LLM 基础 URL，用于 Moonshot 等自定义基地地址。
        search_max_results: Web 搜索返回的最大结果数。
        memory_max_messages: 对话记忆保存的最大消息条数。
        memory_file: 对话记忆持久化文件路径。
        log_level: 日志级别，例如 "INFO" 或 "DEBUG"。
    """

    llm_provider: str
    llm_model: str
    llm_api_key: Optional[str]
    llm_base_url: Optional[str]
    search_max_results: int
    memory_max_messages: int
    memory_file: str
    log_level: str


def load_config(env_path: Optional[str] = None) -> AppConfig:
    """从环境变量或 .env 文件加载应用配置。

    Args:
        env_path: 可选 `.env` 文件路径；为 None 时使用默认搜索。

    Returns:
        AppConfig: 已填充默认值并从环境覆盖的配置对象。

    Raises:
        ValueError: 当数值参数非法或关键路径为空时抛出。
    """

    if env_path:
        load_dotenv(dotenv_path=env_path, override=True)
    else:
        load_dotenv(override=True)

    llm_provider = os.getenv("LLM_PROVIDER", "openai")
    llm_model = os.getenv("LLM_MODEL", "gpt-4o-mini")
    llm_api_key = os.getenv("LLM_API_KEY")
    llm_base_url = os.getenv("LLM_BASE_URL")
    search_max_results = int(os.getenv("SEARCH_MAX_RESULTS", "5"))
    memory_max_messages = int(os.getenv("MEMORY_MAX_MESSAGES", "50"))
    memory_file = os.getenv("MEMORY_FILE", "智能体项目/storage/memory.json")
    log_level = os.getenv("LOG_LEVEL", "INFO")

    if search_max_results <= 0:
        raise ValueError("SEARCH_MAX_RESULTS 必须为正整数。")
    if memory_max_messages <= 0:
        raise ValueError("MEMORY_MAX_MESSAGES 必须为正整数。")
    if not memory_file:
        raise ValueError("MEMORY_FILE 不能为空。")

    return AppConfig(
        llm_provider=llm_provider,
        llm_model=llm_model,
        llm_api_key=llm_api_key,
        llm_base_url=llm_base_url,
        search_max_results=search_max_results,
        memory_max_messages=memory_max_messages,
        memory_file=memory_file,
        log_level=log_level,
    )
