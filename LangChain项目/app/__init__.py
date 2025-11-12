"""LangChain 应用包初始化。

此包包含配置、加载器、向量库、LLM 服务与管道模块，
用于实现标准的检索增强生成（RAG）工作流。
"""

from .config import AppConfig, load_config

__all__ = ["AppConfig", "load_config"]