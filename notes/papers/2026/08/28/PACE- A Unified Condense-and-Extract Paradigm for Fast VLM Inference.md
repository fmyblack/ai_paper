---
type: paper
title: "PACE: A Unified Condense-and-Extract Paradigm for Fast VLM Inference"
aliases: []
authors: ["Junjie Liu", "Shengyuan Ye", "Xu Chen"]
year: 2026
venue: "arXiv"
paper_date: "2026-08-27"
date_added: "2026-08-28"
last_read: "2026-08-28"
topics: ["多模态模型", "VLM", "推理加速", "视觉token"]
status: read
priority: 1
rating:
arxiv_id: "2608.27206"
doi: ""
paper_url: "https://arxiv.org/abs/2608.27206"
code_url: "https://github.com/jjL357/PACE"
pdf_path: "library/raw/2026/08/28/2608.27206v1.pdf"
text_path: "library/text/2026/08/28/2608.27206v1.txt"
sha256: "e0c084e0f086116048e7e903cd3c12d38037b435ddda7c2ccce73dca0a760ec2"
pages: 22
citation_key: ""
related: []
cssclasses:
  - paper-note
---

# PACE: A Unified Condense-and-Extract Paradigm for Fast VLM Inference

## 一句话结论

PACE 是一个 training-free 的双阶段 VLM 推理压缩框架：APC 在 ViT 编码前按全局冗余/局部细节自适应缩放像素，DDAE 在编码后融合 LLM 语义注意力与 ViT 视觉注意力选 token；在 Qwen2.5-VL-7B 固定分辨率、保留 10% visual tokens 时保留 93.8% 平均性能并将 TTFT 从 365.89ms 降至 116.79ms（3.13×），但 query-agnostic 缩放可能丢失微小文字，收益依赖 backbone 和分辨率。

## 三分钟筛选

- **问题**：高分辨率 VLM 的视觉编码和 LLM prefill 都是瓶颈；只在 encoder 后 pruning 只能减少后半段计算，并会丢失 OCR/图表细节。
- **新意**：把 pre-encoder pixel condensation 与 post-encoder dual-attention extraction 统一为 Condense-and-Extract；无需训练新参数。
- **核心证据**：Qwen2.5-VL-7B 九任务 Table 1、RTX 4090 延迟 Table 2、APC 正交性 Table 3、DDAE 深度 Table 4、InternVL3.5-4B 跨 backbone 附录结果。
- **与我的关系**：连接现有 VLM scaling/多模态推理效率主题；可与 ReLoop-UME 的“中间层/固定 workspace”对比。
- **决定**：精读；适合做单卡 inference 复现。

## 问题设定

- **输入、输出与目标**：输入高分辨率图像和文本 query；APC 输出自适应缩放图像，DDAE 输出 top-K visual tokens，目标是在固定 token budget 下最大化视觉任务性能并降低 TTFT（§1、§3，pp.1–5）。
- **现有瓶颈**：Qwen2.5-VL 4K 图像可产生超过 42,000 ViT patches、池化后仍超过 10,500 visual tokens；后置 pruning 对 encoder cost 无能为力，低预算下 ChartQA/DocVQA 显著退化（Figure 2–3，p.2）。
- **关键假设**：ViT 第一 block 的浅层特征足以估计信息密度；局部离群 token 代表细节；LLM/ViT 注意力标准差可作为无监督置信度代理。

## 核心贡献

1. APC：用全局 token 相似度 `ρ_g=1−φ` 和 top-10% 局部对比度 `ρ_d`，按 `ρ=αρ_g+(1−α)ρ_d` 调整输入分辨率（式(1)–(6)，pp.4–5）。
2. DDAE：从第 `L_ext` 个 LLM 层提取语义 attention，与 ViT self-attention 融合；两者标准差经 temperature softmax 得到动态权重，再保留 top-K（式(7)，p.5）。
3. 两阶段互补：APC 降低 ViT encoder token 数，DDAE 降低 LLM prefill token 数；APC 也可正交叠加 VisionZip/MMTok（§5.1，p.8）。

## 方法

### 直觉

先把“整张图里明显重复的像素”压掉，但保留连续 2D 布局；再根据 query 语义和视觉边界共同决定哪些编码 token 进入 LLM。只看语义会漏掉未被文字提及的图表线条，只看视觉会留下无关背景。

### 形式化描述

APC 的全局相似度为所有归一化 preview token 的平均 pairwise cosine；局部项取相对全局均值 baseline 距离最大的 10% token 的距离均值，并用 `γ` 截断。DDAE 的 token 分数 `S_final=α_weight S_llm+β_weight S_vis`，`[α_weight,β_weight]=softmax([σ_llm,σ_vis]/τ)`（§3.2–3.3，pp.4–5）。

### 关键模块与训练流程

默认 Qwen 配置：APC preview depth `K=1`、`α=0.6`、`γ=1.5`；DDAE `L_ext=2`、`τ=0.5`。整个 pipeline training-free，直接插入现有 Qwen2.5-VL/InternVL 推理流程（§4.1，p.6）。

### 计算与数据成本

评测覆盖 MME、POPE、MMBench、MMStar、RealWorldQA、TextVQA、DocVQA、ChartQA、OCRBench 九个数据集；主表为 Qwen2.5-VL-7B 固定分辨率，另测 3B 和 InternVL3.5-4B。单 RTX 4090、10% retention：encoder 148.84→49.47ms（3.01×），prefill 217.05→32.69ms（6.64×），含 APC overhead 的 TTFT 365.89→116.79ms（3.13×）（Table 2，p.8）。自回归 decode 不加速。

## 实验与证据

| 作者主张 | 对应证据 | 定位 | 我的判断 |
| --- | --- | --- | --- |
| 低预算下保持更高质量 | 10% token：PACE 平均 93.8% of Vanilla；比 VisionZip/FastV 高 12.7/13.9 个百分点 | Table 1，p.6；§4.2 p.7 | 支持较强，但主要来自 Qwen2.5-VL-7B 固定分辨率 |
| 同时降低 encoder 与 prefill | encoder 3.01×、prefill 6.64×、TTFT 3.13× | Table 2，p.8 | 测量完整且含 preview overhead；不等于端到端生成吞吐提升 |
| APC 可与后置 pruning 正交组合 | VisionZip/MMTok + APC 在 10%/5% 对 ChartQA、OCRBench、DocVQA 均明显提升 | Table 3，p.8 | 支持模块独立价值；仍需更多 backbone/分辨率验证 |
| 动态双注意力优于单一信号 | Only LLM-Attn 在 ChartQA 下降超 10 分；DDAE 整体更平衡 | Figure 7，p.9 | 支持机制解释，但 attention standard deviation 只是 proxy |

### 数据、基线与指标

- **数据集**：九个视觉/多模态 benchmark；固定分辨率与 dynamic-resolution 两种设置（§4.1，p.6）。
- **基线**：FastV、SparseVLM、DivPrune、DART、VisionZip、MMTok；另有 PACE w/o APC。
- **指标**：任务准确率/F1/MME P+C/DocVQA ANLS、visual-token retention、encoder latency、prefill latency、TTFT。
- **预算/硬件**：Qwen2.5-VL-3B/7B、InternVL3.5-4B；延迟在单 RTX 4090 测量。
- **消融与稳定性**：APC feature、`α`、top-detail percentile、DDAE attention source/depth、动态 vs 静态 resolution、跨 backbone（Appendix B，pp.14–20）。

## 批判性阅读

### 证据支持的结论

- 在 10% retention，PACE 对 OCRBench/DocVQA 的退化明显小于传统 post-encoder pruning；5% 仍保持优势，但绝对性能下降。
- DDAE extraction depth 是明确的质量-延迟旋钮：Qwen 7B 在 layer 2 prefill 35.26ms/2.11×，layer 24 为 68.12ms/1.09×（Table 4，p.9）。
- InternVL3.5-4B 的 25%/20%/10% retention normalized average 比最佳基线高 5.1/4.7/4.0 分，说明方法可迁移但速度收益仍架构相关（Appendix B.3，p.14）。

### 尚未被充分支持的结论

- “保留 93.8% 性能”是九任务宏平均相对值，不代表每个细粒度 OCR/图表任务都接近无压缩模型；DocVQA 仍明显低于 Vanilla。
- 训练-free 不等于零成本：浅层 preview 有约 34.62ms overhead，且需要访问模型内部 attention。
- 论文没有测 decode 阶段、并发吞吐、能耗或多图/视频长上下文收益。

### 局限、风险与可能反证

- APC 是 query-agnostic、one-shot resize；微小字符、细线、低对比度物体一旦在缩放中模糊，DDAE 无法恢复（Limitations，p.10）。
- 在 fixed-grid VLM 上 APC 可能无法减少 encoder token，只剩 DDAE 的 prefill 收益；preview/encoder speedup 依赖分辨率和 backbone。
- `α=0.6` 是经验平衡点：α=1 偏全局会伤害关系/逻辑推理，α=0.2 偏局部会伤害整体布局（Appendix B.1，p.15）。
- 反证路径：细小文字、低对比度图、超高分辨率、多语言 OCR、动态视频，以及不同视觉编码器下做 matched-resolution 对比。

## 与已有知识的连接

- **基础论文**：ViT、Qwen2.5-VL、FastV、VisionZip、MMTok、SparseVLM。
- **相近方法**：ReLoop-UME（中间层循环与固定 registers）、动态分辨率 VLM、视觉 token pruning/merging。
- **后续工作**：query-conditioned pre-encoder condensation、可恢复多尺度 crop、端到端训练的 compressor、video token streaming。
- **与主题笔记的关系**：[[notes/topics/多模态能力迁移与缩放规律]]、[[notes/topics/结构化中间层与可验证执行]]。

## 复现计划

- **是否复现**：是（低成本 inference 复现）。
- **最小验证目标**：在 Qwen2.5-VL-7B、DocVQA/TextVQA/ChartQA/OCRBench 上复现 10% retention 的质量与 TTFT；分别关闭 APC、DDAE。
- **所需资源**：单张 24GB+ GPU、Qwen2.5-VL 权重、lmms-eval、PACE 代码、固定 batch/分辨率和计时脚本。
- **成功标准**：质量曲线方向与 Table 1 一致；TTFT 含 preview overhead 后仍显示约 3× 级别收益；记录 GPU、CUDA、batch、warm-up 与样本数。

## 待追踪问题

- [ ] APC 能否改为 query-conditioned 多尺度 crop，避免 one-shot 丢小字？
- [ ] 在 fixed-grid backbone 上，DDAE 与 KV/cache 优化的收益如何叠加？
- [ ] 视觉 token 压缩是否改变模型的错误类型，而不仅是平均分？

## 原文定位

- Page / Section / Figure / Table / Equation：Figure 2–3 p.2；Figure 4 p.4；式(1)–(7) pp.4–5；Table 1 pp.6–7；Table 2 p.8；Table 3–4 pp.8–9；Figure 7 p.9；Limitations p.10；Appendix B pp.14–20。
