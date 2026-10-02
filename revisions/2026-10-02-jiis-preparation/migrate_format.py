"""Create the complete-content JIIS format baseline without editing scientific files."""
from pathlib import Path
import re
import shutil
import zipfile
import hashlib
import json

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent / '2026-09-26-dke-manuscript'
DEST = HERE / 'format-baseline'
TEMP = Path('C:/Users/lenovo/AppData/Local/Temp')
DEST.mkdir(exist_ok=True)
for directory in ('sections', 'tables', 'figures'):
    if (DEST / directory).exists():
        raise RuntimeError(f'Refusing to overwrite an existing baseline: {directory}')
    shutil.copytree(SOURCE / directory, DEST / directory)
shutil.copy2(SOURCE / 'filtered.bib', DEST / 'filtered.bib')
shutil.copy2(SOURCE / 'supplement.pdf', HERE / 'supplement-dke-baseline.pdf')

archives = [
    (TEMP / 'JIIS-svjour3-official-20261002.zip', ['svjour3.cls', 'svglov3.clo']),
    (TEMP / 'SpringerNature-template-official-20261002.zip', ['sn-basic.bst']),
]
template_manifest = []
for archive, names in archives:
    with zipfile.ZipFile(archive) as zf:
        for name in names:
            candidates = [i for i in zf.infolist() if Path(i.filename).name == name]
            if len(candidates) != 1:
                raise RuntimeError(f'Expected exactly one {name}, got {len(candidates)}')
            data = zf.read(candidates[0])
            (DEST / name).write_bytes(data)
            template_manifest.append({'name': name, 'archive': archive.name,
                'sha256': hashlib.sha256(data).hexdigest()})

old = (SOURCE / 'main.tex').read_text(encoding='utf-8')
abstract = re.search(r'\\begin\{abstract\}\s*(.*?)\s*\\end\{abstract\}', old, re.S).group(1)
body = old[old.index(r'\input{sections/01-introduction}'):old.index(r'\bibliographystyle')]
title = re.search(r'\\title\{([^\n]+)\}', old).group(1)
main = r'''\RequirePackage{fix-cm}
\documentclass[smallcondensed,natbib,nospthms]{svjour3}
\usepackage[T1]{fontenc}
\usepackage[utf8]{inputenc}
\usepackage{lmodern}
\usepackage{amsmath,amssymb}
\usepackage{booktabs,enumitem,graphicx,flafter,microtype,multirow}
\usepackage[section]{placeins}
\usepackage{tabularx,xcolor,xurl}
\usepackage[hidelinks]{hyperref}
\usepackage[nameinlink,noabbrev]{cleveref}
\setcitestyle{numbers,square,comma}
\providecommand{\bibcommenthead}{}
\hypersetup{pdftitle={Correction-Aware Data Admission},pdfauthor={Liang Hanghao; Xuan Wentao; Chen Qile; Peng Peng},pdfsubject={Data integrity, candidate-bound authorization, and field-level provenance}}
\setlength{\emergencystretch}{2em}
\newcommand{\system}{\textsc{Auto-Decte}}
\newcommand{\code}[1]{\nolinkurl{#1}}
\newcommand{\eqc}{\mathrel{=_{\mathrm{json}}}}
\newcommand{\neqc}{\mathrel{\neq_{\mathrm{json}}}}
\journalname{Journal of Intelligent Information Systems}
\begin{document}
\title{''' + title + r'''}
\titlerunning{Correction-Aware Data Admission}
\author{Liang Hanghao \and Xuan Wentao \and Chen Qile \and Peng Peng}
\authorrunning{Liang Hanghao et al.}
\institute{Liang Hanghao \and Xuan Wentao \and Chen Qile \and Peng Peng \at
College of Computer Science and Electronic Engineering, Hunan University, Lushan South Road, Yuelu District, Changsha 410082, China\\
\email{hnu16pp@hnu.edu.cn} (Peng Peng, corresponding author)}
\date{}
\maketitle
\begin{abstract}
''' + abstract + r'''
\keywords{data integrity \and data provenance \and human authorization \and AI-assisted data acquisition \and transactional admission \and relational verification}
\end{abstract}

''' + body + r'''
\bibliographystyle{sn-basic}
\bibliography{filtered}
\end{document}
'''
(DEST / 'main.tex').write_text(main, encoding='utf-8')
(DEST / '.latexmkrc').write_text("$pdf_mode = 1;\n$out_dir = 'out';\nEND { use File::Copy; copy(\"out/main.pdf\", \"main.pdf\") if -f \"out/main.pdf\"; }\n", encoding='utf-8')
(DEST / 'out').mkdir(exist_ok=True)
unchanged = []
for directory in ('sections', 'tables', 'figures'):
    for src in sorted((SOURCE / directory).rglob('*')):
        if src.is_file():
            rel = src.relative_to(SOURCE)
            assert src.read_bytes() == (DEST / rel).read_bytes(), rel
            unchanged.append({'path': rel.as_posix(), 'sha256': hashlib.sha256(src.read_bytes()).hexdigest()})
assert (SOURCE / 'filtered.bib').read_bytes() == (DEST / 'filtered.bib').read_bytes()
assert abstract in main and body in main
manifest = {'status': 'complete_content_format_baseline', 'source_commit': '57b8e68a3cddda2b2915d86b7f36c5258fb74d34',
    'documentclass': 'svjour3', 'format_option': 'smallcondensed', 'body_inputs_identical': True,
    'abstract_identical': True, 'bibliography_database_identical': True, 'unchanged_files': unchanged,
    'template_files': template_manifest,
    'template_source': 'https://media.springer.com/full/springer-instructions-for-authors-assets/zip/1633537_svjour3-Latex-package.zip',
    'bibliography_source': 'https://cms-resources.apps.public.k8s.springernature.io/springer-cms/rest/v1/content/18782940/data/v12'}
(HERE / 'format-migration-manifest.json').write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding='utf-8')
print(f'Created {DEST}; {len(unchanged)} copied scientific/assets files verified identical.')
