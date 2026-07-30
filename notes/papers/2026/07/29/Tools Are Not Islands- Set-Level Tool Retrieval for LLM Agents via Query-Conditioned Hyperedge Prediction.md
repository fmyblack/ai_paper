---
type: paper
title: "Tools Are Not Islands: Set-Level Tool Retrieval for LLM Agents via Query-Conditioned Hyperedge Prediction"
aliases: []
authors: ["Xinyi Hong", "Pinjun Dong", "Xinyang Yu", "Binyan Jiang"]
year: 2026
venue: "arXiv"
paper_date: "2026-07-28"
date_added: "2026-07-29"
last_read: "2026-07-29"
topics: ["Agent", "推理与规划", "长上下文与记忆"]
status: read
priority: 1
rating:
arxiv_id: "2607.25718"
doi: ""
paper_url: "https://arxiv.org/abs/2607.25718"
code_url: "https://github.com/stormwther18/HYSET"
pdf_path: "library/raw/2026/07/29/tools-are-not-islands.pdf"
text_path: "library/text/2026/07/29/tools-are-not-islands.txt"
sha256: "65056cfced60cbca697b0d41a812fc02e09af7d13bdbac8aab058c5dc616f0d3"
pages: 9
citation_key: ""
related: []
cssclasses:
  - paper-note
---

# Tools Are Not Islands: Set-Level Tool Retrieval for LLM Agents via Query-Conditioned Hyperedge Prediction

## 一句话结论

HYSET 把工具检索从“逐工具排序”改写为 query-conditioned hyperedge prediction：候选工具集合本身被评分，并用 cardinality-specific pairwise interaction 表达工具互补性；在严格固定下游 ToolLLaMA agent、工具预算和 3 seeds 的 ToolBench 实验中，COMP@5 与 pass rate 均领先，但主要增益来自 set-level scoring，execution feedback 的额外监督应与标注-only 结果分开解读。

## 三分钟筛选

- **问题**：真实任务往往需要多个 API 联合完成；逐工具相似度会重复召回同类工具，遗漏低单项相关但对完整任务不可替代的工具。
- **新意**：将工具共调用关系建成超图，用集合级 `F_set` 加 query-set alignment `F_align` 评分；交互矩阵随集合大小变化，允许同一工具对在不同 cardinality 下有不同兼容性。
- **核心证据**：ToolBench 上 HYSET(BERT) 标注+reward 的 Recall@5/NDCG@5/COMP@5/GPT-4 Pass/Human Pass 为 84.75/88.99/77.55/69.69/66.17；去掉 `F_set` 后 COMP@5 67.36、Pass 57.97；标注-only 时 COMP 仍为 77.02，但 Recall 降至 82.14。
- **与我的关系**：它位于 HiSkill 的上游：先选择一个完整、互补的工具集合，再由 Agent 的 skill/state 机制执行；同时提供了相对严谨的 set-level 对照范式。
- **决定**：精读并优先复现；代码与 demo 已公开。

## 问题设定

- **输入、输出与目标**：给定查询 `x` 和工具库 `V`，输出一个无序、可变大小的工具集合 `E`，覆盖任务所需的全部工具，并让冻结下游 Agent 在受限工具集上成功。
- **现有瓶颈**：BM25/dense 方法是独立 item scoring；graph-enhanced 方法最终仍做 top-k；generative 方法按序生成工具，集合完整性只能在生成后判断。
- **关键假设**：训练标注的 API 集合能作为可接受 ground truth；集合大小不超过训练最大 `M=5`；工具互补主要可由低阶 pairwise interaction 近似。

## 核心贡献

1. 以 tool co-invocation hypergraph 统一 semantic、graph-enhanced、generative retriever，并将集合而非单工具作为评分单位。
2. 用 cardinality-specific matrices `M_m` 表达随集合大小变化的工具兼容性，避免固定 pairwise redundancy/coverage 分数。
3. 设计不改下游 agent 的两阶段推理：先按单工具 relevance + complementarity 建 shortlist，再在小集合空间中枚举/重排；同时利用 execution feedback 做 reward-weighted self-training。

## 方法

### 直觉

“Flight”单独看很相关，但选中 Flight 后再选两个相似 flight API 可能不如补上 Hotel、Weather、Currency。集合级目标需要知道已选工具、集合大小和 query 之间的联合关系。

### 形式化描述

- 候选 hyperedge `E⊆V`，`1≤|E|≤M`；学习 `Fθ(x,E)` 并取 `argmax_E Fθ(x,E)`（Eq. 1）。
- 总分 `Fθ=F_set(E)+F_align(x,E)`（Eq. 2）。
- `F_set(E)=Σ_{a<b} z_{j_a}^T M_m z_{j_b}`，其中 `m=|E|`，使用共享工具 embedding `Z` 与 cardinality-specific `M_m`（Eq. 3）。
- `F_align` 用冻结 query encoder 的表示作为 cross-attention query，对集合内工具做 query-conditioned pooling（Eqs. 4–6）。
- 训练候选池含金标集合与负例；损失为 retrieval loss + `η` reward-weighted self-training + `λ` matrix regularization（Eqs. 8–11）。

### 训练与推理

- 负例按 50% size-matched uniform、30% in-batch、20% hard neighbor replacement 构造。
- `K1=15` 个单工具 seed 与补充互补工具形成 `Kpool=20` shortlist，`M=5` 时重排 21,699 个候选集合。
- 训练只更新 `θ=(Z,{M_m},P)`；query encoder、tool encoder、下游 ToolLLaMA-2-7B-v2 agent 和 DFSDT protocol 冻结。
- 推理得到的 `E` 是无序可变大小集合；另用 greedy marginal gain 生成 rank 序列供 Recall/NDCG 评估。

### 计算与数据成本

- ToolBench：13,860 个 callable endpoints、200,311 条指令、6 个 held-out test set 共 600 queries。
- BERT 配置训练参数 13.59M，固定 encoder 109.5M；`N_sub=5,000` queries 使用 execution feedback，每 20,000 steps refresh，最多 20,000 rollouts/judge calls。
- 推理约 12.4ms、3.21GB/query（库大小 13,860）；训练 43.2 GPU-hours，judge calls 约 USD186，使用 2×RTX 4090；所有方法使用缓存 StableToolBench API mirror，不访问 live endpoint。

## 实验与证据

| 作者主张 | 对应证据 | 定位 | 我的判断 |
| --- | --- | --- | --- |
| 集合级评分优于现有三类 retriever | HYSET(BERT) vs ToolGen：COMP@5 77.55 vs 70.01、GPT Pass 69.69 vs 62.30；Qwen 配置进一步到 78.13/71.11 | Table 1、Section 3.2，p. 6 | 支持完整工具集恢复，但 HYSET 主表含 execution feedback，必须先看 annotation-only 控制 |
| 主要收益来自 `F_set` | 去掉 `F_set`：COMP 77.55→67.36、Pass 69.69→57.97；去掉 execution feedback：COMP 77.02、Pass 65.14 | Table 2、Section 3.3，pp. 6–7 | 组件定位清晰：集合建模负责完整性，reward 主要影响最终执行成功 |
| cardinality-specific interaction 必要 | identity matrix/shared M/w/o regularization 逐级低于 Full；Set Transformer 在同目标下仍低于 HYSET | Table 2、Section 3.3，p. 7 | 这是方法最有说服力的 ablation，但需要更多不同 M 的直接实验 |
| 对工具/类别/领域转移有泛化 | cross-domain transfer 保留 79.9% in-domain set completeness；5-shot 恢复 full supervision 的 93.2%；UltraTool 上 COMP 比 ToolGen 高 11.5% | Table 3、Section 3.4，p. 7 | 支持一定 transfer；“unseen tool”协议需区分固定库内 held-out 与整库新工具 |
| set-level 推理成本可控 | 13,860 工具库仍 12.4ms，候选空间受 `Kpool,M` 控制 | Section 3.6，p. 8 | 工程数字有价值，但未覆盖下游 agent、judge 和 API latency |

### 数据、基线与指标

- **数据集**：ToolBench；额外在工具库完全不重叠的 UltraTool 验证。
- **基线**：BM25、Contriever、ToolLLaMA-Retriever、ToolRerank、COLT、ToolGen；另加 dense ranking、MMR、facility-location、DeepSets、Set Transformer。
- **指标**：Recall@K、NDCG@K、COMP@K（完整必需集合覆盖）、GPT-4 Pass Rate、Human Pass Rate；K=3/5。
- **公平性控制**：主结果每个方法至少给与 HYSET 一样多工具给 agent；对强 baselines 用相同 judge/reward/20,000-rollout budget 重训，reward advantage 缩小但 COMP margin 仍保留。
- **稳定性**：3 seeds、early stop on validation Recall@5；paired bootstrap、McNemar、exact significance test；报告误差条。

## 批判性阅读

### 证据支持的结论

- 工具检索确实存在 set completeness 问题，独立 top-k 不能可靠处理工具互补性。
- `F_set` 和 cardinality-specific matrices 对 COMP 的贡献大于 execution feedback，对“完整工具集合”与“下游是否成功”做了因果上较好的分离。
- 通过候选 shortlist 限制集合搜索，超图形式不必付出对全库幂集穷举的代价。

### 尚未被充分支持的结论

- 低阶 pairwise parameterization 是否足以覆盖更复杂的高阶工具组合，Theorem 1 说明“可产生高阶交互”但不等于实证学习到正确高阶结构。
- ToolBench/UltraTool 的 API 描述与标注是否完全代表真实工具库中的版本、权限、参数错误和调用顺序，论文没有在线实测。
- Pass rate 的 GPT-4/Human judge 与真实业务成功之间的偏差未被系统测量。

### 局限、风险与可能反证

- gold tool set 未必唯一；一个任务可能有多个等价 API 集合，单一 `E*` 会把合理替代误判成负例。
- `M=5` 由最大标注集合决定，超过 5 工具的组合、顺序约束和循环调用不在主问题内。
- execution feedback 依赖 20,000 次 rollout/judge calls；这会把额外监督预算引入 HYSET，虽然作者做了重训 baseline 控制，仍需单独核算成本。
- 固定工具库的 held-out tool/category 不等于动态新增工具；论文也把 dynamic library 列为未来工作。
- 负例池中的 false negative、ToolBench 文档重复和 API mirror 版本可能影响训练/测试边界。

## 与已有知识的连接

- **基础论文**：ToolLLM/ToolBench、ToolGen、COLT、ToolRerank、Set Transformer、hypergraph set functions。
- **相近方法**：[[notes/papers/2026/07/29/HiSkill- Empowering LLM Agents with Hierarchical Skill Graphs]]；HYSET 选工具集合，HiSkill 组织和执行程序经验。
- **后续工作**：动态工具库、工具权限/成本/调用顺序联合优化、非唯一 gold set 与 execution trace supervision。
- **与主题笔记的关系**：[[notes/topics/结构化中间层与可验证执行]]。

## 复现计划

- **是否复现**：是，优先级高。
- **最小验证目标**：固定 BERT backbone、ToolLLaMA agent、annotation-only objective，复现 Full、w/o `F_set`、Set Transformer 三臂；再单独加入 execution feedback。
- **所需资源**：HYSET 代码、ToolBench/UltraTool、缓存 API mirror、GPT-4/Human judge 配置；约 2×4090 级别训练资源。
- **成功标准**：3 seeds 下 COMP@5 方向与论文一致；记录候选集合大小、12.4ms 级别检索延迟、judge 成本和 false-negative rate。

## 待追踪问题

- [ ] 用等价工具集合标注替代单一 `E*` 后，HYSET 的 COMP 增益是否仍在？
- [ ] 当 M 从 5 增到 10、工具集合带有调用顺序时，cardinality-specific pairwise 是否足够？
- [ ] 对动态新增工具做 embedding 初始化后，zero-shot transfer 与旧库是否冲突？
- [ ] 将工具价格、权限、失败率和 latency 纳入 `Fθ` 后，Pass Rate 与真实 TCO 是否改善？

## 原文定位

- 动机与超图问题定义：Sections 1–2.3、Figure 1、Eqs. (1)–(2)，pp. 1–3。
- HYSET 评分、训练和推理：Section 2.4、Eqs. (3)–(14)、Figure 2，pp. 3–5。
- 主结果、公平性与消融：Tables 1–2、Sections 3.1–3.3，pp. 6–7。
- 转移、集合交付与成本：Sections 3.4–3.6、Table 3，pp. 7–8。
- 理论的 pairwise-decomposable 条件：Theorem 1、Supplementary A.4，p. 4 and supplement。
