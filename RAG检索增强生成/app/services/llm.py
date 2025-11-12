"""LLM 生成服务模块。

支持 OpenAI 生成；当不可用时，将使用简单模板进行基于检索的拼接回答，
保证流程可运行与可测试。
遵循 Google Python Style Guide。
"""

from __future__ import annotations

from typing import List, Optional

from ..utils.logging import get_logger

LOGGER = get_logger(__name__)


class LLMService:
    """LLM 生成服务。

    Attributes:
        provider: LLM 提供方标识（如 "openai"）。
        model: LLM 模型名称（可选）。
        api_key: API 密钥（可选）。
        _client: OpenAI 客户端实例（可选）。
    """

    def __init__(self, provider: str, model: Optional[str], api_key: Optional[str]) -> None:
        """初始化 LLM 服务。

        Args:
            provider: LLM 提供方标识，例如 "openai" 或 "none"。
            model: LLM 模型名称。
            api_key: API 密钥。
        """
        self.provider = provider
        self.model = model
        self.api_key = api_key
        self._client = None

        if provider == "openai" and api_key:
            try:
                from openai import OpenAI  # type: ignore

                self._client = OpenAI(api_key=api_key)
                LOGGER.info("OpenAI 客户端已初始化，模型: %s", model)
            except Exception as exc:  # pylint: disable=broad-except
                LOGGER.warning("OpenAI 客户端初始化失败，将使用回退生成。原因: %s", exc)

    def generate(self, question: str, contexts: List[str]) -> str:
        """依据查询与检索到的上下文生成回答。

        Args:
            question: 用户查询文本。
            contexts: 与查询相关的上下文文本列表。

        Returns:
            str: 生成的回答文本。
        """
        context_block = "\n\n".join(contexts[:5]) if contexts else "(无检索到的上下文)"

        if self._client and self.model:
            try:
                prompt = (
                    "基于以下检索到的上下文回答用户问题。\n\n"
                    f"上下文:\n{context_block}\n\n"
                    f"问题: {question}\n"
                    "请用简洁、准确的中文回答。"
                )
                # OpenAI Responses API
                resp = self._client.responses.create(model=self.model, input=prompt)
                return resp.output_text
            except Exception as exc:  # pylint: disable=broad-except
                LOGGER.warning("OpenAI 生成失败，将使用回退生成。原因: %s", exc)

        # 回退：拼接式回答（便于本地无依赖测试）
        return (
            "[基于检索的回答]\n"
            f"问题: {question}\n\n"
            f"参考上下文:\n{context_block}\n\n"
            "说明: 当前使用本地回退生成，如需更高质量回答，请在 .env 中配置 OPENAI_API_KEY 与 LLM_MODEL。"
        )