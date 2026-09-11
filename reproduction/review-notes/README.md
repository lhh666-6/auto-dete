# Author working notes — 2026-09-11

> **These are internal author working notes. They are not part of the artifact
> claim, they are not evidence for any manuscript claim, and none of the
> recommendations below have been applied to the manuscript or to the code.**
>
> They are recorded here for provenance: they document an upstream reading of
> the manuscript's prose and a proposed (not executed) compression and
> restructuring plan. A reviewer or reader who finds them should treat them as
> drafts. The manuscript, not these notes, states the authors' claims.

## Contents

| File | What it is |
|---|---|
| `STYLE-REVIEW-2026-09-11.md` | A prose-level review of the manuscript: AI-writing-pattern scan, punctuation and terminology consistency, and a measurement of negation / scope-limiting density across sections. |
| `COMPRESSION-AND-NARRATIVE-PLAN-v2.md` | A proposed page-budget reduction and narrative-restructuring plan, including a claim-wording ("claim ladder") table that constrains how each result may be paraphrased. |
| `tools/` | The read-only probes used to produce the measurements in the two documents above. |

## Status of the recommendations

Nothing in these notes has been applied. The manuscript at the verified
revision is unchanged; the notes are inputs to a decision the authors have not
yet taken. In particular:

- Claims about Proposition 1, the evaluated-control comparison, and the cost
  characterization must keep the exact scoping used in the manuscript. The
  "claim ladder" table in `COMPRESSION-AND-NARRATIVE-PLAN-v2.md` exists to make
  that constraint explicit, because a paraphrase that drops the scope turns a
  bounded result into an over-claim.
- The two papers most likely to be affected by any future edit are the
  second-author's sections; the plan notes where author sign-off would be
  required before editing.

## Running the probes

The three probes take the path to the compiled paper directory from the
`AUTODECTE_PAPER` environment variable, defaulting to `../../latest/paper`
relative to the script. They need Python 3.9+ and `pymupdf` for `page_budget.py`;
the other two use only the standard library.

```bash
export AUTODECTE_PAPER=/path/to/latest/paper
python -B tools/page_budget.py        # per-section page budget (needs PyMuPDF)
python -B tools/readability_probe.py  # negation / scope-limiting density
python -B tools/style_probe.py        # sentence statistics and lexicon counts
```

All three are read-only. Sentence splitting is regex-based and therefore
approximate; `style_probe.py`'s lexicon counts are exact literal substring counts.
