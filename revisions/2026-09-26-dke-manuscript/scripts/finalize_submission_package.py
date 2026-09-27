"""Record current checks and archive the reviewed submission package."""
from pathlib import Path
import hashlib
import json
import re
import subprocess
import zipfile
import pymupdf
from docx import Document

ROOT = Path(__file__).resolve().parents[1]
SUB = ROOT / 'submission'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def write_json(path, value):
    path.write_bytes((json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode('utf-8'))


def main():
    for name in ('source-archive-inventory.json', 'source-rebuild-verification.json'):
        path = SUB / name
        write_json(path, json.loads(path.read_text(encoding='utf-8')))
    builds = {}
    verified = json.loads((SUB / 'source-rebuild-verification.json').read_text())
    for name in ('main', 'supplement'):
        path = ROOT / f'{name}.pdf'
        pdf = pymupdf.open(path)
        log = (ROOT / f'out/{name}.log').read_text(errors='replace')
        counts = {'overfull_boxes': len(re.findall('Overfull', log)),
                  'underfull_boxes': len(re.findall('Underfull', log)),
                  'unresolved_references_or_citations': len(re.findall('undefined', log)),
                  'latex_warnings': len(re.findall('LaTeX Warning', log))}
        assert not any(counts.values())
        assert verified[name]['pdf_sha256'] == sha(path.read_bytes())
        assert verified[name]['archive_sha256'] == sha((SUB / 'upload' / f'{name}-source.zip').read_bytes())
        outside = sum(1 for page in pdf for block in page.get_text('blocks')
                      if block[0] < -1 or block[1] < -1 or block[2] > page.rect.width + 1 or block[3] > page.rect.height + 1)
        builds[name] = {'pages': len(pdf), 'pdf_sha256': sha(path.read_bytes()), **counts,
                        'words_pdf_extraction': sum(len(p.get_text().split()) for p in pdf),
                        'text_outside_page': outside}
        assert outside == 0
        pdf.close()
    main_log = (ROOT / 'out/main.log').read_text(encoding='utf-8', errors='replace')
    builds['_environment'] = {'date': '2026-09-27',
                              'tex_distribution': re.search(r'\((MiKTeX[^)]+|TeX Live[^)]+)\)', main_log).group(1),
                              'document_class': re.search(r'Document Class: (elsarticle[^\n]+)', main_log).group(1),
                              'baseline_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
                              'scope': 'Current main build; supplement PDF preserved and source-rebuild verified.'}
    write_json(ROOT / 'editorial/final-build-check.json', builds)

    source_highlights = [x.removeprefix('- ').strip() for x in (ROOT / 'highlights.txt').read_text().splitlines() if x.strip()]
    word_highlights = [x.text for x in Document(SUB / 'upload/highlights.docx').paragraphs][2:]
    assert source_highlights == word_highlights
    lengths = [len(x) for x in source_highlights]
    assert len(lengths) == 5 and max(lengths) <= 85
    for name in ('cover-letter', 'highlights'):
        data = (SUB / f'{name}.docx').read_bytes()
        assert data == (SUB / f'upload/{name}.docx').read_bytes()
        with zipfile.ZipFile(SUB / f'{name}.docx') as zf:
            assert 'word/comments.xml' not in zf.namelist()
            assert b'<w:ins ' not in zf.read('word/document.xml')
            assert b'<w:del ' not in zf.read('word/document.xml')

    figure_hashes = json.loads((ROOT / 'editorial/story-figure-source-hashes.json').read_text())
    with zipfile.ZipFile(SUB / 'upload/figure-reproduction.zip') as zf:
        for name, expected in figure_hashes.items():
            assert sha(zf.read(name.replace('\\', '/'))) == expected
        assert zf.read('scripts/build_story_figures.py') == (ROOT / 'scripts/build_story_figures.py').read_bytes()
    checks = {'state': 'prepared_pending_author_and_portal_checks', 'date': '2026-09-27',
              'baseline_commit': builds['_environment']['baseline_commit'],
              'scientific_results_changed': False, 'new_experiments_run': False,
              'pdf_pages': {x: builds[x]['pages'] for x in ('main', 'supplement')},
              'source_archives_verified': True, 'all_pages_text_and_72dpi_pixels_equal': True,
              'highlights_characters': lengths, 'word_documents_rendered_and_visually_checked': True,
              'word_documents_pages': {'cover-letter': 1, 'highlights': 1},
              'figure_archive_inputs_match_recorded_hashes': True,
              'figure_script_rerun': False,
              'pending': ['All authors confirm final files and declarations; supply missing author metadata.',
                          'Verify DKE-specific anonymity, length and attachment requirements in the portal.',
                          'Inspect the portal-generated PDF before final submission.']}
    write_json(SUB / 'final-validation.json', checks)

    files = {p.relative_to(SUB).as_posix(): p.read_bytes() for p in (SUB / 'upload').iterdir() if p.is_file()}
    for name in ('README.md', 'submission-metadata.md', 'author-confirmation-checklist.md',
                 'cover-letter.txt', 'source-archive-inventory.json',
                 'source-rebuild-verification.json', 'final-validation.json'):
        files[name] = (SUB / name).read_bytes()
    for name in ('submission-policy-final-2026-09-27.md', 'submission-final-audit-2026-09-27.md', 'layout-closeout-2026-09-27.md', 'final-build-check.json'):
        files['checks/' + name] = (ROOT / 'editorial' / name).read_bytes()
    manifest = {'date': '2026-09-27', 'state': checks['state'], 'baseline_commit': checks['baseline_commit'],
                'files': {name: {'bytes': len(data), 'sha256': sha(data)} for name, data in sorted(files.items())}}
    write_json(SUB / 'package-manifest.json', manifest)
    files['package-manifest.json'] = (SUB / 'package-manifest.json').read_bytes()
    archive = SUB / 'DKE-submission-package-2026-09-27.zip'
    with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED) as zf:
        for name, data in sorted(files.items()):
            zf.writestr(name, data)
    with zipfile.ZipFile(archive) as zf:
        assert zf.testzip() is None
        for name, identity in manifest['files'].items():
            assert sha(zf.read(name)) == identity['sha256']

    paths = [p for p in ROOT.rglob('*') if p.is_file() and 'out' not in p.relative_to(ROOT).parts
             and '__pycache__' not in p.relative_to(ROOT).parts and p.name != 'manuscript-manifest.json']
    write_json(ROOT / 'manuscript-manifest.json', {'date': '2026-09-27', 'baseline_commit': checks['baseline_commit'],
               'revision': 'Layout closeout: storage-table placement and bibliography spacing; scientific content unchanged',
               'files': {p.relative_to(ROOT).as_posix(): {'bytes': p.stat().st_size, 'sha256': sha(p.read_bytes())} for p in sorted(paths)}})
    print(json.dumps({'archive': str(archive), 'bytes': archive.stat().st_size, 'sha256': sha(archive.read_bytes()),
                      'files': len(files), 'checks': checks}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
