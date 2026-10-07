# KAIS 投稿材料核对单

核对日期：2026-10-07。本文材料已进入收尾阶段；本清单不表示已经完成作者签字确认或期刊系统提交。最终上传文件以本轮编译、打包和 [artifact manifest](../reproduction/ARTIFACT-MANIFEST.json) 为准。

**稿题：** Review-to-Execution Continuity for Corrected Agent State Changes
**作者顺序：** Liang Hanghao；Xuan Wentao；Chen Qile；Peng Peng
**通讯作者：** Peng Peng，hnu16pp@hnu.edu.cn
**单位：** College of Computer Science and Electronic Engineering, Hunan University, Changsha 410082, China

## 文件入口与交付状态

| 材料 | 当前入口 | 上传前核对 |
|---|---|---|
| 主文 | [main.pdf](../../revisions/2026-10-07-kais-followup/main.pdf) | 最终版本 12 页，已重新编译并检查修改页；摘要 184 个空白分词。 |
| 可编辑源包 | [KAIS-editable-sources.zip](../../revisions/2026-10-07-kais-followup/KAIS-editable-sources.zip)；[构建说明](../../revisions/2026-10-07-kais-followup/README.md) | 包含主文、SI、所需图形和样式/构建依赖；不要把原始轨迹档案误作排版源包。最终 CRC、成员清单和哈希以打包收据为准。 |
| 补充材料 | [supplement.pdf](../../revisions/2026-10-07-kais-followup/supplement.pdf) | 当前版本 29 页，正文以 Online Resource 1 引用；检查封面信息与描述，上传名可使用 `ESM_1.pdf`。 |
| Fig. 1 概念图 | [矢量 PDF](../../revisions/2026-10-07-kais-followup/figures/revised-figure1-concept.pdf) | 概念构造；不标为实测结果。 |
| Fig. 2 在线配对设计 | [矢量 PDF](../../revisions/2026-10-07-kais-followup/figures/revised-figure3-online-loop.pdf) | 图号以正文 Fig. 2 为准，源文件保留历史命名。 |
| Fig. 3 恢复与成本 | [矢量 PDF](../../revisions/2026-10-07-kais-followup/figures/followup-behavior-comparison.pdf) | Original B 与 supplementary A 分开显示；calls 为均值，seconds 为中位数。 |
| 图形源与数据核查 | [图形目录](../../revisions/2026-10-07-kais-followup/figures/)；[对应关系](../reproduction/ARTIFACT-MAP.md) | 三张正文图的字体全部嵌入；本轮保留图形字节并检查正文显示。上传使用这里的正式导出件。 |
| 数据/代码入口 | [复现指南](../../REPRODUCIBILITY.md)；[实际验证报告](../reproduction/REPRODUCTION-VERIFICATION-2026-10-07.md) | 数据可用性声明应指向固定 release/commit，下载两个原始档案，保留其哈希。 |
| Cover letter | [COVER-LETTER.md](COVER-LETTER.md) | 英文稿已备；通讯作者复核后使用。 |

## 官方格式要求与本稿状态

KAIS 要求提交可编辑源及编译 PDF，摘要 150–250 词、关键词 4–6 个；作者贡献和利益冲突还需填入投稿系统。SI 应含文章/期刊/作者及通讯信息，并配说明。数据可用性声明需说明访问方法。作者名单与提交资格应在正式上传前核实。[官方投稿指南（本次核对）](https://link.springer.com/journal/10115/submission-guidelines)

| 项目 | 当前检查 | 最终动作 |
|---|---|---|
| 摘要 | 最终 `main.tex` 按空白分词为 184 词，校验器分词为 185 词，均在区间内。 | 在投稿系统粘贴同一版本。 |
| 关键词 | 6 个：trustworthy agents；review-to-execution continuity；human authorization；transactional execution；provenance；agent recovery。 | 最终 PDF 与投稿系统保持一致。 |
| 标题页 | 当前源含四位作者、单位、通讯邮箱。 | 作者核对拼写、顺序、单位及可用 ORCID；不擅自补写标识符。 |
| 格式与图形 | 当前为双栏 article 排版，主文 3 图、3 表；图形为程序绘制的矢量输出。 | 最终布局与投稿系统要求核对；期刊模板转换/图形格式调整须保留科学内容。 |
| SI | 首页含稿题、期刊名、四位作者、单位及通讯邮箱；独立 S 编号保留。 | 上传使用同一最终文件和 Online Resource 1 描述。 |
| 文献 | 本轮稿保留 20 个编号参考文献；Table 1 的四个外部来源已重新核对，[对应记录](NEARBY-SOURCE-CHECK.md) 可查。 | 三篇近邻研究保留预印本标识；按投稿系统要求核对文献处理方式。 |

## 科学报告与可用性边界

- [x] 原始 512 arms、后续 117 pairs / 234 arms 和 S13 事后敏感性分析分别标注，不把补采静默替换为原冻结主分析。
- [x] 原始失败、未知完整性结果、补采失败和请求重试记录保留；pilot 不进入正式效应分析。
- [x] 离线复现入口、环境锁、冻结身份、档案哈希、图表来源映射与实际验证结果已有独立文档。
- [x] 最终主文保留既有冻结 commit，并加入固定版本复现指南；指南分别列出原始/补采档案和历史审计入口。未使用未分配的 DOI。
- [x] 最终正文 12 页、SI 29 页；源包 188 个成员，CRC 与成员哈希核查通过。29 项论文证据检查通过；本次仅更新摘要词数及关联图源校验元数据，研究结果与图形不变。

## 需要作者最终确认的声明

以下是现有稿件中的陈述或投稿前应核实的事实，不由自动整理替作者确认。

- [ ] 四位作者确认最终文本、作者顺序、CRediT 贡献和通讯安排；确认所有作者及相关单位同意投稿。
- [ ] 确认原创性、既往发表/相关稿件状态及当前未被其他期刊同时审理；如有需要披露的相关材料，由通讯作者说明。
- [ ] 逐人核实“无外部资助”和“无竞争性利益”陈述；把确认后的作者贡献与竞争性利益录入投稿界面。
- [ ] 核实历史标注参与者的知情情况、志愿参与、伦理审批适用性及稿内表述；不把作者此前判断转写为机构出具的批准。
- [ ] 核实非作者帮助、致谢、资金信息和任何转载材料权限；不代写或自动确认不存在需要致谢的人。
- [ ] 复核 AI-assisted preparation 段覆盖实际用途及人工责任：最终源提及 DeepSeek、OpenAI/Codex 对代码、分析检查、文献组织、图形准备和写作修订的辅助；已按作者更正移除 Claude。
- [ ] 通讯作者复核 cover letter、最终文件名与投稿系统字段；作者完成最终确认后再实际提交。

当前 AI 辅助涉及范围超过单纯拼写/语法润色；稿内已有专门说明。应由作者核对披露的准确性与位置，确保最终研究内容由作者负责。[KAIS 关于 LLM 使用的说明](https://link.springer.com/journal/10115/submission-guidelines)
