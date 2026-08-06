---
type: paper
title: "Perception Before Reasoning: Dynamic Latent Reasoning for Video Understanding and Question Answering"
aliases: ["DyLaR"]
authors: ["Haotian Xia", "Zilin Xiao", "Junbo Zou", "Vicente Ordonez", "Hanjie Chen"]
year: 2026
venue: "arXiv"
paper_date: "2026-08-04"
date_added: "2026-08-06"
last_read: "2026-08-06"
topics: ["视频理解", "多模态推理", "latent reasoning", "多模态模型"]
status: read
priority: 2
rating:
arxiv_id: "2608.04124"
doi: ""
paper_url: "https://arxiv.org/abs/2608.04124"
code_url: ""
pdf_path: ""
text_path: ""
sha256: ""
pages: 17
citation_key: ""
related:
  - "[[notes/papers/2026/07/31/See2Think- Do Multimodal Models Really Use Intermediate Visual States]]"
  - "[[notes/papers/2026/07/23/Look Less, Think Faster- Joint Token-Compute Adaptation for Multimodal LLMs]]"
cssclasses:
  - paper-note
---

# Perception Before Reasoning: Dynamic Latent Reasoning for Video Understanding and Question Answering

## 一句话结论

这篇把视频问答里的“先看再想”做成了一个可训练的 latent route：先用 perception latents 对齐证据，再在需要时展开 reasoning latents。它真正有意思的地方不是“更会说”，而是能用极少的可见 token 把视频 QA 的准确率往上推。

## 三分钟筛选

- **问题**：视频理解任务里，很多问题只需要 grounding，不需要长 CoT；但纯 direct answer 又容易丢掉复杂推理。
- **新意**：把响应拆成 perception / reasoning 两条 latent 路径，并用 adaptive routing 决定何时直接答、何时进入 reasoning。
- **核心证据**：在 4 个 backbone 上都能提分；Qwen3-VL-4B 的平均准确率从 54.0 到 58.2，同时可见 token 从 1220.7 掉到 18.5。
- **与我的关系**：它和 `See2Think`、`Look Less, Think Faster` 一起，把多模态模型的过程控制从外显 token 转向 latent-level routing。
- **决定**：已精读。

## 问题设定

- **输入、输出与目标**：输入视频帧和问题，输出答案；有些题需要证据 grounding，有些题需要后续 reasoning。
- **现有瓶颈**：长文本 CoT 会浪费 token、增加噪声；统一的 answer style 又很难兼顾简单 perception 题和复杂 reasoning 题。
- **关键假设**：模型内部可以学到两个相对分离的 latent 功能区，且 route 选择能根据题目类型动态切换。

## 核心贡献

1. 提出 DyLaR：把 video QA response 分成 perception latents 和 reasoning latents。
2. 用 SFT + RL 两阶段把“先 grounding 再 reasoning”的行为学出来，并显式学 route。
3. 在 9 个视频理解/问答基准上证明，这种 split 不只省 token，也能带来稳定准确率提升。

## 方法

### 直觉

作者不是让模型写更长的解释，而是让模型在内部先对齐视觉证据，再按需展开 reasoning。简单题走短路，复杂题走长路。

### 形式化描述

- **Response format**：输出被组织成 perception 段和 reasoning 段，前者负责证据对齐，后者负责推导。
- **Routing**：模型在 `DIRECT` 与 `REASON` 之间做动态选择，而不是所有样本都走同样的长链条。
- **Training**：SFT 先学 latent format，RL 再用 GRPO 之类的目标强化正确 route 和正确答案。

### 关键模块与训练流程

- **数据**：SFT 约 20K，RL 约 30K；来源混合了 Video-R1-CoT、LongVideo-Reason、CG-Bench、Video-Holmes、MLVU 等。
- **输入预算**：训练使用 16 帧，pixel cap 307,200。
- **冻结策略**：vision encoder 和 projector 冻结，主要更新语言/推理相关参数。
- **Latent design**：perception latents 主要承担 grounding，reasoning latents 只在必要时展开。
- **RL**：用 latent replay 和格式奖励去稳定 route 选择，而不是只盯最终答案。

### 计算与数据成本

- 这篇的主价值是把 visible token 大幅压缩下来，而不是做更大的模型。
- 代价是 latent 过程更难解释，且训练仍依赖高质量 rationale / evidence 数据。

## 实验与证据

| 作者主张 | 对应证据 | 定位 | 我的判断 |
| --- | --- | --- | --- |
| latent reasoning 能在更少可见 token 下提升视频 QA | Qwen3-VL-4B 平均 54.0 -> 58.2，平均 token 1220.7 -> 18.5 | Abstract, Table 1, pp. 1, 5-6 | 很强，且最实用 |
| 这种做法能跨 backbone 工作 | Qwen2.5-VL-7B、InternVL3.5-4B、LLaVA-OneVision-7B 都有稳定增益 | Table 1, pp. 5-6 | 不是单模型偶然 |
| grounding 和 reasoning supervision 都不可少 | w/o reasoning latents 39.1，w/o reasoning supervision 38.3，w/o perception grounding 38.7 | Table 2, p. 7 | 支持“先感知后推理”的结构性假设 |
| route selection 不是装饰项 | w/o adaptive routing 39.1，full DyLaR SFT 40.5 | Table 2, p. 7 | 说明 route 本身有价值 |
| route 真的会随题型变化 | reasoning route 在 reasoning 类问题上约 86.8%，在 perception 类问题上约 40.1% | Figure 3, p. 8 | 很好的选择性证据 |
| RL 进一步提升效果 | Qwen2.5-VL-7B 的 RL 版本平均再涨约 1.5 分 | Table 3, p. 8 | 说明 latent route 可被进一步优化 |

### 数据、基线与指标

- **数据集**：9 个视频理解 / QA 基准。
- **基线**：Video-R1、VideoRFT、Direct-answer 风格、长 CoT 风格和去掉各个 latent 组件的 ablation。
- **指标**：平均准确率、可见 token 数、route 分布、不同问题类型的增益。
- **预算/硬件**：论文重点不在训练算力披露；它更强调 response 预算与效果。
- **消融与稳定性**：对 reasoning latent、perception grounding、adaptive routing 做了明确消融。

## 批判性阅读

### 证据支持的结论

- 视频 QA 不一定需要长可见 CoT，至少在这组基准上，latent reasoning 已经能把准确率和 token 效率一起往上推。
- perception 和 reasoning 分开学，比把所有推理都塞进同一种 response style 更稳。
- route selection 不是可有可无的工程细节，它会直接改变模型该不该“想一下”。

### 尚未被充分支持的结论

- 可见 token 大幅下降不等于总 FLOPs 同比例下降；hidden compute 仍然存在。
- latent reasoning 的内部过程还不够可解释，难以判断它是真在“想”，还是只是学会了更短的输出模板。

### 局限、风险与可能反证

- 论文只在 4 个 open-source backbones 上验证，且 frame sampling 相对固定。
- 没有把 adaptive frame selection 一起纳入 route 学习。
- 训练依赖高质量 evidence/rationale 数据，数据噪声会直接污染 latent route。

## 与已有知识的连接

- **基础论文**：`See2Think`、token-compute adaptation、latent CoT / latent reasoning 系列工作。
- **相近方法**：把视觉证据拆成 perception token，再由 reasoning branch 完成推导的多模态模型。
- **后续工作**：把 route learning 和 frame selection、long-video memory、tool use 结合起来。
- **与主题笔记的关系**：[[notes/topics/结构化中间层与可验证执行]]。

## 复现计划

- **是否复现**：待定
- **最小验证目标**：在一个 backbone 上复现 SFT ablation，尤其是 full / w/o grounding / w/o reasoning / w/o routing 的排序。
- **所需资源**：公开视频 QA 数据、一个可训练的 VLM、以及能够记录 visible token 的评测脚本。
- **成功标准**：准确率方向和 token 压缩方向都能重现。

## 待追踪问题

- [ ] latent route 的收益主要来自更好的决策，还是更强的格式约束？
- [ ] 如果换成更长视频或更密集事件，perception / reasoning split 还稳不稳？
- [ ] 能否把 route 进一步和 frame selection / tool use 合并成同一 policy？

## 原文定位

- Abstract, p. 1
- Latent format and training, Sections 2.1-2.4, pp. 2-4
- Main benchmark results, Table 1, pp. 5-6
- Ablations, Table 2, p. 7
- Routing analysis, Figure 3, p. 8
- Limitations, p. 9

