"""入库 CLI 脚本。

从指定目录加载文档，进行切分与嵌入，并构建向量索引。
遵循 Google Python Style Guide，提供清晰的参数说明。
"""

from __future__ import annotations

import argparse
import sys

from app.config import load_config
from app.pipelines.ingest import run_ingest


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """解析命令行参数。

    Args:
        argv: 命令行参数列表，通常为 None 以使用 sys.argv。

    Returns:
        argparse.Namespace: 解析后的参数对象。
    """
    parser = argparse.ArgumentParser(description="RAG 入库：加载、切分、嵌入并构建索引")
    parser.add_argument(
        "--source_dir",
        type=str,
        default=None,
        help="原始文档目录，若不指定则使用配置中的 RAW_DIR",
    )
    parser.add_argument(
        "--index_dir",
        type=str,
        default=None,
        help="索引输出目录，若不指定则使用配置中的 INDEX_DIR",
    )
    return parser.parse_args(argv)


def main() -> None:
    """程序入口。"""
    cfg = load_config()
    args = parse_args()
    source_dir = args.source_dir or cfg.raw_dir
    index_dir = args.index_dir or cfg.index_dir
    run_ingest(source_dir=source_dir, index_dir=index_dir, cfg=cfg)


if __name__ == "__main__":
    main()