# 压缩 + 叙事重组 执行方案 v2

> v1 = `reports/STYLE-REVIEW-2026-09-11.md` 第三节的研究线与压缩建议。
> v2 按作者 2026-09-11 修正重写。**v2 取代 v1 中所有与本文件冲突的表述。**
> 本文件为方案文档，未改动论文任何文件。

---

## 0. v1 的四处修正（先记下来，避免再犯）

| # | v1 的错误表述 | v2 的正确表述 | 为什么危险 |
|---|---|---|---|
| 1 | 五类信息**各自不可省** | 五类信息**在 declared observation/failure model 内分别表现出 class-wise irredundancy** | 前者是 universal necessity，会把刚收紧的 Proposition 1 重新放宽 |
| 2 | 7/8 + equal-valued substitution **证明了本文关系的必要性** | **the evaluated safeguard bundle does not by itself entail the exact-candidate authorization relation** | separator 是 relation-level non-entailment 的证据，不是 universal necessity 的证明 |
| 3 | C5 改名 `The separating case` | C5 改名 **`Evaluated-control separation`** | `The separating case` 把全文压扁成"就靠一个 edge case"，会招来"63 页就为这一个 case？" |
| 4 | 边界声明只在 §9 写一次，其他章节只允许 `\cref` | **local qualifier once + full boundary once** | 局部限定必须与 claim 绑定，否则为了压页数反而制造新的 overclaim 风险 |

**归属澄清**：v1 的第 1、2 条是**我的转述错误，不是稿子的错误**。原稿的措辞已经是收紧的：

- `main.tex` 摘要：`The evaluated transactional value-audit safeguards do not by themselves entail an explicit authorization-to-exact-candidate relation.`
- `03-problem-contract.tex:161-162`：`It does not establish universal minimality, schema uniqueness, or completeness over all possible admission failures.`

所以本轮**不需要"再收紧一次"**，只需要保证后续编辑不把它改松。

---

## 1. 研究线（P0）——全文唯一骨架

```
1. Authority ambiguity
2. Admission-relation gap
3. Contract + declared observation basis
4. Conditional characterization + evaluated-control separation
5. Transactional realization + multi-layer validation + boundary/cost
```

对应到证据路径：

```
semantic → relational → persisted → engineering
```

| 步 | 一句话 | 主要章节 |
|---|---|---|
| 1 Authority ambiguity | AI 候选与人类授权值可能不同；等值时归因仍可能不同 | §1 |
| 2 Admission-relation gap | 现有机制各自覆盖一部分，没有联合绑定 候选身份+双值归因+新鲜度+批量原子性+源全量 | §2 |
| 3 Contract + declared observation basis | 把义务形式化为 P0–P6，并声明观察/失败模型 | §3 |
| 4 Conditional characterization + evaluated-control separation | 五类信息在 declared model 内 class-wise irredundant；evaluated safeguard bundle 不蕴含 exact-candidate 授权关系 | §3.3、§4、§8 |
| 5 Realization + validation + boundary/cost | 事务实现、形式—具体投影、多级验证、成本与集成、完整边界 | §5–§9 |

**P0 的验收标准**：读者从 §1 末尾就能看到完整五步；每一级验证开头有一句 signpost 回指。

---

## 2. 措辞红线（claim ladder）

编辑时逐条对照。左列是稿子里**已经正确**的表述，右列是**任何改写都不得滑向**的方向。

| Claim | ✅ 允许的最强表述 | ❌ 禁止 |
|---|---|---|
| Proposition 1 | 五类信息在 declared observation/failure model 内 class-wise irredundant | 五类信息各自不可省 / 必需 / universal necessity / 完整分类 |
| Prop 1 证明方式 | paired-history construction；bounded witness | 证明了 / 完整刻画 |
| 7/8 + equal-valued substitution | evaluated safeguard bundle does not by itself entail the exact-candidate authorization relation；equal-valued substitution is the separating case | 证明本文关系必要 / 唯一可行方案 / 优于现有机制 |
| Alloy RQ1–RQ2 | bounded separation within encoded scopes | 形式化证明 / 全面验证 |
| 35-case catalogue | 声明范围内全部通过 | 实现无缺陷 / 已充分测试 |
| 320/335 | conditional on behavior-evaluable runs | 完成率 95.52%（无限定） |
| 0/720、0/179 | counts of executed host operations | 安全 / 零风险 / 无漏洞 |
| 人工标注 | author-involved blinded annotation | independent third-party validation |
| 成本 RQ6 | recorded v8 configuration on the frozen grid | 通用性能结论 / 优于 baseline |
| 可移植性 | exercised SQLite configuration | 支持其他 DBMS / 引擎无关 |

**注意右列的 `优于现有机制`**：这是 v1 里我给 C5 提出的"改名 + 作为正面发现"思路的残留风险。`Evaluated-control separation` 的好处正是它说的是**分离边界**，不是**优劣比较**。

---

## 3. P1 执行项

### P1-a｜§2 Related work：6 页 → 约 4 页

**依据**：§2 共 18 段，其中 **10 句**是同一件事的重复自我定位：

```
Auto-Decte narrows this general activation problem to ...
Auto-Decte instead centers an explicit candidate-bound human authorization ...
We specialize that insight to the construction of a record successor ...
Auto-Decte's unit of analysis is the exact candidate--human authorization--authorized value chain ...
Auto-Decte addresses the construction of a field-level authoritative successor ...
Our characterization adds the joint candidate, authorized-value, and complete-successor relation.
Our harness and repeated-agent experiments mount candidate proposal ...
Our contract uses lineage prospectively ...
We distinguish the abstract admission relation, a test-side projection ...
Our per-conjunct ablations apply this idea to the finite encoding ...
```

**改法**：

1. 前 ~80% 各段**只回答"别人解决了什么"**，删除段尾的 self-positioning 句，保持客观、不踩一贬一。
2. 末尾加**一个统一 synthesis paragraph**，集中回答"我们与它们到底区别在哪里"，用一条链收束：

   ```
   activation · transaction · provenance · authorization
   各自提供部分机制，
   本文研究的是它们之间这个特定组合关系：

   c → a(c, x_a) → S_{v+1} → field-source attribution
   ```

**预计**：省 1.5–2 页。
**风险**：低（删重复，不删内容）。
**注意**：§2 的 10 句是第二作者 `c5e891c4` 的文本，改动需其同意。
**附带收益**：这一项同时修掉了 v1 文体报告里"§2 否定密度 9.1/千词 vs §9 37.5/千词"的部分成因——重复的自我定位句本身就带防御性。

### P1-b｜Abstract 重排（7 步）

严格按此顺序，不增不减：

| # | 步骤 | 现状 |
|---|---|---|
| 1 | **Problem** — AI proposal 与 human-authorized value 可能不同 | 已在第 1 句 ✓ |
| 2 | **Contract** — 定义 authoritative-state admission | 已在前段 ✓ |
| 3 | **Characterization** — five classes 在 declared model 内 class-wise irredundant | 已有，位置偏前 |
| 4 | **Realization + validation** — transactional realization + Alloy + concrete evidence | 已有 |
| 5 | **最关键 control finding** — evaluated audit safeguards 7/8 但 `⊭` exact-candidate authorization | **需要前移**（现约第 8 句） |
| 6 | **Cost / integration** — 一句带过 | 已有（可压缩） |
| 7 | **Boundary** — exact candidate binding 在 review-observation equivalence 下 material；不声称 universal necessity | 现在占 3 句，压成 1 句 |

**目标**：reviewer 在摘要约**一半位置**就看到论文最锋利的 finding。
**注意**：第 5 步的 entailment 句**原样保留**，不要改写；只需移动位置。

### P1-c｜C5 改名为 `Evaluated-control separation`（**保持 C5 编号**）

**建议文本**（作者提供）：

> **C5. Evaluated-control separation.** Strengthening the evaluated transactional value-audit safeguards preserves agreement on seven of eight single-history probes but does not by itself entail an explicit authorization-to-exact-candidate relation; equal-valued candidate substitution provides the separating case, while richer recorded review context narrows that separation.

**逻辑**：

```
研究贡献 = 找出 evaluated controls 与目标 relation 的分离边界
        ≠ 发现一个特殊 case
```

**术语一致性提示**：建议文本用的是 `single-history probes`，但稿子现有术语是：

- `08-results.tex:42`：`single-history outcomes`
- 摘要：`single-history cases`
- `09-discussion-threats.tex:40`：`single-history cases`

落地时统一成 `single-history cases`（或全文统一改），避免引入第三种说法。

**不做**：不把 C5 从第 5 项挪到 C2/C3。临近 freeze 重新编号会牵动 Figure 2、Introduction、Results、Discussion、Supplement、artifact commentary，churn 大于收益。**"前移"= 叙事前移，不是编号前移。**

### P1-d｜Introduction 增加极短 research-roadmap paragraph

在 §1 末尾加 **3 句**因果链（不是再列一遍 C1–C5），例如：

> 本文的研究线是：先给出一个精确的准入关系（§3），再问缺少哪一类可观测信息就无法区分安全与不安全历史（§3.3），然后在 relational / persisted / engineering 三级上验证它（§4–§8），最后定位它与 evaluated transactional controls 的分离边界（§9）。

**成本**：3 句 ≈ 60 词。

---

## 4. P2 执行项

### P2-a｜§7 = How we evaluate，§8 = What we observed（严格分工）

| 章节 | 只允许写 |
|---|---|
| §7 Protocol | 协议、环境、分母定义、判定规则、筛选规则 |
| §8 Results | 观测到的数字与事实 |

**禁止**：§7 提前解释"某个结果意味着什么"；§8 重复"实验脚本到底怎么执行"。
**依据**：§7 的 `Integration controls` 与 `Executable relation controls` 两段与 §8 的 `What strengthened transactional audits leave unspecified` 讲的是同一批实验。
**预计**：省 1–2 页。

### P2-b｜§9 集中**完整** boundary explanation

**不是把所有边界搬进 §9**，而是把**完整解释**集中进去。

正文其他地方只保留最短形式，例如：

- `72 Alloy outcomes` 附近 → `within the encoded scope`
- `320/335` 附近 → `conditional on behavior-evaluable runs`

§9 才展开：scope、mutation coverage、non-induction、DB portability、review-channel assumption 等。

**依据**：实测同一限定跨文件重复——`declared observation model` 6 文件 7 次；`external assumption` 5 文件 5 次；`class-wise irredundancy` 4 文件 4 次；`seven of eight` 3 文件 3 次。
**预计**：省约 1 页。

### P2-c｜§4–§8 增加自然语言 signpost

**不引入 L1/L2/L3 术语体系**（reviewer 可能觉得又多一层 terminology）。用自然语言：

| 级 | 表述 | 出现位置 |
|---|---|---|
| Relational level | what distinctions the declared model requires | §4 开头一句 |
| Persisted-system level | whether the implementation realizes those relations | §6 / §7 开头一句 |
| Engineering level | what they cost and whether they survive AI-agent integration | §8 开头一句 |

**路径**：`semantic → relational → persisted → engineering`

### P2-d｜§8 RQ8 secondary details → Supplement

**可移**：

- confusion matrix 细节
- per-case agreement
- secondary coefficient（AC1 / PABAK）
- cluster sensitivity
- textual acknowledgment 细目

**不可移（红线）**：

- **RQ5 的 baseline / control separation 不能因为想缩 §8 而压薄。**

**§8 目标**：`12 → 10.5–11` 页（**不追求硬指标 10**）。

---

## 5. P3

**Fig. 2 caption 改成研究路线叙事。** 现在 Fig. 2 的 caption 讲的是 C1–C5 的定义映射；改成让 reader 一眼看到方向：

```
contract → characterization → realization → validation → evaluated-control boundary
```

**先核对图本身是否已足够接近该结构。如果是，只改 caption + surrounding paragraph，不重画。**

---

## 6. 保护项 / 不做项

| 项 | 决定 | 理由 |
|---|---|---|
| §3 Contract / Proposition 1 核心内容 | **本轮不动** | fixed basis、observation functions、Prop 1、paired construction、identity-isolation、universal-minimality disclaimer 刚稳定。为省 2 页重新压缩：收益 < 风险 |
| 新实验 | **不做** | — |
| 新 baseline | **不做** | — |
| 新 failure family | **不做** | — |
| 新术语体系（L1/L2/L3、DR-numbered framework 等） | **不做** | 增加 reviewer 认知负担 |
| 重新编号 C1–C5 | **不做** | structural churn |
| 所有数字分母 | **不动** | 320/335、331/335、324/335、286/325、0/720、0/179 等 |

---

## 7. 防回涨规则（v2 修正版）

```
每个 claim 只保留一次局部必要限定；
完整 limitation 只在 §9 展开。
```

**分布契约：**

| 位置 | 保留什么 |
|---|---|
| Abstract | 最小必要限定（**不是零限定**） |
| 首次提出核心 claim 处 | **一句**局部限定 |
| Results | **只保留解释数字所必需的限定** |
| §9 Discussion | **唯一的完整边界解释** |
| Conclusion | **原则上不再重新列免责声明** |

**反例（明确禁止的做法）**：

- ❌ 删掉 `320/335` 旁边的 `conditional on behavior-evaluable runs`，只写"见 §9"
- ❌ 删掉 `72 Alloy outcomes` 旁边的 `within the encoded scope`，只写"见 §9"

这两条会为了压页数制造**新的 overclaim 风险**——正是这一轮要避免的。

**为什么必须有这条规则**：上一轮 64→54 之后，后续 4 轮又涨回 63（现 63 + 20）。没有分布契约，压完仍会涨回来。

---

## 8. 页数目标（v2 修正）

| | v1 估算 | v2 目标 |
|---|---|---|
| 主稿 | 53–55 页 | **56–59 页** |

**不把 53 页当 KPI。** 验收标准是**信息密度**，不是页数：

- Related Work 明显瘦
- Protocol / Results 不重复
- RQ8 不喧宾夺主
- Discussion 不重复前文
- 科研路线更明显

**即使最后是 59 页，也优于硬压到 53 页。**

### 分项页数预算（实测现状 → 目标）

| 章节 | 现状 | 目标 | 手段 |
|---|---|---|---|
| §2 Related work | 6 | **3.5–4** | P1-a |
| §3 Contract | 10 | 10（不动） | 保护 |
| §7 Protocol | 7 | 5.5–6 | P2-a |
| §8 Results | 12 | 10.5–11 | P2-a / P2-d |
| §9 Discussion | 5 | 4 | P2-b |
| 其他 | 23 | 23 | — |
| **合计** | **63** | **56–59** | |

---

## 9. 优先级表（执行版）

| 优先级 | 动作 |
|---|---|
| **P0** | 固定全文科研线：problem → contract → characterization → realization → validation → control separation → cost/integration |
| **P1** | §2 合并重复自我定位，压至约 4 页 |
| **P1** | Abstract 重排，让 evaluated-control finding 提前 |
| **P1** | C5 改成 `Evaluated-control separation`，**保持 C5 编号** |
| **P1** | Introduction 增加极短 research-roadmap paragraph |
| **P2** | §7 只写 protocol，§8 只写 results |
| **P2** | §9 集中完整 boundary explanation |
| **P2** | §4–§8 增加 relational / persisted / engineering 自然语言 signposts |
| **P2** | RQ8 secondary details 移 Supplement |
| **P3** | Fig. 2 caption 改成研究路线叙事 |
| **不动** | §3 / Proposition 1 核心内容 |
| **不做** | 新实验、新 baseline、新 failure family |

---

## 10. 流程与 tag 策略（v2 修正）

v1 报告里"本轮不打 freeze tag"只适用于**当前中间阶段**，不应变成最终投稿策略。

| 阶段 | tag |
|---|---|
| 现在（压缩 + 重组进行中） | **不打 tag** ✓ 当前 `61f99f72` 的记录正确 |
| 正文真正 freeze + 两位作者批准 + final verify 完成 | **应打一个 immutable submission tag** |

**落地流程**（一旦开始动正文）：

1. 动笔前打备份 tag
2. 改正文
3. 重建 `main.pdf` / `supplement.pdf`
4. 重封 `latest/MANIFEST-r27.json`
5. 跑闸门：`verify_latest.py` / `r27-jss/verify_release.py` / `pytest`
6. `git push origin HEAD:main`（**不用** `git push origin main`）
7. 清理 `latest/paper/out/` 与 `__pycache__` 后再 `git add`
8. 保持 `latest/**`、`r27-jss/**` 的 CRLF

---

## 11. 遗留待确认项

| # | 项 | 需要谁 |
|---|---|---|
| 1 | §2、§9、摘要 C5 段与 C5 标题均属第二作者 `c5e891c4` 文本，P1 三项需其同意 | XWT |
| 2 | `single-history probes` vs `single-history cases` 术语统一取哪个 | 作者 |
| 3 | Introduction roadmap paragraph 的最终措辞 | 作者 |
| 4 | Fig. 2 是否需要动图本身，还是只改 caption | 看核对结果 |
| 5 | 最终 submission tag 名称 | 作者 |

---

## 12. Fig. 2 核对结果（2026-09-11，只读）

### 12.1 图实际是什么

`evidence()`（`scripts/build_flowcharts.py:173-199`）**零个 `arrow()` 调用**；对比 `workflow()`（Fig. 1）有 **5 个**。

| | 结构 | 类型 |
|---|---|---|
| Fig. 1 `figure-1-admission-workflow` | 4 段 + 5 箭头 + 虚线回滚 | 流程图 |
| Fig. 2 `figure-2-evidence-map` | 2×2 卡片网格 + 灰色横幅 + 页脚 | **目录表** |

**整张图唯一的箭头在页脚**（`Reproducibility: raw records -> normalized inputs -> reported outputs`），讲的是可复现性，不是研究逻辑。

### 12.2 真正的问题：分组错位（不只是顺序）

| 研究线 | 图中对应 | 吻合？ |
|---|---|---|
| 3 Contract + declared observation basis | C1 | ✅ |
| 4 **Conditional characterization + evaluated-control separation** | C2 **和** C5 | ❌ 被 C3、C4 隔开 |
| 5 Realization + validation + boundary/cost | C3 + C4 | ⚠️ 勉强 |

**结论：按 `C1→C2→C3→C4→C5` 单链加箭头会误表研究线**，因为它把 C2 与 C5 拉开。

论文自己写明了 C5 是 C2 的边界检验：

- `08-results.tex:44`：`The demonstrated increment is therefore exact review linkage …, and does not affect the $D_V$ class-wise result of Proposition 1`
- `09-discussion-threats.tex:40`：`This baseline boundary does not alter the $D_V$ result of Proposition 1: $D_V$ is a class-wise irredundancy result relative to the declared observation model, whereas these controls ask which value/proposal distinctions are already recoverable from a particular transactional audit representation.`

### 12.3 只改 caption 不够的三条理由

1. **体裁不符** —— 图里 0 箭头，caption 讲 flow 会让读者在图上找不到那条 flow；Fig. 1 已承担"有箭头的图"的角色。
2. **C5 被视觉降级** —— 唯一无类别色（灰 `#F3F5F6` vs 蓝/紫/绿/橙）；位于网格下方横跨全宽读作脚注条；第三行 **9.0pt**（其它卡 9.5），`figure-audit.json` 记录 `figure_2.minimum_font_pt: 9.0` = 全图最小字号、且是 Fig. 1（9.5）以下唯一一处。
3. **图内 C5 标题字面就是 `C5 Standard-practice boundary`**（`build_flowcharts.py:195`）—— P1-c 要改的就是它，图无论如何都要重新生成。

### 12.4 建议改动（三处，零内容变更）

| # | 改动 | 依据 |
|---|---|---|
| 1 | C1→C2→C3→C4 **加方向箭头** | 让网格读成序列；与 Fig. 1 的 5 箭头风格一致 |
| 2 | C5 **升级为同级卡**：给类别色、第三行 9.0 → 9.5pt | 消除唯一的最小字号与唯一的无类别色 |
| 3 | 加 **C2 ⇢ C5 虚线箭头**，标注 `within / boundary of the declared observation model` | 编码论文自述的 C2↔C5 关系，修正 12.2 的分组错位 |

**可选**：页脚可复现性链降为框外脚注，使图内唯一可见 flow = 研究线。
**不做**：不重画、不换配色体系、不动 Fig. 1、不动任何数字。

### 12.5 成本、自检、耦合

- **改动面**：仅 `evidence()` 一个函数（27 行，纯 matplotlib 图元，无数据）
- **自检**：`export()`（`build_flowcharts.py:92-122`）在文字重叠 / 出画布 / 出卡片时**直接 raise** → 坏排版无法静默出货
- **不新增**：无新数据、无新 claim、无新实验 → 在"禁止扩大研究范围"之内
- **耦合**：图内 C5 标题、`08-results.tex:53` 的 caption、`08-results.tex:32` 的 C5 条目**三处共用同一 C5 身份**，必须同轮完成，否则重封三次 manifest
- **连带正文**：`08-results.tex:46` 引导句 `\Cref{fig:evidence-chain} maps the contract and conditional characterization to the implementation checks and experimental observations, with separate inference limits.` 是**目录式**表述，图改 roadmap 后需同步改为路线式
