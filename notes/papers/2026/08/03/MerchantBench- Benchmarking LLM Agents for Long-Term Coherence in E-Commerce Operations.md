---
type: paper
title: "MerchantBench: Benchmarking LLM Agents for Long-Term Coherence in E-Commerce Operations"
aliases: []
authors: ["Qiming Shi", "Yulong Tao", "Linbo Jin", "Zhaolu Kang", "Yibo Dou", "Jiawen Zhu", "Tianjun Pan", "Shaokang Fu", "Chengyu Wang", "Siyue Li", "Yaping Cheng", "Di Weng", "Chengfu Huo"]
year: 2026
venue: "arXiv"
paper_date: "2026-07-31"
date_added: "2026-08-03"
last_read: "2026-08-03"
topics: ["Agent", "Benchmark 与评估方法", "长期任务评估"]
status: read
priority: 1
rating:
arxiv_id: "2607.28956"
doi: ""
paper_url: "https://arxiv.org/abs/2607.28956"
code_url: ""
pdf_path: "library/raw/2026/08/03/2607.28956v1.pdf"
text_path: "library/text/2026/08/03/2607.28956v1.txt"
sha256: "d2248fae1becae6d77c173a96727aca621c8e6d1985ff9976de2752d10b22a20"
pages: 36
citation_key: ""
related: []
cssclasses:
  - paper-note
---

# MerchantBench: Benchmarking LLM Agents for Long-Term Coherence in E-Commerce Operations

## 一句话结论

MerchantBench 把 Agent 评测从“完成一个边界清楚的任务”推进到“在 365 天内持续经营同一个电商店铺”：它用 98,843 条真实 1688 商品记录、订单级延迟反馈和 26 个商家工具构造长程 POMDP，显示最强 LLM+框架组合只达到人类平均最终净资产的 27.3%；这强烈支持“长期一致性”仍是当前 Agent 的短板，但结论受模拟器口径、少量人类基线和框架能力不等价影响。

## 三分钟筛选

- **问题**：现有 Agent benchmark 多是短任务、即时反馈、明确完成条件，难测真实部署中长期目标保持、延迟反馈归因和跨月策略修正。
- **新意**：把 seller-side e-commerce 建成 365 天订单级仿真；动作会影响现金、商品组合、订单、罚款和店铺评分，异常订单/供应商事件以不同延迟显现。
- **核心证据**：8 个 LLM × 2 个框架 × 3 次运行共 48 个 LLM runs；最佳配置 Qwen3.7-Max + Hermes 最终净资产 59.46k RMB，而 3 名人类均值为 217.61k RMB，约为 27.3%。
- **与我的关系**：它是“长期 Agent 评估”的很强案例，和 AgentHPOBench 一起说明 benchmark 需要把 feedback latency、state persistence、final-step preservation 单独拉出来看。
- **决定**：精读；优先作为长程 Agent benchmark 参照，不急于复现完整 365 天环境。

## 问题设定

- **输入、输出与目标**：Agent 观察当前店铺、供应商、订单和市场报告，通过商家工具做选品、上架/下架、定价和订单/现金流管理；最终目标是最大化 terminal net assets，即现金、保证金、在途资金和应收账款之和。
- **现有瓶颈**：短任务 benchmark 无法区分一次性成功和长期经营能力；延迟订单结果要求 Agent 把后来的退款、差评、缺货等反馈归因到早先选品/定价；静态商品集合也无法测试持续机会发现。
- **关键假设**：1688 商品记录、需求曲线和平台信号足以近似电商经营中的长期反馈；模拟器的处罚、评分和需求乘数能代表真实业务约束；人类新手操作可作为可解释但非专家上限。

## 核心贡献

1. 提出 Long-Term Coherence 评测口径：Agent 需要在持久环境中维持目标导向，并根据累积证据更新策略。
2. 构建 365 天、8,760 小时步的部分可观测电商经营环境，包含真实商品数据、非平稳需求、上游供应事件和下游订单结果。
3. 用 ReAct 与 Hermes 两种框架评估 8 个 LLM，并通过业务指标、活动指标和轨迹分析刻画 Operational Coherence 与 Strategic Coherence 失败。

## 方法

### 直觉

电商经营的难点不是“会不会调用一个上架工具”，而是早期动作会锁定现金和商品组合，订单风险又在数天后才暴露。一个长期一致的 Agent 必须持续检查、归因、修正，而不是等环境自己恢复。

### 形式化描述

- 环境建模为有限时域 POMDP `M=<S,A,P,O,Z,R,mu0,Hc>`；`Hc=8,760` 小时，Agent 每 12 小时获得一次 decision window。
- 状态包含时间、需求、供应商条件、店铺 listing/finance、活跃订单和未实现事件；未来需求、风险参数和预采样结果对 Agent 隐藏。
- 终局奖励为 `R(s_T)=B_T+D_T+I_T+Q_T`，分别对应现金余额、保证金、在途资金和应收账款。

### 关键模块与训练流程

- **真实数据 grounding**：1688 平台 2025-06-01 到 2026-05-31 的 365 天商品级需求、商品/供应商属性和质量/履约信号；过滤后 98,843 个商品、36,576 个供应商、10 个一级类目。
- **上游供应模拟**：PriceChange、ProductDelisting、ShipmentDelay；Agent 可通过目录/供应商查询看到已发生变化，但不知道触发概率和恢复时间。
- **下游订单模拟**：商品需求转为单件订单；订单经历采购、发货、交付、结算，并可能出现 Cancellation、Stockout、LateShipment、ReturnlessRefund、ReturnAndRefund、BadReview。
- **Agent 接口**：26 个 merchant tools 覆盖日报、商品查询、上架/下架、改价、订单查询、现金管线、店铺快照等。ReAct 只用这些工具；Hermes 还带代码执行、规划、记忆和 skill 管理。

### 计算与数据成本

- 每个 LLM+框架组合 3 次运行，单次模拟 365 天；总计 48 个 LLM runs。
- 初始资金为 2,000 RMB 现金 + 1,000 RMB 保证金，最多 50 个 active listings。
- ReAct 在 160k token 历史时提醒模型写入 persistent memory 并截断到最近 30k；Hermes 使用默认上下文总结，summary model 与被测模型相同。

## 实验与证据

| 作者主张 | 对应证据 | 定位 | 我的判断 |
| --- | --- | --- | --- |
| 当前 LLM Agent 与人类长期经营差距很大 | 最佳 LLM 配置 Qwen3.7-Max + Hermes 最终净资产 59.46k RMB；人类均值 217.61k RMB；最佳 LLM 约为 27.3% | Table 1，p. 5；Abstract，p. 1 | 强证据说明长程经营仍困难；人类样本只有 3 人且非专家，不能当作稳定 human ceiling |
| Agent framework 显著影响长期结果 | Hermes 相对 ReAct 平均最终净资产 +53.3%、GMV +71.5%、订单数 +71.2%；7/8 模型净资产更高 | Section Main Results，p. 5 | 说明“模型能力”与运行时框架不可分；也使模型横向排名更难归因 |
| 失败不只是单次选品错误，而是长期活动衰减和策略漂移 | LLM 的 SWR 在 ReAct 下 10.6%–99.4%，Hermes 下 17.8%–66.1%；部分模型工具调用和 effective window rate 随季度下降 | Table 1，p. 5；Figure 5，pp. 6–7 | 对 Long-Term Coherence 的分解很有价值，比只看 final assets 更可诊断 |
| 延迟订单反馈要求产品级归因和替换策略 | GPT-5.6 Sol/KimiK2.6 能把异常归因到 listing 并替换，Qwen3.7-Plus/DeepSeek-V4-Pro 部分轨迹未及时修正 | Order-Level Risk Propagation，p. 6 | 这是定性轨迹证据，解释力强，但需要更系统的 trace coding 才能量化 |
| 市场需求非平稳性要求持续 portfolio allocation | 人类 demand alignment 从 6 月 56.1 升到 12/1 月 80+，且伴随冬季利润峰值；部分 LLM 需求对齐弱或不能转化为利润 | Figure 6，p. 7 | 支持“静态商品集不够测长期能力”；但 demand alignment 本身不是最终目标 |

### 数据、基线与指标

- **数据集**：98,843 个 1688 商品、36,576 个供应商、365 天需求和 365 份市场日报；覆盖 10 个一级类目。
- **基线**：8 个 LLM 在 ReAct 与 Hermes 下运行；Rule-based baseline；3 名无电商经验的人类操作者。
- **指标**：Final Net Assets、GMV、Net Profit Margin、Orders、Fines、Average Store Rating、Order Anomaly Rate、Average Active Listings、SWR、Tool Calls。
- **预算/硬件**：论文主要报告模拟运行和 token/context 管理，没有给完整 API 成本；每个配置 3 runs。
- **消融与稳定性**：有跨框架比较和三次重复分布；没有严格的 simulator parameter ablation 或 framework component ablation。

## 批判性阅读

### 证据支持的结论

- 长程 Agent 评测需要订单/事件级持久状态和混合延迟反馈；单步 tool-use 分数无法覆盖这个能力。
- 当前强 LLM 在长期目标保持、持续行动和证据校准上仍明显弱于人类新手。
- 框架层的记忆、代码执行和 skill 管理能放大部分模型能力，但不是普遍稳定收益。

### 尚未被充分支持的结论

- “电商长期一致性”是否能代表其他长期真实部署场景，还需要跨领域验证。
- Hermes 相对 ReAct 的收益来自代码、记忆、skill 还是提示模板，论文没有做组件级归因。
- 人类均值很高，但样本小、时间安排和界面经验可能影响结果；不能据此估计专家上限。

### 局限、风险与可能反证

- 仿真器依赖 1688 数据和人工设定的处罚/评分/需求乘数，真实平台竞争、广告、物流协商和外部流量没有完全覆盖。
- 部分“失败模式”来自人工 trace 解读，尚缺统一标注协议、置信区间和 inter-rater reliability。
- LLM/API 版本、Hermes built-in skills 和 summarization 都可能漂移，复现实验需固定 agent stack。
- 最终资产指标会混合风险偏好、规模扩张和利润率；高订单量不一定更优，单一终局值也可能掩盖中途破产风险。

## 与已有知识的连接

- **基础论文**：ReAct；Vending-Bench / RetailBench；长程 Agent 与 business simulation benchmarks。
- **相近方法**：[[notes/papers/2026/08/03/AgentHPOBench- A Benchmark For Evaluating LLM Agents as Sequential Hyperparameter Optimizers]] 同样关注多步反馈利用，但 MerchantBench 更长、更开放、业务状态更复杂。
- **相近记忆**：[[notes/papers/2026/07/29/HiSkill- Empowering LLM Agents with Hierarchical Skill Graphs]] 的 recovery/skill graph 可作为 MerchantBench 中活动衰减和策略漂移的潜在干预机制。
- **与主题笔记的关系**：[[notes/topics/Agent能力形成与过程验证]]、[[notes/topics/结构化中间层与可验证执行]]。

## 复现计划

- **是否复现**：待定。
- **最小验证目标**：不复现完整 8 模型矩阵，先复现 1 个开源模型 + rule-based baseline 的短周期版本，验证 SWR、活动衰减和延迟反馈归因指标是否可重现。
- **所需资源**：公开模拟器/数据、1 个稳定 agent runtime、可控 LLM、运行日志和订单级 trace。
- **成功标准**：能重现活动衰减/延迟反馈误归因中的至少一个失败模式，并报告成本、日志长度、summary 触发点和最终资产方差。

## 待追踪问题

- [ ] MerchantBench 是否公开完整模拟器和 98,843 商品数据，还是只公开部分/脱敏版本？
- [ ] 能否对 Operational Coherence / Strategic Coherence 建立自动化 trace classifier？
- [ ] Hermes 的 code、memory、skill 三类能力分别贡献多少？
- [ ] 如果把目标从净资产换成风险调整收益或破产概率，模型排名是否改变？
- [ ] 人类专家、电商运营新手和 rule-based strategy 的差距如何？

## 原文定位

- 问题动机与 Long-Term Coherence 定义：Abstract、Introduction、Figure 1，pp. 1–2。
- POMDP 与终局净资产目标：Task Formulation、Eqs. (1)–(2)，p. 2。
- 数据 grounding 与需求/供应/订单模拟：Figure 2、Real-World Data Grounding、Eqs. (3) 起，pp. 3–4；Appendix Figures 11–12，p. 14。
- Agent 工具与实验设定：Agent Interface、Experimental Setup，pp. 4–5；Appendix Evaluation Protocol / Tool Sets，pp. 12–13。
- 主结果：Table 1、Main Results，p. 5。
- 长期一致性失败分析：Figures 4–6、Long-Term Coherence Analysis，pp. 6–7。
- 完整工具/提示/可见字段：Tables 2–11，pp. 21–36。
