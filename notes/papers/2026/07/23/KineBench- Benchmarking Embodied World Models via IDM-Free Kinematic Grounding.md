---
type: paper
title: "KineBench: Benchmarking Embodied World Models via IDM-Free Kinematic Grounding"
aliases: ["KineBench"]
authors: ["Zeyu Liu", "Zhangzhe Zhu", "Yang Zhang", "Chenyou Fan", "Chenjia Bai", "Xuelong Li"]
year: 2026
venue: "ECCV 2026"
paper_date: "2026-07-22"
date_added: "2026-07-23"
last_read: "2026-07-23"
topics: ["世界模型", "机器人", "Benchmark 与评估方法"]
status: read
priority: 1
rating: 4
arxiv_id: "2607.19876"
doi: ""
paper_url: "https://arxiv.org/abs/2607.19876"
code_url: "https://github.com/minecraft-zzz/KineBench"
pdf_path: "library/raw/2026/07/23/2607.19876v1.pdf"
text_path: "library/text/2026/07/23/2607.19876v1.txt"
sha256: "77c9de5a6263157072acf7632e2389f611d26a2c83751f7325a082a4c054d488"
pages: 18
citation_key: ""
related:
  - "[[notes/papers/2026/07/22/Masked Visual Actions for Unified World Modeling]]"
  - "[[notes/papers/2026/07/22/Agentic Real2Sim- Physics-based World Modeling with Vision-Language Agents]]"
cssclasses:
  - paper-note
---

# KineBench: Benchmarking Embodied World Models via IDM-Free Kinematic Grounding

## 一句话结论

KineBench 的价值不在于提出更强的世界模型，而在于把生成视频先还原成可检查的 6D 末端轨迹、再送进 ManiSkill3 执行，从而显著减少 IDM 造成的归因混淆；它是比像素指标更接近机器人执行的评估管线，但仍依赖学习式分割/深度、已知夹爪 CAD 和可见末端，也只覆盖运动学而非完整接触物理。

## 三分钟筛选

- **问题**：现有 embodied world model 闭环 benchmark 多用 IDM 从生成帧反推动作；IDM 在新任务/新轨迹上的约 10 cm 误差会把“视频模型失败”和“动作提取器失败”混在一起。
- **新意**：用 YOLO mask、MoGeV2 metric depth 和 FoundationPose 的显式几何链恢复 6D end-effector pose，再以仿真成功率、SPARC 平滑度和 Maruyama manipulability 诊断生成轨迹。
- **核心证据**：在 7 个未见任务的 35 条 simulator trajectory 上，KineBench 平移误差约 1.5-3 cm，IDM 约 10 cm；四套共 20 个 ManiSkill3 任务揭示 task transfer、视觉 OOD 和 scaling 的明显非单调性。
- **与我的关系**：它为“生成式世界模型到底学到了可执行物理，还是只生成了好看视频”提供了一个可审计的中间层，与 Real2Sim 和 observation-space world model 评估直接相关。
- **决定**：精读并保留为评估基线；若复现，先校准 extraction error，再比较模型，不把提取轨迹当 ground truth。

## 问题设定

- **输入、输出与目标**：输入机器人初始帧与任务 prompt，EWM 生成未来视频；benchmark 从每帧恢复夹爪 6D pose，在 ManiSkill3 回放并判断任务成功，同时测轨迹平滑性与机器人可达性。
- **现有瓶颈**：像素指标不等于可执行性；闭环 IDM 又会在生成分布之外失效，使失败原因无法归到世界模型还是 extractor。
- **关键假设**：夹爪 CAD、相机模型和机器人运动学可得；末端在视频中足够可见；生成视频与 simulator 的场景/对象对应；末端 pose 足以驱动任务，未显式建模的力、接触和手指状态不会主导成功。

## 核心贡献

1. 提出 IDM-free 的显式 2D mask → metric depth → CAD 6D pose → simulator rollout 评估管线，并单独测量每个感知环节的误差。
2. 引入 SPARC 与 Maruyama Manipulability，从 robot-centric 视角分别描述时序平滑性和运动学可行性，而非只测视频视觉质量。
3. 构建 20 个任务、四个 suite，分别测 IID 执行、跨任务迁移、视觉 OOD 和 data/compute scaling，并发布代码与数据。

## 方法

### 直觉

不要训练一个黑盒 IDM 去猜动作，而是利用“机器人夹爪是已知刚体”这一先验，把生成帧显式投影回几何空间。Rigid CAD matching 会过滤局部纹理抖动，但对夹爪消失、空间跳变和不可达轨迹仍敏感；每一级输出都可查看，因而失败更容易归因。

### 形式化描述

- Fine-tuned YOLOv11 产生 end-effector mask，two-stage fine-tuned MoGeV2 恢复绝对 metric depth，FoundationPose 通过 render-and-compare 在 $SE(3)$ 中优化夹爪 pose。
- 提取的 pose 序列转为 ManiSkill3 action 执行。SPARC 对速度频谱的归一化幅值曲线求负弧长；越接近 0 越平滑，卡顿/瞬移会引入高频成分（Eq. 1，pp. 7-8）。
- Maruyama 指标 $w=\sqrt{\det(J(q)J(q)^T)}$ 描述 end-effector velocity ellipsoid；用 IK 将 pose 映射到 joint configuration，接近奇异位形或越界时指标恶化（Eq. 2，p. 8）。

### 关键模块与训练流程

- Suite 0：任务、对象、背景 IID；Suite 1：10 个任务训练、10 个未见任务测试；Suite 2：同任务但对象材质/几何/光照按资产划分 seen/unseen；Suite 3：固定 Wan 2.1-1.3B，改变 10-100 条轨迹和 1.5K-15K steps。
- EWM pool 包括 Wan 2.1/2.2、CogVideoX、LoRA 版本与 Wan 2.6/Hailuo-V2 API 模型；任务由 primitive rigid-body 到 articulated long-horizon manipulation。
- Pipeline 不是纯几何：YOLO 和 MoGeV2 均做 simulation-domain fine-tuning；只有 FoundationPose 被描述为 zero-shot pose tracking。

### 计算与数据成本

- 作者给定的现实预算为 4×NVIDIA A100，因此只覆盖少量开源 backbone、LoRA 和两个 API 模型；未报告完整 GPU-hours、训练时长、推理延迟或显存。
- Dataset 页面：<https://huggingface.co/datasets/Zorkzak/KineBenchDatasets>；代码：<https://github.com/minecraft-zzz/KineBench>。
- Suite 3 只在 Wan 2.1-1.3B 上改变数据量/优化步数，适合观察局部趋势，不能推出一般 scaling law。

## 实验与证据

| 作者主张 | 对应证据 | 定位 | 我的判断 |
| --- | --- | --- | --- |
| 显式管线比 IDM 更稳定、可诊断 | 7 个未见任务×5 条轨迹：KineBench 约 1.5-3 cm translation、约 10° rotation；IDM translation 约 10 cm；多种视觉扰动下长尾更少 | Figure 4-5，Section 4.2，pp. 10-12 | 强支持“减少 IDM 混淆”，但未到 error-free，精细装配仍可能被 10° 误差主导 |
| 当前视频模型的可执行性仍低且任务依赖 | Suite 0 最好 56.32%；Suite 1 各模型最高 57.78%；contact-rich StackCube/PickFruits 明显失败 | Table 1，Section 4.3，pp. 12-13 | 支持 benchmark 有区分度，也说明 headline 不是“世界模型已会机器人控制” |
| 简单视觉 OOD 未必击穿，但精细 affordance 会退化 | Suite 2 seen/unseen：前三个 full-tune 模型总体 58.00→55.50、56.11→51.67、57.19→52.83；Wan2.2 的 OpenBoxHard 60%→30% | Table 1，p. 12；Section 4.3，p. 13 | 平均值较稳掩盖 task-level 崩溃；应同时报告 per-task |
| 运动学指标只能作为互补诊断 | SPARC 在弱/未充分训练模型上与成功相关，full-tune 后饱和；manipulability 揭示不可达/奇异 pose | Figure 6-7，pp. 13-14 | 作者自己限定为 task/model-dependent，比宣称统一代理指标更可信 |
| data/compute scaling 非单调且受任务复杂度影响 | OpenBoxEasy 加同质数据 10→100 条，成功率 100%→83.33%；StoreCube-v2 增加 steps 后 13.34%→69.52% | Table 1、Section 4.4，pp. 14-15 | 有启发但样本窄；“过拟合”只是作者假说，不是被验证机制 |

### 数据、基线与指标

- **数据集**：ManiSkill3 中 20 个 manipulation tasks，四个 suite；专家轨迹均由 motion planning 生成。
- **基线**：Dino3DFlowIDM 用于 extractor generalization；EWM 比较含 Wan、CogVideoX、LoRA 和 API models。
- **指标**：closed-loop task success、6D pose translation/rotation error、SPARC、normalized manipulability cost；后者用 PyRoki trajectory cost 并按 10%-90% 分位 robust min-max。
- **预算/硬件**：4×A100；IDM 训练使用 Suite 1 十个训练任务、每任务 100 条轨迹；未见任务评估共 $N=35$。
- **消融与稳定性**：GT depth vs MoGeV2 vs IDM、well-trained vs underfitting MoGe、视觉退化扰动、data/steps scaling；未看到跨随机种子训练区间或多 extractor 重复验证。

## 批判性阅读

### 证据支持的结论

- 在已知夹爪 CAD、足够可见和 simulation-domain depth calibration 下，显式 kinematic grounding 比所测 IDM 更准、更透明。
- 视觉流畅度、运动学可达性和闭环任务成功是不同维度；SPARC/Manipulability 可以解释部分失败，但不能替代 rollout。
- 当前 EWM 的 generalization 与 scaling 高度依赖任务难度、接触类型和数据多样性，简单“模型更大/数据更多”并不保证成功率上升。

### 尚未被充分支持的结论

- 只比较一个 IDM，不能证明所有 learned inverse models 都系统性弱于显式几何管线。
- 在 simulator 内微调 depth、使用精确 CAD 后得到的优势，未证明可以无缝迁移到真实相机、未知工具或 deformable gripper。
- Kinematic rollout success 不证明模型理解摩擦、力、碰撞、柔性和因果；论文也没有 intervention/counterfactual 测试。

### 局限、风险与可能反证

- 管线仍含 learned segmentation 和 metric-depth；错误只是从 IDM 转移到更可拆分的 perception stages，而非消失。
- 必须已知 CAD、机器人结构且夹爪可见；严重遮挡、形变或第三方机器人外观变化会破坏 pose matching。
- 约 10° rotation error 对 pick-and-place 可能可忍，对插孔、旋拧和接触丰富任务可能不可接受。
- 专家数据全由 motion planner 生成，动作分布比人类 teleoperation 更干净、更窄；可能高估视频模型和提取器的稳定性。
- 20 个 simulator tasks、单一机器人设置和 4×A100 model pool 使 scaling 结论只能视作现象报告。

## 与已有知识的连接

- **基础论文**：FoundationPose、MoGeV2、ManiSkill3、SPARC、Maruyama manipulability。
- **相近方法**：World-in-World、WoW-World-Eval、Dino3DFlowIDM。
- **后续工作**：真实视频标定、unknown/gripper-free tracking、多 extractor 交叉校验、加入 contact/force 与 2D semantic metrics。
- **与主题笔记的关系**：[[notes/topics/交互式世界模型与主动感知]]；它把 observation prediction 显式落到机器人 3D 运动学，是从视频相似度到可执行状态的中间层。

## 复现计划

- **是否复现**：是，先复现 evaluator calibration，不急于重训 EWM。
- **最小验证目标**：在 3 个 seen、3 个 unseen task 上，用 simulator GT 视频比较 FoundationPose+GT depth、+MoGeV2、Dino3DFlowIDM，并加入遮挡/模糊扰动。
- **所需资源**：KineBench 代码/数据、ManiSkill3、YOLO/MoGeV2/ FoundationPose 权重、已知 CAD、单卡推理资源。
- **成功标准**：复核 1.5-3 cm vs 约 10 cm 的 translation gap，并量化 extractor error 对最终 success ranking 是否会翻转。

## 待追踪问题

- [ ] 换成更强 IDM 或直接 VLA action decoder 后，归因优势还剩多少？
- [ ] 对插入、旋拧、柔性物体等 contact-rich task，10° orientation error 会造成多大 evaluator bias？
- [ ] 在真实相机的 depth scale drift、motion blur 与遮挡下，MoGeV2 calibration 是否仍稳定？
- [ ] 能否用多个独立 extractor 的一致性估计评价置信度，而非输出单一 success number？

## 原文定位

- IDM 归因混淆与总体框架：Figure 1、Section 1，pp. 1-4。
- 显式 grounding pipeline：Figure 2、Section 3.1，pp. 6-7。
- SPARC 与 manipulability：Section 3.2、Eq. (1)-(2)，pp. 7-8。
- 四个 suite 与模型预算：Section 3.3、4.1，pp. 8-10。
- Extraction generalization/ablation：Figure 4-5、Section 4.2，pp. 10-12。
- 闭环成功率与 OOD：Table 1、Section 4.3，pp. 12-13。
- Kinematic diagnostics：Figure 6-7，pp. 13-14。
- Scaling 与局限：Section 4.4-5，pp. 14-15。
