---
type: paper
title: "Look Less, Think Faster: Joint Token-Compute Adaptation for Multimodal LLMs"
aliases: ["SmartVL"]
authors: ["Pengcheng Wang", "Zhiquan Wang", "Jayoung Lee", "Zhuoyan Xu", "Ran Xu", "Saurabh Bagchi", "Yin Li", "Somali Chaterji"]
year: 2026
venue: "ECCV 2026"
paper_date: "2026-07-22"
date_added: "2026-07-23"
last_read: "2026-07-23"
topics: ["多模态模型", "推理系统", "模型压缩与量化"]
status: read
priority: 1
rating: 3
arxiv_id: "2607.20357"
doi: ""
paper_url: "https://arxiv.org/abs/2607.20357"
code_url: "https://www.schaterji.io/publications/2026/jointtokencompute"
pdf_path: "library/raw/2026/07/23/2607.20357v1.pdf"
text_path: "library/text/2026/07/23/2607.20357v1.txt"
sha256: "cdf1314c14728f66a2461179258c21c6a19f6d09dd6edda477271d08c486f8d4"
pages: 18
citation_key: ""
related:
  - "[[notes/papers/2026/07/22/OmniReasoner- Thinking with Long Audio-Video via Native Tool Use]]"
cssclasses:
  - paper-note
---

# Look Less, Think Faster: Joint Token-Compute Adaptation for Multimodal LLMs

## 一句话结论

SmartVL 的核心判断是对的：多模态推理的视觉 token 数、LLM 深度和宽度共享同一 FLOPs 预算，应该按输入联合分配，而不是先剪 token、再独立剪层；LLaVA-1.5 上的 Pareto 结果支持它比 AdaLLaVA 更稳，但论文只优化/报告 prefill FLOPs，没有实测 latency、decode、训练成本或 sparse-kernel 加速，因此标题中的“Think Faster”目前主要是计算量代理而非部署速度结论。

## 三分钟筛选

- **问题**：token pruning、layer/head skipping 各自改变同一 prefill cost；独立固定比例会错配预算，例如图像信息多的样本需要 token，推理更难的样本需要 depth。
- **新意**：用共享 budget encoding 串联 vision token controller 与 LLM compute controller，联合控制 sequence、depth、head/FFN width；用 differentiable FLOPs estimator 和 asymmetric violation loss 训练一套连续预算模型。
- **核心证据**：LLaVA-1.5-7B 在约 50% FLOPs 下，VQAv2 74.4 vs AdaLLaVA 67.9、TextVQA 54.4 vs 29.8、VizWiz 55.1 vs 34.3；但 MMBench 为 62.0 vs 63.3，并非全任务绝对领先。
- **与我的关系**：它把 inference budget 从部署超参变成显式 conditioning signal，与主动感知“何时多看”和动态推理“何时多算”可统一理解。
- **决定**：方法值得跟踪，当前评 3/5；代码、训练 recipe、真实 latency 和 batch behavior 公布后再决定复现。

## 问题设定

- **输入、输出与目标**：给定 image $I$、text prompt $T$ 和目标 prefill compute ratio $b$，模型为每个样本决定保留哪些 visual tokens、执行哪些 LLM layers，以及激活多少 attention-head/FFN groups，在不超预算时最大化任务准确率。
- **现有瓶颈**：固定模型对所有输入计算相同；token-only 或 compute-only adaptation 忽略 sequence length 与 transformer depth/width 的乘法耦合；串联两个独立 controller 不能找到 content-dependent global optimum。
- **关键假设**：prefill FLOPs 与目标硬件 latency 足够相关；视觉 token、层和宽度存在可学习冗余；budget 可在 batch 内共享；跳层/稀疏 head-FFN 有可用 kernel 才能兑现 wall-clock 收益。

## 核心贡献

1. 把 visual sequence length、LLM depth 和 width 放进统一预算搜索空间，以内容与预算共同决定每个样本的 allocation。
2. 设计跨阶段 token-survival embedding：LLM controller 显式知道 vision stage 已花掉多少序列预算；Gumbel-sigmoid 允许激活数量自行变化而非固定 top-k。
3. 用可微 prefill FLOPs estimator、不对称超/欠预算损失和 inference-time projection，让单个模型覆盖约 20%-100% compute operating points。

## 方法

### 直觉

同样 4 TFLOPs，可以保留更多图像块但少跑几层，也可以少看图而深推理。最优分配随问题变化：POPE 更需要视觉覆盖，VQAv2/TextVQA 随预算增加更需要 LLM depth。SmartVL 把“看多少”和“想多久”交给同一预算条件下的联合 controller。

### 形式化描述

- Search space 为 retained visual sequence $S_{vis}$、effective layers $L_{eff}$ 与每层 active width $\alpha_l$；前 $P$ 个 prefix layers 始终执行，故最低预算 $b_{min}>0$（Section 3，pp. 5-6）。
- Vision controller 把 sinusoidal-encoded $b$ 作为 ViT budget token，与图像融合后输出 per-token logits；straight-through Gumbel-sigmoid 产生二进制 mask（Eq. 5-6，pp. 7-8）。
- LLM budget token 先经过固定 prefix，随后融合 stop-gradient 的 normalized token survival $\kappa$；controller 输出 layer mask（L）或 head-group + FFN group mask（LH）（Eq. 7，pp. 8-9）。
- 可微估计器计算每层 projection/FFN 的线性序列成本与 attention 的二次项，再加 vocabulary projection；以 $r=\hat C/C_{full}$ 对超预算做 quadratic penalty，对低于 $b-\mu$ 做 linear penalty（Eq. 8-10，pp. 9-10）。

### 关键模块与训练流程

- 训练每步从 $[b_{min},b_{max}]$ 均匀采样 budget，同一 batch 共用；vision encoder 冻结，projector、LLM 与 controllers 端到端更新。
- 正 bias 让网络从近 full capacity 开始；budget penalty 逐步 warm up，避免训练早期 controller collapse。
- 推理移除 Gumbel noise；soft loss 偶尔仍超预算，因此 deterministic projection 先丢最低置信 visual tokens，仍不够才减 layers/heads。
- SmartVL-L 只控制 token+layer depth；SmartVL-LH 再控制 head/FFN width。实验反而常见 L 更好，说明细粒度 width gating 不是免费收益。

### 计算与数据成本

- Backbone 为 LLaVA-1.5-7B/13B，vision encoder frozen；7B 在 7 个 benchmark，13B 只报告 VQAv2。
- 论文未披露训练数据配方、optimizer、steps、batch size、硬件、训练时长、controller 参数/开销或多 seed variance，复现信息不完整。
- 报告的“latency estimator”实际输出 analytical prefill FLOPs；没有 measured TTFT、tokens/s、端到端 latency、显存、能耗或不同 batch size 结果。

## 实验与证据

| 作者主张 | 对应证据 | 定位 | 我的判断 |
| --- | --- | --- | --- |
| 联合 token-compute 优于 compute-only | 约 50% FLOPs：VQAv2 74.4 vs AdaLLaVA 67.9；TextVQA 54.4 vs 29.8；VizWiz 55.1 vs 34.3 | Figure 1、3，Section 4.2，pp. 3、11-12 | 低预算优势很强；主要来自 AdaLLaVA 在其最低 operating point 崩塌 |
| 相比 naive sequential 组合更稳 | VQAv2 50%：SmartVL 74.4 vs AdaLLaVA-PruMerge 74.5，70%：75.7 vs 约 75.4；GQA 50% 59.8 vs 60.1 | Figure 1、3，pp. 11-12 | 不总是逐点领先，可信结论应是更宽连续预算范围/整体 Pareto，而非每点 SOTA |
| 不同任务需要不同 token-depth 分配 | POPE 偏 $(T=0.8,C=0.5)$；VQAv2/TextVQA 到 7T 偏 $(0.9,0.8)$；相同 4T 下换分配会改变答案 | Figure 6-7，Section 4.4，pp. 13-14 | 支持联合搜索动机，但图中是 dataset/task 案例，未量化 per-sample oracle gap |
| 更细的 width control 不一定更好 | TextVQA 50% SmartVL-L 54.1，高于 sequential 51.3 和 AdaLLaVA 29.8；L 通常优于 LH，full budget 58.1 vs 57.5 | Figure 5，p. 13 | 反直觉但重要：冗余主要在 sequence/depth，head/FFN width 可能损伤 representation |
| 可扩展到 13B | VQAv2：SmartVL 75.45@7.25T，AdaLLaVA 72.27@8.27T；11.56T 时 77.66 vs 76.45@11.57T | Figure 8，p. 15 | 支持架构可移植，但只有单 benchmark，不等于规模泛化充分 |

### 数据、基线与指标

- **数据集**：zero-shot lmms-eval 的 VQAv2、GQA、TextVQA、ScienceQA、POPE、VizWiz、MMBench。
- **基线**：compute-only AdaLLaVA；token-only FastV、LLaVA-PruMerge+；sequential AdaLLaVA-PruMerge；各自扫 retention configuration 形成 Pareto envelope。
- **指标**：官方 task metric 与平均 analytical prefill FLOPs；图标题写 Accuracy-Latency，但正文实际使用 FLOPs。
- **预算/硬件**：7B 约 2.5T-8.5T 的范围；未报告训练/推理硬件和实测时间。
- **消融与稳定性**：token-only controller、L vs LH、task-level optimal allocation、13B scaling；缺 controller/budget-loss 组件消融、seed、budget compliance distribution 与 latency calibration。

## 批判性阅读

### 证据支持的结论

- 多模态 prefill 的 token 与 LLM capacity 是耦合资源，联合 controller 在低/中预算通常比只减 LLM compute 更稳。
- 单个 budget-conditioned model 可以覆盖连续 operating points，避免为每个数据集手调固定 token/layer ratio。
- Width gating 的自由度未带来稳定增益；先优化 sequence 和 depth 是更稳妥的工程优先级。

### 尚未被充分支持的结论

- 没有 measured latency，因而没有证明“Think Faster”；FLOPs 下降能否转成 TTFT 下降取决于稀疏 kernel、launch overhead、batching 和硬件。
- 没有优化 autoregressive decode；长回答场景中 decode 的 memory bandwidth/KV cache 成本可能主导端到端时延。
- 只在较旧的 LLaVA-1.5 架构上验证，不能直接外推到 native-resolution、multi-image/video、MoE 或 reasoning MLLM。

### 局限、风险与可能反证

- Inference projection 会先额外丢 visual tokens 来“严格合规”，预算控制与学习策略并非完全一致；边界样本可能在 projection 后突然失真。
- 训练时 dropped token 仍以 zeroed static tensors 保持 shape，训练效率未必随 sparsity 提升；论文只讨论推理潜力。
- Batch 内共享 budget 但 allocation 仍按样本变化，真实 serving 中不同 mask 可能造成 divergence，难以获得理论 FLOPs 对应的吞吐。
- LLM、projector 也被端到端更新，却没有披露训练 recipe；full-budget 变化可能来自再训练而非 controller 本身。
- 七个 benchmark 多为短答案单图 VQA；缺生成质量、长输出、OCR dense image、视频和 hallucination safety 的详细 failure analysis。

## 与已有知识的连接

- **基础论文**：LLaVA-1.5、FastV、LLaVA-PruMerge+、AdaLLaVA、Gumbel-sigmoid conditional computation。
- **相近方法**：token pruning、early exit、dynamic depth、head/FFN structured sparsity、MoE routing。
- **后续工作**：decode-aware controller、实测 hardware cost model、batch-friendly routing、KV cache/quantization 联合优化、现代 MLLM 验证。
- **与主题笔记的关系**：[[notes/topics/交互式世界模型与主动感知]]；SmartVL 把“观察预算”和“思考预算”统一为显式条件，但尚未像 OmniReasoner 一样允许真实追加观察。

## 复现计划

- **是否复现**：待代码和 recipe 后做推理侧小规模复现。
- **最小验证目标**：在 LLaVA-1.5-7B 上复核 50% budget 的 VQAv2/TextVQA，并在 A100/H100 测 analytical FLOPs、dense-mask 实现、稀疏 kernel 的 TTFT 和吞吐。
- **所需资源**：公开权重/代码、lmms-eval、至少单张大显存 GPU、可记录 CUDA traces 的 profiler。
- **成功标准**：accuracy/FLOPs 接近论文，且实际 TTFT 随预算近似单调下降；报告 projection 触发率与其 accuracy 损失。

## 待追踪问题

- [ ] FLOPs 与 TTFT 在不同 GPU、batch size、输入分辨率下的相关系数是多少？
- [ ] Budget projection 多常触发，丢 token 后的真实 compute/accuracy 偏差多大？
- [ ] 若只用 token+depth 的 SmartVL-L，能否删去 width controller 而取得更简单、更快的系统？
- [ ] 把 decode length、KV cache 和量化也放进 budget state 后，最优 allocation 会怎样变化？
- [ ] 在 Qwen-VL、InternVL、视频 MLLM 上，sequence/depth redundancy 的结论是否仍成立？

## 原文定位

- 问题、贡献与 VQAv2 Pareto：Figure 1、Section 1，pp. 1-4。
- 统一 search space 与 budget constraint：Section 3，pp. 5-7。
- Vision token controller：Section 3.1、Eq. (5)-(6)，pp. 7-8。
- LLM compute controller：Section 3.2、Eq. (7)，pp. 8-9。
- FLOPs estimator、budget loss 与 projection：Section 3.3、Eq. (8)-(10)，pp. 9-10。
- 七 benchmark 主结果：Figure 3、Section 4.1-4.2，pp. 11-12。
- Token/L-LH/分配消融：Figure 4-7、Section 4.3-4.4，pp. 12-14。
- 13B 与作者承认的部署缺口：Figure 8、Section 4.4-5，p. 15。
