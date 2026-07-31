---
type: paper
title: "MemSecBench: Tracking Agent Memory Poisoning from Persistence to Consequence and Repair"
aliases: []
authors: ["Xuanze Chen", "Xukang Xie", "Wentao Fu", "Jiajun Zhou", "Shanqing Yu", "Qi Xuan"]
year: 2026
venue: "arXiv"
paper_date: "2026-07-29"
date_added: "2026-07-30"
last_read: "2026-07-30"
topics: ["Agent", "长上下文与记忆", "安全、鲁棒性与治理", "Benchmark 与评估方法"]
status: read
priority: 1
rating: 4
arxiv_id: "2607.27080"
doi: ""
paper_url: "https://arxiv.org/abs/2607.27080"
code_url: ""
pdf_path: "library/raw/2026/07/30/memsecbench.pdf"
text_path: "library/text/2026/07/30/memsecbench.txt"
sha256: "a596c1a913fff9ccd83b0b9844e49d9629cfd339e28a058b8e575abd774c14ab"
pages: 28
citation_key: "chen2026memsecbench"
related:
  - "[[notes/papers/2026/07/27/AI Assistants Overassist]]"
  - "[[notes/papers/2026/07/27/Emergent Misalignment Recruits a Pre-existing Persona Subspace]]"
cssclasses:
  - paper-note
---

# MemSecBench: Tracking Agent Memory Poisoning from Persistence to Consequence and Repair

## 一句话结论

MemSecBench 的价值不在于再报一个“记忆会中毒”的攻击率，而在于把同一条恶意语义串成 Write→Execute→Forget 生命周期，并用证据门控区分“写进去了”“被召回并采纳”“真的造成外部后果”“修掉且保留良性记忆”。在 24 个配置的宏平均中，W2 持久化 84.2%、E1 召回 76.1%，最大跌落在 E2 adoption（53.7%），修复侧最大瓶颈是 F2 benign preservation（62.5%）；因此“能删除恶意项”不等于安全恢复。

## 三分钟筛选

- **问题**：现有 memory-security benchmark 往往只测写入、召回或后果之一，不能把恶意语义的传播和选择性修复放在同一条可审计链上。
- **新意**：310 个 case、48 个真实上下文、7 个检查点（W1/W2/E1/E2/E3/F1/F2），在 2 个 harness × 4 个 memory backend × 3 个 LLM backend 的固定配置矩阵中配对比较。
- **核心证据**：摘要与表 2 的 24 配置明细、图 4 的宏平均生命周期、图 5 的相对 Native 对照、附录 E 的证据规则与表 7 的人工一致性（原文第 1、6–7、23 页）。
- **与我的关系**：它是 [[notes/topics/Agent能力形成与过程验证]] 中“记忆生命周期安全”分支，也为 [[notes/papers/2026/07/30/SkillRise- Agentic Reinforcement Learning for Cross-Task Skill Evolution]] 的技能文档提供了安全反例：可迁移的记忆同时也是攻击面。
- **决定**：已精读；值得复现 benchmark loader 和小规模 backend 对照，尤其关注 F1/F2 的语义评估。

## 问题设定

- **输入、输出与目标**：每个 case 是 `T=(ρ,xW,xE,xF,ℓ)`：干净资源 `ρ`、Write/Execute/Forget 三阶段任务、隐藏的 W2 目标语义与 E3 consequence contract。输出是七个 checkpoint 的布尔/证据 verdict 和配置级指标（方法部分，第 3–5 页）。
- **现有瓶颈**：只验证 W1 或 W2 不能证明攻击完成；只有 agent 自述、tool call 或计划也不能证明 Externalization。修复如果清空整个 backend，可能通过 F1 却破坏良性记忆 F2。
- **关键假设**：攻击内容通过受支持的 Carrier 进入正常 memory interface；Execute 和 Forget 从相同的 verified post-Write 状态独立分支；任务后果可绑定到可检查的 service record/ workspace export。

## 核心贡献

1. 发布 310 个 Write–Execute–Forget lifecycle cases，追踪同一恶意语义从 persistence 到 consequence 和 selective repair。
2. 设计在固定 harness、LLM、初始内容和证据协议下比较 memory backend 的统一评估框架。
3. 通过多配置结果说明 memory safety 不是单一模型或 backend 的属性，而是完整 agent configuration 和状态转移的属性（摘要；结论，第 7 页）。

## 方法

### 直觉

把“攻击成功”拆成一条有依赖关系的链：W1 写入操作、W2 恶意语义持久化、E1 被召回、E2 改变代理决策、E3 落成外部后果。Forget 另从同一 poisoned snapshot 分支，要求 F1 去掉恶意操作语义、F2 保留每一条必须保留的 benign memory。

### 形式化描述

- 配置 `Π=(H,B,L)`，其中 `H` 是 agent harness、`B` 是 memory stack、`L` 是 served LLM；judge model 不属于被测配置（威胁模型，第 3 页）。
- 宏平均指标：MPSR（W2 持久化）、MESR（条件于成功写入的 E2/E3 相关指标）、E2E-ASR（全 Write–Execute 链）、SRSR（条件于成功 poisoning 的 F1∧F2）。作者明确对全 310 case 的指标和条件指标分别处理，缺失分母不当作失败（第 5 页）。
- 每个 checkpoint 使用 admissible evidence pack；W1 为 deterministic check，其余由 checkpoint-specific judge（DeepSeek-V4-Pro）并经 programmatic gates 校验（第 4–5 页、附录 E）。

### 关键模块与评估流程

1. **Case construction**：按 Primary Failure Mode、Risk、Carrier、Memory Type 四轴构造，作者用 GPT-5.5 辅助生成/修订，人工 gate 审批；agent 可见材料与 evaluator-only rubric 分离（第 3–4 页、附录 A）。
2. **Runtime**：隔离容器初始化干净 memory `M0`；同一 case 先执行 Write，只有 W1/W2 通过才从 `MW` 分支 Execute 和 Forget；每个配置–case slot 只 finalized 一次（第 4–5 页）。
3. **Evidence adjudication**：E1 只能引用实际 recall event；E2 只能看 recall 后的 reasoning/plan/tool use；E3 必须有任务范围的最终 artifact；F1/F2 只能看 backend before/after snapshot，不接受 delete call 或 agent claim 作为证据（附录 E.2–E.5，第 17–23 页）。

### 计算与数据成本

- 310 cases，跨 Code and Science（113）、Daily Life（107）、Office Work（90）三个领域、48 个 contexts，每个 context 6–10 cases（附录 A.4，第 11 页）。
- 24 配置：OpenClaw/Hermes × Native/Mem0/Mem0-Graph/A-MEM × DeepSeek-V4-Pro/MiniMax-M3/GPT-5.5；每配置覆盖全部 310 cases（表 2，第 6 页）。
- 需要隔离容器、四类 memory backend、三个 LLM service、外部 mock service 和 judge model；论文未提供一键公开 repo，复现基础设施成本高。

## 实验与证据

| 作者主张 | 对应证据 | 定位 | 我的判断 |
| --- | --- | --- | --- |
| 持久化和召回不是主要防线 | 宏平均 W1 91.1→W2 84.2→E1 76.1，只有少量恶意语义在早期被过滤 | 图 4，第 6 页 | 支持；但宏平均是配置等权，未展示按 domain/attack axis 加权后的总体风险。 |
| Adoption 是攻击完成的关键瓶颈 | E2 从 76.1% 降到 53.7%，E2E 仅进一步到 50.3% | 图 4，第 6 页 | 支持；说明被召回不等于代理真正按恶意语义行动。 |
| 选择性修复的主要难点是良性保留 | F1 86.3%、F2 62.5%、SRSR 56.1%；F1 与联合 SRSR 相差 30.2pp | 图 4，第 6 页 | 强支持；清空 backend 是不合格的恢复策略。 |
| backend 没有统一安全排序 | OpenClaw/DeepSeek：Native→A-MEM 的 E2E 仅 59.0→56.5%，SRSR 46.3→87.6%；OpenClaw/GPT-5.5：Mem0-Graph E2E 57.1→41.0%，SRSR 87.5→86.7% | Finding 3、表 2/图 5，第 6–7 页 | 支持配置依赖；不能把某个 backend 的单点结果推广成普遍排名。 |
| judge 结果具备一定人工一致性 | 500 条 run records；与两位标注者匹配 90.60%（453/500）和 91.80%（459/500） | 表 7，附录 E.6，第 23 页 | 支持评估协议的可用性，但不是独立 benchmark ground truth；judge 偏差仍可能系统性存在。 |

### 数据、基线与指标

- **数据集**：310 linked lifecycle cases、48 contexts、三大应用领域；四个 taxonomy axes 用于构造和分层，不直接作为 checkpoint 证据。
- **基线/对照**：Native memory 与 Mem0、Mem0-Graph、A-MEM 的 matched backend comparison；OpenClaw/Hermes 两种 harness，三个 LLM backend。
- **指标**：W1 Write Operation、W2 Persistence、E1 Recall Exposure、E2 Adoption、E3 Externalization、F1 Repair、F2 Benign Preservation、E2E-ASR、SRSR。
- **预算/硬件**：论文给出 24 配置和隔离运行协议，但未在正文披露统一的 token/GPU 成本；外部 judge 为 DeepSeek-V4-Pro。
- **消融与稳定性**：以 matched configurations 和 Figure 5 的相对 Native 差异为主；没有把 backend 内部的 retrieval、summarization、write policy 单独拆开的机制消融。

## 批判性阅读

### 证据支持的结论

- 从持久化到 adoption 的链式统计揭示了“记忆安全”的真正决策边界，攻击面不应只用 W2 或 E1 衡量。
- F1/F2 联合判定把“去掉恶意记忆”和“保持正常记忆”分开，避免把 destructive reset 误报成修复。
- backend 与 harness/LLM 的交互效应明显；安全评估应报告完整 stack，而非只报 memory backend 名称。

### 尚未被充分支持的结论

- benchmark case 的真实生态代表性仍依赖作者设计和 GPT-5.5 辅助 authoring；“48 realistic contexts”并不等价于真实生产流量分布。
- judge-human agreement 只证明抽样记录上的标签接近，不代表每个 checkpoint 的难例、跨 backend 或不同 judge model 都稳定。
- 结果是描述性配置对照，不能据此推断某个 memory backend 的因果安全机制；需要固定 retrieval/write/update 实现的更细粒度实验。

### 局限、风险与可能反证

- 攻击者被限制在支持的 Carrier 和正常接口内，不覆盖账户接管、后端直接写入、隐蔽持久化等更强威胁（威胁模型，第 3 页）。
- E3 依赖 mock service/workspace artifact；真实外部系统的权限、失败重试和并发状态可能改变 adoption→consequence 的比例。
- F1/F2 只覆盖 backend snapshot 中可见的 entries/summary/linked nodes，不保证 inaccessible cache 或 latent representation 被清除（附录 E.4，第 21 页）。
- 评估错误与 checkpoint 失败严格区分是优点，但若 evidence channel 不可用会阻塞聚合，实际部署中需要额外的 observability 设计。

## 与已有知识的连接

- **基础论文**：AgentPoison、A-MEM、Mem0；安全链条与 prompt injection、long-term memory evaluation 直接相连。
- **相近方法**：MemEvoBench、MEMFLOW、MemLeak 等分别覆盖记忆演化、端到端攻击或泄漏诊断；MemSecBench 强调同一 W2 rubric 的生命周期闭环。
- **后续工作**：优先跟踪 mechanism-specific defenses、origin/authority binding、memory provenance 和 selective repair 的可验证实现。
- **与主题笔记的关系**：[[notes/topics/Agent能力形成与过程验证]] 的“记忆生命周期安全”分支；与 SkillRise 的联系是“越能跨任务复用的 memory，越需要 provenance 和 repair guard”。

## 复现计划

- **是否复现**：待定；暂未找到公开 repo，先复现指标计算和小型 case protocol，不承诺完整 24 配置。
- **最小验证目标**：构造 10–20 个包含明确 W2/E3/F2 rubric 的 synthetic cases，在 Native、Mem0、A-MEM 中固定一个 harness 和 LLM，分别统计 W2、E2E、F1、F2、SRSR。
- **所需资源**：隔离容器、memory backend 服务、可记录 recall/tool/service artifact 的 runner，以及独立 judge 或双人工标注。
- **成功标准**：能重现“F1 高于 F2、联合 SRSR 更低”的方向；同时保留每个 verdict 的 admissible evidence，不能只靠最终答案字符串。

## 待追踪问题

- [ ] W2 rubric 如何在不同 backend 的摘要/拆分表示中做语义匹配，是否会偏向文本型 memory？
- [ ] E2 adoption 的失败来自模型拒绝、authority 判断、还是 retrieval context 位置/格式？
- [ ] selective repair 能否用 provenance、置信度或用户确认降低 F1–F2 gap？
- [ ] 在真实工具系统和更长时间跨度下，E3 和 F2 是否仍是同样的瓶颈？

## 原文定位

- **问题与贡献**：摘要、引言，第 1–2 页。
- **威胁模型与生命周期**：Methodology、图 2–3，第 3–5 页。
- **主结果**：表 2、图 4、Finding 1–2，第 5–6 页。
- **backend 对照**：Finding 3–4、图 5，第 6–7 页。
- **人工验证与证据规则**：附录 E.2–E.6、表 7，第 17–23 页。
- **案例与范围**：Case Study、Conclusion，第 7 页；限制条件详见附录 E.4。
