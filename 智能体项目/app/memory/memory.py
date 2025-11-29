"""对话记忆模块。

提供简易的消息存储与滑动窗口读取，并支持持久化到 JSON 文件。
"""

from __future__ import annotations

import json
import os
from typing import List, Dict

from app.utils.logging import get_logger


logger = get_logger(__name__)


class ConversationMemory:
    """对话记忆管理类。

    Attributes:
        max_messages: 最大保存消息条数（过多时裁剪旧消息）。
        file_path: 持久化存储的 JSON 文件路径。
        messages: 内存中的消息列表，元素形如 `{role, content}`。
    """

    def __init__(self, max_messages: int, file_path: str) -> None:
        """初始化记忆。

        Args:
            max_messages: 最大保存消息条数。
            file_path: 持久化存储的 JSON 文件路径。
        """

        self.max_messages = max_messages
        self.file_path = file_path
        self.messages: List[Dict[str, str]] = []
        self._load()

    def add(self, role: str, content: str) -> None:
        """添加一条消息并裁剪到最大长度。"""

        self.messages.append({"role": role, "content": content})
        if len(self.messages) > self.max_messages:
            overflow = len(self.messages) - self.max_messages
            self.messages = self.messages[overflow:]
        self._save()

    def window(self, size: int) -> List[Dict[str, str]]:
        """返回最近的 `size` 条消息。"""

        return self.messages[-size:]

    def _load(self) -> None:
        """从文件加载历史消息。"""

        try:
            if os.path.isfile(self.file_path):
                with open(self.file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if isinstance(data, list):
                    self.messages = [m for m in data if isinstance(m, dict)]
        except Exception:
            logger.info("历史记忆加载失败，忽略并使用空记忆。")

    def _save(self) -> None:
        """将当前消息保存到文件。"""

        try:
            os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump(self.messages, f, ensure_ascii=False, indent=2)
        except Exception:
            logger.info("记忆保存失败，继续运行不阻断流程。")