# X1/X2 修正版实验结果

完成日期 2026-10-21。此报告由通过校验的运行产物生成。
两次运行见 `final-1` 与 `final-2`；完整路径和逐项检查在 `VERIFICATION.json`。
没有调用模型。原实验文件、运行产物和受保护的稿件文件哈希保持不变。

## X1 实际审批对象与同会话续程

共 16 个确定性条件，SQLite 实际记录 18 次效果。版本为 langchain 1.2.10, langchain-core 1.2.13, langgraph 1.0.8, langgraph-checkpoint 4.0.0。
官方中间件和挂起恢复 primitive 未改动。测试图、工具执行器和记录器为作者适配；官方配置、原生行为和适配行为逐条件标注。

| 机制 | 第二轮产生新中断 ID | 第二轮提议新增写入 | 旧 ID 恢复新增写入 | 旧 ID 后当前审批仍挂起 | 当前 ID 恢复新增写入 |
|---|---|---:|---:|---|---:|
| LangChain HITL | 是 | 0 | 0 | 是 | 1 |
| LangGraph primitive＋作者节点 | 是 | 0 | 0 | 是 | 1 |

以上两轮均使用同一个 graph、checkpointer 和 thread，原始 ID 与完整历史另存 RAW-EVIDENCE.json。

| 其他条件 | 读回结果 |
|---|---|
| 同批先批准、后拒绝 | call_t1_c1=100 |
| 同批先拒绝、后批准 | call_t1_c2=100 |
| 明确编辑 100→999 | call_t1_c1=999 |
| 编辑前提议保存在历史 checkpoint | 是 |
| 编辑前审批 payload 保存在历史 checkpoint | 是 |
| L1 第二轮再次传入相同的无键批准输入 | 新增 1 次写入 |
| L1 已完成后再次 resume | 新增 0 次写入 |
| L2 第二轮再次传入相同的无键批准输入 | 新增 1 次写入 |
| L2 已完成后再次 resume | 新增 0 次写入 |
| L1-wrong-count | ValueError，新增 0 次写入 |
| L1-disallowed-edit | ValueError，新增 0 次写入 |
| L1-invalid-type | ValueError，新增 0 次写入 |

相同参数的两个 action-request 条目内容相等为 是，条目包含显式 call-id 键为 否。列表位置仍区分两个决定。
明确编辑是审阅者授权的内容变化，历史保留与最终消息替换可以同时成立。无键批准是调用者在新中断处再次提供的肯定输入，不能等同于旧业务授权被盗用。
这些条件刻画了测试接口中的对象和路由语义，不建立框架存在审批绕过、没有持久授权能力或不能扩展的结论。未做进程重启、并发重放或批准后未授权变更注入。

## X2 绑定范围与真实外部依赖

共 9 个构造案例，跨三种主要绑定方式、一个诊断变体和两种共享执行模式，共 72 条路线。其中主要比较 54 条，诊断 18 条。这些路线不是独立业务样本。
C3 在审阅后实际修改文件。工具按声明的操作读取文件金额并写入 SQLite；验证模式校验并消费同一份读入字节。未变文档对照使用同样的操作。

| 绑定方式 | 未校验外部内容时的语义违规 | 加入共同摘要校验后的语义违规 | 校验执行器停止 | 每种执行模式的案例数 |
|---|---:|---:|---:|---:|
| context | 4 | 3 | 1 | 9 |
| content | 1 | 0 | 1 | 9 |
| instance | 1 | 0 | 1 | 9 |
| content_raw（诊断变体） | 1 | 0 | 1 | 9 |

| C3 路线 | 绑定判定 | 执行器结果 | 实际持久化金额 |
|---|---|---|---|
| C3-referent-mutated / context / unchecked_live | True | written | 999.00 |
| C3-referent-mutated / context / verified_read | True | source_digest_mismatch | 无写入 |
| C3-referent-mutated / content / unchecked_live | True | written | 999.00 |
| C3-referent-mutated / content / verified_read | True | source_digest_mismatch | 无写入 |
| C3-referent-mutated / instance / unchecked_live | True | written | 999.00 |
| C3-referent-mutated / instance / verified_read | True | source_digest_mismatch | 无写入 |
| C3-referent-mutated / content_raw / unchecked_live | True | written | 999.00 |
| C3-referent-mutated / content_raw / verified_read | True | source_digest_mismatch | 无写入 |
| C3-referent-unchanged-control / context / unchecked_live | True | written | 101.00 |
| C3-referent-unchanged-control / context / verified_read | True | written | 101.00 |
| C3-referent-unchanged-control / content / unchecked_live | True | written | 101.00 |
| C3-referent-unchanged-control / content / verified_read | True | written | 101.00 |
| C3-referent-unchanged-control / instance / unchecked_live | True | written | 101.00 |
| C3-referent-unchanged-control / instance / verified_read | True | written | 101.00 |
| C3-referent-unchanged-control / content_raw / unchecked_live | True | written | 101.00 |
| C3-referent-unchanged-control / content_raw / verified_read | True | written | 101.00 |

这组结果将三个问题分开。

1. K 遗漏生效日期或成本中心时，语义改变可以通过窄上下文比较。摘要校验外部文件不会补齐 K 中缺少的业务字段。
2. 完整内容比较与实例绑定在这些语义变化案例中都能拒绝；实例绑定还拒绝同内容的新实例。这是责任对象的选择，不是额外的内容安全胜出。
3. 实例身份和候选字段相等本身不校验外部文件。实际文档消费测试中，共享摘要校验使各绑定方式都停止变更文档、放行未变文档。该收益来自共同执行检查。

独立评分器只读 SQLite，以执行前保存的 approved_effect 判定实际业务语义，再用独立解析的输入检查记录一致性；不导入 gate、投影或规范化实现。另在数据库副本中删除、新增、修改效果，验证评分器能发现异常。
本测试只实现选定绑定比较器及共同执行器，不是正文完整 G。金额按此实验声明的两位小数规则规范化；不能直接替代正文的 canonical JSON 语义。

## 核验与论文用途

X1 内部检查通过为 是；X2 内部检查通过为 是；两次完整运行的语义产物与 SQL 内容一致为 是。
本轮结果适合补充审批对象和设计选择的比较表。原在线续程实验继续承担 agent 行为和成本证据；本轮没有新增模型恢复率、人工审批成本或自然失配率的结论。

完整数据见两次运行的 OBSERVATIONS、CASES、ROUTES、SCORE、grid、RAW-EVIDENCE 及 effects.sqlite。复现命令见 README.md。
