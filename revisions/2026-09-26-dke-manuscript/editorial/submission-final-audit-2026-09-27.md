# 投稿前独立审查（2026-09-27）

审查对象：`revisions/2026-09-26-dke-manuscript`，从远程 `ee4e65ac` 取得的稿件，以及本次收尾补充 Figure 2 方法披露后重新编译的稿件。只检查已有材料；未修改科学正文、未重跑实验、未发起模型调用。本文件不属于投稿正文或补充材料，应留在内部 editorial 目录。

## 审查结论与范围

主文和补充材料的作者、标题、单位、关键实验数字、图表来源和声明相互一致。未发现待填占位符、内部编辑批注、未解析交叉引用、缺失参考文献或丢失图文件。所有检查均限定于本报告列出的范围，不等同于独立复现实验、验证所有科学命题或保证期刊录用。

## 本次亲自执行的检查

### 作者、题名和声明

- 主文首页、补充首页、两份 PDF metadata 和对应 TeX 的顺序均为 Liang Hanghao、Xuan Wentao、Chen Qile、Peng Peng；Chen Qile 在 Xuan Wentao 之后。
- 全部作者共用湖南大学计算机与电子工程学院单位；主文列完整长沙地址，补充使用同一单位的简写地址。Peng Peng 为通讯作者，邮箱 `hnu16pp@hnu.edu.cn`。
- 两稿显示的文章完整题名一致；补充前加 Supplementary material。PDF metadata 使用题名简称，是有意的显示字段差异。
- 主文 CRediT 中 Chen Qile 为 Investigation and Validation，与用户提供的拒稿后实验验证贡献一致。
- 资金、利益冲突、伦理、数据可得性和 AI 使用声明完整存在；本次检查只确认文本一致和完整，不代替作者对事实作最终确认。

### 源文件、参考文献与 PDF 机械检查

- 递归解析主文共 18 份 TeX、补充共 10 份 TeX；全部 input 路径存在。
- 主文的两个 PDF 图文件存在；补充没有外部插图依赖。
- 按文档分别检查：没有重复 label，没有未定义 ref/cref/eqref 等目标。
- 26 个引用键均有 BibTeX 条目，无未引用 BibTeX 条目；本次构建生成的 `out/main.bbl` 含 26 个 bibitem。
- 对纳入正文的 TeX 及两份 PDF 提取文本搜索 TODO、TBD、FIXME、PLACEHOLDER、XXX、pending author、EDITOR NOTE、未解析 `??` 等，无命中；未发现 PDF 批注对象。
- 全部 PDF 页的文字块均处于页框内。这个检查不能单独证明没有重叠，因此另做下述图像审查。
- 本次 TeX Live 构建日志中两稿的 LaTeX Warning、undefined、Overfull、Underfull 均为 0。构建由主任务执行，本审查直接读取生成的日志。

### 数值复核：读取已有记录，未执行实验

- 直接重聚合 `DKE-supplement/results/e1/receipts.jsonl`：495 条，三个机制各 165 条；context/exact/reference 接受数分别为 60/45/45；实例策略违反数为 15/0/0。
- E1 查询结果分别为 1,020 correct 加 60 ambiguous、810 correct、810 correct；未发现 harness_error。165 对 exact/reference 的接受决定和完整 query 列表逐一相同。
- 直接重聚合 E2 `browser-observations.jsonl`：每路径 30 条；原路径接受 21 条，session gate 接受 12 条。候选、值、主体请求替换各 3 条只被原路径接受；display-only substitution 每路径均接受 3 条。
- E1 与 E2 合计 372 次拒绝，其现有记录全部报告 zero-write-on-reject；本次没有重新打开所有数据库检查摘要，也没有重演注入故障。
- 三份 E3 CSV 的 n 分别合计 4,000、4,000、14,400，总计 22,400。128 fields、100 versions、1,000 records 的 trace p50 为 170.2419 / 509.0902 ms，SQL 为 12 / 693，四舍五入后与主文、表格和补充一致。
- 已核对摘要、Results、Supplement S1/S4、E1/E2 表格以及 Figure 2 的关键分母和边界描述；没有把旧实验、查询条数或 replay setup 并入新实验的独立用例数。

### 公开链接与 source 包依赖

2026-09-27 经本机 HTTP 7897 代理向以下四个关键 GitHub 页面实际 GET，均返回 200（web 抓取工具先返回 cache miss，未把它当作链接失效）：

- 固定 E1–E3 数据：`https://github.com/lhh666-6/auto-dete/tree/2645e5e18c900ea91c9c980e44195dc71e410432/DKE-supplement`
- 固定实现：`https://github.com/lhh666-6/auto-dete/tree/c6d512843c905cab6d8521dd8c914f7fb26d85ae/latest/code/implementation-fixed`
- r31：`https://github.com/lhh666-6/auto-dete/tree/r31-jss-2026-09-13/latest`
- v8：`https://github.com/lhh666-6/auto-dete/tree/r21-jss-2026-09-07-v8`

本次未逐一重新访问 26 篇文献的所有 DOI/出版商链接；历史文献核验报告不应混写为本次新验证。

工作稿须保留 `main.tex`、`supplement.tex`、全部被 input 的 sections/tables、`filtered.bib` 和两个 `figures/refined/*.pdf` 的相对关系。投稿用源码 ZIP 已另做扁平化：改写实际 input/图件路径，附最终 `main.bbl`，并独立重建验证，见 `submission/source-rebuild-verification.json`。标准 `elsarticle` 类、`elsarticle-harv` 样式及源文件列出的 LaTeX 包属于 TeX 发行版依赖。Python 图表脚本和 CSV 是图表再生依赖，已经生成的 PDF 图足以编译稿件；内部 editorial 报告、AI 设计原型和无关旧稿不应混入投稿文件。

## 代表性视觉审查

使用实际 Poppler `pdftoppm` 渲染并通过图像工具逐页查看，而非仅依赖文本提取。

- 远程基线主文查看第 1、4、14、20、22、25、28、29、32 页：覆盖首页、两张图、密集属性表、实验表、声明和最后参考文献。
- 远程基线补充查看第 1、5、7、8、12、14、17、21 页：覆盖首页、形式化表、完整性能网格、历史结果和末尾局限。
- 最终收尾重编译后复查主文第 1、4、14、19、20、22、25、29、30、32、33 页，以及补充第 1、14、21 页。
- 已查看页面没有遮挡、裁切、乱码黑块、表格溢出或不可辨认的图注；图文配色和排版清楚。
- 中间构建曾出现主文第 33 页仅余两行参考文献续文的问题，已反馈；最终构建第 33 页包含从 Marinov 到 Zhou 的八条完整参考文献，排版正常，不存在该孤尾问题。最终主文 33 页、补充 21 页；应使用本报告下列身份标识，不沿用远程 MiKTeX 版的 32 页记录。

## 证据边界

历史 `final-mechanical-check.md` 中的 Alloy/witness 重跑、41 个受保护文件一致性，以及 `closest-work-closeout.md` 的全文源文献核验均是已有报告；本次没有冒充重新执行。期刊当前格式、投稿门户字段和作者最终批准由本次其他收尾检查处理；本报告不据旧版 guide 或网页缓存断言全项符合。

## 最终 PDF 身份

最终本地 TeX Live 收尾构建，经直接读取 PDF 再核对：

| 文件 | 页数 | 字节数 | SHA-256 |
|---|---:|---:|---|
| main.pdf | 33 | 541972 | `768f90e9002645971da75299759fc5825da4b8dd764525a5e51d00c0b31203a6` |
| supplement.pdf | 21 | 314901 | `074a8cb4bd7a34fdf32619a1c08e64e47792b0cc9d0eee574cc6e57b6d713aee` |

最终 Methods 保留一句 Figure 2 数据来源、脚本、Matplotlib 3.10.8 和 OpenAI Codex（GPT-6, OpenAI）披露；图注和文末声明继续保留。最终 PDF 再查无 `??`、批注、页外文字块，最终两份日志上述警告计数均为 0。
