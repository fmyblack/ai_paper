---
type: paper
title: "FinPerMA: A Theory-Informed, Event-Grounded Personalized-Memory Benchmark for LLM Agents"
aliases: ["FinPerMA"]
authors: ["Ben Wang", "Kang Zhou", "Lifan Guo", "Feng Chen", "Chi Zhang"]
year: 2026
venue: "arXiv"
paper_date: "2026-08-04"
date_added: "2026-08-06"
last_read: "2026-08-06"
topics: ["长上下文与记忆", "个性化记忆", "Agent", "金融场景"]
status: read
priority: 2
rating:
arxiv_id: "2608.04095"
doi: ""
paper_url: "https://arxiv.org/abs/2608.04095"
code_url: ""
pdf_path: ""
text_path: ""
sha256: ""
pages: 9
citation_key: ""
related:
  - "[[notes/papers/2026/07/23/PRO-LONG- Programmatic Memory Enables Long-Horizon Reasoning]]"
  - "[[notes/papers/2026/07/30/MemSecBench- Tracking Agent Memory Poisoning from Persistence to Consequence and Repair]]"
cssclasses:
  - paper-note
---

# FinPerMA: A Theory-Informed, Event-Grounded Personalized-Memory Benchmark for LLM Agents

## 一句话结论

它不是单纯测“记不记得用户说过什么”，而是测 Agent 能否在长期财经事件里维持并更新个性化画像。最有价值的结论是：堆满全文上下文并不等于好记忆，检索式记忆往往比 summary/profile 更划算；真正难的是 shock 之后的偏好更新。

## 三分钟筛选

- **问题**：LLM agents 的 personalized memory 是否真的能保留用户偏好、风险态度和事件后更新，而不只是复述历史事实？
- **新意**：用 behavioral investment theory 约束 persona 与事件影响，构造 97 个真实金融事件、276 个 persona、2994 道题，并把评测拆到多个 checkpoint 和 post-shock 场景。
- **核心证据**：7 个 backbone、7 类 memory 配置里，full-context 很快饱和在约 0.47 overall accuracy；retrieval 能以远少于 full-context 的 token 追回大约 88% 的差距；summary 更保事实、却丢偏好与 bias 信号。
- **与我的关系**：这篇直接落在 Agent memory 的“更新”而不是“召回”，和 `PRO-LONG`、`MemSecBench` 形成很好的互补。
- **决定**：已精读。

## 问题设定

- **输入、输出与目标**：输入是带时间戳的金融事件、persona 画像和历史对话/状态；输出是对个体偏好、行为倾向和事件后调整的准确响应。
- **现有瓶颈**：大多数 memory benchmark 只测静态 recall 或一次性摘要，无法区分“记住事实”与“更新偏好”。
- **关键假设**：理论约束的合成 persona + 真实事件冲击，足以近似长期个性化记忆的关键结构。

## 核心贡献

1. 构造了一个事件驱动的 personalized-memory benchmark，覆盖 276 personas、97 真实金融事件和 2994 个问题。
2. 把记忆能力分解到多个 checkpoint，尤其加入 post-shock 评测，逼迫模型回答“更新后现在该怎么想”。
3. 对 full-context、summary、retrieval、structured memory 等配置做横向比较，明确区分 factual recall 和 preference retention。

## 方法

### 直觉

作者把长期金融记忆看成“用户状态在事件序列上的演化”，不是一份固定档案。若模型只会记事实、不懂冲击后如何改写偏好，它在真实个性化任务里就会过度自信。

### 形式化描述

- 先根据 behavioral investment theory 生成/筛选 persona，并把 persona 放进稳定的金融与心理特征空间。
- 再用真实金融事件构造时间线，让事件在不同 checkpoint 上对 persona 产生不同影响。
- 最后围绕同一 persona 的不同时间点自动生成多类问题，覆盖事实、偏好、更新和偏差识别。

### 关键模块与训练流程

- **Persona 生成**：276 个 persona，强调金融风险偏好、心理类型与事件敏感性。
- **事件时间线**：97 个真实金融事件，带日期与冲击方向。
- **Impact model**：Figure 1 的三层结构是规则约束 + LLM 叙述 + 自动验证；核心不是自由生成，而是让事件影响保持理论一致性和时序一致性。
- **Question design**：每个 persona 在多个 checkpoint 上生成问题，合计 2994 题，其中 2494 道 MCQ、500 道 open-ended。
- **评测对象**：7 个 frontier LLM × up to 7 种 memory 配置。

### 计算与数据成本

- 论文更像 benchmark paper，不是大规模训练 paper。
- 成本主要在 persona/event 生成、质检和多 checkpoint 评测，而不是模型训练。
- 这意味着它适合做系统比较，但不适合直接外推成真实用户画像服务的端到端成本。

## 实验与证据

| 作者主张 | 对应证据 | 定位 | 我的判断 |
| --- | --- | --- | --- |
| 个性化记忆要看动态更新，不只是静态回忆 | 2994 questions / 276 personas / 97 events，且按多个 checkpoint 评测 | Abstract, Section 2, pp. 1-4 | 方向正确 |
| full-context 不是万能解 | full-context 在总体 accuracy 上很快饱和，约到 0.47 左右 | Table 1, pp. 5-6 | 很实用的反直觉结论 |
| retrieval 比堆上下文更省也更强 | retrieval 以约 1.4k token 对比 full-context 约 12.8k token，追回约 88% 的差距 | Table 1, pp. 5-6 | 最强结论之一 |
| summary 保住事实但会丢偏好信号 | factual recall 接近，但 preference / bias 类指标掉得更明显 | Table 2, Figure 4, p. 6 | 支持“记忆压缩会损人格信号” |
| shock 后的更新比平时更难 | post-shock gap 明显扩大（约 8 pp -> 13 pp） | Figure 5, p. 6 | 很关键，说明更新是核心难点 |
| zero-memory 和单信号过拟合是主要失误模式 | top error modes 包括 defaulting to no-memory、single-signal over-inference、temporal misalignment | Figure 6, p. 6 | 诊断很有价值 |

### 数据、基线与指标

- **数据集**：97 真实金融事件，276 personas，4 个 checkpoint，2994 questions。
- **基线**：full-context、summary、retrieval、structured memory / profile 类配置。
- **指标**：overall accuracy、MCQ accuracy、open-ended quality、checkpoint gap、post-shock sensitivity。
- **预算/硬件**：主要是推理和生成成本，论文没有把它包装成训练大工程。
- **消融与稳定性**：对 memory 配置和 checkpoint 做了系统对照，但仍缺多 seed 的强统计报告。

## 批判性阅读

### 证据支持的结论

- 检索式 memory 在个性化场景里往往比纯 summary 更值得信任。
- 记忆 benchmark 如果不含 post-shock，就很容易高估模型的个性化能力。
- 事实记忆与偏好记忆不是一回事，必须分开测。

### 尚未被充分支持的结论

- 理论约束的合成 persona 是否真的覆盖真实用户画像的复杂性。
- 金融场景下得到的 memory 规律，能否迁移到医疗、教育或消费助手。

### 局限、风险与可能反证

- 合成 benchmark 仍然可能偏向可规则化、可枚举的偏好变化。
- 题目与事件由模型/规则共同生成，可能存在自洽但不够多样的风险。
- 论文主要比较 memory 形态，没有直接验证长期在线交互中的用户满意度。

## 与已有知识的连接

- **基础论文**：`PRO-LONG`、`MemSecBench`、动态用户画像与 personalized response 类 benchmark。
- **相近方法**：summary memory、retrieval memory、profile memory、agentic memory backend。
- **后续工作**：把 post-shock 评测推广到更一般的 agent memory / user model 更新任务。
- **与主题笔记的关系**：[[notes/topics/Agent能力形成与过程验证]]。

## 复现计划

- **是否复现**：待定
- **最小验证目标**：在一个开源模型上重跑小规模 persona/event 子集，确认 retrieval > summary > no-memory 的排序和 post-shock gap。
- **所需资源**：生成脚本、事件库、一个可控的 LLM、少量标注检查。
- **成功标准**：定性排序与 post-shock 退化方向一致，且主要 error mode 可重现。

## 待追踪问题

- [ ] 公开代码是否包含完整 persona 生成与 event impact 规则？
- [ ] retrieval 优势是不是主要来自 token 预算，而不是 memory 结构本身？
- [ ] 如果换成非金融任务，post-shock gap 还会不会是最强信号？

## 原文定位

- Abstract, p. 1
- Benchmark construction, Sections 2.1-2.4, pp. 2-4
- Main comparison, Table 1, pp. 5-6
- Memory-form ablation and error analysis, Table 2 / Figure 4 / Figure 6, p. 6
- Limitations, p. 7

