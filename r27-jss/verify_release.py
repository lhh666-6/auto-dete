from pathlib import Path
import hashlib, json

r = Path(__file__).resolve().parent
m = json.loads((r / 'RELEASE-MANIFEST.json').read_text(encoding='utf-8'))


def delivered(p):
    rel = p.relative_to(r)
    if rel.as_posix() == 'RELEASE-MANIFEST.json':
        return False
    if '__pycache__' in rel.parts or p.suffix == '.pyc':
        return False  # runtime bytecode is not part of the sealed release
    return True


actual = {p.relative_to(r).as_posix() for p in r.rglob('*') if p.is_file() and delivered(p)}
expected = set(m['files'])
if actual != expected:
    missing = sorted(expected - actual)
    extra = sorted(actual - expected)
    raise SystemExit(f'FAIL: {len(missing)} missing (e.g. {missing[:5]}), {len(extra)} extra (e.g. {extra[:5]})')
for name, entry in m['files'].items():
    digest = hashlib.sha256((r / name).read_bytes()).hexdigest()
    if digest != entry['sha256']:
        raise SystemExit(f'FAIL: hash mismatch for {name}')
print('PASS:', len(actual), 'files')
