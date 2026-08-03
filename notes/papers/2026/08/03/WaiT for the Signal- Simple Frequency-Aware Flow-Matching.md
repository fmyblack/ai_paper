---
type: paper
title: "WaiT for the Signal: Simple Frequency-Aware Flow-Matching"
aliases: []
authors: ["Krunoslav Lehman Pavasovic", "Théophane Vallaeys", "Stéphane Mallat", "Giulio Biroli", "Luke Zettlemoyer", "Brian Karrer", "Jakob Verbeek"]
year: 2026
venue: "arXiv"
paper_date: "2026-07-30"
date_added: "2026-08-03"
last_read: "2026-08-03"
topics: ["生成模型", "多模态模型", "推理系统", "图像与视频"]
status: read
priority: 2
rating:
arxiv_id: "2607.28760"
doi: ""
paper_url: "https://arxiv.org/abs/2607.28760"
code_url: ""
pdf_path: "library/raw/2026/08/03/2607.28760v1.pdf"
text_path: "library/text/2026/08/03/2607.28760v1.txt"
sha256: "1defbfb2ad799c4dc838c82df9e409b1d7c3945c2c22e48d23b3d2b14153cc7b"
pages: 35
citation_key: ""
related: []
cssclasses:
  - paper-note
---

# WaiT for the Signal: Simple Frequency-Aware Flow-Matching

## 一句话结论

WaiT 的贡献是用一个很小的先验改动解决高分辨率生成里的频率时序错配：低频先去噪，高频在信号还不可辨时保持纯噪声，等粗结构出现后再加入联合 refinement。它在 ImageNet 512、OpenImages 1024 和视频上同时提升质量/算力 Pareto，但部分结论依赖新指标与自建高分辨率数据，视频实验也主要在较低分辨率 FVD 口径下验证。

## 三分钟筛选

- **问题**：标准 flow matching 对所有空间频率使用同一噪声时间表，早期在高频完全无信号时仍花算力处理 full-resolution tokens；常规 FID 又会下采样，低估局部纹理差异。
- **新意**：用 lossless DWT 分离 LF/HF，设置 HF delayed schedule `t_HF=max(0,(t_LF-t*)/(1-t*))`；采样先在 LF 低分辨率空间跑，再注入 HF 噪声并联合去噪。
- **核心证据**：ImageNet 512 上 WaiT-H/16 397 GFLOPs 达到 FID 1.43、5cFID 1.63、hFWD 0.67；WaiT-G/16 822 GFLOPs 达到 pixel-space FID 1.30。Kinetics-600 上 WaiT-XL/8 FVD 0.84，GFLOPs/102 为 1,110。
- **与我的关系**：它和 ReLoop-UME 都说明“效率优化不是少算，而是按信号结构重新排布计算”。
- **决定**：精读；复现先从 ImageNet 256 的 schedule/normalization 消融开始。

## 问题设定

- **输入、输出与目标**：在 pixel-space flow matching 中生成高分辨率图像/视频；目标是同时改善全局结构、局部细节、纹理 fidelity 与采样 compute。
- **现有瓶颈**：uniform schedule 忽略高频在早期被噪声淹没的事实；cascade/pyramid 方法常有 train-test mismatch 或架构复杂性；FID 299x299 下采样会抹掉高频差异。
- **关键假设**：图像自然频谱存在稳定层级，HF mutual information 在早期接近 0；DWT 提供无损、可逆、无需训练的频率分解；低频先形成能帮助高频恢复。

## 核心贡献

1. 提出 Wavelet-aware image Transformer：只改噪声 schedule 和少量 conditioning，不需要复杂多分支架构。
2. 提出三轴评估：FID 看全局 coherence，5-crop FID 看 native-resolution 局部细节，hFWD 看高频纹理。
3. 在 class-conditional 图像、1024 文生图和视频生成中展示更好的质量/compute tradeoff，并验证方法可迁移到 latent space 和多层 DWT。

## 方法

### 直觉

早期粗结构还没出来时，高频纹理几乎只是噪声。与其让模型在 full-resolution 上反复“看噪声”，不如先用低频带建立结构，等到 `t*` 后再把高频带接进来做联合细化。这个思路像渐进式图像编码，但被写进 flow-matching 的时间表。

### 形式化描述

- 单层 2D DWT 把图像分成 `x_LF in R^{D/4}` 与 `x_HF in R^{3D/4}`，IDWT 可无损还原。
- LF 使用标准线性 schedule：`t_LF=t`；HF 使用延迟 schedule：`t_HF=max(0,(t_LF-t*)/(1-t*))`。
- 当 `t_LF <= t*` 时，`t_HF=0`，HF 仍是单位高斯噪声；在采样时恰好于 `t*` 注入新 HF 噪声，避免 discontinuous cascade 的 train-test mismatch。
- LF band 用训练集绝对 LF 系数的 p95 做归一化，HF 保持原尺度，保留自然稀疏性。

### 关键模块与训练流程

- **Coarse objective**：模型在 normalized LF band 上训练，`t ~ U[0,1]`，即使采样中 coarse 只运行到 `t*`；作者发现 full-range coarse training 更好。
- **Fine objective**：`t>t*` 时在 pixel space 预测图像，再 DWT 分解预测结果，用 band-specific weighting 同时监督 LF/HF。
- **Sampling**：Phase 0 只跑 LF，token 数减少 4x；Phase 1 用 IDWT 合并 LF/HF 并 full-resolution 联合去噪。
- **Resolution conditioning**：加入 resolution scalar embedding，让同一架构区分不同去噪阶段/分辨率。

### 计算与数据成本

- ImageNet 512：WaiT-H/16 397 GFLOPs，WaiT-G/16 822 GFLOPs；相对 JiT-H/16 810 GFLOPs、JiT-G/16 1665 GFLOPs 大幅省算。
- 文生图：构造约 40M 张 1024 分辨率训练图像，来自 SA-1B、DataComp Multimodal、OpenImages，并用 Qwen3-VL / Llama 3.2 Vision 等做 caption enrichment。
- 视频：Taichi-HD 约 3k videos；Kinetics-600 约 450k videos；128x128 和 256x256 设置。

## 实验与证据

| 作者主张 | 对应证据 | 定位 | 我的判断 |
| --- | --- | --- | --- |
| delayed HF schedule 是主要收益来源 | ImageNet 256 cumulative ablation：naive two-stage FID 7.51；delayed linear 5.43；global coarse 3.81；`t*=0.25` 3.57 | Figure 4，p. 6 | 消融清楚，尤其 train-test mismatch 解释有说服力 |
| ImageNet 512 上质量/compute Pareto 强 | WaiT-H/16 397 GFLOPs FID 1.43、5cFID 1.63、hFWD 0.67；WaiT-G/16 822 GFLOPs FID 1.30、5cFID 1.45、hFWD 0.59 | Table 2，p. 7 | 主结果强；和 latent models 比较时要注意训练数据/架构差异 |
| 相对 JiT，WaiT 可用约一半 compute 达到相近或更好质量 | JiT-H/16 810 GFLOPs FID 1.70、5cFID 3.30；WaiT-H/16 397 GFLOPs FID 1.43、5cFID 1.63 | Table 2，p. 7 | 最公平的对照是同 backbone JiT，证据很强 |
| 1024 文生图可迁移且吞吐提升 | 两个 encoder/caption pipeline 下 WaiT-H/32 均接近或优于 JiT；imgs/s 从 0.10->0.29 或 0.12->0.28 | Table 3，p. 8 | 支持工程可迁移，但数据管线很重，且文本对齐指标提升幅度不大 |
| 视频生成也受益 | Kinetics-600 128x128：WaiT-B/8 FVD 1.45 vs JiT-B/8 1.50，GFLOPs/102 210 vs 300；WaiT-XL/8 FVD 0.84 vs JiT-XL/8 0.89 | Tables 4–6，p. 9 | 趋势一致；但作者也承认 FVD 低分辨率下看不到高频纹理 |
| 方法容易扩展 | 3-level OpenImages 1024 savings 33%，5cFID/hFWD 改善但 FID 9.74->10.11；WaiT+DDT 512 FID 1.33 vs DDT 1.28，5cFID 1.77 vs 1.98，GFLOPs 329 vs 525 | Tables 7–8，p. 10 | 说明思路通用但非免费：全局 FID 可能略退，需要调 Pareto |

### 数据、基线与指标

- **数据集**：ImageNet-1k 256/512；作者从 OpenImages V6 构造 native 512/1024 子集；文生图 40M 高分辨率数据；Taichi-HD、Kinetics-600。
- **基线**：JiT 是主要同架构基线；另对比 DiT/SiT/RAE/DDT/SiD2/Pixel DiT 等。
- **指标**：FID、5cFID、hFWD；文生图另有 CLIP、GenEval、DPG、imgs/s；视频使用 FVD、LPIPS、GFLOPs。
- **预算/硬件**：论文报告 GFLOPs 和 throughput，训练资源细节在附录；文生图数据构建成本较高。
- **消融与稳定性**：schedule、`t*`、coarse training range、LF normalization、wavelet family、multi-level DWT、latent transfer；部分 extension 只跑一次且未调参。

## 批判性阅读

### 证据支持的结论

- 频率特定的噪声时间表能更好匹配自然图像的信号形成顺序。
- 单层 DWT 让 Phase 0 token 数减少 4x，是质量和算力同时改善的核心。
- FID 单独不足以评估高分辨率纹理；5cFID/hFWD 对 WaiT 的收益解释更完整。

### 尚未被充分支持的结论

- hFWD 和 5cFID 虽经 PIPAL 相关性验证，但是否能覆盖所有高分辨率生成质量仍需更多人评和任务评估。
- 文生图和视频使用相对基础的 baseline 配置，和最强商业/开源生成系统的差距不清楚。
- multi-level 和 latent-space 扩展只做 out-of-the-box 试验，尚不能说明最佳 Pareto 边界。

### 局限、风险与可能反证

- 作者明确说当前主要使用单层 DWT；更深层 coarse compression 能否保留足够 fine recovery signal 未知。
- 视频实验主要是 128x128，标准 FVD 无法体现高频纹理，削弱了“频率优势迁移到视频”的证据。
- OpenImages 512/1024 子集和文生图 40M 数据集是作者自建，数据过滤、captioning 和近无损 JPEG 处理会影响可比性。
- latent transfer 中 WaiT+DDT 的 FID 略差于 DDT baseline，说明低频/高频调度并非所有设置都无代价。

## 与已有知识的连接

- **基础论文**：Flow Matching、JiT、PixelFlow、Pyramidal Flow、DWT/JPEG 2000、FID/FWD。
- **相近方法**：[[notes/papers/2026/08/03/ReLoop-UME- Recurrent Depth with Learnable Retrieval Registers for Universal Multimodal Embedding]] 也通过结构化调度额外计算提升效率。
- **相关主题**：生成模型、推理系统、高分辨率图像/视频生成、频率域建模。
- **与主题笔记的关系**：[[notes/topics/结构化中间层与可验证执行]]。

## 复现计划

- **是否复现**：待定。
- **最小验证目标**：用 ImageNet 256 小模型复现 schedule ablation：standard JiT、naive two-stage、delayed linear、global coarse、`t*` sweep。
- **所需资源**：JiT baseline 代码、DWT/IDWT 实现、ImageNet 256 或公开小规模替代集、FID/5cFID/hFWD 计算脚本。
- **成功标准**：delayed linear 明显优于 naive two-stage，并在相近 FID 下减少 GFLOPs；同时人工检查高频样例，避免只优化 hFWD。

## 待追踪问题

- [ ] 作者是否公开 WaiT 代码、OpenImages manifest 和 hFWD/5cFID 统计文件？
- [ ] `t*` 是否可按图像类别、分辨率或采样步数自适应？
- [ ] 更深 DWT 层数能否在不损害 FID 的前提下继续省算？
- [ ] 在强 latent diffusion / rectified flow 系统上，WaiT 是否仍能保持 Pareto 优势？
- [ ] 高分辨率视频上能否建立类似 5cFID/hFWD 的纹理评估，而不是只看 FVD？

## 原文定位

- 动机与三轴指标：Abstract、Figures 1–3、Introduction，pp. 1–3。
- DWT 和 frequency-specific schedules：Section 3.1，p. 4。
- 训练目标与采样：Sections 3.2–3.3、Table 1，p. 5。
- 设计消融：Figure 4，p. 6；Appendix Tables 12–16，pp. 20–23。
- ImageNet 512 主结果：Table 2，p. 7。
- 文生图结果：Table 3，p. 8。
- 视频结果：Tables 4–6，p. 9。
- multi-level / latent transfer 与局限：Tables 7–8、Limitations，p. 10。
- 结论：Conclusion，p. 11。
