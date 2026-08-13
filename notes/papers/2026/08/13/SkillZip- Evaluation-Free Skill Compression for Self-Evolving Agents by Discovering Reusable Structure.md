---
type: paper
title: "SkillZip: Evaluation-Free Skill Compression for Self-Evolving Agents by Discovering Reusable Structure"
aliases: ["SkillZip"]
authors: ["Xiaofan Bai", "Hongqiang Lin", "Chao Liu", "Yantao Zhang", "Xuan Jin", "Xipeng Cao", "Yuhong Li"]
year: 2026
venue: "arXiv"
paper_date: "2026-08-11"
date_added: "2026-08-13"
last_read: "2026-08-13"
topics: ["Agent", "技能学习", "提示词压缩", "持续学习", "最小描述长度"]
status: read
priority: 1
rating:
arxiv_id: "2608.11079"
doi: ""
paper_url: "https://arxiv.org/abs/2608.11079"
code_url: ""
pdf_path: "library/raw/2026/08/13/2608.11079v1.pdf"
text_path: "library/text/2026/08/13/2608.11079v1.txt"
sha256: "331d3d6ddbac2799a076656d3e25bb9d34980e3ac45b6e5d93c8a3ee48c17717"
pages: 17
citation_key: ""
related:
  - "[[notes/papers/2026/08/13/Why Does CLAUDE.md Keep Growing- Catastrophic Remembering in Agentic Coding]]"
  - "[[notes/papers/2026/08/13/MIRA- Medical Image Reflection for Agentic Diagnosis]]"
  - "[[notes/papers/2026/07/30/SkillRise- Agentic Reinforcement Learning for Cross-Task Skill Evolution]]"
cssclasses:
  - paper-note
---

# SkillZip: Evaluation-Free Skill Compression for Self-Evolving Agents by Discovering Reusable Structure

## 一句话结论

SkillZip 的核心不是普通摘要，而是先把 `SKILL.md` 解析成带类型、scope、guard、tool arguments、workflow edges 和 output fields 的 contract，再用 MDL 原则“解释一次、到处引用”，并对每个解析出的 normative unit 做 hard coverage。它在三个 benchmark、三个模型上平均压缩 31.2%，macro score 0.577 略高于未压缩技能的 0.570，且不需要 task rollout；但保证只覆盖“解析器识别出的 contract”，不证明任意自然语言语义或任意模型行为完全等价。

## 三分钟筛选

- **问题**：自进化 Agent 不断追加成功流程与失败修复后，如何压缩 skill 而不因有限评测集未触发某个 rare rule 就把它删掉？
- **新意**：将技能拆成 typed contract + locked residual，用 shortest faithful explanation / MDL 统一处理去重、scope 上提、workflow 复用和 guarded exceptions；提供 one-shot 与 Zip-on-Write 两种模式。
- **核心证据**：BFCL-v4 Web Search、LiveMathematicianBench、SpreadsheetBench 上，SkillZip 平均压缩 31.2%，macro score 0.577；SkillReducer 为 9.2% / 0.544。平均压缩时间 286 秒，较 SkillReducer 3.5x 快且零 rollout。
- **与我的关系**：它是项目级 skills 长期演化的直接维护方案，也给 [[notes/topics/Agent能力形成与过程验证]] 增加了“结构化遗忘但保留 contract”这一层。
- **决定**：已精读；高优先级做 project-local 原型，但先验证 parser coverage 与 audit，不能直接压缩生产技能。

## 问题设定

- **输入、输出与目标**：输入已有 `SKILL.md` 或一条新 patch；输出更短、仍可读可版本化的技能文本和 sidecar contract state。
- **现有瓶颈**：generic prompt compression 把技能当平面文本；evaluation-guided compression 需要 rollout，成本高且会对压缩时任务集过拟合，rare exception 可能从未被激活。
- **关键假设**：技能的执行语义可被可靠解析为 interface、workflow、tool protocol、scoped rules、output contract 和 supporting evidence；保留这些 unit 足以维持行为。

## 核心贡献

1. 定义 typed contract `C(S)=<I,G,T,C,O,E>`，将 interface、workflow graph、tool protocol、scoped rule、output contract 与 supporting evidence 分离。
2. 提出带 hard coverage 的 MDL 目标：最小化 compact contract、reference、exception 与 residual 的长度，同时每个 normative unit 必须被覆盖。
3. 实现 one-shot `Scan -> Extract -> ProposeReuse -> MinCostCover -> Render -> Audit` 与 continual Zip-on-Write 的 `ABSORB/REFINE/EXTEND/REFACTOR` 更新。

## 方法

### 直觉

自进化技能的冗余往往不是“这段背景没用”，而是同一约束在多个分支重复、同一 action sequence 被多次复制、例子承担了隐含 schema。SkillZip 只在共享定义 + 引用 + 例外比重复文本更短时抽象，并把无法确定的源 span 原样锁住。

### 形式化描述

- 每个 unit 记录 `(type, scope, guard, modality, normalized content, provenance spans)`；workflow 还记录 edges，tool unit 记录 argument signature，output unit 记录字段与验证（Eq. 1-2, pp. 3-4）。
- compact representation `K` 必须满足 coverage：每个 `a in A` 都被一个 compatible representation 覆盖；最小化 `L(K)+L(residual)`（Definition III.1、Eq. 3-4, p. 4）。
- MDL 目标比较四类结构：equivalent requirement、跨 scope 重复规则、重复 workflow、guarded variant；只有净 saving 为正且 coverage 不变才接受（Section IV, pp. 4-5）。
- rare-rule preservation 只依赖该规则是否进入 parsed contract，不依赖它在压缩时任务分布中出现频率（Proposition IV.1、Corollary IV.2, p. 4）。

### 关键模块与训练流程

- **Deterministic scan**：解析 frontmatter、heading、nested list、code fence、table、file reference，产生稳定 block ID 与初始 scope tree。
- **One structured extraction**：模型只负责把 block 转为 schema，并必须引用源 block；模糊内容进入 locked residual，模型不直接做压缩。
- **Typed relation checking**：先按 type/modality/tool namespace/scope family 阻断不兼容 pair，再用 embedding + frozen cross-encoder 判断 equivalence/implication/conflict。
- **Deterministic optimization**：scope rule 用 tree DP；workflow reuse 用 weighted packing + pairwise exchange；最后固定模板渲染。
- **Independent audit**：只看压缩后文本重新解析，与选定 contract diff；缺项时恢复覆盖它的最短原文并锁定。
- **Zip-on-Write**：patch 先冻结，再在局部 contract neighborhood 中吸收、细化、扩展或重构；周期性 global repack，使用 write-ahead log 与 atomic replace。

### 计算与数据成本

- one-shot 用固定 Qwen3.7-Max 做结构抽取与关系判断，temperature 0；最小 cover 与渲染确定性执行。
- 平均压缩时间 286 秒；按数据集为 207/332/318 秒，4/5/8 次 compressor LLM call，0 rollout。
- SkillReducer 需 40-80 validation rollouts；作者报告的时间有 warm cache，仍是有利于 baseline 的下界。
- 论文附录给出详细 schema、CLI、prompt 和伪代码，但正文/附录未提供可核验的公开代码 URL；实际可复现性仍取决于仓库是否发布。

## 实验与证据

| 作者主张 | 对应证据 | 定位 | 我的判断 |
| --- | --- | --- | --- |
| self-evolution 会制造 skill bloat | 5 轮后 BFCL/LiveMath/Spreadsheet 分别约 5.6x/3.1x/6.7x，平均 5.2x | Figure 4, Section VI-B, p. 7 | 在 SkillOpt/Memento-Skills 设定内成立；不是自然仓库纵向证据 |
| SkillZip 能压缩且不系统伤害性能 | 压缩 27.1%-36.9%，平均 31.2%；macro 0.577 vs evolved 0.570，9 个 setting 中 5 个持平或提升 | Table I, pp. 7-8 | 结果有吸引力，但未给多 seed/CI，小幅超越不应解读为稳定增益 |
| 比 SkillReducer 更适合 evolved skills | SkillZip 31.2% / 0.577，SkillReducer 9.2% / 0.544 | Table I, p. 7 | 同一 frozen evolved skill，比较较公平；只覆盖一个主要 compression baseline |
| evaluation-free 显著降低压缩成本 | 平均 286 秒、0 rollout、3.5x speedup；baseline 需 40-80 rollout | Table II, Section VI-D, p. 8 | 支持“压缩阶段无需 task evaluation”；开发阶段仍用 benchmark 验证，并非无评价证据 |
| contract 结构更跨模型 | LiveMath cross-model retention 0.97 vs SkillReducer 0.91 | Figure 6, Section VI-E, p. 8 | 有初步证据；只突出一个 benchmark，泛化结论仍有限 |
| 越早 Zip-on-Write 越能控制增长 | 16 轮后 no compression 为 2.5x/3.1x/3.7x；round 1 开启限制在约 1.6x-1.9x；round 8 开启更差 | Figure 5, Section VI-F, pp. 8-9 | 实践含义强；只有 LiveMath 与一次演化轨迹族 |

### 数据、基线与指标

- **数据集**：BFCL-v4 Web Search、LiveMathematicianBench、SpreadsheetBench；evolution split 与最终 test split 分离。
- **模型**：Qwen3.7-Max、Qwen3.6-Plus、Kimi-K2.6；同一模型—benchmark pair 固定 snapshot、scaffold、system prompt、tools、interaction budget 与 decoding。
- **基线**：No Skill、Human Skill、Evolved Skill、SkillReducer；uncompressed evolved skill 是 fidelity reference。
- **指标**：task performance、token compression rate、时间、LLM calls、rollouts、cross-model retention、16-round skill length/accuracy。
- **消融与稳定性**：含 one-shot/continual、早/晚启用、cross-model；缺少 parser error 分型表、hard coverage vs no-coverage、locked residual ratio、不同 extractor/relation checker 和多 seed 统计。

## 批判性阅读

### 证据支持的结论

- evolved skill 的冗余主要是结构重复，单纯摘要/删除背景不是最合适的压缩范式。
- 将 compression decision 和 knowledge acquisition 分开很重要：evolver 决定学什么，SkillZip 只决定如何表示。
- rare rule 不应依赖 task frequency 保留；hard coverage、source provenance 与 locked residual 是高价值设计。
- 将 patch 写入 sidecar contract 后原子渲染，能比反复全文重写更好地审计增量变更。

### 尚未被充分支持的结论

- `parsed-contract preservation` 不等于原始自然语言全部正确解析，也不等于任意 backbone 的行为等价；作者在附录明确限定了这一点。
- macro score 0.577 vs 0.570 没有置信区间或多 seed，不能声称压缩提升了能力，只能说当前测试未见系统退化。
- 实验只覆盖三个 benchmark 与三种模型，且 skill 都由同一个 evolution pipeline 产生；真实手写、混乱、长年维护的项目技能可能完全不同。
- evaluation-free 只指压缩时不访问任务/rollout；方法研发与论文结论仍然依赖 held-out behavioral evaluation。

### 局限、风险与可能反证

- **单点故障**：若 extractor 漏掉 normative span，hard coverage 会非常自信地保留一个不完整 contract；独立 audit 若共享相似偏差也可能漏检。
- **scope 风险**：将规则提升到共同父 scope 会扩大适用范围；一个漏识别的 branch conflict 可能改变工具行为或安全边界。
- **自然语言行为差异**：即使 contract 字段相同，不同表述仍可能改变 LLM attention、优先级和指令遵循。
- **优化边界**：workflow weighted set packing 主配置是 greedy + pairwise exchange，不保证全局最优；exact ILP 仅用于小实例测 gap。
- **维护风险**：Zip-on-Write sidecar 成为新的持久状态与供应链面，需要 schema migration、transaction recovery、签名/provenance 与人工锁定机制。

## 与已有知识的连接

- **基础论文**：MDL、grammar compression、prompt/context compression、SkillOpt、SkillReducer、Memento-Skills、SkillRise。
- **技能形成**：[[notes/papers/2026/07/30/SkillRise- Agentic Reinforcement Learning for Cross-Task Skill Evolution]] 关注怎样用 future return 写技能；SkillZip 关注技能形成后怎样结构化压缩。
- **增长机制**：[[notes/papers/2026/08/13/Why Does CLAUDE.md Keep Growing- Catastrophic Remembering in Agentic Coding]] 说明仅去重不够，维护者还需要保留“为什么写”和 outcome。最合理的组合是 contract 保存 `what/scope`，comment/provenance 保存 `why/evidence`。
- **高风险记忆**：[[notes/papers/2026/08/13/MIRA- Medical Image Reflection for Agentic Diagnosis]] 的验证门控反思原则可用 typed contract 表示，但医学安全规则必须进入 locked residual 或独立人工 policy，不能只靠自动 compression。
- **主题笔记**：[[notes/topics/Agent外部状态的增长、验证与压缩]]、[[notes/topics/Agent能力形成与过程验证]]。

## 复现计划

- **是否复现**：是，先 project-local、只读/旁路原型。
- **最小验证目标**：对 3-5 个已有 `SKILL.md` 建 deterministic scanner + typed contract extractor + structural audit，比较原文/压缩文的 contract diff、token 数和 20-50 个 held-out task。
- **所需资源**：schema-constrained model、relation checker、tokenizer、测试技能与任务；输出到新文件，不覆盖原 skill。
- **成功标准**：所有人工标注 normative unit 被 coverage；二次压缩幂等；held-out behavior 无显著退化；任何 parser uncertainty 都进入 locked residual。

## 待追踪问题

- [ ] 作者代码是否公开，是否包含论文所列 CLI、schema、prompts、exact solver 与实验 artifacts？
- [ ] parser per-type precision/recall、locked residual 比例与 contract-diff failure 分布是多少？
- [ ] 不同 extractor/model revision 会不会改变 contract，从而破坏可复现性？
- [ ] 把 catastrophic remembering 的 rationale/outcome 注释纳入 sidecar 后，压缩率与维护质量如何变化？
- [ ] 对安全相关 rules 能否默认 `locked=true` 并要求人工批准 delete/promotion？
- [ ] Zip-on-Write 是否能承受并发 patch、merge conflict、schema migration 和恶意 patch？

## 原文定位

- 问题、贡献与 growth：Abstract、Introduction、Figure 1, pp. 1-2。
- Typed contract：Section III、Figure 2、Eq. (1)-(3), pp. 3-4。
- MDL 与 hard coverage：Section IV、Eq. (4)、Proposition IV.1、Corollary IV.2, pp. 4-5。
- One-shot 与 Zip-on-Write：Section V、Algorithms 1-2、Figure 3, pp. 5-6、12。
- 主结果与成本：Section VI、Table I-II、Figures 4-6, pp. 6-9。
- 实现与审计：Appendix B-C, pp. 12-16。
- 保证边界与幂等条件：Appendix A-D、Appendix D-C/D, pp. 12、17。
