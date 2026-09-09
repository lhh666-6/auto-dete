> 阶段性历史记录。2026-09-09 的补修与当前验证结果见 `DSH-REVIEW-2026-09-09-zh.md`；本文件中的旧测试数量不代表最新状态。

# 可执行检查表：Claude 独立验证报告

日期：2026-09-08。对象：`revisions/2026-09-08-r23-executable-checklist/`。
本报告只描述 Claude 的接续工作与验证结果；Codex/Claude 的逐文件归属见
`docs/WORK-ATTRIBUTION-zh.md`。

## 1. 目的

Codex 的设计文档 `docs/executable-checklist-design.md` 提出：用一个小型、
标准库 Python/SQLite 的**两臂对比**，让「常规值审批设计」与「candidate-bound
特化」的差异可被检查，而不是停留在假想示例。本文验证该设计是否被完整实现、
9 个预先固定的案例是否得到预期结果，以及论文整合是否诚实、可复核。

## 2. 方法

- **被测对象**：Codex 的 `value_audit_demo.py`（未改动）。两臂共享同一基线：
  不可变候选、完整版本快照、principal/value/domain 绑定审批、原子 CAS、
  完整的 before/after 值审计。
- **驱动与观察分离**：Claude 的 `run_example.py` 通过公共 API 驱动两臂；
  每次运行后用**全新的 SQLite 连接**读取全部用户表（`raw_state`），不经过
  `Demo` 对象的内部状态。每个运行记录外部请求动作、pre/post 原始 SQL 快照、
  结果与案例观察。
- **9 个案例在执行前声明**（`CASE_SPECS`），期望结果由 `check_expected_outcomes`
  强制检查；任何偏离都会让 runner 失败。
- **测试**：Codex 的 12 个行为测试（修复测试辅助函数连接泄漏后）+
  Claude 的 10 个 runner 测试 = **22/22 通过**。

## 3. 结果

18 次运行（9 案例 × 2 策略）；`all_expected_outcomes_met = true`。

| 案例 | 期望 | value_audit | candidate_bound |
|---|---|---|---|
| 合法修正 | 两者接受 | 接受；v1 quantity=101 | 接受；v1 quantity=101 |
| 同记录同字段等值候选替换 | 分歧 | **接受；提交 101** | **拒绝 `candidate_binding`；状态不变** |
| 跨记录候选 | 两者拒绝 | 拒绝 `candidate_context` | 拒绝 `candidate_context` |
| 过期期望版本 | 两者拒绝 | 拒绝 `stale_version` | 拒绝 `stale_version` |
| 提交值与批准值不符 | 两者拒绝 | 拒绝 `approved_values` | 拒绝 `approved_values` |
| 部分批准批次 | 两者拒绝 | 拒绝 `approved_values` | 拒绝 `approved_values` |
| 写后注入故障 | 两者回滚 | 回滚，所有表不变 | 回滚，所有表不变 |
| 两步 copy-forward | 两者可重建 | 重建 `quantity=v1:quantity, batch=v2:batch` | 同样重建，**并持久化 source map** |
| 成对 reviewed-candidate 历史 | 关键观察 | 两次运行的完整持久状态**相同** | 完整持久状态**不同**（差异恰为 `approvals`） |

### 3.1 关键发现

1. **唯一的 accept/reject 分歧**是「同记录同字段、等值候选替换」：value-audit
   因候选值相等而放行；candidate-bound 因审批绑定的是被审阅的候选身份而拒绝。
   这与 R1 的值等价修复动机一致——值相等不等于候选身份相等。
2. **成对历史**是最锐利的观察：两次运行审阅 `q100a` 与 `q101`，两者都批准并提交
   101，候选池、值、actor、期望版本完全相同。value-audit 的完整持久数据库在两次
   运行间**逐字节相同**；candidate-bound 只在 `approvals.reviewed_candidates_json`
   上不同。这证明常规策略**省略了审阅联动**，而不是候选值不存在（两臂都保留了
   候选值）。
3. **双值角色可由 join 重建**：candidate-bound 通过 `approvals` 的候选绑定 join
   `candidates.proposed_json`，可重建 proposed=100 与 authorized=101 两个角色；
   value-audit 无法重建 proposed 角色。
4. **copy-forward**：两臂都能仅从完整审计历史重建精确 source map；只有
   candidate-bound 把 source map 持久化。

## 4. 论文整合

- **Supplement S3** 由「假想 worked example」替换为「Executable design
  comparison」（`paper/supplement.tex`，`\label{sec:supp-executable}`），
  含 **Table S4**（`\label{tab:executable-checklist}`，由 runner 从记录派生）。
- **正文短结果**位于 §9 Design implications：两策略在 7/8 个单运行案例上
  accept/reject 一致，1 个分歧；成对历史显示 value-audit 数据库相同、
  candidate-bound 不同。
- **页数**：主稿 **54 页**、补充材料 **7 页**，与 r22-concise 基线完全相同；
  新增 S3 通过收紧表格与行距后未增加页数。
- **编译**：main/supplement 均 0 LaTeX warning、0 overfull/underfull、
  0 undefined reference/citation。
- 正文 §9 引用的 `docs/admission-design-checklist.md` 在 r22-concise 包内缺失；
  Claude 已从 `2026-09-07-r21-design-checklist/docs/` 复制同一文件补齐
  （SHA-256 一致）。

## 5. 与基线的一致性核验

对照 `revisions/2026-09-08-r22-concise/`（54 页主稿 + 7 页补充材料）：

- 基线打包文件 **359** 个；r23 打包文件 **407** 个；新增 **48** 个；
  受保护文件**无删除、无改动**。
- 仅 **4** 个论文文件有意变化：`paper/main.pdf`、
  `paper/sections/09-discussion-threats.tex`、`paper/supplement.pdf`、
  `paper/supplement.tex`；另有 `README.md` 更新。
- 受保护目录中 **301/301** 个文件逐字节相同，包括：§3 契约、§4、declarations、
  artifact_appendix、`filtered.bib`、`references.bib`、4 张主图、
  关键结果表、`code/implementation-fixed/`、`code/formal-fixed/`、
  `fixtures/`、`baseline-v8/` 与 r22 证据。
- 受保护实现套件（源码逐字节相同）由 Claude 复跑，见
  `evidence/pytest-full-claude.txt`；Codex 的 12 个行为测试与 Claude 的
  10 个 runner 测试见 `evidence/checklist-green-tests-claude.txt`（22/22 通过）。

## 6. 诚实边界（不声称的内容）

- 该演示是**说明性特化**，不是 Auto-Decte 契约的第二套生产实现；未实现密码学
  证据验证、企业认证、分布式撤销、竞态压力或性能测量。
- 9 个案例是**确定性构造**，计数不是统计或优越性结论；不构成对任何已部署系统
  缺陷或不可扩展性的证据。
- 测试在单机 SQLite 上运行；未覆盖其他数据库引擎、并发交错或生产负载。
- 未新增 hosted-model 调用、未重跑冻结实验、未重跑 v8 性能测量。
- 作者名单、独立人工盲标、修订补充包的不可变公开地址仍由作者负责。

## 7. 复现命令

```bash
cd revisions/2026-09-08-r23-executable-checklist/code/checklist-example
python -m unittest -v test_value_audit_demo test_run_example
python run_example.py --out ../../evidence/checklist-runs \
    --table ../../paper/tables/generated/checklist_example.tex
cd ../.. && python evidence/claude-verification/compare_baseline.py
cd paper && latexmk -pdf main.tex && latexmk -pdf supplement.tex
cd .. && python evidence/claude-verification/package_r23.py --build
python evidence/claude-verification/package_r23.py --check
```
