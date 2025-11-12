"""查询 CLI 脚本。

对向量索引进行检索，并可选调用 LLM 生成回答。
遵循 Google Python Style Guide，提供清晰参数与类型注释。
"""

from __future__ import annotations

import argparse
from typing import List

from app.config import load_config
from app.pipelines.generate import run_generate
from app.pipelines.retrieve import run_retrieve
from app.services.embeddings import EmbeddingsService
from app.services.llm import LLMService


def parse_args() -> argparse.Namespace:
    """解析命令行参数。

    Returns:
        argparse.Namespace: 解析后的参数对象。
    """
    parser = argparse.ArgumentParser(description="RAG 查询：检索并生成回答")
    parser.add_argument("--query", type=str, required=True, help="查询文本")
    parser.add_argument(
        "--index_dir", type=str, default=None, help="索引目录，默认读取配置中的 INDEX_DIR"
    )
    parser.add_argument(
        "--top_k", type=int, default=5, help="返回的最相关上下文数量"
    )
    parser.add_argument(
        "--no_llm", action="store_true", help="不调用LLM，仅输出检索的上下文"
    )
    return parser.parse_args()


def main() -> None:
    """程序入口。"""
    cfg = load_config()
    args = parse_args()

    index_dir = args.index_dir or cfg.index_dir
    embed = EmbeddingsService(cfg.embedding_model)

    contexts: List[str] = run_retrieve(
        query=args.query, index_dir=index_dir, embed_svc=embed, top_k=args.top_k
    )

    if args.no_llm:
        print("=== 检索到的上下文 ===")
        for i, ctx in enumerate(contexts, start=1):
            print(f"[{i}] {ctx[:400]}" + ("..." if len(ctx) > 400 else ""))
        return

    llm = LLMService(provider=cfg.llm_provider, model=cfg.llm_model, api_key=cfg.openai_api_key)
    answer = run_generate(question=args.query, contexts=contexts, llm=llm)
    print("=== 生成的回答 ===")
    print(answer)


if __name__ == "__main__":
    main()