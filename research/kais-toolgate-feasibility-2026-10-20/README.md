# ToolGate 关系配置：最小离线可行性验证

本目录保存原 ToolGate pipeline 与 C 持久后端的八项开发控制，以及既有 N/E/C 记录的 P0 联合复算。**已保存结果为 T-configured 8/8、C 8/8：两者各四次合法提交、四次拒绝，逐项业务效果持平。** T-configured 与 T+relation 合并为同一条件；这里没有第三个比较组。

先读[结果说明](D:/Claude_Design/auto-decte-paper/research/kais-toolgate-feasibility-2026-10-20/RESULTS.md)了解配置、持久化与观察结果的边界，再读[P0 联合分析](D:/Claude_Design/auto-decte-paper/research/kais-toolgate-feasibility-2026-10-20/P0-JOINT-RESULTS.md)。P0 的六个 U 差异中，三组 stale 确有过期覆盖被阻止；三组 swap 受原生身份映射限制，N 的身份违规仍为 unknown。主线之外新增防御场景为 **0**。

## 文件入口

| 文件 | 用途 |
|---|---|
| [PROTOCOL.md](D:/Claude_Design/auto-decte-paper/research/kais-toolgate-feasibility-2026-10-20/PROTOCOL.md) | 两条路线、共享投影、八项控制和解释边界 |
| [cases.json](D:/Claude_Design/auto-decte-paper/research/kais-toolgate-feasibility-2026-10-20/cases.json) | 八项输入与评分预期；运行器不把预期标签传给 gate |
| [UPSTREAM-SOURCE.json](D:/Claude_Design/auto-decte-paper/research/kais-toolgate-feasibility-2026-10-20/UPSTREAM-SOURCE.json) | ToolGate 固定提交、来源 URL 与逐文件哈希 |
| [toolgate_adapter.py](D:/Claude_Design/auto-decte-paper/research/kais-toolgate-feasibility-2026-10-20/toolgate_adapter.py) | 原 pipeline 的业务回调配置、纯草稿工具和作者提供的 SQLite 桥 |
| [contract_adapter.py](D:/Claude_Design/auto-decte-paper/research/kais-toolgate-feasibility-2026-10-20/contract_adapter.py) | 输入映射与原 C 后端调用；没有重写 C 准入逻辑 |
| [FREEZE.json](D:/Claude_Design/auto-decte-paper/research/kais-toolgate-feasibility-2026-10-20/FREEZE.json) | 执行前固定的输入、协议、实现与受保护文件清单 |
| [run_feasibility.py](D:/Claude_Design/auto-decte-paper/research/kais-toolgate-feasibility-2026-10-20/run_feasibility.py) | 检查冻结来源，每次执行建立新的运行目录，保存原始记录与 SQL |
| [score_feasibility.py](D:/Claude_Design/auto-decte-paper/research/kais-toolgate-feasibility-2026-10-20/score_feasibility.py) | 独立读取保存的数据库与运行记录，不导入 gate |
| [SCORE.json](D:/Claude_Design/auto-decte-paper/research/kais-toolgate-feasibility-2026-10-20/runs/20261020T121403449662Z/SCORE.json) / [逐项 CSV](D:/Claude_Design/auto-decte-paper/research/kais-toolgate-feasibility-2026-10-20/runs/20261020T121403449662Z/SCORE-rows.csv) | 本次 16 条执行的汇总与逐项判断 |
| [p0_joint_analysis.py](D:/Claude_Design/auto-decte-paper/research/kais-toolgate-feasibility-2026-10-20/p0_joint_analysis.py) / [33 行配对表](D:/Claude_Design/auto-decte-paper/research/kais-toolgate-feasibility-2026-10-20/p0_joint_rows.csv) | 既有 99 条 N/E/C 记录的联合复算入口与配对结果 |

## 原始证据如何组织

已完成运行位于 `runs/20261020T121403449662Z/`。每个 `D01`–`D08` 下各有 `T-configured/` 和 `C/` 两个目录，保存 `record.json`、实际 SQLite 数据库及 `sql_after.json`；C 路线还单列 `sql_before.json`。ToolGate 记录中包含持久前后快照、原始 pipeline trace、pre/post 计数及逐谓词检查、工具调用和符号状态。

运行根目录保存本次输入、冻结清单副本、环境、`RUN.json`、`SCORE.json` 与逐项 CSV。`RUN.json` 报告 16 条完成、工程错误 0、网络尝试 0；原始文件和受保护文件哈希在运行后再次核查。预期标签仅供评分器使用。候选登记与目标业务提交分开计数。

ToolGate 固定为提交 `976ad3f5528f89e248cbdf55840347b445934155`。使用固定单工具检索和脚本 reasoner，模型调用为 0。完整业务关系通过原生 Python 回调配置；SQLite 候选/授权/版本/来源记录和 post 后提交桥属于本项目新增适配。

## 只复核保存的评分

以下命令在仓库根目录的 PowerShell 中执行，只复核已保存运行，不调用模型或重新执行控制。评分器读取实际数据库与记录；已有评分若不同会报错并保留原文件。

```powershell
& research/kais-toolgate-feasibility-2026-10-20/.venv/Scripts/python.exe research/kais-toolgate-feasibility-2026-10-20/score_feasibility.py research/kais-toolgate-feasibility-2026-10-20/runs/20261020T121403449662Z
```

P0 的既有记录复算入口为：

```powershell
python research/kais-toolgate-feasibility-2026-10-20/p0_joint_analysis.py
```

P0 使用原保存 scorer，并核对 SQLite、事件 SQL、初末状态与图消息；这不是另一套新写的完整评分器。它不重跑原实验。

## 如需新的一次开发运行

当前环境记录为 Python 3.11.9、SQLite 3.45.1；[固定依赖](D:/Claude_Design/auto-decte-paper/research/kais-toolgate-feasibility-2026-10-20/requirements.txt)包括 numpy 1.26.4、SQLAlchemy 2.0.51、greenlet 3.5.6 和 typing_extensions 4.16.0。C 路线还依赖同一仓库中冻结的 `kais-external-baseline-sprint-2026-10-15` 来源；运行前会检查路径及哈希，因此本目录单独复制到另一台机器并非完整可迁移包。

已有 `FREEZE.json` 不需再次生成。新运行会验证冻结清单，在新的时间戳目录中保存全部结果，并用 Python 审计钩子拒绝网络请求；不会覆盖已完成运行。

```powershell
& research/kais-toolgate-feasibility-2026-10-20/.venv/Scripts/python.exe research/kais-toolgate-feasibility-2026-10-20/run_feasibility.py run
```

随后用评分命令对新目录评分。不要通过修改冻结文件、旧结果或挑选控制来改变这次已保存的结论。若实现需修正，应保留旧运行并建立新的明确记录。

## 解读范围

本目录验证正常配置能否执行共享关系，以及八项输入上两条路线是否一致。它不提供 ToolGate 论文的端到端复现、独有能力、完整公共任务成功率、开发集外表现或统计等效证据。P0 的边界效用也不能替代完整任务 evaluator。

ToolGate 的执行顺序仍是 pre → tool → post → 符号状态更新。这里的工具只生成草稿，作者提供的桥在 post 接受后提交；因此拒绝不证明可撤销任意外部副作用。本轮为顺序执行，没有并发新鲜性保证测试。其他公共工作流实验应使用其独立协议和结果，不能混入本轮 8/8 的分母。
