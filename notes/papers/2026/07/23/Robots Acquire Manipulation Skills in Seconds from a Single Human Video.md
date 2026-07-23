---
type: paper
title: "Robots Acquire Manipulation Skills in Seconds from a Single Human Video"
aliases: ["HOST"]
authors: ["Guangyan Chen", "Meiling Wang", "Te Cui", "Zichen Zhou", "Qi Shao", "Shalfun Li", "Hang Su", "Roy Gan", "Hao Wang", "Mengyin Fu", "Yi Yang", "Yufeng Yue"]
year: 2026
venue: "arXiv"
paper_date: "2026-07-22"
date_added: "2026-07-23"
last_read: "2026-07-23"
topics: ["机器人", "模仿学习", "长上下文与记忆"]
status: read
priority: 1
rating: 4
arxiv_id: "2607.20033"
doi: ""
paper_url: "https://arxiv.org/abs/2607.20033"
code_url: "https://host-site.host-robotics.workers.dev/"
pdf_path: "library/raw/2026/07/23/2607.20033v1.pdf"
text_path: "library/text/2026/07/23/2607.20033v1.txt"
sha256: "8f78c36f42081f0c39b509da5823903929b077a2c350c7608d2d9f37c597d402"
pages: 38
citation_key: ""
related:
  - "[[notes/papers/2026/07/23/PRO-LONG- Programmatic Memory Enables Long-Horizon Reasoning]]"
  - "[[notes/papers/2026/07/22/Masked Visual Actions for Unified World Modeling]]"
cssclasses:
  - paper-note
---

# Robots Acquire Manipulation Skills in Seconds from a Single Human Video

## 一句话结论

HOST 把单个人类视频从“被动条件”变成逐步驱动机器人执行的外部技能：先用 task-progress alignment 找到机器人当前对应的视频阶段，再预测机器人视角的未来 observation，最后据此生成 action；50 个新任务平均成功率 62% 很强，但“29 秒获得技能”只指冻结大模型后的在线适配，背后是 193,462 条机器人轨迹、5,847 组人机配对、60 万步和多次 64-GPU 训练，不能理解为从零学习只需一段视频。

## 三分钟筛选

- **问题**：人和机器人完成同一任务的速度、视角、外观与 embodiment 不同；把完整视频直接喂给 policy 并预测固定未来 action，会让当前状态与目标视频段错位。
- **新意**：用 Smooth-DTW 学共享 progress manifold，把 prediction target 绑定到 demonstration 的“下一段进展”；再构造 localization → robot future observations → actions 的单模型因果级联。
- **核心证据**：单一双臂平台上 50 个 held-out task、每任务 20 次，HOST 平均成功率 62%；最强 one-shot visual baseline 约 19%，50 条机器人示范/task 的 Wall-OSS+SFT 为 56%。
- **与我的关系**：它展示了一种关键范式——技能不必写入权重，可以保留为可检索外部视频，并在执行时动态对齐、解释成当前 embodiment 的 future。
- **决定**：精读并重点跟踪代码/数据发布；认可机制消融，不接受脱离预训练成本的“seconds learning”叙事。

## 问题设定

- **输入、输出与目标**：给定单段人类任务视频、语言指令、机器人当前多视角 observation 与 proprioception，冻结模型逐 chunk 输出双臂动作，目标是在新对象/工具/程序上完成训练中未出现的 manipulation skill。
- **现有瓶颈**：video demonstration 与 robot execution 在时间上异步，且 embodiment、视角、物体状态不同；直接 video-to-action mapping 缺少可解释的跨域中间变量。
- **关键假设**：人类视频和机器人任务共享单调的 task progress；训练集已有足够广的同 embodiment motion/observation prior；视觉足以表达关键操作，没有力觉/触觉才可完成；新任务可由已有 primitive 组合而非要求全新 dynamics。

## 核心贡献

1. 用自监督 temporal cycle consistency + Smooth-DTW 建立 human/robot trajectory 的 frame-level progress correspondence，并据此重定义每个训练 target。
2. 在单个 autoregressive diffusion model 内实现 progress localization、future robot observation prediction 和 action prediction 的因果级联，以自我视角 prediction 缓冲 cross-embodiment gap。
3. 将视频作为外部 skill memory 存储/检索，不改权重地复用技能；在 50 个新任务上比较 one-shot、zero-shot 与 SFT，并评估 retention、扰动和机制消融。

## 方法

### 直觉

模仿不是“看完整视频后直接猜动作”，而是循环回答三个问题：我现在走到演示的哪一步？演示接下来要发生什么？换成我的机器人和当前场景，下一段 observation 与动作应该是什么？视频提供程序结构，机器人自身的 predicted future 提供 embodiment-grounded bridge。

### 形式化描述

- Alignment encoder 将 demonstration $d_{1:T}$ 与 robot trajectory $r_{1:N}$ 映射到共享 embedding；用双向 temporal cycle-consistency 与 normalized Smooth-DTW 学单调 soft correspondence，不需 frame labels（Section 4.2，Eq. 1-10，pp. 18-20）。
- 每个 robot target 不再取固定 $t+H$，而按 correspondence 绑定到 demonstration 的未来 progress。推理时模型预测窗口内 normalized progress $\hat p_t$，换算为全视频 frame index 并滚动 window（Eq. 18，p. 21）。
- Autoregressive diffusion 的 attention mask 强制 noisy localization token 只看条件，observation token 可再看 clean localization，action token 可再看 clean predicted observation；训练时 teacher-forced clean targets stop-gradient，并加噪缓解 exposure gap（Section 4.3，pp. 20-21；Appendix B.2，pp. 34-35）。

### 关键模块与训练流程

- Alignment module 基于 fine-tuned Qwen3-VL-Embedding-8B；先在 robot-robot、人-机器人同任务 pairs 上学 progress correspondence，训练后冻结，离线构造 policy target，推理不再调用。
- Policy 以 Wan2.2-TI2V-5B 为 video expert，并含 action/progress experts；Stage 1 用同 embodiment robot-robot pairs 学“跟随 procedure”，Stage 2 用 human-robot pairs 适配 cross-embodiment。
- 推理时每次执行 $H$ 步 action chunk，再根据 predicted progress 更新 demonstration window；已获得的视频与 instruction/initial scene 一起存入 memory，用语义和场景相似度检索。

### 计算与数据成本

- Alignment：10K steps，64 GPUs，per-GPU batch 4，bf16 + ZeRO-3；GPU 型号、训练时长未披露（Appendix B.1，pp. 32-33）。
- Policy Stage 1：500K steps、193,462 robot trajectories、229 tasks；Stage 2：100K steps、5,847 self-collected human video demonstrations 与相应 robot trajectories；两阶段均 64 GPUs、full-parameter update、batch 128（Appendix B.3，pp. 35-36）。
- 29 秒是部署时把一段视频准备成可执行条件的平均 acquisition time；507× 比较的是 29 秒与最快 SFT baseline 的 4.0 小时，不含上述预训练、数据采集或 robot rollout 时间。

## 实验与证据

| 作者主张 | 对应证据 | 定位 | 我的判断 |
| --- | --- | --- | --- |
| 一段视频可驱动大批新任务 | 50 个 novel tasks，每任务 20 trials，HOST 平均 62%，每个任务都有非零成功 | Figure 4，Section 2.2-2.3，pp. 6-8 | 覆盖面和 trial 数很扎实，但均在单一双臂平台和相近工作台域 |
| 显著优于 one-shot/zero-shot baseline | HOST 62%；最强 OSVI AWDA 约 19%，最强语言 zero-shot 约 17%，分别低 43/45 个百分点 | Figure 5，Section 2.4，pp. 8-9 | 使用共享 HOST backbone 集成 OSVI conditioning 提升公平性；Vid2Robot 是作者复现，仍有实现不确定性 |
| 比任务级微调更省数据/在线时间 | Wall-OSS+SFT 用 50 robot demos/task 达 56%；HOST 用 1 human video 达 62%；29 秒 vs 最快 SFT 4 h = 507× | Figure 6，Section 2.5，pp. 7-10 | 在线适配口径成立，但这是大规模预训练后的 amortized comparison，不是总成本比较 |
| 不改权重避免遗忘 | 7 个 mastered tasks 上 HOST 保持原性能；50 demos/task 后 Wall-OSS、HOST-base、π0.5 分别保留 40%、21%、17% | Figure 7，Section 2.6，pp. 10-11 | 支持 external-context 避免 parameter forgetting；未测 memory interference 的长期规模效应 |
| Progress coupling 是核心因果机制 | full video 0.21 → timestamp window 0.29 → progress window 0.45 → future-coupled target 0.62；人工事件对齐误差 0.079→0.006 | Figure 9，Section 2.8，pp. 12-13 | 强消融，清楚地区分“给视频”和“让视频驱动 target” |
| Self-grounded cascade 各阶段都贡献 | direct action 0.34 → +localization 0.43 → +visual prediction 0.55 → causal cascade 0.62；progress MAE 0.013 | Figure 10A-C，Section 2.9，pp. 14-15 | 机制证据强；future observation 质量主要为定性图，没有独立 calibrated metric |

### 数据、基线与指标

- **数据集**：训练 193,462 robot trajectories / 229 tasks，加 5,847 human demonstrations；测试 50 novel tasks，另 7 个训练任务测 retention。
- **平台**：2×ARX R5 六轴机械臂、parallel-jaw gripper，两个 wrist RGB + 一个 third-person RGB camera；20 randomized trials/task，由人按任务标准判成功。
- **基线**：Vid2Robot、AWDA（同 HOST backbone 接 conditioning）；π0.5、Wall-OSS、HOST-base 的 zero-shot 与 10/20/50 demo LoRA-SFT。
- **指标**：task success、acquisition wall time、旧技能 retention、progress alignment error、memory retrieval/novel recognition；未报告置信区间或显著性检验。
- **消融与稳定性**：target coupling 四级、causal cascade 四级、Stage 1 data fraction、四类 deployment perturbation、retrieved vs fresh video。

## 批判性阅读

### 证据支持的结论

- 单视频 conditioning 的关键不是提供更多视觉上下文，而是把当前执行与演示进度对齐，并让未来 target 随演示推进。
- 预测 robot-centric future observation 是 human video 到 robot action 的有效中间变量；严格 causal ordering 优于并行 visual/action prediction。
- 对冻结模型，external demonstration memory 能快速复用新技能且避免因任务级参数更新造成的 catastrophic forgetting。

### 尚未被充分支持的结论

- “Acquire skills from one video”不等于从头学到新的低层控制能力；更准确地说，是从大规模训练中已有的 primitive/policy prior 里按视频组合和调用。
- 只有单一 bimanual embodiment，尚未证明真正跨机器人 morphology；human→robot gap 与 robot-A→robot-B gap 不是同一难度。
- 62% 是人评 task success，未报告统计区间、失败类型、动作精度或安全约束，离可靠部署仍远。

### 局限、风险与可能反证

- 训练成本巨大但不透明：alignment 与 policy 都用 64 GPUs，未给 GPU 型号、wall time、energy 或数据采集 robot-hours。
- 纯视觉 demonstration 不包含 contact force/tactile，精细插装、受力控制和柔性操作可能无法由 future RGB 恢复。
- Progress 必须大体单调且流程相似；有分支、回退、重复子步骤或多人交互时 Smooth-DTW 对齐假设可能失效。
- Memory 只用 instruction + initial-scene similarity；库变大后细粒度任务可能误检，错误视频会把整个闭环带偏。
- Perturbation 只造成 1%-9% 平均降幅看起来很强，但任务/环境域仍接近，且没有跨实验室复现。

## 与已有知识的连接

- **基础论文**：Soft-DTW、TCC、Wan2.2、flow matching、one-shot visual imitation。
- **相近方法**：AWDA、Vid2Robot、MimicPlay、OSVI-WM、π0.5、Wall-OSS。
- **后续工作**：多 embodiment paired pretraining、force/tactile demonstration、非单调/分支 progress alignment、可扩展 skill retrieval 与 safety verification。
- **与主题笔记的关系**：[[notes/topics/交互式世界模型与主动感知]]；HOST 将视频变为可检索外部技能状态，并在每个 action chunk 主动定位当前 progress。

## 复现计划

- **是否复现**：待代码/权重/数据完整发布后做机制级复核，不尝试从零重训 5B policy。
- **最小验证目标**：在 5 个未见任务上冻结公开模型，比较 full-video、timestamp-window、progress-window 与 causal target，并核算从视频输入到首个动作的真实端到端延迟。
- **所需资源**：作者权重、alignment artifacts、单/双臂平台或兼容 simulator、每任务一段人类视频、至少 20 trials/task。
- **成功标准**：复现 progress coupling 的单调增益，并证明 retrieved video 与 fresh video 的 success 差异在统计误差内。

## 待追踪问题

- [ ] 50 个 novel tasks 中有多少只是已见 primitive 的新对象组合，多少需要真正新动力学？
- [ ] 29 秒具体包含视频编码、检索、首轮 diffusion sampling 的哪些部分，首动作 latency 是多少？
- [ ] 对有回退、循环或可交换子步骤的任务，单调 progress scalar 是否足够？
- [ ] Memory 从几十条扩展到几万条后，false retrieval 如何检测和恢复？
- [ ] 加入 force/tactile target 后，future observation cascade 应怎样扩展？

## 原文定位

- 问题、headline 与总体方法：Figure 1-2、Section 1，pp. 1-5。
- 平台、协议和 baselines：Section 2.2，pp. 6-7。
- 50 任务、baseline、data/time efficiency：Figure 4-6、Section 2.3-2.5，pp. 7-10。
- Retention 与扰动：Figure 7-8、Section 2.6-2.7，pp. 10-12。
- Target coupling 与 alignment 误差：Figure 9、Section 2.8，pp. 12-13。
- Causal cascade、pretraining scale effect、retrieval：Figure 10、Section 2.9-2.11，pp. 14-16。
- 作者局限：Section 3，p. 17。
- Alignment 与 policy 形式化：Section 4.2-4.3，pp. 18-21。
- Architecture/training scale：Appendix B.1-B.3、Supplementary Table 1-3，pp. 32-36。
