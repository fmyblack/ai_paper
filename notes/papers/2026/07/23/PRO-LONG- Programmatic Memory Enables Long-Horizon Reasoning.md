---
type: paper
title: "PRO-LONG: Programmatic Memory Enables Long-Horizon Reasoning"
aliases: []
authors: ["Alexis Fox", "Junlin Wang", "Paul Rosu", "Bhuwan Dhingra"]
year: 2026
venue: "arXiv"
paper_date: "2026-07-22"
date_added: "2026-07-23"
last_read: "2026-07-23"
topics: ["Agent", "长上下文与记忆", "推理与规划"]
status: read
priority: 1
rating: 4
arxiv_id: "2607.20064"
doi: ""
paper_url: "https://arxiv.org/abs/2607.20064"
code_url: "https://github.com/alexisfox7/PRO-LONG"
pdf_path: "library/raw/2026/07/23/2607.20064v1.pdf"
text_path: "library/text/2026/07/23/2607.20064v1.txt"
sha256: "d9c9a2e8755116912fe737e3f42a9cffaba6d28a1177a14bcc0eadf81333a0b2"
pages: 14
citation_key: ""
related:
  - "[[notes/papers/2026/07/22/OmniReasoner- Thinking with Long Audio-Video via Native Tool Use]]"
cssclasses:
  - paper-note
---

# PRO-LONG: Programmatic Memory Enables Long-Horizon Reasoning

## 一句话结论

PRO-LONG 证明了一个很实用但边界清楚的结论：在 ARC-AGI-3 这类历史可完整记录、规则可被代码归纳的交互任务中，“无损追加日志 + Agent 自己用 grep/Python 检索”比让模型维护摘要或手写笔记更可靠、也更省 token；它尚未证明这种记忆方案能泛化到非结构化、部分可观测或真实世界任务。

## 三分钟筛选

- **问题**：长程 Agent 的历史远超活动上下文时，write 阶段的摘要/筛选会永久丢掉“事后才显得重要”的细节，而把一切塞回上下文又昂贵且会产生 context rot。
- **新意**：把 memory 极简化为 append-all `logs.txt`，read 则完全交给 coding agent 的正则、shell 和 Python；不建向量库、不学习 memory policy、不预先压缩。
- **核心证据**：在 25 个 ARC-AGI-3 public games 上，三种 frontier model 相对同模型 no-log baseline 提升 15.7-21.0 个百分点；与强专用 harness 相近或更好，同时在匹配的 500-action 设置中少用 4.2-5.8 倍 billed tokens。
- **与我的关系**：它把“长上下文”改写成“模型当前访问什么、工具还能访问什么”，与主动感知、外部状态和 Agent 工具使用直接相关。
- **决定**：精读后保留为 Agent memory 的强工程基线；优先复核 released logs 和成本口径，不把单 benchmark 结果升级为一般长程智能。

## 问题设定

- **输入、输出与目标**：输入 ARC-AGI-3 的 64x64 ASCII board、可用动作和完整交互 log；Agent 输出短 action sequence，目标是在动作预算内推断隐藏规则并完成 6-10 个递进 level，按 Relative Human Action Efficiency 计分。
- **现有瓶颈**：活动上下文约 100K-1M tokens，而可访问历史可超过 10M tokens；摘要是有损 write，纯语义 retrieval 又未必适合精确 board/action regression。
- **关键假设**：环境输出可完整、结构化记录；历史事实是 ground truth；coding agent 能把检索问题转写成可执行程序；任务规律足以由过去 observation/action 推断。

## 核心贡献

1. 提出 programmatic memory：harness 无损记录每个 action、plan、score 和 board，Agent 在需要时自行编程读取。
2. 在 Codex 与 Claude Code 两种 agent framework、GPT-5.5 / Opus 4.6 / Fable 5 三个模型上验证，并统一重算公开 baseline 的 scoring。
3. 用 full-log truncation、tool ladder、workspace persistence 和逐游戏分析，把主要增益定位到“完整历史 + programmatic access”，而不是专用 prompt、subagent 或手写 notes。

## 方法

### 直觉

不要在写入时猜什么重要。把全部轨迹保存成不可变事件日志，等问题出现后再让 Agent 写代码定位 score transition、重放动作、归纳 transition function 或做 BFS。这样把模型有限的“访问上下文”与磁盘上的“可访问上下文”分开。

### 形式化描述

每个环境含若干 level，单 level 得分为 $S_{l,e}=\min((h_{l,e}/a_{l,e})^2,1.15)$；环境分数对后期 level 加权，再对 25 个环境平均（Eq. 1）。PRO-LONG 的 write 是向 `logs.txt` 追加 action header、score、plan、action 和 resulting board；read 是 `read/grep/sed/awk/Python` 等程序化操作。模型的 active context 不直接承载完整轨迹。

### 关键模块与训练流程

- 没有模型训练，也没有 learned retriever；这是纯 harness/context engineering。
- 默认每 game 最多 500 actions、每 turn 最多 20 actions，high reasoning effort；GPT 使用 Codex，Claude 使用 Claude Code。
- 每个 run、game 都新建 session/workspace，不跨游戏迁移信息；Codex 主要设置运行 5 次，Claude 运行 2 次。
- Baseline 包括同模型 no-log coding agent，以及 WorldModeler、Arcgentica、Schema 等公开专用 harness；作者用公开轨迹统一重算分数。

### 计算与数据成本

- Public benchmark 只有 25 个 game，但每个 game 最多 500 actions；Fable 5 的 headline 结果使用 2,000-action budget。
- GPT-5.5：PRO-LONG 41.2 pass@1，对 WorldModeler 45.1，但 billed token 少 5.8 倍；best@5 达 60.1，成本优势缩小到 1.2 倍。
- Claude Code：PRO-LONG 82.1 best@2，对 Schema 84.4 best@2，少 4.2 倍 billed tokens。
- Fable 5：2,000 actions 下 94.6 pass@1、97.4 best@2，总成本分别约 $1,500 / $1,750；单个 `bp35` game 就花 $298。
- billed token 按同模型输入价格折算并对 output/cache 加权（Eq. 2-3，Appendix A），适合做同模型相对比较，不是硬件级延迟或能耗。

## 实验与证据

| 作者主张 | 对应证据 | 定位 | 我的判断 |
| --- | --- | --- | --- |
| 极简 programmatic memory 显著优于 no-log | 三种模型提升 15.7-21.0pp；GPT-5.5 为 41.2 vs 24.0 | Figure 2，pp. 5-6 | 强同模型证据，但只在一个高度结构化 benchmark 上成立 |
| 完整历史而非短窗口带来收益 | GPT-5.5 best@5：full log 60.1、last-25 51.9、no-log 34.2 | Figure 3，p. 6 | 支持“fullness”重要；best@5 同时放大 compute 和 selection effect |
| 程序化工具层级越强，表现越好 | read 23.1，+grep 27.2，+Python 38.3，+write/edit 41.2 | Table 1，p. 7 | Python 是最大跃升，说明贡献更像可执行分析而非存储本身 |
| Agent-authored workspace memory 不是主要来源 | 清空 workspace：PRO-LONG 41.2→40.7；no-log 24.0→19.9 | Table 2，p. 7 | 很好的干预；但 cleared 条件只有 n=2，区间较宽 |
| 相近性能下 token 成本更低 | GPT/Claude 对强 harness 少 5.8x/4.2x billed tokens | Figure 2，pp. 5-6；Appendix A，p. 12 | 成本方向可信，但 baseline 的选择过程、replicate 和保留日志并不完全对称 |

### 数据、基线与指标

- **数据集**：ARC-AGI-3 public set，25 个未知规则交互 game，每个 6-10 个 level。
- **基线**：同模型 no-log coding agent；WorldModeler（GPT-5.5）、Arcgentica（Opus 4.6）、Schema（Opus 4.8 / Fable 5）。
- **指标**：RHAE-based ARC score、pass@1、best@k、bootstrap 95% CI、billed tokens / game 与美元折算成本。
- **预算/硬件**：主要 500 actions/game；Codex n=5、Claude n=2；没有自训模型。API/推理硬件未披露，获 ARC Prize credits 支持。
- **消融与稳定性**：full/last-25/no-log、tool ladder、workspace persistence、逐 game min-max；作者明确报告 run variance，但部分 prior baseline 没有 replicate 或选择流程。

## 批判性阅读

### 证据支持的结论

- 对结构化、可完整记录的长程交互，append-only log 加程序检索是比只靠活动上下文或手写 notes 更强的 baseline。
- 编程分析能力比单纯搜索更关键：从 grep 到 Python 的提升远大于从 read 到 grep。
- 对同模型、相近 score 的公开 harness，PRO-LONG 的 billed-token 效率明显更高。

### 尚未被充分支持的结论

- 没有证据表明它适用于非结构化网页、长文档、开放桌面、真实机器人或 history 本身可能错误的任务。
- 没有与 learned retrieval、semantic memory、lossy summary 在严格同 prompt/tool/model 下全面比较。
- “long-horizon reasoning”与“更方便地回放结构化状态”仍纠缠；ARC-AGI-3 不能单独证明一般长程规划能力。

### 局限、风险与可能反证

- 公开 game 可能被后发布模型间接污染；作者承认测试的两个模型晚于 benchmark 发布。
- best@k 从 41.2 拉到 60.1，说明单次可靠性仍有限；生产 Agent 更关心 pass@1 和失败恢复，而不是多次取最好。
- 强 baseline 的 replicate、selection procedure 和完整成本日志不对称；Schema 只发布保留的最佳 runs，成本比较只能给下界。
- 无损日志会线性增长；论文展示 320K+ lines 可用，但未测百万级长期任务的磁盘、检索延迟和 tool-output context cost。
- 每步都记录的是环境 ground truth；现实 Agent 的 observation、网页内容和 tool output 可能噪声或相互冲突，无损保存也会无损保存错误。

## 与已有知识的连接

- **基础论文**：MemGPT、Mem0、ReasoningBank、Recursive Language Models、ARC-AGI-3。
- **相近方法**：WorldModeler、Schema harness、Arcgentica，以及 coding agent 的长上下文程序化处理。
- **后续工作**：在同模型下比较 append-all、分层摘要、向量检索与 hybrid memory；把检索/工具成本纳入在线预算；测试 observation 噪声。
- **与主题笔记的关系**：[[notes/topics/交互式世界模型与主动感知]]；它提供“长期状态不必进入 active context，只需保持可程序访问”的机制。

## 复现计划

- **是否复现**：是，优先做 log-level 与小样本 inference 复核，不重复完整 best@5。
- **最小验证目标**：选 5 个 history-dependent games，在同一模型上比较 full log、last-25、结构化 summary 和 grep-only，记录 pass@1 与 token/tool cost。
- **所需资源**：公开代码与 logs、ARC-AGI-3 engine 0.9.7、Codex/Claude Code 类 agent、受控 API 预算。
- **成功标准**：full log 在 history-dependent 子集稳定优于 summary/last-25，并能把增益归因到成功检索而非更多调用或 prompt 差异。

## 待追踪问题

- [ ] 在非 grid、非确定性任务上，append-all log 是否仍优于针对性摘要？
- [ ] 把检索动作和 tool output token 也计入成本后，4.2-5.8x 优势剩多少？
- [ ] 若 observation 有噪声，Agent 是否会用 code 交叉验证，还是把旧错误固化成“事实”？
- [ ] full-log 对 pass@1 的收益能否通过训练/更好 harness 缩小与 best@k 的差距？

## 原文定位

- 问题与 programmatic memory：Section 1、Figure 1，pp. 1-3。
- 环境、RHAE 与协议：Section 2.1、Eq. (1)，pp. 3-4。
- Agent/harness 定义：Section 2.2，pp. 4-5；完整 prompt 见 Appendix B，pp. 12-14。
- 主性能与成本：Figure 2、Section 3.1，pp. 5-6。
- full log / last-25 / no-log：Figure 3，p. 6。
- 工具与 workspace 消融：Table 1-3、Figure 4，pp. 7-8。
- 成本折算：Appendix A、Eq. (2)-(3)，p. 12。
- 作者承认的 benchmark 时序与 run variance：Section 5，p. 9。
