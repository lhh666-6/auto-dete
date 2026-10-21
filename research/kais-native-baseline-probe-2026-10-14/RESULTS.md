# 强近邻离线对照：结果与返修用途

2026-10-14；对应已提交 KAIS 稿件的投稿后探索性补证。

**已完成对象映射、留档执行和异目录重建。共同可表达的准入行为一致，未得到本文优于 CK 的证据。** 本轮是 CK 原生抽象模型与本文原有 Host 的准入探针，不能替代完整外部系统 benchmark。它的价值是明确强近邻已经做了什么，并阻止用一个无法表达审阅实例的抽象模型制造“本文胜出”。

## 1. 实际执行结果

下表两种关系各执行一次：Accept 为提议 20、授权 20；Correction 为提议 20、授权 21。二者在本轮的准入结果相同。**在 CK 中，两值只由适配器编码，模型未单独验证人工纠错关系；两行重复不能算额外纠错能力证据。**

| 场景 | 本文 context | 本文 bound | CK 作者模型 | 比较边界 |
|---|---|---|---|---|
| 正常提交 | 接受 | 接受 | `Commit` | 粗粒度准入一致 |
| 同上下文，新候选沿用原授权 | 接受 | `INSTANCE_MISMATCH` | `not_representable` | 只有本文内部政策比较；CK 没有对应的独立人工审阅候选对象 |
| 授权后发布 E2，仍提交 E1 候选 | `EVIDENCE_SUPERSEDED` | `EVIDENCE_SUPERSEDED` | `RejectExpiredAtActivation` | CK 接收适配器计算的失效判据，不是原生证据字节/签名验证 |
| 授权后推进前驱，仍提交旧候选 | `STALE_VERSION` | `STALE_VERSION` | `RejectStaleHead` | CK 前驱变化由另一个合法原生提交产生 |

- 计划记录 **24 条**：8 格 × 3 路。实际执行 **22 条**；CK 的两个实例替换格子保留为不可表达，不计通过率或失败率。
- 六个共同可表达格子的三路准入决定一致，共 18 条粗粒度准入记录；其中两种纠错关系在 CK 只是外部编码，证据失效在 CK 只验证 supplied predicate 的处理。
- 主矩阵有 **14 次初始拒绝**：context 4、bound 6、CK 4。每次拒绝均未改变当时的权威业务状态，且每条均有脚本构造的合法恢复成功见证。**这是路径存在性，不是 Agent 自发恢复率。**
- 所有 **22 条可执行记录**的原请求重放均返回同样结果，没有重复改变权威状态。拒绝诊断可以增加；“不变”不指整个存储字节不变。
- 另有 **11 项控制**：7 项 CK 原生保护、2 项新实例重新授权通过、2 项错误提交原提议值被拒绝，均符合预先锁定的检查规则。
- 全部 **150 项断言检查通过**。这是对同一小矩阵及控制的实现核查数，不是 150 个独立实验、样本或形式证明。

CK 七项控制分别是候选 root 不匹配、最终新鲜度失效、无效后继、自我扩权、已用 pid 改 core、已用 pid 改 attempt，以及新 pid 重复已消费 effect。均调用未修改的原生 `submit`。不能将 root 不同的控制结果冒充“相同内容、不同实例”的结果。

## 2. 事实与未测项

本文 Host 的 16 条主记录均保留原始值、授权值、尝试候选、已审候选、证据和前驱状态、前后字段及来源。完成预定续行后，每条均只有一个研究内提交，正确执行授权值并保留未改字段/来源；前驱变化场景另外保留环境推进，不将它计为重复研究提交。context 的实例替换接受属于其声明的政策行为；没有用本文 I 把它改标为通用业务安全失败。

CK 原始 Request、完整前后 State、响应均留存；准备时的 head/root 固定，恢复使用新 pid、新摘要和当前准备包，未清除拒绝记录。它的业务最终值、人工审阅实例相等性及字段级来源记为 `null`，不是错误或 0 分。源码的阶段标签也不等于实际执行了完整 witness/hash 验证。

**最关键的结论是：缺少可测对象不等于缺少系统能力。** [CK 原文 §2.2–3](https://arxiv.org/html/2608.11632v1) 已规定提案、证据、解释器和候选状态的绑定。本文四角色关系可能由这类通用机制承载；当前模型不足以判定这种承载是否已满足全部具体纠错义务。现在直接加一个身份不等即拒绝的“CK＋本文”适配器，会把待证明的差异写入规则，不能据此证明新增安全能力。

## 3. 对本篇论文与执行方案的决定

1. **保留本轮结果，作为近邻能力映射及方法公平性的返修储备。** 它适合补充材料中的短表和代码入口；不能替代主表、改写原队列或包装成新的强效果结果。
2. **当前不扩采在线实验。** 本探针没有给出一个能通过增加模型样本解决的外部方法差异；重复采样这些已知准入规则不会增强创新性。
3. **不继续实现缺乏对象依据的 CK＋身份门。** 若后续要做完整直接对照，先取得可运行的具体审批载体，明确它原本绑定的对象，以及独立业务对对象互换和重新授权的要求。已有绑定能力须全部保留。
4. **当前可以收紧贡献定位。** 值得强调的是纠错前后值的归属与四角色执行关系、具体后继/来源义务，以及拒绝之后实际 Agent 行动与成本的证据。不能改称“首次实例绑定”或“近邻无法恢复”。
5. **仍未解决的两项缺口清楚保留：** 完整、同层级的外部系统比较；实例不可互换的独立应用依据。本轮没有测生产部署收益、真人审核成本、自然替换发生率或业务语义等价。

实际审稿若只要求更清楚说明区别，可使用映射表及既有证据回答；若明确要求同层级系统实测，则需补可比实现，不能用此探针声称要求已满足。CommitGuard 产物过期、Cordon 代码尚未定位的状态沿用[前轮审计](../../reviews/kais-execution-plan-2026-10-14/baseline-audit/BASELINE_AUDIT.md)，本轮未重新检索或联系作者。

## 4. 可用于返修的贡献表述草案

以下是储备文字，尚未写入已提交稿，也不是已经收到的审稿意见答复：

> Existing authorization and transactional continuity mechanisms already bind proposals, evidence, and state transitions, and may serve as substrates for correction-aware execution. Our contribution is an explicit relation separating the original proposal, the authorized correction, the reviewed candidate, and the executed transition, together with concrete successor and provenance obligations. The online evaluation examines how agents continue after enforcement feedback, including candidate reuse, renewed authorization, and continuation cost. We do not claim that generic identity binding or recovery is new. The native-model probe reported separately checks overlapping admission behavior; it does not establish superiority over a deployed continuity system.

此定位需要与原稿现有定义和证据共同阅读；不是对“组合一定有足够创新性”的保证。未来有价值的实验必须先说明哪项可观察结论会改变，而不是默认增加任务或更换模型。

## 5. 可复核入口与记录

- [协议及对象映射](PROTOCOL.md)：已披露代理先前的内存 API 可运行性检查；本轮非盲、非预注册。规则在留档运行前锁定。
- [冻结清单](freeze.json)：2026-10-14 07:51:54 UTC（北京时间 15:51:54），11 个文件的 SHA-256，包括两个原生实现、依赖输入、协议、探针及提交版文件。原稿和正式输入未修改。
- [逐项原始结果](results.json)：2026-10-14 07:51:55 UTC，包含完整调用/状态记录、不可表达项、检查和错误列表。
- [异目录重建](recheck.json)：从 Windows 临时目录启动同一入口，语义结果完全一致。不是新虚拟环境或跨平台复现；原生时间戳及派生证书哈希可变化，因此分别保留原始记录。
- [执行入口](run_probe.py)：Python 3.11.9，`jsonschema` 4.26.0；CK 部分仅标准库。输入校验失败拒绝运行，已有输出拒绝覆盖。

仓库根目录执行（已安装上述依赖）：

```powershell
python -X utf8 -B research/kais-native-baseline-probe-2026-10-14/run_probe.py --out research/kais-native-baseline-probe-2026-10-14/reproduced.json
```

语义指纹：`fb22540c66f437fa01615eb4d9e0016a6da80aeaf96a2e6ab65df7f858534be7`。该指纹比较规范化结果，不代表不同采集重复独立。

两路独立只读核查分别检查 CK 映射及 Host/评分。运行前建议的“异常部分记录保留”和“核对具体拒绝原因”已在冻结前修复。留档运行后，Host 核查代理直接从原始 trace/final_state 独立核出 8 次初始接受、14 次拒绝及合法恢复、22 次稳定重放、11 项控制，并确认外部版本推进未被覆盖；未发现该探针范围内的实质问题。没有另行运行全面论文多专家评审。
