# Benchmark Implementation Plan v2 — Changelog

Date: 2026-08-28

## Scope

`BENCHMARK_IMPLEMENTATION_PLAN_v2.md` preserves the approved authority-admission research question,
the fourteen scenarios, the two-tool model surface, historical-evidence immutability, and the
replace-not-stack manuscript strategy. It changes the live-model design and implementation gates.

## Changes from v1

1. Replaced three Codex-requested configurations with a four-slot cross-provider target: two
   GPT/OpenAI live configurations (G1, G2) and two DeepSeek live configurations (D1, D2).
2. Renamed the artifact-facing study to **Repeated Cross-Model Live-Agent Authority Benchmark** and
   the paper-facing study to **Repeated live-agent authority benchmark across multiple model
   configurations and provider families**. It is not framed as GPT-versus-DeepSeek ranking.
3. Added provider-neutral adapters and `ProviderNeutralAgentEvent`; provider-specific raw schemas
   cannot enter the scorer.
4. Added `canonical_tool_surface.json`, captured provider schemas, and a hard logical tool-schema
   equivalence gate. Every model sees proposal and verification only; fact admission remains host-only.
5. Changed the non-citable pilot to `4 × 14 × 2 × 1 = 112` and added
   `pilot-model-qualification.json` plus explicit OpenAI/DeepSeek qualification requirements.
6. Changed the default final design to `4 × 14 × 3 × 10 = 1,680` locked executions. Added the
   pre-result resource fallback `4 × 14 × 3 × 5 = 840`; balanced repetitions are mandatory.
7. Added `FINAL_RESOURCE_GATE.json`. No final call may occur before pilot qualification, resource
   approval, and `FROZEN.json` verification.
8. Froze two primary endpoints before final execution: Benign Task Completion Rate and Unauthorized
   Authoritative Mutation Rate. All other outcomes are secondary or diagnostic.
9. Split agent-mediated behavior from host-driven admission-mechanism challenges in the raw schema,
   normalized outputs, denominators, result tables, captions, and interpretation.
10. Added the explanatory analysis **Behavioral Variation vs Authority Invariance** while keeping
    provider/configuration comparisons descriptive.
11. Expanded adapter tests for OpenAI/Codex, DeepSeek streaming/non-streaming, canonical events,
    malformed/error responses, missing metadata, provider-independent scoring, and tool equivalence.
12. Froze the attempted four-slot roster and qualification outcomes. Final execution requires at
    least one qualified configuration from each provider family; unavailable slots cannot be filled
    by mocks, DSH ToolRuntime, deterministic calls, or replayed traces.
13. Required provider-specific planned T, authority-evaluable N, and runtime-failure F reporting.
    Runtime failures remain visible and cannot be silently removed from denominators.
14. Replaced one mixed result table with two logically separate tables (or two separately labeled
    panels) plus one figure; the complete scenario breakdown remains in the artifact.
15. Updated the authorized implementation order to test first, then deterministic dry run, pilot,
    resource gate, freeze, final run, artifact verification, and manuscript replacement.

## Unchanged hard boundaries

- Core claim: proposal capability is not fact-admission authority.
- Four benign/recoverable and ten negative scenario families.
- No production authority-semantic change and no model-facing fact-write capability.
- No mutation, overwrite, cleanup, or re-manifesting of historical frozen evidence.
- Pilot results are non-citable and physically excluded from final normalization.
- No final benchmark before freeze; no post-result model, prompt, scenario, scoring, denominator,
  retry, timeout, or repetition change.
- Claims remain authoritative-state admission integrity, not general AI safety, prompt-injection
  security, jailbreak resistance, or provider/model superiority.
