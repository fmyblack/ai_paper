---
type: paper
title: "HiSkill: Empowering LLM Agents with Hierarchical Skill Graphs"
aliases: []
authors: ["Yu Hao", "Jinxuan Cai", "Qi Zhang", "Yawen Li", "Zhiqiang Zhang", "Chuan Shi", "Cheng Yang"]
year: 2026
venue: "arXiv"
paper_date: "2026-07-28"
date_added: "2026-07-29"
last_read: "2026-07-29"
topics: ["Agent", "长上下文与记忆", "推理与规划"]
status: read
priority: 1
rating:
arxiv_id: "2607.25853"
doi: ""
paper_url: "https://arxiv.org/abs/2607.25853"
code_url: "https://github.com/BUPT-GAMMA/HiSkill"
pdf_path: "library/raw/2026/07/29/hiskill.pdf"
text_path: "library/text/2026/07/29/hiskill.txt"
sha256: "18e54b94c9f847e5ca74dd65892562bdaa4f1702183ecad3193d73d84ce1cd03"
pages: 26
citation_key: ""
related: []
cssclasses:
  - paper-note
---

# HiSkill: Empowering LLM Agents with Hierarchical Skill Graphs

## 一句话结论

HiSkill 将历史轨迹压缩成“高层 Skill—可执行 AtomicOp—五类关系边”的层次图，并在运行时用小型子图、显式任务状态和 active skill 驱动 LLM；它在 ALFWorld、WebShop、ScienceWorld 上同时提高成功率并显著减少推理 token，但证据主要来自文本交互环境，且离线图构建、LLM 提炼与轨迹采集成本没有进入效率核算。

## 三分钟筛选

- **问题**：现有 trajectory-to-skill 方法把经验存成彼此独立的高层文本规则，高层策略与真正可执行动作之间仍有落差，也难表示前置条件、顺序、支持和恢复关系。
- **新意**：将 skill 与 action template 分成两类节点，以 `decomposes_to`、`can_follow`、`compatible_with`、`supports`、`recovers_with` 五类边组织，并让运行时状态决定技能切换与 AtomicOp 选择。
- **核心证据**：Gemini-2.5-Pro 下，ALFWorld Seen/Unseen 成功率为 94.29%/91.79%，WebShop 成功率 67.60%，ScienceWorld Seen/Unseen 为 84.02%/81.04%；完整方法在所有消融上最佳，推理 token 相对最省基线降低 61.10%–94.12%。
- **与我的关系**：它把 Agent memory 从“检索文本”推进到“检索可执行局部程序图”，与 HYSET 的 set-level tool retrieval、PRO-LONG 的外部日志形成互补。
- **决定**：精读；代码已公开，值得在 ALFWorld 上做最小复现。

## 问题设定

- **输入、输出与目标**：给定历史成功/失败交互轨迹和新任务描述，离线构建技能图；在线检索任务相关子图，并在每一步选择 skill、AtomicOp 与具体环境动作以最大化任务成功。
- **现有瓶颈**：flat skill collection 忽略技能间关系；纯高层文本无法稳定落到动作参数；失败轨迹中的 recovery knowledge 没被结构化使用。
- **关键假设**：环境动作可被 schema canonicalizer 规范为模板；频繁成功片段代表可复用技能；状态摘要能可靠检测完成、缺失前置条件和停滞。

## 核心贡献

1. 从成功轨迹抽取 AtomicOp 与高层 skill，从失败轨迹提取 recovery evidence，构成带类型、有方向的层次技能图。
2. 用 dense embedding + BM25 选取两类 seed node，再按边方向做一跳 graph hydration，避免把完整经验库放进上下文。
3. 在线维护 symbolic task state 与 active skill，使 Agent 可以完成技能、切换后继技能、补前置操作或进入恢复分支。

## 方法

### 直觉

技能不是一段提示词，而应是能回答四个问题的局部程序：什么时候适用、由哪些原子操作组成、之后通常接什么、失败后怎样恢复。HiSkill 将这些关系显式化，再只把当前任务相关的局部图交给 LLM。

### 图构建

- 轨迹按终局奖励分成成功集 `T+` 与失败集 `T-`（Eq. 1）。
- schema canonicalizer 将原始动作的实体替换为 placeholder，合并同模板 occurrence 并累计 support count，形成 AtomicOp 节点。
- 在成功轨迹的 AtomicOp 序列中挖掘 frequent pattern，形成 skill 节点；每个 skill 存有有序 AtomicOp、前后状态、示例、参数候选、支持数和失败提示。
- LLM 只改写 skill 的名称、描述和 failure hint，不改变挖掘出的 AtomicOp 结构。
- 图 `G=(V,E)` 的关系集合为五类（Eqs. 2–3）；成功轨迹主要产生 decomposition、transition、compatibility、support，失败轨迹主要产生 recovery。

### 检索与运行时执行

- 查询由任务描述和初始 observation 拼接；节点相关度为 `λ Dense + (1-λ) Sparse`，skill 与 AtomicOp 分开取 top-K seed（Eq. 5）。
- graph hydration 加入 skill 的向外 `decomposes_to` 邻居和其他关系的入向邻居，保留选中节点间全部类型边（Eq. 6）。
- 运行时 task state 是 key-value memory，记录进展、持有物、当前位置、访问过的实体和近期失败（Eq. 7）。
- active skill 完成时走 `can_follow/compatible_with`，停滞时走 `recovers_with`；缺前置条件时选 `supports` AtomicOp；无可用节点时允许 LLM direct action。
- AtomicOp placeholder 根据任务、当前 observation、task state 和参数候选实例化为合法环境动作（Eq. 8）。

### 计算与数据成本

- 图构建轨迹量：ALFWorld 成功/失败 1,262/1,545，WebShop 646/996，ScienceWorld 800/535；另各留 10% validation。
- 图规模约 66–69 个 skill、112–134 个 AtomicOp、573–649 条边；平均检索子图约 8–14 个 skill、8–9 个 AtomicOp、62–70 条边（Table 5）。
- 论文只报告在线推理 token，没有给轨迹生成、LLM 文本提炼、embedding/BM25 索引和图构建的总 token、时间、API 费用或硬件。

## 实验与证据

| 作者主张 | 对应证据 | 定位 | 我的判断 |
| --- | --- | --- | --- |
| HiSkill 在三类环境上优于训练-free 基线 | Gemini 下 ALFWorld 94.29/91.79%，WebShop score/success 77.50/67.60%，ScienceWorld Seen 88.72/84.02、Unseen 84.20/81.04 | Tables 1–2，pp. 7–8 | 跨三环境与两 backbone 趋势一致，支持结构化经验有用；但环境均为文本交互 |
| 收益不只是 backbone 偶然性 | GPT-5.2-Codex 下仍取得或并列最优，跨数据集相对成功率提升均值 11.91% | Tables 6–7，pp. 22–23 | 两 backbone 是有效稳健性检查，但都很强且是闭源服务 |
| 层次图显著降低在线上下文 | 每任务 token：ALFWorld 6.5K/6.8K、WebShop 4.5K、ScienceWorld 7.7K/8.1K；相对最省基线降 61.10%/94.12%/66.76% | Table 3、Section 4.3，p. 9 | 在线 token 证据强；不能外推为端到端系统总成本降低 |
| graph representation 与 runtime mechanism 都必要 | Full 在五个 setting 为 94.29/91.79/67.60/84.02/81.04；w/o Atom、w/o Edge、w/o State、Static Subgraph 均下降 | Table 4、Section 4.4，pp. 10–11 | 组件消融较完整，尤其 `Static Subgraph` 排除了“仅把图当固定计划” |
| 自家图和执行器需要共同设计 | `OurG+GoSUse` 与 `GoSG+OurUse` 均高于 vanilla GoS，但低于 Full | Table 4、Section 4.4.4，pp. 10–11 | 交叉替换设计很好，支持 representation/consumer coupling |

### 数据、基线与指标

- **数据集**：ALFWorld、WebShop、ScienceWorld；Seen/Unseen 划分按既有工作设置。
- **基线**：ReAct、Reflexion；ExpeL、Mem0、MemP、SimpleMem；Vector Skills、SkillNet、GoS。
- **指标**：ALFWorld success；WebShop/ScienceWorld score 与 success；平均推理 token。
- **backbone**：Gemini-2.5-Pro 与 GPT-5.2-Codex。
- **稳定性**：实验执行 3 次并报均值，但主表没有标准差、置信区间或显著性检验。

## 批判性阅读

### 证据支持的结论

- 高层 skill 与可执行 AtomicOp 分层，比只检索 skill 文本或 flat vector skill 更适合长程交互。
- 一跳相关子图与显式 state 可以显著缩短在线 prompt，同时保持支持、恢复和切换路径。
- typed graph representation 和 runtime state machine 都贡献收益，不能把结果仅归因于更强检索。

### 尚未被充分支持的结论

- “更高效”只在在线 token 口径成立；离线轨迹、LLM 提炼、embedding、图构建和维护成本未计入。
- `recovers_with` 是否真正从失败轨迹学得可泛化恢复，而不是环境特定模板，缺少按 edge type 的精细介入分析。
- 论文没有证明该图能在线持续演化；结论末尾才将 online skill graph evolution 列为未来工作。

### 局限、风险与可能反证

- 三个环境都以文本 observation/action 为主，schema canonicalization 远比真实 GUI、网页 DOM 或机器人控制简单。
- LLM direct-action 是 escape hatch；没有报告它的触发比例，部分成功可能绕过技能图。
- 成功/失败轨迹、baseline memory 和图构建是否使用严格等量的信息预算，需要依赖代码进一步核对。
- 主表只有三次平均值无误差条；某些 ALFWorld 子任务已接近 100%，容易掩盖真实差异。
- 每个数据集单独调 `λ`，K=6 也由 validation 选择；跨域部署需要重新调参的程度不清楚。
- 静态图可能固化错误轨迹、过期操作或有害 recovery，论文未讨论 provenance、权限和冲突消解。

## 与已有知识的连接

- **基础论文**：ReAct、Reflexion、ExpeL、SkillNet、GoS、BM25 + dense hybrid retrieval。
- **相近方法**：[[notes/papers/2026/07/29/Tools Are Not Islands- Set-Level Tool Retrieval for LLM Agents via Query-Conditioned Hyperedge Prediction]] 解决工具集合；HiSkill 解决选定能力之后的程序组织与执行。
- **相近记忆**：[[notes/papers/2026/07/23/PRO-LONG- Programmatic Memory Enables Long-Horizon Reasoning]] 保存完整外部历史，HiSkill 则在写入时做有损程序抽象。
- **与主题笔记的关系**：[[notes/topics/结构化中间层与可验证执行]]。

## 复现计划

- **是否复现**：是。
- **最小验证目标**：只在 ALFWorld 复现 Full、Top-K Prompt、w/o Edge、w/o State 四臂，固定同一 LLM 和轨迹集合。
- **所需资源**：公开代码、ALFWorld、历史成功/失败轨迹、embedding 模型；不需要训练 backbone。
- **成功标准**：Full 相对 Top-K Prompt 和 w/o State 的方向一致；同时报告在线 token、离线图构建 token/时间、direct-action 触发率和 3 seeds CI。

## 待追踪问题

- [ ] direct-action 在三个环境中的触发比例与成功贡献是多少？
- [ ] 删除 `recovers_with` 的影响能否按“真正发生停滞”的 episode 单独统计？
- [ ] 图规模扩大 100 倍后，一跳 hydration 与 symbolic state 是否仍稳定？
- [ ] 轨迹错误、环境版本变化或相互冲突 skill 应如何维护 provenance 与失效策略？

## 原文定位

- 总体框架：Figure 2、Section 3.1，p. 4。
- 图构建、关系定义：Sections 3.2–3.2.2、Eqs. (1)–(3)，pp. 4–5；Appendix A，pp. 15–18。
- 子图检索与执行：Sections 3.3–3.4、Eqs. (4)–(8)，pp. 5–6；Appendices B–C，pp. 18–21。
- 主结果与 token：Tables 1–3、Sections 4.2–4.3，pp. 7–9。
- 消融与调参：Table 4、Figure 3、Sections 4.4–4.5，pp. 10–11。
- 数据/图统计与第二 backbone：Tables 5–7，pp. 21–23。
