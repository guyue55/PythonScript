"""嵌入服务模块。

封装文本到向量的转换，默认使用 Sentence-Transformers；若依赖不可用，
将使用确定性哈希降级生成伪向量，保证流程可运行。
遵循 Google Python Style Guide。
"""

from __future__ import annotations

import hashlib
from typing import Iterable, List

import numpy as np
from ..utils.logging import get_logger

LOGGER = get_logger(__name__)


class EmbeddingsService:
    """文本嵌入服务。

    Attributes:
        model_name: 嵌入模型名称。
        _model: Sentence-Transformers 模型实例（可选）。
        dim: 嵌入维度（降级模式下的维度）。
    """

    def __init__(self, model_name: str) -> None:
        """初始化嵌入服务。

        Args:
            model_name: Sentence-Transformers 模型名称。
        """
        self.model_name = model_name
        self._model = None
        self.dim = 384  # 与 MiniLM 默认维度一致
        try:
            from sentence_transformers import SentenceTransformer  # type: ignore

            self._model = SentenceTransformer(model_name)
            # 尝试获取实际维度（若可用）
            try:
                self.dim = int(self._model.get_sentence_embedding_dimension())
            except Exception:  # pylint: disable=broad-except
                pass
            LOGGER.info("已加载嵌入模型: %s (dim=%d)", model_name, self.dim)
        except Exception as exc:  # pylint: disable=broad-except
            LOGGER.warning("无法加载Sentence-Transformers，将使用降级嵌入。原因: %s", exc)

    def embed(self, texts: Iterable[str]) -> np.ndarray:
        """将文本集合转换为嵌入向量矩阵。

        Args:
            texts: 文本序列。

        Returns:
            numpy.ndarray: 形状为 (N, D) 的向量矩阵，其中 N 为文本数量，D 为维度。
        """
        texts_list: List[str] = list(texts)
        if self._model is not None:
            vectors = self._model.encode(texts_list, normalize_embeddings=True)
            return np.asarray(vectors, dtype=np.float32)

        # 降级模式：使用文本哈希生成确定性随机向量
        rng_vectors: List[np.ndarray] = []
        for t in texts_list:
            h = int(hashlib.md5(t.encode("utf-8")).hexdigest(), 16) % (2 ** 32)
            rng = np.random.RandomState(h)
            v = rng.rand(self.dim).astype(np.float32)
            # 归一化
            v /= np.linalg.norm(v) + 1e-9
            rng_vectors.append(v)
        return np.vstack(rng_vectors)