# DKE 新版论文

日期：2026-09-27（完成投稿材料、独立审查及扁平源码重建验证）

**投稿候选文件以 `submission/README.md` 和 `submission/upload/` 为准。** 当前主文 32 页、补充材料 21 页。排版收尾基于 `dd2f12ea`，仅调整存储表位置及参考文献间距/分页，消除第 26 页近空白页；正文文字和实验结果未改。主文使用本机 MiKTeX 25.12 / elsarticle 3.5 重建，补充 PDF 原样保留。完整传递包为 `submission/DKE-submission-package-2026-09-27.zip`。作者确认和期刊系统要求的剩余核对见该目录说明。

本文件夹是独立的英文论文修订版，面向 Data & Knowledge Engineering。原论文、原仓库和补充实验原始记录未被改写。本次完成论文整合、编译和审查，没有新增模型调用或重新采集实验结果。

## 阅读与编辑

- `main.pdf`：32 页英文主稿，保留两张解释 admission relation 和证据路线的矢量图。
- `supplement.pdf`：21 页补充材料，包含完整观察函数、证据映射、复现说明、工作示例、完整当前性能网格和历史集成结果。
- `main.tex` / `sections/`：主稿 LaTeX 源文件。
- `supplement.tex`：补充材料源文件。
- `filtered.bib`：正文实际使用的参考文献。
- `tables/` / `figures/`：编译所需图表及用于再生成附表的 CSV。
- `highlights.txt`：英文研究要点。
- `修改说明.md`：修订重点、结论边界和作者最终检查事项。
- `editorial/submission-final-audit-2026-09-27.md`：当前独立内容、原始记录和 PDF 版面审查；`submission/source-rebuild-verification.json` 为投稿源码重建验证。
- `editorial/final-mechanical-check.md` / `final-mechanical-check.json`：上一轮五处局部修改、身份映射及机械一致性检查。
- `editorial/submission-closeout.md` / `submission-closeout-check.json`：上轮局部收口、原始记录核对、公开链接及编译检查。
- `editorial/dke-policy-check.md` / `closest-work-closeout.md`：期刊规则核实状态和五篇最近工作的原文核查。
- `editorial/micro-revision.md` / `micro-revision-check.json`：上轮六项局部修订的历史记录。
- `editorial/narrative-revision.md`：上一轮科研故事、文献定位和限定语迁移说明。
- `editorial/narrative-section-counts.md` / `defensive-language-audit.md`：上一轮逐节词数和逐处限定语审查；当前 PDF 提取词数见 `final-mechanical-check.md`。
- 仓库根目录 `docs/literature-review/`：16 个诊断位置、8 族文献检索记录、33 项候选审查、11 维内部矩阵与十问首读检查；不属于投稿正文或补充材料。
- `editorial/`：`layout-closeout-2026-09-27.md`、`layout-closeout-check-2026-09-27.json` 和 `final-build-check.json` 对应当前排版稿；`final-mechanical-check.json` 和 `source-check.json` 对应收尾前 `ee4e65ac`。其他旧审查保留为历史记录，不作为当前 PDF 身份标识。

论文标题：**Correction-Aware Data Admission: Candidate-Bound Authorization and Field-Level Provenance for AI-Derived Updates**。

上一轮以 `b81042e4b4b89be333c427aaf52615c9eeaf8ef1` 的 30 页版本为基线。相关工作补入审批、人工修复及版本化来源的直接先例，形成四个小节；主稿增加 3 页，补充材料仍为 21 页。新增 9 条核验文献，原 17 条保留。正式命题、证明、RQ、契约公式、P0–P6、实验数值以及 17 个表格/CSV 保留；本轮没有新增或重跑科研实验。上一轮本机编译和逐页检查见 `editorial/narrative-quality-check.md`。

上一轮局部修订以 `2eb04fce5f753ea2a0e9b9265cd9f84484f02819` 为基线：补上 equal-valued substitution 到五类信息的桥，明确 E1/E2/E3 的层级，减少支撑性数字在文字及图 2 中的重复，并微调 Related Work 与 Discussion。正文净减少 50 个英文词，PDF 提取字数 8,720→8,656；主稿仍为 33 页。补充材料、表格数据、正式命题和 RQ 不变。该轮检查见 `editorial/micro-revision.md`。

上一轮收口以 `7e65d6a7121c6388ecada94031abc46c0bbc860c` 为基线：仅调整少量句子和必要工具披露，核查五篇最近工作、全部 E1 原始执行记录和公开证据链接。AI 声明 207→60 词；正文 33→32 页，PDF 提取词数 8,656→8,509。命题、证明、RQ、Results、表格、图文件、科研脚本与补充材料不变。完整 DKE Guide for Authors 暂不可访问，因此尚不能宣称全部期刊格式要求已核实。该轮检查见 `editorial/submission-closeout.md`。

上一轮最终检查以 `4701ec8241acd8e38f20968ff1df8dfe9ef2f246` 为基线：仅澄清实例身份与证书摘要的关系，删除 Section 7.1 重复披露，并在 S2.2 同步说明已有模型身份语义。正文保持 32 页，补充材料保持 21 页；PDF 提取词数分别为 8,512 和 6,084。命题、证明、显示公式、RQ、实验数字、表格和科研脚本不变，没有进行大规模润色。见 `editorial/final-mechanical-check.md`。

## 编译

需要安装包含 elsarticle 的 MiKTeX 或 TeX Live，以及 pdflatex、BibTeX。`dd2f12ea` 基线主文由 TeX Live 2025 / elsarticle 3.4c 编译；当前排版主文使用 MiKTeX 25.12 / elsarticle 3.5 编译，补充 PDF 保留该基线文件。进入本文件夹后运行：

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

图 1 为构造例；图 2 的 E1/E2 结果与 165-case 分母读取已有 tables；E3 timing total 读取 CSV 校核，但不再作为图中标题，不生成实验数据。输出为 PDF、SVG 和 PNG，数据源哈希在 `editorial/story-figure-source-hashes.json`。`figures/concepts/` 仅保存 AI 辅助设计原型，未用于正文或 Graphical Abstract；工具用途和版本可用性已写入图注及 AI declaration。

## 实验证据

三组新增实验固定发布于：
https://github.com/lhh666-6/auto-dete/tree/2645e5e18c900ea91c9c980e44195dc71e410432/DKE-supplement

当前参考实现固定提交为 `c6d512843c905cab6d8521dd8c914f7fb26d85ae`。新稿不将旧 v8 性能结果与修复后结果混算。大型数据库的压缩仅改变发布体积，恢复与散列检查方式见补充材料 S1。

本文件夹包含可交给合作者审阅的完整稿件；正式提交前仍应由作者确认最终文字、作者贡献、经费/利益冲突/伦理声明及投稿系统要求。本文档不表示论文已投稿或被接收。
