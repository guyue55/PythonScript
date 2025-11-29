"""Web 搜索工具。

基于 duckduckgo-search 提供简易的网页搜索能力，便于智能体在需要时获取外部信息。
"""

from __future__ import annotations

from typing import List, Optional

from app.utils.logging import get_logger

logger = get_logger(__name__)

def _get_ddgs() -> Optional[object]:
    """惰性获取 DDGS 类（仅 `ddgs`）。失败返回 None。"""

    try:
        from ddgs import DDGS  # type: ignore
        return DDGS
    except Exception:  # pylint: disable=broad-except
        logger.warning("未找到 ddgs 模块，Web 搜索功能将不可用。")
        try:
            from duckduckgo_search import ddgs  # type: ignore
            return ddgs
        except Exception:  # pylint: disable=broad-except
            logger.warning("未找到 duckduckgo 模块，Web 搜索功能将不可用。")
        return None


def web_search(query: str, max_results: int = 5) -> List[str]:
    """使用 DuckDuckGo 进行网页搜索。

    Args:
        query: 搜索的查询字符串。
        max_results: 返回结果的最大条数。

    Returns:
        List[str]: 结果摘要列表（标题 + 链接），用于智能体决策或回答引用。
    """
    print(f"Web 搜索: {query}")

    results: List[str] = []
    DDGS = _get_ddgs()
    if DDGS is None:
        # 使用 httpx 进行轻量级 DuckDuckGo HTML 端点抓取作为降级
        logger.info(f"使用 httpx 进行轻量级 DuckDuckGo HTML 端点抓取作为降级: {query}")
        try:
            import httpx  # type: ignore
            resp = httpx.get("https://duckduckgo.com/html/", params={"q": query}, timeout=10)
            if resp.status_code == 200:
                html = resp.text
                import re
                # 简单提取结果链接与标题（非严格解析，足够展示）
                matches = re.findall(r'<a[^>]+class="result__a"[^>]*>(.*?)</a>', html)
                links = re.findall(r'<a[^>]+class="result__a"[^>]*href="([^"]+)"', html)
                for t, h in zip(matches, links):
                    # 去除 HTML 标签
                    title = re.sub(r"<[^>]+>", "", t)
                    results.append(f"{title} - {h}")
                return results[:max_results]
        except Exception:  # pylint: disable=broad-except
            logger.info("Web 搜索降级失败，返回空结果以不中断流程。")
        return results

    try:
        with DDGS() as ddgs:
            for item in ddgs.text(query, max_results=max_results):
                title = item.get("title", "")
                href = item.get("href", "")
                results.append(f"{title} - {href}")
    except Exception:  # pylint: disable=broad-except
        logger.warning("Web 搜索失败，返回空结果以不中断流程。")
    return results
