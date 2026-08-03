---
type: paper
title: "AgentHPOBench: A Benchmark For Evaluating LLM Agents as Sequential Hyperparameter Optimizers"
aliases: []
authors: ["Tianyu Huai", "Tingshuo Fan", "Xinchi Chen", "Yining Zheng", "Yuxin Wang", "Shuang Chen", "Jie Zhou", "Xuanjing Huang"]
year: 2026
venue: "arXiv"
paper_date: "2026-07-31"
date_added: "2026-08-03"
last_read: "2026-08-03"
topics: ["Agent", "Benchmark 与评估方法", "科学智能", "自动机器学习"]
status: read
priority: 1
rating:
arxiv_id: "2607.29626"
doi: ""
paper_url: "https://arxiv.org/abs/2607.29626"
code_url: "https://github.com/OpenMOSS/AgentHPOBench"
pdf_path: "library/raw/2026/08/03/2607.29626v1.pdf"
text_path: "library/text/2026/08/03/2607.29626v1.txt"
sha256: "d9c395c0c4f5c25bc5a83b5fde380b60c0d19e47d9b8621b3eef8c7cd0692ec8"
pages: 69
citation_key: ""
related: []
cssclasses:
  - paper-note
---

# AgentHPOBench: A Benchmark For Evaluating LLM Agents as Sequential Hyperparameter Optimizers

## 一句话结论

AgentHPOBench 把 AI research agent 的一个关键子能力单独剥离出来：能否读懂已完成实验的配置、指标和日志，并在 5 次连续干预中提出下一个有效超参配置。结果显示强 Agent 确实优于传统 HPO 的 final-step 表现，但 best-so-far 诊断又让传统 HPO 反超多数开源 Agent，说明当前 Agent 的短板不只是“找不到好配置”，还包括不能稳定保留和细化早期收益。

## 三分钟筛选

- **问题**：现有 ML Agent benchmark 常把数据处理、代码修改、debug、架构设计、超参调优混在一起，难判断 Agent 是否真的能基于实验反馈做 sequential HPO。
- **新意**：30 个真实 GitHub ML repo、7 类研究任务、固定 baseline、受限 intervention space、统一 harness、5 次 sequential interventions，并用 MBNS/BWR/MAA 区分相对提升、覆盖率和 anchor attainment。
- **核心证据**：limited-budget 下 Claude Sonnet 4.6 final-step MBNS/BWR/MAA 为 0.407/76.7%/79.5%；Qwen3-32B 是最强开源 MBNS 0.148；无中间反馈时 Qwen3-32B MBNS 从 0.148 降到 0.052。
- **与我的关系**：它是“科学智能 Agent 评估”的重要基线，特别适合用来研究反馈利用、实验诊断和 trajectory preservation。
- **决定**：精读；可作为未来复现/agent harness 对照。

## 问题设定

- **输入、输出与目标**：每个任务给定一个真实 repo、固定 baseline 配置、可选超参空间、目标指标和 paper/repo anchor；Agent 每一步观察历史配置、指标、日志，输出下一个合法配置；最终按第 5 次干预结果评分。
- **现有瓶颈**：传统 HPO benchmark 多是干净 objective interface；ML Agent benchmark 又过于综合，无法隔离“从实验反馈到下一次配置”的能力。
- **关键假设**：受限搜索空间足以代表该 repo 中有意义的超参调优；5 次干预能揭示 sequential refinement；最终一步结果比 best-so-far 更能测 Agent 是否会保留/改进已有收益。

## 核心贡献

1. 构造 30 个 executable ML research repositories 的 HPO task suite，覆盖 NLP、CV、time series、graph、RL、LLM、structured learning。
2. 提供统一 execution harness：验证输出配置、执行实验、记录完整 trace、审计 baseline/interventions/metrics。
3. 系统比较 12 个 Agent/模型与 random search、TPE、BOHB-style baseline，并报告 limited budget、full budget、harness ablation、feedback ablation、best-so-far 和不确定性分析。

## 方法

### 直觉

真正的研究实验不是一次性猜超参，而是看上一轮跑出来的 target metric、auxiliary metrics 和 logs，再判断该保守、探索还是回滚。AgentHPOBench 把这件事从庞杂的“做研究”任务中抽出来，专门测 Agent 的连续实验判断。

### 形式化描述

- 对任务 `t` 和预算 setting `r`，固定 reference baseline `x_{t,0}`，执行得到 `y_{t,0}`。
- 第 `k` 次干预时，Agent 观察 trace history `H_{t,k-1}={tau_{t,0},...,tau_{t,k-1}}`，提出 `x_{t,k} in Omega_t`。
- harness 执行后得到 `y_{t,k}`，5 次干预形成完整 trajectory。
- 评分使用 final intervention：`NS=(s-b)/(a-b)`，再 bound 到 `[-1,1]` 得到 BNS；总体报告 MBNS、BWR 和 MAA。

### 关键模块与训练流程

- **Task construction**：从原 repo 的训练脚本、配置文件或文档构造 intervention space；只保留影响执行/结果的字段，数据集、split、metric、evaluation code 固定。
- **Execution harness**：统一 prompt/context、配置校验、任务执行、结果解析、审计和聚合；配置会被解析为结构化 schema。
- **Limited budget protocol**：baseline 和每次 intervention 约使用原实验 10% 训练/评估预算；每任务 5 次干预。
- **Full budget protocol**：只改变执行预算，保留任务定义、prompt、intervention space、5-decision protocol 和 scoring pipeline。
- **No intermediate feedback ablation**：保留 baseline observation，但隐藏前 1–4 次 intervention 的指标、辅助输出和日志。

### 计算与数据成本

- 30 tasks，每个 Agent 150 个 accepted logical decisions。
- 开源模型和传统 HPO baseline 用 3 个 seeds `{0,1,42}`；API Agent 每个只做 1 个 audited 30-task run。
- 受控实验在 Linux + NVIDIA H200 143,771 MiB 显存机器上运行；每个任务有独立 Conda 环境和预下载权重/数据。
- API campaign 记录 1,231–1,695 requests，约 8.2–11.3 requests / accepted decision，包含 retries 和 validation recovery。

## 实验与证据

| 作者主张 | 对应证据 | 定位 | 我的判断 |
| --- | --- | --- | --- |
| 强 API Agent 在 final-step sequential HPO 上领先 | Claude Sonnet 4.6 limited-budget MBNS 0.407、BWR 76.7%、MAA 79.5%；GPT-5.5 MBNS 0.305 | Table 2，p. 6；Main Results，p. 8 | 支持强，但 API 只跑一次，不能解释 provider-side 方差 |
| 开源 Agent 有可测优化能力但明显弱于最强 API Agent | Qwen3-32B 是最强开源 MBNS 0.148、MAA 69.1%；Phi-4-14B BWR 63.3% 最高 | Table 2，p. 6 | 说明能力存在但不稳定，尤其类别分布差异很大 |
| 传统 HPO 在 final-step 指标下整体落后，但不是完全无效 | BOHB variant MBNS 0.018、MAA 65.3%；random search BWR 48.9% 最高 | Table 2，p. 6 | 对比公平性不错，因为预算和 intervention count 一致；但传统 HPO 没有日志/文本上下文 |
| 中间实验反馈对 Agent 有实质贡献 | Qwen3-32B 去掉中间反馈后 MBNS 0.148 -> 0.052，BWR 60.0% -> 50.0%，MAA 69.1% -> 65.2% | Table 5，p. 9；Section 4，p. 10 | 很关键，直接支持 benchmark 测到 feedback use，而非只靠 baseline + prior |
| final-step 与 best-so-far 测的是不同能力 | best-so-far 下 random/TPE/BOHB MBNS 分别 0.325/0.298/0.291，超过所有开源 Agent；作者解释 final-step 同时测搜索质量与保留/细化早期收益 | Section 11.3，p. 24 | 这是全文最有洞见的诊断之一，说明 Agent 可能会覆盖掉已经找到的好配置 |
| harness 本身会影响结果 | Claude Sonnet 4.6 native harness MBNS 0.407 vs Claude Code CLI 0.332；GPT-5.5 native 0.305 vs Codex CLI 0.266，但 CLI 的 BWR/MAA 可更高 | Table 4，pp. 8–9 | 提醒不要把 agent pipeline 排名误读为纯模型排名 |

### 数据、基线与指标

- **数据集**：30 个 GitHub repo tasks，7 类：NLP、CV、time series、graph、RL、LLM、structured learning。
- **基线**：random search、TPE、fixed-budget BOHB variant；6 个开源模型 Agent；6 个 API Agent。
- **指标**：MBNS、BWR、MAA；另报告 full-budget final-step、best-so-far、task-bootstrap CI 和 paired comparisons。
- **预算/硬件**：limited budget 约原任务 10%；full budget 用原 repo 完整预算；受控实验 H200 + Python 3.10+ + per-task Conda。
- **消融与稳定性**：feedback ablation、harness ablation、3-seed open-weight runs、20,000 category-stratified bootstrap；API 无 repeated seed。

## 批判性阅读

### 证据支持的结论

- Agent 能够利用实验日志和指标改善超参，但能力在类别、预算和运行框架之间高度不均匀。
- 中间反馈确实有用；去掉 feedback 后 Qwen3-32B 大幅退化。
- best-so-far 与 final-step 必须同时报告，否则会混淆“找到好点”和“最终停在好点”。

### 尚未被充分支持的结论

- API Agent 的排名稳定性没有 repeated run 支持；作者也明确说 hosted endpoint 不暴露固定 checkpoint/seed。
- 该 benchmark 测的是可见 objective 的优化，不是自适应模型选择后的隐藏测试泛化。
- Agent 与传统 HPO baseline 比较的是完整 pipeline；Agent 多了任务描述、日志和自然语言上下文，传统 HPO 多了 incumbent-style 返回习惯，二者能力边界不同。

### 局限、风险与可能反证

- 论文明确指出部分任务使用 test metric 或 validation-selected test metric 作为可见 objective，因此不能解释为 hidden test generalization。
- 30 个任务虽然比单 repo 强，但 bootstrap 显示 benchmark composition uncertainty 不小；小差异不能当确定排名。
- 每个 upstream repo 的环境复杂且依赖 Conda/权重/数据，复现成本高，adapter 维护成本也高。
- final-step 作为主指标会惩罚传统 HPO 不返回 incumbent 的协议差异；best-so-far 诊断缓解但不能完全消除设计选择影响。
- API campaign 的 request count 远高于 logical decisions，说明 parsing/validation/retry 也是系统行为的一部分。

## 与已有知识的连接

- **基础论文**：HPOBench、YAHPO Gym、MLGym、MLE-Dojo、PaperBench、RE-Bench、MLR-Bench。
- **相近方法**：[[notes/papers/2026/08/03/MerchantBench- Benchmarking LLM Agents for Long-Term Coherence in E-Commerce Operations]] 评估业务长期一致性；AgentHPOBench 评估科研实验反馈利用。
- **相近记忆**：[[notes/papers/2026/07/29/Interactive Reward Agent- GUI Task Evaluation via Environment-State Verification]] 都强调可执行环境和结果审计，而不是文本自评。
- **与主题笔记的关系**：[[notes/topics/Agent能力形成与过程验证]]、[[notes/topics/结构化中间层与可验证执行]]。

## 复现计划

- **是否复现**：是，做小规模优先。
- **最小验证目标**：选 3 个轻量任务，复现 random/TPE/BOHB、Qwen3-32B 或本地可用模型、no-intermediate-feedback 三臂，比较 final-step 与 best-so-far。
- **所需资源**：AgentHPOBench repo、对应 task assets/Conda env、单机 GPU 或 CPU-friendly tasks、固定 seeds、日志解析工具。
- **成功标准**：能重现“feedback 有用”和“best-so-far 与 final-step 排名不同”两个方向，并报告每任务运行时间、失败/重试率和配置合法性错误。

## 待追踪问题

- [ ] GitHub repo 是否包含 30 个任务的完整 assets、adapters、validation scripts？
- [ ] 哪些任务使用 test metric 作为优化目标，是否能改成 validation-only 再测泛化？
- [ ] 如果 Agent 被允许返回 incumbent/best-so-far，排名如何变化？
- [ ] 日志诊断失败能否分类为 over-exploration、premature exploitation、误读日志、非法配置、覆盖早期收益？
- [ ] 传统 HPO 如果接入日志特征或 LLM summary，能否缩小差距？

## 原文定位

- 问题动机与贡献：Abstract、Introduction、pp. 1–3。
- task/harness 结构：Figure 2、Sections 3.1–3.3，pp. 4–5。
- 评分定义：Section 3.4、Eqs. (6)–(11)，pp. 6–7；Appendix Section 10，pp. 21–22。
- 主结果：Table 2、Main Results，pp. 6、8。
- full-budget / harness / feedback ablation：Tables 3–5、pp. 8–10。
- 任务列表和 baseline：Tables 6–7，pp. 16–17。
- prompt、API usage、复现细节：Figures 4–6、Tables 8–9，pp. 18–21。
- best-so-far 与 bootstrap：Sections 11.2–11.3、Tables 11–14，pp. 23–26。
