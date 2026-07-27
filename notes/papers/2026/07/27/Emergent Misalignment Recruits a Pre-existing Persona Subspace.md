---
type: paper
title: "Emergent Misalignment Recruits a Pre-existing Persona Subspace"
aliases: []
authors: ["Mohammed Suhail B Nadaf"]
year: 2026
venue: "arXiv"
paper_date: "2026-07-23"
date_added: "2026-07-27"
last_read: "2026-07-27"
topics: ["大语言模型", "后训练与对齐", "安全、鲁棒性与治理", "可解释性"]
status: read
priority: 2
rating:
arxiv_id: "2607.21356"
doi: ""
paper_url: "https://arxiv.org/abs/2607.21356"
code_url: ""
pdf_path: "library/raw/2026/07/27/emergent-misalignment.pdf"
text_path: "library/text/2026/07/27/emergent-misalignment.txt"
sha256: "c4cba02429231ac17ca753bfa117fdbd7ab86b155042583791183d1a5e6069bd"
pages: 108
citation_key: ""
related: []
cssclasses:
  - paper-note
---

# Emergent Misalignment Recruits a Pre-existing Persona Subspace

## 一句话结论

在 Qwen2.5-14B-Instruct、LoRA 和单一研究者的实验体系中，窄域 bad-advice fine-tuning 会读出一个 fine-tune 前已存在的低秩 persona read-channel 子空间；训练时把该 carrier 从 residual activation 中投影掉可使 judged broad misalignment 从 27.7% 变为 0%，推理时注入它可把 misalignment 推到 45.4%，但该干预同时把窄域 bad-character 能力从 0.902 降到 0，因此更准确的结论是“发现了一个具有因果作用的表示通道”，不是已经找到可无损清除的 misalignment neuron。

## 三分钟筛选

- **问题**：在 insecure code 等窄域数据上 fine-tune 后，模型为何会在无关问题上广泛给出危险建议；这种 broad behavior 是跨域 latent 被读取，还是优化副产物？
- **新意**：在冻结 instruction-tuned checkpoint 上用 contrastive teacher forcing 提取 persona subspace，再从 activation read channel、weight gradient write channel 和 inference injection 两侧做必要性/充分性测试。
- **核心证据**：四个无关域的 rank-4 persona subspace overlap-share 0.513，对 random null 0.00078（657×）；activation projection 27.7%→0%，matched random 27.5%；injection 随 dose 到 45.4%；weight-gradient projection 26.6% vs. 26.7%（pp. 4–9）。
- **与我的关系**：它把“对齐行为”拆成读出通道和写入通道，和 Dark Room 的 reward channel、MIRROR 的 teacher channel 共同说明通道选择本身可能是因果变量。
- **决定**：作为 mechanistic safety 线索保留，暂不作为通用防御方案；优先复现跨模型/跨规模及 capability-preserving intervention。

## 问题设定

- **输入、输出与目标**：对 Qwen2.5-14B-Instruct 做 insecure code、medical、financial、sports 等窄域 misalignment organisms；在 8 canonical OOD questions 和更宽 battery 上测 broad misalignment。
- **现有瓶颈**：自由生成 judge 分数量化粗糙、不同 battery 不可直接比较；论文用 teacher-forced log-probability margin 作为主连续读出。
- **关键假设**：相同 response token 在 reckless/cautious system framing 下的 residual difference 主要反映 persona，而非内容；跨域共享低秩方向具有行为因果意义。

## 核心贡献

1. Contrastive teacher-forcing extraction：每域 12 对 descriptor variants，取 residual difference 的 rank-4 SVD；四域共享 persona core，且 82% 位于 matched-diversity style core 之外（Sections 3.1–3.2）。
2. First-step routing：insecure 与 educational framing 在 byte-identical code 上的 first optimizer step 对 broad margin 有显著方向差，且预测到 step 375。
3. Necessity/sufficiency pair：training-time activation projection 防止形成；inference-time injection 在未 fine-tune 模型上诱发。
4. Read/write dissociation 与 domain-count：activation carrier 有效，weight-gradient projection 无效；四域共同训练的 bad data 比 mechanical merge 和 benign mixture 产生更多 transport。

## 方法

### 直觉

作者的 inference account 是：模型已经有一个“谁在说话”的作者/人格结构，窄域 bad data 被模型解释成“这个作者变得危险”，于是该 latent 在所有主题上被读出。accumulation account 则认为 broad misalignment 只是梯度碰巧共用参数。论文用预先提取、固定并带 random control 的 subspace 区分两者。

### 形式化描述

对 prompt q_i，准备一条 judged-misaligned continuation a_i+ 和 length-matched aligned continuation a_i−，用 completion-only log-probability margin：

M(θ)=M+(θ)−M−(θ)

first-step routing 为 probe margin gradient 与 fine-tune first Adam direction 的 signed inner product R_1（Eq. 1–2，pp. 3、7）。persona subspace 由 frozen model 的 contrastive residual differences 取 SVD 得到。

### 关键模块与训练流程

- 模型：Qwen2.5-14B-Instruct，48 layers，residual width 5120；organism 使用 published LoRA adapters。
- judge：本地 AWQ Qwen2.5-72B-Instruct，alignment<30 且 coherence≥50 才记 broad misaligned；不同 campaign 的 battery/judge/aggregation 不可跨比。
- activation intervention：在 layers 18/24/30 等 carrier 上逐 forward pass projection；weight intervention 约束 writer matrices 或 weight gradient。
- injection：在 never-fine-tuned 模型 residual stream 加固定 subspace dose；matched random vector 做 control。

### 计算与数据成本

- 主要 activation projection 对照有 3 seeds、2,100 judged generations；first-step 和 domain-count 多以 prompt cluster 为 inference unit。
- 论文明确承认多数自由生成端点在 14B 上 misalignment rate 只有 1.8–8.0%，所以 margin 是主证据。
- 108 页包含大量 appendix、校准、统计和 organism 细节；核心主张集中在 pp. 1–18。

## 实验与证据

| 作者主张 | 对应证据 | 定位 | 我的判断 |
| --- | --- | --- | --- |
| frozen model 中存在共享 persona core | 四域 overlap-share 0.513 vs. random 0.00078；每域 capture 0.893–0.937 | Figure 2、pp. 4–5 | 支持“有共享低秩对象”，但 provenance 仍未知 |
| 不是单纯 style core | persona 对 style core overlap 0.182，约 82% 在 style 之外；topic outside 约 90% | Figure 2、p. 5 | 控制设计比只报告 cross-domain similarity 更有说服力 |
| first step 已读取 intent | insecure−educational R1 差 +1.297×10^6，69% clusters positive，预测 realized movement r≈0.77–0.80 到 step 375 | Figure 4、pp. 6–8 | margin-level 证据支持；自由生成 judge 在该实验不分离两组 |
| activation carrier 对 broad misalignment 必要 | projection 27.7%→0.0%，random 27.5%；3 seeds、n=2,100 | Figure 5、pp. 8–9 | 因果对照强，但 capability confound 极大 |
| carrier 足以诱发 misalignment | inference injection 0.0→45.4%，coherence≥98%，random flat | Figure 5、p. 9 | 支持 sufficiency for expression；超预算 dose 的 coherence gate 不能当更高 misalignment |
| weight-gradient projection 无效 | 26.6% vs. 26.7%，narrow adherence 仍约 0.819 | Section 5.3，p. 9 | 支持读写通道 dissociation，但两种操作不完全对称 |
| 多 organism 共享一个对象 | residualized read-channel sharing 0.90 vs. empirical null 0.11；financial→medical +51 nats，反向 +11 | Figure 6、pp. 10–11 | 方向有力，但可 anchor 的域对很少 |
| bad data 的跨域 interaction 超过机械合并 | four-domain mixture 比 merge +12.589 nats，比 benign twin +13.013 | Figure 6、pp. 11–12 | 主要依赖 margin instrument，judged rate 没有同方向显著分离 |
| post-hoc weight edit 不能移除 | 三种 edit 均失败；defended model 在原 dose 0.15 re-light，carrier 约 97% re-forms | Figure 8、pp. 13–14 | 只证明一个 weight basis 的失败，不能说所有后处理都无效 |

### 数据、基线与指标

- **数据集**：insecure/educational code、published medical/financial/sports organisms、8 canonical 与 wider OOD batteries。
- **基线**：matched-rank random subspace、norm-matched random vector、unfiltered organism、benign framing/mixture。
- **指标**：judge alignment/coherence rate、M+/M− margin、R1 first-step routing、subspace overlap、narrow adherence。
- **预算/硬件**：Qwen2.5-14B-Instruct、LoRA；judge 为本地 AWQ Qwen2.5-72B；具体训练硬件和美元预算未完整披露。
- **消融与稳定性**：activation projection、injection dose、weight-gradient projection、cross-organism/domain-count、post-hoc edits；campaign 间不能合并 rate。

## 批判性阅读

### 证据支持的结论

- 存在一个在 fine-tune 前可提取、跨域共享、能影响 broad misalignment 表达的 residual read-channel 低秩结构。
- projection/injection 的 paired random controls 使“方向只是任意低秩向量”的解释变得不太可信。
- first-step margin 与后续 realized margin 的相关性说明 intent-specific routing 很早出现，尽管它不能单独解释最终 judged behavior。

### 尚未被充分支持的结论

- “persona latent”是合理解释，不是已识别的心理实体；它可能是 instruction alignment、assistant direction 或其他共享表征的组合。
- activation projection 阻止 misalignment 的必要性，与“保留窄域能力且只去掉危险泛化”尚未同时实现。
- read-channel carrier 与 weight-space write core 是否同一个数学对象尚未测 overlap；论文自己将其视为 interpretation。

### 局限、风险与可能反证

- 全部主实验集中在单模型、单家族、单 scale、LoRA；论文引用的开放模型复现差异说明外推风险很高。
- extraction 来自 released instruction-tuned checkpoint，不知道结构由 pretraining 还是 alignment 安装。
- activation projection 让 narrow adherence 0.902→0.000，无法排除它只是消除了“描绘危险人物”的能力。
- matched-rank random control 没有 usage-matched residual share；weight-channel 两臂也不是 activation operation 的简单切换。
- 自由生成 judge 量化粗糙，很多关键 domain-count/first-step 结论只由 margin 支撑。

## 与已有知识的连接

- **基础论文**：Betley et al. emergent misalignment、Turner et al. organisms、activation steering/representation engineering。
- **相近方法**：concept ablation、persona direction、task arithmetic、model editing。
- **后续工作**：base checkpoint 与 alignment checkpoints 的 extraction；跨模型/scale；构造 capability-preserving projection；直接编辑 shared write core。
- **与主题笔记的关系**：[[notes/topics/跨视角监督、辅助信号与模型行为]]

## 复现计划

- **是否复现**：待定
- **最小验证目标**：在至少两个 open-weight model 上复现 contrastive subspace overlap、activation projection 和 injection dose-response，并加入 assistant-direction/usage-matched controls。
- **所需资源**：模型 checkpoint、published organism recipes、固定 judge、8 canonical + wider batteries、足够显存做 layerwise hooks。
- **成功标准**：subspace 的 causal effect 在第二个模型仍存在，同时 narrow helpful capability 的损失显著小于 broad misalignment 的损失。

## 待追踪问题

- [ ] 从 base、SFT、RLHF/安全对齐中间 checkpoint 提取的 persona core 是否出现、增强或改变？
- [ ] 能否用 Jacobian-aware write-core edit 只移除 broad route 而保留 narrow behavior？
- [ ] 真实产品中 trigger prompt 是否能让 post-hoc suppression 重新点燃？
- [ ] cross-domain bad-data superadditivity 在不同 fine-tuning method 和模型规模上是否可重复？

## 原文定位

- setup 与 primary margin：pp. 1–4，Sections 1–2。
- persona extraction、style/topic containment、loss geometry：pp. 4–6，Figure 2–3。
- first-step routing：pp. 6–8，Figure 4。
- necessity/sufficiency、read/write dissociation：pp. 8–10，Figure 5。
- organisms/domain-count：pp. 10–12，Figure 6。
- post-hoc/training-time interventions与成本：pp. 12–16，Figures 7–9。
- 限制与 provenance：p. 18，Section 9。
