"""Archive a complete supplementary cohort without altering any original attempt."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import re
import zipfile

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'research/agent-policy-phase2-quota-recovery-2026-10-07'
DEST = ROOT / 'research/phase2-results-snapshots/2026-10-07-complete'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def main():
    ledger_raw = (SOURCE / 'results/collection-status.json').read_bytes()
    ledger = json.loads(ledger_raw)
    manifest = json.loads((SOURCE / 'recovery-manifest.json').read_bytes())
    expected = {p['pair_id'] for p in manifest['pairs']}
    assert ledger['status'] == 'COMPLETE'
    assert ledger['freeze_id'] == manifest['freeze_id']
    assert len(expected) == manifest['planned_pairs'] == 117
    assert set(ledger['pairs']) == expected
    assert all(p['status'] == 'terminal' for p in ledger['pairs'].values())
    DEST.mkdir(parents=True, exist_ok=False)
    files = [p for p in (SOURCE / 'results').rglob('*') if p.is_file() and p.suffix not in ('.lock', '.pyc')]
    files += [p for p in SOURCE.iterdir() if p.is_file() and p.suffix in ('.py', '.json', '.sha256', '.md', '.log', '.ps1', '.cmd')]
    secret = re.compile(rb'(?:sk-[A-Za-z0-9_-]{20,}|gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{40,}|-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----)')
    records = []
    archive = DEST / 'quota-recovery-complete.zip'
    with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        for path in sorted(files):
            raw = path.read_bytes()
            rel = path.relative_to(ROOT).as_posix()
            if path.suffix not in ('.sqlite', '.db', '.pdf', '.png', '.zip'):
                assert not secret.search(raw), 'Credential-shaped text: ' + rel
            z.writestr(rel, raw)
            records.append({'path': rel, 'bytes': len(raw), 'sha256': sha(raw)})
        z.writestr('SNAPSHOT-MEMBERS.json', json.dumps(records, indent=2))
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None
        assert all(sha(z.read(r['path'])) == r['sha256'] for r in records)
    assert (SOURCE / 'results/collection-status.json').read_bytes() == ledger_raw
    assert all(sha((ROOT / r['path']).read_bytes()) == r['sha256'] for r in records)
    report = {
        'snapshot_utc': datetime.now(timezone.utc).isoformat(),
        'collection_finished_utc': ledger['updated_utc'],
        'freeze_id': manifest['freeze_id'],
        'status': 'COMPLETE', 'planned_pairs': 117, 'planned_arms': 234,
        'terminal_pairs': len(ledger['pairs']),
        'all_attempts_retained': True,
        'attempts': sum(len(p['attempts']) for p in ledger['pairs'].values()),
        'archive': archive.name, 'bytes': archive.stat().st_size,
        'sha256': sha(archive.read_bytes()), 'verified_members': len(records),
        'crc_check': 'PASS', 'all_member_sha256': 'PASS',
        'source_unchanged_during_archive': True, 'credential_pattern_scan': 'PASS',
        'role': 'Complete separately frozen deployment-A follow-up; original 512-arm analysis retained.',
        'scoring': 'See research/phase2-followup-analysis-2026-10-07; this receipt certifies archived inputs, not independently scored outcomes.'
    }
    (DEST / 'archive-receipt.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    (DEST / 'source-collection-status.json').write_bytes(ledger_raw)
    print(json.dumps(report, indent=2), flush=True)


if __name__ == '__main__':
    main()
