---
type: paper
title: "ERPBench: A State-Grounded Evaluation Paradigm for Computer-Use Agents in Enterprise Software"
aliases: []
authors: ["Kratika Bhagtani", "Kusha Sridhar", "Maziyar Baran Pouyan", "Yuying Zhao", "Eugene Siow"]
year: 2026
venue: "arXiv"
paper_date: "2026-09-15"
date_added: "2026-09-18"
last_read: "2026-09-18"
topics: ["Agent", "Benchmark 与评估方法", "多模态模型", "安全、鲁棒性与治理"]
status: read
priority: 1
rating:
arxiv_id: "2609.17885"
arxiv_version: "v1"
version_updated_at: "2026-09-15"
doi: ""
paper_url: "https://arxiv.org/abs/2609.17885"
code_url: ""
pdf_path: "library/raw/2026/09/18/2609.17885.pdf"
text_path: "library/text/2026/09/18/2609.17885.txt"
sha256: "401603e5e65dca580f50739f509de64f4f0c6b4c1c95e786ebec7671c8820dbe"
pages: 8
citation_key: ""
related: ["[[notes/papers/2026/07/29/Interactive Reward Agent- GUI Task Evaluation via Environment-State Verification]]", "[[notes/papers/2026/07/29/Desktop-Delta Bench- Do Computer-Use Models Understand Desktop GUI Transitions]]", "[[notes/papers/2026/09/18/MIRAGE- How Conversation State Shapes Historical Evidence Use in Multimodal Personal Agents]]"]
cssclasses:
  - paper-note
---

# ERPBench: A State-Grounded Evaluation Paradigm for Computer-Use Agents in Enterprise Software

## 一句话结论

ERPBench 有力证明了企业 GUI Agent 的“看起来完成”与“业务状态正确”不是一回事：五个开源模型在 T1 中有 90%–95% 的导航率，却只有 0%–34% 的数据库正确率；但其结论目前只覆盖单一 ERPNext、30 个任务和有限重复，且 grader 只检查目标字段，不能据此断言模型已被完整审计或人审门禁已经足以安全部署。

## 三分钟筛选

- **问题**：截图、动作轨迹和“保存成功”提示无法证明值真正写入了持久数据库；企业流程还包含多字段、多文档依赖与不可逆提交。
- **新意**：在 live、self-hosted ERPNext 上让 Agent 仅看像素并输出坐标动作，同时用 Frappe API 检查数据库字段；再把运行拆成 Navigation、Interaction、Commit、Database 四阶段，并为失败给出操作性 taxonomy。
- **核心证据**：Claude Sonnet 4.6 在 T1/T2/T3 为 94%/100%/100%；最强开源模型 T1 仅 34%，T2 最多 0%，T3 最多 3%。UI-TARS-7B 在 T2 100% 到达、85% 保存，但仅 3% 数据库正确（Tables 2–3，p. 6）。
- **与我的关系**：与 Interactive Reward Agent、Desktop-Delta Bench、MIRAGE 共同回答“结果正确是否来自真实状态/证据”，ERPBench 提供最直接的持久业务状态层。
- **决定**：精读；值得复现 grader 与 silent-commit failure，不应直接把 leaderboard 当成通用 CUA 能力排名。

## 问题设定

- **输入、输出与目标**：Agent 每轮只接收 `1280×720` ERPNext 截图，输出鼠标/键盘动作；任务 YAML 给出 prompt、start URL、fixture、期望字段和 grader 配置。最终成功要求所有目标字段经数据库查询后满足类型化等价关系。
- **现有瓶颈**：DOM/A11y/API 会让 grounding 变容易却不适用于像素型旧系统；只看 GUI 又会漏掉字段未绑定、保存未持久化、旧值残留等 silent failure。
- **关键假设**：目标字段集合足以代表业务成功；Frappe API 返回的是可信 ground truth；按 UUID 隔离记录足以消除跨 run 干扰；任务特定 start URL 没有移除需要评测的关键导航难度。

## 核心贡献

1. 构建 30-task/150-run-per-model 的 ERPNext benchmark：20 个 T1 单记录任务、由运行数可反推的 4 个 T2 多字段任务与 6 个 T3 链式任务。
2. 把 binary database success、field/chain partial credit、四阶段定位和五类失败 taxonomy 放到同一 harness 中。
3. 比较 6 个 CUA 与 3 位作者人类参考，量化一般 GUI benchmark 分数不能直接迁移为 enterprise reliability。

## 方法

### 直觉

企业系统里的真正输出不是屏幕，而是持久数据库。因而应沿 `看见目标 → 操作字段 → 发起保存/提交 → 数据库存对` 逐段取证；一旦只停在动作或截图，错误就可能在下游财务、采购或库存流程中传播。

### 形式化描述

- 对目标字段集合 `F`，期望值与观测值为 `y_i*`、`ŷ_i`。类型化谓词 `g(ŷ_i,y_i*)∈{0,1}` 处理数值容差（默认 `τ=0.01`）、Boolean 等价、HTML stripping 与字符串空白归一化。
- 全任务成功为 `∏_{i∈F} g(ŷ_i,y_i*)=1`；T2 partial credit 对目标字段等权，T3 以正确文档数/链长度定义 chain-depth（Section 3.3，p. 4）。
- stage grader 独立记录 Navigation、Interaction（仅 T1）、Commit、Database；taxonomy 按 `Recovery → Planning → Perception → Save-step → Grounding` 优先级将每个失败 run 强制归入单一类别（Section 4.3，pp. 5–6）。

### 关键模块与训练流程

- ERPNext、MariaDB、Redis 与 noVNC 在 Docker 内运行；Chromium/Xvfb 提供像素界面。Agent 不接触 DOM/A11y/API，grader 与 fixture seeding 才使用 Frappe REST API（Figure 1、Section 3，pp. 3–4）。
- 每次 run 给记录名加 UUID 后缀而不是重置整库。生产模式由 risk classifier 与人工审批 `safe/commit/irreversible` 动作；评测模式以 200 ms auto-approver 替代人审，所有动作自动通过。
- Agent action 包括 move、scroll、click、type、select、set date、clear、key 与 navigate；每步还附理由和风险类别。
- 论文没有训练新模型；实验是在统一 harness 中评测 Claude Sonnet 4.6、Qwen3-VL-32B+OmniParser、OpenCUA-32B/7B、UI-TARS-7B、Holo3-35B-A3B。

### 计算与数据成本

- 每模型 150 runs：T1 `20×5=100`、T2 `4×5=20`、T3 `6×5=30`；3 位作者完成同一任务集作为 human reference（Section 4.1，p. 5）。
- Claude 每 run 平均输入 token 从 T1 231K 增至 T3 2.009M，动作 11.7→36.2，时长 89.2→322.7 秒；输出 token 2,255→6,468（Tables 2、4，p. 6）。
- 开源模型的低动作数/时长多数来自提前终止或 loop-break，不能解释为效率优势；论文没有报告 GPU 型号、总 GPU-hours、API 美元成本或部署端到端 TCO。

## 实验与证据

| 作者主张 | 对应证据 | 定位 | 我的判断 |
| --- | --- | --- | --- |
| 一般 GUI 能力不等于企业可靠性 | UI-TARS/OpenCUA-32B 的 OSWorld-Verified 为 42.5/34.8，但 ERPBench T1 仅 9%/23%；五个开源模型 T2 全为 0%，T3 最高 3% | Section 4.2、Table 2，pp. 5–6 | 在本 benchmark 内证据强；跨 benchmark 的模型配置、prompt 与预算未完全对齐，不能做纯模型能力归因 |
| 导航和 commit 会高估真实成功 | UI-TARS T1：95% navigate、68% commit、9% DB；T2：100% navigate、85% commit、3% DB | Table 3，p. 6 | 是论文最有说服力的 matched evidence，直接暴露 silent commit gap |
| 复杂度加深导致开源模型崩溃 | Holo/Qwen T1 为 34%/32%，T2 均 0%，T3 均 3%；所有开源模型 T3 无完整链 | Tables 2–3，p. 6 | 方向可信，但 T2 仅 20、T3 仅 30 runs/model，3% 实际约等于一次成功，缺 CI |
| 失败主要发生在 post-navigation | T1 失败图中 Qwen 59% Grounding、15% Planning、15% Perception、12% Save-step；UI-TARS 59% Perception、27% Grounding | Figure 3、Section 4.3，pp. 6–7 | 支持操作性定位；类别由优先级强制互斥，`Perception` 可能混入输入绑定/状态刷新等非感知原因 |
| 任务并非仅依赖 ERP 熟练度 | 两位熟手 T1/T2/T3 为 99–100%/95%/97–100%，首次用户仍为 96%/90%/87% | Table 2、Section 4.2，pp. 5–6 | 能排除“完全是 ERP 知识”这一简单解释；只有 3 位作者，且人类直接操作浏览器，非严格 matched baseline |
| blank start 加剧链式失败 | OpenCUA-32B chain-depth 由 warm-start 22% 降至 blank-start 9%；其余开源模型也下降 | Table 5，p. 7 | 说明 URL-level navigation 是额外瓶颈；只在三项 OSWorld-analog 任务上，证据范围窄 |

### 数据、基线与指标

- **数据集**：单一 ERPNext 实例、30 distinct tasks；T1 text-edit/select-toggle/create，T2 6–9 字段记录，T3 2–4 个依赖文档的链式 workflow，其中 3 个 blank-start。
- **基线**：6 个 CUA；3 位作者人类参考。论文横向引用 OSWorld、WindowsAgentArena、WorkArena、SCUBA、CRMArena-Pro、UI-CUBE 与 EntWorld，但未在同一环境重跑这些 benchmark。
- **指标**：all-field database success、T2 field partial credit、T3 chain-depth、stage reach rate、failure taxonomy、actions、turns、duration、input/output tokens、median thinking time。
- **预算/硬件**：开源模型 self-hosted、Claude API；未披露 GPU/量化/采样温度/随机种子/API 费用，模型间 wall-clock 不宜直接比较。
- **消融与稳定性**：每 task 5 runs，但无均值方差、bootstrap CI 或显著性检验；无 start URL、resolution、turn budget、grader rule、human gate 的系统消融。

## 批判性阅读

### 证据支持的结论

- 数据库状态确实能发现截图/轨迹 grader 看不到的错误；UI-TARS 的 commit-to-database gap 是直接证据。
- 在给定 ERPNext 任务上，除 Claude 外的五个模型主要不是“找不到页面”，而是不能可靠操作字段并持久化正确值。
- 随任务从单字段扩展到多字段与文档链，动作、token 和时长显著增加，而开源模型成功率接近零。

### 尚未被充分支持的结论

- “ERPBench 是完整 enterprise readiness test”没有成立：只覆盖 ERPNext、30 个任务、一个分辨率和一套 fixture；没有权限、并发、审计、审批疲劳、异常网络或回滚测试。
- “human-in-the-loop harness 使 Agent 可部署”没有被实验验证。benchmark 完全 auto-approve，未测人工判断质量、延迟、拒绝/升级策略或人机联合成功率。
- “failure taxonomy 揭示 causal failure”证据不足。分类由行为迹象和优先级定义，未报告人工标注一致性，也没有干预实验确认失败原因。
- proprietary/open-weight gap 不能只归因于模型：harness 适配、prompt、grounding parser、token budget、推理配置和硬件并未做严格等预算对照。

### 局限、风险与可能反证

- **未审计 collateral damage**：grader 只查询目标字段；Agent 可能正确写入目标值同时误改其他字段、记录或权限，仍被判成功。企业安全需要 invariant 与 side-effect grader。
- **小样本与离散结果**：T2 只有 4 tasks×5，T3 只有 6×5；3% 成功约等于 1/30，排行榜差异可能很不稳定。
- **taxonomy 命名过强**：保存了错误值被叫作 `Perception`，但也可能是 typing、focus、field binding、autocomplete 或 race condition；`Grounding` 又是 residual category。
- **人类对照不完全 matched**：人类直接操作浏览器，Agent 经过 screenshot-action loop；3 人均为作者，专家/新手各样本极少，完成时间和动作数不可公平比较。
- **任务前置简化**：多数任务从 task-specific URL 开始，降低了真实工作中的登录、模块发现、跨应用导航与权限处理难度。
- **发布状态**：论文只写“intend to release”，当前正文没有 benchmark/harness 的公开代码 URL；“open/reproducible”主要指 ERPNext 可自托管，而非完整 artifact 已可复现。
- **外部有效性**：没有 SAP、Oracle、Dynamics、Salesforce 或真实组织 schema；ERPNext 上的 pixel/field failure 比例不应直接外推到其他企业系统。

## 与已有知识的连接

- **基础论文**：WebArena 的 execution-based verification、OSWorld/WindowsAgentArena 的真实桌面环境、WorkArena/SCUBA/CRMArena-Pro/UI-CUBE/EntWorld 的企业评测。
- **相近方法**：[[notes/papers/2026/07/29/Interactive Reward Agent- GUI Task Evaluation via Environment-State Verification]] 用工具主动取证终局状态；[[notes/papers/2026/07/29/Desktop-Delta Bench- Do Computer-Use Models Understand Desktop GUI Transitions]] 检查中间 GUI transition；ERPBench 则把终局落到数据库字段。
- **后续工作**：加入 invariant/side-effect/权限/审计 grader，覆盖真实人审门禁与 rollback；用 matched compute、公开 prompt 和多 seed 重测模型。
- **与主题笔记的关系**：[[notes/topics/结构化中间层与可验证执行]]；与 MIRAGE 一起说明 outcome-only correctness 会掩盖证据链或状态链断裂。

## 复现计划

- **是否复现**：待定；先复现 grader 与 5–10 个任务，不急于跑全部模型。
- **最小验证目标**：构造 3 类反例：GUI 显示成功但 DB 未改、目标字段正确但其他字段被误改、审批通过但 irreversible action 不应执行；比较 screenshot、trajectory、target-field、full-invariant 四类 grader。
- **所需资源**：固定版本 ERPNext Docker、任务 YAML、Frappe read-only grader、浏览器/noVNC、一个开源 CUA；需记录 DB snapshot 与完整 action provenance。
- **成功标准**：复现明显的 commit-to-database gap；target-field grader 对 collateral damage 的漏检可被 invariant grader捕获；所有 runs 可由 snapshot 恢复。

## 待追踪问题

- [ ] benchmark/harness 实际发布后核对 license、任务 YAML、prompt、turn budget 与模型配置。
- [ ] Stage grader 与 failure taxonomy 是否有独立人工标注和一致性数据？
- [ ] Claude 的 2.009M input tokens/run 如何累计，是否包含整段图像/历史重复计费？
- [ ] 加入负向 invariant 后，Claude 的 94–100% 是否仍保持？
- [ ] 在真实人工审批下，成功率、延迟、误批率和 reviewer fatigue 如何变化？

## 原文定位

- 任务动机、state-grounded 定义与贡献：Abstract、Section 1，pp. 1–2。
- 与既有 benchmark 的属性比较：Table 1、Section 2，pp. 2–3。
- 系统、任务 tiers 与 human gate：Figure 1、Sections 3–3.2，pp. 3–4。
- 数据库谓词、partial/stage grading 与 human baseline：Sections 3.3–3.4，p. 4。
- 实验协议与主要解释：Sections 4.1–4.3，pp. 5–6。
- 成功率、阶段断层、成本：Tables 2–4，p. 6。
- 子任务 partial credit、失败 taxonomy 与结论：Table 5、Figure 3、Section 5，p. 7。
