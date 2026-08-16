# Auto-Decte 论文投稿状态（2026-08 更新，Candidate-Fact Separation 定位）

## 论文定位（已收敛）

> **Trust-Constrained Human-in-the-Loop Document Intelligence via Candidate-Fact Separation**
> —— 一篇「可验证的数据可信约束方法」论文，不是工业系统 demo。

- 核心贡献：**`m ↛ F` 数据模型不变量**（机器输出只能进 candidate/reference，只有人确认才写 fact）+ **selective abstention**（coverage-risk 曲线）。
- 交叉方向：数据挖掘 / 可信 AI / 文档智能 / 人机协同 / 数据质量——所以投稿不锁死单一赛道。
- 稿件：`lncs/main.tex`（Springer LNCS/LNAI，9 页、0 错误、可 freeze）。
- 代码：`github.com/lhh666-6/auto-decte`，478 passing tests + CI gate，架构与论文一致（23 个失败均为 bamboo 业务边角，非论文风险）。

## 投稿梯队（按优先级）

### 第一梯队：CCF C

| 会议 | 定位 | 说明 |
|---|---|---|
| **PAKDD 2027**（CCF C，数据挖掘/知识发现） | Trustworthy Data Mining / Document Intelligence | **主目标**。CFP 9 月核实；Accept 主观约 40%，补真实 case study 可到 ~55% |
| **DASFAA**（CCF C，数据管理/质量/系统） | Data provenance / quality / trustworthy data management | **PAKDD 拒「too much system」时的最匹配去处**，反而更吃系统 |
| **PRICAI**（CCF C，AI） | Trustworthy AI / human-in-the-loop / reliability | 第二梯队，方向匹配 |

### 保底 / 弱化

- **国内 CCF C**（数据库方向 / AI 应用方向）：方法 + 系统 + 实验组合有优势。
- **ICDM workshops**：保发表记录，弱于正式 CCF。

### 不投

- ❌ CV（CVPR/ECCV workshop）——创新不是视觉算法，OCR 只是入口；
- ❌ 纯 NLP——LLM 不是核心；
- ❌ 机器人/具身智能——无机器人实验。

## 路由逻辑（Plan A→B→C）

1. **Plan A（冲）**：PAKDD。
2. **Plan B（稳）**：PAKDD 拒后按审稿意见路由——若「engineering/system」→ **DASFAA**；若「lack theory」→ 补 formal guarantee / selective prediction / uncertainty，再投 **PAKDD / PRICAI**。
3. **Plan C（保底）**：国内 CCF C 或数据库应用会议。

## 可拆分方向（对保研更有利）

- **方向 1（系统论文）**：现在这篇 → PAKDD / DASFAA。
- **方向 2（算法论文）**：从中抽「Selective Recognition + Conformal Calibration」，强化 uncertainty/calibration/abstention → AAAI workshop / CCF AI 会议。
- 目标组合：**CCF C 正式录用 + 开源代码 + 大创/项目负责人**。

## 待办

1. 9 月核实 **PAKDD 2027** 确切截稿 + 主办方（CFP 尚未发布）；
2. 决定是否补**真实 case study**（50~200 张脱敏工业表单，只报统计）——这是 40%→55% 的关键杠杆，也是 PAKDD vs DASFAA 取舍的关键输入；
3. 投稿前把 `\author` 匿名块换成真实作者（一作：你，湖南大学信科院）；
4. 队友知情同意；
5. 若 PAKDD 拒，按上面路由逻辑转 DASFAA/PRICAI，不降级到普通会议。

## 成本备忘（投稿季执行）

- 学生价 + CAA/IEEE 学生会员折扣；
- 湖大信科院科研奖励/创新学分认定需开学问教务（CCF C 是否认，决定回血幅度）；
- 线上参会或就近。
