# DKE 投稿包使用说明

准备日期：2026-09-27。基于远程 `dd2f12ea` 完成排版收尾；这是待作者确认的投稿候选版本，尚未向期刊提交。

## 上传文件

| 文件（均在 `upload/`） | 用途 |
| --- | --- |
| `manuscript.pdf` | 32 页具名主文；供预览或按系统要求作为 Manuscript 上传 |
| `supplementary-material.pdf` | 21 页补充材料；选择 Supplementary material 类别 |
| `cover-letter.docx` | 英文投稿信；可上传或复制到系统 Cover Letter 字段 |
| `highlights.docx` | 5 条英文 Highlights；每条含空格不超过 85 字符 |
| `main-source.zip` | 主文 LaTeX 源码；扁平目录，含参考文献、编译所需图件及 `main.bbl`；主文件是 `main.tex` |
| `supplement-source.zip` | 补充材料源码；主文件是 `supplement.tex`，仅在系统要求时提供 |
| `figure-1-admission-workflow.pdf` / `figure-2-evidence-route.pdf` | 独立矢量图；仅在系统要求单独上传图件时选择相应 Figure 类别 |
| `figure-reproduction.zip` | 图件复现脚本和原始表格/CSV；可作代码附件或留存供编辑索取，不选 Manuscript 类别 |

附件说明可填写：Supplementary material with formal observation details, evidence mapping, a worked example, complete current-version timing grids, and historical integration evidence.

整套 `DKE-submission-package-2026-09-27.zip` 是给作者传递和归档的外层包，**不要把它整体作为 Manuscript 上传**。内部有上传说明、作者确认清单和检查记录；这些不应进入给审稿人的论文 PDF。主文与补充材料源码应分别处理，不要合并编译成一个文档。

## 已完成的检查

- 本轮仅调整存储表的浮动位置、参考文献条目间距与分页，消除原第 26 页近空白页。正文文字、命题、实验数字、作者顺序、贡献及既有图件披露不变。
- 主文在本机 MiKTeX 25.12 / elsarticle 3.5 编译通过；补充 PDF 保留基线文件。当前页数为 32/21，两个源码包均用本机工具链独立重建通过，最终日志无警告、缺失引用或 overfull/underfull。字号、页边距和正文行距保持原样。
- 两个源码 ZIP 均在独立空目录解压并编译。全部页面的提取文本和 72 dpi 渲染像素与对应投稿 PDF 完全一致；结果见 `source-rebuild-verification.json`。
- 两份 Word 文件沿用基线中已渲染并目视检查的单页版本，逐字节未变；本轮不重复 Word 渲染。
- 基线已独立复核 E1/E2 记录、E3 汇总、26 条引用和固定 GitHub 链接。本轮核对科学源文件完整性、引用/交叉引用解析及打包一致性，不重跑科研实验、重新聚合原始记录或调用模型 API。
- `package-manifest.json` 记录全部拟上传文件的 SHA-256；源码包不含内部审稿笔记、旧稿、数据库或 AI 生图原型。

## 作者在提交前完成

1. 阅读 `author-confirmation-checklist.md`，由通讯作者确认全体作者同意投稿、作者信息及所有声明真实。已保留陈奇乐第三作者、同一单位，贡献为 Investigation 和 Validation。
2. 用 `submission-metadata.md` 填写标题、摘要、关键词、作者和贡献。现有资料只提供了通讯作者邮箱；其他邮箱、ORCID 及姓名的 given/family-name 拆分按本人信息填写。
3. 在 DKE 实际投稿系统核对匿名方式、篇幅、摘要/关键词数量、文章类型和附件类别。本次未取得完整专属指南，不能把这些项目标为已合规。当前包为具名稿；如果系统要求匿名，先生成并审查匿名副本。
4. 检查系统合成的 PDF，确认公式、图表、参考文献和补充材料次序正确后，再由通讯作者完成正式提交。

作者指南：https://www.sciencedirect.com/journal/data-and-knowledge-engineering/publish/guide-for-authors

一般 LaTeX 要求：https://www.elsevier.com/researcher/author/policies-and-guidelines/latex-instructions

Highlights 要求：https://www.elsevier.com/researcher/author/tools-and-resources/highlights

AI 披露要求：https://www.elsevier.com/about/policies-and-standards/generative-ai-policies-for-journals

## 后续编辑

在上级目录修改论文源文件，再运行 `scripts/Build.ps1`。若投稿信或 Highlights 文字变化，运行 `scripts/build_submission_documents.py` 并重新渲染检查 Word。随后运行 `scripts/build_submission_package.py`、`scripts/build_submission_package.py --verify`，更新检查报告，再运行 `scripts/finalize_submission_package.py` 同步文件清单和外层 ZIP。不要直接修改扁平源码 ZIP 后继续沿用旧 PDF 或旧校验报告。

图件复现依赖 Matplotlib 3.10.8；本轮核对打包输入及其哈希，不重新生成已经核验的科学图件。
