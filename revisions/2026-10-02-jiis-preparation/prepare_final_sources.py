"""Apply limited JIIS framing and submission-format changes to a separate copy."""
from pathlib import Path
import json
import re
import shutil

HERE = Path(__file__).resolve().parent
BASE = HERE / 'format-baseline'
OLD = HERE.parent / '2026-09-26-dke-manuscript'
DEST = HERE / 'final-source'
if DEST.exists():
    raise RuntimeError('Refusing to overwrite the final-source directory.')
DEST.mkdir()
for directory in ('sections', 'tables', 'figures'):
    shutil.copytree(BASE / directory, DEST / directory)
for name in ('main.tex', 'filtered.bib', 'svjour3.cls', 'svglov3.clo', 'sn-basic.bst', '.gitignore'):
    shutil.copy2(BASE / name, DEST / name)
(DEST / 'out').mkdir()
changes = []
def edit(relative, old, new, reason):
    path = DEST / relative
    text = path.read_text(encoding='utf-8')
    assert old in text, (relative, old)
    path.write_text(text.replace(old, new), encoding='utf-8')
    changes.append({'file': relative, 'reason': reason, 'old': old, 'new': new})

edit('main.tex', 'Identical authoritative values can arise from different machine proposals and human authorizations.',
     'Human-reviewed AI-derived updates in intelligent information systems can produce identical authoritative values despite different machine proposals and authorizations.',
     'State the JIIS application context in the abstract without changing the distinction.')
edit('sections/01-introduction.tex',
     'AI-assisted acquisition produces machine proposals that people review before database admission.',
     'Intelligent information systems combine machine-produced information with persistent operational records. In document intelligence and human-in-the-loop data curation, reviewers may authorize a correction before a proposed value enters those records.',
     'Make the potential application and AI/database handoff explicit.')
edit('sections/01-introduction.tex',
     'We specify which information distinguishes correction-aware admission histories and how to enforce those distinctions through the relation',
     'We specify a correction-aware admission relation for this review-to-state boundary and characterize the information that distinguishes its failure families. The relation connects',
     'Keep the relation and conditional characterization as the principal contribution.')
edit('sections/07-evaluation-protocol.tex',
     'E1 tests why exact candidate binding matters when values and retained context agree.',
     'E1--E3 provide controlled implementation evidence through constructed histories, scripted review interactions, and fixed workloads. E1 tests why exact candidate binding matters when values and retained context agree.',
     'State the evidence identity positively without suggesting production deployment.')
for p in DEST.rglob('*.tex'):
    text = p.read_text(encoding='utf-8')
    if ' (GPT-6)' in text:
        text = text.replace(' (GPT-6)', '')
        changes.append({'file': p.relative_to(DEST).as_posix(), 'reason': 'Remove an unverified model-version attribution; retain OpenAI Codex disclosure.'})
    text = re.sub(r'\bSupplements? (S\d(?:, S\d)*(?:,? and S\d)?)',
                  lambda m: 'Online Resource 1, ' + ('Sections ' if 'and' in m.group(1) or ',' in m.group(1) else 'Section ') + m.group(1), text)
    p.write_text(text, encoding='utf-8')

edit('sections/declarations.tex', r'\section*{Declarations}', r'\section*{Statements and Declarations}', 'Use the journal-specific declaration heading.')
edit('sections/declarations.tex', r'\subsection*{Declaration of competing interest}', r'\subsection*{Competing interests}', 'Use the Springer heading.')
edit('sections/declarations.tex', r'\subsection*{Declaration of generative AI and AI-assisted technologies in the manuscript preparation process}', r'\subsection*{AI-assisted preparation}', 'Shorten the inherited Elsevier-style heading without reducing disclosure.')
edit('sections/declarations.tex',
     r'\url{https://github.com/lhh666-6/auto-dete/tree/2645e5e18c900ea91c9c980e44195dc71e410432/DKE-supplement}',
     r'\href{https://github.com/lhh666-6/auto-dete/tree/2645e5e18c900ea91c9c980e44195dc71e410432/DKE-supplement}{the frozen experiment archive}',
     'Use a neutral visible link label; preserve the verified commit and actual directory.')
edit('sections/declarations.tex',
     r'\url{https://github.com/lhh666-6/auto-dete/tree/r31-jss-2026-09-13/latest}',
     r'\href{https://github.com/lhh666-6/auto-dete/tree/c6d512843c905cab6d8521dd8c914f7fb26d85ae/latest}{the frozen formal and historical evidence archive}',
     'Replace the journal-specific tag with its verified exact commit.')
edit('sections/declarations.tex', r'tag \code{r21-jss-2026-09-07-v8}',
     r'commit \code{abcdb817835a2c0953e5a26d854f34d99347dc6a}',
     'Keep the original v8 evidence identity while displaying its exact commit.')
edit('sections/declarations.tex',
     'The authors used DeepSeek, OpenAI Codex, and Claude to assist with code development, analysis and evidence checks, literature organization, and manuscript and figure preparation. OpenAI image generation (model/version unavailable) supplied Figure 1\'s design prototype. The authors reviewed and edited the outputs, verified sources and results, and take full responsibility for this article.',
     'The authors used DeepSeek, OpenAI Codex, and Claude for code, analysis checks, literature organization, and manuscript and diagram preparation. OpenAI image generation supplied a design prototype for Figure 1; its model/version was not recorded. The final diagrams were rendered from scripts. The authors verified sources, results, and figure content and take responsibility for the article.',
     'Retain actual uses, prototype provenance, and human accountability in a concise statement.')
decl = DEST / 'sections/declarations.tex'
with decl.open('a', encoding='utf-8') as stream:
    stream.write('\n\\subsection*{Supplementary information}\n\nOnline Resource 1 contains the artifact guide, formal observation and projection details, worked correction example, full workload grids, and historical integration and validity records.\n')

# Keep whole names on one line, without changing name spellings or order.
edit('main.tex', r'\author{Liang Hanghao \and Xuan Wentao \and Chen Qile \and Peng Peng}',
     r'\author{\mbox{Liang Hanghao} \and \mbox{Xuan Wentao} \and \mbox{Chen Qile} \and \mbox{Peng Peng}}',
     'Prevent a line break inside an author name.')
edit('sections/01-introduction.tex', r'\begin{figure*}[t]', r'\begin{figure}[!htbp]', 'Use a regular single-column float to avoid the nearly empty page before Figure 1.')
edit('sections/01-introduction.tex', r'\end{figure*}', r'\end{figure}', 'Match the regular figure environment.')

supp = (OLD / 'supplement.tex').read_text(encoding='utf-8')
supp = supp.replace(r'\documentclass[preprint,12pt,authoryear]{elsarticle}', r'\documentclass[11pt,a4paper]{article}' + '\n' + r'\usepackage[margin=25mm]{geometry}')
supp = supp.replace(r'\journal{Data \& Knowledge Engineering}', '')
supp = supp.replace(r'{\Large Supplementary material}', r'{\Large Online Resource 1}')
supp = supp.replace(r'\par\smallskip{\small College of Computer Science and Electronic Engineering, Hunan University, Changsha, China}',
    r'\par\smallskip{\small Journal of Intelligent Information Systems\\College of Computer Science and Electronic Engineering, Hunan University, Changsha, China\\Corresponding author: Peng Peng, \texttt{hnu16pp@hnu.edu.cn}}')
(DEST / 'ESM_1.tex').write_text(supp, encoding='utf-8')
changes.append({'file': 'ESM_1.tex', 'reason': 'Repackage the complete original supplement with JIIS metadata and corresponding-author email; retain all scientific content and section identities.'})
(DEST / '.latexmkrc').write_text('$pdf_mode = 1;\n$out_dir = "out";\nEND { use File::Copy; for my $name ("main", "ESM_1") { copy("out/$name.pdf", "$name.pdf") if -f "out/$name.pdf"; } }\n', encoding='utf-8')
(HERE / 'final-cleanup-changes.json').write_text(json.dumps(changes, indent=2, ensure_ascii=False), encoding='utf-8')
print('Created limited-cleanup source:', DEST)
