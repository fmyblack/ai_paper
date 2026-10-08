---
type: paper
title: "RobotWorld: Benchmarking Multimodal Agents for Robot Use Across Diverse Tasks and Embodiments"
aliases: [RobotWorld]
authors: ["Zhiqin Yang", "Chenxin Li", "Xiaomeng Hu", "Yibin Liu", "Weidong Huang", "Jiankai Sun", "Haitao Li", "Zijian Wu", "Yuzhi Huang", "Fanding Huang", "Hanwen Sun", "Jiashun Liu", "Jingqi Tong", "Mingxin Huang", "Shaoli Hu", "Shijue Huang", "Tianyi Bai", "Xinyuan Wang", "Yunlong Lin", "Zhengyang Tang", "Zhexin Zhang", "Zhuo Chen", "Xierui Song", "Juntao Dai", "Boyuan Chen", "Jiaming Ji", "Fangneng Zhan", "Mengkang Hu", "Wei Xue", "Yonggang Zhang", "Han Hu", "Tsung-Yi Ho", "Yike Guo"]
year: 2026
venue: arXiv
paper_date: "2026-10-07"
date_added: "2026-10-08"
last_read: "2026-10-08"
topics: ["Agent", "机器人", "多模态模型", "Benchmark 与评估方法"]
status: read
priority: 2
rating:
arxiv_id: "2610.10409"
arxiv_version: v1
doi: "10.48550/arXiv.2610.10409"
paper_url: "https://arxiv.org/abs/2610.10409"
code_url: "https://github.com/robotworldai/robotworld"
pdf_path: "library/raw/2026/10/08/2610.10409v1.pdf"
text_path: "library/text/2026/10/08/2610.10409v1.txt"
sha256: "7a6a53e4d7f62bcfaa4b57342fd6b3919134e648bd8e5a7dd1b563edb8bb42c6"
pages: 62
citation_key: ""
related:
  - "[[notes/topics/Agent能力形成与过程验证]]"
cssclasses: [paper-note]
---

# RobotWorld: Benchmarking Multimodal Agents for Robot Use Across Diverse Tasks and Embodiments

## 一句话结论

RobotWorld 用 84 个跨机器人形态的模拟任务检查通用多模态 Agent 是否真的改变了环境；最强单模型仅成功 16/84。但它测的是暂停物理、带原生控制器辅助、固定预算下的工具使用，不能直接代表真实机器人的实时自主控制能力。

**我的判断**：这是一篇评测和失败诊断论文，值得学的是任务合约、状态检查与预算审计；不是训练出新机器人 policy 的论文。单次 episode 的三任务差距也不足以证明稳定的模型排名。

> 阅读范围：arXiv 2610.10409v1，PDF 62 页，正文及附录，重点核对任务接口、表 3、资源统计和附录 H 的 21 条裁定记录。页码为 PDF 页序。PDF/文本已归档；确认官方仓库公开，未运行模拟器、未复现模型排名。

## 到底让 Agent 做什么

任务合约 $T_i=(E_i,\rho_i,g_i,O_i,A_i,C_i,B_i,V_i)$ 明确环境、初始状态、目标、可见观察、动作、控制器辅助、预算与验证器（§3，pp.5–7）。20 个源项目整理成 84 个任务：38 操作、20 移动操作、11 运动、11 驾驶、4 飞行。领域大小不均，overall 等权任务平均会更多受操作类影响。

Agent 看允许的摄像头和机器人状态，能用 shell/图像处理分析信息，然后发出受限机器人动作。主要评测关闭可选的 generated-code control 路径；模型参数不更新（§3–4，pp.5–12）。

两个容易被忽略的条件：

1. **推理和离线计算期间，物理模拟暂停。** 长时间思考不会导致环境继续变化，不测真实系统的延迟代价。
2. **有原生控制器帮助执行动作。** 成功不能完全归因于语言模型的底层运动控制；不同任务的辅助程度也不一致。

上下文包含当前观察，加上最多四个过去观察、每两轮采样一次，而非全部历史（§5.1，p.13）。失败可能来自状态估计、记忆和计划，也可能来自接口/控制器，不能由一条 trajectory 直接确定原因。

## 成功证据在哪里

验证器读取隔离的环境状态，agent 不可查看隐藏 checker 和评审摄像头。目标包括位姿、物体状态、接触/释放/速度、持续保持、事件顺序、路径和安全条件（§4，图 7，pp.10–12）。

**手臂到达目标位姿不等于物体完成目标；某帧看起来成功不等于满足持续时间。** 这种区分比“模型说完成了”更接近具身任务的真实结果。

作者用 fixtures 检查成功/失败条件，但没有为全部任务提供完备的合法参考解。因此“所有模型失败”的任务不一定已被证明在该接口和预算下可解（§4，p.12；§7，p.26）。

## 评测协议对结果的影响

2026-09-30 至 10-06 收集五个模型，每模型每任务 **一条 episode**，共 420 条（§5，pp.13–14）。API retry 不计预算；83 个任务有最多 15 次连续非动作调用，总非动作调用分档为 30/60/120，排球任务另有 20/150。总预算分档参考 Astra 的交互记录校准，不能说完全独立于被比较模型（p.13 脚注）。

论文对部分历史运行按预算边界重新裁定：成功率以规定预算内状态为准，但资源统计使用完整历史运行（§5–6，pp.13、16–17；附录 B/D/H）。因此不能用表中总费用直接除以重新裁定后的成功数，称为相同预算的成功成本。

## 主要实验与失败例子

表 3（p.14）：

| 模型 | 成功任务/84 | 成功率 |
| --- | ---: | ---: |
| GPT-6 Astra | 16 | 19.0% |
| Claude Opus 5.5 | 13 | 15.5% |
| Kimi K3 | 2 | 2.4% |
| DeepSeek V4.1 Flash | 1 | 1.2% |
| Gemini 3.8 Flash | 1 | 1.2% |

Astra 在操作/移动操作/运动/驾驶/飞行分别成功 9/38、4/20、0/11、2/11、1/4；Opus 为 7/38、0/20、1/11、2/11、3/4。优势随领域变化。全部模型成功任务并集为 21/84，但这是事后 oracle union，**不是已实现路由器的 25% 成功率**。

图 12–15（pp.19–22）的轨迹显示：

- 充电任务中，Astra 在第 196 步被目标检测拒绝后调整位置，第 323 步成功；反馈能驱动纠错。
- Kimi 倒液体时瓶子倾倒，后续手臂位姿到达仍不能构成任务成功；动作命令完成与环境目标完成分离。
- Astra 的某次恢复太晚，错过固定时间窗；能补救不等于按时完成。
- 无人机任务中，Opus 维持有效触球序列，Astra 很快失败；单一总体排名掩盖任务结构差异。

§6.6（pp.24–25）按空间推理、接触与平衡要求分组。这些要求重叠、每任务只一条运行，分组是描述性证据，不能直接建立模型视觉或编码能力导致成败的因果关系。

## 预算裁定是核心证据，不是细节

附录 H（pp.59–62）包含 21 条裁定记录：15 条 Opus、6 条 Kimi。其中九条原始 Boolean 缺失，裁为失败；十二条保留历史 Boolean，同时按边界重新计分，包含三条历史成功被改为预算内失败。

例如 Opus 的任务 82：历史第 601 步 native success，但到第 313 步已经用完 30 次总非动作预算，所以 benchmark 计失败。必须分别保存：

`原始 checker 结果 → 首次成功时间 → 预算消耗 → 预算边界状态 → 最终计分`

它不意味着裁定本身错误，而是说明需要完整日志才能复查排名。读者只看视频或原始 success Boolean 会得到不同结果。

## 时间与费用

中位 episode wall time：Astra 30.9 分钟、Opus 54、Kimi 67.6、DeepSeek 16、Gemini 12.8（图 10–11，pp.16–17）。Astra 完整历史运行估算总费约 $9,912.8、941M token、54.6 小时；Opus 约 $2,916.43、1.63B token、140.3 小时（表 12–14，pp.51–52）。

这些数值受模型定价、缓存、输入输出比例和历史运行口径影响，不是等现金预算的效率对照。较短运行也可能只是早失败。

## 我的判断与开放问题

**作者证据支持**：在当前接口和任务集上，通用多模态 Agent 的稳定物理交互能力仍弱；状态和持续过程检查能发现语言/动作表面成功遗漏的错误。

**个人推断**：训练具身 Agent 时，值得记录目标状态、动作后实际状态、拒绝原因和恢复是否及时；仅用一帧图像或模型自述生成 reward 容易把失败当成功。

**尚未解决**：一条 episode 的方差；任务可解性；控制器辅助的贡献；公开源环境的污染；预算校准对模型的偏好；持续动态环境的推理延迟。模拟环境上的 19% 不能换算成真实机器人成功率。

与 ToolRACER 对照：前者的工具观察多为 LLM 模拟，RobotWorld 则能读取实际模拟状态；但状态检查也有覆盖、时限和审计边界。二者不是同一难度的横向排名。

主题综合：[[notes/topics/Agent能力形成与过程验证#2026-10-08 补充：四种反馈及其可信边界]]。

## 最小后续验证

- [ ] 先审计任务 82 等预算边界样例，复核原始 Boolean、首次成功和预算内得分。
- [ ] 选择两个依赖明确、已有可行参考解的任务，每模型配对重复至少 10 个 seed；统一预算。
- [ ] 比较当前观察与完整历史，记录状态误判、恢复时间、动作数；在报告中明确物理暂停。

以上仅是计划，尚未安装模拟器或发起模型调用。详见 [[notes/reproductions/四篇Agent反馈论文的最小验证计划]]。
