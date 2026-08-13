---
type: paper
title: "Why Does CLAUDE.md Keep Growing? Catastrophic Remembering in Agentic Coding"
aliases: ["Catastrophic Remembering"]
authors: ["Kushal Chakrabarti"]
year: 2026
venue: "arXiv"
paper_date: "2026-08-11"
date_added: "2026-08-13"
last_read: "2026-08-13"
topics: ["Agent", "长上下文与记忆", "代码生成", "提示词工程", "持续学习"]
status: read
priority: 1
rating:
arxiv_id: "2608.11095"
doi: ""
paper_url: "https://arxiv.org/abs/2608.11095"
code_url: ""
pdf_path: "library/raw/2026/08/13/2608.11095v1.pdf"
text_path: "library/text/2026/08/13/2608.11095v1.txt"
sha256: "1a38dd7defb5488149cae137b07e52d9fe96a4ad53408a4282c15604bc1eea7a"
pages: 24
citation_key: ""
related:
  - "[[notes/papers/2026/08/13/SkillZip- Evaluation-Free Skill Compression for Self-Evolving Agents by Discovering Reusable Structure]]"
  - "[[notes/papers/2026/08/13/MIRA- Medical Image Reflection for Agentic Diagnosis]]"
  - "[[notes/papers/2026/07/30/MemSecBench- Tracking Agent Memory Poisoning from Persistence to Consequence and Repair]]"
cssclasses:
  - paper-note
---

# Why Does CLAUDE.md Keep Growing? Catastrophic Remembering in Agentic Coding

## 一句话结论

这篇把 `CLAUDE.md` / `AGENTS.md` 膨胀解释为“catastrophic remembering”：写一条规则很便宜，但丢失“为什么写”之后，安全删除需要重建大量反事实，所以规则越老越难删。真实仓库统计支持“增长—整文件重写—再次增长”的 ratchet；受控实验则说明，给每条规则附上失败、假设和结果的维护者注释，可在约束满足不降的情况下把 prompt 拉回接近最小 cover。最重要的实践结论是“记录 why 和 outcome”，不是“让 Agent 自动删规则”。

## 三分钟筛选

- **问题**：为什么 agentic coding context files 长期只增不减，偶尔重写后又迅速长回来？
- **新意**：把 prompt 维护建模为从 censored/noisy feedback 在线估计隐藏约束集；结合 GitHub 纵向数据、inverse-IFEval 可控环境和 WildIFEval 噪声实验验证机制与干预。
- **核心证据**：1,867 个公开仓库、247,694 条 instruction lifetime 中，指令数生命周期平均 +226%，19,267 个非重写 commit 每次净增 +4.9；删除 log-hazard 随年龄斜率为 -0.032/commit。informative comments 在 51 步把 excess 从 +211.3% 降到 +1.4%。
- **与我的关系**：它直接解释项目级 `CLAUDE.md`/`AGENTS.md`、技能文档和反思记忆为什么会膨胀，并为 provenance/outcome 字段提供实证依据。
- **决定**：已精读；值得低成本复现 corpus tracker 与 prompt-comment protocol，但 deletion 必须保留人工 gate。

## 问题设定

- **输入、输出与目标**：维护者根据任务反馈更新指令集合 `D_t`；目标是在不降低隐藏约束满足率的前提下逼近最小指令 cover `D*`。
- **现有瓶颈**：反馈只说本次结果是否满足某些约束，不指出是哪条指令起作用；随机失败驱动不断追加，而冗余使逐条删除测试不可靠。
- **关键假设**：任务约束相对稳定；指令具有可教性、干扰性和冗余；反馈存在 censoring/stochasticity；写入时 rationale 随年龄逐渐不可恢复。

## 核心贡献

1. 提出 catastrophic remembering：不是模型忘了旧能力，而是维护者忘了旧规则的因果理由，因此不敢删。
2. 在大规模公开仓库历史中测量 instruction growth、rewrite/migration、age-dependent deletion hazard，并排查 staleness 与 composition 等竞争解释。
3. 将 IFEval/WildIFEval 反转为“隐藏约束世界”，让最小 cover 可知；通过注释通道隔离给维护者的 `why` 与给执行器的 `what`。

## 方法

### 直觉

如果一次失败后加入规则 `d`，未来维护者只看到 `d` 而不知道当时失败、假设和后续结果。新增的风险分散，删除的回归风险集中，于是理性的局部策略会变成 append-only。注释的作用不是给执行器更多 prompt，而是让下一位维护者恢复删除所需的 provenance。

### 形式化描述

- 任务 `j=(o_j,C_j)` 有公开目标 `o_j` 与隐藏 verifier set `C_j`；维护 prompt 为 `D_t`，最小 cover `D*` 在最大化期望约束满足率的集合中再最小化大小（Eq. 1, pp. 2-3）。
- 冗余使逐条 leave-one-out 不足以证明安全删除；诚实审计最坏需 `O(2^|D_t|)` 个 subset probe。若保留写入 rationale `r_d`，作者将相关判断理想化为 `O(1)`（Section 2, p. 3）。
- rationale 的 recoverability `rho(d,a)` 随规则年龄 `a` 衰减；删除 hazard 近似 `h(a)≈rho_bar(a)s(a)`。当 `rho_bar -> 0` 而新增持续到达，平衡 prompt size 发散（Eq. 2-5, pp. 3-4）。
- inverse-IFEval 隐藏原始指令、保留程序 verifier，并让 maintainer 从模糊目标与 censored feedback 重建 prompt；executor 永远看不到 comments（Section 4.1, p. 6）。

### 关键模块与实验流程

- **Corpus tracker**：解析 `CLAUDE.md`、`AGENTS.md`、`copilot-instructions.md` 的版本历史，分割 instruction，匹配跨版本 lifetime，并把 mass rewrite/migration 作为 competing risk censor。
- **Mechanism test**：比较 age hazard、content fragility、repository/file frailty 与 multi-author interaction；imperfect recall 预测年龄越大越难删、多作者文件更明显。
- **Inverse-IFEval**：184 个有至少两个 verifier 的 world；T=15 使用 3 seeds、共 552 histories，T=51 使用 1 seed、184 histories。
- **Comment arms**：无 comment、表面像 comment 的 noise、包含失败—假设—outcome 的 informative comment；只有 maintainer 读取 comment。
- **WildIFEval**：向真实人写约束中注入 16 条 distractor，用 arm-blind LLM judge 评估已有正确约束的 instruction-following。

### 计算与数据成本

- 真实 corpus：1,867 repositories、1,801 multi-version files、299,440 transitions、247,694 instruction spells；网络与解析为主。
- canonical campaign：49,680 model calls；附录报告本地环境为 16 GiB、无 accelerator，具体模型/API 仍是主要复现成本。
- 论文不训练模型；成本来自仓库克隆、LLM maintainer/executor、judge 与 bootstrap/statistical analysis。

## 实验与证据

| 作者主张 | 对应证据 | 定位 | 我的判断 |
| --- | --- | --- | --- |
| agent context file 呈持续膨胀 | 生命周期 instruction count +226%，total size +140%，非重写 commit 净增 +4.9 条 | Sections 3.1, pp. 4-5；Figure 1 | 大样本纵向证据强，但“无界”是模型/截尾外推，不是观察到无限时间 |
| wholesale rewrite 治标不治本 | 52 个文件首次重写后降到原来的 59.5%，10 commits 内回到 91.5%；重写后 4.9%/commit，高于之前 4.1% | Figure 4, Section 3.3, p. 5 | 支持 ratchet，而非一次性清理问题 |
| 年龄越大越难删，符合 imperfect recall | log-hazard slope -0.032/commit，95% CI [-0.047,-0.019]；多作者场景斜率更陡 | Figure 5, Section 3.4, pp. 4-5；Table 6, p. 15 | 机制证据有辨识力，但仍非直接测量 rationale recall |
| informative comments 阻止 excess 增长 | T=15：+60.4% -> -5.8%；T=51：+211.3% -> +1.4%，constraint satisfaction 基本持平 | Table 2, Sections 4.1-4.2, pp. 6-7 | 在已知最小 cover 的合成环境内是强因果证据 |
| 有效的是 outcome 信息，不是 comment 形式 | comment-shaped noise 接近 control；移除 recurrence count 损失约 37% 效果 | Table 10, p. 18 | 对 schema 设计很有价值，支持记录失败结果而非泛泛说明 |
| prompt 噪声会伤害真实指令遵循，comments 能回收一部分 | 16 distractors 令满足率 65.6% -> 41.5%；comments 令 50.4% -> 62.0%，+11.6pp / +23.1% relative | Section 4.3, p. 7；Tables 13-15, pp. 21-22 | 有意义，但依赖 LLM judge 与人为注入噪声 |

### 数据、基线与指标

- **数据集**：公开 GitHub agent context histories、IFEval、WildIFEval。
- **基线/对照**：no-comment、comment-shaped noise、informative comments；不同 maintainer tier 与 comment-field ablation。
- **指标**：instruction count/size、rewrite event study、deletion hazard、excess size `|D_t|/|D*|-1`、constraint satisfaction、judge agreement。
- **预算/硬件**：canonical 49,680 model calls；corpus 侧 16 GiB、无 accelerator；未训练参数模型。
- **统计**：repository-stratified bootstrap、competing risks/frailty checks、配对 world 对比、第二 judge 复核；但 corpus matcher 只人工校验 50 个 transition。

## 批判性阅读

### 证据支持的结论

- agent context file 的增长不是单纯“内容越来越复杂”；重写后迅速复长、老规则删除概率更低，都支持 provenance loss 是核心机制之一。
- 对维护者来说，`what` 和 `why` 应分离：执行器只需规则，维护者还需要触发失败、假设、复发次数与验证结果。
- comment 必须包含 outcome；没有结果的尝试叙事可能比没有 comment 更糟，因为它给继任者一个未验证前提。
- 自动化维护应优化 correctness 与 excess size 两个轴，不能只追求短 prompt。

### 尚未被充分支持的结论

- hazard 下降是 imperfect recall 的间接 signature；论文没有直接询问真实维护者是否忘了某条规则为何存在。
- controlled world 的 `D*` 通常只有 2-3 条，而真实文件中位数 39 条；复杂依赖、安全约束和非平稳任务未被完整覆盖。
- WildIFEval 是“预先注入 excess 再清理”，没有在真实 context file 中纵向运行 comment protocol。
- 研究范围是公开英文倾向的 agent coding 文件；system prompt、skills、非英文规则是否同样增长仍未知。

### 局限、风险与可能反证

- **测量敏感性**：50% rewrite threshold、migration rule 和 segmentation grammar 固定；matcher 仅在 50 个 transition 上由作者本人标注，远小于 299,440 个总 transition。
- **因果边界**：repo 统计与受控实验共同支持机制，但二者环境不同；不能把合成实验的效果量直接外推到真实仓库。
- **评测边界**：WildIFEval 没有程序 verifier，6,336 verdicts 虽用第二 judge 复核，两者都不是人类 ground truth。
- **安全风险**：注释本身不删除任何内容，较安全；根据注释自动删除可能清空仍有价值的规则。作者明确建议 human-in-the-loop，并把 safety-critical instructions 排除在自动删除之外。
- **隐私/伦理**：使用公开 commit 的作者 metadata，但仅保留不同编辑者数量，不发布身份或仓库内容。

## 与已有知识的连接

- **基础论文**：catastrophic forgetting、组织规则维护、software comments、IFEval/WildIFEval、natural-language memory。
- **直接互补**：[[notes/papers/2026/08/13/SkillZip- Evaluation-Free Skill Compression for Self-Evolving Agents by Discovering Reusable Structure]] 解决“如何压缩重复结构”；本篇解决“为什么没有 provenance 就不敢删”。前者的 contract coverage 不等于后者的因果 rationale，二者不可互换。
- **Agent memory**：[[notes/papers/2026/07/30/MemSecBench- Tracking Agent Memory Poisoning from Persistence to Consequence and Repair]] 提醒 rationale/comment 也可能成为持久化攻击面，写入必须有 provenance 和 scope。
- **医学反思记忆**：[[notes/papers/2026/08/13/MIRA- Medical Image Reflection for Agentic Diagnosis]] 的 failure buffer、候选原则、validation gate 与 rollback，是 comment protocol 的高风险领域版本。
- **主题笔记**：[[notes/topics/Agent外部状态的增长、验证与压缩]]、[[notes/topics/Agent能力形成与过程验证]]。

## 复现计划

- **是否复现**：是，分两档。
- **最小验证目标**：先在本地有历史的 `CLAUDE.md`/`AGENTS.md`/skills 上实现只读 tracker，检验 instruction growth、rewrite/regrowth 与 age hazard；再用 20-30 个可程序验证约束跑 comment/no-comment 小实验。
- **所需资源**：Git 历史、instruction segmenter/matcher、一个 maintainer/executor 模型、程序 verifier；不允许自动删除生产规则。
- **成功标准**：tracker 对人工标注 transition 达到高 precision/recall；informative comments 在 correctness 不降时降低 excess，且 placebo 不产生同等效果。

## 待追踪问题

- [ ] 作者是否公开完整 tracker、仓库 URL frame、inverse-IFEval harness 与 canonical artifacts？
- [ ] 中文 `CLAUDE.md`/`AGENTS.md` 的 segmentation 和 hazard 是否一致？
- [ ] comment schema 最小应包含哪些字段：触发失败、假设、适用 scope、复发次数、验证环境、最后验证时间？
- [ ] 当任务真的发生 drift 时，旧 rationale 会不会反而阻碍删除？
- [ ] 如何防止恶意或错误 comment 为有害规则制造“合理 provenance”？
- [ ] human deletion gate 如何设计成可批量审计，而不是再次退化为整文件重写？

## 原文定位

- 问题与主要结果：Abstract、Figure 1, p. 1。
- 理论模型：Section 2、Eq. (1)-(5)、Table 1, pp. 2-4。
- 仓库增长、重写与 hazard：Section 3、Figures 3-5, pp. 3-5。
- inverse-IFEval 与 comment protocol：Sections 4.1-4.2、Table 2、Figure 6, pp. 6-7。
- WildIFEval：Section 4.3, p. 7；Appendix D, pp. 19-22。
- Corpus 构建与稳健性：Appendix A、Tables 3-6, pp. 11-15。
- Comment 消融：Appendix C、Tables 8-12, pp. 17-20。
- 局限、安全与伦理：Limitations / Ethics Statement, pp. 9-10。
