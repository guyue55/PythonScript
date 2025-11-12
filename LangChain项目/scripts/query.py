"""查询 CLI 脚本。

支持仅检索或检索+LLM 生成两种模式。
遵循 Google Python Style Guide，提供清晰的参数帮助与日志输出。
"""

from __future__ import annotations

import argparse
import os
import sys
from typing import List

# 允许从脚本位置导入 app 包
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
sys.path.append(os.path.join(PROJECT_ROOT, "app"))

from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_openai import OpenAIEmbeddings
from langchain_community.embeddings import HuggingFaceEmbeddings

from app.config import load_config, AppConfig
from app.pipelines.qa import run_qa
from app.vectorstores.store import VectorStoreManager
from app.utils.logging import get_logger


logger = get_logger(__name__)


def parse_args() -> argparse.Namespace:
    """解析命令行参数。"""

    parser = argparse.ArgumentParser(description="查询向量索引并生成答案")
    parser.add_argument("--query", type=str, required=True, help="查询问题文本")
    parser.add_argument(
        "--index_dir",
        type=str,
        default=None,
        help="索引目录（默认读取配置 INDEX_DATA_DIR）",
    )
    parser.add_argument(
        "--no_llm",
        action="store_true",
        help="仅检索不生成答案（输出检索到的文档片段）",
    )
    parser.add_argument(
        "--top_k",
        type=int,
        default=4,
        help="检索返回的文档片段数量",
    )
    return parser.parse_args()


def _get_embeddings(cfg: AppConfig) -> Embeddings:
    """根据配置创建嵌入模型。"""

    if cfg.embeddings_provider.lower() == "openai":
        if not cfg.openai_api_key:
            raise ValueError("使用 OpenAI 嵌入需要 OPENAI_API_KEY。")
        return OpenAIEmbeddings(model=cfg.embeddings_model, api_key=cfg.openai_api_key)
    return HuggingFaceEmbeddings(model_name=cfg.embeddings_model)


def main() -> None:
    """脚本入口：执行检索或检索+生成。"""

    args = parse_args()
    cfg = load_config()

    if args.no_llm:
        # 仅检索模式
        embeddings = _get_embeddings(cfg)
        retriever = VectorStoreManager.load_retriever(
            embeddings=embeddings,
            backend=cfg.vectorstore,
            index_dir=args.index_dir or cfg.index_data_dir,
        )
        docs: List[Document] = retriever.get_relevant_documents(args.query)
        logger.info("检索到 %d 个文档片段：", len(docs))
        for i, d in enumerate(docs[: args.top_k], start=1):
            print(f"[{i}] {d.metadata.get('source', '')}\n{d.page_content}\n")
    else:
        # 检索 + 生成
        result = run_qa(cfg, question=args.query)
        print("答案：\n" + result.get("answer", ""))


if __name__ == "__main__":
    main()