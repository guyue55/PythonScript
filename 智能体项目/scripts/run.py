"""智能体运行 CLI 脚本。

支持从命令行输入任务，执行工具步骤与 LLM 生成，并打印结果与工具日志。
遵循 Google Python Style Guide，提供清晰的参数与错误处理。
"""

from __future__ import annotations

import argparse
import os
import sys

# 允许从脚本位置导入 app 包
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
# 确保可以通过 `import app.*` 方式导入
sys.path.append(PROJECT_ROOT)

from app.config import load_config
from app.agent.agent import Agent
from app.utils.logging import get_logger


logger = get_logger(__name__)


def parse_args() -> argparse.Namespace:
    """解析命令行参数。"""

    parser = argparse.ArgumentParser(description="运行智能体处理任务")
    parser.add_argument("--task", type=str, required=True, help="任务描述文本")
    parser.add_argument("--max_steps", type=int, default=3, help="最多工具步骤数")
    return parser.parse_args()


def main() -> None:
    """脚本入口：执行智能体。"""

    args = parse_args()
    cfg = load_config()
    logger = get_logger(__name__, level=cfg.log_level)
    agent = Agent(cfg)
    result = agent.run(task=args.task, max_steps=args.max_steps)
    print("=== 工具日志 ===")
    for log in result["tool_logs"]:
        print(log)
    print("\n=== 最终答案 ===\n" + result["answer"])


if __name__ == "__main__":
    main()