# LangChain 项目（检索增强生成）

本项目提供一个遵循最佳实践的 LangChain 示例，实现文档加载、文本切分、向量化索引、检索与基于上下文的回答生成。结构清晰、模块化、易扩展。

## 目录结构

```
LangChain项目/
├── README.md
├── requirements.txt
├── .env.example
├── app/
│   ├── __init__.py
│   ├── config.py
│   ├── loaders/
│   │   └── file_loader.py
│   ├── utils/
│   │   └── logging.py
│   ├── vectorstores/
│   │   └── store.py
│   ├── llm/
│   │   └── openai_llm.py
│   └── pipelines/
│       ├── ingest.py
│       └── qa.py
├── data/
│   ├── raw/
│   └── index/
└── scripts/
    ├── ingest.py
    └── query.py
```

## 快速开始

1) 安装依赖：

```
pip install -r LangChain项目/requirements.txt
```

2) 准备数据：将 `.txt` / `.md` / `.pdf` 放入 `LangChain项目/data/raw/`。

3) 构建索引：

```
python LangChain项目/scripts/ingest.py --source_dir LangChain项目/data/raw --index_dir LangChain项目/data/index
```

4) 进行查询（检索 + 生成）：

```
python LangChain项目/scripts/query.py --query "什么是RAG？" --index_dir LangChain项目/data/index
```

仅检索不调用LLM：

```
python LangChain项目/scripts/query.py --query "RAG优势？" --index_dir LangChain项目/data/index --no_llm
```

## 配置环境变量
复制 `.env.example` 为 `.env` 并根据需要填写（OpenAI API Key 等）。

## 设计原则
- 模块化：加载、切分、嵌入、检索、生成分层清晰。
- 可替换：支持 OpenAI 与本地嵌入/LLM，向量库支持 FAISS/Chroma。
- 轻依赖与降级：在依赖缺失时提供降级方案，保证可运行。
- 规范：遵循 Google Python Style Guide，包含详尽文档字符串与类型注释。