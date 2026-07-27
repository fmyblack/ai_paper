---
type: paper
title: "MIRROR: Learning from the Other View for Multi-Modal Reasoning"
aliases: []
authors: ["Wen Ye", "Yuxiao Qu", "Aviral Kumar", "Xuezhe Ma"]
year: 2026
venue: "arXiv"
paper_date: "2026-07-23"
date_added: "2026-07-27"
last_read: "2026-07-27"
topics: ["多模态模型", "推理与规划", "强化学习", "Benchmark 与评估方法"]
status: read
priority: 2
rating:
arxiv_id: "2607.21552"
doi: ""
paper_url: "https://arxiv.org/abs/2607.21552"
code_url: ""
pdf_path: "library/raw/2026/07/27/mirror.pdf"
text_path: "library/text/2026/07/27/mirror.txt"
sha256: "693f73717fd6c8e38714639ac6794bf2151ff2e381bb3b72d789fa933fa7e7c5"
pages: 27
citation_key: ""
related:
  - "[[notes/papers/2026/07/23/Look Less- Think Faster- Joint Token-Compute Adaptation for Multimodal LLMs]]"
cssclasses:
  - paper-note
---

# MIRROR: Learning from the Other View for Multi-Modal Reasoning

## 一句话结论

MIRROR 把同一几何题的文本、图像和图文联合视图之间的成功/失败不一致，转成按题目自适应的教师信号，在 Qwen3-VL-4B 上以约 2K 个筛选样本提升单视图几何推理与跨视图一致性；但 ODA-Data 本身按“模态不对称”筛选，且方法比普通 GRPO 多约 37.5% 更新 FLOPs，因此它首先证明的是一种有针对性的 RL 训练信号，而不是一般视觉推理能力已被解决。

## 三分钟筛选

- **问题**：同一底层几何结构换成文本主导、图像主导或图文联合输入后，VLM 可能只在某一个视图成功；普通混合模态 RL 不会自动把强视图的推理迁移给弱视图。
- **新意**：构造保持问题身份的 ODA-Data，并用 MIRROR 为每题选择当前 rollout 最强的视图作为教师，再对受限视图学生的 on-policy 轨迹施加 reverse-KL；教师采用 EMA 稳定目标。
- **核心证据**：ODA-Val 图像 pass@16 从基础模型 42.57 提升到 57.06，文本 pass@16 从 80.22 提升到 86.10；GeoInt pass@16 从 70.79 提升到 78.38；双视图都可解比例从 42.5% 升到 60.7%（Table 2，Figure 4）。
- **与我的关系**：它为“多模态失败案例是训练信号”提供了一个可复用的 RL 形式化，和已有多模态 token/compute 自适应工作互补。
- **决定**：保留为多模态 RL 的重要方法基线；值得复现自适应教师、EMA 和计算匹配消融，暂不把 ODA-Val 的提升外推到非几何任务。

## 问题设定

- **输入、输出与目标**：每个问题有 text-dominant、image-dominant、combined 三种视图；模型从受限视图生成解题轨迹，最终答案由 verifier 判断，指标为各视图 pass@k 和跨视图共同可解率。
- **现有瓶颈**：图像视图需要恢复对象和空间关系，文本视图则依赖语言中显式给出的关系；两者的错误路径互补，但标准 RL 只看到稀疏最终答案。
- **关键假设**：不同视图语义等价；最终答案可可靠验证；某个视图的高质量 rollout 能为另一视图的 token 分布提供有用但不泄漏输入信息的指导。

## 核心贡献

1. ODA-Data：从 ODA-Math-460k 过滤困难题、生成并验证 TikZ 图，保留约 2K 个视图不对称例子，按 85:15 分为 ODA-Train/Val（pp. 4）。
2. MIRROR：每题在三视图中选择最强教师，学生只在 text/image 受限视图采样；教师仅重评分学生已采样轨迹。
3. 证明自适应教师、模态不对称样本和 EMA 目标共同贡献了效果，而非简单混合模态 GRPO。

## 方法

### 直觉

视图间的不一致不是单纯的鲁棒性缺陷：图像有时揭示结构，文本有时消除视觉 grounding 错误，图文联合视图又能同时验证关系。MIRROR 将“哪个视图这一次做对了”作为题目级教师选择。

### 形式化描述

对问题 x 的视图集合 M(x)，先从每个视图采样 rollout 并按最终答案选最强视图 j⋆(x)。受限学生视图 m 的目标为：

L = L_GRPO + λ_KL L_rKL

其中 L_rKL 在学生自己采样的 y 上，比较学生视图与教师视图对同一 token 的 log-probability（Eq. 1–2，pp. 6）。教师项 stop-gradient，教师参数按 θ̄ ← αθ̄ + (1−α)θ 更新，默认 α=0.99（Eq. 3，p. 6）。

### 关键模块与训练流程

- 基础模型：Qwen3-VL-4B-Instruct；实现基于 verl。
- 每题评估 text、image、combined 视图，按当前 rollout 结果选择 teacher；student 只使用 text 或 image 视图。
- reverse-KL 系数 λ_KL=0.01；GRPO response 上限 16,384 tokens，temperature 0.8。
- EMA 不是装饰项：当前策略直接作为 teacher 会在约 90 steps 后熵与 reference KL 上升并崩溃，EMA teacher 在约 290 steps 仍稳定（Figure 5，p. 10）。

### 计算与数据成本

- ODA-Train 约 2K 样本；单视图/混合视图 GRPO 使用同一数据量。
- MIRROR 每次更新约比普通 mixed-modality GRPO 多 37.5% FLOPs；作者用 step 150 对比 GRPO step 200 做近似计算匹配（p. 8）。
- 训练配置披露了 RL 超参，但没有给出完整硬件小时或美元成本。

## 实验与证据

| 作者主张 | 对应证据 | 定位 | 我的判断 |
| --- | --- | --- | --- |
| MIRROR 优于单视图和混合视图 GRPO | ODA-Val image pass@16 57.06，text pass@16 86.10；对应最强单视图 48.78/83.16，mixed 45.68/81.66 | Table 2，p. 7；Section 6.1，p. 8 | 支持较强，但需注意 MIRROR 的更新 FLOPs 更高 |
| 迁移能泛化到外部几何集 | GeoInt pass@16 78.38，较基础模型 70.79 提升 7.59；MathVerse mean 46.53，较基础模型 41.31 提升 5.22 | Table 2，p. 7 | 有外部验证，但仍是几何/多模态数学邻域 |
| 自适应教师优于固定教师 | adaptive 在 ODA image/text pass@16 为 57.06/86.10，固定 teacher 最高为 52.28/83.77 | Table 3，p. 9 | 支持“题目级选择”而非固定转移方向 |
| 模态不对称是关键训练信号 | 不对称样本相对 paired-control 的 text pass@1 提升 4.43%，control 的 image validation 差 22.15% | p. 9 | 方向合理，但 control 定义与筛选分布仍需更严格复核 |
| EMA 提供长程稳定性 | current-policy teacher 约 step 170 崩溃；EMA reward 到 step 290 约 0.48，entropy/KL 稳定 | Figure 5，p. 10 | 消融很有说服力，但仍主要是单配置运行轨迹 |

### 数据、基线与指标

- **数据集**：ODA-Train/Val；外部 GeoInt、MathVerse。
- **基线**：Qwen3-VL-4B-Instruct、text-only GRPO、image-only GRPO、mixed-modality GRPO，以及 Vision-R1、PAPO、Vero。
- **指标**：pass@1、pass@16（32 rollouts）；MathVerse 使用 GPT-4o-2024-11-20 judge；跨视图共同可解率。
- **预算/硬件**：响应长度上限 16,384；RL 超参披露，硬件/美元成本未完整披露。
- **消融与稳定性**：固定 teacher、λ_KL sweep、当前策略 vs. EMA、模态不对称 vs. paired-control；图 4 的三随机种子给出 min/max error bar。

## 批判性阅读

### 证据支持的结论

- 配对视图只有被显式关联到 teacher-student 目标时，才稳定地产生跨模态迁移；把两种 prompt 混在一起做 sparse-reward GRPO 不够。
- 不同视图的最优教师方向确实随题目变化，固定使用文本、图像或联合视图都不如自适应选择稳定。
- EMA target 解决了自指式 teacher 的移动目标问题，是方法可训练性的必要组成。

### 尚未被充分支持的结论

- 尚未证明 MIRROR 在图表、科学图、视频或真实机器人观察中同样有效；这些任务未必能构造语义等价视图。
- “约 2K 样本胜过 200K+ 多模态数据”的比较受到模型、训练目标、FLOPs 和数据质量差异影响，不能直接解释为数据效率普适领先。
- teacher 选择依赖当前模型 rollout 和答案 verifier；错误答案但推理结构更好的视图如何处理，没有单独分析。

### 局限、风险与可能反证

- ODA-Data 先过滤出模态不对称题，验证集与自然题分布不同，可能放大 MIRROR 的优势。
- reverse-KL 让学生拟合教师在自己轨迹上的 token 偏好，不等于迁移了可解释的中间推理结构。
- GeoInt/MathVerse 仍属于几何推理相邻分布；更广泛的 VLM 能力、视觉幻觉和分布外鲁棒性尚未验证。
- 计算匹配只用 step 150 vs. 200 的累计更新近似，不能替代完整 wall-clock/FLOPs 等价实验。

## 与已有知识的连接

- **基础论文**：GRPO、on-policy distillation、ODA-Math-460k。
- **相近方法**：VOLD、Vision-R1、PAPO；本 vault 中的 [[notes/papers/2026/07/23/Look Less- Think Faster- Joint Token-Compute Adaptation for Multimodal LLMs]]。
- **后续工作**：将视图选择改为不确定性加权；在中间状态对齐；把方法迁移到图表、科学图和视频。
- **与主题笔记的关系**：[[notes/topics/跨视角监督、辅助信号与模型行为]]

## 复现计划

- **是否复现**：待定
- **最小验证目标**：在公开 ODA 数据上复现 adaptive teacher、fixed teacher、mixed GRPO 三组，并以相同更新 FLOPs 比较。
- **所需资源**：Qwen3-VL-4B、verl、ODA-Train/Val、可验证几何答案和至少 3 个随机种子。
- **成功标准**：在保持 teacher rollout、student rollout 和更新预算可比时，adaptive MIRROR 在 image/text 双指标均优于 mixed GRPO。

## 待追踪问题

- [ ] 不做“模态不对称”预筛选时，MIRROR 是否仍能发现有价值的 teacher？
- [ ] reverse-KL 对最终答案和中间步骤的收益分别是多少？
- [ ] 视图数从 3 个扩展到视频帧、depth 或 tool observation 后，teacher selection 是否仍稳定？

## 原文定位

- 问题与三视图不对称：pp. 1–5，Figure 1、Table 1。
- ODA-Data 构造：p. 4，Section 4。
- MIRROR 目标与 EMA：pp. 6–7，Eq. (1)–(3)、Algorithm 1。
- 主结果与计算匹配：pp. 7–10，Table 2–4、Figures 3–5。
