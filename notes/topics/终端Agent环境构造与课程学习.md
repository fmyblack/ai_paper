---
type: topic
aliases:
  - Terminal Agent Environment Construction and Curriculum
topics:
  - Agent
  - 终端环境
  - 强化学习
  - Agentic 数据
  - Prompt 优化
  - Benchmark 与评估方法
status: active
created: 2026-09-04
updated: 2026-09-04
cssclasses:
  - paper-note
---

# 终端 Agent 环境构造与课程学习

## 结论

三篇论文分别处理 Agent 训练栈的三个层面：Terminal-Universe 扩大可复用的环境/任务数据面，Environment Evolution 控制环境难度和 RL 信号寿命，ESPO 优化 prompt 与评估控制面。它们可以组成 `trajectory → executable environment → difficulty lineage → verified rollout → prompt/harness selection`，但目前没有论文验证这条完整闭环。

## 三篇的分工

| 论文 | 可扩展对象 | 核心机制 | 最强证据 | 主要边界 |
| --- | --- | --- | --- | --- |
| [[notes/papers/2026/09/04/Terminal-Universe- Turning Agent Trajectories into Scalable Terminal Environments]] | 真实/半真实 workspace 与任务 | trajectory replay + agentic completion + Single/Cross-WS/Multi-Round re-query | 37,273 task-sufficient；Qwen3.5-27B TB2.1 +11.9pp、EvoCode MT@4 +13.8pp | completion/judge/teacher 共同偏差；依赖源轨迹覆盖 |
| [[notes/papers/2026/09/04/Environment Evolution for Terminal Agents]] | 环境难度与课程顺序 | scenario/skill/length 离线进化 + Evolution-Lineage Scheduler | Qwen3.6-27B/35B-A3B TB2.1 峰值 71.5/64.9，超过 ensemble/co-evolution | `p_T` 估计不透明；闭源模型和单 benchmark |
| [[notes/papers/2026/09/04/ESPO- Error-Structured Prompt Optimization via Diagnose, Diversify, and Stabilize]] | prompt、verifier 和 harness 控制策略 | 全量错误诊断 + 四策略候选 + bootstrap winner vote | 7 任务平均 74.67% vs GEPA 70.91%，prompt 短 47% | 弱初始 prompt、非 Agent 任务；策略独立性是假设 |

## 统一数据流

`τ → Ê₀ → Ê → {q,v} → lineage(E₀…E_g) → scheduled rollout → SFT/RL → prompt/harness update`

- **环境层**：Terminal-Universe 把轨迹中的文件读写证据转成未解决 workspace；completion 是恢复上下文，不应被误认为原始环境的无损快照。
- **难度层**：Environment Evolution 在高层 scenario/skill 序列上做受控变异，并以 8-rollout pass-rate 阈值推进 lineage；这比随机混合环境更接近 curriculum。
- **控制层**：ESPO 用训练错误、候选多样性和验证集稳定性控制自然语言 prompt；同一思想可迁移到 proposer、verifier、solver 的 system prompt。

## 共同证据边界

1. **verifier 是收益来源，也是风险来源。** Terminal-Universe 用 agent-authored pytest 过滤数据；Environment Evolution 用 oracle/no-op/rubric gate；ESPO 用 validation accuracy 选择。三者都需要独立 verifier 或 held-out 检查，否则会把“可测”误当成“正确”。
2. **难度、质量、成本不能压成一个分数。** 更长的 turns 可能是更难，也可能是工具摩擦；更高 pass-rate 可能来自弱 verifier；更短 prompt 可能省 token，却不代表真实任务泛化。
3. **数据分布决定收益边界。** Terminal-Universe 受源轨迹语言/领域限制；Environment Evolution 受 seed 质量和参考分布限制；ESPO 的最大收益出现在故意很弱、远离 student 先验的 prompt。
4. **共同 teacher 会产生相关误差。** 环境补全、任务生成、解答、verifier 或 reflection 若由同一模型承担，结果不能视为独立证据；至少应引入独立 verifier、不同模型和新任务分布。

## 可验证的联合实验

1. 从 Terminal-Universe 重建的 20–50 个 workspace 中选出可独立验证的 seed，比较原始、replay-only、completion 三种环境。
2. 对每个 workspace 生成 length/scenario/skill 三条 5 代 lineage，用两个不同 rollout model 测 pass-rate、turns、oracle/no-op 通过率和 token 成本。
3. 固定同一 solver，在 baseline prompt、GEPA-like 单策略、ESPO 四策略+bootstrap 下比较 verifier pass-rate、首次失败轮次、prompt token、跨 workspace 泛化。
4. 所有结果同时报告环境质量、任务难度、RL/SFT 数据量、teacher 调用成本和独立 verifier 结果，避免只报 peak benchmark accuracy。

## 阅读与复现顺序

1. 先读 Terminal-Universe §3.1–3.3、§4–6，理解“环境从哪里来、怎样可解、怎样生成训练轨迹”。
2. 再读 Environment Evolution §3–5.5，重点核对 `D_T`、三种方向、EL scheduler 和固定预算比较。
3. 最后读 ESPO §3–4.6，先复现 Tweet/GSM8K 的组件消融，再考虑迁移到 Agent prompt。

## 开放问题

- [ ] `trajectory reconstruction` 与 `off-policy difficulty` 能否在同一 workspace lineage 上稳定组合？
- [ ] 独立 verifier、不同 teacher 和新 benchmark 下，三篇的提升是否仍存在？
- [ ] 如何把环境难度、任务真实性、verifier 可靠性和推理成本做成四维采样器，而不是单一 pass-rate？
- [ ] ESPO 的错误 pattern 能否直接成为 Environment Evolution 的 mutation rubric，减少 prompt bloat 又不缩窄任务分布？
- [ ] 长期 RL 中，lineage 变难与 prompt/harness 更新的交互是否会造成 reward hacking 或能力遗忘？

## 证据定位

- Terminal-Universe：表 2–3、4–11，图 4–7，页 7–13。
- Environment Evolution：式 (1)–(2)、表 1、图 3–7，页 3–10。
- ESPO：式 (1)–(7)、表 1–5、附录 A–B，页 3–12。
