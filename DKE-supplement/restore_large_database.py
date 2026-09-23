"""Restore the losslessly compressed database and verify its original SHA-256."""
import gzip
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
RELATIVE = 'results/e3/storage/storage-100000/full.db'

def checksum(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()

def main():
    manifest = json.loads((ROOT / 'artifact-manifest.json').read_text(encoding='utf-8'))
    entries = {k.replace('\\', '/'): v for k, v in manifest['files'].items()}
    expected = entries[RELATIVE]
    target = ROOT / RELATIVE
    if target.exists():
        if checksum(target) != expected:
            raise RuntimeError('Existing database differs; refusing to overwrite it.')
        print('Database already present; original SHA-256 verified.')
        return
    temporary = target.with_suffix('.db.restoring')
    with gzip.open(str(target) + '.gz', 'rb') as source, temporary.open('xb') as destination:
        for block in iter(lambda: source.read(1024 * 1024), b''):
            destination.write(block)
    if checksum(temporary) != expected:
        raise RuntimeError('Decompressed bytes do not match the original artifact manifest.')
    if target.exists():
        raise RuntimeError('Destination appeared during restoration; refusing to overwrite.')
    temporary.rename(target)
    print('Restored database; original SHA-256 verified:', expected)

if __name__ == '__main__':
    main()
