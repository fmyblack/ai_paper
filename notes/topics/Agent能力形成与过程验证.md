---
type: topic
aliases:
  - Agent Capability Formation and Process Verification
topics:
  - Agent
  - 强化学习
  - 长上下文与记忆
  - 多模态模型
  - Benchmark 与评估方法
  - 安全、鲁棒性与治理
status: active
created: 2026-07-31
updated: 2026-08-06
cssclasses:
  - paper-note
---

# Agent 能力形成与过程验证

## 定义与边界

本主题关注 Agent 怎样形成一个可跨步骤或跨任务复用的中间状态，以及怎样证明这个状态真的被后续行为使用。这里的中间状态可以是技能文档、长期记忆或视觉工作区；“形成”不等于“有效”，“被读到”不等于“被采用”，“产生了结果”也不等于“能安全修复”。

## 2026-08-03 补充：长程反馈不是普通上下文

[[notes/papers/2026/08/03/MerchantBench- Benchmarking LLM Agents for Long-Term Coherence in E-Commerce Operations]]、[[notes/papers/2026/08/03/AgentHPOBench- A Benchmark For Evaluating LLM Agents as Sequential Hyperparameter Optimizers]] 和 [[notes/papers/2026/08/03/Beyond Retrieval- Analytic Memory for Multimodal Agents]] 共同补上了“反馈如何进入后续行为”的评测视角。

| 论文 | 反馈形态 | 采用证据 | 关键失败 |
| --- | --- | --- | --- |
| MerchantBench | 延迟订单结果、供应商事件、现金和评分 | 365 天最终净资产、SWR、产品/店铺级轨迹 | 活动衰减、提前放弃、错误记忆和需求漂移应对不足 |
| AgentHPOBench | 已完成实验的配置、指标和日志 | final-step MBNS/BWR/MAA、no-feedback ablation | 找到好配置后不能保留；harness 与 best-so-far 口径影响排名 |
| ADAMM | 多模态历史中的 attribute-value-provenance 记录 | analytic/retrieval ablation、任务级 Judge 提升 | 抽取错误和 schema 错误会传播到计算结果 |

这三篇把“中间状态被使用”进一步拆细：MerchantBench 看真实延迟反馈是否长期改变策略，AgentHPOBench 看短序列实验反馈是否推动下一轮配置，ADAMM 看历史记录是否被转成可执行操作。共同结论是：把反馈塞进长上下文还不够，系统需要维护反馈的来源、适用范围、操作接口和最终结果证据。

本轮三篇论文覆盖同一生命周期的不同切面：

- [[notes/papers/2026/07/30/SkillRise- Agentic Reinforcement Learning for Cross-Task Skill Evolution]] 研究中间技能怎样被 future return 训练并改善后续任务。
- [[notes/papers/2026/07/30/MemSecBench- Tracking Agent Memory Poisoning from Persistence to Consequence and Repair]] 研究恶意记忆怎样从写入传播到外部后果，以及能否选择性修复。
- [[notes/papers/2026/07/31/See2Think- Do Multimodal Models Really Use Intermediate Visual States]] 研究视觉动作怎样被渲染、吸收并因果影响最终答案。

三篇不能被当成同一 benchmark 的横向排名。SkillRise 是训练方法，MemSecBench 是安全生命周期 benchmark，See2Think 是 inference-time 过程诊断框架；它们的共同价值是把“中间产物存在”拆成可验证的状态转移。

## 三篇论文的定位

| 论文 | 中间状态 | 形成/写入 | 暴露/执行 | 使用/采用 | 结果验证 | 更新/修复 | 最强证据 | 主要缺口 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| SkillRise | 文本技能文档 | 根据当前轨迹完整重写 | 后续任务只接收新文档 | solve policy 条件于文档 | 后续任务 future return、Pass@1/3 | 下一次 curate 继续重写 | 三环境 Pass@1 较 GiGPO +2.3/+7.1/+8.5pp；ALFWorld `K=2→6` 为 83.6→87.5% | 依赖 task-family metadata；未证明技能被参数内化；只测文本环境与≤4B |
| MemSecBench | 长期恶意/良性记忆 | W1 操作、W2 语义持久化 | E1 实际 recall event | E2 adoption | E3 外部 artifact，E2E 50.3% | F1 去恶意、F2 保良性，SRSR 56.1% | 310 cases×24 配置；七检查点；judge-human 90.6/91.8% | synthetic/controlled contexts；judge 与 backend snapshot 依赖；无公开 repo |
| See2Think | 外部渲染的视觉状态 | 模型提出结构化视觉动作 | renderer 生成视觉状态 | Feedback Uptake | final accuracy + WrongRender paired drop | 无长期修复，只做干预诊断 | 1.2K×四模型；3D 高 uptake 时错误反馈导致 15.5pp drop | renderer/干预质量不稳定；单 key-step judge；仅四模型 |

## 一个统一的生命周期

可以把三篇抽象成下面的可审计链条：

`proposal/write → persistent state → exposure/render → adoption/uptake → downstream consequence → curation/repair`

| 生命周期阶段 | SkillRise | MemSecBench | See2Think | 应回答的问题 |
| --- | --- | --- | --- | --- |
| 形成/写入 | curate 生成 `Si` | W1/W2 | visual action `At` | 中间状态是否包含目标信息，来源是什么？ |
| 暴露/执行 | 文档进入下一任务上下文 | E1 recall | renderer 生成 `Rt` | 下游是否真实看到了状态，而非只生成调用痕迹？ |
| 采用/使用 | solve policy 受文档条件化 | E2 adoption | Feedback Uptake | 状态是否改变了推理、参数或动作？ |
| 外部结果 | future return、Pass@K | E3 consequence | paired final accuracy | 影响是否落到可验证结果，而非语言自述？ |
| 更新/修复 | 后续 curate 重写 | F1/F2 selective repair | 尚未覆盖 | 如何去除错误而不破坏仍有用的信息？ |

### 作者证据支持的共识

1. **存在不是使用。** MemSecBench 的 W2 84.2% 到 E2 53.7% 大幅下降；See2Think 的高 Action Relevance 与较低 Render Faithfulness/不稳定收益分离；两者都反对用“写入/调用成功”替代 adoption 证据。
2. **结果级监督比中间产物自评更可信。** SkillRise 用后续任务回报奖励 curate；MemSecBench 要求 task-scoped external artifact；See2Think 用 matched WrongRender 改变视觉证据并观察准确率变化。
3. **更新能力必须与保留能力联合评估。** SkillRise 的技能重写需要保留可迁移规则、删除实例细节；MemSecBench 明确显示 F1 去恶意高达 86.3%，但 F1∧F2 只有 56.1%。
4. **中间状态的价值依赖完整系统。** SkillRise 依赖任务族和模型容量；MemSecBench 的 backend 排名随 harness/LLM 反转；See2Think 的最佳设置随模型/环境变化。

### 我的综合判断

一个可持续自我改进的 Agent 不应只有“经验库”或“视觉 scratchpad”，而应为每个中间状态维护四类元数据：`provenance`（从哪里来）、`scope`（何时适用）、`evidence`（被什么结果支持）、`repair policy`（发现错误后如何修改且不伤及良性状态）。SkillRise 提供了基于未来回报的价值信号，MemSecBench 提供生命周期安全 gate，See2Think 提供 matched intervention；三者合在一起才接近“既能学、又能证明使用、还能安全纠错”的闭环。

这仍是个人推断，三篇没有直接实现该组合。尤其不能把 SkillRise 的高 future return 当成 memory provenance 已解决，也不能把 See2Think 的 Feedback Uptake 当成正确使用；MemSecBench 已说明 adoption 本身可能是攻击成功的一环。

## 2026-08-04 补充：过程开始前的 route selection 也需要审计

[[notes/papers/2026/08/04/Learning Compositional Meta-Routing for Agentic Workflows- An Executable Benchmark]] 把 Agent 过程验证提前到第一步：系统还没开始调用模型/工具前，就先显式预测这题是否需要 decomposition、retrieval/tool use、code execution、specialist delegation 和 verification。它的贡献是把“为什么 agent 要走这条 workflow”变成可记录、可训练、可检查的 route，而不是事后从 trace 里猜。

对本主题的补充有三点：

1. **route adoption 不等于 route correctness。** Learned router 标准 test 成功 100%，但 exact-route match 只有 0.741，且多调用 retrieval 77 次而 oracle 只需 49 次；最终成功会掩盖多余操作和风险暴露。
2. **组合能力不是单点工具选择。** one-shot learned router 只有 56.5%，说明 filtered computation、multi-hop retrieval、invoice reconciliation、locale normalization 等任务需要多操作组合。
3. **过程验证必须测分布外措辞。** locked lexical-shift 上 learned router 从 100% 掉到 75.9%，低于 static 93.5%；失败集中在 aggregate code、multi-hop decomposition 和 conflict verification。

这篇不证明真实 Agent workflow routing 已解决，但给了一个很干净的审计接口：把 route 作为 first-class artifact，分别记录 operation probabilities、budget、fallback、执行状态和 typed failure。它可以和 SkillRise/MemSecBench/See2Think 的中间状态生命周期合并，形成 `route proposal -> state/action execution -> evidence -> verification -> repair/fallback`。

## 2026-08-06 增补：个性化 memory 要看“更新”而不只是“召回”

[[notes/papers/2026/08/06/FinPerMA- A Theory-Informed, Event-Grounded Personalized-Memory Benchmark for LLM Agents]] 把 Agent memory 从静态 recall 推进到 personalized state update：它用 276 personas、97 真实金融事件和 2994 道题，逼模型回答“事件之后这个用户现在会怎么想”。这和前面的 memory 生命周期论文互补，因为它不只看写入和保留，还看冲击后的再校准。

| 论文 | 记忆对象 | 关键 checkpoint | 最强证据 | 主要缺口 |
| --- | --- | --- | --- | --- |
| [[notes/papers/2026/08/06/FinPerMA- A Theory-Informed, Event-Grounded Personalized-Memory Benchmark for LLM Agents]] | 个性化金融用户状态 | post-shock、summary / retrieval / full-context 对照 | retrieval 以约 1.4k token 追回大约 88% 差距；summary 记事实但丢偏好；full-context 约 0.47 overall accuracy 饱和 | 合成金融场景；理论约束 persona 是否泛化到真实用户还未知 |

这篇和 `PRO-LONG`、`MemSecBench` 的关系很清楚：`PRO-LONG` 说明结构化外部日志可以承载长程历史，`MemSecBench` 说明 memory 更新本身也可能被攻击，FinPerMA 则补上“对个体偏好的更新到底有没有跟上事件变化”这一层。

## 证据地图

| 结论 | 支持论文与定位 | 反证/限制 | 证据强度 |
| --- | --- | --- | --- |
| 后续行为可以监督中间状态质量 | SkillRise 式（6）–（8）、表 1–2、图 2（第 4–6 页） | 任务顺序和 family metadata 可能贡献收益；无文档扰动实验 | 中-强 |
| recall/exposure 不能代表真正 adoption | MemSecBench 图 4（第 6 页）；See2Think 表 3、图 6（第 9 页） | 两篇都依赖外部语义 judge | 强 |
| behavioral dependence 不等于 utility | See2Think 图 8（第 10 页），3D 高 uptake 的 WrongRender drop 15.5pp | 2D/real-world 关联弱或非单调；WrongRender strict pass 56.7% | 中-强 |
| 删除目标信息不等于安全恢复 | MemSecBench F1 86.3%、SRSR 56.1%，图 4（第 6 页） | 只验证 snapshot 中可见状态，不含潜在/不可访问缓存 | 强 |
| 单一 backend/策略不存在普适最优 | MemSecBench 图 5；See2Think 表 2 | 配置覆盖仍有限 | 中-强 |
| 当前系统已形成可靠、长期、自修复的通用 Agent 能力 | 无 | 三篇分别缺开放任务流、真实生产分布、长期修复闭环 | 不支持 |

## 设计原则

- **区分各阶段指标**：至少分别记录 write/persist、exposure、adoption、external outcome 和 repair；不要用单一 success rate 压平失败位置。
- **让中间状态成为唯一或明确的信息通道**：SkillRise 只传技能文档、MemSecBench 只接受 recall event、See2Think 对 renderer 做 matched intervention，这些设计减少旁路混淆。
- **用外部结果约束语义判断**：tool call、agent claim 和看似合理的 trace 都不足以证明成功；优先使用环境状态、artifact 或配对结果变化。
- **把保留性加入更新目标**：任何 memory/skill optimizer 都应同时测目标删除/修正与 benign preservation，防止通过清空状态获得虚假的修复率。
- **报告完整 stack 和干预质量**：模型、harness、backend、renderer、judge 与 prompt 都会影响结论；干预失败应单独审计。

## 复现优先级

1. **See2Think 3D 小样本干预**：官方 repo 公开，先验证高 Feedback Uptake 是否稳定对应更大的 WrongRender drop，并人工审计 renderer。
2. **SkillRise ALFWorld 小规模消融**：固定 task plays，比较 SkillRise、w/o-curation、随机文档和任务顺序打乱，确认收益来自技能状态而非课程学习。
3. **MemSecBench 最小 lifecycle runner**：若代码仍未公开，手工实现 10–20 case 的 W2/E1/E2/E3/F1/F2 证据 schema，优先验证 benign preservation。
4. **组合实验**：对 SkillRise 文档注入错误/过期规则，用 MemSecBench 式 checkpoint 和 See2Think 式 matched corruption 测试 adoption、后果和修复。

## 开放问题

- [ ] future return 能否同时奖励“有用”并惩罚“不安全/过期”的技能，而不依赖人工 task-family metadata？
- [ ] 如何为文本技能、向量记忆和视觉状态建立统一的 provenance、scope 与 confidence schema？
- [ ] 能否用 paired corruption/遮蔽证明某条技能或 memory 是后续成功的必要原因，而不仅是相关上下文？
- [ ] selective repair 应作用于条目、摘要、图节点还是模型参数，怎样验证没有残留 operative semantics？
- [ ] 当 renderer、judge 或外部 artifact 自身不可靠时，怎样传播评估不确定性而不是给出单个布尔 verdict？
- [ ] 长任务流中，中间状态不断重写会不会出现 benign forgetting、错误固化和累积性偏差？

## 阅读路线

1. 先读 SkillRise 图 1、式（6）–（8）和图 2，理解能力状态怎样被 future return 训练。
2. 再读 MemSecBench 图 3–4 和附录 E.2–E.5，理解“出现—采用—后果—修复”为什么必须拆开。
3. 最后读 See2Think 表 3、图 7–8 和附录 F.2，用 paired intervention 区分中间状态的效用与行为依赖。
