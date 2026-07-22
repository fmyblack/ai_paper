---
type: paper
title: "Agentic Real2Sim: Physics-based World Modeling with Vision-Language Agents"
aliases: []
authors: ["Guanxiong Chen", "Qianjun Xia", "Jiawei Peng", "Heng Zhang", "Bole Ma", "Justin Qian", "Ziyi Jiao", "Bingyang Zhou", "Luoxin Ye", "Kaifeng Zhang", "Kunyi Wang", "Weijia Zeng", "Yunuo Chen", "Pengzhi Yang", "Ziqiu Zeng", "Huamin Wang", "Chao Liu", "Alan Yuille", "Fan Shi", "Changxi Zheng", "Yunzhu Li", "Chenfanfu Jiang", "Peter Yichen Chen"]
year: 2026
venue: "arXiv"
paper_date: "2026-07-21"
date_added: "2026-07-22"
last_read: "2026-07-22"
topics: ["世界模型", "Agent", "机器人"]
status: read
priority: 1
rating: 3
arxiv_id: "2607.19190"
doi: ""
paper_url: "https://arxiv.org/abs/2607.19190"
code_url: "https://agentic-real2sim.github.io/"
pdf_path: "library/raw/2026/07/22/2607.19190v1.pdf"
text_path: "library/text/2026/07/22/2607.19190v1.txt"
sha256: "5c0882c9e32f9bd9923a58b8bfa4ff7e2b59eeb3e82dbd456e7aed7be6f90dc8"
pages: 12
citation_key: ""
related: ["[[notes/papers/2026/07/22/Masked Visual Actions for Unified World Modeling]]", "[[notes/papers/2026/07/22/AlayaWorld- Interactive Long-Horizon World Modeling - Full Technical Report]]"]
cssclasses:
  - paper-note
---

# Agentic Real2Sim: Physics-based World Modeling with Vision-Language Agents

## 一句话结论

Agentic Real2Sim 的实质是一个 VLM 编排的 real-to-sim 工程流水线：让 Agent 做对象选择、关键帧和 critic 决策，让 SAM 3、SAM 3D、FoundationPose、MuJoCo 和 grasp sweep 做确定性计算；DROID-100 证明开放 31B VLM 可以廉价替代闭源 backend，但绝对成功率仍低于 50%，且尚未证明 deformable/humanoid 的规模化转换或数字孪生能改善下游策略学习。

## 三分钟筛选

- **问题**：把真实交互录像转换为可运行物理仿真，不只需要视觉重建，还要组合对象状态、几何、相机、机器人轨迹、材料参数和 simulator refinement。
- **新意**：定义统一 episode twin contract，并把含歧义的高层判断交给 VLM Agent，把分割、重建、跟踪、标定和抓取搜索保留为确定性工具。
- **核心证据**：DROID-100 上四种 VLM backend 的 replay success 为 37-48%；Gemma 4 31B 达 48%，模型调用账单仅 $2.62，对 GPT-5.4 的 $82.30。
- **与我的关系**：说明 Agent 的价值可能主要来自“把成熟工具接成可修复 DAG”，而不是让模型直接预测物理；也是评估 VLM-as-orchestrator 的案例。
- **决定**：精读后保留，但对“generalized physical world modeling”主张降级解读为早期系统原型。

## 问题设定

- **输入、输出与目标**：输入同步视频、相机/深度、机器人轨迹和任务上下文；输出可在 MuJoCo 等 backend 中重放的 episode twin，包括观察、actors、geometry、states、physical parameters、backend 与评估 traces。
- **现有瓶颈**：工具跨域拼接脆弱；对象发现、关键帧、mask、ground plane 和修复方向带有语义歧义；视觉错误会在后续物理仿真中级联。
- **关键假设**：多数数值计算可由专用工具可靠完成，VLM 只需做 bounded schema-constrained decisions；replay similarity 可以作为数字孪生质量的代理。

## 核心贡献

1. 定义 episode twin $\mathcal{T}$ 和跨 rigid / deformable / humanoid 的共享 artifact contract。
2. 提出四阶段流水线：visual processing、physical-prior inference、scene preparation、simulator-in-the-loop grasp optimization。
3. 在 DROID-100 比较四种 VLM backend 的转换结果与模型账单，并用定性案例扩展到 deformable 与 humanoid。

## 方法

### 直觉

不要让 VLM 自己“看图输出物理世界”。让它只决定哪个对象重要、哪一帧适合分割、当前 mask/track 是否可接受、下一步应该调用哪个修复工具；所有几何、姿态和物理搜索仍由专用程序执行。这样小型开放 VLM 也可能胜任编排。

### 形式化描述

Episode twin 写为 $\mathcal{T}=(\mathcal{O},\mathcal{A},\mathcal{G},\mathcal{S}_{1:T},\Theta,\mathcal{B},\mathcal{M})$，分别对应真实观察、actors/end-effectors、几何资产、时间状态、物理/对齐参数、simulator backend 和转换指标/trace。共享 contract 不要求所有域共享同一物理状态，只要求它们暴露统一 artifact、replay 和 critic 接口。参见 Section 3，Eq. (1)。

### 关键模块与训练流程

1. Visual processing agent：对象发现、关键帧、SAM 3 分割、SAM 3D mesh、Depth、FoundationPose 6-DoF tracking，并由 mask/track critic 有界重试。
2. Physical-prior agent：从视觉和任务上下文推断对象身份、材料类别、质量提示与接触属性。
3. Scene preparation：相机选择与标定、robot base pose、ground plane、对象初始状态和 MuJoCo scene。
4. Simulator loop：确定性 grasp sweep 或 LLM-assisted refinement，根据 contact、lift 和 displacement feedback 调整对象位置。
5. Deformable / humanoid adapter 只复用 contract 和 repair interface，内部状态与 solver 仍是领域专用的。

### 计算与数据成本

- 定量实验为随机采样的 DROID-100；每个 episode 保留在分母中，即使中途失败。
- 四种 backend 的 100-episode model bill 为 Gemma $2.62、Claude $9.16、Qwen $12.97、GPT-5.4 $82.30。
- 上述只是不透明的“模型账单”，未包含 SAM 3/SAM 3D、depth、pose tracking、MuJoCo、grasp sweep、存储和人工工程成本，也未报告 wall-clock latency 或硬件。

## 实验与证据

| 作者主张 | 对应证据 | 定位 | 我的判断 |
| --- | --- | --- | --- |
| 流水线能批量生成 rigid episode twins | Gemma backend 在 DROID-100 中 48 success、8 partial、44 failure | Section 4.2、Figure 3；p. 8 | 证明“能跑到端到端”，但绝对成功率不足一半，仍是早期系统 |
| 开放 VLM 足以承担编排 | Gemma 4 31B / Qwen 3.6 35B / GPT-5.4 / Claude Haiku 4.5 分别成功 48 / 45 / 43 / 37 | Section 4.3、Figure 3；pp. 8-9 | 支持 backend 不是当前主要瓶颈；不能证明 Agent 本身优于规则系统 |
| 开放 backend 大幅降低成本 | Gemma $2.62，对 GPT-5.4 $82.30，即 31.4× 差距 | Figure 3；p. 8 | 对模型 API 成本成立，但不是全流水线 TCO |
| 同一 contract 可扩展到 deformable 和 humanoid | 论文展示 PhysTwin-style 软体案例和 Unitree G1 retargeted motions | Section 4.4、Figure 4；pp. 9-10 | 只有定性 stress test，没有 aggregate metrics，证据弱 |
| 可支持下游 policy learning/evaluation | 论文将此列为目标和 future work | Abstract、Section 5；pp. 1、10 | 尚无下游实验，不能作为已实现贡献 |

### 数据、基线与指标

- **数据集**：DROID-100 定量；PhysTwin-style deformable 与 LAFAN1/Unitree G1 humanoid 定性。
- **基线**：没有非 Agent pipeline、人工工程流程或其他 Real2Sim 系统的定量基线；只比较 VLM backend。
- **指标**：VLM-judged replay success/partial/failure 与 model bill。成功定义为三个异构 VLM judges 中任一 judge 对最多五个候选中的最佳候选打分至少 8/10。
- **预算/硬件**：未披露视觉/仿真工具计算成本和总延迟。
- **消融与稳定性**：没有逐阶段 agent/critic/tool ablation，没有人工校准 judge，也没有重复采样或置信区间。

## 批判性阅读

### 证据支持的结论

- 把 VLM 作用域限制在有界语义判断后，31B 开放模型可以与更昂贵闭源模型获得相近的 observed replay outcomes。
- 当前系统的主要瓶颈更可能是上游分割、几何、pose 和 simulator alignment，而非更强 VLM。
- 统一 artifact contract 能在代码组织层面连接多个物理域。

### 尚未被充分支持的结论

- 没有证据表明 agentic routing 比固定规则、人工编排或简单 heuristic 更可靠。
- “generalized” 只在 rigid DROID 上有定量证据；deformable 和 humanoid 只是案例图。
- 数字孪生对策略训练、评估或 sim-to-real 的实际价值尚未测试。

### 局限、风险与可能反证

- Replay metric 较乐观：先从 grasp sweep 选至多五个候选，再让三个 judges 各自找最佳，只要任一 judge ≥8 即成功，相当于多重取最大值。
- 论文没有报告 VLM judge 与人工专家的一致率；错误对象、错误末态或 contact plausibility 可能被误判。
- 物理先验包含材料和质量“提示”，但成功 rubric 主要检查关键帧外观与动作相似性，未直接测量动力学参数正确性。
- 模型账单忽略 specialist tools，不能据此推断端到端成本低。
- 上游误差级联明显，作者也承认 rigid focus 和 perception/simulator feedback sensitivity。

## 与已有知识的连接

- **基础论文**：DROID、MuJoCo、SAM 3/3D、FoundationPose、Real2Sim/Real2Sim2Real。
- **相近方法**：PhysTwin、PhysX-Omni、BFM-Zero，以及 generate-critic-improve 式 simulation asset agents。
- **后续工作**：人工校准 replay metric、逐阶段消融、端到端成本测量，并用 twins 训练/评估 policy。
- **与主题笔记的关系**：[[notes/topics/交互式世界模型与主动感知]]。

## 复现计划

- **是否复现**：待定；先复核评估协议，不先跑全栈。
- **最小验证目标**：在 20 个 DROID episodes 上人工盲评各 backend 的最佳 replay，并与论文的 any-of-three VLM metric 比较。
- **所需资源**：项目代码/配置、DROID、MuJoCo、SAM/pose tools、多模态 backend，以及至少两名人工评审。
- **成功标准**：人工一致率和 VLM metric 的 precision/recall 可量化；若 optimistic bias 很大，改成多数投票或固定候选协议后重新比较。

## 待追踪问题

- [ ] 三个 judge 的身份、相互相关性和人工校准结果是什么？
- [ ] 若移除 VLM agent、保留同一工具和固定 heuristic，成功率会下降多少？
- [ ] 生成 twin 的物理参数在 unseen intervention 下是否仍然正确，而不仅是重放看起来相似？
- [ ] 完整 pipeline 每个 episode 的 wall-clock、GPU 和存储成本是多少？

## 原文定位

- 问题与贡献：Section 1、Figure 1，pp. 1-2。
- Episode twin 与系统：Section 3、Eq. (1)，Figure 1，pp. 5-6。
- 工具/技能边界：Table 1，p. 7。
- 评估协议：Section 4.1，pp. 6-7。
- DROID-100 与 backend/cost：Section 4.2-4.3、Figure 3，pp. 8-9。
- Deformable/humanoid：Section 4.4、Figure 4，pp. 9-10。
- 局限：Section 5，p. 10。
