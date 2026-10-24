# v14 形式化模型、定义与实现边界独立审阅

审查对象：`D:/desktop/JSS论文/dke-publish`，HEAD `bff38c9a`；正文 `revisions/2026-10-24-ase-framing-v14/main.tex` 和对应 29 页 PDF，Online Resource 1 的 S2–S3，Online Resource 2 的 A9–A11、A14–A15，以及正文点名的冻结见证源。先读正文/补充定义，再读 audit；未改正式文件、未提交、未推送。只读核验 Git 对象，不改变稀疏 checkout。

## 结论

没有发现足以推翻四角色 contract、context/instance 包含关系或 endpoint indistinguishability 的核心逻辑反例，也没有发现把有限 Alloy 检查说成任意规模证明的现行表述。发现一个应在投稿前修正的**中等严重性工件一致性问题**：正文所引用的冻结 observation checker 并非处处遵守 canonical JSON equality；可在其接受的 history 域中复现“全部投影相同、局部 outcome 不同”。这不自动否定数学上按带类型/规范 JSON 值定义的 T1b，但它使可执行支撑的忠实性不成立。修复可以限于新增派生 checker、离线回归和报告更新，无须新 hosted 实验。另有一句较小的 scope 表述歧义。

因此：**不存在已证实的阻断投稿的实质理论逻辑问题；存在明确、有限、可本地修复的证据工件问题。建议修完再投。** 这不是“全文形式化已证明正确”的结论；没有重新运行 Alloy Analyzer，也没有对完整代码库作安全审计。

## 主要优点

1. **四角色真正分开。** 正文 §3.1，p.7，main.tex:141–149，区分 proposal `x_c`、authorized correction `x_a`、reviewed candidate `c_r` 与 persisted transition。改正值无需等于机器建议；提议保持不变，持久化必须使用授权值。这避免把 correction 错归给机器。
2. **P1 与 P2 不再混淆。** main.tex:159–171 和 A9 的 formal-mapping.tex:26–63 分别定义跨候选 binding 与 submitted candidate 内部 evidence/context 完整性，且明确 G 不得隐含 instance comparison。因而 context 策略并非先通过 G 偷偷变成 instance 策略。
3. **定义性结果与观测性结果分得清楚。** main.tex:175–187、197–210；A9 T2a–T2d（extended-specification.tex:76–97）正确说明 bound ⊆ context 是合取消去，严格包含还需可达差集，实际轨迹没有 substitution 也不证明策略在全部可能请求上相等。恢复路线、成本、完成度没有被声称能从定义推出。
4. **scope 链有必要前提。** main.tex:199，A10（extended-specification.tex:168–177）要求 `R ⊇ K`、trusted immutable lookup 与 checked record preserved to use；主 contract/agent study 的 `K = R` 与扩展 X2 的 `K ⊂ R` 明确分开。P_value = G 是共享其余义务的比较点，不是对所有授权机制的普适优劣排序。
5. **有限形式化范围讲得准确。** 正文 §5.1，p.11，main.tex:224；S2.4–S2.6，online-resource-1/main.tex:214–239；formal-mapping.tex:114–159。72 = 两个 profile 各 22 SAT + 14 UNSAT，SAT 是见证，UNSAT 是命令有限 scope 无反例；positive P6 只覆盖有前提的一步、被 admitted 的字段，非任意历史归纳。context 策略没有单独 Alloy assertion 也明确披露。
6. **TOCTOU 的真实边界比通常描述精确。** main.tex:171、187、289–293；S2.2（OR1 p.6，main.tex:165–167）；A14 native-contract.tex:16–37。候选 id→不可变 record→同 record 消费属于信任前提；external bytes 需要“验证 digest 且消费同一捕获 bytes”；principal allow-list 只有 commit-entry revalidation，并非可取消在途提交的线性化撤权。checkpoint/grant handles 在内存、无 restart-safe/distributed/concurrent replay 证明，均已披露。

## 问题 F1：冻结 observation checker 的投影/域相等仍混用 Python equality

**严重性：中等（工件与定义一致性）；建议投稿前修复。**

**正文和补充证据位置**：main.tex:149、185（p.7–8）；Online Resource 1 S2.6–S2.8，main.tex:231–247（p.8，精确引用此 checker，并说 equality repair 与 planner/trace/formal projection 一致）；Online Resource 2 A9.2 T1b，extended-specification.tex:48–58（p.10）。

**冻结源码**：`c6d512843c905cab6d8521dd8c914f7fb26d85ae:latest/code/formal-fixed/observation_witnesses.py`，SHA-256 `32bed3ae1aed344c3bf5c57c7f7e545e4e05836a154ae14d278be3aebd6b7832`。`observe()` 的 D_V（行 160–169）返回原始 Python proposal/authorization/successor values；`project()`（188–189）保留它们，而归档 verify 的 projection equality 用普通 tuple `==`。另一方面 `_attribution_ok` 的 authorized/committed equality 使用 `_canonical_equal`（27–37、相应 attribution 函数）。`validate_history_domain`（220、226）又用普通 dict equality 验证 commit 连通性和 endpoint。

**可复述反例一**：从合法单字段 history 构造 predecessor 90、proposal 100、授权整数 1、commit 整数 1、正确整数 1 source；另一 history 仅把 authorized value 改为 Boolean true。二者均通过 domain predicate；Python 的 `1 == True` 使全部五类 projection 相等；`_canonical_equal(1, True)` 为 false，故原者 outcome 为 admissible，后者为 inadmissible。原文件 `verify()` 本身仍 PASS。

只读复现脚本：`D:/desktop/JSS论文/tmp/v14-review/observation_equality_repro.py`；在 dke-publish 目录运行：

```text
python D:/desktop/JSS论文/tmp/v14-review/observation_equality_repro.py
```

脚本只从 Git 对象读源并在内存执行；输出：

```text
Existing verification: PASS
Domain errors: () ()
All projections equal: True
Good outcome: ('admissible', 'complete-successor', 'complete-trace')
Bad outcome: ('inadmissible', 'complete-successor', 'complete-trace')
```

**同一根因的反例二**：保持实际 commit step 的 after 为整数 1，把声明 successor endpoint、授权、source 全改为 Boolean true。`validate_history_domain` 仍返回空错误，`normative_outcome` 为 admissible，尽管按 canonical JSON equality，该 commit sequence 并未到达所声称的 endpoint。该例同样在脚本末尾执行。

**影响**：实现版 π_D 的 equality 不足以支持“相等投影 ⇒ 相同 O_obs”，其 domain predicate 也比所宣称的 canonical 连通 history 域宽。报告的五组既有 witness 仍可成立；问题没有推翻 policy 的合取包含、identity-only endpoint witness、生产 gate 已修正的 canonical 比较，也没有显示 hosted 轨迹统计有误。

**合理反驳**：T1b 是对数学上的 canonical/带类型 value observation 的因子分解论证；冻结 checker 只声称核验有限构造，未声称穷举一般 admission oracle。此反驳足以阻止把问题升级为核心理论推翻，但不能消除它作为被精确引用可执行投影的语义不一致。S2 同时提及 handoff 的另一 repaired construction；本审查没有取得该未检出路径，不能声称它也有此 bug。

**最小修改**：保留历史 freeze，增加独立版本派生 checker：D_V 中值以 canonical JSON 字符串或显式类型标签返回；history 连通和 endpoint map 比较也统一 canonical equality；补 1/true、2/2.0、嵌套值的投影与域回归；重出见证报告并把正文 S2 入口指向该版本。T1b 附一短句明确 projection equality 采用 canonical JSON 值相等，可使数学/实现关系可核验。

**是否必须新实验**：无需新模型调用或 agent 样本。需要新的离线回归/见证检查记录；通常无需重新运行全部 Alloy（除非同步修改 Alloy 的 Value 映射）。

## 问题 F2：re-preview 句的“matching grant”适用 scope 可说得更明确

**严重性：低；文字澄清。** main.tex:167，正文 §3.2 p.8，在刚定义两种策略后说 “re-preview can materialize a new candidate requiring a matching grant”。

**影响及反例**：按该段已经定义的 context policy，c2 若与 c1 的 K 相同且 G 成立，原 a1 就允许 c2；并不必然需要授权 target = c2。句子单独读易被当成两种策略共有的生命周期要求，与本文核心比较发生语义冲突。

**合理反驳**：“can” 可以解释为重预览可能改变 context，或者此处的 matching 指所选策略要求的匹配；后文 §3.4/A9 已清楚解释两路恢复，因此不构成公式错误。

**最小修改**：改成 “... can materialize a new candidate, which requires a new matching grant under instance binding.” 若想涵盖 context 变化，再补 “Changes to retained context require renewed authorization under either policy.”

**是否必须新实验**：否。

## 应保留的限制与投稿判断

- T1 的充足性来自 O_obs 被定义为五个 observation checks 的函数；它是所宣告分类的 irredundant basis，不能包装成发现了普适最小日志格式或完整操作系统行为理论。v14 A9.2 现有说明基本足够，建议不要在摘要/cover letter 另行拔高。
- T3 的 soundness 仍是“信任 gate/adapter + 检查关系与安装同对象原子一致”等前提下的 conditional argument；Alloy 与 SQL oracle 是不同层次佐证，不能让其承担认证、真实展示、不可变存储、分布式撤权的证明责任。v14 目前基本守住此边界。
- 原 candidate+grant 的 reuse 条件是 identity-only mismatch、grant active/unconsumed、候选保持不可变、evidence 与 predecessor 仍有效、当前授权主体仍可用、提交修正值与 idempotency key 可用，并满足其余 G。32 集合的 post-hoc audit 只证实 rejection 时的可用且可见，不证实在生产等待后的持续有效或路线最优。当前 main.tex:187–191、447 和 availability 脚本/summary 均做了相应限定。
- “trace category complete” 在 O_obs 中只意味着 local source checks；完整 P6 仍需 deep chain、有效 immutable references、良构 predecessor 与 unique transitions。A9.1:33 和 T3:108 已清楚区分，不建议将这两层合并措辞。

总体评价：定义一致性和边界自律较强；理论贡献以澄清/组织已知义务为主，真正经验增量在恢复选择与成本。以“核心证明有致命错误”拒稿不公平；以“定义性形式化的新颖性有限、应用现实边界尚窄”提出贡献与外部效度问题则合理。F1 应落实修正后提交，所需工作规模很小。
