#!/usr/bin/env python3
"""
Daily AI Brief — 命令行入口

用法:
  python main.py                          # 默认主题 "AI Agent"
  python main.py --topic "多模态大模型"     # 指定主题
  python main.py --focus "开源模型"         # 聚焦方向
  python main.py --papers-only             # 只看论文
  python main.py --news-only               # 只看新闻
"""

import argparse
import sys
from pathlib import Path

# 把项目根加入 path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from agent.core import run_brief


def main():
    parser = argparse.ArgumentParser(
        description="AI 每日简报 Agent — 自动检索论文+新闻，生成结构化 Markdown 简报",
    )
    parser.add_argument(
        "--topic", "-t",
        default="AI Agent LLM 大模型",
        help="简报主题 / 搜索关键词（默认: AI Agent LLM 大模型）",
    )
    parser.add_argument(
        "--focus", "-f",
        default="",
        help="聚焦方向，如 '多模态 Agent' 'RAG 检索增强'",
    )
    parser.add_argument(
        "--papers-only",
        action="store_true",
        help="只检索论文，跳过新闻",
    )
    parser.add_argument(
        "--news-only",
        action="store_true",
        help="只检索新闻，跳过论文",
    )

    args = parser.parse_args()

    topic = args.topic
    if args.papers_only:
        topic += " (仅论文)"
    elif args.news_only:
        topic += " (仅新闻)"

    print(f"\n{'='*60}")
    print(f"  AI 每日简报 Agent")
    print(f"  主题: {topic}")
    if args.focus:
        print(f"  聚焦: {args.focus}")
    print(f"{'='*60}\n")

    result = run_brief(topic=topic, focus=args.focus)

    if result["status"] == "success":
        print(f"\n✅ 简报生成完成")
        print(f"📄 简报已保存至 output/ 目录")
    else:
        print(f"\n❌ 生成失败: {result['output']}")
        sys.exit(1)


if __name__ == "__main__":
    main()
