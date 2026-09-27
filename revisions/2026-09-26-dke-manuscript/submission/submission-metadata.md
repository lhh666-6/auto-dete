# DKE 投稿信息

供投稿系统复制填写；本文件不代替作者确认，也不随主文上传。信息取自本目录 `main.tex` 和 `sections/declarations.tex`。文章类型拟选 Research article；最终以投稿系统可选项为准。

## Title

Correction-Aware Data Admission: Candidate-Bound Authorization and Field-Level Provenance for AI-Derived Updates

## Abstract

Identical authoritative values can arise from different machine proposals and human authorizations. Correction must preserve what the machine proposed while recording the value a reviewer authorized. Even equal-valued candidates with equivalent retained context can be distinct authorization targets. We specify a correction-aware admission relation that binds review to an exact persisted candidate and an explicit authorized value. It checks predecessor freshness and atomically creates a complete successor with total field-level sources. Five paired histories establish class-wise irredundancy of failure-distinguishing information classes in the declared observation model. A Python/SQLite realization connects the relation to bounded Alloy analysis, formal–concrete projections, and a 35-case fault catalogue. In a policy comparison, an exact-binding event journal and the relational reference agree on all 165 corresponding cases. A context journal accepts 15 equal-valued substitutions that satisfy its value/context policy but violate instance authorization; both exact-binding mechanisms reject them. A server-held review-session gate rejects nine request substitutions accepted by the original confirmation path, while three display-only substitutions remain admissible in both paths. Current-version workloads characterize admission, reverse-trace, and storage costs. Together, the results establish an executable relation that preserves corrected proposal histories, enforces instance-specific authorization across two storage designs, and makes each committed field's authorization and source queryable.

## Keywords

data integrity; data provenance; human authorization; AI-assisted data acquisition; transactional admission; relational verification

## Authors, in manuscript order

| Order | Display name in manuscript | Affiliation | Corresponding author | Known email |
| --- | --- | --- | --- | --- |
| 1 | Liang Hanghao | 1 | No | Not supplied |
| 2 | Xuan Wentao | 1 | No | Not supplied |
| 3 | Chen Qile | 1 | No | Not supplied |
| 4 | Peng Peng | 1 | Yes | hnu16pp@hnu.edu.cn |

Affiliation 1: College of Computer Science and Electronic Engineering, Hunan University, Lushan South Road, Yuelu District, Changsha 410082, China.

姓名沿用论文既有显示格式；投稿系统的 given name / family name 拆分需本人确认，不能依据显示顺序自动推定。原稿未提供 ORCID，须由各作者提供或按系统规则留空。第三作者为陈奇乐，与其他作者使用相同单位。

## CRediT authorship contribution statement

Liang Hanghao: Conceptualization, Methodology, Software, Formal analysis, Investigation, Data curation, Validation, Visualization, Project administration, Writing–original draft, and Writing–review & editing.

Xuan Wentao: Methodology, Formal analysis, Investigation, Data curation, Validation, Visualization, and Writing–review & editing.

Chen Qile: Investigation and Validation.

Peng Peng: Supervision and Writing–review & editing.

## Funding and competing interests

Current manuscript funding statement: This research received no external funding.

Current manuscript competing-interest statement: The authors declare no competing interests.

两项均须经全体作者最终确认；此处仅转录既有声明。

## Data and software availability

New comparison, browser-boundary, and current-version cost evidence:
https://github.com/lhh666-6/auto-dete/tree/2645e5e18c900ea91c9c980e44195dc71e410432/DKE-supplement

Reference implementation: commit c6d512843c905cab6d8521dd8c914f7fb26d85ae, directory latest/code/implementation-fixed.

Formal models, observation witnesses, and earlier annotation/integration evidence:
https://github.com/lhh666-6/auto-dete/tree/r31-jss-2026-09-13/latest

Historical v8 evidence tag: r21-jss-2026-09-07-v8.

Use the full declaration in `sections/declarations.tex` if the system requests a full data-availability statement. Supplement S1 identifies evidence layers and explains restoration of the compressed large database.

## Other disclosures and upload mapping

- Manuscript: `submission/upload/manuscript.pdf`; flat source archive: `submission/upload/main-source.zip`, entry point `main.tex`.
- Supplementary material: `submission/upload/supplementary-material.pdf`; flat source archive: `submission/upload/supplement-source.zip`, entry point `supplement.tex`.
- Highlights: `submission/upload/highlights.docx` (five bullets; respective text lengths including spaces, excluding bullet markers: 79, 78, 74, 79, 77 characters).
- Cover letter: `submission/upload/cover-letter.docx`; editable plain text: `submission/cover-letter.txt`; final text is subject to corresponding-author approval.
- Ethics and generative-AI statements: use the final text in `sections/declarations.tex`, not a separately retyped or older statement.
- Author confirmations: `submission/author-confirmation-checklist.md` is for internal use only.

Do not upload editorial working notes, this metadata sheet, or the internal author-confirmation checklist as supplementary scientific material.
