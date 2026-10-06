"""Formal collection is opt-in and refuses an unready or changed freeze."""
import argparse, hashlib, json, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'src'))

def verify_freeze(root=ROOT):
    manifest=json.loads((root/'frozen-formal/master-sha256.json').read_text(encoding='utf-8'))
    errors=[]
    for name,expected in manifest['files'].items():
        path=root/name
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest()!=expected: errors.append(name)
    if errors: raise ValueError('FREEZE_HASH_MISMATCH: '+','.join(errors))
    actual=hashlib.sha256((root/'frozen-formal/master-sha256.json').read_bytes()).hexdigest()
    expected=(root/'frozen-formal/master-sha256.txt').read_text().split()[0]
    if actual!=expected: raise ValueError('MASTER_HASH_MISMATCH')
    return actual

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--verify-only',action='store_true')
    parser.add_argument('--author-start',default='')
    parser.add_argument('--resume',action='store_true')
    parser.add_argument('--output',type=Path,default=ROOT/'formal-results')
    args=parser.parse_args()
    print('master_sha256='+verify_freeze(),flush=True)
    if not args.verify_only:
        from phase2.orchestrator import collect
        result=collect(ROOT/'frozen-formal',args.output,args.author_start,args.resume)
        print(json.dumps({'status':result['status'],'terminal_pairs':result['terminal_pairs']}))
