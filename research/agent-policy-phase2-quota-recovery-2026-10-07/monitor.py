"""Read-only live monitor. No model calls, writes to results, or process control."""
import argparse
from collections import Counter
from datetime import datetime, timedelta, timezone
import json
import os
from pathlib import Path
import statistics
import sys
import time

ROOT=Path(__file__).resolve().parent
SHANGHAI=timezone(timedelta(hours=8))


def read_json(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def dt(value):
    return datetime.fromisoformat(value.replace('Z','+00:00'))


def read_events(path):
    try: lines=path.read_text(encoding='utf-8-sig').splitlines()
    except FileNotFoundError: return []
    events=[]
    for i,line in enumerate(lines):
        try: events.append(json.loads(line))
        except ValueError:
            if i!=len(lines)-1: raise
            # The collector may be in the middle of appending the final line.
    return events


def process_alive(launch):
    if not launch: return None
    pid=int(launch['pid'])
    if os.name!='nt':
        try: os.kill(pid,0); return True
        except ProcessLookupError: return False
        except PermissionError: return None
    import ctypes
    from ctypes import wintypes
    kernel=ctypes.WinDLL('kernel32',use_last_error=True)
    kernel.OpenProcess.argtypes=[wintypes.DWORD,wintypes.BOOL,wintypes.DWORD]
    kernel.OpenProcess.restype=wintypes.HANDLE
    kernel.GetExitCodeProcess.argtypes=[wintypes.HANDLE,ctypes.POINTER(wintypes.DWORD)]
    kernel.GetProcessTimes.argtypes=[wintypes.HANDLE]+[ctypes.POINTER(wintypes.FILETIME)]*4
    kernel.CloseHandle.argtypes=[wintypes.HANDLE]
    handle=kernel.OpenProcess(0x1000,False,pid)
    if not handle: return None if ctypes.get_last_error()==5 else False
    try:
        code=wintypes.DWORD()
        if not kernel.GetExitCodeProcess(handle,ctypes.byref(code)): return None
        if code.value!=259: return False
        times=[wintypes.FILETIME() for _ in range(4)]
        if kernel.GetProcessTimes(handle,*[ctypes.byref(t) for t in times]):
            created=((times[0].dwHighDateTime<<32)+times[0].dwLowDateTime)/10000000-11644473600
            # A recycled PID must not make a stopped collector appear active.
            if abs(created-dt(launch['started_utc']).timestamp())>30: return False
        return True
    finally: kernel.CloseHandle(handle)


def snapshot(root=ROOT, process_check=process_alive):
    now=datetime.now(timezone.utc)
    manifest=read_json(root/'recovery-manifest.json')
    status=read_json(root/'results/collection-status.json')
    launches=[]
    for p in root.glob('*launch.json'):
        try: launches.append(read_json(p))
        except (OSError,ValueError): continue
    launch=max(launches,key=lambda x:dt(x['started_utc'])) if launches else None
    alive=process_check(launch) if launch else None
    pairs=status['pairs']; terminals=0; success=0; intact=0; violation=0; unknown=0
    runtime=0; durations=[]; active=[]; recent=[]; finished_arms=0; complete_pairs=0
    for name,pair in pairs.items():
        attempts=pair.get('attempts',[])
        if not attempts: continue
        attempt=attempts[-1]; result=attempt.get('result',{})
        if pair['status']=='terminal':
            terminals+=1
            if attempt.get('finished_utc'):
                durations.append((dt(attempt['finished_utc']), max(0,(dt(attempt['finished_utc'])-dt(attempt['started_utc'])).total_seconds())))
            complete_pairs+=all(result.get(policy,{}).get('task_completion') is True for policy in ('context','bound'))
            for policy in ('context','bound'):
                arm=result.get(policy)
                if not arm: continue
                finished_arms+=1; success+=arm.get('task_completion') is True
                intact+=arm.get('I')==1; violation+=arm.get('I')==0; unknown+=arm.get('I')=='unknown'
                terminal=arm.get('terminal','unknown')
                runtime+=terminal in ('runtime_error','prefix_failure','timeout','budget','audit_state_missing')
                if terminal!='agent_final': recent.append((attempt.get('finished_utc',''),f'{name} / {policy}: {terminal}'))
        if pair['status'] in ('running','waiting_for_quota'):
            dest=root/'results'/attempt['directory']; counts=Counter(); errors=[]; last=None; phase=None
            for f in dest.glob('*/events.jsonl'):
                events=read_events(f); counts.update(e['event_type'] for e in events)
                if events:
                    newest=max((dt(e['timestamp_utc']) for e in events if e.get('timestamp_utc')),default=None)
                    if newest and (last is None or newest>last): last=newest; phase=f.parent.name
                errors.extend(e.get('payload',{}).get('error_code','unknown') for e in events if e['event_type']=='model_error')
            active.append({'pair':name,'state':pair['status'],'phase':phase,'attempt':len(attempts),
                'elapsed_seconds':max(0,(now-dt(attempt['started_utc'])).total_seconds()),
                'seconds_since_event':max(0,(now-last).total_seconds()) if last else None,
                'model_requests':counts['model_request'],'model_responses':counts['model_response'],
                'tool_calls':counts['tool_call'],'errors':errors[-3:]})
    last_durations=[v for _,v in sorted(durations)[-10:]]
    mean=statistics.mean(last_durations) if last_durations else None
    remaining=max(0,manifest['planned_pairs']-terminals)
    remaining_seconds=max(0,remaining*mean-sum(a['elapsed_seconds'] for a in active if a['state']=='running')) if mean else None
    finish=now+timedelta(seconds=remaining_seconds) if remaining_seconds is not None and alive is True and status['status']=='RUNNING' else None
    return {'time_shanghai':now.astimezone(SHANGHAI).isoformat(timespec='seconds'),
        'batch_status':status['status'],'process_alive':alive,'pid':launch.get('pid') if launch else None,
        'planned_pairs':manifest['planned_pairs'],'planned_arms':manifest['planned_arms'],
        'terminal_pairs':terminals,'remaining_pairs':remaining,'two_successful_arms_pairs':complete_pairs,
        'finished_arms':finished_arms,'successful_arms':success,'intact_arms':intact,
        'violation_arms':violation,'unknown_arms':unknown,'runtime_failure_arms':runtime,
        'recent_mean_pair_seconds':mean,'remaining_run_seconds':remaining_seconds,
        'estimated_finish_shanghai':finish.astimezone(SHANGHAI).strftime('%m-%d %H:%M') if finish else None,
        'active':active,'recent_failures':[v for _,v in sorted(recent)[-4:]],
        'collector_error':status.get('error'),'source':str(root/'results/collection-status.json')}


def duration(seconds):
    if seconds is None: return '样本不足'
    seconds=int(seconds)
    return f'{seconds//3600}小时{seconds%3600//60:02d}分' if seconds>=3600 else f'{seconds//60}分{seconds%60:02d}秒'


def render(s, interval):
    names={'RUNNING':'运行中','COMPLETE':'已结束','PAUSED_QUOTA':'额度不足，已暂停',
           'PAUSED_DEPLOYMENT':'部署变化，已暂停','PAUSED_AUDIT':'审计异常，已暂停','PAUSED_INFRASTRUCTURE':'运行异常，已暂停'}
    alive={True:'运行中',False:'已停止',None:'无法确认'}[s['process_alive']]
    percent=s['terminal_pairs']/s['planned_pairs'] if s['planned_pairs'] else 0
    bar='#'*int(percent*30)+'-'*(30-int(percent*30))
    print('Phase 2 补采实时监测（只读，不消耗模型额度）')
    print(f"北京时间 {s['time_shanghai'][:19].replace('T',' ')}  |  每 {interval:g} 秒刷新  |  Ctrl+C 退出\n")
    print(f"批次：{names.get(s['batch_status'],s['batch_status'])}    进程：{alive}    PID：{s['pid']}")
    if s['batch_status']=='RUNNING' and s['process_alive'] is False: print('提示：账本仍写着运行中，但进程已停止，需要检查采集日志。')
    print(f"[{bar}] {percent:.1%}  已结束配对 {s['terminal_pairs']}/{s['planned_pairs']}，剩余 {s['remaining_pairs']}")
    print(f"已结束策略臂 {s['finished_arms']}/{s['planned_arms']}；任务成功 {s['successful_arms']}；两臂都成功的配对 {s['two_successful_arms_pairs']}")
    print(f"完整性：I=1 {s['intact_arms']}，I=0 {s['violation_arms']}，未知 {s['unknown_arms']}；运行/超时等终止 {s['runtime_failure_arms']}")
    print('说明：已结束包含失败；任务成功与完整性分别统计。')
    print(f"\n最近最多10对平均耗时：{duration(s['recent_mean_pair_seconds'])}")
    print(f"预计剩余纯运行时间：{duration(s['remaining_run_seconds'])}")
    print(f"预计结束：{s['estimated_finish_shanghai'] or '暂停或进程未确认，暂不估算完成时刻'}（不含未来额度等待）")
    print('\n当前任务：')
    if not s['active']: print('  暂无正在执行的配对。')
    for a in s['active']:
        print(f"  {a['pair']} | {a['phase'] or a['state']} | 第{a['attempt']}次 | 已用 {duration(a['elapsed_seconds'])}")
        print(f"  模型请求/响应 {a['model_requests']}/{a['model_responses']}，工具调用 {a['tool_calls']}，距最近事件 {duration(a['seconds_since_event'])}")
        if a['seconds_since_event'] is not None and a['seconds_since_event']>180: print('  提示：超过3分钟未出现新事件，请检查模型连接或采集日志；这不自动判定为卡死。')
        if a['errors']: print('  最近请求错误：'+', '.join(a['errors']))
    if s['recent_failures']: print('\n最近异常终止：\n  '+'\n  '.join(s['recent_failures']))
    if s['collector_error']: print('\n采集器错误：'+s['collector_error'])
    print('\n关闭此窗口只关闭监测，不会停止实验。')
    print('数据源：'+s['source'])


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--interval',type=float,default=5)
    parser.add_argument('--once',action='store_true')
    parser.add_argument('--json',action='store_true')
    parser.add_argument('--root',type=Path,default=ROOT)
    args=parser.parse_args()
    if args.interval<1: parser.error('--interval must be at least 1 second')
    try:
        while True:
            try:
                data=snapshot(args.root)
                if not args.once and not args.json and sys.stdout.isatty(): os.system('cls' if os.name=='nt' else 'clear')
                if args.json: print(json.dumps(data,ensure_ascii=False,indent=2),flush=True)
                else: render(data,args.interval)
            except (OSError,ValueError,KeyError) as exc:
                print('读取状态暂时失败：'+str(exc),file=sys.stderr,flush=True)
                if args.once: return 1
            if args.once: return 0
            time.sleep(args.interval)
    except KeyboardInterrupt:
        print('\n监测已关闭，实验继续运行。')
        return 0


if __name__=='__main__': sys.exit(main())
