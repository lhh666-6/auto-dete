# 写作风格审阅报告 — Auto-Decte JSS 投稿稿

- 审阅对象：`D:/Claude_Design/autodecte-b1/review-c5e891c4/latest/paper/`（= `origin/main` 的 `61f99f72`）
- 审阅方式：**只读**。未修改任何论文文件、未提交、未推送。
- 探针脚本（本次新建，只读）：
  - `D:/Claude_Design/autodecte-b1/tools/style_probe.py` → `reports/style-probe-2026-09-11.txt`
  - `D:/Claude_Design/autodecte-b1/tools/readability_probe.py` → `reports/readability-probe-2026-09-11.txt`
- 所有数字可由上述两个脚本重跑复现。词频为**字面精确计数**；句子切分基于正则，属近似（已在文中标注）。

---

## 0. 结论速览

| 维度 | 结论 |
|---|---|
| 论文类型 | methods / 设计科学（problem → contract → realization → evidence） |
| 去 AI 化（18 类模式） | **通过，且异常干净**：18 类特征词命中 0 次 |
| 语法/标点/术语一致性 | 基本通过；2 处低优先级瑕疵 |
| 句子长度 | 健康（中位 18 词，仅 4.2% ≥40 词） |
| **限定语密度** | **主要问题**：否定 17.1/千词（§9 达 37.5/千词） |
| 从句堆叠 | 次要问题：分号每 82 词一个 |
| 主张—证据一致性 | 未见 over-claim |

一句话：**这不是"写得不好"，而是"限定得太平"。** 论文的问题不是缺少谨慎，而是谨慎没有分级——真正关键的限定与例行限定用了完全相同的语气，读者无法分辨哪一个是要害。

---

## 1. 论文类型与叙事弧

- 类型：**methods**（问题→现有缺陷→契约→验证→边界），不是 discovery。
- 叙事弧完整：§1 提出候选—授权—值三元关系 → §3 形式化契约 → §4 有界关系验证 → §5 事务实现 → §6 形式—具体投影 → §7 评测协议 → §8 结果 → §9 边界。
- 章节标题全部句首大写，一致 ✓
- C1–C5 贡献列表结构平行（名词短语 + 陈述句）✓

---

## 2. 去 AI 化检测（18 类模式）

**结论：0 命中。**

对 `sections/*.tex` + `main.tex` + `supplement.tex` 做词边界、大小写不敏感扫描，以下全部为 0：

```
delve  intricate  nuanced  pivotal  leverage  robust  multifaceted
commendable  seamless  groundbreaking  revolutionary  unprecedented
transformative  holistic  paradigm  realm  landscape  underscore
showcase  myriad  comprehensive  meticulous  furthermore  moreover
in conclusion  in summary  taken together  in recent years
state-of-the-art  it is worth noting  to the best of our knowledge
```

唯一含 "additionally" 的 10 处，全部是句中副词（"additionally traverses…"），**没有一处是段首填充词**。

摘要首句直接给问题（"AI-derived record updates must distinguish a machine proposal from the value a human authorizes."），没有 "In recent years" / "With the rapid development of" 式开场 ✓

**这是这篇稿子最强的一项，不需要任何"去 AI 化"处理。**

---

## 3. 语法 / 标点 / 术语一致性

已核对，**基本通过**：

| 检查项 | 结果 |
|---|---|
| 双空格 | 无（grep 命中的全是缩进） |
| 引号 | 统一用 LaTeX 反引号对（``…''），4 处一致 ✓ |
| `e.g.` / `i.e.` / `et al.` 用法 | 正文 0 处；`et al.` 由 `authoryear` 样式生成，非正文问题 ✓ |
| 连字符一致性 | `per-field` / `per field`、`value-audit` / `value audit` 的分歧**是合法的**（定语 vs 名词），非错误 |
| 数学环境编号 | 未见重复标签（构建日志 0 multdef） |

**低优先级瑕疵 2 处：**

1. **§2 中 "Auto-Decte" 用普通字体书写 4 次**（`02-related-work.tex:8,10,14,16`），其余章节统一用 `\system{}`（小型大写）。同一稿内两种字形。
2. **同名 run-in 标题重复**：`\paragraph{Admission}`、`\paragraph{Reverse trace}`、`\paragraph{Storage}` 在 §7 与 §8 各出现一次（全文共 22 个 `\paragraph{}`）。读者在目录/交叉引用时无法区分。

---

## 4. 主要问题：限定语密度（核心发现）

### 4.1 数据

以散文段落为口径（已剔除浮动体、公式、表格、图注），全文 **12,339 词 / 643 句**：

| 章节 | 句数 | 词数 | 否定次数 | **否定/千词** | 限定装置/千词 |
|---|---|---|---|---|---|
| 01 Introduction | 35 | 678 | 6 | 8.8 | 22.1 |
| **02 Related work** | 62 | 1209 | 11 | **9.1** | 14.9 |
| 03 Contract | 114 | 2177 | 39 | 17.9 | 22.5 |
| 04 Relational | 38 | 753 | 11 | 14.6 | 27.9 |
| 05 Realization | 47 | 967 | 14 | 14.5 | 18.6 |
| 06 Projection | 31 | 520 | 7 | 13.5 | 30.8 |
| 07 Protocol | 109 | 2066 | 37 | 17.9 | **32.9** |
| 08 Results | 111 | 2080 | 33 | 15.9 | 26.9 |
| **09 Discussion** | 60 | 1172 | 44 | **37.5** | **38.4** |
| 10 Conclusion | 10 | 173 | 0 | 0.0 | 34.7 |
| Declarations | 26 | 544 | 9 | 16.5 | 22.1 |
| **全文** | **643** | **12339** | **211** | **17.1** | **26.3** |

**内部对照（最有说服力的一点）**：§2 描述**他人的工作**时，否定密度是 9.1/千词；§9 描述**自己的限度**时是 37.5/千词——**4 倍**。同一作者、同一文体、同一篇论文。差别不在写作能力，而在"写自己的东西时自动进入防守模式"。

### 4.2 旁证：限定词字面频次

```
separate / separately / separated ........... 60
declared ..................................... 53
frozen ....................................... 37
remain / remains ............................. 35
only ......................................... 31
rather than .................................. 19
outside the / outside this ................... 8
external assumption .......................... 5
```

**"separate" 出现 60 次**——全文最高频的限定词。论文不厌其烦地告诉读者"这两件事是分开的"。

### 4.3 结构性后果：连续否定

**15 个段落存在 ≥3 句连续否定句**。最长的一组在 §9：连续 4 句、加上紧随其后的 3 句，一段之内 7 句否定。

读者扫读时，连续否定句会被读成"这一节什么都没证明"，而不是"这一节精确地划定了三条边界"。

---

## 5. 具体建议（**均为建议，未执行**）

> 归属提示：下面第 1、2、4 条涉及的三段，`git blame` 显示最后修改者均为第二作者 `c5e891c4`（XWT）。改动前需要他同意。

### 建议 1｜§7.3「Primary endpoint definitions」拆成定义列表 ★最高收益

- 位置：`07-evaluation-protocol.tex:45`
- 现状：**单段 225 词 / 10 句**，一口气定义 5 个构念（behavior-evaluable、strict-trajectory task completion、endpoint completion、authority-evaluable、unauthorized authoritative mutation）
- 这是 RQ8 全部可读性的枢纽段落，也是全稿最难读的一段
- 建议：改用论文**已经在用的** `description` 环境（RQ1–RQ8 列表就是），一个构念一条。**不增删任何内容，只重排**。
- 风险：极低。

### 建议 2｜§9.3 开头重构：先给成立的结论，再归并否定

- 位置：`09-discussion-threats.tex:22`
- 现状：9 句，其中 4 句连续否定；唯一正面结论（"independent oracles reduce shared-code risk"）被压在从句里
- 建议方向（示意，非最终措辞）：

  > 现在：`Independent oracles reduce shared-code risk but cannot exclude shared semantic defects, as the repaired value-equality error illustrates. Trace completeness establishes consistency among persisted relations, not evidence truth, … The admission adapter …; it does not re-read and hash external evidence bytes …`
  >
  > 建议：把三条边界**合并为一句总括**，正面结论提到主句：
  > `The two oracles are independent of the production planner and trace builder, which reduces shared-code risk; the repaired value-equality error shows that a shared semantic defect can still pass both. Three limits follow: trace completeness establishes consistency among persisted relations rather than evidence truth or sound human judgment; the adapter compares persisted digests and canonical locators without re-reading external bytes, so an out-of-band replacement that leaves stored metadata intact is undetected; and byte-level integrity therefore needs immutable or content-addressed storage.`

- 要点：**没有删掉任何一条限定**，只是从"5 个独立否定句"变成"1 个总括 + 3 个并列分句"。
- 风险：低（同义改写）。

### 建议 3｜双重否定句必须拆开

- 位置：`09-discussion-threats.tex:40`
- 现状：

  > `Our claim is therefore neither that transactional auditing cannot preserve proposal or review context nor that exact candidate identity is the only possible discriminator; …`

  一个句子里有 `neither` + `cannot` + `nor` + `only`，读者需要做 4 次逻辑翻转。

- 建议（等价改写为正面陈述）：

  > `Transactional auditing can preserve proposal and review context, and exact candidate identity is one of several possible discriminators. Candidate-level binding becomes material when several persisted candidates remain equivalent under the observations the review mechanism records.`

- 风险：低。语义已逐项对照原文，未增减主张。

### 建议 4｜分号拆句（150 处中挑约 30 处）

- 现状：**分号 150 个（每 82 词一个）**，**109 个冒号（每 113 词一个）**；19.1% 的句子含分号。
- 分号在本稿中的用法是"把两个独立断言焊进同一句"，读者必须在同一句内切换两次论述对象。
- 典型样本（`05-transactional-realization.tex:30`）：

  > `Schema constraints provide additional defense in depth: among other relations, fact transitions and authorization bindings have unique decision and certificate indexes, and transition identity is unique per record/version/field.`

- 建议判据：**分号两侧主语不同 → 拆成两句**；主语相同 → 保留。
- 风险：低。

### 建议 5｜恢复第一人称（需要作者决定）

- 现状：**"we" 全文 15 次 / 15,468 词 = 0.97/千词**；"our" 14 次。绝大多数句子以 `The contract / The implementation / The projection / The study / This construction` 开头。
- 后果：读者分不清"我们做了什么"与"系统做了什么"。
- 建议：在**"我们选择/我们发现/我们限定"**处恢复 `we`；在"系统执行了什么"处维持被动。目标 ~40 次。
- 风险：**中**。这涉及作者声音，且与 JSS 惯例有关，需要两位作者同意。**可选项，不是必须。**

### 建议 6｜低优先级清理

- `\paragraph{Admission}` / `{Reverse trace}` / `{Storage}` 在 §7、§8 各出现一次 → §8 改为 `Admission cost` 等，或 §7 加 `protocol` 后缀
- §2 的 4 处普通字体 "Auto-Decte" → 统一为 `\system{}`

---

## 6. 哪些限定**不能改**

这一点比上面所有建议都重要。以下否定的**承重**，删掉就会变成 over-claim：

| 位置 | 句子 | 为什么必须保留 |
|---|---|---|
| `04-relational-analysis.tex:42` | `Precondition reachability, the absence of a counterexample in the encoded scope, and sensitivity to one removed conjunct are therefore three separate results rather than one proof.` | 删掉即暗示"这是证明" |
| `03-problem-contract.tex:198` | `This is the declared scope rather than an implementation gap` | 删掉即暗示实现有缺陷 |
| `main.tex` 摘要 | `do not by themselves entail an explicit authorization-to-exact-candidate relation` | 这是 C5 的全部要害 |
| `09-discussion-threats.tex:32` | `Agreement of that separate review with the strict rule does not resolve the distinction between terminal completion and strict-trajectory compliance.` | 对应 320/335 vs 335/335 的核心区分 |
| `08-results.tex:102` | `This observed increase is a consequence of a more permissive alternative criterion, not an unbiased correction` | 对应 endpoint sensitivity 的解释权 |

**本报告建议的是"归并"和"重排"，不是"削减总量"。** 全文否定密度从 17.1 降到 11–12/千词是健康的；降到 5/千词会直接把稿子变成 over-claim。

---

## 7. 优先级与风险

| 优先级 | 动作 | 风险 | 影响面 | 需要谁同意 |
|---|---|---|---|---|
| **P1** | §7:45 定义段改用 `description` 列表 | 极低 | 1 段 | XWT |
| **P1** | §9:22 段重构（正面结论提主句 + 归并否定） | 低 | 1 段 | XWT |
| **P2** | §9:40 双重否定句拆开 | 低 | 1 句 | XWT |
| **P2** | 分号拆句（挑约 30 处） | 低 | 多段 | 双方 |
| **P3** | run-in 标题去重 | 极低 | 7 个标题 | 双方 |
| **P3** | §2 字体统一 | 无 | 4 处 | 双方 |
| **可选** | 恢复 `we` | 中 | 多段 | 双方 |
| **不做** | 削减限定语总量 | 高 | 全文 | — |

### 关于"现在要不要改"

- 若要"审稿人第一遍读得懂"：**只做 P1**（2 段），收益/风险比最高。
- 稿子已由第二作者签过字，P1 改的是**他写的段落**，需要他同意后再动。
- 一旦改动正文，按既有流程需要：重建 PDF → 重封 `latest/MANIFEST` → 重跑 `verify_latest.py` / `verify_release.py` / `pytest` → 推送 `origin HEAD:main`。
- 若决定投稿前冻结：P3 可以留到 proof 阶段。
