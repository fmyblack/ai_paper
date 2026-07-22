#!/usr/bin/env python3

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
from datetime import date, datetime, timezone
from pathlib import Path


STATUSES = (
    "inbox",
    "skimmed",
    "reading",
    "read",
    "reproducing",
    "reproduced",
    "archived",
)


def parse_comma_list(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file_handle:
        for chunk in iter(lambda: file_handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def safe_note_name(title: str) -> str:
    forbidden = '<>:"/\\|?*\0'
    cleaned = "".join("-" if character in forbidden else character for character in title)
    cleaned = " ".join(cleaned.split()).strip(" .-")
    return cleaned[:180] or "untitled-paper"


def yaml_string(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def yaml_list(values: list[str]) -> str:
    return json.dumps(values, ensure_ascii=False)


def read_pdf(path: Path) -> tuple[int | None, str | None]:
    try:
        from pypdf import PdfReader
    except ImportError:
        return None, None

    reader = PdfReader(str(path))
    pages = len(reader.pages)
    extracted_pages = []
    for page_number, page in enumerate(reader.pages, start=1):
        try:
            page_text = page.extract_text() or ""
        except Exception as error:
            page_text = f"[Page {page_number} extraction failed: {error}]"
        extracted_pages.append(f"\n\n--- Page {page_number} ---\n\n{page_text.strip()}")
    return pages, "".join(extracted_pages).strip() + "\n"


def load_known_hashes(index_path: Path) -> set[str]:
    if not index_path.exists():
        return set()

    known_hashes = set()
    for line in index_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError:
            continue
        if record.get("sha256"):
            known_hashes.add(record["sha256"])
    return known_hashes


def unique_destination(path: Path, source_hash: str) -> Path:
    if not path.exists() or file_sha256(path) == source_hash:
        return path
    return path.with_name(f"{path.stem}-{source_hash[:8]}{path.suffix}")


def paper_note(record: dict[str, object]) -> str:
    authors = record["authors"]
    topics = record["topics"]
    pages = record["pages"]
    pages_value = "" if pages is None else str(pages)
    return f'''---
type: paper
title: {yaml_string(str(record["title"]))}
aliases: []
authors: {yaml_list(authors if isinstance(authors, list) else [])}
year: {record["year"]}
venue: {yaml_string(str(record["venue"]))}
paper_date: {yaml_string(str(record["paper_date"]))}
date_added: {yaml_string(str(record["date_added"]))}
last_read: {yaml_string(str(record["date_added"]))}
topics: {yaml_list(topics if isinstance(topics, list) else [])}
status: {record["status"]}
priority: {record["priority"]}
rating:
arxiv_id: {yaml_string(str(record["arxiv_id"]))}
doi: {yaml_string(str(record["doi"]))}
paper_url: {yaml_string(str(record["paper_url"]))}
code_url: {yaml_string(str(record["code_url"]))}
pdf_path: {yaml_string(str(record["pdf_path"]))}
text_path: {yaml_string(str(record["text_path"]))}
sha256: {yaml_string(str(record["sha256"]))}
pages: {pages_value}
citation_key: ""
related: []
cssclasses:
  - paper-note
---

# {record["title"]}

## 一句话结论

待研读。

## 三分钟筛选

- **问题**：
- **新意**：
- **核心证据**：
- **与我的关系**：
- **决定**：精读 / 稍后读 / 归档 / 复现

## 问题设定

- **输入、输出与目标**：
- **现有瓶颈**：
- **关键假设**：

## 核心贡献

1. 
2. 
3. 

## 方法

### 直觉


### 形式化描述


### 关键模块与训练流程


### 计算与数据成本


## 实验与证据

| 作者主张 | 对应证据 | 定位 | 我的判断 |
| --- | --- | --- | --- |
|  |  |  |  |

### 数据、基线与指标

- **数据集**：
- **基线**：
- **指标**：
- **预算/硬件**：
- **消融与稳定性**：

## 批判性阅读

### 证据支持的结论

- 

### 尚未被充分支持的结论

- 

### 局限、风险与可能反证

- 

## 与已有知识的连接

- **基础论文**：
- **相近方法**：
- **后续工作**：
- **与主题笔记的关系**：

## 复现计划

- **是否复现**：否 / 是 / 待定
- **最小验证目标**：
- **所需资源**：
- **成功标准**：

## 待追踪问题

- [ ] 

## 原文定位

- Page / Section / Figure / Table / Equation：
'''


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Import one AI paper PDF into this Obsidian vault."
    )
    parser.add_argument("pdf", type=Path, help="Path to the source PDF")
    parser.add_argument("--title", help="Paper title; defaults to the PDF filename")
    parser.add_argument("--authors", default="", help="Comma-separated author names")
    parser.add_argument("--year", type=int, help="Publication or preprint year")
    parser.add_argument("--venue", default="", help="Conference, journal, or arXiv")
    parser.add_argument("--paper-date", default="", help="Paper date in YYYY-MM-DD format")
    parser.add_argument("--topics", default="", help="Comma-separated reusable topics")
    parser.add_argument("--status", choices=STATUSES, default="inbox")
    parser.add_argument("--priority", type=int, choices=range(1, 6), default=3)
    parser.add_argument("--arxiv-id", default="")
    parser.add_argument("--doi", default="")
    parser.add_argument("--paper-url", default="")
    parser.add_argument("--code-url", default="")
    parser.add_argument(
        "--force-note",
        action="store_true",
        help="Overwrite an existing generated note. Use with care.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    source_pdf = args.pdf.expanduser().resolve()
    if not source_pdf.is_file():
        print(f"error: PDF not found: {source_pdf}", file=sys.stderr)
        return 2
    if source_pdf.suffix.lower() != ".pdf":
        print(f"error: source is not a PDF: {source_pdf}", file=sys.stderr)
        return 2

    vault_root = Path(__file__).resolve().parents[1]
    added_date = date.today()
    paper_year = args.year or added_date.year
    source_hash = file_sha256(source_pdf)

    date_parts = (
        str(added_date.year),
        f"{added_date.month:02d}",
        f"{added_date.day:02d}",
    )
    raw_directory = vault_root.joinpath("library", "raw", *date_parts)
    text_directory = vault_root.joinpath("library", "text", *date_parts)
    note_directory = vault_root.joinpath("notes", "papers", *date_parts)
    raw_directory.mkdir(parents=True, exist_ok=True)
    text_directory.mkdir(parents=True, exist_ok=True)
    note_directory.mkdir(parents=True, exist_ok=True)

    destination_pdf = unique_destination(raw_directory / source_pdf.name, source_hash)
    if not destination_pdf.exists():
        shutil.copy2(source_pdf, destination_pdf)

    pages, extracted_text = read_pdf(destination_pdf)
    text_path = ""
    if extracted_text is not None:
        destination_text = text_directory / f"{destination_pdf.stem}.txt"
        destination_text.write_text(extracted_text, encoding="utf-8")
        text_path = destination_text.relative_to(vault_root).as_posix()

    title = args.title.strip() if args.title else source_pdf.stem
    note_path = note_directory / f"{safe_note_name(title)}.md"
    record = {
        "title": title,
        "authors": parse_comma_list(args.authors),
        "year": paper_year,
        "venue": args.venue.strip(),
        "paper_date": args.paper_date.strip(),
        "date_added": added_date.isoformat(),
        "topics": parse_comma_list(args.topics),
        "status": args.status,
        "priority": args.priority,
        "arxiv_id": args.arxiv_id.strip(),
        "doi": args.doi.strip(),
        "paper_url": args.paper_url.strip(),
        "code_url": args.code_url.strip(),
        "pdf_path": destination_pdf.relative_to(vault_root).as_posix(),
        "text_path": text_path,
        "sha256": source_hash,
        "pages": pages,
        "note_path": note_path.relative_to(vault_root).as_posix(),
        "ingested_at": datetime.now(timezone.utc).isoformat(),
    }

    if note_path.exists() and not args.force_note:
        print(f"kept existing note: {note_path.relative_to(vault_root)}")
    else:
        note_path.write_text(paper_note(record), encoding="utf-8")
        print(f"wrote note: {note_path.relative_to(vault_root)}")

    index_path = vault_root / "metadata" / "papers.jsonl"
    index_path.parent.mkdir(parents=True, exist_ok=True)
    if source_hash not in load_known_hashes(index_path):
        with index_path.open("a", encoding="utf-8") as index_file:
            index_file.write(json.dumps(record, ensure_ascii=False) + "\n")
        print(f"updated index: {index_path.relative_to(vault_root)}")
    else:
        print(f"index already contains sha256: {source_hash}")

    print(f"stored PDF: {destination_pdf.relative_to(vault_root)}")
    if extracted_text is None:
        print("text extraction skipped: install pypdf to enable it")
    else:
        print(f"extracted text: {text_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
