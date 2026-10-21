# 投稿上传说明（2026-10-21）

本目录按你提供的投稿系统页面整理，可逐项上传。没有生成总压缩包。

| 投稿页面栏目 | 选择文件 | 说明 |
|---|---|---|
| Manuscript file | `Manuscript-sources.zip` | 可编辑 LaTeX 主稿；ZIP 根目录只有一个 `main.tex`，正文图表已内嵌，含参考文献、模板与图文件 |
| Supplementary material | `Online-Resource-1.pdf` | 标题可填 Online Resource 1 — Supplementary evidence and reproduction guide |
| Supplementary material | `Online-Resource-2.pdf` | 标题可填 Online Resource 2 — Supplementary addendum |
| Supplementary material | `X1-X2-reproduction.zip` | 标题可填 X1–X2 reproduction package；确定性实验源码、已保存运行及验证入口 |
| Figures and tables | 初次投稿可以留空 | 四幅图和全部表格已在主稿中；无需重复上传 |
| Related files | 本次可以留空 | 内部审查记录、压缩对照和检查日志不需要上传 |

`Manuscript.pdf` 是核对用的主稿预览。当前页面要求可编辑稿，优先上传上述 LaTeX ZIP；若后续系统另要求 PDF，再选择此文件。`Cover-letter.txt` 供后续 Cover letter 栏粘贴或上传，不必为了放文件而提交到 Related files。`FILES.json` 与本说明留作本地核对。

上传后打开系统生成的 PDF，核对标题、作者、公式、四幅图、七张表、参考文献和文末声明。核实系统生成稿与本地 Manuscript.pdf 内容相同后再完成提交。

此版已补上表 1 的正文引用；四图宽度随正文栏宽自动适配；图注只删除末尾句号，保留内部句号。未改变论文主线、实验结果或证据边界。主稿 ZIP 与完整源码独立重编译后的逐页文本和渲染一致；两份补充材料与上一版逐页一致。

完整正文及两份补充材料的编辑源文件另保留为上一级 `ASE-manuscript-sources.zip`，并纳入 GitHub 复现仓库。它不是本页面 Manuscript 栏使用的精简 ZIP。上一级旧的总压缩包是历史快照，不是本次提交文件。

官网说明核对日期：2026-10-21。期刊指南要求图适配栏宽、图注末尾无标点；页面的可编辑稿上传要求以本次截图为依据。指南的 Additional Information 仍写 PDF submission only，因此同时保留 PDF 预览供系统另行要求时使用。
https://link.springer.com/journal/10515/submission-guidelines
