---
type: paper
title: "BrowserForge: Scaling Web Episode via Parallel Browser Sandboxes"
aliases: []
authors: ["Fei Tang", "Huawen Shen", "Zhiqiong Lu", "Zhengxi Lu", "Pengyuan Lyu", "Chengquan Zhang", "Weiming Lu", "Jun Xiao", "Yueting Zhuang", "Yongliang Shen"]
year: 2026
venue: "arXiv"
paper_date: "2026-08-25"
date_added: "2026-08-26"
last_read: "2026-08-26"
topics: ["Agent", "Web Agent", "多模态模型", "浏览器自动化", "数据生成"]
status: read
priority: 2
rating: 4
arxiv_id: "2608.24848"
doi: ""
paper_url: "https://arxiv.org/abs/2608.24848"
code_url: ""
pdf_path: "library/raw/2026/08/26/2608.24848.pdf"
text_path: "library/text/2026/08/26/2608.24848.txt"
sha256: "5f319829e96a96c1217d5b593461dc460f38987aa113b732d01cd8b9292691d1"
pages: 15
citation_key: "tang2026browserforge"
related:
  - "[[notes/topics/Agent能力形成与过程验证]]"
  - "[[notes/topics/Agent外部状态的增长、验证与压缩]]"
cssclasses:
  - paper-note
---

# BrowserForge: Scaling Web Episode via Parallel Browser Sandboxes

## 一句话结论

BrowserForge 的主要贡献不是新的 Web Agent policy，而是把“开放网页覆盖度”变成可扩展的数据变量：Common Crawl URL + 并行浏览器沙箱 + Proposer–Solver + 严格清洗，使 203,238 条轨迹分别来自约 20 万个网站；在固定 Qwen3.5 backbone 和训练预算下，数据源与网站多样性带来稳定提升，但 live benchmark 的主要失败仍是重复点击、回退和滚动，说明数据规模没有解决状态反馈与停止条件。

## 三分钟筛选

- **问题**：纯截图 Web Agent 需要跨大量网站的高质量多步轨迹，但既有数据集通常只覆盖几十到几百个固定网站。
- **新意**：把开放网页本身作为数据分布，用最多 300 个并行浏览器沙箱扩大网站数，再用 Proposer–Solver 和 rule/model 双重验证控制噪声。
- **核心证据**：203,238 条轨迹、每条来自不同网站；Qwen3.5-4B/9B 在 Online-Mind2Web 分别从 25.66%/29.33% 提升到 33.33%/38.00%；固定 backbone 的数据源对照和清洗消融支持因果方向（Table 3–5，Figure 2）。
- **与我的关系**：直接连接 Agent 数据工程、可验证执行和外部状态/轨迹质量，而不是只比较更大的多模态 backbone。
- **决定**：精读；暂不复现全量集，优先复现数据源对照和重复失败分析。

## 问题设定

- **输入、输出与目标**：输入是开放网页 URL、当前截图、页面标题/URL 与合成阶段可用的 accessibility tree；输出是统一低层动作序列。训练后推理只使用截图，a11y tree 不进入 agent inference（§3.1–3.2，Table 1）。
- **现有瓶颈**：固定网站列表导致轨迹数增加但网站分布不扩张；开放网页又包含失效、静态、敏感和 benchmark 泄漏页面。
- **关键假设**：网站覆盖度能近似代表开放 Web 的交互分布；规则过滤和 Qwen3-VL-235B judge 足以把自动执行轨迹过滤成可用监督；统一 chain-of-thought 格式有助于下游模型学习。

## 核心贡献

1. 用 Common Crawl URL sourcing 将网站多样性与轨迹规模解耦于固定 seed list（§3.2）。
2. 用共享 work queue、sandbox pool 和 Proposer–Solver loop 将页面变成可执行任务及验证轨迹（Figure 1，§3.3–3.4）。
3. 发布 203,238 条不同网站轨迹；在动态和静态 Web Agent 基准上验证数据源、规模与清洗的作用（Table 2–6）。

## 方法

### 直觉

“更多轨迹”不等于“更多开放网页能力”。BrowserForge 先扩大 URL 分布，再把每个 URL 变成一次独立的浏览器交互；只有在动作格式合法、完成动作结束且模型 judge 认可任务完成后，轨迹才进入训练集。

### 形式化描述

对每个清洗后的 URL，生成 `(screenshot, URL, title, a11y tree)` 页面状态。Proposer 产生候选任务并选择最可执行者；Solver 在统一动作空间中执行。原始轨迹经规则过滤和模型判定，最终抽样约 200K steps，由 Seed 2.0 Pro 重写成统一 reasoning 格式。推理策略固定为“截图 → 单个动作”，不依赖 a11y tree。

### 关键模块与训练流程

1. **URL sourcing/cleaning**：可达性、页面类型、内容长度、黑名单和 cluster IP 重新验证；随机化屏幕分辨率、user agent 和界面语言（§3.2）。
2. **Sandbox orchestration**：共享 URL 队列、最多 300 个浏览器沙箱、worker pool 和 CDP 隔离；慢页面只阻塞自己的 worker（§3.3）。
3. **Proposer–Solver**：Proposer 分两阶段提出并筛选任务；Solver 使用 plan–act–reflect–verify loop，单步输出规范化坐标动作（§3.4，Table 1）。
4. **Cleaning**：约 30% 原始 interaction steps 存活；合法 `finish` 规则过滤与 Qwen3-VL judge 互补，随后统一 CoT 重写（§3.5）。

### 计算与数据成本

- 规模：203,238 raw trajectories，约 20 万网站；约 600K verified steps，最终抽样 200K steps 训练（§3.5，Table 2）。
- 训练：Qwen3.5-4B/9B，冻结 visual encoder/adapter，只全参数微调 language model；3 epochs，learning rate `1e-5`，最大视觉尺寸 99,999,999 pixels（§4.1）。
- 评估：Online-Mind2Web 300 个 live tasks，以 WebJudge-7B 计 success rate；Multimodal-Mind2Web 以 Pass@1/Pass@4 step accuracy 评估三个 split（§4.1）。
- 未披露：浏览器集群的 GPU/CPU 规模、单轨迹真实采集成本、Proposer/Solver/judge 的 API 总成本和完整数据发布可复现脚本。

## 实验与证据

| 作者主张 | 对应证据 | 定位 | 我的判断 |
| --- | --- | --- | --- |
| BrowserForge 数据提升 end-to-end Web Agent 成功率 | 4B: 25.66%→33.33%；9B: 29.33%→38.00% | Table 3，p.7–8 | 方向清晰，但 Online-Mind2Web 使用 WebJudge-7B 自动判定，不能等同于人工真实完成率。 |
| 提升来自数据源而非训练 recipe | 同 backbone、同 3 epochs、同 200K 样本；BrowserForge 平均 Pass@1 41.33% 对开源轨迹 32.74% | Table 5，§4.3，p.9 | 这是最有价值的控制对照，仍未覆盖不同数据清洗质量和任务难度匹配。 |
| 网站/数据规模具有单调收益 | 0→200K 样本时 Online-Mind2Web 25.66%→33.33%，静态 step accuracy 23.11%→54.36% | Figure 2(a)，§4.3，p.9–10 | 支持规模趋势，但最大点尚未饱和，不能外推无限线性收益。 |
| 清洗各阶段互补 | 无清洗 24.0%，rule-only 27.0%，judge-only 29.0%，无 unified CoT 31.0%，完整 33.3% | Figure 2(b)，§4.4，p.10 | 消融支持“过滤 + 统一监督”组合；组件之间存在数据量和分布变化，不能拆成纯独立因果效应。 |
| 失败主要是状态反馈问题 | click loop 29%、back loop 22%、scroll-only tail 20%，三者合计 71% | Table 6，p.10–11 | 这是对成功率之外的关键诊断：下一步应研究 consequence tracking、stop/abort 和恢复策略。 |

### 数据、基线与指标

- **数据集**：BrowserForge corpus；Online-Mind2Web；Multimodal-Mind2Web。
- **基线**：Qwen3.5-4B/9B zero-shot；Qwen3-VL、GUI-Libra、ScaleCUA、WebStar 等；训练数据源对照使用现有开源 Web trajectories。
- **指标**：Online-Mind2Web success rate；静态 benchmark Pass@1/Pass@4 step accuracy；清洗消融使用 Online-Mind2Web SR。
- **预算/硬件**：报告模型和 epoch，但未给出浏览器集群与数据合成的完整 wall-clock/TCO。
- **消融与稳定性**：数据规模、数据源、rule/judge/CoT 三个清洗组件；跨两种 backbone、三种静态 split，方向一致。

## 批判性阅读

### 证据支持的结论

- 在固定 backbone 和训练轮数下，扩大网站分布并保持验证/清洗，能显著提升纯截图 Web Agent 的 benchmark 表现。
- 规则合法性和语义完成度 judge 互补；只保留“结束动作合法”会把未完成轨迹混入监督。
- 开放网页带来的真实分布多样性是论文最可信的技术变量，超过单纯重复已有网站的轨迹扩增。

### 尚未被充分支持的结论

- “每条轨迹来自不同网站”并不等于每条轨迹提供独立的交互机制；同一模板、CMS 或页面组件可能高度相关。
- WebJudge-7B 的自动评分没有给出人工校准误差，也没有报告不同网站类别上的置信区间。
- 统一 CoT 重写使用强模型生成，可能把 teacher style 或错误 rationale 传播到训练集，且没有比较不重写但保留结构化 action trace 的替代方案。

### 局限、风险与可能反证

- Common Crawl 与网页平台存在语言、地区、版权、隐私和安全偏差；论文只做 benchmark overlap blacklist，未给出全面内容安全审计。
- 登录墙、CAPTCHA、Cloudflare 和动态变化会把环境失败混入 agent 能力失败；作者将 access blocked 归为 9% 失败。
- 训练数据使用 a11y tree 作为 synthesis-time signal，可能造成任务选择和轨迹分布对结构化页面的偏置。
- 30-step 上限和 11% clean termination 说明该模型仍未解决长任务的进度跟踪；更大数据可能只让循环失败更熟练。

## 与已有知识的连接

- **基础论文**：Mind2Web、WebArena、SeeAct、Qwen-VL 系列。
- **相近方法**：Explorer、AgentTrek、OpenWebVoyager；BrowserForge 的差异在于先扩大 website distribution，而非在固定来源上继续采样。
- **后续工作**：[[notes/topics/Agent能力形成与过程验证]]；可与轨迹验证、技能压缩和外部状态维护结合。
- **与主题笔记的关系**：[[notes/topics/Agent外部状态的增长、验证与压缩]]；本论文把浏览器沙箱、任务、轨迹和 judge 结果做成可再利用的外部训练状态。

## 复现计划

- **是否复现**：待定
- **最小验证目标**：在 3–5 个公开网站类别上比较固定 4B backbone 的“固定 seed list 扩增”与“开放 URL 扩增”，保持样本数、训练步数和 judge 规则一致。
- **所需资源**：可重复的 Playwright/CDP sandbox、公开网页快照、一个小型 VLM judge、Qwen3.5-4B 级别 GPU 训练资源。
- **成功标准**：跨两个未见网站 split 的 step accuracy 提升，并且 click/back/scroll loop 比例下降；若只提升成功率而循环失败不变，视为部分复现。

## 待追踪问题

- [ ] 公开完整 BrowserForge corpus、过滤规则、网站类别统计和去重方法了吗？
- [ ] WebJudge-7B 与人工成功率的一致性、不同网站类型的误差是多少？
- [ ] 将统一 CoT 替换为结构化 observation→action→outcome trace，是否能减少错误 rationale 传播？
- [ ] consequence-aware state tracking、失败恢复和动态停止条件能否解决 71% 的重复类失败？

## 原文定位

- Abstract / Introduction：pp. 1–2。
- 方法总览与四模块：Figure 1、§3.1–3.5，pp. 3–6。
- 语料规模与既有数据集比较：Table 2，p. 7。
- 主结果：Table 3–4，§4.2，pp. 7–9。
- 数据源与规模控制：Table 5、Figure 2(a)，§4.3，p. 9。
- 清洗消融与失败分布：Figure 2(b)、Table 6，§4.4–4.5，pp. 10–11。
