---
type: paper
title: "LAION-BVD: A 10-Million-Hour Open Video Dataset for Multimodal Pre-training"
aliases: []
authors: ["Andreas Hochlehnert", "Marianna Nezhurina", "Mehdi Cherti", "Andrej Radonjic", "Thaddäus Wiedemer", "Christoph Schuhmann", "Romain Beaumont", "Wieland Brendel", "Bernhard Schölkopf", "A. Sophia Koepke", "Jenia Jitsev", "Matthias Bethge"]
year: 2026
venue: "arXiv"
paper_date: "2026-08-25"
date_added: "2026-08-26"
last_read: "2026-08-26"
topics: ["多模态模型", "视频理解", "预训练数据", "数据集", "音视频学习"]
status: read
priority: 2
rating: 4
arxiv_id: "2608.24845"
doi: ""
paper_url: "https://arxiv.org/abs/2608.24845"
code_url: "https://projects.laion.ai/bvd/"
pdf_path: "library/raw/2026/08/26/2608.24845.pdf"
text_path: "library/text/2026/08/26/2608.24845.txt"
sha256: "ebe9b1ee2e9769c135f71d6090dd98d20a1f9bc2bb24cbac73d5f681f115afba"
pages: 33
citation_key: "hochlehnert2026laionbvd"
related:
  - "[[notes/topics/多模态能力迁移与缩放规律]]"
  - "[[notes/papers/2026/08/04/What Transfers from Text to Vision- Capability Scaling Laws and Transfer Dynamics for VLMs]]"
cssclasses:
  - paper-note
---

# LAION-BVD: A 10-Million-Hour Open Video Dataset for Multimodal Pre-training

## 一句话结论

LAION-BVD 的价值在于开放多模态数据规模和模态覆盖，而不只是“10M hours”这个 headline：从 1.3B Common Crawl platform URLs 中成功下载约 80M videos/10M hours，再抽取 55M video/audio clips 和 300M scene-changing frames。ViCLIP、CLAP、CLIP 验证显示它对 video-text、audio-text 和 image-text retrieval 有稳定 scaling，但 ImageNet classification 较弱；自动短 caption、平台/语言偏差、minimal safety filtering、未验证 generative VLM 与未做 joint audio-visual training 是主要边界。

## 三分钟筛选

- **问题**：开放视频多模态预训练数据仍远小于图文数据，视频、音频、帧级监督的规模化获取和处理成本高。
- **新意**：Common Crawl URL sourcing + 2,000 virtual servers 下载 + scene/audio/frame 三路自动 caption，提供统一的 video/audio/image 训练资源。
- **核心证据**：55M clips 上 ViCLIP 超过 matched InternVid；BVD-A-10M 的 CLAP 在多模型规模下匹配/超过 LAION-Audio；BVD-I-300M 在 MS-COCO retrieval 强但 ImageNet-1k 弱（Table 4–10，Figure 5）。
- **与我的关系**：连接多模态数据工程、scaling evidence 和 benchmark 目标错配；可作为后续 VLM 训练/数据审计的开放数据源。
- **决定**：精读；不直接复现 10M-hour collection，优先做 caption/data subset 的小规模质量审计。

## 问题设定

- **输入、输出与目标**：输入是 Common Crawl WAT 中的平台视频 URL；输出是 raw videos、scene-level video/audio clips、synthetic captions 和 scene-change frame-caption pairs，供 ViCLIP/CLAP/CLIP 预训练。
- **现有瓶颈**：视频规模受下载、代理、存储和 captioning 计算限制；开放数据还需兼顾 modality alignment、跨语言覆盖和 benchmark contamination。
- **关键假设**：自动 caption 的弱监督在大规模下足以支持 representation learning；视频帧的分布能补充传统 web-image corpora；平台 moderation 足以替代数据收集阶段的额外 safety filter。

## 核心贡献

1. 发布 1.3B candidate URLs、约 80M downloaded videos、10M video hours（§3.1，Figure 2）。
2. 从约 2.4M sampled videos 生成 55M clips，分别提供 Qwen3-VL-2B video captions 和 Audio Flamingo 3 audio captions；另生成 300M scene-changing frames 和 DeepSeek-VL2-tiny captions（§3.1–3.2，Figure 4）。
3. 用 ViCLIP、CLAP、CLIP 在不同 model/data scales 和 video/audio/image benchmarks 验证数据效用，同时公开 URLs、captions subset 和 Hugging Face collection（§4–6）。

## 方法

### 直觉

视频不是单一模态数据：同一段视频可以贡献运动视觉、音频事件和场景变化帧。LAION-BVD 的系统贡献是把一次下载和预处理摊销到三种训练信号，再分别用 contrastive models 验证，而不是声称已经训练出统一 audio-visual foundation model。

### 形式化描述

- URL pipeline：4.7B Common Crawl candidate URLs → platform filter（YouTube/Vimeo/Dailymotion）→ 1.3B URLs → attempted 130M downloads → 80M successful videos/10M hours。
- Video/audio subset：随机 2.4M videos，过滤 10s–30min，PySceneDetect scene split，过滤静态片段，形成 BVD-V-55M 和对应 audio clips。
- Frame subset：从全量池抽样视频，用 ffmpeg scene threshold 0.1 保留约 300M scene-change frames，形成 BVD-I-300M。
- Captioning：video 每 clip 最多 32 frames，Qwen3-VL-2B-Instruct，20 words 以内；audio 用 Audio Flamingo 3，10 words 以内；frames 用 DeepSeek-VL2-tiny（§3.2）。

### 关键模块与训练流程

1. 通过 cc2dataset + Spark 从 WAT 提取 platform-specific URLs。
2. 用 2,000 virtual servers、Celery、yt-dlp 和 residential proxy network 下载；约 60% link success rate。
3. 生成三个数据分支：BVD-V（video-text）、BVD-A（audio-text）、BVD-I（frame-image-text）。
4. 训练/评估 ViCLIP、CLAP、CLIP，分别测 zero-shot classification、video/audio/image-text retrieval 和 scaling。

### 计算与数据成本

- 下载：尝试 130M videos，80M 成功，10M hours；存储和代理网络成本极高。
- 标注：55M clips、300M frames 的自动 caption；caption model 本身引入推理成本和 systematic bias。
- ViCLIP：使用 BVD-V-10M/50M、BVD-V-55M；CLAP 使用 BVD-A-1.7M/10M；CLIP 使用最多 300M frames。
- 公开边界：URL 和部分 captions 公开，raw data 需研究机构接受 terms 后下载；复现全量收集不现实。

## 实验与证据

| 作者主张 | 对应证据 | 定位 | 我的判断 |
| --- | --- | --- | --- |
| BVD 是有效 video-text pretraining data | 50M samples seen 时，BVD-V-10M/50M 比 InternVid-10M-FLT aggregate 高 3.3/4.0 pp；WiSE-FT 后 BVD-V-50M Avg 62.6 | Table 4、Table 6、§4.1，pp. 8–9 | 有 matched scale 对照，但 caption/model pipeline 与 InternVid 的差异仍可能混入。 |
| BVD audio 可替代/补充 LAION-Audio | BVD-A-10M 在四种 CLAP model scale 上匹配或超过 LAION-Audio；只有加 AudioSet 的 LA+AS 更强 | Table 7–9、§4.2，pp. 9–10 | 支持 audio representation learning，但纯数据源结果不能推断 unified audio-visual ability。 |
| frame captions 适合 retrieval | ViT-B/16、300M samples 的 BVD-I 在 COCO T2I/I2T 达 0.63/0.80，但 ImageNet-1k 仅 0.28 | Table 10、Figure 5、§4.3，pp. 10–12 | 清楚展示 benchmark target mismatch：检索强不等于分类强。 |
| 数据和 compute 有 scaling | ViCLIP/CLAP/CLIP 在多种 model/data scales 有上升趋势 | Table 5、Table 9、Figure 5 | 趋势可信，但存在重复采样（110M seen vs 10M unique）和 caption ceiling。 |

### 数据、基线与指标

- **数据集**：LAION-BVD raw、BVD-V-55M、BVD-A-10M、BVD-I-300M；对照 InternVid、LAION-Audio、DataComp-1B、Re-LAION-2B。
- **基线**：ViCLIP/CLAP/CLIP 在相同 model/data scales 下训练；WiSE-FT checkpoint merging 作为额外对照。
- **指标**：Kinetics-400/UCF-101/HMDB51 top-1；MSR-VTT/MSVD retrieval；UrbanSound8K、AudioCaps、Clotho；ImageNet-1k/R/Sketch/V2 与 MS-COCO retrieval。
- **预算/硬件**：训练超参数和部分 GFLOPs 在 Appendix A；全量下载用 2,000 virtual servers，但未给全 pipeline monetary cost。
- **消融与稳定性**：data scale、model scale、WiSE-FT、mixed audio datasets、不同 frame samples；没有 safety-filter 或 captioner 替换的系统消融。

## 批判性阅读

### 证据支持的结论

- LAION-BVD 是一个大规模、跨 video/audio/frame 的开放资源，且至少对 contrastive representation learning 有用。
- 数据效果明显依赖任务：video-text/audio-text 与 retrieval 表现较强，ImageNet-style classification 明显较弱。
- 大数据规模并没有消除 caption style、语言分布和平台来源偏差；论文自己报告 94% 视频来自 YouTube、English 约 57%。

### 尚未被充分支持的结论

- “multimodal pre-training”在本文主要是三种单独的 contrastive training；没有 joint audio-visual model、生成式 VLM 或需要时序同步的任务。
- competitive benchmark performance 不能证明 10M hours 的边际质量优于更小、更精筛的数据；DataComp/Re-LAION 的 filtering and caption pipeline 不是完全对齐。
- 公开 URL/caption metadata 不等于研究者可以稳定取得全部 raw video；平台 policy、地域和 proxy 条件影响可重复性。

### 局限、风险与可能反证

- captions 全部自动生成且短，可能遗漏细粒度动作、时间关系和长尾概念；captioner error 会被规模放大。
- 数据收集阶段没有额外 safety filters，仅依赖平台 moderation；潜在有害内容、版权、隐私和 stereotype 风险仍未系统量化。
- 94% YouTube、约一半非英语但长尾语言不均衡；地区、平台、upload year 和主题偏差可能导致 representation skew。
- 仅做 contrastive encoder 验证；不能把 ViCLIP/CLAP/CLIP 结果直接外推到 video generation、instruction following 或 embodied action。

## 与已有知识的连接

- **基础论文**：LAION-5B、InternVid、Panda-70M、LAION-CLAP、DataComp。
- **相近方法**：[[notes/topics/多模态能力迁移与缩放规律]]；数据规模与目标 benchmark 的 alignment 比单纯数据量更关键。
- **后续工作**：视频数据去重、caption quality audit、multimodal safety、joint audio-visual pretraining。
- **与主题笔记的关系**：可作为多模态数据工程与缩放证据的开放基线，暂不作为“统一多模态理解”证据。

## 复现计划

- **是否复现**：待定
- **最小验证目标**：下载公开 BVD-V/BVD-I 小子集，复现 caption length/language/source statistics，并在 ViCLIP/CLIP 小模型上比较 retrieval 与 ImageNet classification 的目标错配。
- **所需资源**：Hugging Face metadata/captions、公开视频下载许可、ffmpeg/PySceneDetect、单机多 GPU contrastive training。
- **成功标准**：小规模上复现“retrieval 明显强于 ImageNet classification”的相对模式，并量化 captioner/source filtering 对结果的影响。

## 待追踪问题

- [ ] Hugging Face collection 是否包含去重、版权/安全过滤、URL freshness 和完整 provenance 字段？
- [ ] 换用强 captioner、ASR/字幕和多语言 caption 后，retrieval/classification gap 是否缩小？
- [ ] BVD 在 generative video-language、audio-visual QA 和 temporal grounding 上是否仍有优势？
- [ ] 如何在不丢失规模的情况下加入可审计的 content safety、PII、版权和 dedup pipeline？

## 原文定位

- 数据规模与贡献：Abstract、Figure 1、§1，pp. 1–3。
- URL 下载与三路数据管线：Figure 2、§3.1–3.3，pp. 5–7。
- ViCLIP 验证：Table 4–6、§4.1，pp. 8–9。
- CLAP 验证：Table 7–9、§4.2，pp. 9–10。
- CLIP/frame 验证：Table 10、Figure 5、§4.3，pp. 10–12。
- 局限与结论：§5–6，pp. 12–13。
