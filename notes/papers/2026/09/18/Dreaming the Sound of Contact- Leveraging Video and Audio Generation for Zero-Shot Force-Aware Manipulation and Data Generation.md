---
type: paper
title: "Dreaming the Sound of Contact: Leveraging Video and Audio Generation for Zero-Shot Force-Aware Manipulation and Data Generation"
aliases: []
authors: ["Guanhua Ji", "Tianyu Li", "Dayoon Suh", "Yuqian Zhang", "Boyan Zhang", "Nadia Figueroa"]
year: 2026
venue: "arXiv"
paper_date: "2026-09-16"
date_added: "2026-09-18"
last_read: "2026-09-18"
topics: ["机器人", "生成模型", "多模态模型", "模仿学习"]
status: read
priority: 2
rating:
arxiv_id: "2609.19137"
arxiv_version: "v2"
version_updated_at: "2026-09-17"
doi: ""
paper_url: "https://arxiv.org/abs/2609.19137"
code_url: "https://dreamingcontactsound.github.io/"
pdf_path: "library/raw/2026/09/18/2609.19137.pdf"
text_path: "library/text/2026/09/18/2609.19137.txt"
sha256: "843e98d18700ab249840a7262c3f3ad3b3ce2d5614205e396d40abe5fdc3cef0"
pages: 8
citation_key: ""
related: ["[[notes/papers/2026/09/18/PointZero- 3D Point Track Completion for Learning Transferable 3D Dynamics]]", "[[notes/papers/2026/07/22/Agentic Real2Sim- Physics-based World Modeling with Vision-Language Agents]]", "[[notes/papers/2026/07/23/Robots Acquire Manipulation Skills in Seconds from a Single Human Video]]", "[[notes/papers/2026/08/31/Aero Hand Open- A Simulation-Ready Tendon-Driven Hand for Dexterous Manipulation Learning]]"]
cssclasses:
  - paper-note
---

# Dreaming the Sound of Contact: Leveraging Video and Audio Generation for Zero-Shot Force-Aware Manipulation and Data Generation

## 一句话结论

Dreaming the Sound of Contact v2 有力证明了“真实力反馈闭环 + 有界、渐进的参考力曲线”能把不精确的生成轨迹变成更可靠的接触操作：四任务成功率从无力补偿的 8/40 提到 36/40；但生成音频只决定单个 clip 内的**相对曲线形状**，绝对 3.75–15 N 范围由人工设定，且论文没有 matched smooth-ramp 基线，因此尚未隔离 audio 相对普通平滑起力曲线的独立因果贡献。

## 三分钟筛选

- **问题**：视频生成器能给出看似合理的操作轨迹，却没有显式接触力；毫米级几何误差就可能让擦拭、削皮、堆叠、按压完全失效。能否利用同步生成音频构造力曲线，再靠真实机器人反馈闭环执行？
- **新意**：从 Seedance 2.0 的生成 video 提取 EEF SE(3) 轨迹和接触方向，从分离后的 contact audio loudness 提取相对 force profile；用首帧真实 depth、标定与人工 force bounds 锚定到 Franka，再以 50 Hz force regulator 追踪参考力。
- **核心证据**：在四个任务、每任务 10 条 generation 的成对实验中，force-aware 为 Wiping 10/10、Peeling 9/10、Stacking 9/10、Pressing 8/10，总计 36/40；desired force 置零的 kinematic baseline 仅 0/10、5/10、3/10、0/10，总计 8/40（Table I，p. 5）。
- **与我的关系**：它把“生成世界”接到真实执行，说明开放环视觉轨迹必须经过可测外部状态闭环；与 PointZero 互补，但前者补 dense geometry，本文补 contact-force channel 的方向仍只是研究推断。
- **决定**：精读；最值得复现的是 audio-shaped、matched ramp、shuffled/reversed audio 与 constant profile 的四臂成对实验。

## 问题设定

- **输入、输出与目标**：输入初始 RGB `I0`、真实 depth `D0`、标定相机位姿、机器人初始 EEF pose 和结构化任务 prompt；生成同步 video/audio，经离线处理得到 EEF trajectory、contact direction 与 bounded force profile，最后由真实力反馈执行。
- **现有瓶颈**：生成视频的 3D pose 有尺度、深度和接触误差；纯 kinematic replay 不会补偿表面高度偏差；音频 loudness 不是经过标定的 Newton 力，执行又必须满足机器人安全阈值。
- **关键假设**：生成视频中的对象/夹爪可被可靠分割跟踪；接触声 loudness 的时间变化能提供有用的相对力形状；人工统一的 `Fmin/Fmax` 对四类任务足够；处理期间场景保持不变；Franka torque-derived force 足以作为控制反馈。

## 核心贡献

1. 构造 video-to-motion、audio-to-relative-force、geometry-to-direction 的多模型离线流水线，把生成结果锚定到真实相机和机器人坐标。
2. 用 1 kHz Cartesian impedance + 50 Hz force regulator 执行，而不是开放环回放生成动作；四任务成对实验直接显示接触反馈的重要性。
3. 用成功的真实 force-aware executions 收集每任务 50 条 demonstrations，并训练可带/不带 measured force input 的 Diffusion Policy，展示生成信号可辅助真实数据采集，但不是纯 synthetic policy data。

## 方法

### 直觉

生成视频擅长提供“往哪里、按什么时序移动”，同步声音或许提供“接触强弱怎样随时间变化”。二者都不够精确时，可以只把它们当 reference：真实 depth 负责度量锚定，几何负责力方向，人工边界负责绝对幅值，机器人 torque feedback 在执行时纠正轨迹误差。因而系统成功来自生成先验与经典反馈控制的组合，而不是让生成模型直接控制机器人。

### 形式化描述

- video 分支用 MolmoPoint 定位对象和 gripper、SAM 2 分割、TAPIP3D 估计 depth/3D tracks；首帧预测 depth 由真实 `D0` 拟合全局 scale + offset，再以 rigid alignment 恢复 gripper 相对 SE(3) trajectory，并锚定到实测初始 EEF pose（Equations 2–5、Figure 2，pp. 2–3）。
- audio 分支先用 SAM-Audio 分离 contact sound，低于 `-65 LUFS` 置零，再令 `r_t=2^(ℓ_t/10)`，把每个 clip 内的最小/最大值 min-max 映射到 `[F_min,F_max]`（Equations 6–7，pp. 3–4）。zero-shot 实验统一 `F_max=15 N`、`F_min=0.25F_max=3.75 N`。
- 因此 audio 只决定**相对时序形状**：任何非静音 clip 都被拉伸到相同绝对范围，不能解释为从声音估计 Newton 力。
- contact direction 由 gripper/object point cloud 的最近邻向量估计，距离小于 3 cm 才保留非零力；方向和 contact gating 都不是 audio 输出（Equations 8–10，p. 4）。
- 固定刚度 Cartesian impedance 以 1 kHz 运行，外层 force regulator 以 50 Hz 调整 reference trajectory；平移/旋转刚度为 `2000 N/m`、`150 N·m/rad`，积分增益 `K_I=0.0003`，Franka protective threshold 为 20 N（Equations 11–14，pp. 4–5）。

### 关键模块与训练流程

- Seedance 2.0 以固定相机 prompt 生成带同步音频的视频；结构化 prompt 要求显式接触动作和突出 contact sound。整个 perception/generation pipeline 离线运行，场景在处理期间不能变化。
- 执行时不录制或处理音频，也没有 online vision correction；控制器只追踪预先生成的 motion/force references，并用 Franka 关节力矩估计出的实时力闭环修正。
- zero-shot 轨迹 keyframe 为 4 Hz。Wiping、Peeling、Pressing 各直接使用 10 条 generation；Stacking 先生成 20 条，再按不可执行 grasp/EEF flip 的人工规则筛掉 10 条，即 50% generation 被排除（Section IV-A，p. 5）。
- policy data 阶段每任务保留 50 条**成功的真实机器人 rollout**，共 200 demos；每条记录 EEF pose、force profile 与两个 RGB views。Diffusion Policy 预测 16 个 absolute poses @10 Hz，执行前 8 个后重规划；测试时不再使用 force regulator（Section IV-D，pp. 6–7）。

### 计算与数据成本

- 硬件为 Franka Panda；外部相机 RealSense L515、腕部 D455；peeling 使用双臂布置（Figure 5，p. 6）。
- 论文未报告 Seedance API 费用/延迟、Molmo/SAM/TAPIP3D 推理成本、policy 训练 GPU/epoch/seed、完整处理时长或机器人总采集时间。
- 200 demos 只统计被保留的成功 executions；生成/执行总尝试数、失败和筛选成本未披露，因此不能把“自动数据生成”理解为零人工、零失败成本。

## 实验与证据

| 作者主张 | 对应证据 | 定位 | 我的判断 |
| --- | --- | --- | --- |
| force-aware execution 优于 kinematic replay | Wiping/Peeling/Stacking/Pressing 为 10/9/9/8 成功；desired force=0 baseline 为 0/5/3/0，总计 36/40 vs 8/40 | Table I，p. 5 | 强力支持真实力反馈闭环能吸收几何误差；baseline 完全没有接触补偿，不能单独归因于 audio |
| variable profile 比 constant step 更安全有效 | Wiping 的 variable 15N 为 10/10、constant 15N 为 2/10；Peeling 为 9/10 vs 6/10。constant 15N impulse 分别 30.28±6.32、106.42±61.97 N·s | Table II、Figure 4，pp. 5–6 | 支持渐进 profile 避免 initial-contact overshoot；缺 matched smooth ramp/shuffle/reverse，无法证明音频语义必要 |
| prompt 可控制相对敲击强弱顺序 | `(5N,20N)` 与 `(20N,5N)` 各 10 条，20 次中 18 次 loudness 顺序符合 prompt，两方向各 9/10 | Section IV-C，p. 6 | 只证明生成器遵循 prompt 的相对 loudness 顺序；没有真实 hammer force，不是 audio-to-force calibration |
| 生成轨迹可收集策略数据 | 4 tasks × 50 成功真实 rollout；无 force input policy 总计 29/40，有 measured 3D force input 为 34/40 | Table III、Section IV-D，pp. 6–7 | 支持小范围 task-specific data collection；仍依赖 200 条真实成功执行与真实力输入，不是纯生成数据 |
| force input 改善 policy | Wiping/Peeling/Stacking/Pressing 从 8/8/8/5 提到 9/10/8/7，每项 10 trials | Table III，p. 7 | 样本小、无多 seed/CI；peak/impulse 只在各自成功子集统计，不能作无偏安全对比 |

### 数据、基线与指标

- **数据集**：四类桌面接触任务；zero-shot 共 50 次原始 generation，其中 stacking 筛掉 10 条后评估 40 条；profile ablation 为 2 tasks × 4 profiles × 10 trials；policy 训练保留 4×50 条成功真实 rollout。
- **基线**：相同 motion trajectory、desired force 设零的 kinematic execution；force-profile ablation 比 variable 10/15N 与 constant 10/15N；policy 比带/不带 measured 3D force input。
- **指标**：外部相机人工判定的 task success；peak force、force impulse；hammer prompt 的 loudness ordering。没有 trajectory tracking error、direction error、audio-profile correlation 或独立安全事件统计。
- **预算/硬件**：真实机器人与传感器型号明确，但生成、处理、训练、执行时间和总成本不完整。
- **消融与稳定性**：有 constant-vs-variable 与 force-input ablation；没有 hand-designed ramp、shuffled/time-reversed audio、no-audio smooth profile、force-bound sweep、多随机种子或统计显著性检验。

## 批判性阅读

### 证据支持的结论

- 在给定四个固定任务上，真实力反馈闭环显著优于无接触补偿的运动学回放；`36/40 vs 8/40` 是全文最强、最直接的证据。
- 在 wiping/peeling 上，有界、渐进的 variable profile 能降低 step-like constant force 的接触 overshoot，并改善成功率或 impulse。
- 生成 video/audio 可以作为 reference 提议，再由真实 depth、标定、人工安全边界和反馈控制落地；这比把生成结果直接当可执行动作更可靠。
- 这套 pipeline 能收集可用于小规模 policy training 的真实演示；加入 measured force observation 在 40 次测试中把成功从 29 次提高到 34 次。

### 尚未被充分支持的结论

- 论文没有证明 audio 能估计绝对接触力：Newton 范围来自人工 `F_min/F_max`，loudness 只经 clip 内归一化控制相对形状。
- 没有证据证明 audio-shaped profile 优于任何平滑 ramp。作者观察到的主要机制正是“渐进上升避免 step overshoot”，但缺少能隔离声音信息的对照。
- 系统不是实时多模态闭环：video/audio 只在执行前离线处理；执行中没有听觉或视觉反馈，只有 torque-derived force feedback。
- “data generation”不是纯 synthetic data：policy 训练集来自 200 条成功的真实机器人执行，并可能有未报告的失败尝试与人工筛选。
- 任务成功不能直接外推到一般接触物理理解：对象、初始位置、任务和 force bounds 都较窄，policy 测试主要在训练位置范围内采样。

### 局限、风险与可能反证

- **弱 baseline**：kinematic baseline 的 desired force 为零，没有 compliance/ramp/视觉 servoing；巨大差距主要证明闭环 force regulation 的价值，无法唯一归因生成音频。
- **筛选偏差**：stacking 丢弃一半 generation；policy 只保留成功 rollout。未披露其他任务的隐性筛选、总尝试次数或失败分布。
- **音频归一化风险**：clip 内 min-max 会把轻微噪声和强接触都扩到同一力区间；SAM-Audio 分离错误或 LUFS outlier 可能产生不合理 profile。
- **方向与接触门限脆弱**：最近邻点云向量与 3 cm gate 受 depth、mask、遮挡影响；错误方向可能让 force controller 主动推向危险区域。
- **统计口径不一致**：Table II 包含失败 trials，Table III 的 peak/impulse 只统计成功 trials；带/不带 force policy 的成功集合不同，数值不可直接做 matched safety 结论。
- **复现参数不全**：低通滤波、lookahead `t_la`、gripper threshold、训练 recipe 和 seed 未披露；代码/数据尚未发布。

## 与已有知识的连接

- **基础论文**：Seedance 2.0 提供同步 video/audio；MolmoPoint、SAM 2、TAPIP3D、SAM-Audio 构成 perception pipeline；Diffusion Policy 学习 demonstrations。
- **相近方法**：[[notes/papers/2026/07/22/Agentic Real2Sim- Physics-based World Modeling with Vision-Language Agents]] 用显式物理模拟连接生成与执行；[[notes/papers/2026/07/23/Robots Acquire Manipulation Skills in Seconds from a Single Human Video]] 从单视频提取可执行技能；[[notes/papers/2026/09/18/PointZero- 3D Point Track Completion for Learning Transferable 3D Dynamics]] 学 dense 3D motion prior，但不建模接触力。
- **后续工作**：加入 matched ramp、shuffle/reverse 和 no-audio profile；学习任务/材料条件化的 force bound；把视觉/声音重新接入在线闭环；报告所有 generation、筛选与真实执行成本。
- **与主题笔记的关系**：[[notes/topics/结构化中间层与可验证执行]] 与 [[notes/topics/生成模型与机器人从表示到物理可用性]]；本文把 `video/audio → trajectory/direction/profile → feedback execution` 显式化，真实力测量是最终 verifier。

## 复现计划

- **是否复现**：待代码/数据发布；优先做判别性消融，不急于复刻整条生成 pipeline。
- **最小验证目标**：在 wiping 上固定同一组 10 条 motion trajectories，成对比较 audio-shaped、匹配起止值/平滑度的 hand-designed ramp、shuffled/time-reversed audio profile、constant 10N。
- **所需资源**：带可靠 torque/force sensing 的 compliant robot、相同 impedance/force controller、可重复的表面与任务、已导出的 trajectory/profile；不必先复现 Seedance 和所有感知模型。
- **成功标准**：同 controller、安全阈值和轨迹下，audio-shaped 在 success、peak、impulse、tracking error 上显著优于 matched ramp 与 shuffle/reverse；若只胜 constant step，应把贡献表述为 smooth force scheduling。

## 待追踪问题

- [ ] arXiv v2 对应的代码、dataset、prompt、controller 和处理配置何时公开？项目页目前仍显示 Coming Soon。
- [ ] `F_min/F_max` 如何跨材料、工具和任务选择？是否需要真实 calibration trial？
- [ ] audio-shaped profile 与 matched ramp、shuffle、reverse 的成对结果怎样？
- [ ] 50 条成功 rollout 分别需要多少生成和机器人尝试，筛选由谁完成？
- [ ] Table III 若对所有 trials 或相同成功集合统计 peak/impulse，结论是否保持？
- [ ] 加入 online visual/audio feedback 后，场景变化、滑移与方向误差能否被恢复？

## 原文定位

- 问题、系统总览与输入：Abstract、Sections I–III-A、Figure 1，pp. 1–2。
- video-to-motion 与真实 depth/pose 锚定：Section III-B、Figure 2、Equations 2–5，pp. 2–3。
- audio profile、direction 与 contact gate：Sections III-C–III-D、Equations 6–10，pp. 3–4。
- impedance/force controller：Section III-E、Equations 11–14，pp. 4–5。
- 四任务 zero-shot 与 force-profile ablation：Sections IV-A–IV-B、Tables I–II、Figures 3–4，pp. 5–6。
- hammer ordering 与 policy data generation：Sections IV-C–IV-D、Table III、Figure 5，pp. 6–7。
- 限制与结论：Sections V–VI，pp. 7–8。
- 项目页：https://dreamingcontactsound.github.io/（2026-09-18 的 Code/Dataset 仍为 Coming Soon）。
