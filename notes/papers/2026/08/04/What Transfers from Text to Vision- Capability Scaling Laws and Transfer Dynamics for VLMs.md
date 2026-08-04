---
type: paper
title: "What Transfers from Text to Vision? Capability Scaling Laws and Transfer Dynamics for VLMs"
aliases: []
authors: ["Ziran Li", "Qiang Wang", "Zhengyu Chen", "Shanglin Lei", "Borun Chen", "Jingang Wang", "Xunliang Cai"]
year: 2026
venue: "arXiv"
paper_date: "2026-06-24"
date_added: "2026-08-04"
last_read: "2026-08-04"
topics: ["多模态模型", "能力迁移", "缩放规律", "Benchmark 与评估方法"]
status: read
priority: 2
rating:
arxiv_id: "2608.00013"
doi: ""
paper_url: "https://arxiv.org/abs/2608.00013"
code_url: "https://github.com/wangq-dev/CDMScaling"
pdf_path: "library/raw/2026/08/04/2608.00013v1.pdf"
text_path: "library/text/2026/08/04/2608.00013v1.txt"
sha256: "81931d993afbbb97af791d5e07fc12164a38b48fff369a1285cd13191d51f36e"
pages: 24
citation_key: ""
related: []
cssclasses:
  - paper-note
---

# What Transfers from Text to Vision? Capability Scaling Laws and Transfer Dynamics for VLMs

## 一句话结论

这篇论文的核心价值不是又给 VLM 刷了一个 benchmark，而是把“选哪个 LLM 做 VLM backbone”从经验试错改写成一个可拟合的能力迁移问题：用 200+ 文本 benchmark 经 PCA 得到文本能力分数 `S`，再用 transfer rate 与 absorption rate 预测多模态训练轨迹。证据规模很大（34 个 LLM、150+ 个 VLM、35 个多模态 benchmark、25,000 H800 GPU-days），但结论目前主要适用于 LLaVA-OneVision 式 late-fusion、固定视觉编码器的训练配方；不能直接外推到 native multimodal / early-fusion 模型。

## 三分钟筛选

- **问题**：VLM 训练里最关键的设计之一是选择 LLM backbone，但传统 compute/parameter scaling law 跨模型家族失效，无法回答“某个文本模型能力会怎样迁移到视觉语言任务”。
- **新意**：把可观察的文本 benchmark 表现压缩成低维 capability score `S`，用 `P = A*S + (B0 - Bm*S) ln Dmm + P0` 同时建模文本能力 transfer 和多模态数据 absorption。
- **核心证据**：能力驱动 loss fitting 将跨家族 MAE 从 compute-based 的 0.0383 降到 0.0087；平均多模态准确率预测 MAE 约 1.287%；Qwen2.5-72B holdout 轨迹 MAE 约 1.193%。
- **与我的关系**：它是多模态模型选型、训练预算规划和“文本能力到底迁移什么”的强证据基线，也能补充 [[notes/topics/多模态能力迁移与缩放规律]]。
- **决定**：已精读；优先跟踪代码/数据公开质量，暂不做完整复现。

## 问题设定

- **输入、输出与目标**：输入候选 LLM backbone 的文本 benchmark 矩阵 `X`、多模态训练数据量 `Dmm`；输出 VLM 多模态 benchmark accuracy 或训练 loss trajectory 的预测。
- **现有瓶颈**：参数量 `N` 不能表示预训练数据、训练策略、家族差异和 instruction tuning 后的真实能力；相同参数规模模型的 VLM loss trajectory 可以显著不同。
- **关键假设**：文本 benchmark 的低秩结构可代表 LLM latent capability；固定视觉编码器和统一训练配方下，LLM backbone 是主要可变因素；下游多模态准确率对文本能力和 `ln Dmm` 可近似线性分解。

## 核心贡献

1. 提出 Capability-Driven Multimodal Scaling Law，用文本 benchmark PCA 后的 `S` 替代参数量，跨家族预测 VLM loss 与 accuracy trajectory。
2. 引入 transfer / absorption 解释框架：`A*S` 表示文本能力直接迁移，`(B0 - Bm*S) ln Dmm` 表示多模态数据吸收效率及其随文本能力变化的衰减。
3. 给出三类实践洞察：存在 transfer tax benchmark；base LLM 在大数据 regime 下通常比 instruct LLM 更适合作 VLM backbone；不同模型家族位于不同 transfer-absorption tradeoff。

## 方法

### 直觉

参数量只是模型外壳；VLM 真正继承的是 LLM 已形成的知识、推理、语言结构和表示几何。作者用文本 benchmark 直接量测这种能力，再观察它在统一 VLM 训练配方中如何被视觉数据“接上”和“继续吸收”。

### 形式化描述

- 文本 benchmark-model 矩阵 `X in R^{T x M}` 先中心化，再做 PCA，取能解释至少 95% 方差的 top-K components。
- 每个模型的低维 capability vector 为 `S_m`，标量能力分数 `S = w^T S_m`，`w` 与下游 scaling law 联合优化。
- loss 形式：`L = A e^{-alpha S} + B / Dmm^beta + E`，用于把 classical scaling law 的 `N` 替换成可观测能力。
- accuracy 形式：`P = Ahat*S + Bhat*ln Dmm + P0`，其中 `Bhat = B0 - Bm*S`。
- 单个文本 benchmark 的有效迁移系数为 `lambda_i = w^T gamma_i`；`Ahat*lambda_i < 0` 被定义为 transfer tax。

### 关键模块与训练流程

- **Backbone 集合**：34 个 LLM，覆盖 Qwen3、Qwen2.5、Falcon3、Llama-3.2、Gemma-2、Mistral、DeepSeek，0.6B 到 72B，base/instruct 成对覆盖。
- **VLM 架构**：统一使用 LLaVA-OneVision，SigLIP vision tower、two-layer MLP projector、language backbone。
- **训练数据**：Infinity-MM 子集；Stage 1 约 5M samples，仅训练 projector；Stage 2 约 12M samples，全模型微调。
- **评估**：200+ 文本 benchmark，35 个多模态 benchmark，Average Multimodal Accuracy 为主指标。
- **拟合**：PCA 取 3 个主成分解释 95%+ 方差；performance predictor 用 Huber loss、absorption 非负 soft penalty、Differential Evolution + L-BFGS-B。

### 计算与数据成本

- **训练总量**：作者在结论中披露总计约 25,000 H800 GPU-days。
- **训练配置**：Stage 1 batch size 512、LR 1e-3；Stage 2 batch size 512、LR 1e-5；视觉分辨率 384，Stage 2 使用 AnyResMax-9。
- **成本判断**：证据强但复现门槛极高；个人层面的复现应优先复现拟合流程和小规模数据，而不是重训 150+ VLM。

## 实验与证据

| 作者主张 | 对应证据 | 定位 | 我的判断 |
| --- | --- | --- | --- |
| 参数量/compute-based scaling law 跨家族不够 | Falcon3/Llama-3.2 loss fitting：compute-based 需要分家族拟合且误差高；换成 capability score 后跨家族 MAE 0.0383 -> 0.0087 | Section 3.3, Figure 1, pp. 5-6；Appendix A.2, Figure 7, pp. 16-17 | 支持较强；但仍在 late-fusion recipe 内验证 |
| 文本能力可预测 VLM 多模态 accuracy trajectory | 32 个 backbone 的 accuracy fitting MAE 1.287%；Qwen2.5-72B holdout trajectory MAE 1.193% | Section 3.4, Figures 2-3, pp. 5-7 | 是本文最强主证据；holdout 是大规模但仍只一个家族/scale 外推 |
| absorption term 需要随能力变化 | 对 `S > 0.6` 的 72B 外推，加 `Bm*S` 后 Base MAE 2.374% -> 2.055%，Instruct 0.476% -> 0.394% | Table 1, p. 7 | 效果方向成立，但改善幅度有限，需看更大 heldout 集合 |
| 某些文本 benchmark 是 transfer tax | `boolean_expressions_hard` -0.078、`contextual_param_knowledge_conflicts` -0.048、`mnist_ascii` -0.043 等负系数 | Section 4.1, p. 8；Table 7, p. 22 | 很有启发，但“benchmark gaming”是作者解释，尚未被机制实验直接证明 |
| Base LLM 在大数据 VLM 训练中优于 Instruct | Instruct 初始 transfer slope 更高（0.254 vs 0.212），但 absorption decay 1.33x 更高；Base 平均 absorption 0.0161 vs Instruct 0.0147 | Section 4.2, Table 2, p. 8 | 支持“alignment tax”假说，但因果来源仍需表示/训练消融 |
| 家族之间有 transfer-absorption tradeoff | Llama 高 transfer 低 absorption；Qwen3 低 transfer 高 absorption；Gemma/Falcon3 介于其间 | Section 4.3, Table 3, pp. 8-9 | 对 backbone 选型有用；但只覆盖有限开源家族 |
| capability metric 可推 hyperparameter | 最优 batch size 随 `A*S + (B0 - Bm*S) ln Dmm` 增长；Qwen2.5-72B 预测 batch size 2663/4194 | Section 4.4, Figure 5, pp. 9-10 | 更像应用示例，证据弱于主 scaling law |

### 数据、基线与指标

- **文本 benchmark**：200+ 项，分 Knowledge、Language、Math、Reasoning、NLI/NLU、Information Extraction；Appendix Table 5 列出具体代表项。
- **多模态 benchmark**：35 项，分 General VQA、STEM Puzzle、Document Understanding、Alignment；Appendix Table 6 列出 MMBench、MMStar、MMMU、MathVista、DocVQA、HallusionBench、POPE 等。
- **基线**：compute/parameter-based scaling law；不加 capability-modulated absorption 的 ablation；leave-one-family-out 验证。
- **指标**：training loss MAE、Average Multimodal Accuracy MAE、holdout MAE、transfer coefficient `lambda_j`。
- **预算/硬件**：25,000 H800 GPU-days；150+ VLM training runs；未见完整 seed 方差报告。
- **消融与稳定性**：≤8B vs 72B absorption ablation、Qwen2.5-72B holdout、Qwen3/DeepSeek/Falcon3/Gemma-2 leave-one-family-out。

## 批判性阅读

### 证据支持的结论

- 用可观测文本能力替代参数量，确实能改善 late-fusion VLM 的跨家族性能预测。
- LLM-to-VLM transfer 不是单一“越强越好”：文本能力有正迁移、负迁移和饱和维度。
- instruction tuning 可能带来 multimodal data absorption 的效率损失；在大数据训练 regime 下 base backbone 更值得优先考虑。
- backbone 家族的 transfer/absorption profile 比参数量更接近实际选型变量。

### 尚未被充分支持的结论

- “负系数 benchmark = benchmark gaming”仍是作者解释；论文没有直接干预某项文本能力来证明它挤占视觉对齐空间。
- scaling law 在 early-fusion/native multimodal、可训练视觉编码器、视频/多图长上下文等设置下尚未验证。
- hyperparameter extrapolation 只做了 batch size 小集合实验，不能当成通用训练配置搜索替代品。
- 论文用 35 个 benchmark 的平均分做主目标；如果应用关注 OCR、数学、图表或安全幻觉，单个子域可能偏离平均规律。

### 局限、风险与可能反证

- **架构边界**：所有实验基于 LLaVA-OneVision late-fusion；作者明确把 early-fusion/native mixed-modal 作为未来工作。
- **视觉端边界**：SigLIP vision tower 固定，未建模视觉 encoder 容量、分辨率、动态视频和多图 token budget 的 co-scaling。
- **数据边界**：Infinity-MM 子集和统一 recipe 有助于隔离变量，但也可能让 law 学到该配方的特定偏差。
- **统计边界**：大规模训练覆盖很多 backbone，但 holdout 大模型主要看 Qwen2.5-72B；API/闭源家族、不同数据质量和多 seed 方差不足。
- **元数据注记**：PDF 页脚与 arXiv API 均显示 `24 Jun 2026`，但本次由 2026-08-04 arXiv new/list 发现；笔记保留原文 paper date，不把列表日期写成论文日期。

## 与已有知识的连接

- **基础论文**：Kaplan scaling laws、Chinchilla/Hoffmann scaling laws、LLaVA、LLaVA-OneVision、SigLIP、Infinity-MM。
- **相近方法**：OpenCompass 的 text/multimodal leaderboard correlation、native multimodal scaling laws、downstream task performance scaling。
- **相关论文**：[[notes/papers/2026/08/03/ReLoop-UME- Recurrent Depth with Learnable Retrieval Registers for Universal Multimodal Embedding]] 关注多模态 embedding 的深度计算分配；本篇关注 LLM backbone 到 VLM 的训练轨迹预测。
- **与主题笔记的关系**：[[notes/topics/多模态能力迁移与缩放规律]]、[[notes/topics/跨视角监督、辅助信号与模型行为]]。

## 复现计划

- **是否复现**：待定，优先复现拟合和公开数据一致性，不优先重训 VLM。
- **最小验证目标**：下载作者公开 text benchmark / VLM trajectory 表，重现 PCA、`S`、Eq. (7) 拟合、Table 1/2/3 的关键系数方向。
- **所需资源**：作者 repo、benchmark score CSV、训练 checkpoint trajectory；本地 CPU 即可验证拟合，重训小 VLM 需 GPU。
- **成功标准**：复现 MAE 量级（约 1.3% accuracy MAE）和三个定性结论：transfer tax、Base/Instruct absorption gap、family tradeoff。

## 待追踪问题

- [ ] 作者 repo 是否包含全部 34 backbone 的文本分数、VLM trajectory、训练配置和随机种子？
- [ ] 如果只用更少、更稳定的文本 benchmark，`S` 是否仍能预测多模态表现？
- [ ] 对 instruction-tuned 模型做 visual alignment 前的 representation probe，能否直接观察到作者所说的 alignment tax？
- [ ] OCR / document / math / hallucination 子指标是否各自需要不同的 `lambda_j`，而不是一个 Average Multimodal Accuracy？
- [ ] early-fusion 或 native multimodal 模型是否仍可用文本-only `S` 解释，还是必须加入视觉 encoder / tokenization 指标？

## 原文定位

- 元数据与摘要：Abstract, p. 1；arXiv 页脚 `2608.00013v1 [cs.CL] 24 Jun 2026`。
- 模型定义：Eqs. (1)-(9), Sections 2.1-2.2, pp. 2-4。
- 训练设定：Sections 3.1-3.2, p. 5；Appendix C, Tables 4-8, pp. 19-22。
- 主结果：Figures 1-4、Table 1, pp. 6-8。
- transfer tax：Section 4.1, p. 8；Table 7, p. 22。
- Base/Instruct 与家族差异：Sections 4.2-4.3, Tables 2-3, pp. 8-9。
- hyperparameter extrapolation：Section 4.4, Figure 5, pp. 9-10。
- 限制：Limitations, p. 10。
