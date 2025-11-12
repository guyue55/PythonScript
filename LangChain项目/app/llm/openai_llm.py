"""OpenAI LLM 服务模块。

提供基于 `langchain-openai` 的 Chat LLM 初始化封装。
"""

from __future__ import annotations

from typing import Optional

from langchain_openai import ChatOpenAI


def get_chat_llm(model: str, api_key: Optional[str]) -> ChatOpenAI:
    """创建 ChatOpenAI 模型实例。

    Args:
        model: OpenAI 对话模型名称（例如 `gpt-4o-mini`）。
        api_key: OpenAI API Key。

    Returns:
        ChatOpenAI: 已初始化的 ChatOpenAI 模型实例。

    Raises:
        ValueError: 当未提供 API Key 时抛出。
    """

    if not api_key:
        raise ValueError("未提供 OPENAI_API_KEY，无法初始化 OpenAI LLM。")
    return ChatOpenAI(model=model, api_key=api_key, temperature=0.2)