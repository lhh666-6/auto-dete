# 授权策略 × 输出预算：同期续行敏感性结果

完成日期：2026-10-14（Asia/Shanghai）。采集从02:41:53至03:55:26 UTC，约73.5分钟。固定的96条续行全部终止，未开始和不完整条目均为0。

**本批扩大预算组48/48完成、未观察到输出截断；低预算组45/48完成，3次失败均在截断后以格式错误终止。扩大预算下两政策的观察完成率相同，实例完整性的分离仍然存在。** 这是当前部署、归档审查检查点之后的描述性敏感性证据，不证明政策等效，也不替换原论文结果。

## 设计与分母

从原128个冻结任务中按E/G/L/N/R/V六情境各随机抽取4个任务。每个任务经历context/bound × 4096/393216四条件，共24任务、96续行；每格一次，任务块和Williams臂顺序在采集前固定。CL、CH分别表示context的低/扩大预算，BL、BH表示bound的低/扩大预算。

四臂复用同一原始B审查检查点及完整可见前缀，重新执行原情境事件。两预算使用相同当前部署、temperature=0及共同等待上限：单请求1800秒、续行21600秒；原20决策步、24工具调用、整条历史一次格式修复规则保留。低预算也放宽了等待时间，因此本轮并非原90/720秒设置的精确重跑。

U表示条件于归档检查点的完整任务完成；I表示实例完整性，二者独立。总体以24任务等权计算，对应六情境等权，不等同原128任务的情境权重。

## 完成、完整性与交互

| 条件 | U=1 | I=1 | I=0 | invalid_output终止 | 截断响应 / 全部响应 |
|---|---:|---:|---:|---:|---:|
| CL：context / 4096 | 23/24 | 20/24 | 4/24 | 1 | 6/100 |
| CH：context / 393216 | 24/24 | 20/24 | 4/24 | 0 | 0/96 |
| BL：bound / 4096 | 22/24 | 24/24 | 0/24 | 2 | 8/93 |
| BH：bound / 393216 | 24/24 | 24/24 | 0/24 | 0 | 0/100 |

没有未知U或I。每个条件的state_goal达成数与U=1数相同。context中每预算的4个I=0均来自G的程序化交接：同值、同保留上下文的新实例使用旧授权获准提交。它符合context准入规则，但不满足本文的实例完整性要求；这不是4次自然发生的代理替换。

按任务先做差再平均：

- 低预算政策差 `U_BL − U_CL = −1/24`，即−4.17个百分点。
- 扩大预算政策差 `U_BH − U_CH = 0/24`。
- 交互 `(U_BH − U_CH) − (U_BL − U_CL) = +1/24`，即+4.17个百分点。
- 同政策扩大预算减低预算：context为+1/24，bound为+2/24，分别为+4.17和+8.33个百分点。

交互来自三个任务：FORMAL-V-016和FORMAL-V-011各为+1，FORMAL-N-028为−1；其余21任务为0。差异不能据此概括为稳定的政策×预算交互。本轮未做p值、bootstrap区间或等效性检验；全部结果已知时，缺失结果的识别上下界与观察值重合，这不是零宽置信区间。

## 截断与失败

低预算193次响应中有14次报告`stop_reason=max_tokens`，涉及11条臂：CL有5条，BL有6条。其中8条最终完成；另外3条各有两次截断，消耗一次格式修复后以`invalid_output`终止：

| 任务 | 条件 | U / I | 工具调用 | 模型请求 | 实际续行秒数 |
|---|---|---|---:|---:|---:|
| FORMAL-N-028 | CL | 0 / 1 | 0 | 2 | 50.547 |
| FORMAL-V-016 | BL | 0 / 1 | 0 | 2 | 50.484 |
| FORMAL-V-011 | BL | 0 / 1 | 0 | 2 | 53.547 |

三者均未达到state_goal，末次提供商响应仍为截断；失败保留在原定分母中。不能将全部14次过程中截断都计为14次任务失败。

扩大预算196次响应全部报告`end_turn`，没有截断或格式修复；其中13次提供商报告的`output_tokens`超过4096，最大8447。因此扩大预算实际容纳了低预算无法一次容纳的输出，并非仅修改一个未触及的上限。两预算继承的前缀格式修复数均为0；低预算续行新消耗11次修复。全批389次请求均收到响应，无外层传输重试。

## 全部终态的成本

以下均包含失败臂，三条失败续行合计154.578秒已计入。时间是新续行实际墙钟时间，未使用旧720秒封顶值。旧前缀仅作为输入复用，没有重新采集；用量表仍包含本轮请求中发送的历史上下文及缓存读取。提供商用量字段均有记录，分别列示，不换算货币。

| 指标 | CL | CH | BL | BH |
|---|---:|---:|---:|---:|
| 续行时间合计（秒） | 1132.779 | 1116.097 | 1068.982 | 1037.641 |
| 每臂时间均值（秒） | 47.199 | 46.504 | 44.541 | 43.235 |
| 每臂时间中位数（秒） | 39.836 | 33.133 | 38.586 | 39.383 |
| 代理工具调用总数 | 71 | 72 | 63 | 76 |
| 模型请求 / 响应 | 100/100 | 96/96 | 93/93 | 100/100 |
| output_tokens | 172249 | 171582 | 164153 | 155614 |
| input_tokens | 29712 | 28690 | 26024 | 30439 |
| cache_read_input_tokens | 236032 | 227072 | 217467 | 236032 |
| cache_creation_input_tokens | 0 | 0 | 0 | 0 |

全部24对的bound减context时间差：低预算均值−2.658秒、中位数+3.267秒，范围−56.078至+27.954秒；扩大预算均值−3.269秒、中位数−1.985秒，范围−53.312至+33.203秒。扩大预算减低预算的时间差，context均值−0.695秒、中位数+0.157秒；bound均值−1.306秒、中位数+2.852秒。均值与中位数并不呈现一致的方向，不能据此声称稳定节省时延。

低预算bound的工具调用总量较少，包含两条在任何工具动作前已终止的轨迹；这种差异不能直接解释为更高效率。完成率、调用量、输出用量和实际时间应共同阅读。

## G的拒绝后恢复

同4个G任务在低预算和扩大预算下，bound均为4/4完成、4/4保持I=1。8条bound续行都实际收到可恢复的实例失配反馈，首个有意义动作均为`commit`，通过复用已审阅实例恢复，无额外重新授权。这里是同4任务的两个预算条件，不能视为8个独立新任务。

本批G任务每种预算下的代理工具调用均为context合计2次、bound合计5次，即每任务均值0.50和1.25次，配对平均增加0.75次。该成本对应这4个检查点的本轮续行，不替换原论文的G成本估计。

G中完整续行的bound减context时间差，低预算均值15.473秒、中位数19.156秒；扩大预算均值18.227秒、中位数16.938秒。低预算仍有一对为−4.375秒。这些是确定性审查器条件下的完整续行差，不是纯修复动作耗时或真人审批成本。G是强制暴露探针，不能估计自然失配率或保证未来总能恢复。

## 答审价值与边界

本轮为“原完成率是否受输出限制影响”提供了比失败归类更直接的同期证据：当前任务样本中，扩大预算未再出现截断终止，两政策均完成24/24；观察到的低预算完成差在扩大预算下为零。实例完整性的政策分离在两个预算下都保留，说明这项分离在本批中没有依赖低输出上限。

仍须保留四项边界：这是同一构造任务族、每任务每条件一次的小规模补证；起点是已达到的归档检查点；当前模型别名不能证明与原采集时是同一不可变版本；共同等待上限也已改变。结果不能恢复原18条失败在旧模型、另一预算下的反事实，不能证明政策等效、非劣或普遍效用提高，也不能回答自然工作流的采用价值和真人审核负担。

可供以后返修使用的英文说明：

> In a separately frozen post-submission sensitivity study, we continued 24 archived review checkpoints under a contemporaneous 2 × 2 design crossing authorization policy with output caps of 4,096 and 393,216 tokens. Both budget conditions used the same extended waiting limits. Completion was 23/24 for context and 22/24 for bound at the lower cap, and 24/24 for both at the expanded cap. The descriptive bound-minus-context completion difference therefore changed from −1/24 to 0, giving a task-level difference-in-differences of +1/24. Fourteen lower-cap responses reported output truncation; three trajectories terminated with invalid output after truncation and remain counted as failures. No expanded-cap response was truncated, and 13 reported more than 4,096 output tokens. Instance integrity remained 20/24 for context and 24/24 for bound under each budget, with context violations confined to the standardized G handoff. These results document budget sensitivity in the sampled continuations; they do not establish policy equivalence, recover historical model counterfactuals, or replace the original cohorts.

## 证据入口与核验状态

- [冻结协议](PROTOCOL.md)、[分配清单](allocation.json)、[冻结文件清单](freeze.json)。
- [汇总](summary.json)、[独立重建及逐请求诊断](analysis.json)、[96臂原值](cells.csv)、[24任务配对](pairs.csv)。原始请求、响应和事件在`live/<task>/<low|high>/<context|bound>/`。
- 离线重建96/96条轨迹，评分及请求预算/响应/事件证据核查错误数为0；同政策跨预算首次输入和请求差异、四臂检查点一致性核查通过。最终汇总`audit_pass=true`。20项运行层测试加33项分析层测试通过。
- [最终独立审查](../../reviews/kais-budget-sensitivity-2026-10-14/final-audit.md)结论为PASS，复核389次请求与响应、24任务配对、失败保留及成本；其中375次响应为`end_turn`、14次为`max_tokens`，无传输错误或外层重试。
- [原材料保护核验](protection-after.json)：14597个文件无变化；冻结核验通过。已投稿主文、原512臂、补充A和此前实验均保留，本报告属于独立返修储备。

`python -B analysis.py`只进行离线分析，读取本目录的`vendor/`、`live/`及配置；原D:路径作为来源元数据保留，分析不重新读取该路径下的原研究，也不读取API凭据。准备、测试及原材料保护核验另有原项目路径依赖。本次只在当前Python 3.11与jsonschema环境验证，尚未完成跨机器迁移验证，不宣称整个采集与核验包可直接移机复现。
