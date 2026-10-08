---
type: paper
title: "U-Space: Uncovering When and Why Uncertainty Arises in Language Models"
aliases: [U-Space]
authors: ["Tobias Braun", "Nils Loose", "Alexander Herzog", "Virginia Ceccatelli", "Marcus Rohrbach", "Thomas Eisenbarth", "Lorenzo Cavallaro"]
year: 2026
venue: arXiv
paper_date: "2026-10-06"
date_added: "2026-10-08"
last_read: "2026-10-08"
topics: ["大语言模型", "可解释性", "Benchmark 与评估方法", "安全、鲁棒性与治理"]
status: read
priority: 2
rating:
arxiv_id: "2610.09087"
arxiv_version: v1
doi: "10.48550/arXiv.2610.09087"
paper_url: "https://arxiv.org/abs/2610.09087"
html_url: "https://arxiv.org/html/2610.09087v1"
code_url: "https://github.com/s2labres/U-Space"
source_format: html
archive_status: incomplete
pdf_path: ""
text_path: ""
sha256: ""
pages:
citation_key: ""
related:
  - "[[notes/topics/Agent能力形成与过程验证]]"
cssclasses: [paper-note]
---

# U-Space: Uncovering When and Why Uncertainty Arises in Language Models

## 一句话结论

U-Space 从隐藏状态构造四类不确定性的语义方向，再结合推理 token 的预测熵识别错误答案；控制输出长度后优于所比较的基线，但它不是校准的错误概率，也没有证明四个方向完整代表模型真正“知道自己不知道”。

**我的判断**：值得研究的内部诊断工具，尤其适合做选择性预测和触发外部验证。实际使用前必须核查同一 token 范围的 entropy 基线、截断样本与跨模型重建成本。

> 阅读范围：[arXiv 2610.09087v1 官方 HTML 全文](https://arxiv.org/html/2610.09087v1)，正文及附录 A–H；按章节、公式、表/图定位。本轮 PDF 下载权限被拒绝，未再次尝试；没有本地原始 PDF/全文归档，frontmatter 留空并标为 incomplete。已核对公式的 MathML 与表格，确认官方仓库公开；未提取模型激活、未复现指标。

## 问题与四类方向

作者希望在不使用任务正确性标签、也不更新模型权重的情况下，从一次生成发现不确定性及其来源。四类人为选择的 lexical anchors 对应 ambiguity、incompleteness、conflicting evidence、general uncertainty（§3.1）。这是语义分类方案，不是已被独立标注验证的完备认知分类。

方法借助 J-lens 的平均 Jacobian，把 vocabulary anchors 映射回某层 residual space。每类分别平均 uncertain/certain anchors，做归一化差方向 $b_c$；令 $B=[b_1,\ldots,b_4]$，再正交化：

\[
U=B(B^TB)^{-1/2}.
\]

该基与模型 checkpoint、层和 J-lens 预计算有关，不能默认跨模型共用。任务无需训练标签不意味着部署无需模型内部访问。

## 分数到底怎么算

§3.1–3.2、式 1–5：把推理 token 的 residual state 归一化后投到四维空间，再作正方向变换：

\[
\alpha_t=U^T\operatorname{norm}(h_t),\quad
s_t=\operatorname{softplus}(\sqrt C\,\operatorname{norm}(\alpha_t)),\quad C=4,
\]

\[
A_{\mathrm{cone}}(h_t)=\|s_t\|_2,\qquad
S(r)=A_{\mathrm{cone}}(h_{\mathrm{eot}})\;\bar H(r),
\quad\bar H(r)=\frac1T\sum_{t=1}^T H(p_t).
\]

这里的 `norm` 是归一化，移除投影幅度，主要保留方向；$\sqrt C$ 乘在归一化向量上后再 softplus。最终分数使用 **推理结束位置的方向读数 × 全段推理平均预测熵**，不是仅凭四维隐藏状态，也不是答案概率。

四类占比的可视化方便说明语义构成，但不能当成四种错误的校准概率。方向上的“犹豫”可能来自表达习惯，熵也可能来自词汇选择；两者与错误相关，不等于能分离 epistemic/aleatoric uncertainty。

## “无需训练”的实际成本

作者不优化探针、不需要任务正确性标签。若没有现成 J-lens artifact，仍要在 100 个 WikiText-103 prompt、长度 128 上做 Jacobian 预计算，包含反向传播（附录 A）。逐次评分也需要 logits 与隐藏状态；通常不能直接用于只返回文本的黑盒 API。

选层为模型深度约三分之二：Gemma4 40/60、Qwen3.5 42/64、Magistral 27/40（附录 A）。选层、anchors、checkpoint 与归一化均应在测试之前冻结。工程成本不能由“无训练”三个字推断为零。

## 实验设计

三个开放 reasoning model（Gemma4 31B、Qwen3.5 27B、Magistral Small 2507），四个各 1,000 题的数据集：MMLU-Pro、OmniMATH、SuperGPQA、TriviaQA；固定 seed 42 抽题，生成 seed 41/42/43。名义规模是 36,000 个回答，实际会排除截断和无法解析的输出（§4；附录 E）。

Gemma/Qwen 的最大生成预算 65,536 token，Magistral 32,768；Qwen 在 OmniMATH 最终留下 926±7/1,000，Magistral 在 TriviaQA 留下 929±4（表 9–10）。困难长样本被排除会影响适用分布，最好把截断作为失败单独评估。

比较对象包括 length、MSP、max entropy、mean NLL、self-certainty、DeepConf 的均值变体、PTrue、TokUR（五次前向）、semantic entropy/SAR（十次采样）以及 supervised FeatureGaps。不是所有方法都具有相同推理成本；也没有覆盖各原方法的全部变体。

**重要协议差异**：单次基线往往在 thinking+answer 上评分，而 U-Space 的平均熵只用 thinking（附录 E）。要证明几何子空间真正有增益，仍需同一 trace span 的 entropy-only 对照。监督方法还使用 256 fit/256 validation 和选层，测试样本池应另做对齐。

## 结果与不能遗漏的反例

AUROC/AUPRC 测错误排序，AURC 测保留样本的 risk-coverage；**它们不是回答准确率增益，也不是概率校准误差**。

表 1：原始汇总 U-Space 为 AUROC 71.1±4.7、AUPRC 45.5、AURC 16.2；±主要反映模型间变动，不应称为跨 seed 置信区间。长度本身的 AUROC 从 68.6 降到长度控制后的 52.4，U-Space 从 71.1 降到 69.3，说明大量基线信号来自长答案更易错。

长度控制是按 token 数分十个 quantile bins，在 bin 内算指标并加权。它减弱混杂，不等于同题同长度的因果控制；bin 内仍有长度变化。

表 2，长度控制后的 AUROC（百分比）：

| 模型 | U-Space | 最强比较基线 | 差值 |
| --- | ---: | ---: | ---: |
| Gemma4 | 68.4 | 66.2 | +2.2 pp |
| Qwen3.5 | 71.0 | 69.1 | +1.9 pp |
| Magistral | 68.3 | 63.6 | +4.7 pp |

U-Space 在三模型×三指标的九个长度控制汇总栏领先。**不能推广成所有原始设置都第一**：附录 F.3 表 12，Gemma 的原始 AUROC 为 TokUR 75.1 > U-Space 73.2；Magistral 为 Acone 68.5 > 完整 U-Space 65.7。相乘的 entropy 信号在某些模型上会拖累排序。

附录 F.4（表 13–17）展示 supervised probe 的跨数据集下降，但 transfer 实验只有一个生成 seed。U-Space 的无标签固定基提供一种迁移取舍，不保证优于所有域内监督方法，也不意味着跨 checkpoint 无需重建。

## 机理证据的强度

附录 F.1 对 Gemma4 的 24 个简单事实题插入最长约 20k token 的计数内容：Acone 的变化比 sum NLL 小且趋饱和。这测试的是 **Acone**，不是整个乘积 $S$ 的严格长度不变性。

附录 H 的 steering 只测 Qwen3.5、单 seed，干预中后部层或短推理窗口，能改变犹豫表达和方向读数。它支持方向与生成行为相关，但没有充分证明提高事实正确性、概率校准，或独立分离每一类真实不确定性。

**我的推断**：先把它当作“应增加验证资源”的排序信号更合适。若用来拒答或决定是否执行动作，还需独立 calibration set、错误代价和风险阈值；论文未验证这种 Agent 集成。

## 开放问题与连接

- anchors 更换、随机方向、语言和措辞变化后是否保持优势？
- 同一 thinking span 的 entropy-only 能解释多少提升？
- 截断/未解析全部计入失败时，性能是否稳定？
- 分数是否识别真正知识缺失，还是识别模型更常表达的犹豫？
- 错误率随阈值变化能否跨任务校准，部署域变化时是否需重新设阈值？

与 Kernaut/RobotWorld 连接：不确定性读数可用于分配额外检查，但不能取代核函数合约或环境状态验证。与 ToolRACER 连接：高风险状态是否应追问、停止或重试，需要操作后果和可完成性标签，而非仅凭低置信度。

主题综合：[[notes/topics/Agent能力形成与过程验证#2026-10-08 补充：四种反馈及其可信边界]]。

## 最小后续验证

- [ ] 优先使用可共享的缓存 logits/hidden states，比较同 trace span 的 entropy、Acone 和乘积。
- [ ] 加入 matched length、截断计失败、随机 anchors 与词汇犹豫干预。
- [ ] 独立留出校准/测试集，报告 AUROC、AURC、固定 coverage 的错误率与额外计算成本。

本轮只完成阅读，没有申请或占用 GPU；详见 [[notes/reproductions/四篇Agent反馈论文的最小验证计划]]。
