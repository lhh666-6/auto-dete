#!/usr/bin/env python3
"""Read-only SHA-256 verification of the complete materialized submission tree."""
import hashlib
import json
from pathlib import Path


def verify(root):
    root = Path(root).resolve()
    manifest = json.loads((root / 'FREEZE-MANIFEST-r30.json').read_text(encoding='utf-8'))
    errors = []
    for name, entry in manifest['files'].items():
        path = (root / name).resolve()
        if not path.is_relative_to(root):
            errors.append(f'path outside archive: {name}')
            continue
        if not path.is_file():
            errors.append(f'missing: {name}')
            continue
        with path.open('rb') as stream:
            head = stream.read(128)
            if head.startswith(b'version https://git-lfs.github.com/spec/v1'):
                errors.append(f'LFS pointer, run git lfs pull in a clone: {name}')
                continue
            stream.seek(0)
            digest = hashlib.file_digest(stream, 'sha256').hexdigest()
        if path.stat().st_size != entry['bytes'] or digest != entry['sha256']:
            errors.append(f'digest or size mismatch: {name}')
    return manifest, errors


if __name__ == '__main__':
    manifest, errors = verify(Path(__file__).parent)
    for error in errors:
        print(error)
    if not errors:
        print(f"Full freeze verified: {len(manifest['files'])} files; {manifest['revision']}")
        print('Unlisted working files are not part of the freeze. The manifest excludes itself.')
    raise SystemExit(bool(errors))
