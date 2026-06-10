"""
Daily AI Brief — 自定义工具集

三组工具：
  1. fetch_arxiv  — 检索 ArXiv 最新 AI 论文
  2. search_news  — 搜索 AI 行业新闻
  3. save_brief   — 将简报写入 Markdown 文件
"""

import json
import os
import re
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Optional

# --- ArXiv tool ---

def fetch_arxiv_papers(query: str = "large language model agent", max_results: int = 10) -> str:
    """从 ArXiv 检索近期 AI 论文，返回标题 + 摘要 + 链接。

    Args:
        query: 搜索关键词，支持 ArXiv 前缀语法 (ti:/au:/cat:)。
               cat:cs.AI cat:cs.CL cat:cs.LG 分别对应 AI / NLP / ML 分类。
        max_results: 最大返回条数，默认 10。

    Returns:
        JSON 字符串，每篇论文含 title, summary, authors, published, url。
        出错时返回含 error 键的 JSON。
    """
    try:
        import arxiv
    except ImportError:
        return json.dumps({"error": "arxiv 库未安装，请 pip install arxiv"}, ensure_ascii=False)

    try:
        client = arxiv.Client()
        search = arxiv.Search(
            query=query,
            max_results=max_results,
            sort_by=arxiv.SortCriterion.SubmittedDate,
        )
        papers = []
        for result in client.results(search):
            papers.append({
                "title": result.title,
                "summary": result.summary.replace("\n", " ")[:500],
                "authors": [a.name for a in result.authors[:5]],
                "published": result.published.isoformat(),
                "url": result.entry_id,
            })
        if not papers:
            return json.dumps({"message": "未找到匹配论文", "count": 0}, ensure_ascii=False)
        return json.dumps({"count": len(papers), "papers": papers}, ensure_ascii=False)

    except Exception as e:
        return json.dumps({"error": f"ArXiv 检索失败: {e}"}, ensure_ascii=False)


# --- News search tool ---

def search_ai_news(query: str = "AI Agent LLM 最新进展", max_results: int = 8) -> str:
    """搜索 AI 行业新闻，返回标题 + 摘要 + 来源。

    Args:
        query: 搜索关键词，中文 / 英文均可。
        max_results: 最大返回条数，默认 8。

    Returns:
        JSON 字符串，每条新闻含 title, snippet, source, url。
        出错时返回含 error 键的 JSON。
    """
    try:
        from duckduckgo_search import DDGS
    except ImportError:
        return json.dumps({"error": "duckduckgo-search 库未安装"}, ensure_ascii=False)

    try:
        results = []
        with DDGS() as ddgs:
            for r in ddgs.text(f"{query} 2025 2026", max_results=max_results):
                results.append({
                    "title": r.get("title", ""),
                    "snippet": r.get("body", "")[:300],
                    "source": r.get("href", ""),
                })
        if not results:
            return json.dumps({"message": "未找到相关新闻", "count": 0}, ensure_ascii=False)
        return json.dumps({"count": len(results), "news": results}, ensure_ascii=False)

    except Exception as e:
        return json.dumps({"error": f"新闻搜索失败: {e}"}, ensure_ascii=False)


# --- Save brief tool ---

# 本地时间
TZ = timezone(timedelta(hours=8))

def save_daily_brief(content: str, filename: Optional[str] = None) -> str:
    """把生成的 AI 简报保存为 Markdown 文件。

    Args:
        content: 简报 Markdown 正文（Agent 生成的结构化内容）。
        filename: 可选文件名，默认 AI简报_日期.md，保存到 output/ 目录。

    Returns:
        JSON 字符串，含 saved_path 或 error。
    """
    try:
        if filename is None:
            date_str = datetime.now(TZ).strftime("%Y%m%d")
            filename = f"AI简报_{date_str}.md"
        if not filename.endswith(".md"):
            filename += ".md"

        output_dir = Path(__file__).resolve().parent.parent / "output"
        output_dir.mkdir(parents=True, exist_ok=True)
        dest = output_dir / filename

        # 添加页眉
        timestamp = datetime.now(TZ).strftime("%Y-%m-%d %H:%M")
        header_block = (
            f"> AI 每日简报 | 生成时间：{timestamp}\n"
            f"> 由 LangChain Agent 自动编排生成\n\n---\n\n"
        )
        dest.write_text(header_block + content, encoding="utf-8")
        return json.dumps({
            "saved_path": str(dest.resolve()),
            "filename": filename,
            "size_bytes": dest.stat().st_size,
        }, ensure_ascii=False)

    except Exception as e:
        return json.dumps({"error": f"保存失败: {e}"}, ensure_ascii=False)


# --- 工具注册表 ---

TOOL_REGISTRY = {
    "fetch_arxiv_papers": fetch_arxiv_papers,
    "search_ai_news": search_ai_news,
    "save_daily_brief": save_daily_brief,
}
