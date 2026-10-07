"""Package the final manuscript overlay with byte-verified members; no model calls."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import re
import zipfile

ROOT = Path(__file__).resolve().parent
TOP = (
    '.gitattributes', '.latexmkrc', 'main.tex', 'main.pdf', 'supplement.tex',
    'supplement.pdf', 'build.ps1', 'build.sh', 'README.md', 'FOLLOWUP-README.md',
    'FOLLOWUP-REVISION-NOTES.md', 'FOLLOWUP-CONTENT-AUDIT.md',
    'FOLLOWUP-FIGURE-QA.md', 'FOLLOWUP-PDF-QA.md', 'FOLLOWUP-VERIFICATION.md',
    'QA-RECEIPT.json', 'WORK-PLAN.md', 'make_revision_figures.py',
    'make_followup_figure.py', 'make_figures.py', 'derive_results.py',
    'verify_evidence.py', 'render_review.py', 'package_followup.py',
    'FINAL-POLISH-NOTES.md', 'FINAL-POLISH-CITATION-AUDIT.md',
    'FINAL-POLISH-FIGURE-QA.md', 'FINAL-POLISH-PDF-QA.md',
    'FINAL-POLISH-VERIFICATION.md',
    '.research/literature_matrix.md', 'REVIEW-CLOSURE-COMPARISON.md',
    'REVIEW-CLOSURE-NOTES.md',
)


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def main():
    files = [ROOT / p for p in TOP]
    assert all(p.is_file() for p in files), 'Missing required final deliverable'
    for directory in ('evidence', 'baseline', 'figures'):
        files.extend(p for p in (ROOT / directory).rglob('*') if p.is_file()
                     and '__pycache__' not in p.parts and p.suffix != '.pyc')
    files = sorted(set(files))
    secret = re.compile(rb'(?:sk-[A-Za-z0-9_-]{20,}|gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{40,}|-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----)')
    records = []
    for path in files:
        raw = path.read_bytes()
        if path.suffix.lower() not in ('.pdf', '.png', '.zip', '.db', '.sqlite'):
            assert not secret.search(raw), 'Credential-shaped string in ' + path.name
        records.append({'path': path.relative_to(ROOT).as_posix(),
                        'bytes': len(raw), 'sha256': digest(raw)})
    manifest = {'created_utc': datetime.now(timezone.utc).isoformat(),
                'role': 'Manuscript overlay and derived evidence; raw inputs are separate pinned archives.',
                'file_count': len(records), 'records': records}
    mp = ROOT / 'EDITABLE-PACKAGE-MANIFEST.json'
    mp.write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
    archive = ROOT / 'KAIS-editable-sources.zip'
    with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        for p in files:
            z.write(p, p.relative_to(ROOT).as_posix())
        z.write(mp, mp.name)
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None
        assert len(z.namelist()) == len(records) + 1
        for r in records:
            assert digest(z.read(r['path'])) == r['sha256']
        assert z.read(mp.name) == mp.read_bytes()
    receipt = {'archive': archive.name, 'bytes': archive.stat().st_size,
               'sha256': digest(archive.read_bytes()), 'verified_members': len(records) + 1,
               'crc_check': 'PASS', 'all_member_sha256': 'PASS',
               'credential_pattern_scan': 'PASS'}
    (ROOT / 'EDITABLE-PACKAGE-RECEIPT.json').write_text(
        json.dumps(receipt, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(receipt, indent=2))


if __name__ == '__main__':
    main()
