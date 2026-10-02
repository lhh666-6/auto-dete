"""Verify format-only preservation and render the compiled baseline for inspection."""
from pathlib import Path
import hashlib
import json
import re
import fitz

HERE = Path(__file__).resolve().parent
OLD = HERE.parent / '2026-09-26-dke-manuscript'
NEW = HERE / 'format-baseline'
OUT = NEW / 'out'
def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
manifest = json.loads((HERE / 'format-migration-manifest.json').read_text(encoding='utf-8'))
for entry in manifest['unchanged_files']:
    assert digest(OLD / entry['path']) == digest(NEW / entry['path']) == entry['sha256'], entry['path']
assert digest(OLD / 'filtered.bib') == digest(NEW / 'filtered.bib')
for entry in manifest['template_files']:
    assert digest(NEW / entry['name']) == entry['sha256']
old_main = (OLD / 'main.tex').read_text(encoding='utf-8')
new_main = (NEW / 'main.tex').read_text(encoding='utf-8')
abstract_pattern = r'\\begin\{abstract\}\s*(.*?)\s*\\end\{abstract\}'
old_abs = re.search(abstract_pattern, old_main, re.S).group(1)
new_abs = re.search(abstract_pattern, new_main, re.S).group(1).split(r'\keywords')[0].strip()
assert old_abs == new_abs
def body(text):
    return text[text.index(r'\input{sections/01-introduction}'):text.index(r'\bibliographystyle')].strip()
assert body(old_main) == body(new_main)
included = {}
def visit(relative):
    p = NEW / relative
    if p in included:
        return
    text = p.read_text(encoding='utf-8')
    clean = re.sub(r'(?<!\\)%[^\n]*', '', text)
    included[p] = clean
    for child in re.findall(r'\\(?:input|include)\{([^}]+)\}', clean):
        visit(child if child.endswith('.tex') else child + '.tex')
visit('main.tex')
text = '\n'.join(included.values())
keys = set()
for group in re.findall(r'\\(?:cite|citep|citet|textcite|parencite|autocite)\*?(?:\[[^\]]*\])*\{([^}]+)\}', text):
    keys.update(k.strip() for k in group.split(','))
bibkeys = set(re.findall(r'@\w+\s*\{\s*([^,]+),', (NEW / 'filtered.bib').read_text(encoding='utf-8')))
labels = re.findall(r'\\label\{([^}]+)\}', text)
refs = set()
for group in re.findall(r'\\(?:ref|eqref|cref|Cref|pageref)\*?\{([^}]+)\}', text):
    refs.update(k.strip() for k in group.split(','))
missing_cites = sorted(keys - bibkeys)
missing_refs = sorted(refs - set(labels))
duplicates = sorted(k for k in set(labels) if labels.count(k) > 1)
assert not missing_cites and not missing_refs and not duplicates
log = (OUT / 'main.log').read_text(encoding='utf-8', errors='replace')
assert not re.search(r'undefined|multiply defined|LaTeX Font Warning|Overfull \\[hv]box', log, re.I)
lint_patterns = {
    'vertical_surgery': r'\\(?:vspace|vskip|enlargethispage|pagebreak|nopagebreak)\b',
    'semantic_linebreak': r'\\(?:section|subsection|subsubsection|paragraph|caption)\{[^}]*\\\\|\\(?:newline|linebreak)\b',
    'forced_floats': r'\\begin\{(?:figure|table)\}\[[!Hh]+\]|\\FloatBarrier',
    'shrink_to_fit': r'\\(?:resizebox|scalebox)\s*\{[^}]*\\textwidth|\\begin\{adjustbox\}[^\n]*width\s*=.*\\textwidth',
    'tiny_typography': r'\\(?:scriptsize|tiny)\b|\\setlength\{\\tabcolsep\}\{\s*-|\\renewcommand\{\\arraystretch\}\{0\.[0-8]',
    'overlap_positioning': r'\\(?:raisebox|llap|rlap|smash|hspace\*)\b|\\makebox\s*\[0pt\]',
    'absolute_width': r'\\begin\{minipage\}\{[0-9.]+cm\}|\\parbox\{[0-9.]+cm\}|\bp\{[0-9.]+cm\}',
}
lint = {name: [] for name in lint_patterns}
lint['label_before_caption'] = []
lint['spacing_conflict'] = []
for p, source in included.items():
    for name, pattern in lint_patterns.items():
        for m in re.finditer(pattern, source):
            lint[name].append({'file': p.relative_to(NEW).as_posix(), 'line': source[:m.start()].count('\n') + 1})
    for m in re.finditer(r'\\begin\{(figure|table)\}.*?\\end\{\1\}', source, re.S):
        b = m.group()
        if r'\label{' in b and r'\caption{' in b and b.index(r'\label{') < b.index(r'\caption{'):
            lint['label_before_caption'].append(p.relative_to(NEW).as_posix())
    if re.search(r'\\(?:onehalfspacing|doublespacing|setstretch)', source) and re.search(r'\\vspace\*?\{\s*-|\\\\\[\s*-', source):
        lint['spacing_conflict'].append(p.relative_to(NEW).as_posix())
pdf = fitz.open(NEW / 'main.pdf')
assert all(len(page.get_text().strip()) > 50 for page in pdf)
render_dir = OUT / 'visual-check'
render_dir.mkdir(exist_ok=True)
for start in range(0, len(pdf), 6):
    contact = fitz.open()
    sheet = contact.new_page(width=1000, height=2170)
    for offset in range(6):
        index = start + offset
        if index >= len(pdf):
            break
        x = (offset % 2) * 500
        y = (offset // 2) * 720
        sheet.insert_text((x + 12, y + 16), f'Page {index + 1}', fontsize=11)
        sheet.show_pdf_page(fitz.Rect(x + 8, y + 22, x + 492, y + 709), pdf, index)
    sheet.get_pixmap().save(render_dir / f'contact-{start + 1:02d}-{min(start + 6, len(pdf)):02d}.png')
feature_pages = {}
for name, phrase in {'figure1': 'Fig. 1', 'figure2': 'Fig. 2', 'proposition': 'Proposition 1', 'references': 'References'}.items():
    feature_pages[name] = [i + 1 for i, p in enumerate(pdf) if phrase in p.get_text()]
selected = {1, len(pdf), 16} | set(feature_pages['figure1'][:1]) | set(feature_pages['figure2'][:1])
for number in sorted(selected):
    page = pdf[number - 1]
    page.get_pixmap(matrix=fitz.Matrix(2, 2)).save(render_dir / f'page-{number:02d}.png')
chk = (OUT / 'chktex.txt').read_text(encoding='utf-8', errors='replace')
warning_codes = sorted(set(re.findall(r'Warning (\d+)', chk)), key=int)
result = {
    'pages': len(pdf), 'original_pages': len(fitz.open(OLD / 'main.pdf')),
    'abstract_words': len(old_abs.split()), 'keywords': 6,
    'byte_identical_scientific_assets': len(manifest['unchanged_files']),
    'abstract_identical': True, 'body_inputs_identical': True, 'bibliography_identical': True,
    'included_tex_files': len(included), 'cited_keys': len(keys), 'bibliography_entries': len(bibkeys),
    'missing_citations': missing_cites, 'unused_bibliography_keys': sorted(bibkeys - keys),
    'missing_references': missing_refs, 'duplicate_labels': duplicates,
    'underfull_boxes': len(re.findall(r'Underfull \\[hv]box', log)), 'overfull_boxes': 0,
    'font_substitution_warnings': 0, 'source_lint': lint, 'chktex_warning_codes': warning_codes,
    'feature_pages': feature_pages, 'main_pdf_sha256': digest(NEW / 'main.pdf'),
    'frozen_main_pdf_sha256': digest(OLD / 'main.pdf'),
    'frozen_supplement_pdf_sha256': digest(OLD / 'supplement.pdf'),
}
(HERE / 'format-audit.json').write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding='utf-8')
print(json.dumps(result, ensure_ascii=False, indent=2))
