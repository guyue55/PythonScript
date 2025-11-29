# 智能体项目（Agent）

本项目提供一个遵循最佳实践的 Python 智能体（Agent）示例，包含：配置管理、LLM 服务、工具执行（Web 搜索与安全计算）、对话记忆、智能体决策循环，以及可运行的 CLI 脚本。

更多内容请阅读：
- docs/学习教程.md
- docs/使用教程.md

## 目录结构

```
智能体项目/
├── README.md
├── requirements.txt
├── .env.example
├── app/
│   ├── __init__.py
│   ├── config.py
│   ├── utils/
│   │   └── logging.py
│   ├── services/
│   │   └── llm.py
│   ├── tools/
│   │   ├── web_search.py
│   │   └── calculator.py
│   ├── memory/
│   │   └── memory.py
│   └── agent/
│       └── agent.py
├── storage/
│   └── .gitkeep
└── scripts/
    └── run.py
```

## 快速开始

1) 安装依赖：

```
pip install -r 智能体项目/requirements.txt
```

2) 配置环境：复制 `.env.example` 为 `.env` 并按需填写。

3) 运行智能体：

```
python 智能体项目/scripts/run.py --task "帮我搜索本周AI热点" --max_steps 3
```

## 设计原则
- 模块化：配置、工具、记忆、服务与智能体核心分层清晰。
- 安全性：工具调用受控；计算器仅支持安全算术表达式；Web 搜索通过公共API包实现。
- 可维护性：遵循 Google Python Style Guide，提供详尽文档字符串与类型注释。
- 可扩展：易于新增工具、替换LLM或改进决策策略。