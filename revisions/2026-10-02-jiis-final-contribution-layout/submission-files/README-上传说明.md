# JIIS 最终投稿包

本包基于 GitHub 提交 `e65f760d0f486bbf70114207d969f66e4219abeb` 中完整的 JIIS 投稿源码制作。该提交的 Manuscript.pdf 与你上传的 PDF 的 SHA256 完全一致。

本次在独立副本中完成贡献与创新表达强化及排版修订。本包用于发布到 GitHub 的新增修订目录，旧版本和原件保留，未向期刊实际提交。

## 上传文件

- `Manuscript.pdf`：正文，24 页（包括参考文献、表格和图片），使用原有 smallcondensed LaTeX 模板。
- `Manuscript-LaTeX.zip`：正文完整源码，ZIP 内文件为平铺结构，入口 `main.tex`。
- `ESM_1.pdf`：Online Resource 1，14 页；补充材料内容未修改，由原 LaTeX 源码重新编译。
- `Online-Resource-LaTeX.zip`：补充材料完整源码，平铺结构，入口 `ESM_1.tex`。
- `cover-letter.txt`：匹配最终论文创新叙事的投稿信，可粘贴到投稿系统。
- `submission-metadata.txt`：标题、摘要、关键词、作者及通信信息；摘要与正文完全一致。

外层 ZIP 是交付包，不建议把整个外层 ZIP 当作论文源码上传。请按投稿系统实际栏目选择上述文件；源码字段上传对应源码 ZIP，supplementary information 字段上传 ESM_1.pdf。检查报告和本说明供作者使用，不属于论文附件。

## 修改边界

强化 Abstract、Introduction（含 Contributions）、Related Work、Discussion 9.1 和 Conclusion，并补充本轮 AI 辅助编辑披露。核心是 correction-specific candidate-bound authorization、proposal/value/instance 三者区分、等值候选替换的 policy separator、两种存储表示的实现一致性，以及 E2 的 presentation boundary。

没有增加实验或更改结果。Sections 3--8 的技术内容、Discussion 9.2--9.3、实验数据、图、参考文献数据库和所有补充材料源码保持不变；仅调整 Section 3 和 Alloy 汇总表的浮动位置参数。保留 19 个编号公式及原标签。保留近邻工作 Continuity Kernel 的 exact-proposal binding 先例，不宣称首次提出一般性的 exact binding，也不把 E3 性能写成主要创新。

作者顺序与贡献声明沿用队友上传版本，第二作者仍为 Xuan Wentao（宣文韬）。

## 排版修订

三张表的浮动参数由 `[t]` 改为 `[!htbp]`，消除原第 10、12 页的大面积留白。贡献列表以同宽不可分页块排版，C1--C3 连续放在第 2 页；机制比较段落移到列表后，文字未改。正文从 25 页降为 24 页，smallcondensed 的默认版心、字号和页边距没有改变，所以整体仍有模板默认的左上方版心与外侧留白。

## 本地复编译

解压 Manuscript-LaTeX.zip 到空目录，在该目录运行：

```powershell
latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex
```

解压 Online-Resource-LaTeX.zip 到另一个空目录，在该目录运行：

```powershell
latexmk -pdf -interaction=nonstopmode -halt-on-error ESM_1.tex
```

本机使用 TeX Live 2025 / pdfLaTeX / BibTeX / latexmk；提交源码 ZIP 不含缓存、中间文件或本机路径配置。

## 投稿前作者确认

请确认全体作者同意本版本、作者和单位信息、通信邮箱、披露与声明准确，以及没有同时在另一期刊审理。投稿信沿用原源码包的未同时投稿声明，本轮没有独立核实作者行政事项。

已参照 JIIS 官方指南的 LaTeX、小版式、24 页、150--250 词摘要、4--6 个关键词与平铺源码要求：
https://link.springer.com/journal/10844/submission-guidelines

本机内置编辑器编译器报平台目录错误；最终两个 PDF 由本机现有 TeX Live 工具链实际编译并核验，不是直接编辑 PDF 或文档转换。
