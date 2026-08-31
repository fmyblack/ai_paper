---
type: paper
title: "A Programming Paradigm for Spatiotemporal Composability"
aliases: []
authors: ["Yifan Shi", "Wei Zhang", "Tianyi Cui"]
year: 2026
venue: "arXiv"
paper_date: "2026-08-26"
date_added: "2026-08-31"
last_read: "2026-08-31"
topics: ["programming languages", "software composition", "reversible effects", "coeffects", "runtime systems"]
status: read
priority: 2
rating:
arxiv_id: "2608.25512"
doi: ""
paper_url: "https://arxiv.org/abs/2608.25512"
code_url: ""
pdf_path: "library/raw/2026/08/31/2608.25512v1.pdf"
text_path: "library/text/2026/08/31/2608.25512v1.txt"
sha256: "390775dbc9debdcf2ed1b076eed013387ca057630be3cb594617b2b742e48cf0"
pages: 92
citation_key: ""
related: []
cssclasses:
  - paper-note
---

# A Programming Paradigm for Spatiotemporal Composability

## 一句话结论

论文把动态组件组合拆成两个可证明的维度：用带显式逆的 `revertible effects` 解决卸载时的时间可组合性，用按依赖满足度反应式触发的 `reactive coeffects` 解决运行时空间可组合性；其 calculus 在一组较强假设下给出恢复、依赖顺序、终止与合流定理，并由 Cordis/Koishi 做了生产存在性验证，但没有性能对照或自进化 Agent 实验。

## 三分钟筛选

- **问题**：如何让运行中的组件在动态加载、卸载、重配置时既能撤销自己的环境修改，又能随 provider/consumer 拓扑变化安全地重算依赖？
- **新意**：把 effect/coeffect 从静态、词法作用域提升为运行时 context 机制；每个 effect 携带逆，依赖变化触发组件激活/停用，并在统一 context 上定义组件级 calculus。
- **核心证据**：Theorem 68/70/71 分别给出交错恢复、依赖生命周期顺序与解析一致性；Theorem 73 在无环、有限名字、有限迭代前提下证明无死锁/终止；Theorem 80 给出与从头加载相同的合流正规形（Section 4.3，pp. 44–55）。
- **与我的关系**：对 self-evolving agent harness 的运行时热替换、工具/记忆/权限依赖有直接概念价值，但论文没有 Agent harness 的实验验证。
- **决定**：精读；暂不复现，先关注其前提是否能映射到 Agent 系统。

## 问题设定

- **输入、输出与目标**：输入是可动态插入、移除、重配置的组件；输出是组件生命周期和共享 context 的稳定状态，目标是在不中断整个进程的情况下恢复组件贡献并重算依赖。
- **现有瓶颈**：传统插件往往只能重启宿主进程；静态 DI/模块导入不能处理运行时依赖出现、消失或换 provider；手写 `deactivate` 难以保证完整清理（Section 1.1–1.2，pp. 4–6）。
- **关键假设**：所有可管理交互都经由 context key；effect 作者提供正确逆；同一 key 的操作满足 commutativity witness；provision 不重叠；依赖/实例化关系无环；迭代长度和运行中 fiber 名字有限。

## 核心贡献

1. `Revertible effects`：effect 类型为 `Γ → Γ × (Γ → Γ)`，运行时累积逆函数，按 LIFO 卸载；`effect iterator` 允许异步/分段执行（Definitions 8–18，pp. 12–16）。
2. `Reactive coeffects`：coeffect context 是带类型族的有限依赖表；`notify_d` 将每次 context 变化分类为 activating/deactivating/neutral，驱动依赖组件生命周期（Definitions 19–22，pp. 17–18）。
3. `Context paradigm + calculus`：统一 effect/coeffect context，以组件 `(d,p,e)`、fiber、target/committed view 和 guard 组织九条规则；在 observational equivalence 下证明全局时空可组合性（Definitions 28–30、48–56，pp. 21–38）。
4. `Cordis`：`ctx.effect/use/set/get`、isolation/interception、声明式 loader、HMR；Koishi 用 4000+ 社区插件作为生产案例（Section 5.1–5.3，pp. 57–70）。

## 方法

### 直觉

把组件看作“对共享 context 的一段可撤销事务”和“对其他 key 的声明式依赖”。加载时逐步执行 effect 并保存每一步逆；卸载时反向执行。provider 进入卸载后先停止对外提供，依赖它的 consumer 先完成 teardown，最后 provider 才真正回收。

### 形式化描述

`effect` 在 `Γ` 上返回新状态和只需在当前状态成立的逆；`effect_Γ` 把它提升到带 accumulator 的 context。统一 context `Γ∞ = μΓ. Γ × (Γ → Γ) × Σ` 同时保存递归父 context、当前层 accumulator 和 coeffect 表。组件的 effect iterator 只能在其声明的 `d ∪ p` key 上读写（Confinement，Definition 55–57）。

跨组件安全不是“两个 composite effect 相等”，而是更强的 `independence`：两边所有 forward/inverse transformation 彼此交换，且不改变对方 iterator 产生的 inverse/continuation（Definition 42）。在 context-mediated 纪律、key-local 操作和 commutative coeffect witness 下，Theorem 47 将该条件归约到 key 层。

### 关键模块与训练流程

无模型训练；这是 programming-language/runtime 设计。实现分三层：core library（effect tracking、coeffect notification、lifecycle）、component loader（配置 reconciliation、realm 管理、HMR）、上层应用框架（Koishi）。异步宿主采用 inertial 语义：transition 运行到边界后再响应 target 变化（Section 4.4，pp. 55–57）。

### 计算与数据成本

论文未报告 benchmark、延迟、内存、吞吐、故障率或开发效率对照；只给出 92 页形式化与算法描述，以及 Koishi 的生产采用情况。实现使用 TypeScript/Node.js 语义，论文未提供 `code_url` 或可直接复现实验包。

## 实验与证据

| 作者主张 | 对应证据 | 定位 | 我的判断 |
| --- | --- | --- | --- |
| 单组件 effect 可在卸载时恢复其 context 贡献 | accumulator 组合逆；Theorem 7、16；跨 fiber 交错时 Theorem 68/Corollary 69 | Sections 3.1、4.3.2，pp. 11–16、44–47 | 在 witness、confinement 和 observational equivalence 前提下是形式化结果；不是物理状态逐字节回滚 |
| 依赖变化会以正确顺序触发停用/激活 | `target`/`committed view`、`relied` guard；Theorem 70/71 | Sections 4.2.2、4.3.3，pp. 35–49 | 依赖生命周期顺序论证较完整，但只覆盖 context 内可 reify 的依赖 |
| 任意调度最终达到从头加载等价的状态 | Theorem 73（progress）与 Theorem 80（confluence） | Sections 4.3.4–4.3.5，pp. 49–55 | 强假设下的 operational metatheory；不保证中间 emission 可撤销，也不覆盖失败 fiber 的合流 |
| Cordis 能支撑真实开放插件生态 | Koishi 4000+ 社区插件、服务端与 web console 两个 Cordis 应用 | Section 5.3，pp. 69–70 | 是 existence/adoption evidence；作者明确承认单生态、单宿主语言、无受控对照 |

### 数据、基线与指标

- **数据集**：无数据集；Koishi 生产插件生态（4000+ plugins）为案例背景。
- **基线**：无受控架构基线；只在 related work 中概念性比较 VSCode、OSGi、HMR、DI、FRP 等。
- **指标**：无定量指标；主要是定理成立条件、算法对应关系和案例观察。
- **预算/硬件**：未报告硬件、运行时开销或规模上限；实现语境为 TypeScript/Node.js。
- **消融与稳定性**：无 ablation、随机种子、重复实验或统计区间。

## 批判性阅读

### 证据支持的结论

- 形式化结论真正证明的是“在 context-mediated、可逆、可交换且无环的受限世界中，动态生命周期可组合”；不是任意 JavaScript side effect 都能被安全回滚。
- Theorem 80 的正规形依赖 `total on provision`；论文承认组件只在某些配置安装 provision 时，最终加载集合也会依赖配置/运行路径。

### 尚未被充分支持的结论

- runtime 不检查 effect 返回的逆是否正确，也不检查 coeffect 操作是否真的 commutative；这些 witness 是组件作者责任（Section 5.1.1，p. 59）。
- system boundary 外的 emission（网络发送、持久化写入等）按 `id_Γ` 处理，不能由 calculus 自动撤销；只能 withholding 或应用更粗粒度 compensation（Section 6.1，pp. 70–71）。
- 依赖图有环时组件永久 inactive；key 仅按名连接，独立构建的 provider/consumer 仍有 interface drift 与 key collision（Sections 6.5–6.6，pp. 74–76）。
- HMR 采用“撤销旧组件、干净重载新组件”，不会自动迁移组件私有内存状态；与 DSU 的 state migration 互补而非替代（Section 7.3，pp. 79–81）。

### 局限、风险与可能反证

- 若组件把未经过 context 的全局变量、线程、定时器或外部句柄藏在闭包中，confinement 不成立，形式化恢复结论不能覆盖。
- `total on provision`、无环和有限实例化是合流/终止的必要前提；开放插件生态若允许任意自实例化或循环依赖，需要额外检测与策略。
- 单一 Koishi 案例无法区分 Cordis 抽象、TypeScript 实现和领域工程实践的贡献，也无法说明大规模通知/依赖图下的性能。

## 与已有知识的连接

- **基础论文**：Moggi 的 monadic effects、Plotkin/Pretnar 的 algebraic effects、Petricek 等的 coeffects；论文 Section 2 给出定位。
- **相近方法**：OSGi Declarative Services/iPOJO（可用性反应式服务）、Nooks/Akeso（运行时资源回收）、Webpack/Vite HMR（模块替换）、FRP signals（值级反应式）。
- **后续工作**：作者提出把 Cordis 接到 self-evolving agent harness，验证高频自修改下的恢复与依赖协调；当前只是 future validation（Section 8，p. 83）。
- **与主题笔记的关系**：[[notes/topics/动态软件组合与可逆运行时]]；与 [[notes/topics/Agent外部状态的增长、验证与压缩]] 的连接点是“状态/工具生命周期的可归属与撤销边界”。

## 复现计划

- **是否复现**：待定
- **最小验证目标**：用 TypeScript 写两个 provider/consumer 和一个可中断 iterator，验证 provider 替换、consumer 先 teardown、逆按 LIFO 执行，以及非 context emission 不会被误称为已恢复。
- **所需资源**：Node.js/TypeScript；论文未给出独立代码仓库，需依据 Algorithms 1–7 自行实现最小原型。
- **成功标准**：在不同 lifecycle 调度顺序下，context 内状态与从头加载等价；故意破坏 inverse、引入依赖环和跨边界 emission，确认失败模式符合论文限制。

## 待追踪问题

- [ ] 查找 Cordis v4 的公开实现与版本差异，确认论文算法是否已在仓库落地。
- [ ] 在 Agent harness 中定义哪些状态属于 context 内 acquisition，哪些属于不可回滚 emission。
- [ ] 测量 `ctx.effect`/notification/guard 的运行时开销，并与重启或手写 cleanup 基线比较。

## 原文定位

- Page / Section / Figure / Table / Equation：摘要 p. 1；Definitions 8–18（pp. 12–16）；Definitions 19–30（pp. 17–22）；Definition 42/Theorem 43/47（pp. 27–30）；Theorem 64、68–73、80（pp. 43–55）；Algorithms 1–10 与 Table 2（pp. 58–69）；案例与限制（pp. 69–76、82–83）。
