---
type: paper
title: "WikiSkill: Compiling Agent Experience into Persistent Knowledge for Skill Evolution"
aliases: []
authors: ["Liyan Tang", "Cyrus Rashtchian", "Chun-Sung Ferng", "Andrew Tomkins", "Da-Cheng Juan", "Tu Vu"]
year: 2026
venue: "arXiv"
paper_date: "2026-08-27"
date_added: "2026-08-28"
last_read: "2026-08-28"
topics: ["Agent", "技能演化", "长期记忆", "LLM"]
status: read
priority: 1
rating:
arxiv_id: "2608.27454"
doi: ""
paper_url: "https://arxiv.org/abs/2608.27454"
code_url: ""
pdf_path: "library/raw/2026/08/28/2608.27454v1.pdf"
text_path: "library/text/2026/08/28/2608.27454v1.txt"
sha256: "65afc6e12f6f707483fe1b79a97ab67c03abf4b4992f82fde03eb7b8d9ad4a69"
pages: 28
citation_key: ""
related: []
cssclasses:
  - paper-note
---

# WikiSkill: Compiling Agent Experience into Persistent Knowledge for Skill Evolution

## 一句话结论

WikiSkill 的核心不是“让 Agent 记住更多文本”，而是把不可变执行轨迹编译为可累积、可审计的 wiki，再用 wiki 约束技能提案；在五个 benchmark、五个模型上平均优于现有 skill-evolution 基线，但结论仍受直接注入技能、短验证集和有限 horizon 限制。

## 三分钟筛选

- **问题**：既有 EvoSkill/Trace2Skill/SkillOpt 从轨迹更新技能，却把跨迭代的失败模式、被拒提案和成功经验散落在优化历史中。
- **新意**：把 workspace 分为 Raw/Wiki/Skills 三层；wiki 永不回滚，技能更新则经过 validation gating。
- **核心证据**：Table 1 的五模型×五任务结果、Table 2 的跨模型迁移、Table 3 的 wiki-access 消融、ALFWorld case study（§4–5）。
- **与我的关系**：直接连接 Agent 能力形成、外部状态增长、技能压缩与可验证执行主题；可与 SkillRise 对比“技能如何形成”和“知识如何累积”。
- **决定**：精读；优先做小规模消融复现。

## 问题设定

- **输入、输出与目标**：任务数据划分为 `D_train/D_val/D_test`；Inference Agent 产生轨迹，Wiki Maintainer 更新知识，Skill Proposer 产出一次原子技能变更，目标是提升未见任务的 `R(T_test)`（§2，p.3）。
- **现有瓶颈**：技能演化器可从当前轨迹提炼经验，却缺少跨迭代的结构化记忆和失败提案审计。
- **关键假设**：技能可用完整 system-prompt 注入；验证分数足以作为接受门控；wiki 模式可由 LLM 从采样轨迹中可靠归纳。

## 核心贡献

1. 三层架构：`raw/` 保存不可变完整轨迹，`wiki/` 保存 pattern、`logs.md`、`skill-impact.md`，`skills/` 保存可执行 `SKILL.md` 与 `PURPOSE.md`（§3.1，pp.4–5）。
2. 四组件循环：Inference Agent → Wiki Maintainer → Skill Proposer（ReAct）→ Gating/Rollback（Figure 2，p.4）。
3. wiki 持久化带来跨模型迁移和持续细化；但技能本身只在验证集严格变好时接受。

## 方法

### 直觉

把“经验”与“当前策略”分开：轨迹是事实档案，wiki 是归纳后的模式和历史，skill 是当前可执行程序。这样被拒绝的提案也能成为后续推理的负面证据。

### 形式化描述

系统状态为 `(S_k, W_k)`。每轮先采样 `T_train,k`，再执行 `W'_k ← M_WM(W_{k-1}, T_sample,k)`、`P_k ← M_P(W'_k,S_{k-1},T_train,k)`，应用得到 `S'_k`，若 `R(T_val,k)>R_best` 则接受，否则只回滚技能而保留 wiki（式(2)–(4)，pp.5–6；Algorithm 1，p.19）。

### 关键模块与训练流程

Inference Agent 在训练 rollout 时只能读 active skills、不能读 wiki；Maintainer 每轮最多采样 8 条轨迹（最多 5 fail + 3 pass），单条日志最多 15,000 字符；Proposer 通过 `read_file` 按需读取 pattern/raw trace（Appendix C，p.21）。

### 计算与数据成本

五个 benchmark 的训练/验证/测试规模分别为：LiveMath 35/18/124、SealQA 16/10/85、Spreadsheet 80/40/280、OfficeQA 50/24/172、ALFWorld 39/18/134（Table 6，p.20）。完整训练集模式下，每轮 optimizer 调用复杂度为 `1+T_ReAct`，论文观测 `T_ReAct≈10–20`，相对训练集大小为 `O(1)`，但 rollout 与验证推理成本仍随任务数增长（Appendix D.2，pp.22–23）。

## 实验与证据

| 作者主张 | 对应证据 | 定位 | 我的判断 |
| --- | --- | --- | --- |
| WikiSkill 在多模型、多任务上优于基线 | 五模型、五 benchmark 的平均分；相对最强基线提升 3.3/5.1/10.0/5.8/12.0 个百分点 | Table 1，pp.7–8 | 支持较强；三次独立运行并做 paired bootstrap，但任务规模小 |
| wiki 持久化是关键 | Gemini-3.5-Flash 消融：无 wiki proposer 平均 48.7%，默认配置 63.7%；给 Inference Agent wiki 反而降至 60.9% | Table 3，p.11 | 支持“维护者可见 wiki”有因果贡献；也支持训练时隔离 wiki 的设计 |
| 技能可跨模型迁移 | Qwen-3.6-27B 技能让 Qwen-3.5-9B 的 Spreadsheet 从 33.6% 升到 50.5%；但 Qwen-3.5-4B 技能使 Gemini Spreadsheet 从 50.5% 降到 18.1% | Table 2，p.10 | 支持迁移存在，但也明确显示 model-specific negative transfer |

### 数据、基线与指标

- **数据集**：LiveMath、SealQA、SpreadsheetBench、OfficeQA、ALFWorld；覆盖数学、搜索、表格、长上下文 QA、具身交互（§4.1，p.7）。
- **基线**：No skill、Trace2Skill、EvoSkill、SkillOpt；开放模型 Qwen-3.5-4B/9B、Qwen-3.6-27B、Gemma-4-31B，闭源 Gemini-3.5-Flash（p.7）。
- **指标**：各 benchmark task score，表中为测试集平均分；每方法完整演化流程三次独立运行。
- **预算/硬件**：Qwen/Gemma 通过 vLLM；闭源 Gemini；论文未给出统一美元成本或总 token/FLOPs。
- **消融与稳定性**：Table 3 wiki access；Table 2 跨模型 transfer；1000 次 paired bootstrap，`p<0.05`（Appendix C，p.21）。

## 批判性阅读

### 证据支持的结论

- 持久 wiki 比“只看当前轨迹”的 proposer 更能利用重复失败和历史拒绝；默认配置平均比无 wiki proposer 高 15.0 个百分点（Table 3）。
- 技能收益随 Qwen 模型规模上升：4B/9B/27B 相对 no-skill 平均提升 12.3/17.5/23.9 个百分点（§4.2.1，p.9）。
- 技能质量与执行能力可分离：较弱模型产生的程序化 workaround 可能帮助自己，却限制更强模型（§4.2.2，p.10）。

### 尚未被充分支持的结论

- “可复用技能”尚未在动态 skill retrieval/triggering 下验证；实验直接把所有 active skills 注入 prompt。
- `O(1)` 只描述每轮 optimizer LLM call 相对训练集大小，不等于端到端成本或 wall-clock 成本恒定。
- 持久 wiki 的长期收益尚未在数百步、数小时级任务上验证。

### 局限、风险与可能反证

- 严格的 `R_val` 单调门控会拒绝“短期不变、长期有益”的中性提案（Limitations，p.14）。
- wiki 无自动 pruning，长期运行可能膨胀、冲突或污染后续提案。
- 训练时禁止 Inference Agent 读 wiki 是人为 protocol；真实部署中 Agent 可能需要读取结构化记忆，当前消融不能直接给出产品策略。
- 反证路径：固定 rollout/验证预算，比较“持久 wiki”“仅 raw trace”“随机/打乱 wiki”“可检索技能库”，并测试跨任务族和长 horizon。

## 与已有知识的连接

- **基础论文**：ReAct；经验驱动 skill evolution；Anthropic Agent Skills。
- **相近方法**：[[notes/papers/2026/07/30/SkillRise- Agentic Reinforcement Learning for Cross-Task Skill Evolution]]（future-return 技能形成）、Trace2Skill、EvoSkill、SkillOpt、SkillZip。
- **后续工作**：技能 retrieval/triggering、wiki pruning、在线单轨迹内适应。
- **与主题笔记的关系**：[[notes/topics/Agent外部状态的增长、验证与压缩]]；本篇补足“外部状态如何沉淀并反哺技能”。

## 复现计划

- **是否复现**：待定（建议小规模复现）。
- **最小验证目标**：在 ALFWorld 或 Spreadsheet 上复现 Table 3 的四种 wiki-access 配置，并加入 shuffled-wiki placebo。
- **所需资源**：一个可调用的开源 instruct 模型、任务环境、轨迹记录器、markdown patch 工具和固定验证集。
- **成功标准**：默认配置相对 no-wiki proposer 的提升方向一致；负迁移在模型/任务切换时可被观测。

## 待追踪问题

- [ ] wiki pattern 的质量能否用独立人工/规则审计，而不是只看最终分数？
- [ ] 中性提案、wiki pruning 和冲突检测会不会改善长程演化？
- [ ] 动态 skill retrieval 下，持久 wiki 是否仍优于纯 embedding memory？

## 原文定位

- Page / Section / Figure / Table / Equation：§2 p.3；Figure 2 p.4；§3.1–3.2 pp.4–6；Table 1 pp.7–8；Table 2 p.10；Table 3 p.11；Figure 3 p.12；Limitations p.14；Algorithm 1 p.19；Table 6 p.20；Appendix C–D pp.21–23。
