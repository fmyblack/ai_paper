---
type: paper
title: "Beyond Retrieval: Analytic Memory for Multimodal Agents"
aliases: []
authors: ["Zhoujin Tian", "Yao Tian", "Hao Zhang", "Cheng Chen", "Yakun Li", "Lei Zhang", "Xiaofang Zhou"]
year: 2026
venue: "arXiv"
paper_date: "2026-07-31"
date_added: "2026-08-03"
last_read: "2026-08-03"
topics: ["Agent", "长上下文与记忆", "多模态模型", "检索增强生成"]
status: read
priority: 1
rating:
arxiv_id: "2607.29440"
doi: ""
paper_url: "https://arxiv.org/abs/2607.29440"
code_url: ""
pdf_path: "library/raw/2026/08/03/2607.29440v1.pdf"
text_path: "library/text/2026/08/03/2607.29440v1.txt"
sha256: "0f740fd06a8ff869ae3474e74db057c6bb9886199bf0eec09b0101b6ce2c4f33"
pages: 10
citation_key: ""
related: []
cssclasses:
  - paper-note
---

# Beyond Retrieval: Analytic Memory for Multimodal Agents

## 一句话结论

Beyond Retrieval 提出一个很清楚的 memory 分工：retrieval memory 负责找相关历史，analytic memory 负责把反复出现的多模态观察组织成可过滤、聚合、排序、时间比较的表结构；ADAMM 在 MemEye / MemGallery 上稳定超过强检索基线，但它的瓶颈也很明确：属性抽取错误会传染到 schema 和计算结果，工具集合仍是预定义的。

## 三分钟筛选

- **问题**：长期多模态记忆不只需要“检索相关内容”，还需要对历史观察做完整范围的过滤、聚合、排序和时间比较；纯 retrieval 会在覆盖率和上下文长度之间摇摆。
- **新意**：从对话、图像和元数据中抽取带 provenance 的 attribute-value observations，自动发现重复 schema 并物化成表，再用 planner 在 retrieval tools 和 analytic tools 之间编排。
- **核心证据**：在 MemEye / MemGallery 两个 benchmark、GPT-4.1-nano 和 GPT-5.4-mini 两个回答模型下，ADAMM 所有指标最佳；GPT-5.4-mini 上 MemEye LLM-Judge 从最强基线 49.4 提升到 60.7。
- **与我的关系**：它补上 Agent memory 的“可计算性”缺口，和 MemSecBench/HiSkill 一起支持 memory 需要 provenance、scope、operation 和 repair 机制。
- **决定**：精读；适合作为多模态长期记忆系统设计的概念基线。

## 问题设定

- **输入、输出与目标**：输入是跨 session 的多模态交互历史 `H={S_i}`，每轮包含对话、视觉观察和时间；目标是对用户查询给出基于历史证据的正确答案。
- **现有瓶颈**：retrieval memory 擅长返回相关片段，但对“过去一个月平均睡眠”“最近哪个品牌出现最多”“按时间比较数值变化”这类查询，必须找全记录并执行操作；检索 top-k 可能漏掉必要观察，放大 top-k 又浪费上下文。
- **关键假设**：多模态历史中存在可重复出现的字段结构；LLM/视觉模型能抽取足够可靠的 attribute-value pairs；常见分析需求可被有限工具集合覆盖。

## 核心贡献

1. 明确提出 retrieval-analysis mismatch：相关性检索不能替代完整范围的结构化计算。
2. 提出 ADAMM：同时维护 schema-induced analytic memory 和 hierarchical retrieval memory。
3. 设计 memory-aware planner，让查询先转为高层信息目标，再渐进实例化 LOOKUP / FILTER / COMPUTE / RANK / SEMANTICMATCH / EVENTLOCATE 等工具调用。

## 方法

### 直觉

如果用户问“上个月平均睡眠多久”，把若干相似截图塞给 LLM 并不可靠；系统应先把每次睡眠记录整理成表，再对时间范围过滤和求均值。ADAMM 的关键是让长期记忆既能召回故事，也能像小型数据库一样被计算。

### 形式化描述

- 每个 interaction round `R_t` 被抽取为 `O_t={(a_tl, x_tl, p_tl)}`，其中 `a` 是属性、`x` 是值、`p` 是支持证据指针。
- 对每轮属性集合 `A_t` 做候选模式挖掘，用 support 保证模式反复出现，用 all-confidence 避免把常见属性错误合并到所有 schema。
- 对已有 schema 用 extension confidence 判断新属性是否稳定伴随旧 schema 出现，从而做 schema evolution。
- retrieval memory 采用 topic -> episode -> event 三层，保留开放语义和细粒度证据；analytic memory 采用表结构，支持确定性操作。

### 关键模块与训练流程

- **Attribute Extraction**：LLM-based extractor 从对话和视觉内容中抽取所有可落地的 attribute-value-provenance 三元组。
- **Schema Discovery / Evolution**：基于 Apriori 风格的频繁项集挖掘，发现新 schema 或扩展旧 schema。
- **Memory Materialization**：每个 schema 物化为表，属性为列，interaction round 为行，额外保留 order/time。
- **Memory Access Tools**：analytic tools 包含 LOOKUP、FILTER、COMPUTE、RANK；retrieval tools 包含 SEMANTICMATCH、EVENTLOCATE。
- **Joint Query Planning**：先用 hybrid metadata ranking 构造 planning context，再生成高层 plan；工具调用逐步实例化，后续参数可依赖前序结果。

### 计算与数据成本

- Benchmark 规模：MemEye 221 sessions / 848 rounds / 438 images / 742 QA pairs；MemGallery 240 sessions / 3,962 rounds / 1,003 images / 1,711 QA pairs。
- 实现：GPT-4.1-nano 与 GPT-5.4-mini 作为 answer/memory construction backbones；MiniLM-L6-v2 与 siglip2-base-patch16-384 做文本/图像表示。
- 查询预算：检索基线 top-10 memory units；ADAMM planner 最多 3 个 execution steps，共享 10 evidence units；结果平均 3 runs。

## 实验与证据

| 作者主张 | 对应证据 | 定位 | 我的判断 |
| --- | --- | --- | --- |
| analytic memory + retrieval memory 优于纯检索/纯记忆基线 | GPT-5.4-mini 下 ADAMM 在 MemEye EM/BLEU/Judge 为 65.5/35.9/60.7，MemGallery F1/BLEU/Judge 为 69.1/64.1/83.9，所有列最佳 | Table 3，p. 8 | 主结果支持强，且两个回答模型趋势一致 |
| 复杂分析型查询收益最大 | MemEye 的 Card Playlog、Personal Health 相对最强基线提升 18.8% 和 16.7%；MemGallery 的 Conflict Detection / Knowledge Resolution 提升 10.6% / 10.5% | Figure 3，p. 7 | 与方法动机一致，说明收益不是平均摊出来的 |
| analytic 和 retrieval 是互补能力 | 去掉 analytic memory 总体 -4.6%，Health -14.9%；去掉 retrieval memory 总体 -7.5%，Brand -9.9% | Figure 4，p. 8 | 消融很直接，支持双 memory 设计 |
| planner 需要知道当前 memory structure 且逐步执行 | 无 planning context 总体 -3.3%，Health/Brand -6.7/-6.3；非 progressive execution 在 Health/Brand 分别 -4.2/-3.2 | Figure 4，p. 8 | 支持工具调用不能一次性静态展开，后续参数依赖前序结果 |
| 结构化访问提升不是简单换更强回答模型 | GPT-4.1-nano 和 GPT-5.4-mini 两个 backbone 下均稳定领先 | Table 3，p. 8 | 有一定稳健性，但构建 memory 的 LLM 质量仍是系统变量 |

### 数据、基线与指标

- **数据集**：MemEye、MemGallery。
- **基线**：A-Mem、MemoryOS、M2A、MMA、MIRIX、MM-RAG、UniversalRAG。
- **指标**：MemEye 使用 EM、BLEU-1、LLM-Judge；MemGallery 使用 F1、BLEU-1、LLM-Judge。
- **预算/硬件**：每次查询最多 3 个计划步骤、10 evidence units；未报告端到端成本、延迟或构建时间。
- **消融与稳定性**：4 个组件消融，3 runs；未看到 schema extraction precision/recall 的人工审计。

## 批判性阅读

### 证据支持的结论

- 多模态长期记忆里的“相关”与“可计算”是两类不同需求，不能只靠 top-k retrieval 解决。
- 自动 schema induction 对重复记录型历史有明显价值，尤其是健康、卡牌日志、冲突检测、知识消解这类跨轮次查询。
- memory-aware progressive planning 是必要组件，因为查询执行常常需要先定位再过滤/计算。

### 尚未被充分支持的结论

- ADAMM 是否适合 schema 稀疏或概念变化很快的开放环境，还没有充分证据。
- 论文没有直接量化属性抽取错误、schema 错误和最终答案错误之间的传播路径。
- 工具集合仍由作者预定义，尚不能说明系统能自动扩展到新领域操作。

### 局限、风险与可能反证

- 作者明确指出，record fragment extraction 的错误/遗漏会传播到 schema induction、table construction 和 downstream computation。
- `LOOKUP/FILTER/COMPUTE/RANK` 等工具足以覆盖 benchmark，但真实用户可能需要更复杂的 domain-specific operations。
- LLM-Judge 是重要指标，但如果 judge 更偏好结构化解释，可能放大 ADAMM 的优势；需要人工评估或任务级精确答案补充。
- schema 物化会把历史固定到表结构中；如果某些属性语义漂移或单位不一致，计算可能看似确定但实际错误。

## 与已有知识的连接

- **基础论文**：MemGPT、MemoryBank、A-Mem、MIRIX、M2A、MM-RAG、UniversalRAG。
- **相近方法**：[[notes/papers/2026/07/23/PRO-LONG- Programmatic Memory Enables Long-Horizon Reasoning]] 让记忆以可执行程序形式服务长程推理；ADAMM 更偏多模态历史的 schema/table 化。
- **对照论文**：[[notes/papers/2026/07/30/MemSecBench- Tracking Agent Memory Poisoning from Persistence to Consequence and Repair]] 提醒 analytic memory 也需要污染检测和 selective repair。
- **与主题笔记的关系**：[[notes/topics/Agent能力形成与过程验证]]、[[notes/topics/结构化中间层与可验证执行]]。

## 复现计划

- **是否复现**：待定。
- **最小验证目标**：选 MemEye Personal Health 子集，比较 retrieval-only、manual schema、ADAMM-like schema induction 三臂，人工审计 extraction/schema/answer 三层错误。
- **所需资源**：公开 benchmark、图像/对话历史、LLM extractor、简单 SQLite/table executor、LLM judge 或人工标注。
- **成功标准**：在相同 evidence budget 下，analytic memory 对需要聚合/过滤的问题有稳定收益，同时报告错误传播比例。

## 待追踪问题

- [ ] ADAMM 是否公开代码和 induced schemas，便于审计 schema 质量？
- [ ] attribute-value extraction 的 precision/recall 如何人工评估？
- [ ] 如果引入 confidence-aware extraction，最终答案收益是否来自少量低置信记录过滤？
- [ ] 自生成新工具如何验证安全性和 determinism？
- [ ] analytic memory 与 memory poisoning/隐私删除请求如何兼容？

## 原文定位

- retrieval-analysis mismatch：Introduction、Figure 1，pp. 1–2。
- ADAMM 总览：Figure 2、Section 3.2，p. 4。
- 属性抽取与 schema induction：Sections 3.3.1–3.3.2、Eqs. (1)–(7)，pp. 3–5。
- memory materialization 与 retrieval memory：Sections 3.3.3–3.4，p. 5。
- access tools 与 progressive planning：Table 1、Section 3.5，p. 6。
- 实验设定与主结果：Tables 2–3、Sections 4.1–4.2，pp. 7–8。
- 消融：Figure 4、Section 4.3，p. 8。
- 作者局限：Limitations，p. 9。
