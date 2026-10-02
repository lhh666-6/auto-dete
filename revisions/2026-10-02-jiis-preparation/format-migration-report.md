# JIIS 完整内容模板迁移检查

日期：2026-10-02。结论：**DKE 32 页 → JIIS smallcondensed 24 页，完整内容保留。** 这是格式基线，不是最终投稿包；本轮没有新增实验，也没有改写科学叙事。

| 项目 | 检查结果 |
| --- | --- |
| Springer 主文 | 24 页，包含声明、26 条参考文献、全部原有主文图表 |
| 摘要 / 关键词 | 原摘要逐字保留；201 词，6 个关键词 |
| 内容完整性 | 38 个章节、表格及图件文件逐字节一致；主文输入列表及 bibliography 数据库一致 |
| 引用与交叉引用 | 26 个 cited keys 对应 26 个 bibliography entries；无缺失、无未引用条目、无重复 label |
| 编译 | 本机 MiKTeX pdfLaTeX + BibTeX 成功；没有字体替换、溢出框、未解析引用或交叉引用 |
| 科学结论是否改变 | **No**。形式定义、Proposition、数值、实验结果与证据关系均未编辑 |
| 冻结版本 | DKE 主文及补充 PDF 的原 SHA-256 均未变化 |
| 补充材料 | 原 21 页补充 PDF 仅另存为 supplement-dke-baseline.pdf，尚未迁移 Springer 格式 |

## 实际变动

采用官方 `svjour3` 的 `smallcondensed` 选项；保留其默认正文尺寸和版心，没有缩小字号、减少边距或设置负间距。主文尺寸为 12.2 × 19.8 cm，默认正文 9.5 pt / 11.5 pt。原有 Latin Modern 字体保留。

将 Elsevier 的 frontmatter 改为 Springer 的标题、作者、单位、摘要和关键词命令；作者及单位信息不变。参考文献改用官方 `sn-basic.bst`，以数字方括号引用，原 bib 元数据不变。

为旧版官方 SVJour3 与本机现代 LaTeX 兼容，外层 main.tex 做了三处调整：使用官方支持的 `nospthms` 关闭本文未使用的预定义 theorem 环境；为空的 `bibcommenthead` 提供兼容命令；按官方模板在 documentclass 前加载 `fix-cm`。没有修改 vendor class / style 文件，也没有修改科学章节。

官方模板来源：

- [SVJour3 官方 ZIP](https://media.springer.com/full/springer-instructions-for-authors-assets/zip/1633537_svjour3-Latex-package.zip)
- [Springer Nature 官方模板及 bibliography styles](https://cms-resources.apps.public.k8s.springernature.io/springer-cms/rest/v1/content/18782940/data/v12)
- [JIIS submission guidelines](https://link.springer.com/journal/10844/submission-guidelines)

## 页面检查与保留问题

逐页检查了 24 页的缩略图，并放大检查首页、两幅主图及最后的参考文献页。没有发现文字裁切、图表重叠或空白页。两幅图位于第 4、16 页，内容及图注均保留；参考文献始于第 23 页。

第 3、12 页的正文较少，模板的浮动体与 section 边界处理产生较多留白；第 16 页有一次 underfull vbox（badness 4940）。首页也有模板默认的标题与摘要间距，第三位作者姓名跨行。上述问题不影响完整性或 25 页门槛，但后续可仅从 frontmatter 和浮动位置处理排版。本轮遵守“先原内容完整编译”，没有更改这些版面行为。

九类 source-pathology 检查未发现强制浮动、负间距、缩放表格、极小字号、固定厘米列宽、label-before-caption 等问题。ChkTeX 给出五类提示（1、12、13、24、35）：涉及命令后的空格、句间距、label 邻近空白，以及将 `v_{exp}` 中的 exp 误认为指数函数；仅记录，不自动改写冻结内容。

latexindent 因本机缺少 Perl 无法运行，未据此判断源码有错误。Skill 引用的共享 outputs verifier 在本地缺失，改用文件存在性、SHA-256、PDF 解析、内容比对及引用审计核验产物；没有提交 Git commit。

## 格式检查评分

这是 LaTeX skill 的机械检查分数，**不是科研水平、创新性或录用概率评分**。

| Metric | Value |
| --- | --- |
| Score | **91 / 100** |
| Verdict | Ship with notes（仅指本轮可审阅的格式基线） |

| Issue | Deduction |
| --- | --- |
| 一次 underfull vbox | -1 |
| 五类 ChkTeX 提示，各计一次 | -5 |
| 模板兼容修复合计五次 pdfLaTeX 调用，超过两次的三次调用 | -3 |
| Total | **-9** |

## 下一步

无需为了页数删减证据或移动主要实验。后续只做 JIIS 的小幅首尾 framing 与排版/声明收口，再准备扁平源码、Online Resource 和投稿信。保持“真实运行系统 + 构造输入”的准确描述，不将已有输入宣称为生产系统的代表性 traces。

证据文件：`format-audit.json` 与 `format-migration-manifest.json`。检查脚本及渲染缩略图属于内部工作记录，不作为科学补充材料上传。
