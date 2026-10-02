# 贡献与创新表达强化及排版修订：最终整合说明

## 排版修订（2026-10-02）

保留期刊 smallcondensed 的默认版心、字体和页边距。三张表的浮动位置参数改为 `[!htbp]`，消除原第 10、12 页的大留白；贡献列表采用同宽不可分页块，缩减列表项目间的冗余间距，C1--C3 连续位于第 2 页。机制比较段落移到列表后，全部文字保持一致。

正文从 25 页降为 24 页，Supplement 仍为 14 页。源码归一化检查确认本轮没有改动文字、公式、实验数据、图片或限制；只有上述排版命令和段落位置变化。38 页最终 PDF 均完成渲染巡检；没有短小的非末尾正文页、裁切或溢出。内置编辑器编译器的本机平台目录错误仍存在，最终成果由已有 TeX Live 工具链实际编译。

## 前轮贡献强化完成了什么

本轮不是普通润色，也没有新增实验。正文把创新焦点明确为：human-reviewed AI-derived updates 引入 correction-specific authorization problem；machine proposal、human-authorized value 与 exact reviewed candidate 是三个不同的对象。

即使候选的值和保留的审查上下文一致，实例授权目标仍可能不同。在要求 instance accountability 的政策下，candidate identity 参与 authoritative admission 的完整性条件，而不只是审计附加信息。

## 具体改动

1. Abstract：改为 problem → distinction → relation → characterization → separator → boundary → implication，保留 165、15、9、3 这组决定性证据；删除实现工具和次要计时结果的流水账。摘要为 191 词。
2. Introduction：先建立 correction-specific 问题，随后明确 candidate-bound authorization；保留原公式 (1)、(2) 与 Figure 1。Contributions 归为完整性要求与关系、五类信息刻画、跨表示实现与政策区分三项。
3. Related Work：解释 transaction、freshness、provenance、approval 各自保障什么，以及为什么这些保障单独不能推出“提交的正是被审查的实例”。明确承认 Continuity Kernel 的 exact-proposal binding 先例，避免 first-ever 论断。
4. Discussion 9.1：把 equal-valued candidate substitution 提升为政策区分实验；解释 cross-representation agreement、五类 paired histories、E2 保证边界与 E3 成本测量的不同知识角色。
5. Conclusion：回收 proposal/value/instance 的三重区分与完整 admission relation，落脚于 intelligent information systems 的可执行 correction integrity。
6. AI-assisted preparation：补充本轮 contribution-focused restructuring 的披露。作者顺序、宣文韬的贡献声明和既有行政声明未改变。
7. 投稿信和系统元数据：与最终论文使用一致的创新叙事，系统摘要与 LaTeX 摘要完全一致。

## 保留的证据与限制

- Section 3 的 Proposition 1 scope statement、全部正式定义与证明范围保持不变。
- Sections 3--8 的技术内容保持一致；Section 3 与 Alloy 表仅有浮动参数变化，其余源码、全部实验数据、两幅图与参考文献数据库保持一致。
- Discussion 9.2--9.3 与原版本完全相同；finite scopes、same-study implementation、constructed histories、scripted fixture、presentation integrity 和成本比较混杂因素均未删除。
- 所有补充材料 LaTeX 源码和表格通过 SHA256 一致性检查；补充 PDF 从这些源码重新编译。
- 未把跨表示一致性写成通用数据库无关定理；未把等值替换写成 context policy 的一般性错误；未把 server-held binding 写成 display integrity 保障。
- 未把 E3 的跨实现时间差解释为纯 exact-binding overhead。

## 编译与排版检查

正文 24 页，补充 14 页；均由 TeX Live 2025 的 pdfLaTeX 工具链编译，入口源码分别是 main.tex 和 ESM_1.tex。

两套平铺源码分别在空目录中成功完成独立构建。最终日志没有 undefined references/citations、multiply-defined labels 或 Overfull boxes。正文保留 4 处 Underfull vbox 提示，来自原模板的分页与浮动体布局；逐页渲染检查未见裁切、重叠或表格溢出。正文 24 页、补充 14 页全部生成页面图并作版式巡检。

原标题、作者、版式、19 个编号公式及 15 个 eq: 标签保留；没有通过缩小字体或页边距规避页数上限。

来源提交：e65f760d0f486bbf70114207d969f66e4219abeb。原始 PDF 与用户上传 PDF 的 SHA256 完全一致。机器核验明细见 verification.json。

作者仍需在投稿系统中确认全体作者批准、声明准确、通信信息，以及未同时在其他期刊审理。没有实际向期刊提交；GitHub 按新增修订目录发布，原始准备稿保留。
