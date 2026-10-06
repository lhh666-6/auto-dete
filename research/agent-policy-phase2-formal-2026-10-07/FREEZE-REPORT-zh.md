# 正式实验冻结结果（2026-10-07）

FORMAL_FREEZE_READY = YES。Unresolved blockers：[]。

- 128 tasks：L32 + N32 + G16 + E16 + V16 + R16；256 pairs；512 formal arms；repetition=1。
- 8类业务模板，17个参数维度，128个唯一参数向量。真实变化进入 evidence bytes/locator、metadata、候选envelope、版本和历史、reference_note/source及显式field order；有限参数空间，存在预定相关性，不宣称全因子或自然随机样本。
- A requested gpt-5.6-terra / account-backed Codex CLI / reasoning low；availability已确认；returned model/revision不可观测，如实为null。B requested及当前returned identifier为deepseek-v4-flash / 冻结DSH-compatible endpoint / temperature 0；immutable snapshot/revision不可观测。版本和原始probe记录在 agent-config-manifest及preflight。
- 最新57项runner/scorer/provider/来源/恢复/统计/账本回归测试PASS。
- 全128case确定性预检PASS：128 host pairs、256工程arms、0 online model calls、0 formal online arms；E/V/R含真实共享checkpoint→两臂→拒绝/不可用反馈→脚本化后续决策→独立审计。不是模型结果。
- 两个provider lane并发、pair内两臂相邻，预定平衡order；原会话/预算safe-boundary恢复、90秒请求、有限2次重连、一次通用格式反馈；语义不确定动作不重复执行。细节与限制见failure-handling。
- 四张结果表、配对效应、完整失败分类、唯一prefix资源账本及后续两图的代码已冻结。
- 核心科学问题、两种policy及唯一I_eq差异未变。正式细化包括E发布后current-evidence共同边界、V外部note正确utility目标、R能力不可读/receipt内部存在区分及任务参数化；均显式记录，没有按pilot效果选模型/场景或强迫N错误。
- Pilot完全排除正式分析；本轮正式轨迹尚未启动，由共同作者在作者指令后执行。

Freeze ID：phase2-formal-v1.0-9fd97d11ceaed652。
UTC timestamp：2026-10-06T18:55:47.225978+00:00。
Master SHA256：7773563b40c8db30d6def121915f50fbad032537edde32afd4ba39ec3eea744b。

冻结件全部在frozen-formal/：FINAL protocol、task/assignment/agent/prompt manifests、tool/event schemas、analysis/scorer/failure规则、fixture/environment/source/input-hash manifests、diversity、readiness及master。master覆盖逐文件源代码/测试/探针/确定性原始ZIP和文档；CONSISTENCY-AUDIT.json是封存后的独立一致性核验。接手入口为README.md。
