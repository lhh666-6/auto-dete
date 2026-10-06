"""Two availability/identity probes only. Never invokes formal task collection."""
import json, platform, subprocess, sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent/'src'))
from phase2.kernel import utc, canonical
from phase2.providers import Provider, TransportError, parse_action

def probe(destination):
    root=Path(__file__).resolve().parent
    source=root.parent/'agent-policy-phase2-pilot-2026-10-06/frozen-execution/configs.json'
    configs=json.loads(source.read_text(encoding='utf-8'))
    destination.mkdir(parents=True,exist_ok=False)
    observations=[]
    cli=subprocess.run(['codex','--version'],capture_output=True,text=True).stdout.strip()
    for config in configs:
        start=utc()
        config.update(top_p=None,seed_support='not observable/not requested',
            requested_alias=config['model'],sdk=cli if config['id']=='A' else 'urllib/Python-'+platform.python_version())
        try:
            result=Provider(config).decide([{'kind':'diagnostic','instruction':'Availability/identity check only. Return final with report_json {"availability":"ok"}. No correction task.'}],destination/config['id'])
            parse_action(result['raw_action'])
            observation={'status':'AVAILABLE','requested_alias':config['model'],
                'actual_returned_identifier':result.get('model'),'observable_revision':result.get('returned_revision'),
                'provider_request_id':result.get('provider_request_id'),'usage':result.get('usage'),
                'identity_limitation':'CLI does not expose returned model/revision' if config['id']=='A' else 'Returned alias does not certify an immutable snapshot'}
        except (TransportError,ValueError) as exc:
            observation={'status':getattr(exc,'code',str(exc)),'actual_returned_identifier':None,'observable_revision':None}
        observation.update(config=config,probe_start_utc=start,probe_end_utc=utc(),formal_arm=False)
        observations.append(observation)
        (destination/'agent-config-observations.json').write_text(canonical(observations),encoding='utf-8')
        print(canonical({'config':config['id'],'status':observation['status'],'returned_identifier':observation['actual_returned_identifier']}),flush=True)
    return observations

if __name__=='__main__': probe(Path(sys.argv[1]) if len(sys.argv)>1 else Path(__file__).resolve().parent/'preflight/deployment-identity')
