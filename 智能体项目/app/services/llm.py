"""LLM 服务模块。

提供面向智能体的统一 LLM 调用接口，支持 OpenAI 与 Moonshot(Kimi)。
当未配置外部提供商时，回退到简单模板回复。
"""

from __future__ import annotations

from typing import Optional, List, Dict

from openai import OpenAI

from app.utils.logging import get_logger


logger = get_logger(__name__)


class LLMService:
    """封装 LLM 生成的服务类。

    Attributes:
        provider: LLM 提供商标识，例如 "openai" 或 "moonshot"。
        model: LLM 模型名称字符串。
        api_key: 提供商对应的 API Key，可为空（将触发回退）。
        base_url: 可选的基础 URL（OpenAI 兼容供应商需设置为其 API 地址）。
    """

    def __init__(
        self,
        provider: str,
        model: str,
        api_key: Optional[str],
        base_url: Optional[str] = None,
    ) -> None:
        """初始化 LLM 服务。

        Args:
            provider: LLM 提供商标识。
            model: LLM 模型名称。
            api_key: 提供商 API Key。
            base_url: 可选基础 URL（如 Moonshot 默认为 https://api.moonshot.cn/v1）。
        """

        self.provider = provider
        self.model = model
        self.api_key = api_key
        self.base_url = base_url
        self._client = None

        prov = provider.lower()
        if api_key:
            if prov == "openai" and not base_url:
                self._client = OpenAI(api_key=api_key)
            else:
                # 通用 OpenAI 兼容：需要提供 base_url
                if base_url:
                    self._client = OpenAI(api_key=api_key, base_url=base_url)

    def generate(self, system_prompt: str, messages: List[Dict[str, str]]) -> str:
        """生成回复文本。

        Args:
            system_prompt: 系统指令，用于约束回答风格与行为。
            messages: 对话消息列表，形如 `{role, content}`。

        Returns:
            str: 模型生成的回复文本；当未配置外部 LLM 时返回模板化回退回复。
        """

        if self._client is None:
            logger.info("未配置外部 LLM，使用回退生成。")
            last_user = next((m["content"] for m in reversed(messages) if m["role"] == "user"), "")
            return (
                f"[回退生成] 我已收到你的请求：{last_user}\n"
                "（建议配置对应提供商的 API Key 以启用高质量生成）"
            )

        chat_messages = [{"role": "system", "content": system_prompt}] + messages
        resp = self._client.chat.completions.create(
            model=self.model,
            messages=chat_messages,
            temperature=0.2,
        )
        return resp.choices[0].message.content or ""
