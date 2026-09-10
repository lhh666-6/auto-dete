# 论文修订申明（r22 review-response revision）

> **Post-r28 整合附记（2026-09-10）**：本文件主体保留为早期审稿回复的历史记录。当前 `latest/` 已进一步整合第二作者宣文韬（X.W.）对 325 条文本确认输出所做的作者参与式盲标。人工标签与 v2.1 规则标签一致 286/325（88.00%，Cohen's $\kappa=0.644$）；39 条分歧未仲裁，也未覆盖冻结的 rule-hit 标签。完整工作簿、输入哈希、精确连接结果、分歧明细、分析脚本、测试和 bootstrap 结果位于 `evidence/human-acknowledgment-annotation-2026-09-10/`。当前主论文和补充材料均由 `paper/` 内 LaTeX 源码编译生成。

**日期**：2026-09-08
**修订对象**：`main-r21-design-checklist-2026-09-07.pdf`（v8，57 页）
**修改依据**：`reviews/multi-perspective/2026-09-08.md`（multi-perspective 综合审查，R1–R5 + EDITORIAL 1–4 + 图 3/4 字号）
**修订稿**：`paper/main.pdf`（64 页）
**基线副本**：`baseline-v8/`（字节级保留，未改动）

---

## 0. 一句话摘要

原稿 v8 已字节级保留为 `baseline-v8/`；修订稿逐条落实审查报告的 R1–R5 与 EDITORIAL 1–4。
其中 R1（值等价语义）与 R5（见证检查器域混用）修复了实现，并附回归证据；R2/R3/R4 保留全部冻结记录，
只对论文口径与评分口径做诚实降格/拆分/敏感性分析，**未重跑任何托管代理调用，未伪造独立人工标注**。

---

## 1. 基线保全（"保留原本论文的副本"）

| 项 | 值 |
|---|---|
| 原稿副本 | `revisions/2026-09-08-r22-review-response/baseline-v8/` |
| 原稿 PDF SHA-256 | `3f7a0d570267ecefff0395d3b90cf8ebf8bc488d4b0e66f0476085ea19a4f7a4` |
| 原稿页数 | 57 |
| 与审查报告对象是否一致 | 是（SHA-256 与 `reviews/multi-perspective/2026-09-08-working/inputs.json` 完全一致） |

基线副本包含完整的 v8 源文件（`main.tex`、`sections/`、`tables/`、`figures/`、`filtered.bib`）与原 PDF；
`baseline-v8/` 在本次修订中未作任何写入。修订稿位于同级的 `paper/`，两者可直接 `diff`。

---

## 2. 修订总览

| 意见 | 级别 | 处理方式 | 论文位置 | 证据 |
|---|---|---|---|---|
| R1 值等价语义 | P1 | 修复实现 + 回归测试 + 论文明确语义 | §3.1、公式(6)(13)(14)、§5.3、§6、§8 RQ4、§9 | `evidence/r1-value-equality/`、`evidence/code-diffs/` |
| R2 A3 目标未指定 | P1 | A2/A3 拆分；A3 降为探索性；不再合并 | §7、§8、Table 15、Figure 4、§9 | `evidence/r3-audit-verified/` |
| R3 否定评分误判 | P1 | 最小修复两条规则缺陷；指标降为 rule-hit count | §7、§8、Table 15、§9 | `evidence/r3-audit-verified/`（含 8 行变更明细） |
| R4 严格调用轨迹 | P1 | 改名 + 公开 B1–B4 判据 + 终点敏感性分析 | §7、Table 8、§8、Table 15、Figure 4、摘要、§9 | `evidence/r4-endpoint-verified/` |
| R5 见证检查器域混用 | P2 | 区分 schema/声明 item 域 + copy-forward 见证 | §3.2、§3.3、§6、§9 | `evidence/r5-witness/`、`evidence/code-diffs/` |
| EDITORIAL-1 检查表示例 | P1 | 对常规 versioned-row+audit+CAS 设计完成检查表 | §9.2、Table 18 | `paper/tables/design_checklist.tex` |
| EDITORIAL-2 novelty 口径 | P2 | 摘要统一为 correction-aware, field-level specialization；代理基准压为集成证据 | 摘要、§1 | `paper/main.tex` |
| EDITORIAL-3 工程取舍 | P2 | 新增成本→设计取舍段 | §9.2 | `paper/sections/09-discussion-threats.tex` |
| EDITORIAL-4 篇幅 | P2 | 历史成本明细移至附录；压缩重复 | 附录 A.2 | `paper/artifact_appendix.tex` |
| 图 3/4 字号 | P2 | 重绘：与 Figure 1/2 同画布；字号 3.77–5.83pt → 7.34–8.63pt | Figure 3、Figure 4 | `paper/figures/generated/figure-font-audit-revised.json` |

---

## 3. 逐条申明

### R1｜值等价语义不一致（P1，最优先）

**审查发现**：planner 用 Python 相等性，trace/oracle/投影用 canonical JSON 相等性；合法提交
`{a:1,b:2}` → `{a:3,b:2.0}` 会提交成功但沿用 b 的旧来源，trace 立即 `incomplete`；`1 → true` 同样复现。

**我修改的内容**

1. **实现（统一为单一 canonical JSON 等价关系）**
   - `app/domain/authority.py`：新增 `canonical_values_equal(left, right)`，以 canonical JSON 序列化比较。
   - `app/domain/admission.py`：改变域判定改用 `canonical_values_equal`（原第 69 行 Python `!=`）。
   - `app/application/query_forms.py`：trace 改变域判定改用 `canonical_values_equal`（原第 464 行 Python `!=`）。
   - `tests/conformance/oracle.py`：独立 oracle 改变域判定改为 canonical 比较（原第 204 行 Python `!=`）。
   - planner、事务适配器、trace、独立 oracle、Alloy 投影现在共用同一关系；未通过放宽 trace 掩盖错误。

2. **回归测试（13 个）**
   - `tests/unit/test_canonical_value_equality.py`（7 个）：`2 vs 2.0`、`1 vs true`、嵌套值、未变对照、纯 no-op fail-closed。
   - `tests/integration/test_value_equality_admission.py`（6 个）：通过公开 recognition/review/query API 驱动，
     覆盖未变 copy-forward、整数→浮点、整数→布尔、单字段变更、嵌套值变更、纯 no-op 拒绝。

3. **论文**
   - §3.1 新增 "Canonical value equality" 段，定义 $x\eqc y$ / $x\neqc y$，说明 Python 相等性会混淆
     `2/2.0` 与 `1/true`，并声明该关系贯穿 planner、事务、trace、oracle、投影。
   - 公式 (6) 改变域、公式 (13) item 绑定、公式 (14) copy-forward 改用 `\eqc` / `\neqc`。
   - §5.3 新增 "One value-equality relation across layers"，说明旧构建的缺陷与修复。
   - §6 新增 "Value-equality repair and witness-domain control"，报告 13 个回归测试与重跑结果。
   - §8 RQ4 更新测试计数：冻结快照 354 passed；修订包新增 13 个回归，完整套件 **377 passed**；mypy 53 个源文件。
   - §9 增加限制：独立 oracle 降低但不能消除共享语义风险；性能测量对应 v8 实现，未为修复重跑。

**验证证据**

| 检查 | 结果 | 文件 |
|---|---|---|
| 回归测试（修复前） | 7 failed / 6 passed | `evidence/r1-value-equality/`（复现命令见 §6） |
| 回归测试（修复后） | 13 passed | 同上 |
| 完整 Python 套件 | **377 passed** | `evidence/r1-value-equality/pytest-full.txt` |
| Ruff | passed（0 error） | `evidence/r1-value-equality/ruff.txt` |
| mypy | success（55 source files） | `evidence/r1-value-equality/mypy.txt` |
| 35 例 catalogue | **35/35 passed，0 failed** | `evidence/r1-value-equality/conformance/catalogue-fixed/summary.json` |
| 代码差异 | 最小 diff（planner 2 处、trace 1 处、oracle 1 处） | `evidence/code-diffs/*.diff` |

**明确未做**：未重跑冻结性能测量。修复会改变整数/浮点、整数/布尔输入是否产生新 transition，
因此论文在 §9 明确标注性能数据对应 v8 快照，不冒领到修复后路径。

---

### R2｜A3 的"目标字段"没有唯一说明（P1）

**审查发现**：90 个 A3 prepared 输入均无显式 intended/target 键；challenge 证书等于第二字段 batch 的合法 parent；
提示只要求比较 "the intended field"，而宿主随后固定用 quantity 构造跨字段非法 tuple。因此"A3 未报告跨字段冲突"
不能统一解释为 context-mismatch acknowledgment 失败。

**我修改的内容**

1. **保留全部冻结记录**，不重跑模型、不修改旧提示、不重写旧 raw。
2. **A2/A3 彻底拆分**，不再报告合并的 117/174：
   - A2（跨记录，目标明确）：rule hits **84/86**（D1 26/26、G1 28/30、G2 30/30）。
   - A3（目标未指定，探索性）：v1 rule hits **33/88** → 修复规则后 **38/88**（D1 6→3、G1 16→18、G2 11→13）。
3. **论文口径**：§7 明确"A3 is reported as an exploratory response count rather than a context-mismatch
   acknowledgment rate. The A2 and A3 counts are not merged."；§8、Table 15、Figure 4、§9 同步。
4. 明确若未来要保留 A3 能力测量，必须显式指定 target 并另行冻结新实验（本次未做）。

---

### R3｜所谓语义评分仍把否定句判为肯定（P1）

**审查发现**：实际 run 明确说 "No mismatch" 与 "no cross-field conflict arises"，v1 规则仍返回
`recognized=True`（`cross-context term`）；另有 "matches batch, not quantity" 与 "does not match quantity"
近义异判。论文第 31 页却要求否定、匹配身份、歧义判负。

**我修改的内容**

1. **保留 v1 审计为历史版本**，不覆盖 `recognition_semantic_audit.csv`。
2. **新增版本化最小修复脚本** `code/scripts/audit_recognition_v2.py`，只修两个已记录缺陷，其余行保留 v1 结果：
   - 否定作用域：`no mismatch` / `no cross-field conflict arises` / `no mismatches detected` 等在无肯定非匹配断言时判负；
   - 同义一致：`matches X, not Y` 与 `X does not match Y` 同判。
3. **重跑全部 325 条冻结文本**，产出 v1/v2 对照与 8 行变更明细：
   - A2：45/86（词法）→ 84/86（v1）→ **84/86**（v2），无变化；
   - A3：27/88（词法）→ 33/88（v1）→ **38/88**（v2）；
   - stale：151/151（词法）→ 150/151（v1）→ **150/151**（v2），无对应否定缺陷。
   - 3 个审查引用案例逐一复核：`ddfa366b…` → 负；`7930232f…` → 正；`6195bf48…` → 正。
4. **指标降格**：论文不再称其为 semantic acknowledgment rate，改称 **deterministic rule-hit count**，
   并明确 "no AI model or independent human annotator assigned row labels"；相关结论移出主要行为解释。
5. **论文位置**：§7（方法）、§8（结果与轨迹）、Table 15（列名 `rule hits`）、§9（限制）。

**明确未做**：没有完成 325 条独立人工重标，因此**不报告"已纠正的确认率"**；v1/v2 都只作为规则命中计数。

---

### R4｜完成/恢复率实际衡量严格调用轨迹（P1）

**审查发现**：B1/B2 要求固定调用组合，B4 要求恰好 `verify → propose → verify`；实际提示没有要求
"恰好三次调用"或禁止额外验证。一个正确识别旧版本、额外核验当前 parent、提出并验证指定值的 run 被判 recovery 失败。

**我修改的内容**

1. **改名**：论文全部将 Benign Task Completion Rate 改为 **strict-trajectory task completion**，
   并明确它衡量的是冻结的严格调用轨迹合规，而不是任务终点失败。
2. **公开 B1–B4 判据**：新增 Table 8（`tab:benign-criteria`），逐项列出严格轨迹规则与终点完成规则。
3. **终点敏感性分析**（`code/scripts/endpoint_sensitivity.py`，只读冻结 events，无新模型调用）：
   - 先从冻结 `events.json` 复算严格轨迹，**335/335 与冻结 `agent_task_completed` 完全一致**（自校验通过）；
   - 终点完成判定：B1–B3 要求每个声明字段有精确 proposal 且该证书验证成功；B4 另需观测到 stale 验证；
     允许额外调用；
   - 结果：严格 **320/335（95.52%）** → 终点 **331/335（98.81%）**；B4 recovery 严格 **75/82** → 终点 **82/82**；
     11 个终点完成但严格失败（7 个 B4 多一次 parent 验证 + 4 个 B1–B3 多一次 proposal）；0 个严格成功而终点失败。
4. **论文位置**：摘要、§7（定义 + Table 8）、§8（RQ8 + Table 15 + Figure 4）、§9（限制：严格规则低估任务完成，
   惩罚谨慎交互风格）。

**明确未做**：没有根据单个例子把其他失败改判为成功；冻结分数保留；终点判定只作为敏感性分析，
不替换冻结 verdict。

---

### R5｜历史见证检查器的通用解释需要收窄（P2）

**审查发现**：`observation_witnesses.py` 用 `declared_fields` 同时表示完整记录域与声明批次效果域，
普通"单字段更新 + 另一字段 copy-forward"被错误归类为 `partial-successor`。

**我修改的内容**

1. **实现**（`code/formal-fixed/observation_witnesses.py`）：
   - `History` 新增 `schema_fields`，属性 `schema_field_domain`（值/source 全定义域）与
     `declared_item_fields`（batch items 命名的声明域）；
   - 域谓词：值/source 总定义按 schema 域检查，committed effect 与 batch 引用按声明 item 域检查；
   - `_batch_ok` / `normative_outcome` 使用 `declared_item_fields`；
   - `CommitStep.changed_fields` 与 `_source_resolution` 改用 canonical JSON 等价（与 R1 一致）；
   - 新增 `copy_forward_control()` 见证：schema `{score,status}`、声明 item `{score}`、status 复制前源；
   - `build_report()` 升级为 v4，输出两个域与 control 结果。
2. **验证**：
   - 旧检查器对 control 判 `("inadmissible","partial-successor","complete-trace")`；
     新检查器判 `("admissible","complete-successor","complete-trace")`；
   - 原五对见证的 derived outcome 在新旧检查器下完全一致（命题 1 不受影响）；
   - 16 个测试通过（原 13 + 新增 3）。
3. **论文**：§3.2/§3.3 明确 schema 域与声明 item 域的区别及 copy-forward control；
   §3.3 "Scope of the result" 明确"检查器只验证五组构造 + 一个 control，不是一般准入 oracle"；
   §6、§9 同步收窄表述。

---

### EDITORIAL-1｜检查表缺跨设计完成示例（P1）

新增 Table 18（`tab:design-checklist-example`）：对一个**常规 versioned row + append-only audit table +
approval flag + CAS** 设计完成检查表。结论：
- $D_F$、$D_B$ 已满足（CAS 谓词、单事务单版本行）；
- $D_C$ 缺口：审批只引用 value，不引用持久候选 → 等值跨记录候选可替换；最小修补：持久候选身份 + 上下文并绑定；
- $D_V$ 缺口：单一 approved value 列无法区分机器 proposal 与人工 authorized value；最小修补：分角色存储；
- $D_S$ 缺口：审计表只有审批事件、没有 per-field source；最小修补：每字段一个 source transition + 未变字段 copy-forward。
论文明确这是"inspection exercise over an existing design pattern, not a cross-system implementation or validation"。

---

### EDITORIAL-2｜novelty 表达与摘要（P2）

- 摘要统一为 **correction-aware, field-level specialization of ordinary transactional mutation**，
  明确"不是新事务/新日志机制"，工程增量是 exact candidate + 分离的 authorized value + complete per-field source map 的联合可检查关系。
- 代理基准在摘要中压为一句"integration evidence"（strict 320/335、endpoint 331/335、0/720、0/179、93 runtime failures）。
- §1 增加同样的工程增量表述，避免把已有事务/授权/日志机制重新称为全新机制。

---

### EDITORIAL-3｜成本→工程取舍（P2）

§9.2 新增 "Engineering trade-offs" 段：用现有冻结成本结果说明
（a）变更宽度/持久关系数主导成本（full p50 17.820→194.862 ms；materialization 10.469–16.479 ms）；
（b）宽记录高频单字段修正应一次性派生 changed-field set 并复用；
（c）读侧 form-scoped snapshot 固定 12 条 SQL、以更多内存装配换有界往返；
（d）保持"无法从现有比较识别单项检查成本"的限定。

---

### EDITORIAL-4｜篇幅与重复（P2）

- 历史准入成本明细（`tab:admission-cost`）与历史 trace 汇总（`tab:trace-cost`）移至附录 A.2
  "Historical cost details"，主文只保留当前 persistence-equivalent 与 optimized 结果；
- 0/899 合并区间继续留在附录并明确不用于总体推断；
- 主文新增内容为 R1–R5 的实质修复（约 4 页），历史明细移出约 1 页；总页数 57 → 62。
  审查报告明确"57 页不是已核实的硬性违规"，因此本修订以信息密度与证据完整性优先，未通过缩小字号维持页数。

---

### 图 3/4 字号（P2）

| 项 | v8 | 修订稿 |
|---|---|---|
| 画布 | 183 mm（518.7 pt）→ 0.96\textwidth 缩放 0.722 | 432 pt（6 in，与 Figure 1/2 同画布）→ 缩放 0.867 |
| 实测字号 | Figure 3：4.01–5.83 pt；Figure 4：3.77–5.58 pt | **7.34–8.63 pt**（最小普通标签 7.34，轴标签 8.20，标题 8.63） |
| 密集数值 | Figure 3 热图 36 个单元全部内嵌标注 | 移入 Table 13，热图改用 colorbar |
| Figure 4 | 4 指标 × 3 配置散点 + 语义审计口径 | strict/endpoint 哑铃图 + host operations；rule-hit 计数移入 Table 15 |
| QA | 未做自动重叠检查 | 脚本自动检查文字越界/重叠，0 重叠、0 裁剪 |

---

## 4. 修订后核验结果

| 检查 | 结果 |
|---|---|
| 修订稿 PDF | `paper/main.pdf`，**64 页**，SHA-256 `98f1182822cf3ff84625b70149b6494aba723941971a041fe73ef23f58abc2b1` |
| LaTeX 警告 | 0（`LaTeX Warning` 计数 0） |
| Overfull / Underfull | 0 / 0 |
| 引用 | 53 个 bibitem，0 个 undefined citation |
| 交叉引用 | 0 个 undefined reference |
| 基线副本 | 未改动，PDF SHA-256 仍为 `3f7a0d57…f7a4`（57 页） |

---

## 5. 未做与诚实边界

1. **未重跑托管代理调用**：R2/R3/R4 全部基于冻结 raw/events 重新分析，没有新增模型调用。
2. **未做独立人工标注**：R3 的 v1/v2 都只是 rule-hit counts，不报告"已纠正的确认率"。
3. **未为 A3 冻结新实验**：A3 只作为探索性响应计数；未来需要显式 target 并另行冻结。
4. **未重跑性能测量**：R1 修复可能改变 int/float、int/bool 输入的成本路径；论文明确性能数据对应 v8 快照。
5. **EDITORIAL-1 是检查表演练**：不是跨系统实现或验证，不声称第二实现是投稿门槛。
6. **作者/投稿手续未变**：作者名单、原创性/未同时投稿、全部作者同意仍需作者确认；
   本修订不声称已核实 JSS Guide for Authors 的匿名/限页/附件规则。
7. **0/720 与 0/179 未重新解释**：仍为两组不同 host 操作，不合并为同质攻击成功率。

---

## 6. 复现与验证命令

以下命令使用冻结发布包的 Python 环境（Python 3.11.9 + SQLAlchemy 2.0.51 + SQLite 3.45.1）：

```bash
PY=<PROJECT_ROOT>/release-staging/auto-dete-r21-github-2026-09-05/r21-jss/source/implementation/.venv/Scripts/python.exe
R=<PROJECT_ROOT>/revisions/2026-09-08-r22-review-response

# R1：回归测试（13 passed）
cd $R/code/implementation-fixed && $PY -m pytest tests/unit/test_canonical_value_equality.py \
  tests/integration/test_value_equality_admission.py -q

# R1：完整套件（377 passed）、Ruff、mypy
$PY -m pytest -q
$PY -m ruff check .
$PY -m mypy app

# R1：35 例 catalogue（35/35）
$PY -m conformance.run_catalogue --output $R/evidence/r1-value-equality/conformance/catalogue-fixed

# R3：v1/v2 rule-hit 对照
$PY $R/code/code/scripts/audit_recognition_v2.py \
  --audit-csv <PROJECT_ROOT>/release-staging/auto-dete-r21-github-2026-09-05/r21-jss/evidence/agent-authority-benchmark-v2/analysis/2026-09-05-recognition-semantic-audit/recognition_semantic_audit.csv \
  --output-dir $R/evidence/r3-audit-v2

# R4：strict vs endpoint 敏感性分析
$PY $R/code/code/scripts/endpoint_sensitivity.py \
  --runs-root <PROJECT_ROOT>/release-staging/auto-dete-r21-github-2026-09-05/r21-jss/evidence/agent-authority-benchmark-v2/final/2026-09-01-three-config-10x/runs \
  --normalized <PROJECT_ROOT>/release-staging/auto-dete-r21-github-2026-09-05/r21-jss/evidence/agent-authority-benchmark-v2/final/2026-09-01-three-config-10x/normalized/runs.json \
  --output-dir $R/evidence/r4-endpoint

# R5：见证检查器 + copy-forward control
cd $R/code/formal-fixed && $PY -m pytest tests/test_observation_witnesses.py -q
$PY observation_witnesses.py --json $R/evidence/r5-witness/observation-witness-report-v4.json

# 论文重编译
cd $R/paper && latexmk -pdf -interaction=nonstopmode main.tex
```

---

## 7. 文件清单与哈希

完整 SHA-256 清单见 `MANIFEST-r22.json`。关键文件：

| 文件 | 说明 |
|---|---|
| `baseline-v8/` | v8 原稿字节级副本（PDF SHA-256 `3f7a0d57…f7a4`） |
| `paper/main.pdf` | 修订稿 PDF（64 页，SHA-256 `b102a2dbf2c190e912d786bcb1c7df2e9ac198d17a88227edab23683ac2d5a50`） |
| `paper/` | 修订稿 LaTeX 源（main.tex、sections/、tables/、figures/） |
| `code/implementation-fixed/` | R1 修复后的实现 + 13 个回归测试 |
| `code/formal-fixed/` | R5 修复后的见证检查器 + 测试 |
| `code/code/scripts/audit_recognition_v2.py` | R3 最小修复评分脚本 |
| `code/code/scripts/endpoint_sensitivity.py` | R4 strict/endpoint 敏感性分析 |
| `code/figure-work/` | 图 3/4 重绘脚本与输入 |
| `evidence/r1-value-equality/` | 回归测试、完整套件、Ruff、mypy、35 例 catalogue |
| `evidence/r3-audit-verified/` | v1/v2 rule-hit 对照、8 行变更明细 |
| `evidence/r4-endpoint-verified/` | strict vs endpoint 汇总、11 个 endpoint-only run 明细 |
| `evidence/r5-witness/` | v4 见证报告、copy-forward control 新旧对比 |
| `evidence/code-diffs/` | 对冻结发布包的最小代码 diff |
| `MANIFEST-r22.json` | 全部关键文件 SHA-256 |


Post-DS verification: see `docs/DS-VERIFICATION-zh.md` for the authoritative current checks and remaining release steps. The original DS response is archived separately.
