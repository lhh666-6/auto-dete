"""Export flat manuscript and supplement sources without touching frozen archives."""
from pathlib import Path
import hashlib
import json
import re
import shutil

HERE = Path(__file__).resolve().parent
SOURCE = HERE / 'final-source'
DEST = HERE / 'submission-files'
DEST.mkdir(exist_ok=True)
def export(root_name, directory):
    target = DEST / directory
    if target.exists():
        raise RuntimeError(f'Refusing to overwrite an existing export: {target}')
    target.mkdir()
    included = {}
    def visit(relative):
        if relative in included:
            return
        text = (SOURCE / relative).read_text(encoding='utf-8')
        included[relative] = text
        for item in re.findall(r'\\(?:input|include)\{([^}]+)\}', text):
            visit(item if item.endswith('.tex') else item + '.tex')
    visit(root_name)
    names = {name: name.replace('/', '-') for name in included}
    images = {}
    for text in included.values():
        for image in re.findall(r'\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}', text):
            images[image] = 'Fig1.pdf' if 'figure-1-' in image else 'Fig2.pdf'
    for relative, text in included.items():
        text = re.sub(r'(\\(?:input|include)\{)([^}]+)(\})',
            lambda m: m.group(1) + names[m.group(2) if m.group(2).endswith('.tex') else m.group(2)+'.tex'].removesuffix('.tex') + m.group(3), text)
        for old, new in images.items():
            text = text.replace('{' + old + '}', '{' + new + '}')
        (target / names[relative]).write_text(text, encoding='utf-8')
    for old, new in images.items():
        shutil.copy2(SOURCE / old, target / new)
    if root_name == 'main.tex':
        for name in ('filtered.bib', 'svjour3.cls', 'svglov3.clo', 'sn-basic.bst'):
            shutil.copy2(SOURCE / name, target / name)
        shutil.copy2(SOURCE / 'out/main.bbl', target / 'main.bbl')
    assert not any(p.is_dir() for p in target.iterdir())
    return names
maps = {'manuscript': export('main.tex', 'Manuscript-LaTeX'),
        'online_resource': export('ESM_1.tex', 'Online-Resource-LaTeX')}
for old, new in [('main.pdf','Manuscript.pdf'), ('ESM_1.pdf','ESM_1.pdf')]:
    shutil.copy2(SOURCE / old, DEST / new)
main = (SOURCE / 'main.tex').read_text(encoding='utf-8')
abstract = re.search(r'\\begin\{abstract\}\s*(.*?)\\keywords', main, re.S).group(1).strip()
title = re.search(r'\\title\{([^}]+)\}', main).group(1)
metadata = f'Title\n{title}\n\nAbstract\n{abstract}\n\nKeywords\ndata integrity; data provenance; human authorization; AI-assisted data acquisition; transactional admission; relational verification\n'
(DEST / 'submission-metadata.txt').write_text(metadata, encoding='utf-8')
letter = f'''2 October 2026

Dear Editors of the Journal of Intelligent Information Systems,

We submit our manuscript, "{title}", for consideration as a research article.

The paper studies how human-reviewed AI-derived information becomes authoritative operational data. A correction can authorize a value different from the machine proposal, while equal-valued candidates can remain distinct authorization targets. We specify an admission relation that retains the reviewed candidate and authorized correction, checks predecessor freshness, and commits a complete successor with field-level provenance.

The contribution is a formal data relation and its conditional failure-distinguishability characterization, supported by an executable realization and controlled implementation evidence. The exact-binding journal and relational reference agree on 165 corresponding cases; 15 equal-valued substitutions distinguish instance authorization from context approval. Scripted browser cases examine the review-to-confirmation boundary, and fixed workloads characterize enforcement and provenance-query costs.

This work addresses the integration of AI-derived information, human review, and persistent data management in intelligent information systems. Experiments use constructed histories, scripted review interactions, and fixed workloads. Code, inputs, and execution records are publicly available, and Online Resource 1 provides the detailed evidence and reproduction guide.

The manuscript is not under consideration by another journal. Funding, competing interests, author contributions, historical annotation ethics, and AI-assisted preparation are disclosed in the manuscript.

Sincerely,
Peng Peng
Corresponding author, on behalf of the authors
College of Computer Science and Electronic Engineering
Hunan University, Changsha, China
hnu16pp@hnu.edu.cn
'''
(DEST / 'cover-letter.txt').write_text(letter, encoding='utf-8')
(DEST / 'README-上传说明.md').write_text('''# JIIS 投稿文件

- 主文：Manuscript.pdf；可编辑源码取 Manuscript-LaTeX 内的文件。该目录内部没有子文件夹，上传时选择其中的文件，主文件为 main.tex。
- 补充材料：ESM_1.pdf，类别选 Supplementary Information / Online Resource。其可编辑源码独立保存在 Online-Resource-LaTeX；不要把 ESM_1.tex 混入主文编译。
- 投稿信：cover-letter.txt，可直接粘贴到投稿系统的 Cover Letter 栏。
- 标题、摘要、关键词：submission-metadata.txt。

不上传本说明、内部审计报告、检查日志或历史投稿包。无需上传摘要中的构造示例作为新数据。在线系统生成的 PDF 仍需作者检查；贡献、利益冲突等界面字段按正文如实填写。
''', encoding='utf-8')
(HERE / 'submission-source-map.json').write_text(json.dumps(maps, indent=2), encoding='utf-8')
manifest = {p.relative_to(DEST).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(DEST.rglob('*')) if p.is_file()}
(HERE / 'submission-files-manifest.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
print(f'Exported {len(manifest)} files; two separately flattened source sets.')
