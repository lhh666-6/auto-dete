# Phase 2 正式实验：共同作者接手入口

本包准备 128 tasks × 2 Agent configs × 2 policies = **512 条正式轨迹**，256 pairs，repetition=1。分布 L32/N32/G16/E16/V16/R16。当前没有启动正式模型采集。邻接 pilot 的 16 条在线 arms 和本包 deterministic preflight 均不进入正式效果分析。

先读 `frozen-formal/readiness.json`；只有 `FORMAL_FREEZE_READY=YES`、全部哈希核对通过且作者明确要求采集，才能执行启动命令。`master-sha256.txt` 是整个冻结包的 SHA256。`reviews/final-review.md` 保存独立复核；`WORK-PLAN.md` 和初审报告保留升级过程。

## 接手顺序

1. `frozen-formal/Phase2-protocol-FINAL.md`：科学问题、唯一 policy 差异、六种场景和 E 当前证据语义。
2. `frozen-formal/analysis-plan.md`、`scorer-definition.md`、`failure-handling.md`：分母、未知、恢复机械分类与中断处理。
3. `formal-task-manifest.json`、`assignment-manifest.json`、`agent-config-manifest.json`、`prompt-manifest.json` 和两份 schema。
4. `preflight/deterministic-final-128/`：完整 128 fixtures 的结果及压缩原始轨迹；这些是无模型工程测试。
5. `src/phase2/`、`run_formal.py`、`analyze_formal.py`：运行及分析源码，版本/哈希在冻结目录。

## 安装和离线核验

从仓库根目录运行，Python 3.11（冻结时 3.11.9）：

```powershell
python -m pip install -r research/agent-policy-phase2-formal-2026-10-07/requirements.txt
$env:PYTHONPATH = 'research/agent-policy-phase2-formal-2026-10-07/src'
python -m unittest discover -s research/agent-policy-phase2-formal-2026-10-07/tests -v
python research/agent-policy-phase2-formal-2026-10-07/run_formal.py --verify-only
```

也可在本包目录运行这些入口脚本。`.gitattributes` 保留字节，避免 Windows 换行转换破坏冻结哈希。不要修改源代码/冻结件来适配运行环境后仍沿用原 freeze ID。

## 两个部署和凭据

A：与 pilot 相同的 account-backed Codex CLI 路线，请安装冻结清单中的 CLI 版本并用自己的账户登录；requested alias 固定 `gpt-5.6-terra`、reasoning low。CLI 未提供实际 returned model/revision，不能宣称可观测 immutable snapshot。冻结环境已有代理 `http://127.0.0.1:7897`。若本机部署、CLI/代理设置不同，先做仅可用性/身份核验并建立单独、记录差异的新执行 freeze；不要改旧 freeze 或按结果换模型。

B：requested alias 固定 `deepseek-v4-flash`，当前 probe 的 returned identifier 记录在清单，endpoint 为清单中的 DSH-compatible endpoint。temperature=0；top_p/seed 未显式传入，不虚构服务默认值或不可观测版本。4096 上游 output cap 只适用于 B，A 未支持；两者同样有请求、工具、模型响应和时间上限。货币费用未知。

密钥不在仓库。原 Windows 用户加密文件路径仅作为本机运行配置记录，不可给其他人解密。共同作者用自己的凭据，通过本机环境变量 `PHASE2_DSH_API_KEY` 提供，切勿写入源码、JSON、Git或聊天。账户额度/CLI部署可用性由共同作者在采集前确认。同模型别名也不能保证跨时间 immutable identity；可观测变化会暂停运行。

## 作者批准后的正式启动

```powershell
python research/agent-policy-phase2-formal-2026-10-07/run_formal.py --author-start RUN_512_FORMAL_ARMS
```

固定两条 provider 通道，每条一次执行一个完整 pair；pair 内 policy 顺序已经冻结且相邻执行。不得临时增加线程数。`formal-results/collection-status.json` 保存已完成/失败/运行状态；输出目录默认不进 Git，采集完成后单独提交不可变结果包。

中断后用同一 freeze、同一 output 恢复：

```powershell
python research/agent-policy-phase2-formal-2026-10-07/run_formal.py --author-start RUN_512_FORMAL_ARMS --resume
```

恢复跳过所有终态 pair，包括失败 pair；沿用原会话、已用预算及 elapsed time。网络延迟/中断只在有限预算内重试；语义动作中断或缺失恢复边界会保留为不确定/失败，不重复执行、不撤回已持久化授权或提交。Observable deployment drift 暂停两通道。读 `failure-handling.md` 后检查暂停原因；需要改变科学输入时保留原批次并 version bump/re-freeze。

## 完成后的机械分析

```powershell
python research/agent-policy-phase2-formal-2026-10-07/analyze_formal.py --output research/agent-policy-phase2-formal-2026-10-07/analysis-results-v1 --figures
```

输出四表、配对效应、全部失败轨迹分类、唯一 shared-prefix 资源账本和两张矢量/300dpi 图。未完成正式采集会拒绝绘制正式图，且分析 summary 明确禁止最终推断。不要把 512 arms 当作 IID：整体 bootstrap 以 128 tasks 为 cluster，保留两个 config 和两臂；McNemar 每 config 分开。G 为 harness recovery probe；N 保留 Agent 自主性。不能把 context 的 A_instance 不兼容成功改写为 I=1，也不能用不显著声称无 utility loss。
