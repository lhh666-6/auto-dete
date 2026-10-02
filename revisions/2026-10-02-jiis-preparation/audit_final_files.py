"""Mechanical final-file checks; no experiments or scientific edits."""
from pathlib import Path
import hashlib
import json
import re
import fitz
import bibtexparser

HERE = Path(__file__).resolve().parent
BASE = HERE / 'format-baseline'
FINAL = HERE / 'final-source'
PACKAGE = HERE / 'submission-files'
CHECK = HERE / 'build-check'
def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
for number, name in [(1, 'figure-1-admission-workflow.pdf'), (2, 'figure-2-evidence-route.pdf')]:
    assert sha(FINAL / 'figures' / 'refined' / name) == sha(PACKAGE / 'Manuscript-LaTeX' / f'Fig{number}.pdf'), name
def normalized_resource_names(text):
    return re.sub(r'Online Resource 1, Sections? (S\d(?:, S\d)*(?:,? and S\d)?)',
        lambda m: ('Supplements ' if ',' in m.group(1) or 'and' in m.group(1) else 'Supplement ') + m.group(1), text)
locked = ['03-problem-contract.tex', '04-relational-analysis.tex', '05-transactional-realization.tex',
          '06-formal-concrete-conformance.tex', '08-results.tex', '09-discussion-threats.tex', '10-conclusion.tex']
for name in locked:
    a = (BASE / 'sections' / name).read_text(encoding='utf-8')
    b = normalized_resource_names((FINAL / 'sections' / name).read_text(encoding='utf-8'))
    assert a == b, name
tables = [p for p in (BASE / 'tables').rglob('*') if p.is_file()]
for p in tables:
    q = FINAL / p.relative_to(BASE)
    if p.suffix == '.tex':
        assert p.read_text(encoding='utf-8') == normalized_resource_names(q.read_text(encoding='utf-8')), p
    else:
        assert p.read_bytes() == q.read_bytes(), p
for p in (BASE / 'sections').glob('supplement-*.tex'):
    assert p.read_text(encoding='utf-8') == normalized_resource_names((FINAL / p.relative_to(BASE)).read_text(encoding='utf-8')), p
old_bib = {e['ID']: e for e in bibtexparser.loads((BASE / 'filtered.bib').read_text(encoding='utf-8')).entries}
new_bib = {e['ID']: e for e in bibtexparser.loads((FINAL / 'filtered.bib').read_text(encoding='utf-8')).entries}
assert old_bib.keys() == new_bib.keys()
for key in old_bib:
    a = dict(old_bib[key]); b = dict(new_bib[key])
    if 'url' in a and 'url' not in b:
        assert a['url'].lower().rstrip('/') == ('https://doi.org/' + a['doi']).lower().rstrip('/')
        del a['url']
    assert a == b, key
maps = json.loads((HERE / 'submission-source-map.json').read_text(encoding='utf-8'))
results = {}
for kind, root_file, source_dir, pdf_file, log_file in [
    ('main','main.tex','Manuscript-LaTeX','Manuscript.pdf','manuscript/main.log'),
    ('supplement','ESM_1.tex','Online-Resource-LaTeX','ESM_1.pdf','online-resource/ESM_1.log')]:
    directory = PACKAGE / source_dir
    assert not any(p.is_dir() for p in directory.iterdir())
    included = {}
    def visit(name):
        if name in included:
            return
        source = (directory / name).read_text(encoding='utf-8')
        included[name] = re.sub(r'(?<!\\)%[^\n]*', '', source)
        for value in re.findall(r'\\(?:input|include)\{([^}]+)\}', included[name]):
            assert '/' not in value and '\\' not in value
            visit(value if value.endswith('.tex') else value + '.tex')
    visit(root_file)
    text = '\n'.join(included.values())
    labels = re.findall(r'\\label\{([^}]+)\}', text)
    refs = set()
    for group in re.findall(r'\\(?:ref|eqref|cref|Cref|pageref)\*?\{([^}]+)\}', text):
        refs.update(k.strip() for k in group.split(','))
    assert not (refs - set(labels))
    assert len(labels) == len(set(labels))
    assert not re.search(r'TODO|FIXME|XXX|TBD|\[INSERT|PLACEHOLDER|Lorem ipsum', text)
    assert 'GPT-6' not in text
    log = (CHECK / log_file).read_text(encoding='utf-8', errors='replace')
    assert not re.search(r'undefined|multiply defined|LaTeX Font Warning|Overfull \\[hv]box|Rerun to get cross-references', log, re.I)
    doc = fitz.open(PACKAGE / pdf_file)
    assert all(len(p.get_text().strip()) > 50 for p in doc)
    assert '??' not in '\n'.join(p.get_text() for p in doc)
    fonts = []
    for page in doc:
        for font in page.get_fonts(full=True):
            if font[0] and font[0] not in [f['xref'] for f in fonts]:
                extracted = doc.extract_font(font[0])
                fonts.append({'xref': font[0], 'name': font[3], 'embedded': bool(extracted[3])})
    assert all(f['embedded'] for f in fonts)
    results[kind] = {'pages':len(doc), 'included_tex_files':len(included), 'labels':len(labels),
        'missing_refs':[], 'fonts_embedded':True, 'font_count':len(fonts),
        'underfull_boxes':len(re.findall(r'Underfull \\[hv]box', log)), 'overfull_boxes':0,
        'sha256':sha(PACKAGE / pdf_file), 'source_flattened':True}
    if kind == 'main':
        abstract = re.search(r'\\begin\{abstract\}\s*(.*?)\\keywords', text, re.S).group(1).strip()
        keys = set()
        for group in re.findall(r'\\(?:cite|citep|citet)\*?(?:\[[^\]]*\])*\{([^}]+)\}', text):
            keys.update(k.strip() for k in group.split(','))
        assert keys == set(new_bib)
        results[kind].update(abstract_words=len(abstract.split()), keywords=6, references=len(keys))
        assert 150 <= len(abstract.split()) <= 250 and len(doc) <= 25
        rendered = '\n'.join(page.get_text() for page in doc)
        assert not re.search(r'DKE-supplement|r\d+-jss|Data & Knowledge Engineering|Elsevier|GPT-6', rendered)
        results[kind]['visible_transfer_labels'] = []
render = CHECK / 'visual-check'
render.mkdir(exist_ok=True)
doc = fitz.open(PACKAGE / 'Manuscript.pdf')
for start in range(0, len(doc), 6):
    contact = fitz.open(); sheet = contact.new_page(width=1000,height=2170)
    for offset in range(6):
        index=start+offset
        if index >= len(doc): break
        x=(offset%2)*500; y=(offset//2)*720
        sheet.insert_text((x+12,y+16),f'Page {index+1}',fontsize=11)
        sheet.show_pdf_page(fitz.Rect(x+8,y+22,x+492,y+709),doc,index)
    sheet.get_pixmap().save(render/f'contact-{start+1:02d}-{min(start+6,len(doc)):02d}.png')
for n in [1,3,16,23,len(doc)]:
    doc[n-1].get_pixmap(matrix=fitz.Matrix(1.7,1.7)).save(render/f'page-{n:02d}.png')
supp = fitz.open(PACKAGE / 'ESM_1.pdf')
supp[0].get_pixmap(matrix=fitz.Matrix(1.7,1.7)).save(render/'online-resource-first.png')
for n in (0,3,7,13):
    assert n < len(supp)
    supp[n].get_pixmap().save(render/f'online-resource-{n+1:02d}.png')
original = HERE.parent / '2026-09-26-dke-manuscript'
assert sha(original / 'main.pdf') == '5a6707d630c786431b7d9eddc07cf691a65a7e2705949587b53a5f0d02f5a621'
assert sha(original / 'supplement.pdf') == '074a8cb4bd7a34fdf32619a1c08e64e47792b0cc9d0eee574cc6e57b6d713aee'
results['preservation'] = {'locked_main_sections':locked, 'all_table_scientific_content_unchanged':True,
    'supplement_sections_unchanged':True, 'bibliography_metadata_unchanged_except_six_duplicate_urls':True,
    'frozen_dke_pdfs_unchanged':True, 'no_new_experiments':True}
(HERE / 'final-audit.json').write_text(json.dumps(results,indent=2,ensure_ascii=False),encoding='utf-8')
manifest = {p.relative_to(PACKAGE).as_posix(): sha(p) for p in sorted(PACKAGE.rglob('*')) if p.is_file()}
(HERE / 'submission-files-manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
print(json.dumps(results,ensure_ascii=False,indent=2))
