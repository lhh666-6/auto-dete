# Auto-Decte 论文投稿状态（2026-08 更新，Candidate-Fact Separation 定位）

## 论文定位（已收敛）

> **Trust-Constrained Human-in-the-Loop Document Intelligence via Candidate-Fact Separation**
> —— 一篇「可验证的数据可信约束方法」论文，不是工业系统 demo。

- 核心贡献：**`m ↛ F` 数据模型不变量**（机器输出只能进 candidate/reference，只有人确认才写 fact）+ **selective abstention**（coverage-risk 曲线）。
- 交叉方向：数据挖掘 / 可信 AI / 文档智能 / 人机协同 / 数据质量。
- 稿件：`lncs/main.tex`（Springer LNCS/LNAI，9 页、0 错误、可 freeze）。
- 代码：`github.com/lhh666-6/auto-decte`，478 passing tests + CI gate，架构与论文一致（23 个失败均为 bamboo 业务边角，非论文风险）。

## 投稿梯队（主线 + 期刊备选）

### 第一梯队：CCF C 会议

| 会议 | 定位 | 说明 |
|---|---|---|
| **PAKDD 2027**（CCF C，数据挖掘/知识发现） | Trustworthy Data Mining / Document Intelligence | **主投**。CFP 9 月核实；Accept 主观约 40%，补真实 case study 可到 ~55% |
| **DASFAA**（CCF C，数据管理/质量/系统） | Data provenance / quality / trustworthy data management | PAKDD 拒「too much system」时最匹配 |
| **PRICAI**（CCF C，AI） | Trustworthy AI / HITL / reliability | 第二梯队 |

### 期刊备选（低差旅成本）

| 期刊 | 定位 | 说明 |
|---|---|---|
| **ESWA**（Expert Systems with Applications，Elsevier，SCI） | Intelligent systems / information management / knowledge discovery / data-text mining / production management | **PAKDD 拒稿后的期刊扩展版首选**（扩到 12–18 页）。无会议注册费、无差旅；选 subscription 出版不交 OA APC |
| **PRL**（Pattern Recognition Letters，Elsevier） | Document processing / text-graphics recognition / IR | 若进一步强化视觉/识别方法才考虑；当前更像「trustworthy intelligent system」而非「新识别算法」，故排 ESWA 后 |

### 保底 / 弱化

- **国内 CCF C**（数据库方向 / AI 应用方向）；
- **ICDM workshops**：保发表记录，弱于正式 CCF。

### 不投

- ❌ CV（CVPR/ECCV workshop）——创新不是视觉算法，OCR 只是入口；
- ❌ 纯 NLP——LLM 不是核心；
- ❌ 机器人/具身智能——无机器人实验。

## 费用对比（关键）

| | PAKDD | ESWA |
|---|---|---|
| 论文匹配度 | 高 | 很高 |
| CCF | C | 不按 CCF 会议计，按 SCI/分区认定（看学校）|
| 线下参会 | 有明确要求/风险 | 无会议参会问题 |
| 注册费 | **每篇 accepted paper 单独注册**；PAKDD 2026 参考：学生 HKD 5,460 早鸟 / 5,850 普通 / 6,240 晚（2027 未公布）| 无会议注册费 |
| OA APC | 不适用（会议）| 可选 OA 才交 APC（Elsevier 约 USD 200–11,400 不等，会调价）；**选 subscription 出版不交 OA APC** |
| 交通住宿 | 可能很高 | 无会议差旅 |
| 对保研 | CCF C 直接 | 看学校/学院对 SCI/分区的认定 |

> 投稿（submission）免费；只有录用后按「每篇」交注册费/APC。同一作者多篇同会录用通常「1 全价 + (N−1) 额外篇折扣」，跨会议则分别注册。

> 湖南大学是否覆盖 Elsevier 的 Read & Publish 机构协议（可免 APC）**未确认**，投稿前需向学校核实。

## 路由逻辑（Plan A→B→C）

1. **Plan A（冲）**：PAKDD（9 页版）。
2. **Plan B（稳）**：PAKDD 拒后按审稿意见——
   - 「engineering/system」→ **DASFAA**；
   - 「lack theory」→ 补 formal guarantee / selective prediction / uncertainty，回投 **PAKDD / PRICAI**；
   - 直接转期刊 → 按 reviewer 意见扩成 12–18 页 **ESWA**（subscription 出版、无差旅）。
3. **Plan C（保底）**：国内 CCF C 或数据库应用会议。

## 可拆分方向（对保研更有利）

- **方向 1（系统论文）**：现在这篇 → PAKDD / DASFAA（或 ESWA）。
- **方向 2（算法论文）**：抽「Selective Recognition + Conformal Calibration」，强化 uncertainty/calibration/abstention → AAAI workshop / CCF AI 会议（或 PRL）。
- 目标组合：**CCF C 正式录用 + 开源代码 + 大创/项目负责人**。

## 待办

1. 9 月核实 **PAKDD 2027** 确切截稿 + 主办方 + 注册费（CFP 尚未发布）；
2. 决定是否补**真实 case study**（50~200 张脱敏工业表单，只报统计）——40%→55% 的关键杠杆，也是 PAKDD vs 期刊路线取舍的关键输入；
3. 投稿前把 `\author` 匿名块换成真实作者（一作：你，湖南大学信科院）；
4. 队友知情同意；
5. 若走 ESWA，向学校核实 **Read & Publish 机构协议是否覆盖 APC**、以及学院对 SCI/分区的保研认定口径；
6. 若 PAKDD 拒，按路由逻辑转 DASFAA / ESWA / PRICAI，不降级到普通会议。

## 成本备忘（投稿季执行）

- 会议：学生价 + CAA/IEEE 学生会员折扣；
- 期刊：ESWA 选 subscription 出版可避免 OA APC，但需确认学校/导师无 OA 强制要求；
- 湖大信科院科研奖励/创新学分认定需开学问教务（CCF C 是否认 + SCI 分区口径，决定回血幅度）；
- 线上参会或就近。
