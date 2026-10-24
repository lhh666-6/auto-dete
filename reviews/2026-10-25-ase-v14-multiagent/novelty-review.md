# v14 创新性、最近工作与 ASE 期刊定位审查

审查对象：`D:/desktop/JSS论文/dke-publish/revisions/2026-10-24-ase-framing-v14/main.tex` 与同目录 29 页 `main.pdf`；仓库 HEAD `bff38c9a4c3c83ce30d26b18c7d64da816451d5b`。先独立阅读主稿与相关补充，再查看 v14 changelog 和历史 reference audit。只读，不修改论文，不提交、不推送。页码为 PDF 实际页码。

## 整体判断

v14 的论证是成立而克制的，但其创新应理解为**以共同持久化义务为控制条件的审批范围比较，以及具有状态/输入证据的恢复路线研究**。不能把实例绑定、提交时授权、受阻后的继续执行或六项义务本身当作全新方法。这不是我发现作者存在这些夸大：v14 已明确将准入集合包含关系称为定义结果，承认沿用既有基础，也明确不把 context 合法替换判为该策略下的安全失败。

最有价值且尚不直接由定义推出的观察是：在 32 次已送达的实例不匹配中，原候选和有效旧授权在保存状态中可用、在实际模型输入中可见；代理仍分为 24 次直接复用与 8 次重新请求授权。这个联合证据比“32/32 恢复”或“实例策略多一次调用”更值得作为论文主线。它证明了这些轨迹中的路线选择，尚不证明多余授权的原因、最优性、生产环境负担，或任何一般的模型优劣。

从 Automated Software Engineering **期刊**定位看，属于可辩护的范围：论文把 agent framework 的审批适配、运行时验证、持久化约束和恢复协议作为待构建/分析的软件系统。ASE 官方范围包括协作系统、软件过程建模、开发支持工具与验证，并不要求每篇稿件都完成代码生成任务。但本稿的主要行为结果来自简化单字段业务主机，真实 SE 价值需通过开发者面对的审批适配问题来讲清，不能只靠标题中的 “software”。期刊相关性不是致命缺陷；创新增量与实践解释的锋利度才是主要风险。

## 主要优点

1. **研究对象区分得准确。** §3.3（p.8；main.tex:175–187）把定义决定的 admission difference 与行为实验分开；§6.1（p.16–17；354、362）明说 G 是 harness 提交的暴露，且 instance oracle 不是 context 策略安全 oracle，避免以人为选定判据制造“优越性”。
2. **旧授权可用性与模型可见性都有证据。** §6.3（pp.18–20；403–407）不只依赖 host 的 legal-path 日志，而读保存状态与真实输入；还给出一次 fresh authorization 的完整事件链。这是重要的机制解释和可审计性增量。
3. **把调用成本拆开而不是将所有后缀调用归因于重授权。** Table 7、§6.3（pp.19–20；407–425）分开恢复提交、授权请求、提交后确认和 context 侧调用，同时声明 deterministic grant 不能估计人的时间。
4. **最近工作总体比较公平。** §2.1（pp.4–6；115–123）对 ReSA 的 consumed-object/preservation 与 Guarded Commits 的 derived-record reuse 描述与原文相符；ToolGate 被称为 configured implementability study，SDK 结论也限定版本与入口，没有以接入演示冒充原生能力缺陷。
5. **证据各有分工。** 关系库/日志、bounded formal checks、ToolGate 扩展、原生 SDK 与行为轨迹有明确边界。尤其 §5.3 的真实 SDK continuation-route 对照，是能让 SE 读者感到问题具体存在的材料。

## 最关键问题（按重要性）

### 1. 相对最近工作的“尚未解决的知识问题”仍不够凝练

- **位置：** Introduction C1–C3（p.3；main.tex:42、51–53），§2.1 closest comparison（pp.4–6；115–123），§7.1（p.21；445–460）；OR2 A15 `obligation-positioning.tex` 全表。
- **证据：** OR2 A15 已把 P1–P6 分别映射到现有的绑定、保留/原子验证、EDIT、OCC、事务与 provenance 基础。ReSA §2.1/§3.1 已按 exact/scoped grants 分析 consumed versions；Guarded Commits §3/§3.1 已提供 artifact/EDIT triple、validated decision reuse 与 renewed review。因此，contract 的价值主要是组织比较条件与测量，而非新执行机制。主文说“其复用新派生记录，本文一路径复用旧候选旧 grant”准确，却容易让评审认为这只是记录设计差异，尚未说明它为什么改变需研究的开发者决策。
- **合理反驳：** 集成既有义务以隔离一个变量、再测量剩余行为，是有效的经验 SE 贡献；不要求每个 conjunct 都新。v14 也没声称世界首个审批执行机制。
- **最小修正：** 用一段明确的“已知—未知—本文结果”取代相邻的两次概括：已知如何绑定/验证授权；未知在相同有效权限仍存在时代理选择哪个合法继续路线及其可观测成本；本文以状态与输入审计把“不得不重授权”与“选择重授权”分开。强调旧/新记录差异是测量单位的解释，不是单独的技术优越性。C1、C2 保持为对照基础，C3 给出知识增量。
- **必须新增实验？** 否。已有状态/输入/事件资料足以支持这一定义得当的增量。若坚持比现有系统更少人审、更安全或更高效，则需要相应比较，但这不是当前合理主张的必需条件。

### 2. RefineAct 已有恢复行为实证，当前两句话不足以防止读者误读恢复贡献

- **位置：** §2.1（p.6；main.tex:119、123）；Introduction C3（p.3；53）；§6.3（pp.18–20）。
- **证据：** 已核验作者实验室 camera-ready PDF。RefineAct §4.4（原文 p.7）有 per-invocation scoped confirmation 和 feedback retry；§6.3/Table 5（原文 pp.9–10）对 292 次 Revision Required 事件报告 198 次三次以内修正成功（68%），并分析补前置动作后重试原动作的常见模式。因此“运行时拒绝后代理能继续/恢复，并测量其行为”已不是空白。v14 的两句描述没有错误，但只提 confirmation/corrective feedback，没有说明已有恢复测量。
- **合理反驳：** RefineAct 的对象是任务意图与前置条件，不是经过持久化检查的旧候选/旧 grant 是否仍有效；它的 68% 也不是本稿 identity-only mismatch 的同一单位，不能拿两个百分比比较性能。其结果没有直接消除本稿研究问题。
- **最小修正：** 补两三句承认 RefineAct 已分析 feedback-driven retries，并明确本文细化的是“审批范围决定的 admissibility、已可用旧授权、复用/重新授权的路线与后续确认分解”。不必扩充成庞大综述，也不必把 RefineAct 强行作为不相容的实验基线。
- **必须新增实验？** 否。准确补充范围与测量单位的比较即可。不能把“引用了”直接等同“已充分论证差异”，但也不能据此判为缺失全部最近工作。

### 3. 核心行为发现有事实增量，但任务结构让“成本”与“成功率”很容易显得机械

- **位置：** §6.1（pp.15–17；main.tex:343–356），§6.3（pp.18–20；394–425），§6.4（p.20；429–433），Threats（pp.22–23；464–468）。
- **证据：** context 侧在 feedback 进入代理前已由 harness 完成提交；instance 侧必须补一个 commit。全部 24 reuse 路线都是一个 commit，8 reauthorization 路线都是 authorize+commit，中间没有失败/探索调用。reviewer 对合法请求立即批准。故“instance suffix 较贵”有重要的设计内生部分，“32/32恢复”也发生在一个极清晰的两步可行路径中。真正未被程序预定的是 24/8 选择，以及提交后查询；这既是贡献强点，也是经验广度的边界。
- **合理反驳：** 作者已在354、407、425明确说明成本边界，且没有声称 LLM 优于规则。构造性对照不因路径简单而无效；它能隔离身份条件，适合先建立测量方法。
- **最小修正：** Discussion 更直接写出三层：准入结果为定义结果；最短合法恢复调用数由接口给定；观测增量是选路与随后确认。把“available and visible reuse 下的8次fresh authorization”置于贡献中心，同时不称其为 unnecessary 或 suboptimal（无反事实效用/人审成本证据）。可直接借用现有 Table7 和 pilot 的规则控制来说明实验没有建立 LLM 必要性。
- **必须新增实验？** 否，只要保持狭义、描述性研究定位。若期刊要求强实践效应而作者决定主张减少人审/复杂故障恢复，则需新的真实延迟或更复杂自主场景；那属于提升主张，不是现有结论成立的前提。

### 4. ASE 相关性存在，但需要让读者看见“开发者据此怎样构建/验证系统”

- **位置：** Introduction 第一例（p.2；main.tex:29–42），§5.2 ToolGate（pp.11–12；230–258），§5.3 SDK（pp.12–14；268–272），§6.1 reduced host（p.16；356），§7.1（p.21；451–460）。
- **证据：** 最近且最具 SE 识别度的真实材料是 SDK reviewed-argument 传递、Agno 不同 continuation route 与 Pydantic 历史 trust boundary；主行为实验则是单字段更新，tau2 Retail 又是脚本决策和自写 commit bridge。大量实验条件不能自动转化成一项广泛的软件开发工作流评估。
- **合理反驳：** ASE 官方 scope 明确覆盖协作系统、软件对象/过程模型、验证、集成与支持开发的工具；本稿是在工程化 agent 软件，业务任务可作为测试载荷。不能以“没有 SWE-bench/真实代码库实验”一票否决相关性。
- **最小修正：** 在问题定义或讨论中用一个已有证据支持的端到端开发者 vignette，把“UI/SDK pending request、immutable application candidate、durable grant、executed argument、persisted receipt”对应清楚；指明原生 SDK 只保证哪层、应用 bridge 还承担哪层。可复用 A14/A17 资料，不另造未经验证的代码审查成效。Cover letter 应将主题写为审批适配与恢复协议的验证/测量，不写成改善代码任务成功率。
- **必须新增实验？** 否。现实 coding-agent case study 会增强实践分量，但不能作为当前范围内逻辑成立的强制条件。

## 已证实、可解释与不能推出的内容

- **已证实于所测条件：** scope 定义的集合关系；具体实现/fixture 的符合性；32 次已送达 G mismatch 的路线与状态/输入可用性；SDK 所测版本/入口的具体行为。
- **有证据但只宜描述：** 相同可用恢复机会下有不同路线、不同后续查询成本；后续动态权限 pilot 中依据当前状态调整能完成可行路径。
- **不能推出：** identity-only substitution 自然发生的频率；context策略整体不安全；instance策略有任务完成优势；8次重授权一定浪费；真实人审时间；模型A/B差异是模型因果效应；本方法优于 ReSA/Guarded/RefineAct；LLM 恢复优于规则。

## 审稿倾向

我倾向于**大修后重新判断**：不是因为发现实证矛盾或理论反例，而是核心知识增量仍可能被看成“已知授权义务的组合 + 简单路径中的有限行为观察”。若严格按 v14 的克制主张审，工作有可信的方法与可复核的证据，不应轻率判成纯粹同义反复。是否达到 ASE 期刊的显著性门槛，主要取决于编辑/评审是否认可“审批范围与授权仍可用时的选路测量”这一狭而清楚的经验贡献。优先做上面的差异化与论证聚焦，不能承诺只靠措辞就必然解决显著性。

## 已核验的原始来源

- ReSA v1，§2.1、§2.2、§3.1：[arXiv full text](https://arxiv.org/html/2609.26529v1)。特别注意其 exact 是 normalized security meaning 的 singleton，并非无条件要求持久候选实例 ID 相等；in-scope 或语义不变替换不算 APAS。
- Guarded Commits v1，§3、§3.1：[arXiv full text](https://arxiv.org/html/2610.00037v1)。其 EDIT triple、derived-record reuse 和 renewed review 已存在。
- AgentSpec camera-ready 对应公开全文，§3–4：[arXiv full text](https://arxiv.org/html/2503.18666)。包含 user_inspection、llm_self_examine、invoke_action 与执行循环 hook。
- RefineAct camera-ready，§4.4、§6.3/Table5：[作者实验室PDF](https://lab-design.github.io/papers/ASE-26/ase26.pdf)，[论文官方作者页](https://lab-design.github.io/papers/ASE-26/)。有 scoped per-invocation consent、retry loop 与198/292修正观察。
- ASE 期刊范围：[Springer aims and scope](https://link.springer.com/journal/10515/aims-and-scope)。期刊与同名会议不可混作同一录用标准。

历史 audit 备注：v14 中 `audit/REFERENCE-STATUS-2026-10-24.md` 的内容仍明确写 v10 scope，并列出后续已移除的工作。它只能作历史记录，不能当 v14 全部参考文献状态的独立新核查；本报告的关键文献判断来自上述原始来源。
