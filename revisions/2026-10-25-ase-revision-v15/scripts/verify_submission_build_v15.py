"""Clean-extraction build/readback of the prepared v15 source packages.

Runs only local TeX and standard-library regression code. Requires PyMuPDF
for exact page-text and 72-dpi rendering comparison; never recollects studies.
"""
from pathlib import Path
from io import BytesIO
import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
import zipfile
import pymupdf

ROOT = Path(__file__).resolve().parents[1]


def sha(data):
    return hashlib.sha256(data).hexdigest()


def extract(data, destination):
    with zipfile.ZipFile(BytesIO(data)) as zf:
        for name in zf.namelist():
            target = (destination / name).resolve()
            target.relative_to(destination.resolve())
        assert zf.testzip() is None
        zf.extractall(destination)


def command(args, cwd):
    result = subprocess.run(args, cwd=cwd, capture_output=True)
    if result.returncode:
        raise RuntimeError(result.stdout.decode(errors='replace')[-5000:] + result.stderr.decode(errors='replace')[-3000:])


def compare(original, rebuilt):
    with pymupdf.open(original) as a, pymupdf.open(rebuilt) as b:
        assert len(a) == len(b), (original, len(a), len(b))
        assert all(x.get_text() == y.get_text() for x, y in zip(a, b)), f'text differs: {original}'
        assert all(x.get_pixmap().samples == y.get_pixmap().samples for x, y in zip(a, b)), f'render differs: {original}'
        return {'pages': len(a), 'supplied_pdf_sha256': sha(original.read_bytes()),
                'all_page_text_equal': True, 'all_page_pixels_equal_at_72dpi': True}


def main(output):
    # Keep extracted files outside the scientific revision and preserve all freezes.
    scratch_parent = ROOT.parents[2] / 'tmp/v15-package-rebuild'
    scratch_parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=scratch_parent, prefix='verify-') as work:
        work = Path(work)
        single = work / 'single'
        full = work / 'full'
        single.mkdir()
        full.mkdir()
        single_bytes = (ROOT / 'upload-package/Manuscript-source.zip').read_bytes()
        extract(single_bytes, single)
        with zipfile.ZipFile(ROOT / 'upload-package/ESM_3.zip') as esm:
            extract(esm.read('Manuscript-sources.zip'), full)
        source = full / 'Manuscript-sources'
        command(['pdflatex', '-interaction=nonstopmode', '-halt-on-error', 'main.tex'], single)
        command(['bibtex', 'main'], single)
        for _ in range(5):
            command(['pdflatex', '-interaction=nonstopmode', '-halt-on-error', 'main.tex'], single)
            log = (single / 'main.log').read_text(errors='replace')
            if not re.search(r'Label\(s\) may have changed|There were undefined references|(?:Reference|Citation).*undefined|Rerun to get', log):
                break
        assert not re.search(r'Overfull|undefined|LaTeX Warning', log), 'single-source build needs attention'
        checks = {'single_entry_manuscript': compare(ROOT / 'main.pdf', single / 'main.pdf')}
        command([sys.executable, '-B', 'build.py'], source)
        for name, log_path in (
                ('main.pdf', 'out/main.log'),
                ('Online-Resource-1.pdf', 'supplements/online-resource-1/out/main.log'),
                ('Online-Resource-2.pdf', 'supplements/online-resource-2/out/main.log')):
            log = (source / log_path).read_text(errors='replace')
            assert not re.search(r'Overfull|undefined|LaTeX Warning', log), log_path
            checks[name] = compare(ROOT / name, source / name)
        receipt = work / 'extracted-regression.json'
        command([sys.executable, '-B', str(source / 'qa/test_observation_equality_v15.py'),
                 '--output', str(receipt)], work)
        regression = json.loads(receipt.read_text(encoding='utf-8'))
        assert regression['status'] == 'PASS'
        # These identities cover every compilation or checker input. Audit additions
        # can subsequently be packaged without a self-referential archive hash.
        identities = {}
        for path in source.rglob('*'):
            rel = path.relative_to(source)
            if (path.is_file() and not set(rel.parts) & {'out', 'audit', '__pycache__'}
                    and path.suffix in {'.tex', '.bib', '.bst', '.cls', '.py', '.pdf'}
                    and rel.as_posix() not in {'main.pdf', 'Online-Resource-1.pdf', 'Online-Resource-2.pdf'}):
                original = ROOT / rel
                assert path.read_bytes() == original.read_bytes(), str(rel)
                identities[rel.as_posix()] = sha(path.read_bytes())
        result = {'date': '2026-10-25', 'status': 'PASS', 'checks': checks,
                  'new_equality_regressions': regression['new_regressions']['count'],
                  'upstream_fixture_sha256': regression['upstream_raw_sha256'],
                  'preserved_checks': regression['preserved_checks'],
                  'source_input_sha256': identities,
                  'scope': 'Clean extracted source builds, all-page text/render identity, and extracted offline checker regression. No hosted experiments, SDK recollection or complete Alloy rerun. Underfull spacing warnings are assessed visually rather than treated as missing content.'}
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_bytes((json.dumps(result, indent=2, ensure_ascii=False) + '\n').encode('utf-8'))
        print(json.dumps({'status': 'PASS', 'documents': checks, 'new_regressions': 38, 'receipt': str(output)}, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    main(parser.parse_args().output.resolve())
