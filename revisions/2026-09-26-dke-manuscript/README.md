# DKE 新版论文

日期：2026-09-27（压缩与图解修订）

本文件夹是独立的英文论文修订版，面向 Data & Knowledge Engineering。原论文、原仓库和补充实验原始记录未被改写。本次完成论文整合、编译和审查，没有新增模型调用或重新采集实验结果。

## 阅读与编辑

- `main.pdf`：30 页英文主稿，新增两张解释 admission relation 和证据路线的矢量图。
- `supplement.pdf`：21 页补充材料，包含完整观察函数、证据映射、复现说明、工作示例、完整当前性能网格和历史集成结果。
- `main.tex` / `sections/`：主稿 LaTeX 源文件。
- `supplement.tex`：补充材料源文件。
- `filtered.bib`：正文实际使用的参考文献。
- `tables/` / `figures/`：编译所需图表及用于再生成附表的 CSV。
- `highlights.txt`：英文研究要点。
- `修改说明.md`：修订重点、结论边界和作者最终检查事项。
- `editorial/compression-map.md`：逐节词数、段落标签、压缩后的英文、迁移位置和图解写作思路；不属于投稿正文。
- `editorial/`：核查记录。`compression-verification.json` 和 `final-build-check.json` 对应本次结果；9 月 26 日的审核记录保留为原 44 页版本的历史记录。

论文标题：**Correction-Aware Data Admission: Candidate-Bound Authorization and Field-Level Provenance for AI-Derived Updates**。

## 编译

需要安装包含 elsarticle 的 MiKTeX 或 TeX Live，以及 pdflatex、BibTeX。本次在作者本机使用 MiKTeX 25.12 编译。进入本文件夹后运行：

```powershell
.\scripts\Build.ps1
```

脚本依次编译正文、参考文献和补充材料，处理交叉引用，检查最终日志后将 PDF 放回本文件夹。无需 latexmk 或 Perl。已有 latexmk 环境也可以运行：

```text
latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex
latexmk -pdf -interaction=nonstopmode -halt-on-error supplement.tex
```

中间文件写入 `out/`。可直接修改章节后重新编译，不依赖原始论文目录。附表重建脚本使用 Python 标准库，读取本文件夹自带的 CSV：

```text
python scripts/build_supplement_tables.py
```

两张概念/证据图可用 Python 和 Matplotlib 3.10.8 重新生成：

```text
python scripts/build_story_figures.py
```

图 1 为构造例；图 2 的 E1/E2 计数与 E3 timing total 读取已有 tables/CSV 并校核，不生成实验数据。输出为 PDF、SVG 和 PNG，数据源哈希在 `editorial/story-figure-source-hashes.json`。`figures/concepts/` 仅保存 AI 辅助设计原型，未用于正文或 Graphical Abstract；工具用途和版本可用性已写入图注及 AI declaration。

## 实验证据

三组新增实验固定发布于：
https://github.com/lhh666-6/auto-dete/tree/2645e5e18c900ea91c9c980e44195dc71e410432/DKE-supplement

当前参考实现固定提交为 `c6d512843c905cab6d8521dd8c914f7fb26d85ae`。新稿不将旧 v8 性能结果与修复后结果混算。大型数据库的压缩仅改变发布体积，恢复与散列检查方式见补充材料 S1。

本文件夹包含可交给合作者审阅的完整稿件；正式提交前仍应由作者确认最终文字、作者贡献、经费/利益冲突/伦理声明及投稿系统要求。本文档不表示论文已投稿或被接收。
