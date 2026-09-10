# Third-party re-adjudication protocol (not yet completed)

The r27 manuscript discloses that the 12 author-adjudicated items were resolved
by an author, not by an independent non-author third party. This protocol and
template make the optional strengthening step concrete. **It has not been
performed; the manuscript does not claim that it has.**

## Scope

The 12 items are the 11 pre-adjudication human--rule disagreements
(T014, T061, T120, T122, T126, T142, T152, T171, T183, T226, T248) plus T153.
All 12 are recorded in `third-party-adjudication-template.csv` together with
the two annotators' labels and rationales, the frozen rule label, and the
author's adjudicated label and note.

## What an independent adjudicator would do

1. Receive only the task prompt, the model response, and the frozen completion
   rubric (1 = terminal state reached, 0 = not reached or over-claimed host
   authority, 9 = truncated/unavailable/undetermined).
2. Be blind to the author's adjudicated label, the model configuration, the
   prompt variant, the repetition, and the study hypotheses. The
   `third_party_label` column is blank for this reason.
3. Record an independent label in `third_party_label` and a short rationale in
   `third_party_note`, plus a pseudonymous identifier and a
   `third_party_blind_confirmation` flag.
4. Report disagreement with the author adjudication rather than forcing
   consensus. Disagreements would be reported in the manuscript and would not
   be overwritten.

## What the result would change

- If the third-party labels agree with the author's 12 labels, the manuscript
  could state that the author adjudication was independently reproduced.
- If they disagree, the manuscript would report the disagreement and the
  pre-adjudication human--rule disagreements would remain the evidential basis.
  The current r27 text already limits the claim to author adjudication, so a
  disagreement would not invalidate the reported 320/335 strict count; it would
  change the interpretation of the adjudicated labels only.

## Current status

The public package contains this protocol and the blank template. No
third-party labels exist in the package. A completed template, if supplied by a
non-author adjudicator, should be committed as a new versioned file rather than
overwriting this template.

## Relation to the manuscript

`paper/supplement.tex` (human-annotation subsection) and
`paper/sections/08-results.tex` currently state that the adjudicator was the
author and that the 11 pre-adjudication human--rule disagreements remain
visible. Those statements remain accurate. This protocol is the documented path
to a stronger claim, not evidence that the stronger claim has been made.
