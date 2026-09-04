---
type: paper
title: "Environment Evolution for Terminal Agents"
aliases: []
authors: ["Zhiyuan Fan", "Tinghao Yu", "Yuanjun Cai", "Jiang Zhou", "Jiangtao Guan", "Jincheng Liu", "Yun Yang", "Dingxin Hu", "Zhuo Han", "Xing Wu", "Feng Zhang", "Lilin Wang"]
year: 2026
venue: "arXiv"
paper_date: "2026-09-03"
date_added: "2026-09-04"
last_read: "2026-09-04"
topics: ["agents", "terminal environments", "reinforcement learning", "curriculum learning"]
status: reading
priority: 1
rating:
arxiv_id: "2609.04128"
doi: ""
paper_url: "https://arxiv.org/abs/2609.04128"
code_url: ""
pdf_path: "library/raw/2026/09/04/2609.04128v1.pdf"
text_path: "library/text/2026/09/04/2609.04128v1.txt"
sha256: "3f563b4e4e737c3d3f855a879114ffbeade1c04d1dc1ece027dcde142c462963"
pages: 13
citation_key: ""
related:
  - "[[notes/papers/2026/09/04/Terminal-Universe- Turning Agent Trajectories into Scalable Terminal Environments]]"
  - "[[notes/papers/2026/09/04/ESPO- Error-Structured Prompt Optimization via Diagnose, Diversify, and Stabilize]]"
  - "[[notes/topics/终端Agent环境构造与课程学习]]"
cssclasses:
  - paper-note
---

# Environment Evolution for Terminal Agents

## 一句话结论

Environment Evolution 用与目标模型无关的难度信号离线进化终端环境，并按 lineage 从易到难调度给 GRPO；在固定训练环境预算下，Qwen3.6-27B/35B-A3B 的 Terminal-Bench 2.1 峰值分别达到 71.5%/64.9%，高于 co-evolution 的 62.9%/55.1% 与 ensemble 的 60.0%/52.8%（页 9–10）。

## 三分钟筛选

- **问题**：从零生成的环境很快被 frontier model 解完；on-policy co-evolution 又把难度绑定到某个模型的弱点，难以持续提供可学习信号。
- **新意**：从多轮学习目标推导离线难度，沿 `scenario novelty`、`skill rarity`、`execution length` 三个方向逐代修改环境，再用 Evolution-Lineage Scheduler 按能力阈值推进。
- **核心证据**：15 代 lineage 在 Hy4、Claude Opus 5、GPT-5.6 Sol 上都变难；200-step GRPO 对两个 Qwen 模型均超过 ensemble/co-evolution。
- **与我的关系**：与 Terminal-Universe 互补：前者构造可复用环境，本文控制环境课程和 RL 信号寿命。
- **决定**：精读；完整复现成本高，先做难度曲线和 scheduler 的小规模验证。

## 问题设定

- **输入、输出与目标**：输入已验证的 terminal environment `E_g`；输出下一代 `E_{g+1}`、可执行 oracle/verifier 和按代调度的训练分布。
- **现有瓶颈**：on-policy 难度只测当前模型；随机采样后代会产生全失败 rollout，GRPO advantage 失效；环境质量和 verifier 错误会污染 RL。
- **关键假设**：参考分布 `T` 能近似 scenario/skill 的普遍性；序列编辑能单调提高难度且不破坏 solvability；pass-rate 阈值可作为推进课程的充分信号。

## 核心贡献

1. **Off-policy difficulty**：`D_T(ξ)=Σ_t[-log p_T(σ_{t-1}|g)-log p_T(κ_t|σ_{t-1},g)]`，将环境难度拆为场景新颖度、技能稀有度和执行长度；模型弱点是相对 `D_T` 的 excess difficulty。
2. **Two-loop evolver**：Plan Refinement 由 proposer/reviewer 生成并审查序列修改；Environment Refinement 由 modifier 落地，Oracle、Invalid-test、general-rubrics 三个 verifier 并行 gate。
3. **Evolution-Lineage Scheduler**：每代用 `B=8` 次 rollout，pass-rate 阈值 `τ=6/8`；当前环境达到阈值后推进同代下一个环境，当前代耗尽后才进入下一代。

## 方法

### 直觉

环境本身像 curriculum 的“样本空间”：不等目标模型暴露失败，再根据失败补题，而是预先构造一条难度 lineage，并只在模型接近解会时放入下一代。

### 形式化描述

高层轨迹 `ξ=(σ₀,κ₁,σ₁,…,κ_L,σ_L)`；模型特定难度 `D_θ` 依赖策略概率，论文用参考分布 `T` 替换得到模型无关 `D_T`。三种 evolution direction 分别修改 `L`、`σ` 或 `κ`；`evolution effort` low/high/max 控制编辑范围。

### 关键模块与训练流程

1. 从 47,678 个 Hugging Face/GitHub 环境经质量、可解性和难度过滤，得到 500 个 seed。
2. 每个 seed 生成 15 代 lineage；每代通过 oracle、no-op invalid-test 和 general-rubrics 检查。
3. 先 RFT 提高策略熵，再用 GRPO 训练 Qwen3.6-27B 与 Qwen3.6-35B-A3B 共 200 steps；固定 Claude Opus 5 做环境合成器比较 ensemble/co-evolution。

### 计算与数据成本

每个难度评估使用 8 次独立 rollout；训练和评估依赖 Claude Code harness、256k context、最多 4 小时/任务、32 CPU/48 GB benchmark 容器。环境生成还需要多 Agent proposer/reviewer/modifier/verifier 以及人工审查反馈（页 5–7）。


## 实验与证据

| 作者主张 | 对应证据 | 定位 | 我的判断 |
| --- | --- | --- | --- |
| 作者主张 | 对应证据 | 定位 | 我的判断 |
| --- | --- | --- | --- |
| 离线进化确实逐代增加难度 | 三个独立模型上 pass-rate 下降、平均 turns 上升；high/max 比 low 更接近单调 | §5.2、图 3–4（页 6–7） | 跨模型重复是优点，但难度指标仍是 rollout-derived，参考分布 `T` 的估计过程不够透明。 |
| 三个方向有可区分的作用 | high effort 下 length 单步 `−7.1 pp` pass-rate、scenario `+13.5` turns、skill `+12.5` turns | §5.3、表 1（页 7–8） | 支持方向性编辑，但 mutation rate 与任务质量耦合，不能只看 pass-rate。 |
| lineage scheduler 提供更有效 RL 信号 | EL scheduler 使 partial-solved rate/reward 高于 random（前 50 steps） | §5.4、图 5–6（页 8–9） | 机制合理；需报告 scheduler 的额外 rollout 成本与阈值敏感性。 |
| Environment Evolution 优于其他扩展范式 | TB2.1 峰值 71.5/64.9 vs co-evolution 62.9/55.1、ensemble 60.0/52.8 | §5.5、图 7（页 9–10） | 比较固定环境预算且合成器一致，较公平；仍是单 benchmark、单 harness。 |

### 数据、基线与指标

- **数据集**：500 个平衡 seed environment；主要评估 Terminal-Bench 2.1 Verified。
- **基线**：Environment Ensemble、Agent–Environment Co-Evolution、随机 lineage scheduling。
- **指标**：8-rollout pass-rate、平均 assistant turns、partial-solved rate、mean reward、TB2.1 accuracy。
- **预算/硬件**：GRPO 200 steps；Qwen3.6-27B dense 与 Qwen3.6-35B-A3B MoE；32 CPU/48 GB、4 小时任务超时。
- **消融与稳定性**：low/high/max effort、scenario/skill/length 方向、EL vs random、三种扩展范式；TB 评估每 10 steps 一次。

## 批判性阅读

### 证据支持的结论

- `D_T` 依赖 reference model/distribution 的估计，论文提出“可由 deep-research agent 估计”，但没有给出可独立复核的概率模型或标注集。
- 生成阶段使用强模型和人工-in-the-loop rubric，训练目标模型又使用同一 Claude Code stack；质量 gate 的泛化到其他 harness 未证明。
- 所谓“更难”以 pass-rate/turns 为主，可能混入任务长度、工具摩擦或 verifier 变化；需要 separately audit solvability、bug-free 和 cost。
- RL 峰值而非固定 step 的最终结果，且两模型使用不同稳定化设置（MoE 额外 R3），跨模型比较要谨慎。

### 尚未被充分支持的结论

- 

### 局限、风险与可能反证

- 

## 与已有知识的连接

- **基础论文**：POET、UED、GRPO；Terminal-Bench 2.1 是主要 held-out 评估。
- **相近方法**：[[notes/papers/2026/09/04/Terminal-Universe- Turning Agent Trajectories into Scalable Terminal Environments]]、SETA、CLI-Universe、RST、CalibForge。
- **后续工作**：论文提出扩展到 SWE agents 与 Computer-Use Agents；可与 Terminal-Universe 的真实 workspace lineage 结合。
- **与主题笔记的关系**：补充 [[notes/topics/Agent能力形成与过程验证]] 的“环境反馈→能力形成”层。

## 复现计划

- **是否复现**：待定
- **最小验证目标**：在 5–10 个可公开验证的终端环境上实现 length/scenario/skill 单步进化，复现三模型 pass-rate/turns 方向与 EL scheduler 的 partial-solved 优势。
- **所需资源**：容器化终端任务、独立 oracle/no-op verifier、至少一个可重复调用的 rollout model；完整 200-step GRPO 需要大规模 GPU 与闭源模型。
- **成功标准**：进化后任务保持 oracle 可解、no-op 必败，独立模型难度曲线单调趋势显著；EL 在同 rollout 预算下提高非全失败组比例。

## 待追踪问题

- [ ] `p_T(σ|g)` 与 `p_T(κ|σ,g)` 的估计如何实现，是否可由非闭源模型复现？
- [ ] 把 seed 换成 Terminal-Universe 重建环境后，lineage 难度是否仍保持跨模型一致？
- [ ] 难度增加带来的收益能否在 SWE/GUI 环境而非 terminal benchmark 上保持？

## 原文定位

- 难度定义：§3、式 (1)–(2)（页 3–4）；双循环 harness：图 2、§4.1（页 4–5）；EL scheduler：§4.2（页 5）；effort/方向：图 3–4、表 1（页 6–8）；RL dynamics：图 5–6（页 8–9）；范式比较：图 7（页 9–10）；局限与结论：页 10。
