---
type: paper
title: "What Makes Good Agentic Data? An ACE Lens on Data Generation for LLM Agents"
aliases: []
authors: ["Xingshan Zeng", "Zishan Xu", "Boju Zhang", "Yuzhou Wu", "Lingzhi Wang", "Jianghao Lin", "Liangyou Li", "Yasheng Wang", "Lifeng Shang", "Xin Jiang", "Weinan Zhang", "Yong Yu", "Qun Liu", "Weiwen Liu"]
year: 2026
venue: "arXiv"
paper_date: "2026-08-27"
date_added: "2026-08-28"
last_read: "2026-08-28"
topics: ["Agent", "数据生成", "强化学习", "评测"]
status: read
priority: 1
rating:
arxiv_id: "2608.27260"
doi: ""
paper_url: "https://arxiv.org/abs/2608.27260"
code_url: ""
pdf_path: "library/raw/2026/08/28/2608.27260v1.pdf"
text_path: "library/text/2026/08/28/2608.27260v1.txt"
sha256: "29a88532d9dff6ab5ecb9dcb4fe49a8ebd7f08a3ce78b4a4ad1d554bcd8a3006"
pages: 44
citation_key: ""
related: []
cssclasses:
  - paper-note
---

# What Makes Good Agentic Data? An ACE Lens on Data Generation for LLM Agents

## 一句话结论

ACE 是一篇把 Agent 数据生成重新定义为“受约束的分布设计”的综述与形式化框架：先用 Accuracy 把无效样本挡在门外，再按特定 learner 的 Complexity 和行为 Diversity 分配有效数据；它统一了术语，但没有提供一个已验证的单一生成器或通用评分器。

## 三分钟筛选

- **问题**：Agent 数据研究按 tool/API、coding、GUI、embodied 等领域分散，常把候选构造、验证、筛选和分配混在一起，难以比较。
- **新意**：用共同数据对象 `d=(E,q,τ,v)` 和 ACE 三维镜头统一跨领域生成机制与质量目标。
- **核心证据**：式(7) 的生成分解、式(8) 的 ACE 目标、Accuracy/Complexity/Diversity 三章的机制综述和局限分析。
- **与我的关系**：为 WikiSkill 的轨迹质量、技能演化数据和未来复现定义可检查的质量维度；也能约束 VLM/Agent benchmark 设计。
- **决定**：精读；作为方法论基线，不把它当作单一算法 benchmark。

## 问题设定

- **输入、输出与目标**：环境 `E`、任务信号 `q`、交互轨迹 `τ`、可选验证器/奖励接口 `v`；目标是在满足准确性接受率约束下，生成对指定 learner 有用、且非冗余的经验（§2–3，pp.5–11）。
- **现有瓶颈**：生成的任务可能不可执行，轨迹可能不符合状态转移，verifier 可能奖励捷径；即使有效数据也可能过易、过难或重复。
- **关键假设**：能定义某种 validity gate `A(d)`；能在声明的模型/工具/预算配置 `z` 下估计实例难度；能定义有意义的 coverage/redundancy 单位。

## 核心贡献

1. 共同对象 `d=(E,q,τ,v)`：把环境、任务、轨迹和成功信号的关系显式化（式(6)，p.6）。
2. 机制分类：按主要 anchor 区分 forward、reverse、structure-first 等生成范式，而不是按应用领域分类（Figure 3，p.9）。
3. ACE 非 checklist，而是非对称目标：Accuracy 定义可行域；Complexity 与 Diversity 只在可行域内优化（式(8)，p.11）。

## 方法

### 直觉

“难”和“新”不能拯救错误样本。先保证任务、环境、动作、观察和 verifier 彼此一致，再决定哪些有效样本值得学习。

### 形式化描述

常见生成顺序为 `p(E,q,τ)=p(E)p(q|E)p(τ|E,q)`（式(7)，p.9），但 task-first/trajectory-first 等顺序也可以。准确性判定为 `A(d)=V_E∧V_q∧V_τ∧V_v`，复杂度可用指定配置 `z` 下的失败概率 `C_z(d)=1-Pr[v(d,τ)=1|d,z]` 表示（式(9)–(10)，pp.12–16）。ACE 目标在 `Pr[A(d)=1]≥α` 下最大化有效样本的复杂度效用与 batch diversity（式(8)，p.11）。

### 关键模块与训练流程

Accuracy：schema/权限/状态转移/编译测试/模拟器 predicate/人工或模型审查；Complexity：结构组合、信息控制、环境与交互设计、完成条件、渐进变换、failure-driven calibration；Diversity：组合、探索、反事实扰动、coverage-guided balancing、周期性广泛探索（§4–6）。

### 计算与数据成本

论文是 survey/formulation，没有统一训练硬件或总成本。它明确指出成本随验证强度上升：规则检查 < 执行/仓库 setup/模拟 rollout < 多模型审查 < 人工检查（§4.4，p.15）。模型相对复杂度需要重复 rollout 估计，Diversity 还需要 coverage、entropy、joint-distribution 与 redundancy 统计（§6.4，pp.27–29）。

## 实验与证据

| 作者主张 | 对应证据 | 定位 | 我的判断 |
| --- | --- | --- | --- |
| Agent 数据不是“指令+回答” | `E,q,τ,v` 需要可行动环境、可行任务、状态一致轨迹和成功接口 | §2.3–2.4，pp.5–6 | 概念上清楚，适合作为数据审计 schema；不是实证定理 |
| Accuracy 必须是先决 gate | `A(d)` 为四项 validity 的合取；无样本通过 gate 时 utility=0 | §3.4、§4.1，pp.11–12 | 是规范性设计选择；真实 verifier 仍可能有 loophole/偏差 |
| 难度应相对 learner 校准 | `C_z(d)` 随模型、工具、scaffold、预算变化；有用样本位于 moving learnable band | §5.1，pp.16–17，Figure 6 | 比按 horizon/tool 数量定义难度更合理，但需要额外 rollout 成本 |
| 多样性应衡量行为覆盖 | coverage/normalized entropy 还需 joint distributions，且要去除 behaviorally redundant samples | §6.4，pp.27–29 | 重要；“数据量扩大”不能直接等于能力覆盖扩大 |

### 数据、基线与指标

- **数据集**：跨 tool-use、web/GUI、coding、embodied、social、scientific/formal 领域的代表性工作（Tables 1–3，pp.9、13、26–27）。
- **基线**：不是单一实验基线，而是 APIGen、ToolACE、OSWorld、AndroidWorld、SWE-rebench、ProcTHOR、SOTOPIA、FunSearch 等机制实例。
- **指标**：Accuracy gate/acceptance、learner-relative solve probability、coverage、normalized entropy、behavioral redundancy、held-out transfer。
- **预算/硬件**：各被综述工作异质；ACE 本身不报告统一硬件或成本。
- **消融与稳定性**：通过文献比较和 trade-off 分析，不是 ACE 框架自身的统一消融实验。

## 批判性阅读

### 证据支持的结论

- 执行验证比纯 plausibility judge 更接近轨迹正确性，但不能排除 verifier loophole、隐式约束违规和语义错误（§4.3–4.4，pp.14–16）。
- 结构长度、工具数、token 数都是解释变量，不是跨模型通用难度指标；同一任务在不同 `z` 下复杂度不同（§5.1–5.2，pp.16–18）。
- 表面改写会制造“名义多样性”；有价值的是环境状态、依赖关系、恢复路径和策略行为的覆盖（§6，pp.22–29）。

### 尚未被充分支持的结论

- ACE 还没有给出跨领域可直接计算的 `A(d)`、`g_z(C_z)` 和 `D(B_A)` 标准实现。
- “learnable band” 的阈值 `ρ` 与 utility 形式是 protocol-dependent，尚无统一校准方法。
- 综述中的跨工作趋势不能当作同一实验条件下的因果比较。

### 局限、风险与可能反证

- verifier bias：固定 verifier 会诱导“对检查器优化”，把真实能力变成可通过捷径。
- 生成、验证、修复闭环可能缩窄分布；过度 failure-driven 会过拟合当前模型的短期失败，导致遗忘和覆盖收缩（§6.3.5、§6.5）。
- 真实环境昂贵、危险且会漂移；LLM simulator 又可能保持局部连贯但错误的状态动力学（§4.4，p.15）。
- 反证路径：同一数据在独立 verifier、人工审计、held-out environment 和不同 learner 上比较；报告 validity、difficulty、coverage 与成本，而非单一 aggregate score。

## 与已有知识的连接

- **基础论文**：ReAct、ToolLLM、APIGen、OSWorld、FunSearch 等被综述的环境/轨迹生成工作。
- **相近方法**：WikiSkill、SkillRise、SkillZip；以及 AgentHPOBench/MetaSpace 中的过程级评测思想。
- **后续工作**：把 ACE 变成可执行 data card/schema、跨 verifier 审计、learner-aware sampler、coverage-controlled scaling law。
- **与主题笔记的关系**：[[notes/topics/Agent、世界模型与多模态数据]]；可补充“中间轨迹质量和数据分布设计”的统一语言。

## 复现计划

- **是否复现**：待定（更适合复现一个小型 ACE 审计器，而非整篇 survey）。
- **最小验证目标**：为一个 tool-use 或 coding 数据集记录 `(E,q,τ,v)`，实现四项 Accuracy gate、模型相对 solve-rate、category coverage 和语义去重。
- **所需资源**：可执行环境、独立 verifier、至少两个 learner 配置、轨迹日志和 held-out tasks。
- **成功标准**：能识别“表面不同但行为重复”“难度来自坏环境”“verifier 接受但任务未完成”三类反例。

## 待追踪问题

- [ ] 如何定义跨领域可比的行为单元，而不是依赖人工 taxonomy？
- [ ] 复杂度 frontier 移动时，如何同时保持 broad replay coverage？
- [ ] ACE 的 validity gate 如何与安全、成本、隐私和环境漂移联合优化？

## 原文定位

- Page / Section / Figure / Table / Equation：Figure 1 p.4；§2 pp.5–6；Figure 3 p.9；式(7) p.9；式(8) p.11；式(9) p.12；式(10) p.16；Figure 6 p.17；Figure 9 p.25；§6.4 pp.27–29；§7–8 pp.29–32。
