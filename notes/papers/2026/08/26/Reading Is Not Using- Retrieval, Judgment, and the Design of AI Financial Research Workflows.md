---
type: paper
title: "Reading Is Not Using: Retrieval, Judgment, and the Design of AI Financial Research Workflows"
aliases: []
authors: ["Miao Liu", "Zhizhe Liu"]
year: 2026
venue: "arXiv"
paper_date: "2026-08-25"
date_added: "2026-08-26"
last_read: "2026-08-26"
topics: ["Agent", "金融人工智能", "长上下文与记忆", "检索增强", "评估与工作流"]
status: read
priority: 1
rating: 5
arxiv_id: "2608.24842"
doi: ""
paper_url: "https://arxiv.org/abs/2608.24842"
code_url: ""
pdf_path: "library/raw/2026/08/26/2608.24842.pdf"
text_path: "library/text/2026/08/26/2608.24842.txt"
sha256: "ff148dd3f1105edb61e1a800834533c081348fbec7507e52e39b83e162ec5035"
pages: 83
citation_key: "liu2026readingisnotusing"
related:
  - "[[notes/papers/2026/08/06/FinPerMA- A Theory-Informed, Event-Grounded Personalized-Memory Benchmark for LLM Agents]]"
  - "[[notes/topics/Agent外部状态的增长、验证与压缩]]"
  - "[[notes/topics/Agent能力形成与过程验证]]"
cssclasses:
  - paper-note
---

# Reading Is Not Using: Retrieval, Judgment, and the Design of AI Financial Research Workflows

## 一句话结论

这篇论文最重要的发现是：LLM 能准确检索一条风险披露，不代表它会在投资判断中使用这条信息。把无关上下文从 2K 扩到 128K tokens 后，9B workhorse 的边际决策影响从 +0.032 降至噪声地板，而检索在 128K 仍为 12/12 正确；因果干预把瓶颈定位到 running summary 与 attention lookup 的信息传输。作者的 workflow 结论很具体：targeted、structured、decision-proximal 的 extract-then-decide 能把 128K 的影响保留率从 12% 提到 67%，而 generic chunk-and-summarize 在其实现中把披露完全驱逐。

## 三分钟筛选

- **问题**：AI analyst 的检索准确率是否能代表检索信息改变了最终投资判断？
- **新意**：把“使用”定义成 disclosure 与 neutral replacement 的 counterfactual decision difference，而不是继续用 QA/retrieval proxy 代替决策结果。
- **核心证据**：12 家美国注册公司、2K/8K/32K/128K 受控上下文；多模型家族复现；真实 10-K surgical redaction；memory transplant、attention blackout 和 workflow gradient（Table 2–9，Figure 1–6）。
- **与我的关系**：直接补充 Agent memory 的“可访问不等于被决策使用”边界，也为金融 AI 工作流提供可复现的 decision-aligned evaluation。
- **决定**：精读并列为优先复现；最小复现是 retrieval score 与 marginal decision influence 的分离。

## 问题设定

- **输入、输出与目标**：输入是包含一条量化风险披露的 filing 与无关、同文体 filler；输出是 sell/buy propensity 或 12 个月 default probability。目标是估计单条 disclosure 对 delegated judgment 的边际影响。
- **现有瓶颈**：检索是可观察、方便的中间任务，但 retrieval accuracy 不能证明 information integration；长上下文可能只让模型“读到”而不让它“加权”。
- **关键假设**：neutral replacement、单点编辑和同文体 filler 能保持 focal firm information fixed；模型输出是确定性 readout，足以做 firm-level counterfactual。

## 核心贡献

1. 定义 `Use(ℓ) = Decision(target, ℓ) − mean(Decision(neutral_m, ℓ))`，并用 10 个 pseudo-target insertions 构造 empirical noise floor（§3.1、§3.4）。
2. 证明 retrieval–integration gap 不是检索失败：Qwen 9B 在 128K 对 12/12 firms 检索正确且 neutral filings 无 false positive，但 decision influence 与无关插入不可区分（§4.1–4.3）。
3. 通过 memory/attention causal interventions 和四种 workflow architecture，提出 decision-proximal representation principle（§5–6、Table 6–9）。

## 方法

### 直觉

论文把 delegated AI task 拆成两个阶段：**找到事实**与**把事实带到判断点并赋予权重**。前者可以正常，后者仍会因固定容量的 running summary、衰减的 decision-time lookup 或泛化摘要预算而失败。

### 形式化描述

每个 firm 在每个 context length `ℓ` 有一个 target filing 和五个 neutral versions。`Use(ℓ)` 是 target decision 与五个 neutral decision 的平均差。检索另起调用，用 frozen answer keys 评分，避免把“先找后用”的指令混入 decision task（§3.1、§3.4）。

### 关键模块与训练流程

1. **材料构造**：12 家 U.S. registrants，人工写入 covenant threshold、settlement、indemnification cap 等可验证风险段落，并通过 whole-filing coherence audit；另有 20 个真实 10-K redaction extension（§3.2–3.3）。
2. **长度操纵**：保持 focal mini-filing 不变，仅追加经济上无关、会计/法律文体匹配的 2K、8K、32K、128K filler；另测 disclosure 到 decision 的距离和 before/after arrangement（§3.3）。
3. **统计推断**：firm bootstrap 置信区间 + pseudo-target randomization inference；零结果需相对于插入噪声而非数学 0 判断（§3.4）。
4. **机制与工作流**：移植 running summary、切断全 attention heads 对 disclosure 的访问；比较 extract-then-decide、chunk-then-aggregate、re-present 与 extended reasoning（§5–6）。

### 计算与数据成本

- 评估模型：Qwen3.5 9B workhorse、Llama、Gemma 和一个 production API model；不同模型的 readout units 不混合（§3.1、§3.5）。
- 设计规模：12 个构造 filing、20 个真实 10-K、7-level severity ladder、4 个长度级别及多种 workflow。
- 运行控制：冻结硬件/软件配置；对 deterministic readout 使用 firm-level bootstrap 和 exact/randomization tests。
- 复现成本：论文为 preliminary draft，实验材料和代码“可向作者索取”，预计 9 月底发布 replication package；当前最大成本是 filing 构造审计与多模型长上下文调用。

## 实验与证据

| 作者主张 | 对应证据 | 定位 | 我的判断 |
| --- | --- | --- | --- |
| 决策影响随无关上下文增长而衰减 | Qwen 9B `Use`: +0.032 (2K) → +0.005 (8K) → +0.001 (32K) → +0.004 (128K)，32K/128K 相对 pseudo-null 不显著 | Table 2、Figure 1、§4.1，pp. 20–22 | 受控设计强，且 null 不是 0；但实验任务是风险段落插入，不等于所有金融判断。 |
| 不是 retrieval failure | 128K 时 Qwen 对 12/12 firm 仍正确检索、neutral control 0 false positive | Table 3、Figure 3、§4.3，pp. 23–25 | 这是论文最干净的证据链，真正把 QA proxy 与 decision outcome 分开。 |
| 模型仍能排序但不能保留经济幅度 | severity response range 0.23→0.04，压缩 5.6×；pairwise ordering 0.93→0.79 | Figure 2、§4.2，pp. 22–24 | 说明长上下文损失不是简单“全忘”，而是 cardinal weighting 被压平。 |
| 两个 memory channel 都传输 disclosure | running-summary transplant 去除约 65% influence；全 attention access blackout 去除 44–48% | Table 6、§5，pp. 33–36、44 | 支持双通道，但作者明确不主张可加和或谁更重要。 |
| workflow architecture 比额外 reasoning 更关键 | baseline 128K retention 12%；extract-then-decide 67%；chunk-aggregate 近 0；extended reasoning 未恢复 | Table 7–9、Figure 6、§6.2–6.4，pp. 36–42 | 方向强且有 decomposition；“structured/targeted/proximal”仍是组合包，不是单因素识别。 |

### 数据、基线与指标

- **数据集**：12 个构造 U.S. filing；20 个真实 10-K exploratory extension。
- **基线**：direct decision、neutral insertion empirical null、不同模型 family、不同 workflow architecture。
- **指标**：marginal decision influence `Use(ℓ)`、retrieval completeness/false positives、severity range/order accuracy、retention rate、bootstrap CI 与 randomization p-value。
- **预算/硬件**：报告模型设置和 deterministic inference；未报告完整 token/API/wall-clock 成本。
- **消融与稳定性**：模型 family、第二种经济判断、真实 redaction、memory/attention interventions、workflow decomposition；但材料/代码尚未公开。

## 批判性阅读

### 证据支持的结论

- 对该实验设定，retrieval-based evaluation 不能替代 decision-aligned evaluation。
- generic chunk-and-summarize 的失败发生在 extraction 阶段：24/24 个 2K/128K firm-arrangement cells 的 consolidated notes 没有 target disclosure。
- targeted structured restatement 邻接 decision 能恢复影响，且 experimenter-written answer key 与 model-written extraction 效果相近，说明“模型自述”不是必要条件。

### 尚未被充分支持的结论

- “workflow architecture jointly determines AI analyst performance” 在本研究的 filing、模型和四个 workflow 实现中成立，但不能外推所有 RAG、map-reduce 或 reasoning system。
- memory transplant 和 attention blackout 证明 channel 有因果份额，却不能给出 fixed-size summary 的直接容量曲线。
- 真实 10-K extension 有生态真实性，但为 exploratory，且 surgical edits、披露移除和泄漏控制本身带来新的实验者判断。

### 局限、风险与可能反证

- 论文标注为 very preliminary draft；代码、材料和 replication package 尚未公开，当前不可独立重跑。
- 12 家公司与人工撰写披露的外部效度有限；行业、语言、会计复杂度和真实分析流程可能改变 failure frontier。
- workflow 中的 `extract-then-decide` 直接把目标答案放到 decision 邻近位置，可能低估了实际 analyst pipeline 的检索/校验成本。
- 研究测量的是单条 disclosure 的边际影响，不直接证明最终投资收益、风险校准或人机协作价值。

## 与已有知识的连接

- **基础论文**：long-context retrieval、RAG、information integration、AI-assisted decision making。
- **相近方法**：[[notes/papers/2026/08/06/FinPerMA- A Theory-Informed, Event-Grounded Personalized-Memory Benchmark for LLM Agents]]；共同关注“记忆被召回后是否真正改变后续行为”。
- **后续工作**：与 Agent workflow verification、structured memory、decision-aligned benchmark 连接。
- **与主题笔记的关系**：[[notes/topics/Agent外部状态的增长、验证与压缩]]；本论文提供“外部状态被看到但未被使用”的反例。

## 复现计划

- **是否复现**：是
- **最小验证目标**：用 3–4 个公开 10-K 和一条可核验风险事实，复现 2K/32K/128K 的 retrieval completeness 与 `Use(ℓ)` 差异；先不做内部 representation intervention。
- **所需资源**：公开 SEC filings、一个可固定版本的长上下文模型、可控 neutral replacement/filler 生成器、bootstrap/randomization 脚本。
- **成功标准**：retrieval 保持高准确而 `Use` 随上下文下降，并且 targeted structured restatement 比 generic summarization 保留更高 decision influence；若只出现 QA 下降，说明未复现核心 gap。

## 待追踪问题

- [ ] replication package 是否按预告在 2026-09 发布？
- [ ] 换成真实 analyst workflow、multi-disclosure portfolio judgment 后，decision-proximal principle 是否仍成立？
- [ ] 能否把 `Use(ℓ)` 扩展为多事实 interaction、时间序列判断和最终投资回报校准？
- [ ] 如何测量 targeted restatement 的额外 token、延迟和审计成本？

## 原文定位

- Abstract / retrieval–integration gap 定义：pp. 1–4。
- `Use(ℓ)` 与实验材料：§3.1–3.3，pp. 14–19。
- 主结果与 retrieval 对照：Table 2–3、Figure 1–3、§4.1–4.3，pp. 20–25。
- 机制干预：Table 6、§5，pp. 33–36、43–44。
- Workflow gradient：Table 7–9、Figure 6、§6.1–6.5，pp. 36–42。
- 结论与 principle：§7，pp. 42–45。
