# v14 实验设计、统计与经验结论独立评析

审阅对象：`dke-publish` HEAD `bff38c9a`，`revisions/2026-10-24-ase-framing-v14/`；重点正文 §5–7、OR1 S8–S12、OR2 A8/A11–A17。页码来自本版 LaTeX `out/main.aux`，不是凭旧版推测。未改稿件、分发 tables 或冻结实验。未调用模型、未重采集。以下“已复核”与“作者归档声称”明确区分。

## 总判断

本版最强的经验结论很窄，但目前表述基本诚实：在构造的单字段 host、即时确定性 reviewer 和给定提示下，32 次已经送达的身份替换拒绝均得到合法恢复，24 次复用、8 次重新授权。它不是自然错误发生率、实例绑定的生产收益、模型能力排名，也没有证明完成率优势。未发现足以推翻这些窄结论的数字或统计错误。

ASE 审稿主要风险是**经验贡献的深度和现实解释力**，不是“样本其实算错了”：G 的 admission 差异由定义决定；32 个恢复都只需 1 或 2 个接口操作，没有失败/探索；规则控制在扩展实验同样成功。审稿人可能认为这是精心审计过的接口演示，而不是足够丰富的 agent 软件实证。大量 165/72/504/54/16 单元并不能弥补这个问题，因为它们覆盖不同性质的确定性条件，不是自主代理恢复样本。

## 最强结果及应如何使用

1. **恢复路线与当前授权可用性分离，是最有价值的实际观察。** 正文 p.18–20、§6.3，`main.tex:394–425`；OR2 p.17–19 A12，`recovery-extension.tex:11–32,61–66`。派生 CSV 与 figure-data 独立复算得到 32 pairs、16 task definitions、24 reuse / 8 reauthorization；bound 32/32 完成，context 30/32。全部路线达到该接口下的所选路线最少调用数，不能把八次重新授权直接叫“无效调用”。作者的 availability 程序直接检查 13 个状态/输入谓词，不导入 admission engine，也不依赖 legal-path 标签；因此比“日志说可复用”更强。但本次原始大归档不可用，尚未独立重验全部 32 条原始 state/input。

2. **成本分解是可复核的，且正确区分恢复与确认。** 正文 p.19–20，表7、`main.tex:407–425`；OR2 A12 `recovery-extension.tex:73–103`。复算得到：B 16 pairs，恢复 1.000、commit 后 0.375、bound suffix 1.375、context 0.375，均值差 1.000；supp A 15 pairs，对应 1.467/1.533/3.000/1.400、差 1.600；original A 单例差 2。重做 seed 20261023 的 10,000 次 paired bootstrap 得 B [0.75,1.25]、supp A [0.8667,2.3333]，与稿件一致。中位时间差 14.539 / 14.532 / 23.671 秒也一致。

3. **反馈实验的零总调用差没有被包装为有效性优势。** 正文 p.20–21 §6.4，`main.tex:429–433`；OR2 p.19–20 A13，`recovery-extension.tex:108–142,174–229`。复核 saved pairs CSV：12 model pairs 只覆盖4个 task definitions；calls delta 是 -1 三对、0 六对、+1 三对；valid/revoked/unavailable 合计分别 +2/+1/-3，整体0。时间和输出 token 的下降主要集中在无路可走的条件，不足以支持全局效率收益。文中已明确没有证明 feedback equivalence 或 LLM 优势，此处应保持。

4. **SDK 效果层面的证据比单纯 API 返回值更强。** 正文 p.12–14 §5.3、表4，`main.tex:264–284`；OR2 p.23–25 A17，`correction-consumption.tex:12–31,55–95,97–117`。从 v14 `ESM_3.zip` 的三个独立归档提取到临时目录，先验证交付 ZIP SHA-256，再审读 portable verifier，并实际以标准库只读 SQLite 运行：504→444 match /60 mismatch（19,400 checks）；54→42/12（1,942）；16→12/4（674），全部 PASS。没有导入 SDK，没有重运行 native 执行。这支持“保存的实际效果与既有评分一致”，不等于在当前依赖环境重新执行，也不验证 freeze 中机器绝对路径所指 SDK 源码。

## 主要可信度限制与最小修正

1. **G 是强制暴露，context 已由 harness 提前提交，因此成本差不是纯 gate overhead。高风险误读，现稿已充分披露。** p.15–17 §6.1 `main.tex:343–364`，尤其354；OR1 p.16–18 S8 `main.tex:531–563`；A12 `recovery-extension.tex:97–103`。context-side harness commit 不计入 agent calls，bound 被迫多一次恢复 commit；B 的 +1 平均 calls 很大一部分就是该设计的必需工作。因此不能将该数解释为“代理无谓绕行”或 instance checking 的计算成本。最小修正不是补显著性，而是让任何独立出现的成本图/摘要都保留 agent-side/complete-suffix 口径；可在表7脚注追加 context index commit 为 harness 行为且未计入 calls。正文354已有解释，不应批评为未披露。

2. **任务泛化很弱，32 次不等于32个独立问题。** p.17–20 `main.tex:368,394,407`；OR1 S8 `main.tex:527–529`；OR2 A12 `recovery-extension.tex:61–66`。16 G 定义分别出现于A/B；模板参数变化也不是新生产流程。单次 realization 无法估计相同 fixture 上的服务随机性；B温度0也不使服务确定。最小修正：保持每个主要结论同时写“32 delivered pairs /16 definitions”，不要用跨 cohort 的32次做无条件置信区间或模型差异检验。v14目前做到这一点。

3. **A/B 路线差有 provider、时期、prefix 与预算/服务状态混杂。** p.16、20 `main.tex:358–360,407`；OR1 S9/S12 `main.tex:567–575,742–748,826–828`；A12 `recovery-extension.tex:61–66`。A没有 returned immutable model identity；A16次由1 original+15 quota-selected supplementary拼成；B16次原始样本全部复用。没有把“八个discordant pairs”解释成模型效应是正确的。最小修正：继续称 configuration/deployment 描述性差异，不能升级为 GPT vs DeepSeek 能力排名。增加更多异期模型名不能解决该混杂。

4. **selection/censoring 处理比常见稿件透明，但无法变成总体效果。** p.17–18 §6.2 `main.tex:380–390`；OR1 S8 `main.tex:557–563`、S12 `main.tex:742–746`。original A 的117对是quota前零response，不是行为失败；补充只选这117对，选择不依赖U/I是合理的，但仍是后来且选定的collection。planned-ledger completion把可用性和策略完成混在一起；pooled对比是B差值和bootstrap分布的恰好一半，没有新增信息。v14已明确。最小修正：以分cohort结果为主，保留pooled为历史透明性，不用 pooled CI 暗示精度增强。

5. **completion 没有优势证据，context I=0也不是其自定政策下的安全失败。** p.16–18 `main.tex:362,368,388`，p.22 §7.2 `main.tex:466`。I reference选择 instance continuity；G context admission 本来合法。B完成差+1.56个百分点，95%[-3.91,7.03]；输出截断/格式失败又影响完成差。supp A +1.71个百分点 [0,4.27]是探索性，不能被当作已确认正收益。最小修正：任何海报/摘要/图例继续使用“instance-rule conformance”而非笼统“safety”，保持“no established completion advantage”。这不是统计功效不足就自动需要再采集的理由。

6. **availability 与 visibility 的证据只覆盖保存的边界。** p.18–19 `main.tex:403–405`，p.22 `main.tex:466`；A12 `recovery-extension.tex:18–32`；`qa/recovery_availability.py:66–98`。visible = 输入中出现完整对象，不等于可检索性/注意到/理解，也不保证人审批等待后仍有效。十三谓词和实际input哈希是合理的事后重构，但不识别为什么重新授权，也没有执行未选择的reuse反事实。最小修正：描述“presence in actual inputs / valid at saved rejection boundary”，不写“agent knew reuse was legal”或“unnecessary review”。现稿较好。

7. **human approval 与生产 latency 完全未测。** p.16 `main.tex:343,356,358`，p.22 `main.tex:464`；OR1 S8/S9 `main.tex:563,569`。reviewer立即批准所有有效请求，fresh grant supersedes old。重授权计数8是路由行为，不是八次真实审阅成本；14.5秒是suffix wall time，混入模型/传输/确认/终止。最小修正：只能报告 tool interactions 与 elapsed suffix time；若要声称节约审批劳动或部署延迟，必须新增真实/受控审批队列研究。对于当前窄结论，可推迟人类研究。

8. **配对公平性足以隔离本地policy conjunct，无法支持框架能力对比。** p.11–12 §5.2 `main.tex:230–258`；OR2 p.6–8 A8 `main.tex:208–253`。ToolGate手工callbacks、作者SQLite bridge、scripted reasoner/recovery；六个公开reference workflows只比较共同业务要求与最终world，未跑官方benchmark evaluator。两边clone/draft顺序不同，也未声称成本优势。最小修正：继续称implementability case study；不要把23/24 strict PASS的初始化日志差解释成对本方法的性能胜利。现稿的strict FAIL保留与独立business outcome分开是正确处理。

9. **504/54/16是三个不同check，不能累计为574个恢复样本或缺陷率。** p.12–14 `main.tex:268–284`；A17 `correction-consumption.tex:67–95,97–117`。504中的60失败是同一个Agno机制的重复条件；54拆路由与process，但route和object identity一起变；16的history是应用维护的信任边界，不是原生framework漏洞。最小修正：保留分表、versions/routes、known issue与边界措辞；不对生态系统算“x% unsafe”。本次复核无数值问题。

10. **动态pilot很诚实，但其两个task不能填补外推。** p.20–21 `main.tex:433`；OR2 p.22–23 A16 `dynamic-recovery.tex:3–18,25–29,58–84`。8 hosted +8 adaptive rule +8 cached route都为独立controller单元。hosted六个feasible business corrections成功，但冻结get_state-only completion是0/6；不能静默用新终点覆盖旧0。文中保留测量局限是正确的。adaptive rule也6/6说明这是可适应的权限路由fixture，而不是LLM能力优势。

## 真正必须补、可推迟与审稿策略

**当前窄主张下，没有从本次读数中发现必须靠新实验修复的统计硬伤。** 必须完成的是证据可得性与主张一致性：①最终公开版本应能实际下载两份G原始ZIP并以给定SHA校验，才能独立执行 availability/cost 科学核验；本地缺对象不能证明远端链接坏，但我也未验证其公开可得性。②任何面向读者的概括都应保留“构造任务、即时确定性审批、已送达反馈、16 definitions”；③若论文声称 instance binding 的收益，应精确是执行边界维持所声明的instance规则，而不是获证性能、自然安全或人审批节约。

**若目标是更强的ASE经验性贡献，真正需要的是一个能产生新知识的对照，而不是继续扩大确定性矩阵。** 例如同一时期、同一服务配置下，对全新任务/工作流固定availability，随机化reviewed-object呈现或可直接复用的操作接口，并对同一任务做重复采样，观察何时复用/重新授权发生及代价；或至少加入真实多字段/多步骤工作流的自主恢复。现有四任务feedback study已显示单纯添加path labels没有net tool-call收益，不能再把标签假说当已支持结论。这样的扩展是为了改变“演示性”审稿判断；如果维持当前描述性论文定位，可推迟，并接受贡献力度风险。

可推迟：生产审批队列、人类参与者、多组织部署、任意多record/distributed事务、全面framework生态调查，以及扩大到更多模型。前四项只在明确声称对应现实收益/保证时才是必补；增加模型数量本身不会消除任务与时期混杂。

## 本次复核记录

- `empirical-readback/derived-readback.json`：G的派生CSV/figure一致性、各cohort分解、重新bootstrap及feedback strata。
- 三个 `*-verify.json`：由ESM_3内独立SDK归档的portable verifier重读原始SQLite并检查package/freeze/raw artifacts哈希。只写临时目录。
- 两个G固定历史路径执行 `git cat-file -s` 均报告path不存在：`475e66f5:cloud-handoff/replication-package.zip`、`f5fe7231:research/phase2-results-snapshots/2026-10-07-complete/quota-recovery-complete.zip`。没有网络fetch，没有伪称完成原始G重验。
