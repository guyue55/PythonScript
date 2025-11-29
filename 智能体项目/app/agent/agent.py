"""智能体核心模块。

提供基础的决策循环：解析任务、判断是否调用工具（Web 搜索或计算器），
结合对话记忆与 LLM 生成最终回复。示例策略简单且可扩展。
"""

from __future__ import annotations

import re
from typing import Dict, Any, List

from app.config import AppConfig
from app.services.llm import LLMService
from app.tools.web_search import web_search
from app.tools.calculator import safe_calculate
from app.memory.memory import ConversationMemory


SYSTEM_PROMPT = (
    "你是一个可靠的中文智能体。"
    "在有需要时先检索或计算，再组织清晰、可执行的答案。"
    "回答中尽量给出简要步骤与来源链接。"
)


class Agent:
    """最简智能体实现。"""

    def __init__(self, cfg: AppConfig) -> None:
        """初始化智能体。

        Args:
            cfg: 应用配置对象。
        """

        self.cfg = cfg
        # 根据提供商选择通用/专用的 API Key 与基础 URL
        prov = cfg.llm_provider.lower()
        api_key = cfg.llm_api_key
        base_url = cfg.llm_base_url
        self.llm = LLMService(cfg.llm_provider, cfg.llm_model, api_key, base_url)
        self.memory = ConversationMemory(cfg.memory_max_messages, cfg.memory_file)

    def _should_search(self, task: str) -> bool:
        """根据任务文本判断是否需要网络搜索。"""

        keywords = ["搜索", "查找", "news", "热点", "trending", "资料"]
        return any(k in task.lower() for k in keywords)

    def _extract_math(self, task: str) -> str | None:
        """尝试从任务中抽取算术表达式。"""

        pattern = r"[\d\s\+\-\*\/\(\)\%\^]+"
        match = re.search(pattern, task)
        return match.group(0) if match else None

    def run(self, task: str, max_steps: int = 3) -> Dict[str, Any]:
        """执行智能体主循环。

        Args:
            task: 用户任务描述。
            max_steps: 最大工具步骤数（不含最终生成）。

        Returns:
            Dict[str, Any]: 包含 `answer`、`tool_logs` 的结果字典。
        """

        tool_logs: List[str] = []
        self.memory.add("user", task)

        # Step 1: 工具使用（可选）
        steps = 0
        if steps < max_steps and self._should_search(task):
            results = web_search(task, max_results=self.cfg.search_max_results)
            tool_logs.append(f"[web_search] 共返回 {len(results)} 条结果")
            self.memory.add("assistant", "已进行搜索：\n" + "\n".join(results[:5]))
            steps += 1

        if steps < max_steps:
            expr = self._extract_math(task)
            if expr and re.search(r"\d", expr):
                try:
                    value = safe_calculate(expr)
                    tool_logs.append(f"[calculator] {expr} = {value}")
                    self.memory.add("assistant", f"计算结果：{expr} = {value}")
                    steps += 1
                except Exception:
                    tool_logs.append("[calculator] 表达式解析失败，已跳过")

        # Step 2: LLM 生成最终答案
        window = self.memory.window(size=min(10, self.cfg.memory_max_messages))
        answer = self.llm.generate(
            system_prompt=SYSTEM_PROMPT,
            messages=window,
        )
        self.memory.add("assistant", answer)

        return {"answer": answer, "tool_logs": tool_logs}
