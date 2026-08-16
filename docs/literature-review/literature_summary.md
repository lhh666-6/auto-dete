# Focused literature synthesis for the ESWA revision

## Scope and method

The revision uses a focused bibliography spanning document understanding, selective prediction, human oversight, provenance, generative information extraction, and AI governance. DOI-bearing records were checked against Crossref or official publisher metadata; PMLR, ACL Anthology, W3C, NIST, and arXiv records were checked on their official pages where applicable. Paperpile and the local `scholarly` command were unavailable, so collection-membership checks could not be performed.

## Synthesis

Document-AI research establishes strong representation and recognition baselines (LayoutLM, LayoutLMv2/v3, DocFormer, Donut, TrOCR, and PP-OCRv3). These systems primarily improve inference. ArUco research provides deterministic form geometry. Neither strand directly specifies how a prediction acquires authority in an operational data model.

Human-in-the-loop literature motivates uncertainty-driven review and user control. Selective-classification work formalizes the error--rejection trade-off, while calibration and conformal-prediction work clarify uncertainty reporting. Auto-Decte uses a transparent distance-margin selector, but its paper-level contribution is the coupling of abstention with candidate--fact separation.

Provenance literature supplies concepts for tracing entities, activities, and agents. Human-centered AI and risk-governance sources motivate explicit oversight, lifecycle controls, and accountability. Generative information extraction and RAG explain the capabilities of optional assistance, but not its authority. The revision therefore positions LLM output and retrieval results as non-authoritative artifacts that require an attributable human transition before entering versioned facts.

## Gap statement

The reviewed strands cover prediction quality, selective routing, human interaction, provenance, and generative assistance separately. The paper targets the narrower systems gap of making machine-to-fact isolation an executable application invariant and testing that invariant through injected faults and reverse-trace checks.

## Evidence boundary

The literature supports the design motivation, not claims of production effectiveness. The current quantitative evidence is synthetic. A real-form study with independent double transcription and a human-review experiment are required before making field-performance or reviewer-benefit claims.
