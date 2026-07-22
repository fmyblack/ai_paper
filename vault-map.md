# Vault Map

Last updated: 2026-07-22

## Purpose

本 vault 用于回答：

- 我收集了哪些 AI 论文，分别处于什么阅读状态？
- 一篇论文真正的新意、证据和局限是什么？
- 多篇论文对同一问题有哪些共识与冲突？
- 哪些结论值得复现，复现结果是否支持原论文？
- 未来应该读什么、验证什么、更新什么？

## Entry Files

1. `me.md`：研究目标、兴趣与输出偏好。
2. `vault-map.md`：目录、检索路径和字段约定。
3. `workflows.md`：收集、筛选、精读、综述和复现流程。
4. `README.md`：使用方法、命令和状态约定。
5. `首页.md`：Obsidian 日常入口。

## Storage Layers

- `library/raw/YYYY/MM/DD/`：按入库日归档的不可变原始 PDF 层。
- `library/text/YYYY/MM/DD/`：按入库日归档、用于搜索与 AI 辅助阅读的提取文本层。
- `notes/papers/YYYY/MM/DD/`：按入库日归档的单篇理解层。
- `notes/daily/`：时间线与阅读过程层。
- `notes/topics/`：跨论文知识层。
- `notes/reproductions/`：实验验证层。
- `dashboards/`：属性检索与行动层。
- `metadata/`：机器可读索引层。

## Retrieval Guide

### 查找一篇论文

1. 打开 `dashboards/论文总览.base` 按标题、作者、主题、年份或状态筛选。
2. 阅读 `notes/papers/` 中的结构化笔记。
3. 需要精确措辞时搜索 `library/text/`。
4. 需要图、表、公式或排版时打开 `library/raw/` 中的 PDF。

### 理解一个主题

1. 先读 `notes/topics/AI研究地图.md` 和对应主题笔记。
2. 沿主题笔记中的论文双链回到单篇证据。
3. 对比任务定义、数据、基线、计算预算和评估指标。
4. 把稳定结论、争议和开放问题更新回主题笔记。

### 决定下一篇读什么

1. 查看 `notes/reading/阅读队列.md` 的选择理由。
2. 查看 `dashboards/论文总览.base` 的高优先级与阅读中视图。
3. 优先处理能解决当前问题、建立关键基线或验证重要争议的论文。

## Paper Properties

论文笔记统一使用：

- `type`: 固定为 `paper`。
- `title`: 论文标题。
- `authors`: 作者列表。
- `year`: 发表或预印本年份。
- `venue`: 会议、期刊或 `arXiv`。
- `paper_date`: 论文日期，未知可留空。
- `date_added`: 加入 vault 的日期。
- `last_read`: 最近阅读日期。
- `topics`: 稳定、可复用的主题列表。
- `status`: 见 `README.md` 中的状态约定。
- `priority`: 1–5。
- `rating`: 1–5，可在读完后填写。
- `arxiv_id`, `doi`, `paper_url`, `code_url`: 外部标识与链接。
- `pdf_path`, `text_path`: vault 内相对路径。
- `sha256`, `pages`: 文件校验值与页数。
- `citation_key`: 可选引用键。
- `related`: 相关论文笔记双链列表。

## Linking Rules

- 主题使用 `topics` 属性和 `[[notes/topics/...]]` 双链连接。
- 论文之间的直接关系写入 `related`，并在正文说明关系类型：基础、改进、对照、复现或反证。
- 不为每个新词建立主题笔记；只有需要跨论文复用时才建立。
- 重要摘录保留页码、章节、图号、表号或公式号。

## Git Sync

开始新研究任务前先运行 `git status --short`；工作区干净时运行 `git pull --ff-only`。如果工作区有改动，先检查并保留本地变化，不要覆盖无关工作。

完成研究任务后，检查变更，只暂存本次任务相关文件，创建简洁 commit 并推送到 GitHub。不要提交 API keys、cookies、访问令牌、签名 URL、本地环境文件或其他秘密材料。
