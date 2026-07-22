---
type: paper
title: "AlayaWorld: Interactive Long-Horizon World Modeling - Full Technical Report"
aliases: []
authors: ["AlayaWorld Team", "Kaipeng Zhang", "Chuanhao Li", "Yifan Zhan", "Yongtao Ge", "Yuanyang Yin", "Jiaming Tan", "Kang He", "Liaoyuan Fan", "Mingliang Zhai", "Ruicong Liu", "Xiaojie Xu", "Xuangeng Chu", "Zhen Li", "Zhengyuan Lin", "Zhixiang Wang", "Zian Meng", "Zihui Gao"]
year: 2026
venue: "arXiv"
paper_date: "2026-07-20"
date_added: "2026-07-22"
last_read: "2026-07-22"
topics: ["世界模型", "生成模型", "语音、图像与视频", "推理与规划"]
status: read
priority: 1
rating: 3
arxiv_id: "2607.18367"
doi: ""
paper_url: "https://arxiv.org/abs/2607.18367"
code_url: "https://github.com/AlayaLab/AlayaWorld"
pdf_path: "library/raw/2026/07/2607.18367v1.pdf"
text_path: "library/text/2026/07/2607.18367v1.txt"
sha256: "ecfe162ed101f47d18e3be467ea93cb8b49077e62d390539fd5e6ecfea90ec64"
pages: 16
citation_key: ""
related: ["[[notes/papers/2026/Masked Visual Actions for Unified World Modeling]]", "[[notes/papers/2026/OmniReasoner- Thinking with Long Audio-Video via Native Tool Use]]"]
cssclasses:
  - paper-note
---

# AlayaWorld: Interactive Long-Horizon World Modeling - Full Technical Report

## 一句话结论

AlayaWorld 的强项是把短块自回归、全局 sink、压缩时间记忆、显式 3D warp 空间记忆、anti-drift training 和 4-step distillation 组合成完整交互视频系统；iWorld-Bench 上 8 项指标赢 7 项，但论文缺少组件消融、实际交互延迟和训练算力，且所谓“无限世界”目前只展示到 60 秒视觉 rollout，不能等同于持久状态或物理因果世界模型。

## 三分钟筛选

- **问题**：交互视频世界需要同时满足控制响应、回访一致性、长时稳定和低延迟；短视频扩散模型在自回归 rollout 中会积累模糊、亮度和几何漂移。
- **新意**：在固定长度 prefix 中组合四种记忆，并用模型自身 residual 构造 error bank，再将约 30-step teacher 蒸馏为 4-step student。
- **核心证据**：iWorld-Bench 上 brightness、color temperature、sharpness、motion、trajectory 与 memory 指标领先；长时定性视频展示至 60 秒。
- **与我的关系**：是交互式生成世界模型的系统路线代表，可与 MVA 的动作接口和显式物理 simulator 路线对照。
- **决定**：精读；保留为系统架构参考，但不把 benchmark 优势升级为“学会世界规律”。

## 问题设定

- **输入、输出与目标**：输入参考图像/视频、逐 chunk 相机轨迹和可切换文本 prompt；输出 24 fps、540p/720p 的持续视频流，每个 chunk 约 1 秒。
- **现有瓶颈**：短上下文无法记住远处场景；无限累积上下文成本增长；自生成历史带来 exposure bias；多步 diffusion 推理太慢。
- **关键假设**：单帧全局 anchor、近邻 frame、6 latent frames 的时间记忆和最多 10 个 warp 过往视图，足以支撑视觉身份、短期动力学和回访一致性。

## 核心贡献

1. 构建 bounded context 的 chunk-autoregressive world model，并显式融合 temporal 与 geometry-aligned spatial memory。
2. 用 Helios-style corruption 和模型 residual error bank 训练模型从自身 rollout 错误中恢复。
3. 组合 DMD、self-forcing++ 与 consistency distillation，把约 30 个采样步压到 4 步并保留控制与记忆栈。

## 方法

### 直觉

短期连续性、长期回访和场景身份不是同一种记忆问题：最近一帧负责视觉接缝，压缩窗口负责局部运动，3D warp cache 负责“离开后再回来”，固定 sink 负责全局身份。每次只带固定数量 token，因此时长增加时单 chunk 理论计算量不增长。

### 形式化描述

视频在 VAE latent 中分块为 $z_1,z_2,\ldots$，按 $p_\theta(z_{1:N}\mid\pi_{1:N},y_{1:N})=\prod_i p_\theta(z_i\mid z_{<i},\pi_{\le i},y_i)$ 生成。每个目标块的 prefix 为 $S_i=[s;h_i;g_i;n_i;z_i^\tau]$：sink $s$、时间记忆 $h_i$、空间记忆 $g_i$、最近帧 $n_i$ 和带噪目标。空间记忆将过去 RGB、单目深度和 camera pose 反投影到目标视角。参见 Section 3.1，Eq. (1)-(3)。

### 关键模块与训练流程

1. Backbone：公开 LTX-2.3 为 22B multimodal；移除 audio 后论文方法部分称约 13B video DiT，摘要又称 15B，参数口径不完全一致。
2. Stage 1：对 bidirectional video prior 做 full-parameter domain adaptation，最长 20 秒、24 fps、540p/720p。
3. Stage 2：先冻结 backbone 预训练 history compressor，再 full-stack fine-tune camera AdaLN、temporal/spatial memory、next-forcing head。
4. Anti-drift：对历史施加噪声、模糊、饱和度扰动，并回放模型自身按 chunk/noise bucket 存储的 reconstruction residual。
5. Stage 3：在 student 自己的多 chunk rollout 上做 DMD + self-forcing++ + consistency distillation，最终 4 steps/chunk。

### 计算与数据成本

- 训练语料 222,147 clips；最大来源是内部 GameVerse 124,116 clips，另有内部 MUGEN 21,436、生成式 GenEvent 6,490，以及 Sekai-Real、SpatialVid、RealEstate10K、DL3DV。
- GameVerse 单条约 66 秒，MUGEN 来源包含 YouTube；相机缺失时用 ViPE 恢复 pose。
- 论文没有披露训练 GPU 类型、数量、总 GPU-hours、batch size 或总训练时长。
- 推理从约 30 steps/chunk 降至 4 steps/chunk，但没有报告端到端 first-frame latency、实时倍率、显存或吞吐；“low latency”目前缺少直接证据。

## 实验与证据

| 作者主张 | 对应证据 | 定位 | 我的判断 |
| --- | --- | --- | --- |
| 长时 rollout 的视觉漂移更小 | brightness 0.9492、color temperature 0.9379、sharpness 0.8361，均明显领先 | Table 3；p. 11 | 对 iWorld-Bench 成立；缺少去掉 anti-drift/error bank 的消融，无法归因 |
| 相机控制准确 | motion smoothness 0.9924、trajectory accuracy 0.7985，均为表中最高 | Table 3；p. 11 | 支持 camera-conditioned navigation，但只在 benchmark prompt adaptation 后评估 |
| 空间/时间记忆改善回访一致性 | memory symmetry 0.8871、trajectory alignment 0.7018，领先 HY-World 1.5 的 0.8481 / 0.6776 | Table 3；p. 11 | 结果支持系统有效，但没有 spatial-only / temporal-only / sink ablation |
| 生成质量最佳 | 8 项指标中 7 项第一，但 Image Quality 0.6620，低于 HunyuanVideo-1.5 的 0.7128 | Table 3；p. 11 | 更准确的说法是“稳定性和控制最好”，不是静态画质最好 |
| 支持稳定无限生成 | bounded context 使每 chunk 计算量恒定；Figure 8 展示 0-60 秒 rollout | Section 3.1、Figure 8；pp. 8、13 | 计算复杂度可扩展不等于语义状态无限稳定；实证 horizon 仍短 |

### 数据、基线与指标

- **数据集**：七源 222,147 clips；评估使用 iWorld-Bench，并提到 WorldMark / World Model Arena。
- **基线**：NVIDIA Cosmos、HunyuanVideo-1.5、WAN 2.2、YUME 1.5、Matrix-Game 2.0、HY-World 1.5。
- **指标**：Image Quality、Brightness Consistency、Color Temperature Constraint、Sharpness Retention、Motion Smoothness、Trajectory Accuracy、Memory Symmetry、Trajectory Alignment。
- **预算/硬件**：训练成本未披露；评估使用 480p 初始帧和 distilled 4-step 模型，而产品能力宣称为 540p/720p。
- **消融与稳定性**：没有核心模块、数据、anti-drift 或 distillation ablation；没有置信区间、随机种子或人评样本数。

## 批判性阅读

### 证据支持的结论

- bounded memory + geometry warp 的系统在 iWorld-Bench 上具有很强的视觉稳定性、相机控制和回访指标。
- 4-step distilled student 在该 benchmark 上仍保持竞争力。
- 固定 prefix 使每 chunk 的 transformer context 大小受控，理论上避免随生成时长线性增长。

### 尚未被充分支持的结论

- 没有消融能证明 sink、temporal memory、spatial memory、error bank 和 self-forcing++ 各自必要。
- 没有实测延迟，因此不能确认达到实时交互；24 fps 是输出视频帧率，不等于生成吞吐 24 fps。
- “unbounded world”仅是计算结构上的可继续采样，未证明长时对象状态、任务目标或因果关系持久。

### 局限、风险与可能反证

- 作者在引言明确承认模型主要保存视觉 observation、估计 geometry 和 visual memory，对 object state、physical causality、long-term task structure 的理解有限（p. 2）。
- 3D warp 依赖单目深度和 camera pose；深度误差、动态物体和遮挡会污染长期 cache。
- 空间 memory 选择最多 10 帧，所谓“长期”仍会遗忘未覆盖或错误覆盖区域。
- 评估前自动把 benchmark instructions 改写成训练 prompt 风格，可能造成方法特有的 prompt advantage。
- 内部 GameVerse/MUGEN 占比高，数据细节、许可与可复现性弱；论文的 open-source 目标不等同于完整训练数据可用。
- 生成事件偏向可见后果，缺少可查询状态、碰撞约束和守恒规律，不能替代真实 simulator。

## 与已有知识的连接

- **基础论文**：LTX-2.3、GEN3C、Depth-Anything-3、Helios、DMD、Causal-rCM、self-forcing++。
- **相近方法**：Cosmos、YUME、Matrix-Game、HY-World、GameCraft、DIAMOND。
- **后续工作**：报告 latency/TCO；做 memory 与 anti-drift 消融；加入显式 object state、physics constraint 和 task memory。
- **与主题笔记的关系**：[[notes/topics/交互式世界模型与主动感知]]。

## 复现计划

- **是否复现**：待定；先做 checkpoint-level benchmark 与 latency audit。
- **最小验证目标**：在固定 480p/4-step 设置复跑 leave-and-return trajectories，并分别关闭 spatial memory、temporal memory 和 error-bank-trained checkpoint（若作者提供）。
- **所需资源**：公开代码/权重、iWorld-Bench、支持约 13-15B video DiT 的 GPU，以及 wall-clock profiler。
- **成功标准**：复现 Table 3 的主要排序；同时报告 sec/chunk、VRAM、生成/播放实时倍率和 5-10 分钟 rollout 的 drift 曲线。

## 待追踪问题

- [ ] 摘要 15B 与方法约 13B 的参数统计口径如何对应？
- [ ] 4-step 模型在 720p 下的真实 sec/chunk、显存和可交互延迟是多少？
- [ ] 如果关闭 prompt adaptation，iWorld-Bench 排名是否保持？
- [ ] 5 分钟以上回访时，geometry cache 的错误是否会自我强化？

## 原文定位

- 问题与边界：Section 1，pp. 1-2。
- 数据组成：Section 2、Table 1-2，pp. 3-5。
- Prefix 与记忆：Section 3.1、Figure 4、Eq. (1)-(3)，pp. 6-8。
- Anti-drift：Section 3.3、Eq. (4)-(6)，pp. 8-9。
- 4-step distillation：Section 3.4、Eq. (7)-(8)，pp. 9-10。
- 主结果：Table 3，p. 11。
- 交互、回访和 60 秒 rollout：Figure 5-8，pp. 12-13。
