"""入库 CLI 脚本。

从命令行运行文档加载、切分、嵌入与索引构建流程。
遵循 Google Python Style Guide，提供清晰的参数帮助与日志输出。
"""

from __future__ import annotations

import argparse
import os
import sys

# 允许从脚本位置导入 app 包
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
sys.path.append(os.path.join(PROJECT_ROOT, "app"))

from app.config import load_config
from app.pipelines.ingest import run_ingest
from app.utils.logging import get_logger


logger = get_logger(__name__)


def parse_args() -> argparse.Namespace:
    """解析命令行参数。

    Returns:
        argparse.Namespace: 参数命名空间，包含 `source_dir` 与 `index_dir`。
    """

    parser = argparse.ArgumentParser(description="构建文档向量索引")
    parser.add_argument(
        "--source_dir",
        type=str,
        default=None,
        help="文档源目录（默认读取配置 RAW_DATA_DIR）",
    )
    parser.add_argument(
        "--index_dir",
        type=str,
        default=None,
        help="索引保存目录（默认读取配置 INDEX_DATA_DIR）",
    )
    return parser.parse_args()


def main() -> None:
    """脚本入口：执行入库流程。"""

    args = parse_args()
    cfg = load_config()
    run_ingest(cfg, source_dir=args.source_dir, index_dir=args.index_dir)
    logger.info("入库流程完成。")


if __name__ == "__main__":
    main()