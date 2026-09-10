> 阶段性历史记录。2026-09-09 的补修与当前验证结果见 `DSH-REVIEW-2026-09-09-zh.md`；本文件中的旧测试数量不代表最新状态。

# Codex / Claude 工作归属声明

日期：2026-09-08（本地）。对象：`revisions/2026-09-08-r23-executable-checklist/`。
本文件用于把**Codex 的原始工作**与**Claude 的接续工作**逐文件分开，避免把两方
的贡献混在一起。原始 r22 交付（`2026-09-08-r22-review-response/`、
`2026-09-08-r22-concise/`）未被修改。

## 0. 一句话结论

- **Codex**：完成了可执行对比的**设计文档**、**先写的 12 个行为测试（红）**和
  **两臂 SQLite 演示实现**；在第一次运行测试后撞上用量上限中断，未完成 runner、
  LaTeX 表、论文整合与打包。
- **Claude**：修复测试连接泄漏、按 Codex 设计补齐 runner 与 runner 测试、
  生成运行记录与 LaTeX 表、替换 Supplement S3、更新正文短结果、重编译、
  重建 MANIFEST/ZIP、独立核验，并撰写本声明与验证报告。
- **未改动**：Codex 的 `value_audit_demo.py` 与设计文档原样保留；r22 两个既有
  交付与 `baseline-v8/` 未改动。

## 1. 背景与时间线

| 时间（UTC） | 事件 |
|---|---|
| 2026-09-08 15:38 | 用户要求压缩论文 10 页；Codex 产出 r22-concise（54 页主稿 + 7 页补充材料） |
| 15:48–15:52 | 用户询问 novelty；Codex 给出增强选项 |
| 15:50 | 用户选择「第一个」：小型可执行对比 |
| 15:53 | Codex 写 `reviews/executable-checklist-2026-09-08/design.md` |
| 15:54 | Codex 先写 `test_value_audit_demo.py`，记录红状态（12 失败） |
| 15:56 | Codex 写 `value_audit_demo.py`，运行测试，保存输出 |
| **15:56:14** | **Codex 撞上用量上限，任务中断**（`task_complete`，`last_agent_message=null`） |
| 接续 | Claude 接管：复核、修复、补齐、整合、打包、声明 |

## 2. Codex 的工作（原样保留，可逐字节复核）

| 文件 | Codex 角色 | SHA-256 | 当前状态 |
|---|---|---|---|
| `docs/executable-checklist-design.md` | 设计与实施计划（授权来源） | `07107fda82456da6eaa2718f9fb2f1e0c754d51cc71990ae7f2fbd35fc66a4d6` | 原样保留 |
| `code/checklist-example/value_audit_demo.py` | 两臂 SQLite 演示实现 | `3d94a2f2ec2d45425ba747a2f01d53502c6b00f45b98125cff7ac11ed032ec89` | **未改动** |
| `code/checklist-example/test_value_audit_demo.py` | 12 个黑盒行为测试（先写） | 原版 `b25110f617676e4dccad2b63efc7317b1809d83bf365b74347bdf121eff0b7ec` | 仅修 1 处连接泄漏（见 §3） |
| `evidence/checklist-red-tests.txt` | 红状态证据：12 失败，`Demo=None` | `873ef0b857988644e778414d13b80d7cdcff7d26979e14d627fa97b5fbac2e25` | 原样保留 |
| `evidence/checklist-green-tests.txt` | **名为 green，实为失败运行** | `51fa59b0a718f6539ee8934449a5196de997a028a797ff6169203c8a7e657406` | 原样保留为历史记录 |

Codex 原文件另存于 `evidence/codex-handoff/`，并附 `SHA256SUMS.txt`。
该目录的 `checklist-green-tests.codex.txt` 结尾为 `Ran 12 tests` / `FAILED (errors=10)`，
10 个 ERROR 全部是 Windows `PermissionError: [WinError 32]`；根因是测试辅助函数
`persisted()` 使用 `with sqlite3.connect(path) as con:`——该上下文管理器只提交/回滚、
**不关闭连接**，临时目录清理时无法删除 `.db`。Codex 的实现逻辑本身没有问题。

## 3. Claude 的工作（本轮新增或修改）

| 文件 | 动作 | 说明 |
|---|---|---|
| `code/checklist-example/test_value_audit_demo.py` | 最小修改 | 加 `from contextlib import closing`；`with closing(sqlite3.connect(path)) as con:`。完整 diff：`evidence/claude-test-harness-fix.diff` |
| `code/checklist-example/run_example.py` | 新增 | 按 Codex 设计实现：9 个预先固定的案例 × 2 策略；用**独立新连接**读取全部原始 SQL 表；每个运行写外部请求动作、pre/post 快照、结果与案例观察；导出 LaTeX 表 |
| `code/checklist-example/test_run_example.py` | 新增 | 10 个 runner 测试：期望结果、唯一分歧、拒绝后状态不变、成对历史、copy-forward 重建、双值角色 join、独立读取、记录完整性、表格覆盖、拒绝覆盖已有 DB |
| `evidence/checklist-green-tests-claude.txt` | 新增 | Claude 测试运行：**22/22 通过**（12 个 Codex 行为测试 + 10 个 Claude runner 测试） |
| `evidence/checklist-runs/` | 新增 | 18 次运行记录 + 20 个原始 SQLite 文件 + `runs.json` + `summary.json` |
| `paper/tables/generated/checklist_example.tex` | 新增 | 由 `run_example.py` 从记录派生的对比表（Table S4） |
| `paper/supplement.tex` | 修改 | 用 S3「Executable design comparison」替换原假想 worked example；引用 Table S4 |
| `paper/sections/09-discussion-threats.tex` | 修改 | 正文短结果：两策略在 7/8 单运行案例上一致，1 个分歧；成对历史显示 value-audit 数据库相同、candidate-bound 不同 |
| `paper/main.pdf` / `paper/supplement.pdf` | 重编译 | 主稿 **54 页**、补充材料 **7 页**（与基线页数相同）；0 warning、0 overfull/underfull、0 undefined |
| `docs/admission-design-checklist.md` | 新增（补缺） | 正文 §9 引用了该 worksheet，但 r22-concise 包内缺失；Claude 从 `2026-09-07-r21-design-checklist/docs/` 复制同一文件补齐（SHA-256 一致） |
| `evidence/claude-verification/` | 新增 | 独立核验脚本（基线对比、引文核对、打包校验）与表格页渲染图 |
| `evidence/pytest-full-claude.txt` | 新增 | 受保护实现套件的 Claude 复跑证据（源码与基线逐字节相同） |
| `MANIFEST-r23.json` / `r23-executable-checklist-2026-09-08.zip` | 重建 | 新 schema、逐文件 SHA-256、ZIP 与目录一致 |
| `docs/CODEX-HANDOFF-STATE-zh.md` | 新增 | 冻结 Codex 产物、中断时间线与「green 实为失败」的复核记录 |
| `docs/WORK-ATTRIBUTION-zh.md` | 新增 | 本声明 |
| `docs/EXECUTABLE-CHECKLIST-VERIFICATION-zh.md` | 新增 | Claude 独立验证报告 |
| `README.md` | 修改 | 更新为 r23 包说明 |

## 4. 分工边界与未越界事项

- 未修改 `revisions/2026-09-08-r22-review-response/`、`revisions/2026-09-08-r22-concise/`
  及其 ZIP/manifest。
- 未修改 Codex 的 `value_audit_demo.py`（SHA-256 与 Codex 原版一致）。
- 未修改 `code/implementation-fixed/`、`code/formal-fixed/`、`fixtures/`、`baseline-v8/`
  （与 r22-concise 基线逐字节相同；受保护目录 301/301 一致）。
- 仅删除了 r23 根目录下从 r22-concise 复制来的**过期** `MANIFEST-r22.json`；
  r22-concise 自己的 manifest 仍保留在原包中，r23 使用 `MANIFEST-r23.json`。
- 未新增 hosted-model 调用、未重跑冻结实验、未做性能测量。
- 未声称任何已部署系统存在缺陷，也未声称统计优越性；9 个案例是确定性构造。
- 作者名单、独立人工盲标、修订补充包的不可变公开地址仍由作者负责。

## 5. 论文中新增内容的具体位置

- **Supplement S3**：`paper/supplement.tex`，`\label{sec:supp-executable}`。
- **Table S4**：`paper/tables/generated/checklist_example.tex`，`\label{tab:executable-checklist}`。
- **正文短结果**：`paper/sections/09-discussion-threats.tex` 第 12 行（Design implications）。
- 主稿 54 页、补充材料 7 页，与 r22-concise 基线页数相同；新增 S3 对比通过收紧
  表格与行距后未增加页数。

## 6. 复现命令

```bash
cd revisions/2026-09-08-r23-executable-checklist/code/checklist-example

# 1) 测试：Codex 行为测试（已修连接泄漏）+ Claude runner 测试
python -m unittest -v test_value_audit_demo test_run_example

# 2) 运行 9 个固定案例，写原始 SQLite 与记录，并派生 LaTeX 表
python run_example.py --out ../../evidence/checklist-runs \
    --table ../../paper/tables/generated/checklist_example.tex

# 3) 与 r22-concise 基线对比（应只看到 4 个论文文件变化、0 删除）
python ../../evidence/claude-verification/compare_baseline.py

# 4) 编译
cd ../../paper && latexmk -pdf main.tex && latexmk -pdf supplement.tex

# 5) 打包与校验
cd ..
python evidence/claude-verification/package_r23.py --build
python evidence/claude-verification/package_r23.py --check
```

- 旧假想示例表 `paper/tables/design_checklist_example.tex` 保留在包内（与基线逐字节相同），但不再被 `\input`；S3 已替换为可执行对比。
