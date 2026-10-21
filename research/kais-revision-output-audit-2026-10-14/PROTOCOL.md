# 投稿后离线输出诊断协议

日期：2026-10-14。此协议在编写分析实现和全量普查前固定；先前已抽查并检查 18 条 invalid_output 的原始响应，因此不是盲态预注册。目的是细分既有终止记录，不改变原正式实验。

## 输入与分母

- 唯一研究分母：原正式 B 的 128 个任务 × context/bound，共 256 arms；共享 prefix 为 128 份，provider 请求/响应统计只计一次。
- 原正式 512-arm ITT、U/I、缺失与 unknown、原始失败均保持原值。A 不纳入本次响应普查，也不替换补充 A。
- 读取 `agent-policy-phase2-formal-2026-10-07/formal-results/*-B` 的全部事件、请求输入、provider-raw、状态和评分；读取冻结配置/解析器及 `phase2-results-snapshots/2026-10-07T021002Z/original-formal-analysis` 的原表。
- 原始 B 适配器未保存 HTTP request body；request 证据为 model_request 事件、model-inputs、prompt.txt。输出上限的依据明确标为冻结配置和适配器，而非虚构逐请求 wire capture。
- 全部上述输入逐文件 SHA-256 在运行前后核对；只写本目录，无 API、无模型调用、无原文件导入副作用。

## 逐 attempt 规则

以 `(pair_id, phase, decision_index, transport_attempt)` 为键，取事件中 model_request 与磁盘 provider-raw 目录的并集；不把格式修复的下一决策称为 transport retry。保留缺响应、未完成请求、HTTP/鉴权、真正部分字节/EOF/传输故障与 malformed envelope 的独立字段。

1. 完整响应的 `stop_reason=max_tokens` 才标 provider-reported output truncation；仅 output_tokens 等于上限不足以判定。
2. 拼接 type=text 的块，以冻结 `parse_action` 的语义做离线可解析性检查。分别报告空 text、非空但不能解析（partial/nonparseable）、可解析动作。可解析不等于工具正确或 U 成功；不推断隐藏 thinking 的语义。
3. 自然结束但不可解析，单列 natural_stop_empty / natural_stop_nonparseable；未知停止原因保留未知。
4. 记录 request/response/error 事件与路径、请求输入是否含 format_error、序号、停止原因、usage、末次 received response / 末次 request。保留原事件与原始文本匹配检查。

## 逐 arm 归因

保留原 terminal、U、I、原工具调用/轮次/时间。另加截断诊断，不覆盖原标签。

- 只有原 terminal=invalid_output、终止前最后一个 provider outcome 为不可解析 response，且该 response 的停止原因为 max_tokens，才标 `invalid_output_after_output_truncation`。
- 额外记录最后请求是否已经带格式修复反馈、前面不可解析响应的 ID/子类型及中间是否有合法动作。只有可见修复链和最后不可解析响应都得到证据支持，才细分 `..._after_format_repair`。早期截断后自然恢复、后续 transport failure、缺终止等，均不能自动归入上述终止原因。
- prefix 截断记录独立，并在 arm 中仅提供关联字段，不把共享调用重复计费。没有初始化/最终终止的 arm 仍保留在 256 分母。
- 对不可解析与 runtime/EOF/auth/unknown 的混合链，保留各自事件；不以输出截断取代真正的最终故障。

## 配对与解释

输出全部 128 个 context/bound 配对；差值统一为 bound-context。列出两侧 U、terminal、截断归因、工具与轮次及实际时间。按受影响位置（neither/context_only/bound_only/both）分解原 U 差值的算术贡献，不把这些事后分组当作随机化效应。

审计可说明原格式终止是否受测量预算制约，以及工具数/时间为何不能自动解释为纯恢复效率；不能识别扩大预算后的反事实 U、纯预算因果效应或非劣。禁止删除截断者、改分母或只补失败样本；不重算排除截断后的完成率。拟议投稿措辞仅放本报告。

## 验证与交付

关键分类单测覆盖：截断空/partial/parseable、自然结束格式错、早期截断但后续自然结束/传输失败、真实格式修复链、缺终止。交付 analysis.py、test_analysis.py、attempts.csv、arms.csv、pairs.csv、summary.json、输入前后 SHA 清单、完整性检查和 RESULTS.md。结果使用原始证据路径，可与成本审计按 pair_id+policy 关联。
