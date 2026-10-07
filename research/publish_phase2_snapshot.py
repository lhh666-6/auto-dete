"""Create an immutable, credential-scanned results handoff from completed pairs."""
from pathlib import Path
import csv
from collections import Counter
from datetime import datetime, timezone, timedelta
import hashlib
import json
import re
import shutil
import zipfile

REPO=Path(__file__).resolve().parents[1]
FORMAL=REPO/'research/agent-policy-phase2-formal-2026-10-07'
RECOVERY=REPO/'research/agent-policy-phase2-quota-recovery-2026-10-07'
REVISION=REPO/'revisions/2026-10-07-kais-continuity'
now=datetime.now(timezone.utc)
stamp=now.strftime('%Y-%m-%dT%H%M%SZ')
DEST=REPO/'research/phase2-results-snapshots'/stamp
DEST.mkdir(parents=True,exist_ok=False)
secret=re.compile(rb'sk-[A-Za-z0-9_-]{24,}|(?:ghp_|github_pat_)[A-Za-z0-9_]{30,}')


def read(path): return json.loads(path.read_text(encoding='utf-8-sig'))
def digest(raw): return hashlib.sha256(raw).hexdigest()
def save(path,obj): path.write_text(json.dumps(obj,ensure_ascii=False,indent=2),encoding='utf-8')


def scan(raw,name):
    if secret.search(raw): raise ValueError('Credential-shaped content in '+name)


def archive(name, paths, extras=None):
    records=[]
    with zipfile.ZipFile(DEST/name,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for p in sorted(paths):
            raw=p.read_bytes(); rel=p.relative_to(REPO).as_posix()
            if p.suffix.lower() not in ('.sqlite','.db','.png','.pdf','.zip'): scan(raw,rel)
            z.writestr(rel,raw); records.append({'path':rel,'bytes':len(raw),'sha256':digest(raw)})
        for rel,raw in (extras or {}).items():
            scan(raw,rel); z.writestr(rel,raw)
            records.append({'path':rel,'bytes':len(raw),'sha256':digest(raw)})
        z.writestr('SNAPSHOT-MEMBERS.json',json.dumps(records,indent=2))
    with zipfile.ZipFile(DEST/name) as z:
        if z.testzip() is not None: raise ValueError('ZIP CRC failed')
        for record in records:
            if digest(z.read(record['path']))!=record['sha256']: raise ValueError('Member hash failed')
    return {'file':name,'bytes':(DEST/name).stat().st_size,'sha256':digest((DEST/name).read_bytes()),'verified_members':len(records)}


source_status=read(RECOVERY/'results/collection-status.json')
selected={name:record for name,record in source_status['pairs'].items() if record['status']=='terminal'}
manifest=read(RECOVERY/'recovery-manifest.json')
rows=[]; errors=Counter(); scenarios=Counter()
for name,record in selected.items():
    result=record['attempts'][-1]['result']; scenarios[record['assignment'].get('scenario','unknown')]+=1
    for policy in ('context','bound'):
        arm=result.get(policy,{})
        rows.append({'pair_id':name,'scenario':record['assignment'].get('scenario'),
            'policy':policy,'U':arm.get('task_completion'),'I':arm.get('I'),
            'terminal':arm.get('terminal'),'attempt_directory':record['attempts'][-1]['directory'],
            'finished_utc':record['attempts'][-1].get('finished_utc')})
    for p in (RECOVERY/'results'/name).glob('attempt-*/*/events.jsonl'):
        for line in p.read_text(encoding='utf-8').splitlines():
            e=json.loads(line)
            if e['event_type']=='model_error': errors[e['payload'].get('error_code','unknown')]+=1
snapshot_status={**source_status,'status':'SNAPSHOT_PARTIAL','pairs':selected,
    'snapshot_utc':now.isoformat(),'terminal_pairs':len(selected),'source_status':source_status['status'],
    'note':'Completed/terminal pairs only. Active and unstarted pairs omitted from this immutable snapshot; this is not a final recovery analysis.'}
save(DEST/'source-collection-status.json',source_status)
save(DEST/'recovery-snapshot-status.json',snapshot_status)
raw_status=json.dumps(snapshot_status,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()
formal_paths=[p for p in (FORMAL/'formal-results').rglob('*') if p.is_file() and p.suffix.lower()!='.lock']
formal_receipt=archive('formal-results-complete.zip',formal_paths)
recovery_paths=[p for name in selected for p in (RECOVERY/'results'/name).rglob('*') if p.is_file() and p.suffix.lower()!='.lock']
recovery_receipt=archive('quota-recovery-terminal-pairs.zip',recovery_paths,
    {'research/agent-policy-phase2-quota-recovery-2026-10-07/results/collection-status.json':raw_status})
analysis=DEST/'original-formal-analysis'; analysis.mkdir()
for p in (REVISION/'evidence/online').iterdir():
    if p.is_file() and p.suffix in ('.csv','.json','.pdf','.png','.svg'): shutil.copy2(p,analysis/p.name)
with (DEST/'recovery-terminal-arm-outcomes.csv').open('w',encoding='utf-8',newline='') as f:
    writer=csv.DictWriter(f,fieldnames=list(rows[0])); writer.writeheader(); writer.writerows(rows)
groups={}
for policy in ('context','bound'):
    subset=[r for r in rows if r['policy']==policy]
    groups[policy]={'terminal_arms':len(subset),'U1':sum(r['U'] is True for r in subset),
        'I1':sum(r['I']==1 for r in subset),'I0':sum(r['I']==0 for r in subset),
        'I_unknown':sum(r['I']=='unknown' for r in subset)}
summary={'snapshot_utc':now.isoformat(),'snapshot_shanghai':now.astimezone(timezone(timedelta(hours=8))).isoformat(),
    'original_formal_status':read(FORMAL/'formal-results/collection-status.json')['status'],
    'original_formal_planned_arms':512,'recovery_status':'PARTIAL','recovery_freeze_id':manifest['freeze_id'],
    'recovery_planned_pairs':117,'recovery_terminal_pairs_included':len(selected),'recovery_planned_arms':234,
    'recovery_terminal_arms_included':len(rows),'recovery_groups':groups,'recovery_scenarios':dict(scenarios),
    'recovery_model_errors':dict(errors),'formal_inference_from_partial_recovery_allowed':False,
    'archives':[formal_receipt,recovery_receipt],
    'data_preservation':'Original records retained. Recovery cohort not substituted silently into primary outcomes.',
    'credential_scan':'Included text scanned; external credentials and account config files not selected.'}
save(DEST/'snapshot-summary.json',summary)
local_time=now.astimezone(timezone(timedelta(hours=8))).strftime('%Y-%m-%d %H:%M:%S')
(DEST/'README.md').write_text(f'''# Phase 2 实验结果快照

快照时间：**{local_time}（北京时间）**。

原正式批次已结束，128 tasks × 2 configs × 2 policies = 512 个计划臂，失败和 unknown 均保留。本轮额度恢复补采仍在进行：117 个计划配对中，本快照只纳入 **{len(selected)} 个已终止配对 / {len(rows)} 个策略臂**。已终止包含失败；正在写入的轨迹没有收入压缩包。

## 内容

- `formal-results-complete.zip`：原正式批次原始轨迹、状态数据库、提供方响应、账本。
- `quota-recovery-terminal-pairs.zip`：补采已终止配对及独立快照账本；每个原任务保留对应关系。
- `original-formal-analysis/`：原批次四张结果表、配对效应、全部失败分类、分析摘要和图。
- `recovery-terminal-arm-outcomes.csv`：补采当前逐臂描述性结果。
- `snapshot-summary.json`：进度、分母、分组计数和压缩包 SHA-256。
- `source-collection-status.json`：采样时原账本，含当时运行中的任务元数据；这部分没有打包未稳定的原始文件。
- 每个 ZIP 中的 `SNAPSHOT-MEMBERS.json`：逐文件 SHA-256；已验证 CRC 和全部成员哈希。

## 离线复算

在本仓库根目录解压 `formal-results-complete.zip`，其中路径以 `research/` 开始。安装正式包的固定依赖后运行：

```powershell
python research/agent-policy-phase2-formal-2026-10-07/analyze_formal.py --output fresh-formal-analysis --figures
```

这只做离线评分，不调用模型。补采代码与 freeze 位于 `research/agent-policy-phase2-quota-recovery-2026-10-07/`。本快照的补采数据尚未覆盖完整队列，只用于检查和描述，不能当成最终推断。保留原批次分析；任何合并视图必须明确标注原批次与补采来源。

原冻结协议、任务、模型别名、工具、评分器和配对顺序不因上传改变。原始运行日志保留已观察到的额度故障。调用凭据不在包内。共同作者读取结果即可；恢复或另行采集需协调批次，避免多人重复采集。
''',encoding='utf-8')
shutil.copy2(Path(__file__),DEST/'build_snapshot.py')
for p in DEST.rglob('*'):
    if p.is_file() and p.suffix not in ('.zip','.png','.pdf'): scan(p.read_bytes(),p.relative_to(DEST).as_posix())
save(DEST/'files-sha256.json',{p.relative_to(DEST).as_posix():digest(p.read_bytes()) for p in sorted(DEST.rglob('*')) if p.is_file()})
print(json.dumps({'destination':str(DEST),'terminal_pairs':len(selected),'archives':summary['archives']},indent=2),flush=True)
