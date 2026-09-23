# DKE 补充实验复现包

本目录包含三组实际执行的补充实验，均不调用任何在线模型 API。
结果解释以 `REPORT.md` 为准，实验原始记录位于 `results/e1`、
`results/e2` 和 `results/e3`。`pilot-*` 是保留的预跑，不能混入正式统计。

## 源码与环境

- 源码：`../dke-experiments`，公开仓库 `https://github.com/lhh666-6/auto-dete`。
- 固定提交：`c6d512843c905cab6d8521dd8c914f7fb26d85ae`，标签 `r31-jss-2026-09-13`。
- 使用 `latest/code/implementation-fixed`；实验通过适配器调用该实现，没有修改该目录中的跟踪源码。
- 执行解释器：`../.venv-study/Scripts/python.exe`，CPython 3.11.16。
- 锁定依赖：`requirements-source-lock.txt`，由原始 `uv.lock` 导出。
- 浏览器驱动：系统 `D:/Python312/python.exe` 的 Playwright，使用本机 Chrome；仅连接 127.0.0.1。

## 复现命令

在工作区 `D:\desktop\JSS论文` 中使用 PowerShell。输出目录必须换为尚不存在的目录，
不要覆盖这次正式结果。性能实验应在其他实验和测试结束后独立执行。

```powershell
& '.venv-study\Scripts\python.exe' -B -m pytest DKE-supplement\test_supplement.py -q -p no:cacheprovider
& '.venv-study\Scripts\python.exe' -B DKE-supplement\experiment1.py --output DKE-supplement\results\replicate-e1
& '.venv-study\Scripts\python.exe' -B DKE-supplement\experiment2.py --output DKE-supplement\results\replicate-e2
& '.venv-study\Scripts\python.exe' -B DKE-supplement\experiment3.py --output DKE-supplement\results\replicate-e3
```

E3 也可通过 `--section mechanism`、`--section ablation`、`--section trace`、
`--section storage` 在同一新输出目录中逐节顺序执行，不可重复执行已存在的节。
`--pilot` 使用缩小网格，不能替代正式实验。E1 的 `--limit 1` 和 E2 的 `--limit`
同样仅用于预跑。

原实现相关回归测试：

```powershell
Set-Location dke-experiments\latest\code\implementation-fixed
& 'D:\desktop\JSS论文\.venv-study\Scripts\python.exe' -B -m pytest tests/integration/test_value_equality_admission.py tests/conformance -q -p no:cacheprovider
```

本次正式数据的汇总与核验脚本为 `audit_rejections.py`、`make_report.py` 和
`seal_results.py`。绘图脚本使用系统 Python 的 matplotlib；它们读取本目录固定的
`results/e1`、`results/e2`、`results/e3`，不会把其他名字的复跑目录自动混入统计。
`reproduce_existing_baseline.py` 另行复现原论文强基线的 8 类准入案例和 1 项配对历史检查。

## 文件用途

| 文件 | 用途 |
|---|---|
| `PROTOCOL.md` | 运行前计划、适用范围和预跑后的明确修订 |
| `reference.py` | 对未修改的论文实现进行调用、故障注入和独立数据库查询 |
| `journal.py` | 本次独立编写的 sqlite3 事件日志对照；不是商业或外部团队基线 |
| `experiment1.py` | 归档输入选择、11 类准入案例、三种机制、查询答案检查 |
| `experiment2.py` | 本地审核页面、原接口和实验性会话绑定 |
| `browser_driver.py` | 浏览器操作、独立 DOM 观察和故障注入 |
| `experiment3.py` | 当前修复版的准入、追溯和存储测量 |
| `test_supplement.py` | 检查身份与类型区分、真实实现调用和回滚路径 |

## 解释限制

1. 归档模型输出被重放为新构造案例的输入，不是新模型运行，也不是原任务端到端复现。
2. E1/E2 是有限的合成故障实验；不能将案例比例解释为真实攻击成功率或用户误操作率。
3. 新事件日志基线与参考实现仅在共同测试的契约和负载上比较，不代表二者完整产品功能相同。
4. E2 使用固定的模拟审核人标识，不评估身份认证；会话库与事实库不是跨库原子事务。
5. 模型证据在 E1/E2 中以构造的注册元数据参与检查，不评估真实影像内容或外部文件篡改。
6. 性能数据来自单机单次运行；重复计时的置信区间不能覆盖不同机器或不同部署的变异。
7. 数据库文件保留用于复核。E3 中 `*-working.db` 是该格最后一次运行，完整逐次计时在 JSONL 中。
