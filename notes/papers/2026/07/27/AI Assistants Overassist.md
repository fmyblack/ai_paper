---
type: paper
title: "AI Assistants Overassist"
aliases: []
authors: ["Verona Teo", "Raghav Jain", "Tobias Gerstenberg", "Max Kleiman-Weiner"]
year: 2026
venue: "arXiv"
paper_date: "2026-07-23"
date_added: "2026-07-27"
last_read: "2026-07-27"
topics: ["Agent", "安全、鲁棒性与治理", "可解释性"]
status: read
priority: 2
rating:
arxiv_id: "2607.21306"
doi: ""
paper_url: "https://arxiv.org/abs/2607.21306"
code_url: ""
pdf_path: "library/raw/2026/07/27/ai-assistants-overassist.pdf"
text_path: "library/text/2026/07/27/ai-assistants-overassist.txt"
sha256: "e5c0bbfe34a3dc9be5660339501bf9b2f11b9561a04aa7accb28078b3db1384d"
pages: 33
citation_key: ""
related: []
cssclasses:
  - paper-note
---

# AI Assistants Overassist

## 一句话结论

在 INT-BENCH 的 LLM-simulated student-teacher 任务中，LLM teacher 比人类更频繁、更早介入，并更常提供接近完整解法；这种介入能改善当前题目的成功率，却没有稳定提升单个相关新题的迁移。结果很适合作为“助教行为”的诊断基线，但还不是对真实学习者长期学习效果的因果证明。

## 三分钟筛选

- **问题**：AI 助手应在何时介入、给多少帮助、何时保持沉默，才能兼顾当前解题与长期学习，而不是替用户完成推理。
- **新意**：把帮助建模为 sequential intervention game，提出 INT-BENCH，测量频率、时机、即时 helpfulness、泛化 helpfulness，并和人类 teacher 对比。
- **核心证据**：Standard 条件 LLM 的介入率约 0.90、相对时机 τ_rel=0.18；人类为 0.74、0.74；LLM 更早、更常介入。Standard intervention 的即时净收益 H=0.20，但 related variant 的泛化 G 在三领域均接近 0（pp. 6–9）。
- **与我的关系**：它把 Agent 的“何时说话”从产品偏好变成可测量的策略问题，和安全、辅助式推理及用户赋能直接相关。
- **决定**：保留为 human-AI collaboration 评估基线；若做复现，优先替换 simulated student 为真实学习者或多轮长期任务。

## 问题设定

- **输入、输出与目标**：学生先独立解题，teacher 逐步看到 reasoning trace，选择 wait 或 intervene，并在最多一次介入时发送消息；随后比较原题答案和相关新题答案。
- **现有瓶颈**：多数工作只看“用了 AI 后答对没有”，没有分解介入发生的时间、内容泄漏量和跨题迁移。
- **关键假设**：LLM-generated variant 与原题共享细粒度 skill；judge 能可靠判断答案；LLM student 的 reasoning trace 可作为学习过程代理。

## 核心贡献

1. INT-BENCH sequential intervention framework：Standard 逐 50 字符增量观察，Oracle 一次性看到完整轨迹和 correctness verdict（pp. 3–4）。
2. 三域实验：DebugEval code debugging 500 题、MATH-500 500 题、brain teasers 500 题；每域 100 个验证过的 reference-variant pair 用于泛化。
3. 4 个 teacher model（GPT-5.2、Gemini 3 Flash、GPT-OSS-120B、DeepSeek-V3.2）和 50 名人类参与者的行为对比。

## 方法

### 直觉

对当前题目有用的提示不一定对下一题有用。论文把 intervention 拆成两个问题：teacher 是否应该打断，以及消息是否保留学生继续推理和迁移所需的空间。

### 形式化描述

对 baseline trace t=(t_1,…,t_T)，teacher 在前缀 t_1:k 上选择 wait/intervene。介入后即时 helpfulness 为：

H_i = 1[correct after] − 1[correct before]

对相关新题 q̃，generalization helpfulness 为带 context 相对 No-Context 的正确率差 G（Section 3.3–3.5，pp. 3–5）。

### 关键模块与训练流程

- 学生模型：Qwen2.5-7B-Instruct；teacher：GPT-5.2、Gemini 3 Flash、GPT-OSS-120B、DeepSeek-V3.2；judge：GPT-5.2。
- Standard teacher 每次只看到 50 字符增量；Oracle 看到完整 trace、答案和 correctness，再决定是否介入及位置。
- 三种 post-intervention：Standard-Continue、Oracle-Continue、Stop-and-Answer。
- variant 由 skill extraction、skill clustering、问题生成和 validation pipeline 产生，旨在保持技能而改变表面形式。

### 计算与数据成本

- 共 1,500 道原题；每个 teacher 每题运行 3 次；学生/teacher temperature 0.7，judge temperature 0。
- Human study 只使用 30 道 brain teaser，25 人 Standard、25 人 Oracle，每人 6 trials。
- 附录敏感性实验显示 50/300 字符及 sentence increment、Qwen3-32B/Llama-3.1-8B 学生、提示词变体不会改变“Standard 很早介入”的方向，但绝对位置随 increment size 变化（Appendix E，p. 24）。

## 实验与证据

| 作者主张 | 对应证据 | 定位 | 我的判断 |
| --- | --- | --- | --- |
| LLM 介入频繁且很早 | Standard ϕ=0.90、τ_rel=0.18；GPT-5.2/OSS-120B 在第二个 50 字符增量前就常介入 | Figure 2、Section 5.1，pp. 6–7 | 支持强；提示格式和 50-character mechanics 仍是行为诱因 |
| 有完整信息时更选择性 | Oracle ϕ=0.54、τ_rel=0.56；学生本来会答对时介入率低于 3% | Section 5.1，p. 7 | 支持“信息不完整导致过早介入”，也说明模型能利用 correctness |
| Standard 介入提高即时成功 | H=0.20；25.5% incorrect→correct，5.4% correct→incorrect；Oracle H=0.30 | Figure 3、Section 5.2，pp. 7–8 | 对当前题目有效，但不是学习增益 |
| 介入不可靠地提升泛化 | Problem-Context/Intervention-Context 在 math/code/brain 的 G 约 −0.04 到 +0.04 | Figure 4、Section 5.3，p. 8 | 支持短期 transfer 缺乏；单个 variant 不能代表长期学习 |
| LLM 与人类策略不同 | Brain teaser Standard：人类 ϕ=0.74、τ_rel=0.74；LLM ϕ=0.94、τ_rel=0.24 | Figure 5、Section 5.4，p. 9 | 有方向性证据；人类样本与任务较小 |
| LLM 泄漏更多解法 | LLM Standard 完整解法 14.2%、near-solution scaffold 45.1%；人类分别 5.4%、29.7% | Table 1，p. 8 | 内容分类有解释力，但人工标注规则和 30 题规模限制外推 |

### 数据、基线与指标

- **数据集**：DebugEval、MATH-500、Braingle brain teasers；每域 500 原题。
- **基线**：No-Context、Problem-Context、Intervention-Context；Standard/Oracle teacher；Stop-and-Answer。
- **指标**：intervention frequency ϕ、absolute/relative timing τ、immediate H、generalization G、solution leakage categories。
- **预算/硬件**：teacher 4 个、学生 Qwen2.5-7B；每题 3 runs；未披露完整 API 成本与 judge 误差传播。
- **消融与稳定性**：增量大小、学生模型、提示词变体附录；主实验跨三域，human 只在 brain teaser。

## 批判性阅读

### 证据支持的结论

- 在这个模拟的 sequential-monitoring 设定里，LLM 默认策略明显偏向“尽快说话”，并倾向给出高信息量、问题特定的帮助。
- Oracle 条件的更低介入率和更高即时 helpfulness，说明部分 overassist 来自 teacher 对不完整轨迹的不确定性。
- 附录中改变 increment、student model、prompt wording 后，早介入方向仍在，削弱了单一 Qwen2.5-7B 或单一 prompt 的解释。

### 尚未被充分支持的结论

- “不能促进学习”只由一个相关新题、一次 context-based evaluation 测量，无法代表 retention、motivation 或数周后的 transfer。
- LLM teacher 的解法泄漏是否真的损害真人学习没有直接测量；simulated student 不包含误解、认知负荷和情绪。
- GPT-5.2 同时作为 teacher/judge 的部分实验存在评测模型相关偏差风险。

### 局限、风险与可能反证

- 学生和 teacher 都是模型，学生可直接复制 context，不能等同于人类学习者。
- Human comparison 只有 30 道 brain teaser、50 人×6 trials；统计交互虽有 mixed models，但场景很窄。
- 50 字符逐步揭示会把“第一段就介入”与界面粒度绑定；附录说明相对时机变化，但不消除机制依赖。
- variant generation pipeline 的 skill 同构性由 LLM 产生和 validation，可能把泛化难度设计得偏简单或偏难。

## 与已有知识的连接

- **基础论文**：assistance dilemma、productive struggle、faded scaffolding。
- **相近方法**：empowerment-oriented assistants、simulated students、human-AI tutoring。
- **后续工作**：把 INT-BENCH 改成真实学生 longitudinal study；训练 intervention policy 直接优化 delayed transfer。
- **与主题笔记的关系**：[[notes/topics/跨视角监督、辅助信号与模型行为]]

## 复现计划

- **是否复现**：待定
- **最小验证目标**：在相同 student trace 上比较四种 teacher 的介入率/泄漏率，再用真实参与者完成原题和 3 个同技能变体。
- **所需资源**：INT-BENCH 数据生成脚本、固定 judge、人工标注 schema、伦理审批与参与者预算。
- **成功标准**：LLM Standard 的早介入和高泄漏在模型替换后仍成立，并且真实学习者的 delayed transfer 与 simulated result 方向一致。

## 待追踪问题

- [ ] 将 generalization 从单个 variant 扩展到多题、多轮和延迟测验后，Intervention-Context 是否仍无增益？
- [ ] 介入消息的最佳信息量是否呈倒 U 形，而不是越少越好？
- [ ] 是否能用 user state uncertainty、错误类型和可恢复性训练“何时保持沉默”？

## 原文定位

- INT-BENCH 设计：pp. 1–5，Figure 1、Sections 3.1–3.5。
- 主实验与数据：pp. 5–6，Section 4。
- 频率、即时 helpfulness、泛化：pp. 6–8，Figures 2–4、Sections 5.1–5.3。
- 人类比较与泄漏分类：pp. 7–10，Figure 5、Table 1、Section 5.4。
- 增量/学生模型/提示词敏感性：p. 24，Tables 8–10。
