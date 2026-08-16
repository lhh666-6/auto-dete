# Auto-Decte 论文投稿状态（2026-08 更新，Candidate-Fact Separation 定位）

## 论文定位（已收敛）

> **Trust-Constrained Human-in-the-Loop Document Intelligence via Candidate-Fact Separation**
> —— 一篇「可验证的数据可信约束方法」论文，不是工业系统 demo。

- 核心贡献：**`m ↛ F` 数据模型不变量**（机器输出只能进 candidate/reference，只有人确认才写 fact）+ **selective abstention**（coverage-risk 曲线）。
- 交叉方向：数据挖掘 / 可信 AI / 文档智能 / 人机协同 / 数据质量。
- 稿件：`lncs/main.tex`（Springer LNCS/LNAI，9 页、0 错误、可 freeze）。
- 代码：`github.com/lhh666-6/auto-decte`，478 passing tests + CI gate，架构与论文一致（23 个失败均为 bamboo 业务边角，非论文风险）。

## 投稿主线（不二选一：会议快线 + 期刊慢线并行）

### 会议路线（更快，9 页版直接投）

| 会议 | 定位 | 说明 |
|---|---|---|
| **PAKDD 2027**（CCF-C 会议，数据挖掘/知识发现） | Trustworthy Data Mining / Document Intelligence | **快线主投**，CFP 9 月核实；主观命中「中等偏难」 |
| **DASFAA**（CCF-C，数据管理/质量/系统） | Data provenance / quality / trustworthy data management | PAKDD 拒「too much system」时最匹配 |
| **PRICAI**（CCF-C，AI） | Trustworthy AI / HITL / reliability | 第二梯队 |

### 期刊路线（更慢，但要认真准备 journal extension）

| 期刊 | 定位 | 说明 |
|---|---|---|
| **ESWA**（Expert Systems with Applications，Elsevier，SCI + **CCF-C 期刊**） | Industrial intelligent systems / information management / knowledge discovery / data-text mining | **主投期刊**。方向匹配度很高；扩到 12–18 页；无会议注册费、无差旅；选 subscription 出版不交 OA APC |
| **PRL**（Pattern Recognition Letters，Elsevier） | Document processing / text-graphics recognition | 若进一步强化视觉/识别方法才考虑；当前更像「trustworthy intelligent system」而非「新识别算法」 |

### 保底 / 弱化

- **国内 CCF C**（数据库 / AI 应用方向）；**ICDM workshops**（弱于正式 CCF）。

### 不投

- ❌ CV / 纯 NLP / 机器人——创新不在此，reviewer 会问「算法创新在哪」。

## 命中难度（针对本篇的主观判断，非官方录用率）

**ESWA（中等）< PAKDD（中等偏难）≈ KBS（中等偏难）< IPM（偏难）< PRL（偏难）**

原因：ESWA 更接受「方法 + intelligent system + application + evaluation」的组合，正是本文类型；纯算法期刊反而会追问「OCR 算法创新在哪」。

> ⚠️ 但 ESWA **不是水刊**。reviewer 最可能攻击的点：**「candidate-fact isolation 到底是不是研究贡献，而不是软件权限设计？」**——这是期刊稿最需要补强的地方（见下方「期刊扩展要补什么」）。

## 费用对比（关键）

| | PAKDD | ESWA |
|---|---|---|
| 论文匹配度 | 高 | 很高 |
| CCF | **CCF-C 会议** | **CCF-C 期刊**（SCI）|
| 线下参会 | 有明确要求/风险 | 无会议参会问题 |
| 注册费 | 每篇 accepted paper 单独注册；2026 参考：学生 HKD 5,460 早鸟 / 5,850 普通 / 6,240 晚 | 无会议注册费 |
| OA APC | 不适用（会议）| 选 subscription 出版不交 APC；选 OA 才交（Elsevier 约 USD 200–11,400，会调价）|
| 交通住宿 | 可能很高 | 无会议差旅 |

> 投稿免费；只有录用后按「每篇」交注册费/APC。同会多篇录用通常「1 全价 + (N−1) 额外篇折扣」，跨会议/期刊分别注册。
> 湖南大学是否覆盖 Elsevier Read & Publish 机构协议（可免 APC）**未确认**，投稿前核实。
> ⚠️ **CCF-C「会议」与 CCF-C「期刊」是两套目录**，湖大保研对二者的权重可能不同——这是 ESWA vs PAKDD 取舍的最终裁判，开学问教务。

## 期刊扩展要补什么（ESWA 的关键动作）

现在 9 页版**不能原样投 ESWA**。扩成期刊稿时，围绕「这到底是不是 research contribution」补：

1. **formal guarantee**：把 `m ↛ F` 从「架构不变量」提升成有定义、有命题/不变量声明的形式化表述（哪怕是轻量形式化），并给出 fault-injection 验证；
2. **selective prediction / uncertainty**：把 coverage-risk 曲线 + 与 Chow/Geifman/conformal 的关系写深（这正好是「方向 2 算法论文」的种子）；
3. **controlled experiments 的边界写清楚**：synthetic benchmark 的假设、度量定义、与真实分布的差距（已有 §8/§9 底子，扩写即可）。

## 路由逻辑

1. **快线**：PAKDD（9 页版）——中则解决注册/差旅/作者参会。
2. **慢线**：并行准备 ESWA journal extension（12–18 页）——PAKDD 拒或想双保险时投。
3. **分流**：PAKDD 拒「engineering/system」→ DASFAA；「lack theory」→ 补 formal guarantee 回 PAKDD/PRICAI 或投 ESWA；纯视觉质疑 → 不动（本就非算法论文）。
4. **保底**：国内 CCF C / 数据库应用会议。

## 可拆分方向（对保研更有利）

- **方向 1（系统论文）**：本篇 → PAKDD / DASFAA / ESWA。
- **方向 2（算法论文）**：抽「Selective Recognition + Conformal Calibration」，强化 uncertainty/calibration/abstention → AAAI workshop / CCF AI 会议 / PRL。
- 目标组合：**CCF-C 录用（会议或期刊）+ 开源代码 + 大创/项目负责人**。

## 待办

1. 9 月核实 **PAKDD 2027** 确切截稿 + 主办方 + 注册费；
2. 开学问教务：**CCF-C 会议 vs CCF-C 期刊的保研权重**（决定 ESWA 还是 PAKDD 更值钱）+ SCI 分区口径 + 科研奖励/创新学分；
3. 决定是否补**真实 case study**（50~200 张脱敏表单，只报统计）；
4. 若走 ESWA：核实学校 Read & Publish 协议是否覆盖 APC；并按「期刊扩展要补什么」扩稿；
5. 投稿前把 `\author` 匿名块换成真实作者（一作：你）；队友知情同意；
6. 若 PAKDD 拒，按分流转 DASFAA / ESWA / PRICAI，不降级到普通会议。

## 成本备忘（投稿季执行）

- 会议：学生价 + CAA/IEEE 学生会员折扣；
- 期刊：ESWA 选 subscription 出版可避免 OA APC，但需确认学校/导师无 OA 强制；
- 线上参会或就近。
