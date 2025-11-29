"""日志工具模块。

提供统一的日志记录器，便于在各模块中保持一致的格式与级别。
"""

import logging
from typing import Optional


def get_logger(name: Optional[str] = None, level: str = "INFO") -> logging.Logger:
    """获取或创建日志记录器。

    Args:
        name: 日志记录器名称；为 None 时返回根记录器。
        level: 日志级别字符串，例如 "INFO" 或 "DEBUG"。

    Returns:
        logging.Logger: 配置好的日志记录器实例。
    """

    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(getattr(logging, level.upper(), logging.INFO))
        handler = logging.StreamHandler()
        fmt = (
            "[%(asctime)s] %(levelname)s %(name)s - "
            "%(message)s"
        )
        handler.setFormatter(logging.Formatter(fmt))
        logger.addHandler(handler)
    return logger