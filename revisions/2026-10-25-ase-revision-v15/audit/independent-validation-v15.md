# v15 independent validation

审查日期：2026-10-25。独立审查对象为 v15 派生 observation checker、离线回归与相对 v14 的稿件修订。未修改 checker、文稿、实验数据、正式 JSON receipt 或 v14；验证输出只写入 `tmp/v15-independent/`。本报告是独立有限复核，不是整篇论文形式化正确性证明。

## 结论

已亲自验证 F1 的两个具体反例得到适当修复，F2 的 scope 歧义得到澄清。当前未发现新增阻断问题。派生 checker 的修复、T1b 等价约定和 S2 的有限证据声明相符，没有把无效 history 的局部 outcome 错称为修复后的 inadmissible。

## 亲自执行与源码核查

- 读 v14 `formal-review.md` 后独立逐函数检查 v15：`D_V` 公开 proposal/authorization/successor 的 canonical JSON 字符串，`D_F` 公开 canonical predecessor discriminators；归因、changed fields、local source consistency、freshness、commit connection 和 endpoint 均用同一 `_canonical_equal`。opaque string identifiers 仍按 identifier equality。此处沿用 sorted-key、whitespace-minimal JSON serialization；并非 RFC 8785 或一般 JSON 输入验证器，稿件也没有如此声称。
- 直接执行 `python revisions/2026-10-25-ase-revision-v15/qa/test_observation_equality_v15.py --output tmp/v15-independent/equality.json`：38 项新回归及 frozen/v15 原有构造均 PASS。上游 blob 的 SHA-256 在执行前按代码内固定值检查。
- 把 checker、test harness 和 bundled upstream 三个文件复制至 `tmp/v15-independent/standalone/`，从该目录之外调用 test harness 并显式指定输出：exit 0，38 项 PASS。该运行的源路径不依赖 Git 或原始实验 checkout，仅标准库 Python；这不是发布 ZIP 本身的解压验证。
- 另行直接构造反例一：integer-1 合法 history 与只把 authorization 改为 Boolean true 的 history 均 domain-valid；修后 full projections 不同，local outcomes 分别 admissible/inadmissible。故原来“同投影、异 outcome”的冲突消除。
- 另行直接构造反例二：真实 commit after 为 integer 1，声明 successor、authorization、source 为 Boolean true；修后 domain 返回 `commit sequence does not reach successor values`，但局部 `normative_outcome` 仍返回 admissible。这是正确边界：该函数未包含 domain 检查，T1b 的前提是 well-formed histories，不能把域外标签解释为 gate 的有效 admission。
- 额外生成 8,192 个含 null/bool/int/float/string/list/dict、两种 attribution role 和四种 discriminator 的 domain-valid histories，逐一调用 public projection/outcome，未报运行错误。所有 full projections 在该生成器下互异，因此这项抽样不构成对等价投影定理的实证检验，也不作为加强 T1b 的证据。

## 测试可靠性与范围

38 项不是仅断言 `_canonical_equal` 的同义镜像：36 项采用显式预期 equal/unequal，分别触达三个公开投影角色、归因、changed fields、source resolution、endpoint、connection 和 freshness，另两项在 byte-exact frozen source 上重现历史反例，并比较派生版。这能发现只修 helper 而漏掉 projection、domain 或 freshness 消费点的回归。dictionary-order 控制防止修复把键顺序误当差异。保留五个 omission pairs、额外 identity pair 和 copy-forward control，避免修复以破坏旧构造为代价。

其覆盖仍有限：不是任意 Python Any 的验证、所有 malformed records 的 admission oracle、完整 provenance/P6 检查或一般定理穷举。`default=str`、非 JSON 值、运行时 identifier 类型不受新验证保证。现行 scope/equality_scope 与正文明确限制到所声明 JSON payload 和 opaque string handles，因此这些是边界而非本轮新增缺陷。

## 稿件和冻结证据

- 逐段审阅 `main.tex` 相对 v14 的差异，以及 OR1 S2.6/S2.8 与 OR2 A9 T1 的文本差异。仍区分定义性 admission、接口决定的 route minima、实际 route/confirmation 选择，未提升为一般恢复最优性或完整安全证明。
- F2 改为 matching grant “under instance binding”，与 context policy 可复用旧 grant 的定义一致。
- T1b 明确 JSON 值与 snapshot equality、D_F/freshness 的同一约定；S2 公开旧 checker 缺陷、独立派生路径和 38 项有限回归。未更改旧 Alloy 72 commands、早期 13 tests 或历史实验总数。
- AI-assisted preparation 已移除 Codex “solely audit” 的不准确限制，包含 manuscript revision、verification-code preparation 和 GPT-6.1 Sol 多角度审查；符合本次实际工作。未声称作者已完成本轮之外的人工复验。
- 亲自按 SHA-256 比较 v14/v15 根目录 `tables/` 的 16 个文件及 `figures/` 的 4 个文件；进一步递归比较含 supplements 在内所有 `tables`/`figures` 子目录的 35 个文件：路径集合与内容全部相同；`references.bib` 字节相同。没有重新采集模型轨迹、重新统计实验表或重跑 hosted experiments。
- 新增 RefineAct 198/292、三次内 approved-action 陈述已亲自核对[作者官方 PDF](https://lab-design.github.io/papers/ASE-26/ase26.pdf) §6.3/Table 5 邻接的 Retry Effectiveness 段（PDF 第 9 页并续至第 10 页）。其 unit 是 revision event；稿件明确与 delivered identity mismatch 区别，未跨论文比较成功率。

## 未覆盖与后续视觉检查

未重跑 Alloy、生产 gate、agent studies、完整安全审计或所有引用论文；没有验证尚未发布的 remote v15 release。

使用已有 Poppler 将本轮编译结果渲染为 PNG 并亲自逐页查看：main p2/3/6/7/8/9/10/16/21/22/24/25、OR1 p8/9、OR2 p10。覆盖本轮引言、related work、F2、S2 repair 入口、discussion、availability、AI 声明、equality disclosure 和 T1b 的主要变化。所看页面的字体、公式、图文、页边界无裁切或重叠；不是全部 87 页的逐页视觉认证。初次发现 OR1 p8 的 `\\code{--output PATH}` 在 nolinkurl 中吞掉空格，显示为 `--outputPATH`；通知后集成 agent 已改为 `\\texttt{-{}-output PATH}`。已重新渲染并亲自检查 12:34:11 版 OR1 p8，flag 与 placeholder 间空格清楚、布局正常，此项已关闭。无未关闭的本轮审查问题。

最终回看：按集成 agent 通知再次渲染 OR1 p8/32、OR2 p10/26；OR2 p10 压缩后的 T1b 仍保留 observation/history-domain canonical serialization、D_F/F 一致、opaque identifier、factorization 和有限回归边界，没有改变论证范围。两份补充末页留白属于正常结束分页，没有截断或强行压版问题。本审查不声称编译日志所有 underfull 为零；以所列页面视觉结果判断可读性。

最终审查所对应 PDF SHA-256（页数 main 29、OR1 32、OR2 26）：

| 文件 | SHA-256 |
| --- | --- |
| `main.pdf` | `dfef2044d7d60fdc74ce641877549233a26d482a87a848b33afc1130c700621d` |
| `Online-Resource-1.pdf` | `755cfadd5b1d350162b7a41b43224d05c40fc4a6e9afc7bf5de2c3a438111bd3` |
| `Online-Resource-2.pdf` | `b3c2cf2cfc0a7ac9fad06cfebccc0df100ca0989d8a44355146ced29492fd2e5` |
