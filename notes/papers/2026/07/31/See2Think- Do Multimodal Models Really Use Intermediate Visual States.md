---
type: paper
title: "See2Think: Do Multimodal Models Really Use Intermediate Visual States?"
aliases: []
authors: ["Siyu Yan", "Zhuoran Yan", "Haiying Xu", "Panhao Zhou", "Jingyu Chen", "Chenhao Ji", "Shuo Cao", "Yongheng Zhang", "Haoze Liu", "Siyu Zhang", "Xiwen Gu", "Yihao Liu", "Alex Jinpeng Wang"]
year: 2026
venue: "arXiv"
paper_date: "2026-07-29"
date_added: "2026-07-31"
last_read: "2026-07-31"
topics: ["多模态模型", "Agent", "Benchmark 与评估方法", "推理与规划", "可解释性"]
status: read
priority: 1
rating: 4
arxiv_id: "2607.26769"
doi: ""
paper_url: "https://arxiv.org/abs/2607.26769"
code_url: "https://github.com/CSU-JPG/See2Think"
pdf_path: "library/raw/2026/07/31/see2think-merged.pdf"
text_path: "library/text/2026/07/31/see2think-merged.txt"
sha256: "157f481a4d2dc38f3accdec73cec9bce9e437706e1055625c4547d40d5363f7b"
pages: 33
citation_key: "yan2026see2think"
related:
  - "[[notes/papers/2026/07/27/3D-Aware VLMs with Implicit and Explicit Geometries]]"
  - "[[notes/papers/2026/07/27/MIRROR- Learning from the Other View for Multi-Modal Reasoning]]"
cssclasses:
  - paper-note
---

# See2Think: Do Multimodal Models Really Use Intermediate Visual States?

## 一句话结论

See2Think 把“模型调用了视觉工具”拆成三个可观测问题：动作是否相关（Action Relevance）、渲染是否忠实（Render Faithfulness）、后续推理是否真的吸收反馈（Feedback Uptake）。在 1,200 个样本、12 类任务和四个多模态模型上，没有统一最优推理设置；动作相关性接近饱和，但忠实渲染是更明确的瓶颈。错误反馈在 3D 场景、且模型高 uptake 时可带来 10.3–15.5pp 的准确率下降，说明“依赖视觉状态”与“从正确状态获益”不是一回事。

## 三分钟筛选

- **问题**：视觉 scratchpad/工具轨迹的存在和最终答案正确，并不能证明中间视觉状态被正确生成、使用或因果依赖。
- **新意**：See2ThinkBench + VAoT（Visual Action-of-Thought）统一记录 textual thought、visual action、rendered state、subsequent reasoning，并加入 matched WrongRender 干预。
- **核心证据**：表 2 的四设置准确率、表 3 的三阶段过程分数、图 6–8 的正确性分层和错误反馈敏感性、表 4 的人工验证（第 7–11 页）。
- **与我的关系**：它是 [[notes/topics/Agent能力形成与过程验证]] 的“过程验证”分支，可作为 [[notes/papers/2026/07/30/SkillRise- Agentic Reinforcement Learning for Cross-Task Skill Evolution]] 中间技能文档是否被真正使用的评估范式类比。
- **决定**：已精读；值得复现 process judge 与 WrongRender 质量审计，优先做 3D 场景的 paired intervention。

## 问题设定

- **输入、输出与目标**：输入为图像 `I`、问题 `q` 和统一的开放式答案接口。VAoT 交替产生文本思考 `Tt`、结构化视觉动作 `At`、外部 renderer 返回的视觉状态 `Rt`，直到最终答案；目标不是训练新模型，而是诊断中间状态的生成与使用（第 1–3 节，第 1–6 页）。
- **现有瓶颈**：既有 benchmark 可能存在 text-only shortcut，或只看 final accuracy、oracle visual clue、aggregate trace quality，无法同时识别 action、render、use 三个阶段。
- **关键假设**：renderer 能执行结构化视觉操作且不替模型解题；WrongRender 能在保留大体操作意图和自然外观的同时修改 task-relevant evidence；外部 judge 可以从完整轨迹中选出关键视觉步骤。

## 核心贡献

1. 定义 genuine visual-state use 为一个可干预的诊断问题，区分 visual-state utility 与 behavioral dependence。
2. 构造 1.2K 样本、12 类任务、三种视觉环境的 See2ThinkBench，并用 caption-only solvability filtering 降低文本捷径。
3. 提出 inference-time VAoT 与四种设置：CoT、VAoT-NoRender、VAoT、VAoT-WrongRender；以过程分数和 paired intervention 超越只报最终答案的评估。

## 方法

### 直觉

一个相关的视觉动作可能仍被错误渲染；一个模型也可能读取了渲染结果，却把错误信息当成证据。因此需要三阶段诊断，再用“正确渲染 vs 错误渲染”的同样本比较测试行为是否依赖返回状态。

### 形式化描述

文本模型在历史 `Ht={(Ti,Ai,Ri)}1..t` 条件下生成下一步 `Tt+1`。过程 judge 对每条 VAoT 轨迹选一个 key visual step，并以 `{0,0.5,1}` 评分：

- **Action Relevance**：动作是否直接瞄准解决问题所需的视觉证据。
- **Render Faithfulness**：返回视觉状态是否忠实执行动作。
- **Feedback Uptake**：后续推理是否使用返回状态中的信息。

paired analysis 分别比较 `VAoT-NoRender→VAoT`（render benefit/harm）与 `VAoT→VAoT-WrongRender`（`AccVAoT−AccWrongRender`）；后者的正值表示错误反馈导致性能损失（第 4.4 节，第 10 页；附录 C.3）。

### 关键模块与评估流程

1. **数据过滤**：从现有视觉 reasoning 数据集出发，先做 caption-only solvability test，再统一答案格式并做人审质量控制；每类 100 个样本（第 2.1–2.2 节，第 3–5 页）。
2. **四种 inference setting**：CoT 只在原图上文本推理；VAoT-NoRender 生成动作但不执行；VAoT 执行动作并返回渲染状态；VAoT-WrongRender 返回自然但 task-relevant 的错误状态（第 4.1 节，第 7 页）。
3. **过程与结果联合评估**：四个模型都跑完整 1,200 样本；过程分析使用 4,800 条 VAoT trajectories；GPT-5.4 作为 external answer/process judge，模型身份和显式正确性标签对过程 judge 隐藏（附录 B，第 21–22 页）。

### 计算与数据成本

- 1,200 样本覆盖 2D structured reasoning（Geometry、Spatial Puzzle、Physics、Chemistry、Science QA、Abstract Pattern）、3D scene reasoning（Object Attributes、Compositional 3D）和 real-world visual reasoning（Robot Manipulation、Robot State Change、Visual Commonsense、Intuitive Physics）。
- 模型：GPT-5.5、GPT-o3、Gemini 3.5 Flash、Qwen3-VL-32B-Instruct；每模型每设置使用同一 benchmark 和 interaction budget（附录 B.1，第 22 页）。
- 主要成本是四模型 × 四设置 × 1,200 样本的闭环推理、外部 renderer 和 judge；论文未把 renderer 生成失败/调用成本换算成端到端预算。

## 实验与证据

| 作者主张 | 对应证据 | 定位 | 我的判断 |
| --- | --- | --- | --- |
| 没有统一最优视觉推理设置 | GPT-5.5/Qwen3-VL-32B-Instruct 最好是 CoT，GPT-o3 最好是 VAoT，Gemini 3.5 Flash 最好是 VAoT-NoRender；Robot Manipulation 是一致低准确率 outlier | 表 2、图 5、Takeaway 1–2，第 7–8 页 | 强支持“模型/环境依赖”；四个模型仍不足以覆盖整个 VLM 族。 |
| 动作选择通常不是瓶颈 | 表 3 overall Action Relevance：GPT-5.5 0.985、GPT-o3 0.978、Gemini 0.976、Qwen3 0.958 | 表 3，第 9 页 | 支持接近饱和；自动 judge 的上限和选择单一 key step 可能隐藏多步动作问题。 |
| 渲染忠实度是更明确瓶颈 | 表 3 overall Render Faithfulness 仅 0.594–0.630，明显低于 Action Relevance；3D correct–incorrect gap 的 Render 差为 0.097 | 表 3、图 6，第 9 页 | 强支持“动作之后的执行/使用”更关键，且不同环境的失败阶段不同。 |
| 正确渲染不一定带来净收益 | 完全不忠实渲染在 2D/3D 的 benefit-harm balance 为 −6.1/−9.3pp；更高忠实度主要减少 harm，而非保证大幅增益 | 图 7、Takeaway 5，第 10 页 | 支持 utility 与 dependence 的区分，但 benefit/harm 受 renderer 质量分桶影响。 |
| 模型会行为上依赖返回视觉状态 | 3D 场景按 Feedback Uptake=0/0.5/1 分组，准确率下降 3.5/10.3/15.5pp；四模型语义答案改变率 32.7–54.2% | 图 8、表 8、Takeaway 6，第 10–11 页 | 强支持 3D 中的依赖关系；2D/real-world 关联较弱或非单调，不能普遍化。 |
| 过程 judge 具备可接受的人类一致性 | 两位 annotator 对四个目标的 reasonable-or-partial 均为 92.9–96.9% | 表 4，第 11 页 | 支持诊断工具可用，但更像“部分合理”审计，不是严格准确率证明。 |

### 数据、基线与指标

- **数据集**：See2ThinkBench 12 类、每类 100 个样本；127 个样本保留结构化候选集，其余 1,073 个用 free-form answers（附录 A.3，第 22 页）。
- **基线/设置**：CoT、VAoT-NoRender、VAoT、VAoT-WrongRender；与 MIRA、ViC-Bench、TWI-PRMBench、TwiFF-Bench 的覆盖维度做比较（表 1，第 4 页）。
- **指标**：normalized exact match / semantic-equivalence accuracy；Action Relevance、Render Faithfulness、Feedback Uptake；render benefit/harm；WrongRender sensitivity。
- **预算/硬件**：四模型完整 1.2K benchmark；每模型 1,200 VAoT trajectories，合计 4,800；GPT-5.4 judge。未报告传统多 seed 置信区间。
- **消融与稳定性**：matched settings、错误反馈干预、人工 audit；没有训练目标消融，因为论文是 inference-time diagnostic framework。

## 批判性阅读

### 证据支持的结论

- “有视觉 action trace”不是“视觉状态有用”的充分证据；需要同时看动作、渲染和后续反馈使用。
- 3D 场景对渲染忠实度和错误反馈最敏感，说明视觉闭环的执行误差会直接转成关系推理错误。
- Feedback Uptake 高只说明模型使用了返回内容，不保证该内容正确，也不保证最终准确率提升。

### 尚未被充分支持的结论

- benchmark 的 caption-only filtering 能减少 shortcut，但不能证明每个样本都“必须”看原图；过滤模型自身可能引入偏差。
- WrongRender 的因果解释依赖干预质量；作者附录 F.2 的 120-case audit 中 strict pass 仅 56.7%、acceptable 78.3%，因此 aggregate drop 应视为诊断信号而非精确效应量。
- 过程 judge 只选择一个 key visual step，可能遗漏多步协作、错误在早期传播后被后续步骤修正等情况。

### 局限、风险与可能反证

- 只覆盖四个代表性模型；模型 API 版本、renderer 和 judge 更新可能改变结果（第 6 节，第 12 页）。
- VAoT 依赖外部 renderer；其生成偏差既可能被误判为模型 render failure，也可能改变错误反馈强度。
- 3D 结果的高敏感性不等于实际部署收益，因为任务准确率总体仍可能低，Robot Manipulation 尤其是低准确率 outlier。
- 若模型能从原图旁路读取与 renderer 状态无关的证据，Feedback Uptake 与 behavioral dependence 的解释需要更严格的信息流控制。

## 与已有知识的连接

- **基础论文**：Multimodal CoT、tool-based visual reasoning、MIRA、ViC-Bench、TWI-PRMBench、TwiFF-Bench。
- **相近方法**：[[notes/papers/2026/07/27/3D-Aware VLMs with Implicit and Explicit Geometries]] 关注几何表示与视觉 grounding；See2Think 关注这些中间视觉状态是否真正被执行和使用。
- **后续工作**：跟踪能够学习 renderer、做 information bottleneck/视图 dropout、或把过程监督直接纳入训练的工作。
- **与主题笔记的关系**：[[notes/topics/Agent能力形成与过程验证]] 的“中间状态过程验证”分支；与 SkillRise 的共同问题是“中间产物被生成”与“中间产物改变后续行为”之间存在鸿沟。

## 复现计划

- **是否复现**：是（小规模）；官方 repo 和网站公开。
- **最小验证目标**：选 3D Scene 中 2–3 类、固定一个开源模型，复现 VAoT/VAoT-WrongRender 的 paired accuracy drop，人工抽查 Render Faithfulness 与 Feedback Uptake。
- **所需资源**：See2Think 官方 repo、renderer、Qwen3-VL 或可用 VLM API；记录原图、结构化 action、faithful/wrong render、后续 reasoning 和 judge 输入。
- **成功标准**：在相同样本配对下，高 uptake 组的 WrongRender drop 高于低 uptake 组；同时单独报告 WrongRender quality audit，不把失败干预混入主效应。

## 待追踪问题

- [ ] 让 renderer 输出结构化状态或可验证图形，而不是依赖图像生成，是否能显著提升 Render Faithfulness？
- [ ] 用多 key-step、step-level causal masking 替代单 key-step judge，过程结论是否稳定？
- [ ] 视觉反馈依赖性与模型的原图访问、上下文长度、动作轮数之间是什么关系？
- [ ] 把 Action/Render/Feedback 三项作为训练 reward，是否会产生可被模型投机的过程行为？

## 原文定位

- **框架与数据**：摘要、图 1–2、表 1，第 1–4 页。
- **VAoT 与设置**：第 3 节、式（1）–（2）、第 4.1 节，第 6–7 页。
- **主结果**：表 2、图 5，Takeaway 1–3，第 7–8 页。
- **过程诊断**：表 3、图 6，Takeaway 4，第 9 页。
- **干预与反馈依赖**：图 7–8、表 4、Takeaway 5–6，第 10–11 页。
- **限制与质量审计**：第 6 节，第 12 页；附录 F.1–F.2、表 11–12，第 29–30 页。
