---
type: paper
title: "SkillRise: Agentic Reinforcement Learning for Cross-Task Skill Evolution"
aliases: []
authors: ["Zhiyuan Yao", "Yuxin Chen", "Zhengxi Lu", "Zishan Xu", "Yueqing Sun", "Yifu Guo", "Yuquan Lu", "Zhengzhou Cai", "Kangning Zhang", "Zhuowen Han", "Zi-Han Wang", "Ziang Ye", "Qi Gu", "Xunliang Cai", "Weiwen Liu", "Yongliang Shen"]
year: 2026
venue: "arXiv"
paper_date: "2026-07-29"
date_added: "2026-07-30"
last_read: "2026-07-30"
topics: ["Agent", "强化学习", "长上下文与记忆", "推理与规划"]
status: read
priority: 1
rating: 4
arxiv_id: "2607.26784"
doi: ""
paper_url: "https://arxiv.org/abs/2607.26784"
code_url: "https://github.com/Within-yao/SkillRise"
pdf_path: "library/raw/2026/07/30/skillrise.pdf"
text_path: "library/text/2026/07/30/skillrise.txt"
sha256: "21a5542fd36ee26fee36f28d383a4a93fa2607bd581bc6bd31350157a4c0f19b"
pages: 18
citation_key: "yao2026skillrise"
related:
  - "[[notes/papers/2026/07/29/HiSkill- Empowering LLM Agents with Hierarchical Skill Graphs]]"
  - "[[notes/papers/2026/07/27/The Dark Room in the Reward Channel- Dense Prediction Rewards Collapse GRPO-Trained LLM Agents – and What Actually Works]]"
cssclasses:
  - paper-note
---

# SkillRise: Agentic Reinforcement Learning for Cross-Task Skill Evolution

## 一句话结论

SkillRise 把 Agent 的“技能学习”从单任务反思改写为跨任务序列上的 delayed-credit 问题：同一个策略交替执行 `solve` 与 `curate`，用后续任务回报监督技能整理。Qwen3-4B 在 ALFWorld、WebShop、ScienceWorld 的 Pass@1 为 85.9/84.4/54.6，超过最强对比基线 GiGPO 2.3/7.1/8.5 个百分点；但方法依赖任务族元数据、文本环境和可验证奖励，通用性仍待验证。

## 三分钟筛选

- **问题**：独立 episode 的 Agentic RL 无法把早期交互转成后续任务可复用的程序性技能。
- **新意**：构造“相似但不同”的有序任务序列；同一策略负责解题与重写技能文档；把当前回报和未来回报分配给不同角色。
- **核心证据**：表 1 的三环境 Pass@1、表 2 的同任务重试 Pass@3、图 2 的跨任务测试时扩展、图 3 的去掉整理阶段消融、图 4 的效率比较（原文第 5–8 页）。
- **与我的关系**：它把 [[notes/topics/Agent能力形成与过程验证]] 中的“能力形成”具体化为可观测的技能状态转移，并与 [[notes/papers/2026/07/29/HiSkill- Empowering LLM Agents with Hierarchical Skill Graphs]] 的结构化技能表示形成对照。
- **决定**：已精读；值得做小规模复现，优先验证跨任务顺序和技能文档是否是必要中介。

## 问题设定

- **输入、输出与目标**：给定同一 task family 中的有序任务序列 `x=(x1,...,xK)`。第 `i` 个任务使用当前技能文档 `S(i-1)` 生成轨迹 `τi` 和结果 `ri`；除最后一个任务外，策略根据 `S(i-1), τi, ri` 重写 `Si`，目标是提升后续任务成功率（第 3.1–3.2 节，原文第 3–4 页）。
- **现有瓶颈**：标准 RL 将任务独立采样，LaMer 主要对同一个实例反复尝试；多阶段 skill pipeline 还把抽取、存储、检索、更新和执行耦合在一起，难以归因且成本高（第 5.4 节，第 8 页）。
- **关键假设**：任务族元数据能识别“相似但不同”的实例；技能文档能压缩跨任务可迁移规律；后续任务的结果足以作为整理质量的代理信号。

## 核心贡献

1. 将跨任务技能学习形式化为由任务序列连接的 RL 问题，而不是独立 episode 的优化。
2. 提出单策略、双角色的 SkillRise，并用 role-aware group-relative optimization 避免 solve 与 curate 互相污染基线。
3. 在三个交互式文本环境验证跨任务迁移、同任务重试泛化、测试时序列扩展和较低 pipeline 成本（摘要；第 4–5 节）。

## 方法

### 直觉

每个任务只把一份经过压缩的技能文档传给下一个任务，早期完整轨迹不会直接泄漏。若文档中的规则真的可迁移，后续不同实例的成功率应上升；因此“整理得好不好”由 future return 间接监督，而不是由语言模型自评。

### 形式化描述

对第 `i` 个任务，solve 阶段回报为 `G(i,solve)=ri`；curate 阶段回报为后续任务折扣和 `G(i,curate)=Σ(j=i+1..K) γ^(j-i) rj`，论文取 `γ=0.6`（式 6，第 4 页；实验设置第 5 页）。同一序列内按任务位置 `i` 和角色 `z` 对 `N` 条 trial 计算组相对优势，再使用 clipped policy objective 更新共享策略（式 7–8）。

### 关键模块与训练流程

1. **Cross-task sequence construction**：按环境提供的 family metadata 分组，再按难度从简单到复杂排列；WebShop 例子按商品类别和属性/选项数量排序（第 3.1 节，第 3–4 页）。
2. **Cross-task rollout**：`S0=∅`；solve 当前任务；curate 完整重写文档，保留成功程序/失败模式并删除实例细节；只把新文档交给下一个任务（图 1，第 3 页）。
3. **Decoupled credit assignment**：当前结果只奖励 solve，未来结果只奖励 curate；同一策略参数但 role-specific instructions 分离学习信号。

### 计算与数据成本

- ALFWorld、WebShop、ScienceWorld；每个环境 128 个 held-out 实例。Qwen3-1.7B/4B，SkillRise 每 batch 为 16 个序列、每序列 `K=3`、每任务 `N=8` trials，即每次更新 384 次 task plays。
- actor learning rate `1e-6`，mini-batch 128，最长回复 1,024 tokens，最多 150 updates，temperature 0.7；FSDP + vLLM，8 张 NVIDIA H800（第 4.1 节，第 5 页）。
- ALFWorld 上与 RetroAgent/SkillRL 比较时，SkillRise 的相对运行时间为 1.0×，两者为 6.0×/4.3×；效率比较使用作者的 SkillRL reproduction，需注意复现实作可能影响结论（图 4，第 8 页）。

## 实验与证据

| 作者主张 | 对应证据 | 定位 | 我的判断 |
| --- | --- | --- | --- |
| 跨任务技能学习提升总体性能 | Qwen3-4B Pass@1：ALFWorld 85.9、WebShop 84.4、ScienceWorld 54.6；较 GiGPO +2.3/+7.1/+8.5pp | 表 1，第 5 页 | 支持；三环境方向一致，但都是文本环境、单次汇总，尚不足以证明开放域泛化。 |
| 技能整理策略可迁移到同任务重试 | Pass@3 为 92.2/96.1/61.0，三环境均为最高；ScienceWorld 较最强基线 +5.5pp | 表 2，第 6 页 | 支持“同任务重试”这一协议内结论；它不是跨分布泛化测试。 |
| 更多相关任务在测试时带来持续收益 | ALFWorld Pass@1 从 `K=2` 的 83.6% 升到 `K=6` 的 87.5%，领先基线的差距从 3.9pp 扩大到 8.6pp | 图 2，第 6 页 | 有说服力，但任务序列由作者按 metadata 和难度构造，顺序敏感性仍未测。 |
| 技能整理本身是必要的 | 去掉 curation、保持相同序列和交互预算后，训练末期 SkillRise 约领先 3pp；较 GRPO 超过 6pp | 图 3，第 7–8 页 | 支持必要性；消融没有拆分“文档内容质量”和“额外 role token/计算”两种因素。 |
| 端到端设计更高效 | ALFWorld 85.9% 与 RetroAgent 持平、比 SkillRL 高 12.5pp；运行时间 1.0× 对 6.0×/4.3× | 图 4，第 8 页 | 支持成本优势的方向；硬件、实现和 reproduction 差异应在复现中核对。 |

### 数据、基线与指标

- **数据集**：ALFWorld TextWorld 六类任务、1,000-product WebShop、ScienceWorld；每环境 128 held-out 实例。
- **基线**：Zero-shot、ReAct、Reflexion、PPO、RLOO、GRPO、GiGPO、LaMer；另与 RetroAgent、SkillRL 做 pipeline 比较。
- **指标**：Pass@1/2/3、不同跨任务序列长度的 Pass@1、训练 reward、相对运行时间。
- **预算/硬件**：Qwen3-4B 主结果，8×H800；每次训练更新 384 task plays。论文没有给出完整多 seed 统计或置信区间。
- **消融与稳定性**：`γ∈{0.3,0.4,0.6,0.7}` 的曲线最终约在 1pp 内；去掉 curation 的对照明确保留交互预算（图 3，第 7 页）。

## 批判性阅读

### 证据支持的结论

- 在作者选择的三类文本交互环境和 Qwen3-1.7B/4B 规模内，跨任务序列 + future-return curation 比独立 RL 和同任务反思基线更有效。
- “技能文档是唯一跨任务通道”使后续性能成为技能质量的可操作代理；这是比直接把全部历史塞入上下文更清晰的因果隔离。
- 论文还展示了同任务重试泛化和低 pipeline overhead，两者共同说明方法不只是在训练 batch 中利用额外采样。

### 尚未被充分支持的结论

- “技能”是否真正被模型参数内化，还是主要依赖运行时文本文档，尚无文档遮蔽、改写或跨环境迁移实验。
- 性能提升是否来自更好的任务排序/课程学习，而非 curation 机制本身，现有 ablation 没有完全拆开。
- `K` 变长时是否存在文档膨胀、错误累积或后期退化，图 2 只覆盖 ALFWorld 的 `K=2,4,6`。

### 局限、风险与可能反证

- 需要环境提供 task-family metadata；开放任务流中自动发现相关性仍是未解决问题（第 8 节，第 9 页）。
- 只测到 4B 参数、三个文本 benchmark 和 verifiable reward；多模态、真实工具、稀疏/主观奖励下的结论未知。
- 共享策略同时生成动作和技能文档，可能把“语言化总结能力”与策略改进混在一起；应比较冻结 curator、外部 summarizer 和随机/无效文档。

## 与已有知识的连接

- **基础论文**：GRPO/PPO/RLOO 的 group-relative 或 policy-gradient 优化；LaMer 代表同任务多次尝试的 Meta-RL。
- **相近方法**：[[notes/papers/2026/07/29/HiSkill- Empowering LLM Agents with Hierarchical Skill Graphs]] 关注技能图结构；RetroAgent/SkillRL 代表多阶段管理管线。
- **后续工作**：优先寻找不依赖人工 task-family metadata、能在真实工具或多模态环境中学习技能的后续方法。
- **与主题笔记的关系**：[[notes/topics/Agent能力形成与过程验证]] 的“技能演化”分支；与 [[notes/topics/跨视角监督、辅助信号与模型行为]] 的共同点是用后续行为而非自述验证中间产物。

## 复现计划

- **是否复现**：待定；代码已公开，但完整训练需要 8×H800 级资源。
- **最小验证目标**：在 ALFWorld 选 2–3 个 task families，比较 GRPO、SkillRise、w/o-curation；固定相同 task plays，记录技能文档长度、跨任务顺序和 Pass@1/Pass@3。
- **所需资源**：SkillRise 官方 repo、Qwen3-1.7B/4B、ALFWorld、vLLM/FSDP；至少 1 张高显存 GPU 可先做 inference/小规模 ablation。
- **成功标准**：在相同随机种子与预算下，SkillRise 相对 w/o-curation 的收益稳定为正；若收益消失，进一步检查 task ordering 或文档 prompt 是否为主因。

## 待追踪问题

- [ ] 没有 task-family metadata 时，能否用 embedding/轨迹相似度在线构造序列？
- [ ] 技能文档被截断、污染或替换后，Pass@3 和跨任务扩展如何变化？
- [ ] 把 curate 产物外置为可审计结构化 skill graph，是否能降低错误累积？
- [ ] 在工具调用、视觉状态或不可验证奖励环境中，future-return 是否仍能稳定归因？

## 原文定位

- **问题与贡献**：摘要、图 1，第 1–3 页。
- **序列构造与 rollout**：第 3.1–3.2 节，图 1，第 3–4 页。
- **信用分配**：式（6）–（8），第 3.3 节，第 4 页。
- **主结果与重试泛化**：表 1–2，第 5–6 页。
- **测试时扩展与消融**：图 2–3，第 6–8 页。
- **效率与限制**：图 4，第 8 页；第 8 节，第 9 页。
