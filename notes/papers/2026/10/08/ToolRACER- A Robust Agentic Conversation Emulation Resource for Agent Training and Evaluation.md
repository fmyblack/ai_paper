---
type: paper
title: "ToolRACER: A Robust Agentic Conversation Emulation Resource for Agent Training and Evaluation"
aliases: [ToolRACER]
authors: ["Arkajyoti Chakraborty", "Aryan Tayal", "Ishika Agarwal", "Tanner Sorensen", "Justin Chiu", "Alessandro Di Bari", "Neha Gupta", "Andreas Stolcke"]
year: 2026
venue: arXiv
paper_date: "2026-10-06"
date_added: "2026-10-08"
last_read: "2026-10-08"
topics: ["Agent", "数据生成", "Benchmark 与评估方法"]
status: read
priority: 1
rating:
arxiv_id: "2610.09163"
arxiv_version: v1
doi: "10.48550/arXiv.2610.09163"
paper_url: "https://arxiv.org/abs/2610.09163"
code_url: ""
pdf_path: "library/raw/2026/10/08/2610.09163v1.pdf"
text_path: "library/text/2026/10/08/2610.09163v1.txt"
sha256: "b377232d3580f1f5852559603cd40b76b3feb4bb77b327745e54b9d0154b7c8c"
pages: 21
citation_key: ""
related:
  - "[[notes/topics/Agent能力形成与过程验证]]"
  - "[[notes/papers/2026/08/28/What Makes Good Agentic Data- An ACE Lens on Data Generation for LLM Agents]]"
cssclasses: [paper-note]
---

# ToolRACER: A Robust Agentic Conversation Emulation Resource for Agent Training and Evaluation

## 一句话结论

ToolRACER 把目标改变、逐步披露约束和不可完成请求纳入多轮工具调用训练，改善小模型的部分任务表现；它验证了这类数据的价值，但没有证明长程 Agent 的整体可靠性，部分过程指标反而下降。

**我的判断**：值得借鉴的是 scenario contract 和失败后重新模拟的数据生成流程。不能把 LLM 模拟的工具结果当成真实后端执行证据，也不能只凭最终成功率宣布鲁棒性提高。

> 阅读范围：arXiv 2610.09163v1，PDF 21 页，正文及附录 A–E；页码为 PDF 页序。核对表 3–6 和模拟提示词。已归档原始 PDF 与逐页文本；未训练模型、未复现分数。论文宣称发布资源，但本轮未确认可用的官方数据/代码链接。

## 问题与方法

普通合成轨迹常假定用户目标清晰、工具正常、请求一定可完成。实际对话中，用户会晚些才给约束、改主意，后端也会失败。作者把这些变化提前写入数据分布，而不是只让模型学习一条理想成功路径（§1–3，pp.1–7）。

场景输入包含任务目标、硬约束、软偏好、初始环境、成功条件与工具 schema。assistant、user、tool 三个 LLM 角色按各自可见历史交互；**tool 角色生成模拟观察，不是调用一个真实、确定性的服务后端**（§3.2.2，p.5；附录 B 图 3，p.13）。

| 情境 | 设计含义 | 应学会的行为 |
| --- | --- | --- |
| Happy | 信息充分且可完成 | 正确规划与调用 |
| Unhappy | 仍可完成，但信息不全、约束迟到、目标改变或用户不满 | 追问、更新计划、纠错 |
| Impossible | 工具故障、无结果或政策/资源约束导致无法完成 | 解释原因、提出替代，避免虚构完成 |

生成后检查 syntax/schema、faithfulness、role confusion 和 task success；失败原因转成 hints，最多重试两次，仍失败则丢弃（§3.2.3–3.2.4，pp.5–6）。这里的 faithfulness 和 success 仍含 LLM 判断，需要与后端状态核验区分。

作者得到 5,643 条对话：训练 3,762，测试 1,881；六领域共 72 个工具、55 种 persona。训练集 Happy/Unhappy/Impossible 分别为 1,259/1,304/1,199，约三分之二为后两类（表 1，p.6；§3.1）。这是对话条数，不是 token 数。

## 训练实际改变了什么

每段对话按 assistant 响应切开，用完整历史预测下一条 assistant 文本或动作。主要实验是 Qwen3-4B-Instruct-2507 的 LoRA SFT，rank 32、学习率 1e-4、batch 32；另测 Qwen2.5-32B 的 ACEBench。没有提出新的 RL 算法（§4.1，p.7）。

APIGen-MT 对照有 5,000 条轨迹，ToolRACER 有 3,762 条。数据条数接近不能保证训练 token、更新步数或难度相等；完整资源成本和重复实验置信区间不足以支撑严格性价比排序。

## 实验证据与反例

### 外部任务成功率

表 3（p.8），同一 Qwen3-4B 主实验，百分比；τ² macro 是 airline 与 retail 的均值。

| 数据 | BFCL non-live | τ² airline | τ² retail | τ² macro |
| --- | ---: | ---: | ---: | ---: |
| Base | 89.83 | 24.0 | 40.4 | 32.20 |
| APIGen-MT | 90.83 | 30.0 | 43.9 | 36.95 |
| ToolRACER | 91.00 | 34.4 | 44.0 | 39.20 |
| APIGen-MT + ToolRACER | 90.50 | 30.0 | 52.5 | 41.25 |

ToolRACER 单独训练较 base 的 τ² macro 提高 **7.0 个百分点**；混合训练提高 9.05 个百分点。**52.5% 仅是混合模型的 retail 成功率，不能称为总体成功率。** 混合数据提高 retail，却不如单独 ToolRACER 的 airline 表现。

Impossible-only 的 BFCL irrelevance/relevance 为 95.5/100，但 τ² macro 仅 34.45；Happy+Impossible 的 macro 30.8，低于 base 32.2（表 3）。因此拒绝无效请求、一般工具能力和端到端完成率是不同目标，数据组合也不是越多越好。表中的 † 外部模型行使用不同来源/协议，不适合直接证明公平优胜。

### 域内改善并不等于在线交互改善

域内评估用参考历史逐轮预测，即 teacher-forced turn-level 测试。ToolRACER 的 Happy 参数 F1 从 43.2 提高到 67.2，Impossible action recall 从 68.6 到 76.0（表 4，p.9）。这说明在给定正确历史下更会生成下一步，不能自动推导实际 rollout 中的错误不会累积。

ACEBench 50 个任务的过程指标出现反向变化（表 5，p.9）：

| 模型 | End Accuracy：base → ToolRACER | Process Accuracy：base → ToolRACER |
| --- | ---: | ---: |
| Qwen3-4B | 8.4 → 10.0 | 29.2 → 19.0 |
| Qwen2.5-32B | 19.2 → 25.0 | 38.3 → 33.1 |

终点成功提高，但过程准确率下降 10.2/5.2 个百分点。作者也承认超过六轮的长程交互仍有缺口。不能仅看终点而忽略多余调用、错误尝试和纠错成本。

### 数据生成本身的通过率

初始 multi-agent 模拟整体有效率为 26.3%；失败轨迹进入 refinement 后，恢复率为 65.4%（附录 A 表 6，p.12）。**65.4% 的分母是失败轨迹，不是所有生成轨迹，不能作为最终总体有效率。** 丢弃失败样本也可能使数据偏向 judge 能认可的情境。

## 可信范围与开放问题

**作者证据支持**：加入困难但可完成、以及不可完成的场景能提升部分外部任务成功率；分情境训练产生不同能力偏好。

**我的推断**：其最实用的贡献是把“合理停止/拒绝”和“继续完成”都写入训练目标，并让约束变化成为可控变量。若用于生产，工具模拟应尽量换成真实状态机，语义 judge 用于补充检查。

**尚未回答**：

- assistant/user/tool/judge 的错误是否相互相关，是否存在共同偏差？
- train/test 的任务模板、persona 和近重复轨迹隔离到什么程度？
- 在等 token、等更新次数、等难度条件下，Unhappy/Impossible 的增益还剩多少？
- 无效拒绝率、误拒绝可完成请求、成本与错误副作用能否同时改善？
- 混合训练的增益是否跨 seed 稳定？

## 与已有阅读连接

[[notes/papers/2026/08/28/What Makes Good Agentic Data- An ACE Lens on Data Generation for LLM Agents]] 把数据写成 `(E,q,τ,v)`，先检查 Accuracy，再谈 Complexity/Diversity。ToolRACER 是这个框架的具体实例，但它的 `E` 与 `v` 大量依赖模拟和语义判断；约束丰富度不能代替环境真实性。

主题综合：[[notes/topics/Agent能力形成与过程验证#2026-10-08 补充：四种反馈及其可信边界]]。

## 最小后续验证

- [ ] 做 30 个目标变化、30 个不可完成请求的确定性工具状态机；检查模拟观察与真实状态一致率。
- [ ] 等 token 训练 Happy-only 与加入 Unhappy/Impossible 两组，同时报告任务成功、过程准确、误拒绝和预算。
- [ ] 对 judge 接受/拒绝样本做独立复核，保留被丢弃轨迹而非只分析最终数据。

以上是计划，尚未执行。统一实验边界见 [[notes/reproductions/四篇Agent反馈论文的最小验证计划]]。
