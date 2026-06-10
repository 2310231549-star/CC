"""
读取简历和 JD 文件，输出纯文本内容。
支持 .docx / .pdf / .txt 格式。
"""

import argparse
import json
import sys
from pathlib import Path


def read_txt(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def read_docx(path: str) -> str:
    try:
        from docx import Document
    except ImportError:
        print("正在安装 python-docx...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "python-docx", "-q"])
        from docx import Document

    doc = Document(path)
    return "\n".join(p.text for p in doc.paragraphs if p.text.strip())


def read_pdf(path: str) -> str:
    try:
        import fitz  # PyMuPDF
    except ImportError:
        try:
            from pdfminer.high_level import extract_text
            return extract_text(path)
        except ImportError:
            print("正在安装 pdfminer.six...")
            import subprocess
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pdfminer.six", "-q"])
            from pdfminer.high_level import extract_text
            return extract_text(path)

    doc = fitz.open(path)
    text = "\n".join(page.get_text() for page in doc)
    doc.close()
    return text


def read_file(path: str) -> str:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"文件不存在: {path}")

    ext = p.suffix.lower()
    if ext == ".txt":
        return read_txt(path)
    elif ext == ".docx":
        return read_docx(path)
    elif ext == ".pdf":
        return read_pdf(path)
    else:
        raise ValueError(f"不支持的文件格式: {ext}，支持 .txt / .docx / .pdf")


def main():
    parser = argparse.ArgumentParser(description="读取简历和JD文件")
    parser.add_argument("--resume", required=True, help="简历文件路径")
    parser.add_argument("--jd", default=None, help="JD文件路径（可选）")
    parser.add_argument("--cache", default=".interview_cache.json", help="缓存文件路径")
    args = parser.parse_args()

    result = {}

    print("=" * 60)
    print("📄 简历内容")
    print("=" * 60)
    resume_text = read_file(args.resume)
    result["resume"] = resume_text
    print(resume_text)

    if args.jd:
        print("\n" + "=" * 60)
        print("📋 JD 内容")
        print("=" * 60)
        jd_text = read_file(args.jd)
        result["jd"] = jd_text
        print(jd_text)

    # 缓存
    cache_path = Path(args.cache)
    cache_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n✅ 已缓存到 {cache_path}")

    # 也输出 JSON 摘要到 stdout 最后一行，方便解析
    summary = {
        "resume_length": len(resume_text),
        "resume_preview": resume_text[:200] + "..." if len(resume_text) > 200 else resume_text,
    }
    if args.jd:
        summary["jd_length"] = len(jd_text)
        summary["jd_preview"] = jd_text[:200] + "..." if len(jd_text) > 200 else jd_text

    print("\n---JSON_SUMMARY---")
    print(json.dumps(summary, ensure_ascii=False))


if __name__ == "__main__":
    main()
