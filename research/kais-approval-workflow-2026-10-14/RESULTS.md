# 已审计划工作流：应用依据与强绑定对照结果

2026-10-14。投稿后探索性工程验证；原投稿、原冻结在线队列及补充 A 队列不变。

**结论：已验证一个有独立官方依据的审批工作流，并完成真实 OpenTofu 程序上的局部集成对照。已有强绑定流程与增加纠错记录的流程在共同义务上表现一致。本轮支持集成可行性和贡献边界澄清，不支持新增安全优势。在线扩采决定为 NO-GO。**

## 1. 独立依据及比较范围

[HashiCorp 官方自动化指南](https://developer.hashicorp.com/terraform/tutorials/automation/automate-terraform)要求审批与正确的保存计划对应。这提供实际工程依据，但不证明所有同语义对象一律不可互换。本实验明确实现“批准命名的逻辑计划产物；另一个计划需重新批准；相同产物可以复制或搬运”的流程规则。

[OpenTofu apply 文档](https://opentofu.org/docs/cli/commands/apply/)将传入保存计划本身视作批准。因而我们在两个实验路线中都加入相同的可信审批记录及产物 ID／摘要核对，再调用未修改的官方二进制。此核对是公开的工作流包装器，不是 OpenTofu 自带的人类审批 API。其他强系统也已有对象绑定，例如 [HCP 的 run-specific apply](https://developer.hashicorp.com/terraform/cloud-docs/api-docs/run)；不将其描述为普遍缺少实例绑定。

- **基线路：** `saved_plan_binding`，保留逻辑产物绑定、文件摘要和全部原生计划／状态保护。
- **扩展路：** `binding_plus_correction_receipt`，保留上述保护，增加原提议、授权值、已审计划、执行结果的显式纠错记录及局部一致性检查。
- 两路持有同样的原始提议、计划和审批信息。基线可从其日志重建关系；本实验没有测量人工审计时间，不能声称它无法审计。
- 使用 OpenTofu **1.13.1**、内建 `terraform_data` 和构造的本地状态。没有云资源、外部 provider、真人审批或模型调用；不是生产工作负载。
- 纠错值必须先编译成新计划，再审阅批准。该对象映射不是论文合约逐字段同构；这里未移植完整后继／来源、授权消费和原子性合约。

详细规则见 [WORKFLOW_PROTOCOL.md](WORKFLOW_PROTOCOL.md)，官方网页及固定版本源码见 [sources/manifest.json](sources/manifest.json)。

## 2. 覆盖与全部结果

Accept（20→20）及 Correction（20→21）× 六场景 × 两路，共 **24 条主记录，即 12 组方法配对**。每个独立目录从原生状态 7 开始，保留 `reference_note`。另有 8 条控制。它们是确定性构造条件，不是随机抽样的成功率估计。

| 场景（每行 4 条主记录） | 两路共同观察 |
|---|---|
| 正常提交 | 执行获批值；随后重放不产生第二次状态变更 |
| 审批后当前配置改为 99 | 仍执行保存计划中的获批值 20／21 |
| 等效重新生成的另一逻辑产物 | 旧批准在外层绑定门被拒；脚本明确选择已审计划后成功 |
| 改为值 42 的另一计划 | 旧批准在绑定门被拒；复用已审计划后成功 |
| 前驱状态已推进 | 外层门通过，但原生明确返回 `Saved plan is stale`；重新计划并批准后成功 |
| 同一产物搬到另一文件位置 | ID 与字节保留，实际执行搬运后的文件并成功 |

主实验共 8 次外层初始拒绝、4 次原生陈旧状态初始拒绝；12 次脚本恢复成功。24 条最终业务值和未改字段均符合批准；24 次重放均由原生陈旧计划检查拒绝，未再改状态。**无重复变更不等于返回缓存成功回执；这里实际观察到的是重放被拒绝。**

8 条控制单独计数：2 条直接给原生 CLI 传入等效新计划均执行成功，符合 CLI 的批准语义；4 条新计划取得新批准后成功；2 条故意损坏纠错记录的控制被扩展路阻止。最后两条只是新增记录条件自检，未给基线记业务失败。

| 主实验指标 | 基线路（12 条） | 扩展路（12 条） |
|---|---:|---:|
| 最终获批业务值及 reference_note 符合要求 | 12 | 12 |
| 有脚本恢复的条件 | 6 | 6 |
| 原生 CLI 调用总数 | 128 | 128 |
| 审批记录总数 | 16 | 16 |
| 额外纠错记录文件 | 0 | 60 |
| 额外纠错记录字节 | 0 | 40,521 |

调用数包括初始化、计划、读取、执行和重放；审批数包含 stale_state 的独立合法推进。每条扩展主记录增加 4–6 份 JSON（前／后记录，含恢复与重放），共 2,709–4,051 字节。它们只描述此记录格式的本地开销，不是最小存储成本、端到端性能或人力成本。

首次运行及新目录完整重建均为 **24 主记录＋8 控制，32 pass、0 fail、0 unknown；240/240 检查，333 次原生 CLI 调用**。检查数不是样本量；重建不是另一批独立统计样本。

## 3. 可复核性与执行过程

在首次 fixture 执行前完成代码及公平性独立审查，修正了“任意非零退出不能算陈旧计划保护成功”和“初始化提交后超时不能算成功”两处异常归因。随后于 **2026-10-14 08:40:40 UTC** 锁定 [12 项输入](PROTOCOL_FREEZE.json)。事先仅查询过二进制版本，未运行这些 fixture；这仍是源码知情的探索性设计，不称预注册盲测。

首次完成于 08:41:21 UTC，重建完成于 08:42:12 UTC；冻结后未修改执行器或协议，也没有删除或覆盖失败运行。两个目录的规范化结果完全一致，SHA-256 为 `b2f07634d44bde2e73f2a12c4ed0e0d783b56f73e85e642722836e6adc4e85bb`。规范化排除时间、绝对路径、随机资源 ID／lineage 和计划摘要，原值仍保留在原始文件。

独立代理核查首次原始输出，主线程另核查两次运行各 107 份计划元数据、198 份状态快照、66 次包装器尝试、28 个原生陈旧计划诊断和 34 份执行后记录。12 组配对的共同结果、原生调用数及审批数一致。见 [verification.json](verification.json)、[首次汇总](runs/initial/run_summary.json)、[重建汇总](runs/rebuild/run_summary.json)。

软件包与官方 HTTPS 校验清单匹配，执行文件摘要固定；未验证发布者签名。版本与下载来源见 [software_sources.json](software_sources.json)。重建在同一台 Windows 主机的新工作目录完成，不冒称跨平台或全新机器验证。

Windows、Python 3.11；本实验脚本只用标准库。在本目录执行：

```powershell
python -X utf8 -B fetch_software.py
python -X utf8 -B run_workflow.py --run --out-dir runs/reviewer-check --freeze PROTOCOL_FREEZE.json
python -c "import json,pathlib; p=pathlib.Path('runs'); assert json.loads((p/'initial/normalized_summary.json').read_text()) == json.loads((p/'reviewer-check/normalized_summary.json').read_text()); print('MATCH')"
```

首次下载原生程序需要联网；程序已存在且摘要正确时直接复用。运行只写新的 `runs/` 子目录，拒绝覆盖已有目录。原生命令的参数、输出、退出码、配置、计划、审批、执行前后状态全部保留。该复现步骤不需要模型 API 账号。

## 4. 在线采集决策及返修用法

**NO-GO：不为当前对照追加在线 Agent 采集。** 两路已经具备相同对象绑定、共同执行义务、合法恢复和 CLI／审批数；这次差异是显式纠错记录。当前没有确定一个在同样信息和权限下、必须由 Agent 选择且可能改变本文结论的新增恢复问题。多跑模型不能把相同保护变成安全优势。

这不是论文整体不可继续。当前可用的新增证据是：有一个独立文档支持的具体审批对象；强绑定已有充分先例；显式纠错关系可以接入真实执行引擎且在此构造范围内不增加原生调用或审批。仍未解决生产采用需求强度、审计效率收益、完整合约系统集成及同层级研究系统 benchmark。

返修优先用一段简短定位和一个补充表交代本结果。贡献继续落在**纠错四角色关系、明确的后继／来源义务，以及原在线研究中实际观察到的 Agent 续行**，不把身份绑定本身说成首次提出，也不说本实验证明优于成熟工作流。

若后续确有实际使用方提出审计问题，可独立研究“在相同原始记录下，显式纠错关系是否减少归因错误及核查时间”，事先固定核查问题、盲化评分和错误成本；需要真实审计任务／人员或清楚限定的自动审计任务，不能用两条故意损坏自身记录的控制替代收益证据。该方向未启动，不是当前返修默认必补实验。

可用英文定位草案（未写入提交稿）：

> In a separate post-submission integration check using OpenTofu 1.13.1 and constructed local state, both a saved-plan binding workflow and the same workflow augmented with explicit correction receipts satisfied the tested common obligations. Their native command and approval counts matched. The augmentation made the correction relation explicit; this check did not demonstrate additional execution protection or improved audit efficiency over the existing binding workflow.
