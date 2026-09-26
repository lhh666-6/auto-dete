# DKE 新版论文

日期：2026-09-26

本文件夹是独立的英文论文修订版，面向 Data & Knowledge Engineering。原论文、原仓库和补充实验原始记录未被改写。本次完成论文整合、编译和审查，没有新增模型调用或重新采集实验结果。

## 阅读与编辑

- `main.pdf`：新版英文主稿。
- `supplement.pdf`：新版补充材料，包含证据分层、复现说明、形式化细节、工作示例、完整当前性能网格和历史集成结果。
- `main.tex` / `sections/`：主稿 LaTeX 源文件。
- `supplement.tex`：补充材料源文件。
- `filtered.bib`：正文实际使用的参考文献。
- `tables/` / `figures/`：编译所需图表及用于再生成附表的 CSV。
- `highlights.txt`：英文研究要点。
- `修改说明.md`：修订重点、结论边界和作者最终检查事项。
- `editorial/`：文献核查、形式化审查、实验核查、质量检查记录；不属于投稿正文。

论文标题：**Correction-Aware Data Admission: Candidate-Bound Authorization and Field-Level Provenance for AI-Derived Updates**。

## 编译

需要安装包含 elsarticle 的 TeX Live（本次使用 TeX Live 2025），以及 latexmk、BibTeX。进入本文件夹后运行：

```powershell
.\scripts\Build.ps1
```

或：

```text
latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex
latexmk -pdf -interaction=nonstopmode -halt-on-error supplement.tex
```

`.latexmkrc` 将中间文件写入 `out/`，并把最终 PDF 放回本文件夹。可直接修改章节后重新编译，不依赖原始论文目录。附表重建脚本使用 Python 标准库，读取本文件夹自带的 CSV：

```text
python scripts/build_supplement_tables.py
```

## 实验证据

三组新增实验固定发布于：
https://github.com/lhh666-6/auto-dete/tree/2645e5e18c900ea91c9c980e44195dc71e410432/DKE-supplement

当前参考实现固定提交为 `c6d512843c905cab6d8521dd8c914f7fb26d85ae`。新稿不将旧 v8 性能结果与修复后结果混算。大型数据库的压缩仅改变发布体积，恢复与散列检查方式见补充材料 S1。

本文件夹包含可交给合作者审阅的完整稿件；正式提交前仍应由作者确认最终文字、作者贡献、经费/利益冲突/伦理声明及投稿系统要求。本文档不表示论文已投稿或被接收。
