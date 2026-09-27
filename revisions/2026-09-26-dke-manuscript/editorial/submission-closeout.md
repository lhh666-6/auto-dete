# 投稿前局部收口

日期：2026-09-27。基线：`7e65d6a7121c6388ecada94031abc46c0bbc860c`。

本轮保留现有主故事，不增加概念贡献或实验。只调整少量句子，澄清两个已有术语关系，缩短披露，并完成源文件、原始执行记录、引用、公开链接和 PDF 检查。

## 修改及保留

- Introduction、Related Work 和 Discussion 做五处句子级调整；equal-valued substitution 核心句、五类信息桥接、E1 公平区分两种政策、Discussion 正面结果在前的结构均保留。
- Section 5 明确 certificate 固定候选身份和创建时间，与既有实现及 E1 context 排除项一致。另明确完整快照覆盖字段值/来源，完整 trace 检查这些来源的授权链。没有改动形式定义、命题或契约。
- AI 声明从 207 词缩至 60 词，保留实际代码、分析、文献、写作和制图用途。图注仍按已核实政策保留最短说明；Section 7 说明图 2 的可复现生成方法。
- 没有继续删除结果中的验证数字。72 Alloy outcomes、85 regressions、10 harness checks 等已有主叙述位置保留；15 substitutions 与 165 paired agreement 仍是主线记忆点。
- 所有表格/CSV、图文件、科研脚本、参考文献、摘要、作者信息、正式命题/证明/公式、RQ、Results、Conclusion 和补充材料源文件均保留。补充 PDF 也保留原发布字节。

## 一致性核查

`x_c` 始终是原始提案，`x_a` 是显式授权值；Correction 保留前者而将后者提交。`c_id` 为模型身份，具体实现的 candidate identifier 与 certificate identifier 分别指候选及其冻结内容；EID 是证据内容摘要加规范定位信息，不是候选身份。

candidate 是持久化提案实例，reviewed candidate 是审查针对的实例，certificate 固定其内容与上下文。instance authorization 描述政策，exact binding 描述执行该政策的绑定，instance accountability 描述可查询的责任粒度。complete successor、total field sources 和 complete trace 分别描述完整状态、全字段来源覆盖及来源链一致性，没有合并为一个术语。

从公开存档直接读取 495 条 E1 receipts，重新汇总并与既有 CSV、Table 4、Results、Figure 2 的表格输入核对：

| 机制 | 执行 | 接受 | 拒绝 | instance violations | 正确回答 | 歧义回答 |
|---|---:|---:|---:|---:|---:|---:|
| Context journal | 165 | 60 | 105 | 15 | 1,020 | 60 |
| Exact journal | 165 | 45 | 120 | 0 | 810 | 0 |
| Reference | 165 | 45 | 120 | 0 | 810 | 0 |

165 对 exact/reference 的决定与完整 query-answer sets 一致；15 个 same-value substitutions 分开两种政策。60 个歧义答案是 query 分母，不是 substitution 数量。每个接受历史提供 18 个答案。所有执行无 harness error；拒绝均未写入事实数据库。没有重新运行科研实验。

新实验存档、协议、manifest、原始 E1 receipts、固定实现提交、r31 与历史 v8 标签的实际公开目录均返回 HTTP 200。v8 标签早于 `latest/` 布局，其内容在标签根目录的 `artifacts/`、`paper/` 等目录；正文只标识标签，未写错误的 `latest/` 链接。

五篇最近工作核查见 [closest-work-closeout.md](closest-work-closeout.md)。规则核查见 [dke-policy-check.md](dke-policy-check.md)：完整 DKE Guide for Authors 暂不可访问，不能据此宣称全部格式合规。

## 本机编译与版面

使用作者本机 MiKTeX 编译正文与补充材料，最终均无未解析引用、LaTeX warning 或 overfull/underfull box。未改变字号、页边距、图表尺寸或参考文献样式。

正文 33→32 页；PDF 提取词数 8,656→8,509。补充材料保持 21 页、6,086 词。词数是 PDF 提取统计，包含图注、声明和参考文献，不等于仅正文段落的词数。

Scientific claim affected: **No**。机器可读检查、链接状态及 PDF 散列见 [submission-closeout-check.json](submission-closeout-check.json)。此前 `micro-revision*` 仍记录上轮 33 页稿，不作为当前稿的检查报告。
