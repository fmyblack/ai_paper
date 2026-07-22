---
type: paper
title: "OmniReasoner: Thinking with Long Audio-Video via Native Tool Use"
aliases: []
authors: ["Yu Chen", "Caorui Li", "Ziyu Xiong", "Yidong Wang", "Mingqi Gao", "Shuman Liu", "Biao Liu", "Chunfeng Yang", "Anxiang Zeng", "Haibo Zhang", "Chaofan Chen"]
year: 2026
venue: "arXiv"
paper_date: "2026-07-21"
date_added: "2026-07-22"
last_read: "2026-07-22"
topics: ["多模态模型", "Agent", "长上下文与记忆", "推理与规划", "语音、图像与视频"]
status: read
priority: 2
rating: 4
arxiv_id: "2607.19339"
doi: ""
paper_url: "https://arxiv.org/abs/2607.19339"
code_url: "https://github.com/RockyChen0205/OmniReasoner"
pdf_path: "library/raw/2026/07/22/2607.19339v1.pdf"
text_path: "library/text/2026/07/22/2607.19339v1.txt"
sha256: "00ba5f75970fd7ffd27b02262cd30b2055d569c0ffb78bff117d68f02f7642aa"
pages: 19
citation_key: ""
related: ["[[notes/papers/2026/07/22/Masked Visual Actions for Unified World Modeling]]", "[[notes/papers/2026/07/22/AlayaWorld- Interactive Long-Horizon World Modeling - Full Technical Report]]"]
cssclasses:
  - paper-note
---

# OmniReasoner: Thinking with Long Audio-Video via Native Tool Use

## 一句话结论

OmniReasoner 把长音视频理解重写为主动感知：模型先低成本浏览全局，再决定是否按绝对时间区间重新看和听；完整消融支持“音频、tool-return、SFT warm-up、RL 和 TimeAnchor 都有贡献”，但它仍是最多一次 zoom-in 的两阶段策略，而且没有报告额外帧数、延迟或 token 成本。

## 三分钟筛选

- **问题**：长音视频的关键证据往往短暂且跨模态；全程高分辨率处理太贵，统一降采样又会丢失决定性细节。
- **新意**：让 omni-modal LLM 学习 direct answer 或 `zoom([s,e])`；用绝对秒数的 TimeAnchor 跨全局低采样和局部高采样对齐音频、视频与工具参数。
- **核心证据**：相对 Qwen2.5-Omni-7B，在六个 benchmark 上全部提升；10-30 分钟视频增益达 9.9 点；去掉音频、tool-return、TimeAnchor 或 cold-start SFT 均明显下降。
- **与我的关系**：这是 Agent 中“先决定获取什么证据，再推理”的干净案例，也说明长上下文问题不一定靠扩大窗口解决。
- **决定**：精读；适合作为主动感知与多模态工具使用的基线。

## 问题设定

- **输入、输出与目标**：输入长音视频 $x$ 和问题 $q$；模型先看低成本全局 observation，然后直接回答或选择时间区间，接收高保真局部音视频后作答。
- **现有瓶颈**：视觉帧和连续音频同时占用上下文；不同 sampling grid 下 frame index 不一致；现有 long-video agent 多只搜索视觉证据。
- **关键假设**：全局低保真预览足以定位候选区间；关键证据集中在一个局部窗口；绝对时间戳可以成为跨模态、跨采样率的稳定工具坐标。

## 核心贡献

1. 提出两阶段 long audio-video tool-use policy，学习“是否 zoom”和“zoom 到哪里”。
2. 提出 TimeAnchor，以原视频绝对秒数保持工具调用在不同采样粒度间 round-trip consistent。
3. 构造 Temporal Augmented Data Engine，并用 SFT warm-up + agentic RL 学习工具格式、区间选择和证据使用。

## 方法

### 直觉

像人看长视频一样，模型先拖动进度条形成粗略时间线，只在不确定时回看可疑区间。这样将固定上下文预算从“均匀覆盖所有时刻”转成“低成本覆盖 + 高成本局部验证”。

### 形式化描述

先构造全局观察 $g=\Phi_{global}(x)$，策略采样 $a_1\sim\pi_\theta(\cdot\mid g,q)$，其中 $a_1$ 是直接回答或 `zoom([s,e])`。若调用工具，环境返回 $z_{s:e}=\Phi_{local}(x,[s,e])$，再基于全局与局部证据生成答案。TimeAnchor 将 $[s,e]$ 固定在原始媒体时间轴，而不是某次采样的帧号。参见 Section 3.1-3.2，Eq. (1)-(6)。

### 关键模块与训练流程

1. Global preview 保留全时长但降低帧率/分辨率；zoom-in 返回对应绝对时间区间的高保真音视频。
2. Temporal Augmented Data Engine 通过多段视频组合与异常插入，自动得到已知证据区间和两阶段轨迹。
3. SFT 先建立合法工具调用与稳定回答格式；RL 从 SFT policy 中筛选有非退化 group-relative reward 的样本继续优化。
4. 推理最多一次 zoom-in，第二阶段基于 tool-return 回答，并非开放式多轮 Agent。

### 计算与数据成本

- Base model 为 Qwen2.5-Omni-7B，32K context。
- SFT 25,839 examples：13,222 multi-segment、5,319 anomaly insertion、2,581 FineVideo、2,988 AVQA-R1、1,729 CG-Bench；其中 21,032 条是 interval trajectories。
- RL 2,731 examples；每 prompt 采样 8 rollouts。
- SFT + RL 使用 8×H100 80GB，总计约 480 H100 GPU-hours；论文没有报告推理阶段因 zoom-in 增加的帧、token、延迟或费用。

## 实验与证据

| 作者主张 | 对应证据 | 定位 | 我的判断 |
| --- | --- | --- | --- |
| tool-use post-training 普遍改善音视频推理 | 六个 benchmark 相对 base 分别 +5.5、+3.4、+2.1、+1.3、+1.1、+15.6 | Table 1；p. 7 | 覆盖面好，但大部分绝对增益中等；VideoHolmes 大增益部分来自读取更多帧 |
| 视频越长，主动 zoom 越有价值 | OmniVideoBench 的 0-5 / 5-10 / 10-30 min 增益为 +3.2 / +6.6 / +9.9；tool call rate 随时长升高 | Table 2、Figure 4；pp. 7-9 | 与机制预期一致，是很有价值的 duration-wise evidence |
| 模型真正使用音频和返回片段 | 去掉音频在三项上下降 3.9 / 4.1 / 8.3；去掉 tool-return 下降 2.2 / 1.5 / 2.0 | Table 3；p. 7 | 直接干预比 attention visualization 更可信，支持因果使用局部证据 |
| SFT 与 RL 缺一不可 | SFT-only 比 Full 低 1.2-1.9；RL-only 比 Full 低 7.2-8.7 | Table 3；pp. 7-8 | 强烈说明 RL 不能直接从不会调用工具的 base model 冷启动 |
| TimeAnchor 改善跨粒度 grounding | Charades-STA mIoU 从 base 33.7 到 w/o TimeAnchor 37.9，再到 41.3；answer accuracy 也增加 | Table 4；p. 9 | 设计与结果匹配，是论文最可复用的工程贡献 |

### 数据、基线与指标

- **数据集**：OmniVideoBench、LVOmniBench、Daily-Omni、WorldSense、VideoMME、VideoHolmes、Charades-STA；训练数据见 Appendix A.3。
- **基线**：Qwen2.5-Omni-7B 是主要同源基线；另列 Gemini 2.0/2.5、VideoLLaMA2、MiniCPM-o、VITA、HumanOmniV2 等参考值。
- **指标**：QA accuracy；Charades-STA 的 IoU@0.3/0.5/0.7 与 mIoU；tool call rate。
- **预算/硬件**：约 480 H100 GPU-hours；推理预算未统一披露。
- **消融与稳定性**：data recipe、audio、tool-return、SFT/RL、TimeAnchor 的消融较完整；未见多随机种子、置信区间或显著性检验。

## 批判性阅读

### 证据支持的结论

- 对长视频均匀采样的补充局部检索，确实能在相同 base model 上提升稀疏证据问答。
- 绝对秒数比 frame index 更适合跨音频、视频和采样粒度的工具参数。
- 监督冷启动是多模态 tool-use RL 的关键前提。

### 尚未被充分支持的结论

- “高效分配计算”只展示了行为，没有端到端 latency、token、帧数或成本曲线。
- 结果不能证明模型学会一般工具规划；它只在固定的 direct-answer / single-zoom action space 中决策。
- 与不同架构和闭源模型的表格不是严格同预算比较。

### 局限、风险与可能反证

- Tool-use accuracy 与 direct-answer accuracy 受 selection bias 影响：模型把难例交给工具，因此两者不能直接比较。
- 合成 composition / anomaly 数据可能让模型学习到数据引擎的区间结构，真实开放视频上的分布外泛化仍需验证。
- Qwen2.5-Omni-7B 的 32K context 和最多一次 zoom 限制了多证据、多轮交叉验证。
- 作者明确指出当前 omni-modal RL infrastructure 不成熟，base model 缺少工具预训练；还未测试更大的 Qwen-Omni-3。
- 外部知识检索、代码执行和结构化数据库工具不在范围内；高风险应用仍可能产生错误 temporal grounding 或幻觉证据。

## 与已有知识的连接

- **基础论文**：长视频时间定位、tool-augmented LLM、SFT + RL post-training。
- **相近方法**：Omni-R1、OmniVideo-R1、TimeSearch-R、VideoAgent、OmniGAIA。
- **后续工作**：多次 zoom、跨区间证据聚合、可学习停止条件，以及将感知成本直接纳入 reward。
- **与主题笔记的关系**：[[notes/topics/交互式世界模型与主动感知]]。

## 复现计划

- **是否复现**：是，优先做 inference-level 复核和小规模 SFT，不复现完整 RL。
- **最小验证目标**：在一组 10-60 分钟中文音视频上比较 uniform sampling、oracle interval、模型 zoom 与无 TimeAnchor 四种设置。
- **所需资源**：公开 checkpoint/代码、单张可容纳 Qwen2.5-Omni-7B 的 GPU、带秒级证据区间的测试集。
- **成功标准**：模型 zoom 在相同总帧数或 token 预算下优于 uniform sampling，并且区间 IoU 与最终准确率相关。

## 待追踪问题

- [ ] 把 tool cost 加入 RL reward 后，模型会减少无效 zoom 还是牺牲准确率？
- [ ] 一个区间不足时，如何避免早期错误定位锁死后续推理？
- [ ] 合成数据中已知的 evidence interval 是否会造成与真实视频不同的捷径？

## 原文定位

- 系统定义：Section 3.1，Figure 2，Eq. (1)-(4)，pp. 3-4。
- TimeAnchor：Section 3.2，Eq. (5)-(6)，p. 4。
- 数据引擎与训练：Section 3.3-3.4，Figure 3，pp. 5-6；Appendix A.3、Figure 6，pp. 13-15。
- 主结果与 duration split：Table 1-2，p. 7。
- 消融：Table 3，pp. 7-8；TimeAnchor 见 Table 4，p. 9。
- 工具行为和证据使用：Figure 4-5，pp. 8-9、14。
- 局限：Limitations，pp. 9-10。
