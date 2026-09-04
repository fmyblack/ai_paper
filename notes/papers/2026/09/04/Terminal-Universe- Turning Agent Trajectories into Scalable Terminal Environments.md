---
type: paper
title: "Terminal-Universe: Turning Agent Trajectories into Scalable Terminal Environments"
aliases: []
authors: ["Jie Wu", "Zhenru Zhang", "Beichen Zhang", "Xuwu Wang", "Yuhui Su", "Mouxiang Chen", "Peng Wang", "Zhihai Wang", "Que Shen", "Hao Zhou", "An Yang", "Fei Huang", "Yujiu Yang", "Dayiheng Liu"]
year: 2026
venue: "arXiv"
paper_date: "2026-09-03"
date_added: "2026-09-04"
last_read: "2026-09-04"
topics: ["agents", "terminal environments", "reinforcement learning", "code agents"]
status: reading
priority: 1
rating:
arxiv_id: "2609.04148"
doi: ""
paper_url: "https://arxiv.org/abs/2609.04148"
code_url: ""
pdf_path: "library/raw/2026/09/04/2609.04148v1.pdf"
text_path: "library/text/2026/09/04/2609.04148v1.txt"
sha256: "681041b9963b4fc0d0d633046ee5a26a4d3177050d51f697a232ab7458cd36dc"
pages: 32
citation_key: ""
related:
  - "[[notes/papers/2026/09/04/Environment Evolution for Terminal Agents]]"
  - "[[notes/papers/2026/09/04/ESPO- Error-Structured Prompt Optimization via Diagnose, Diversify, and Stabilize]]"
  - "[[notes/topics/终端Agent环境构造与课程学习]]"
cssclasses:
  - paper-note
---

# Terminal-Universe: Turning Agent Trajectories into Scalable Terminal Environments

## 一句话结论

Terminal-Universe 把一次性的 Agent 轨迹反演成可执行、可复用的工作空间，再在同一空间内生成单仓库、跨仓库和多轮任务；在 Qwen3.5-27B 上，32.0k 条筛选后的示范使 Terminal-Bench 2.1 提升 11.9 个百分点、EvoCode-Bench v2 MT@4 提升 13.8 个百分点（作者报告，页 1–2、8–9）。

## 三分钟筛选

- **问题**：终端 Agent 轨迹规模大但环境稀缺；轨迹是冻结示范，环境才能被重复求解、验证和加难。
- **新意**：从工具执行记录重建环境，而不是从仓库历史、扰动或零起点生成环境；同时沿 breadth（Cross-WS）和 depth（Multi-Round）扩展任务。
- **核心证据**：68,263 个重建环境中 37,273 个被判定为 task-sufficient；31,977 条 verifier-filtered SFT 轨迹带来跨 benchmark 提升。
- **与我的关系**：直接连接 Agent 能力形成、可验证执行和 agentic data；可作为后续环境课程与过程监督的数据底座。
- **决定**：精读；若公开数据和重建代码可得，再做小规模复现。

## 问题设定

- **输入、输出与目标**：输入带有 Read/Write/Edit/命令记录的终端轨迹 `τ`；输出是未解决的可执行工作空间 `Ê`、任务 `q`、任务 verifier 和通过筛选的 solution trajectory。
- **现有瓶颈**：原始轨迹不可重解、无法确认修改正确；人工容器和 verifier 构造成本高；从抽象规格生成的环境往往过小且不真实。
- **关键假设**：轨迹暴露的文件操作足以恢复任务相关上下文；completion agent 能补齐缺失依赖而不泄露解法；agent-authored verifier 能可靠区分通过与失败。

## 核心贡献

1. **Environment reconstruction**：按时间回放文件操作得到部分工作空间，再由 completion agent 补齐文件、配置和依赖，最后由 sufficiency judge 过滤。
2. **Re-querying**：Intent Recovery 恢复原任务；Single-WS 在单仓库生成新任务；Cross-WS 连接有方向依赖的读写仓库；Multi-Round 让 user agent 逐轮改变或修正需求。
3. **Verifier-filtered data**：为任务生成 pytest verifier，保留通过轨迹；多轮任务保留至少两轮通过且保留可恢复的中间失败。

## 方法

### 直觉

轨迹和环境是同一 episode 的两个视角：常规方法是 `environment → rollout`，本文做逆映射 `trajectory → environment`。回放负责可观察状态，completion 负责不可观察但任务必需的上下文。

### 形式化描述

`τ → Ê₀`：对每个被访问路径取 agent 首次修改前的最早内容，排除 agent 自己创建/修改的文件；`(Ê₀,q) → Ê`：completion agent 补全项目；`Ê → {q_i, v_i}`：生成任务和 verifier；只保留 `v_i(Ê_after)=pass` 的轨迹。

### 关键模块与训练流程

1. Intent Recovery / Single-WS / Cross-WS / Multi-Round 生成四种任务。
2. verifier agent 在容器内写自包含测试；solver 使用 Qwen3.7-Max（xhigh）在 Claude Code scaffold 中滚动解决。
3. 用 31,977 条轨迹对 Qwen3.5-27B 做两 epoch SFT，再在 Terminal-Bench 与 EvoCode-Bench 上评估。

### 计算与数据成本

源轨迹 359,593 条，去污染和仓库去重后重建 68,263 个环境；completion 后 37,273 个 task-sufficient；最终 1.42B training tokens。单次 rollout 最多 500 turns、4 小时、256k context；训练使用 global batch 256、学习率 `7×10⁻⁶`、序列长 256k（页 6–8、附录 A）。


## 实验与证据

| 作者主张 | 对应证据 | 定位 | 我的判断 |
| --- | --- | --- | --- |
| 作者主张 | 对应证据 | 定位 | 我的判断 |
| --- | --- | --- | --- |
| 轨迹可转成大规模可用环境 | 68,263 重建、37,273 task-sufficient；completion 后 Terminal sufficiency 40.2%→93.5% | §4.2、表 2、图 4–5（页 7–8） | 证据充分，但 sufficiency 是 agentic judge 判断，不等于所有任务都可稳定构建。 |
| 重解比模仿原轨迹更有效 | Intent Recovery Avg 52.1 vs source-trajectory SFT 36.7 | §6.1、表 4（页 9–10） | 对照控制较好，同数据量和 schema 隔离了“重解”因素。 |
| completion 与 verifier 有增益 | completion 52.9 vs replay-only 48.7；Cross-WS verifier 55.4 vs 无 verifier 53.2 | §6.2–6.3、表 5–6（页 10） | 支持“上下文恢复”和“过滤”各自有用，代价是大量丢弃轨迹。 |
| breadth/depth 扩展改善泛化 | Single-WS+Cross-WS 58.4；加入 Multi-Round 后 MT@4 21.0、Case 76.9 | §6.4–6.5、表 7、9（页 11–12） | 任务分布与 benchmark 仍高度相关，不能直接推出真实软件工程泛化。 |
| Full Mixture 提升终端 Agent | TB2.1 46.2→58.1，EvoCode MT@4 6.3→20.1 | §5.2、表 3（页 8–9） | 六次/四次独立运行和去污染是优点；仍需独立复核 scaffold 与 verifier。 |

### 数据、基线与指标

- **数据集**：LFM2-Terminal、LiteCoder-Terminal、SWE-rebench、SWE-smith、CoderForge、SWE-Gym；评估 Terminal-Bench 2.0/2.1、EvoCode-Bench v2。
- **基线**：source-trajectory SFT、replay-only、Single-WS、Cross-WS、Multi-Round 及 Terminal task synthesis 方法（表 1、3）。
- **指标**：Avg Pass@1、EvoCode MT@4、Case score、workspace sufficiency、teacher pass@1。
- **预算/硬件**：训练两 epoch；评估容器 12 CPU/32 GiB（Terminal-Bench），EvoCode 单任务最长 10 小时；teacher rollout 最高 4 小时。
- **消融与稳定性**：re-solving、completion、verifier、Cross-WS、Multi-Round、环境/查询/解答扩展轴均有消融；TB 结果取六次独立运行。

## 批判性阅读

### 证据支持的结论

- 回放只恢复被访问内容；未访问文件、隐式系统依赖、外部网络资源可能永久缺失。completion 不是无偏恢复，而是由同一类 agent 推断出的补全。
- 37,273 是“被 judge 认为足够”，不等于 37,273 个环境都经过独立人工验证；30 个随机 completion 检查中有 8 个加入了不必要的大文件/代码（附录 B）。
- 一个 Qwen3.7-Max 同时生成任务、解和 verifier，存在能力上限、共同偏差和漏测错误；作者明确将独立 verifier 留给未来工作。
- Ubuntu 24.04 通用容器降低成本，但专用系统依赖、复杂编译和数据许可可能造成 fidelity 风险。

### 尚未被充分支持的结论

- 

### 局限、风险与可能反证

- 

## 与已有知识的连接

- **基础论文**：[[notes/papers/2026/08/03/AgentHPOBench- A Benchmark For Evaluating LLM Agents as Sequential Hyperparameter Optimizers]]（过程反馈与 verifier 口径）。
- **相近方法**：SWE-Gym、SWE-smith、CLI-Gym、CLI-Universe、RST、CalibForge（表 1、相关工作）。
- **后续工作**：与 [[notes/papers/2026/09/04/Environment Evolution for Terminal Agents]] 组合成“环境重建→难度课程”；与 [[notes/papers/2026/09/04/ESPO- Error-Structured Prompt Optimization via Diagnose, Diversify, and Stabilize]] 的 verifier/prompt 控制形成方法互补。
- **与主题笔记的关系**：补充 [[notes/topics/Agent能力形成与过程验证]] 中“可验证执行”和 agentic data 的环境层。

## 复现计划

- **是否复现**：待定
- **最小验证目标**：从公开 trajectory 重放出未解决工作空间，比较 source-SFT 与 re-solve-SFT 在同一小型终端任务集上的差异。
- **所需资源**：公开轨迹及许可、容器运行时、一个能写 verifier 的强模型、独立测试执行器；完整 1.42B-token 训练不可作为个人默认预算。
- **成功标准**：回放/补全 workspace 的任务可解率、独立 verifier 通过率、source vs re-solve 的 paired pass-rate 提升；记录 completion 泄露和错误补全比例。

## 待追踪问题

- [ ] 公开代码、原始轨迹和 37.3k 环境是否可获取，许可是否允许再训练？
- [ ] 独立 verifier 或人工复核后，TB2.1 提升是否仍成立？
- [ ] Cross-WS 的收益来自跨仓库依赖本身，还是更长的 token/turn 预算？

## 原文定位

- 摘要与贡献：页 1–3；框架：图 1–2（页 2、5）；重建统计：表 2、图 4–5（页 7–8）；主结果：表 3（页 8–9）；消融：表 4–11（页 9–12）；局限：页 13；数据源与泄露过滤：表 12–14（页 17–19）。
