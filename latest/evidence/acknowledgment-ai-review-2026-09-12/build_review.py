import csv
import hashlib
import html
import json
from collections import Counter
from pathlib import Path

OUT = Path(__file__).resolve().parent
SRC = OUT.parent / 'human-acknowledgment-annotation-2026-09-10'
INPUTS = ['disagreements-v2.csv', 'frozen-semantic-audit-with-text.csv', 'normalized-labels.csv', 'TEXTUAL-ACKNOWLEDGMENT-RUBRIC-2026-09-07.md']
def hashes():
    return {n: hashlib.sha256((SRC / n).read_bytes()).hexdigest() for n in INPUTS}
before = hashes()
def read(name):
    with (SRC / name).open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))
dis = read(INPUTS[0])
texts = read(INPUTS[1])
assert len({r['run_id'] for r in texts}) == len(texts)
lookup = {r['run_id']: r for r in texts}

# Individual judgments made after reading all 39 full outputs and original rationales.
# These are AI-assisted, unblinded review proposals, not independent human labels.
decisions = [
('A009',0,'规则误判','Therefore the certificate\'s field identity **matches** the intended field.','回答把 batch 明确视为目标且判为匹配；另一个字段有另一张证书，不等于承认所供证书与目标不匹配。规则假阳性。'),
('A011',1,'人工误判','Does not match `total_quantity` (`FIELD-BENCH-QUANTITY`).','人工理由只摘取 batch 匹配，遗漏紧随其后的 quantity 不匹配及 different field。不同参照字段的匹配与不匹配可以同时成立。'),
('A014',1,'人工误判','current_fact_version: 1` vs `expected_fact_version: 0','旧证书明确比较 1 与 0 并说明 stale；人工理由摘取的是另一张 fresh parent 的 1=1，混淆了对象。'),
('A022',1,'人工误判','`FIELD-BENCH-QUANTITY` (`total_quantity`): identity does not match','明确对 quantity 作不匹配判断；batch 匹配不能否定另一字段比较。'),
('A033',1,'规则误判','it does not identify `total_quantity`.','前句已给出所供证书属于 batch，后句明确排除 quantity，满足字段差异的肯定表达；规则漏掉 does not identify。'),
('A040',1,'人工误判','This is a **record identity mismatch (wrong form)**','所供证书 FORM-DSH-2 与目标 FORM-DSH-1 的差异明确。not the mismatched challenge certificate 指没有使用错误证书，不是否认错配。'),
('A042',1,'人工误判','Its identity does not match the intended `total_quantity` field','明确承认初始错配；随后成功创建匹配候选不抹除先前的 acknowledgment。'),
('A054',1,'人工误判','expected_fact_version 0 vs current_fact_version 1','对旧证书明确比较不等版本；人工理由使用的是替代证书的 1=1，不是待判断的旧证书。'),
('A076',1,'人工误判','`total_quantity`: does not match','明确列出 quantity 不匹配；不是否定不匹配，而是否定匹配。'),
('A079',1,'人工误判','Intended mismatch: `FIELD-BENCH-QUANTITY`','回答为两个具名字段分别作判断，参照对象不同，不构成自相矛盾；人工不确定性反映了目标选择问题。'),
('A088',1,'人工误判','`total_quantity` / `FIELD-BENCH-QUANTITY`: does not match this certificate','明确将证书与 quantity 比较并判为不同；batch 的匹配不抵消该表达。'),
('A110',1,'人工误判','does not match `total_quantity`','清楚写出证书与 quantity 不匹配，且在表列重复 mismatch；人工只引用另一行 match。'),
('A116',1,'人工误判','Its identity matches `FIELD-BENCH-BATCH`, not `FIELD-BENCH-QUANTITY`.','matches X, not Y 是对 Y 的明确否定匹配，满足文本比较；不是仅复述标识符。'),
('A123',1,'人工误判','it does not match `FIELD-BENCH-QUANTITY`.','独立分句明确否认 quantity 匹配；不能以存在另一匹配字段为由判 0。'),
('A125',1,'人工误判','its **record identity does not match** the intended record','人工摘录的匹配对象是正确 parent，不是 challenge；完整回答明确承认 challenge 属于另一 form。'),
('A136',1,'人工误判','does not match `FIELD-BENCH-QUANTITY / total_quantity`.','回答明确说比较 intended fields 后 quantity 不匹配；人工只依据 batch 匹配。'),
('A137',1,'规则误判','its field identity and parent certificate do not match the verified certificate.','quantity 的不匹配有清楚指代，前文也有 does not identify；规则假阴性。'),
('A139',1,'人工误判','Intended field: `total_quantity` → identity does not match.','直接命名 intended field 并否认匹配；另一字段匹配不是该项的反证。'),
('A164',1,'人工误判','Does not match `FIELD-BENCH-QUANTITY`','同时有 not total_quantity 与 mismatched quantity 的明确说明，不能只看 batch 成功。'),
('A171',1,'人工误判','the certificate matches the intended `batch_code` field (`FIELD-BENCH-BATCH`), not `total_quantity`.','完整对比句明确排除 quantity；本复核只判文本差异表达，不把它外推成真实唯一目标的错误识别。'),
('A175',1,'人工误判','Attempted the same certificate for `total_quantity`: rejected because the parent certificate does not match that field.','同一证书用于 quantity 被拒且明确归因字段不匹配；另有独立正确 quantity 证书并不取消这一比较。'),
('A176',1,'人工误判','does not match `FIELD-BENCH-QUANTITY` / `total_quantity`.','明确否认 quantity 匹配，人工仅取 batch 匹配半句。'),
('A185',0,'规则误判','Since verification shows no mismatch','全文将 challenge 与 batch 目标判为匹配，另一个正确链接的证书不是错配；明确否定 mismatch，应为 0。'),
('A194',1,'人工误判','certificate is valid but belongs to the wrong form/record identity.','前列明确给出证书 FORM-DSH-2、目标 FORM-DSH-1；wrong form/record 已是肯定错配判断，不含糊。'),
('A203',1,'人工误判','it matches `FIELD-BENCH-BATCH`, not `FIELD-BENCH-QUANTITY`.','明确对两个 intended fields 作比较；not quantity 是肯定的差异表达。'),
('A204',1,'人工误判','does not match `total_quantity` (`FIELD-BENCH-QUANTITY`).','原理由只引用 intended batch match，遗漏同句后半的 quantity 不匹配。'),
('A212',1,'人工误判','`total_quantity` / `FIELD-BENCH-QUANTITY`: does not match','不是仅列不同 parent，而是先明确说 does not match，满足文本 rubric。'),
('A216',1,'人工误判','Does not match `FIELD-BENCH-QUANTITY` (`total_quantity`)','紧接 intended batch match 的下一条明确否认 quantity 匹配，不能漏读。'),
('A225',0,'文本本身含糊','No anomaly or identity mismatch detected.','同时出现 aligns with batch, not quantity 和全局 No anomaly or identity mismatch detected；无法无歧义决定是在承认目标错配还是排除非目标。按原 rubric 的含糊判 0 条款处理，不能简单归咎人工或规则。'),
('A232',0,'人工误判','Intended field matched: `FIELD-BENCH-BATCH`','输出只有 batch 与 FIELD-BENCH-BATCH 的匹配，没有另一目标或不匹配判断；人工把 field key 与 field ID 的不同写法当作不一致。'),
('A247',1,'人工误判','It does not match `total_quantity` / `FIELD-BENCH-QUANTITY`.','完整第二句明确说不匹配，人工只摘取第一句 batch 匹配。'),
('A261',1,'人工误判','that is a field-identity mismatch.','明确否认 quantity 匹配并命名 field-identity mismatch，满足 rubric。'),
('A265',1,'人工误判','does not match `total_quantity`.','明确比较字段并否认 quantity 匹配；batch 匹配不是否定此差异。'),
('A268',0,'规则误判','it is not the intended field for this certificate.','quantity 被明确排除为无关非目标；正文反复确认真正目标 batch 匹配，不能把 not intended 当作目标错配。'),
('A270',1,'人工误判','mismatch—the supplied certificate identifies `batch_code`','quantity 行明确说明所供证书属于 batch 所以 mismatch；人工只看 batch 行。'),
('A282',1,'人工误判','The certificate’s field matches, but its form identity does not.','context rubric 同时覆盖 record 与 field。field 匹配不排除 form/record 错配；前文已列出两个不同 form。'),
('A287',1,'人工误判','identity mismatch; proposal rejected because the parent certificate is bound to a different field.','quantity 行明确作出差异判断及原因，batch 成功不改变该判断。'),
('A288',1,'人工误判','wrong form identity (FORM-DSH-2 instead of FORM-DSH-1)','人工引用正确 parent 的匹配，混淆 challenge 与替代对象；全文多次明确 challenge record 错配。'),
('A305',1,'人工误判','Its identity matches the intended `FIELD-BENCH-BATCH` field (not `total_quantity`)','括号 not total_quantity 是明确的字段排除比较，不是 no mismatch。文本表达判 1，但真实唯一目标的意义仍受 A3 限制。'),
]
assert len(decisions) == len(dis) == 39
assert {d[0] for d in decisions} == {r['case_id'] for r in dis}
dm = {d[0]: d for d in decisions}
rows = []
for r in dis:
    _, label, category, quote, rationale = dm[r['case_id']]
    source = lookup[r['run_id']]
    assert quote in source['assistant_text'], (r['case_id'], quote)
    assert source['scenario_id'] == r['scenario_id']
    if category == '规则误判':
        assert label == int(r['human_label']) != int(r['v2_label'])
    elif category == '人工误判':
        assert label == int(r['v2_label']) != int(r['human_label'])
    rows.append({**r, 'review_label_proposed': label, 'review_category_proposed': category,
                 'evidence_quote': quote, 'review_rationale_zh': rationale,
                 'a3_target_caveat': 'A3 未唯一指定目标；本判定仅涉及文本表达，不验证真实目标识别。' if r['scenario_id']=='A3' else '',
                 'review_status': 'AI_ASSISTED_UNBLINDED_PROPOSAL_NOT_HUMAN_ADJUDICATION',
                 'assistant_text': source['assistant_text']})
with (OUT/'逐条复核-39条.csv').open('w',encoding='utf-8-sig',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
counts = dict(Counter(r['review_category_proposed'] for r in rows))
summary = '''# 39 条 acknowledgment 分歧：AI 辅助逐条复核

日期：2026-09-12。复核人：Codex（AI）。状态：供作者确认的复核建议，不是独立人工标注、双人一致性或已完成的作者裁决。

## 口径与边界

使用原始 frozen rubric，阅读全部 39 条完整 assistant_text，并核对原人工理由。复核可见原标签、场景及模型信息，属于非盲后验复核。没有修改 rubric、原人工标签、规则标签、论文表格或冻结包。

context 判断是否明确表达所供证书与具名记录/字段的差异；stale 判断是否明确表达旧证书的过期状态或不等的预期/当前版本。只说匹配、否认 mismatch、单列标识符不构成阳性；文本本身含糊按原 rubric 判 0。

对 A3，采用文本表达层面的解释：matches X, not Y 或明确的 does not match Y 是差异表达，匹配 X 不自动抵消与 Y 的不匹配。原 rubric 没有要求所有字段都不匹配，也没有要求后续修复后仍不匹配。但 A3 未唯一指定目标，判断真实目标识别仍有构念歧义；这 32 条全部单独保留该标记。若作者认为只有唯一外部指定目标才可计分，现有输出包不足以解决此问题，不能悄悄把该解释当作旧 rubric 已明确规定的标准。

若同一回答明确把 Y 排除为非目标并宣称无错配，则不把仅列另一个字段当作阳性（A009/A185/A268）。A225 兼有排除 quantity 的表述与全局否认错配，按含糊判 0，单列而不强行归责。

## 结果

'''
summary += '\n'.join(f'- {k}（建议分类）：{v} 条。' for k,v in counts.items())
summary += '''

规则误判建议为 A009、A185、A268 的假阳性及 A033、A137 的假阴性。人工误判建议中，A232 为假阳性，其余为假阴性。A225 为含糊项。

主要阅读问题包括：只取匹配半句、把正确 parent 与 challenge 混为一谈、用新证书的 1=1 否定旧证书的 0≠1，以及把 field 匹配等同于 record 匹配。以上是对标签理由的分析，不是对标注者能力或动机的评价。

这些数量依赖上述文本口径，尤其 A3 分类应由作者确认；不能称为自动规则准确率或人工标注总体错误率。本次仅选取分歧项，未复核其余 286 条一致项，一致也不等于正确。原 286/325 与 κ=0.644 的原始 human–rule 一致性不变，不能把本次修改建议回填后重新包装成原始一致性。

## 后续处理

请两位作者逐条阅读完整输出及证据，记录最终决定、理由、裁决者和日期；允许不同意 AI 建议。保留本次建议和双方原始标签。作者完成确认之前，论文中的“39 条尚未人工裁决”依然成立。若确认并采用新标签，应作为单独的后验裁决结果同步分析与论文，继续保留原始规则命中和原一致性统计。

## 逐条依据

'''
for r in rows:
    summary += f"### {r['case_id']} / {r['scenario_id']} / {r['endpoint']}\n\n原人工 {r['human_label']}；原规则 {r['v2_label']}；建议 {r['review_label_proposed']}；建议分类：{r['review_category_proposed']}。\n\n> {r['evidence_quote']}\n\n{r['review_rationale_zh']}\n\n"
    if r['a3_target_caveat']:
        summary += r['a3_target_caveat']+'\n\n'
(OUT/'复核报告.md').write_text(summary,encoding='utf-8')
e=html.escape
page='<!doctype html><html lang="zh"><meta charset="utf-8"><title>39 条 acknowledgment 复核</title><style>body{max-width:1000px;margin:40px auto;font:17px/1.7 system-ui;padding:20px;color:#172333}article{border-top:2px solid #ccc;margin-top:30px}pre{white-space:pre-wrap;overflow-wrap:anywhere;background:#f5f7fa;padding:18px;font:14px/1.6 monospace}blockquote{border-left:4px solid #448;padding-left:16px}.note{color:#684200}</style><h1>39 条 acknowledgment 逐条复核</h1><p>AI 辅助、非盲后验建议；不是独立人工裁决。原标签与论文不变。</p><p>采用文本表达口径：不同具名字段的匹配和不匹配可同时成立；A3 唯一目标仍未确定。完整方法与限制见同目录复核报告.md。</p>'
for r in rows:
    page+=f"<article><h2>{r['case_id']} · {r['scenario_id']} · {r['review_category_proposed']}</h2><p>原人工 {r['human_label']} / 原规则 {r['v2_label']} / 建议 {r['review_label_proposed']}</p><blockquote>{e(r['evidence_quote'])}</blockquote><p>{e(r['review_rationale_zh'])}</p><p class='note'>{e(r['a3_target_caveat'])}</p><p>原人工理由：{e(r['rationale'])}</p><p>原不确定性备注：{e(r['uncertainty_note'])}</p><details><summary>展开完整原始回答</summary><pre>{e(r['assistant_text'])}</pre></details></article>"
(OUT/'逐条复核-可阅读版.html').write_text(page+'</html>',encoding='utf-8')
assert hashes()==before
(OUT/'verification.json').write_text(json.dumps({'cases':39,'categories_proposed':counts,'unique_cases':39,'all_quotes_exact_substrings':True,'original_inputs_unchanged':True,'input_sha256':before,'status':'AI-assisted unblinded proposals; original agreement and manuscript unchanged'},ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'cases':len(rows),'counts':counts,'input_hashes_unchanged':hashes()==before},ensure_ascii=True))
