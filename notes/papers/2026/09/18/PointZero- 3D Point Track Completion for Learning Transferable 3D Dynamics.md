---
type: paper
title: "PointZero: 3D Point Track Completion for Learning Transferable 3D Dynamics"
aliases: []
authors: ["Bardienus P. Duisterhof", "Kaifeng Zhang", "Adam Hung", "Bowen Wen", "Stan Birchfield", "Yunzhu Li", "Deva Ramanan", "Jeffrey Ichnowski"]
year: 2026
venue: "arXiv"
paper_date: "2026-09-16"
date_added: "2026-09-18"
last_read: "2026-09-18"
topics: ["世界模型", "机器人", "模仿学习", "预训练数据"]
status: read
priority: 2
rating:
arxiv_id: "2609.19142"
arxiv_version: "v1"
version_updated_at: "2026-09-16"
doi: ""
paper_url: "https://arxiv.org/abs/2609.19142"
code_url: "https://github.com/Duisterhof/pointzero"
pdf_path: "library/raw/2026/09/18/2609.19142.pdf"
text_path: "library/text/2026/09/18/2609.19142.txt"
sha256: "4cc75b95f2eb40b3c9134e0dfc2ea2ffa2da34f0b2ec9ebb0e880e9427865324"
pages: 18
citation_key: ""
related: ["[[notes/papers/2026/09/18/Zing-0.5- Toward Playable Worlds with Real-Time Joint Action and Text Control]]", "[[notes/papers/2026/08/26/Do Robotic World Models Really Follow Actions- Diagnosing and Aligning Action-Conditioned Generation for Policy Learning]]", "[[notes/papers/2026/07/23/KineBench- Benchmarking Embodied World Models via IDM-Free Kinematic Grounding]]", "[[notes/papers/2026/07/29/SAM3D-Guided Object-Centric Representation Alignment for Vision-Language-Action Models]]"]
cssclasses:
  - paper-note
---

# PointZero: 3D Point Track Completion for Learning Transferable 3D Dynamics

## 一句话结论

PointZero 有力证明了“大规模合成 3D point-track completion 能形成可迁移的几何运动先验”：在同输入、同训练数据下，它显著优于逐点和自回归基线，并能提升 task-specific imitation learning；但预训练与 zero-shot 评测都已给出至少一条完整未来真值轨迹，多个最强数字又使用 ground-truth best-of-10 oracle，因此证据支持的是**条件式 3D 运动补全**，不是从单张图像独立预测物理未来。

## 三分钟筛选

- **问题**：机器人视频包含大量对象运动，却通常缺少动作标签；直接预测 RGB 既浪费容量，也难把几何动力学迁移给控制策略。怎样用可扩展的合成数据学习稠密 3D 运动，再适配少量有动作数据的下游任务？
- **新意**：把世界模型预训练改写为 point-track completion：输入单帧 RGB-D、前景点云和 1–3 条跨完整未来的稀疏条件轨迹，由 DiT 一次性补全所有初始可见点的 10 帧 3D 轨迹；再把条件接口替换成机器人动作做动力学后训练或 action-track 联合模仿学习。
- **核心证据**：约 290 万 synthetic frames 上，FM first-sample 的 deformable/articulated/rigid MDE 为 3.60/2.39/28.97 cm，最佳非 PointZero 基线为 9.01/8.25/61.97 cm；相同全参数协议下，预训练把三个仿真任务平均成功率从 80.5% 提到 88.2%（Tables 1、4，pp. 7、9）。
- **与我的关系**：它为 Zing-0.5 的像素级“可玩世界”补上显式 3D 几何表示，也与 SAM3D-VLA 的 object-centric teacher 形成训练期重监督、部署期轻接口的共同模式。
- **决定**：精读；优先复现 first-sample completion 与 matched pretrained-vs-scratch，不以 oracle-10 数字作为主要结论。

## 问题设定

- **输入、输出与目标**：预训练输入首帧 RGB-D、前景 mask、相机内参和 `N_a∈{1,2,3}` 条跨 `T=10` 帧的完整 3D 条件轨迹；模型预测首帧所有可见前景点的完整未来轨迹。后训练可把稀疏轨迹替换成 6-DoF EEF pose 与 gripper state，并可增加 action head。
- **现有瓶颈**：RGB world model 容量大量消耗在纹理与渲染，point-level 模型又常逐点独立或逐帧自回归，难表达对象整体相关性并累积 rollout error；真实机器人动作视频昂贵且规模小。
- **关键假设**：合成器中的 deformable/articulated/rigid 运动足以学到可迁移几何先验；首帧 depth、mask 和稀疏未来轨迹在部署时可获得；final-timestep point metrics 能代表对控制有用的动力学；伪真值 stereo/tracker error 不会改变模型排序。

## 核心贡献

1. 提出统一的 3D point-track completion 预训练任务，在一个序列 transformer 中联合预测整段、整对象运动，而非逐点/逐帧滚动。
2. 用 FleX、Genesis/PartNet-Mobility 和 Kubric 构造约 290 万帧的 deformable、articulated、rigid 混合数据，并比较 regression、flow matching 与 JiT-style x-prediction。
3. 展示预训练表示可迁移到真实对象 zero-shot completion、scene-specific dynamics 和 action-track 联合 imitation learning，但三类实验的 grounding 与 oracle 口径并不相同。

## 方法

### 直觉

对象上一小部分点的未来轨迹携带“被怎样推动/转动”的条件，其余点的运动受形状、关节和材料相关性约束。若模型能从稀疏未来 track 补全稠密 track，它就可能学到一种比像素生成更紧凑、比单点回归更整体的运动先验。这个直觉成立的前提是把“预测未知未来”和“利用已知未来条件传播运动”分清。

### 形式化描述

- 首帧深度经内参反投影为前景点云 `P_obs∈R^(N_p×3)`；条件 `A∈R^(N_a×T×3)` 是 `N_a` 条已知的完整未来 3D 轨迹，目标 `X∈R^(N_p×T×3)` 是所有初始可见点的未来位置（Section 3，p. 3）。
- direct regression 直接最小化预测与真值轨迹的误差；flow matching 从 `N(0,0.2²I)` 噪声到数据轨迹学习 velocity field；JiT-style x-prediction 直接预测 clean sample，并把训练中的 `1-t` 下限 clip 为 0.05（Equations 1–3，pp. 5–6）。
- FM/JiT 推理都只做 4 次 forward-Euler，使用 `μ=-3, σ=1` 的 logit-normal time grid；训练时以 0.2 概率显式采样 `t=0`（Section 5.1，p. 6）。
- 论文的主要离线指标只比较 final timestep：MDE、MSE、Chamfer Distance 与 Earth Mover's Distance；因此不检查中间速度、碰撞、接触、能量或轨迹连续性。

### 关键模块与训练流程

- DINOv2 image tokens 经三层 Perceiver-IO 压成 4 个 visual tokens；point、action 与 visual tokens 进入交替 self-/cross-attention 的 DiT。Base 配置为 hidden dimension 768、12 heads、12 layers（Figure 2、Section 4，p. 4）。
- 合成数据混合约 42.67% deformable、43.10% articulated、14.22% rigid，约为 `3:3:1`。deformable 覆盖 towel/T-shirt/shorts 与随机 stiffness/drag；articulated 来自 PartNet-Mobility + Genesis；rigid 为修改后的 Kubric、最多 3 个对象（Appendix A.1–A.3，pp. 14–15）。
- articulated/rigid 的条件轨迹从未来位移最大的点中选取，不是随机可见点；这让条件更有信息，也缩小了“任意稀疏 observation”外推范围（Appendix A.3，p. 15）。
- scene-specific dynamics 用 EEF pose + gripper state 替换 track 条件；imitation learning 再加入 action head，联合预测 action chunk 与 point tracks（Section 4.3，p. 6）。

### 计算与数据成本

- 每个预训练 variant 约使用 `8×H100×2 days`，即约 384 H100-GPU-hours；论文没有给出总 variant 数、baseline 训练成本、后训练成本或美元成本（Section 5.1，p. 6）。
- synthetic held-out 约 32K scenes。真实 completion benchmark 含 14 个对象、124 次人工交互：6 articulated、5 deformable、3 rigid；“真值”由 FoundationStereo + CoTracker3 生成，不是 motion capture（Sections 3.2、5.3，pp. 5、8）。
- imitation learning 每任务使用 20 个带动作 demonstrations 加 100 个无动作 videos；仿真任务另有每任务 1000 rollout 的预训练隔离实验（Section 5.5、Tables 3–5，p. 9）。

## 实验与证据

| 作者主张 | 对应证据 | 定位 | 我的判断 |
| --- | --- | --- | --- |
| whole-sequence completion 优于现有架构 | FM first-sample MDE：deformable 3.60、articulated 2.39、rigid 28.97 cm；最佳非 PointZero 为 9.01、8.25、61.97 cm | Table 1、Table 8，pp. 7、16 | 同数据输入下证据强，且 first-sample 已支持；但自回归基线天然承受 rollout accumulation，容量与 compute 未完全匹配 |
| 生成式目标优于直接回归 | FM/JiT first-sample 在 12 个 synthetic 指标中赢 11 个；例外是 rigid MSE，JiT 48.63、regression 44.58（`10^-2 m²`） | Table 8，p. 16 | 支持多模态目标总体更好，不支持所有类别/指标一致占优 |
| zero-shot 可迁移到真实对象 | FM oracle-10 在真实 deformable/articulated/rigid 的 MDE 为 2.923/1.720/2.322 cm，作者称 12 项赢 11 项 | Table 9，p. 17 | 结论依赖用真值选 10 个样本中 MDE 最低者；rigid first-sample 四项全部弱于 PTv3，不能把 11/12 当作部署性能 |
| 预训练改善 scene-specific dynamics | Bread/Paperbag/Cloth/Box/Rope/Sloth 的 FT MDE 为 1.5/1.6/4.0/2.4/3.3/3.9 cm，scratch 为 4.2/4.2/5.6/3.7/9.3/7.3 | Table 2，p. 9 | 增益明显，但两行都逐场景、逐指标 best-of-10；FT 是 LoRA、scratch 是全参数，不是完全 matched |
| 预训练改善机器人策略 | 仿真 Blockstack/Microwave/Glass 99.8%/93.1%/95.9%；真实 Drawer/Cup/Paper/Sock 100%/100%/70%/90%，6/7 最高或并列最高 | Tables 3、5，p. 9 | 有真实执行证据，但真实任务 trial 数、CI、多 seed 未披露；Paper 低于 3PoinTr 的 90% |
| 增益来自 point-track 预训练而非额外视频 | 相同全参数协议、无额外视频时，有 downstream track supervision 的平均成功率 80.5%→88.2%，无 track supervision 74.1%→80.0% | Table 4，p. 9 | 本文最干净的 transfer 证据；仍只覆盖 3 个仿真任务和单一训练预算 |

### 数据、基线与指标

- **数据集**：约 290 万 synthetic frames；约 32K held-out synthetic scenes；14 个真实对象/124 次交互；PGND scenes；7 个 simulation/real imitation tasks。
- **基线**：逐点 MLP、PTv3、Point Transformer、并行 transformer 与自回归 transformer；scene dynamics 对 PGND；policy 对 ACT、Diffusion Policy、3PoinTr 等。
- **指标**：final-timestep MDE/MSE/CD/EMD；机器人 task success。mean-10 是十个样本均值，oracle-10 是按 ground-truth MDE 选最优样本，二者不能与可部署 first-sample 混写。
- **预算/硬件**：每个 PointZero variant 约 384 H100-GPU-hours；其余模型、后训练和机器人采集成本未完整披露。
- **消融与稳定性**：articulated real split 的数据量消融 MDE 为 2.2/3.1/3.3 cm（100%/10%/5%），但小数据训练 250/500 epochs 以近似保持优化步数；45M Small 为 3.1 cm、Base 2.2 cm。没有 seed variance 或显著性检验（Tables 6–7，p. 15）。

## 批判性阅读

### 证据支持的结论

- 同数据、同条件下，联合建模整对象、整时间序列的 transformer 明显优于逐点和自回归架构；优势在 first-sample 指标上已存在，不完全来自 oracle sampling。
- 大规模 synthetic point-track completion 能改善少量下游 action data 的 imitation learning；Table 4 的相同全参数协议比主表更直接支持预训练迁移。
- 稀疏 track 是有效的运动条件接口：给定未来运动线索时，模型能在一定 sim-to-real gap 下传播到未观测点。

### 尚未被充分支持的结论

- 论文没有证明单帧 RGB-D 足以预测未来：预训练和真实 zero-shot completion 都条件于至少一条**完整未来轨迹**；PGND zero-shot 也抽取一条 ground-truth object trajectory。
- “learned physics”表述不能按力学模型理解：表示中没有质量、力、摩擦或接触状态，评估也不约束能量、碰撞和中间时刻物理一致性。
- 主结果中的 oracle-10 不是可部署预测。尤其真实 rigid first-sample 的 MDE/MSE/CD/EMD 均弱于 PTv3，best-of-10 才反转结论。
- 下游机器人结果是 task-specific post-training，不是预训练模型直接做通用 planning 或 online world-model rollout。

### 局限、风险与可能反证

- **信息泄露式误读风险**：条件轨迹并非 label leakage，因为任务定义本就要求 conditional completion；但把它宣传成 image-only future prediction 就会越过论文证据边界。
- **oracle selection**：Table 2 和 Table 9 用真实答案挑样本；部署时没有这个选择器，必须同时报告 first、mean 和可实现的 learned ranking。
- **伪真值误差**：真实 benchmark 的 stereo + tracker 可能在遮挡、无纹理、快速运动时系统性偏差；没有 motion-capture audit。
- **合成覆盖有限**：rigid 只占 14.22% 且最多 3 个对象；真实材料、手物接触、clutter、长时域和 topology change 未充分覆盖。
- **公平性与统计不足**：baseline 参数/compute 未匹配；数据量消融改变 epoch；真实机器人缺 trial 数、CI 和多 seed。
- **时间范围有限**：固定 `T=10`，离线指标只看终帧，不能证明长时稳定或中间接触正确。

## 与已有知识的连接

- **基础论文**：DINOv2 提供视觉 token；DiT/flow matching/JiT 提供生成式轨迹建模；FoundationStereo 与 CoTracker3 构造真实视频伪标签。
- **相近方法**：[[notes/papers/2026/08/26/Do Robotic World Models Really Follow Actions- Diagnosing and Aligning Action-Conditioned Generation for Policy Learning]] 检验 action-conditioned video 是否真正遵循动作；[[notes/papers/2026/07/29/SAM3D-Guided Object-Centric Representation Alignment for Vision-Language-Action Models]] 用 object-centric 3D teacher 对齐 VLA；[[notes/papers/2026/09/18/Zing-0.5- Toward Playable Worlds with Real-Time Joint Action and Text Control]] 走实时像素生成路线。
- **后续工作**：用 robot action 而非 ground-truth future track 做严格 zero-shot；加入 contact/force 与中间轨迹指标；训练 learned sample selector；用 matched compute、参数量与多 seed 重做 architecture/transfer ablation。
- **与主题笔记的关系**：[[notes/topics/结构化中间层与可验证执行]] 与 [[notes/topics/生成模型与机器人从表示到物理可用性]]；PointZero 把稀疏未来条件变成可检查的稠密 3D 中间层，但还没有闭环 verifier。

## 复现计划

- **是否复现**：待代码、数据和 checkpoint 实际发布后做最小复现。
- **最小验证目标**：先用 5% articulated split + 45M Small，固定 `T=10`，复现 regression/PTv3 与 FM 的 first-sample MDE；再在一个 PGND scene 做同 trainable parameters、同 optimizer、3 seeds 的 pretrained-vs-scratch。
- **所需资源**：官方 synthetic subset、数据生成/track sampling 代码、45M checkpoint recipe、单机多 GPU；真实部分另需 RGB-D 或 stereo、可靠 point tracker。
- **成功标准**：first-sample 而非 oracle 指标稳定优于 matched baseline；预训练在 3 seeds 下显著改善 held-out dynamics；报告中间帧、contact violation 与 sample-selection cost。

## 待追踪问题

- [ ] 代码仓库何时从 “Release coming soon” 变成可执行 release？dataset、checkpoint、license 与完整 recipe 是否同步公开？
- [ ] Base 的准确参数量、所有 variants 的累计 GPU-hours 和 baseline compute 是多少？
- [ ] 若条件轨迹随机采样而不是选最大位移点，性能下降多少？条件轨迹含未来多少信息？
- [ ] Table 9 在 first-sample、mean-10 和 learned selector 下的完整 12 指标分别怎样？
- [ ] 真实 robot 表的 trial 数、随机种子、失败类型和置信区间是什么？
- [ ] 加入力、接触和中间轨迹一致性后，final-point 优势是否仍成立？

## 原文定位

- 任务定义、输入与真实数据：Section 3、Figure 1，pp. 3–5。
- 架构、三种目标与后训练：Section 4、Figure 2、Equations 1–3，pp. 4–6。
- 训练配置、采样与 synthetic 主结果：Sections 5.1–5.2、Table 1，pp. 6–7。
- 真实 zero-shot、PGND 与机器人策略：Sections 5.3–5.5、Tables 2–5，pp. 8–9。
- 主要限制与结论：Sections 6–7，pp. 10–11。
- 数据生成、条件点选择、数据量与模型量消融：Appendix A、Tables 6–7，pp. 14–15。
- 完整 synthetic/real completion 数字与 oracle 口径：Tables 8–10，pp. 16–17。
- 项目页：https://pointzero-wm.github.io/；代码仓库：https://github.com/Duisterhof/pointzero（2026-09-18 仅 placeholder README，dataset/checkpoint 未发布）。
