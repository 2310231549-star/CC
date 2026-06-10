"""
Daily AI Brief — Agent 核心

用 LangChain + DeepSeek (OpenAI 兼容协议) 构建 Tool-calling Agent。
Agent 自动决策调用哪些工具、如何处理结果、何时输出最终答案。
"""

import json
import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from .tools import TOOL_REGISTRY

# 加载 .env
_env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(_env_path)


# ──── System Prompt ────

SYSTEM_PROMPT = """你是 AI 每日简报编辑 Agent。你的任务是根据用户指令：

1. 检索 ArXiv 最新 AI/ML 论文（用 fetch_arxiv_papers）
2. 搜索 AI 行业新闻（用 search_ai_news）
3. 将所有信息整合成结构化的 Markdown 简报
4. 调用 save_daily_brief 保存简报

工作流程建议（你自己判断是否调整）：
- 先用中文关键词搜索一轮论文（如 "large language model", "AI agent", "retrieval augmented generation"）
- 再搜索一轮中文 AI 新闻
- 如果结果太少，换关键词补搜一轮
- 汇总去重后，生成如下结构的 Markdown 简报，然后调用 save_daily_brief 保存

简报 Markdown 结构要求：
## 📰 今日 AI 速览
> 一句话概览今日重点

## 🔬 ArXiv 论文精选
每篇：**标题** | 第一作者 | 日期
- 核心贡献（一句话）
- 与你何干（一句话）
🔗 [链接]

## 📡 行业动态
每条：**标题** - 来源
- 要点（一句话）

## 🧠 今日关键词
3-5 个今日出现的高频技术关键词，一句话解释每个

## 💡 我的看法（可选）
如果信息足够，写 2-3 句对今日动态的个人评论

要求：
- 用中文输出，专业术语保留英文
- 每篇论文写清"与你何干"——为什么值得关注
- 不要输出虚构或不确定的内容
- 简报不超过 1500 字
"""


# ──── Tool 包装 ────

@tool
def fetch_arxiv_papers(query: str = "large language model agent", max_results: int = 10) -> str:
    """检索 ArXiv 最新 AI/ML 论文。query 支持 ArXiv 前缀 (ti:/au:/cat:)。返回 JSON。"""
    return TOOL_REGISTRY["fetch_arxiv_papers"](query, max_results)


@tool
def search_ai_news(query: str = "AI Agent LLM 最新进展", max_results: int = 8) -> str:
    """搜索 AI 行业新闻，中文/英文均可。返回 JSON。"""
    return TOOL_REGISTRY["search_ai_news"](query, max_results)


@tool
def save_daily_brief(content: str, filename: str = "") -> str:
    """把最终 Markdown 简报保存到 output/ 目录。content 为完整 Markdown。返回 JSON。"""
    return TOOL_REGISTRY["save_daily_brief"](content, filename or None)


# ──── Agent 构建 ────

def build_agent(model_name: str = "", temperature: float = 0.3):
    """构建并返回 AgentExecutor。

    Args:
        model_name: 模型名，默认读环境变量 MODEL_NAME 或 deepseek-chat。
        temperature: 生成温度，简报任务建议 0.2-0.4。
    """
    api_key = os.getenv("DEEPSEEK_API_KEY") or os.getenv("OPENAI_API_KEY")
    base_url = os.getenv("DEEPSEEK_BASE_URL") or os.getenv("OPENAI_BASE_URL")

    if not api_key:
        raise RuntimeError(
            "未设置 API Key。请复制 .env.example 为 .env 并填入密钥。"
        )

    if not model_name:
        model_name = os.getenv("MODEL_NAME", "deepseek-chat")

    llm = ChatOpenAI(
        model=model_name,
        api_key=api_key,
        base_url=base_url,
        temperature=temperature,
        max_tokens=4096,
    )

    tools = [fetch_arxiv_papers, search_ai_news, save_daily_brief]

    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])

    agent = create_tool_calling_agent(llm, tools, prompt)
    executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        max_iterations=12,
        handle_parsing_errors=True,
    )
    return executor


# ──── 一次运行 ────

def run_brief(topic: str = "AI Agent 最新进展", focus: str = "") -> dict:
    """运行一次简报生成。

    Args:
        topic: 简报主题 / 搜索关键词。
        focus: 可选聚焦方向，如 "多模态 Agent"。

    Returns:
        {"status": "success"|"error", "output": str, "path": str|None}
    """
    user_input = f"请生成今日 AI 简报。主题：{topic}。"
    if focus:
        user_input += f" 聚焦方向：{focus}。"

    try:
        executor = build_agent()
        result = executor.invoke({"input": user_input})
        return {
            "status": "success",
            "output": result["output"],
            "path": None,  # path 由 save_daily_brief 工具返回，需从中间步骤提取
        }
    except Exception as e:
        return {"status": "error", "output": str(e), "path": None}
