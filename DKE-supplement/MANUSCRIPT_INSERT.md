# Suggested manuscript insertion (new experiments)

These paragraphs describe the completed supplementary runs. They should be integrated with the paper's definitions and threat model, not presented as independent field validation.

## Strong-context comparator and retrospective queries

We implemented a separate SQLite event-journal comparator retaining candidates, rich review context, immutable events, complete field-source maps, freshness checks, and transactional updates. A second configuration additionally recorded the exact reviewed candidate identifier. This comparator was written for the study; it is not an independently deployed third-party system. We used twelve archived proposal values selected deterministically across the existing three model configurations and four benign scenario labels, supplemented by three synthetic JSON-type boundary inputs. These values were mapped into constructed form histories; no hosted model was called.

Across 15 inputs, 11 case families, and three mechanisms, all 495 executions completed. The exactly bound journal and the reference implementation agreed on all 165 paired cases and their query answers. Each admitted 45 legal cases and rejected 120 cases without changing the fact database. The context-only journal admitted 15 equal-valued candidate substitutions. These admissions satisfied the defined value-level policy but violated the instance-level policy. Conversely, both exactly bound mechanisms rejected these 15 otherwise value-valid substitutions. Among successful histories, 60 reviewed-candidate query answers were ambiguous in the context-only journal; all 810 answers for each exactly bound mechanism were correct. These counts are finite constructed cases and field-level answers, not population failure-rate estimates.

The results identify an enforcement requirement rather than an architectural impossibility: an event journal supplied with the same exact authorization binding can implement the tested contract.

The value-level policy also requires the retained field, version, evidence, and review context to match; it does not mean numeric equality alone. The context projection explicitly omits the certificate identifier, candidate identifier, and per-instance creation timestamp.

The three archived model configurations yielded identical proposal values in the selected four scenarios, so the twelve archived cells contain only four distinct proposal values. Including the synthetic controls gives seven distinct proposal values; execution counts must not be interpreted as independent workflow diversity or provider comparisons.

## Review-boundary experiment

An instrumented local browser interface exercised the unmodified confirmation service and an experimental server-held review-session gate. An independent driver recorded the displayed candidate and authorized value from the DOM before confirmation. Across 60 browser cases, both paths admitted all 9 legitimate controls per path. The original confirmation path admitted 9 request substitutions inconsistent with the previously recorded review intent; the session gate rejected all 9. This exposes the original service's trusted-caller boundary, not a violation of an independently established binding inside its transaction. Both paths rejected stale submissions, replays, and injected precommit interruptions without fact writes.

Both paths admitted all 3 DOM-only substitutions, in which the displayed identifier changed while the server-side target remained unchanged. Thus, session binding does not attest display integrity. The study used scripted interactions and fixed principal labels, and did not test human attention, authentication security, a compromised host, or cross-database crash atomicity.

## Current-version cost characterization

We reran cost measurements against the equality-repaired implementation on one Windows machine using CPython 3.11.16 and SQLite 3.53.1. Each cell used five warmups and 200 measured executions per arm, with seeded interleaving. Two ten-cell admission comparisons distinguished complete confirmation under the shared workload from an explicitly prevalidated materialization ablation. The latter verified the resulting relational-state fingerprint but omitted validation from its timed region; it is not a complete admission alternative.

The 36-cell trace comparison held the current verifier fixed and changed three bulk repository reads to identifier enumeration followed by point lookups. The full returned trace object was identical after every invocation. At 128 fields, 100 versions, and 1,000 records, bulk tracing had a median latency of 170.24 ms; the point-to-bulk median ratio was 2.99. These are within-run access-pattern measurements, not historical cross-machine speedups. Synthetic storage fixtures at 1,000, 10,000, and 100,000 transitions characterize schema footprint only. All raw observations, configurations, code hashes, and paired summaries are retained.

The complete-mechanism timer covers the confirmation call and excludes database cloning and adapter construction. The journal opens its SQLite connection eagerly during construction, whereas the ORM arm opens its first connection lazily inside the call. These measurements therefore characterize the stated interface boundary; they are not a connection-controlled algorithm microbenchmark or an isolated estimate of exact-binding overhead.
