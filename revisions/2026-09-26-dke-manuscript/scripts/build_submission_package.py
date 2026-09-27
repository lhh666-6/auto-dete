"""Build flat Editorial Manager source archives and verify clean rebuilds."""
from pathlib import Path
import argparse
import hashlib
import json
import re
import shutil
import subprocess
import tempfile
import zipfile
import pymupdf

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'submission'
UPLOAD = OUT / 'upload'
PATTERN = re.compile(r'\\(input|includegraphics)(\[[^\]]*\])?\{([^}]+)\}')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def flat_archive(document):
    files = {}
    original_names = {}

    def collect(path):
        path = path.resolve()
        path.relative_to(ROOT.resolve())
        name = path.name
        if name in original_names:
            assert original_names[name] == path, f'Flat-name collision: {name}'
            return name
        assert path.is_file(), path
        original_names[name] = path
        if path.suffix == '.tex':
            content = path.read_text(encoding='utf-8-sig')

            def replace(match):
                target = ROOT / match[3]
                if match[1] == 'input' and not target.suffix:
                    target = target.with_suffix('.tex')
                dependency = collect(target)
                return '\\' + match[1] + (match[2] or '') + '{' + dependency + '}'

            files[name] = PATTERN.sub(replace, content).encode('utf-8')
        else:
            files[name] = path.read_bytes()
        return name

    collect(ROOT / f'{document}.tex')
    if document == 'main':
        collect(ROOT / 'filtered.bib')
        collect(ROOT / 'out/main.bbl')
    files['SOURCE-README.txt'] = (
        f'Top-level document: {document}.tex\n'
        'Engine: pdfLaTeX. Class: elsarticle (standard Elsevier TeX package).\n'
        'All compilation dependencies in this archive use flat filenames.\n'
        'Compile with pdflatex, run bibtex main for the main document, then\n'
        'run pdflatex three more times to settle citations and references.\n'
        'Select only this archive for this document in Editorial Manager.\n'
        'Do not combine main and supplement as one review PDF.\n'
        'Figure-generation scripts and CSVs retain their original layout in\n'
        'the separate figure-reproduction.zip; they are not TeX dependencies.\n'
    ).encode('ascii')
    destination = UPLOAD / f'{document}-source.zip'
    with zipfile.ZipFile(destination, 'w', zipfile.ZIP_DEFLATED) as zf:
        for name, content in sorted(files.items()):
            assert '/' not in name and '\\' not in name
            zf.writestr(name, content)
    return {'entries': sorted(files), 'sha256': sha(destination)}


def build():
    UPLOAD.mkdir(parents=True, exist_ok=True)
    for source, target in ((ROOT / 'main.pdf', 'manuscript.pdf'),
                           (ROOT / 'supplement.pdf', 'supplementary-material.pdf'),
                           (OUT / 'cover-letter.docx', 'cover-letter.docx'),
                           (OUT / 'highlights.docx', 'highlights.docx')):
        shutil.copy2(source, UPLOAD / target)
    archives = {document: flat_archive(document) for document in ('main', 'supplement')}
    for path in sorted((ROOT / 'figures/refined').glob('*.pdf')):
        shutil.copy2(path, UPLOAD / path.name)
    figure_archive()
    (OUT / 'source-archive-inventory.json').write_text(json.dumps(archives, indent=2) + '\n', encoding='utf-8')
    return archives


def figure_archive():
    with zipfile.ZipFile(UPLOAD / 'figure-reproduction.zip', 'w', zipfile.ZIP_DEFLATED) as zf:
        paths = [ROOT / 'scripts/build_story_figures.py']
        paths += sorted((ROOT / 'tables').rglob('*.tex'))
        paths += sorted((ROOT / 'tables').rglob('*.csv'))
        for path in paths:
            zf.write(path, path.relative_to(ROOT).as_posix())
        zf.writestr('README.txt', 'Requires Python and Matplotlib 3.10.8.\nRun python scripts/build_story_figures.py from this directory.\nAll inputs are archived tables and CSV summaries; no experiments or model calls run.\nOutputs: figures/refined and editorial/story-figure-source-hashes.json.\n')
        zf.writestr('editorial/.gitkeep', '')
    return {'figure_archive_sha256': sha(UPLOAD / 'figure-reproduction.zip')}


def verify():
    verification = {}
    scratch = ROOT / 'out/submission-source-verification'
    scratch.mkdir(parents=True, exist_ok=True)
    for document in ('main', 'supplement'):
        with tempfile.TemporaryDirectory(prefix=document + '-', dir=scratch) as temporary:
            target = Path(temporary)
            with zipfile.ZipFile(UPLOAD / f'{document}-source.zip') as zf:
                assert all('/' not in x and '\\' not in x for x in zf.namelist())
                zf.extractall(target)
            commands = [['pdflatex', '-interaction=nonstopmode', '-halt-on-error', document + '.tex']]
            if document == 'main':
                commands.append(['bibtex', 'main'])
            commands.extend([commands[0]] * 3)
            for command in commands:
                result = subprocess.run(command, cwd=target, capture_output=True)
                if result.returncode:
                    raise RuntimeError(result.stdout.decode(errors='replace')[-6000:])
            log = (target / f'{document}.log').read_text(errors='replace')
            issues = [line for line in log.splitlines() if re.search(r'LaTeX Warning|Overfull|Underfull|undefined', line)]
            assert not issues, issues
            original = pymupdf.open(ROOT / f'{document}.pdf')
            rebuilt = pymupdf.open(target / f'{document}.pdf')
            assert len(original) == len(rebuilt)
            text_match = all(a.get_text() == b.get_text() for a, b in zip(original, rebuilt))
            pixel_match = all(a.get_pixmap().samples == b.get_pixmap().samples for a, b in zip(original, rebuilt))
            assert text_match and pixel_match, f'{document} differs from submission PDF'
            verification[document] = {'archive_sha256': sha(UPLOAD / f'{document}-source.zip'),
                                      'pdf_sha256': sha(ROOT / f'{document}.pdf'),
                                      'pages': len(original), 'clean_directory_build': True,
                                      'warnings': issues, 'all_pages_text_equal': text_match,
                                      'all_pages_pixels_equal_at_72dpi': pixel_match}
            original.close()
            rebuilt.close()
    (OUT / 'source-rebuild-verification.json').write_text(json.dumps(verification, indent=2) + '\n', encoding='utf-8')
    return verification


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--verify', action='store_true')
    parser.add_argument('--figures-only', action='store_true')
    args = parser.parse_args()
    print(json.dumps(figure_archive() if args.figures_only else verify() if args.verify else build(), indent=2))
