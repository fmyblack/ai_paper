---
type: paper
title: "ESPO: Error-Structured Prompt Optimization via Diagnose, Diversify, and Stabilize"
aliases: []
authors: ["Lihao Liu", "Peng Tang", "Kunwar Yashraj Singh", "Shabnam Ghadar"]
year: 2026
venue: "arXiv"
paper_date: "2026-09-03"
date_added: "2026-09-04"
last_read: "2026-09-04"
topics: ["prompt optimization", "language models", "NLP", "evaluation"]
status: reading
priority: 2
rating:
arxiv_id: "2609.04197"
doi: ""
paper_url: "https://arxiv.org/abs/2609.04197"
code_url: ""
pdf_path: "library/raw/2026/09/04/2609.04197v1.pdf"
text_path: "library/text/2026/09/04/2609.04197v1.txt"
sha256: "7684b4a1d92fe7afbffc7a1ac8787ecb81ac3334fd0372105880d2c716868e01"
pages: 17
citation_key: ""
related:
  - "[[notes/papers/2026/09/04/Terminal-Universe- Turning Agent Trajectories into Scalable Terminal Environments]]"
  - "[[notes/papers/2026/09/04/Environment Evolution for Terminal Agents]]"
  - "[[notes/topics/终端Agent环境构造与课程学习]]"
cssclasses:
  - paper-note
---

# ESPO: Error-Structured Prompt Optimization via Diagnose, Diversify, and Stabilize

## 一句话结论

ESPO 将 prompt 优化从逐轮追加规则的 evolutionary search 改成“全量错误结构化诊断—多策略候选—bootstrap 稳定选择”；在七个 NLP benchmark 上相对 GEPA 平均提升 3.76 个百分点，同时 prompt 平均缩短 47%（74.67% vs 70.91%；页 1–2、5–6）。

## 三分钟筛选

- **问题**：GEPA 等反思式优化只看少量错误、使用单一 mutation、在小 validation set 上点估计选择，导致 prompt bloat、搜索偏差和选择噪声。
- **新意**：Diagnose 一次覆盖全部训练错误；Propose 用四种独立偏置生成候选；Select 用 20 次 bootstrap winner voting，并以短 prompt 打破平局。
- **核心证据**：Sonnet 4.5 学生的 7 数据集平均 74.67%/1,004 字符 vs GEPA 70.91%/1,878 字符；四个额外 student model 平均准确率均领先 GEPA。
- **与我的关系**：可用于优化 terminal-agent system prompt、verifier prompt 或环境生成 harness，但当前实验不覆盖 tool use、长上下文和多轮 Agent。
- **决定**：精读；先做低成本 prompt-search 复现，不把理论 bound 当作已验证保证。

## 问题设定

- **输入、输出与目标**：给定 `D_train/D_val`、学生模型 `m`、初始 prompt `p₀` 和 metric，输出测试准确率高且长度短的 prompt `p*`。
- **现有瓶颈**：训练错误观察不全（GEPA 每轮 3–8 条）、候选策略单一、约 30 条验证样本上的多重比较导致误选。
- **关键假设**：错误可聚成 3–7 个结构模式；四个 proposal strategy 具有部分独立偏置；最佳候选在 bootstrap 中胜率 `p₁>1/2`。

## 核心贡献

1. **Diagnose**：收集全部训练错误，由 reflection LLM 聚成 3–7 个 pattern（描述、代表样本、计数）。
2. **Propose**：diagnostic revision、consolidation、ablation、factual injection 四策略各生成 1–2 个候选，再做两轮 cross-pollination/refinement，候选池上限 10。
3. **Select**：对 30 条 validation 做 `B=20` 次 bootstrap，每次选准确率最高候选，按胜出次数投票；平局选短 prompt。

## 方法

### 直觉

先回答“错误模式是什么”，再让不同策略提出互补修复，最后问“这个候选在验证集重采样下是否稳定”；长度下降是 consolidation/ablation 的副产品，而非单独的长度惩罚。

### 形式化描述

`φ=D(E_train,p)`，`P=G(p,φ,S₁…S_K)`，`p*=R(P,D_val,B)`。作者给出非正式 bound：偏差 floor 由多策略降低，order statistics 带来探索增益，bootstrap 将选择误差项从 `O(1/√n_val)` 收紧到约 `O(√(ln K/(n_val B)))`。

### 关键模块与训练流程

70 train / 30 validation / 500 test；默认 `K=4,N≈10,B=20,m=all`。reflection 始终为 Claude Sonnet 4.5（T=0.7），默认 student 也是 Sonnet 4.5（T=0），另测 Gemma 3 12B、Mistral 14B、Qwen3 32B、Claude Haiku 4.5。

### 计算与数据成本

bootstrap 需要 `B×N` 候选-验证评估；作者称 ESPO 完整运行成本约等于默认 GEPA，reflection token 约为 GEPA 的 39%。实验仍依赖多次闭源 LLM reflection/student 调用。


## 实验与证据

| 作者主张 | 对应证据 | 定位 | 我的判断 |
| --- | --- | --- | --- |
| 作者主张 | 对应证据 | 定位 | 我的判断 |
| --- | --- | --- | --- |
| ESPO 同时提高准确率并减少 prompt bloat | 七任务平均 74.67% vs 70.91%，1,004 vs 1,878 chars；每行不低于 GEPA | §4.2、表 1、图 1（页 5–6） | 总体差距约 3.1× paired SE，但 HotpotQA/PUPA 在 1σ 内应视为 on-par。 |
| 收益不是单纯长度控制 | constrained GEPA 1,171 chars、71.00%，几乎不增准确率；ESPO 74.67% | §4.2、表 2（页 6） | 支持结构化诊断和稳定选择共同贡献。 |
| 跨模型泛化 | 四个额外 student 的平均准确率均高于 GEPA；Qwen3 GSM8K 35.4→91.4 | §4.3、表 3（页 7） | 有说服力但 reflection LLM 固定为 Sonnet，且弱 prompt 设置放大了 headroom。 |
| 三组件存在协同 | Tweet：Diagnose +2.0、Bootstrap +3.6、全量 +6.18；Diversity alone −1.20 | §4.5、表 4（页 8） | 支持“多样性必须配合稳定选择”，但只在 Tweet 做组件消融。 |
| 理论 bound 解释三个阶段 | Theorem 1、Lemma 1–3 与 coupon-collector 推导 | §3.5、附录 A–B（页 4–5、11–12） | 是设计动机和条件性解释，不是每个数据集的紧概率保证。 |

### 数据、基线与指标

- **数据集**：Tweet、MMLU、GSM8K、HotpotQA、ScoNe、HoVer、PUPA；70/30/500 划分。
- **基线**：Default、BootstrapFewShot、COPRO、MIPROv2、GEPA、Constrained GEPA。
- **指标**：accuracy、GSM8K/HotpotQA/ScoNe exact match、PUPA semantic F1、prompt chars、inference latency。
- **预算/硬件**：学生推理 deterministic；反思 Sonnet 4.5 T=0.7；每个主表 cell 以单次优化结果呈现，附 3 个独立 optimization seeds 的 ±std；500 测试样本的 95% binomial CI 在 p=.75 时约 ±3.8 pp。
- **消融与稳定性**：Diagnose/Diversity/Bootstrap 组件、K/B/m 超参、strategy diversity、constrained GEPA；完整 6×7×3-seed 网格在附录。

## 批判性阅读

### 证据支持的结论

- 实验从“故意很弱”的初始 prompt 开始，能证明 recovery，但不能代表已有高质量 system prompt 的增益；真实 Agent prompt 往往还含 tool schema、状态和多轮历史。
- `K=4` 候选并不真正独立：四策略共享同一 reflection LLM；附录给出 pairwise Jaccard 0.62、Pearson 0.48，理论独立性只是近似。
- 统计上七个数据集的平均差距较有利，但单数据集差距受 500 样本 CI 约束；GSM8K 已接近 ceiling，HotpotQA/PUPA 差距不显著。
- 论文没有把 optimizer 输出在新任务分布、工具调用、长上下文或多轮对话上验证；bootstrap 选择还要付出大量 student eval 成本。

### 尚未被充分支持的结论

- 

### 局限、风险与可能反证

- 

## 与已有知识的连接

- **基础论文**：GEPA、APE、OPRO、MIPROv2、DSPy、TextGrad、TRIPLE。
- **相近方法**：PromptBreeder、ReflectivePrompt、REMO、MemAPO、Promptolution。
- **后续工作**：将 ESPO 的 error schema 用于 Terminal-Universe 的 verifier/solver prompt，并测试 Environment Evolution 中 proposer/reviewer 的 prompt 稳定性。
- **与主题笔记的关系**：补充 [[notes/topics/Agentic数据、技能演化与VLM推理效率]] 的“数据/技能控制面”，也连接 [[notes/topics/Agent能力形成与过程验证]] 的过程验证。

## 复现计划

- **是否复现**：待定
- **最小验证目标**：在 Tweet/GSM8K/一个多跳 QA 子集上实现 `m=all,K=4,B=20`，与 GEPA 或等价单策略/点估计基线做 paired seeds。
- **所需资源**：可调用的同一 student/reflection model、公开数据、固定 70/30/500 split；若无法使用 Sonnet，需把模型变化作为显式实验因素。
- **成功标准**：平均准确率、prompt 长度、每例 latency 同时报告；单独报告 bootstrap 选择错误率与跨 seed 方差。

## 待追踪问题

- [ ] 在已有强 prompt 而非故意弱 prompt 上，ESPO 是否仍优于 GEPA？
- [ ] 误差聚类的 pattern 数量和 reflection model 改变时，候选是否稳定？
- [ ] 将验证集 bootstrap 选择迁移到 verifier pass-rate/工具调用成本，多目标选择是否仍有效？

## 原文定位

- 框架与公式：§3、式 (1)–(7)（页 3–4）；主结果：表 1、图 1（页 5–6）；长度控制：表 2（页 6）；跨模型：表 3（页 7）；消融/超参：表 4–5（页 8）；局限：§6（页 8–9）；理论证明：附录 A–B（页 11–12）。
