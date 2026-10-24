# v14 叙事、视觉与发布包装只读评析

审阅基线：`D:/desktop/JSS论文/dke-publish`，HEAD `bff38c9a`。最新稿为 `revisions/2026-10-24-ase-framing-v14/main.tex` / `main.pdf`，29 页；OR1 31 页、OR2 25 页。下文主文行号均指该 `main.tex`。没有修改稿件、重建源 PDF 或提交；截图与提取文字仅写在 `D:/desktop/JSS论文/tmp/v14-review/editorial/`。

## 总体判断

v14 的主线已经成立：**approval scope 决定可接受哪些替换；continuation 是另一个需要观察的行为结果**。C1 模型、C2 跨层验证、C3 恢复行为的顺序，与 RQ1–RQ3、Sections 3–6、Table 1 一致。摘要、引言、相关工作末段、讨论和结论都保持这一主张，不再把 context 合法接纳等同于安全失败，也没有把必然的 admission 差异伪装成模型的经验发现。24 reuse / 8 fresh authorization、32 delivered pairs / 16 task definitions 和 available-and-visible-at-rejection 的边界表达一致。

从编辑与读者角度，这是可读的完整稿，未见版面性阻断问题。真正仍会受到审稿追问的是增量与外推：RQ1 的核心集合包含是定义性的，C2 主要验证条件义务，C3 则是在小型宿主与确定性 reviewer 下观察恢复选择；这些不是靠语言润色就能消除的科学边界。文本现已大体诚实地呈现它们，宜继续保持这一窄而明确的定位。

## 需优先核实的准确性问题

### E1. AI 声明中的 “solely” 范围可能窄于稿件继承工作的真实用途（P1；声明准确性，须作者核实）

- 当前证据：主文 p.25，lines 503–508，尤其 line 504：`Codex was used solely to audit and review experimental procedures and results.`；同文复制于 `audit/DECLARATIONS-v14.txt:24–25`。这不只是没有写全某个工具版本，而是对全部用途作排他限定。
- 可定位的历史相反记录：`revisions/2026-09-26-dke-manuscript/sections/declarations.tex:29–31` 明确列出 OpenAI Codex 等工具参与 code development、analysis/evidence checks、literature organization、manuscript and figure preparation；`sections/07-evaluation-protocol.tex:18,23` 明确写 Codex diagram scripting；`editorial/ai-disclosure-closeout-2026-09-27.md:5–9` 还说明保留真实用途，未将科研辅助改写为仅语法检查。v14 仍使用这些早期实验与参考实现，因此不能仅凭 v11 后来冻结了窄句，就认为当前句已完成事实核验。
- 另一个应分清的角色：主文 p.16，line 358 把 Codex CLI 列为 deployment A 实验接口。实验设备角色与 preparation assistance 不是同一概念，这一处本身不能证明声明失实，却会令未作区分的 `solely` 更容易产生歧义。
- 最小修改：作者按最终稿与保留研究产物逐项核实实际使用；移除未经事实支持的 `solely`，明确区分准备稿件/代码/图件时的辅助用途与实验中作为模型接口的用途，仅保留确实适用的历史用途，并同步正文、声明副本和投稿表单。不要把“旧稿曾如此声明”直接升级为作者不端结论。
- 审阅结论：这是投稿前应解决的准确性事项。现有 hash / verbatim PASS 只能证明声明复制一致，不能证明用途描述完整。

## 审稿科学问题与叙事建议

### E2. C2 含有过多独立证据系列，最有辨识度的 C3 出现偏晚（P2；叙事，科学增量仍需审稿判断）

- 证据：贡献在 p.3（lines 48–52）；Table 1 在 p.4（lines 58–73）。Section 5 pp.11–15（lines 214–335）连续引入 165/72/24/16/504/54/16/10/72 等不同单位。C3 的 32/24/8 路由及额外授权成本到 pp.18–20（lines 392–425）才展开。
- 影响：C1/C2/C3 的排序逻辑正确，但读者容易先把稿件理解成“一组框架检查的总包”，而未立刻看到增量是相同权限条件下的合法路径选择及其成本。C2 本身也容易被误读成完整系统安全保证；现文局限语已避免该过度主张。
- 最小修改：在 Table 1 后或 Section 5 开头增加一条明确的阅读路线：存储/形式检查验证本地关系；ToolGate 验证扩展可实现性；SDK 检查 reviewed-argument consumption；这些均不解释代理为何选择 24/8 路由。将每项 C2 证据直接挂到一个义务/结论，避免再增加一个总称。保留 Section 6.3 的具体已归档 reauthorization 例子；它现在是全文最有用的落地叙事。

### E3. 主文足以理解政策差异，但“契约贡献”的可检查性仍强依赖 A9（P2；可读性与贡献评估）

- 证据：pp.7–9，lines 147,169,185,187 将 typed satisfaction、P1–P6 细目、五信息类与条件正确性指向 OR2 A9；OR2 A9 实际占 pp.9–14。主文给出了候选元组、两政策和义务清单，故不是没有模型，而是关键严密内容分布较远。
- 影响：对把 C1 理解为比较模型的读者已经够用；对期待独立形式结果的读者，主文未完全展示所声称性质的精确边界。对 ASE 的正式研究稿定位，重心应是可执行比较和行为观察，而不能仅以“多层证据”代替增量解释。
- 最小修改：不搬入整套证明；在主文 line 187 旁加一个紧凑的“条件—保证”表或两句说明，标明哪些是定义性包含、哪些由有界检查支持、哪些需要 trusted storage / adapter 假设。现有 A9 细节继续保留。

### E4. 56 页补充材料具有保存价值，但阅读入口还可以进一步围绕论文问题组织（P2；阅读负担）

- 证据：主文 line 511 的补充说明逐项列 S 与 A1–A17；OR1 `supplements/online-resource-1/main.tex:27–31` 已有 Reading guide；OR2 `supplements/online-resource-2/main.tex:22` 是较长的一段范围目录。OR1 pp.29–30 的 S12.6 明确保留 reuse 和 reauthorization 两个例子，OR2 pp.23–25 的 A17 保留 SDK 明细与 artifact sources。
- 影响：29 页主文加 56 页补充并非自动缺陷；目前主文也保留了关键 32/24/8 结果。但读者要跨两份补充追踪多批次、单位、版本和冻结记录，仍然昂贵。
- 最小修改：在 OR2 首页或主文 Table 1 增加一张只需一行一个 RQ 的“必读定位”：RQ1 → A9 与 A11；RQ2 → S2–S3/A14/A17；RQ3 → S12.6/A12/A13。区分核查核心结论所必需的章节与保存历史的章节。不要把所有历史证据都称为支持同一端到端结论。

### E5. 术语总体一致，尚有可压缩的别名成本（P3；编辑小修）

- 证据：主文使用 `instance binding`；政策符号为 `P_bound`（lines 162–164）；实现称 `exact journal`（lines 220–222）；表 6 注释解释 Inst archived as bound（line 371），表 7 又使用 Bound suffix（line 415）；图4正文交替用 bound/instance。`I` 已在 line 362 定义为 instance-reference conformance，图注和表注多次澄清它并非 context-policy safety。
- 判断：没有发现实质概念矛盾，但 instance / bound / exact 三个别名和 context / Ctx / C 增加初读负担。P1–P6 的分组也与历史 Alloy 命名存在映射，文本已有解释。
- 最小修改：在第一次 implementation 名称处加一条 `instance-bound (archived as exact/bound)`；后续叙事及表 7 展示名统一为 Instance。归档字段、文件名和原始数据不必改动。

### E6. Human review 研究动机与自动 reviewer 实验目前分得清，应保持此界线（非缺陷；勿再扩张）

- 证据：摘要明确 reduced host + deterministic reviewer；lines 343,356,407,425,464,468 与结论 line 480 均说明授权立即且确定、未测人类审查负担/排队延迟，未建立完成率优势；cover letter 第4–5段也保持这一限制。
- 判断：标题和开头 human approval 可作为应用问题；现稿没有把代理对确定性授权接口的行为冒充 human-in-the-loop 用户实验。下一轮切勿把额外 authorization request 直接换算为人类工作量、认知成本或生产收益。

## 视觉审阅

使用 PDF 技能，以 Poppler 渲染已有 PDF。检查主文 p.1–6、10、12–14、16、18–22、24–25；重点全尺寸查看 4 图所在 p.2/10/16/19，并看相关工作表 p.5、结果密表 p.18/20、声明 p.24/25。另检查 OR1 pp.29–31 与 OR2 pp.23–25。

- 首页：标题、作者、摘要和关键词完整；排布符合当前 Springer 样式，没有异常空白、截断或重叠。
- Figure 1（p.2）：90→101 的两种 approval history 差异清楚，c1/c2、grant 与 no-commit 可读，放在引言第一实例下方合理。
- Figure 2（p.10）：集合包含和 recovery branch 分开，图注列出 immutable records / shared checks / R includes K 条件；没有把 reauthorization 画成更强绑定级别。
- Figure 3（p.16）：Harness exposure / Measured continuation 的两部分明确，能防止把人为提交的替换误称为 agent substitution behavior。
- Figure 4（p.19）：32/32、24/8 总结明显；task 列对齐、空缺与 failure 分开；差值方向与图注一致，范围线明确不是 CI。
- Tables 4–7 和 supplement 后部表格：未发现裁切、覆盖、漏行或坏字符。
- 视觉小修（P3）：Table 2（p.5，main.tex line 81 开始）7.6 pt 五列较密，作者/引文在首列换行频繁；宜优先缩短 Source 引文展示或将版本证据移到表注，给机制与边界更多空间，而不是继续缩小字。图注长度尚可，但 Figure 1 的末句 `disclosed below` 可改为明确的 declaration pointer，避免“below”距离二十多页。

未发现需要重画四幅图或因 AI glyph 本身而拒稿的依据。声明已说明作者定义对象/标签/连接、代码组装和源资产，是否满足期刊政策应按现行官方政策与实际使用核实。

## 冻结与发布包装问题（与科学有效性分开）

### E7. 根 README 仍把 v13/28 页称为 current，容易引导审稿人拿错稿（P2；发布入口）

- 证据：根 `README.md:3–18` 仍为 layout v13、28 pages，所有入口固定到 v13。v14 的 `README.txt`、submission README 与 main.pdf 均为 29 页、OR1 31 页、OR2 25 页。
- v13 实验入口并非无意错误：主文 p.24 line 483 固定 v13，`V14-CHANGELOG.md:270–273` 明确解释七个实验档案未变。保留 v13 科研冻结引用可以成立，但当前根 README 混淆“最新稿”和“旧实验冻结”。
- 最小修改：根 README 把 Current manuscript 指向 v14；另保留独立一句说明实验档案仍依赖已发布 v13。正文 availability 加一句 `The v14 manuscript/source revision and the unchanged experimental freeze have separate release identifiers.`，并给 v14 源稿的固定入口（在确有可访问冻结后）。无需重跑实验。

### E8. Changelog 同时声称 v14 已推送和仅本地，需收口发布状态（P2；归档事实）

- 证据：`V14-CHANGELOG.md:268–273` 称 committed/tagged/pushed to origin；同文件 `:296–297` 又说 commit/tag exist only locally、pushing is author decision。
- 最小修改：按实际远端状态更新 Remaining open items，或将旧状态标为已解决；不要仅追加新句留下两条当前时态的断言。审阅没有访问远端，因此不依据本地是否有 tag 推断远端真实状态。
- 当前没有 hash 损坏：独立逐项复算 `FINAL-FREEZE-v14.json` 的 125 条记录，缺失 0、SHA-256 不匹配 0；其中包括当前 changelog。其 pages 字段与三份 PDF 一致。这是状态说明冲突，不是冻结内容已被篡改。
- Changelog 前半保留的 C2/C3 旧顺序、28 页与旧 float 位置已在 Final polish 明确被后续 pass 替代；若作为逐次记录可保留，不必当作当前稿件矛盾。

### E9. 投稿目录的 cover letter 与“public deposit 不含 correspondence”说明不一致（P2；投稿包装）

- 证据：`submission/ASE-2026-10-24-v14/README.md:5–15` 表只列 5 科学 payload，`FILES.json` 也仅列5项，并称 author correspondence 不属于 public research deposit；实际 `ready-to-upload/` 有6文件，第6个 `Cover-letter.pdf` 被 Git 跟踪。该 cover letter 第一段包含此前 ASE submission ID，并表述在此前稿件撤回后作为新稿提交。
- 判断：5 个科研 payload 的记录是自洽的，Cover letter 作为第6个投稿角色也合理；问题是目录说明没呈现实际边界。“not part public deposit” 与当前 tracked path 不一致。它不影响实验或主文结论，但可能使作者错误认为通信没有公开归档。
- 最小修改：明确 cover letter 的 correspondence 上传角色与清单范围；按作者已授权的发布边界安置该文件，或至少让 README 如实说明研究 payload 清单不含 correspondence。不要在未确认前将 cover letter 的“已撤回”措辞当作实际撤稿完成的证据；changelog :294–295 仍明确要求先取得 withdrawal confirmation。

## 优先级与改动边界

先核实并修正 E1 的实际 AI 用途；再修 E7–E9 的发布入口、状态和通信范围。E2–E5 属进一步提升读者理解与贡献辨识的修改，不需要改实验或夸大外推。版面已经合格，优先保持当前四图与结果数据，避免为了视觉“升级”引入新解释风险。

来源 PDF：`D:/desktop/JSS论文/dke-publish/revisions/2026-10-24-ase-framing-v14/main.pdf`、`Online-Resource-1.pdf`、`Online-Resource-2.pdf`；投稿信为 `D:/desktop/JSS论文/dke-publish/submission/ASE-2026-10-24-v14/ready-to-upload/Cover-letter.pdf`。具体源行定位如上。
