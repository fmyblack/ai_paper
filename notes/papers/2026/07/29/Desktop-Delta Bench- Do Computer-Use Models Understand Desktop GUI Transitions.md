---
type: paper
title: "Desktop-Delta Bench: Do Computer-Use Models Understand Desktop GUI Transitions?"
aliases: []
authors: ["Abhishek Pillai", "Samir Kumar Nayak", "Yuan Chen"]
year: 2026
venue: "arXiv"
paper_date: "2026-07-28"
date_added: "2026-07-29"
last_read: "2026-07-29"
topics: ["Agent", "Benchmark 与评估方法", "多模态模型"]
status: read
priority: 1
rating:
arxiv_id: "2607.26041"
doi: ""
paper_url: "https://arxiv.org/abs/2607.26041"
code_url: "https://github.com/abhipi/DDB"
pdf_path: "library/raw/2026/07/29/desktop-delta-bench.pdf"
text_path: "library/text/2026/07/29/desktop-delta-bench.txt"
sha256: "b57aa90e964dcfd91bad96e03bd833b6a907d4ca2ffff16bf7393f2b3a04c635"
pages: 15
citation_key: ""
related: []
cssclasses:
  - paper-note
---

# Desktop-Delta Bench: Do Computer-Use Models Understand Desktop GUI Transitions?

## 一句话结论

Desktop-Delta Bench（DDB）把 Computer-Use Agent 的复合成败拆成“状态先后排序”和“单步动作重建”：8 个模型家族中，最佳三帧精确排序仅 64.1%，最佳单动作 macro-F1 为 0.800；任务描述主要帮助识别异源截图而非判断真实时间顺序，说明当前强 VLM 会认界面、会猜目标，却仍不稳定地理解动作造成的 GUI 状态变化。

## 三分钟筛选

- **问题**：端到端 GUI benchmark 只告诉我们任务是否完成，静态 grounding benchmark 只告诉我们模型能否定位控件；两者都无法定位 Agent 是否理解“执行动作后状态发生了什么”。
- **新意**：构造离线、逐步、可审计的 transition benchmark，分别测试三帧时序与 decoy 排除，以及 before/after 到动作族和 payload 的逆向重建。
- **核心证据**：2,013 个经人工复核的样本；最佳 non-decoy/decoy exact match 为 65.1%/65.7%，最佳 pairwise accuracy 78.8%；任务上下文令 decoy identification 平均 +6.9pp，却令 non-decoy exact match -2.2pp；单动作中 click F1 最高 0.961，而 key-command 精确 payload 最高仅 46.4%。
- **与我的关系**：为 GUI Agent 增加了介于 grounding 与终局成功之间的诊断层，可与 Interactive Reward Agent 的终局环境验证组成“过程理解 + 结果验证”评测栈。
- **决定**：精读；适合作为 CUA 状态验证和恢复机制的离线回归集。

## 问题设定

- **输入、输出与目标**：任务一输入 3 张打乱标签的桌面截图，可选提供任务指令，输出同轨迹截图的时间顺序及异源截图集合；任务二输入一个动作前后各 1 张截图，输出 5 类动作之一及结构化 payload。
- **现有瓶颈**：推理、远程输入、应用渲染和截图捕获异步，Agent 可能把延迟、弹窗、遮挡、错误窗口或旧画面当作真实进展，并将错误状态继续带入规划。
- **关键假设**：人工录制的输入事件是动作金标；从少量离散截图恢复高层状态进展，能代表 CUA 的 transition understanding；离线任务与在线 Agent 的验证/恢复能力相关。

## 核心贡献

1. 从 Ubuntu 24.04 的 50 个任务域、约 15 个应用和 356 个任务 artifact 中构建 463 个三帧排序样本与 1,550 个单动作样本。
2. 用 105 个 cross-trajectory decoy 测试 source tracking，并平衡 A/B/C 标签排列以测量 presentation-order shortcut。
3. 把动作理解拆成动作族识别、非空间 payload 精确恢复、click/drag 空间误差和 pairwise chronology，多维定位失败来源。

## 方法

### 直觉

一个可靠的 CUA 不能只会“看见按钮”，还要确认按钮是否产生预期状态、当前截图是否属于本任务，以及失败后应从哪个状态恢复。DDB 不运行 Agent，而是直接向 VLM 提问这些中间问题。

### 形式化描述

- **Temporal ordering**：对截图集合 `O={A,B,C}`，模型预测异源集合 `U`、同源集合 `R=O\U` 及 `R` 的全序。严格 exact match 同时要求异源判断与顺序全部正确；另报 gold precedence pair 的 pairwise accuracy。
- **Single-action reconstruction**：动作空间包含 `click`、`drag`、`scroll`、`text_entry`、`key_command`；空间动作以屏幕对角线归一化误差评估，非空间动作要求方向、文本或按键序列精确匹配。
- 排序的随机基线为已知 decoy 条件下 1/6；不知道是否有 decoy 时为 1/12。动作族主指标使用 macro-F1，避免 70.8% click 样本主导。

### 数据与评测流程

- 人类示范者在 Ubuntu 24.04 GNOME 完成多应用 workflow；客体侧 recorder 以 10fps 录屏并同步键鼠事件。
- 初始 3,209 个候选经第二位审阅者标注 approved/corrected/indeterminate，最终保留 2,013 个（62.7%）。
- 三帧不是连续视频帧，而是同一 workflow 中间隔数秒或数分钟的动作映射状态，要求推断高层任务进展。
- 评测 4 个闭源与 4 个开源模型家族，共 32 个排序设置和 16 个动作设置；闭源使用 medium/high reasoning，开源使用 2K/4K 输出预算。

### 计算与数据成本

- 论文报告了样本量、模型调用设置与访问日期，但没有 API 成本、总推理 token、运行时间或人工标注工时。
- 数据采集来自 50 次录制，排序样本与单动作样本共享这些 workflow，样本数大于独立任务数。

## 实验与证据

| 作者主张 | 对应证据 | 定位 | 我的判断 |
| --- | --- | --- | --- |
| GUI transition understanding 尚未饱和 | Gemini 3.6 Flash 最佳 non-decoy 65.1%、decoy 65.7%、pairwise 78.8%；Claude Opus 4.8 decoy ID 97.1% 时 decoy exact 仅 51.4% | Section 6.2、Figure 5、Table A1，pp. 7, 10 | 强支持“识别来源不等于重建顺序”，但 benchmark 仍局限单 OS 与 50 个 workflow |
| 任务上下文帮助 membership 而非 chronology | 16 个设置平均 decoy ID +6.9pp、decoy exact +5.9pp、non-decoy exact -2.2pp | Figure 5，p. 7 | 有清晰配对对照，是论文最有诊断性的结论之一 |
| 部分模型依赖展示顺序 shortcut | GLM-4.6V 与 MiniMax M3 的错误中，A→B→C 占 37.7%–45.6%，完整逆序仅 1.6%–5.5% | Figure 6，p. 7 | 标签已平衡，能排除金标偏置；说明输出 bias 强于视觉证据 |
| 动作族识别比 payload 与 drag 定位容易 | 最佳 macro-F1 0.800；click F1 0.961，drag F1 0.757；click/drag AUC 0.857/0.535；key exact 46.4% | Section 6.3、Table 2、Tables A2-a/b，pp. 8, 11 | 支持把“是什么动作”与“动作参数是什么”拆开评估 |
| 闭源模型总体优于开源模型 | minimal prompt 下闭源整体 exact 53.5%，开源 30.6% | Figure 5、Section 6.2.2，p. 7 | 观察成立，但模型规模、训练数据和推理控制不匹配，不能归因于开源/闭源属性本身 |

### 数据、基线与指标

- **数据集**：463 个排序样本（358 同轨迹、105 decoy）；1,550 个动作样本；覆盖 50 个任务域、约 15 个应用。
- **模型**：GPT-5.6-Sol、Claude Opus 4.8、Claude Sonnet 5、Gemini 3.6 Flash、Holo 3.1、MiniMax M3、Kimi K2.6、GLM-4.6V。
- **指标**：ordering exact、pairwise accuracy、decoy identification、presentation-order echo；动作 macro/per-class F1、空间 AUC、exact payload。
- **标注**：全部候选由第二位审阅者复核，但未报告双人独立标注的一致性系数。
- **稳定性**：A/B/C 用 seed 42 平衡；未报告不同 permutation seed、bootstrap CI 或人类任务基线。

## 批判性阅读

### 证据支持的结论

- 当前强 VLM 在 GUI 状态先后、异源状态排除和动作 payload 恢复上存在明显且可分离的缺口。
- 任务描述可能成为“这个截图是否像目标任务”的 membership 线索，却不保证模型依据可见变化排序。
- 动作识别的主要瓶颈不只在定位：drag 的动作族 recall 和 key/text 的精确 payload 都仍不足。

### 尚未被充分支持的结论

- DDB 分数是否预测 OSWorld/OSWorld2.0 的在线成功、验证或恢复能力，论文没有做模型级相关性或干预实验。
- 三张间隔较远的截图混合了应用常识、任务规划和视觉变化，不能把全部错误都解释为“因果 transition understanding”失败。
- 论文没有证明三帧排序和单动作逆推覆盖了 CUA 状态理解的全部关键维度，例如不可见文件状态、网络副作用和长期约束保持。

### 局限、风险与可能反证

- 2,013 个样本来自 50 次录制，样本并非 2,013 个独立任务；同一 workflow 的视觉风格、artifact 和应用状态可能形成相关性。
- click 占动作样本 70.8%，scroll 只有 33 个；macro-F1 减轻类别失衡，但小类结论方差仍会很大。
- temporal ordering 使用间隔数秒至数分钟的非连续状态，更像“任务进展排序”而非严格的一步 action-effect prediction。
- 只有 Ubuntu 24.04 GNOME；Windows、macOS、浏览器 DOM、移动端与动态网页状态都未覆盖。
- 没有按任务、录制或 artifact 做显式 held-out generalization 分析，也没有报告标注一致性、置信区间与人类上限。

## 与已有知识的连接

- **基础论文**：OSWorld、OSWorld 2.0、ScreenSpot-Pro、EvoGUI、Computer-Using World Model。
- **相近方法**：[[notes/papers/2026/07/29/Interactive Reward Agent- GUI Task Evaluation via Environment-State Verification]] 负责终局环境证据，DDB 负责过程级视觉变化理解。
- **后续工作**：将 DDB 指标与在线 Agent 的 stale-observation rejection、verification retry 和 recovery success 做相关性与训练干预。
- **与主题笔记的关系**：[[notes/topics/结构化中间层与可验证执行]]。

## 复现计划

- **是否复现**：是，优先级中高。
- **最小验证目标**：在发布数据上复现 Gemini/开源 VLM 的 ordering exact 与 presentation-order echo，并新增按 recording 分组的 held-out 评估。
- **所需资源**：DDB 数据与 evaluator；至少一个可本地运行的 VLM；无需在线 VM。
- **成功标准**：主指标误差在论文值 ±2pp 内；确认任务上下文对 decoy 与 chronology 的相反影响；报告 5 个 permutation seeds 的均值和 CI。

## 待追踪问题

- [ ] DDB 分数与 OSWorld2.0 的在线验证/恢复失败是否模型级相关？
- [ ] 只保留连续动作帧后，模型排序和逆向动作重建会提高多少？
- [ ] 按 recording/task/artifact 严格切分后，当前分数是否显著下降？
- [ ] 将 DDB 样本加入训练，改善的是视觉因果理解还是提示格式适配？

## 原文定位

- 任务定义与总体架构：Figure 1、Sections 1, 3，pp. 1–4。
- 数据采集、类别分布与人工复核：Figures 2–4、Section 4，pp. 5–6。
- 指标定义：Section 5，pp. 6–7。
- 主要结果：Figures 5–8、Table 2、Section 6，pp. 7–8。
- 完整模型矩阵与 prompts：Tables A1–A3、A2-a/b、Appendices A–B，pp. 10–15。
