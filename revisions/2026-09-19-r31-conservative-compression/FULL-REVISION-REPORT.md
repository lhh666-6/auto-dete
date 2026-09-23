# r31 全文保守压缩与润色报告

已完成正文逐节润色。已投稿 r31 原稿保持不变；此目录是独立修改稿，未发布到论文工件仓库。

## 结果

- 主文：**60 → 53 页**，减少 7 页（11.7%）；仍比期望的 48–52 页上限多 1 页。
- 正文叙述：**9,617 → 7,936 词**，减少 **17.48%**。
- Supplement：**20 → 22 页**。新增 S4 原样保存 8 段执行设置、范围向量、工作负载网格及历史验证计数。
- 摘要：采用用户确认的最终候选，188 → 180 词；本轮未再次修改。
- 每节的 scientific claim 影响核对：**No**。这表示编辑比对未发现科学含义改变，不表示本轮重新运行了实验或证明。

计数只覆盖第 1–10 节正文叙述（含 contribution 标题和 RQ 问句），不计章节标题、数学表达式、表格、图注、引文/交叉引用标记、Declarations 和参考文献。连字符和斜杠复合词按一个空格分词单元计数。前后使用同一程序；字数下降不等同于页数下降。

## 分节统计与逐段记录

逐段记录列出 KEEP / COMPRESS / MOVE-SUPP / DELETE、理由、原段落、修改后的英文；迁移段另列正文保留版本及 Supplement 位置。

| 部分 | 原字数 | 修改后 | 压缩比例 | 影响 scientific claim | 逐段记录 |
|---|---:|---:|---:|---|---|
| Introduction | 551 | 457 | 17.06% | No | [查看](reviews/01-introduction.md) |
| Related Work | 940 | 794 | 15.53% | No | [查看](reviews/02-related-work.md) |
| Contract | 1,789 | 1,591 | 11.07% | No | [查看](reviews/03-problem-contract.md) |
| Bounded relational characterization | 643 | 517 | 19.60% | No | [查看](reviews/04-relational-analysis.md) |
| Transactional realization | 876 | 709 | 19.06% | No | [查看](reviews/05-transactional-realization.md) |
| Formal–concrete conformance | 525 | 414 | 21.14% | No | [查看](reviews/06-formal-concrete-conformance.md) |
| Evaluation Protocol | 1,698 | 1,361 | 19.85% | No | [查看](reviews/07-evaluation-protocol.md) |
| Results | 1,615 | 1,294 | 19.88% | No | [查看](reviews/08-results.md) |
| Discussion / Threats | 808 | 664 | 17.82% | No | [查看](reviews/09-discussion-threats.md) |
| Conclusion | 172 | 135 | 21.51% | No | [查看](reviews/10-conclusion.md) |

[摘要阶段记录](abstract-review.md)与[引言详细记录](introduction-review.md)保留此前编辑过程。Declarations 和既有 Supplement S1–S3 均为 KEEP：保留作者贡献、伦理、AI 披露、数据可用性以及原有复现说明。

## 主要调整

1. Related Work 精简背景教学和重复总结，保留原有 54 个引用键，不新增文献结论。
2. Contract 保留定义、五类观察、Proposition 1 与证明，只压缩周围解释和重复限定。
3. Realization / Conformance 集中呈现实现义务和证据边界，保留 CAS、独立 oracle、no-op、schema uniqueness 及 prefix tracing 的差异。
4. Protocol 将环境小版本、连接参数、完整成本/并发网格移至 Supplement S4；正文保留设计、判据、样本量及主要比较逻辑。
5. Results 保留数值、比例、区间、分母和关键对照结论，减少重复的方法解释；版本化测试历史在 Supplement S4 完整保留。
6. Discussion 合并重复措辞，但保留所有真实适用边界、未测试对象、作者参与标注限制和宿主假设。

## 重复信息的主叙述位置

| 内容 | 主叙述位置 | 其他位置的处理 |
|---|---|---|
| Admission relation / canonical equality | Contract | Abstract、Introduction 只保留贡献和直观动机；Realization 引用定义。 |
| 五类 irredundancy 与适用边界 | Contract / Proposition 1 | Alloy 只解释编码检查，Discussion 保留外推限制。 |
| 相邻工作的机制和定位 | Related Work | Introduction 保留引用和简述。 |
| 两种对照及 equal-valued substitution | Results RQ5 | Protocol 说明构造，Discussion 解释 richer-context 边界。 |
| 行为 endpoint、计分、标注和分母 | Evaluation Protocol | Results 报告结果，Discussion 保留构念和依赖性限制。 |
| 完整参数、网格、历史验证版本 | Supplement S4 与原有 artifact | 正文保留摘要和明确指引。 |
| Trust boundary / revocation timing | Contract | 方法和 Discussion 保留使用该假设的必要提示。 |

## 科学内容保护检查

- 33 个图像、表格源文件、参考文献库及 Declarations 文件与投稿包逐字节相同。
- 所有 displayed equation / align、内嵌表格、图和图注、description 环境保持原文；包括 RQ1–RQ8 和 endpoint 定义。
- Proposition 1、proof sketch、irredundancy 公式及其中论证保持原文。
- 原始引用键集合不变，54 个键全部存在于 bibliography。
- Supplement S1–S3 全文不变；8 个迁移段落在 S4 中逐字比对通过。
- 数值词法检查的三处提示已逐项解决：重复的 canonical-equality 示例仍在 Contract；11 改写为英文 eleven 而数值未变；T153 的提示只是正则截取了编号尾部。
- 没有运行新实验、改变原始记录或覆盖已投稿论文。

[机器核对记录](reviews/verification.json)；[完整源文件 diff](reviews/manuscript.diff)。

## 编译与版面检查

主文和 Supplement 均由 LaTeX 成功编译：无错误，无未定义引用/交叉引用，无 overfull box。主文有一处 underfull hbox（badness 1194，Storage protocol，PDF 第 31 页）；已放大检查，未见遮挡或溢出。75 页均查看了缩略图，并对关键公式、结果和新增补充页进行放大检查。

本机现有 MiKTeX 在沙箱内无法读取安装配置；沙箱外首次运行又缺少 Perl 路径。随后使用已安装的 D:/Git/usr/bin/perl.exe，仅补充当前编译进程 PATH，成功完成编译；未安装新依赖或更改论文排版参数。

### LaTeX 技术质量评分

| 指标 | 结果 |
|---|---|
| Score | 99 / 100 |
| Verdict | Ship（仅指编译与版面技术检查，不代表期刊录用判断） |
| 扣分 | 一处 underfull hbox，-1 |

## 交付物

- [主文 PDF](paper/main.pdf)
- [Supplement PDF](paper/supplement.pdf)
- [主文 LaTeX](paper/main.tex)
- [完整可编辑稿件包](r31-polished-source.zip)

稿件包包含编译所需源文件、原图表、参考文献和两份成品 PDF；中间编译文件与内部编辑脚本不包含在稿件包内。
