# DKE 投稿规则最终核查（2026-09-27）

核查基线：`ee4e65ac`。本报告只记录已读取的官方规则、当前稿件状态和投稿前动作，不改正文、不代表编辑部认可或投稿已经完成。主任务后续对材料的修正应以最终投稿包清单为准。

## 结论

论文可以进入投稿材料准备阶段。本轮可落实的三个动作是：补齐 Figure 2 的 Methods 可复现说明、准备 Word 格式 Highlights、另做 Editorial Manager 可处理的扁平化 LaTeX 源码包。没有从已核实的官方规则中发现要求追加科学实验的事项。

**不能将“全部 DKE 格式要求已满足”标为完成。** DKE 专属 Guide for Authors 的完整正文仍未取得；匿名方式、篇幅上限、摘要/关键词限制、具体附件义务要在上传时按该刊指南或系统提示核对。仅准备材料无需因此停止。

## 官方来源与适用范围

1. [DKE Guide for Authors](https://www.sciencedirect.com/journal/data-and-knowledge-engineering/publish/guide-for-authors)：本次读取未返回正文。旧 ScienceDirect ISSN 路径、Elsevier 旧期刊指南路径和旧官方 PDF 路径亦未取得可用指南。既有核查记录为 HTTP 403，本轮工具返回 Internal Error。没有绕过访问限制。
2. [Elsevier LaTeX instructions](https://www.elsevier.com/researcher/author/policies-and-guidelines/latex-instructions)：已读取，适用于 Elsevier/Editorial Manager 的一般源码准备；该刊系统实际文件分类优先。
3. [How do I include Highlights with my manuscript?](https://www.elsevier.support/publishing/answer/how-do-i-include-highlights-with-my-manuscript)：已读取，更新于 2026-06-01；[Highlights](https://www.elsevier.com/researcher/author/tools-and-resources/highlights) 同时交叉核对。通用规则不能据此认定 DKE 初投强制要求 Highlights。
4. [Generative AI policies for journals](https://www.elsevier.com/about/policies-and-standards/generative-ai-policies-for-journals)：已读取，页面标明更新于 2026 年 6 月。
5. [Artwork formats checklist](https://www.elsevier.com/about/policies-and-standards/author/artwork-and-media-instructions/artwork-formats-checklist)：已读取，通用图件要求。
6. [How do I prepare my files for submission in Editorial Manager?](https://www.elsevier.support/publishing/answer/how-do-i-prepare-my-files-for-submission-in-editorial-manager)：已读取；明确期刊专属要求优先于通用说明。

搜索得到的第三方模板、旧问答及其他 Elsevier 期刊指南均未作为 DKE 专属规则的证据。尤其不能把 Your Paper Your Way 的其他刊群说明直接套成 DKE 的单匿名规则。

## 当前文件核对及具体动作

| 项目 | 基线稿件情况 | 投稿前动作/判定 |
|---|---|---|
| 审稿匿名模式 | `main.tex` 含四名作者、单位、通讯邮箱；PDF metadata 也含作者 | DKE 模式尚未核实。保留具名版本，不擅自声称双匿名或单匿名；若系统要求双匿名，再准备去作者、声明可识别信息和 PDF metadata 的审稿副本，并检查 GitHub 链接造成的身份暴露 |
| 页数及字数 | 最终记录为主文 32 页、补充 21 页 | 未核实 DKE 上限，不能把 32 页自动视为超限或合规；无需无依据继续压缩 |
| 摘要/关键词 | `main.tex` 摘要按空白分词为 201 词，关键词 6 项 | DKE 数量上限未核实；保留现文，到系统内核对，不套用其他刊物规则 |
| Highlights | `highlights.txt` 共 5 条；去掉列表标记后长度为 79、78、74、79、77 字符，含空格 | 内容满足 Elsevier 通用的 3–5 条、每条不超过 85 字符。官方资源页明确 Word 文档，支持页也指向 Microsoft Word 源文件；补 `Highlights.docx`。TXT 可保留供粘贴，不称其已满足 Word 要求 |
| LaTeX 源码 | 工作稿采用 `sections/`、`tables/`、`figures/` 子目录 | 另建扁平化上传 ZIP 并重写包内相对引用。官方说明 EM 无法处理子目录。工作目录可继续保持原结构；投稿包应包含实际依赖、参考文献及图件，排除日志和内部核查记录 |
| PDF 与源码类型 | 已有主文和补充 PDF | 依据上传系统选 Manuscript / LaTeX source files；不要把主文 LaTeX 源码误选为供读者发表的 Supplementary material。主文 PDF 与上传源码必须对应同一版本 |
| 图件 | 主文使用 PDF 矢量图，图注在正文；脚本设置 PDF TrueType 嵌入 | PDF 是官方允许图件格式。最终包核查字体嵌入、清晰度和编号/图注对应；不必把矢量图改成位图 |
| 补充材料 | 现有独立 `supplement.pdf`，主文有 S1–S6 引用 | 随论文提交并给简短附件说明。DKE 的附件类别、体积限制和是否另需源文件仍按系统提示；不要把整个实验数据库全部嵌入文章源码包 |
| AI 全文声明 | 声明位于参考文献之前，列出工具、用途、审查及责任；Figure 1/2 有图注披露 | 保留；无需因为 AI 辅助而删掉合规解释性图示 |
| Figure 2 的 Methods 披露 | §7.1 有实验输入概述，Figure 2 图注有 OpenAI Codex (GPT-6)，但方法正文不再含图件生成工具 | 当前图含实验数量，建议按数据可视化规则处理，在 §7.1 加简短可复现方法，写明脚本、数据输入、Matplotlib 3.10.8 和 OpenAI Codex (GPT-6) 的辅助用途；图注不能完全替代 Methods |
| Figure 1 的版本信息 | 图注/声明如实写明 image generation 的 model/version unavailable | 不编造缺失版本。可记录服务名、用途、作者复核、原型归档；若编辑要求再提供可得记录。当前是概念图，不是原始实验图 |
| Graphical Abstract | 未发现独立投稿图文摘要 | DKE 是否强制尚未核实，不凭空增加。不要直接把通用生成式 AI 生图原型充作 Graphical Abstract |
| 作者及声明 | Liang Hanghao、Xuan Wentao、Chen Qile、Peng Peng；同一湖南大学单位；Chen Qile 为 Investigation and Validation | 文件层面一致。通讯作者在正式上传时确认拼写、邮箱、顺序、贡献以及全体作者对最终稿的认可；不能由助手代替作真实同意声明 |

## Figure 2 方法补充依据

Elsevier 现行 AI 政策区分解释性图示与数据可视化。解释性图示需图注和全文声明披露；AI 辅助的数据可视化须来源于可追溯数据，在 Methods 提供可复现方法。研究过程中的 AI 辅助代码也应在 Methods 说明。通用 AI 图像生成工具不能用于图文摘要；这一限制不能误套为“所有正文示意图都禁用”。

本地可核对的生成链为 `scripts/build_story_figures.py`：Figure 2 从 `tables/dke/comparator.tex`、`tables/dke/review.tex` 读取 E1/E2 数值，并读取 `tables/supplement-current/` 下三份 E3 汇总 CSV 核对 22,400 次计时总数。脚本包含断言并输出源哈希到 `editorial/story-figure-source-hashes.json`。可以用一句方法说明指向该脚本和上述归档输入，不必重复整段 AI 声明。该建议属于可修复的披露位置问题，不是新增实验要求。

## 留给正式上传阶段的核对

- 获取 DKE 的匿名模式、文章类型及实际附件类别；通用支持页不能替代这些刊物设置。
- 对照系统核对篇幅、摘要/关键词数量和 Highlights/Graphical Abstract 的具体要求。
- 由通讯作者确认最终作者与声明、无同时投稿状态；若系统询问既往拒稿/转投，真实填写，勿把自主新投稿写成编辑部正式转稿。
- 上传后查看系统合成 PDF：标题、作者、公式、图表、引用、补充材料顺序及字体应完整；源码本地编译通过不能代替该检查。

以上未核实项应作为明确的上传前清单保留，而非把整个准备任务标为失败，也不应以未经核实的规则引发大规模重写。
