from pathlib import Path
import hashlib, json
r=Path(__file__).resolve().parent
m=json.loads((r/'RELEASE-MANIFEST.json').read_text(encoding='utf-8'))
actual={p.relative_to(r).as_posix() for p in r.rglob('*') if p.is_file() and p.relative_to(r).as_posix()!='RELEASE-MANIFEST.json'}
assert actual==set(m['files']), 'missing or extra files'
for name, entry in m['files'].items():
    assert hashlib.sha256((r/name).read_bytes()).hexdigest()==entry['sha256'], name
print('PASS:',len(actual),'files')
