---
type: topic
aliases:
  - Maintainable Agent External State
topics:
  - Agent
  - 长上下文与记忆
  - 技能学习
  - 反思与自我修正
  - 安全、鲁棒性与治理
status: active
created: 2026-08-13
updated: 2026-08-13
cssclasses:
  - paper-note
---

# Agent 外部状态的增长、验证与压缩

## 结论

这三篇共同说明：Agent 的外部状态——项目规则、技能文档、反思记忆——不是“越多越好”的普通上下文，而是一个需要写入 provenance、验证 usefulness、控制 scope、允许压缩又能安全回滚的持久程序层。

但三篇解决的不是同一个问题：MIRA 训练“哪些失败经验应进入可执行诊断原则”，Catastrophic Remembering 解释“为什么缺失 rationale 会让规则只增不减”，SkillZip 研究“如何在不跑压缩时评测的情况下合并重复结构”。不能用 SkillZip 的 contract coverage 替代 MIRA 的行为验证，也不能用 comment rationale 替代 contract 的工具参数与输出字段。

## 三篇的角色

| 论文 | 外部状态 | 写入依据 | 保留/删除依据 | 最强证据 | 主要边界 |
| --- | --- | --- | --- | --- | --- |
| [[notes/papers/2026/08/13/MIRA- Medical Image Reflection for Agentic Diagnosis]] | 全局医学反思原则 | on-policy 失败的重复模式 | 同一冻结 policy、同一 validation set 上 reward 是否提升 | reflection memory 将平均分从 62.69 提到 64.73；direct tools 反而从 57.29 降至 53.04 | judge/validation 可能过拟合；无临床证据 |
| [[notes/papers/2026/08/13/Why Does CLAUDE.md Keep Growing- Catastrophic Remembering in Agentic Coding]] | `CLAUDE.md` / `AGENTS.md` 指令及其 comment | 一次失败后追加规则与 rationale | rationale 是否可恢复、失败是否复发、约束满足是否保持 | 247,694 lifetimes 的 ratchet；informative comments 将 T=51 excess +211.3% 降到 +1.4% | 真实仓库是观察性；因果实验是小 cover 合成世界 |
| [[notes/papers/2026/08/13/SkillZip- Evaluation-Free Skill Compression for Self-Evolving Agents by Discovering Reusable Structure]] | typed skill contract + residual | accepted self-evolution patch | hard coverage + MDL saving + structural audit | 平均压缩 31.2%，0 rollout，macro score 0.577 vs 0.570 | 只保证 parsed contract；parser 漏项会穿透保证 |

## 一个统一的维护闭环

可以把可维护 Agent 外部状态抽象为：

`failure/feedback -> candidate patch -> typed contract + rationale -> validation gate -> atomic commit -> execution/adoption -> outcome -> compress/repack -> audit/rollback`

| 阶段 | 应保存的信息 | 三篇提供的机制 | 不能省略的检查 |
| --- | --- | --- | --- |
| 观察失败 | task、环境、版本、tool result、final outcome | MIRA failure buffer；comments 的 failure/outcome | 区分一次性异常与重复模式 |
| 提出修改 | 规则文本、适用 scope、guard、预期证据 | MIRA memory editor；SkillZip patch parser | 禁止 case-specific/格式破坏规则 |
| 保存 rationale | 为什么写、尝试过什么、结果如何、复发次数 | informative prompt comments | comment 也可能错误或恶意，需 provenance |
| 结构化表示 | interface、workflow、tool args、output fields、exceptions | SkillZip typed contract | 模糊 span 原样锁定，安全规则人工锁定 |
| 行为验证 | 同 policy/同数据对照、held-out outcome | MIRA validation-gated trial | contract 相同不等于行为相同 |
| 压缩整理 | 去重、scope 上提、workflow 复用 | SkillZip MDL / Zip-on-Write | 保留 rationale 与 rare rules；不能只看出现频率 |
| 部署与回滚 | state version、policy version、transaction log | MIRA checkpoint pairing；SkillZip atomic commit | 可追溯、可 diff、失败不覆盖上一版本 |

## 作者证据支持的共识

1. **无差别增加状态会伤害结果。** MIRA 的 direct tools 平均 -4.25pp；WildIFEval 中 16 条 distractor 令正确约束满足率下降 24.1pp；SkillZip 的动机实验里 evolved skills 约长到 seed 的 5.2 倍。
2. **失败经验只有带 outcome 才值得继承。** Catastrophic Remembering 的 comment-shaped noise 无效，移除 recurrence count 会损失明显效果；MIRA 只从真实失败 rollout 提案，并用验证 reward 接受或拒绝。
3. **“结构完整”与“行为有效”必须双重验证。** SkillZip hard coverage 防止 silent deletion，但保证只相对 parsed contract；MIRA 的同 policy A/B trial 才测规则是否提升行为。
4. **早期治理优于事后整文件重写。** Prompt wholesale rewrite 后 10 commits 回到 91.5%；Zip-on-Write 从 round 1 启用优于 round 8；MIRA 用小 patch 和逐渐收紧的 edit budget 避免全量重写。
5. **高风险规则不能自动删除。** Catastrophic Remembering 明确要求人留在 deletion path；SkillZip 的 locked residual 和 MIRA 的 rollback 给出了工程支点，但都没有证明自动化安全。

## 我的综合设计

建议把每条持久规则建模为双层记录：

- **Contract 层（what）**：`id/type/scope/guard/modality/workflow edges/tool args/output fields`。
- **Evidence 层（why）**：`triggering failure/hypothesis/outcome/recurrence/validation set/policy version/last verified/provenance`。

写入时必须回答“它新增了什么 contract unit”；保留时回答“当前 evidence 是否仍支持”；压缩时只合并 contract 的重复表示，不删除 evidence；真正删除时同时要求 contract coverage、behavioral trial 和人工安全 gate。

这是跨三篇的个人推断，不是任一论文已经实现的完整系统。尤其需要防止两个新风险：错误 rationale 为坏规则提供永久正当性，或 parser 漏项让 hard coverage 产生虚假安全感。

## 与已有主题的连接

- [[notes/topics/Agent能力形成与过程验证]] 已有 `proposal/write -> exposure -> adoption -> consequence -> repair` 生命周期；本篇补上 persistent state 的 `rationale -> validation -> compression -> rollback`。
- [[notes/papers/2026/07/30/SkillRise- Agentic Reinforcement Learning for Cross-Task Skill Evolution]] 研究用 future return 写技能；本篇三篇补充技能写完后如何维护。
- [[notes/papers/2026/07/30/MemSecBench- Tracking Agent Memory Poisoning from Persistence to Consequence and Repair]] 提醒任何 comment/skill/memory 都是攻击面，provenance 不是可信性的充分条件。
- [[notes/papers/2026/07/31/See2Think- Do Multimodal Models Really Use Intermediate Visual States]] 提供 matched intervention，用于验证外部状态是否真的改变行为，而不仅是被读取。

## 最小可复现系统

1. 只读解析一个项目的 `AGENTS.md`/`CLAUDE.md`/skills，建立 instruction lifetime 与 provenance 表。
2. 为规则增加 sidecar：contract unit + rationale/outcome，不改原文件。
3. 实现 SkillZip 式 scan/coverage/audit，只输出 `*.compact.md` 候选，不自动覆盖。
4. 用 held-out tasks 做原文/候选 A/B，并记录 correctness、cost、rare-rule activation、regression。
5. 只有人工批准后替换；保留上一版、transaction log 与一键 rollback。

## 开放问题

- [ ] 如何证明 parser coverage，而不是只证明 optimizer coverage？
- [ ] rationale 多久必须重新验证，怎样表示任务 drift 与适用 scope 变化？
- [ ] behavioral validation set 会不会像普通 benchmark 一样被反复优化后失效？
- [ ] 如何给安全、权限、隐私和数据删除规则定义不可自动压缩/删除的 policy tier？
- [ ] comment/sidecar 被污染时，怎样沿 provenance 追踪到 downstream consequence？
- [ ] 多 Agent 并发写同一个外部状态时，如何做冲突检测、merge 与事务隔离？

## 证据边界

- **事实**：三篇 PDF、公式、表格和附录均已本地核对；数字来自各自 v1。
- **作者主张**：MIRA 的医学可靠性、Catastrophic Remembering 的机制归因、SkillZip 的 faithful compression 都只在各自实验边界内成立。
- **个人推断**：双层 contract/evidence schema 与统一闭环是跨论文综合，尚未被直接实验验证。
- **复现成本**：SkillZip project-local 原型最低；prompt-comment 受控实验次之；MIRA 完整训练最高且含未公开数据与闭源 teacher/judge。
