"""日志工具模块。

提供统一的日志记录器，简化各模块的日志使用。
遵循 Google Python Style Guide。
"""

from __future__ import annotations

import logging
from typing import Optional


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """获取或创建日志记录器。

    Args:
        name: 日志记录器名称，默认为根记录器。

    Returns:
        logging.Logger: 配置好格式与级别的日志记录器。
    """
    logger = logging.getLogger(name if name else __name__)
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger