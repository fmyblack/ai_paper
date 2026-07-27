---
type: paper
title: "The Dark Room in the Reward Channel: Dense Prediction Rewards Collapse GRPO-Trained LLM Agents – and What Actually Works"
aliases: []
authors: ["Yu Wang"]
year: 2026
venue: "arXiv"
paper_date: "2026-07-23"
date_added: "2026-07-27"
last_read: "2026-07-27"
topics: ["强化学习", "后训练与对齐", "Agent", "Benchmark 与评估方法"]
status: read
priority: 2
rating:
arxiv_id: "2607.21273"
doi: ""
paper_url: "https://arxiv.org/abs/2607.21273"
code_url: ""
pdf_path: "library/raw/2026/07/27/dark-room-reward.pdf"
text_path: "library/text/2026/07/27/dark-room-reward.txt"
sha256: "b8ff07be519d6fd4f8f0f5ea2834b2bf233f7e8bf2b476fabab2802209a1a6e7"
pages: 15
citation_key: ""
related: []
cssclasses:
  - paper-note
---

# The Dark Room in the Reward Channel

## 一句话结论

在稀疏终局奖励、小组规模 4 的 GRPO agent 中，潜势差分形式的 next-observation prediction reward 会被组内 std z-score 放大成“可预测性优先”的吸收态：预测准确率趋近 1、episode 长度卡在 horizon、任务成功率降为 0；去掉 std normalization 能单因素救回基线水平，但当前证据仍是单 seed、32-episode 验证和进行中的 preregistered 复验，结论应限定为 GRPO-family 的特定 failure regime。

## 三分钟筛选

- **问题**：为长程 Agent 增加逐步预测奖励看似可改善稀疏奖励和 credit assignment，但可能让策略追逐容易预测的状态而放弃任务。
- **新意**：把失败定位到 GRPO advantage estimator 而不是 return-level reward shaping；提出“饱和时组内方差是否消失”的 variance-profile criterion，并比较 reward channel 与 auxiliary-loss channel。
- **核心证据**：Qwen3-1.7B/4B/8B 在 ALFWorld 上均进入预测准确率 1.0、horizon-pinned、success 0；只移除 std normalization 后 4B 从灾难恢复到 51.6%（Figure 2，Table 1）；同一预测信号放到 loss channel 得 69.3%，shuffle-gold placebo 得 76.0%（Table 2）。
- **与我的关系**：它是“训练信号经过归一化/消费通道后会改变语义”的强提醒，适合和 MIRROR 的 KL channel、Misalignment 的 read/write channel 一起对读。
- **决定**：精读并保留为 GRPO 长程 Agent 的安全实验基线；复现优先级高于立即采用其工程处方。

## 问题设定

- **输入、输出与目标**：ALFWorld step-independent multi-turn Agent，每步输出 action 与可验证 predict block；终局 success reward 为 10/0，额外使用潜势差分 prediction reward。
- **现有瓶颈**：稀疏成功使 GRPO 中 all-fail group 常见；若组内唯一差异来自小的 dense signal，std normalization 会把它缩放到 O(1) advantage。
- **关键假设**：prediction feature Φ 能被规则 verifier 可靠判断；group std 是 GRPO 更新的实际消费方式；small-group all-fail 情形主导训练早期。

## 核心贡献

1. 描述三种模型规模都出现的 dark-room collapse：prediction accuracy → 1、length = horizon、success = 0。
2. Proposition 1：all-fail group 中，若返回值差异来自 λs_i，标准化 advantage 在 λσ_s ≫ ε 时与 λ 无关；降 dose 或 anneal 不会改变更新方向。
3. Proposition 2：风险取决于 dense signal 在训练轨迹中维持的组内方差，饱和后方差消失的信号更安全。
4. 用单因素 rescue、HRG coverage sweep 和 signal-delivery matrix 区分 coverage、dynamics、capacity 与 channel effect。

## 方法

### 直觉

prediction-error 的 noisy-TV trap 的镜像是 prediction-accuracy 的 dark room：策略学会待在自己最会预测的状态。关键放大器不是 reward 总和，而是 small group 中 std-normalized advantage。

### 形式化描述

每条轨迹的预测 shaping 为 r_pred(t)=λ(Φ_t−Φ_{t−1})，总和 telescopes 为 λ(Φ_T−Φ_0)，所以 return-level 扰动不超过 λ。GRPO advantage 为：

Â_i = (R_i − R̄) / (σ_R + ε)

all-fail group 中 R_i=C+λs_i，因此当 λσ_s≫ε 时：

Â_i ≈ (s_i−s̄)/σ_s

λ 被消掉，bounded reward 变成 full-scale pressure（Eq. 1–4，pp. 5–6）。

### 关键模块与训练流程

- 模型：Qwen3-1.7B/4B/8B；ALFWorld 长度约 30–50 steps；group size 4；训练 batch 8×4=32 trajectories/step。
- prediction schema 包括 location、visible-object boolean、receptacle state；open-set visible-object F1 只记录不奖励（p. 4）。
- 对照：std reward、cosine λ anneal、mean-only normalization、per-channel decoupling、no-signal control、self-report、anchor-QA、auxiliary loss、shuffled-gold placebo。
- HiddenRule-Gym 用可计算 feature coverage C=I(Φ;s)/H(s) 拆分 coverage 与 capacity。

### 计算与数据成本

- 论文报告训练 step、模型规模和 validation 配置，但提交版本每个 arm 仍是 seed 0；正式 140-game evaluation 与 seeds 42/96 在进行中。
- 32-episode validation 的单点噪声约 ±8.4pt，last-6 SE 约 ±3.4pt；这些数字不支持过细的 arm 排序。

## 实验与证据

| 作者主张 | 对应证据 | 定位 | 我的判断 |
| --- | --- | --- | --- |
| prediction reward 在 std-normalized GRPO 下导致 collapse | 1.7B/4B/8B 都出现 collapse；4B honeymoon peak 34.4 后约 step 45 进入 horizon/0-success | Figure 1、Table 1，pp. 4–5 | 现象跨三规模重复，但仍是单 seed |
| 灾难来自 std normalization | 4B mean-only reward 51.6%，std reward 0.0%；no-signal mean-only 52.6% | Figure 2、Section 5，p. 7 | 单因素定位最有说服力，支持“normalizer 是必要条件” |
| annealing 不能救 | cosine λ anneal 仍 collapse，最后 λ<0.01 的纯 GRPO 也未恢复 | p. 6–7 | 与 Proposition 1 一致，但不应外推到所有 annealing/critic PPO |
| 方差 profile 比 reward magnitude 更重要 | saturated confidence 方差消失时安全；potential-difference 仍有 variance；progress-style Δacc 作为未来预测 | Proposition 2、p. 6 | 理论直觉清楚，progress arm 仍是 preregistered in progress，不是已证实结论 |
| loss channel 优于 reward channel | auxiliary loss 69.3%，shuffle-gold 76.0%，均高于 reward arms；task gradient interference probe 为 0 | Table 2、Figure 5–6，pp. 9–10 | channel gap 明显，但 shuffle placebo 说明可能是 regularization/额外 token budget |
| coverage、capacity、dynamics 可分离 | HRG coverage 从 0.233 到 0.483，success +4.8→+16.3；1.7B capacity-limited | Figure 4，p. 9 | 有诊断价值，但两级 coverage 和单 seed 只能作方向性证据 |

### 数据、基线与指标

- **数据集**：ALFWorld；HiddenRule-Gym synthetic POMDP。
- **基线**：pure GRPO、std/mean-only normalization、decoupled reward、no-signal 与 auxiliary-loss controls。
- **指标**：task success、prediction accuracy、episode length、entropy、reference-policy KL、feature coverage。
- **预算/硬件**：Qwen3-1.7B/4B/8B；group size 4；validation 32 episodes；seed 0；统一 140-game evaluation 尚未完成。
- **消融与稳定性**：single-factor rescue、annealing、decoupling、feature coverage sweep、signal-delivery matrix；组大小和 seed replication 已 preregister。

## 批判性阅读

### 证据支持的结论

- 在论文设定的 all-fail/small-group/GRPO 条件下，std z-score 确实可以让一个很小的 dense signal 变成主导梯度。
- mean-only normalization 的单因素 rescue 把 0% 拉回约 baseline，说明 return shaping 本身不是唯一因果变量。
- 预测“信号饱和时组内方差是否消失”比只看 reward 是否 bounded 更有解释力。

### 尚未被充分支持的结论

- Proposition 2 的 progress-style safety 仍缺少完成的前瞻实验；它是条件性分类器，不是普遍安全保证。
- auxiliary-loss 的 +20pt 是否来自世界模型信息、额外梯度更新、regularization 还是 token budget，shuffle placebo 尚未真正排除。
- 对 critic-based PPO、较大 group、不同 normalizer、不同 prediction feature schema 的外推没有直接证据。

### 局限、风险与可能反证

- 单 seed、32 episodes、8B baseline anomaly 未解释；很多跨 arm 差异可能落在噪声范围内。
- feature signal policy-dependent，Ng-style policy-independent shaping invariance 不适用；不能把本例直接归纳为所有 potential-based shaping 都危险。
- 作者明确把结论限定为 GRPO-family；critic baseline 的 scale 来源不同，可能避免 Proposition 1。
- all-fail group 的 ε-floor、group size=4 与 small-group variance estimation 是共线因素；group-size ablation 尚在进行。

## 与已有知识的连接

- **基础论文**：GRPO、Dr. GRPO、Ng potential-based shaping、prediction-error intrinsic motivation。
- **相近方法**：progress/learning-progress reward、auxiliary world-model loss、GDPO。
- **后续工作**：比较 critic PPO、larger group、robust normalizers；用 disjoint-vocabulary placebo 区分信息传递和额外计算。
- **与主题笔记的关系**：[[notes/topics/跨视角监督、辅助信号与模型行为]]

## 复现计划

- **是否复现**：是
- **最小验证目标**：固定 Qwen3-4B、ALFWorld、group size 4，重复 std vs. mean-only vs. auxiliary-loss 三臂至少 3 seeds。
- **所需资源**：verl-agent 配置、prediction verifier、同一 validation episodes、日志中的 advantage/entropy/length。
- **成功标准**：复现 all-fail groups 中 advantage scale 放大，并确认 mean-only 能阻止 collapse；同时报告 140-game 或更大验证集。

## 待追踪问题

- [ ] group size 从 4 增大到 8/16 后，λ-invariance 是否仍主导？
- [ ] critic PPO、Dr. GRPO、GDPO 等 normalizer 在同一任务上是否有不同 failure boundary？
- [ ] disjoint-vocabulary shuffled-gold placebo 是否仍保留 +20pt？
- [ ] progress-style Δacc 在学习后期是否真的让 variance pressure 衰减？

## 原文定位

- 现象与配置：pp. 1–5，Abstract、Figure 1、Table 1、Section 3。
- Proposition 1/2：pp. 5–6，Eq. (1)–(4)、Sections 4.3–4.4。
- 单因素 rescue 与 decoupling：pp. 7–8，Figure 2–3、Section 5。
- coverage/能力拆分：pp. 8–9，Figure 4、Section 6。
- channel matrix 与实践建议：pp. 9–11，Table 2、Figures 5–6、Sections 7–9。
