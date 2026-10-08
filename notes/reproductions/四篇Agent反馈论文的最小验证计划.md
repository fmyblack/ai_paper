---
type: reproduction
paper: "[[notes/topics/Agent能力形成与过程验证]]"
status: planned
created: "2026-10-08"
updated: "2026-10-08"
repository: ""
environment: "待锁定；本轮仅研读和方案设计"
hardware: "未分配；优先 CPU，涉及训练或开放模型激活时再评估 GPU"
topics: ["Agent", "科学智能", "机器人", "Benchmark 与评估方法"]
cssclasses: [paper-note]
---

# 四篇 Agent 反馈论文的最小验证计划

## 状态与最小验证目标

**计划，未执行。** 本轮只阅读论文、核对关键图表和仓库入口；没有安装研究依赖、调用实验模型、训练模型或跑模拟器。以下预算是个人拟定上限，不是论文结果。

验证共同问题：反馈是否准确描述实际后果；在同预算下，它是否改善下一步行为，而非只让输出显得更合理？四个实验分别成立，不需要先搭一个大系统。

| 顺序 | 来源 | 最小目标 | 成功标准 | 停止条件 |
| --- | --- | --- | --- | --- |
| 1 | [[notes/papers/2026/10/08/Kernel Autoresearch for Open-Ended Model Discovery\|Kernaut]] | 合约验证与 DWF 结构失配 | 固定程序重放一致；中心对称/偏心的 paired CRPS 与条件数可复查 | 需改用 test 选参数，或无法重放作者固定构造 |
| 2 | [[notes/papers/2026/10/08/ToolRACER- A Robust Agentic Conversation Emulation Resource for Agent Training and Evaluation\|ToolRACER]] | 模拟观察是否符合实际状态 | 60 个固定场景的 schema/状态/可完成性独立核验报告 | 无法获取官方数据/提示词时，只能称方法审计，不能称数据复现 |
| 3 | [[notes/papers/2026/10/08/RobotWorld- Benchmarking Multimodal Agents for Robot Use Across Diverse Tasks and Embodiments\|RobotWorld]] | 历史成功与预算内成功是否一致 | 已发布日志的裁定可确定性复算；参考解证明小任务可解 | 缺失时间/预算日志，或后端在现有硬件不支持 |
| 4 | [[notes/papers/2026/10/08/U-Space- Uncovering When and Why Uncertainty Arises in Language Models\|U-Space]] | 语义方向是否提供 entropy 之外的增益 | 对齐 traces、输出范围、样本池后报告 paired 差值 | 无 logits/hidden states 或模型显存不合适；不以文本 API 仿冒 U-Space |

## 与论文设定的差异

| 项目 | 论文 | 本计划 | 可能影响 |
| --- | --- | --- | --- |
| Kernaut 搜索 | 多模型、多个 campaign、多个领域 | 先固定 DWF/Matérn 与 offline demo | 只能验证构造和部分迁移规律，不能验证自主发现能力 |
| ToolRACER 训练 | 千条多领域合成对话、4B/32B SFT | 先 60 个确定性场景审计 | 不能推断训练收益；SFT 是后续独立阶段 |
| RobotWorld | 84 任务×5 模型，每对一条 episode | 日志审计，然后两任务各至少 10 个配对 seed | 任务更少；重复更多；不复现总体排名 |
| U-Space | 三个大 reasoning model×四数据集 | 优先缓存激活/单 checkpoint | 限定模型与数据范围；不复现全部 transfer/steering |

## 环境与记录要求

- **代码 commit / 依赖锁文件**：待获取和锁定，不用浮动 main 作为复现身份。
- **硬件**：待记录 CPU/GPU、内存、dtype；大模型激活和机器人依赖先估算资源。
- **seed**：建议 paired 0–19（CPU核比较）；若重跑原始实验另用作者 seed。
- **输入身份**：场景、函数参数、任务初始状态、模型 checkpoint、anchors、数据子集分别 hash。
- **预算**：先记录调用/动作/生成 token 上限，再运行；API retry 单独计数。
- **输出**：不可变候选版本、原始日志、失败原因、第一次成功、预算边界、独立 test 结果。

## 实验 1：Kernaut 的固定构造与分布失配

**假设**：DWF 的优势随近中心对称程度变化，而非普遍超越 Matérn。依据附录 B.7（p.30）与附录 C（pp.31–34）。

1. 从官方仓库确认并固定 commit，先检查 offline 示例；它回放预设模型回复。
2. 使用论文冻结 λ/ν/ζ 和 ℓ；不根据 test 调参。对中心对称、平移偏心和无对称函数，用相同点与随机数比较 DWF/Matérn。
3. 初步 20 seed×3 类函数，CPU wall-time 上限 30 分钟；先 prediction，BBO 多轮另计预算。
4. 报告每类 CRPS/NLL、Gram 最小特征值、条件数、Cholesky 失败率、paired 中位数及重采样区间。

作者 README 的入口（**未执行**）：

```sh
kernaut task-run --task sine --config examples/extension/offline.toml \
  --baseline linear-demo --archive runs/demo/archive.sqlite
```

此命令验证接口和回放，不能证明 Agent 自主发现。真正搜索阶段应独立锁定 API 预算、训练/验证/test，且禁止按 test 回馈修改结构。

## 实验 2：ToolRACER 的环境真实性

**假设**：语义上可信的模拟工具结果仍可能违反确定性状态；把状态检查接入生成后能改善数据有效性，但训练收益需要另外测量。

构造 30 个目标/约束变化、30 个不可完成请求；工具后端保存真实可用性、余额/预约/库存等状态。分别核查 schema、参数、状态变化、可完成性和 assistant 的拒绝理由。保留 judge 接受但状态错误、judge 拒绝但可行两类，不只分析幸存样本。

初步最多 120 条生成轨迹，token 上限及模型待定。进入 SFT 前匹配 assistant 训练 token、步数和 seed；Happy-only 与加入 Unhappy/Impossible 两组同时测任务成功、过程准确、误拒绝、额外动作与成本。不能用 teacher-forced 域内分数代替 live rollout。

## 实验 3：RobotWorld 的预算审计

**假设**：raw Boolean、历史成功与预算内成功是三项不同数据，混用会改变评估。

先用作者公开轨迹复核附录 H 的任务 82 等样例，重建 `step→动作/非动作→剩余预算→checker→首次成功`。缺字段时明确“不可复算”，不补造状态。

若后端可用，再选两个已有可行参考解的任务，统一预算，配对重复至少 10 seed，比较当前观察与完整历史。单 run 最长 60 分钟；先两条 pilot 确认成本，再决定是否扩大。保留物理暂停和原生控制器配置，不声称测了实时部署。

## 实验 4：U-Space 的同范围基线

**假设**：几何方向有 entropy 之外的增量信息，但效果可能依赖模型、输出范围和样本筛选。

先找可共享缓存；否则评估模型资源后再生成。对同一批样本、同一 thinking span 比较平均 entropy、Acone 与乘积；冻结 anchors/层/Jacobian，再看 test。复现数据抽样和生成 seed 时遵循作者设定。

加入四个诊断：十长度 bin 与更细 matched-length；截断计错误/单列；随机 anchors/方向；保留题意但改变犹豫措辞。用独立 calibration 与 test 集报告 AUROC/AURC、固定 coverage 的错误率、跨域阈值和额外前向/反向成本。

先 100 条缓存 traces 检查计算链，再扩样本；这是工程 smoke test，不足以验证论文显著性。没有模型内部访问时停止这项，不以输出文本的“自信词”替代方法。

## 运行记录与结果

| 实验 | 实际命令/版本 | 实际预算 | 结果 |
| --- | --- | --- | --- |
| Kernaut | 未运行 | 未使用 | 待验证 |
| ToolRACER | 未运行 | 未使用 | 待验证 |
| RobotWorld | 未运行 | 未使用 | 待验证 |
| U-Space | 未运行 | 未使用 | 待验证 |

## 待办

- [ ] 固定 Kernaut commit 与测试函数，再执行最小 CPU 验证。
- [ ] 确认 ToolRACER 官方数据可用性和语义 judge 配置。
- [ ] 检查 RobotWorld 轨迹是否公开且包含预算重建所需字段。
- [ ] 确认 U-Space 缓存激活/Jacobian 产物与模型资源需求。
