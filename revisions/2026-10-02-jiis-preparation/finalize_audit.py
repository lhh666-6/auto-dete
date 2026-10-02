"""Close the limited JIIS preparation audit; never run experiments or modify frozen sources."""
from pathlib import Path
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parent
audit = json.loads((ROOT / 'final-audit.json').read_text(encoding='utf-8'))
external = json.loads((ROOT / 'external-source-audit.json').read_text(encoding='utf-8'))
manifest = json.loads((ROOT / 'submission-files-manifest.json').read_text(encoding='utf-8'))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
for name, expected in manifest.items():
    assert sha(ROOT / 'submission-files' / name) == expected, name
for source, expected in json.loads((ROOT / 'figure-source-hashes.json').read_text()).items():
    assert sha(ROOT.parent / '2026-09-26-dke-manuscript' / source) == expected, source
assert len(external['references']) == 26
assert all(r['http_status'] == 200 for r in external['references'])
assert all(link['accessible'] for link in external['artifact_links'])
doi_refs = [r for r in external['references'] if r['status'] == 'metadata_matches']
assert len(doi_refs) == 15
for r in doi_refs:
    norm = lambda text: re.sub(r'[^a-z0-9]', '', text.lower())
    assert r.get('title_similarity', 0) > .8 or norm(r['title']) == norm(r['registered_title']), r['key']
base = ROOT / 'format-baseline'
final = ROOT / 'final-source'
rq = lambda p: re.findall(r'\\item\[RQ\d+\].*', p.read_text(encoding='utf-8'))
assert rq(base / 'sections/07-evaluation-protocol.tex') == rq(final / 'sections/07-evaluation-protocol.tex')
assert len(rq(final / 'sections/07-evaluation-protocol.tex')) == 3
old_supp = (ROOT.parent / '2026-09-26-dke-manuscript/supplement.tex').read_text(encoding='utf-8')
new_supp = (final / 'ESM_1.tex').read_text(encoding='utf-8')
# The supplementary header/preamble changed; its scientific body is retained.
start = 'This supplement documents'
assert old_supp[old_supp.index(start):] == new_supp[new_supp.index(start):]
for folder in ['Manuscript-LaTeX', 'Online-Resource-LaTeX']:
    assert not any(p.is_dir() for p in (ROOT / 'submission-files' / folder).iterdir())
assert not any(p.name == 'texput.log' for p in (ROOT / 'submission-files').rglob('*'))

def write_report(relative, text):
    path = ROOT / relative
    if path.exists():
        if relative == 'reviews/pre-submission-report/2026-10-02.md':
            path = path.with_name('2026-10-02-final.md')
            assert not path.exists(), f'Preserve existing report: {path}'
        elif relative != 'reviews/INDEX.md':
            return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding='utf-8')

write_report('reviews/pre-submission-report/2026-10-02.md', f'''# JIIS final preparation audit — 2 October 2026

**Verdict: technical submission checks PASS.** No remaining blocker was identified within this limited format, framing, reference-access, and preservation audit. The main manuscript is **{audit['main']['pages']} pages**, exactly at the journal ceiling. This is preparation for author submission, not evidence of acceptance or a new full scientific peer review.

## Scope and hard requirements

The untouched Springer migration was 24 pages; the final cleanup is 25 pages. The abstract has **{audit['main']['abstract_words']} words**, with **6 keywords** and **26 cited references**. The official requirements are 25 pages including references, figures, and tables; LaTeX source; a 150–250-word abstract; and 4–6 keywords. The manuscript uses `svjour3` with `smallcondensed`, numbered bracket citations, and `sn-basic`. No margin or body-font reduction was introduced to force compliance. [JIIS submission guidelines](https://link.springer.com/journal/10844/submission-guidelines).

The opening now identifies human-reviewed AI-derived updates in intelligent information systems. The contribution remains a formal admission relation with a conditional failure-distinguishability characterization, executable realization, and controlled implementation evidence. Constructed histories, scripted browser interactions, and fixed workloads are identified explicitly. These are not represented as production deployment or representative production traces. This fits the stated AI/database integration motivation; editorial scope selection remains the journal's decision. [JIIS aims and scope](https://link.springer.com/journal/10844/aims-and-scope).

## Completed limited revisions

1. Revised the Abstract and Introduction opening to make the AI/database/human-review boundary explicit. Kept the relation and its evidence unchanged.
2. Used neutral visible artifact-link labels and equivalent pinned commit links. Actual historical directory/tag identities remain where needed for reproducibility; no remote alias or release was invented or published.
3. Removed all three unverified `GPT-6` attributions. Consolidated duplicated protocol disclosure into captions and the preparation declaration. The declaration records the image-generation prototype, the unrecorded model/version, script rendering with Matplotlib 3.10.8, and author verification/responsibility.
4. Identified E1–E3 as controlled implementation evidence without weakening the existing validity boundaries.
5. Moved Figure 1 onto page 3, removed overall titles/subtitles embedded in both illustrations, and corrected a crowded text block in Figure 2. No arrows, scientific labels, or result values were removed.
6. Added the Online Resource metadata and references, separated and flattened the two editable source sets, and prepared a cover letter and submission metadata.
7. Removed six redundant DOI URLs from bibliography entries while retaining their DOI fields. No citation or bibliographic scientific identity was changed.

## Scientific preservation

The current RQ1–RQ3 wording is identical to the baseline. The contract, Proposition 1, five classes, realization, formal–concrete correspondence, Results, Discussion/Threats, and Conclusion are unchanged apart from supplementary-resource naming. All table scientific content is unchanged; raw data/CSV assets remain byte-identical. The supplementary scientific body and included sections are unchanged. The original DKE main and supplementary PDF hashes still match the frozen originals. No experiment was added or rerun.

The 15 equal-valued substitutions and 165 corresponding-case agreement remain central. Context approval is not portrayed as universally erroneous. Exact binding, complete successors, and total field-source attribution retain their distinct meanings.

## Compilation and package verification

The separately flattened source sets compiled with local MiKTeX. The final main figure revision was followed by two successful passes. There are no unresolved references/citations, overfull boxes, font substitutions, or empty PDF pages. All 30 main and 15 supplementary fonts are embedded. The main has four underfull vertical-box warnings; the supplement has none. All 25 main pages were inspected using rendered contact sheets; relevant pages and both diagrams were also inspected at higher resolution. Supplementary metadata and sampled pages 1, 4, 8, and 14 were inspected, not every supplementary page at full resolution.

**Main:** 25 pages, SHA256 `{audit['main']['sha256']}`.

**Online Resource 1:** 14 pages, SHA256 `{audit['supplement']['sha256']}`. Its former 21-page layout was reformatted; scientific content was retained.

The upload package contains {len(manifest)} files with verified hashes. Each source-set directory is internally flat; upload its files rather than preserving a nested directory tree. The manuscript source and supplementary source are separate compilation targets. The platform-generated PDF should be checked before submission. [JIIS source-upload instructions](https://link.springer.com/journal/10844/submission-guidelines).

## References and availability

All 26 citation keys resolve and are used. Fifteen DOI-bearing entries were checked against Crossref; eleven other entries have accessible primary-source URLs. Three apparent title differences were registered title/subtitle splits, not errors. Two rate-limited lookups were recovered using Crossref's DOI filter endpoint. Four frozen artifact endpoints are accessible. This checks identity metadata and access, not every cited claim or every preprint's latest publication status. Paperpile and its CLI were unavailable; primary/Crossref checks supplied the fallback.

## Independent review and disposition

The [targeted independent review](../paper-critic/2026-10-02-jiis-targeted.md) found no scientific/framing blocker. Its conditional packaging issue is closed by the verified flat-source export. Its supplied abstract count of 208 was superseded by the final mechanical count of 207. No venue-specific citations were added merely to signal fit. The optional recommendation to add caption-final punctuation was not applied because the official guideline specifies captions without terminal punctuation.

Research quality score: **not reassessed**, because the user froze the research and requested limited submission cleanup. Mechanical LaTeX score: **91/100**, applying four underfull-box deductions and five distinct ChkTeX warning-category deductions. This is a formatting diagnostic, not an acceptance probability or novelty grade. `latexmk`/`latexindent` could not run without Perl; direct MiKTeX compilation was used. Missing shared report-stamping/output-verification helpers were replaced with explicit file/hash/PDF/dependency verification and a manual report index.

## Remaining minor observations

- The paper has no page-count buffer. Pages 10 and 12 retain some sparse float-driven space; the final page contains the last two references. No further scientific deletion or layout overhaul was made.
- Figure annotations are readable at the retained width; the smallest text is around 7 pt. The exports are vector PDFs with embedded fonts, plus SVG and 300-dpi PNG previews.
- Historical JSS tags and the DKE-supplement directory remain valid artifact identifiers in the reproduction material. Current visible main-paper journal designation is JIIS. Renaming the frozen archive was neither necessary nor performed.

No remaining issue in this limited audit calls for new experiments. Authors still complete normal submission declarations, author/contribution/competing-interest interface fields, and approval of the platform-generated PDF. The files have not been submitted to JIIS or uploaded to GitHub in this audit.
''')

write_report('reviews/bib-validate/2026-10-02.md', '''# Citation identity and access audit — 2 October 2026

26 cited keys resolve to 26 bibliography entries; no missing or unused entry. Fifteen DOI-bearing records have Crossref metadata and matching titles (including registered subtitles); eleven other references have accessible primary URLs. All four pinned artifact endpoints are accessible. Six redundant DOI URL fields were removed without removing their DOI fields or changing titles, authors, years, or citation keys.

Two HTTP 429 lookups were recovered using Crossref DOI-filter queries. Paperpile/CLI unavailable. This is a metadata and reachability audit, not full cited-claim verification or an exhaustive search for published replacements of preprints. Machine-readable results: `../../external-source-audit.json`.
''')

write_report('figure-qa-report.md', '''# Figure QA — JIIS limited revision

Two four-panel conceptual/evidence diagrams were rerendered by copying the whole original production script and retaining its table/CSV sources. The canvas is 119 × 110 mm. Overall image titles/subtitles were removed; panel headings, scientific labels, arrows, and result values remain. The final exact/reference box received a local line-spacing adjustment after rendered inspection revealed crowding.

## Four-pass review

- Anti-pattern scan: no raster-only master, rainbow scale, default statistical chart, hidden legend, or screenshot source. Boxes and arrows are appropriate for these diagrams.
- Code compliance: copied production drawing/data functions, recorded original-source hashes, vector PDF/SVG and 300-dpi PNG exports, embedded PDF fonts. Journal column width governs size; generic Nature width defaults are inapplicable. Text spans approximately 7–9 pt.
- Visual logic/data integrity: candidate identity differs from value equality; original proposal and authorized correction remain distinct; complete successor and total sources remain explicit. E1 policy separation, E2 request/display boundary, and E3 cost interpretation retain their roles. Numeric source assertions verify 165 agreement, 15 substitutions, request admissions 9→0, three display-only substitutions per condition, and 22,400 timing observations. Colors accompany text, so no conclusion depends on color alone.
- Rendered verification: both diagrams inspected, with Figure 2 re-inspected after the local crowding fix. No overlap or clipping identified in the final exports. Font embedding and inclusion in the final 25-page PDF verified.

## Quantitative-panel documentation

Figure 1 is a constructed explanatory example (candidate proposal 100, authorized value 101, retained batch B-008), not a measured result. Figure 2 is an evidence-route summary with counts, not a new statistical plot. E1 counts paired constructed cases, E2 counts scripted browser cases, and E3 names fixed workload measurements. No mean, spread, confidence interval, hypothesis test, or multiplicity correction is introduced by these diagrams. Their statistical-analysis items are therefore N/A here; existing experiment definitions and numerical tables remain authoritative.

Traceability: E1 labels derive from `tables/dke/comparator.tex`; E2 labels from `tables/dke/review.tex`; E3 source verification includes the original current-study CSVs. `figure-source-hashes.json` records all source hashes. `scripts/build_jiis_figures.py` contains the full adapted script. No AI image generation or scientific data generation occurred in this revision. Earlier prototype assistance remains disclosed in the manuscript.

Verdict: deliverable, with small annotation type documented above. No statistical result was created or altered.
''')

write_report('reviews/INDEX.md', '''# JIIS preparation review index

Trigger: pre-submission-report. Date: 2026-10-02. Scope: limited final format/framing preparation; research frozen.

| Latest per source | Report | Disposition |
| --- | --- | --- |
| pre-submission-report | [Final audit](pre-submission-report/2026-10-02-final.md) | Technical checks PASS; main 25 pages |
| bib-validate | [Reference identity/access](bib-validate/2026-10-02.md) | 26 resolved; metadata/access limits recorded |
| targeted independent review | [JIIS transfer review](paper-critic/2026-10-02-jiis-targeted.md) | No scientific/framing blocker; packaging issue closed |
| academic-figure-skill | [Figure QA](../figure-qa-report.md) | Local figure crowding corrected; source counts preserved |

The shared stamping helper is absent in this installation; this index is maintained directly. The independent review's supplied word count is superseded by `../final-audit.json`.
''')

plan_path = ROOT / 'transition-plan.md'
plan = plan_path.read_text(encoding='utf-8')
first = plan.splitlines()[2]
plan = plan.replace(first, '日期：2026-10-02。状态：**JIIS FINAL PREPARATION AUDIT COMPLETE — SCIENCE FROZEN**。原内容完整迁移的基线为 24 页；完成轻量 framing、声明、图件和上传包装清理后的最终主文为 **25 页（含参考文献、表格和图件）**，补充材料为 **14 页**。摘要 207 词，关键词 6 个。实际投稿文件在 `submission-files/`，最终审计在 `reviews/pre-submission-report/2026-10-02-final.md`。未新增实验，未向 JIIS 提交，也未在本轮推送 GitHub。', 1)
plan_path.write_text(plan, encoding='utf-8')
outputs = ['submission-files/Manuscript.pdf', 'submission-files/ESM_1.pdf',
           'submission-files/cover-letter.txt', 'submission-files/submission-metadata.txt',
           'reviews/pre-submission-report/2026-10-02-final.md', 'final-audit.json',
           'submission-files-manifest.json', 'figure-qa-report.md']
(ROOT / 'final-outputs-manifest.json').write_text(json.dumps({p:sha(ROOT / p) for p in outputs}, indent=2), encoding='utf-8')
print(f'Final checks PASS: {len(manifest)} package files, 26 reference endpoints, 4 artifact endpoints; reports saved.')
