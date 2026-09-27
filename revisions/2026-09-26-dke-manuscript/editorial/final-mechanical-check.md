# 最终身份澄清与机械一致性检查

日期：2026-09-27。基线：`4701ec8241acd8e38f20968ff1df8dfe9ef2f246`。

## 五处局部修改

1. Section 3.1：将 “identity over the modeled candidate content” 改为精确持久化候选实例的身份；提案值和保留审查上下文相同，仍区分不同实例。
2. Section 3.2：certificate/stable handle 的要求明确为保留实例区分，去掉容易被理解为按内容合并的 “another equivalence class”。
3. Section 5.1：`c_id` 抽象具体的 `certificate_id`；后者摘要覆盖完整规范证书，包含持久化实例标识 `candidate_id`、创建时间及提案。
4. Supplement S2.2：明确 Alloy 的不同 certificate 对象有不同 `CertId`，即使 modeled content 相同。没有改变模型或散列假设。
5. Section 7.1：只删除 Figure 2 的重复工具/版本句。Figure 2 caption 和文末 Declaration 保持原文。

## 身份关系的依据

检查固定实现提交 `c6d512843c905cab6d8521dd8c914f7fb26d85ae`：

- `app/domain/authority.py` 的证书规范内容包含 `candidate_id` 和 `created_at`，`certificate_id` 摘要覆盖该完整内容。它不是仅对提案值或保留审查上下文计算的摘要。
- 已存档 Alloy `certIdentityFacts` 要求相同 `certId` 只能指同一 certificate 对象；相同 modeled content 不会令两个不同对象合并。
- `observation_witnesses.py` 的身份隔离对固定候选池与其他字段，仅改变被选候选身份。重检通过：五类 pairs、额外 identity pair 和 copy-forward domain/control checks。

EID 仍表示证据内容摘要加规范定位信息，没有与候选身份合并。没有新增身份生成算法、约束、命题或实验。

## 机械检查结果

Scientific claim affected: **No**。

- 41 个受保护文件与基线逐字节一致；所有表格、CSV、图文件、科研脚本和参考文献均未改动。
- 所有显示公式、Proposition 1、证明、batch relation、P0–P6、RQ、Abstract、Results、Conclusion 保持原文。实验数值未变化。
- Figure 2 caption、图 1 caption 和 AI Declaration 未改动；7.1 段落中不再出现工具披露。
- 再核对已有 495 条 E1 原始 receipts：每机制 165 次，exact/reference 165 对决定与 query-answer sets 一致，15 个 substitutions 分开政策；context/exact/reference 接受数仍为 60/45/45。拒绝均无事实数据库写入。
- LaTeX input 路径、图路径、标签与交叉引用全部解析；26 条实际引用均有对应 BibTeX 条目，无缺失或未用条目。
- 使用本机 MiKTeX 重新编译正文与补充材料，均无未解析引用、LaTeX warning、overfull 或 underfull box。正文 32 页，补充材料 21 页；字号、页边距、图尺寸和参考文献样式未改变。
- 正文 PDF 提取词数 8,509→8,512，补充材料 6,086→6,084。仅反映这五处局部修改，不是重新压缩目标。

详细替换内容、编译散列及检查结果见 [final-mechanical-check.json](final-mechanical-check.json)。此前 `submission-closeout*` 对应提交 `4701ec82` 的历史检查。
