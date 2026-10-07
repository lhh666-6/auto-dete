"""Copy only verified new handoff artifacts to the existing managed checkout.

Run only after package_followup.py and final QA. Does not stage, commit, or push.
"""
from pathlib import Path
import hashlib
import json
import re
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]
DEST = Path(r'C:/Users/lenovo/.codex/worktrees/phase2-results-upload/auto-decte-paper')
BASE = '47b1168a36656ea998d36746a492eaaae512909d'
PAPER = 'revisions/2026-10-07-kais-followup'
ANALYSIS = 'research/phase2-followup-analysis-2026-10-07'
SENSITIVITY = 'research/phase2-followup-sensitivity-2026-10-07'
SNAPSHOT = 'research/phase2-results-snapshots/2026-10-07-complete'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=DEST, text=True).strip()
    assert head == BASE, 'Remote/base changed: review before copying'
    manifest = json.loads((ROOT / PAPER / 'EDITABLE-PACKAGE-MANIFEST.json').read_bytes())
    records = manifest['records']
    assert all(sha(ROOT / PAPER / r['path']) == r['sha256'] for r in records)
    paths = {f"{PAPER}/{r['path']}" for r in records}
    paths.update(f'{PAPER}/{name}' for name in (
        'EDITABLE-PACKAGE-MANIFEST.json', 'EDITABLE-PACKAGE-RECEIPT.json',
        'KAIS-editable-sources.zip'))
    for directory in (ANALYSIS, SENSITIVITY):
        base = ROOT / directory
        paths.update(p.relative_to(ROOT).as_posix() for p in base.iterdir()
                     if p.is_file() and (p.suffix == '.py' or p.name in ('README.md', '.gitattributes')))
        paths.update(p.relative_to(ROOT).as_posix() for p in (base / 'outputs').rglob('*') if p.is_file())
    paths.update(p.relative_to(ROOT).as_posix() for p in (ROOT / SNAPSHOT).iterdir() if p.is_file())
    paths.update(('research/publish_completed_recovery.py', 'research/publish_completed_handoff.py'))
    secret = re.compile(rb'(?:sk-[A-Za-z0-9_-]{20,}|gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{40,}|-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----)')
    for rel in sorted(paths):
        source, target = ROOT / rel, DEST / rel
        assert source.is_file()
        assert not target.exists() or source.read_bytes() == target.read_bytes(), 'Existing different target: ' + rel
        if source.suffix.lower() not in ('.pdf', '.png', '.zip', '.db', '.sqlite'):
            assert not secret.search(source.read_bytes()), 'Credential-shaped string: ' + rel
    for rel in sorted(paths):
        source, target = ROOT / rel, DEST / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        assert sha(source) == sha(target)
    readme = DEST / 'README.md'
    old = readme.read_text(encoding='utf-8-sig')
    marker = '# Correction-Aware Data Admission'
    assert marker in old
    new = (
        '> **完整补充实验与新版论文（2026-10-07）**：补采已于北京时间 17:46:49 完成，117 对 / 234 臂全部入账。'
        f' [新版正文（13 页）]({PAPER}/main.pdf) · [补充材料（28 页）]({PAPER}/supplement.pdf) · '
        f'[可编辑源码]({PAPER}/KAIS-editable-sources.zip) · [核验报告]({PAPER}/FOLLOWUP-VERIFICATION.md)。\n\n'
        '> 原始 512-arm 主分析完整保留；117 对补充 A 单独标明来源和分母，事后敏感性分析在 S13。'
        ' [完整结果与复算入口](PHASE2-RESULTS-LATEST.md)。以下 JIIS 入口是历史提交档案。\n\n'
        + old[old.index(marker):])
    readme.write_text(new, encoding='utf-8')
    latest = (
        '# Phase 2 completed supplementary evaluation\n\n'
        'Collection completed 2026-10-07 17:46:49 Asia/Shanghai. '
        'The original 512-arm analysis remains unchanged. Supplementary A comprises 117 pairs / 234 arms; '
        'all scheduled outcomes, including failures, are retained.\n\n'
        '| Evidence | Open |\n|---|---|\n'
        f'| Revised article and supplement | [{PAPER}/README.md]({PAPER}/README.md) |\n'
        f'| Complete raw supplementary archive and hashes | [{SNAPSHOT}/README.md]({SNAPSHOT}/README.md) |\n'
        f'| Independent scoring and native accounting | [{ANALYSIS}/README.md]({ANALYSIS}/README.md) |\n'
        f'| Explicit post hoc sensitivity | [{SENSITIVITY}/README.md]({SENSITIVITY}/README.md) |\n'
        '| Original complete inputs | [Pinned original archive](https://github.com/lhh666-6/auto-dete/blob/475e66f549613aaaaa62c2ec81ffdee483636c54/cloud-handoff/replication-package.zip) |\n\n'
        'Supplementary completion: context 114/117; bound 116/117. In the 15 G pairs, context admits all substituted instances; '
        'bound rejects and recovers all 15, through eight reviewed-candidate reuses and seven reauthorizations. '
        'Mean paired G cost is +1.6 calls and +17.9667 seconds. '
        'The completion contrast is exploratory and conditional on this selected later cohort, not a replacement primary estimator.\n\n'
        'The older 45-pair snapshot remains available under `research/phase2-results-snapshots/2026-10-07T021002Z/` '
        'as a historical intermediate artifact. It is superseded only for supplementary coverage. '
        'Follow the package READMEs for offline reproduction. No new provider calls are needed.\n')
    (DEST / 'PHASE2-RESULTS-LATEST.md').write_text(latest, encoding='utf-8')
    cloud = DEST / 'cloud-handoff/CLOUD-HANDOFF.md'
    prior = cloud.read_text(encoding='utf-8-sig')
    notice = ('> **Completed follow-up update (7 October 2026):** The active manuscript is now '
              '`revisions/2026-10-07-kais-followup/` (13-page article, 28-page supplement). '
              'See [current results and offline reproduction](../PHASE2-RESULTS-LATEST.md). '
              'The 117-pair supplementary collection is complete and independently scored. '
              'The instructions below document the earlier handoff; its partial-collection status and old editing target are historical.\n\n')
    cloud.write_text(notice + prior, encoding='utf-8')
    paths.update(('README.md', 'PHASE2-RESULTS-LATEST.md', 'cloud-handoff/CLOUD-HANDOFF.md'))
    receipt = {'base': BASE, 'branch': 'codex/phase2-formal-512-handoff',
               'file_count': len(paths), 'files': [{'path': p, 'sha256': sha(DEST / p)} for p in sorted(paths)]}
    out = ROOT / 'reviews/followup-publication-2026-10-07'
    out.mkdir(exist_ok=True)
    (out / 'copied-files.json').write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'base': BASE, 'copied_files': len(paths), 'all_hashes_match': True}))


if __name__ == '__main__':
    main()
