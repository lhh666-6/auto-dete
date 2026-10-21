# 原正式 B 输出终止：投稿后离线诊断

2026-10-14。**原论文的 18 条 B `invalid_output` 都以一次达到 4096-token 上限、无法解析成动作的响应结束；该末次请求已收到格式修复提示。因此不能把这 18 条解释为自然结束后的自主格式不遵从。** 原始终止标签、任务失败计分与完整性评分均未改动。

这是看到问题线索后的离线诊断，不是预注册新实验。没有调用模型、扩大预算补跑或筛除失败；原 512-arm ITT 保留。本次完整普查 B 的 128 个任务、256 arms，128 份共享 prefix 只计一次。

## 全部响应，而非只查失败

| 项目 | 观测 |
|---|---:|
| provider 请求、完整原始响应、model_response 事件 | 各 1,372 |
| shared prefix / context suffix / bound suffix | 384 / 493 / 495 |
| 自然结束且可解析动作 | 1,293 |
| `max_tokens` 且无 text | 76 |
| `max_tokens` 且有不可解析的部分 text | 3 |
| `max_tokens` 且动作可解析 | 0 |
| 自然结束但动作不可解析 | 0 |
| 已记录 transport retry / model_error / HTTP 或 EOF 故障 | 0 / 0 / 0 |

79 次输出截断全部发生在 suffix；prefix 没有输出截断。这里的“截断”由原始响应的 `stop_reason=max_tokens` 确认，不是由 token 数碰巧等于上限推断。原适配器没有保存逐请求 HTTP body；4096 上限来自冻结配置与适配器源码，请求本身的证据为事件、输入消息与保存的 prompt，不能冒称 wire capture。

| 政策 | 全部分母 | 至少一次 suffix 截断 | 截断响应数 | 原 `invalid_output` | 原完成 U |
|---|---:|---:|---:|---:|---:|
| context | 128 | 33 | 43 | 10 | 117 |
| bound | 128 | 28 | 36 | 8 | 119 |

61 条曾截断的 arms 中，**42 条后来正常结束并完成任务、18 条以 `invalid_output` 终止、1 条仍是原 `termination_missing`**。不能将“曾出现截断”等同于“被截断导致失败”。所有 256 arms 的原终止为 236 `agent_final`、18 `invalid_output`、1 `termination_missing`、1 `not_started`。

## 18 条终止的具体链条

每条失败都有两次 `max_tokens` 不可解析响应：共 36 次，34 次空 text、2 次部分 text。**末次响应为 17 次空 text、1 次部分 text**，且末次输入都含实际 `format_error` 反馈。余下 43 次截断对应后来成功的 42 arms 和原 unknown 的 1 arm。

只有 13 条在第一次和第二次不可解析响应之间没有可解析动作；另外 5 条中间存在合法格式动作：`FORMAL-E-001-B/bound`、`FORMAL-N-027-B/context`、`FORMAL-V-001-B/bound`、`FORMAL-V-008-B/context`、`FORMAL-V-008-B/bound`。因此这里是**一次格式修复机会在逻辑历史中已使用后，后续不可解析响应触发终止**，不是 18 次“连续 transport 重试失败”。transport retry 实际为零。

末次为部分 text 的失败是 `FORMAL-N-031-B/bound`。另外两次部分 text 分别出现在 `FORMAL-E-008-B/context` 的较早截断，以及后来成功的 `FORMAL-V-012-B/context`。

`FORMAL-N-020-B/context` 虽然最后保存的响应也是截断，但缺最终终止/状态记录；不能据此补造终止原因。它和未启动的 bound 仍为原 unknown I、U=false，不改分母。

全部失败及首末响应位置在 [invalid-output-arms.csv](invalid-output-arms.csv)，每份原始响应路径、请求序号、format_error 可见性及事件关联在 [attempts.csv](attempts.csv)。例如 `research/agent-policy-phase2-formal-2026-10-07/formal-results/FORMAL-G-001-B/context/provider-raw/0-0/response.json` 和 `1-0/response.json` 都只含 thinking，停止原因为 `max_tokens`。

## 配对位置与能够解释的边界

按“末次截断后 `invalid_output` 终止”分组，128 配对中：

| 终止位置 | 配对数 | 原 U 差值之和（bound − context） |
|---|---:|---:|
| 两侧均无此终止 | 113 | 0 |
| 仅 context | 7 | +7 |
| 仅 bound | 5 | −5 |
| 两侧都有 | 3 | 0 |
| 全部 | 128 | +2 |

这只是原 119−117 的算术分解。它揭示原完成差异与有限输出预算下的终止位置重合，**不能识别放宽预算后的反事实完成率、纯预算因果效应、等效或非劣**。按“任意早期截断”分组的完整位置也保留在 [pairs.csv](pairs.csv)，没有删除任何配对后重算结果。

工具调用数只计真正执行的动作；截断导致没有动作时，调用数可能被提前终止压低。格式修复又会增加模型轮次、输出用量和等待。因此调用少不自动表示恢复更有效率；实际 suffix 时间和失败赋 720 秒的 capped time-to-success 也不是同一种量。本审计保留原所有成本列，未用失败排除法证明无额外成本。完整续行成本仍由独立成本核对处理，可按 `pair_id + policy` 关联 [arms.csv](arms.csv)。

以下结论不改变：原 B 的 U=117/128 与119/128、原 512-arm ITT 及统计推断、实际已执行转换的 I 和来源连续性判定、unknown 的处理，以及 B 的16/16条件恢复描述。特别是 G-001/G-005 context 的不一致实例执行先于输出截断，截断不会撤销这些已经发生的完整性违例。A 的额度故障不属于本次响应普查，不以 B 的结果重新解释。

## 拟议替换措辞（仅备选，不改投稿稿件）

> Configuration B's 18 invalid-output terminations ended in provider-reported output truncation at the 4096-token cap, with no parseable action after the history's format-repair allowance had already been used. Five histories contained intervening parseable actions between their two truncated responses. These outcomes remain failures in the original intention-to-treat ledger; they should not be interpreted as naturally completed format noncompliance or as estimates of behavior under a larger output budget.

可另补一句：Across all 1,372 recorded B responses, 79 were output-truncated; the 61 affected arms included 42 later task completions, 18 invalid-output terminations, and one arm with missing termination evidence.

## 完整性与复跑

19 项关键分类测试通过。10,409 个原输入文件在审计前后 SHA-256 一致；1,372 份原响应提取文本与事件一致，事件引用的输入和响应等 artifact 哈希核验无异常。上述核验是本诊断的输入与关联完整性检查，不替代原论文的全部 I oracle 或形式证明。

实现、输入清单与机器可读结果见 [README.md](README.md)、[summary.json](summary.json)、[integrity.json](integrity.json)。本目录之外未写入任何文件；原日志、scorer、稿件和新 ablation 均保持不变。
