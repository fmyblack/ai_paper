# AI Paper Vault

这是一个面向 AI 论文阅读的 Obsidian vault，参考 `~/paper_reader` 的分层方式构建：原始 PDF、提取文本、单篇论文笔记、每日阅读、主题综述和复现实验彼此分离，并通过属性与双链关联。

## 开始使用

1. 在 Obsidian 中选择“打开本地仓库”，打开当前目录 `ai_paper`。
2. 从 [[首页]] 进入论文总览、阅读队列和研究地图。
3. 把 PDF 放入 `library/raw/YYYY/MM/DD/`，或运行导入脚本：

   ```bash
   python3 scripts/ingest_paper.py /path/to/paper.pdf \
     --title "Paper Title" \
     --authors "Author A, Author B" \
     --year 2026 \
     --venue "arXiv" \
     --topics "agents, reasoning"
   ```

4. 在 `notes/papers/YYYY/MM/DD/` 中继续填写自动生成的论文笔记。
5. 阅读过程中，把可复用结论沉淀到 `notes/topics/`，把实验过程记录到 `notes/reproductions/`。

如果环境中安装了 `pypdf`，导入脚本会同时生成可搜索文本并记录页数；未安装时仍会复制 PDF、创建论文笔记和元数据索引。

## 目录

- `library/raw/YYYY/MM/DD/`：按入库日归档的原始 PDF。
- `library/text/YYYY/MM/DD/`：按入库日归档的提取文本。
- `notes/papers/YYYY/MM/DD/`：按入库日归档的单篇论文笔记。
- `notes/daily/`：每日阅读记录。
- `notes/topics/`：跨论文主题综述与概念笔记。
- `notes/reading/`：阅读队列与选择理由。
- `notes/reproductions/`：代码复现和实验记录。
- `dashboards/`：Obsidian Bases 总览与任务追踪。
- `metadata/papers.jsonl`：由导入脚本维护的机器可读索引。
- `templates/`：论文、日记、主题与复现模板。
- `assets/`：笔记中的图片和附件。
- `scripts/ingest_paper.py`：单篇论文导入脚本。

## 状态约定

论文笔记的 `status` 使用以下固定值：

- `inbox`：已收集，未筛选。
- `skimmed`：已快速浏览。
- `reading`：正在精读。
- `read`：已完成阅读笔记。
- `reproducing`：正在复现。
- `reproduced`：已完成关键复现。
- `archived`：不再跟进。

`priority` 建议使用 `1`（最高）到 `5`（最低），`rating` 使用 `1` 到 `5`。

## 可选插件

当前 vault 不依赖社区插件。若后续需要增强体验，可自行安装：

- PDF++：PDF 标注与引用。
- Omnisearch：全文检索。
- Tasks：跨笔记任务管理。
- Linter：统一 Markdown 与 frontmatter 格式。

## Git

按你的安排，当前没有初始化 git。`.gitignore` 已准备好，后续可以直接使用。
