"""Fetch a pinned official OpenTofu Windows executable; verify publisher SHA256SUMS."""
import hashlib
import io
import json
import urllib.request
import zipfile
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
VERSION = '1.13.1'
BASE = f'https://github.com/opentofu/opentofu/releases/download/v{VERSION}'
NAME = f'tofu_{VERSION}_windows_amd64.zip'


def get(url):
    request = urllib.request.Request(url, headers={'User-Agent': 'KAIS-offline-reproduction'})
    with urllib.request.urlopen(request, timeout=60) as response:
        return response.read()


def digest(data):
    return hashlib.sha256(data).hexdigest()


def main():
    manifest_path = HERE / 'software_sources.json'
    vendor = HERE / 'vendor'
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
        binary = vendor / 'tofu.exe'
        if binary.exists() and digest(binary.read_bytes()) == manifest['binary_sha256']:
            print('Pinned binary already present and verified.')
            return
        archive = get(manifest['archive_url'])
        if digest(archive) != manifest['archive_sha256']:
            raise RuntimeError('Pinned archive hash mismatch')
    else:
        vendor.mkdir(exist_ok=True)
        sums = get(f'{BASE}/tofu_{VERSION}_SHA256SUMS')
        expected = next(line.split()[0] for line in sums.decode().splitlines() if line.split()[-1] == NAME)
        archive = get(f'{BASE}/{NAME}')
        if digest(archive) != expected:
            raise RuntimeError('Publisher archive checksum mismatch')
        (vendor / 'SHA256SUMS').write_bytes(sums)
        manifest = {'version': VERSION, 'platform': 'windows_amd64',
                    'retrieved_at_utc': datetime.now(timezone.utc).isoformat(),
                    'archive_url': f'{BASE}/{NAME}', 'archive_sha256': expected,
                    'checksum_url': f'{BASE}/tofu_{VERSION}_SHA256SUMS',
                    'checksum_sha256': digest(sums),
                    'verification': 'Archive matched publisher SHA256SUMS over HTTPS; signature not verified.'}
    vendor.mkdir(exist_ok=True)
    (vendor / NAME).write_bytes(archive)
    with zipfile.ZipFile(io.BytesIO(archive)) as z:
        binary = z.read('tofu.exe')
        if 'binary_sha256' in manifest and digest(binary) != manifest['binary_sha256']:
            raise RuntimeError('Pinned executable checksum mismatch')
        (vendor / 'tofu.exe').write_bytes(binary)
        for name in ('LICENSE', 'LICENSE.txt'):
            if name in z.namelist():
                (vendor / name).write_bytes(z.read(name))
    manifest['binary_sha256'] = digest(binary)
    manifest['binary_path'] = 'vendor/tofu.exe'
    if not manifest_path.exists():
        manifest_path.write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'version': VERSION, 'archive_verified': True, 'binary_sha256': digest(binary)}))


if __name__ == '__main__':
    main()
