# Daily AI Brief — LangChain Agent 自动简报

> 基于 LangChain Agent + DeepSeek API，自动检索 ArXiv 论文与行业新闻，生成结构化 AI 每日简报。

## 功能演示

```
$ python main.py --topic "AI Agent" --focus "多模态"

============================================================
  AI 每日简报 Agent
  主题: AI Agent
  聚焦: 多模态
============================================================

Agent 自动执行:
  1. fetch_arxiv_papers("multi-modal agent") → 检索到 10 篇论文
  2. search_ai_news("多模态 AI Agent 最新进展") → 搜索到 8 条新闻
  3. [LLM 整合分析...]
  4. save_daily_brief(content) → output/AI简报_20260610.md

✅ 简报生成完成
```

## 生成简报结构

```markdown
## 📰 今日 AI 速览
> 一句话概览

## 🔬 ArXiv 论文精选
- 每篇：标题 | 作者 | 核心贡献 | 与你何干 | 链接

## 📡 行业动态
- 每条：标题 | 来源 | 要点

## 🧠 今日关键词
- 3-5 个高频技术词 + 一句话解释

## 💡 我的看法
- AI 对今日动态的评论
```

## 技术架构

```
用户输入 → LangChain Agent (DeepSeek v3)
              ├── Tool 1: fetch_arxiv_papers  → ArXiv API
              ├── Tool 2: search_ai_news      → DuckDuckGo
              └── Tool 3: save_daily_brief    → output/*.md
```

核心依赖：
- **LangChain** — Agent 框架，Tool-calling Agent + AgentExecutor
- **DeepSeek API** — 大模型推理（OpenAI 兼容协议，成本 ≈ GPT-4 的 1/10）
- **ArXiv API** — 论文检索
- **DuckDuckGo Search** — 新闻搜索

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置 API Key

```bash
cp .env.example .env
# 编辑 .env，填入你的 DeepSeek API Key
```

获取 Key: [platform.deepseek.com](https://platform.deepseek.com)

### 3. 运行

```bash
# 默认主题
python main.py

# 指定主题
python main.py --topic "多模态大模型"

# 只看论文
python main.py --papers-only --topic "RAG retrieval augmented generation"

# 只看新闻
python main.py --news-only --topic "OpenAI Gemini"
```

## 项目结构

```
daily-ai-brief/
├── main.py              # CLI 入口
├── agent/
│   ├── __init__.py
│   ├── core.py          # Agent 构建 + System Prompt + 执行逻辑
│   └── tools.py         # 自定义工具：ArXiv 检索 / 新闻搜索 / 文件保存
├── output/              # 生成的简报 (.md)
├── requirements.txt
├── .env.example
└── README.md
```

## 面试相关

本项目展示以下能力：

| 能力 | 对应 JD 要求 | 项目体现 |
|------|-------------|---------|
| LangChain Agent | 调研 Agent 技术 | 完整的 Tool-calling Agent + AgentExecutor |
| Tool Use / Function Calling | 工具调用模块优化 | 3 个自定义 Tool，含 schema 定义和错误处理 |
| Prompt Engineering | 提示词工程 | 结构化 System Prompt + 输出格式约束 |
| Python 工程能力 | 扎实编程基础 | 模块化设计、类型提示、CLI 工具 |
| API 集成 | 模型接口对接 | DeepSeek OpenAI 兼容协议接入 |

## License

MIT
