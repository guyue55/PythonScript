"""问答（检索增强生成）管道。

基于 LangChain 的检索链组合，实现从向量库检索相关文档，
并使用 LLM 结合上下文生成答案。
"""

from __future__ import annotations

from typing import Dict, Any

from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains.retrieval import create_retrieval_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable
from langchain_core.embeddings import Embeddings
from langchain_openai import OpenAIEmbeddings
from langchain_community.embeddings import HuggingFaceEmbeddings

from app.config import AppConfig
from app.llm.openai_llm import get_chat_llm
from app.vectorstores.store import VectorStoreManager
from app.utils.logging import get_logger


logger = get_logger(__name__)


def _get_embeddings(cfg: AppConfig) -> Embeddings:
    """根据配置创建嵌入模型实例。

    Args:
        cfg: 应用配置对象。

    Returns:
        Embeddings: 嵌入模型实例。
    """

    if cfg.embeddings_provider.lower() == "openai":
        if not cfg.openai_api_key:
            raise ValueError("使用 OpenAI 嵌入需要 OPENAI_API_KEY。")
        return OpenAIEmbeddings(model=cfg.embeddings_model, api_key=cfg.openai_api_key)
    return HuggingFaceEmbeddings(model_name=cfg.embeddings_model)


def build_qa_chain(cfg: AppConfig) -> Runnable:
    """构建检索增强生成链。

    Args:
        cfg: 应用配置对象。

    Returns:
        Runnable: 可 `invoke({"input": "问题"})` 的链对象。
    """

    embeddings = _get_embeddings(cfg)
    retriever = VectorStoreManager.load_retriever(
        embeddings=embeddings, backend=cfg.vectorstore, index_dir=cfg.index_data_dir
    )

    if cfg.llm_provider.lower() == "openai":
        llm = get_chat_llm(model=cfg.llm_model, api_key=cfg.openai_api_key)
    else:
        raise ValueError("当前仅示例 OpenAI LLM，可在需要时扩展本地LLM。")

    prompt = ChatPromptTemplate.from_messages([
        ("system", "你是一个严谨的中文助理。基于提供的上下文回答用户问题。"),
        ("human", "问题：{input}\n\n上下文：{context}"),
    ])
    combine_chain = create_stuff_documents_chain(llm, prompt)
    chain = create_retrieval_chain(retriever, combine_chain)
    return chain


def run_qa(cfg: AppConfig, question: str) -> Dict[str, Any]:
    """执行检索增强生成流程。

    Args:
        cfg: 应用配置对象。
        question: 用户问题字符串。

    Returns:
        Dict[str, Any]: 包含 `answer` 与 `context` 的结果字典。
    """

    chain = build_qa_chain(cfg)
    result = chain.invoke({"input": question})
    # 标准返回包含 `answer` 与作为中间变量的文档列表
    logger.info("生成完成。")
    return result