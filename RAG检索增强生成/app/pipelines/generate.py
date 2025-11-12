"""生成管道模块。

在检索结果基础上调用 LLM 生成最终回答。
遵循 Google Python Style Guide。
"""

from __future__ import annotations

from typing import List

from ..services.llm import LLMService


def run_generate(question: str, contexts: List[str], llm: LLMService) -> str:
    """执行基于检索的回答生成。

    Args:
        question: 用户查询文本。
        contexts: 相关上下文文本列表。
        llm: LLM 服务实例。

    Returns:
        str: 生成的回答文本。
    """
    return llm.generate(question, contexts)