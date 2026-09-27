# DKE 投稿规则核查

核查日期：2026-09-27。这里只记录可核实要求，不将第三方模板、旧问答或已发表论文的版式当作现行投稿规则。

## 已核实

Elsevier 官方 [DKE 介绍](https://shop.elsevier.com/journals/data-and-knowledge-engineering/0169-023X) 列出数据库与知识库的表示、操作、设计、实现、完整性、安全及维护等主题。本文的期刊定位应围绕 correction-aware admission relation、数据完整性和字段级来源展开；这是一项适配性判断，不代表编辑部已认可选题。

Elsevier 现行 [生成式 AI 政策](https://www.elsevier.com/about/policies-and-standards/generative-ai-policies-for-journals) 要求：

- 论文末尾、参考文献前设置 AI 声明，说明工具、用途、作者审查及责任。
- AI 辅助的解释性流程图/概念图，在各自图注及全文声明中披露；图注说明工具、版本和用途。
- 数据可视化直接来自底层数据，生成方法可复现；AI 辅助方法及工具信息在 Methods 中说明。
- 普通生成式 AI 生图工具不能用于 Graphical Abstract。

据此，本轮将 AI 声明缩为 60 个英文词，图 1/2 各保留简短披露。Section 7 补充图 2 的工具、数据输入与矢量生成方法。图 1 的生图服务未暴露模型/版本，保留实际可用信息，不编造版本。设计原型仍单独归档，正文图与再生成脚本均未改动。

## 尚未核实

官方 [Guide for Authors](https://www.sciencedirect.com/journal/data-and-knowledge-engineering/publish/guide-for-authors) 在网页工具和直接请求中均返回 HTTP 403，另一个官方路径及官方旧链接也未取得完整指南。

因此，以下项目不标记为已满足：正文页数/字数上限、摘要字数上限、关键词数量、匿名审稿方式、Highlights 的具体要求、Graphical Abstract 是否必需、参考文献格式及投稿附件要求。第三方所述“20–40 页”来自旧问答，不能作为现行规则。

当前稿使用 elsarticle 单栏预印本格式，正文 32 页、补充材料 21 页。编译通过与完整期刊格式合规是两项不同检查；正式上传投稿系统前仍需取得可访问的完整官方指南或系统说明。
