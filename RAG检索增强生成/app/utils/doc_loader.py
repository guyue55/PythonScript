"""文档加载工具模块。

支持从目录读取 .txt 与 .md 文档，返回文本列表与元数据。
遵循 Google Python Style Guide，函数包含详细注释。
"""

from __future__ import annotations

import os
from typing import Dict, List, Tuple

from .logging import get_logger

LOGGER = get_logger(__name__)


def load_documents(source_dir: str) -> List[Dict[str, str]]:
    """从指定目录加载文档。

    Args:
        source_dir: 文档所在目录路径。

    Returns:
        List[Dict[str, str]]: 文档列表，其中每项包含键 `path` 与 `text`。

    Raises:
        FileNotFoundError: 当目录不存在时抛出。
    """
    if not os.path.isdir(source_dir):
        raise FileNotFoundError(f"输入目录不存在: {source_dir}")

    docs: List[Dict[str, str]] = []
    for root, _dirs, files in os.walk(source_dir):
        for fname in files:
            if not (fname.lower().endswith(".txt") or fname.lower().endswith(".md")):
                continue
            fpath = os.path.join(root, fname)
            try:
                with open(fpath, "r", encoding="utf-8") as f:
                    text = f.read()
                docs.append({"path": fpath, "text": text})
            except UnicodeDecodeError:
                LOGGER.warning("跳过非UTF-8文件: %s", fpath)
    LOGGER.info("已加载文档数量: %d", len(docs))
    return docs