"""Web 搜索工具。

基于 duckduckgo-search 提供简易的网页搜索能力，便于智能体在需要时获取外部信息。
"""

from __future__ import annotations

from typing import List

from duckduckgo_search import DDGS
from app.utils.logging import get_logger


logger = get_logger(__name__)


def web_search(query: str, max_results: int = 5) -> List[str]:
    """使用 DuckDuckGo 进行网页搜索。

    Args:
        query: 搜索的查询字符串。
        max_results: 返回结果的最大条数。

    Returns:
        List[str]: 结果摘要列表（标题 + 链接），用于智能体决策或回答引用。
    """

    results: List[str] = []
    try:
        with DDGS() as ddgs:
            for item in ddgs.text(query, max_results=max_results):
                title = item.get("title", "")
                href = item.get("href", "")
                results.append(f"{title} - {href}")
    except Exception:
        logger.info("Web 搜索失败，返回空结果以不中断流程。")
    return results
