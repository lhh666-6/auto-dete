# First-read reviewer check

Date: 27 September 2026. Read only the title, abstract, introduction/C1-C3, Figure 1, Related Work and conclusion. Answers are restricted to the revised account; they do not rely on the internal comparison matrix.

1. **What concrete problem is solved?** The final authoritative value cannot identify the reviewed proposal, authorized correction or retained field sources. The paper specifies and implements the relation that preserves these distinctions when a reviewed update enters a new authoritative version.

2. **Why distinguish xc from xa in Correction?** The machine may propose 100 while a human authorizes 101. Preserving both values avoids falsely assigning the human correction to the original machine proposal.

3. **Why does equal-valued candidate substitution matter?** It holds the value and retained review context equivalent while changing the admitted instance. The 15 substitutions therefore isolate the authorization target, rather than a difference in value or evidence.

4. **How do context and instance authorization differ?** A context policy permits a candidate satisfying the approved content/context. Instance authorization permits the particular persisted candidate selected for review; an equivalent substitute is still a different target.

5. **What is the admission relation?** Exact persisted candidate -> candidate-bound authorization -> explicit authorized value -> fresh authoritative predecessor -> atomic complete successor -> total field sources. Changed fields resolve to their authorization transitions; unchanged fields preserve exact prior sources.

6. **How does this relate to transactions/OCC/provenance?** Transactions and optimistic validation enforce atomicity and freshness; provenance supplies source/history representations and queries. The manuscript specifies the application-level review and Correction bindings that these mechanisms jointly enforce.

7. **Which prior works are closest?** UPA 2015 is the direct version-specific approval neighbor; Guided Data Repair and Falcon are correction/semantic-effect neighbors. DBWiki and curated-database provenance supply version/source history, while Continuity Kernel supplies closely overlapping exact-proposal activation.

8. **What do those works already cover?** They establish historical-version approval, human replacement values, equal effects with different semantics, unchanged predecessor sources, fine-grained versioned provenance, and exact proposal/pre-state/complete-unit activation. The revised Section 2 explicitly acknowledges these achievements.

9. **What does this paper add?** It specifies this field-level Correction admission relation, characterizes five failure-distinguishing information classes conditionally, and connects that specification to transactional and journal realizations. Its controlled comparator isolates equal-valued instance substitution, and its review-boundary and cost studies examine execution of the specified relation; it does not claim that prior representations cannot encode it.

10. **Why study this distinction independently?** A system can commit the expected value with complete contextual records yet admit an instance that was not the review target. Separating those policies makes the intended accountability question explicit and allows its enforcement and later query answers to be tested.

All ten questions have answers in one to three sentences. The first-read test supports narrative visibility, not a universal originality or publication-readiness verdict. The literature audit separately records the unread AUDIT 2018 method and other coverage gaps.
