---
type: paper
title: "Logos: An Agent Harness on a Cross-Process Bus"
aliases: []
authors: ["Hanzhang Jia", "Liheng Zeng", "Hao Cheng", "Yi Gao", "Bo Ma"]
year: 2026
venue: "arXiv"
paper_date: "2026-08-28"
date_added: "2026-08-31"
last_read: "2026-08-31"
topics: ["agent-infrastructure", "distributed-systems", "fault-tolerance", "composability"]
status: read
priority: 2
rating:
arxiv_id: "2608.28553"
doi: ""
paper_url: "https://arxiv.org/abs/2608.28553"
code_url: ""
pdf_path: "library/raw/2026/08/31/2608.28553.pdf"
text_path: "library/text/2026/08/31/2608.28553.txt"
sha256: "9a22f970959c884c9ecca63c2dd04e9476566b56260e51306146f07aced905a2"
pages: 10
citation_key: ""
related: []
cssclasses:
  - paper-note
---

# Logos: An Agent Harness on a Cross-Process Bus

## 一句话结论

Logos 将 agent 的插件、组合和会话从单进程搬到 peer-process bus；在单机、可信网络和 append-only transcript 假设下，作者用故障注入展示了局部故障隔离与 cold-switch 恢复，但尚未证明多机网络分区、恶意节点或高吞吐生产场景下的端到端可靠性。

## 三分钟筛选

- **问题**：传统 agent harness 把工具、组合记录和多个 session 放在一个进程，单点故障会同时中断所有组件与会话。
- **新意**：把 plugin 定义为进程，把 composition/assembly 放到 bus，把 transcript 作为跨进程的唯一持久状态，并给出四个充分条件。
- **核心证据**：80 次在 tool-call 四个边界注入 kill 后均恢复且无重复副作用；3500 次并发调用无丢失、重复或误路由；单进程对照中一个 host fault 会中断全部共驻 session。
- **与我的关系**：直接关联 agent-infrastructure、session transcript、MCP/工具编排和故障恢复设计。
- **决定**：精读；适合做本地最小 bus/transcript 原型，不宜直接当生产级分布式一致性证明。

## 问题设定

- **输入、输出与目标**：harness 从 transcript 合成模型输入；模型输出工具调用；router 按 capability 转发；结果先写 transcript，再广播状态变化。
- **现有瓶颈**：单进程物理故障域、插件重载造成级联停顿、单语言运行时，以及会话状态与组件状态绑在一起。
- **关键假设**：模型推理是无状态纯函数；可逆 effect 的 anchor 在发生时持久化；每个 capability 只有一个 writer；组件 effect 两两独立或通过单写工具隔离。

## 核心贡献

1. Theorem 4.5：在 transcript 持久化和 single-writer 两条件下，将 spatiotemporal-composability 的 reversibility 从单进程推广到任意进程分配。
2. Logos 架构：Go router、Python/Node harness/tool peer、NDJSON/TCP bus、append-only JSONL transcript 和独立 event stream。
3. 覆盖 router/tool kill、冷切换、多会话、动态工具上线、重复注册竞争和单进程对照的故障测试。

## 方法

### 直觉

模型每一步只读写外部状态，因此 session 的连续性不需要留在模型进程内。只要把状态写入不属于任何单一进程的 transcript，新进程可以从前缀重建 projection 和 recovery accumulator；组件之间的恢复可局部执行。

### 形式化描述

- `H = (S, Π)` 的跨进程实现要求存在 faithful assignment，使实现轨迹在 macrostate projection `Π` 下与抽象轨迹逐点一致。
- Lemma 4.1 把跨步状态放到 shared sector；Lemma 4.2 用 persistent carrier 替代进程内 inverse history；Lemma 4.3 依赖 effect independence 做 recovery localization；Lemma 4.4 将 capability resolution 外置为 routing table。
- 工程约束 E1/E2/E3 分别对应 call-result 配对、单注册拒绝、广播顺序一致。

### 关键模块与训练流程

- **Router**：只持有 capability→connection routing table，负责 registration、forwarding、broadcast；不读取 payload。
- **Bus**：NDJSON over TCP；control message 至少一次投递并以 global call id 幂等配对；lossy stream 允许丢前缀但保持剩余序列连续。
- **Transcript**：每个 round、input、tool use/result、streamed text 都 append；projection 可裁剪长结果，但原文不删除。
- **Recovery**：新进程从 transcript 第一行重放；I1–I4 检查顺序、单调 id、每个 tool use 恰好一个 result、projection 一致。
- **动态组合**：工具缺失时显式拒绝；online broadcast 后自动 rebind；provider offline 后按 capability 重新解析。

### 计算与数据成本

实验全部在一台 AMD Ryzen 7 7435H、16 GB、Windows 11 上运行；router 用 Go 1.26，harness/tool 用 Python 3.13 与 Node.js 24。模型调用主要使用 DeepSeek V4 Flash、GLM-5.2/5.3、Claude Opus 4.6/5、GPT-5.4 等（第 6.1 节）。bus hop 中位数 0.215 ms，模型首 token 中位数 177 ms；transcript 是明文 JSONL，快照/压缩只列为未来工程项。

## 实验与证据

| 作者主张 | 对应证据 | 定位 | 我的判断 |
| --- | --- | --- | --- |
| 跨进程 bus 满足传输约束 | 3500 calls、最多 200 并发；无 loss/duplication/misattribution；100 个同名注册中 1 个成功、99 个显式拒绝 | p.2, §6.2, §6.5 | 支持工程可行性，但只测 loopback/受控网络 |
| process kill 后可恢复且不重复副作用 | 12 sessions/6 kills；额外 80 sessions 覆盖 tool execution、return-before-persist、persist-before-announce、announce 后四个边界，均完成且无重复 effect | p.2, §6.4, Fig. 2, §6.6 | 这是论文最强证据；仍依赖 transcript 写入顺序和 effect 边界可观测 |
| peer-process 缩小故障域 | 单进程 host kill 使 4/4 无辜 session 中断；peer 结构 10/10 只影响 faulty node；无故障 makespan 仅差 0.8% | §6.7, Table 4 | 对照公平性较好，但 workload 与机器规模有限 |
| 动态工具上线可被模型采用 | registry broadcast 后首次调用 8.4 s；3 次及扩展 10/10 成功 | §6.5 | 证明 late binding 路径，不证明模型在复杂任务中会正确选择新工具 |

### 数据、基线与指标

- **数据集**：合成 session、故障注入与并发压力场景；不是公开 benchmark。
- **基线**：spatiotemporal-composability calculus 的 reference implementation v0.1.0-rc.5 单进程配置，同样 fault/injection/criteria。
- **指标**：恢复成功率、重复 effect、loss/duplication/misattribution、hop latency、重启/重挂载时间、无辜 session interruption。
- **预算/硬件**：单机 16 GB；模型与 bus 同机，router/node 均独立进程。
- **消融与稳定性**：有单进程对照、四个 crash point、router/tool kill、并发与注册竞争；没有跨机器、网络分区、持久化损坏、恶意 provider 或长时间 soak test。

## 批判性阅读

### 证据支持的结论

- 在“可信 loopback/私有网络 + append-only transcript + 可重放 tool effect”条件下，分进程确实能降低单点故障的 blast radius。
- transcript 的 durable-before-visible 顺序是恢复正确性的核心，而不是 bus 本身自动提供 exactly-once。
- 进程间 hop 相比模型延迟小三个数量级，至少在论文 workload 中不会主导端到端时间。

### 尚未被充分支持的结论

- “reversibility holds across processes”是基于理想化状态空间和实现前提的充分条件，不是对任意外部 effect 的通用定理。
- 论文没有展示真实多机网络、磁盘损坏/双写、时钟漂移、重复提交到第三方 API、权限隔离和 transcript 加密。
- router 仍是单进程；其死亡窗口由 supervision 恢复，未给出持久 routing table 或多 router 共识方案。

### 局限、风险与可能反证

- 对付款、发消息、硬件动作等不可逆 outward effect，系统只提供 withholding/compensation，不能靠 transcript 精确回滚。
- “single writer per capability”在 provider 热迁移和租约失效时可能成为可用性瓶颈。
- 明文 transcript 含完整 session/tool 结果，存在隐私、注入和篡改风险；快照压缩与访问控制尚未实现。

## 与已有知识的连接

- **基础论文**：[[A Programming Paradigm for Spatiotemporal Composability]]；本文将其单进程 carrier 解释为可外置 transcript。
- **相近方法**：MCP 把 tool server 外置，Temporal 把 execution 外置；Logos 进一步把 composition/assembly 外置到 bus（Table 1）。
- **后续工作**：多 router、网络分区容错、加密 transcript、第三方副作用的 transactional/compensation adapter。
- **与主题笔记的关系**：agent-infrastructure、fault-tolerance、session transcript、MCP orchestration。

## 复现计划

- **是否复现**：待定
- **最小验证目标**：实现一个 router + 两个 tool peer + 一个 harness，用 JSONL transcript 覆盖 kill-before-persist 与 kill-after-persist 两个边界。
- **所需资源**：Go/Python/Node、本机 loopback、一个可替换模型或 mock model；不需要 GPU。
- **成功标准**：恢复后 transcript I1–I4 通过；已完成 tool effect 不重复；provider fault 不影响其他 session；记录恢复窗口。

## 待追踪问题

- [ ] transcript append 的 fsync/崩溃一致性边界是什么？
- [ ] 如何处理第三方 API 已提交但结果尚未写入 transcript 的窗口？
- [ ] 多 router 或跨主机 bus 是否仍能保持 E2/E3？
- [ ] 与现有 MCP/Temporal 的组合是否会产生双重重试或重复 effect？

## 原文定位

- Abstract–p.2：问题、架构与 80-session 摘要。
- §4.1–§4.4, pp.3–4：四个 lemma 与 Theorem 4.5。
- §5.1–§5.7, pp.4–6：router、transcript、event stream、recovery 与 deployment boundary。
- §6.2–§6.8, pp.6–8、Table 3–4、Fig. 2：延迟、故障、并发、对照与 replay verification。
