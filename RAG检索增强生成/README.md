# RAG 检索增强生成 项目

本项目提供一个遵循最佳实践的 RAG（Retrieval-Augmented Generation）示例，实现数据加载、文本切分、嵌入向量化、向量检索以及基于上下文的答案生成。

## 目录结构

```
RAG检索增强生成/
├── README.md
├── requirements.txt
├── .env.example
├── app/
│   ├── __init__.py
│   ├── config.py
│   ├── pipelines/
│   │   ├── __init__.py
│   │   ├── ingest.py
│   │   ├── index.py
│   │   ├── retrieve.py
│   │   └── generate.py
│   ├── services/
│   │   ├── embeddings.py
│   │   ├── vector_store.py
│   │   └── llm.py
│   └── utils/
│       ├── text_splitter.py
│       ├── doc_loader.py
│       └── logging.py
├── data/
│   ├── raw/
│   ├── processed/
│   └── index/
└── scripts/
    ├── ingest.py
    └── query.py
```

## 快速开始

1. 安装依赖：

```
pip install -r requirements.txt
```

2. 准备数据：将 `.txt` 或 `.md` 文档放入 `data/raw/`。

3. 构建索引：

```
python scripts/ingest.py --source_dir data/raw --index_dir data/index
```

4. 进行查询：

```
python scripts/query.py --query "什么是RAG？" --index_dir data/index
```

## 可选：配置环境变量
复制 `.env.example` 为 `.env` 并填写必要的变量（如 OpenAI Key）。

## 设计原则
- 模块化：加载、切分、嵌入、检索、生成明确分层。
- 可替换：嵌入模型和LLM均可通过配置替换。
- 轻依赖：默认使用本地 `sentence-transformers` 与 `faiss-cpu`。
- 规范：代码遵循 Google Python Style Guide，并包含详尽注释与文档字符串。