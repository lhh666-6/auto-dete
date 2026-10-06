# Phase 2 formal 独立终审

审查日期：2026-10-07（Asia/Shanghai）。范围：新 formal 包的 kernel/oracle/runner/providers/generator/trajectories/analysis/orchestrator 与 run_formal.py。只读源码审查；仅在临时目录运行无模型复现。未改实验代码，未重跑线上探针，未启动正式采集。正式 freeze 文档在本轮审查时仍由主代理生成中，因而本文不能认证最终 master hash 或所有18类 freeze artifacts 已完整。

**当前 verdict：FINAL RETEST — PASS（正式采集前的代码与设计终审）。** 审查中发现的问题已经修补，最终独立复验见文末。下文“尚待修补”保留为原审查发现的历史记录，不代表最终未解决 blocker。完整全套tests、最新128case preflight和master封存由主代理随后完成；本文不声称已经验证尚未生成的最终master hash，也不授权正式模型采集。

## 通过的核心设计检查

- 两 policy 仍共享同一 Host/tool/reviewer/context guards，bound 唯一额外 gate 条件为 instance equality；两臂都保留 reviewed candidate。
- N 的实际 notice 要求刷新 preview，但没有强迫旧grant/newcandidate提交；合法 reuse-reviewed 和主动重授权仍可选。
- G 的 sibling/index action 明确标 harness_handoff，真实 host outcome 进入后续消息，不伪装 Agent attack。
- 生成器固定 L32/N32/G16/E16/V16/R16，128 task vectors；正式 ID 与 pilot ID 分开。128×A/B×context/bound，256 pairs/512 arms，repetition=1。
- E2 的有效快照与 locator 改变可以产生 V_eq=1/K_eq=0；V 合法 external advance 有前后快照/journal；R 内部 durable receipt 保留、首次可见 receipt path 暂时不可用，get_state仍可用。
- Oracle 独立于 Host/gate，copy-forward/value/source/context/continuity 分别核验；已证实 violation 优先于 unknown。新 V utility 已允许冻结的 external reference note。
- 正式 scorer 新增原始 provider response → parsed action → Agent tool_call 来源核验，TEST 轨迹显式标 engineering，不能进入正式 online evidence。
- assignment scenario×config 内 first arm 平衡、两臂相邻。2 provider lanes、每lane1pair，没有增加第三config/重复轮数。
- collection start 要求 readiness=YES 与精确作者运行指令；CLI先验freeze哈希，默认不会启动正式实验。
- paired bootstrap 保留两configs/两policies，以task聚类、scenario分层；exact McNemar按config分开；unknown continuity有上下界，而非填0。

## 审查期间发现且已经修复的实际问题

1. **Prefix deployment drift不暂停。** 原 orchestrator 仅看 suffix runtime_error，prefix drift漏检。最新代码已有 result.deployment_changed 和整pair events扫描；execute_pair 已阻断 drift后的新suffix采样。仍见下文跨lane暂停问题。
2. **缺safe-boundary时用空会话resume。** 最新loop返回 RESUME_BOUNDARY_MISSING，不再真正采样空history。无法证明安全边界的已有语义流程应终止保留unknown，不能重新注入G/E/V。
3. **恢复prefix时覆盖durable DB。** 初次无模型复现：authorization已落盘后中断，resume使 grants从1变0。整改后独立复测为1→1，prefix runtime_error，未重执行语义动作。safe-boundary正常restore与语义中断保留DB已分开。
4. **准确失败报告误标hallucinated success。** 初版把任何record/version/value final报告都当成功声明；最新准确报告旧状态的失败只记abandon，不再误判hallucination。
5. **State confirmation由最终成功倒推。** 最新分类改按当次get_state对应snapshot的goal判断，不再读取最终score的state_goal。
6. **Idempotent receipt把键冲突算确认。** 最新key_was_used要求同完整args且历史result.status=ok；失败缓存及IDEMPOTENCY_COLLISION不会计成功receipt重试。scorer的post-feedback新commit也排除精确receipt重放。

以上只表示具体缺陷在抽查代码中已修补。完整回归测试和全case deterministic重跑仍应由最终一致性流程覆盖。

## 尚待修补/验收的阻断项

### A. 网络读取阶段重连未覆盖（Major，已无模型复现）

`providers.py` 的 urllib request/read 目前只将 TimeoutError / URLError 映射retryable TransportError。连接已建立后 response.read可能抛ConnectionResetError、ConnectionAbortedError或http.client.IncompleteRead。当前这些异常会逃出loop，进入collection的unexpected infrastructure exception并暂停，而没有执行冻结的两次transport retry。

用patched urlopen/context.read模拟ConnectionResetError（没有网络/凭据）实测：`exception=ConnectionResetError, mapped_transport=false, retryable=null`。

要求：明确网络读中断映射为可重试transport错误；IncompleteRead保留partial bytes；HTTP错误主体读取失败也不能遮盖已知HTTP状态。仍不能笼统catch所有Exception掩盖实现bug。新增有意义的无模型测试验证总attempt不超过3，已有语义工具不重复，等待遵守wall deadline。

### B. Deployment drift只在另一个lane的pair结束时全局暂停（Major）

`orchestrator.py` 中paused由异常lane完成execute_pair后设置，另一个lane只在每个新pair之前检查。在飞的另一pair可能继续其余多个模型决策和第二policy arm，即使freeze约定“observable deployment change时暂停”。

要求：共享stop event传至provider/runner每次新模型调用的安全边界；已在飞响应保留，不擅自重跑，下一决策不得继续。不要在底层任意中断sqlite mutation；暂停语义必须与saved原消息、预算、未完成planned arms的状态一致。用两个deterministic provider lanes测试一个drift、另一个不能再开始后续新请求。

### C. 完整正式分析出口尚未证明可用（Major）

初审时analysis.py只实现两个primary paired estimates/McNemar，trajectories只有episode增量。需要冻结并验证能从完整assignment和原始结果生成四张要求表与全部planned arms，而非只遍历terminal/completed pairs：

- Table 1：512 planned、checkpoint、机制exposure、feedback delivery/rejection、U/state-goal、I/unknown/runtime；未启动/暂停也有行。
- Table 2：value/context/instance/admissibility/A_instance/source/copy-forward，精确幂等receipt与新transition分开。
- Table 3：全部delivered feedback episodes、第一有意义动作、完整primitive路径、U/I、calls/steps/reviews，失败考古覆盖所有U0/I0/unknown。
- Table 4：paired completion/calls/model-turns/auth/latency与usage，成功与失败都保留；budget-capped time-to-success按预声明上限，早失败不能当更快完成。
- 实际收费总账为每pair prefix一次+两个suffix；arm attribution中的共享prefix单列，不能重复汇总。Unknown monetary/usage成本为null，不跨provider直接混成统一token或货币口径。

如果上述出口由主代理随后新增，应以完整无模型512-row fixture核验后再freeze，而非采集后按结果设计输出。

## 冻结前应明确的设计/口径事项

### E：旧candidate并不会仅因发布E2而自动失效

当前publish_evidence新增E2，但保留E1不可变快照；Host.valid(c1)仍合法。E2候选配旧authorization确实两policy因K不同拒绝，但Agent收到“E2 available”之后也可以复用c1旧grant，直接成功。DeterministicAgent主动生成E2再试旧grant不能证明所有真实E arms都会进入K-mismatch。

这不是理由去优化prompt追逐rejection。冻结前明确：E是否测量changed-context exposure机会，实际K0/rejection为观测值，还是业务deliverable要求当前E2支持的执行。不可一方面允许c1复用，一方面在论文声称所有E旧authorization都必拒绝；也不可偷偷新增policy差异或把当前证据revision guard写进instance条件。固定共同语义、实际exposure denominator与预声明utility标准即可审查。

### Legacy recovery_path与episodes可能冲突

已产生的R deterministic记录中旧兼容字段recovery_path=abort_or_failure，但episodes的recovery_strategy=successful-confirmation-via-state且recovered=true。正式表3/论文应唯一使用frozen episode rules，或同步/明确废弃旧字段；不能从不同字段选择更好看的分类。

### Provider身份的可观测边界

现有探针记录A requested alias gpt-5.6-terra、CLI 0.160.1、low，returned model/revision不可观测；B endpoint api.deepseek.com/anthropic，requested/returned alias deepseek-v4-flash、temperature0。B返回字符串不证明immutable V4 snapshot。A provider_request_id实际上CLI thread ID，应在manifest明确identifier kind，不能称上游request ID。top_p/seed/revision等null应如实解释，不按表现换模型。

### Integrity与runtime失败应继续分开

中断语义动作不重复是正确保守处理，但保留真实DB/post snapshots非常关键。能独立证明“无违例且审计完整”的runtime失败可以I1；无法证明transition或原始文件缺失才unknown，不能把runtime固定I0，也不能为了好看统一unknown。

## 现有无模型验收证据

读取到 `preflight/deterministic-all-128/deterministic-fixture-results.json`：status PASS、128 host tasks/pairs、256工程policy arms、formal_online_arms=0、online_model_calls=0；六场景分配正确。它是单TEST配置的host流程验证，不是512真实在线样本，也不代表2lane恢复/identity drift全部故障已测试。

正式freeze最终还需核对：最新代码的所有测试结果、上述故障回归、所有freeze件完整性、18类artifact inventory、input/prompt/tool/source hashes、readiness/master hash交叉一致、freeze验证入口。未发现需要第三model、新场景、额外repetition或prompt sweep的理由。

**原轮结论：核心科学问题保持，N/G自主性与配对结构可保留。修好A/B并确认C及E口径后，再做最终hash级验收；本报告不授权启动512条在线实验。**

## FINAL RETEST — PASS

最终复验日期：2026-10-07（Asia/Shanghai）。核对了最新代码与 `frozen-formal/Phase2-protocol-FINAL.md`、`analysis-plan.md`、`scorer-definition.md`，并运行无模型测试；未调用实际provider。

- 独立运行 `test_formal.py`：19项测试全部通过（23.946秒）。覆盖E/V/R流程、实际N/G/E/V/R双配置工程轨迹的export、512 planned ledger、不选择性重跑、语义中断恢复、deployment drift与全局stop。
- 再次独立模拟response.read的ConnectionResetError：现映射 `DEEPSEEK_TRANSPORT`、retryable=true，并保存transport-error诊断；IncompleteRead部分原始bytes也由代码保留。
- 共享stop_event已传至IdentityProvider；对另lane已置stop后的decide独立验证返回COLLECTION_PAUSED，Provider.decide没有被调用。原轮跨lane下一决策暂停缺口已关闭。
- 最新exporter新增四表、完整失败考古、256个唯一prefix账本与全部512planned rows、paired工具/模型/授权/时间/usage差及预声明720秒suffix capped time-to-success；正式未完成时不允许最终推断/绘图。用真实N workflow工程轨迹加其余未启动planned arms独立运行export，得到512planned且无TypeError。event_exposure的字符串求和缺陷已修。
- Table2不再使用弱guard：复用独立 `oracle.transition_outcomes` 的全部条件；source/copy-forward也取相同独立检查。三值聚合独立验证：True+None→null，False+None→false，全部True→true，unknown不会被压成已证实inadmissible。
- E2最新证据业务边界已明确写入正式protocol；Host与独立recovery oracle共同要求当前证据。transition记录当次current_evidence_ref，Integrity加入独立current_evidence检查。用hostbug mutant强行让E1 superseded candidate提交成功，独立oracle确判I=0/current_evidence violation。c2/E2旧grant仍通过V_eq=1/K_eq=0展示共同context拒绝，新review可合法执行。两policy唯一差异仍是I_eq。
- Provider保存exact canonical prompt.txt，raw审计核对OUTPUT_RULE+可见inputs；final报告也绑定最后实际raw final action.report。冻结prompt hash定义与实际发送serialization一致，不把runner更正后的报告冒充Agent输出。
- 语义中断后的prefix DB授权保持1→1，不回退、不重执行；缺safe-boundary不采样空会话；幂等成功receipt与键冲突/缓存失败区分；准确失败报告不误标hallucinated success。

最终源码/设计审查未留下实际blocking错误。先前E业务边界与出口不足已关闭；legacy recovery_path不得替代正式episode taxonomy的口径在文档中明确。最终封存仍须主代理完成最新全套tests与全128case无模型preflight的source hash一致性、18类artifact inventory和master验证。若这些后续校验失败，readiness必须NO；否则可以报告正式freeze准备就绪。无论freeze YES与否，都必须等作者另行明确运行指令才启动512条正式在线轨迹。
