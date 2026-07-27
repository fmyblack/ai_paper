---
type: paper
title: "3D-Aware VLMs with Implicit and Explicit Geometries"
aliases: ["VLM-IE3D"]
authors: ["Wenhao Li", "Xueying Jiang", "Quanhao Qian", "Deli Zhao", "Ran Xu", "Shijian Lu", "Gongjie Zhang"]
year: 2026
venue: "arXiv"
paper_date: "2026-07-23"
date_added: "2026-07-27"
last_read: "2026-07-27"
topics: ["多模态模型", "语音、图像与视频", "推理与规划", "机器人"]
status: read
priority: 2
rating:
arxiv_id: "2607.21595"
doi: ""
paper_url: "https://arxiv.org/abs/2607.21595"
code_url: "https://github.com/Vegetebird/VLM-IE3D"
pdf_path: "library/raw/2026/07/27/3d-aware-vlms.pdf"
text_path: "library/text/2026/07/27/3d-aware-vlms.txt"
sha256: "861448281662aa40d5cab4b4c7d28d8313b641dbf953a55229beeb8717bf4af9"
pages: 20
citation_key: ""
related: []
cssclasses:
  - paper-note
---

# 3D-Aware VLMs with Implicit and Explicit Geometries

## 一句话结论

VLM-IE3D 把 RGB 视频中的粗粒度隐式几何 token 与由深度/点图/3D Gaussian 重建得到的细粒度显式几何 token，通过 implicit-explicit cross-attention 和 2D token addition 融入 Qwen2.5-VL-3B；在 3D 检测、grounding、captioning 和 VSI-Bench 上优于 RGB-only 基线，但仍依赖冻结的 AnySplat 3D 几何编码器、特定数据训练和重建质量，不能简单等价于“VLM 已从纯 RGB 获得真实 3D”。

## 三分钟筛选

- **问题**：多数 2D VLM 或只使用粗粒度 implicit 3D representation，难以做定量位置、尺度和关系推理；显式 point/depth 输入又需要专用 3D 传感器。
- **新意**：同一 RGB 视频同时取 Implicit Geometry Tokens（IGTs）和 Explicit Geometry Tokens（EGTs），用轻量显式 embedding 与 IEA adapter 组合全局先验、局部几何和 2D 语义。
- **核心证据**：3D video detection F1@25 从 Qwen2.5-VL-3B 的 30.9 提升到 42.8；ScanRefer 无 proposal refinement 的 Acc@0.25 为 43.2，RGB-only 方法中领先；VSI-Bench 平均 47.6，高于 VG LLM-4B 的 47.3（Tables 1–5）。
- **与我的关系**：它是“显式中间表示补足隐式世界模型”的视觉实例，与主动感知、机器人空间推理和多模态表示融合相连。
- **决定**：作为 3D-aware VLM 工程基线保留；复现优先做 IGT/EGT/IEA 消融和重建误差敏感性，不只复现 headline score。

## 问题设定

- **输入、输出与目标**：输入 RGB video sequence 与自然语言 query；输出 3D captions、3D boxes、first-frame grounding 或空间推理答案。
- **现有瓶颈**：隐式 token 有全局布局但难解释定量几何；显式几何结构精确但可能昂贵、缺少语言语义。
- **关键假设**：AnySplat 从 RGB 视频重建的深度/相机/point/gaussian 属性足够可靠；轻量 embedding 能保留可用坐标信息；冻结几何 encoder 的先验可迁移到下游任务。

## 核心贡献

1. IGTs：从 AnySplat fusion decoder 读取高层、全局 3D spatial priors。
2. EGTs：将 depth maps、camera poses、point maps 或 3D Gaussian splats 经过 one-layer patch embedding + two-layer MLP 编为细粒度显式 token。
3. 3D-aware adapter：IGT 作为 query、EGT 作为 key/value 做 multi-head cross-attention，再与压缩后的 2D token 相加。

## 方法

### 直觉

论文将 IGT 类比为粗略的“3D cognitive map”，将 EGT 类比为带数量和局部结构的“3D reconstruction map”。前者负责全局关系和泛化，后者把精确位置、尺度和深度显式暴露给语言模型。

### 形式化描述

从视频得到 T_2D、T_I、T_E，2×2 空间合并后得到压缩 token。对每帧：

T_3D^i = T̃_I^i + MCA(T̃_I^i, T̃_E^i, T̃_E^i)

最终 T_3D = T̃_2D + T̃_3D（Eq. 1–3，pp. 6–7）。

### 关键模块与训练流程

- backbone：Qwen2.5-VL-3B；geometry encoder：AnySplat；2D 和 3D geometry encoder 冻结。
- VLM backbone 与 explicit embedding 可训练；Adam，一 epoch，warmup ratio 0.03，peak LR 1e−5。
- 输入裁剪 392×518，最多 32 frames，patch size 14，token channel 2048，压缩后 m=252。
- 默认 EGT 使用 depth map；另测 point map、3D Gaussian；first frame 为参考坐标（3D grounding 例外使用 frame-local coordinates）。

### 计算与数据成本

- 训练使用 8× H100 80G，batch size 1/GPU。
- VLM-IE3D 约 3.23B trainable parameters，VG LLM 3.13B；单 H100 速度 6 FPS vs. 7 FPS。
- 显式 embedding 只增加约 0.008B 参数；但 AnySplat 的推理和重建成本没有单独拆出。

## 实验与证据

| 作者主张 | 对应证据 | 定位 | 我的判断 |
| --- | --- | --- | --- |
| RGB-only 3D dense captioning 有竞争力 | Scan2Cap C@0.5=80.4，超过 Qwen2.5-VL-3B 58.0、VG LLM 78.6；M@0.5=28.8 | Table 1，p. 8 | 支持；但 object proposals 使用 LEO 的 Mask3D detections，输入管线不是完全端到端 |
| 3D visual grounding 改善 | Acc@0.25/0.50=43.2/16.9；proposal refinement 后 55.4/48.9 | Table 2，p. 9 | 无 refinement 时领先 RGB-only；refinement 对结果贡献很大，需分开解读 |
| 3D video detection 改善 | P25/R25/F125=44.2/41.9/42.8，较 baseline F1 +11.9，较 VG LLM F1 +4.6 | Table 3，pp. 9–10 | 消融和主比较一致，核心证据较强 |
| 空间推理提升 | VSI-Bench average 47.6，VG LLM-4B 47.3；object count 67.5 | Table 4，p. 10 | 平均优势很小，单项优势更有信息但仍需统计重复 |
| IGT/EGT 互补 | baseline F1 30.9；+EGT 34.7；+IGT 40.5；+IGT+EGT 42.8 | Table 5，p. 12 | 支持互补，但 IGT 单独贡献明显更大 |
| IEA 是最佳融合 | concat 41.5、addition 42.4、weighted 41.2、IEA 42.8 | Table 6，p. 12 | 有消融支持；增益相对小，尚未说明跨数据集稳定性 |
| 轻量显式 embedding 优于 deep encoder | None 40.5、Deep Encoder 35.9、VLM-IE3D 42.8 | Table 8，p. 13 | 有趣但可能受训练/冻结设置影响，不能泛化为深 encoder 本身无用 |

### 数据、基线与指标

- **数据集**：Scan2Cap、ScanRefer、EmbodiedScan 派生 3D video detection、VSI-Bench；空间推理训练使用 SPAR-7M 子集与 LLaVA-Video-178K 子集。
- **基线**：Qwen2.5-VL、VG LLM、SPAR、Video-3D LLM、LLaVA-3D，以及若干带 3D input 方法。
- **指标**：caption C@0.5/M@0.5、grounding Acc@0.25/0.50、detection P/R/F1@0.25、VSI-Bench average。
- **预算/硬件**：Qwen2.5-VL-3B；8 H100 80G；one epoch；冻结 encoder。
- **消融与稳定性**：IGT/EGT、fusion、explicit attribute、embedding、geometry encoder 多组消融，但没有多 seed 置信区间。

## 批判性阅读

### 证据支持的结论

- 细粒度显式几何 token 确实在 implicit-only baseline 之上提供增益，且 IGT 与 EGT 联合最好。
- 轻量、直接的坐标 embedding 比额外堆深度视觉 encoder 更适合作为 IGT 的互补信息，至少在该训练设置下如此。
- 方法在检测、grounding、captioning 和 spatial reasoning 四类任务方向一致，说明不是单一 metric 的偶然增益。

### 尚未被充分支持的结论

- “无需额外 3D inputs”是输入接口意义上的 RGB-only，不等于无需 3D 先验：AnySplat 仍由大规模 3D 任务预训练。
- VSI-Bench average 仅比 VG LLM 高 0.3，不能单独证明一般空间推理大幅提升。
- 各任务分别训练模型，不能说明同一个 joint model 在所有场景同时保持优势。

### 局限、风险与可能反证

- AnySplat 的重建误差、相机漂移和室外/动态场景失效没有系统敏感性实验。
- Scan2Cap 使用预检测 object proposals，ScanRefer 的 proposal refinement 会显著改变 absolute score。
- 只在 Qwen2.5-VL-3B、8 H100 和一个训练 epoch 上评估，没有 scaling law 或低算力复现。
- 几何 token 与视频帧数、分辨率、推理延迟的实际 trade-off 未完整披露。

## 与已有知识的连接

- **基础论文**：Qwen2.5-VL、VG LLM、AnySplat、VGGT、Video-3D LLM。
- **相近方法**：3D-LLM、PointLLM、Scene-LLM、SPAR。
- **后续工作**：加入重建不确定性 token；在动态/室外/机器人视频上做 noise stress test；分离 geometry encoder inference cost。
- **与主题笔记的关系**：[[notes/topics/交互式世界模型与主动感知]]；[[notes/topics/跨视角监督、辅助信号与模型行为]]

## 复现计划

- **是否复现**：待定
- **最小验证目标**：在 3D video detection 上复现 baseline、+IGT、+EGT、+IEA 四组，记录 AnySplat 预处理误差与 FPS。
- **所需资源**：VLM-IE3D code/model、Qwen2.5-VL-3B、AnySplat、EmbodiedScan 派生数据、至少 2 张 H100 等价 GPU。
- **成功标准**：F125 相对 baseline 的增益在不同随机种子和重建质量扰动下保持，且报告每条 pipeline 的时间成本。

## 待追踪问题

- [ ] 只给 noisy depth/pose 时，EGT 是否仍帮助，还是会把错误几何放大？
- [ ] 在真实机器人视频中，IGT/EGT 是否能改善 action grounding，而不仅是离线 3D benchmark？
- [ ] EGT 是否可用稀疏深度或低成本估计替代 AnySplat 全量重建？

## 原文定位

- 动机与框架：pp. 1–4，Figures 1–2。
- IGT/EGT 与 adapter：pp. 5–7，Figure 3、Eq. (1)–(3)。
- 训练设置与主任务：pp. 7–11，Tables 1–4。
- 组件消融：pp. 12–14，Tables 5–9。
