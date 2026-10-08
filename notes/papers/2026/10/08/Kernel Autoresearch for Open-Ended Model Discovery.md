---
type: paper
title: "Kernel Autoresearch for Open-Ended Model Discovery"
aliases: [Kernaut]
authors: ["Richard Cornelius Suwandi", "Feng Yin", "Kevin Murphy"]
year: 2026
venue: arXiv
paper_date: "2026-10-07"
date_added: "2026-10-08"
last_read: "2026-10-08"
topics: ["Agent", "科学智能", "Benchmark 与评估方法"]
status: read
priority: 1
rating:
arxiv_id: "2610.10394"
arxiv_version: v1
doi: "10.48550/arXiv.2610.10394"
paper_url: "https://arxiv.org/abs/2610.10394"
code_url: "https://github.com/richardcsuwandi/kernaut"
pdf_path: "library/raw/2026/10/08/2610.10394v1.pdf"
text_path: "library/text/2026/10/08/2610.10394v1.txt"
sha256: "53115eeec9e2e2da648d07d3518c95b5e6e60efa9b4068e76919c24e494b3bba"
pages: 61
citation_key: ""
related:
  - "[[notes/topics/Agent能力形成与过程验证]]"
  - "[[notes/papers/2026/09/29/OpenAI4S- Code as Action, Science as Sessions]]"
cssclasses: [paper-note]
---

# Kernel Autoresearch for Open-Ended Model Discovery

## 一句话结论

Kernaut 让 LLM Agent 在受约束的程序空间中提出高斯过程核函数，用可信后端保留正半定结构、执行评估并冻结结构做独立测试；特定小数据任务上有效，但附录显示代表性核 DWF 依赖任务的对称先验，远未成为普遍优于标准核的发现。

**我的判断**：四篇中最值得先做低成本复核的一篇。真正可复用的是“可检验提案接口 + 保持数学性质的组装 + 留出评估”，而不是把任意模型生成代码称为自动科学发现。

> 阅读范围：arXiv 2610.10394v1，PDF 61 页，正文与附录 A–H，重点核对验证压力测试、搜索消融、DWF 外部分布与公式。页码为 PDF 页序。已归档 PDF/文本；确认官方公开仓库和 README 离线演示入口，但未静态审计全部代码、未运行实验。

## 研究对象和边界

这里的 kernel 是高斯过程的协方差函数 $k(x,y)$，不是 GPU/CUDA kernel，也不是训练大语言模型。任务是从少量观测建立可迁移的结构先验；搜索空间允许新特征、输入变换和频谱结构，超过固定核库的加法/乘法组合（§1–3，pp.1–5）。

Agent 提案进入 archive，经过验证与参数拟合，获得数值反馈后再提出修改或新方向。MAP-Elites 风格保留多个结构/复杂度位置上的候选，而非只保留单一最高分。算法 1（p.4）描述迭代，算法 3（p.17）描述冻结、验证集选择与最终测试。

## 数学约束怎样进入程序接口

| 合约 | 可信后端的组装方式 | 正半定性的来源 |
| --- | --- | --- |
| feature | $k(x,y)=\phi(x)^T\phi(y)$ | 特征内积 |
| spectral | 非负权重的 cosine 频谱和，权重由平方参数产生 | 非负谱测度 |
| pullback | $k_0(T(x),T(y))$ | 已知 PSD 核经确定性输入变换 |
| closure | 和、乘积、非负缩放 | PSD 闭包性质 |

LLM 提出组件，可信解释器组装最终核。命题 1（p.3）要求组件有限、形状正确，并且是只依赖输入和参数的纯函数。**这是条件性保证**；静态检查和有限测试不能证明任意程序没有隐藏状态或批次依赖。

验证分三级：T0 检查执行/形状；T1 检查有限随机 Gram 矩阵 PSD；T2 加入结构合约和一致性测试。仅 T2 候选进入 archive。置换、子集、扩展、重复输入和确定性检查用于发现“样本矩阵过关，但并不是同一个函数”的漏洞（附录 A，表 3，p.19）。执行限制包括约 20 秒 wall time、15 秒 CPU、1GB 内存；这些是资源限制，不应据此声称完成了任意第三方代码的安全证明。

作者要求提案给出 PSD 论证和可证伪预测。这些文字是研究假设；接受证据来自 verifier 与数值实验，不能把提案里的自我解释当成结果。

## 搜索与评估协议

每个主要 BBO/时间序列 campaign 约 12 次提案预算，化学任务 8 次；候选含参数时由后端 Halton 搜索拟合（初始值加 63 个点）。一个模型组合使用 GLM5.2/DeepSeekV4Pro/Qwen3.8Max 的 bandit，另一路固定 GPT-6 Astra（附录 A，pp.14–17）。

Gram fingerprint 在有限 probes 上近似比较结构；novelty 阈值是软惩罚，不是数学新颖性的证明。14 个 BBO campaign 的 160 个提案中只有 4 个受到非零惩罚，也没有完全隔离 novelty 单项收益（p.17）。

搜索后冻结**程序结构**，用独立 validation 选择候选，最后测试；GP 的幅度/噪声等仍可在具体 episode 内拟合。因此“冻结”不意味着不再拟合任何参数。命题 3 的有限候选泛化界要求有界 CRPS，而实际评估没有按该界裁剪损失；它不是分布外迁移的证书（算法 3，p.17；命题 3，p.20）。

## 哪些结果值得相信

### 有限域内，开放结构搜索有增益

BBO 在五类函数上搜索，六个未见函数族上测试；观测预算 `8+2d`、32 次 query、50 个 validation/60 个 test episode，维数不超过 8（§4.1，pp.6–7）。七个 ensemble campaign 中六个优于 strongest fixed Matérn，平均约 3%；七个 Astra campaign 平均改善 8.3%，标准差 2.0%。

不要混淆三个结果层级：七次 campaign 的平均、一个代表性核 DWF、另行做的 12-seed 消融。代表性 DWF 在图 3（p.7）的 test CRPS 是 0.601，Matérn 为 0.612，仅约 1.8% 改善；这不是 8.3% 的那个统计量。

匹配提案预算的消融结果（附录 B，表 7，p.28；CRPS 越低越好）：

| 搜索系统 | CRPS 均值±标准差 | Regret AUC |
| --- | ---: | ---: |
| Full archive | 0.571±0.031 | 0.681 |
| Independent proposals | 0.617±0.037 | 0.695 |
| Closure-only | 0.618±0.021 | 0.706 |
| CKS | 0.625 | 0.684 |

Full 对 closure/independent 都在 12 个 seed 中赢 11 次。Independent 同时改变反馈、保留和 novelty 等因素，不能把差值全部归因于 archive 一个模块。

### 程序过检查仍会暴露漏洞

验证压力测试针对三批各 40 个候选：初始通过 35/31/37 个，隐藏测试随后否定其中 12/18/8 个，即条件失败率 34.3%/58.1%/21.6%（附录 A.6，pp.21–22，图 7）。隐藏测试扩到维数 1–32、不同批次与输入尺度。

这些比例的分母是**通过初始检查的候选**，不能当作全部 LLM 程序失败率。它们支持的是：抽样 PSD 检查远不如结构合约加批次一致性检查可靠；后者依然存在有限覆盖边界。

### 最重要的反证：DWF 并不普遍占优

附录 B.7（p.30）扩展到 88 个合成函数变体：

| 分布/设置 | DWF 胜出 | CRPS 相对改善中位数 | 含义 |
| --- | ---: | ---: | --- |
| 88 变体，冻结参数 | 44/88 | −0.2% | 总体没有明显优势，p=0.77 |
| 88 变体，重新拟合 | 57/88 | +0.6% | 有小中位收益，但少数严重失败拉低均值至 −11.9% |
| 高反射对称的 20 变体，冻结 | 16/20 | +5.6% | 更符合其归纳偏置 |
| 偏心的 44 变体，冻结 | 15/44 | −3.3% | 先验失配 |
| 真实数据 16 个比较，冻结 | 4/16 | −4.2% | 迁移较弱 |
| 真实数据 16 个比较，重新拟合 | 11/16 | +1.3% | p=0.12，证据不足以宣称普遍优势 |

这比摘要中的平均收益更决定使用范围。DWF 的 warp 和 fold 将特定镜像关系嵌入距离，不能据此推断一般数据都具有这种结构。

预测和优化也要分开：冻结 DWF 在这 88 个变体上的 regret AUC 赢 52 个，中位改善 2.7%、p=0.004；重新拟合的 regret AUC 则未显著区别于 Matérn（p=0.70，附录 B.7）。预测 CRPS 没有优势，不意味着所有目标都无收益。

### 其他领域与成本

酶动力学五个留出机制共 75 个 episode：Astra 选出的 F2 相对 fixed Matérn 降低 CRPS 约 57%，但不同 agent 核的表现不一。血糖任务来自虚拟患者，搜索/验证/测试使用儿童/青少年/成人群组；两次训练 episode 下 nMSE 改善 38–67%，增加到六次时收益降至 0–23%（§4，pp.8–9；图 5）。这些不是临床有效性证据。

作者估计一个 campaign 约 100 次 LLM 调用、30 分钟，单次 verification 约 3 秒；详细 token 用量随模型和任务变化很大（§5，p.9；表 11，p.37）。不应将 30 分钟解释为复现全部实验的预算。

## 可以复核的具体构造

附录 C（pp.31–32）的 DWF 使用逐维变换后套 Matérn-5/2：

\[
w_\lambda(u)=\frac{1-e^{-\lambda u}}{1-e^{-\lambda}},\qquad
a_\nu(u)=\frac{\arcsin(\sin(\pi\nu u))}{\pi}.
\]

每维拼接 $w_\lambda(u)$ 与 $\sin(\zeta) a_\nu(u)$，长度尺度 0.5；冻结参数为 λ=0.215、ν=0.975、ζ=1.433。fold 峰值约 0.513，体现对中心附近的镜像结构偏好。最小实验可在相同观测点、相同 seed 下比较中心对称与偏心函数，检查收益是否跟随对称性。

## 我的判断与未解问题

**作者证据支持**：在受约束的小数据任务分布上，开放程序空间与迭代搜索可以找到有用核；合约检查比单纯抽样 PSD 更强。

**个人推断**：自动研究适合先从有明确数学不变量、廉价失败检查和独立留出数据的领域入手。这里的创新是搜索可解释结构，而非“LLM 可以自主发现普遍科学规律”。

**开放问题**：有限 probe 的 fingerprint 是否掩盖新结构？命名清楚的 benchmark 是否提供语义先验？人类后处理的增益如何与 test exposure 隔离？高维、噪声、纯度漏洞和更强对抗提案如何影响结果？作者在附录 G（pp.53–55）承认小维数、程序纯度和 prompt prior 等限制。

[[notes/papers/2026/09/29/OpenAI4S- Code as Action, Science as Sessions]] 解决计算会话、产物与恢复；Kernaut 补上候选模型的数学合约和独立测量。二者结合是个人系统设想，论文没有直接验证这套组合。

主题综合：[[notes/topics/Agent能力形成与过程验证#2026-10-08 补充：四种反馈及其可信边界]]。

## 后续动作

- [ ] 先跑不调用 API 的 offline demo，确认注册、验证和 archive 工作流；它回放预设回复，不能称作自主发现复现。
- [ ] CPU 比较冻结 DWF 与 Matérn 在中心对称/偏心函数上的 CRPS、条件数和失败率。
- [ ] 固定代码 commit、seed 和预算后，再考虑真正自主搜索；独立保留 test，禁止根据 test 改结构。

详见 [[notes/reproductions/四篇Agent反馈论文的最小验证计划]]；本轮未执行。
