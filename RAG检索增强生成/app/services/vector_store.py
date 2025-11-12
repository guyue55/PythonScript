"""向量库服务模块。

支持使用 FAISS 进行高效相似度检索，若不可用则自动降级为 NumPy 基础检索。
索引将保存为 `index.faiss`（若可用）与 `meta.json` / `vectors.npy`。
遵循 Google Python Style Guide。
"""

from __future__ import annotations

import json
import os
from typing import Dict, List, Optional, Tuple

import numpy as np
from ..utils.logging import get_logger

LOGGER = get_logger(__name__)


class VectorStore:
    """向量索引存储与检索服务。"""

    def __init__(self, dim: int) -> None:
        """初始化向量库。

        Args:
            dim: 向量维度。
        """
        self.dim = dim
        self._faiss_index = None
        self._metas: List[Dict[str, str]] = []
        self._vectors: Optional[np.ndarray] = None

        # 尝试加载 FAISS
        try:
            import faiss  # type: ignore

            self._faiss = faiss
            self._faiss_index = faiss.IndexFlatIP(dim)
            LOGGER.info("使用 FAISS 进行相似度检索 (dim=%d)", dim)
        except Exception:  # pylint: disable=broad-except
            self._faiss = None
            LOGGER.info("FAISS 不可用，使用 NumPy 降级检索 (dim=%d)", dim)

    def add(self, vectors: np.ndarray, metas: List[Dict[str, str]]) -> None:
        """向索引添加向量与元数据。

        Args:
            vectors: 形状为 (N, D) 的向量矩阵。
            metas: 与向量对应的元数据列表。
        """
        if vectors.ndim != 2 or vectors.shape[1] != self.dim:
            raise ValueError("向量维度不匹配或输入形状无效")
        if len(metas) != vectors.shape[0]:
            raise ValueError("元数据数量必须与向量数量一致")

        self._metas.extend(metas)
        if self._faiss_index is not None:
            self._faiss_index.add(vectors)
        else:
            if self._vectors is None:
                self._vectors = vectors.astype(np.float32)
            else:
                self._vectors = np.vstack([self._vectors, vectors]).astype(np.float32)

    def save(self, index_dir: str) -> None:
        """保存索引到磁盘。

        Args:
            index_dir: 索引存储目录路径。
        """
        os.makedirs(index_dir, exist_ok=True)
        meta_path = os.path.join(index_dir, "meta.json")
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(self._metas, f, ensure_ascii=False, indent=2)

        if self._faiss_index is not None:
            index_path = os.path.join(index_dir, "index.faiss")
            self._faiss.write_index(self._faiss_index, index_path)
        else:
            vec_path = os.path.join(index_dir, "vectors.npy")
            np.save(vec_path, self._vectors if self._vectors is not None else np.zeros((0, self.dim), dtype=np.float32))
        LOGGER.info("索引已保存至: %s", index_dir)

    def load(self, index_dir: str) -> None:
        """从磁盘加载索引。

        Args:
            index_dir: 索引存储目录路径。
        """
        meta_path = os.path.join(index_dir, "meta.json")
        if os.path.exists(meta_path):
            with open(meta_path, "r", encoding="utf-8") as f:
                self._metas = json.load(f)
        else:
            self._metas = []

        if self._faiss_index is not None:
            index_path = os.path.join(index_dir, "index.faiss")
            if os.path.exists(index_path):
                self._faiss_index = self._faiss.read_index(index_path)
        else:
            vec_path = os.path.join(index_dir, "vectors.npy")
            if os.path.exists(vec_path):
                self._vectors = np.load(vec_path).astype(np.float32)
            else:
                self._vectors = np.zeros((0, self.dim), dtype=np.float32)

    def search(self, query_vec: np.ndarray, top_k: int = 5) -> List[Tuple[float, Dict[str, str]]]:
        """执行相似度检索。

        Args:
            query_vec: 形状为 (1, D) 的查询向量。
            top_k: 返回的最相似项数量。

        Returns:
            List[Tuple[float, Dict[str, str]]]: (相似度, 元数据) 的列表，按相似度降序排列。
        """
        if query_vec.ndim != 2 or query_vec.shape[0] != 1 or query_vec.shape[1] != self.dim:
            raise ValueError("查询向量维度无效，应为形状 (1, dim)")

        if self._faiss_index is not None:
            scores, idxs = self._faiss_index.search(query_vec.astype(np.float32), top_k)
            results: List[Tuple[float, Dict[str, str]]] = []
            for score, idx in zip(scores[0], idxs[0]):
                if idx < 0 or idx >= len(self._metas):
                    continue
                results.append((float(score), self._metas[idx]))
            return results

        # NumPy 降级：余弦相似度
        if self._vectors is None or len(self._metas) == 0:
            return []
        # 归一化
        q = query_vec.astype(np.float32)
        q /= np.linalg.norm(q) + 1e-9
        m = self._vectors.astype(np.float32)
        m /= (np.linalg.norm(m, axis=1, keepdims=True) + 1e-9)
        sims = (m @ q.T).reshape(-1)
        top_idx = np.argsort(-sims)[:top_k]
        return [(float(sims[i]), self._metas[i]) for i in top_idx]