---
type: topic
aliases: ["Agentic Data, Skill Evolution, and VLM Efficiency"]
topics: ["Agent", "数据生成", "技能演化", "多模态模型", "推理加速", "评估与工作流"]
status: active
created: "2026-08-28"
updated: "2026-08-28"
cssclasses:
  - paper-note
---

# Agentic 数据、技能演化与 VLM 推理效率

## 三篇论文的分工

| 论文 | 系统层 | 外部化对象 | 主要收益 | 证据边界 |
| --- | --- | --- | --- | --- |
| [[notes/papers/2026/08/28/WikiSkill- Compiling Agent Experience into Persistent Knowledge for Skill Evolution]] | Agent 自我改进 | raw trace → wiki pattern → skill | 跨迭代技能细化与跨模型迁移 | 直接注入技能；短验证集；无动态 retrieval |
| [[notes/papers/2026/08/28/What Makes Good Agentic Data- An ACE Lens on Data Generation for LLM Agents]] | 数据生成与评测方法论 | `d=(E,q,τ,v)` | 先 validity，再 learner-relative difficulty 与行为覆盖 | survey/formulation；没有统一实现或新模型实验 |
| [[notes/papers/2026/08/28/PACE- A Unified Condense-and-Extract Paradigm for Fast VLM Inference]] | VLM 推理系统 | pixel density、ViT/LLM attention、top-K tokens | 同时减少 encoder 与 prefill 成本 | query-agnostic；收益依赖 backbone；不加速 decode |

## 共同主线

三篇论文都把“最终分数”拆成可检查的中间对象：WikiSkill 记录轨迹和提案历史，ACE 明确环境/任务/轨迹/verifier 的关系，PACE 显式测量像素冗余、局部细节与注意力来源。共同启示是：只有把中间对象、验证接口和成本口径保存下来，才能区分真实能力提升、数据分布变化和计算捷径。

## 互补关系

- **WikiSkill × ACE**：WikiSkill 的 `raw/wiki/skills` 可以直接用 ACE 审计。每条 pattern/skill 应注明来源轨迹、任务可行性、verifier、适用 learner 与行为覆盖；否则 wiki 可能只是“看似合理的文本记忆”。
- **ACE × PACE**：PACE 的九任务 benchmark、10% token retention 和 TTFT 结果是一个具体的 learner-relative utility 案例；但它主要优化效率/质量，不覆盖 ACE 的环境真实性和轨迹多样性。
- **WikiSkill × PACE**：未来 VLM Agent 可把压缩策略作为可演化 skill，但必须记录 query 类型、细节丢失、模型 backbone 和预算，避免把某一视觉编码器的 workaround 迁移到其他模型。

## 当前综合判断（个人推断）

更可靠的 Agent 训练/推理栈应形成一条可回滚链路：`执行轨迹 → ACE validity gate → 结构化知识/技能 → learner-relative 采样或 token budget → 独立验证`。其中，WikiSkill 解决“经验如何积累”，ACE 解决“什么经验值得保留”，PACE 解决“在固定算力下如何保留关键视觉证据”。三者都不能单独证明长期泛化：技能可能负迁移，数据可能被 verifier 偏置，压缩可能丢失未被 query 指出的细节。

## 可验证的联合实验

1. 在一个多模态 tool-use Agent 上收集 `(E,q,τ,v)`，比较无 wiki、持久 wiki、shuffled wiki。
2. 对同一任务族做 PACE token budget sweep，并把视觉压缩造成的失败按 ACE 的 `A(d)` 与 `C_z(d)` 记录。
3. 在 held-out model/backbone、不同 query 类型和独立 verifier 上评估技能迁移、视觉证据保真度、成本与非冗余覆盖。

## 开放问题

- [ ] Wiki pattern 是否能成为 ACE 中可验证的 `v`，还是必须保留独立执行 verifier？
- [ ] VLM token compression 后的“缺失证据”如何写入 Agent memory，避免后续 skill 把压缩伪影当成事实？
- [ ] 是否能用统一 evidence graph 连接轨迹、技能 diff、数据 validity、token budget 和最终决策？
