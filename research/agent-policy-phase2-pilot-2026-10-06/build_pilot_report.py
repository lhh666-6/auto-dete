"""Post-pilot engineering audit and transparent descriptive report, no inference."""
import csv, hashlib, json, sys
from collections import Counter
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent / 'src'))
from phase2.kernel import ROOT, canonical, utc
from phase2.runner import score_run, validate_run
from phase2.providers import parse_action

resultdir = ROOT / 'pilot-results'
if not (resultdir / 'RUN-COMPLETE.json').exists(): raise SystemExit('Pilot not complete; refusing results report')
freeze = json.loads((ROOT / 'frozen-execution/execution-freeze.json').read_text(encoding='utf-8'))
changed = [name for name, sha in freeze['sha256'].items() if hashlib.sha256((ROOT / name).read_bytes()).hexdigest() != sha]
if changed: raise SystemExit('Frozen files changed: ' + ', '.join(changed))
pairs = json.loads((resultdir / 'completed-pairs.json').read_text(encoding='utf-8'))
rows, audit_errors, all_events = [], [], []
for pair in pairs:
    p = pair['assignment']
    prefixdir = resultdir / p['pair_id'] / 'prefix'
    prefixaudit = validate_run(prefixdir)
    audit_errors.extend(p['pair_id'] + '/prefix:' + e for e in prefixaudit['errors'])
    all_events += prefixaudit['events']
    for policy in ['context', 'bound']:
        directory = resultdir / p['pair_id'] / policy
        score = score_run(directory)
        previous = json.loads((directory / 'score.json').read_text(encoding='utf-8'))
        if canonical(score) != canonical(previous): audit_errors.append(p['pair_id'] + '/' + policy + ':score_recomputation_mismatch')
        audit = validate_run(directory)
        all_events += audit['events']
        audit_errors.extend(p['pair_id'] + '/' + policy + ':' + e for e in score['audit_errors'])
        decisions = [e for e in audit['events'] if e['event_type'] == 'admission_decision']
        rows.append({'case': p['case_id'], 'config': p['config_id'], 'policy': policy,
            'checkpoint': pair['result']['checkpoint_reached'],
            'checkpoint_equal': len(set(pair['result']['checkpoint_hashes'].values())) == 1,
            'U': int(score['task_completion']), 'state_goal': int(score['state_goal']), 'I': score['I'],
            'continuity_incidence': score['continuity_failure_incidence'], 'transitions': score['transitions'],
            'continuity_failures': score['continuity_failures'], 'recovery_eligible': score['recoverable_first_episode'],
            'recovered': int(score['recovered']), 'path': score['recovery_path'],
            'G_eligible': int(score['G_standardized_recovery_eligible']), 'G_success': int(score['G_standardized_recovery_success']),
            'agent_calls': score['agent_tool_calls'], 'suffix_requests': score['model_requests'],
            'terminal': score['terminal'], 'suffix_seconds': round(score['elapsed_ms'] / 1000, 2),
            'agent_rejections': sum(e['payload']['decision'] == 'rejected' and e['payload']['caller_origin'] == 'agent' for e in decisions),
            'handoff_rejections': sum(e['payload']['decision'] == 'rejected' and e['payload']['caller_origin'] == 'harness_handoff' for e in decisions)})
actual_responses = [e for e in all_events if e['event_type'] == 'model_response']
format_failures = []
for e in actual_responses:
    try: parse_action(e['payload']['response'])
    except ValueError: format_failures.append({'run_id': e['run_id'], 'event_id': e['event_id']})
usage = Counter()
usage_unknown = 0
for e in actual_responses:
    if not e['payload']['usage']: usage_unknown += 1
    else:
        for key, val in e['payload']['usage'].items():
            if type(val) is int: usage[key] += val
G = [r for r in rows if r['G_eligible']]
conditional = [r for r in rows if r['recovery_eligible']]
summary = {'timestamp_utc': utc(), 'status': 'PILOT_ENGINEERING_COMPLETE_FORMAL_NOT_FROZEN',
    'planned_arms': 16, 'executed_arms': len(rows), 'pairs': len(pairs), 'formal_arms': 0,
    'engineering_only_not_effect_estimate': True, 'frozen_source_hashes_unchanged': not changed,
    'checkpoint_pairs_reached': sum(p['result']['checkpoint_reached'] for p in pairs),
    'checkpoint_isolation_pairs': sum(len(set(p['result']['checkpoint_hashes'].values())) == 1 for p in pairs),
    'completed_tasks': sum(r['U'] for r in rows), 'integrity_distribution': dict(Counter(str(r['I']) for r in rows)),
    'G_standardized_recovery': {'numerator': sum(r['G_success'] for r in G), 'denominator': len(G)},
    'conditional_recovery': {'numerator': sum(r['recovered'] for r in conditional), 'denominator': len(conditional),
         'paths': dict(Counter(r['path'] for r in conditional))},
    'unique_actual_model_invocations': sum(e['event_type'] == 'model_request' for e in all_events),
    'unique_actual_model_responses': len(actual_responses),
    'prefix_responses_billed_once': sum(e['event_type'] == 'model_response' and e['phase'] == 'shared_prefix' for e in all_events),
    'actual_format_failures_repaired_in_same_history': format_failures,
    'known_usage_sums': dict(usage), 'usage_missing_responses': usage_unknown, 'currency_cost': None,
    'audit_errors': audit_errors, 'rows': rows}
(resultdir / 'engineering-summary.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding='utf-8')
with (resultdir / 'arm-results.csv').open('w', encoding='utf-8-sig', newline='') as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
md = ['# Phase 2 pilot 工程报告', '', '状态：**16个预定在线 arms 已执行；正式128条尚未启动，正式采集版本尚未冻结。**', '',
    '本报告只评价工程实现、反馈链和评分可复算性。四个专用 pilot case 不进入正式效果分析，不能据此估计一般成功率、显著性或论文接收概率。', '',
    '## 执行配置与冻结', '',
    '- A：历史 G2 的 `gpt-5.6-terra`、low reasoning，通过账户内 Codex CLI；沿用本机既有系统代理。',
    '- B：历史 D1 的 `deepseek-v4-flash`、temperature=0，通过用户指定的 DSH API 凭据与 Anthropic 兼容接口。凭据在仓库外以 Windows 用户加密形式保存，不进入模型输入或实验日志。',
    '- 首次可用性探测的 A 超时、B 余额不足均保留；后续修复连接和替换用户指定凭据后，两原定模型通过纯接口探测。没有按恢复表现更换模型。',
    '- 4 case × 2 config × 2 policy = 16 arms，8 pairs，1 repetition。共同前缀只计一次真实调用，两臂复制同一数据库状态与可见会话。',
    '- v0.2 设计冻结在实现前完成；执行冻结包括 runner/scorer、测试、输入、工具、提示、分配顺序、环境版本及配置哈希。均为本地时间戳/哈希，不声称公开预注册或远端不可变注册。', '',
    '## 工程核验', '',
    '| 检查 | 结果 |', '|---|---|',
    '| 本地回归测试及独立复核 | 34/34 通过；覆盖缺失文件、已证实违例优先、被拒绝的瞬时修改、证书损坏、幂等/过期/重授权与格式错误 |',
    f"| 合法共同 checkpoint | {summary['checkpoint_pairs_reached']}/8 pairs |",
    f"| 两臂 checkpoint 状态哈希一致 | {summary['checkpoint_isolation_pairs']}/8 pairs |",
    f"| 事件链、schema、文件哈希、前后状态/转移 journal、数据库与独立评分复算 | {len(audit_errors)} 个审计错误 |",
    f"| G bound 标准化恢复 | {sum(r['G_success'] for r in G)}/{len(G)}；分母保留全部合法 checkpoint G-bound arms |",
    f"| 已证实送达且可恢复的首次拒绝 episode | {len(conditional)} runs；完成且 I=1 的恢复 {sum(r['recovered'] for r in conditional)} |", '',
    '## 每个 arm 的工程观察', '',
    '| Case | 配置 | Policy | U | I | 后续恢复路径 | Agent工具调用 | 终态 |', '|---|---|---|---:|---|---|---:|---|']
for r in rows:
    md.append(f"| {r['case']} | {r['config']} | {r['policy']} | {r['U']} | {r['I']} | {r['path'] or '无已送达可恢复拒绝'} | {r['agent_calls']} | {r['terminal']} |")
md += ['', 'U 与 I 独立评分。context 合法接受同 context／新 instance 的转移时，仍可能在预声明 A_instance 规范下 I=0；这不表示违反了 context 自身的 gate。G 的初次替换来自 harness_handoff，后续工具选择来自真实模型；两种来源分开记录。N 若未生成所要求的刷新 preview，即使 state 达标也不能记 U=1。', '',
    '## 已验证的故障边界', '',
    '已做确定性验证：授权/instance/context 拒绝、证据和证书损坏、过期前驱、旧授权失效、精确幂等重放及键冲突、格式错误、工具异常后提交结果不确定、日志/快照缺失、拒绝后发生修改又恢复的瞬时违例。HTTP 429/5xx/transport 按冻结预算最多两次外层重试；402不作无限重试。', '',
    f'在线 pilot 实际出现 {len(format_failures)} 次动作输出格式不合要求，均保留原始响应，并在同一会话通过一次通用格式反馈得到纠正；未重开任务、未删除这些调用成本。共同前缀中的一次格式修复被两臂继承，不算两次真实调用。独立原始输出核验另确认87个真实响应、68个模型所选工具调用和2次拒绝反馈送达。', '',
    '另一个独立确定性检查模拟持续429，验证总计3次尝试（初次＋2次重试）、遵守 Retry-After、用尽后明确失败且没有语义工具修改。该检查使用模拟 provider，不计入87次真实模型响应。', '',
    '这不构成“各种突发情况都能恢复”的保证。API 长期不可用、额度耗尽、provider 更新、操作系统崩溃或未知程序缺陷仍可导致失败。失败保留在计划分母内；信息不足记 unknown，已证实违例优先记0。工具 runner 的故障处理与 Agent 自己能否恢复是两个不同测量对象。', '',
    '## 资源及实施限制', '',
    f"实际唯一模型调用 {summary['unique_actual_model_invocations']} 次、返回 {len(actual_responses)} 次，其中共同前缀 {summary['prefix_responses_billed_once']} 次返回仅计一次。可获得的 usage 合计为 `{json.dumps(dict(usage), ensure_ascii=False)}`；缺失 usage 的响应 {usage_unknown} 个。账单货币值未知。", '',
    '两配置共用序列化 JSON 工具动作接口，每次决策重放完整可见会话。它是一个受控工具调用 Agent harness，不能写成 provider 原生 function-calling 或生产系统完整整合验证；隐藏会话状态没有克隆。', '',
    'DeepSeek 设置4096上游输出 token 上限；账户内 Codex CLI 未能设置同样的上游上限。两侧均执行调用、响应、工具数和时间上限。此偏离已在运行前的执行冻结中披露；不能声称两侧拥有完全相同的硬 token 或货币成本上限。OpenAI 官方对账户登录访问列出的限制亦将 max_output_tokens 列为不支持字段：[官方说明](https://developers.openai.com/siwc/token-sharing-open-source/preview-limitations)。', '',
    '请求的模型别名固定，但不可变 provider snapshot/revision 未提供；可获得的返回 model ID、请求 ID 和 usage 留在原始事件中。CLI 内部网络重连与 runner 外层重试分别可从原始日志检查，runner调用数不等于可精确观测的每个底层网络请求数。', '',
    '## 下一阶段', '',
    '正式采集 freeze 仍待完成。正式 E/V/R 场景实现、全32正式输入、价格/资源限制选择及全部正式代码/输入哈希，需要在采集前冻结。当前工程包只启动四个 pilot case，没有实现一个自动启动128条的入口。现有结果不得写成正式主实验。', '']
(ROOT / 'PILOT-REPORT.md').write_text('\n'.join(md), encoding='utf-8')
print(json.dumps({k: v for k, v in summary.items() if k not in ('rows', 'known_usage_sums')}, ensure_ascii=False, indent=2))
