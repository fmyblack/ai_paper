---
type: paper
title: "Aero Hand Open: A Simulation-Ready Tendon-Driven Hand for Dexterous Manipulation Learning"
aliases: []
authors: ["Nan Wang", "Mohit Yadav", "Jonathan Wulff", "Aidan Rosenbaum", "Kezhou Chen", "Yuvan Sharma", "Xu Dong", "Yiwei Tao"]
year: 2026
venue: "arXiv"
paper_date: "2026-08-28"
date_added: "2026-08-31"
last_read: "2026-08-31"
topics: ["robotics", "dexterous-manipulation", "sim-to-real", "reinforcement-learning", "open-hardware"]
status: read
priority: 2
rating:
arxiv_id: "2608.28578"
doi: ""
paper_url: "https://arxiv.org/abs/2608.28578"
code_url: "https://github.com/TetherIA/aero-hand-open"
pdf_path: "library/raw/2026/08/31/2608.28578.pdf"
text_path: "library/text/2026/08/31/2608.28578.txt"
sha256: "eae312d3bd0086b0910700275057d0eba73c4140a2fbfe486b59a3a023f08f04"
pages: 20
citation_key: ""
related: []
cssclasses:
  - paper-note
---

# Aero Hand Open: A Simulation-Ready Tendon-Driven Hand for Dexterous Manipulation Learning

## 一句话结论

Aero Hand Open 的真正贡献不是“又一只低成本机械手”，而是把腱传动本身、双向 actuation map 和硬件可用 observation 一起交付，使 PPO 策略能在 MuJoCo 中训练后零样本部署。论文给出很强的传动复现证据（四指 excursion mismatch 0.04–1.40 mm、动态 tracking RMS 0.29–0.45 mm），但拇指仍是明显弱点，真实旋转速率未记录，且 cube 摩擦/质量随机化实际被覆盖为固定值。

## 三分钟筛选

- **问题**：腱驱动手便宜且拟人，但一个电机驱动多个关节、存在摩擦/松弛和耦合，独立关节 actuator 的仿真无法直接迁移。
- **新意**：MuJoCo spatial tendons 复现 pulley routing；由 CAD 推导 joint→cable→motor map，并以仅七个 encoder 信号训练/部署。
- **核心证据**：16 joints/7 motors 的 374 g、$314 机械手；四指动态 RMS 0.29–0.45 mm；sim cube 15 s 转 7.64 rad；真实 hand 无 fine-tuning/no state estimation 约 55 s 转一圈。
- **与我的关系**：连接 sim-to-real、可复现硬件、underactuation、结构化中间层和制造后物理验证。
- **决定**：精读并优先做软件/传动映射复现；真实任务复现需先解决拇指校准与 pose logging。

## 问题设定

- **输入、输出与目标**：输入七路 motor command/encoder；仿真通过七维 cable/joint channel 产生 16 个 joint motion；目标是以硬件可观测量训练 in-hand cube rotation 并直接部署。
- **现有瓶颈**：15 个关节由腱驱动、只有 motor encoder；joint-level state 在真实手不可得；thumb 三路耦合使逆映射不可直接求逆。
- **关键假设**：CAD 路由和有效 winding radius 足以描述 transmission；线性/仿射 map 在工作区有效；域随机化覆盖主要 sim-to-real 差异；任务可由七路低层目标完成。

## 核心贡献

1. 开源可维修的 5-finger hand：16 revolute joints、7 motors、374 g、BOM $314，全结构 3D printed。
2. MuJoCo tendon-level model：20 spatial tendons、wrapping geometries、coupling cables、return springs，路由来自 CAD。
3. 双向 identified actuation map 与只依赖硬件信号的 PPO package；在模拟和真实手上验证 cube rotation。

## 方法

### 直觉

把“电机转多少”与“关节到哪里”之间不可见的腱传动显式化。策略不再假设能读到 16 个 joint angles，而是学习在真实部署同样存在的七个 cable/abduction channel 上闭环。

### 形式化描述

- 四指单 cable 驱动 MCP/PIP/DIP：`d_f = 12.49 q_mcp + 7.32 q_pip + 9.00 q_dip`（mm/rad）。
- 拇指两 cable 与 abduction/CMC/MCP/IP 的耦合：`d_th,cmc = 2.50 q_abd + 12.49 q_cmc`；`d_th,flexor = 2.50 q_abd - 2.50 q_cmc + 9.44 q_mcp + 12.50 q_ip`。
- 六个 cable channel 用 spool radius 9 mm 转成 shaft angle，16-bit command 由各自 `[θmin, θmax]` 仿射归一化；abduction 直接由 joint actuator 控制。
- 四指 forward/inverse map 是 affine；thumb 因 `C∈R^{3×4}` 非可逆，使用 sweep 得到的一阶拟合恢复 cable lengths，再经过 joint-to-actuation model。

### 关键模块与训练流程

- **机械传动**：四指每指一个 actuation cable、一个 PIP–DIP coupling cable、两根 return springs；MCP spring 较软，形成先 MCP 后 distal 的 staged closure。thumb 有 CMC abduction linkage、CMC flexion cable 和 spanning MCP/IP 的 flexor cable。
- **MuJoCo model**：16 hinge joints、20 spatial tendons、7 actuators；显式 wrapping cylinders（半径约 1.7–4.5 mm），排除不需要的内部碰撞，10 ms semi-implicit Euler。
- **接口约束**：observation `o_t=(noisy 7-channel length, a_{t-1})∈R^14`；critic 额外看 81D privileged state，actor 不看 joint state。
- **PPO**：20 Hz policy、100 Hz physics、25 s episodes；MLP `(512,256,128)` swish，`3×10^8` environment steps、8192 parallel envs。
- **Reward**：鼓励 cube z-axis angular velocity，fall penalty −100，动作变化惩罚 −1；其他 pose/torque/energy 项权重为 0。

### 计算与数据成本

训练规模为 3×10^8 steps × 8192 并行环境，论文给出 PPO 超参数但未报告 wall-clock、GPU 型号或总能耗。硬件制造方面，结构件约 13 h 打印，单指约 45 min；7 个舵机占 BOM $208.81。发布内容包括 CAD、firmware、MuJoCo/Menagerie model、ROS 2 deployment node 与分析脚本。

## 实验与证据

| 作者主张 | 对应证据 | 定位 | 我的判断 |
| --- | --- | --- | --- |
| 低成本手仍覆盖广泛 grasp | 5 fingers、16 joints、7 motors、374 g、$314；图 1 展示 GRASP taxonomy 33 类 | pp.1–3, Table 1, Fig.1 | 机械规格与展示支持 capability claim；没有逐类成功率、力/姿态置信区间 |
| tendon-level simulator 忠实复现硬件 | 四 finger cable excursion mismatch 0.04/0.32/1.40/0.41 mm；dynamic RMS 0.29–0.45 mm | pp.12–14, Table 2, Fig.6 | 这是最强证据，且 excursion 由 CAD/硬件独立测量；thumb mismatch 明显更大 |
| map 能连接 sim 与 motor commands | 7-channel affine/fit chain，包含 thumb three-way coupling；双向 kinematic/dynamic validation | §4.1–4.5, Eqs.1–12, Table 2 | 工程接口定义清楚，但线性假设和 first-order thumb compensation 在极端姿态仍可能失真 |
| policy 可 zero-shot transfer | sim 15 s、7.64 rad（0.51 rad/s）；真实手无 fine-tuning/state estimation，约 55 s 一圈 | pp.15–17, §6.1–6.3, Fig.8–9 | 支持“能转起来”；真实速率未记录，且训练/部署 nominal/scales 有调参差异 |
| 域随机化带来 robustness | finger friction、inertia、COM、zero offsets、dry friction、mass、gain、damping 随机化 | p.15, Table 3 | cube friction 与 mass 虽列出但被覆盖为固定值，不能声称对二者鲁棒 |

### 数据、基线与指标

- **数据集**：没有传统数据集；MuJoCo Playground cube task，50 mm、69.2 g cube，随机初始 hand pose/位置/SO(3) orientation。
- **基线**：Table 1 与 InMoov、LEAP、Shadow 等硬件平台比较；学习任务没有独立 policy baseline 或传动模型 ablation。
- **指标**：cable excursion mismatch、settled tracking RMS、10–90% rise time、sim rotation rad/revolution、真实完成一圈时间。
- **预算/硬件**：Bambu X1C（0.4 mm nozzle/0.2 mm layer）；ESP32-S3；7× Feetech HLS3606M（约 0.59 N·m stall torque）；训练 GPU 型号与 wall-clock 未报告。
- **消融与稳定性**：有 open-loop replay 分离 transmission mismatch 与 policy feedback；无多 seed policy 方差、长时磨损后的再校准或不同物体质量/摩擦 sweep。

## 批判性阅读

### 证据支持的结论

- 
- **传动建模确实提升了 sim-to-real 可解释性**：每个误差能定位到 cable excursion、thumb cross-term 或 actuator timing，而不是笼统归因于 domain gap。
- **硬件诚实接口是关键设计**：actor 只看七个 encoder-derived channels，避免 privileged joint state 造成部署时信息缺失。
- **开放硬件降低复现门槛**：CAD、BOM、打印和 firmware 信息足以先复现机械/仿真层，再决定是否训练策略。

### 尚未被充分支持的结论

- 拇指 CMC/flexor 的 excursion mismatch 为 32.7%/31.2%，flexor dynamic residual 0.63 mm，且某耦合 sweep 可达 7.1% full scale；“完整传动复现”应理解为四指强、拇指近似补偿。
- 真实 cube pose 未记录，55 s 一圈是视频/人工观察的时间尺度，不是带 encoder/vision 的速度 benchmark。
- Table 4 中部署对四指 action scale 放大 20–30%、nominal pose 关闭 4–8 mm；因此 zero-shot 是无 fine-tuning policy，但并非完全零校准。
- 论文没有报告抓取成功率、不同物体、连续运行失败率或真实接触力分布；33 grasp types 是可展示范围，不等于每类定量性能。

### 局限、风险与可能反证

- 

## 与已有知识的连接

- **基础论文**：MuJoCo spatial tendon/contact simulation；GRASP taxonomy；PPO/Brax/MuJoCo Playground。
- **相近方法**：LEAP Hand（servo-driven/direct joint interface）、Shadow Dexterous Hand（高成本 tendon hand）、InMoov/Amazing Hand（低成本平台）。
- **后续工作**：记录真实 cube pose/角速度；对 thumb transmission 做 nonlinear calibration；加入物体摩擦/质量随机化和多物体任务；报告 policy seeds 与寿命曲线。
- **与主题笔记的关系**：[[notes/topics/结构化中间层与可验证执行]]：actuation map 是 sim-to-real 的结构化接口；与 InstructMesh 对照“生成/仿真表示必须经过物理证据才能称可用”。

## 复现计划

- **是否复现**：是（先软件，后硬件）
- **最小验证目标**：下载仓库模型，在 MuJoCo 中复现 7-channel actuation map、Table 2 的静态/动态 tracking，再跑短程 cube rotation。
- **所需资源**：公开 GitHub/CAD、MuJoCo/Brax 或 Playground、可选 7-servo hand；硬件阶段需要 ESP32-S3、3D printer、Kevlar/Vectran cable 和 calibrated cube。
- **成功标准**：四指 excursion ≤1.5 mm、tracking RMS 接近 0.3–0.5 mm；仿真 15 s 不掉 cube；真实部署记录 pose 后报告角速度、掉落率与多 seed 方差。

## 待追踪问题

- [ ] 核对 GitHub release 与论文 v1 的模型/firmware 版本是否一致。
- [ ] 复现 thumb map 的 inverse fit，单独测量 abduction→flexion cross-term。
- [ ] 给真实 cube 加视觉/AprilTag pose logging，避免只用“约一圈/55 s”的主观结果。
- [ ] 在不覆盖参数的条件下真正随机化 cube friction/mass，测量 transfer degradation。

## 原文定位

- pp.1–6, §§1–2, Table 1, Fig.1–2：机械规格、腱/弹簧路由、可维修性、耐久与制造。
- pp.6–10, §3–4.2, Fig.3–4, Eqs.1–7：MuJoCo tendons、routing、joint-to-actuation map 与 channel limits。
- pp.10–14, §§4.3–4.5, Eqs.8–12, Table 2, Fig.6：双向映射、静态 excursion 与动态 tracking。
- pp.14–17, §§5–6.3, Tables 3–4, Fig.7–9：PPO、domain randomisation、仿真与 zero-shot cube rotation。
- p.18, §8：项目网站、GitHub、文档入口。
