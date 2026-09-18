---
type: paper
title: "MIRAGE: How Conversation State Shapes Historical Evidence Use in Multimodal Personal Agents"
aliases: []
authors: ["Yu Liu", "Wenxiao Zhang", "Cheng Hu", "Cong Cao", "Fangfang Yuan", "Xinyu Wang", "Jin B. Hong", "Yanbing Liu"]
year: 2026
venue: "ACM Multimedia 2026"
paper_date: "2026-08-25"
date_added: "2026-09-18"
last_read: "2026-09-18"
topics: ["Agent", "长上下文与记忆", "多模态模型", "Benchmark 与评估方法"]
status: read
priority: 1
rating:
arxiv_id: "2609.19059"
arxiv_version: "v1"
version_updated_at: "2026-08-25"
doi: "10.1145/3767308.3835540"
paper_url: "https://arxiv.org/abs/2609.19059"
code_url: "https://github.com/prisma-research/MIRAGE"
pdf_path: "library/raw/2026/09/18/2609.19059.pdf"
text_path: "library/text/2026/09/18/2609.19059.txt"
sha256: "989ffd25a06b6440b68083cb8352d2624e2c64fe238e1e5d5f6e4a312364885f"
pages: 12
citation_key: ""
related: ["[[notes/papers/2026/09/18/ERPBench- A State-Grounded Evaluation Paradigm for Computer-Use Agents in Enterprise Software]]", "[[notes/papers/2026/08/03/Beyond Retrieval- Analytic Memory for Multimodal Agents]]", "[[notes/papers/2026/07/30/MemSecBench- Tracking Agent Memory Poisoning from Persistence to Consequence and Repair]]"]
cssclasses:
  - paper-note
---

# MIRAGE: How Conversation State Shapes Historical Evidence Use in Multimodal Personal Agents

## 一句话结论

MIRAGE 在同一 OpenClaw runtime、6 个 planted artifacts、200 个问题和 7 个模型的受控实验中证明了“答对”不等于“使用了正确历史证据”，并显示 context depth 与 compaction 会产生模型相关、非单调失效；但 `SOURCE` 仍是模型自报，状态变量捆绑了位置、filler、summary 与 tool orchestration，因此它不能因果证明 compaction 本身销毁了持久证据，也不能直接外推到一般个人 Agent。

## 三分钟筛选

- **问题**：长会话 Agent 可以凭 residual context 或先验猜中答案，即使已经找不到原始证据；只评分 final answer 会把这种 provenance failure 当成成功。
- **新意**：固定证据、问题、scorer 与 checkpoint family，只改变四种 conversation state；同时评分 answerability、source attribution、value correctness 和二者联合的 grounded correctness。
- **核心证据**：Qwen3-VL-8B 在 `S1-d80k` 的 `VC=47%`、`GC=18%`，outcome-only 高估 29pp，`MI=78%`；强制工具检索让 d80k 的 SC/GC 上升，却在 S2 对三个 Qwen 全部回退并提高 hallucination rate（Table 1、Figure 6，pp. 6、8）。
- **与我的关系**：与 ERPBench 形成镜像：ERPBench 暴露“保存了但数据库错”，MIRAGE 暴露“答对了但来源错”；二者共同反对 outcome-only evaluation。
- **决定**：精读；优先复现 state perturbation、workspace audit 与 retrieval counterfactual，不把 SC 当作因果 proof-of-use。

## 问题设定

- **输入、输出与目标**：给定历史 checkpoint 与 probe，模型必须输出 `ANSWERABLE=YES|NO`、`SOURCE=<artifact_id|NONE>`、`ANSWER=<value|NONE>`；目标是确认 Agent 是否能判断可答、找回正确来源并由它回答。
- **现有瓶颈**：模型当前可见 active context `c_t` 与 workspace `W` 会随深度和 compaction 改变；同一个值可以通过 context retrieval、tool retrieval 或直接猜测得到。
- **关键假设**：source self-report 与 canonicalization 足以近似 provenance；固定 6 个 artifact 和 topic-disjoint filler 能隔离 state effect；共享 checkpoint/summary pipeline 不会对某些模型造成系统性偏差。

## 核心贡献

1. 提出 state-conditioned protocol：同一 planted evidence/question 在 `d0/d50k/d80k/S2` 四状态分别 probe，每题都从 checkpoint 的 fresh copy 恢复。
2. 将结果拆成 `AC/SC/VC/GC/HR/WS/PF`，并引入 Mirage Index、outcome overestimation gap、depth sensitivity 与 retention。
3. 用 mandatory `artifact_recall` 干预检验 tool-mediated retrieval 的修复边界，并提供 summary-format、evidence-type、depth-normalization 与不确定性附录分析。

## 方法

### 直觉

把“记得”拆成三个问题：知道现在是否可答、知道证据在哪里、答案是否与证据一致。然后对同一问题只改变会话状态；如果答案不变而来源从正确 artifact 漂到 `NONE`，outcome metric 就暴露出盲区。

### 形式化描述

- Agent 历史有 active context `c_t` 与长期 workspace `W` 两种 surface；证据可经 `R_context` 或 `R_tool` 访问（Section 3，p. 3）。
- `AC` 评 answerability；`SC` 评 canonicalized source；`VC` 评 normalized value；`GC=SC×VC` 要求来源和值同时正确（Eqs. 9–14，p. 5）。
- `HR` 是 unanswerable probe 上声称 `YES` 或给非 `NONE` 答案；`WS` 是 answerable probe 上 source mismatch（含 `NONE`）；`PF` 单列 parse failure。
- `MI` 是 answerable 上声称可答但 `GC=0` 的比例；`OG=VC−GC` 表示只看答案会高估多少。`DS` 与 `Ret` 分别衡量 d0→d80k 的降幅和保持率（Eq. 15、Section 4.1，p. 5）。

### 关键模块与训练流程

- 不是训练新模型，而是构造 `T=C_plant⊕F` 的固定 trunk：种入 6 个 ChartQA/ScreenSpot 多模态证据，再追加 20 个固定 seed 的 persona-consistent filler（Algorithm 1、Sections 3.2–3.3，pp. 3–4）。
- 四状态：`S1-d0=23,184 EIT`、`S1-d50k=50,217`、`S1-d80k=80,436`、`S2=100,081` 且发生 1 次 native compaction。`d0` 并非零 token，S2 仍是 same-session（Sections 3.3、4.1，pp. 4–5）。
- `C0` 使用默认访问行为；`Cm` 强制回答前调用 `artifact_recall`，只对 5 个本地 open-weight 模型尝试，可靠效果解释最终集中于 3 个 Qwen（Section 4.2.3，p. 7）。
- 模型：GPT-5、Claude-4.5-Haiku、Qwen3-VL-4B/8B/30B、InternVL3.5-20B MoE、Gemma-3-27B。

### 计算与数据成本

- 200 probes=`100 answerable+100 matched-unanswerable`；4 states；作者称每 cell 是 3 次独立运行均值。按完整 C0/Cm 设计推算约 28,800 probe calls，但论文未报告总调用数/费用。
- 主 evidence 只有 6 个 artifact；附录另有 109 probes（55/54），扩展到 photo、infographic、code、email、invoice PDF、table-report PDF（Appendix A.1，p. 11）。
- 未披露 API 费用、总 token、时延、temperature/top-p、精确 seeds、硬件与软件 commit；论文表格无法从已公开 raw outputs 一键重算。

## 实验与证据

| 作者主张 | 对应证据 | 定位 | 我的判断 |
| --- | --- | --- | --- |
| outcome-only 会漏掉 provenance failure | Qwen-8B d80k：`VC 47%`、`SC 27%`、`GC 18%`、`OG 29pp`、`MI 78%`；fitness username 在各状态始终答对但 d80k source=`NONE` | Table 1、Figure 3、Table 3，pp. 6、8 | 直接支持“答案值不足以评估 evidence use”；但 source 仍是自报，不是因果依赖 |
| 状态退化不是单调曲线 | Qwen-4B `GC 54→18→1→34.4%`，Qwen-8B `69.8→54→18→44%`；Haiku/30B 在 S2 继续下降 | Table 1、Figure 4，pp. 6–7 | 描述性证据强；不能确定是 summary、position、workspace、index 还是 tool routing 导致 |
| open models 很少自发切换 tool retrieval | Qwen-4B/8B 在 C0 几乎不调用工具；Qwen-30B 只有 d0 34/200、S2 28/200；GPT-5 S2 为 50/200 | Figure 5、Section 4.2.2，p. 7 | Trace 支持“在这套 orchestration 下少调用”；不能纯归因于模型策略，parser/schema/runtime 也是混淆 |
| mandatory retrieval 修复 deep pre-compaction attribution | d80k `Cm−C0`：Qwen-4B `SC +78/GC +18pp`，8B `+56/+21pp`，30B `+33/+14pp` | Figure 6，p. 8 | 对 tool-compliant Qwen 成立；同时 HR 分别 `+28/+18/+76pp`，修复有显著保守性/误答代价 |
| post-compaction retrieval consistently regresses | S2 `Cm−C0`：Qwen-4B `SC −14/GC −25pp`，8B `−37/−26pp`，30B `−12/−8pp` | Figure 6，p. 8 | 说明强制检索不是通用修复；没有 workspace/index pre-post audit，不能说证据已被 compaction 销毁 |
| summary 加 citation 可修复 attribution | Qwen-8B S2：verbatim `SC/GC 79/44`，per-fact citation `95/47`；4B/30B 的 GC 反而下降 | Table 5、Appendix A.2，p. 11 | 只改善部分 source reporting，不能稳定改善 grounded answer |

### 数据、基线与指标

- **数据集**：6 个主 artifact、200 个手工问题；同一问题跨四状态。Filler 固定、topic-disjoint，内部有效性高但不代表自然长历史。
- **基线**：7 个 frontier/open-weight backbone；不是独立 memory system baseline 排行，而是 shared runtime 下的状态敏感性比较。
- **指标**：AC、SC、VC、GC、HR、WS、PF、MI、OG、DS、`Δcomp`、Ret；需同时区分 valid-only 与 intent-to-treat。
- **预算/硬件**：正文未给。公开仓库称 open-weight 运行使用 4×H100，但属于仓库事实，不能当作论文实验披露。
- **消融与稳定性**：evidence-type extension、3 种 compaction summary、depth normalization、tool parser check；主表为 3 次均值但没有 seed-level SD/paired CI。Table 9 的 Wilson CI 是单次 run 内二项区间，未处理 artifact clustering。

## 批判性阅读

### 证据支持的结论

- 在固定 runtime 与刺激下，多个模型的 grounded correctness 会随 state 大幅且非单调改变。
- 仅看 value correctness 会漏掉 source attribution failure；Qwen-8B d80k 的 29pp gap 是清楚实例。
- 对能可靠执行 tool contract 的 Qwen，强制检索可提高 d80k 的 SC/GC；同一干预会提高 HR，并在 S2 全部退化。
- Compaction summary 的来源格式改善不等于 grounded answering 改善。

### 尚未被充分支持的结论

- “compaction 销毁 stored evidence”没有被证明：未系统比较 compaction 前后 workspace 文件、hash、index 与 tool result。
- `R_tool+SC+VC` 也不是 proof-of-use；模型可能调用工具后仍依赖先验，需 retrieved-value counterfactual 才能检验因果依赖。
- “conversation state 是唯一变量”只在实验构造层成立；实际 state 同时改变 depth、position、filler、summary 和 compaction。
- Frontier/open 的差异不能解释为根本机制差异，因为 API tool support、context window、模型规模与 deployment stack 均未控制。
- 附录扩展只对 3 个 Qwen 报 SC，不能证明七模型/全部指标都跨 evidence type 泛化。

### 局限、风险与可能反证

- **样本聚类**：100 个 answerable questions 只来自 6 个 artifact；probe-level Wilson CI 可能严重低估 artifact-level 不确定性。
- **共享状态生态偏差**：所有 answerer 使用同一 checkpoint family，S2 summary 由 GPT-5 生成；提高可比性，却不代表各模型自行长期运行形成的 endogenous state。
- **Source self-report**：canonicalization 会把原图、派生 JSON、截图摘要和 dated memory note 归到同一 evidence ID；SC 衡量 attribution consistency，不等于真实内部 grounding。
- **PF denominator**：主指标只在 parse-success 样本上计算；InternVL d80k 有 78 PF，valid-only 可能选择性高估，应把 PF 计失败再做 sensitivity。
- **状态不等难**：d80k 只占 GPT-5 window 20%，却占 Gemma 63%；固定绝对 EIT 不是 normalized difficulty。
- **自然分布缺失**：topic-disjoint filler 去掉现实中的冲突更新、语义相近干扰和用户纠正；外部有效性有限。
- **Cm 是复合干预**：同时改变 prompt、强制工具、tool exposure 与 parser 路径，不能把差异只归因于 retrieval pressure。
- **公开复现不完整**：仓库有 200 题 bank、runner、scorer、tool plugin，但 raw logs/results 未发布，README 与论文模型/文案也有偏差。

## 与已有知识的连接

- **基础论文**：长会话 memory benchmark、tool-mediated retrieval faithfulness、personal Agent memory 与 state compaction。
- **相近方法**：[[notes/papers/2026/08/03/Beyond Retrieval- Analytic Memory for Multimodal Agents]] 将记忆外置为带 provenance 的表；[[notes/papers/2026/07/30/MemSecBench- Tracking Agent Memory Poisoning from Persistence to Consequence and Repair]] 追踪持久化到行为后果；ERPBench 核验外部事务状态。
- **后续工作**：workspace/index pre-post audit、retrieved-value counterfactual、artifact-cluster bootstrap、自生成 state、自然冲突历史与 intent-to-treat 评分。
- **与主题笔记的关系**：[[notes/topics/结构化中间层与可验证执行]]；MIRAGE 把 provenance 与 state perturbation 加到 outcome/evidence 链。

## 复现计划

- **是否复现**：是，先做 600-call 最小版，不追完整 28.8K calls。
- **最小验证目标**：1 个 chart+1 个 UI artifact，各 10 answerable/10 matched-unanswerable；Qwen3-VL-8B；`C0:{d0,d80,S2}` 与 `Cm:{d80,S2}`，每 cell 3 runs。
- **所需资源**：固定仓库/OpenClaw/Qwen snapshot、vLLM/ms-swift/CUDA 与 decoding 参数；保存 raw response、tool payload、workspace hash、EIT、compactionCount、PF 与 seeds。
- **成功标准**：C0/d80 出现 `VC>GC`；Cm/d80 提升 SC/GC；Cm/S2 不提升或下降；paired bootstrap/McNemar 与 artifact/run cluster bootstrap 均报告。
- **因果加测**：交换 retrieved value 看答案是否跟随；逐文件/hash/index 审计 compaction 前后 W，区分 evidence loss 与 lookup failure。

## 待追踪问题

- [ ] 把 PF 全计失败后，InternVL/Gemma 的结论是否改变？
- [ ] 模型输出 source ID 会不会只是格式模仿，而非对 retrieved payload 的因果使用？
- [ ] 各模型自行生成 summary/checkpoint 后，非单调轨迹是否保持？
- [ ] artifact-level cluster bootstrap 后，d50/d80/S2 的差异是否仍显著？
- [ ] 公开仓库是否补齐 paper runs、锁定依赖和可重算主表的原始结果？

## 原文定位

- 问题、same-answer/different-grounding 例子：Figure 1、Section 1，pp. 1–2。
- 状态、retrieval surface 与形式化：Sections 3–3.5、Eqs. (2)–(15)、Figure 2，pp. 3–5。
- 模型、样本量、条件与协议：Section 4.1，p. 5。
- 七模型 C0 全量结果：Table 1、Figure 3，p. 6。
- state transition、retrieval path、diagnostic：Figures 4–5、Table 2，pp. 7–8。
- mandatory retrieval 效果与 case studies：Figure 6、Table 3，p. 8。
- evidence-type、summary 与 tool parser 消融：Tables 4–5、Appendix A.1–A.4，p. 11。
- context normalization 与不确定性：Tables 8–9、Appendix A.5–A.6，p. 12。
