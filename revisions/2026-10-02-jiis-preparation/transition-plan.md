# Auto-Decte：JIIS 转投准备记录

日期：2026-10-02。状态：**JIIS FINAL PREPARATION AUDIT COMPLETE — SCIENCE FROZEN**。原内容完整迁移的基线为 24 页；完成轻量 framing、声明、图件和上传包装清理后的最终主文为 **25 页（含参考文献、表格和图件）**，补充材料为 **14 页**。摘要 207 词，关键词 6 个。实际投稿文件在 `submission-files/`，最终审计在 `reviews/pre-submission-report/2026-10-02-final.md`。未新增实验，未向 JIIS 提交，也未在本轮推送 GitHub。

## 当前研究身份与工作范围

研究问题：AI 辅助信息获取中的机器提案，经人工审核和修正后，如何成为可查询、可追溯的权威数据版本。

核心贡献仍是 correction-aware admission relation 及其条件性的 failure-distinguishability characterization。关系连接 exact persisted candidate、candidate-bound authorization、explicit authorized value、fresh predecessor、complete successor 和 total field-source attribution。AI 是提案产生的场景；不将本研究改写为新的识别模型或专家系统推理算法。

稿件身份固定为 **formal/data-model contribution + executable realization + controlled implementation evidence**。不将其强行定位为大规模实证 systems paper；稿件标签也不能代替对期刊实验要求的实质满足。

统一 framing：Human-reviewed AI-derived updates in intelligent information systems require an admission relation that preserves the exact reviewed candidate, the authorized correction, predecessor freshness, and field-level provenance when the resulting value becomes authoritative state.

目前有真实运行的系统实验，但 workload/input 主要是 constructed，并非已证实的 representative traces from real systems。真实执行、真实输入轨迹与实际生产部署是不同事实；实验次数和 timing 数量不能替代输入来源与代表性的说明。

用户的资源约束：沿用现有实验，控制转投投入，不追加企业部署、招募用户或大规模模型实验。所谓“强 C / B 边缘”是投稿策略判断，不是已由外审证明的等级或录用概率。

## 投稿历史：按证据强度记录

| 期刊 | 时间与状态 | 原因及证据边界 |
| --- | --- | --- |
| ESWA | 用户提供的项目记录：2026-08-20，desk reject | 记录称 intelligent/expert-system 创新不足。本轮未重新读取原始决定信。 |
| JSS | 2026 年 9 月，desk reject | 会话中原始截图明确写 out of scope，要求直接的 Software Engineering 贡献。 |
| DKE | 本会话截图确认于 2026-09-28 00:29 提交；用户现报告已拒稿，编号 DATAK-D-26-02063 | 用户提供的 transfer 邮件说明最近已拒稿；正式 decision letter 尚未取得。拒稿原因未知，不能记录为 scope reject。 |

三次拒稿不能统一解释为方向不匹配，也不能解释为实验或形式化已通过外审。后续定位应直接说明新关系和可区分的历史，避免以“智能系统”标签替代贡献论证。

## 已核对的官方定位与投稿要求

1. CCF 当前数据库/数据挖掘/内容检索目录将 JIIS 列为 C 类。
2. JIIS 的范围覆盖 AI 与数据库技术结合的智能信息系统，包括模型基础、设计、验证与系统实现。其系统论文要求解释实际系统实验，或采用真实系统代表性轨迹的模拟实验。规则没有直接要求企业生产部署。
3. 投稿总页数上限为 25 页，包括参考文献、表格和图件；只接受 LaTeX。
4. Author tools 一节明确指定 Springer 宏包的 `smallcondensed`；迁移采用 `svjour3` 和官方样式文件。上传可编辑源码及编译 PDF，最终投稿源码应扁平化，避免依赖子目录。
5. 摘要 150–250 词，关键词 4–6 个，引用采用方括号数字编号。冻结稿的 201 词摘要和六个关键词在数量上符合要求。
6. 声明需按 Springer 要求和真实使用范围核对；贡献及利益冲突也需在投稿界面填写。图件与 AI 披露不能只沿用 Elsevier 的合规结论。

官方来源（核对日期：2026-10-02）：

- CCF：https://www.ccf.org.cn/Academic_Evaluation/DM_CS/
- JIIS scope：https://link.springer.com/journal/10844/aims-and-scope
- JIIS author guidelines：https://link.springer.com/journal/10844/submission-guidelines
- Springer policies：https://link.springer.com/brands/springer/journal-policies

## 最小转投路线

### 1. 先迁移模板，再确定文字压缩量

在独立 JIIS 版本中迁移现有源码、图表及引用。先正常编译并测量页数，再压缩冗余；DKE 的 32 页和 JIIS 的 25 页采用不同排版，不能直接换算为文字删减比例。保留合理字号、边距与可读图表。

第一轮只迁移模板和参考文献显示格式，不删改正文、表格、形式定义、结果或补充材料。实际页数不超过 25 页时，仅进入 framing 和一致性收口；超限时，再根据差额制定迁移量。调整优先级为完整故障目录、重复网格、次级实现细节、复现/恢复说明及较长的 validity 子项。五类 distinguishability、15 substitutions、165-case agreement、browser boundary 和 cost characterization 始终构成主证据链。

已完成的模板基线为 24 页，因此当前无需为页数迁移证据或压缩正文。下一步只做小幅 framing、图表留白及 Springer 投稿合规收口；不新增实验线。页数下降来自排版和参考文献样式变化，不代表正文词数减少了 25%。

### 2. 只调整首尾叙事与社区接口

- 摘要和引言以 AI-assisted information acquisition 的人工修正与权威状态衔接为应用动机。
- 用一个已有实例贯穿两种区别：机器提案与授权值不同；值与保留上下文相同的候选仍可属于不同授权对象。
- admission relation 是主贡献，五类信息是对同一问题的系统化刻画。
- Related Work 围绕 human review、data repair、provenance 和授权对象的关系整合现有文献，不为增加引用数量扩写背景。
- Discussion 解释该关系怎样支持智能信息系统的可靠数据更新；不增加识别精度、用户效率或真实部署收益等未测量主张。

### 3. 将现有证据按问题组织

| 证据 | 主文任务 | 需要准确保留的内容 |
| --- | --- | --- |
| E1 | 说明 exact instance binding 带来的可区分性 | 495 executions；165 个对应案例 exact/reference 一致；15 个 equal-valued substitutions 分离授权政策。不能把 context policy 宣称为天然错误。 |
| Formal/concrete 与 fault catalogue | 说明关系的形式边界及实现对应 | Proposition 的条件、五类信息、投影定义、35-case 主要结果；完整矩阵与次级验证清单可放 Online Resource。 |
| E2 | 说明审核意图到确认请求的执行边界 | 60 browser cases；九个请求替换被 gate 拒绝；三个 display-only cases 的真实结果。 |
| E3 | 说明实现与查询成本 | 22,400 timing observations；代表性结果、测量边界及完整调用比较的解释。完整 workload grids 与环境参数留补充材料。 |

既有 E1 使用实际 SQLite 机制，E2 使用 Chrome/Playwright 与实际确认函数；这些属于运行系统的证据，但输入和交互是构造的。转稿需明确对应的运行对象、输入来源和应用含义，不将它们描述成用户研究或生产轨迹。历史 AI-origin/agent 证据可用作背景支持，不扩大为新实验。

### 4. 优先删除重复，保留决定命题含义的信息

主文保留 separator、关系、条件性刻画、形式—实现连接、核心 E1/E2/E3 表格以及统一讨论的 trust boundary。完整证明细节、故障用例逐项记录、脚本命令、版本号、历史模型矩阵和完整性能网格归入补充材料，正文留下必要定义、结果及明确指向。

最重要的数字记忆点是 15 和 165。支撑性验证数量只在最相关位置报告，避免引言、流程图、协议、结果和讨论反复出现同一清单。

### 5. 完成收口检查与投稿附件

统一 cid / candidate-instance identity、proposal/authorized value、source transition、complete successor、total sources 的定义与用法；检查所有分母、表格、补充材料引用和冻结仓库链接。确认 Springer's 数字引用、声明、Online Resource 标识、图件来源及源码打包。

产物目标：不超过 25 页的 JIIS 主文 PDF、独立补充 PDF、完整扁平 LaTeX 源码、投稿信、最短且真实的声明，以及一份说明改动位置和科学内容完整性的记录。

## 冻结基线

DKE tag：`dke-submission-2026-09-27`，提交 `57b8e68a3cddda2b2915d86b7f36c5258fb74d34`。

- `main.pdf` SHA-256：`5a6707d630c786431b7d9eddc07cf691a65a7e2705949587b53a5f0d02f5a621`
- `supplement.pdf` SHA-256：`074a8cb4bd7a34fdf32619a1c08e64e47792b0cc9d0eee574cc6e57b6d713aee`

转投文件保存在独立的 `format-baseline/` 下，保留 DKE 冻结论文和投稿包。编译结果及内容完整性核对将记录在 `format-migration-report.md`。本准备记录不上传作为科学补充材料。
