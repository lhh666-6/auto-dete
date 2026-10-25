"""Prepare/verify the v15 local scientific package; never modifies v13/v14.

Default: read-only preflight. After PDF and scientific validation:
  python scripts/package_v15.py --package --validated
  python scripts/package_v15.py --verify
Uses Python standard library plus pdfinfo on PATH or optional pypdf.
"""
from pathlib import Path, PurePosixPath
from io import BytesIO
import argparse
import hashlib
import json
import re
import shutil
import subprocess
import zipfile

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]
SUB = REPO / 'submission/ASE-2026-10-25-v15'
UPLOAD = ROOT / 'upload-package'
OLD = REPO / 'submission/ASE-2026-10-24-v14/ready-to-upload/ESM_3.zip'
STUDIES = (
    'X1-X2-reproduction.zip', 'Native-contract-reproduction.zip',
    'Feedback-sensitivity-reproduction.zip', 'Dynamic-recovery-reproduction.zip',
    'Correction-consumption-reproduction.zip', 'Agno-entrypoint-reproduction.zip',
    'Reviewed-instance-substitution-reproduction.zip',
)
PDFS = {'Manuscript.pdf': 'main.pdf', 'ESM_1.pdf': 'Online-Resource-1.pdf',
        'ESM_2.pdf': 'Online-Resource-2.pdf'}
PAYLOADS = tuple(PDFS) + ('Manuscript-source.zip', 'ESM_3.zip')
ROOT_SOURCE = ('.latexmkrc', 'build.py', 'main.tex', 'references.bib', 'sn-basic.bst',
               'sn-jnl.cls', 'README.txt', 'REPRODUCE-RECOVERY.md',
               'requirements-figures.txt', 'EXTERNAL-INPUTS.json', 'V15-CHANGELOG.md')
SOURCE_DIRS = ('figures', 'scripts', 'supplements', 'tables', 'qa', 'audit')
SUFFIXES = {'.tex', '.bib', '.bst', '.cls', '.pdf', '.py', '.json', '.md', '.txt',
            '.csv', '.tsv', '.svg', '.png', '.jpg', '.jpeg', '.yaml', '.yml'}
EXCLUDE = {'out', '__pycache__', '.git', 'upload-package', 'node_modules'}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def record(name, data):
    return {'path': name, 'bytes': len(data), 'sha256': digest(data)}


def json_bytes(obj):
    return (json.dumps(obj, indent=2, ensure_ascii=False) + '\n').encode('utf8')


def manifest(mapping, schema):
    return {'schema': schema, 'files': [record(k, v) for k, v in sorted(mapping.items())]}


def zip_bytes(mapping):
    stream = BytesIO()
    with zipfile.ZipFile(stream, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for name, data in sorted(mapping.items()):
            info = zipfile.ZipInfo(name, date_time=(2026, 10, 25, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            z.writestr(info, data)
    return stream.getvalue()


def open_zip(data):
    with zipfile.ZipFile(BytesIO(data)) as z:
        assert z.testzip() is None, 'ZIP CRC error'
        names = z.namelist()
        assert len(names) == len(set(names)), 'duplicate ZIP members'
        for name in names:
            p = PurePosixPath(name)
            assert not p.is_absolute() and '..' not in p.parts and '\\' not in name, name
        return {name: z.read(name) for name in names if not name.endswith('/')}


def verify_manifest(obj, members):
    expected = {r['path']: r for r in obj['files']}
    assert set(expected) == set(members), 'manifest member set differs'
    for name, data in members.items():
        assert expected[name] == record(name, data), f'hash/size differs: {name}'


def source_files():
    files = {name: (ROOT / name).read_bytes() for name in ROOT_SOURCE}
    for directory in SOURCE_DIRS:
        for p in sorted((ROOT / directory).rglob('*')):
            rel = p.relative_to(ROOT)
            if p.is_file() and not set(rel.parts) & EXCLUDE and p.suffix.lower() in SUFFIXES:
                # Only current v15 audit outputs are admitted, never inherited freezes.
                if directory == 'audit' and any(x.startswith('inherited-') for x in rel.parts):
                    continue
                files[rel.as_posix()] = p.read_bytes()
    return files


def dependencies(files, entry):
    """Resolve local TeX dependencies recursively; standard TeX classes stay external."""
    result = set()
    def resolve(parent, target, suffixes, local_required=True):
        base = PurePosixPath(parent).parent / target
        # Normalize relative paths without permitting archive escape.
        parts = []
        for part in base.parts:
            if part == '..':
                assert parts, f'dependency escapes archive: {target}'
                parts.pop()
            elif part != '.':
                parts.append(part)
        name = '/'.join(parts)
        for candidate in [name] + [name + suffix for suffix in suffixes]:
            if candidate in files:
                visit(candidate)
                return
        assert not local_required, f'missing dependency of {parent}: {target}'
    def visit(name):
        if name in result:
            return
        result.add(name)
        if not name.endswith('.tex'):
            return
        text = re.sub(r'(?<!\\)%[^\n]*', '', files[name].decode('utf8'))
        for command, target in re.findall(
                r'\\(input|include|includegraphics|bibliography|bibliographystyle|documentclass)'
                r'(?:\[[^\]]*\])?\{([^}]+)\}', text):
            extensions = {'input': ['.tex'], 'include': ['.tex'],
                          'includegraphics': ['.pdf', '.png', '.jpg'],
                          'bibliography': ['.bib'], 'bibliographystyle': ['.bst'],
                          'documentclass': ['.cls']}[command]
            for item in target.split(','):
                resolve(name, item, extensions,
                        command not in {'documentclass', 'bibliographystyle'}
                        or item in {'sn-jnl', 'sn-basic'})
    visit(entry)
    return result


def pages(path):
    pdfinfo = shutil.which('pdfinfo')
    if pdfinfo:
        output = subprocess.check_output([pdfinfo, str(path)], text=True, encoding='utf8', errors='replace')
        match = re.search(r'^Pages:\s+(\d+)', output, re.M)
        assert match, f'pdfinfo could not count pages: {path}'
        return int(match.group(1))
    try:
        from pypdf import PdfReader
    except ImportError as exc:
        raise RuntimeError('Install pypdf or put pdfinfo on PATH for runtime page counts') from exc
    return len(PdfReader(path).pages)


def inputs(require_pdfs=False):
    files = source_files()
    for entry in ('main.tex', 'supplements/online-resource-1/main.tex',
                  'supplements/online-resource-2/main.tex'):
        dependencies(files, entry)
    old = open_zip(OLD.read_bytes())
    studies = {name: old[name] for name in STUDIES}
    for data in studies.values():
        open_zip(data)
    count = {}
    if require_pdfs:
        for required in ('qa/observation_witnesses_v15.py',
                         'qa/test_observation_equality_v15.py',
                         'qa/upstream/observation_witnesses.py',
                         'audit/observation-equality-v15.md',
                         'audit/observation-equality-v15.json'):
            assert required in files, f'current checker/test/audit missing: {required}'
        for dest, src in PDFS.items():
            assert (ROOT / src).is_file(), f'PDF not built: {src}'
            count[dest] = pages(ROOT / src)
        assert (ROOT / 'out/main.bbl').is_file(), 'build manuscript before packaging (main.bbl missing)'
    return files, studies, count


def package():
    files, studies, count = inputs(True)
    # Only the five scientific payloads belong here; correspondence is authored separately.
    for directory in (UPLOAD, SUB / 'ready-to-upload'):
        directory.mkdir(parents=True, exist_ok=True)
        unknown = {p.name for p in directory.iterdir()} - set(PAYLOADS) - {'FILES.json'}
        assert not unknown, f'unexpected files in {directory}: {sorted(unknown)}'
    source_manifest = manifest(files, 'ase-v15-source-1')
    (ROOT / 'SOURCE-MANIFEST.json').write_bytes(json_bytes(source_manifest))
    full = {'Manuscript-sources/' + name: data for name, data in files.items()}
    full['Manuscript-sources/SOURCE-MANIFEST.json'] = json_bytes(source_manifest)
    full_zip = zip_bytes(full)
    main_names = dependencies(files, 'main.tex')
    # sn-jnl selects sn-basic internally from the documentclass option, so the
    # style is a required dependency even without an explicit bibliographystyle.
    main_names.update({'sn-jnl.cls', 'sn-basic.bst'})
    main = {name: files[name] for name in main_names}
    main['main.bbl'] = (ROOT / 'out/main.bbl').read_bytes()
    main['.latexmkrc'] = files['.latexmkrc']
    main['README.md'] = (
        '# v15 manuscript source\n\nCompile main.tex with pdfLaTeX and BibTeX. '
        'There is one main.tex at archive root. Full three-document sources, QA and '
        'analysis scripts are in ESM_3.zip / Manuscript-sources.zip.\n').encode()
    main['SOURCE-MANIFEST.json'] = json_bytes(manifest(main, 'ase-v15-main-source-1'))
    esm = dict(studies)
    esm['Manuscript-sources.zip'] = full_zip
    esm['README.md'] = (
        '# Online Resource 3 — v15 local revision\n\n'
        'Manuscript-sources.zip contains all three document sources, figures, analysis '
        'scripts, corrected observation checker and tests, and current v15 audit reports. '
        'Extract it and read Manuscript-sources/README.txt.\n\n'
        'The seven named study archives are byte-identical members of v14 ESM_3.zip; '
        'no experimental data were recollected or rewritten. Each retains its own guide. '
        'For the SDK studies begin with START-HERE.md and verify_offline.py. '
        'The v15 checker correction is separate from historical experiment freezes.\n\n'
        'MANIFEST.json inventories every other member; it deliberately excludes itself.\n').encode('utf8')
    esm['MANIFEST.json'] = json_bytes(manifest(esm, 'ase-v15-esm3-1'))
    payload = {name: (ROOT / src).read_bytes() for name, src in PDFS.items()}
    payload['Manuscript-source.zip'] = zip_bytes(main)
    payload['ESM_3.zip'] = zip_bytes(esm)
    file_manifest = manifest(payload, 'ase-v15-upload-1')
    file_manifest.update({'status': 'local revision; not a publication or submission', 'pages': count})
    for directory in (UPLOAD, SUB / 'ready-to-upload'):
        for name, data in payload.items():
            (directory / name).write_bytes(data)
    (UPLOAD / 'FILES.json').write_bytes(json_bytes(file_manifest))
    (SUB / 'FILES.json').write_bytes(json_bytes(file_manifest))
    freeze_files = dict(files)
    for name in ('SOURCE-MANIFEST.json', *PDFS.values()):
        freeze_files[name] = (ROOT / name).read_bytes()
    for name in (*PAYLOADS, 'FILES.json'):
        freeze_files['upload-package/' + name] = (UPLOAD / name).read_bytes()
    freeze = manifest(freeze_files, 'ase-v15-freeze-1')
    freeze.update({'status': 'local revision; no remote tag asserted',
                   'base_revision': '2026-10-24-ase-framing-v14',
                   'pages': count, 'validation_acknowledged': True,
                   'historical_studies': [record(k, v) for k, v in studies.items()],
                   'historical_esm3_sha256': digest(OLD.read_bytes()),
                   'hash_scope': 'Paths relative to this revision; excludes this freeze file itself.'})
    (ROOT / 'FINAL-FREEZE-v15.json').write_bytes(json_bytes(freeze))
    verify()


def verify():
    files, studies, count = inputs(True)
    freeze = json.loads((ROOT / 'FINAL-FREEZE-v15.json').read_text(encoding='utf8'))
    for row in freeze['files']:
        assert row == record(row['path'], (ROOT / row['path']).read_bytes()), row['path']
    assert freeze['pages'] == count, 'page counts changed'
    assert freeze['historical_esm3_sha256'] == digest(OLD.read_bytes())
    source = json.loads((ROOT / 'SOURCE-MANIFEST.json').read_text(encoding='utf8'))
    verify_manifest(source, files)
    payload = {name: (UPLOAD / name).read_bytes() for name in PAYLOADS}
    fm = json.loads((UPLOAD / 'FILES.json').read_text(encoding='utf8'))
    verify_manifest(fm, payload)
    assert fm['pages'] == count
    assert (SUB / 'FILES.json').read_bytes() == (UPLOAD / 'FILES.json').read_bytes()
    for name, data in payload.items():
        assert (SUB / 'ready-to-upload' / name).read_bytes() == data, name
    for dest, src in PDFS.items():
        assert payload[dest] == (ROOT / src).read_bytes(), dest
    main = open_zip(payload['Manuscript-source.zip'])
    mm = json.loads(main.pop('SOURCE-MANIFEST.json'))
    verify_manifest(mm, main)
    assert [k for k in main if PurePosixPath(k).name == 'main.tex'] == ['main.tex']
    dependencies(main, 'main.tex')
    for name in ('sn-jnl.cls', 'sn-basic.bst'):
        assert main[name] == files[name], f'implicit class/style dependency differs: {name}'
    for name in dependencies(files, 'main.tex'):
        assert main[name] == files[name], name
    assert main['main.bbl'] == (ROOT / 'out/main.bbl').read_bytes()
    esm = open_zip(payload['ESM_3.zip'])
    em = json.loads(esm.pop('MANIFEST.json'))
    verify_manifest(em, esm)
    for name, data in studies.items():
        assert esm[name] == data, f'historical archive changed: {name}'
        open_zip(esm[name])
    full = open_zip(esm['Manuscript-sources.zip'])
    prefix = 'Manuscript-sources/'
    assert all(name.startswith(prefix) for name in full)
    full = {name[len(prefix):]: data for name, data in full.items()}
    sm = json.loads(full.pop('SOURCE-MANIFEST.json'))
    verify_manifest(sm, full)
    assert full == files, 'full sources no longer match current source tree'
    print(json.dumps({'status': 'PASS', 'payloads': len(payload), 'pages': count,
                      'source_files': len(files), 'unchanged_study_archives': len(studies),
                      'freeze_sha256': digest((ROOT / 'FINAL-FREEZE-v15.json').read_bytes())}, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    action = parser.add_mutually_exclusive_group()
    action.add_argument('--package', action='store_true')
    action.add_argument('--verify', action='store_true')
    action.add_argument('--check', action='store_true', help='read-only preflight (default)')
    parser.add_argument('--validated', action='store_true',
                        help='acknowledge external PDF/scientific QA completed before freezing')
    args = parser.parse_args()
    if args.package:
        parser.error('--package requires --validated after completing PDF/scientific QA') if not args.validated else package()
    elif args.verify:
        verify()
    else:
        files, studies, _ = inputs()
        print(json.dumps({'status': 'PREFLIGHT PASS; no package written',
                          'source_files': len(files), 'historical_study_archives': len(studies),
                          'pdfs_present': {k: (ROOT / v).exists() for k, v in PDFS.items()}}, indent=2))
