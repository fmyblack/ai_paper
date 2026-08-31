---
type: paper
title: "EvoUndo: Recoverability-Constrained Self-Evolution for LLM Agent Harnesses"
aliases: []
authors: ["Tanmay Sah", "Dolly Sah", "Harshul Jain", "Tanya Sah"]
year: 2026
venue: "arXiv"
paper_date: "2026-08-28"
date_added: "2026-08-31"
last_read: "2026-08-31"
topics: ["agent-self-evolution", "safety", "verification", "fault-tolerance"]
status: read
priority: 2
rating:
arxiv_id: "2608.28363"
doi: ""
paper_url: "https://arxiv.org/abs/2608.28363"
code_url: ""
pdf_path: "library/raw/2026/08/31/2608.28363.pdf"
text_path: "library/text/2026/08/31/2608.28363.txt"
sha256: "64861098dbbcb96a6f02d0828c1e5925cf6b3b2f4c44ae0692b0ca2582e1a647"
pages: 22
citation_key: ""
related: []
cssclasses:
  - paper-note
---

# EvoUndo: Recoverability-Constrained Self-Evolution for LLM Agent Harnesses

## 一句话结论

EvoUndo 把“能提升能力”与“能在反事实状态中安全恢复”绑定起来；在其六类沙盒 harness 状态和两种恢复语言内，表示能力与地址 grounding 是主要瓶颈，验证驱动修复可大幅提升成功率，但结果不等同于对真实分布式生产 harness 的完备安全保证。

## 三分钟筛选

- **问题**：LLM agent 会改 prompt、tool、middleware、listener、文件和资源；只优化 forward capability 会留下无法撤销的持久副作用。
- **新意**：候选是 `(m, w, u, Ce)`，其中 forward mutation `m` 固定，witness capture、recovery program 和 effect contract 在反事实状态上闭环验证。
- **核心证据**：600 个 unseen task 中 197 个 capability-positive mutation 初始恢复失败；`D0L1` 在预算 4 修复 180/197；`D1L0` 在语言足够的 S0 修复 38/48；`D1L1` 在 gpt-oss-120b 的 S1 反而低于 `D0L1`（133/143 vs 142/143）。
- **与我的关系**：直接关联 agent self-evolution、可审计状态变更、rollback/compensation 和工具/中间件动态重配置。
- **决定**：精读；优先复现其 failure taxonomy 与 recoverability verifier，而不是直接部署生成式 undo。

## 问题设定

- **输入、输出与目标**：harness `H=(S,Π)`；mutation `m:S→S'` 若 `J(m(S))-J(S)>0` 则 forward-improving；恢复要求 `u(m(s),w(s)) ≃Ce s` 在反事实状态分布 `Q` 上达到阈值。
- **现有瓶颈**：覆盖/重排配置会丢失 pre-state；静态 inverse 无法处理不同状态、结构化序列或多 surface mutation。
- **关键假设**：状态 surface 可被 typed snapshot/diff 观察；effect contract 能描述需要恢复的范围；恢复语言 primitives 的语义是可信的；实验状态局限于沙盒可控资源。

## 核心贡献

1. recoverability-constrained objective，把 capability gain、witness、recovery 与 observational contract 一起纳入 admission。
2. 两种恢复语言：`L0` 覆盖 config/prompt/tool/routing，`L1` 加入 middleware、listener、sandbox file、socket 与有序组合。
3. 2×2 `diagnostic granularity × language expressivity` factorial，分离 grounding 与 expressivity bottleneck，并做 Qwen3.8-27B replication。

## 方法

### 直觉

恢复不是“把一个固定命令再执行一次”，而是要读取 mutation 前的 witness，在状态不同、后续更新存在时恢复到 contract 定义的 observational equivalence。系统先验证 mutation 的真实 effect，再拒绝漏报或不可表达的恢复程序。

### 形式化描述

- Candidate `ξ=(m,w,u,Ce)`；repair 阶段锁定 `m=m0`，只改 `w,u,Ce`，防止通过把 mutation 变成 no-op 逃避恢复。
- `E(m,s)=SnapshotDiff(s,m(s)) ∪ ExecutionTraceEffects(m,s)`，admission 需满足 `E(m,s)⊆Ce`。
- `RL,Q,Ce(m)` 要求存在语言 `L` 中的 `(w,u)`，使 `Pr_{s~Q}[u(m(s),w(s)) ≃Ce s] ≥ τR`。
- admission 使用 hidden counterfactual 的 95% Wilson lower confidence bound，阈值 `τR=0.85`。

### 关键模块与训练流程

- **Witness capture**：mutation 前保存 typed pre-state；config scalar、middleware sequence、listener、file、socket 分别用不同 primitive。
- **Counterfactual verifier**：`Qdev` 提供诊断，`Qhid` 隐藏逐状态结果；fresh holdout 完全隔离反馈。
- **D0/D1 diagnosis**：D0 只给 subsystem/defect class；D1 增加 canonical state address 与 ordering trace。
- **L0/L1**：L1 支持严格 LIFO 的跨 surface 恢复；语言外 primitive、syntax error、exception 直接 fail closed。
- **Closed loop**：预算 `B∈{1,2,3,4}`，通过 verifier feedback 重写 `(w,u,Ce)`，开发集通过后再进 hidden admission。

### 计算与数据成本

主 factorial：gpt-oss-120b，MXFP4、temperature 0.2、medium reasoning、8× NVIDIA H200；197 个 natural failures，每个 10 development + 40 hidden states。fresh holdout 为 300 tasks、每个 100 hidden states。Qwen replication 为 96-task subset。主 cohort 平均每 task 1.78–2.40 calls，模型调用延迟 5.25–5.85 s；fresh holdout 约 2.39–3.09 calls、3.37k–4.30k tokens/task（§7）。

## 实验与证据

| 作者主张 | 对应证据 | 定位 | 我的判断 |
| --- | --- | --- | --- |
| verifier feedback 能修复表示范围内的缺陷 | controlled 120 defects：independent regeneration 4/120，typed diagnosis 114/120，prescriptive hint 117/120 | p.6, §5.1 | 说明闭环反馈有效，但 controlled defect 比 natural failure 容易 |
| natural failure 不是单纯 prompting 不够 | L0 下四种 repair 均 0/197；180/197 涉及 predefined taxonomy 外的 structural transformation | p.6, §5.2 | 强证据支持“表示/语言瓶颈”，但 failure generator 决定外推范围 |
| expressivity 是 S1 主瓶颈 | S1: `D0L0` 0/143 → `D0L1` 142/143，+99.30pp，Holm p=1.08×10⁻⁴² | p.7, §6.2 | factorial 对比清晰，依赖 oracle-defined stratum |
| exact address 并非总是更好 | gpt-oss-120b S1: `D0L1` 142/143 → `D1L1` 133/143，−6.29pp，pHolm=0.0117；Qwen 变化 +6.25pp、p=0.375 | pp.7–8, §6.3, Table 3 | 重要但模型依赖，不能泛化为“粗诊断优于细诊断” |
| L1 在 fresh tasks 上不只是 cohort 过拟合 | 300 fresh tasks；Q2→Q20 将 development-to-hidden false positive 从 16.8% 降至 0%，但 Rescue@4 从 49.7% 降至 35.0% | p.8, §7 | 支持 precision–coverage trade-off，不支持固定阈值最优 |

### 数据、基线与指标

- **数据集**：六类各 100 个 self-evolution task：Configuration、Tools、Middleware、Listeners、Resources、Multi-Surface；controlled 120 defects；fresh holdout 300。
- **基线**：independent regeneration、generic/raw/typed/prescriptive verifier feedback；effect-scoped snapshot、full snapshot；无 WAL/ARIES runtime 实验。
- **指标**：Rescue@B、Wilson LCB、paired risk difference、McNemar + Holm、forward capability regression、storage/latency。
- **预算/硬件**：8× H200；主模型 gpt-oss-120b 与 Qwen3.8-27B replication。
- **消融与稳定性**：L0/L1、D0/D1、B=1–4、τR=0.75–0.95、Q2/Q5/Q10/Q20、hidden n=10–100；stratum membership 在 10 次重采样中 Jaccard=1.0。

## 批判性阅读

### 证据支持的结论

- 对可表达的恢复任务，typed feedback 与更丰富 primitive 能显著提高 recovery synthesis。
- recoverability 是 mutation、witness、contract、language 和 counterfactual distribution 的关系属性，不是 mutation 的单一静态标签。
- stricter development verification 可减少 false positive，但会牺牲 yield；这对生产 admission policy 很关键。

### 尚未被充分支持的结论

- `L1` 只覆盖论文建模的 in-memory/sandbox surfaces，没有 formal completeness；不能推出任意 agent stack 都可恢复。
- repair 实验锁定 `m`，所以没有测 capability gain 与 recoverability 的 joint trade-off，也没有测 transactional redesign mutation 本身。
- 主要模型只有 gpt-oss-120b 与 Qwen3.8-27B；负 interaction 的跨模型普适性未知。

### 局限、风险与可能反证

- full snapshot 在后续状态并发变化时会 clobber state；effect-scoped snapshot 在已知 affected pre-state 时反而优于 EvoUndo（不同 surface 100% vs 81%）。
- distributed DB、第三方 API、unmanaged OS process、物理/金融副作用不在 contract 覆盖范围；这些需要分布式 observational contract 或 compensation。
- witness 可能包含秘密和个人数据；生产部署必须增加 ACL、加密、保留期限与字段脱敏。

## 与已有知识的连接

- **基础论文**：可逆 effect、view-update、ARIES/WAL、形式化 agent specification。
- **相近方法**：Vigil/AgentSpec 关注 runtime policy enforcement；EvoUndo 关注持久 mutation 的事后可恢复性，两者可组合。
- **后续工作**：adaptive coarse-to-exact diagnosis、snapshot/WAL/synthesis hybrid dispatcher、joint mutation–recovery search。
- **与主题笔记的关系**：agent-self-evolution、verification、fault-tolerance、rollback/compensation。

## 复现计划

- **是否复现**：待定
- **最小验证目标**：先复现 6 类 state surface 中 config overwrite、middleware prepend、listener registration 三类，验证 D0/D1 与 L0/L1 的方向性差异。
- **所需资源**：小型开源模型即可做机制复现；需要 typed state generator、hidden split、Wilson/McNemar 统计实现。
- **成功标准**：锁定 mutation 后，L1 相对 L0 的 rescue 提升可复现；exact-address 在 rich language 下不应被先验假设为单调增益。

## 待追踪问题

- [ ] hidden counterfactual generator 如何避免被 recovery language 过拟合？
- [ ] `Ce` over-declaration 的安全成本如何量化？
- [ ] 并发 mutation 与外部不可逆 effect 的 compensation contract 怎么定义？
- [ ] 能否将 EvoUndo 的 witness/transcript 与 Logos 的 append-only transcript 统一？

## 原文定位

- pp.1–3：动机、witnessed recovery、observational equivalence、目标式 (1)–(2)。
- pp.4–6：candidate、D0/D1、L0/L1、admission、task benchmark 与 oracle strata。
- pp.6–8、Table 2–3：controlled/natural failure、factorial、跨模型 replication、fresh holdout。
- p.9：snapshot 对照、局限、数据治理与部署边界。
