---
type: paper
title: "Interactive Reward Agent: GUI Task Evaluation via Environment-State Verification"
aliases: []
authors: ["Chenrui Shi", "Yuwei Wu", "Yang Liu", "Ruining Feng", "Zirui Shang", "Zhi Gao", "Lifeng Fan", "Che Sun"]
year: 2026
venue: "arXiv"
paper_date: "2026-07-28"
date_added: "2026-07-29"
last_read: "2026-07-29"
topics: ["Agent", "Benchmark 与评估方法", "后训练与对齐"]
status: read
priority: 1
rating:
arxiv_id: "2607.25904"
doi: ""
paper_url: "https://arxiv.org/abs/2607.25904"
code_url: "https://kendrick-stein.github.io/InteractiveRewardAgent-OfficialRepo/"
pdf_path: "library/raw/2026/07/29/interactive-reward-agent.pdf"
text_path: "library/text/2026/07/29/interactive-reward-agent.txt"
sha256: "86576a26eec6e0338498f3eb32c825812daf00863483ccf5c753b351adb3c03e"
pages: 29
citation_key: ""
related: []
cssclasses:
  - paper-note
---

# Interactive Reward Agent: GUI Task Evaluation via Environment-State Verification

## 一句话结论

Interactive Reward Agent（IRA）把 GUI 任务评价从“看截图直接猜成功”改成“先提出任务完成条件，再用系统、应用和 GUI 工具逐条取证”；在 321 条 Ubuntu 轨迹上 GPT-5.5 准确率从同 backbone 的 VLM-only 78.5% 提升到 86.9%，但平均每任务 59.5K token（中位数 14.9K），且工具交互可能改变被评环境，因而它更像高质量、昂贵的 verifier，而不是免费 reward model。

## 三分钟筛选

- **问题**：截图无法确认文件内容、保存持久性、应用配置或跨应用 artifact；脚本 evaluator 准确但每个任务都需手工编写，VLM evaluator 可扩展但只能使用被动视觉证据。
- **新意**：将 evaluator 设计成 propose-then-verify Agent：从 instruction 与首末截图提出条件，再为每个条件自主选择系统、应用或 GUI 工具，直到获得明确证据。
- **核心证据**：GUI-RewardBench 共 321 条稳定重放轨迹（192 artifact、89 hidden-state、40 visible-state）；IRA 三个 backbone 均超过被动基线，GPT-5.5 86.9% accuracy/F1 84.9%；RL 中 IRA reward 34.0% OSWorld success，接近脚本 reward 34.9%。
- **与我的关系**：它与 DDB 分工互补：DDB 诊断过程中的状态转移理解，IRA 验证终局环境是否满足显式条件；两者可组成 CUA 的 process/endpoint 双层评测。
- **决定**：精读；适合用于研究 verifier 设计和 reward channel 成本，而不是直接把 86.9% 当作通用 GUI judge 能力。

## 问题设定

- **输入、输出与目标**：输入任务指令 `T`、初始/最终截图 `Iinit, Ifinal` 和可交互环境状态 `Senv`；输出每个 completion condition 的二值 verdict、均值 reward `r∈[0,1]` 和总 Success/Failure。
- **现有瓶颈**：证据分散在截图、文件、配置、应用状态、命令输出和 accessibility tree 中，任务间没有固定检查顺序；截图与真实持久状态可能不一致。
- **关键假设**：VLM 能从 instruction 与截图提出足够完整、粒度正确的条件；工具返回的状态是真实且安全的；条件逐条独立取证后平均聚合能代表任务完成度。

## 核心贡献

1. 提出 propose-then-verify 的 interactive reward agent，将 completion-condition generation 与环境证据获取分离。
2. 构建 GUI-RewardBench：10 类 Ubuntu desktop app、321 条稳定 replay 轨迹，覆盖 visible、hidden-state、artifact verification。
3. 把 IRA 作为 reward 用于 OSWorld RL，并测试没有 task-specific script 的自动生成任务。

## 方法

### 直觉

先问“任务具体要求哪些可观察条件”，再问“哪一种工具能证明每个条件”，比让 VLM 对一张最终截图做整体直觉判断更可审计，也能把失败定位到条件遗漏、工具选择或证据不足。

### 形式化描述

- 条件 proposer 生成 `C={Ci}`：`C=Pθ(T,Iinit,Ifinal)`（Eq. 3）。
- 对每个 `Ci`，维护 history `Hi^t`；Agent 选择工具动作 `ai,t=IRA(Ci,Hi^{t-1})`，工具返回 `oi,t=Tool(ai,t,Senv)`，再把 action/observation 追加到 history（Eqs. 4–6）。
- 仅当 history 提供明确环境证据时，条件 verdict `yi=1`（Eq. 7）；总 reward 为 `rIRA=(1/N)Σyi`（Eq. 8），`r>0.8` 判为 Success。
- 工具分三类：system tools（文件、配置、命令、结构化状态）、application tools（文档/表格/演示 artifact）、GUI tools（导航和交互式状态）。

### Benchmark 与 RL

- 从 OSWorld 衍生任务和手工任务生成候选，使用 UI-TARS-1.5/EvoCUA-8B 生成轨迹；327 个候选各 replay 3 次，删掉 6 个不稳定样本，保留 321 个。
- 每次 live evaluation 之后仍执行 task-specific script 作为 ground truth，与被评估环境的实际状态对齐。
- RL 三臂：A=OSWorld+script，B=同任务+IRA，C=自动生成 OOD tasks+IRA；采用 DART 训练流程。

### 计算与数据成本

- IRA 平均步骤：GPT-5.5 3.34、GPT-5.4 3.27、Qwen3.6 8.20。
- token 中位数/均值：GPT-5.5 14.9K/59.5K，GPT-5.4 23.8K/120.0K，Qwen3.6 25.9K/约139.1K；Qwen 平均 7.31 次工具调用，GPT 约 2.34–2.53 次。
- 实验配置最大 30 verification steps、temperature 0、最多 3 次 API retry；未报告总 API 费用、VM wall-clock 或 RL 训练预算。

## 实验与证据

| 作者主张 | 对应证据 | 定位 | 我的判断 |
| --- | --- | --- | --- |
| 主动取证优于截图直觉 | GPT-5.5 VLM-only 78.5%→IRA 86.9%（+8.4pp），GPT-5.4 +9.1pp，Qwen +6.2pp；三种 IRA 均超过四个 passive baseline | Table 1–2、Section 5，pp. 6–7 | 同 backbone 的 matched comparison 很有说服力，且准确率/成本一起报告 |
| 环境证据在 hidden/artifact 任务尤其有用 | Calc 文件更新但截图未刷新、VLC 配置持久性等案例由 IRA 正确验证 | Figure 5、Section 5.3、Appendix A.6，pp. 6, 13 | 机制例子清楚，但定量 category breakdown 仍依赖 321 条小 benchmark |
| propose-then-verify 比开放式 GUI exploration 稳定 | GPT-5.4/5.5 GUI-only 与 IRA 的 precision-recall 曲线，Qwen GUI-only recall 下降而 IRA 恢复 | Figure 6、Section 5.4，p. 7 | 支持“结构化条件”而非“有工具就好”是关键 |
| IRA 可替代 task-specific reward script | OSWorld RL：script 34.9%、IRA 34.0%；自动生成 OOD tasks+IRA 33.5% | Table 3、Section 5.6，p. 7 | 差距只有 0.9pp/1.4pp，但没有 seeds、方差或训练曲线，不能过度解读 |
| 与人类判断高度一致 | 100 个自动生成任务，agreement 94%、κ=0.84 | Table 8、Section A.8，p. 14 | 成功类仅 29 条且 IRA 无 false positive、6 false negative，类别失衡让 κ/accuracy 需谨慎解释 |

### 数据、基线与指标

- **数据集**：GUI-RewardBench 321 条；artifact 192、hidden 89、visible 40；轨迹长度从 <5 到 >80 steps。
- **基线**：WebRL、ZeroGUI、DigiRL、DistRL 等 passive VLM reward evaluators；matched VLM-only 与 GUI-only。
- **指标**：accuracy、precision、recall、F1、TP/FP/TN/FN；reward >0.8 二值化。
- **Backbone**：Qwen3.6-35B-A3B、GPT-5.4、GPT-5.5。
- **ground truth**：每次 live evaluation 后运行 task-specific script；不是 321 条全部由独立人工重新判定。
- **稳定性**：轨迹 replay 三次筛稳定，但主表没有 bootstrap CI；RL 结果没有 seed/方差。

## 批判性阅读

### 证据支持的结论

- GUI reward 的核心瓶颈确实是 evidence acquisition，而不仅是视觉分类；文件/配置/跨应用状态能解释 passive evaluator 的系统性 false negative。
- 条件级 verification 让工具调用变得可审计，并在相同 backbone 下改善 precision-recall trade-off。
- 在论文给定的 OSWorld/DART 配置中，IRA reward 与脚本 reward 的 RL 结果接近，说明自动生成任务可以获得一定可用监督。

### 尚未被充分支持的结论

- `r>0.8` 阈值、条件等权平均和“所有条件必须显式证明”的语义没有做阈值/权重消融；不同任务可能需要硬性条件与软性条件的不同聚合。
- 34.0% vs 34.9% 的 RL 相近性缺少多 seed、训练曲线、样本效率和 reward calibration，无法确认两种 reward 真正等价。
- script ground truth 仍可能含有任务特定偏差；IRA 与脚本的高一致不等于与用户意图或真实业务成功一致。

### 局限、风险与可能反证

- tool invocation 可能改变被评环境：打开应用、执行命令、修改 focus 或缓存；论文承认不同 evaluator 的 TP/TN 总数会略变，但没有给出污染审计或 snapshot/rollback 机制。
- 平均 token 远高于 passive evaluator，Qwen mean 约 139K，实际成本和延迟可能使其无法作为在线 reward loop。
- 条件 proposer 的错误粒度、过度字面解释和漏检 persistence 是主要失败源（Figure 8）；这说明 verifier 仍依赖同一个 VLM 对规范进行语义编译。
- 321 条来自 Ubuntu desktop，自动生成 855 条任务共享初始 configuration；跨平台、真实文件权限、网络、长时任务尚未覆盖。
- 命令工具能读取敏感文件或改变系统；部署时需要权限沙箱、只读默认和 provenance 记录。

## 与已有知识的连接

- **基础论文**：DigiRL、DistRL、WebRL、OSWorld、DART、script-based GUI evaluators。
- **相近方法**：[[notes/papers/2026/07/29/Desktop-Delta Bench- Do Computer-Use Models Understand Desktop GUI Transitions]] 负责中间 transition diagnosis；IRA 负责终局环境验证。
- **后续工作**：结构化 reward condition、verifier calibration、state snapshot/rollback、低成本分层评估。
- **与主题笔记的关系**：[[notes/topics/结构化中间层与可验证执行]]。

## 复现计划

- **是否复现**：待定，优先做 evaluator 小规模复现，不立即做 RL。
- **最小验证目标**：在 30–50 条任务上比较 VLM-only、GUI-only、IRA，固定同一 GPT/Qwen backbone，报告条件召回、最终 reward、步骤数和 token。
- **所需资源**：公开 benchmark/config、Ubuntu VM snapshot、system/application/GUI tool wrappers；需要严格只读权限和回滚。
- **成功标准**：matched backbone accuracy 提升方向一致；对 artifact/hidden-state 单独报告收益；阈值和条件权重 sweep 后给 calibration curve。

## 待追踪问题

- [ ] 只读 snapshot 环境与真实 live 环境的 IRA 结果差异多大？
- [ ] 条件级 precision/recall 能否取代固定 0.8 threshold，并减少过度严格 false negative？
- [ ] 何时用便宜的 DDB/静态检查，何时升级到高 token IRA？
- [ ] 训练时 reward verifier 的错误如何传播到 GUI Agent policy，是否会诱导“满足 verifier 而非满足用户”？

## 原文定位

- 问题与贡献：Abstract、Sections 1–3，pp. 1–3。
- IRA 形式化与工具设计：Figure 2、Eqs. (1)–(8)、Section 4，pp. 3–4。
- GUI-RewardBench 构建与协议：Sections 4.2–4.3，pp. 4–5。
- 主结果、消融与成本：Tables 1–2、Figures 5–6、Sections 5.1–5.5，pp. 6–7。
- RL reward 对照：Table 3、Section 5.6，p. 7。
- 自动任务、人类一致性与工具统计：Tables 5–9、Appendix A.7–A.9，pp. 13–14。
- 失败案例：Figure 8、Appendix A.11，pp. 25–29。
