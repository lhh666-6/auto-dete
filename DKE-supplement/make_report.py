"""Summarize completed measurements only; never fabricate missing cells."""
import csv
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parent
def read(path):return json.loads((ROOT/path).read_text(encoding='utf-8'))
def jsonl(path):return [json.loads(s) for s in (ROOT/path).read_text(encoding='utf-8').splitlines()]
def table(headers,rows):
    return '\n'.join(['| '+' | '.join(headers)+' |','| '+' | '.join(['---']*len(headers))+' |']+['| '+' | '.join(map(str,r))+' |' for r in rows])
def csvfile(name,rows):
    path=ROOT/'tables'/name;path.parent.mkdir(exist_ok=True)
    with path.open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def hashfile(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    e1=read('results/e1/summary.json');r1=jsonl('results/e1/receipts.jsonl')
    e2=read('results/e2/summary.json');r2=jsonl('results/e2/browser-observations.jsonl')
    assert len(r1)==495 and all(not r['harness_error'] for r in r1)
    assert len(r2)==60 and all(not r['harness_error'] for r in r2)
    assert all(r['acceptance_equal'] and r['query_answers_equal'] for r in e1['exact_baseline_reference_comparisons'])
    assert all(r['accepted'] or r['zero_write_on_reject'] for r in r1)
    assert all(r['response']['accepted'] or r['response']['zero_write_on_reject'] for r in r2)
    for mode in ['original_confirm','session_gate']:
        assert all(r['response']['accepted'] and not r['review_mismatches'] for r in r2 if r['mode']==mode and r['case'] in ['accept','correction','reselect'])
    for name,count in [('mechanism',4000),('ablation',4000),('trace',14400)]:
        receipt=read('results/e3/'+name+'-receipt.json')
        assert receipt['status']=='complete' and receipt['observations']==count
        raw=jsonl('results/e3/'+name+'/raw.jsonl');assert len(raw)==count
        csvfile('e3-'+name+'-summary.csv',read('results/e3/'+name+'/summary.json'))
    assert read('results/e3/storage-receipt.json')['cells']==3
    # Check pre-run source hashes; additional reporting scripts do not alter them.
    frozen=read('results/e3/pre-run-manifest-all.json')
    for path,digest in frozen.items():
        path=path.replace('\\','/')
        actual=(ROOT.parent/'dke-experiments'/path) if path.startswith('latest/') else ROOT/path
        assert hashfile(actual)==digest,('measurement source changed',path)
    mechanism=read('results/e3/mechanism/summary.json');ablation=read('results/e3/ablation/summary.json');trace=read('results/e3/trace/summary.json')
    pairs=read('results/e3/trace/paired.json');storage=read('results/e3/storage/raw.json')['observations']
    cells=sorted({(r['fields'],r['changed']) for r in mechanism})
    find=lambda rows,**kw:next(r for r in rows if all(r[k]==v for k,v in kw.items()))
    admission_rows=[]
    for f,c in cells:
        a=find(mechanism,fields=f,changed=c,arm='reference');b=find(mechanism,fields=f,changed=c,arm='journal_exact')
        x=find(ablation,fields=f,changed=c,arm='full');y=find(ablation,fields=f,changed=c,arm='materialization')
        admission_rows.append([f,c,f"{a['p50_ms']:.2f} / {a['p95_ms']:.2f}",f"{b['p50_ms']:.2f} / {b['p95_ms']:.2f}",f"{x['p50_ms']:.2f} / {x['p95_ms']:.2f}",f"{y['p50_ms']:.2f} / {y['p95_ms']:.2f}"])
    trace_rows=[]
    for v in [1,10,100]:
        a=find(trace,fields=128,versions=v,records=1000,arm='batch');b=find(trace,fields=128,versions=v,records=1000,arm='point_lookup')
        trace_rows.append([128,v,1000,f"{a['p50_ms']:.2f} / {a['p95_ms']:.2f}",f"{b['p50_ms']:.2f} / {b['p95_ms']:.2f}",a['sql_min'],b['sql_min']])
    csvfile('e1-comparison.csv',[{k:v for k,v in a.items() if k!='query_counts'}|{('query_'+k):a['query_counts'].get(k,0) for k in ['correct','wrong','ambiguous','unavailable']} for a in e1['arms']])
    csvfile('e2-cases.csv',[{k:r[k] for k in ['label','mode','case']}|{'accepted':r['response']['accepted'],'review_mismatches':';'.join(r['review_mismatches']),'zero_write_on_reject':r['response']['zero_write_on_reject']} for r in r2])
    csvfile('storage.csv',[{'transitions':r['transitions'],'full_bytes':r['full']['bytes'],'lower_bytes':r['lower']['bytes'],'incremental_bytes':r['incremental_bytes']} for r in storage])
    e1table=table(['机制','案例数','接受','实例级不当接受','值级不当接受','正确查询答案','不确定答案'],[[a['arm'],a['planned'],a['accepted'],a['instance_policy_violations'],a['value_policy_violations'],a['query_counts'].get('correct',0),a['query_counts'].get('ambiguous',0)] for a in e1['arms']])
    e2table=table(['路径','案例数','合法控制通过','请求替换不一致','仅显示篡改不一致','拒绝后写入'],[[m,30,'9/9',sum(bool(r['review_mismatches']) for r in r2 if r['mode']==m and r['case']!='dom_only_substitution'),sum(bool(r['review_mismatches']) for r in r2 if r['mode']==m and r['case']=='dom_only_substitution'),0] for m in ['original_confirm','session_gate']])
    runtimes={n:read('results/e3/'+n+'-receipt.json')['elapsed_seconds'] for n in ['mechanism','ablation','trace','storage']}
    slow=find(trace,fields=128,versions=100,records=1000,arm='batch')
    ratio=find(pairs,fields=128,versions=100,records=1000)['p50_ratio_first_over_second']
    report=f'''# 三组 DKE 补充实验结果

三组实验已实际运行完成，**没有调用 DeepSeek 或其他在线模型 API**。源码、原始记录、数据库、浏览器截图与复现命令均保留。

本次结果支持实例级授权约束的必要性，同时明确了两个限制：完整事件日志加入同样绑定后可以达到相同判定；数据库约束本身不能证明用户确实看到了某个页面内容。

## 运行范围

- 固定源码提交：`c6d512843c905cab6d8521dd8c914f7fb26d85ae`，实际调用 `latest/code/implementation-fixed`，包含 JSON 类型相等性修复。
- E1：15 个输入 × 11 类案例 × 3 种机制 = **495 次案例执行**。
- E2：3 种 JSON 值 × 10 类交互 × 2 条路径 = **60 次浏览器案例**，另有 6 次重放案例的首次确认。
- E3：两组各 10 格准入比较、36 格追溯比较；每格每臂 5 次预热、200 次计时，共 **22,400 条正式计时**，不含预热。另有 3 个存储规模。
- 原实现相关测试 **85 项通过**，新增实验检查 **10 项通过**。没有把测试通过数当作独立攻击样本数。

## 第一组：强上下文基线、精确绑定和溯源查询

输入按预设规则从原归档 G1/G2/D1 × B1–B4 中选取首个包含候选提议的运行，不按任务成功标签筛选；另外加入 `2→2.0`、`1→true`、嵌套 JSON 数值类型变化三项合成控制。归档值被映射到新构造的表单，不是原工作流的端到端重跑。证书和审核事件均重新构造；来源文件路径、事件编号和散列见 `results/e1/inputs.json`。

三个配置在这些选中案例中的提议值相同，12 个归档单元实际只有 **4 种不同提议值**：8、100、字符串 B-008、9；加上合成控制共 7 种不同提议值。因此 495 是完整执行组合数，不是 495 个独立场景。归档中请求的模型名称为 gpt-5.6-luna、gpt-5.6-terra、deepseek-v4-flash，仅描述历史元数据，本次没有重新调用它们。

新基线采用独立编写的 sqlite3 事件日志，保留候选、审核上下文、版本、完整字段来源、不可变日志和事务控制。精确绑定版额外记录被审核的候选标识。它是本次实验代码，不能称为第三方系统或外部团队复现。

本实验的“值级策略”仍要求字段、版本、证据与保留的审核上下文相符，只不要求候选实例标识相同；不是仅检查一个数值相等。上下文投影明确排除了候选标识、候选内部编号和实例创建时间。

{e1table}

11 类案例包括合法接受、纠正、多字段提交、同值替换、不同证据替换、过期、重放、未经授权的值，以及 CAS 后、写入转换前、提交前中断。

精确绑定日志与参考实现的 **165/165** 对应案例判定及查询答案一致。两者的 45 个合法案例全部接受；120 个预期拒绝案例均未改变事实库状态。上下文日志接受 15 个同值实例替换：它们违反实例级策略，但满足此实验定义的值级策略。相应地，两种精确绑定机制在值级策略下表现为 15 次额外拒绝，这属于策略更严格，不能只报“安全提升”而省略代价。

零写入检查的起点是授权准备完成后、准入尝试之前；它不要求撤销先前已记录的审核意图。事件日志的授权准备会预先持久化审核记录，参考适配器则捕获原服务生成的准入包后再送入真实事务。三种中断案例检验的是回滚行为，不是三个独立攻击模型。

每次成功提交对 3 个字段查询提议值、授权值、审核人、被审核候选、当前值和来源版本，共 18 项答案。上下文日志有 60 项候选身份答案不唯一，其余答案正确；两种精确绑定机制各 810 项答案全部正确。该总数是字段查询数，不能当作 810 个独立实验。

另行复现原论文的 strengthened baseline：B1 在 8 类准入案例中有 7 类与候选绑定判定一致，同值替换仍是差异；配对历史区分是另列的第 9 项检查。原 Full 配置 9/9 检查与预设参考一致。连续性结果见 `results/original-baseline-continuity`，不混入新增 495 次实验统计。

**建议写入论文的结论：**区分值级相等与实例级授权；贡献在于明确绑定、事务落实和可检查来源链，而不是排除事件日志架构实现相同契约的可能。

## 第二组：显示、审核授权与最终确认

使用本地真实 Chrome 和 Playwright；审核页面是本次新建的实验夹具，后端调用论文原 `ReviewForms.confirm`，并非对原产品完整 UI 的安全评估。独立驱动在点击授权之前读取 DOM 中的候选标识、提议值与授权值，再与提交数据库中的结果比较。三个输入为 100、2.5 和 true。新路径增加服务器持有的候选、版本、审核人和授权值绑定。

{e2table}

合法接受、纠正、重新选择共每路径 9 个案例，全部正常通过。原确认路径在候选、授权值、审核人请求替换的 9 个案例中，接受了与已记录审核意图不一致的输入；新增会话绑定全部拒绝。过期、重放和提交前中断在两条路径中均被拒绝，事实库均零写入。

两条路径都无法阻止 **3 个“仅篡改 DOM 显示”案例**：页面显示 B，服务器和请求仍处理 A。这一负结果必须保留。它说明服务器绑定不能替代可信显示；不是证明模型、浏览器或认证系统遭到了真实攻击。

原接口本来把调用者传入的候选和值当作审核授权输入，因此上述 9 个案例揭示的是调用边界的可信前提，不能描述成原实现违反了它已经建立的数据库绑定。新增会话绑定是实验扩展，使用固定模拟身份；会话库与事实库分离，没有验证跨库崩溃原子性或恶意宿主防护。

**建议写入论文的结论：**将可信审核界面和认证调用者写入前提，明确绑定应当在审核步骤建立；把 DOM-only 案例作为边界控制。

## 第三组：当前修复版的性能与存储

环境：Intel Core i7-10875H，Windows 10 build 19045，CPython 3.11.16，SQLite 3.53.1，SQLAlchemy 2.0.51。未控制操作系统背景负载。两臂随机交错执行，种子 20260923；比较对象都在本机本次重新计时。准入采用 SQLite DELETE 日志与 FULL 同步。原依赖锁已保留。

### 准入成本

下表单位为毫秒，均为 **p50 / p95**。前两列比较共同负载下的完整确认路径；后两列是独立的预验证落库消融。不能跨两组直接相减，也不能把预验证落库当成具有完整验证功能的系统。

完整机制组使用预先登记的识别候选；原有落库消融夹具使用手工录入来源。因此两个“完整确认”列不是同一负载的重复测量。

{table(['字段数','变化字段','参考完整确认','精确绑定日志','完整确认（消融组）','预验证落库'],admission_rows)}

完整机制比较每对都验证最终查询结果相同，包括未改字段来源保留；参考实现还包含不同的模式、ORM 和证书验证成本，因此差距不能归因于单一绑定操作。事件日志没有实现参考应用的全部产品功能。两种 SQL 计数钩子对触发器的计数口径不同，不比较其绝对数量。

完整机制组计时覆盖 `confirm` 调用，排除数据库复制和适配器对象构造。sqlite3 连接在对象构造时建立，而 SQLAlchemy 的首次连接在调用内惰性建立；小规模结果因此还包含不同连接生命周期的影响。这是明确调用边界下的实现成本描述，不是严格隔离所有因素的算法微基准。

消融组在计时外预先生成有效数据库增量，每次落库后验证完整关系状态指纹一致。它衡量省略验证和计划构造后的持久化成本，不是可直接部署的安全基线。

指纹对照的是预先生成的参考后状态。完整确认每次会生成新的审核标识和时间戳，因此没有声称随机交错的两臂数据库文件逐字节相同。

### 追溯成本

采用 4 个字段规模 × 3 个版本规模 × 3 个总记录规模的原 36 格网格。对照保持当前验证器相同，只将证书、证书证据关联和转换记录的三个批量读取操作改为枚举标识后逐项读取。每次计时结束后核对**整个追溯返回对象**相等。

以下列出字段数 128、总记录数 1000 的三格，单位仍为 p50 / p95 毫秒：

{table(['字段','版本','总记录','批量读取','逐项读取','批量 SQL','逐项 SQL'],trace_rows)}

最大网格点的批量读取 p50 为 **{slow['p50_ms']:.2f} ms**，逐项读取与批量读取的 p50 比值为 **{ratio:.2f}**。这是相同当前验证器下的访问方式消融，不是旧机器旧代码与新机器的性能提升倍数。36 格完整结果、每次 SQL 数、配对差值和 bootstrap 区间见附表及 JSON。

### 存储

{table(['转换数','完整模式 MiB','简化存储 MiB','增量字节/转换'],[[r['transitions'],f"{r['full']['bytes']/1048576:.2f}",f"{r['lower']['bytes']/1048576:.2f}",f"{r['incremental_bytes']/r['transitions']:.1f}"] for r in storage])}

存储实验沿用直接填充关系的合成规模夹具，使用 WAL/NORMAL 并完成 checkpoint；它说明模式占用，不表示这些行逐条通过了准入，也不表示简化库具有相同审计功能。

该夹具采用单字段版本增长和稳定证据引用，统计数据库文件，不包含影像或模型原始输出文件的外部存储占用。

## 交付与适用边界

- `results/e1/receipts.jsonl`：逐案例判定、错误、数据库摘要和查询答案。
- `results/e2/browser-observations.jsonl`：页面观察、请求、提交结果；同目录保留截图和会话数据库。
- `results/e3/*/raw.jsonl`：逐次延迟、执行顺序和 SQL 数；`summary.json`、`paired.json` 提供汇总。
- `tables/`：可直接整理成论文表格的 CSV；`figures/`：PNG 和矢量 SVG。
- `README.md`：复现命令；`PROTOCOL.md`：实验计划及明确修订。
- `rejection-audit.json`：逐类核对 372 次拒绝的具体原因，确认是预期约束或注入中断，而非任意程序异常。
- `results/e3/pre-run-manifest-all.json`：正式性能运行前的源码散列；报告生成时再次核对未发生变化。

这些结果补足了强基线、审核边界和修复后成本证据，但仍没有独立机构部署、真实用户实验或新模型调用。所有故障比例只描述有限构造案例。时间区间只反映本机重复计时，不覆盖跨机器或跨部署变异。

E3 四节实际耗时分别为：完整机制 {runtimes['mechanism']:.1f} 秒、落库消融 {runtimes['ablation']:.1f} 秒、追溯 {runtimes['trace']:.1f} 秒、存储 {runtimes['storage']:.1f} 秒。
'''
    (ROOT/'REPORT.md').write_text(report,encoding='utf-8')
    plots(mechanism,ablation,trace,storage,cells)
    manuscript=f'''# Suggested manuscript insertion (new experiments)

These paragraphs describe the completed supplementary runs. They should be integrated with the paper's definitions and threat model, not presented as independent field validation.

## Strong-context comparator and retrospective queries

We implemented a separate SQLite event-journal comparator retaining candidates, rich review context, immutable events, complete field-source maps, freshness checks, and transactional updates. A second configuration additionally recorded the exact reviewed candidate identifier. This comparator was written for the study; it is not an independently deployed third-party system. We used twelve archived proposal values selected deterministically across the existing three model configurations and four benign scenario labels, supplemented by three synthetic JSON-type boundary inputs. These values were mapped into constructed form histories; no hosted model was called.

Across 15 inputs, 11 case families, and three mechanisms, all 495 executions completed. The exactly bound journal and the reference implementation agreed on all 165 paired cases and their query answers. Each admitted 45 legal cases and rejected 120 cases without changing the fact database. The context-only journal admitted 15 equal-valued candidate substitutions. These admissions satisfied the defined value-level policy but violated the instance-level policy. Conversely, both exactly bound mechanisms rejected these 15 otherwise value-valid substitutions. Among successful histories, 60 reviewed-candidate query answers were ambiguous in the context-only journal; all 810 answers for each exactly bound mechanism were correct. These counts are finite constructed cases and field-level answers, not population failure-rate estimates.

The results identify an enforcement requirement rather than an architectural impossibility: an event journal supplied with the same exact authorization binding can implement the tested contract.

The value-level policy also requires the retained field, version, evidence, and review context to match; it does not mean numeric equality alone. The context projection explicitly omits the certificate identifier, candidate identifier, and per-instance creation timestamp.

The three archived model configurations yielded identical proposal values in the selected four scenarios, so the twelve archived cells contain only four distinct proposal values. Including the synthetic controls gives seven distinct proposal values; execution counts must not be interpreted as independent workflow diversity or provider comparisons.

## Review-boundary experiment

An instrumented local browser interface exercised the unmodified confirmation service and an experimental server-held review-session gate. An independent driver recorded the displayed candidate and authorized value from the DOM before confirmation. Across 60 browser cases, both paths admitted all 9 legitimate controls per path. The original confirmation path admitted 9 request substitutions inconsistent with the previously recorded review intent; the session gate rejected all 9. This exposes the original service's trusted-caller boundary, not a violation of an independently established binding inside its transaction. Both paths rejected stale submissions, replays, and injected precommit interruptions without fact writes.

Both paths admitted all 3 DOM-only substitutions, in which the displayed identifier changed while the server-side target remained unchanged. Thus, session binding does not attest display integrity. The study used scripted interactions and fixed principal labels, and did not test human attention, authentication security, a compromised host, or cross-database crash atomicity.

## Current-version cost characterization

We reran cost measurements against the equality-repaired implementation on one Windows machine using CPython 3.11.16 and SQLite 3.53.1. Each cell used five warmups and 200 measured executions per arm, with seeded interleaving. Two ten-cell admission comparisons distinguished complete confirmation under the shared workload from an explicitly prevalidated materialization ablation. The latter verified the resulting relational-state fingerprint but omitted validation from its timed region; it is not a complete admission alternative.

The 36-cell trace comparison held the current verifier fixed and changed three bulk repository reads to identifier enumeration followed by point lookups. The full returned trace object was identical after every invocation. At 128 fields, 100 versions, and 1,000 records, bulk tracing had a median latency of {slow['p50_ms']:.2f} ms; the point-to-bulk median ratio was {ratio:.2f}. These are within-run access-pattern measurements, not historical cross-machine speedups. Synthetic storage fixtures at 1,000, 10,000, and 100,000 transitions characterize schema footprint only. All raw observations, configurations, code hashes, and paired summaries are retained.

The complete-mechanism timer covers the confirmation call and excludes database cloning and adapter construction. The journal opens its SQLite connection eagerly during construction, whereas the ORM arm opens its first connection lazily inside the call. These measurements therefore characterize the stated interface boundary; they are not a connection-controlled algorithm microbenchmark or an isolated estimate of exact-binding overhead.
'''
    (ROOT/'MANUSCRIPT_INSERT.md').write_text(manuscript,encoding='utf-8')
    verification={'e1_cases':len(r1),'e2_cases':len(r2),'e3_timed_observations':22400,'exact_reference_pairs_equal':165,
        'measurement_source_hashes_verified':len(frozen),'all_expected_result_counts_verified':True,
        'all_rejection_fact_digests_unchanged':True,'hosted_model_calls':0}
    (ROOT/'verification.json').write_text(json.dumps(verification,indent=2),encoding='utf-8')
    print(json.dumps(verification,indent=2))

def plots(mechanism,ablation,trace,storage,cells):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    plt.rcParams.update({'font.size':10,'svg.fonttype':'none','axes.spines.top':False,'axes.spines.right':False})
    out=ROOT/'figures';out.mkdir(exist_ok=True)
    fig,axs=plt.subplots(2,2,figsize=(12,8),layout='constrained')
    for ax,rows,arms,title in [(axs[0,0],mechanism,['reference','journal_exact'],'Complete confirmation: shared workload'),(axs[0,1],ablation,['full','materialization'],'Prevalidated materialization ablation')]:
        for arm in arms:
            rs=[next(r for r in rows if r['arm']==arm and (r['fields'],r['changed'])==cell) for cell in cells]
            ax.plot(range(len(cells)),[r['p50_ms'] for r in rs],marker='o',label=arm)
        ax.set_xticks(range(len(cells)),[f'{f}/{c}' for f,c in cells],rotation=45);ax.set_yscale('log');ax.set_ylabel('Median latency (ms, log scale)');ax.set_xlabel('Fields / changed fields');ax.set_title(title);ax.legend(fontsize=8);ax.grid(alpha=.2)
    for arm in ['batch','point_lookup']:
        rs=sorted([r for r in trace if r['fields']==128 and r['records']==1000 and r['arm']==arm],key=lambda r:r['versions'])
        axs[1,0].plot([r['versions'] for r in rs],[r['p50_ms'] for r in rs],marker='o',label=arm)
        axs[1,1].plot([r['versions'] for r in rs],[r['sql_min'] for r in rs],marker='o',label=arm)
    for ax in axs[1]:ax.set_xscale('log');ax.set_xlabel('Versions (128 fields; 1,000 total records)');ax.legend();ax.grid(alpha=.2)
    axs[1,0].set_ylabel('Median latency (ms)');axs[1,0].set_title('Same current trace verifier')
    axs[1,1].set_ylabel('SQL statements per trace');axs[1,1].set_title('Batch versus actual point reads')
    for suffix in ['png','svg']:fig.savefig(out/('costs.'+suffix),dpi=180)
    plt.close(fig)
    fig,ax=plt.subplots(figsize=(6.6,4.4),layout='constrained')
    for arm,label in [('full','Full schema'),('lower','Reduced footprint fixture')]:
        ax.plot([r['transitions'] for r in storage],[r[arm]['bytes']/1048576 for r in storage],marker='o',label=label)
    ax.set_xscale('log');ax.set_yscale('log');ax.set_xlabel('Synthetic transitions');ax.set_ylabel('Checkpointed database (MiB)');ax.set_title('Storage footprint (not a functional comparison)');ax.grid(alpha=.2);ax.legend()
    for suffix in ['png','svg']:fig.savefig(out/('storage.'+suffix),dpi=180)
    plt.close(fig)

if __name__=='__main__':main()
